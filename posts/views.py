from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment


@cache_page(20)
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
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
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
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    return render(
        request,
        "post.html",
        {
            "post": post,
            "author": author,
            "posts": posts,
            "form": form,
            "comments": comments,
        }
    )


@login_required()
def post_edit(request, username, post_id):
    edit_title = "Редактирование записи"
    edit_button = "Сохранить"
    edit_header = "Редактировать запись"
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
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
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect("post", username=post.author, post_id=post.pk)
    return render(
        request,
        "post",
        {
            "post": post,
            "form": form,
        },
    )


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
