from django.db import models
from django.contrib.auth.models import AbstractUser

from .model_managers import UserManager

class Theme(models.TextChoices):
    STRYPES = 'STR', 'Strypes'
    MINTMILK = 'MMM', 'Mint Milk'
    PURPLEHAZE = 'PRH', 'Purple haze'
    CAPRESE = 'CPR', 'Caprese'


class CustomUser(AbstractUser):
    username = None

    theme = models.CharField(
        max_length=3,
        choices=Theme.choices,
        default=Theme.STRYPES,
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateTimeField(auto_now=False, editable=True)
    iban = models.CharField(max_length=100, blank=True)
    revolut = models.CharField(max_length=100, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def form_birthdate(self):
        return self.birthdate.strftime("%Y-%m-%d")

    @property
    def human_birthday(self):
        return self.birthdate.strftime("%d %B %Y")

    def get_events_involved_in(self):
        '''Get list of events the user is part of.'''
        participating = self.participated_events.all()
        hosting = self.hosted_events.all()
        return {
            'participated_events': participating.difference(hosting),
            'hosted_events': hosting
        }

    def get_eligible_events(self, all):
        '''Get all eligible events for a user based on all events as input.'''
        participating = self.participated_events.all()
        hosting = self.hosted_events.all()
        return {
            'participated_events': participating.difference(hosting),
            'hosted_events': hosting,
            'other_events': all.difference(participating).difference(hosting)
        }

    def get_all_other_users(self):
        '''Get all users except self.'''
        return {'users': CustomUser.objects.all().exclude(id=self.id)}
