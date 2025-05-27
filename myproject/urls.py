from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from . import views
from site_app import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('feedback/', views.submit_feedback, name='feedback'),
    path('admin/', admin.site.urls),
    path('', include('site_app.urls')),
    path('api/likes/', views.like_dislike, name='like-api'),
    # path('api/comments/', views.add_comment, name='comment-api'),
] + static(settings.STATIC_URL, document_root=str(settings.STATIC_ROOT))



