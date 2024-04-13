import pytest
from django.test import TestCase, Client
from django.urls import reverse
import redis
import json
from django.core.cache import cache

from ..models import *
from ..serializers import BannerSerializer
from ..views import UserBannerView

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def redis_client():
    return redis.Redis(host='localhost', port=6379, db=0)

@pytest.mark.django_db
def test_get_user_banner_with_last_revision(client, redis_client):
    feature = Feature.objects.create(name='Feature 1')
    tag = Tag.objects.create(name='Tag 1')
    Banner.objects.create(feature_id=feature,
                                   content={'title': 'banner1 title',
                                            'text': 'banner1 text',
                                            'url': 'banner1 url'},
                                    is_active=True).tag_id.add(tag)
    
    data = {
        "tag_id": 1,
        "feature_id": 1,
        "use_last_revision": True,
    }
    url = reverse('user_banner')
    headers = {
        'HTTP_TOKEN': 'user_token'
    }
    response = client.get(url, data=data, **headers)


    assert response.status_code == 200

    expected_data = {
        'title': 'banner1 title',
        'text': 'banner1 text',
        'url': 'banner1 url',
    }
    assert response.data == expected_data

@pytest.mark.django_db
def test_get_user_banner_without_last_revision(client, redis_client):
    feature = Feature.objects.create(name='Feature 2')
    tag = Tag.objects.create(name='Tag 2')
    Banner.objects.create(feature_id=feature,
                                   content={'title': 'banner2 title',
                                            'text': 'banner2 text',
                                            'url': 'banner2 url'},
                                    is_active=True).tag_id.add(tag)
    
    banner = Banner.objects.get(tag_id=2, feature_id=2)
    redis_client.set(f'banner:{banner.feature_id}:{banner.id}', json.dumps(banner.content), ex=10)
    url = reverse('user_banner')
    parameters = {
        'tag_id': 2,
        'feature_id': 2,
        'use_last_revision': False,
    }

    headers = {
        'HTTP_TOKEN': 'user_token'
    }
    response = client.get(url, data=parameters, **headers)

    assert response.status_code == 200

    expected_data = banner.content
    assert response.data == expected_data

@pytest.mark.django_db
def test_get_user_banner_404_error(client):
    feature = Feature.objects.create(name='Feature 3')
    tag = Tag.objects.create(name='Tag 3')
    Tag.objects.create(name='Tag 4')
    Banner.objects.create(feature_id=feature,
                                   content={'title': 'banner3 title',
                                            'text': 'banner3 text',
                                            'url': 'banner3 url'},
                                    is_active=True).tag_id.add(tag)
    url = reverse('user_banner')
    parameters = {
        'tag_id': 4,
        'feature_id': 3,
        'use_last_revision': False,
    }

    headers = {
        'HTTP_TOKEN': 'user_token'
    }
    response = client.get(url, data=parameters, **headers)

    assert response.status_code == 404

    expected_data = {'description': 'Баннер не найден',
                     'status_code': 404
    }
    assert response.data == expected_data

@pytest.mark.django_db
def test_get_user_banner_403_error(client):
    url = reverse('user_banner')
    parameters = {
        'tag_id': 20,
        'feature_id': 20,
        'use_last_revision': False,
    }

    headers = {
        'HTTP_TOKEN': 'user_token12345'
    }
    response = client.post(url, data=parameters, **headers)

    assert response.status_code == 403

    expected_data = {'description': 'Пользователь не имеет доступа',
                     'status_code': 403
    }
    assert response.data == expected_data


@pytest.mark.django_db
def test_get_user_banner_500_error(client):
    Feature.objects.create(name='Feature 5')
    Tag.objects.create(name='Tag 5')
    Tag.objects.create(name='Tag 6')
    url = reverse('user_banner')
    parameters = {
        'tag_id': 5,
        'feature_id': 4,
        'use_last_revision': True,
    }

    headers = {
        'HTTP_TOKEN': 'user_token'
    }
    response = client.get(url, data=parameters, **headers)

    assert response.status_code == 500

    expected_data = {'description': 'Внутренняя ошибка сервера',
                     'status_code': 500
    }
    assert response.data == expected_data