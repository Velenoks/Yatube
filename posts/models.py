from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Имя группы",
        help_text="Придумайте название группы",
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name="URL",
        help_text="Придумайте URL группы",
        max_length=50,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание группы",
    )

    class Meta:
        ordering = ("title",)
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
    )
    image = models.ImageField(
        upload_to="posts/",
        verbose_name="Картинка",
        blank=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Пост",
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comments",
    )
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_follow"),
        ]
