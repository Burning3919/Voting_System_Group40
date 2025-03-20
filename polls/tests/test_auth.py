from django.test import TestCase, RequestFactory
from rest_framework.exceptions import AuthenticationFailed
from polls.auth import CustomerAuthentication
from polls.models import Customer
from django.conf import settings
import jwt
import datetime

class CustomerAuthenticationTest(TestCase):
    def setUp(self):
        self.auth = CustomerAuthentication()
        self.factory = RequestFactory()
        self.user = Customer.objects.create(customer_id=1, name='Test User', email='test@example.com')
        self.valid_token = jwt.encode({'user_id': self.user.customer_id}, settings.SECRET_KEY, algorithm='HS256')
        self.invalid_token = 'invalid.jwt.token'
        self.expired_token = jwt.encode({
            'user_id': self.user.customer_id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        }, settings.SECRET_KEY, algorithm='HS256')

    def get_request(self, token):
        request = self.factory.get('/')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return request

    def test_no_authorization_header(self):
        request = self.factory.get('/')
        self.assertIsNone(self.auth.authenticate(request))

    def test_invalid_authorization_format(self):
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'InvalidHeaderWithoutBearer'
        self.assertIsNone(self.auth.authenticate(request))

    def test_invalid_jwt_token(self):
        request = self.get_request(self.invalid_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_expired_jwt_token(self):
        request = self.get_request(self.expired_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_valid_jwt_token(self):
        request = self.get_request(self.valid_token)
        user, _ = self.auth.authenticate(request)
        self.assertEqual(user, self.user)

    def test_non_existent_user(self):
        non_existent_token = jwt.encode({'user_id': 999}, settings.SECRET_KEY, algorithm='HS256')
        request = self.get_request(non_existent_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_empty_user_id(self):
        empty_user_token = jwt.encode({'user_id': None}, settings.SECRET_KEY, algorithm='HS256')
        request = self.get_request(empty_user_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_corrupt_jwt_token(self):
        request = self.get_request('corrupted.token')
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)