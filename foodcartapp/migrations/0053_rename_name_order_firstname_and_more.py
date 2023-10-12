# Generated by Django 4.2.4 on 2023-10-10 16:34

import datetime
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_alter_order_registrated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='surname',
            new_name='lastname',
        ),
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='телефон'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 10, 10, 16, 33, 44, 486251, tzinfo=datetime.timezone.utc), verbose_name='дата и время поступления заказа'),
        ),
    ]
