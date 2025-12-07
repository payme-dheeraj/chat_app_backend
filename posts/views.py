from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, PollOption, PollVote, Like, Comment
from .serializers import (
    PostSerializer, PostCreateSerializer, CommentSerializer, VoteSerializer
)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for API"""
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@api_view(['GET'])
@permission_classes([AllowAny])
def list_posts(request):
    """Get all public posts"""
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response({
        'success': True,
        'posts': serializer.data
    })


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def create_post(request):
    """Create a new post"""
    serializer = PostCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        post = serializer.save(author=request.user)
        return Response({
            'success': True,
            'message': 'Post created successfully',
            'post': PostSerializer(post, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post(request, post_id):
    """Get a single post"""
    post = get_object_or_404(Post, id=post_id)
    serializer = PostSerializer(post, context={'request': request})
    return Response({
        'success': True,
        'post': serializer.data
    })


@api_view(['DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    """Delete a post (only by author)"""
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        return Response({
            'success': False,
            'message': 'You can only delete your own posts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    post.delete()
    return Response({
        'success': True,
        'message': 'Post deleted successfully'
    })


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        return Response({
            'success': True,
            'liked': False,
            'likes_count': post.likes_count
        })
    
    return Response({
        'success': True,
        'liked': True,
        'likes_count': post.likes_count
    })


@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def post_comments(request, post_id):
    """Get or add comments on a post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'GET':
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'success': True,
            'comments': serializer.data
        })
    
    # POST - Add comment
    content = request.data.get('content', '').strip()
    
    if not content:
        return Response({
            'success': False,
            'message': 'Comment content is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        content=content
    )
    
    return Response({
        'success': True,
        'message': 'Comment added',
        'comment': CommentSerializer(comment).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def vote_poll(request, post_id):
    """Vote on a poll"""
    post = get_object_or_404(Post, id=post_id)
    
    if post.post_type != 'poll':
        return Response({
            'success': False,
            'message': 'This post is not a poll'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = VoteSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    option_id = serializer.validated_data['option_id']
    option = get_object_or_404(PollOption, id=option_id, post=post)
    
    # Check if user already voted on this poll
    existing_vote = PollVote.objects.filter(
        user=request.user,
        option__post=post
    ).first()
    
    if existing_vote:
        if existing_vote.option.id == option_id:
            return Response({
                'success': False,
                'message': 'You already voted for this option'
            }, status=status.HTTP_400_BAD_REQUEST)
        # Change vote
        existing_vote.option = option
        existing_vote.save()
    else:
        PollVote.objects.create(user=request.user, option=option)
    
    # Return updated poll data
    return Response({
        'success': True,
        'message': 'Vote recorded',
        'post': PostSerializer(post, context={'request': request}).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    """Get current user's posts"""
    posts = Post.objects.filter(author=request.user)
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response({
        'success': True,
        'posts': serializer.data
    })
