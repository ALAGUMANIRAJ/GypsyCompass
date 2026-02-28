from django.contrib import admin
from .models import TripRequest, ContactMessage


@admin.register(TripRequest)
class TripRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'from_location', 'budget', 'currency', 'num_days', 'created_at')
    list_filter = ('travel_scope', 'travel_type', 'created_at')
    search_fields = ('name', 'from_location')
    readonly_fields = ('created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'short_message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = 'Mark selected as unread'
