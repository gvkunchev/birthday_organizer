from django import forms
from .models import Circle


class AddCircleForm(forms.ModelForm):

    class Meta:
        model = Circle
        fields = ('name', )
