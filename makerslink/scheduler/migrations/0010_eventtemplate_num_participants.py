# Generated by Django 2.0.5 on 2018-08-03 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0009_eventinstance_participants'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtemplate',
            name='num_participants',
            field=models.IntegerField(default=0, help_text='Number of participants, -1 for infinite'),
        ),
    ]
