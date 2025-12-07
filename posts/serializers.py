from rest_framework import serializers
from .models import Post, PollOption, PollVote, Like, Comment
from users.serializers import UserSerializer


class PollOptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.ReadOnlyField()
    
    class Meta:
        model = PollOption
        fields = ['id', 'option_text', 'votes_count']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    poll_options = PollOptionSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'post_type', 'content', 'image', 'video',
            'poll_options', 'likes_count', 'comments_count', 'is_liked',
            'user_vote', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.post_type == 'poll':
            vote = PollVote.objects.filter(
                user=request.user,
                option__post=obj
            ).first()
            if vote:
                return vote.option.id
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    poll_options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = ['post_type', 'content', 'image', 'video', 'poll_options']
    
    def validate(self, data):
        post_type = data.get('post_type')
        
        if post_type == 'image' and not data.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for image posts'})
        
        if post_type == 'video' and not data.get('video'):
            raise serializers.ValidationError({'video': 'Video is required for video posts'})
        
        if post_type == 'poll':
            poll_options = data.get('poll_options', [])
            if len(poll_options) < 2:
                raise serializers.ValidationError({'poll_options': 'At least 2 options required for poll'})
        
        return data
    
    def create(self, validated_data):
        poll_options = validated_data.pop('poll_options', [])
        post = Post.objects.create(**validated_data)
        
        if post.post_type == 'poll':
            for option_text in poll_options:
                PollOption.objects.create(post=post, option_text=option_text)
        
        return post


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']


class VoteSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()
