#轉換遊戲名稱
def switch(data, user_id):
    try:
        name = data['GAME_NAME'][data.index == user_id][0]
    except:
        name = '未加入王國'
    return name
