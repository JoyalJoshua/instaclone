from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required(login_url="login")
def feed(request):
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)

    posts = Post.objects.filter(
        user__in=following_users
    ).order_by('-created_at') | Post.objects.filter(user=request.user)

    liked_posts = Like.objects.filter(
        user=request.user
    ).values_list('post_id', flat=True)

    return render(request, "core/feed.html", {
        "posts": posts,
        "liked_posts": liked_posts
    })





def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, "core/signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("feed")

    return render(request, "core/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("feed")
        else:
            return render(request, "core/login.html", {"error": "Invalid credentials"})

    return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")


# End of file instaclone/core/views.py
#profile signal file

from .models import Profile

@login_required(login_url="login")
def profile(request):
    profile = Profile.objects.get(user=request.user)
    posts = Post.objects.filter(user=request.user)
    return render(request, "core/profile.html", {
        "profile": profile,
        "posts": posts
    })


#upload view
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def upload(request):
    if request.method == "POST":
        image = request.FILES['image']
        caption = request.POST.get('caption', '')

        Post.objects.create(
            user=request.user,
            image=image,
            caption=caption
        )
        return redirect("feed")

    return render(request, "core/upload.html")

# End of file instaclone/core/views.py

#like view
from .models import Like
from django.shortcuts import get_object_or_404

@login_required(login_url="login")
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)

        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                notification_type="like",
                post=post
            )

    return redirect("feed")

# End of file instaclone/core/views.py

#follow view
from .models import Follow

from .models import Notification

@login_required(login_url="login")
def follow_toggle(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)

    if user_to_follow == request.user:
        return redirect("profile")

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).first()

    if follow:
        follow.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

        # 🔔 CREATE NOTIFICATION
        Notification.objects.create(
            sender=request.user,
            receiver=user_to_follow,
            notification_type="follow"
        )

    return redirect("user_profile", user_id=user_to_follow.id)


@login_required(login_url="login")
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user)

    is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    return render(request, "core/user_profile.html", {
        "profile_user": user,
        "profile": profile,
        "posts": posts,
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count
    })

# End of file instaclone/core/views.py

#edit profile view
@login_required(login_url="login")
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        profile.bio = request.POST.get("bio", "")
        profile.save()

        return redirect("profile")

    return render(request, "core/edit_profile.html", {"profile": profile})
# End of file instaclone/core/views.py

#comments view
from .models import Comment

@login_required(login_url="login")
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        text = request.POST.get("comment")

        if text:
            Comment.objects.create(
                user=request.user,
                post=post,
                text=text
            )

            if post.user != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    notification_type="comment",
                    post=post
                )

    return redirect("feed")

# End of file instaclone/core/views.py

#explore view
@login_required(login_url="login")
def explore(request):
    posts = Post.objects.all().order_by('-created_at')

    liked_posts = Like.objects.filter(
        user=request.user
    ).values_list('post_id', flat=True)

    return render(request, "core/explore.html", {
        "posts": posts,
        "liked_posts": liked_posts
    })
# End of file instaclone/core/views.py

#delete view
@login_required(login_url="login")
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Only owner can delete
    if post.user != request.user:
        return redirect("feed")

    post.delete()
    return redirect("feed")
# End of file instaclone/core/views.py

#notification view
@login_required(login_url="login")
def notifications(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by("-created_at")

    # Mark all as seen
    notifications.update(is_seen=True)

    return render(request, "core/notifications.html", {"notifications": notifications})
# End of file instaclone/core/views.py

#chat model view
from django.db.models import Q
from .models import Message

@login_required(login_url="login")
def inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    )

    users = {}

    for m in messages:
        if m.sender != request.user:
            other = m.sender
        else:
            other = m.receiver

        if other not in users:
            users[other] = 0

    # count unread messages
    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    )

    for m in unread_messages:
        if m.sender in users:
            users[m.sender] += 1

    return render(request, "core/inbox.html", {"users": users})



@login_required(login_url="login")
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("created_at")
    # Mark received messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get("message")
        image = request.FILES.get("image")

        if text or image:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text if text else "",
                image=image
            )

        return redirect("chat", user_id=other_user.id)


    return render(request, "core/chat.html", {
        "other_user": other_user,
        "messages": messages
    })
# End of file instaclone/core/views.py