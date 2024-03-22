from django.db.models.signals import post_save
from django.dispatch import receiver
import requests

from backend.settings import WEBHOOK_FULL_URL
from .models import Event
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
            url=WEBHOOK_FULL_URL,
            json=data,
            headers=headers
        )
