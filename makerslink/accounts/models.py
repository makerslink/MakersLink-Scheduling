import logging
logger = logging.getLogger(__name__)

from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    
    objects = UserManager()

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_registration_complete = models.BooleanField(default=False)

    def get_full_name(self):
        return self.email
    def get_short_name(self):
        return self.email
    
@receiver(pre_save, sender=User)
def finish_registration(sender, **kwargs):
    if not sender.is_registration_complete:
        sender.is_active = False
        sender.is_registration_complete = True
