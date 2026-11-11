from django.test import TestCase
from django.urls import reverse

from accounts.models import User


def make_member(email="member@example.com", slack="member", password="Long-enough-pw-1"):
    user = User.objects.create(email=email, slackId=slack, is_active=True,
                               is_registration_complete=True)
    user.set_password(password)
    user.save()
    return user


class LogoutTests(TestCase):
    """
    Django 5.0 removed GET support from LogoutView. The menu used a plain link,
    so "Logga ut" answered 405 and left the user signed in.
    """

    def setUp(self):
        self.user = make_member()
        self.client.force_login(self.user)

    def test_menu_logs_out_with_a_post_form(self):
        html = self.client.get(reverse("joinEvent")).content.decode()
        self.assertRegex(html, r'<form method="post" action="%s"' % reverse("logout"))
        self.assertNotIn('href="%s"' % reverse("logout"), html)

    def test_post_logs_out(self):
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_does_not_log_out(self):
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


class LoggedOutMenuTests(TestCase):
    """A visitor who is not signed in should not be offered member pages or logout."""

    def test_login_page_menu(self):
        html = self.client.get(reverse("login")).content.decode()
        self.assertNotIn("Logga ut", html)
        self.assertNotIn('href="%s"' % reverse("profile"), html)
        self.assertNotIn('href="%s"' % reverse("joinEvent"), html)
        self.assertIn('href="%s"' % reverse("login"), html)
