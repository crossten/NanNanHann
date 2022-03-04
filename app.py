
#linebot package
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent, UnsendEvent, StickerMessage, ImageMessage, TextMessage, Sender
    )
from flask import Flask, request, abort
#self package
import _account #帳號管理
import _staticdata #資料來源
import _nickname #轉換遊戲名稱
import _line_message #常用line-api功能簡化
import _redis #redis cloud操作

from self_package import (
    game_lottery, game_rank, game_carte, game_crusade, game_kingdom, game_attack, crawler, crawler_selenium, game_pet, game_wolf
    )
#一般package
import pandas as pd
import numpy as np
import json
import os
import re
import random
import pyimgur
from itertools import product

#account管理
channel_access_token = _account.line_token()
channel_secret = _account.line_secret()
admin_id = _account.admin()
im = pyimgur.Imgur(_account.imgur()) 

#基礎設定
app = Flask(__name__)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
message_action= _line_message.menu()
message_log = pd.DataFrame(columns = ['user_id', 'display_name', 'message_id', 'msg'])
Keyword_image = os.listdir('picture')

#暫存資料
join_list = {}
Unsend_list = {}
#data_source
member = _staticdata.pd_member()
push_id = member.index[member['PUSH_MSG'] == 1]
pet_data = _staticdata.pd_pet()

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
    message_action.TextMsg(event, '週週抽獎抽不完~ 請輸入遊戲名字~ \n例如 : 白涵公主,加入王國')
    return

#圖片訊息紀錄
@handler.add(MessageEvent, message= ImageMessage)
def Image_dict(event):
    redis_model = _redis.redis_db()
    redis_model.update(event, 'Image')

#貼圖訊息紀錄
@handler.add(MessageEvent, message= StickerMessage)
def Sticker_dict(event):
    redis_model = _redis.redis_db()
    redis_model.update(event, 'Sticker')

#收回訊息紀錄
@handler.add(UnsendEvent)
def Unsend_dict(event):
    global message_log, Unsend_list
    redis_model = _redis.redis_db()
    message_log['message_id'] = message_log['message_id'].fillna(0).astype(np.int64).astype('str')
    redis_model.update(event, 'Unsend')
    profile_user = event.source.user_id
    message_id = event.unsend.message_id
    display_name = message_log['display_name'][(message_log['user_id'] == profile_user) & (message_log['message_id'] == message_id)].iloc[-1]
    game_name = _nickname.switch(member, profile_user)
    Unsend_msg = message_log['msg'][(message_log['user_id'] == profile_user) & (message_log['message_id'] == message_id)].iloc[-1]
    Unsend_list[message_id] = ["{display}({game})".format(display= display_name,game = game_name), Unsend_msg]
    return 

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def reply(event):
    global join_list, message_log, Unsend_list
    msg = event.message.text
    redis_model = _redis.redis_db()
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
#記錄訊息暫存
    message_log = message_log.append(
                {
            'user_id': event.source.user_id, 
            'message_id': event.message.id, 
            'display_name': profile_name,
            'msg': msg
            }, 
            ignore_index=True
        )  

#增加經驗值
    redis_model.update(event, 'Msg')

