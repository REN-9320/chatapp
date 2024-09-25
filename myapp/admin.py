from django.contrib import admin
from .models import CustomUser, Chat
# Register your models here.

admin.site.register(CustomUser)

admin.site.register(Chat)