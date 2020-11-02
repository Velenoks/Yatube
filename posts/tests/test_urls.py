from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Witcher')
        self.authorized_client = Client()        
        self.authorized_client.force_login(self.user)
        self.unauthorized_client = Client()

    def test_homepage(self):
        """Делаем запрос к главной странице и проверяем статус."""
        response = self.unauthorized_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_force_login(self):
        """Делаем запрос к странице /new/ и проверяем статус."""
        response = self.authorized_client.get(reverse('new_post'))      
        self.assertEqual(response.status_code, 200)

    def test_new_profile(self):
        """Делаем запрос к странице пользователя и проверяем статус."""
        response = self.authorized_client.get(
            reverse('profile', args=[self.user.username]))      
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_newpage(self):
        """Тестируем редирект: правильно ли идёт переадресация."""
        response = self.unauthorized_client.get(reverse('new_post'))
        self.assertRedirects(
            response,
            '/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200,)
