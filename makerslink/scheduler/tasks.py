from __future__ import absolute_import, unicode_literals
from celery import shared_task
from scheduler.models import EventInstance

import logging
logger = logging.getLogger(__name__)

@shared_task
def add(x, y):
    return x+y

@shared_task
def create_cancellation_task(id, time):
    logger.warning('EventInstance should be cancelled at some point in time')
    # Schedule the actual cancellation
    cancel_eventinstance.apply_async(args=(id,), eta=time)

@shared_task
def cancel_eventinstance(id):
    logger.warning('EventInstance should now be cancelled')

    eventInstance = EventInstance.get(pk=id)
    eventInstance.status=2
    eventInstance.save()
