import datetime
import re
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from accounts.tokens import INVITE_VALID_FOR, invite_token_generator
from scheduler.models import SchedulingPeriod

PASSWORD = "Long-enough-pw-1"


def make_user(email, slack, **extra):
    user = User.objects.create(email=email, slackId=slack, is_active=True,
                               is_registration_complete=True, **extra)
    user.set_password(PASSWORD)
    user.save()
    return user


class InviteTestCase(TestCase):
    def setUp(self):
        self.staff = make_user("staff@example.com", "staff", is_staff=True)
        self.client.force_login(self.staff)

    def invite(self, email="new@example.com"):
        mail.outbox = []
        return self.client.post(reverse("invites"), {"email": email}, follow=True)

    def link(self, message=None):
        body = (message or mail.outbox[-1]).body
        return re.search(r"https?://testserver(/accounts/invite/\S+/)", body).group(1)

    def accept(self, link, slack="nykomling", password="Brand-new-pw-77", client=None):
        client = client or self.client_class()
        page = client.get(link, follow=True)
        return client, page, client.post(page.redirect_chain[-1][0] if page.redirect_chain else link, {
            "slackId": slack, "new_password1": password, "new_password2": password}, follow=True)


class InvitePageAccessTests(InviteTestCase):

    def test_only_staff_see_the_page_and_menu_item(self):
        self.assertEqual(self.client.get(reverse("invites")).status_code, 200)
        self.assertIn('href="%s"' % reverse("invites"),
                      self.client.get(reverse("joinEvent")).content.decode())

        member = make_user("member@example.com", "member")
        self.client.force_login(member)
        self.assertEqual(self.client.get(reverse("invites")).status_code, 403)
        self.assertEqual(self.client.post(reverse("invites"), {"email": "x@example.com"}).status_code, 403)
        self.assertNotIn('href="%s"' % reverse("invites"),
                         self.client.get(reverse("joinEvent")).content.decode())
        self.assertFalse(User.objects.filter(email="x@example.com").exists())

        self.client.logout()
        self.assertEqual(self.client.get(reverse("invites")).status_code, 302)


class InviteFlowTests(InviteTestCase):

    def test_invite_creates_an_inactive_account_without_a_password(self):
        page = self.invite().content.decode()

        user = User.objects.get(email="new@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())
        self.assertIsNone(user.slackId)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        self.assertIn("Invite sent to new@example.com", page)
        self.assertIn("new@example.com", page.split("Waiting to be accepted", 1)[1])

    def test_invitee_cannot_log_in_or_reset_a_password_before_accepting(self):
        self.invite()
        mail.outbox = []
        self.assertFalse(self.client_class().login(username="new@example.com", password=""))
        self.client_class().post(reverse("password_reset"), {"email": "new@example.com"})
        self.assertEqual(mail.outbox, [])

    def test_accepting_sets_slack_name_and_password_and_logs_in(self):
        self.invite()
        client, form_page, done = self.accept(self.link())

        self.assertTemplateUsed(form_page, "accounts/invite_accept.html")
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.is_active and user.is_registration_complete)
        self.assertEqual(user.slackId, "nykomling")
        self.assertTrue(user.check_password("Brand-new-pw-77"))
        self.assertEqual(int(client.session["_auth_user_id"]), user.pk)
        self.assertIn("Välkommen", done.content.decode())
        self.assertNotIn("new@example.com", self.client.get(reverse("invites")).content.decode()
                         .split("Waiting to be accepted", 1)[1])

    def test_accepted_member_can_open_the_booking_page(self):
        today = timezone.localdate()
        SchedulingPeriod.objects.create(start=today - datetime.timedelta(days=30),
                                        end=today + datetime.timedelta(days=150))
        self.invite()
        client, _, _ = self.accept(self.link())
        self.assertEqual(client.get(reverse("index")).status_code, 200)

    def test_link_works_only_once(self):
        self.invite()
        link = self.link()
        self.accept(link)
        _, again, _ = self.accept(link, slack="someone-else")
        self.assertFalse(again.context["validlink"])
        self.assertEqual(User.objects.get(email="new@example.com").slackId, "nykomling")

    def test_resend_replaces_the_old_link(self):
        self.invite()
        old_link = self.link()
        user = User.objects.get(email="new@example.com")
        self.client.post(reverse("invite_resend", args=[user.pk]))
        new_link = self.link()

        _, old_page, _ = self.accept(old_link)
        self.assertFalse(old_page.context["validlink"])
        _, new_page, _ = self.accept(new_link)
        self.assertTrue(User.objects.get(email="new@example.com").is_active)

    def test_link_expires(self):
        self.invite()
        user = User.objects.get(email="new@example.com")
        token = self.link().rstrip("/").rsplit("/", 1)[1]
        later = invite_token_generator._now() + INVITE_VALID_FOR + datetime.timedelta(minutes=1)
        with mock.patch.object(invite_token_generator, "_now", return_value=later):
            self.assertFalse(invite_token_generator.check_token(user, token))
        self.assertTrue(invite_token_generator.check_token(user, token))

    def test_invite_link_is_not_a_password_reset_token(self):
        from django.contrib.auth.tokens import default_token_generator
        self.invite()
        user = User.objects.get(email="new@example.com")
        token = self.link().rstrip("/").rsplit("/", 1)[1]
        self.assertFalse(default_token_generator.check_token(user, token))

    def test_slack_name_must_be_free_and_without_at_sign(self):
        make_user("taken@example.com", "upptagen")
        self.invite()
        link = self.link()
        _, _, taken = self.accept(link, slack="Upptagen")
        self.assertIn("används redan", taken.content.decode())
        _, _, at_sign = self.accept(link, slack="@nykomling")
        self.assertIn("utan @-tecken", at_sign.content.decode())
        self.assertFalse(User.objects.get(email="new@example.com").is_active)


class InviteEdgeCaseTests(InviteTestCase):

    def test_existing_account_is_not_reinvited(self):
        make_user("member@example.com", "member")
        page = self.invite("Member@Example.com").content.decode()
        self.assertIn("already exists", page)
        self.assertEqual(mail.outbox, [])
        self.assertTrue(User.objects.get(email="member@example.com").has_usable_password())

    def test_inviting_the_same_email_twice_resends(self):
        self.invite()
        self.invite()
        self.assertEqual(User.objects.filter(email="new@example.com").count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_unused_old_signup_can_be_invited(self):
        old = User.objects.create(email="old@example.com", slackId="gammal",
                                  is_active=False, is_registration_complete=False)
        old.set_password("random-from-old-signup")
        old.save()
        self.invite("old@example.com")
        self.accept(self.link(), slack="gammal")
        old.refresh_from_db()
        self.assertTrue(old.is_active and old.is_registration_complete)

    def test_pending_invite_is_left_out_of_host_lists(self):
        self.invite()
        today = timezone.localdate()
        SchedulingPeriod.objects.create(start=today - datetime.timedelta(days=30),
                                        end=today + datetime.timedelta(days=150))
        page = self.client.get(reverse("hosts"))
        self.assertEqual(page.status_code, 200)
        self.assertNotIn(None, page.context["period_host_list"])
