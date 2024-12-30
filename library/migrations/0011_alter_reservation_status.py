# Generated by Django 5.1.1 on 2024-12-29 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0010_reservation_status_reservation_username_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reservation",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[("confirm booking", "Confirm Booking")],
                default="confirm booking",
                max_length=200,
                null=True,
            ),
        ),
    ]
