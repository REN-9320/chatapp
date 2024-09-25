from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    image = models.ImageField()
    
class Chat(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver")
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    
    def __str__(self):
        return f"FROM:{self.sender} TO:{self.receiver} {self.content}"