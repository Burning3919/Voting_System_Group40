from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .jwt import CustomerTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'polls', views.PollViewSet)
router.register(r'options', views.OptionViewSet)
router.register(r'administrators', views.AdministratorViewSet)

# 应用命名空间
app_name = 'polls'

# API URL模式
urlpatterns = [
    # 原有的API路由
    path('api/', include(router.urls)),

    # 用户认证API
    path('api/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),

    # 用户资料API
    path('api/profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('api/token/', CustomerTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('', views.IndexView.as_view(), name='index'),



]