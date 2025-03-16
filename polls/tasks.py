from celery import shared_task
from .models import Poll, Option
from .cache import get_poll_from_cache, clear_poll_cache
from django.utils import timezone
@shared_task
def sync_poll_data_to_db():
    """
    将Redis中的投票数据同步到PostgreSQL
    此任务应该定期运行
    """
    polls = Poll.objects.filter(active=True)
    for poll in polls:
        poll_data = get_poll_from_cache(poll.poll_id)
        if poll_data:
            # 更新选项的投票数
            for option_data in poll_data['options']:
                try:
                    option = Option.objects.get(option_id=option_data['option_id'])
                    option.count = option_data['count']
                    option.save()
                except Option.DoesNotExist:
                    pass
@shared_task
def update_poll_status():
    """
    检查并更新已过期的投票问卷状态
    """
    now = timezone.now()
    expired_polls = Poll.objects.filter(cut_off__lt=now, active=True)
    for poll in expired_polls:
        poll.active = False
        poll.save()

        # 清除缓存
        try:
            clear_poll_cache(poll.poll_id)
        except Exception as e:
            print(f"清除缓存失败: {str(e)}")

    return f"已更新 {expired_polls.count()} 个过期投票问卷的状态"