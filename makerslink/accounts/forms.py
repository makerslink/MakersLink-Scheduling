import logging
logger = logging.getLogger(__name__)

from .models import User

class RegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', ]
