# Generated by Django 2.0.5 on 2018-10-19 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0018_auto_20181018_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtemplate',
            name='count_key',
            field=models.CharField(default='D', help_text='Key displayed when counting participantcy', max_length=1),
        ),
    ]
