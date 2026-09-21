import datetime

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User

from .models import (Event, EventInstance, EventTemplate, MISSING_RELATION_TITLE,
                     SchedulingCalendar, SchedulingPeriod)


def make_staff(email="staff@example.com", slack="staff"):
    user = User.objects.create(email=email, slackId=slack, is_active=True,
                               is_staff=True, is_registration_complete=True)
    user.set_password("password")
    user.save()
    return user


class ProtectedRelationTests(TestCase):
    """
    Deleting a calendar or a template used to SET_NULL the rows that depend on
    it, which left EventInstance unable to render its own title and took out
    every page that listed instances. These relations are PROTECT now.
    """

    def setUp(self):
        self.calendar = SchedulingCalendar.objects.create(
            name="cal", google_calendar_id="g", service_account_username="s",
            timezone="Europe/Stockholm")
        self.template = EventTemplate.objects.create(
            name="t", title="Open", num_participants=2,
            calendar=self.calendar, synchronize=False)
        today = timezone.now().date()
        self.period = SchedulingPeriod.objects.create(
            start=today - datetime.timedelta(days=30),
            end=today + datetime.timedelta(days=120))
        self.event = Event.objects.create(
            name="e", template=self.template,
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=3))
        self.instance = EventInstance.objects.create(
            event=self.event, start=self.event.start, end=self.event.end,
            status=0, period=self.period)

    def test_deleting_a_used_template_is_refused(self):
        with self.assertRaises(ProtectedError):
            self.template.delete()
        self.event.refresh_from_db()
        self.assertEqual(self.event.template, self.template)

    def test_deleting_a_used_calendar_is_refused(self):
        with self.assertRaises(ProtectedError):
            self.calendar.delete()
        self.template.refresh_from_db()
        self.assertEqual(self.template.calendar, self.calendar)

    def test_deleting_a_used_event_is_refused(self):
        with self.assertRaises(ProtectedError):
            self.event.delete()
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.event, self.event)

    def test_unused_template_can_still_be_deleted(self):
        spare = EventTemplate.objects.create(
            name="spare", title="Spare", calendar=self.calendar, synchronize=False)
        spare.delete()
        self.assertFalse(EventTemplate.objects.filter(name="spare").exists())


