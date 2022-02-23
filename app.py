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
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import time
import json
import os
import re
import random
import pyimgur
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from itertools import product

# 必須放上自己的Channel Access Token、Channel Secret
channel_access_token = 'channel_access_token'
channel_secret = 'channel_secret'
#管理員帳號
admin_id = ['admin_id']
#分享照片 Imgur-api
im = pyimgur.Imgur('Imgur') 

#常用定義/功能
app = Flask(__name__)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
member = pd.read_csv('data_member.csv', header= 0, index_col= None)
member['GAME_NAME'] = member['GAME_NAME'].fillna(',')+ ','+ member['LINE_NAME'] 
member['GAME_NAME']  = member['GAME_NAME'].str.split(',', expand=True)[0]
MsgLog = pd.DataFrame(columns = ['user_id', 'display_name', 'message_id', 'msg'])
Keyword_image = os.listdir('pitchure')
pet_data = pd.read_csv('data_pet.csv', header= 0, index_col= None)
pet_new = pd.DataFrame(
    data = {
        'Name': '★★★★托奇',
        'Probability': 0.0333,
        'Url': 'https://hedwig-cf.netmarble.com/forum-common/ennt/ennt_t/thumbnail/17ec567cfa314cadb4910ca8be3781bc_1644452443006_d.jpg'
        },
    index=[0])
pet_data = pd.concat([pet_data, pet_new])
pet_data.set_index('Name', inplace = True)
skill_list = pd.read_csv('data_skill.csv', header= 0, index_col= None)
skill_list.set_index('name', inplace = True)
adjective = pd.read_csv('data_adjective.csv', header= 0, index_col= None)
star = pd.read_csv('data_star.csv', header= 0, index_col= None)
join_list = {}
Unsend_list = {}


#redis_db設定 --redis-api
class redis_db():
    def __init__(self):
        self.host = 'cloud.redislabs.com'
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
        self.magnify = {
            'Msg' : random.randint(0,5),
            'Mention': random.randint(5,10),
            'Sticker' : random.randint(3,8),
            'Unsend' : -1 * random.randint(0,5),
            'Image' : random.randint(7,15),
            'Postback' : 1,
            'Attack' : 1
        }
    def reply(self, KeyName):
        val = self.connect.get(KeyName)
        return json.loads(val)
    def insert(self, KeyName, text):
        self.connect.set(KeyName, json.dumps(text))
    def pop(self, KeyName):
        self.connect.delete(KeyName)
    def read_data(self, event):
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
    def update(self, event, message_type, is_mention = False, mention_id = '', exp= 1):
        self.read_data(event)
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

#推播訊息
def PushMsg(uid, text): 
    try:
        line_bot_api.push_message(to= uid, messages= TextSendMessage(text= text))
    except:
        None
def MultMsg(uid, text): 
    try:
        line_bot_api.multicast(to= uid,messages= TextSendMessage(text= text))
    except:
        None
def MultFlexMsg(uid, text, flex): 
    try:
        line_bot_api.multicast(to= uid,
                messages=FlexSendMessage(alt_text= text, contents= json.loads(json.dumps(flex, ensure_ascii=False))
            )
        )
    except:
        None
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
            'wrap' : True,
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
        game['footer']['backgroundColor'] = '#fffdeb'
        buttonbox = self.button_box(backgroundColor= '#fffdeb')
        buttonbox['contents'].append(self.button(color= '#ffbc47', label= '參加抽獎', data= '抽獎編號-參加-' + room))
        buttonbox['contents'].append(self.button(color= '#ffbc47', label= '取消抽獎', data= '抽獎編號-取消-' + room))
        buttonbox['contents'].append(self.button(color= '#ffbc47', label= '參加名單', data= '抽獎編號-名單-' + room))
        game['footer']['contents'].append(buttonbox)
        buttonbox = self.button_box(backgroundColor= '#ffe6cc')
        buttonbox['contents'].append(self.button(color= '#ababab',label= '開獎', data= '抽獎編號-開獎-' + room))  
        game['footer']['contents'].append(buttonbox)
        return game

