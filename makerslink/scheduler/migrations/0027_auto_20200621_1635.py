# Generated by Django 3.0.7 on 2020-06-21 14:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduler', '0026_auto_20200621_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulingperiod',
            name='hosts',
            field=models.ManyToManyField(blank=True, related_name='periods', related_query_name='period', to=settings.AUTH_USER_MODEL),
        ),
    ]