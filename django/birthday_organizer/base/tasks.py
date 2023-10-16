import datetime

from django.utils import timezone
from django.template.loader import render_to_string

from celery import shared_task
from .email import Email
from .models import Event
from users.models import CustomUser


# Time before a birthday that should trigger event creation
EVENT_CREATOR_SPAN = datetime.timedelta(days=14)

# Time after a birthday that should trigger event archive
EVENT_ARCHIVER_SPAN = datetime.timedelta(days=14)

# Time before an event that should trigger an alert if no host yet
NO_HOST_ALERT_SPAN = datetime.timedelta(days=14)

# Domain name for constructing links
# TODO: Put the real one once in production
DOMAIN_NAME = 'https://birthday-organizer.onrender.com/'


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
            continue
        except Event.DoesNotExist:
            event = Event(name=name, date=date, celebrant=celebrant)
            event.save()
        # Collect all users to receive an alert email for the new event
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser or not user.allow_alerts:
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
        if event.celebrant:
            context = {
                'wishlist_link': f'{DOMAIN_NAME}/wishlist'
            }
            email.send_email([event.celebrant.email],
                            f'Wishlist reminder',
                            render_to_string('emails/wishlist_reminder.html', context))

@shared_task(name="alert_for_events_without_host")
def alert_for_events_without_host(*args, **kwargs):
    """Alert for upcoming events that still doesn't have hosts."""
    all_events = Event.objects.all().filter(archived=False)
    for event in all_events.iterator():
        if not datetime.timedelta() < event.date - timezone.now() < NO_HOST_ALERT_SPAN:
            continue # Event passed or not close enough
        if event.host is not None:
            continue # Already has a host
        # Collect all users to receive an alert email
        all_users = event.participants.all()
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser or not user.allow_alerts:
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
        comments_to_alert_for = []
        for comment in event.comments.all():
            if not comment.alert_sent:
                comments_to_alert_for.append(comment)
            comment.alert_sent = True
            comment.save()
        if not len(comments_to_alert_for):
            continue # No new comments - no need to alert
        # Collect all users to receive an alert email
        all_emails = []
        for user in all_users.iterator():
            if user.is_superuser or not user.allow_alerts:
                continue
            if event.eligible_for_actions(user):
                # Ensure that there are comments for that event
                # from users other than the current one.
                # If there are, break the `for`, resulting in
                # appending to `all_emails`, if there are not,
                # the `else` of the `for` is executed, resulting
                # in `continue` for the outer `for` and skipping to
                # the next user.
                for comment in comments_to_alert_for:
                    if comment.user.id != user.id:
                        break
                else:
                    continue
                all_emails.append(user.email)
        context = {
            'event_link': f'{DOMAIN_NAME}/event?id={event.id}',
            'event_name': event.name,
            'comments': comments_to_alert_for
        }
        email.send_email(all_emails,
                         f'New comments - "{event.name}"',
                         render_to_string('emails/new_comments.html', context))

@shared_task(name="archive_events")
def archive_events(*args, **kwargs):
    """Archive passed events."""
    all_events = Event.objects.all().filter(archived=False)
    for event in all_events.iterator():
        if timezone.now() - event.date > EVENT_CREATOR_SPAN:
            event.archived = True
            event.save()
            # If event has selected wishlist items - deactivate them
            for item in event.wishlist_item.all():
                item.active = False
                item.save()

@shared_task(name="participants_wanted")
def send_email_participants_wanted(event):
    """Broadcast email, asking for more participants."""
    all_users = CustomUser.objects.all()
    all_emails = []
    for user in all_users:
        if event.celebrant and user.pk == event.celebrant.pk:
            continue
        if user.pk == event.host.pk:
            continue
        if user in event.participants.all():
            continue
        all_emails.append(user.email)
    if not all_emails:
        return False
    context = {
        'event_link': f'{DOMAIN_NAME}/event?id={event.id}',
        'event_name': event.name
    }
    email.send_email(all_emails,
                        f'Participants wanted - "{event.name}"',
                        render_to_string('emails/participants_wanted.html', context))
