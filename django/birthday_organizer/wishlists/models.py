from django.db import models

from users.models import CustomUser


class WishlistItem(models.Model):

    class Meta:
        ordering = ('-active', 'title')

    title = models.CharField(max_length=300)
    description = models.CharField(max_length=1000, default='',
                                   blank=True, null=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.full_name} - {self.title}"