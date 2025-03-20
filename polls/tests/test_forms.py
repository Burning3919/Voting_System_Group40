# polls/tests/test_forms.py
from django.test import TestCase
from polls.forms import CustomerRegistrationForm, CustomerLoginForm


class CustomerRegistrationFormTest(TestCase):
    def test_valid_form(self):
        """测试有效的注册表单"""
        data = {
            'name': '测试用户',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        form = CustomerRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """测试密码不匹配的情况"""
        data = {
            'name': '测试用户',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }
        form = CustomerRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('密码不匹配', form.errors.get('__all__', []))