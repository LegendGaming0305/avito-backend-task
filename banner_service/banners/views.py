from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.db.utils import IntegrityError
from django.db import connection
from datetime import datetime, timedelta
from django.db.models import Q, F, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
import redis
import json

from .models import Banner, Tag
from .serializers import BannerSerializer, TagSerializer
from .permissions import AdminTokenPermission, UserTokenPermission


class UserBannerView(APIView):
    permission_classes = [UserTokenPermission | AdminTokenPermission]
    
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)

    def get(self, request):
        query_data_serializer = BannerSerializer(data=request.query_params)
        query_data_serializer.is_valid(raise_exception=True)
        query_data = query_data_serializer.data
        tag_id = query_data.get("tag_id")[0]
        feature_id = query_data.get("feature_id")

        use_last_revision = request.query_params.get("use_last_revision").lower() != 'false'

        if use_last_revision:
            try:
                queryset = Banner.objects.filter(is_active=True, tag_id=tag_id, feature_id=feature_id)
                serializer = BannerSerializer(queryset, many=True)
                content = serializer.data[0]['content']
                return Response(data=content, status=status.HTTP_200_OK)
            except Exception as exc:
                return Response(data={'description': 'Внутренняя ошибка сервера', 'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            cache_key = f'banner:{feature_id}:{tag_id}'
            try:
                cached_data = self.redis_client.get(cache_key)
            except Exception:
                pass

            if cached_data:
                return Response(json.loads(cached_data), status=status.HTTP_200_OK)
            else:
                try:
                    banner_info = Banner.objects.values('content').get(is_active=True, tag_id=tag_id, feature_id=feature_id)
                except Exception:
                    return Response(data={'description': 'Баннер не найден', 'status_code': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
                self.redis_client.set(f'banner:{feature_id}:{tag_id}', json.dumps(banner_info['content']), ex=300)
                return Response(data=banner_info['content'], status=status.HTTP_200_OK)


class BannerView(APIView):
    permission_classes = [AdminTokenPermission]

    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
    
    def get(self, request):
        query_data_serializer = BannerSerializer(data=request.query_params)
        query_data_serializer.is_valid(raise_exception=True)
        query_data = query_data_serializer.data
        feature_id = query_data.get('feature_id')
        tag_id = query_data.get('tag_id')[0] if query_data.get('tag_id') else None
        limit = int(request.query_params.get('limit'))
        offset = int(request.query_params.get('offset', 0))

        queryset = Banner.objects.all()

        if feature_id:
            queryset = queryset.filter(feature_id=feature_id)

        if tag_id:
            queryset = queryset.filter(tag_id=tag_id)

        queryset = queryset[int(offset):]

        if limit:
            queryset = queryset[:int(limit)]

        serializer = BannerSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = BannerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        banner = serializer.save()

        for tag_id in request.data.get('tag_ids'):
            try:
                tag = Tag.objects.get(id=tag_id)
                banner.tag_id.add(tag)
            except Tag.DoesNotExist:
                raise NotFound()
            
        banner = Banner.objects.get(content=serializer.data['content'], is_active=serializer.data['is_active'], created_at=serializer.data['created_at'])
        serializer_id = BannerSerializer(banner)
        banner_id = serializer_id.data['id']
        return Response(data={'id': banner_id}, status=status.HTTP_201_CREATED)


class BannerIdView(APIView):
    permission_classes = [AdminTokenPermission]

    def get(self, request, id):
        previous_version_uuid_subquery = Banner.objects.filter(
            id=id
        ).order_by('-updated_at').values('previous_version_uuid')[:1]

        last_three_banners_subquery = Banner.objects.filter(
            id=id
        ).values_list(
            Coalesce('previous_version_uuid', Subquery(previous_version_uuid_subquery)),
            flat=True
        ).order_by('-updated_at')[:3]

        queryset = Banner.objects.filter(
            Q(id=id, is_active=True) |
            Q(uuid__in=Subquery(last_three_banners_subquery))
        ).order_by('-updated_at')

        serializer = BannerSerializer(queryset, many=True)
        return Response(data=serializer.data)

    
    def patch(self, request, id):
        banner = get_object_or_404(Banner.objects.filter(id=id, is_active=True))
        serializer = BannerSerializer(banner, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                pass

            is_active = not serializer.validated_data.get('is_active')
            Banner.objects.filter(uuid=serializer.data['uuid']).update(is_active=is_active)

            patched_banner = Banner.objects.filter(id=id).order_by('-updated_at').first()

            tag_ids = request.data.get('tag_ids', [])
            for tag_id in tag_ids:
                try:
                    tag = get_object_or_404(Tag, id=tag_id)
                    patched_banner.tag_id.add(tag)
                except NotFound:
                    raise
            return Response(data={'description': 'OK'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            banner = Banner.objects.get(id=id)
            banner.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'description': 'Некорректные данные'}, status=status.HTTP_400_BAD_REQUEST)
        
class BannerIdVersionView(APIView):
    permission_classes = [AdminTokenPermission]

    def get(self, request, id, uuid):
        banner = Banner.objects.get(id=id, uuid=uuid)
        serializer = BannerSerializer(banner)
        return Response(data=serializer.data)