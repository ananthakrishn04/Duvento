# Generated by Django 5.1.5 on 2025-03-01 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CodingGrounds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameparticipation',
            name='is_ready',
            field=models.BooleanField(default=False),
        ),
    ]
