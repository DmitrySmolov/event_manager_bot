from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Event
from .serializers import EventSerializer, EventStatusSerializer


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'id'

    @action(
        detail=True,
        methods=['post'],
        url_path='status',
    )
    def update_status(self, request, pk=None, *args, **kwargs):
        event = self.get_object()
        event_status = event.status.first()
        if not event_status:
            return Response(
                {'detail': 'Статус мероприятия не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        event_status_serializer = EventStatusSerializer(
            instance=event_status,
            data=request.data,
        )
        if event_status_serializer.is_valid(raise_exception=True):
            event_status_serializer.save()
            return Response(
                event_status_serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            event_status_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
