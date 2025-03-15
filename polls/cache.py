import redis
import json
from django.conf import settings

# 连接到Redis
redis_client = redis.Redis(host='localhost', port=6379, db=1)

def get_poll_from_cache(poll_id):
    """从Redis缓存获取投票数据"""
    poll_data = redis_client.get(f'poll:{poll_id}')
    if poll_data:
        return json.loads(poll_data)
    return None

def set_poll_to_cache(poll_id, poll_data):
    """将投票数据存入Redis缓存"""
    redis_client.set(f'poll:{poll_id}', json.dumps(poll_data))
    # 设置过期时间，例如1小时
    redis_client.expire(f'poll:{poll_id}', 3600)

def increment_option_count(poll_id, option_id):
    """增加选项的投票数"""
    poll_data = get_poll_from_cache(poll_id)
    if poll_data:
        for option in poll_data['options']:
            if option['option_id'] == option_id:
                option['count'] += 1
                set_poll_to_cache(poll_id, poll_data)
                return True
    return False

def clear_poll_cache(poll_id):
    """清除投票缓存"""
    redis_client.delete(f'poll:{poll_id}')