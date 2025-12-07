from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_anonymous_user, name='generate_anonymous'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('recaptcha-key/', views.get_recaptcha_site_key, name='recaptcha_key'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('search/', views.search_users, name='search_users'),
]
