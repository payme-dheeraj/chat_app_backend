from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'message_type', 'content', 'image', 'video', 'file', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'unread_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_type', 'content', 'image', 'video', 'file']
    
    def validate(self, data):
        message_type = data.get('message_type', 'text')
        
        if message_type == 'text' and not data.get('content'):
            raise serializers.ValidationError({'content': 'Content is required for text messages'})
        
        if message_type == 'image' and not data.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for image messages'})
        
        return data
