from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
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


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
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
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
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
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, 
        "profile.html", 
        {
            "author": author, 
            "page": page, 
            "paginator": paginator,
            },
        )

 
def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    posts = Post.objects.filter(author=author).count()
    return render(
        request, 
        "post.html", 
        {
            "post": post,
            "author": author, 
            "posts": posts
            }
        )


@login_required()
def post_edit(request, username, post_id):
    edit_title = "Редактирование записи"
    edit_button = "Сохранить"
    edit_header = "Редактировать запись"
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("post", username=post.author, post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
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
