# Generated by Django 5.1.1 on 2024-10-08 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_mark',
            field=models.BooleanField(default=False),
        ),
    ]
