#linebot相關Package
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent, UnsendEvent, StickerMessage, ImageMessage, 
    TextMessage, TextSendMessage, FlexSendMessage, ImageSendMessage
    )
from flask import Flask, request, abort
import redis
#追加功能相關Package
from random import shuffle
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import json
import os
import re
import random
import pyimgur
import requests

#line-api 必須放上自己的Channel Access Token、Channel Secret
channel_access_token = 'channel_access_token'
channel_secret = 'channel_secret'
#管理員帳號 
admin_id = ['admin_id']
#分享照片Imgur-api
im = pyimgur.Imgur('Imgur') 

#常用定義/功能
app = Flask(__name__)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
member = pd.read_csv('member.csv', header= 0, index_col= None)
member['GAME_NAME'] = member['GAME_NAME'].fillna(',')+ ','+ member['LINE_NAME'] 
member['GAME_NAME']  = member['GAME_NAME'].str.split(',', expand=True)[0]
MsgLog = pd.DataFrame(columns = ['user_id', 'display_name', 'message_id', 'msg'])
Keyword_image = os.listdir('pitchure')        
pet_new = pd.DataFrame(
    data = {
        'Name': '★★★★托奇',
        'Probability': '0.0333%',
        'Total': '100%',
        'Url': 'https://hedwig-cf.netmarble.com/forum-common/ennt/ennt_t/thumbnail/17ec567cfa314cadb4910ca8be3781bc_1644452443006_d.jpg'
        },
    index=[0])
pet_data = pd.read_csv('pet.csv', header= 0, index_col= None)
join_list = {}
Unsend_list = {}


#redis_db設定 --redis-api
class redis_db():
    def __init__(self):
        self.host = 'redis-host.com'
        self.port = 'port'
        self.password = 'password'
        self.connect = redis.StrictRedis(
                host=self.host,
                port=self.port, 
                password = self.password,
                decode_responses=True
                )
        self.data = {},
        self.game_room = []
        self.game_key = {}
    def insert(self, KeyName, text):
        self.connect.set(KeyName, json.dumps(text))
    def reply(self, KeyName):
        val = self.connect.get(KeyName)
        return json.loads(val)
    def pop(self, KeyName):
        self.connect.delete(KeyName)
    def update(self, event, message_type):
        try:
            self.data = self.reply(event.source.group_id)
        except:
            self.data = self.reply('personal')            
        try:
            self.data[event.source.user_id][message_type] += 1
        except:
            self.data[event.source.user_id] = {}
            self.data[event.source.user_id][message_type] = 1
        try:
            self.insert(event.source.group_id, self.data)
        except:
            self.insert('personal', self.data)

#推播訊息
def PushMsg(uid, text): 
    try:
        line_bot_api.push_message(to= uid, messages= TextSendMessage(text= text))
    except:
        print('line pushmsg發送失敗')
def MultMsg(uid, text): 
    try:
        line_bot_api.multicast(to= uid,messages= TextSendMessage(text= text))
    except:
        print('line pushmsg發送失敗')
def MultFlexMsg(uid, text, flex): 
    try:
        line_bot_api.multicast(to= uid,
                messages=FlexSendMessage(alt_text= text, contents= json.loads(json.dumps(flex, ensure_ascii=False))
            )
        )
    except:
        print('line pushmsg發送失敗')
#文字訊息
def TextMsg(event, text): 
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text= text)
        )
#客製化訊息
def FlexMsg(event, text, flex): 
    line_bot_api.reply_message(
        event.reply_token,
        messages=FlexSendMessage(
            alt_text= text,
            contents= json.loads(json.dumps(flex, ensure_ascii=False))
            )
        )
#圖片訊息
def ImageMsg(event, URL):
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url= URL, 
            preview_image_url= URL
            )
        )  

