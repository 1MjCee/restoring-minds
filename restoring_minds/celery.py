from restoring_minds.celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restoring_minds.settings')
app = Celery('restoring_minds')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()