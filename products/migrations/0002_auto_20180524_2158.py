# Generated by Django 2.0.5 on 2018-05-24 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'get_latest_by': 'date', 'verbose_name': 'Цена'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Продукция'},
        ),
    ]
