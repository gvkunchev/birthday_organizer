import datetime

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from .model_managers import UserManager


def validate_strypes(value):
    if not value.endswith('ict.eu'):
        raise ValidationError(
            "Only Strypes employees are allowed (*@ict.eu)",
            params={"value": value},
        )


class Theme(models.TextChoices):
    STRYPES = 'STR', 'Strypes'
    MINTMILK = 'MMM', 'Mint Milk'
    PURPLEHAZE = 'PRH', 'Purple haze'
    CAPRESE = 'CPR', 'Caprese'
    NIGHTVISION = 'NTV', 'Night vision'


class CustomUser(AbstractUser):
    username = None

    theme = models.CharField(
        max_length=3,
        choices=Theme.choices,
        default=Theme.STRYPES,
    )

    email = models.EmailField(unique=True, validators=[validate_strypes])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateTimeField(auto_now=False, editable=True)
    iban = models.CharField(max_length=100, blank=True)
    revolut = models.CharField(max_length=100, blank=True)
    allow_alerts = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)
    
    @property
    def revolut_clean(self):
        return self.revolut.replace('@', '')

    @property
    def form_birthdate(self):
        return self.birthdate.strftime("%Y-%m-%d")

    @property
    def human_birthday(self):
        return self.birthdate.strftime("%d %B %Y")

    def get_events_involved_in(self):
        '''Get list of events the user is part of.'''
        participating = self.participated_events.filter(archived=False)
        hosting = self.hosted_events.filter(archived=False)
        return {
            'participated_events': participating.difference(hosting),
            'hosted_events': hosting
        }

    def get_eligible_events(self, all):
        '''Get all eligible events for a user based on all events as input.'''
        participating = self.participated_events.filter(archived=False)
        hosting = self.hosted_events.filter(archived=False)
        return {
            'participated_events': participating.difference(hosting),
            'hosted_events': hosting,
            'other_events': all.difference(participating).difference(hosting)
        }

    def get_all_other_users(self):
        '''Get all users except self.'''
        return {'users': CustomUser.objects.all().exclude(id=self.id).exclude(is_superuser=True).exclude(is_active=False)}

    def get_next_birthday(self):
        '''Get the date for the next birthday.'''
        next_birthday = self.birthdate.replace(year=datetime.datetime.now().year)
        # If this year's birthday already passed, get next year's one
        if next_birthday - timezone.now() < datetime.timedelta():
            next_birthday = self.birthdate.replace(year=timezone.now().year + 1)
        return next_birthday
    
    def get_overview(self, events):
        """Get overview items for the home page."""
        # Events is passed as argument, because base.models imports from here
        # and thus base.models.Event cannot be imported here - circular import.
        LIMIT = 12 # Show only the most recent items
        overview_list = []
        for event in sorted(events, key=lambda x: x.date, reverse=True):
            self_participates = event.participants.filter(id=self.id)
            # New events you are not part of
            if event.host != self and not self_participates:
                    if self != event.celebrant:
                        overview_list.append({
                            'name': event.name,
                            'id': event.id,
                            'type': 'new'
                        })
            # Events your are part of without a host yet
            if event.host is None and self_participates:
                overview_list.append({
                    'name': event.name,
                    'id': event.id,
                    'type': 'no_host'
                })
            # Events you are part of (or you are a host) without payment
            if event.host and (event.host.id == self.id or self_participates):
                for payment in event.payments.iterator():
                    if self.payments.filter(id=payment.id):
                        break
                else:
                    overview_list.append({
                        'name': event.name,
                        'id': event.id,
                        'type': 'payment_missing'
                    })
            # Events you are host of with unconfirmed payments
            if event.host and (event.host.id == self.id):
                for payment in event.payments.iterator():
                    if not payment.confirmed and payment.user is not self:
                        overview_list.append({
                            'name': event.name,
                            'id': event.id,
                            'type': 'confirmation_missing'
                        })
                        break
            if len(overview_list) >= LIMIT:
                break
        return {'overview_tasks': overview_list}

    def get_wishlist_items(self):
        """Get all wishlist items."""
        return self.wishlistitem_set.all()
