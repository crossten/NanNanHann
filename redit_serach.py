import redis
import json
import _redis
#redis_db設定 --redis-api

redis_model = _redis.redis_db()
all = redis_model.connect.keys()
all.sort()
print(all)

# coupon_ninokuni = redis_model.reply('coupon_ninokuni')
# print(coupon_ninokuni)
#清空序號領取紀錄
# for i in coupon_ninokuni['天鵝'].keys():
#     if len(i) == 0 : continue
#     coupon_ninokuni['天鵝'][i] = []    
# redis_model.insert('coupon_ninokuni', coupon_ninokuni)

#抽獎房間
# print('\n ---- ', redis_model.reply('game_crusade'), ' ---- \n')  
# game_crusade = redis_model.reply('game_crusade')
# for i in game_crusade:
#     print(' ---- ', redis_model.reply(i), ' ---- ')  

# #會員紀錄
# for i in all:
#     if i == 'game_room' : continue
#     if i == 'game_crusade' : continue
#     if i == 'coupon_ninokuni' : continue
#     file = redis_model.reply(i)
#     file_key = list(file.keys())
#     file_key.sort(reverse= True)
#     print('\n ---- ', i, ' ---- \n')  
#     for j in file_key:
#         print(j, file[j])
