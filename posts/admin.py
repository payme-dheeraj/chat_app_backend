from django.contrib import admin
from .models import Post, PollOption, PollVote, Like, Comment


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_type', 'created_at', 'likes_count', 'comments_count']
    list_filter = ['post_type', 'created_at']
    search_fields = ['author__username', 'content']
    inlines = [PollOptionInline]


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'option_text', 'votes_count']


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'created_at']
    search_fields = ['user__username', 'content']