#排行榜介面
class game_rank():
    def __init__(self):
        self.Msgtype = {
            'EXP' : '等級',
            'Msg' : '幹話王',
            'Mention' : '人氣王',
            'Sticker' : '貼圖王',
            'Unsend' : '訊息回收車',
            'Image' : '圖片老司機',
            'Postback' : '狂點按鈕'
        }
        self.image = {
            'EXP' : 'https://tv-english.club/wp-content/uploads/2014/11/Level-Up_500px.jpg',
            'Msg' : 'https://i.imgur.com/M3MZ7Ox.jpg',
            'Mention' : 'https://i.imgur.com/7GCQVUD.png',
            'Sticker' : 'https://pic.52112.com/180623/JPG-180623A_368/glj9rVcoRS_small.jpg',
            'Unsend' : 'https://img.ltn.com.tw/Upload/news/600/2019/03/14/2726930_1.jpg',
            'Image' : 'https://i.imgur.com/aYYAzNm.png',
            'Postback' : 'https://img.sj3c.com.tw/uploads/2018/03/KEY-1-2-min.jpg'
        }
        self.flex_carousel = {'contents':[],'type':'carousel'}
    def base_box(self, layout):
        box = {
            'type': 'box',
            'layout': layout,
            'contents': []
                }
        return box
    def text_box(self, text, color):
        box = {
            'type': 'text',
            'text': text,
            'weight': 'bold',
            'color': color,
            'wrap' : True,            
            'size': 'xl'
                }
        return box
    def rank_box(self, group):
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['header'] = self.base_box(layout= 'vertical')
        game['header']['contents'].append(self.text_box(text= self.Msgtype[group] + ' 排行榜', color= '#171717'))
        game['hero'] = {
            'type': 'image',
            'url': self.image[group],
            'size': 'full',
            'aspectRatio': '20:13',
            'aspectMode': 'cover'
            }
        game['body'] = self.base_box(layout= 'vertical')
        return game
    def rowbox(self, color):
        box = {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': color,
            'height': '16px',
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
            'adjustMode': 'shrink-to-fit'
        }
        return box
    def level(self, group, data):
        game = self.rank_box(group)
        row = self.rowbox(color = '#3C3C3C')
        for i in ['LEVEL', 'LINE', '遊戲名稱', '經驗值']:
            space = self.spacebox(text= i, color= '#FFFFFF')
            row['contents'].append(space)
        game['body']['contents'].append(row)
        for i in range(len(data)):
            row = self.rowbox(color = '#FCFCFC')
            for j in ['LEVEL', 'LINE_NAME', 'GAME_NAME']:
                space = self.spacebox(text= data.iloc[i][j], color= '#000000')
                row['contents'].append(space)
            back = self.rowbox(color = '#FAD2A76E')
            bar = self.rowbox(color = '#FF641C')
            bar['width'] = data.iloc[i]['EXP']
            back['contents'].append(bar)
            row['contents'].append(back)
            game['body']['contents'].append(row)
        return game
    def rank(self, group, data):
        game = self.rank_box(group)
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
            add = add.fillna(0)
            add = add.sort_values(by=['Counts'], ascending = False).reset_index(drop=True)
            add = add.iloc[:10]
            if i == 'EXP':
                add['LEVEL'] = 1 + add['Counts'] / 100
                add['LEVEL'] = add['LEVEL'].astype('int').astype('str')
                add['EXP'] = add['Counts'] % 100
                add['EXP'] = add['EXP'].astype('str') + '%'
                self.flex_carousel['contents'].append(self.level(i, add))
                continue
            add['Counts'] = add['Counts'].astype('str')
            self.flex_carousel['contents'].append(self.rank(i, add))

#遊戲名稱
def nickname(user_id):
    try:
        name = member['GAME_NAME'][member['LINE_UID'] == user_id].iloc[0]
    except:
        name = '未加入王國'
    return name

