# Generated by Django 2.0.5 on 2018-06-21 18:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_auto_20180524_2158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'get_latest_by': 'date', 'ordering': ['date'], 'verbose_name': 'Цена'},
        ),
    ]