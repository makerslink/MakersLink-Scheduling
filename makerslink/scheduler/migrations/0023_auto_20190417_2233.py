# Generated by Django 2.0.5 on 2019-04-17 20:33

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0022_auto_20190414_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulingcalendar',
            name='service_account',
            field=models.FileField(blank=True, help_text='Upload client_secret json-file', null=True, storage=django.core.files.storage.FileSystemStorage(location='/home/larlin/Projects/MakersLink-Scheduling/pks'), upload_to=''),
        ),
    ]