from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.list_conversations, name='list_conversations'),
    path('conversations/start/', views.start_conversation, name='start_conversation'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversations/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
]
