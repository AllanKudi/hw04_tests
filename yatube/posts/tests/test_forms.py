from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Авторизованный пользователь'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Измененный текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text']
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма со страницы edit изменяет пост в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Измененный текст 2',
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_edit, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                group=form_data['group'],
                text=form_data['text']
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)