class ProtectedDeleteViewTests(TestCase):
    """
    The database refusal must reach the user as an explanation, not a 500.
    """

    def setUp(self):
        make_staff()
        self.client.login(email="staff@example.com", password="password")
        self.calendar = SchedulingCalendar.objects.create(
            name="Huvudkalender", google_calendar_id="g",
            service_account_username="s", timezone="Europe/Stockholm")
        self.template = EventTemplate.objects.create(
            name="Kvallsoppet", title="Open", calendar=self.calendar,
            synchronize=False)
        self.event = Event.objects.create(
            name="Tisdagskvall", template=self.template,
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=3))

    def test_deleting_used_template_renders_the_blockers(self):
        response = self.client.post(
            '/scheduler/template/{}/delete'.format(self.template.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cannot delete this template")
        self.assertContains(response, "Tisdagskvall")
        self.assertEqual(response.context['protected_count'], 1)
        self.assertTrue(EventTemplate.objects.filter(pk=self.template.pk).exists())

    def test_deleting_used_calendar_renders_the_blockers(self):
        response = self.client.post(
            '/scheduler/calendar/{}/delete'.format(self.calendar.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cannot delete this calendar")
        self.assertContains(response, "Kvallsoppet")
        self.assertTrue(SchedulingCalendar.objects.filter(pk=self.calendar.pk).exists())

    def test_deleting_an_unused_template_still_works(self):
        spare = EventTemplate.objects.create(
            name="Oanvand", title="Spare", calendar=self.calendar, synchronize=False)
        response = self.client.post('/scheduler/template/{}/delete'.format(spare.pk))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(EventTemplate.objects.filter(pk=spare.pk).exists())


class SynchronizeWithoutCalendarTests(TestCase):
    """
    synchronize=True with no calendar used to fail as an AttributeError inside
    EventInstance.save(). It is now rejected at validation time, and the
    remaining runtime path names the template instead of the missing attribute.
    """

    def test_clean_rejects_synchronize_without_calendar(self):
        template = EventTemplate(name="t", title="Open", synchronize=True, calendar=None)
        with self.assertRaises(ValidationError) as caught:
            template.clean()
        self.assertIn('calendar', caught.exception.message_dict)

    def test_clean_allows_no_calendar_when_not_synchronizing(self):
        EventTemplate(name="t", title="Open", synchronize=False, calendar=None).clean()

    def test_runtime_error_names_the_template(self):
        template = EventTemplate.objects.create(
            name="Trasig", title="Open", synchronize=True, calendar=None)
        with self.assertRaises(ValueError) as caught:
            template.createEventEntry(None, timezone.now(), timezone.now(), 0)
        self.assertIn("Trasig", str(caught.exception))


class OrphanedRowTests(TestCase):
    """
    Databases written before PROTECT still hold rows whose template or event was
    nulled. Those rows must stay loadable so they can be repaired or deleted.
    """

    def setUp(self):
        make_staff()
        self.client.login(email="staff@example.com", password="password")
        calendar = SchedulingCalendar.objects.create(
            name="cal", google_calendar_id="g", service_account_username="s",
            timezone="Europe/Stockholm")
        template = EventTemplate.objects.create(
            name="t", title="Open", calendar=calendar, synchronize=False)
        today = timezone.now().date()
        period = SchedulingPeriod.objects.create(
            start=today - datetime.timedelta(days=30),
            end=today + datetime.timedelta(days=120))
        event = Event.objects.create(
            name="e", template=template,
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=3))
        self.instance = EventInstance.objects.create(
            event=event, start=event.start, end=event.end, status=1,
            host=make_staff("host@example.com", "host"), period=period)
        # Reproduce the legacy state that SET_NULL used to produce.
        Event.objects.filter(pk=event.pk).update(template=None)
        self.orphan_event = Event.objects.get(pk=event.pk)
        self.instance.refresh_from_db()

    def test_title_falls_back_instead_of_raising(self):
        self.assertEqual(self.instance.title, MISSING_RELATION_TITLE)
        self.assertIsNone(self.instance.template)
        self.assertIsNone(self.instance.header)
        self.assertIsNone(self.instance.body)
        self.assertEqual(self.instance.max_num_participants, 0)
        self.assertEqual(self.orphan_event.max_num_participants, 0)

    def test_str_and_as_dict_do_not_raise(self):
        self.assertIn(MISSING_RELATION_TITLE, str(self.instance))
        self.assertEqual(self.instance.as_dict()['event'], self.orphan_event.pk)

    def test_orphaned_instance_can_still_be_saved_and_deleted(self):
        self.instance.status = 2
        self.instance.save()
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, 2)
        self.instance.delete()
        self.assertFalse(EventInstance.objects.filter(pk=self.instance.pk).exists())

    def test_instance_listing_pages_still_load(self):
        for url in ['/scheduler/eventinstances-admin', '/scheduler/joinEvent']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_admin_changelist_still_loads(self):
        admin = make_staff("su@example.com", "su")
        admin.is_superuser = True
        admin.save()
        self.client.login(email="su@example.com", password="password")
        response = self.client.get('/admin/scheduler/eventinstance/')
        self.assertEqual(response.status_code, 200)


class HostlessInstanceTests(TestCase):
    """
    host is nullable and is None for every unbooked instance, so display_host()
    took out the whole admin changelist as soon as one free slot existed.
    """

    def setUp(self):
        calendar = SchedulingCalendar.objects.create(
            name="cal", google_calendar_id="g", service_account_username="s",
            timezone="Europe/Stockholm")
        template = EventTemplate.objects.create(
            name="t", title="Open", calendar=calendar, synchronize=False)
        today = timezone.now().date()
        self.period = SchedulingPeriod.objects.create(
            start=today - datetime.timedelta(days=30),
            end=today + datetime.timedelta(days=120))
        self.event = Event.objects.create(
            name="e", template=template,
            start=timezone.now() + datetime.timedelta(days=1),
            end=timezone.now() + datetime.timedelta(days=1, hours=3))
        self.free = EventInstance.objects.create(
            event=self.event, start=self.event.start, end=self.event.end,
            status=0, host=None, period=self.period)

    def test_display_host_is_blank_without_a_host(self):
        self.assertIsNone(self.free.display_host())

    def test_display_host_returns_the_email_when_hosted(self):
        self.free.host = make_staff("host@example.com", "host")
        self.assertEqual(self.free.display_host(), "host@example.com")

    def test_admin_changelist_loads_with_a_free_instance(self):
        admin = make_staff("su@example.com", "su")
        admin.is_superuser = True
        admin.save()
        self.client.login(email="su@example.com", password="password")
        response = self.client.get('/admin/scheduler/eventinstance/')
        self.assertEqual(response.status_code, 200)
