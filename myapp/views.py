from django.shortcuts import redirect, render
from .forms import SignupForm, ChangeUsernameForm, ChangeEmailForm, ChangeImageForm, PasswordChangeForm, SearchForm
from django.contrib.auth import login
from .models import CustomUser, Chat
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from . import forms
from django.db.models import Q, Max
from django.urls import reverse_lazy
from django.utils import timezone as dj_timezone
from datetime import datetime, timezone

def index(request):
    return render(request, "myapp/index.html")

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            image = form.cleaned_data.get('image')
            password = form.cleaned_data.get('password1')
            user = CustomUser(username=username, email=email, image=image, password=password)
            user.save()
            login(request, user)
            return redirect('friends')
    else:
        form = SignupForm()
            
    return render(request, "myapp/signup.html", {'form':form})

def login_view(request):
    return LoginView.as_view(template_name='myapp/login.html')(request)

class LiginView(LoginView):
    form_class = forms.LoginForm
    template_name = "myapp/login.html"

@login_required
def friends(request):
    current_user = request.user
    searchForm = SearchForm(request.GET)
    
    if searchForm.is_valid():
        keyword = searchForm.cleaned_data['keyword'] 
        other_users = CustomUser.objects.exclude(id=current_user.id)
        other_users = other_users.filter(Q(username__icontains=keyword) | Q(email__contains=keyword))
    else:
        searchForm = SearchForm() 
        other_users = CustomUser.objects.exclude(id=current_user.id)
    
    
    users_chats_list = []  

    latest_chats = (
        Chat.objects.filter(
            Q(sender=current_user) | Q(receiver=current_user)
        )
        .values('sender', 'receiver', 'id')
        .annotate(latest_time=Max('created_at'))  # 最新のチャット日時を取得
    )

    # 2. 最新チャットを辞書に整理してキャッシュ
    latest_chat_dict = {
        (chat['sender'], chat['receiver']): (chat['latest_time'], chat['id'])
        for chat in latest_chats
    }

    chat_ids = [chat['id'] for chat in latest_chats]
    chats_in_bulk = Chat.objects.in_bulk(chat_ids)

    # 3. 他のユーザーに対して、最新のチャットを取得
    for other_user in other_users:
        chat_key = (current_user.id, other_user.id)
        reverse_key = (other_user.id, current_user.id)

        # 最新のチャットがあるか確認
        latest_time_id = latest_chat_dict.get(chat_key) or latest_chat_dict.get(reverse_key)
        
        if latest_time_id:
            # 最新チャットを取得
            latest_chat = chats_in_bulk.get(latest_time_id[1])
        else:
            # チャットがない場合の仮オブジェクト
        
            latest_chat_model = Chat(
                sender=current_user,
                receiver=other_user,
                created_at=None,
                content="まだトークしていません"
            )
            
        
        # 4. ユーザーとチャットのペアをリストに追加
        user_chat_dict = {
            'user': other_user,
            'chat': latest_chat
        }
        users_chats_list.append(user_chat_dict)

    # 5. 最新チャットでソート
    sorted_chats = sorted(
        users_chats_list,
        key=lambda x: x['chat'].created_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    # 6. コンテキストに追加してテンプレートへ
    context = {
        'users_chats_list': sorted_chats,
        'searchForm': searchForm,
    }
    return render(request, "myapp/friends.html", context)

"""
    for other_user in other_users:
            chats = Chat.objects.filter(sender__in=[current_user, other_user], receiver__in=[current_user, other_user])
            
            if chats.count() != 0:
                latest_chat = chats.latest("created_at")
                latest_chats.append(latest_chat)
                
            else:
                latest_chat = Chat(sender=current_user, receiver=other_user, created_at=None, content="まだトークしていません")
                latest_chats.append(latest_chat)
                
    min_datetime = datetime.min.replace(tzinfo=timezone.utc)
    sorted_chats = sorted(latest_chats, key=lambda x: x.created_at or min_datetime, reverse=True)
    for chat in sorted_chats:
        
        if chat.sender == current_user:
            user = chat.receiver
        else:
            user = chat.sender
        
        user_chat_dict = {
            'user':user,
            'chat':chat
        }
        users_chats_list.append(user_chat_dict)
        
    context = {
        'users_chats_list':users_chats_list,
        'searchForm': searchForm,
    }
    return render(request, "myapp/friends.html", context)
"""
@login_required
def talk_room(request, pk):
    receiver = CustomUser.objects.get(id=pk)
    current_user = request.user
    
    if request.method == 'POST':
        chat = Chat(sender=current_user, receiver=receiver, content=request.POST['content'], created_at=dj_timezone.now())
        if chat.content:
            chat.save()
            return redirect('talk_room', pk=receiver.id)
    
    chats  = Chat.objects.filter(sender__in=[current_user.id, receiver.id], receiver__in=[current_user.id, receiver.id])
    context = {
        'chats':chats.order_by('created_at'),
        'receiver':receiver,
    }
    
    return render(request, "myapp/talk_room.html", context)

@login_required
def setting(request):
    return render(request, "myapp/setting.html")

@login_required
def logout_view(request):
    return LogoutView.as_view(template_name='myapp/login.html')(request)

class LogoutView(LoginRequiredMixin, LogoutView):
    pass

@login_required
def username_update(request):
    user = request.user
    form = ChangeUsernameForm()
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data.get('username')
            user.save()
            return redirect('setting')
    
    return render(request, "myapp/username_update.html", {'form':form})

@login_required
def email_update(request):
    user = request.user
    form = ChangeEmailForm()
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            user.email = form.cleaned_data.get('email')
            user.save()
            return redirect('setting')
    
    return render(request, "myapp/email_update.html", {'form':form})

@login_required
def image_update(request):
    user = request.user
    form = ChangeImageForm()
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, request.FILES)
        if form.is_valid():
            user.image = request.FILES['image']
            user.save()
            return redirect('setting')
    return render(request, "myapp/image_update.html", {'form':form})


class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'myapp/password_update.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Change Password"
        return context
    
class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'myapp/password_change_done.html'