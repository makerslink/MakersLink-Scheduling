# Generated by Django 3.1.14 on 2021-12-23 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0031_auto_20211222_1204'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['start']},
        ),
    ]