#抽獎介面
class Lottery():
    def __init__(self):
        self.jpg = {
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
    def flex(self, room, award, sizes):
        try :
            award_rex = re.search('|'.join(self.self.keys()), award).group(0)
            jpg = self.jpg[award_rex]
        except :
            jpg = 'https://i.imgur.com/IoPqQPZ.png'
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['header'] = {
            'type': 'box',
            'layout': 'vertical',
            'contents': []
                }
        image = {
            'type': 'image',
            'url': jpg,
            'size': 'full',
            'aspectMode': 'cover'
                }
        game['header']['contents'].append(image)
        game['body'] = {
                'type': 'box',
                'layout': 'vertical',
                'contents': []
                }
        tittle = {
            'type': 'text',
            'text': award + ' 抽取人數 : '+ sizes + ' ----開始報名',
            'weight': 'bold',
            'color': '#171717',
            'size': 'sm'
                }
        separator = {'type': 'separator'}
        instruction = {
            'type': 'text',
            'text': '代抽方式 : 遊戲名稱,{room},參加抽獎'.format(room = room),
            'weight': 'bold',
            'color': '#171717',
            'size': 'sm'
                }
        game['body']['contents'].append(tittle)
        game['body']['contents'].append(separator)
        game['body']['contents'].append(instruction)
        game['footer'] = {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#fffdeb',
            'contents' : []
                }
        buttonbox = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': '#fffdeb',
            'contents': []
            }
        button = {
            'type': 'button',
            'color' : '#ffbc47',
            'style' : 'primary',
            'action': {
                'type': 'postback',
                'label': '參加抽獎',
                'data': '抽獎編號-參加-' + room
                }
            }
        buttonbox['contents'].append(button)
        button = {
            'type': 'button',
            'color' : '#ffbc47',
            'style' : 'primary',
            'action': {
                'type': 'postback',
                'label': '取消抽獎',
                'data': '抽獎編號-取消-' + room
                }
            }
        buttonbox['contents'].append(button)
        button = {
            'type': 'button',
            'color' : '#ffbc47',
            'style' : 'primary',
            'action': {
                'type': 'postback',
                'label': '參加名單',
                'data': '抽獎編號-名單-' + room
                }
            }
        buttonbox['contents'].append(button)
        game['footer']['contents'].append(buttonbox)
        buttonbox = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': '#ffe6cc',
            'contents': []
            }
        button = {
            'type': 'button',
            'color' : '#ababab',
            'style' : 'primary',
            'action': {
                'type': 'postback',
                'label': '開獎',
                'data': '抽獎編號-開獎-' + room
                }
            }
        buttonbox['contents'].append(button)
        game['footer']['contents'].append(buttonbox)
        return game

#排行榜介面
class game_rank():
    def __init__(self):
        self.Msgtype = {
            'Msg' : '幹話王',
            'Sticker' : '貼圖王',
            'Unsend' : '訊息回收車',
            'Image' : '圖片老司機',
            'postback' : '狂點按鈕'
        }
        self.image = {
            'Image' : 'https://i.imgur.com/aYYAzNm.png',
            'Sticker' : 'https://pic.52112.com/180623/JPG-180623A_368/glj9rVcoRS_small.jpg',
            'Unsend' : 'https://img.ltn.com.tw/Upload/news/600/2019/03/14/2726930_1.jpg',
            'Msg' : 'https://i.imgur.com/M3MZ7Ox.jpg',
            'postback' : 'https://img.sj3c.com.tw/uploads/2018/03/KEY-1-2-min.jpg'
        }
        self.flex_carousel = {'contents':[],'type':'carousel'}
    def rowbox(self, color):
        box = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': color,
            'paddingAll': '5px',
            'contents': []
        }
        return box
    def spacebox(self, text, color):
        box = {
            'type': 'text',
            'text': text,
            'align': 'center',
            'color': color,
            'size': 'sm',
            'wrap': True,
            'adjustMode': 'shrink-to-fit'
        }
        return box
    def rank(self, group, data):
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['header'] = {
            'type': 'box',
            'layout': 'vertical',
            'contents': []
            }
        tittle = {
                'type': 'text',
                'text': self.Msgtype[group] + ' 累積排行榜',
                'weight': 'bold',
                'color': '#171717',
                'size': 'xl'
            }
        game['header']['contents'].append(tittle)
        game['hero'] = {
            'type': 'image',
            'url': self.image[group],
            'size': 'full',
            'aspectMode': 'fit'
            }
        game['body'] = {
            'type': 'box',
            'layout': 'vertical',
            'contents': []
            }
        row = self.rowbox(color = '#3C3C3C')
        for i in ['LINE', '遊戲名稱', '累積次數']:
            space = self.spacebox(text= i, color= '#FFFFFF')
            row['contents'].append(space)
        game['body']['contents'].append(row)
        for i in range(len(data)):
            row = self.rowbox(color = '#FCFCFC')
            for j in ['LINE_NAME', 'GAME_NAME', 'Counts']:
                space = self.spacebox(text= data.iloc[i][j], color= '#000000')
                row['contents'].append(space)
            game['body']['contents'].append(row)
        return game
    def insert(self, data):
        for i in self.Msgtype.keys():
            add = data[data['MsgType']== i]
            if len(add) == 0 : continue
            add.sort_values(by=['Counts'], ascending = False).reset_index(drop=True)
            add = add.iloc[:10]
            add['Counts'] = add['Counts'].astype('str')
            self.flex_carousel['contents'].append(self.rank(i, add))

