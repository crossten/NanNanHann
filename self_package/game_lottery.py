import re
import random

#創建抽獎
def create(redis_model, pool, max):
    room = 'r'
    for i in range(0,6):           
        room += str(random.randint(0,9))
    while room in redis_model.game_room:
        room += str(random.randint(0,9))
    redis_model.game_key = {
                'game_list' : {},
                'game_draw' : [],
                'game_end' : False, 
                'game_max' : max, 
                'game_pool' : pool
                }
    redis_model.game_room.append(room)
    redis_model.insert('game_room', redis_model.game_room)
    redis_model.insert(room, redis_model.game_key)
    return room

#人工參加/取消抽獎
def join(redis_model, room, player):
    load_game = redis_model.reply(room)
    load_game['game_list'][player] = player
    redis_model.insert(room, load_game)
def cancel(redis_model, room, player):
    load_game = redis_model.reply(room)
    del load_game['game_list'][player]
    redis_model.insert(room, load_game)

#抽獎介面
class flex_simulator():
    def __init__(self):
        self.item = {
            '狼' : 'https://content.quizzclub.com/trivia/2018-11/gde-obitaet-dingo.jpg',
            '綠木' : 'https://i.imgur.com/S1c4F5a.jpg',
            '火焰' : 'https://i.imgur.com/ngbSa6K.png',
            '魔法書III' : 'https://i.imgur.com/ieaBIuY.jpg',
            '魔法書II' : 'https://p2.bahamut.com.tw/HOME/creationCover/92/0003391192_B.JPG',
            '魔法書I' : 'https://images.gamme.com.tw/news2/2016/74/99/qZqYpqSYlaGcqKQ.jpg',
            '黑色染劑' : 'https://i.imgur.com/muXGlj9.jpg',
            '魔法書頁' : 'https://img.itw01.com/images/2019/04/10/14/1258_JPVi2W_UFJOBEH.jpg!r800x0.jpg',
            '逆轉' : 'https://resource01-proxy.ulifestyle.com.hk/res/v3/image/content/2300000/2301165/time02--_1024.jpg'
            }
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
    def flex(self, room, award, sizes):
        try :
            award_rex = re.search('|'.join(self.item.keys()), award).group(0)
            image_link = self.item[award_rex]
        except :
            image_link = 'https://i.imgur.com/IoPqQPZ.png'
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['header'] = self.base_box('vertical')
        game['header']['contents'].append(self.image_box(image= image_link))
        game['body'] = self.base_box('vertical')
        game['body']['contents'].append(self.text_box(text= award + ' 抽取人數 : '+ sizes + ' ----開始報名', color= '#171717'))
        game['body']['contents'].append(self.separator)
        game['body']['contents'].append(self.text_box(text= '代抽方式 : 遊戲名稱,{room},參加抽獎'.format(room = room), color= '#171717'))
        game['footer'] = self.base_box('vertical')
        game['footer']['backgroundColor'] = '#FFFDEB'
        buttonbox = self.button_box(backgroundColor= '#fffdeb')
        buttonbox['contents'].append(self.button(color= '#FFBC47', label= '參加抽獎', data= '抽獎編號-參加-' + room))
        buttonbox['contents'].append(self.button(color= '#FFBC47', label= '取消抽獎', data= '抽獎編號-取消-' + room))
        buttonbox['contents'].append(self.button(color= '#FFBC47', label= '參加名單', data= '抽獎編號-名單-' + room))
        game['footer']['contents'].append(buttonbox)
        buttonbox = self.button_box(backgroundColor= '#FFE6CC')
        buttonbox['contents'].append(self.button(color= '#ABABAB',label= '開獎', data= '抽獎編號-開獎-' + room))  
        game['footer']['contents'].append(buttonbox)
        return game

class postback():
    def __init__(self, data):
        self.ordr, self.room = data.split('-')[1:3]
    def load(self, redis_model):
        redis_model.game_room = redis_model.reply('game_room')
        if self.room not in redis_model.game_room: 
            return False
        self.load_game = redis_model.reply(self.room)
        return True
    def joinlist(self, message_action, event):
        game_list = '\n'.join(self.load_game['game_list'].values())
        text= self.load_game['game_pool'] \
            +'----抽取人數 : ' \
            + self.load_game['game_max'] \
            +'\n參加名單\n------------------\n' \
            + game_list
        message_action.TextMsg(event, text)
        return
    def join(self, redis_model, game_name, event, message_action):
        self.load_game['game_list'][event.source.user_id] = game_name
        redis_model.insert(self.room, self.load_game)
        message_action.TextMsg(event, game_name +'----抽獎編號{room}--報名成功'.format(room = self.room))
        return
    def cancel(self, redis_model, game_name, event, message_action):
        del self.load_game['game_list'][event.source.user_id]
        redis_model.insert(self.room, self.load_game)
        message_action.TextMsg(event, game_name +'----抽獎編號{room}--刪除成功'.format(room = self.room))
        return
    def draw(self, admin_id, redis_model, event, message_action):
        if event.source.user_id not in admin_id:
            return
        elif self.load_game['game_end'] :
            return
        elif len(self.load_game['game_list']) < int(self.load_game['game_max']) :
            message_action.TextMsg(event, '參加人數不足')
            return
        else:
            r = random.sample(self.load_game['game_list'].keys(), k = int(self.load_game['game_max']))
            for num, i in enumerate(r):
                name = self.load_game['game_list'][i]
                self.load_game['game_draw'].append(name) 
                text= self.load_game['game_pool'] \
                    +'----抽獎編號 : ' \
                    + self.room \
                    + '\n恭喜 {name} 中獎----請投標由左到右數來第{num}個'.format(num = str(num+1), name = name)
                message_action.PushMsg(i, text) 
        game_list = '\n'.join(self.load_game['game_draw'])
        text = self.load_game['game_pool'] \
                + '----' \
                + self.room \
                + '\n得獎名單\n------------------\n' \
                + game_list
        self.load_game['game_end'] = True
        redis_model.game_room.remove(self.room)
        redis_model.insert('game_room', redis_model.game_room)
        redis_model.insert(self.room, self.load_game)
        message_action.TextMsg(event, text)
        return