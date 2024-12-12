from django.contrib import admin
from django.urls import path, include
from . import views 

urlpatterns = [
   path('', views.index, name='index'),
   path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
   path('profile/', views.profile, name='profile'),
   path('profile/<int:user_id>/', views.profile, name='profile_with_id'),
   path('post/', views.post, name='post'),
   path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
   path('post_delete/<int:post_id>/', views.post_delete, name='post_delete'),
   path('post_edit/<int:post_id>/', views.edit_post, name='edit_post'),
   path('logout/', views.logout, name='logout'),
   path('like/<int:post_id>/', views.like_post, name='like_post'),
   path('dislikes/<int:post_id>/', views.dislike_post, name='dislike_post'),
   path('add_comment/', views.add_comment, name='add_comment'),
   path('search/', views.serch_users, name='search_users'),
   


]