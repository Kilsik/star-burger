# Generated by Django 4.2.4 on 2023-10-12 12:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_remove_order_foodcartapp_phone_675d71_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 10, 12, 12, 26, 58, 770551, tzinfo=datetime.timezone.utc), verbose_name='дата и время поступления заказа'),
        ),
    ]
