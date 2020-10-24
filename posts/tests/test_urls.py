from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post


User = get_user_model()


class StaticURLTests(TestCase):
    # Метод класса должен быть декорирован
    @classmethod
    def setUpClass(cls):
        # Вызываем родительский метод, чтобы не перезаписывать его полностью, а расширить
        super().setUpClass()
        # Устанавливаем данные для тестирования
        # Создаём пользователя
        cls.user = User.objects.create_user(username='StasBasov')
        # Создаем клиент и авторизуем пользователя
        cls.authorized_client = Client()        
        cls.authorized_client.force_login(cls.user)
        # Создаём второй клиент, без авторизации
        cls.unauthorized_client = Client()

    def test_homepage(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.unauthorized_client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_force_login(self):
        # Делаем запрос к странице /new/ и проверяем статус
        response = self.authorized_client.get('/new/')      
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        # Определим текущее количество записей в модели Post
        current_posts_count = Post.objects.count()
        # Создаём новую публикацию, отправляя данные POST-запросом
        # Разрешаем редирект после отправки данных
        response = self.authorized_client.post(
            '/new/', 
            {'text': 'Это текст публикации'}, 
            follow=True,
            )
        # Проверим, что после размещения поста клиент был успешно перенаправлен        
        self.assertEqual(response.status_code, 200)
        # Убедимся, что в базе стало на одну публикацию больше, чем было
        self.assertEqual(Post.objects.count(), current_posts_count + 1)

    def test_unauthorized_user_newpage(self):
        response = self.unauthorized_client.get('/new/')
        # Тестируем редирект: правильно ли идёт переадресация и правильный ли статус
        self.assertRedirects(
            response,
            '/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200,
            )

