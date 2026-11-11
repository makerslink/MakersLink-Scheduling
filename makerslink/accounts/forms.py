import logging
logger = logging.getLogger(__name__)

from django import forms
from .models import User
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'slackId')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'slackId', 'is_active', 'is_staff', 'is_registration_complete',  'is_superuser')


class InviteForm(forms.Form):
    email = forms.EmailField(label="Email address")


class InviteAcceptForm(SetPasswordForm):
    """Lets an invited member choose their Slack name and password."""
    slackId = forms.CharField(label="Slacknamn", max_length=100, validators=[User.slackIdValid],
                              help_text="Ditt namn på MakersLinks Slack, utan @.")
    field_order = ["slackId", "new_password1", "new_password2"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["slackId"].initial = user.slackId

    def clean_slackId(self):
        slack = self.cleaned_data["slackId"].strip()
        if User.objects.filter(slackId__iexact=slack).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Det slacknamnet används redan av ett annat konto.")
        return slack

    def save(self, commit=True):
        self.user.slackId = self.cleaned_data["slackId"]
        self.user.is_active = True
        self.user.is_registration_complete = True
        return super().save(commit)
