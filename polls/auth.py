from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import Customer


class CustomerAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 获取认证头
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        # 提取令牌
        token = auth_header.split(' ')[1]

        try:
            # 解码令牌
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )

            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('令牌无效')

            # 查询用户
            user = Customer.objects.filter(customer_id=user_id).first()
            if not user:
                raise AuthenticationFailed('用户不存在')

            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('令牌已过期')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('令牌无效')
        except Exception as e:
            raise AuthenticationFailed(f'认证失败: {str(e)}')