# Generated by Django 4.2.4 on 2024-04-16 11:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_orderitem_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipping_status",
            field=models.TextField(
                choices=[
                    ("NEW", "NEW"),
                    ("SHIPPED", "SHIPPED"),
                    ("DELIVERED", "DELIVERED"),
                    ("CLOSED", "CLOSED"),
                ],
                default="NEW",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.TextField(
                choices=[
                    ("NEW", "NEW"),
                    ("AWAITING_PAYMENT", "AWAITING_PAYMENT"),
                    ("UNPAID", "UNPAID"),
                    ("PAID", "PAID"),
                    ("SHIPPED", "SHIPPED"),
                    ("DELIVERED", "DELIVERED"),
                    ("CLOSED", "CLOSED"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="update_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
