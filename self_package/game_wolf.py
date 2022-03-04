#狼人殺
import random 

#建立遊戲
def create(redis_model):
    room = 'w'
    for i in range(0,6):           
        room += str(random.randint(0,9))
    # while room in redis_model.game_room:
    #     room += str(random.randint(0,9))
    data = {
        'game_list' : {},
        'game_turn' : {0 : False}
        }
    # redis_model.game_room.append(room)
    # redis_model.insert('game_room', redis_model.game_room)
    # redis_model.insert(room, data)
    return room

#操作介面
class flex_simulator():
    def __init__(self):
        self.image = {
            'start' : 'https://i.imgur.com/b0CJ5JV.png?1',
            'daylight' : '',
            'night' : ''            
            }
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.separator = {'type': 'separator'}
    def base_box(self, layout):
        box = {
            'type': 'box',
            'layout': layout,
            'contents': []
                }
        return box
    def image_box(self, image):
        box = {
            'type': 'image',
            'url': image,
            'size': 'full',
            'aspectMode': 'cover'
                }
        return box
    def text_box(self, text, color):
        box = {
            'type': 'text',
            'text': text,
            'weight': 'bold',
            'color': color,
            'wrap' : True,
            'size': 'sm'
                }
        return box
    def button_box(self, backgroundColor):
        box = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': backgroundColor,
            'contents': []
            } 
        return box
    def button(self,color, label, data):
        box = {
            'type': 'button',
            'color' : color,
            'style' : 'primary'
            }
        box['action'] = {
            'type': 'postback',
            'label': label,
            'data': data
                }
        return box
    def start(self, room):
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['hero'] = self.image_box(image= self.image['start'])
        game['hero']['aspectRatio'] = '13:9'
        game['footer'] = self.base_box('vertical')
        game['footer']['backgroundColor'] = '#D1D1D1'
        buttonbox = self.button_box(backgroundColor= '#D1D1D1')
        buttonbox['contents'].append(self.button(color= '#4D000F', label= '參加遊戲', data= '狼人殺-參加-'+ room))
        buttonbox['contents'].append(self.button(color= '#4D000F', label= '遊戲開始', data= '狼人殺-開始-'+ room))
        game['footer']['contents'].append(buttonbox)
        return game

    def vote(self):
        return

    def check(self):
        return

    def seer(self):
        return

    def winner(self):
        return

class role(): 
    def __init__(self, redis_model, room):
        self.redis_model = redis_model
        self.data = redis_model.reply(room)

    def distribute(self):
        uid = random.choice(self.data['game_list'])
        del self.data['game_list'][uid]
        return uid

    def start(self, room):
        room = {
            'game_list' : self.data['game_list'],
            'dead' : [],
            'alive' : [],
            'vote' : {},
            'werewolves' : {
                'wolf' : [],
                'minion' : []
                },
            'village' : {
                'seer' : [],
                'witch' : [],
                'hunter' : [],
                'acient' : [],
                'svior' : [],
                'villagers' : []       
                },
            'protect' : [],
            'night' : True,
            'game_turn' : {0 : True, 1 : False},
            'game_end' : False
        }
        all = len(self.data['game_list'])
        room['werewolves']['wolf'].append(self.distribute())
        room['werewolves']['seer'].append(self.distribute())
        room['werewolves']['hunter'].append(self.distribute())
        for i in range(int((all - 6) / 3)): 
            room['werewolves'][random.choice(['wolf', 'minion'])].append(self.distribute())
            room['werewolves'][random.choice(['seer', 'hunter', 'witch', 'acient', 'svior'])].append(self.distribute())
        for i in self.date['game_list'].keys():
            room['werewolves']['villagers'].append(self.date['game_list'][i])
        for i in room['village']['seer']:
            room[i] = {'see' : 0, 'turn' : 0}
        for i in room['village']['witch']:
            room[i] = {'poison' : True, 'antidote' : True}
        for i in room['village']['hunter']:
            room[i] = {'deathrattle' : False}
        for i in room['village']['acient']:
            room[i] = {'life' : 2}
        room['werewolves']['all'] = room['werewolves']['wolf']  + room['werewolves']['minion'] 
        room['villagers']['all'] = room['villagers']['seer'] + room['villagers']['hunter'] + room['villagers']['witch'] + room['villagers']['acient'] + room['villagers']['svior'] 
        self.save()

    #預言
    def seer(self, uid):
        if self.data[uid]['see'] < self.data[uid]['turn']:
            return True
        else :
            return False

    def save(self):
        self.redis_model.insert(self.data['room'], self.data)

#按鍵
class action():
    def __init__(self, redis_model, room):
        self.redis_model = redis_model
        self.data = redis_model.reply(room)

#加入遊戲
    def join(self, data):
        if self.data['game_turn'][0] : return
        self.data ['game_list'][data['uid']] = data['name']
        self.save()

#死亡
    def dead(self, data):
        self.data['alive'].remove(data)
        self.data['dead'].append(data)
        if data in self.data['werewolves']['wolf']:
            self.data['werewolves']['wolf'].remove(data)
        if self.winner() != False :
            self.data ['game_end'] = True

    def kill(self, uid, data):
#狼人
        if self.data['night'] :
            if uid in self.data['werewolves']['wolf']:
                ta = random.choice(data)
                self.dead(ta)
                self.save()
#投票
        elif uid == 'vote':
            self.data['alive'].remove(data)
            self.data['dead'].append(data)
            if data in self.data['village']['hunter']:
                self.data[data] = {'deathrattle' : True}
                self.save()
            if data == '棄票' :
                self.data['check'][uid] = True

#獵人
        elif uid in self.data['village']['hunter'] :
            if self.data[uid]['deathrattle']:
                self.data['alive'].remove(data)
                self.data['dead'].append(data)
                self.save()

#投票階段
    def vote(self, uid, data):
        self.data['vote'][uid] = data
        count_vote = len(self.data['vote'][uid].keys())
        count_alive = len(self.data['alive'])
        if count_vote == count_alive:
            self.data['menu'] = {i: self.data['vote'][uid].values().count(i) for i in self.data['vote'][uid].values()}
        self.save()

#確認階段
    def check(self, uid):
        self.data['check'][uid] = True
        self.data['check'][uid] = False
        count_check = len(self.data['check'][uid].keys())
        count_vote = len(self.data['vote'][uid].keys())
        count_alive = len(self.data['alive'])
        if count_check == count_alive:
            if count_vote == 0: None
            else :
                for i in self.data['vote'].keys():
                    if self.data['vote'][i] == max(self.data['vote'].values()):
                        self.kill(self, 'vote', i)
            self.data['night'] = True
        self.save()    

#勝利
    def winner(self):
        if len(self.data['werewolves']['wolf']) > len(self.data['alive']) /2 -1 :
            return 'werewolves'
        elif len(self.data['werewolves']['wolf']) == 0 :
            return 'village'
        return False

    def save(self):
        self.redis_model.insert(self.data['room'], self.data)

