# Generated by Django 5.0.3 on 2024-03-20 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='telegram_id',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='ID в телеграме'),
        ),
    ]
