from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic.edit import FormView

from .forms import InviteAcceptForm, InviteForm
from .models import User
from .tokens import INVITE_VALID_FOR, invite_token_generator


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


def can_be_invited(user):
    """
    Pending invites, and leftover self-registered accounts that were never
    used, can be (re)invited. Accounts someone has used cannot.
    """
    return not user.is_registration_complete and user.last_login is None and not user.is_staff


def send_invite(request, user):
    """
    Mail the person a link to choose their Slack name and password. The
    account stays inactive, with no usable password, until they do.
    Sending a new invite invalidates any earlier link.
    """
    user.is_active = False
    user.set_unusable_password()
    user.invited_at = timezone.now()
    user.save()
    path = reverse("invite_accept", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": invite_token_generator.make_token(user),
    })
    context = {"link": request.build_absolute_uri(path), "valid_days": INVITE_VALID_FOR.days}
    subject = " ".join(render_to_string("accounts/invite_subject.txt", context).split())
    send_mail(subject, render_to_string("accounts/invite_email.txt", context), None, [user.email])


class InviteView(StaffRequiredMixin, FormView):
    """Staff page: invite someone by email and see invites not yet accepted."""
    form_class = InviteForm
    template_name = "accounts/invites.html"
    success_url = reverse_lazy("invites")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending = list(User.objects.filter(is_registration_complete=False, invited_at__isnull=False)
                       .order_by("-invited_at"))
        for user in pending:
            user.invite_expired = user.invited_at + INVITE_VALID_FOR < timezone.now()
        context["pending"] = pending
        return context

    def form_valid(self, form):
        email = User.objects.normalize_email(form.cleaned_data["email"])
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User(email=email, is_registration_complete=False)
        elif not can_be_invited(user):
            form.add_error("email", "An account with this email address already exists.")
            return self.form_invalid(form)
        send_invite(self.request, user)
        messages.success(self.request, f"Invite sent to {user.email}.")
        return super().form_valid(form)


class InviteResendView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if can_be_invited(user):
            send_invite(request, user)
            messages.success(request, f"Invite sent again to {user.email}.")
        else:
            messages.error(request, f"{user.email} has already accepted their invite.")
        return redirect("invites")


class InviteAcceptView(PasswordResetConfirmView):
    """
    The link in the invite email. Built on PasswordResetConfirmView, which
    moves the token out of the URL into the session before showing the form.
    """
    token_generator = invite_token_generator
    form_class = InviteAcceptForm
    template_name = "accounts/invite_accept.html"
    post_reset_login = True
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Välkommen! Ditt konto är klart.")
        return response
