# Generated by Django 5.1.1 on 2024-10-06 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(blank=True, choices=[('ADMIN', 'ADMIN')], max_length=20, null=True),
        ),
    ]
