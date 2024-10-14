from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('friends', views.friends, name='friends'),
    path('talk_room/<int:pk>', views.talk_room, name='talk_room'),
    path('setting', views.setting, name='setting'),
    path("username_update/", views.username_update, name="username_update"),
    path("email_update/", views.email_update, name="email_update"),
    path("image_update/", views.image_update, name="image_update"),
    path('password_update/', views.PasswordChange.as_view(), name='password_update'),
    path('password_update/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
]
