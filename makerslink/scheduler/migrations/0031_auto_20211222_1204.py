# Generated by Django 3.1.14 on 2021-12-22 11:04

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0030_auto_20211222_1154'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='eventinstance',
            constraint=models.CheckConstraint(check=models.Q(start__lt=django.db.models.expressions.F('end')), name='check_instance_start_before_end'),
        ),
    ]