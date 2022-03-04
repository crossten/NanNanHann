import redis
import json
import _redis
#redis_db設定 --redis-api

redis_model = _redis.redis_db()
all = redis_model.connect.keys()
all.sort()
print(all)

x = redis_model.reply('personal')

print(x)