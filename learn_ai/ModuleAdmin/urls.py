from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('users/', user_add, name='users'),
    path('list_course/', course_list, name='list_course'),

    
    path('add_course/', add_course, name='add_course'),
    path('view_course/<int:course_id>/', view_course, name='view_course'),
    path('delete_course/<int:course_id>/', delete_course, name='delete_course'),

    path('chatbot/', stream, name='chatbot'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)