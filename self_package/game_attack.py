import random

def calculate(redis_model, event, attack_1, attack_2, name_2, play_2) :
    y = '{name}({play})'.format(name= name_2, play= play_2)
    game = random.randint(0, attack_1) - random.randint(0, attack_2)
    exp = random.randint(0, int(attack_2 /10)+1) if game > 0 else -1 * random.randint(0, int(attack_1 /10)+1)
    exp = int(exp * attack_2/attack_1) if exp >0 else exp
    redis_model.update(event, 'Attack', exp= exp)
    if game > 0 :
        return {'exp' : exp, 'text' : '攻擊 {y} 成功 增加經驗值 {exp}\n'.format(y= y, exp= exp)}
    else :
        return  {'exp' : exp, 'text' : '攻擊 {y} 失敗 經驗值 {exp}\n'.format(y= y, exp= exp)}