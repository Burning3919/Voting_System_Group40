from django.test import TestCase
from django.contrib.auth.hashers import make_password
from polls.models import Customer, Administrator, Poll, Option


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=1,
            name="John Doe",
            email="john@example.com",
            password=make_password("securepassword")
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "John Doe")

    def test_check_password_correct(self):
        self.assertTrue(self.customer.check_password("securepassword"))

    def test_check_password_incorrect(self):
        self.assertFalse(self.customer.check_password("wrongpassword"))

    def test_is_anonymous(self):
        self.assertFalse(self.customer.is_anonymous)

    def test_is_authenticated(self):
        self.assertTrue(self.customer.is_authenticated)


class AdministratorModelTest(TestCase):
    def setUp(self):
        self.admin = Administrator.objects.create(
            admin_id=1,
            admin_psw="admin123"
        )

    def test_admin_str(self):
        self.assertEqual(str(self.admin), f"Admin {self.admin.admin_id}")


class PollModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=1,
            name="Test User",
            email="test@example.com",
            password=make_password("password123")
        )
        self.poll = Poll.objects.create(customer=self.customer, title="Sample Poll")

    def test_create_poll(self):
        self.assertIsNotNone(self.poll.poll_id)

    def test_poll_str(self):
        self.assertEqual(str(self.poll), "Sample Poll")


class OptionModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=1,
            name="Test User",
            email="test@example.com",
            password=make_password("password123")
        )
        self.poll = Poll.objects.create(customer=self.customer, title="Sample Poll")
        self.option = Option.objects.create(poll=self.poll, content="Option 1")

    def test_option_str(self):
        self.assertEqual(str(self.option), "Option 1")
