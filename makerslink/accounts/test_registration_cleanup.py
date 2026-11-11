import importlib

from django.apps import apps
from django.test import TestCase
from django.utils import timezone

from accounts.models import User

cleanup = importlib.import_module("accounts.migrations.0006_deactivate_unused_signups")


class SignalRemovedTests(TestCase):
    """
    finish_registration deactivated any user who was not marked complete as
    soon as their password changed, which locked out admin-created users the
    first time they reset their password.
    """

    def test_password_change_keeps_an_active_user_active(self):
        user = User.objects.create(email="a@example.com", slackId="a", is_active=True,
                                   is_registration_complete=False)
        user.set_password("Long-enough-pw-1")
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_active)


class DeactivateUnusedSignupsTests(TestCase):

    def make(self, slack, **fields):
        defaults = dict(is_active=True, is_registration_complete=False)
        defaults.update(fields)
        return User.objects.create(email=f"{slack}@example.com", slackId=slack, **defaults)

    def test_only_never_used_signups_are_switched_off(self):
        pending = self.make("pending")
        completed = self.make("completed", is_registration_complete=True)
        logged_in = self.make("loggedin", last_login=timezone.now())
        staff = self.make("staff", is_staff=True)
        superuser = self.make("super", is_superuser=True)

        cleanup.deactivate_unused_signups(apps, None)

        active = {u.slackId: u.is_active for u in User.objects.all()}
        self.assertEqual(active, {"pending": False, "completed": True, "loggedin": True,
                                  "staff": True, "super": True})
