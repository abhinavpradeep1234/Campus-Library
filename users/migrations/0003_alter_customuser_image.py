# Generated by Django 5.1.1 on 2024-12-10 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_customuser_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="image",
            field=models.ImageField(
                default="static/image/user_default.png", upload_to="profile"
            ),
        ),
    ]
