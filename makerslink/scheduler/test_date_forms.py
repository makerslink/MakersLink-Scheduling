"""
Staff forms with date fields. django-bootstrap-datepicker-plus 3.0.5 used the
{% ifnotequal %} tag that Django 4.0 removed, so every page rendering one of
these widgets was a 500. The model clean() methods also compared dates
without checking they were set, and allowed start == end, which the database
constraints then refused with an IntegrityError.
"""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .models import Event, SchedulingPeriod, SchedulingRuleExclusion


class DateFormTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create(email="staff@example.com", slackId="staff",
                                         is_active=True, is_staff=True,
                                         is_registration_complete=True)
        self.client.force_login(self.staff)
        today = timezone.localdate()
        self.period = SchedulingPeriod.objects.create(
            start=today - datetime.timedelta(days=30), end=today + datetime.timedelta(days=150))
        self.event = Event.objects.get(name="Måndagar")
        self.exclusion = SchedulingRuleExclusion.objects.create(
            excluded_date=today + datetime.timedelta(days=10), description="Stängt")

    def test_date_picker_pages_render(self):
        pages = [reverse("event-create"), reverse("event-update", args=[self.event.pk]),
                 reverse("period-create"), reverse("period-update", args=[self.period.pk]),
                 reverse("ruleexclusion-create"),
                 reverse("ruleexclusion-update", args=[self.exclusion.pk])]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                self.assertIn('&quot;locale&quot;:&quot;sv&quot;', response.content.decode())

    def event_data(self, start, end):
        return {"name": "Torsdag", "description": "Öppet", "template": self.event.template_id,
                "start": start, "end": end, "repeat_end": "", "rule": ""}

    def test_event_with_empty_dates_is_a_form_error(self):
        response = self.client.post(reverse("event-create"), self.event_data("", ""))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["start"])

    def test_event_starting_when_it_ends_is_a_form_error(self):
        when = (timezone.localtime() + datetime.timedelta(days=5)).strftime("%Y-%m-%d 17:00:00")
        response = self.client.post(reverse("event-create"), self.event_data(when, when))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Start must be before end", response.context["form"].errors["start"])

    def test_event_is_created(self):
        day = (timezone.localtime() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        response = self.client.post(reverse("event-create"),
                                    self.event_data(f"{day} 17:00:00", f"{day} 21:00:00"))
        self.assertEqual(response.status_code, 302)
        created = Event.objects.get(name="Torsdag")
        self.assertEqual(timezone.localtime(created.start).hour, 17)

    def period_data(self, start, end):
        return {"start": start, "end": end, "num_required_events": 6,
                "participant_key_string": ""}

    def test_period_with_empty_dates_is_a_form_error(self):
        response = self.client.post(reverse("period-create"), self.period_data("", ""))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["start"])

    def test_period_starting_when_it_ends_is_a_form_error(self):
        response = self.client.post(reverse("period-create"),
                                    self.period_data("2027-09-01", "2027-09-01"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Start must be before end", response.context["form"].errors["start"])
