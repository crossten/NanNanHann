import random
import _staticdata
import _nickname 

skill_list = _staticdata.pd_skill_list()
member = _staticdata.pd_member()

#名片介面
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
        box['Offset'] = {
            'offsetTop' : 'xs'
            }
        box['action'] = {
            'type': 'postback',
            'label': label,
            'data': data
            }
        return box
    def flex(self, line_uid, user_data, room):
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
        self.flex_carousel['contents'].append(bub)        
        return
