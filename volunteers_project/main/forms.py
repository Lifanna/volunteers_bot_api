from django import forms
from . import models
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = models.CustomUser
        fields = (
            'username',
            'email',
            'date_of_birth',
            'first_name',
            'last_name',
            'phone_number',
        )


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.CustomUser
        fields = (
            'username',
            'email',
            'date_of_birth',
            'first_name',
            'last_name',
            'phone_number',
        )
