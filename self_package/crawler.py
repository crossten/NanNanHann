from fake_useragent import UserAgent
import requests
import re

#百度搜圖
def baidu(keyword):
    url = 'https://image.baidu.com/search/acjson?'
    param = {
        'tn': 'resultjson_com',
        'logid':'11388364236666527695',
        'ipn': 'rj',
        'ct': '201326592',
        'is': '',
        'fp': 'result',
        'fr' : '',
        'word': keyword,
        'queryWord':keyword,
        'cl': '2',
        'lm': '-1',
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': '-1',
        'z': '',
        'ic': '0',
        'hd': '',
        'latest': '',
        'copyright': '',
        's': '',
        'se': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': '0',
        'istype': '2',
        'qc': '',
        'nc': '1',
        'expermode': '',
        'nojc': '',
        'isAsync': '',
        'pn': '1',
        'rn': '30',
        'gsm' : '1',
        '1644984363126':''
        }
    response = requests.get(url= url, 
                            headers= {'User-Agent': UserAgent().random},
                            params= param
                        )
    return response.text

#魔鏡搜詞 #heroku無法使用
def mojim(keyword):
    url = 'https://mojim.com/{keyword}.html?t4'.format(keyword= keyword)
    response = requests.get(url= url, 
                            headers= {
                                'User-Agent': UserAgent().random
                            }
                        )
    if re.search('沒有符合的,請重新輸入', response.text) : return 
    if int(re.findall('共有 (.*?)筆相關歌詞', response.text)[0]) > 30 : return 
    part = re.findall('href="/twy(.*?)x(.*?).htm"', response.text)
    url = 'https://mojim.com/twy{main}x{no}.htm'.format(main= part[0][0], no= part[0][1])
    response = requests.get(url= url, 
                            headers= {'User-Agent': UserAgent().random}
                        )
    text = re.findall("<br />(.*?)<br />", response.text)
    count = 1
    while count < 100:
        for num, i in enumerate(text):
            if keyword in i :
                return re.sub('[A-Za-z0-9\!\%\[\]\,\。:.]', '', text[num +1])
        keyword = keyword[1:]
        if keyword == '' : return
        count += 1
    return 