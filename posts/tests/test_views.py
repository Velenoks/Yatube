import shutil
import tempfile
from unittest.mock import MagicMock
from django.conf import settings
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, Follow
from django.contrib.auth.models import User
from django.core.cache import cache
from io import BytesIO
from PIL import Image


class PreparationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='Witcher')
        self.user1 = User.objects.create_user(username='Geralt')
        self.user2 = User.objects.create_user(username='Ciri')
        self.group = Group.objects.create(
            title='Тестовая гуппа',
            slug='test_group',
            description='Эта группа используется для тестирования')
        self.file = MagicMock(spec=File, name='FileMock')
        self.authorized_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1.force_login(self.user1)
        self.post_user2 = Post.objects.create(
            author=self.user2,
            text='Новый пост Ciri')
        self.follow = Follow.objects.create(
            user=self.user1,
            author=self.user2)
        self.unauthorized_client = Client()
        self.index_url = reverse('index')
        self.follow_url = reverse('follow_index')
        self.profile_url = reverse('profile', args=[self.user.username])
        self.group_url = reverse('group', args=[self.group.slug])
        self.urls_list = [
            self.index_url,
            self.profile_url,
            self.group_url,
        ]


class PostTest(PreparationTests):
    def test_new_post(self):
        """Проверка на добавление поста."""
        current_posts_count = Post.objects.count()
        text_post = 'Текст новой публикации'
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': text_post,
             'group': self.group.id,
             },
            follow=True)
        post_check = Post.objects.filter(text=text_post)[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count + 1)
        self.assertEqual(post_check.text, text_post)
        self.assertEqual(post_check.group, self.group)
        self.assertEqual(post_check.author, self.user)

    def test_new_post_check(self):
        """Проверяем наличие поста на нескольких страницах. 
        На странице главной, пользователя, отдельного поста
        """
        post = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=self.group)
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        self.url_test(post, urls_list)

    def test_post_edit(self):
        """Проверяем редактируемость поста."""
        cache.clear()
        post = Post.objects.create(
            author=self.user,
            text='Новый пост')
        post_edit = self.authorized_client.post(
            reverse('post_edit', args=[self.user.username, post.id]),
            {'text': 'Новый текст поста',
             'group': self.group.id,
             },
            follow=True)
        post = Post.objects.filter(text='Новый текст поста')[0]
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        self.url_test(post, urls_list)

    def url_test(self, post, urls_list):
        for url in urls_list:
            with self.subTest(i=url):
                cache.clear()
                webpage = self.unauthorized_client.get(url)
                if 'paginator' in webpage.context.keys():
                    post_web = webpage.context['page'].object_list[0]
                else:
                    post_web = webpage.context['post']
                self.assertEqual(post.text, post_web.text)
                self.assertEqual(post.author, post_web.author)
                self.assertEqual(post.group, post_web.group)


class UrlTest(PreparationTests):
    def test_new_post(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse('group', args=[self.group.slug]),
            'profile.html': reverse('profile', args=[self.user.username]),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class FileTest(PreparationTests):
    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def test_image_add(self):
        """Проверяем добавление картинки."""
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'Добавляем картинку',
             'group': self.group.id,
             'image': self.get_image_file('image.png'),
             },
            follow=True)
        post = Post.objects.filter(text='Добавляем картинку')[0]
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        cache.clear()
        for url in self.urls_list:
            with self.subTest(i=url):
                webpage = self.unauthorized_client.get(url)
                self.assertContains(webpage, "<img")

    def test_not_image_add(self):
        """Проверяем защиту от другого формата."""
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'Добавляем картинку',
             'group': self.group.id,
             'image': self.file,
             },
            follow=True)
        self.assertFormError(response, 'form', 'image',
                             'Загрузите правильное изображение. '
                             + 'Файл, который вы загрузили, '
                             + 'поврежден или не является изображением.')

    def test_cash(self):
        """Проверяем работу кэша."""
        text = 'Проверяем работу кэш'
        webpage = self.unauthorized_client.get(self.index_url)
        post = Post.objects.create(
            author=self.user,
            text=text,
            group=self.group
        )
        webpage = self.unauthorized_client.get(self.index_url)
        self.assertNotIn(text, webpage.content.decode('UTF-8'))
        cache.clear()
        webpage = self.unauthorized_client.get(self.index_url)
        self.assertEqual(text, webpage.context['page'].object_list[0].text)


class FollowTest(PreparationTests):
    def test_follow(self):
        """Проверяем подписку."""
        url_follow = reverse('profile_follow', args=[self.user1.username])
        self.authorized_client.get(url_follow)
        self.assertEqual(Follow.objects.filter(user=self.user,
                                               author=self.user1).count(), 1)

    def test_unfollow(self):
        """Проверяем отписку."""
        url_unfollow = reverse('profile_unfollow', args=[self.user1.username])
        self.authorized_client.get(url_unfollow)
        self.assertEqual(Follow.objects.filter(user=self.user,
                                               author=self.user1).count(), 0)

    def test_subscription(self):
        """Проверка нового поста у подписчика."""
        follow_url = self.authorized_client1.get(self.follow_url)
        post_follow = follow_url.context['page'].object_list[0]
        self.assertEqual(post_follow, self.post_user2)

    def test_unsubscription(self):
        """Проверяем отсутсвие нового поста у неподписанного пользователя"""
        cache.clear()
        unfollow_url = self.authorized_client.get(self.follow_url)
        post_unfollow = unfollow_url.context['page'].object_list.count()
        self.assertEqual(post_unfollow, 0)
