import _staticdata
import _nickname 

member = _staticdata.pd_member()

#名片介面
class flex_simulator():
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
        if _nickname.switch(member, line_uid) == '未加入王國' :
            game_name = user_data['name'] if 'name' in member_keys else '未登入名稱'
        else :
            game_name = _nickname.switch(member, line_uid)
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