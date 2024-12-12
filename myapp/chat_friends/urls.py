from django.urls import path, include
from . import views 
urlpatterns = [
    path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat'),
    path('friends_list', views.list_friends, name='friend_list'),
     path('friends/remove/<int:friend_id>/', views.remove_friend, name='remove_friend'),  # Удаление друг
    
]