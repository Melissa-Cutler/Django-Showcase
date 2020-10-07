# Generated by Django 3.1.2 on 2020-10-07 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fund_number', models.IntegerField(unique=True)),
                ('initial_balance', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investment_number', models.IntegerField(unique=True)),
                ('date', models.DateTimeField(verbose_name='date of investment')),
                ('amount_usd', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Commitment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commitment_number', models.IntegerField(unique=True)),
                ('date', models.DateTimeField(verbose_name='date of commitment')),
                ('amount_usd', models.FloatField(default=0.0)),
                ('fund', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capitalcallapp.fund')),
            ],
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_usd', models.FloatField(default=0)),
                ('date', models.DateTimeField(verbose_name='date of call')),
                ('commitment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capitalcallapp.commitment')),
                ('fund', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capitalcallapp.fund')),
                ('investment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capitalcallapp.investment')),
            ],
        ),
    ]
