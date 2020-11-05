from unittest.mock import MagicMock
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


class PostsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Witcher')
        self.group = Group.objects.create(
            title='Тестовая гуппа',
            slug='test_group',
            description='Эта группа используется для тестирования')
        self.image = SimpleUploadedFile(
            name='test.jpg',
            content=open('media/test.jpg', 'rb').read(),
            content_type='image/jpeg')
        self.file = MagicMock(spec=File, name='FileMock')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.unauthorized_client = Client()
        self.index_url = reverse('index')
        self.profile_url = reverse('profile', args=[self.user.username])
        self.group_url = reverse('group', args=[self.group.slug])
        self.urls_list = [
            self.index_url,
            self.profile_url,
            self.group_url,
        ]

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
        post_check = Post.objects.filter(pk=1)[0]
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
            group=self.group
        )
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        self.url_test(post, urls_list)

    def test_post_edit(self):
        """Проверяем редактируемость поста."""
        post = Post.objects.create(
            author=self.user,
            text='Новый пост',
        )
        post_edit = self.authorized_client.post(
            reverse('post_edit', args=[self.user.username, post.id]),
            {'text': 'Новый текст поста',
             'group': self.group.id,
             },
            follow=True, )
        post = Post.objects.filter(text='Новый текст поста')[0]
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        self.url_test(post, urls_list)

    def test_image_add(self):
        """Проверяем добавление картинки."""
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'Добавляем картинку',
             'group': self.group.id,
             'image': self.image,
             },
            follow=True)
        post = Post.objects.filter(text='Добавляем картинку')[0]
        post_url = reverse('post', args=[self.user.username, post.id])
        urls_list = self.urls_list
        urls_list.append(post_url)
        cache.clear()
        for url in self.urls_list:
            webpage = self.unauthorized_client.get(url)
            self.assertContains(webpage, "<img")

    def test_not_image_add(self):
        """Проверяем защиту от другого формата."""
        current_posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'Добавляем картинку',
             'group': self.group.id,
             'image': self.file,
             },
            follow=True)
        self.assertEqual(Post.objects.count(), current_posts_count)

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


    def url_test(self, post, urls_list):
        for url in urls_list:
            cache.clear()
            webpage = self.unauthorized_client.get(url)
            if 'paginator' in webpage.context.keys():
                post_web = webpage.context['page'].object_list[0]
            else:
                post_web = webpage.context['post']
            self.assertEqual(post.text, post_web.text)
            self.assertEqual(post.author, post_web.author)
            self.assertEqual(post.group, post_web.group)
