import os
import pandas as pd

def path_join(file1, file2):
    return os.path.join(file1, file2)

def pd_pet():
    new = pd.DataFrame(
        data = {
            'Probability': 0.0333,
            'Url': 'https://hedwig-cf.netmarble.com/forum-common/ennt/ennt_t/thumbnail/17ec567cfa314cadb4910ca8be3781bc_1644452443006_d.jpg'
            },
        index= ['★★★★托奇'])
    path = path_join('data', 'pet.csv')
    data = pd.read_csv(path, header= 0, index_col= 'Name')
    data = pd.concat([data, new])
    return data

def pd_member():
    path = path_join('data', 'member.csv')    
    return pd.read_csv(path, header= 0, index_col= 'LINE_UID')

def pd_skill_list():
    path = path_join('data', 'skill.csv')    
    return pd.read_csv(path, header= 0, index_col= 'name')

def pd_star():
    path = path_join('data', 'star.csv')    
    return pd.read_csv(path, header= 0, index_col= None)

def pd_adjective():
    path = path_join('data', 'adjective.csv')    
    return pd.read_csv(path, header= 0, index_col= None)