#名片介面
class carte():
    def __init__(self):
        self.Msgtype = {
            'Msg' : '訊息數',
            'Mention' : '被Tag次數',
            'Sticker' : '貼圖次數',
            'Unsend' : '回收訊息次數',
            'Image' : '圖片次數',
            'Postback' : '按鈕點擊次數',
            'EXP' : '經驗值'
        }
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.separator = {'type': 'separator', 'color' : '#E0E0E0'}
        self.error = False
        self.hp = 0
    def base_box(self, layout):
        box = {
            'type': 'box',
            'layout': layout,
            'contents': []
                }
        return box
    def image_box(self, image_url):
        box = {
            'type': 'image',
            'url': image_url,
            'aspectMode': 'cover',
            'size': 'full'
                }
        return box
    def text_box(self, text, size):
        box = {
            'type': 'text',
            'text': text,
            'color' : '#E0E0E0',
            'wrap' : True,
            'size' : size
                }
        return box
    def button(self, label, data):
        box = {
            'type': 'button',
            'style' : 'secondary',
            'color' : '#B5B5B5',
            'wrap' : True
            }
        box['action'] = {
            'type': 'postback',
            'label': label,
            'data': data
            }
        return box
    def crusade(self, line_uid, user_data, room):
        member_keys = user_data.keys()
        bub = {'type': 'bubble', 'size' : 'mega'}
        if 'EXP' not in member_keys :
            self.error = True
            return
        else : 
            self.hp = user_data['EXP']
        bub['body'] = self.base_box(layout = 'vertical')
        bub['body']['backgroundColor'] = '#3D3D3D'
        if 'url' in member_keys:
            bub['body']['contents'].append(self.image_box(image_url = user_data['url']) )
        else :
            bub['body']['contents'].append(self.image_box(image_url= 'https://cdn0.popo.tw/uc/61/50365/O.jpg'))
        user_data['LEVEL'] = 1 + int(user_data['EXP'] / 100)
        box_vertical = self.base_box(layout = 'vertical')
        box_vertical['paddingStart'] = 'md'
        box = self.base_box(layout = 'baseline')
        text = self.text_box(text = 'Level : ' + str(user_data['LEVEL']), size = 'lg')
        box['contents'].append(text)
        box_vertical['contents'].append(box)
        box_vertical['contents'].append(self.separator)
        if nickname(line_uid) == '未加入王國' :
            game_name = user_data['name'] if 'name' in member_keys else '未登入名稱'
        else :
            game_name = nickname(line_uid)
        box = self.base_box(layout = 'baseline')
        box['spacing'] = 'sm'
        box['contents'].append(self.text_box(text = game_name, size = 'lg'))
        box_vertical['contents'].append(box)
        box = self.base_box(layout = 'baseline')
        box['spacing'] = 'sm'
        text = self.text_box(text = '生命值 : {hp}'.format(hp = self.hp), size = 'lg')
        box['contents'].append(text)
        box_vertical['contents'].append(box)
        text = self.text_box(text = '可使用技能', size = 'lg')
        box_vertical['contents'].append(text)
        box_vertical['contents'].append(self.separator)
        skill = random.choices(list(skill_list.index), k = 4)
        for i in skill:
            box = self.button(label = i, data = '討伐-{game_name}-{line_uid}-{room}-{skill}'.format(game_name = game_name, line_uid = line_uid, room = room, skill= i))
            box_vertical['contents'].append(box)
        bub['body']['contents'].append(box_vertical)
        self.flex_carousel['contents'].append(bub)        
        return

    def flex(self, line_uid, user_data):
        member_keys = user_data.keys()
        bub = {'type': 'bubble', 'size' : 'giga'}
        user_data['EXP'] = 0 if 'EXP' not in member_keys else user_data['EXP']
        bub['body'] = self.base_box(layout = 'horizontal')
        bub['body']['backgroundColor'] = '#3D3D3D'
        if 'url' in member_keys:
            bub['body']['contents'].append(self.image_box(image_url = user_data['url']) )
        else :
            bub['body']['contents'].append(self.image_box(image_url= 'https://cdn0.popo.tw/uc/61/50365/O.jpg'))
        user_data['LEVEL'] = 1 + int(user_data['EXP'] / 100)
        box_vertical = self.base_box(layout = 'vertical')
        box_vertical['paddingStart'] = 'md'
        box = self.base_box(layout = 'baseline')
        text = self.text_box(text = 'Level : ' + str(user_data['LEVEL']), size = 'lg')
        box['contents'].append(text)
        box_vertical['contents'].append(box)
        box_vertical['contents'].append(self.separator)
        if nickname(line_uid) == '未加入王國' :
            game_name = user_data['name'] if 'name' in member_keys else '未登入名稱'
        else :
            game_name = nickname(line_uid)
        box = self.base_box(layout = 'baseline')
        box['spacing'] = 'sm'
        box['contents'].append(self.text_box(text = game_name, size = 'lg'))
        box_vertical['contents'].append(box)
        for i in self.Msgtype.keys():
            if i in member_keys:
                box = self.base_box(layout = 'baseline')
                box['spacing'] = 'sm'
                text = self.text_box(text = '{row} : {data}'.format(row = self.Msgtype[i], data = user_data[i]), size = 'sm')
                box['contents'].append(text)
                box_vertical['contents'].append(box)
        exp = int(user_data['EXP'] % 100)
        bub['body']['contents'].append(box_vertical)
        bub['footer'] = self.base_box(layout = 'baseline')
        bub['footer']['width'] = str(exp) + '%'
        bub['footer']['height'] = '16px'
        bub['footer']['backgroundColor'] = '#FF6666'
        self.flex_carousel['contents'].append(bub)        

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
class game_pet():
    def __init__(self) :
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.image_url = pet_new['Url'][0]
        self.theme = '抽幻獸 {name} 活動池'.format(name = pet_new['Name'][0])
    def base_box(self, layout):
        box = {
            'type': 'box',
            'layout': layout,
            'contents': []
                }
        return box
    def image_box(self, image_url):
        box = {
            'type': 'image',
            'url': image_url,
            'size': 'full',
            'aspectMode': 'cover'
            }
        return box
    def button(self, label, data):
        box = {
            'type': 'button',
            'color' : '#E0E0E0',
            }
        box['action'] = {
            'type': 'postback',
            'label': label,
            'data': data
            }
        return box
    def menu(self):
        game = {'type': 'bubble'}
        game['header'] = self.base_box(layout = 'vertical')
        game['header']['contents'].append(self.image_box(image_url= self.image_url))
        game['footer'] = self.base_box(layout = 'horizontal')
        game['footer']['backgroundColor'] = '#FFFDEB'
        game['footer']['contents'].append(self.button(label= '單抽', data= '抽幻獸1抽'))
        game['footer']['contents'].append(self.button(label= '十抽', data= '抽幻獸10抽'))
        return game
    def report(self, player, pet_url, pet_name):
        flex = {'type': 'bubble'}
        flex['body'] = self.base_box(layout = 'vertical')
        flex['footer'] = self.base_box(layout = 'vertical')
        image = self.image_box(image_url= pet_url)
        image['aspectRatio'] = '12:9'
        flex['footer']['contents'].append(image)
        add_box = self.base_box(layout = 'vertical')
        add_box['spacing'] = 'sm'
        add_player = {
            'type': 'text',
            'text': player,
            'weight': 'bold',
            'size': 'sm',
            'margin': 'md'
            }
        add_pet = {
            'type': 'text',
            'size': 'lg',
            'color': '#555555',
            'align': 'center',
            'gravity': 'center',
            'flex': 0,
            'text': pet_name
            }
        add_theme = {
            'type': 'text',
            'text': self.theme,
            'weight': 'bold',
            'color': '#1f1f1f',
            'size': 'sm'
            }
        add_box['contents'].append(add_pet)
        flex['body']['contents'].append(add_player)
        flex['body']['contents'].append(add_theme)
        flex['body']['contents'].append(add_box)
        return flex

