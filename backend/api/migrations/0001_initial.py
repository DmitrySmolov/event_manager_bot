# Generated by Django 5.0.3 on 2024-03-19 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('location', models.URLField(verbose_name='Локация (ссылка)')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='ID в телеграме')),
                ('username', models.CharField(blank=True, max_length=32, null=True, verbose_name='username в телеграме')),
            ],
            options={
                'verbose_name': 'Пользователь телеграма',
                'verbose_name_plural': 'Пользователи телеграма',
            },
        ),
        migrations.CreateModel(
            name='EventStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='api.event')),
            ],
            options={
                'verbose_name': 'Статус мероприятия',
                'verbose_name_plural': 'Статусы мероприятий',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_events', to='api.telegramuser'),
        ),
        migrations.AddField(
            model_name='event',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hosted_events', to='api.telegramuser'),
        ),
    ]
