from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, MessageCreateSerializer
from users.models import User


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for API"""
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    """Get all conversations for current user"""
    conversations = Conversation.objects.filter(participants=request.user)
    serializer = ConversationSerializer(conversations, many=True, context={'request': request})
    return Response({
        'success': True,
        'conversations': serializer.data
    })


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    """Start a new conversation with a user"""
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({
            'success': False,
            'message': 'user_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        return Response({
            'success': False,
            'message': 'Cannot start conversation with yourself'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if conversation already exists
    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing:
        return Response({
            'success': True,
            'conversation': ConversationSerializer(existing, context={'request': request}).data,
            'existing': True
        })
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return Response({
        'success': True,
        'conversation': ConversationSerializer(conversation, context={'request': request}).data,
        'existing': False
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, conversation_id):
    """Get messages for a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return Response({
            'success': False,
            'message': 'You are not a participant in this conversation'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Mark messages as read
    conversation.messages.exclude(sender=request.user).update(is_read=True)
    
    messages = conversation.messages.all().order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    
    return Response({
        'success': True,
        'messages': serializer.data
    })


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id):
    """Send a message in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return Response({
            'success': False,
            'message': 'You are not a participant in this conversation'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MessageCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        message = serializer.save(conversation=conversation, sender=request.user)
        
        # Update conversation timestamp
        conversation.save()
        
        return Response({
            'success': True,
            'message': MessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    """Get a single conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return Response({
            'success': False,
            'message': 'You are not a participant in this conversation'
        }, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'success': True,
        'conversation': ConversationSerializer(conversation, context={'request': request}).data
    })
