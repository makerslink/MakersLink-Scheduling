# Generated by Django 2.0.5 on 2018-08-01 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0005_auto_20180801_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventinstance',
            name='host',
        ),
    ]
