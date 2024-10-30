from django.shortcuts import redirect, render
from .forms import SignupForm, ChangeUsernameForm, ChangeEmailForm, ChangeImageForm, PasswordChangeForm, SearchForm
from django.contrib.auth import login
from .models import CustomUser, Chat
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from . import forms
from django.db.models import Q, Max, Min, Case, When, Value, IntegerField,TextField, F
from django.db.models.functions import Coalesce, Greatest
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
    user = request.user

    friends = (
    CustomUser.objects.exclude(id=user.id)  # 除外するユーザー
    .annotate(
        send_max=Max("sender__created_at", filter=Q(sender__receiver=user)),  # 送信したメッセージの最新時刻
        receive_max=Max("receiver__created_at", filter=Q(receiver__sender=user)),  # 受信したメッセージの最新時刻
        latest_time=Greatest("send_max", "receive_max"),  # 送受信の最新時刻
        latest_msg_time=Coalesce("latest_time", "send_max", "receive_max"),  # 最新のメッセージ時刻
        latest_msg_talk=Case(  # 最新メッセージの内容を取得
            When(latest_msg_time=F("receiver__created_at"), then=F("receiver__content")),  # 送信メッセージの内容
            When(latest_msg_time=F("sender__created_at"), then=F("sender__content")),
            default=Value("まだトークしていません"),
            output_field=TextField() # 受信メッセージの内容
        )
    )
    .values('id', 'username', 'latest_msg_talk', 'latest_msg_time')
    .distinct()
    .order_by(F("latest_msg_time").desc(nulls_last=True))  # 最新メッセージ時刻でソート
    )

    searchForm = SearchForm()

    if request.method == "GET" and "friends_search" in request.GET:
        searchForm = SearchForm(request.GET)

        # 送信内容があった場合
        if searchForm.is_valid():
            keyword = searchForm.cleaned_data.get("keyword")
            # 何も入力せずに検索した時に全件を表示するようにするため、分岐しておく
            if keyword:
                # 入力に対して部分一致する友達を絞り込む
                friends = friends.filter(
                    Q(username__icontains=keyword)            # ユーザーネームの部分一致
                    | Q(email__icontains=keyword)             # メールアドレスの部分一致
                    | Q(latest_msg_talk__icontains=keyword)   # 最新のトーク内容の部分一致
                )

            

                # friendsに何らか情報があったとき
                context = {
                    "friends": friends,
                    "searchForm": searchForm,
                }
                return render(request, "myapp/friends.html", context)
    
    
    context = {
        "friends": friends,
        "searchForm": searchForm,
    }
    return render(request, "myapp/friends.html", context)

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