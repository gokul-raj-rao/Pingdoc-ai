from django.urls import path
from .views import register, user_login, user_logout, users

urlpatterns = [
    path('register/', register, name='register'),
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    # path('dashboard/', dashboard, name='dashboard'),
    path('user/', users, name='redirect_to_app2'),
]
