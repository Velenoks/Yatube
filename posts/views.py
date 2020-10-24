import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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
        {"page": page, "paginator": paginator},
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
        {"group": group, "page": page, "paginator": paginator},
        )


@login_required()
def new_post(request):
    new_title = "Новая запись"
    new_button = "Добавить"
    new_header = "Добавить запись"
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("index")
        return render(
            request, 
            "new_post.html", 
            {"form": form, "new_title": new_title, "new_button": new_button,"new_header": new_header},
            )
    form = PostForm()
    return render(
        request, 
        "new_post.html", 
        {"form": form, "new_title": new_title, "new_button": new_button,"new_header": new_header},
        )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    posts = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, 
        "profile.html", 
        {"posts": posts, "page": page, "paginator": paginator},
        )

 
def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post_one = Post.objects.filter(id=post_id)
    posts = Post.objects.filter(author=user).count()
    return render(
        request, 
        "post.html", 
        {"posts": posts, "post_one": post_one}
        )


@login_required()
def post_edit(request, username, post_id):
    edit_title = "Редактирование записи"
    edit_button = "Сохранить"
    edit_header = "Редактировать запись"
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("post", username=post.author, post_id=post.pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.pub_date = dt.datetime.now()
            post.save()
            return redirect("index")
        return render(
            request, 
            "new_post.html", 
            {"form": form, "edit_title": edit_title, "edit_button": edit_button,"edit_header": edit_header},
            )
    else:
        form = PostForm(instance=post)
    return render(
        request, 
        "new_post.html", 
        {"form": form, "edit_title": edit_title, "edit_button": edit_button,"edit_header": edit_header},
        )
