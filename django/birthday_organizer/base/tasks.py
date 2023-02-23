from celery import shared_task
from datetime import datetime

@shared_task(name="create_birthday_event")
def create_birthday_event(*args, **kwargs):
    with open('/tmp/' + datetime.now().strftime('%H_%M_%S'), 'w'):
        pass