class chrome_coupon():
    def __init__(self):
        self.nthchid = {'天鵝' : 'li:nth-child(5)'}
        self.result = {'OK':[],  'Error':[]}
    def pull_coupon(self, game_id, coupon_id):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless") #無頭模式
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
            driver.get('https://couponweb.netmarble.com/coupon/ennt/1324') #官方網址
            time.sleep(5)
            driver.find_element(By.ID, "ip_cunpon1").click()
            driver.find_element(By.ID, "ip_cunpon1").send_keys(coupon_id) #填入序號
            driver.find_element(By.ID, "ip_cunpon2").click()
            driver.find_element(By.ID, "ip_cunpon2").send_keys(game_id) #填入帳號
            driver.find_element(By.CSS_SELECTOR, "#serverList .select_icon").click() #選伺服器
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, self.nthchid['天鵝']).click()
            driver.find_element(By.CSS_SELECTOR, "#submitCoupon > p").click()
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, "li:nth-child(2) p").click() #確認角色
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, ".go_main > p").click() #確認送出
            driver.quit()
            self.result['OK'].append(game_id)
        except:
            self.result['Error'].append(game_id)

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
    game_name = nickname(profile_user)
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
    try:
        mention = event.message.mention.mentionees
        for i in mention :
            redis_model.update(event, 'Mention', True, i.user_id)
        if re.search('查詢', msg):
            card = carte()
            redis_model.data = redis_model.reply(event.source.group_id)
            try:
                for num, i in enumerate(mention) :
                    line_uid = i.user_id
                    card.flex(line_uid, redis_model.data[line_uid])
                    if num == 10: break
                FlexMsg(event, '查詢名片', card.flex_carousel)
            except:
                TextMsg(event, msg.split('@')[1]+ ' 尚未留下任何紀錄')
        if re.search('討伐', msg):
            card = carte()
            line_uid = mention[0].user_id
            redis_model.game_room = redis_model.reply('game_crusade')
            room = 'k'
            for i in range(0,6):           
                room += str(random.randint(0,9))
            while room in redis_model.game_room:
                room += str(random.randint(0,9))
            redis_model.game_room.append(room)
            card.crusade(line_uid, redis_model.data[line_uid], room)
            if card.error :
                TextMsg(event, msg.split('@')[1]+ ' 尚未留下任何紀錄')
                return 
            redis_model.game_key = {
                        'game_list' : {},
                        'game_max' : card.hp, 
                        'game_end' : False
                        }
            redis_model.insert('game_crusade', redis_model.game_room)
            redis_model.insert(room, redis_model.game_key)
            FlexMsg(event, '討伐' + room, card.flex_carousel)
            return
            
        if re.search('攻擊', msg):
            try:
                name_1 = profile_user.display_name
                play_1 = nickname(event.source.user_id)
            except:
                TextMsg(event, '請先+好友~')
                return                
            redis_model.data = redis_model.reply(event.source.group_id)
            attack_1 = redis_model.data[event.source.user_id]['EXP']
            text = '--------攻擊結果--------\n'
            for num, i in enumerate(mention) :
                try:
                    name_2 = msg.split('@')[num+1]
                    play_2 = nickname(i.user_id)
                    attack_2 = redis_model.data[i.user_id]['EXP']
                    game = random.randint(0, attack_1) - random.randint(0, attack_2)
                    exp = random.randint(0, int(attack_2 /10)+1) if game > 0 else -1 * random.randint(0, int(attack_1 /10)+1)
                    redis_model.update(event, 'Attack', exp= exp)
                    if game > 0 :
                        text += '{name_1}({play_1}) 攻擊 {name_2}({play_2}) 成功 增加經驗值 {exp}\n'.format(name_1= name_1, play_1= play_1, name_2= name_2, play_2= play_2 ,exp= exp)
                    else :
                        text += '{name_1}({play_1}) 攻擊 {name_2}({play_2}) 失敗 經驗值 {exp}\n'.format(name_1= name_1, play_1= play_1, name_2= name_2, play_2= play_2 ,exp= exp)
                except:
                    text += '{name_2} 未建立資料，攻擊無效'.format(name_2 = name_2)
            TextMsg(event, text)
        if re.search('加入王國', msg):
            for i, j in zip(mention, msg.split('@')[1:]) :
                join_list[i.user_id] = '{name},{game}'.format(name= j.split(' ')[0], game = j.split(' ')[1])
            TextMsg(event, '新增至加入清單\n' + msg)
            return
    except:
        None

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
        if event.source.user_id not in admin_id:
           return
        text = 'LINE_UID,LINE_NAME,GAME_NAME\n' 
        for i, j in zip(join_list.keys(), join_list.values()):
            text += '{uid},{name}\n'.format(uid= i, name= j)
        join_list = {}
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
        TextMsg(event, profile_name+ ' 歡迎加入王國名單~')
        return
        
    if re.search('清空', msg):
        if event.source.user_id not in admin_id:
            return
        if re.search('清空抽獎紀錄', msg):
            for elem in redis_model.connect.keys():
                if elem[0] == 'r' :
                    redis_model.pop(elem)
            TextMsg(event, '清空抽獎紀錄完成')
            return
        if re.search('清空討伐紀錄', msg):
            for elem in redis_model.connect.keys():
                if elem[0] == 'k' and elem!= 'keyword':
                    redis_model.pop(elem)
            TextMsg(event, '清空討伐紀錄')
            return
        if re.search('清空資料庫', msg):
            for elem in redis_model.connect.keys():
                redis_model.pop(elem)
            redis_model.insert('game_room', [])
            redis_model.insert('game_crusade', [])
            redis_model.insert('personal', {})
            redis_model.insert('keyword', {})
            TextMsg(event, '資料庫清空完成')
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

    if re.search('/炎炎', msg):
        chrome = chrome_coupon()
        game_id = redis_model.reply('coupon_ninokuni')
        if re.search('代領序號', msg):
            MultMsg(admin_id, '開始執行序號領取，結束後通知管理員，期間不受理代領')
            if game_id['天鵝']['switch'] : 
                TextMsg(event, '機器人領取序號中......')
            game_id['天鵝']['switch'] = True
            redis_model.insert('coupon_ninokuni', game_id)
            for i, j in product(game_id['天鵝'].keys(), msg.split(' ')[1:]):
                if i == 'switch' : continue
                elif j in game_id['天鵝'][i] : continue
                else:
                    chrome.pull_coupon(i, j)
                    game_id['天鵝'][i].append(j)
            game_id['天鵝']['switch'] = False
            redis_model.insert('coupon_ninokuni', game_id)
            try:
                TextMsg(event, '領取成功 :\n----------------\n' 
                    + '\n'.join(chrome.result['OK'])
                    )
            except:
                MultMsg(admin_id, '領取成功 :\n----------------\n' 
                    + '\n'.join(chrome.result['OK']) 
                    )
            return
        elif re.search('新增帳號', msg):
            for i in msg.split(' ')[1:]:
                game_id['天鵝'][id] = []
                redis_model.insert('coupon_ninokuni', game_id)
            TextMsg(event, id + '--------新增成功')     
            return
        TextMsg(event, '任務不明!!')     
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

    keyword_dict = redis_model.reply('keyword')
    if re.search('關鍵字', msg):
        key = msg.split(' ')[1].split('=')[0]
        word = msg.split(' ')[1].split('=')[1:]
        if re.search('新增關鍵字', msg):
            if key not in keyword_dict.keys(): keyword_dict[key] = [] 
            for i in word:
                keyword_dict[key].append(i)
            redis_model.insert('keyword', keyword_dict)
            TextMsg(event, key + '--------新增成功')            
        elif re.search('刪除關鍵字', msg):
            if key in keyword_dict.keys():
                try:
                    for i in word:
                        keyword_dict[key].remove(i)
                    if keyword_dict[key] == [] : del keyword_dict[key]
                    redis_model.insert('keyword', keyword_dict)
                    TextMsg(event, key + '--------刪除成功')
                except :
                    TextMsg(event, '刪除失敗\n '+ key +' : '+ keyword_dict[key])
        return
    text_key = re.search('|'.join(keyword_dict.keys()), msg)
    image_key = re.search('|'.join(Keyword_image), msg)
    if text_key and image_key and random.random() > 0.5 : text_key = True
    else : 
        if image_key : text_key = False
    if text_key:
        part = re.search('|'.join(keyword_dict.keys()), msg).group(0)
        TextMsg(event, random.choice(keyword_dict[part]))
        return
    elif image_key:
        i = re.search('|'.join(Keyword_image), msg).group(0)
        key = os.listdir(os.path.join('pitchure', i))
        pick = os.path.join('pitchure',i , random.choice(key))
        uploaded_image = im.upload_image(pick)
        ImageMsg(event, uploaded_image.link)
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
        redis_model.update(event, 'Postback')
    except:
        None

    if re.search('抽幻獸', val):
        flex = game_pet()
        pick = random.choices(list(pet_data.index), weights = pet_data['Probability'], k = int(re.findall('抽幻獸(.*?)抽', val)[0]))
        for i in pick :
            flex.flex_carousel['contents'].append(flex.report(player= profile_name, 
                pet_url= pet_data['Url'][pet_data.index == i][0], pet_name= i))
        FlexMsg(event, '抽獎結果', flex.flex_carousel)
        return

    if re.search('討伐', val) :
        boss = val.split('-')[1]
        boss_id = val.split('-')[2]
        room = val.split('-')[3]
        skill = val.split('-')[4]
        redis_model.game_room = redis_model.reply('game_crusade')
        if room not in redis_model.game_room : return
        load_game = redis_model.reply(room)
        if load_game['game_end'] == True : return
        game_name = profile_name + '({name})'.format(name = nickname(event.source.user_id))
        if game_name not in load_game['game_list'].keys() :
            load_game['game_list'][game_name] = 1
        else : 
            load_game['game_list'][game_name] += 1
        accurate = skill_list['accurate'][skill_list.index == skill][0]
        if nickname(event.source.user_id) == boss and boss != '未登入名稱' and boss != '未加入王國':
            sidestep = -1
        else:
            sidestep = 1 if random.randint(0, 100) < accurate else 0
        redis_model.data = redis_model.reply(event.source.group_id)
        attack = random.randint(0, redis_model.data[event.source.user_id]['EXP']) + skill_list['attack'][skill_list.index == skill][0] 
        attack = attack * sidestep if sidestep == 0 else attack
        exp = random.randint(0, skill_list['attack'][skill_list.index == skill][0]) * sidestep
        if sidestep == 1 :
            redis_model.update(event, 'Attack', exp = exp)
        else :
            redis_model.update(event, 'Attack', exp = -1* exp)
        loss_hp = int(load_game['game_max']) - attack
        if loss_hp <= 0 :
            loss_hp = 0
            boss_exp = -1 * exp * len(load_game['game_list'].keys()) * sidestep
            boss_message = '成功討伐 {boss} 額外獲得經驗 {exp}'.format(boss= boss, exp= exp) + '\n' \
                + '{boss} 損失經驗 {exp}'.format(boss = boss, exp = boss_exp) +'\n' \
                + '------累積攻擊紀錄------\n'  \
                + str(load_game['game_list'])[1:-1].replace(',','\n')
            redis_model.update(event, 'Attack', is_mention= True, mention_id= boss_id, exp = boss_exp)
            load_game['game_end'] = True
        else :
            boss_message = '{boss} 剩餘生命 : '.format(boss= boss) + format(loss_hp, ',') + '\n' \
                + '野生 {boss} 活躍中'.format(boss = boss)
        obj_end = '碎片' if sidestep == 0 else ''   
        obj = random.choices(star['Star'], weights= star['Per'])[0]+ random.choice(adjective['list']) +'的'+ boss + obj_end
        if sidestep == 1:
            sidestep = '成功' 
        elif sidestep == -1 :
            sidestep = '自殘'
        else :
            sidestep = '失敗'
        text = '{game_name} 嘗試使用 {skill} 攻擊 {boss}'.format(game_name= game_name, skill= skill, boss= boss) +'\n' \
            + '命中判斷 : ' + sidestep + '\n' \
            + '造成傷害 : ' + format(attack, ',')  + '\n' \
            + '獲得經驗 : ' + format(exp, ',') + '\n' \
            + '獲得道具 : ' + obj + '\n' \
            + '------------------\n'  \
            + boss_message
        load_game['game_max'] = str(loss_hp)
        redis_model.insert(room, load_game)
        TextMsg(event, text)

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
        game_name = nickname(event.source.user_id)
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
            redis_model.game_room.remove(room)
            redis_model.insert('game_room', redis_model.game_room)
            redis_model.insert(room, load_game)
            TextMsg(event, text)
            return

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
