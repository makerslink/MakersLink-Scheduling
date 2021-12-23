# Generated by Django 3.1.14 on 2021-12-22 10:54

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0029_auto_20211222_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='repeat_end',
            field=models.DateTimeField(blank=True, help_text='Date to end repetition, must be after start', null=True),
        ),
        migrations.AddConstraint(
            model_name='schedulingperiod',
            constraint=models.CheckConstraint(check=models.Q(start__lt=django.db.models.expressions.F('end')), name='check_period_start_before_end'),
        ),
    ]