# Generated by Django 2.0.5 on 2018-07-27 19:33

from django.db import migrations
from ..models import User

def create_testusers(apps, schema_editor):
    superuser = User()
    superuser.is_active = True
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.email = "admin"
    superuser.set_password('adminadmin')
    superuser.save()

    user1 = User()
    user1.is_active = True
    user1.is_superuser = False
    user1.is_staff = False
    user1.email = "user1"
    user1.set_password('testtest')
    user1.save()

    user2 = User()
    user2.is_active = True
    user2.is_superuser = False
    user2.is_staff = False
    user2.email = "user2"
    user2.set_password('testtest')
    user2.save()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_testusers)
    ]
    
