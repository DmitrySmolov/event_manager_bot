from django.db import transaction
from rest_framework import serializers

from . import models


class TelegramUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TelegramUser
        fields = '__all__'

    def validate(self, data):
        if not data.get('telegram_id') and not data.get('username'):
            raise serializers.ValidationError(
                'Оба поля не могут быть пустыми'
            )
        return data


class EventSerializer(serializers.ModelSerializer):
    host = TelegramUserSerializer()
    created_by = TelegramUserSerializer()

    class Meta:
        model = models.Event
        fields = '__all__'

    def create(self, validated_data):
        host_data = validated_data.pop('host')
        created_by_data = validated_data.pop('created_by')

        host_telegram_id = host_data.get('telegram_id')
        host_username = host_data.get('username')
        host, created = models.TelegramUser.objects.get_or_create(
            telegram_id=host_telegram_id,
            defaults={'username': host_username}
        )

        created_by_telegram_id = created_by_data.get('telegram_id')
        created_by_username = created_by_data.get('username')
        created_by, created = models.TelegramUser.objects.get_or_create(
            telegram_id=created_by_telegram_id,
            defaults={'username': created_by_username}
        )
        with transaction.atomic():
            try:
                event = models.Event.objects.create(
                    host=host,
                    created_by=created_by,
                    **validated_data
                )
                models.EventStatus.objects.create(event=event)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return event


class EventStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.EventStatus
        fields = '__all__'
        read_only_fields = ('event',)
