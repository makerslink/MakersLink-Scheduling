import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render
from .models import User
from .forms import RegistrationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm

# Create your views here.

class RegistrationView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('register-done')
    model = User

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.set_password(User.objects.make_random_password())
        obj.is_active = True  # PasswordResetForm won't send to inactive users.
        obj.save()

        # This form only requires the "email" field, so will validate.
        reset_form = PasswordResetForm(self.request.POST)
        reset_form.is_valid()  # Must trigger validation
        # Copied from django/contrib/auth/views.py : password_reset
        opts = {
            'use_https': self.request.is_secure(),
            'email_template_name': 'accounts/password_reset_email.html',
            'subject_template_name': 'accounts/verification_subject.txt',
            'request': self.request,
            # 'html_email_template_name': provide an HTML content template if you desire.
        }
        # This form sends the email on save()
        reset_form.save(**opts)
        #logger.warning("get sucess url:"+self.get_success_url())
        
        #return redirect(self.get_success_url())
        
        
        return CreateView.form_valid(self, form)

