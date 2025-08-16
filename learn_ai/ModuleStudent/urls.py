from django.urls import path, re_path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('list_course/', course_list, name='list_course_student'),
    path('view_courses/<int:course_id>/', view_course, name='view_courses'),

    path('UP', upload_file, name="upload"),
    path('DEL/', delete_image, name="delete_image"),
    re_path('create_vector_store/', chat_view, name='create_vector_store'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)