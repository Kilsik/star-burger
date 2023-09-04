# Generated by Django 4.2.4 on 2023-09-03 14:02

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_payment_alter_order_registrated_at'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='prepared_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.restaurant', verbose_name='Готовит'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 9, 3, 14, 2, 46, 48797, tzinfo=datetime.timezone.utc), verbose_name='дата и время поступления заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Необработан'), ('PRE', 'Готовится'), ('DLV', 'Доставляется'), ('DONE', 'Доставлен')], db_index=True, max_length=4, verbose_name='Статус'),
        ),
    ]
