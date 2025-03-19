from django.http import Http404
from .jwt import get_tokens_for_customer, generate_token
from django.views.generic import TemplateView
import random
import datetime

from .serializers import (
    CustomerSerializer, PollSerializer, OptionSerializer,
    AdministratorSerializer, CustomerProfileSerializer,
    ChangePasswordSerializer, LoginSerializer, PollCreateSerializer, PollUpdateSerializer,
    AdminLoginSerializer  # New serializer for admin login
)
from django.views.generic import TemplateView
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth.hashers import make_password

from .models import Customer, Poll, Option, Administrator

from .cache import get_poll_from_cache, set_poll_to_cache, increment_option_count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from .models import Customer
from .jwt import generate_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect


# New API version of admin_login
@api_view(['POST'])
@permission_classes([AllowAny])
def api_admin_login(request):
    """API endpoint for admin login"""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None and user.is_staff:
        login(request, user)
        # Generate token for admin
        token = generate_admin_token(user)
        return Response({
            'message': 'Login successful',
            'token': token,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid username or password'
        }, status=status.HTTP_401_UNAUTHORIZED)


# Helper function to generate admin token
def generate_admin_token(user):
    """Generate a token for admin users"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


# New API version of admin_logout
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_admin_logout(request):
    """API endpoint for admin logout"""
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


# New API version of admin_dashboard
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_admin_dashboard(request):
    """API endpoint for admin dashboard - returns all polls"""
    polls = Poll.objects.all()
    serializer = PollSerializer(polls, many=True)
    return Response(serializer.data)


# Keep the original template-based function for backward compatibility
def admin_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("polls:admin_dashboard")  # ✅ 这样 Django 才能找到 `admin_dashboard`

        else:
            return render(request, "polls/admin_login.html", {"error": "用户名或密码错误"})
    return render(request, "polls/admin_login.html")  # ✅ 确保模板路径正确


def admin_logout(request):
    logout(request)
    return redirect("polls:admin_login")


def admin_dashboard(request):
    polls = Poll.objects.all()
    for poll in polls:
        print(f"Poll: {poll.title}, Poll ID: {poll.poll_id}")  # ✅ 确保 poll.poll_id 正确
    return render(request, "polls/admin_dashboard.html", {"polls": polls})


def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, poll_id=poll_id)
    options = Option.objects.filter(poll=poll)

    if request.method == "POST":
        form = PollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()

            # 处理选项（更新已有的，添加新的）
            options_data = request.POST.getlist('options[]')  # 获取所有选项内容
            existing_options = list(options)  # 将已有选项转换成列表

            for index, content in enumerate(options_data):
                if index < len(existing_options):
                    # 更新已有的选项
                    existing_options[index].content = content
                    existing_options[index].save()
                else:
                    # 添加新选项
                    Option.objects.create(poll=poll, content=content)

            return redirect("polls:admin_dashboard")  # 保存后返回后台

    else:
        form = PollForm(instance=poll)

    return render(request, "polls/edit_poll.html", {"form": form, "options": options})


def delete_option(request, option_id):
    option = get_object_or_404(Option, pk=option_id)
    poll_id = option.poll.poll_id  # 先获取问卷 ID
    option.delete()  # 删除选项
    return redirect('polls:edit_poll', poll_id=poll_id)  # 重定向回编辑页面


@login_required
@staff_member_required
def manage_poll(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)  # 先不保存到数据库
            poll.customer = Customer.objects.get(customer_id=request.user.id)

            poll.poll_id = random.randint(10000000, 99999999)  # 生成随机 poll_id
            poll.save()

            # 处理选项
            options_data = request.POST.getlist('options[]')
            for content in options_data:
                Option.objects.create(poll=poll, content=content)

            return redirect("polls:admin_dashboard")
    else:
        form = PollForm()

    return render(request, "polls/manage_poll.html", {"form": form})


def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, poll_id=poll_id)  # 确保 poll_id 而不是 id
    poll.delete()
    return redirect("polls:admin_dashboard")


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


class PollCreateAPIView(generics.CreateAPIView):
    serializer_class = PollCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


# 用户的投票问卷列表
class UserPollsAPIView(generics.ListAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(customer=self.request.user)


# 更新投票问卷
class PollUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PollUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(customer=self.request.user, active=True)

    def update(self, request, *args, **kwargs):
        poll = self.get_object()
        serializer = self.get_serializer(poll, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 更新投票问卷基本信息
        poll.title = serializer.validated_data.get('title', poll.title)
        poll.cut_off = serializer.validated_data.get('cut_off', poll.cut_off)
        poll.save()

        # 处理现有选项的更新和删除
        if 'options' in serializer.validated_data:
            for option_data in serializer.validated_data['options']:
                if option_data.get('delete', False):
                    # 删除选项
                    if 'option_id' in option_data:
                        try:
                            option = Option.objects.get(option_id=option_data['option_id'], poll=poll)
                            option.delete()
                        except Option.DoesNotExist:
                            pass
                elif 'option_id' in option_data:
                    # 更新选项
                    try:
                        option = Option.objects.get(option_id=option_data['option_id'], poll=poll)
                        option.content = option_data['content']
                        option.save()
                    except Option.DoesNotExist:
                        pass

        # 添加新选项
        if 'new_options' in serializer.validated_data:
            for option_text in serializer.validated_data['new_options']:
                Option.objects.create(poll=poll, content=option_text)

        # 清除缓存
        from .cache import clear_poll_cache
        clear_poll_cache(poll.poll_id)

        # 返回更新后的投票问卷
        return Response(PollSerializer(poll).data)


# 删除投票问卷
class PollDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(customer=self.request.user)

    def perform_destroy(self, instance):
        # 清除缓存
        from .cache import clear_poll_cache
        clear_poll_cache(instance.poll_id)
        instance.delete()


# 通过标识符查找投票问卷
@api_view(['GET'])
@permission_classes([AllowAny])
def get_poll_by_identifier(request, identifier):
    try:
        poll = Poll.objects.get(identifier=identifier)
        serializer = PollSerializer(poll)
        return Response(serializer.data)
    except Poll.DoesNotExist:
        return Response({"error": "找不到该投票问卷"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])  # 允许任何人查看结果
def poll_results(request, poll_id):
    """
    获取投票结果
    """
    poll = get_object_or_404(Poll, poll_id=poll_id)
    serializer = PollSerializer(poll)
    data = serializer.data

    # 计算总票数
    total_votes = sum(option['count'] for option in data['options'])

    # 计算每个选项的百分比
    for option in data['options']:
        if total_votes > 0:
            option['percentage'] = round((option['count'] / total_votes) * 100, 1)
        else:
            option['percentage'] = 0

    # 添加总票数信息
    data['total_votes'] = total_votes

    return Response(data)


# 公开投票页面视图
class PublicVoteView(TemplateView):
    template_name = "polls/public_vote.html"


# 公开投票API (无需登录)
@api_view(['POST'])
@permission_classes([AllowAny])
def public_vote(request, poll_id):
    """
    公开投票API，允许未登录用户进行投票
    """
    try:
        poll = get_object_or_404(Poll, poll_id=poll_id)

        # 检查投票是否已结束
        if not poll.active:
            return Response({"error": "此投票已结束"}, status=status.HTTP_400_BAD_REQUEST)

        option_id = request.data.get('option_id')
        if not option_id:
            return Response({"error": "请选择一个选项"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查选项是否存在
        option = get_object_or_404(Option, option_id=option_id, poll=poll)

        # 增加投票计数
        option.count += 1
        option.save()

        # 尝试更新缓存
        try:
            from .cache import increment_option_count, clear_poll_cache
            increment_option_count(poll_id, option_id)
        except Exception as e:
            print(f"缓存更新失败: {str(e)}")

        return Response({"status": "投票成功"})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def view_poll(request, poll_id):
    poll = get_object_or_404(Poll, poll_id=poll_id)
    options = poll.options.all()
    return render(request, "polls/view_poll.html", {"poll": poll, "options": options})