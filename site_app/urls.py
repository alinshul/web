from django.urls import path
from .views import index
from . import views


urlpatterns = [
    path('', index, name='index'),
    path('like_dislike/', views.like_dislike, name='like_dislike'),
    # path('add_comment/', views.add_comment, name='add_comment'),
]