#百度搜圖
def baidu(keyword):
    url = 'https://image.baidu.com/search/acjson?'
    param = {
        'tn': 'resultjson_com',
        'logid':'11388364236666527695',
        'ipn': 'rj',
        'ct': '201326592',
        'is': '',
        'fp': 'result',
        'fr' : '',
        'word': keyword,
        'queryWord':keyword,
        'cl': '2',
        'lm': '-1',
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': '-1',
        'z': '',
        'ic': '0',
        'hd': '',
        'latest': '',
        'copyright': '',
        's': '',
        'se': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': '0',
        'istype': '2',
        'qc': '',
        'nc': '1',
        'expermode': '',
        'nojc': '',
        'isAsync': '',
        'pn': '1',
        'rn': '30',
        'gsm' : '1',
        '1644984363126':''
        }
    response = requests.get(url= url, 
                            headers= {'User-Agent': UserAgent().random},
                            params= param)
    return response.text

#抽幻獸介面
pet_data = pd.concat([pet_data, pet_new])
pet_data['Total'] = pet_data['Total'].str.replace('%', '').astype('float')/100
pet_data = pet_data.sort_values(by=['Total']).reset_index(drop=True)
class game_pet():
    def __init__(self) :
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.url = pet_new['Url'][0]
        self.theme = '抽幻獸 {name} 活動池'.format(name = pet_new['Name'][0])
    def menu(self):
        game = {
            'type': 'bubble',
            'header' : {},
            'footer' : {}
            }
        game['header'] = {
            'type': 'box',
                'layout': 'vertical',
                'contents': []
                }
        image = {
            'type': 'image',
            'url': self.url,
            'size': 'full',
            'aspectMode': 'cover'
            }
        game['header']['contents'].append(image)
        game['footer'] = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': '#fffdeb',
            'contents': []
                }
        button = {
            'type': 'button',
            'action': {
                'type': 'postback',
                'label': '單抽',
                'data': '抽幻獸1抽'}
                }
        game['footer']['contents'].append(button)
        button = {
            'type': 'button',
            'action': {
                'type': 'postback',
                'label': '十抽',
                'data': '抽幻獸10抽'
                }
            }
        game['footer']['contents'].append(button)
        return game
    def report(self, player, pet_url, pet_name):
        flex = {'type': 'bubble'}
        flex['body'] = {
                'type': 'box',
                'layout': 'vertical',
                'contents': []
            }
        flex['footer'] = {
            'type': 'box',
            'layout': 'vertical',
            'contents': []
            }
        image = {
            'type': 'image',
            'url': pet_url,
            'size': 'full',
            'aspectRatio': '12:9',
            'aspectMode': 'cover'
            }
        flex['footer']['contents'].append(image)
        name = {
            'type': 'text',
            'text': player,
            'weight': 'bold',
            'size': 'sm',
            'margin': 'md'
            }
        tittle = {
            'type': 'text',
            'text': self.theme,
            'weight': 'bold',
            'color': '#1f1f1f',
            'size': 'sm'
            }
        drawer = {
            'type': 'box',
            'layout': 'vertical',
            'spacing': 'sm',
            'contents': []
            }
        pet = {
            'type': 'text',
            'size': 'lg',
            'color': '#555555',
            'align': 'center',
            'gravity': 'center',
            'flex': 0,
            'text': pet_name
            }
        drawer['contents'].append(pet)
        flex['body']['contents'].append(name)
        flex['body']['contents'].append(tittle)
        flex['body']['contents'].append(drawer)
        return flex

