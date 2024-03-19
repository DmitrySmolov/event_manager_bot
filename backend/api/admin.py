from django.contrib import admin

from .models import Event, EventStatus, TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_id',
        'username',
    )
    search_fields = (
        'telegram_id',
        'username',
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'location',
        'host',
        'created_by',
    )
    search_fields = (
        'name',
        'location',
        'host',
        'created_by',
    )


@admin.register(EventStatus)
class EventStatusAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'status',
    )
    search_fields = (
        'event',
        'status',
    )
