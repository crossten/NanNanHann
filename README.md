#使用工具


    LINE Official Account : LINE官方帳號API channel_access_token、channel_secret (https://developers.line.biz/en/)


    Imgur API : ImageSendMseeage (https://api.imgur.com/)


    redislabs : redis colud(host、port、password (https://app.redislabs.com/#/login)


    heroku : 部屬平台 (https://id.heroku.com/login) or ngrok (https://ngrok.com/)
    
    
    技能表參考 : 神奇寶貝百科招式列表 (https://wiki.52poke.com/zh-hant/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8)


#手動更新文件


    data_member.csv : 會員清單
    
    
    data_pet.csv : 幻獸卡池


    data_adjective.csv : 討伐掉落物形容詞
    
    
    data_star.csv : 討伐掉落物星級
    
    
    data_skill.csv : 討伐技能池


#使用說明

    pitchure : 新增資料夾名稱 =  關鍵字，隨機回覆資料夾中的圖片


    pet_new : 手動更新最新活動 #幻獸資訊


#抽獎介面調整圖片


    jpg : 手動設定關鍵字 & 對應圖片，無設定時套用('https://i.imgur.com/IoPqQPZ.png')


    #排行榜介面圖片


    Msgtype : 手動設定排行榜名稱


    image : 手動設定排行榜圖片


#指令

--關鍵字指令


    遊戲名稱,加入王國
    
    
    加入王國 @xxx 遊戲名稱 (新增至加入清單)


    加入清單 : #每次重啟時重製，管理者維護至data_member.csv


    抽幻獸


    排行榜


    抽幻獸


    .jpg or 快樂 : 百度搜圖 (https://image.baidu.com/)
    
    
    新增關鍵字/刪除關鍵字 xxxx=yyyy=zzzz (關鍵字 = xxxx)
    
    
    攻擊@xxxx @xxxx (發動攻擊!!)
    
    
    討伐@xxxx (發動討伐!!)
    
    
    隨機討伐/野生原野 : 隨機討伐對象、查看目前未結算的討伐對象
    
    
    王國成員 : 查看王國成員清單

    
    /白白代領序號 xxxx
    
    
    /白白新增帳號 遊戲帳號 (天鵝限定)


  --抽獎相關指令


    開始抽獎 : 推播開始抽獎訊息至 data_member.csv[PUSH_ID] == 1 的會員


    舉辦抽獎,活動道具,數量


    查看抽獎 : 查看所有未開獎活動


    手動設定抽獎


    --參加人,抽獎編號,參加抽獎


    --參加人,抽獎編號,取消抽獎


    開獎功能 : #管理者限定
