# Generated by Django 2.0.5 on 2018-06-21 19:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0002_add_related_names'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'get_latest_by': 'date', 'ordering': ['date']},
        ),
    ]
