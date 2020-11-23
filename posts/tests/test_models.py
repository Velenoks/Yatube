from django.test import TestCase
from django.contrib.auth.models import User
from posts.models import Post, Group


class StaticURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Witcher')
        self.post_user = Post.objects.create(
            author=self.user,
            text='Новый пост Witcher')
        self.group = Group.objects.create(
            title='Тестовая гуппа',
            slug='test_group',
            description='Эта группа используется для тестирования')

    def test_verbose_name_post(self):
        """verbose_name в Post совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    self.post_user._meta.get_field(
                        value).verbose_name, expected)

    def test_verbose_name_group(self):
        """verbose_name в Group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Имя группы',
            'slug': 'URL',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    self.group._meta.get_field(
                        value).verbose_name, expected)

    def test_str_post(self):
        """Проверяем работу метода str у модели Post."""
        post_name = self.post_user.text[:15]
        self.assertEquals(post_name, str(self.post_user))

    def test_str_group(self):
        """Проверяем работу метода str у модели Group."""
        group_name = self.group.title
        self.assertEquals(group_name, str(self.group))
