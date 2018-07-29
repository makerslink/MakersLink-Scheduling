import logging
logger = logging.getLogger(__name__)

from .models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=User)
def finish_registration(sender, instance, *args, **kwargs):
    # This is called 3 times....
    # First at creation with id = None and _password set
    # Second when email was sent with id set and _password = None
    # This when password is set from email with id set and _password set
    # This is when we want to inactivate the user until approval.
    if not instance.is_registration_complete and instance.id and instance._password:
        instance.is_active = False
        instance.is_registration_complete = True
        instance.save()
        
        