#監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#加好友回報ID
@handler.add(FollowEvent)
def handle_join(event):
    global join_list
    profile_user = line_bot_api.get_profile(event.source.user_id) 
    join_list[event.source.user_id] = profile_user.display_name
    TextMsg(event, '週週抽獎抽不完~ 請輸入遊戲名字~ \n例如 : 白涵公主,加入王國')
    return

#圖片訊息紀錄
@handler.add(MessageEvent, message= ImageMessage)
def Image_dict(event):
    redis_model = redis_db()
    redis_model.update(event, 'Image')

#貼圖訊息紀錄
@handler.add(MessageEvent, message= StickerMessage)
def Sticker_dict(event):
    redis_model = redis_db()
    redis_model.update(event, 'Sticker')

#收回訊息紀錄
@handler.add(UnsendEvent)
def Unsend_dict(event):
    global MsgLog, Unsend_list
    redis_model = redis_db()
    MsgLog['message_id'] = MsgLog['message_id'].fillna(0).astype(np.int64).astype('str')
    redis_model.update(event, 'Unsend')
    profile_user = event.source.user_id
    message_id = event.unsend.message_id
    display_name = MsgLog['display_name'][(MsgLog['user_id'] == profile_user) & (MsgLog['message_id'] == message_id)].iloc[-1]
    try:
        game_name = member['GAME_NAME'][member['LINE_UID'] == profile_user].iloc[0]
    except:
        game_name = '未加入王國'
    Unsend_msg = MsgLog['msg'][(MsgLog['user_id'] == profile_user) & (MsgLog['message_id'] == message_id)].iloc[-1]
    Unsend_list[message_id] = ["{display}({game})".format(display= display_name,game = game_name), Unsend_msg]
    return 

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def reply(event):
    global join_list, MsgLog, Unsend_list
    msg = event.message.text
    redis_model = redis_db()
    try:
        profile_user = line_bot_api.get_profile(event.source.user_id) 
        try:
            profile_name = profile_user.display_name
            profile_group = line_bot_api.get_group_summary(event.source.group_id) 
        except:
            profile_group = line_bot_api.get_group_summary(event.source.group_id) 
            profile_name = profile_group.group_name
    except:
        None
    redis_model.update(event, 'Msg')
    MsgLog = MsgLog.append(
                {
            'user_id': event.source.user_id, 
            'message_id': event.message.id, 
            'display_name': profile_name,
            'msg': msg
            }, 
            ignore_index=True
        )  
    try:
        log = list(Unsend_list.keys())[0]
        text = '{name} 剛剛收回了 : {message}'.format(name= Unsend_list[log][0], message = Unsend_list[log][1])
        del Unsend_list[log]
        TextMsg(event, text)
        return
    except:
        None

    if re.search('加入清單', msg):
        text = 'LINE_UID,LINE_NAME,GAME_NAME\n' 
        for i, j in zip(join_list.keys(), join_list.values()):
            text += '{uid},{name}\n'.format(uid= i, name= j)
        TextMsg(event, text)
        return

    if re.search('加入王國', msg):
        text = event.source.user_id \
            + '\n' \
            + profile_name \
            + '\n' \
            + msg.split(',')[0] \
            + '\n大頭貼 : ' \
            + profile_user.picture_url
        join_list[event.source.user_id] = '{name},{game}'.format(name= profile_name, game = msg.split(',')[0])
        MultMsg(admin_id, text)
        TextMsg(event, profile_name+ ' 歡迎加入王國抽獎名單~')
        return
        
    if re.search('抽獎', msg):
        game_split = msg.split(',')
        redis_model.game_room = redis_model.reply('game_room')
        if game_split[0] == '舉辦抽獎' :
              room = 'r'
              for i in range(0,6):           
                  room += str(random.randint(0,9))
              while room in redis_model.game_room:
                  room += str(random.randint(0,9))
              redis_model.game_key = {
                            'game_list' : {},
                            'game_draw' : [],
                            'game_end' : False, 
                            'game_max' : game_split[2], 
                            'game_pool' : game_split[1]
                            }
              redis_model.game_room.append(room)
              redis_model.insert('game_room', redis_model.game_room)
              redis_model.insert(room, redis_model.game_key)
              game = Lottery()
              FlexMsg(event, '抽獎編號' + room, game.flex(room= room, award= game_split[1], sizes= game_split[2]))
              return
        elif msg == '查看抽獎' :
              flex_carousel = {'contents':[],'type':'carousel'}
              for num, i in enumerate(redis_model.reply('game_room')) :
                  load_game = redis_model.reply(i)
                  game = Lottery()
                  flex_carousel['contents'].append(game.flex(room= i, award= load_game['game_pool'], sizes= load_game['game_max']))
                  if num == 10: break
              FlexMsg(event, '抽獎編號-mix', flex_carousel)
              return
        elif game_split[1] in redis_model.game_room:
              player = game_split[0]
              room = game_split[1]
              if game_split[2] == '參加抽獎':
                  load_game = redis_model.reply(room)
                  load_game['game_list'][player] = player
                  redis_model.insert(room, load_game)
                  TextMsg(event, player + '({id})----報名成功'.format(id= room))
                  return
              elif game_split[2] == '取消抽獎':
                  load_game = redis_model.reply(room)
                  del load_game['game_list'][player]
                  redis_model.insert(room, load_game)
                  TextMsg(event, player + '({id})----刪除成功'.format(id= room))
                  return
              elif game_split[0] == '刪除抽獎':
                  redis_model.pop(room)
                  TextMsg(event, '刪除抽獎活動編號 : ' + room)
  
    if re.search('抽幻獸', msg):
        flex = game_pet() 
        FlexMsg(event, '抽幻獸', flex.menu())
        return

    if re.search('排行榜', msg):
        flex = game_rank()
        try:
            redis_model.data = redis_model.reply(event.source.group_id)
        except:
            if event.source.user_id not in admin_id:
                return
            redis_model.data = redis_model.reply('personal')
        data = pd.concat({k: pd.Series(v) for k, v in redis_model.data.items()}).reset_index()
        data.columns = ['LINE_UID', 'MsgType', 'Counts']
        data = data.merge(member, how = 'left', on= 'LINE_UID').fillna('未加入王國')
        flex.insert(data)
        FlexMsg(event, '排行榜', flex.flex_carousel)
        return

    if re.search('.jpg|快樂', msg):
        part = re.search('.jpg|快樂', msg).group(0)
        keyword = msg.split(part)[0]
        image_url = []
        while image_url == []:
            search = json.loads(baidu(keyword), strict=False)['data']
            for i in search:
                try:
                    image_url.append(i['thumbURL'])
                except:
                    continue
            image_url = ['https://www.post.gov.tw/post/internet/images/NoResult.jpg'] if image_url == [] else image_url
        random_img_url = random.choice(image_url)
        ImageMsg(event, random_img_url)
        return

    if re.search('|'.join(Keyword_image), msg):
        i = re.search('|'.join(Keyword_image), msg).group(0)
        key = os.listdir(os.path.join('pitchure', i))
        pick = os.path.join('pitchure',i , random.choice(key))
        uploaded_image = im.upload_image(pick)
        ImageMsg(event, uploaded_image.link)
        return 

