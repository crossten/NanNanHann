#排行榜介面
class flex_simulator():
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
            'size' : 'mega',
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
            'wrap': True,
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