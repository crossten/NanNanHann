#linebot package
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent, UnsendEvent, StickerMessage, ImageMessage, TextMessage
    )
from flask import Flask, request, abort
#self package
import _account #帳號管理
import _staticdata #資料來源
import _nickname #轉換遊戲名稱
import _line_message #常用line-api功能簡化
import _redis #redis cloud操作
from self_package import (
    game_lottery, game_rank, game_carte, game_crusade, crawler, crawler_selenium, game_pet
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
Keyword_image = os.listdir('pitchure')

#暫存資料
join_list = {}
Unsend_list = {}

#data_source
member = _staticdata.pd_member()
pet_data = _staticdata.pd_pet()
skill_list = _staticdata.pd_skill_list()
star = _staticdata.pd_star()
adjective = _staticdata.pd_adjective()

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
    redis_model.update(event, 'Msg')
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
            redis_model.game_room = redis_model.reply('game_crusade')
            room = 'k'
            for i in range(0,6):           
                room += str(random.randint(0,9))
            while room in redis_model.game_room:
                room += str(random.randint(0,9))
            redis_model.game_room.append(room)
            card.flex(line_uid, redis_model.data[line_uid], room)
            if card.error :
                message_action.TextMsg(event, msg.split('@')[1]+ ' 尚未留下任何紀錄')
                return 
            redis_model.game_key = {
                        'game_list' : {},
                        'game_max' : card.hp, 
                        'game_end' : False
                        }
            redis_model.insert('game_crusade', redis_model.game_room)
            redis_model.insert(room, redis_model.game_key)
            message_action.FlexMsg(event, '討伐' + room, card.flex_carousel)
            return
            
        if re.search('攻擊', msg):
            try:
                name_1 = profile_user.display_name
                play_1 = _nickname.switch(member, event.source.user_id)
            except:
                message_action.TextMsg(event, '請先+好友~')
                return                
            redis_model.data = redis_model.reply(event.source.group_id)
            attack_1 = redis_model.data[event.source.user_id]['EXP']
            text = '--------攻擊結果--------\n'
            for num, i in enumerate(mention) :
                try:
                    name_2 = msg.split('@')[num+1]
                    play_2 = _nickname.switch(member, i.user_id)
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
            message_action.TextMsg(event, text)
        if re.search('加入王國', msg):
            for i, j in zip(mention, msg.split('@')[1:]) :
                join_list[i.user_id] = '{name},{game}'.format(name= j.split(' ')[0], game = j.split(' ')[1])
            message_action.TextMsg(event, '新增至加入清單\n' + msg)
            return
    except:
        None

    message_log = message_log.append(
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
        message_action.TextMsg(event, text)
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
        message_action.TextMsg(event, text)
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
        message_action.MultMsg(admin_id, text)
        message_action.TextMsg(event, profile_name+ ' 歡迎加入王國名單~')
        return
        
    if re.search('清空', msg):
        if event.source.user_id not in admin_id:
            return
        if re.search('清空抽獎紀錄', msg):
            for elem in redis_model.connect.keys():
                if elem[0] == 'r' :
                    redis_model.pop(elem)
            redis_model.insert('game_room', [])
            message_action.TextMsg(event, '清空抽獎紀錄完成')
            return
        if re.search('清空討伐紀錄', msg):
            for elem in redis_model.connect.keys():
                if elem[0] == 'k' :
                    redis_model.pop(elem)
            redis_model.insert('game_crusade', [])
            message_action.TextMsg(event, '清空討伐紀錄')
            return
        if re.search('清空資料庫', msg):
            for elem in redis_model.connect.keys():
                redis_model.pop(elem)
            redis_model.insert('game_room', [])
            redis_model.insert('game_crusade', [])
            redis_model.insert('personal', {})
            redis_model.insert('keyword', {})
            message_action.TextMsg(event, '資料庫清空完成')
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
              game = game_lottery.flex_simulator()
              message_action.FlexMsg(event, '抽獎編號' + room, game.flex(room= room, award= game_split[1], sizes= game_split[2]))
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
              player = game_split[0]
              room = game_split[1]
              if game_split[2] == '參加抽獎':
                  load_game = redis_model.reply(room)
                  load_game['game_list'][player] = player
                  redis_model.insert(room, load_game)
                  message_action.TextMsg(event, player + '({id})----報名成功'.format(id= room))
                  return
              elif game_split[2] == '取消抽獎':
                  load_game = redis_model.reply(room)
                  del load_game['game_list'][player]
                  redis_model.insert(room, load_game)
                  message_action.TextMsg(event, player + '({id})----刪除成功'.format(id= room))
                  return
              elif game_split[0] == '刪除抽獎':
                  redis_model.pop(room)
                  message_action.TextMsg(event, '刪除抽獎活動編號 : ' + room)
  
    if re.search('抽幻獸', msg):
        flex = game_pet() 
        message_action.FlexMsg(event, '抽幻獸', flex.menu())
        return

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

    if re.search('/炎炎', msg):
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
                message_action.TextMsg(event, '領取成功 :\n----------------\n' 
                    + '\n'.join(chrome.result['OK'])
                    )
            except:
                message_action.MultMsg(admin_id, '領取成功 :\n----------------\n' 
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

    keyword_dict = redis_model.reply('keyword')
    if re.search('關鍵字', msg):
        key = msg.split(' ')[1].split('=')[0]
        word = msg.split(' ')[1].split('=')[1:]
        if re.search('新增關鍵字', msg):
            if key not in keyword_dict.keys(): keyword_dict[key] = [] 
            for i in word:
                keyword_dict[key].append(i)
            redis_model.insert('keyword', keyword_dict)
            message_action.TextMsg(event, key + '--------新增成功')            
        elif re.search('刪除關鍵字', msg):
            if key in keyword_dict.keys():
                try:
                    for i in word:
                        keyword_dict[key].remove(i)
                    if keyword_dict[key] == [] : del keyword_dict[key]
                    redis_model.insert('keyword', keyword_dict)
                    message_action.TextMsg(event, key + '--------刪除成功')
                except :
                    message_action.TextMsg(event, '刪除失敗\n '+ key +' : '+ keyword_dict[key])
        return
    text_key = re.search('|'.join(keyword_dict.keys()), msg)
    image_key = re.search('|'.join(Keyword_image), msg)
    if text_key and image_key and random.random() > 0.5 : text_key = True
    else : 
        if image_key : text_key = False
    if text_key:
        part = re.search('|'.join(keyword_dict.keys()), msg).group(0)
        message_action.TextMsg(event, random.choice(keyword_dict[part]))
        return
    elif image_key:
        i = re.search('|'.join(Keyword_image), msg).group(0)
        key = os.listdir(os.path.join('pitchure', i))
        pick = os.path.join('pitchure',i , random.choice(key))
        uploaded_image = im.upload_image(pick)
        message_action.ImageMsg(event, uploaded_image.link)
        return 

@handler.add(PostbackEvent)
def Postback_game(event):
    val = event.postback.data
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

    if re.search('抽幻獸', val):
        flex = game_pet.flex_simulator()
        pick = random.choices(list(pet_data.index), weights = pet_data['Probability'], k = int(re.findall('抽幻獸(.*?)抽', val)[0]))
        for i in pick :
            flex.flex_carousel['contents'].append(flex.report(player= profile_name, 
                pet_url= pet_data['Url'][pet_data.index == i][0], pet_name= i))
        message_action.FlexMsg(event, '抽獎結果', flex.flex_carousel)
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
        game_name = profile_name + '({name})'.format(name = _nickname.switch(member, event.source.user_id))
        if game_name not in load_game['game_list'].keys() :
            load_game['game_list'][game_name] = 1
        else : 
            load_game['game_list'][game_name] += 1
        accurate = skill_list['accurate'][skill_list.index == skill][0]
        if _nickname.switch(member, event.source.user_id) == boss and boss != '未登入名稱' and boss != '未加入王國':
            sidestep = -1
        else:
            sidestep = 1 if random.randint(0, 100) < accurate else 0
        redis_model.data = redis_model.reply(event.source.group_id)
        attack = random.randint(0, redis_model.data[event.source.user_id]['EXP']) + skill_list['attack'][skill_list.index == skill][0] 
        attack = attack * sidestep if sidestep == -1 else attack
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
        message_action.TextMsg(event, text)

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
            message_action.TextMsg(event, text)
            return
        game_name = _nickname.switch(member, event.source.user_id)
        if ordr == '參加':
            load_game['game_list'][event.source.user_id] = game_name
            redis_model.insert(room, load_game)
            message_action.TextMsg(event, game_name +'----抽獎編號{room}--報名成功'.format(room = room))
            return
        elif ordr == '取消':
            del load_game['game_list'][event.source.user_id]
            redis_model.insert(room, load_game)
            message_action.TextMsg(event, game_name +'----抽獎編號{room}--刪除成功'.format(room = room))
            return
        elif ordr == '開獎' :
            if event.source.user_id not in admin_id:
                return
            elif load_game['game_end'] :
                return
            elif len(load_game['game_list']) < int(load_game['game_max']) :
                message_action.TextMsg(event, '參加人數不足')
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
                    message_action.PushMsg(i, text) 
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
            message_action.TextMsg(event, text)
            return

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
