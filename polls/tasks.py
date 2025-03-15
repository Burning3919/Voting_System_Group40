from celery import shared_task
from .models import Poll, Option
from .cache import get_poll_from_cache, clear_poll_cache

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