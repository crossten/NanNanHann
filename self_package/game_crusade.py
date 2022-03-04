import random
import _staticdata
import _nickname 

skill_list = _staticdata.pd_skill_list()
star = _staticdata.pd_star()
adjective = _staticdata.pd_adjective()
member = _staticdata.pd_member()

#討伐介面
class flex_simulator():
    def __init__(self):
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
            'color' : '#E0E0E0'
            }
        box['action'] = {
            'type': 'postback',
            'label': label,
            'data': data
            }
        return box
    def flex(self, line_uid, user_data, room, hp_percentage = '100%', new_game = True, game_loss = 0):
        member_keys = user_data.keys()
        bub = {'type': 'bubble', 'size' : 'mega'}
        if 'EXP' not in member_keys :
            self.error = True
            return
        else : 
            self.hp = user_data['EXP'] if new_game else game_loss
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
        if _nickname.switch(member, line_uid) == '未加入王國' :
            game_name = user_data['name'] if 'name' in member_keys else '未登入名稱'
        else :
            game_name = _nickname.switch(member, line_uid)
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
        bub['footer'] = self.base_box(layout = 'baseline')
        bub['footer']['width'] = hp_percentage
        bub['footer']['height'] = '16px'
        bub['footer']['backgroundColor'] = '#FF6666'
        self.flex_carousel['contents'].append(bub)        
        return

def process(redis_model, card, line_uid):
    redis_model.game_room = redis_model.reply('game_crusade')
    room = 'k'
    for i in range(0,6):           
        room += str(random.randint(0,9))
    while room in redis_model.game_room:
        room += str(random.randint(0,9))
    redis_model.game_room.append(room)
    card.flex(line_uid, redis_model.data[line_uid], room)
    redis_model.game_key = {
                'game_list' : {},
                'boss_uid' : line_uid,
                'game_loss' : card.hp, 
                'game_init' : card.hp, 
                'game_end' : False
                }
    redis_model.insert('game_crusade', redis_model.game_room)
    redis_model.insert(room, redis_model.game_key)

def call(redis_model, card, line_uid, room):
    redis_model.game_room = redis_model.reply(room)
    hp = int(redis_model.game_room['game_loss']) / int(redis_model.game_room['game_init']) *100
    card.flex(
        line_uid, 
        redis_model.data[line_uid], 
        room, 
        hp_percentage = str(int(hp)) +'%', 
        new_game = False, 
        game_loss = redis_model.game_room['game_loss']
        )

class postback():
    def __init__(self, data):
        self.boss, self.boss_id, self.room, self.skill = data.split('-')[1:5]
    def load(self, redis_model, game_name):
        redis_model.game_room = redis_model.reply('game_crusade')
        if self.room not in redis_model.game_room : return False
        self.load_game = redis_model.reply(self.room)
        if self.load_game['game_end'] == True : return False
        if game_name not in self.load_game['game_list'].keys() :
            self.load_game['game_list'][game_name] = 1
        else : 
            self.load_game['game_list'][game_name] += 1
        return True
    def text(self, redis_model, event):
        redis_model.data = redis_model.reply(event.source.group_id)
        attack_exp = redis_model.data[event.source.user_id]['EXP']
        attack = random.randint(0, attack_exp) + skill_list['attack'][skill_list.index == self.skill][0] 
        if event.source.user_id == self.boss_id :
            sidestep = -1
        else:
            sidestep = 1 if random.randint(0, 100) < skill_list['accurate'][skill_list.index == self.skill][0] else 0
        exp = random.randint(0, skill_list['attack'][skill_list.index == self.skill][0]) * sidestep
        redis_model.update(event, 'Attack', exp = exp)
        loss_hp = int(self.load_game['game_loss']) - attack * sidestep * sidestep
        if loss_hp <= 0 :
            loss_hp = 0
            boss_exp = redis_model.data[self.boss_id]['EXP']
            random_loss = random.randint(1, int(boss_exp /attack_exp) +5)
            boss_exp = -1 * exp * len(self.load_game['game_list'].keys()) * sidestep * random_loss * random_loss
            exp = exp * random_loss
            boss_message = '成功討伐 {boss} 額外獲得經驗 {exp}'.format(boss= self.boss, exp= exp) + '\n' \
                + '{boss} 損失經驗 {exp}'.format(boss = self.boss, exp = boss_exp) +'\n' \
                + '------------------累積攻擊紀錄------------------\n'  \
                + str(self.load_game['game_list'])[1:-1].replace(',','\n')
            redis_model.game_room.remove(self.room)
            redis_model.insert('game_crusade', redis_model.game_room)
            redis_model.pop('room')
            redis_model.update(event, 'Attack', exp = exp)
            redis_model.update(event, 'Attack', is_mention= True, mention_id= self.boss_id, exp = boss_exp)
            redis_model.update(event, 'Dead', is_mention= True, mention_id= self.boss_id, exp = 0)
            self.load_game['game_end'] = True
        else :
            boss_message = '野生 {boss} 剩餘生命 活躍中: '.format(boss= self.boss) + format(loss_hp, ',') 
        obj_end = '碎片' if sidestep == 0 else ''   
        obj = random.choices(star['Star'], weights= star['Per'])[0]+ random.choice(adjective['list']) +'的'+ self.boss + obj_end
        if sidestep == 1:
            sidestep = '成功' 
        elif sidestep == -1 :
            sidestep = '自殘'
        else :
            sidestep = '失敗'
        text = '嘗試使用 {skill} 攻擊 {boss}'.format(skill= self.skill, boss= self.boss) +'\n' \
            + '命中判斷 : ' + sidestep  \
            + '  造成傷害 : ' + format(attack, ',') \
            + '  獲得經驗 : ' + format(exp, ',') \
            + '  獲得道具 : ' + obj + '\n' \
            + '------------------------------------\n'  \
            + boss_message
        self.load_game['game_loss'] = str(loss_hp)
        redis_model.insert(self.room, self.load_game)
        return text