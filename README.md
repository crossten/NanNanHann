#使用工具


    LINE Official Account : LINE官方帳號API channel_access_token、channel_secret (https://developers.line.biz/en/)


    Imgur API : ImageSendMseeage (https://api.imgur.com/)


    redislabs : redis colud(host、port、password (https://app.redislabs.com/#/login)


    heroku : 部屬平台 (https://id.heroku.com/login) or ngrok (https://ngrok.com/)
    
    
    heroku-selenium : CHROMEDRIVER環境變數設定 (https://aishuafei.com/heroku-selenium/)


#手動更新文件


    member.csv : 會員清單



#使用說明

    pitchure : 新增資料夾名稱 =  關鍵字，隨機回覆資料夾中的圖片


    pet_new : 手動更新最新活動 #幻獸資訊


#調整圖片


    #抽獎介面 
    
    
    image_link : 手動設定關鍵字 & 對應圖片，無設定時套用('https://i.imgur.com/IoPqQPZ.png')


    #排行榜介 
    
    
    Msgtype : 手動設定排行榜名稱


    image : 手動設定排行榜圖片

    
    image_url : 無此會員紀錄時套用('https://cdn0.popo.tw/uc/61/50365/O.jpg')


#代領序號


    #官方網址 : https://couponweb.netmarble.com/coupon/ennt/1324


    流程 : 填入序號 >  填入帳號 > 選伺服器 > 確認角色 > 確認送出


#自動化訊息


    #加好友回報 : 週週抽獎抽不完~ 請輸入遊戲名字~ \n例如 : 白涵公主,加入王國
    
    
    #收回訊息 : 將在下一個人說話時回放
    

#指令

--關鍵字指令


    加入清單 : #每次重啟時重製

    
    個人加入王國 : 遊戲名稱,加入王國

    
    TAG其他人進加入清單 : 加入王國 @LINE 遊戲名稱 @LINE 遊戲名稱.. 
    
    
    查詢 @LINE : 查詢經驗值 & 紀錄


    抽幻獸


    排行榜


    抽幻獸


    xxx.jpg or xxx快樂 : 百度搜圖


    新增關鍵字刪除關鍵字 關鍵字=xxxx=yyyy=zzzz : 從多個關鍵字中抽取一個回應；可以一次新增多個
    
    
    /炎炎代領序號 xxxx xxxx xxxx :可以一次領多個，每個序號執行約10分鐘 (天鵝限定)


    /炎炎新增帳號 xxxx xxxx xxxx :可以一次新增多個 (天鵝限定)


  --抽獎相關指令


    舉辦抽獎,活動道具,數量


    開始抽獎 : 推播訊息給王國成員 [member.csv[PUSH_MSG] == 1]


    查看抽獎 : 查看所有未開獎活動


    #手動設定抽獎


        參加人,抽獎編號,參加抽獎


        參加人,抽獎編號,取消抽獎


    開獎 : (管理者限定)
