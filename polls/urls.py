from rest_framework.routers import DefaultRouter
from . import views
from .jwt import CustomerTokenObtainPairView
from django.urls import path, include
from .views import admin_login, admin_logout, admin_dashboard, manage_poll, delete_poll, edit_poll, delete_option

# 定义 REST API 的路由
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'polls', views.PollViewSet)
router.register(r'options', views.OptionViewSet)
router.register(r'administrators', views.AdministratorViewSet)

# 应用命名空间
app_name = 'polls'

urlpatterns = [
    # 保留原有的模板路由，确保向后兼容
    path("admin-panel/login/", admin_login, name="admin_login"),
    path("admin-panel/logout/", admin_logout, name="admin_logout"),
    path("admin-panel/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-panel/poll/manage/", manage_poll, name="manage_poll"),
    path("admin-panel/poll/edit/<int:poll_id>/", edit_poll, name="edit_poll"),
    path("admin-panel/poll/delete/<int:poll_id>/", delete_poll, name="delete_poll"),
    path('admin-panel/poll/option/delete/<int:option_id>/', delete_option, name='delete_option'),
    path('polls/view/<int:poll_id>/', views.view_poll, name='view_poll'),

    # 新的API路由 - 只添加三个管理员API接口
    path("api/admin/login/", views.api_admin_login, name="api_admin_login"),
    path("api/admin/logout/", views.api_admin_logout, name="api_admin_logout"),
    path("api/admin/dashboard/", views.api_admin_dashboard, name="api_admin_dashboard"),

# 投票 API
    path('api/polls/create/', views.PollCreateAPIView.as_view(), name='poll-create'),
    path('api/polls/my-polls/', views.UserPollsAPIView.as_view(), name='my-polls'),
    path('api/polls/<int:pk>/update/', views.PollUpdateAPIView.as_view(), name='poll-update'),
    path('api/polls/<int:pk>/delete/', views.PollDeleteAPIView.as_view(), name='poll-delete'),
    path('api/polls/find/<str:identifier>/', views.get_poll_by_identifier, name='find-poll'),
    path('api/polls/<int:poll_id>/results/', views.poll_results, name='poll-results'),
    # REST API
    path('api/', include(router.urls)),

    # 用户认证 API
    path('api/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),

    # 用户资料 API
    path('api/profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('api/token/', CustomerTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('', views.IndexView.as_view(), name='index'),



    # 公开投票页面和 API
    path('public-vote/', views.PublicVoteView.as_view(), name='public-vote'),
    path('api/polls/<int:poll_id>/public-vote/', views.public_vote, name='public-vote-api'),
]