from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import configparser
import os
import json

app = Flask(__name__, static_url_path="/images", static_folder="./images/")

config = configparser.ConfigParser()
config.read("config.ini")
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])


# 導入訊息資料
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return json.loads(file.read())
        except json.decoder.JSONDecodeError:
            print("ERROR: Failed to import {}".format(file_path))
            return []


# 文字訊息
def send_text_message(reply_token, data):
    line_bot_api.reply_message(reply_token, TextSendMessage(text=data['text']))


# 表單動作
def set_template_actions(action_list):
    actions = []
    for action in action_list:
        if 'mode' in action.keys():
            actions.append(
                DatetimePickerTemplateAction(
                    label=action['label'],
                    data=action['data'],
                    mode=action['mode']
                )
            )
        elif 'data' in action.keys():
            actions.append(
                PostbackTemplateAction(
                    label=action['label'],
                    data=action['data']
                )
            )
        elif 'text' in action.keys():
            actions.append(
                MessageTemplateAction(
                    label=action['label'],
                    text=action['text']
                )
            )
        elif 'uri' in action.keys():
            actions.append(
                URITemplateAction(
                    label=action['label'],
                    uri=action['uri']
                )
            )
    return actions


# 滑動欄位
def set_template_columns(column_list):
    columns = []
    for column in column_list:
        thumbnail_image_url = column['thumbnail_image_url']
        columns.append(
            CarouselColumn(
                thumbnail_image_url=thumbnail_image_url,
                title=column['title'],
                text=column['text'],
                actions=set_template_actions(column['actions'])
            )
        )
    return columns


# 滑動表單
def send_carousel_template(reply_token, data):
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=set_template_columns(data['columns'])
        )
    )
    line_bot_api.reply_message(reply_token, carousel_template_message)


# 確認表單
def send_confirm_template(reply_token, data):
    confirm_template_message = TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text=data['text'],
            actions=set_template_actions(data['actions'])
        )
    )
    line_bot_api.reply_message(reply_token, confirm_template_message)


# 按鈕表單
def send_buttons_template(reply_token, data):
    thumbnail_image_url = data['thumbnail_image_url']
    buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url=thumbnail_image_url,
            title=data['title'],
            text=data['text'],
            actions=set_template_actions(data['actions'])
        )
    )
    line_bot_api.reply_message(reply_token, buttons_template_message)


# 圖片訊息動作
def set_imagemap_action(actions_dict):
    actions = []
    for action in actions_dict:
        if 'text' in action.keys():
            actions.append(
                MessageImagemapAction(
                    text=action['text'],
                    area=ImagemapArea(
                        x=action['x'], y=action['y'], width=action['width'], height=action['height']
                    )
                )
            )
        elif 'link_uri' in action.keys():
            actions.append(
                URIImagemapAction(
                    link_uri=action['link_uri'],
                    area=ImagemapArea(
                        x=action['x'], y=action['y'], width=action['width'], height=action['height']
                    )
                )
            )
    return actions


# 圖片訊息
def send_imagemap_message(reply_token, data):
    imagemap_message = ImagemapSendMessage(
        base_url=data['base_url'],
        alt_text='this is an imagemap',
        base_size=BaseSize(height=data['height'], width=data['width']),
        actions=set_imagemap_action(data['actions'])
    )
    line_bot_api.reply_message(reply_token, imagemap_message)


# 主動文字訊息
def push_text_message(user_id, data):
    line_bot_api.push_message(user_id, TextSendMessage(text=data['text']))


@app.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return 'OK'

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("MESSAGE", event)
    print("event.message.text:", event.message.text)
    # user_id = json.loads(str(event.source))['userId']
    # profile = line_bot_api.get_profile(user_id)

    for data in message_list:
        if event.message.text == data['message']:
            if data['type'] == 'text':
                send_text_message(event.reply_token, data)
                return 0
            if data['type'] == 'buttons':
                send_buttons_template(event.reply_token, data)
                return 0
            if data['type'] == 'carousel':
                send_carousel_template(event.reply_token, data)
                return 0
            if data['type'] == 'confirm':
                send_confirm_template(event.reply_token, data)
                return 0
            if data['type'] == 'imagemap':
                send_imagemap_message(event.reply_token, data)
                return 0


# 處理圖片訊息 (參考 line-bot-sdk/linebot/models/messages.py)
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    print("IMAGE_MESSAGE", event)
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('./images/'+event.message.id+'.jpg', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

@handler.add(PostbackEvent)
def handle_postback(event):
    print("POSTBACK", event)
    print("postback message: ", event.postback.data)


@handler.add(FollowEvent)
def handle_follow(event):
    print("FOLLOW", event)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print("UNFOLLOW", event)
    # user_id = json.loads(str(event.source))['userId']


@handler.add(JoinEvent)
def handle_join(event):
    print("JOIN", event)


@handler.add(LeaveEvent)
def handle_leave(event):
    print("LEAVE", event)


@handler.add(BeaconEvent)
def handle_beacon(event):
    print("BEACON", event)


message_list = []
messages_path = 'messages'
message_files = os.listdir(messages_path)
for message_file in message_files:
    message_list += load_data(messages_path + "/" + message_file)

if __name__ == "__main__":
    app.run()
