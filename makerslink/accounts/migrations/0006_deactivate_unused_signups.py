from django.db import migrations


def deactivate_unused_signups(apps, schema_editor):
    """
    Self-registration left each new account active, with a random password
    nobody knew, until its owner set one from the emailed link; the
    finish_registration signal then switched it off pending approval. With
    the signal gone, "forgot password" would turn such an account into a
    working one without anyone approving it.

    Accounts that never finished registering and never logged in are
    switched off. Nobody could use them anyway; staff can invite the person
    again.
    """
    User = apps.get_model("accounts", "User")
    User.objects.filter(
        is_registration_complete=False, last_login__isnull=True, is_active=True,
        is_staff=False, is_superuser=False,
    ).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_alter_user_id"),
    ]

    operations = [
        migrations.RunPython(deactivate_unused_signups, migrations.RunPython.noop),
    ]
