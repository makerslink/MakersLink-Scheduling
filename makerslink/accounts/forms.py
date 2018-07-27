import logging
logger = logging.getLogger(__name__)

from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', ]
