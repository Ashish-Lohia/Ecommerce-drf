# Generated by Django 5.2.3 on 2025-06-25 11:20

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0003_alter_category_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('base_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('convenience_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('created', 'Created'), ('confirmed', 'Confirmed'), ('pickup_scheduled', 'Pickup Scheduled'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='created', max_length=50)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_bought', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_sold', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price_at_order', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='product.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
