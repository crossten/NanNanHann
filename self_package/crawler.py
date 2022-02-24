from fake_useragent import UserAgent
import requests

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
                            params= param)
    return response.text