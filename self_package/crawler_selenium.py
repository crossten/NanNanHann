import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

#操作代領序號
class chrome_coupon():
    def __init__(self):
        self.nthchid = {'天鵝' : 'li:nth-child(5)'}
        self.result = {'OK':[],  'Error':[]}
    def pull_coupon(self, game_id, coupon_id):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless") #無頭模式
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
            driver.get('https://couponweb.netmarble.com/coupon/ennt/1324') #官方網址
            time.sleep(5)
            driver.find_element(By.ID, "ip_cunpon1").click()
            driver.find_element(By.ID, "ip_cunpon1").send_keys(coupon_id) #填入序號
            driver.find_element(By.ID, "ip_cunpon2").click()
            driver.find_element(By.ID, "ip_cunpon2").send_keys(game_id) #填入帳號
            driver.find_element(By.CSS_SELECTOR, "#serverList .select_icon").click() #選伺服器
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, self.nthchid['天鵝']).click()
            driver.find_element(By.CSS_SELECTOR, "#submitCoupon > p").click()
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, "li:nth-child(2) p").click() #確認角色
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, ".go_main > p").click() #確認送出
            driver.quit()
            self.result['OK'].append(game_id)
        except:
            self.result['Error'].append(game_id)