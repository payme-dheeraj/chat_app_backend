from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_posts, name='list_posts'),
    path('create/', views.create_post, name='create_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('<int:post_id>/', views.get_post, name='get_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('<int:post_id>/comments/', views.post_comments, name='post_comments'),
    path('<int:post_id>/vote/', views.vote_poll, name='vote_poll'),
]
