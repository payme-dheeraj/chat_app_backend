from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'message_type', 'content', 'created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ", ".join([u.username for u in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'content', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['sender__username', 'content']
