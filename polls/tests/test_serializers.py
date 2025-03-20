from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from polls.models import Customer, Poll, Option, Administrator
from polls.serializers import (
    CustomerSerializer, CustomerProfileSerializer, PollSerializer,
    OptionSerializer, PollCreateSerializer, LoginSerializer,
    ChangePasswordSerializer
)
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request


class CustomerSerializerTest(TestCase):
    def setUp(self):
        self.customer_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securePassword123"
        }
        self.customer = Customer.objects.create(
            name="Existing User",
            email="existing@example.com",
            password=make_password("password123")
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')

    def test_validate_data(self):
        """Test serializer data validation"""
        serializer = CustomerSerializer(data=self.customer_data)
        self.assertTrue(serializer.is_valid())

    def test_create_customer(self):
        """Test customer creation through serializer"""
        serializer = CustomerSerializer(data=self.customer_data)
        serializer.is_valid()
        customer = serializer.save()

        self.assertEqual(customer.name, "Test User")
        self.assertEqual(customer.email, "test@example.com")
        # Password should be hashed, not stored as plaintext
        self.assertNotEqual(customer.password, "securePassword123")

    def test_profile_serializer(self):
        """Test customer profile serializer"""
        serializer = CustomerProfileSerializer(self.customer)
        data = serializer.data

        self.assertEqual(data['name'], "Existing User")
        self.assertEqual(data['email'], "existing@example.com")
        self.assertNotIn('password', data)


class OptionSerializerTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Poll Creator",
            email="creator@example.com",
            password="password123"
        )

        self.poll = Poll.objects.create(
            customer=self.customer,
            title="Test Poll",
            cut_off=timezone.now() + timedelta(days=7),
            active=True
        )

        self.option = Option.objects.create(
            poll=self.poll,
            content="Test Option",
            count=10
        )

    def test_option_serializer(self):
        """Test that option serializer correctly serializes data"""
        serializer = OptionSerializer(self.option)
        data = serializer.data

        self.assertEqual(data['option_id'], self.option.option_id)
        self.assertEqual(data['content'], "Test Option")
        self.assertEqual(data['count'], 10)


class PollSerializerTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Poll Creator",
            email="creator@example.com",
            password="password123"
        )

        self.poll = Poll.objects.create(
            customer=self.customer,
            title="Test Poll",
            cut_off=timezone.now() + timedelta(days=7),
            active=True,
            chart_type="pieChart"
        )

        self.option1 = Option.objects.create(
            poll=self.poll,
            content="Option 1",
            count=5
        )

        self.option2 = Option.objects.create(
            poll=self.poll,
            content="Option 2",
            count=10
        )

        self.factory = APIRequestFactory()

    def test_poll_serializer(self):
        """Test poll serializer with related options"""
        serializer = PollSerializer(self.poll)
        data = serializer.data

        self.assertEqual(data['poll_id'], self.poll.poll_id)
        self.assertEqual(data['title'], "Test Poll")
        self.assertEqual(data['chart_type'], "pieChart")
        self.assertTrue(data['active'])
        self.assertEqual(len(data['options']), 2)

        # Verify options are included
        option_contents = [opt['content'] for opt in data['options']]
        self.assertIn("Option 1", option_contents)
        self.assertIn("Option 2", option_contents)

    def test_poll_create_serializer(self):
        """测试创建投票序列化器"""
        # 创建模拟请求
        request = self.factory.post('/')

        # 关键修复：正确设置request.user为Customer实例
        request.user = self.customer  # 而不是默认的AnonymousUser

        poll_data = {
            "title": "New Poll",
            "cut_off": timezone.now() + timedelta(days=14),
            "chart_type": "barChart",
            "options": ["Choice A", "Choice B", "Choice C"]
        }

        serializer_context = {'request': request}
        serializer = PollCreateSerializer(data=poll_data, context=serializer_context)
        self.assertTrue(serializer.is_valid())

        # 现在customer是正确的Customer实例
        new_poll = serializer.save(customer=self.customer)

        self.assertEqual(new_poll.title, "New Poll")
        self.assertEqual(new_poll.chart_type, "barChart")

        # 检查选项是否创建
        options = Option.objects.filter(poll=new_poll)
        self.assertEqual(options.count(), 3)
class LoginSerializerTest(TestCase):
    def test_login_serializer_validation(self):
        """Test validation of login serializer"""
        data = {"email": "user@example.com", "password": "password123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Test invalid data
        invalid_data = {"email": "not-an-email", "password": ""}
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())