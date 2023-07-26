# Generated by Django 3.2.20 on 2023-07-26 12:57

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20230717_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='RU', verbose_name='телефон'),
        ),
    ]
