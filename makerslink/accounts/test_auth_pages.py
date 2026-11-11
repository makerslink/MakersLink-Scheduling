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


class SelfRegistrationRemovedTests(TestCase):
    """Accounts are no longer created from a public form."""

    def test_register_url_is_gone(self):
        self.assertEqual(self.client.get("/accounts/register/").status_code, 404)
        self.assertEqual(self.client.post("/accounts/register/", {
            "email": "new@example.com", "slackId": "new"}).status_code, 404)
        self.assertFalse(User.objects.filter(email="new@example.com").exists())


class PasswordResetTests(TestCase):
    """Password reset shares the set-password page the registration flow used."""

    def test_reset_flow_end_to_end(self):
        from django.core import mail
        import re
        user = make_member()
        self.client.post(reverse("password_reset"), {"email": user.email})
        link = re.search(r"https?://testserver(/accounts/\S+/)", mail.outbox[0].body).group(1)
        form_page = self.client.get(link, follow=True)
        self.assertTemplateUsed(form_page, "accounts/set_password.html")
        self.client.post(form_page.redirect_chain[-1][0], {
            "new_password1": "Another-long-pw-2", "new_password2": "Another-long-pw-2"})
        user.refresh_from_db()
        self.assertTrue(user.check_password("Another-long-pw-2"))
