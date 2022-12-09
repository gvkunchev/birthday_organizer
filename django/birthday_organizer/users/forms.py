from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


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
