# Generated by Django 3.1.14 on 2021-12-23 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0032_auto_20211223_1016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-start']},
        ),
    ]