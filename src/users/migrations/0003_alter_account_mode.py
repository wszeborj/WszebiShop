# Generated by Django 4.2.4 on 2024-04-22 21:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_account_mode_alter_account_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="mode",
            field=models.TextField(
                choices=[("SELLER", "SELLER"), ("BUYER", "BUYER")], default="BUYER"
            ),
        ),
    ]
