from datetime import timedelta

from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import jwt
import datetime
from django.conf import settings

class CustomerToken(Token):
    """自定义令牌类，用于为Customer模型生成令牌"""
    token_type = 'access'
    lifetime = timedelta(hours=1)


def get_tokens_for_customer(customer):
    """为Customer生成访问和刷新令牌"""
    # 创建访问令牌
    access = CustomerToken()
    # 添加自定义声明
    access['user_id'] = customer.customer_id
    access['name'] = customer.name
    access['email'] = customer.email
    access['token_type'] = 'access'

    # 创建刷新令牌
    refresh = CustomerToken()
    refresh['user_id'] = customer.customer_id
    refresh['token_type'] = 'refresh'

    return {
        'access': str(access),
        'refresh': str(refresh),
    }


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 添加自定义声明
        token['user_id'] = user.customer_id
        token['name'] = user.name
        token['email'] = user.email

        return token


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


def generate_token(user):
    """生成访问令牌和刷新令牌"""
    # 设置访问令牌有效期为1小时
    access_payload = {
        'user_id': user.customer_id,
        'name': user.name,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }

    # 设置刷新令牌有效期为7天
    refresh_payload = {
        'user_id': user.customer_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }

    # 生成令牌
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )

    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )

    return {
        'access': access_token,
        'refresh': refresh_token
    }