# polls/tests/test_urls.py

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from polls.views import (
    RegisterAPIView, LoginAPIView, PollCreateAPIView,
    UserPollsAPIView, api_admin_login, public_vote
)


class UrlsTest(SimpleTestCase):
    def test_register_url_resolves(self):
        """测试注册URL解析到正确的视图"""
        url = reverse('polls:register')
        self.assertEqual(resolve(url).func.view_class, RegisterAPIView)

    def test_login_url_resolves(self):
        """测试登录URL解析到正确的视图"""
        url = reverse('polls:login')
        self.assertEqual(resolve(url).func.view_class, LoginAPIView)

    def test_poll_create_url_resolves(self):
        """测试创建投票URL解析到正确的视图"""
        url = reverse('polls:poll-create')
        self.assertEqual(resolve(url).func.view_class, PollCreateAPIView)

    def test_user_polls_url_resolves(self):
        """测试用户投票URL解析到正确的视图"""
        url = reverse('polls:my-polls')
        self.assertEqual(resolve(url).func.view_class, UserPollsAPIView)

    def test_admin_login_url_resolves(self):
        """测试管理员登录URL解析到正确的视图"""
        url = reverse('polls:api_admin_login')
        self.assertEqual(resolve(url).func, api_admin_login)

    def test_public_vote_url_resolves(self):
        """测试公开投票URL解析到正确的视图"""
        url = reverse('polls:public-vote-api', kwargs={'poll_id': 1})
        self.assertEqual(resolve(url).func, public_vote)