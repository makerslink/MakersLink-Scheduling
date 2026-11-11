from datetime import timedelta

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

INVITE_VALID_FOR = timedelta(days=14)


class InviteTokenGenerator(PasswordResetTokenGenerator):
    """
    Tokens for invite links. A separate salt keeps them from working as
    password-reset tokens and the other way round.

    The hash covers the password, active and completed flags and the time
    the invite was sent, so a link stops working once the invite is accepted
    and when a newer invite replaces it. Links also expire after
    INVITE_VALID_FOR, which is longer than the password-reset timeout.
    """
    key_salt = "accounts.tokens.InviteTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        invited_at = "" if user.invited_at is None else user.invited_at.timestamp()
        return (f"{user.pk}{user.password}{user.is_active}{user.is_registration_complete}"
                f"{invited_at}{timestamp}{user.email}")

    def check_token(self, user, token):
        # Same checks as PasswordResetTokenGenerator.check_token, with the
        # invite lifetime instead of PASSWORD_RESET_TIMEOUT.
        if not (user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(self._make_token_with_timestamp(user, ts, secret), token):
                break
        else:
            return False
        return self._num_seconds(self._now()) - ts <= INVITE_VALID_FOR.total_seconds()


invite_token_generator = InviteTokenGenerator()
