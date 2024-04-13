from banner_service.celery import app
from .models import Banner
from .serializers import BannerSerializer

import redis
import json

@app.task
def update_redis_info():
    banners = Banner.objects.filter(is_active=True)
    serializer = BannerSerializer(banners, many=True)
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    redis_client.flushall()
    for row in serializer.data:
        if len(row['tag_id']) > 1:
            for tag_id in row['tag_id']:
                redis_client.set(f'banner:{row["feature_id"]}:{tag_id}', json.dumps(row), ex=300)
        else:
            redis_client.set(f'banner:{row["feature_id"]}:{row["tag_id"][0]}', json.dumps(row), ex=300)

def test():
    banners = Banner.objects.filter(is_active=True)
    serializer = BannerSerializer(banners, many=True)
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    for row in serializer.data:
        if len(row['tag_id']) > 1:
            for tag_id in row['tag_id']:
                redis_client.set(f'banner:{row["feature_id"]}:{tag_id}', json.dumps(row), ex=298)
        else:
            redis_client.set(f'banner:{row["feature_id"]}:{row["tag_id"][0]}', json.dumps(row), ex=298)