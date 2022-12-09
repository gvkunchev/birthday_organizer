from celery import shared_task
from .models import CustomUser

@shared_task(name="create_birthday_event")
def create_birthday_event(*args, **kwargs):
    print('Working')

