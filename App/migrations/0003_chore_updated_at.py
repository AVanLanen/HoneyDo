# Generated by Django 5.1 on 2024-08-30 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_chore_completed_at_userprofile_chores_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='chore',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
