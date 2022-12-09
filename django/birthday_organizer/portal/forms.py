from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Event, Payment, Comment


class SignUpForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'birthdate',
                  'password1', 'password2', )


class EditPersonalInformationForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'birthdate',
                  'iban', 'revolut', 'theme')


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


class CommentAdminForm(forms.ModelForm):
    content = forms.CharField( widget=forms.Textarea )

    class Meta:
        model = Comment
        fields = ('user', 'event', 'content')


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('user', 'event', 'content')
