from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('follow/', views.follow_index, name='follow_index'),
    path('users/', views.users_all, name='users'),
    path('groups_all/', views.groups_all, name='groups'),
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('<str:username>/', views.profile, name='profile'),
    path(
        '<str:username>/<int:post_id>/',
        views.post_view,
        name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'),
    path(
        '<str:username>/<int:post_id>/delete/',
        views.post_delete,
        name='post_delete'),
    path(
        '<str:username>/<int:post_id>/comment',
        views.add_comment,
        name='add_comment'),
    path(
        '<str:username>/<int:post_id>/<int:comment_id>/delete_comment',
        views.delete_comment,
        name='delete_comment'),
    path('<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('<str:username>/unfollow/', views.profile_unfollow,
         name='profile_unfollow'),
]
