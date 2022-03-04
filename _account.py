def line_token():
    return 'line_token'

def line_secret():
    return 'line_secret'

def admin():
    return []

def imgur():
    return 'imgur api client ID'

def redis(dict):
    data = {
        'host' : 'redis-xxx.cloud.redislabs.com',
        'port' : 'port',
        'password' : 'password'
    }
    return data[dict]
