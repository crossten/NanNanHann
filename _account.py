def line_token():
    return 'line_token'

def line_secret():
    return 'line_secret'

def admin():
    return ['admin']

def imgur():
    return 'imgur'

def redis(dict):
    data = {
        'host' : 'host',
        'port' : 'port',
        'password' : 'password'
    }
    return data[dict]