#查看資料庫 redis_model.connect.keys()
    if re.search('清空資料庫', msg):
        for elem in redis_model.connect.keys():
            redis_model.pop(elem)
        redis_model.insert('game_room', [])
        redis_model.insert('personal', {})
        TextMsg(event, '資料庫清空完成')
        return

@handler.add(PostbackEvent)
def Postback_game(event):
    val = event.postback.data
    redis_model = redis_db()
    try:
        profile_user = line_bot_api.get_profile(event.source.user_id) 
        profile_name = profile_user.display_name
    except:
        TextMsg(event, '請先+好友~')
    try:
        redis_model.update(event, 'postback')
    except:
        None

    if re.search('抽幻獸', val):
        flex = game_pet()
        probability = []
        pet_name = []
        pet_url = []
        turn = int(re.findall('抽幻獸(.*?)抽', val)[0])
        for i in range(0, turn):
            probability.append(random.random())
        probability.sort()
        for num, i in enumerate(pet_data['Total']):
            for j in probability :
                if i > j :
                    pet_name.append(pet_data['Name'][num])
                    pet_url.append(pet_data['Url'][num])
                    probability.pop(0)
                if i <= j : break
        pick = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9][:turn]
        shuffle(pick)
        for i in pick :
            flex.flex_carousel['contents'].append(flex.report(player= profile_name, pet_url= pet_url[i], pet_name= pet_name[i] ))
        FlexMsg(event, '抽獎結果', flex.flex_carousel)
        return

    if re.search('抽獎編號', val):
        ordr = val.split('-')[1]
        room = val.split('-')[2]
        redis_model.game_room = redis_model.reply('game_room')
        if room not in redis_model.game_room: return
        load_game = redis_model.reply(room)
        if ordr == '名單':
            game_list = '\n'.join(load_game['game_list'].values())
            text= load_game['game_pool'] \
                +'----抽取人數 : ' \
                + load_game['game_max'] \
                +'\n參加名單\n--------\n' \
                + game_list
            TextMsg(event, text)
            return
        try:
            game_name = member['GAME_NAME'][member['LINE_UID'] == event.source.user_id].iloc[0]
        except:
            TextMsg(event, '尚未加入王國名單，請手動輸入抽獎編號參加抽獎')
        if ordr == '參加':
            load_game['game_list'][event.source.user_id] = game_name
            redis_model.insert(room, load_game)
            TextMsg(event, game_name +'----抽獎編號{room}--報名成功'.format(room = room))
            return
        elif ordr == '取消':
            del load_game['game_list'][event.source.user_id]
            redis_model.insert(room, load_game)
            TextMsg(event, game_name +'----抽獎編號{room}--刪除成功'.format(room = room))
            return
        elif ordr == '開獎' :
            if event.source.user_id not in admin_id:
                return
            elif load_game['game_end'] :
                return
            elif len(load_game['game_list']) < int(load_game['game_max']) :
                TextMsg(event, '參加人數不足')
                return
            else:
                r = random.sample(load_game['game_list'].keys(), k = int(load_game['game_max']))
                for num, i in enumerate(r):
                    name = load_game['game_list'][i]
                    load_game['game_draw'].append(name) 
                    text= load_game['game_pool'] \
                        +'----抽獎編號 : ' \
                        + room \
                        + '\n恭喜 {name} 中獎----請投標由左到右數來第{num}個'.format(num = str(num+1), name = name)
                    PushMsg(i, text) 
            game_list = '\n'.join(load_game['game_draw'])
            text = load_game['game_pool'] \
                 + '----' \
                 + room \
                 + '\n得獎名單\n--------\n' \
                 + game_list
            load_game['game_end'] = True
            redis_model.game_room = redis_model.game_room.remove(room)
            redis_model.insert(room, load_game)
            TextMsg(event, text)
            return

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)