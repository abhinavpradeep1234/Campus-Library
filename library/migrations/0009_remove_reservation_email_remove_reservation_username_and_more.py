# Generated by Django 5.1.1 on 2024-12-29 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0008_reservation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reservation",
            name="email",
        ),
        migrations.RemoveField(
            model_name="reservation",
            name="username",
        ),
        migrations.AddField(
            model_name="reservation",
            name="reserve_date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
