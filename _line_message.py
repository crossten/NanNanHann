import _account #帳號管理
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, FlexSendMessage, ImageSendMessage
    )
import json

class menu():
    def __init__(self):
        channel_access_token = _account.line_token()
        self.line_bot_api = LineBotApi(channel_access_token)
    def PushMsg(self, uid, text): 
        try:
            self.line_bot_api.push_message(
                to = uid, 
                messages = TextSendMessage(
                    text = text
                    )
                )
        except:
            None
    def MultMsg(self,uid, text): 
        try:
            self.line_bot_api.multicast(
                to = uid,
                messages = TextSendMessage(
                    text = text)
                )
        except:
            None
    def TextMsg(self,event, text, sender= None): 
        self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text = text, 
                    sender = sender
                )
            )
    def FlexMsg(self,event, text, flex): 
        self.line_bot_api.reply_message(
            event.reply_token,
            messages=FlexSendMessage(
                alt_text= text,
                contents= json.loads(json.dumps(flex, ensure_ascii=False))
                )
            )
    def ImageMsg(self,event, URL):
        self.line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url = URL, 
                preview_image_url = URL
                )
            ) 
