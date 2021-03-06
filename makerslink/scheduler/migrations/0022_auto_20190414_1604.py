# Generated by Django 2.0.5 on 2019-04-14 14:04

from django.db import migrations

def SetExclusionFlag(apps, schema_editor):
    SchedulingRule = apps.get_model('scheduler', 'SchedulingRule')
    for srule in SchedulingRule.objects.all():
        srule.use_exclusions = True
        srule.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0021_auto_20190414_1555'),
    ]

    operations = [
        migrations.RunPython(SetExclusionFlag),
    ]
