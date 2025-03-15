from django.http import Http404
from .jwt import get_tokens_for_customer, generate_token

from .serializers import (
    CustomerSerializer, PollSerializer, OptionSerializer,
    AdministratorSerializer, CustomerProfileSerializer,
    ChangePasswordSerializer, LoginSerializer
)
from django.views.generic import TemplateView
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404

from .models import Customer, Poll, Option, Administrator

from .cache import get_poll_from_cache, set_poll_to_cache, increment_option_count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from .models import Customer
from .jwt import generate_token
# 保留原有的ViewSet...

# 用户注册API
class RegisterAPIView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 创建JWT令牌，使用自定义函数
        tokens = generate_token(user)

        return Response({
            'user': CustomerProfileSerializer(user).data,
            'refresh': tokens['refresh'],
            'access': tokens['access'],
        }, status=status.HTTP_201_CREATED)




# 用户登录API
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = Customer.objects.get(email=serializer.validated_data['email'])
            if user.check_password(serializer.validated_data['password']):
                tokens = generate_token(user)
                return Response({
                    'user': CustomerProfileSerializer(user).data,
                    'refresh': tokens['refresh'],
                    'access': tokens['access'],
                    'user_id': user.customer_id,
                    'name': user.name
                })
            else:
                return Response({'error': '密码不正确'}, status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


# 用户个人资料API
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # self.request.user 现在应该是Customer对象
        return self.request.user


# 修改密码API
class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.password = make_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': '密码已成功修改'}, status=status.HTTP_200_OK)


# 用户投票数据API
class CustomerPollsAPIView(generics.ListAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(customer=self.request.user)
class IndexView(TemplateView):
    template_name = "polls/index.html"


# 原有的视图集 - 保留这些，它们处理投票系统的核心功能
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def retrieve(self, request, pk=None):
        # 尝试从缓存获取
        poll_data = get_poll_from_cache(pk)
        if poll_data:
            return Response(poll_data)

        # 缓存未命中，从数据库获取
        poll = get_object_or_404(Poll, poll_id=pk)
        serializer = self.get_serializer(poll)
        data = serializer.data

        # 存入缓存
        set_poll_to_cache(pk, data)

        return Response(data)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        option_id = request.data.get('option_id')
        if not option_id:
            return Response({'error': 'Option ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用Redis增加投票计数
        success = increment_option_count(pk, option_id)
        if success:
            return Response({'status': 'vote recorded'})

        # 如果Redis操作失败，则直接操作数据库
        option = get_object_or_404(Option, option_id=option_id, poll_id=pk)
        option.count += 1
        option.save()

        # 更新缓存
        poll = get_object_or_404(Poll, poll_id=pk)
        serializer = self.get_serializer(poll)
        set_poll_to_cache(pk, serializer.data)

        return Response({'status': 'vote recorded'})


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class AdministratorViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer


class RefreshTokenView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': '缺少刷新令牌'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 解码刷新令牌
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )

            # 验证令牌类型
            if payload.get('type') != 'refresh':
                return Response({'error': '无效的令牌类型'}, status=status.HTTP_400_BAD_REQUEST)

            # 获取用户
            user_id = payload.get('user_id')
            user = Customer.objects.get(customer_id=user_id)

            # 生成新令牌
            tokens = generate_token(user)

            return Response({
                'access': tokens['access'],
                'refresh': tokens['refresh']
            })
        except jwt.ExpiredSignatureError:
            return Response({'error': '令牌已过期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': '令牌无效'}, status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
