import datetime

from django.utils import timezone
from django.template.loader import render_to_string

from celery import shared_task
from .email import Email
from .models import Event
from users.models import CustomUser


# Time before a birthday that should trigger event creation
EVENT_CREATOR_SPAN = datetime.timedelta(days=14)

# Time before an event that should trigger an alert if no host yet
NO_HOST_ALERT_SPAN = datetime.timedelta(days=14)

# Domain name for constructing links
# TODO: Put the real one once in production
DOMAIN_NAME = 'http://34.118.114.251'


email = Email()


@shared_task(name="create_birthday_event_per_user")
def create_birthday_event_per_user(*args, **kwargs):
    """Create birthday events automatically."""
    all_users = CustomUser.objects.all()
    for user in all_users.iterator():
        if user.is_superuser:
            continue
        next_birthday = user.get_next_birthday()
        if not datetime.timedelta() < next_birthday - timezone.now() < EVENT_CREATOR_SPAN:
            continue # Birthday passed or not close enough
        # Prepare data for a new event
        name = f'{user.full_name} {next_birthday.year - user.birthdate.year} Birthday'
        date = next_birthday
        celebrant = user
        # Ensure the event doesn't exist and create it
        try:
            Event.objects.get(date=date, celebrant=celebrant)
        except Event.DoesNotExist:
            event = Event(name=name, date=date, celebrant=celebrant)
            event.save()
        # Collect all users to receive an alert email for the new event
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser:
                continue
            if user != event.celebrant:
                all_emails.append(user.email)
        context = {
            'event_link': f'{DOMAIN_NAME}/event?id={event.id}',
            'event_name': event.name
        }
        email.send_email(all_emails,
                         f'New event - "{event.name}"',
                         render_to_string('emails/new_event.html', context))

@shared_task(name="alert_for_events_without_host")
def alert_for_events_without_host(*args, **kwargs):
    """Alert for upcoming events that still doesn't have hosts."""
    all_events = Event.objects.all().filter(archived=False)
    all_users = CustomUser.objects.all()
    for event in all_events.iterator():
        if not datetime.timedelta() < event.date - timezone.now() < NO_HOST_ALERT_SPAN:
            continue # Event passed or not close enough
        if event.host is not None:
            continue # Already has a host
        # Collect all users to receive an alert email
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser:
                continue
            if user != event.celebrant:
                all_emails.append(user.email)
        context = {
            'event_link': f'{DOMAIN_NAME}/event?id={event.id}',
            'event_name': event.name
        }
        email.send_email(all_emails,
                         f'Host wanted - "{event.name}"',
                         render_to_string('emails/no_host_alert.html', context))

@shared_task(name="alert_for_new_comments")
def alert_for_new_comments(*args, **kwargs):
    """Alert for new comments on events that the person participates in."""
    all_events = Event.objects.all().filter(archived=False)
    all_users = CustomUser.objects.all()
    for event in all_events.iterator():
        send_alert = False
        for comment in event.comments.all():
            if not comment.alert_sent:
                send_alert = True
            comment.alert_sent = True
            comment.save()
        if not send_alert:
            continue # No new comments - no need to alert
        # Collect all users to receive an alert email
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser:
                continue
            if event.eligible_for_actions(user):
                all_emails.append(user.email)
        context = {
            'event_link': f'{DOMAIN_NAME}/event?id={event.id}',
            'event_name': event.name
        }
        email.send_email(all_emails,
                         f'New comments - "{event.name}"',
                         render_to_string('emails/new_comments.html', context))

@shared_task(name="archive_events")
def archive_events(*args, **kwargs):
    """Archive passed events."""
    all_events = Event.objects.all().filter(archived=False)
    for event in all_events.iterator():
        if event.date < timezone.now():
            event.archived = True
            event.save()
