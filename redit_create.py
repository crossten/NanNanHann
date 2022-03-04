import _redis

redis_model = _redis.redis_db()
redis_model.insert('Keyword', {})
redis_model.insert('coupon_ninokuni', {'天鵝': {'switch': False}})
redis_model.insert('game_crusade', [])
redis_model.insert('game_room', [])