#tag相關指令
    try:
        mention = event.message.mention.mentionees
        for i in mention :
            redis_model.update(event, 'Mention', True, i.user_id)
        if re.search('查詢', msg):
            card = game_carte.flex_simulator()
            redis_model.data = redis_model.reply(event.source.group_id)
            try:
                for num, i in enumerate(mention) :
                    line_uid = i.user_id
                    card.flex(line_uid, redis_model.data[line_uid])
                    if num == 10: break
                message_action.FlexMsg(event, '查詢名片', card.flex_carousel)
            except:
                message_action.TextMsg(event, msg.split('@')[1]+ ' 尚未留下任何紀錄')

        if re.search('討伐', msg):
            card = game_crusade.flex_simulator()
            line_uid = mention[0].user_id
            game_crusade.process(redis_model, card, line_uid)
            message_action.FlexMsg(event, '討伐-個人', card.flex_carousel)
            return
            
        if re.search('攻擊', msg):
            try:
                name_1 = profile_user.display_name
            except:
                message_action.TextMsg(event, '請先+好友~')
                return                
            redis_model.data = redis_model.reply(event.source.group_id)
            total = []
            text = '------------------攻擊結果------------------\n'
            for num, i in enumerate(mention) :
                try:
                    name_2 = msg.split('@')[num+1]
                    result = game_attack.calculate(
                        redis_model,
                        event, 
                        attack_1 = redis_model.data[event.source.user_id]['EXP'], 
                        attack_2 = redis_model.data[i.user_id]['EXP'], 
                        name_2 = msg.split('@')[num+1], 
                        play_2 = _nickname.switch(member, i.user_id)
                        )
                    text += result['text']
                    total.append(result['exp'])
                except:
                    text += '{name_2} 未建立資料，攻擊無效'.format(name_2 = name_2)                            
            text += '-------------------------------------------\n'
            text += '經驗結算 : {exp}'.format(exp = format(sum(total),','))
            sender = Sender(
                    name = '{name}({play})'.format(name= name_1, play= _nickname.switch(member, event.source.user_id)),
                    icon_url = profile_user.picture_url
                )            
            message_action.TextMsg(event, text, sender = sender)

        if re.search('加入王國', msg):
            for i, j in zip(mention, msg.split('@')[1:]) :
                join_list[i.user_id] = '{name},{game}'.format(name= j.split(' ')[0], game = j.split(' ')[1])
            message_action.TextMsg(event, '新增至加入清單\n' + msg)
            return
    except:
        None

#訊息回收回放
    try:
        log = list(Unsend_list.keys())[0]
        text = '{name} 剛剛收回了 : {message}'.format(name= Unsend_list[log][0], message = Unsend_list[log][1])
        del Unsend_list[log]
        message_action.TextMsg(event, text)
        return
    except:
        None

#王國成員
    if re.search('王國成員', msg):
        card = game_kingdom.flex_simulator()
        card.insert(member['GAME_NAME'][member['PUSH_MSG'] == 1])
        message_action.FlexMsg(event, '王國成員清單', card.flex_carousel)
        return

#隨機討伐
    if re.search('隨機原野', msg):
        card = game_crusade.flex_simulator()
        source = redis_model.reply(event.source.group_id)
        monster = pd.DataFrame()
        monster_list = pd.concat({k: pd.Series(v) for k, v in source.items()}).reset_index()
        monster_list.columns = ['LINE_UID', 'MsgType', 'Counts']
        monster = pd.concat([monster ,monster_list])
        monster = random.choices(list(monster['LINE_UID'][(monster['MsgType'] == 'url')]), k = (random.randint(1,10)))
        for add in monster:
            game_crusade.process(redis_model, card, add)
        message_action.FlexMsg(event, '討伐-mix', card.flex_carousel)
        return

#剩餘原野
    if re.search('野生原野', msg):
        card = game_crusade.flex_simulator()
        source = redis_model.reply('game_crusade')
        legal = redis_model.reply(event.source.group_id).keys()
        if source == [] : return message_action.TextMsg(event, '原野空蕩蕩一片。。。=}>')
        for add in source[:10]:
            data =  redis_model.reply(add)
            if data['boss_uid'] not in legal : continue
            game_crusade.call(redis_model, card, data['boss_uid'], add)
        message_action.FlexMsg(event, '討伐-mix', card.flex_carousel)
        return

#開始遊戲
    if re.search('開始遊戲', msg):
        room = game_wolf.create(redis_model)
        game = game_wolf.flex_simulator()
        message_action.FlexMsg(event, '狼人殺開始囉', game.start(room))
        return

#指令:加入王國相關
    if re.search('加入清單', msg):
        if event.source.user_id not in admin_id and admin_id != []:
           return
        text = 'LINE_UID,LINE_NAME,GAME_NAME\n' 
        for i, j in zip(join_list.keys(), join_list.values()):
            text += '{uid},{name}\n'.format(uid= i, name= j)
        join_list = {}
        message_action.TextMsg(event, text)
        return

    if re.search('加入王國', msg):
        if re.search('@', msg):
            message_action.TextMsg(event, msg.split('@')[1:] + '讀取失敗，需先加好友')
            return
        text = event.source.user_id \
            + '\n' \
            + profile_name \
            + '\n' \
            + msg.split(',')[0] \
            + '\n大頭貼 : ' \
            + profile_user.picture_url
        join_list[event.source.user_id] = '{name},{game}'.format(name= profile_name, game = msg.split(',')[0])
        message_action.MultMsg(admin_id, text)
        message_action.TextMsg(event, profile_name+ ' 歡迎加入王國名單~')
        return

