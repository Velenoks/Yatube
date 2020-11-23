from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.db import IntegrityError

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


@cache_page(1 * 20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all().select_related(
        'author', 'group'
    ).annotate(
        count_comments=Count('comments'),
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "page": page,
            "paginator": paginator,
        },
    )


@cache_page(1 * 20, key_prefix="users_all")
def users_all(request):
    users = User.objects.all().order_by("username")
    return render(
        request,
        "users.html",
        {
            "users": users,
        },
    )


@cache_page(1 * 60, key_prefix="groups_all")
def groups_all(request):
    groups = Group.objects.all()
    return render(
        request,
        "groups.html",
        {
            "groups": groups,
        },
    )


@cache_page(1 * 20, key_prefix="group_page")
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.prefetch_related(
        'author', 'group'
    ).all().annotate(
        count_comments=Count('comments'),
    ).order_by('-pub_date')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {
            "group": group,
            "page": page,
            "paginator": paginator,
        },
    )


@login_required()
def new_post(request):
    new_title = "Новая запись"
    new_button = "Добавить"
    new_header = "Добавить запись"
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect("index")
    return render(
        request,
        "new_post.html",
        {
            "form": form,
            "title": new_title,
            "button": new_button,
            "header": new_header,
        },
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related(
        'author',
        'group',
    ).filter(author=author).annotate(
        count_comments=Count('comments'),
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    subscribers = Follow.objects.filter(author=author).count()
    signed = Follow.objects.filter(user=author).count()
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    return render(
        request,
        "profile.html",
        {
            "author": author,
            "page": page,
            "paginator": paginator,
            "subscribers": subscribers,
            "signed": signed,
            "following": following,
        },
    )


def post_view(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=username)
    author = post.author
    posts = Post.objects.filter(author=author).count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.prefetch_related(
        'author',
    ).filter(
        post=post
    )
    subscribers = Follow.objects.filter(author=username).count()
    signed = Follow.objects.filter(user=username).count()
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=username).exists():
            following = True
    return render(
        request,
        "post.html",
        {
            "post": post,
            "author": author,
            "posts": posts,
            "form": form,
            "comments": comments,
            "subscribers": subscribers,
            "signed": signed,
            "following": following,
        }
    )


@login_required()
def post_edit(request, username, post_id):
    edit_title = "Редактирование записи"
    edit_button = "Сохранить"
    edit_header = "Редактировать запись"
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=username)
    if post.author != request.user:
        return redirect("post", username=post.author, post_id=post.pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.save()
        return redirect("post", username=post.author, post_id=post.pk)
    return render(
        request,
        "new_post.html",
        {
            "post": post,
            "form": form,
            "title": edit_title,
            "button": edit_button,
            "header": edit_header,
        },
    )


@login_required()
def post_delete(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=username)
    post.delete()
    return redirect("profile", username=username)


@login_required()
def add_comment(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user_profile)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect("post", username=post.author, post_id=post.pk)
    return redirect("post", username=post.author, post_id=post.pk)


@login_required()
def delete_comment(request, username, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect("post", username=username, post_id=post_id)


@login_required
@cache_page(1 * 20, key_prefix="index_page")
def follow_index(request):
    posts = Post.objects.select_related(
        'author',
        'group',
    ).filter(
        author__following__user=request.user
    ).annotate(
        count_comments=Count('comments'),
    ).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {
            "page": page,
            "paginator": paginator,
        },
    )


@login_required
def profile_follow(request, username):
    user_profile = get_object_or_404(User, username=username)
    if user_profile != request.user:
        try:
            new_follow = Follow.objects.create(
                user=request.user,
                author=user_profile)
            return redirect("profile", username=username)
        except IntegrityError:
            return redirect("profile", username=username)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    user_profile = get_object_or_404(User, username=username)
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author=user_profile)
    follow.delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        "misc/500.html",
        status=500
    )
