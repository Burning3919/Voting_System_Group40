import os
from celery import Celery

# 设置Django设置模块的默认值
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')

app = Celery('voting_system')

# 使用CELERY前缀的设置来配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的Django应用中发现任务
app.autodiscover_tasks()

# 配置定期任务
app.conf.beat_schedule = {
    'sync-poll-data-every-5-minutes': {
        'task': 'polls.tasks.sync_poll_data_to_db',
        'schedule': 300.0,  # 每5分钟运行一次
    },
}