from django.conf import settings
from django.test import TestCase

from .models import SchedulingCalendar


class ServiceAccountStorageTests(TestCase):
    def test_keys_are_stored_in_calendar_pk_dir(self):
        storage = SchedulingCalendar._meta.get_field("service_account").storage
        self.assertEqual(storage.location, settings.CALENDAR_PK_DIR)
