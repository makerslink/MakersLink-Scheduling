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

from unittest import mock

from django.db import IntegrityError, connection, transaction
from django.test import TestCase, TransactionTestCase
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


class HiddenFieldTrustTests(SignupTestCase):
    """
    Start, end, status, event and period travel as hidden fields. The server
    used to save whatever came back, so any member could move, invent or
    re-point a slot, and the change was pushed to the public calendar.
    """

    def free_instance(self, data, index):
        start, end = slot_times(data, index)
        return EventInstance.objects.create(
            event=self.event, start=start, end=end, status=0, period=self.period)

    def row_for(self, data, instance):
        return next(i for i in range(int(data["form-TOTAL_FORMS"]))
                    if data.get(f"form-{i}-id") == str(instance.pk))

    def test_generated_slot_is_booked_from_server_values(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        start, end = slot_times(data, index)
        data[f"form-{index}-perform_action"] = "on"
        data[f"form-{index}-period"] = ""
        data[f"form-{index}-status"] = "2"

        self.client.post(reverse("index"), data)

        booked = EventInstance.objects.get(event=self.event, start=start, end=end)
        self.assertEqual((booked.status, booked.host, booked.period), (1, self.member, self.period))

    def test_existing_slot_cannot_be_moved(self):
        free = self.free_instance(self.signup_page(), generated_slots(self.signup_page())[0])
        data = self.signup_page()
        index = self.row_for(data, free)
        data[f"form-{index}-perform_action"] = "on"
        data[f"form-{index}-start"] = "2031-01-01 03:00:00"
        data[f"form-{index}-end"] = "2031-01-01 04:00:00"

        self.client.post(reverse("index"), data)

        moved = EventInstance.objects.get(pk=free.pk)
        self.assertEqual((moved.start, moved.end), (free.start, free.end))
        self.assertEqual((moved.status, moved.host), (1, self.member))

    def test_slot_cannot_be_invented(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        data[f"form-{index}-perform_action"] = "on"
        data[f"form-{index}-start"] = "2030-06-06 01:00:00"
        data[f"form-{index}-end"] = "2030-06-06 23:00:00"

        self.client.post(reverse("index"), data)

        self.assertFalse(EventInstance.objects.exists())

    def test_slot_cannot_be_pointed_at_another_event(self):
        other_event = Event.objects.create(
            name="Annat", template=self.event.template,
            start=timezone.now() + datetime.timedelta(days=400),
            end=timezone.now() + datetime.timedelta(days=400, hours=2))
        data = self.signup_page()
        index = generated_slots(data)[0]
        data[f"form-{index}-perform_action"] = "on"
        data[f"form-{index}-event"] = str(other_event.pk)

        self.client.post(reverse("index"), data)

        self.assertFalse(EventInstance.objects.exists())

    def test_own_slot_can_be_released(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        data[f"form-{index}-perform_action"] = "on"
        self.client.post(reverse("index"), data)
        mine = EventInstance.objects.get()

        data = self.signup_page()
        data.pop(f"form-{self.row_for(data, mine)}-perform_action")
        self.client.post(reverse("index"), data)

        mine.refresh_from_db()
        self.assertEqual((mine.status, mine.host), (-1, self.member))

    def test_someone_elses_slot_cannot_be_released_by_swapping_the_id(self):
        data = self.signup_page()
        first, second = generated_slots(data)[:2]
        data[f"form-{first}-perform_action"] = "on"
        self.client.post(reverse("index"), data)
        mine = EventInstance.objects.get()
        theirs = self.book_for_other(data, second)

        data = self.signup_page()
        index = self.row_for(data, mine)
        data[f"form-{index}-id"] = str(theirs.pk)
        data.pop(f"form-{index}-perform_action")
        self.client.post(reverse("index"), data)

        theirs.refresh_from_db()
        self.assertEqual((theirs.status, theirs.host), (1, self.other))

    def test_stale_page_does_not_take_over_a_booked_slot(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        theirs = self.book_for_other(data, index)
        data[f"form-{index}-perform_action"] = "on"

        page = self.client.post(reverse("index"), data, follow=True).content.decode()

        theirs.refresh_from_db()
        self.assertEqual((theirs.status, theirs.host), (1, self.other))
        self.assertIn("were not taken", page)

    def test_stale_page_does_not_take_over_an_existing_free_slot_booked_since(self):
        data = self.signup_page()
        free = self.free_instance(data, generated_slots(data)[0])
        data = self.signup_page()
        index = self.row_for(data, free)
        EventInstance.objects.filter(pk=free.pk).update(status=1, host=self.other)
        data[f"form-{index}-perform_action"] = "on"

        self.client.post(reverse("index"), data)

        free.refresh_from_db()
        self.assertEqual((free.status, free.host), (1, self.other))


class SerializedBookingTests(SignupTestCase):
    """
    Two members ticking the same slot used to be separated only by the
    unique constraint, whose handler was a Python 2 pre_save signal that
    raised NameError.
    """

    def test_sqlite_takes_the_write_lock_up_front(self):
        self.assertEqual(connection.settings_dict["OPTIONS"]["transaction_mode"], "IMMEDIATE")

    def test_duplicate_slot_hits_the_database_constraint(self):
        data = self.signup_page()
        theirs = self.book_for_other(data, generated_slots(data)[0])
        with self.assertRaises(IntegrityError), transaction.atomic():
            EventInstance.objects.create(event=theirs.event, start=theirs.start, end=theirs.end)

    def test_slot_created_between_read_and_write_is_reported_not_a_500(self):
        data = self.signup_page()
        index = generated_slots(data)[0]
        theirs = self.book_for_other(data, index)
        data[f"form-{index}-perform_action"] = "on"

        # Pretend the locked read ran just before the other booking committed.
        with mock.patch("scheduler.views._slot_in_db", return_value=None):
            page = self.client.post(reverse("index"), data, follow=True).content.decode()

        theirs.refresh_from_db()
        self.assertEqual((theirs.status, theirs.host), (1, self.other))
        self.assertIn("were not taken", page)


class BookingTransactionTests(TransactionTestCase):
    """Outside TestCase's wrapping transaction, so the view's own atomic block is visible."""

    def test_each_booking_is_saved_inside_a_transaction(self):
        today = timezone.localdate()
        SchedulingPeriod.objects.create(start=today - datetime.timedelta(days=30),
                                        end=today + datetime.timedelta(days=150))
        member = make_user("member@example.com", "member")
        self.client.force_login(member)
        data = formset_data(self.client.get(reverse("index")).content.decode())
        data[f"form-{generated_slots(data)[0]}-perform_action"] = "on"
        seen = []
        original_save = EventInstance.save

        def recording_save(instance, *args, **kwargs):
            seen.append(connection.in_atomic_block)
            return original_save(instance, *args, **kwargs)

        with mock.patch.object(EventInstance, "save", recording_save):
            self.client.post(reverse("index"), data)

        self.assertEqual(seen, [True])
