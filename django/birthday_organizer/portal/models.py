from django.core.validators import MinValueValidator
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

    def get_eligible_events(self):
        '''Get all eligible events for a user.'''
        participating = self.participated_events.all()
        hosting = self.hosted_events.all()
        all = Event.objects.all().exclude(celebrant=self)
        return {
            'participated_events': participating.difference(hosting),
            'hosted_events': hosting,
            'other_events': all.difference(participating).difference(hosting)
        }

    def get_all_other_users(self):
        '''Get all users except self.'''
        return {'users': CustomUser.objects.all().exclude(id=self.id)}


class Event(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now=False, editable=True)
    participants = models.ManyToManyField(CustomUser,
                                          related_name='participated_events')
    celebrant = models.ForeignKey(CustomUser, models.SET_NULL,
                                  blank=True, null=True, related_name='+')
    host = models.ForeignKey(CustomUser, models.SET_NULL,
                             blank=True, null=True,
                             related_name='hosted_events')

    def __str__(self):
        return self.name

    @property
    def human_date(self):
        return self.date.strftime("%d %B %Y")

    @property
    def year(self):
        return self.date.strftime("%Y")

    @property
    def month(self):
        return self.date.strftime("%m").lstrip('0')

    @property
    def day(self):
        return self.date.strftime("%d").lstrip('0')

    @property
    def date_input(self):
        return self.date.strftime("%Y-%m-%d")

    @property
    def get_total_money(self):
        '''Get total money gathered.'''
        total = 0
        for payment in self.payments.all():
            total += payment.amount
        return total

    @property
    def participants_ids(self):
        return map(lambda x: x.id, self.participants.all())

    def get_all_payments(self):
        '''Get all payments for the event.'''
        payments = {}
        for user in list(self.participants.all()) + [self.host]:
            if user is None:
                continue
            payments[user.id] = []
            for payment in self.payments.all():
                if user == payment.user:
                    payments[user.id].append({
                        'amount': payment.amount,
                        'confirmed': payment.confirmed,
                        'currency': payment.currency,
                        'id': payment.id,
                        'user': payment.user
                    })
        return payments

    def eligible_for_actions(self, user):
        '''Check if a user is eligible to make actions for the event.'''
        return user == self.host or user in self.participants.all()

    @property
    def sorted_comments(self):
        '''List of comments sorted new-old.'''
        return sorted(self.comments.all(), reverse=True,
                      key=lambda x: x.timestamp)


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, models.SET_NULL,
                             blank=True, null=True, related_name='payments')
    amount = models.FloatField(validators=[MinValueValidator(1.0)])
    event = models.ForeignKey(Event, models.SET_NULL, blank=True, null=True,
                              related_name='payments')
    confirmed = models.BooleanField(default=False)

    @staticmethod
    def currency():
        '''Get currency literal.'''
        return 'лв'

    def save(self, *args, **kwargs):
        '''Save model instance.'''
        # All payments from the host are automatically confirmed
        if self.event.host and self.event.host == self.user:
            self.confirmed = True
        super(Payment, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {} by {}'.format(self.event.name, self.amount,
                                      self.user.full_name)

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, models.SET_NULL,
                             blank=True, null=True, related_name='comments')
    event = models.ForeignKey(Event, models.SET_NULL, blank=True, null=True,
                              related_name='comments')
    timestamp = models.DateTimeField(auto_now=False, editable=True,
                                     auto_now_add=True)
    content = models.CharField(max_length=10000)

    @property
    def human_timestamp(self):
        '''Return timestamp in human readable format.'''
        return self.timestamp.strftime("%Y %B %d %H:%M:%S")
