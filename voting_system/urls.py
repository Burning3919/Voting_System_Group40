from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('polls/', include('polls.urls')),
    # 默认重定向到登录页
    path('', RedirectView.as_view(pattern_name='polls:login'), name='home'),
]