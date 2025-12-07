import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')
        content = data.get('content', '')
        sender_id = data.get('sender_id')
        
        # Save message to database
        message = await self.save_message(sender_id, message_type, content)
        
        if message:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender_id': sender_id,
                        'sender_username': message.sender.username,
                        'message_type': message_type,
                        'content': content,
                        'created_at': message.created_at.isoformat(),
                    }
                }
            )
    
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, message_type, content):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            sender = User.objects.get(id=sender_id)
            
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                message_type=message_type,
                content=content
            )
            
            # Update conversation timestamp
            conversation.save()
            
            return message
        except (Conversation.DoesNotExist, User.DoesNotExist):
            return None
