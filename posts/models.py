from django.db import models
from django.conf import settings


class Post(models.Model):
    """Model for user posts (images, videos, polls, text)"""
    
    POST_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('poll', 'Poll'),
    ]
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)  # Caption or text content
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username} - {self.post_type} - {self.created_at}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()


class PollOption(models.Model):
    """Poll options for poll-type posts"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poll_options')
    option_text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.option_text
    
    @property
    def votes_count(self):
        return self.votes.count()


class PollVote(models.Model):
    """User votes on poll options"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'option']
    
    def __str__(self):
        return f"{self.user.username} voted for {self.option.option_text}"


class Like(models.Model):
    """Likes on posts"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"


class Comment(models.Model):
    """Comments on posts"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"
