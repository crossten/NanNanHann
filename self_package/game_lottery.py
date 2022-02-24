import re

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