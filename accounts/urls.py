from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_parent, name='register_parent'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.user_info_view, name='user_info'),
]
