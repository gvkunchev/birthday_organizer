from django import forms
from django.core.exceptions import ValidationError
from base.models import Event, Payment, Comment


class AddEventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ('name', 'date', 'participants', 'celebrant', 'host')

    def clean(self):
        """Make sure the celebrant is not part of the event."""
        if 'celebrant' in self.cleaned_data:
            celebrant = self.cleaned_data['celebrant']
            if 'host' in self.cleaned_data:
                if celebrant and celebrant == self.cleaned_data['host']:
                    raise ValidationError({'host':
                                           "The celebrant can't be a host."})
            if 'participants' in self.cleaned_data:
                if celebrant in self.cleaned_data['participants']:
                    raise ValidationError({'participants':
                                           "The celebrant can't participate."})
        return self.cleaned_data


class AddPaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ('event', 'user', 'amount', 'confirmed')


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('user', 'event', 'content')
