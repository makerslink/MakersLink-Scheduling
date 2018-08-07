import logging
logger = logging.getLogger(__name__)

from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class RegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', 'slackId']

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'slackId')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'slackId')
