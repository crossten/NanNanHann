from linebot import LineBotApi
import _account
import redis
import random
import json

channel_access_token = _account.line_token()
line_bot_api = LineBotApi(channel_access_token)

#redis_db設定 --redis-api
class redis_db():
    def __init__(self):
        self.connect = redis.StrictRedis(
                host=_account.redis('host'),
                port=_account.redis('port'), 
                password = _account.redis('password'),
                decode_responses = True
                )
        self.data = {},
        self.game_room = []
        self.game_key = {}
        self.magnify = {
            'Msg' : random.randint(0,5),
            'Mention': random.randint(5,10),
            'Sticker' : random.randint(3,8),
            'Unsend' : -1 * random.randint(0,5),
            'Image' : random.randint(7,15),
            'Postback' : 1,
            'Attack' : 1,
            'Dead' : 0
        }
    def reply(self, KeyName):
        val = self.connect.get(KeyName)
        return json.loads(val)
    def insert(self, KeyName, text):
        self.connect.set(KeyName, json.dumps(text))
    def pop(self, KeyName):
        self.connect.delete(KeyName)
    def refresh(self, event):
        try:
            profile_user = line_bot_api.get_profile(event.source.user_id)
            self.data[event.source.user_id]['name'] = profile_user.display_name
            self.data[event.source.user_id]['url'] = profile_user.picture_url
        except:
            None
        try:
            profile_group = line_bot_api.get_group_summary(event.source.group_id) 
            self.data['name'] = profile_group.group_name
            return [event.source.user_id, event.source.group_id]
        except:
            return [event.source.user_id, 'personal']
    def read_lineid(self, event):
        try:
            self.data = self.reply(event.source.group_id)
        except:
            try:
                event.source.group_id
                self.data = {}
            except:
                self.data = self.reply('personal')
        if event.source.user_id not in self.data.keys():
            self.data[event.source.user_id] = {}
    def update(self, event, message_type, is_mention = False, mention_id = '', exp= 1):
        self.read_lineid(event)
        member_id = [mention_id, event.source.group_id] if is_mention else self.refresh(event)
        try:
            self.data[member_id[0]][message_type] += 1
        except:
            self.data[member_id[0]][message_type] = 1
        try:
            self.data[member_id[0]]['EXP'] += self.magnify[message_type] * exp
            if self.data[member_id[0]]['EXP'] < 0 : self.data[member_id[0]]['EXP'] = 0
        except:
            self.data[member_id[0]]['EXP'] = 0
        self.insert(member_id[1], self.data)