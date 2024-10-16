# Generated by Django 4.2.4 on 2024-09-18 15:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(
                help_text="Image of the product.",
                max_length=255,
                upload_to="product_images",
            ),
        ),
    ]
