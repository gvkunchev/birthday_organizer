from django import forms
from django.core.exceptions import ValidationError

from .models import WishlistItem


class WishlistItemForm(forms.ModelForm):

    class Meta:
        model = WishlistItem
        fields = ('title', 'description', 'owner')
