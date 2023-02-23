from celery import shared_task
from .email import Email


email = Email()


@shared_task(name="sample_periodic_event")
def sample_periodic_event(*args, **kwargs):
    email.send_email(['gvkunchev@gmail.com'], 'Birthday organizer', 'It works!')

