from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """Conversation between two or more users"""
    
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id}"
    
    @property
    def last_message(self):
        return self.messages.first()


class Message(models.Model):
    """Individual messages in a conversation"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/', blank=True, null=True)
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
