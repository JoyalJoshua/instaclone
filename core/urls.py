from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name="feed"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('upload/', views.upload, name="upload"),
    path('like/<int:post_id>/', views.like_post, name="like"),
    path('user/<int:user_id>/', views.user_profile, name="user_profile"),
    path('follow/<int:user_id>/', views.follow_toggle, name="follow"),
    path('edit-profile/', views.edit_profile, name="edit_profile"),
    path('comment/<int:post_id>/', views.add_comment, name="add_comment"),
    path('explore/', views.explore, name="explore"),
    path('delete-post/<int:post_id>/', views.delete_post, name="delete_post"),
    path('notifications/', views.notifications, name="notifications"),
    path('inbox/', views.inbox, name="inbox"),
    path('chat/<int:user_id>/', views.chat, name="chat"),










]


