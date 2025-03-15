from django.contrib.auth.hashers import check_password
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=100)  # 实际应用中应使用更安全的密码存储方式

    def __str__(self):
        return self.name
    def check_password(self, raw_password):
        """验证密码是否正确"""
        return check_password(raw_password, self.password)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class Administrator(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_psw = models.CharField(max_length=10)  # 实际应用中应使用更安全的密码存储方式

    def __str__(self):
        return f"Admin {self.admin_id}"


class Poll(models.Model):
    poll_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='polls')
    title = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    cut_off = models.DurationField()  # 投票截止时间
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Option(models.Model):
    option_id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    content = models.CharField(max_length=20)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.content
