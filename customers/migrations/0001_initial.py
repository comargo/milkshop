# Generated by Django 2.0.5 on 2018-05-21 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='Имя')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Debit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0, verbose_name='Приход')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debits', to='customers.Customer', verbose_name='Покупатель')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]