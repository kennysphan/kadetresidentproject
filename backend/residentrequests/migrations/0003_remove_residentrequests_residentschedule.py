# Generated by Django 3.1.6 on 2021-05-03 04:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('residentrequests', '0002_residentrequests_residentschedule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='residentrequests',
            name='ResidentSchedule',
        ),
    ]
