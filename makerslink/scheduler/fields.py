import logging
logger = logging.getLogger(__name__)

from django.db import models


class ParticipantKeyField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(ParticipantKeyField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super(ParticipantKeyField, self).get_prep_value(value)
        
        #Make uppercase.
        value = value.upper()
        
        #Sort to make it easier to compare.
        value = ''.join(sorted(value))

        return value
