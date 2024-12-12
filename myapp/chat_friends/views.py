from django.shortcuts import render
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FriendshipRequest, Friend, Chat, Message
from django.http import JsonResponse
from django.db.models import Q


def get_or_create_chat(user1, user2):
    # Проверяем, существует ли уже чат между двумя пользователями
    chat = Chat.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).first()  # Ищем чат, где один пользователь - user1, а другой - user2, или наоборот

    if not chat:
        # Если чат не найден, создаем новый чат
        chat = Chat.objects.create(user1=user1, user2=user2)

    return chat  # Возвращаем найденный или созданный чат

@login_required
def start_chat(request, user_id):
    # Получаем объект другого пользователя по его идентификатору
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # После получения друого пользователя создаем чат между нами и пользователлям 
    chat = get_or_create_chat(request.user, other_user)  
    
    # Перенаправляем пользователя на страницу чата с идентификатором чата
    return redirect('chat', chat_id=chat.id)  

@login_required
def chat_view(request, chat_id):
    # Получаем объект чата по его идентификатору
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Получаем все сообщения из чата
    messages = chat.messages.all()

    if request.method == 'POST':
        # Если запрос является POST-запросом, то обрабатываем отправку сообщения
        content = request.POST.get('message')  # Получаем текст сообщения из формы
        if content:
            # Создаем новое сообщение и сохраняем его в базе данных
            message = Message.objects.create(chat=chat, sender=request.user, content=content)
            # Возвращаем JSON-ответ с информацией о новом сообщении
            return JsonResponse({
                'username': message.sender.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            })

    # Определяем, кто является другим пользователем в чате
    other_user = chat.user1 if chat.user1 != request.user else chat.user2

    # Отображаем страницу чата с сообщениями и информацией о другом пользователе
    return render(request, 'main/chat.html', {
        'chat': chat,
        'messages': messages,
        'other_user': other_user,
    })
def list_friends(request):
    friends_list = Friend.objects.filter(user=request.user)
    return render(request, 'main/list_friends.html', {'friends_list': friends_list})



def remove_friend(request, friend_id):
    if request.method == "POST":
        user = request.user
        
        # Находим в модель френд друзей текущего пользовтеля
        friendship = get_object_or_404(Friend, user=user, friend_id=friend_id)
        
        # Удаляем запись о дружбе для текущего пользователя
        friendship.delete()
        
        # Удаляем запись о дружбе для друга
        Friend.objects.filter(user=friend_id, friend=user).delete()
        
        # Перенаправляем обратно на страницу со списком друзей
        return redirect('friend_list')  # Убедитесь, что этот URL соответствует вашему маршруту