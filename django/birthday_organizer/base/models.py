from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser
from django.utils import timezone

from wishlists.models import WishlistItem

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=False, editable=True)
    participants = models.ManyToManyField(CustomUser,
                                          related_name='participated_events')
    celebrant = models.ForeignKey(CustomUser, models.SET_NULL,
                                  blank=True, null=True, related_name='+')
    host = models.ForeignKey(CustomUser, models.SET_NULL,
                             blank=True, null=True,
                             related_name='hosted_events')
    archived = models.BooleanField(default=False)
    wishlist_item = models.ManyToManyField(WishlistItem, blank=True)

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
    
    def get_email_recepients(self):
        """Get all users that share a circle with the celebrant."""
        if not self.celebrant:
            return list(CustomUser.objects.all())
        users = []
        for circle in self.celebrant.circles.all():
            for user in circle.users.all():
                if user.pk != self.celebrant.pk:
                    if user not in users:
                        users.append(user)
        return users

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
                        'added_by_host': payment.added_by_host,
                        'id': payment.id,
                        'user': payment.user
                    })
        return payments

    def eligible_for_actions(self, user):
        '''Check if a user is eligible to make actions for the event.'''
        return not self.archived and (user == self.host or user in self.participants.all())

    @property
    def sorted_comments(self):
        '''List of comments sorted new-old.'''
        return sorted(self.comments.all(), reverse=True,
                      key=lambda x: x.timestamp)


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, models.CASCADE,
                             blank=True, null=True, related_name='payments')
    amount = models.FloatField(validators=[MinValueValidator(1.0)])
    event = models.ForeignKey(Event, models.CASCADE, blank=True, null=True,
                              related_name='payments')
    confirmed = models.BooleanField(default=False)
    added_by_host = models.BooleanField(default=False)

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
    user = models.ForeignKey(CustomUser, models.CASCADE,
                             blank=True, null=True, related_name='comments')
    event = models.ForeignKey(Event, models.CASCADE, blank=True, null=True,
                              related_name='comments')
    timestamp = models.DateTimeField(default=timezone.now, editable=True)
    content = models.CharField(max_length=10000)
    alert_sent = models.BooleanField(default=False)
    likes = models.ManyToManyField(CustomUser, blank=True, related_name='comment_likes')

    @property
    def human_timestamp(self):
        '''Return timestamp in human readable format.'''
        return timezone.localtime(self.timestamp).strftime("%Y/%m/%d %H:%M:%S")
