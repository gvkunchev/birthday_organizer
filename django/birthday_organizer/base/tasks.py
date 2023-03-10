import datetime

from django.utils import timezone

from celery import shared_task
from .email import Email
from .models import Event
from users.models import CustomUser


# Time before a birthday that should trigger event creation
EVENT_CREATOR_SPAN = datetime.timedelta(days=14)


# TODO: Put this line back if emails are needed
#email = Email()


@shared_task(name="create_birthday_event_per_user")
def create_birthday_event_per_user(*args, **kwargs):
    all_users = CustomUser.objects.all()
    for user in all_users.iterator():
        next_birthday = user.get_next_birthday()
        if not (datetime.timedelta() < next_birthday - timezone.now() < EVENT_CREATOR_SPAN):
            continue # Birthday passed or not close enough
        # Prepare data for a new event
        name = f'{user.full_name} {next_birthday.year - user.birthdate.year} Birthday'
        date = next_birthday
        celebrant = user
        # Ensure the event doesn't exist and create it
        try:
            Event.objects.get(date=date, celebrant=celebrant)
        except Event.DoesNotExist:
            new_event = Event(name=name, date=date, celebrant=celebrant)
            new_event.save()
