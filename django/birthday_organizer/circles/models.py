from django.db import models

from base.models import CustomUser


class Circle(models.Model):
    name = models.CharField(max_length=1000)
    users = models.ManyToManyField(CustomUser, blank=True, null=True, related_name='circles')
