
import _staticdata
pet_data = _staticdata.pd_pet()

#抽幻獸介面
class flex_simulator():
    def __init__(self) :
        self.flex_carousel = {'contents':[],'type':'carousel'}
        self.image_url = pet_data['Url'][-1]
        self.theme = '抽幻獸 {name} 活動池'.format(name = pet_data['Name'][-1])
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
