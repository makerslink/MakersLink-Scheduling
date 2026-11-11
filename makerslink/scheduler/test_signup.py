"""
Tests for the host signup page (/scheduler/ and /scheduler/signup).

The page renders one hidden-field form per bookable slot: existing
EventInstance rows first, then slots generated from the Event rules that do
not exist in the database yet. These tests drive it the way a browser does,
by posting back the fields the page rendered.
"""
import datetime
import html
import re

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .models import Event, EventInstance, EventTemplate, SchedulingPeriod


def make_user(email, slack, **extra):
    user = User.objects.create(email=email, slackId=slack, is_active=True,
                               is_registration_complete=True, **extra)
    user.set_password("Long-enough-pw-1")
    user.save()
    return user


def formset_data(page):
    """The POST data a browser would send back for the rendered signup page."""
    data = {}
    for tag in re.findall(r"<input[^>]*>", page):
        name = re.search(r'name="([^"]+)"', tag)
        if not name:
            continue
        kind = re.search(r'type="([^"]+)"', tag)
        if kind and kind.group(1) == "checkbox":
            if "checked" in tag:
                data[name.group(1)] = "on"
            continue
        value = re.search(r'value="([^"]*)"', tag)
        data[name.group(1)] = html.unescape(value.group(1)) if value else ""
    return data


def generated_slots(data):
    """Form indexes of slots that do not exist in the database yet."""
    initial = int(data["form-INITIAL_FORMS"])
    total = int(data["form-TOTAL_FORMS"])
    return [i for i in range(initial, total) if f"form-{i}-event" in data]


def slot_times(data, index):
    parse = lambda value: timezone.make_aware(
        datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    return parse(data[f"form-{index}-start"]), parse(data[f"form-{index}-end"])


class SignupTestCase(TestCase):
    """
    Migration 0002 seeds a weekly "Måndagar" event; a period covering the next
    months makes its Mondays show up as generated slots.
    """

    def setUp(self):
        today = timezone.localdate()
        self.period = SchedulingPeriod.objects.create(
            start=today - datetime.timedelta(days=30),
            end=today + datetime.timedelta(days=150))
        self.event = Event.objects.get(name="Måndagar")
        self.member = make_user("member@example.com", "member")
        self.other = make_user("other@example.com", "other")
        self.client.force_login(self.member)

    def signup_page(self):
        return formset_data(self.client.get(reverse("index")).content.decode())

    def book_for_other(self, data, index):
        """Simulate someone else booking a slot after this page was rendered."""
        start, end = slot_times(data, index)
        return EventInstance.objects.create(
            event=self.event, start=start, end=end, status=1, host=self.other,
            period=self.period)


class TakenMessageTests(SignupTestCase):
    """
    The "not taken" message used to be built by string concatenation from
    POSTed values and rendered with |safe.
    """

    def test_posted_title_is_not_rendered_as_html(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        self.book_for_other(data, index)
        data[f"form-{index}-perform_action"] = "on"
        data[f"form-{index}-title"] = "<img src=x onerror=alert(1)>"

        page = self.client.post(reverse("index"), data, follow=True).content.decode()

        self.assertIn("were not taken", page)
        self.assertNotIn("<img src=x onerror=alert(1)>", page)

    def test_template_title_is_escaped_once(self):
        EventTemplate.objects.filter(pk=self.event.template_id).update(title="Öppet & fika")
        data = self.signup_page()
        index = generated_slots(data)[0]
        self.book_for_other(data, index)
        data[f"form-{index}-perform_action"] = "on"

        page = self.client.post(reverse("index"), data, follow=True).content.decode()
        message = page.split("were not taken", 1)[1].split("</table>", 1)[0]

        self.assertIn("<td>Öppet &amp; fika</td>", message)
        self.assertNotIn("&amp;amp;", message)