#指令:抽獎活動
    if re.search('抽獎', msg):
        game_split = msg.split(',')
        redis_model.game_room = redis_model.reply('game_room')
        if game_split[0] == '舉辦抽獎' :
              pool, max = game_split[1:3]
              room = game_lottery.create(redis_model, pool, max)
              game = game_lottery.flex_simulator()
              message_action.FlexMsg(event, '抽獎編號' + room, game.flex(room= room, award= pool, sizes= max))
              return
        elif msg == '查看抽獎' :
              flex_carousel = {'contents':[],'type':'carousel'}
              for num, i in enumerate(redis_model.reply('game_room')) :
                  load_game = redis_model.reply(i)
                  game = game_lottery.flex_simulator()
                  flex_carousel['contents'].append(game.flex(room= i, award= load_game['game_pool'], sizes= load_game['game_max']))
                  if num == 10: break
              message_action.FlexMsg(event, '抽獎編號-mix', flex_carousel)
              return
        elif game_split[1] in redis_model.game_room:
              player, room, key = game_split[0:3]
              if key == '參加抽獎':
                  game_lottery.join(redis_model, pool, player)
                  message_action.TextMsg(event, player + '({id})----報名成功'.format(id= room))
                  return
              elif key == '取消抽獎':
                  game_lottery.cancel(redis_model, pool, player)
                  message_action.TextMsg(event, player + '({id})----刪除成功'.format(id= room))
                  return
              elif key == '刪除抽獎':
                  redis_model.pop(room)
                  message_action.TextMsg(event, '刪除抽獎活動編號 : ' + room)

  #指令:抽幻獸
    if re.search('抽幻獸', msg):
        flex = game_pet() 
        message_action.FlexMsg(event, '抽幻獸', flex.menu())
        return

  #指令:排行榜
    if re.search('排行榜', msg):
        flex = game_rank.flex_simulator()
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
        message_action.FlexMsg(event, '排行榜', flex.flex_carousel)
        return

  #指令:代領作業
    if re.search('/白白', msg):
        chrome = crawler_selenium.chrome_coupon()
        game_id = redis_model.reply('coupon_ninokuni')
        if re.search('代領序號', msg):
            message_action.MultMsg(admin_id, '開始執行序號領取，結束後通知管理員，期間不受理代領')
            if game_id['天鵝']['switch'] : 
                message_action.TextMsg(event, '機器人領取序號中......')
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
                message_action.TextMsg(event, '領取成功 :\n------------------n' 
                    + '\n'.join(chrome.result['OK'])
                    )
            except:
                message_action.MultMsg(admin_id, '領取成功 :\n------------------n' 
                    + '\n'.join(chrome.result['OK']) 
                    )
            return
        elif re.search('新增帳號', msg):
            for i in msg.split(' ')[1:]:
                game_id['天鵝'][id] = []
                redis_model.insert('coupon_ninokuni', game_id)
            message_action.TextMsg(event, id + '--------新增成功')     
            return
        message_action.TextMsg(event, '任務不明!!')     
        return 

  #指令:關鍵字搜圖
    if re.search('.jpg|快樂', msg):
        part = re.search('.jpg|快樂', msg).group(0)
        keyword = msg.split(part)[0]
        image_url = []
        while image_url == []:
            search = json.loads(crawler.baidu(keyword), strict=False)['data']
            for i in search:
                try:
                    image_url.append(i['thumbURL'])
                except:
                    continue
            image_url = ['https://www.post.gov.tw/post/internet/images/NoResult.jpg'] if image_url == [] else image_url
        random_img_url = random.choice(image_url)
        message_action.ImageMsg(event, random_img_url)
        return

  #指令:關鍵字新增刪除
    keyword_dict = redis_model.reply('Keyword')
    if re.search('關鍵字', msg):
        key = msg.split(' ')[1].split('=')[0]
        word = msg.split(' ')[1].split('=')[1:]
        if re.search('新增關鍵字', msg):
            if key not in keyword_dict.keys(): keyword_dict[key] = [] 
            for i in word:
                keyword_dict[key].append(i)
            redis_model.insert('Keyword', keyword_dict)
            message_action.TextMsg(event, key + '--------新增成功')            
        elif re.search('刪除關鍵字', msg):
            if key in keyword_dict.keys():
                try:
                    for i in word:
                        keyword_dict[key].remove(i)
                    if keyword_dict[key] == [] : del keyword_dict[key]
                    redis_model.insert('Keyword', keyword_dict)
                    message_action.TextMsg(event, key + '--------刪除成功')
                except :
                    message_action.TextMsg(event, '刪除失敗\n '+ key +' : '+ keyword_dict[key])
        return

  #指令:關鍵字文字 & 圖片抽選
    text_key = re.search('|'.join(keyword_dict.keys()), msg)
    image_key = re.search('|'.join(Keyword_image), msg)
    if text_key and image_key and random.random() > 0.65 : text_key = True
    else : 
        if image_key : text_key = False
    if text_key:
        part = re.search('|'.join(keyword_dict.keys()), msg).group(0)
        message_action.TextMsg(event, random.choice(keyword_dict[part]))
        return
    elif image_key:
        i = re.search('|'.join(Keyword_image), msg).group(0)
        key = os.listdir(os.path.join('picture', i))
        pick = os.path.join('picture',i , random.choice(key))
        uploaded_image = im.upload_image(pick)
        message_action.ImageMsg(event, uploaded_image.link)
        return 

