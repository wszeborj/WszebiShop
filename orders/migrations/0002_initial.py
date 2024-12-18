# Generated by Django 4.2.4 on 2024-09-18 13:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("shop", "0001_initial"),
        ("orders", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="account",
            field=models.ForeignKey(
                help_text="User account associated with the order item.",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                blank=True,
                help_text="Associated order for the order item.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="orders.order",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                help_text="Product included in the order.",
                on_delete=django.db.models.deletion.CASCADE,
                to="shop.product",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.ForeignKey(
                help_text="Shipping address for the order.",
                on_delete=django.db.models.deletion.PROTECT,
                to="orders.address",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="buyer",
            field=models.ForeignKey(
                help_text="User account who placed the order.",
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_type",
            field=models.ForeignKey(
                help_text="Selected shipping type for the order.",
                on_delete=django.db.models.deletion.PROTECT,
                to="orders.shippingtype",
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="account",
            field=models.ForeignKey(
                help_text="User account associated with the address.",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
