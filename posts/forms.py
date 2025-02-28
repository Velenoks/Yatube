from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Добавить изображение',
        }
        help_texts = {
            'text': 'Можешь здесь писать все, что хочешь :)',
            'group': 'Группу выбирать не обязательно',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