@handler.add(PostbackEvent)
def Postback_game(event):
    key = event.postback.data
    redis_model = _redis.redis_db()
    try:
        profile_user = line_bot_api.get_profile(event.source.user_id) 
        profile_name = profile_user.display_name
    except:
        message_action.TextMsg(event, '請先+好友~')
    try:
        redis_model.update(event, 'Postback')
    except:
        None

#按鍵:抽幻獸
    if re.search('抽幻獸', key):
        flex = game_pet.flex_simulator()
        pick = random.choices(list(pet_data.index), weights = pet_data['Probability'], k = int(re.findall('抽幻獸(.*?)抽', val)[0]))
        for i in pick :
            flex.flex_carousel['contents'].append(flex.report(player= profile_name, 
                pet_url= pet_data['Url'][pet_data.index == i][0], pet_name= i))
        message_action.FlexMsg(event, '抽獎結果', flex.flex_carousel)
        return

#按鍵:討伐技能
    if re.search('討伐', key) :
        game = game_crusade.postback(event.postback.data)
        game_name = profile_name + '({name})'.format(name = _nickname.switch(member, event.source.user_id))
        if game.load(redis_model, game_name) == False :return
        text = game.text(redis_model, event)
        sender = Sender(
                name = game_name,
                icon_url = profile_user.picture_url
            )            
        message_action.TextMsg(event, text, sender = sender)
        return

#按鍵:抽獎功能
    if re.search('抽獎編號', key):
        game = game_lottery.postback(event.postback.data)
        if game.load(redis_model) == False :return
        if game.ordr == '名單':
            game.joinlist(message_action, event)
            return
        game_name = _nickname.switch(member, event.source.user_id)
        if game.ordr == '參加':
            game.join(redis_model, game_name, event, message_action)
        if game.ordr == '取消':
            game.cancel(redis_model, game_name, event, message_action)
            return
        elif game.ordr == '開獎' :
            game.draw(admin_id, redis_model, event, message_action)
            return

#按鍵:點名
    if re.search('點名', key) :
        if event.source.user_id not in admin_id:
            message_action.TextMsg(event, '你不是鳥鳥老師~無法使用點名功能~')
        try:
            line_uid, game_name = key.split('-')[1:]
            message_action.PushMsg(line_uid, '鳥鳥老師點名中~~點到請舉手~~{game_name}'.format(game_name = game_name))
            message_action.TextMsg(event, '鳥鳥老師點名中~')
        except:
            message_action.TextMsg(event, '本月額度已使用完畢無法推播~')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
