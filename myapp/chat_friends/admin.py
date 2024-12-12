from django.contrib import admin
from .models import FriendshipRequest, Friend, Chat, Message

admin.site.register(Friend)

admin.site.register(FriendshipRequest)

admin.site.register(Chat)

admin.site.register(Message)


