from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, LoginForm, PostForm, CommentForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from .models import CustomUser, Post, Like
from django.contrib.auth.decorators import login_required
from chat_friends.models import CustomUser, FriendshipRequest, Friend, Chat, Message



# Create your views here.

def index(request):
    posts = Post.objects.all()
    return render(request, 'main/index.html', {'posts': posts})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Выполнение входа
                return redirect('profile')  # Перенаправляем на профиль без параметров
    else:
        form = LoginForm()  # Инициализация формы для GET-запроса
    return render(request, 'main/login.html', {'form': form})


@login_required
def profile(request, user_id=None):
    if user_id is not None:  # Проверяем, передан ли user_id
        user = get_object_or_404(CustomUser, id=user_id)  # Получаем пользователя по ID
    else:
        user = request.user  # Если user_id нет, используем текущего пользователя

    # Проверяем, является ли пользователь другом
    is_friend = Friend.objects.filter(user=request.user, friend=user).exists()
    request_sent = FriendshipRequest.objects.filter(from_user=request.user, to_user=user).exists()
    incoming_requests = FriendshipRequest.objects.filter(to_user=request.user)

    # Обработка POST-запросов
    if request.method == 'POST':
        # Добавление в друзья
        if 'add_friend' in request.POST:
            if not is_friend and not request_sent:
                FriendshipRequest.objects.create(from_user=request.user, to_user=user)
                return redirect('profile_with_id', user_id=user.id)

        # Принятие запроса на дружбу
        elif 'accept_request' in request.POST:
            request_id = request.POST.get('request_id')
            friend_request = get_object_or_404(FriendshipRequest, id=request_id)
            if friend_request.to_user == request.user:
                Friend.objects.create(user=request.user, friend=friend_request.from_user)
                Friend.objects.create(user=friend_request.from_user, friend=request.user)
                friend_request.delete()
                return redirect('profile_with_id', user_id=user.id)

        # Отклонение запроса на дружбу
        elif 'decline_request' in request.POST:
            request_id = request.POST.get('request_id')
            friend_request = get_object_or_404(FriendshipRequest, id=request_id)
            if friend_request.to_user == request.user:
                friend_request.delete()  # Удаляем запрос
                return redirect('profile_with_id', user_id=user.id)

        # Начало чата
        elif 'start_chat' in request.POST:
            chat, created = Chat.objects.get_or_create(
                user1=request.user,
                user2=user
            )
            return redirect('chat', chat_id=chat.id)

    # Получение постов пользователя
    posts = Post.objects.filter(author=user)  # Предполагается наличие модели Post
    post_data = []
    for post in posts:
        likes_count = Like.objects.filter(post=post, is_like=True).count()
        dislikes_count = Like.objects.filter(post=post, is_like=False).count()
        post_data.append({
            'post': post,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
        })

    return render(request, 'main/profile.html', {
        'user': user,
        'is_friend': is_friend,
        'request_sent': request_sent,
        'incoming_requests': incoming_requests,
        'post_data': post_data,
    })



def post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Не забудьте передать request.FILES для загрузки изображений
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно опубликован')
            return redirect('profile')
    else:
        form = PostForm()  # Создание пустой формы при GET запросе

    return render(request, 'main/post.html', {'form': form})  # Убедитесь


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    return render(request, 'main/detail_post.html', {'post': post})  # Передайте post в шаблон


def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален')
        return redirect('profile')
    

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post) # instance of Post показывает текущее данные 
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, 'Пост успешно изменен')
            return redirect('profile')
    else:
        form = PostForm(instance=post)  # Инициализация формы с текущими данными

    return render(request, 'main/edit_post.html', {'form': form, 'post': post})  # Добавляем post в контекст



def logout(request):
    if request.method == 'POST':
        auth_logout(request)  # Выполнение выхода
        return redirect('index')
   

def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # Попытка получить существующий лайк
        like = Like.objects.filter(user=request.user, post=post).first()
        
        if like:
            # Если лайк уже существует, меняем его состояние
            if like.is_like:  # Если это лайк
                like.delete()  # Удаляем лайк
            else:
                like.is_like = True  # Если это дизлайк, меняем на лайк
                like.save()
        else:
            # Если лайка не было, создаем новый
            Like.objects.create(user=request.user, post=post, is_like=True)

    # Перенаправляем на профиль пользователя, который является автором поста
    return redirect('profile_with_id', user_id=post.author.id)  # Используем ID автора поста

def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # Попытка получить существующий лайк
        like = Like.objects.filter(user=request.user, post=post).first()
        
        if like:
            # Если лайк уже существует, меняем его состояние
            if not like.is_like:  # Если это дизлайк
                like.delete()  # Удаляем дизлайк
            else:
                like.is_like = False  # Если это лайк, меняем на дизлайк
                like.save()
        else:
            # Если лайка не было, создаем новый
            Like.objects.create(user=request.user, post=post, is_like=False)

    # Перенаправляем на профиль пользователя, который является автором поста
    return redirect('profile_with_id', user_id=post.author.id)  # Используем ID автора поста




def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user  # Установка автора комментария
            comment.post = get_object_or_404(Post, id=request.POST.get('post_id'))  # Привязка к посту
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен')
            return redirect('post_detail', post_id=comment.post.id)  # Перенаправление на страницу поста
    return redirect('index')  # Если форма не валидна, перенаправление на список постов



def serch_users(request):
    query = request.GET.get('q')
    users = CustomUser.objects.all()

    if query:
        # Измените фильтрацию на поиск по полю nickname
        users = users.filter(nickname__icontains=query)

    return render(request, 'main/serch_users.html', {'users': users, 'query': query})