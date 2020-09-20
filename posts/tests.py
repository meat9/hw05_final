from django.test import TestCase, Client
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from users.forms import User
from .models import Post, Group, Follow, Comment


class ProfileTest(TestCase):


        def setUp(self):
                self.client = Client()
                self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
                self.client.login(username="sarah", password="12345")
                self.group = Group.objects.create(title='group_name', slug='sgroup', description='tests group from sarah')
                self.post = Post.objects.create(author=self.user, text='TEXT', group=self.group)
                with open('./media/posts/file.jpg', 'rb') as img:
                        self.client.post(f"/{self.user.username}/{self.post.id}/edit/",
                        {'author': self.user, 'text': 'TEXT', 'image': img, 'group': self.group.id})


        def test_profile(self):
                response = self.client.get(f"/{self.user.username}/")
                self.assertEqual(response.status_code, 200)


        def test_post(self):
                self.client.login(username="sarah", password="12345")
                response = self.client.get("/new/")
                self.assertEqual(str(response.context["user"]), "sarah")
                self.assertEqual(response.status_code, 200)


        def test_non_auth_user_creates_new_post(self):
                self.client.logout()      
                response = self.client.get("/new/")
                self.assertRedirects(response, "/auth/login/?next=/new/")


        def test_new_post_in_all_page(self):
                self.client.login(username="sarah", password="12345")
                response = self.client.get("/")
                self.assertContains(response, self.post.text, status_code=200)
                response = self.client.get(f"/{self.user.username}/")
                self.assertContains(response, self.post.text, status_code=200)
                response = self.client.get(f"/{self.user.username}/{self.post.id}/")
                self.assertContains(response, self.post.text, status_code=200)


        def test_edit_post_in_all_page(self):
                edit_post = "You are do not talking about things!"
                self.client.login(username="sarah", password="12345")
                response = self.client.post(f"/{self.user.username}/{self.post.id}/edit/", {"text": edit_post}, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, edit_post, status_code=200)
                response = self.client.get(f"/{self.user.username}/")
                self.assertContains(response, edit_post, status_code=200)
                response = self.client.get(f"/{self.user.username}/{self.post.id}/")
                self.assertContains(response, edit_post, status_code=200)


        def test_error404(self):
                response = self.client.get('/erfg454tg4y/')
                self.assertEqual(response.status_code, 404)


        def test_post_with_img(self):
                response = self.client.get("/")
                self.assertContains(response, '<img', status_code=200)
                response = self.client.get(f"/{self.user.username}/")
                self.assertContains(response, '<img', status_code=200)
                response = self.client.get(f"/{self.user.username}/{self.post.id}/")
                self.assertContains(response, '<img')
                response = self.client.get(f"/group/{self.group.slug}/")
                self.assertContains(response, '<img')


        def test_notimage_on_pages(self):
                with open('posts/file.txt', 'rb') as img:
                        self.client.post(f"/{self.user.username}/{self.post.id}/edit/", 
                        {'author': self.user, 'text': 'text', 'image': img}, follow=True)
                response = self.client.get(f"/{self.user.username}/{self.post.id}/edit/")
                self.assertNotContains(response, '<img', status_code=200)


        def test_cache(self):
                response = self.client.get("/")
                self.assertEqual(response.status_code, 200)
                key = make_template_fragment_key('index_page')
                cashe = cache.get(key)
                self.assertFalse(cashe is None)


        def test_following_unfollowing(self):
                user2 = User.objects.create_user(username="john", email="connor88.s@skynet.com", password="12345")
                post2 = Post.objects.create(author=user2, text='TEXT2')
                self.client.login(username="sarah", password="12345")
                response = self.client.get(f"/{user2.username}/follow/")
                Follow.objects.create(user=self.user, author=user2)
                response = self.client.get("/")
                response = self.client.get(f"/{user2.username}/")
                response = self.client.get("/follow/")
                self.assertContains(response, post2.text)
                Follow.objects.filter(user=self.user, author=user2).delete()
                response = self.client.get("/follow/")
                

        def test_comment_not_login_user(self):
                self.client.logout() 
                response = self.client.get(f"/{self.user.username}/{self.post.id}/comment")
                self.assertEqual(response.status_code, 301)
                response = self.client.get("/auth/login/")
                self.assertEqual(response.status_code, 200)


        def test_comment_login_user(self):
                self.client.login(username="sarah", password="12345")
                response = self.client.get(f"/{self.user.username}/{self.post.id}/comment/")
                comm = Comment.objects.create(post=self.post, author=self.user, text="test commenting")
                response = self.client.get(f"/{self.user.username}/{self.post.id}/")
                self.assertContains(response, comm.text)
