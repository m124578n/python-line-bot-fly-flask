from flask import Flask, render_template, request
import json
import config
from linebot import LineBotApi, WebhookHandler
import requests
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)


@app.route('/', methods=['POST'])
@app.route('/<name>')
def hello(name=None):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)  # json 格式化訊息內容
        access_token = config.CHANNEL_ACCESS_TOKEN
        secret = config.CHANNEL_SECRET
        line_bot_api = LineBotApi(access_token)  # 確認 token 是否正確
        handler = WebhookHandler(secret)  # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']  # 加入回傳的 headers
        handler.handle(body, signature)  # 綁定訊息回傳的相關資訊
        token = json_data['events'][0]['replyToken']  # 取得回傳訊息的 Token
        message_type = json_data['events'][0]['message']['type']  # 取得 LINe 收到的訊息類型
        if message_type == 'text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            line_notify_message(msg)
        if message_type == 'image':
            msg_id = json_data['events'][0]['message']['id']
            message_content = line_bot_api.get_message_content(msg_id)
            with open(f'{msg_id}.jpg', 'wb') as fd:  # /workspace/{msg_id}.jpg
                fd.write(message_content.content)
            line_notify_image(msg_id)
    except:
        print(body)  # 如果發生錯誤，印出收到的內容
    return 'OK'


def line_notify_message(msg):
    token = config.TOKEN

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': msg}

    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data)


def line_notify_image(msg_id):
    token = config.TOKEN

    # 要發送的訊息
    message = '這是用 Python 發送的訊息與圖片'

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}

    # 要傳送的圖片檔案
    image = open(f'/workspace/{msg_id}.jpg', 'rb')
    files = {'imageFile': image}

    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, files=files)
