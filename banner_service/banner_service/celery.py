import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banner_service.settings')

app = Celery('banner_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'update-redis-info': { 
        'task': 'banners.tasks.update_redis_info',
        'schedule': crontab(minute='*/5'),
    },

}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')