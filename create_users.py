import os
import random 

import django
from dateutil import tz
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intern.settings")
django.setup()

from myapp.models import Chat, CustomUser

fakegen = Faker(["ja_JP"])

def create_users(n):
    users = [
        CustomUser(username=fakegen.user_name(), email=fakegen.ascii_safe_email())
        for _ in range(n)
    ]
    
    CustomUser.objects.bulk_create(users, ignore_conflicts=True)
    
    
    my_id = CustomUser.objects.get(username="admin").id
   
    user_ids = CustomUser.objects.exclude(id=my_id).values_list("id", flat=True)
    
    chats = []
    
    for _ in range(len(user_ids)):
        sent_chat = Chat(
            sender_id=my_id,
            receiver_id=random.choice(user_ids),
            content=fakegen.text(),
        )
        received_chat = Chat(
            sender_id=random.choice(user_ids),
            receiver_id=my_id,
            content=fakegen.text()
        )
        chats.extend([sent_chat, received_chat])
    Chat.objects.bulk_create(chats, ignore_conflicts=True)
    
    chats = Chat.objects.order_by("-created_at")[:2 * len(user_ids)]
    for chat in chats:
        chat.time = fakegen.date_time_this_year(tzinfo=tz.gettz("Asia/Tokyo"))
    Chat.objects.bulk_update(chats, fields=["created_at"])
    
if __name__ == "__main__":
    print("creating users ...", end="")
    create_users(1000)
    print("done")