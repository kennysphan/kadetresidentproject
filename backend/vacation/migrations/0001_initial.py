# Generated by Django 3.1.6 on 2021-05-03 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VacationRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('requestOne', models.DateField(blank=True, null=True)),
                ('requestTwo', models.DateField(blank=True, null=True)),
                ('requestThree', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
