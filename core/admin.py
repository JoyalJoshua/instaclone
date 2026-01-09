from django.contrib import admin

# Register your models here.


from .models import Post, Profile, Like, Follow, Comment, Notification
from .models import Message

admin.site.register(Message)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Notification)
