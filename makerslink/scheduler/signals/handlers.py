import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.db.models import signals
from django.utils.text import get_text_list
from django.db import connection, IntegrityError
from django.utils.translation import ugettext as _
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from scheduler.models import EventInstance
from django.apps import apps
import datetime
from scheduler import tasks

# From django-tools, slightly modified
@receiver(pre_save, sender=EventInstance)
def check_unique_together(sender, **kwargs):
    """
    Check models unique_together manually. Django enforced unique together only the database level, but
    some databases (e.g. SQLite) doesn't support this.

    usage:
        from django.db.models import signals
        signals.pre_save.connect(check_unique_together, sender=MyModelClass)

    or use auto_add_check_unique_together(), see below
    """
    instance = kwargs["instance"]
    for field_names in sender._meta.unique_together:
        model_kwargs = {}
        for field_name in field_names:
            try:
                data = getattr(instance, field_name)
            except FieldDoesNotExist:
                # e.g.: a missing field, which is however necessary.
                # The real exception on model creation should be raised.
                continue
            model_kwargs[field_name] = data

        query_set = sender.objects.filter(**model_kwargs)
        if instance.pk != None:
            # Exclude the instance if it was saved in the past
            query_set = query_set.exclude(pk=instance.pk)

        count = query_set.count()
        if count > 0:
            field_names = get_text_list(field_names, _('and'))
            msg = _(u"%(model_name)s with this %(field_names)s already exists.") % {
                'model_name': unicode(instance.__class__.__name__),
                'field_names': unicode(field_names)
            }
            raise IntegrityError(msg)


def auto_add_check_unique_together(model_class):
    """
    Add only the signal handler check_unique_together, if a database without UNIQUE support is used.
    """
    if settings.DATABASE_ENGINE in ('sqlite3',):  # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        signals.pre_save.connect(check_unique_together, sender=model_class)

@receiver(post_save, sender=EventInstance)
def create_statistics_row_after_event(sender, instance, created, **kwargs):
    # If statistics-app is installed we will create a task to update that after the event is done only if this was a creation event
    if apps.is_installed('schedulerstatistics') and created:
        logger.warning('Statistics app is installed and something should happen since this EventInstance was created')

@receiver(post_save, sender=EventInstance)
def cancel_event_before_start(sender, instance, created, **kwargs):
    # Create a scheduled task that handles checking if event should be cancelled and give it them ETA for cancelling.
    cancellation_time = instance.start - datetime.timedelta(hours=settings.SCHEDULER_CALENDAR_TIMELIMIT)
    tasks.create_cancellation_task(instance.id, cancellation_time)
