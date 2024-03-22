from django.db.models.signals import post_save
from django.dispatch import receiver
import requests

from backend.settings import EVENT_WHOOK_FULL_URL, STATUS_WHOOK_FULL_URL
from .models import Event, EventStatus
from .serializers import EventSerializer


@receiver(post_save, sender=Event)
def send_event_to_bot(sender, instance, created, **kwargs):
    """
    Принимает сигнал о создании нового мероприятия и отправляет его в
    телеграм-бот.
    """
    if created:
        serializer = EventSerializer(instance)
        data = serializer.data
        headers = {
            'Content-Type': 'application/json'
        }
        requests.post(
            url=EVENT_WHOOK_FULL_URL,
            json=data,
            headers=headers
        )


@receiver(post_save, sender=EventStatus)
def send_updated_event_status(sender, instance, created, **kwargs):
    """
    Принимает сигнал об изменении статуса мероприятия и отправляет его в
    телеграм-бот.
    """
    if not created:
        event_status = instance.status
        event_name = instance.event.name
        created_by_tg_id = instance.event.created_by.telegram_id
        requests.post(
            url=STATUS_WHOOK_FULL_URL,
            json={
                'event_name': event_name,
                'status': event_status,
                'created_by_tg_id': created_by_tg_id
            }
        )
