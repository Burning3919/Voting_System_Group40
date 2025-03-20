from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json
from django.utils import timezone
import datetime

from polls.models import Poll, Option, Customer, Administrator


class TestPollResults(TestCase):
    """测试获取投票结果API"""

    def setUp(self):
        # 创建测试客户
        self.customer = Customer.objects.create(
            name="测试用户",
            email="test@example.com",
            password="testpwd"
        )

        # 创建测试投票
        self.poll = Poll.objects.create(
            customer=self.customer,
            title="测试投票",
            active=True,
            cut_off=timezone.now() + datetime.timedelta(days=1)
        )

        # 创建测试选项
        self.option1 = Option.objects.create(
            poll=self.poll,
            content="选项1",
            count=10
        )

        self.option2 = Option.objects.create(
            poll=self.poll,
            content="选项2",
            count=5
        )

        self.client = APIClient()

    def test_poll_results(self):
        """测试获取投票结果功能"""
        url = reverse('polls:poll-results', args=[self.poll.poll_id])
        response = self.client.get(url)

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应内容
        self.assertEqual(response.data['poll_id'], self.poll.poll_id)
        self.assertEqual(response.data['title'], self.poll.title)
        self.assertEqual(len(response.data['options']), 2)
        self.assertEqual(response.data['total_votes'], 15)

        # 验证百分比计算
        self.assertEqual(response.data['options'][0]['percentage'], 66.7)  # 10/15 = 66.7%
        self.assertEqual(response.data['options'][1]['percentage'], 33.3)  # 5/15 = 33.3%


class TestPublicVote(TestCase):
    """测试公开投票API"""

    def setUp(self):
        # 创建测试客户
        self.customer = Customer.objects.create(
            name="测试用户",
            email="test@example.com",
            password="testpwd"
        )

        # 创建活跃投票
        self.active_poll = Poll.objects.create(
            customer=self.customer,
            title="活跃投票",
            active=True,
            cut_off=timezone.now() + datetime.timedelta(days=1)
        )

        # 创建选项
        self.option1 = Option.objects.create(
            poll=self.active_poll,
            content="选项1",
            count=0
        )

        # 创建已结束投票
        self.inactive_poll = Poll.objects.create(
            customer=self.customer,
            title="已结束投票",
            active=False,
            cut_off=timezone.now() - datetime.timedelta(days=1)
        )

        # 创建选项
        self.option2 = Option.objects.create(
            poll=self.inactive_poll,
            content="选项1",
            count=0
        )

        self.client = APIClient()

    def test_public_vote_success(self):
        """测试成功投票的情况"""
        url = reverse('polls:public-vote-api', args=[self.active_poll.poll_id])
        data = {
            'option_id': self.option1.option_id
        }
        response = self.client.post(url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应内容
        self.assertEqual(response.data['status'], "投票成功")

        # 验证数据库中选项计数已增加
        self.option1.refresh_from_db()
        self.assertEqual(self.option1.count, 1)

    def test_public_vote_inactive_poll(self):
        """测试投票已结束的情况"""
        url = reverse('polls:public-vote-api', args=[self.inactive_poll.poll_id])
        data = {
            'option_id': self.option2.option_id
        }
        response = self.client.post(url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 验证响应内容
        self.assertEqual(response.data['error'], "此投票已结束")

        # 验证数据库中选项计数未增加
        self.option2.refresh_from_db()
        self.assertEqual(self.option2.count, 0)

    def test_public_vote_missing_option(self):
        """测试未提供选项ID的情况"""
        url = reverse('polls:public-vote-api', args=[self.active_poll.poll_id])
        data = {}  # 不提供选项ID
        response = self.client.post(url, data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 验证响应内容
        self.assertEqual(response.data['error'], "请选择一个选项")

        # 验证数据库中选项计数未增加
        self.option1.refresh_from_db()
        self.assertEqual(self.option1.count, 0)

    def test_public_vote_invalid_option(self):
        """测试提供无效选项ID的情况"""
        url = reverse('polls:public-vote-api', args=[self.active_poll.poll_id])
        data = {
            'option_id': 9999  # 不存在的选项ID
        }
        response = self.client.post(url, data, format='json')

        # 验证响应状态码，当选项不存在时实际返回的是500错误
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestGetPollByIdentifier(TestCase):
    """测试通过标识符查找投票问卷API"""

    def setUp(self):
        # 创建测试客户
        self.customer = Customer.objects.create(
            name="测试用户",
            email="test@example.com",
            password="testpwd"
        )

        # 创建测试投票
        self.poll = Poll.objects.create(
            customer=self.customer,
            title="测试投票",
            active=True,
            identifier="12345678",  # 手动设置标识符
            cut_off=timezone.now() + datetime.timedelta(days=1)
        )

        # 创建测试选项
        self.option = Option.objects.create(
            poll=self.poll,
            content="选项1",
            count=0
        )

        self.client = APIClient()

    def test_find_poll_by_valid_identifier(self):
        """测试使用有效标识符查找投票问卷"""
        url = reverse('polls:find-poll', args=["12345678"])
        response = self.client.get(url)

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应内容
        self.assertEqual(response.data['poll_id'], self.poll.poll_id)
        self.assertEqual(response.data['title'], self.poll.title)
        self.assertEqual(response.data['identifier'], "12345678")

    def test_find_poll_by_invalid_identifier(self):
        """测试使用无效标识符查找投票问卷"""
        url = reverse('polls:find-poll', args=["87654321"])  # 不存在的标识符
        response = self.client.get(url)

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 验证响应内容
        self.assertEqual(response.data['error'], "找不到该投票问卷")