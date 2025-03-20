# polls/tests/test_cache.py
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from unittest import mock
from polls.models import Customer, Poll, Option
from polls.cache import get_poll_from_cache, set_poll_to_cache, increment_option_count


# 模拟 Redis
class MockRedis:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        return True

    def expire(self, key, time):
        return True

    def delete(self, key):
        if key in self.data:
            del self.data[key]
        return True


class CacheTest(TestCase):
    @mock.patch('polls.cache.redis_client', MockRedis())
    def setUp(self):
        self.customer = Customer.objects.create(
            name='缓存用户',
            email='cache@example.com',
            password=make_password('password123')
        )

        self.poll = Poll.objects.create(
            customer=self.customer,
            title="缓存测试投票",
            active=True
        )

        # 投票数据格式
        self.poll_data = {
            'poll_id': self.poll.poll_id,
            'title': '缓存测试投票',
            'active': True,
            'options': []
        }

    @mock.patch('polls.cache.redis_client', MockRedis())
    def test_set_and_get_poll_cache(self):
        """测试缓存投票数据的设置和获取"""
        # 设置缓存中的投票数据
        set_poll_to_cache(self.poll.poll_id, self.poll_data)

        # 从缓存获取投票数据
        cached_data = get_poll_from_cache(self.poll.poll_id)

        self.assertEqual(cached_data, self.poll_data)