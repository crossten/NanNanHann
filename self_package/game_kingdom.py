#排行榜介面
class flex_simulator():
    def __init__(self):
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.separator = {'type': 'separator', 'color' : '#AAAAAA'}
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
    def postbackbox(self, label, data):
        box = {
            'type' : 'postback',
            'label' : label,
            'data' : data
        }
        return box
    def insert(self, data):
        game = {
            'type': 'bubble',
            'size' : 'giga',
            }
        game['body'] = self.base_box(layout= 'vertical')
        row = self.rowbox(color = '#3C3C3C')
        for i in ['第一排', '第二排', '第三排']:
            space = self.spacebox(text= i, color= '#FFFFFF')
            row['contents'].append(space)
        game['body']['contents'].append(row)
        for i in range(len(data)):
            if i % 3 != 0 : continue
            row = self.rowbox(color = '#FCFCFC')
            row['contents'].append(self.separator)
            for j in range(3):
                i += 1                
                if i >= len(data) : break
                space = self.spacebox(text= data[i], color= '#000000')
                space['action'] = self.postbackbox(
                    label = '點名', 
                    data = '點名-{UID}-{NAME}'.format(UID = data.index[i], NAME = data[i])
                    )
                row['contents'].append(space)
                row['contents'].append(self.separator)
            game['body']['contents'].append(row)
            game['body']['contents'].append(self.separator)
            game['offsetStart'] = 'sm'
            game['offsetEnd'] = 'sm'
        self.flex_carousel['contents'].append(game)
