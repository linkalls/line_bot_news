from flask import Flask, request, abort
from waitress import serve
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

app = Flask(__name__)

# 環境変数からLINE Botの設定を読み込む
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証用のシグネチャを取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # ウェブフックボディを処理
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # ユーザーからのメッセージを取得
    user_message = event.message.text
    # イベントのソースタイプをチェック（個人またはグループ）
    source_type = event.source.type

    # グループLINEの場合
    if source_type == 'group':
        # '@news'という単語で始まるメッセージを処理
        if user_message.startswith('@news'):
            search_word = user_message[len('@news'):].strip()
            search_and_send_yahoo_news(search_word, event)
        # '@google'という単語で始まるメッセージを処理
        elif user_message.startswith('@google'):
            search_word = user_message[len('@google'):].strip()
            search_and_send_google_news(search_word, event)
    # 個人LINEの場合
    elif source_type == 'user':
        # '@google'という単語で始まるメッセージを処理
        if user_message.startswith('@google'):
            search_word = user_message[len('@google'):].strip()
            search_and_send_google_news(search_word, event)
        # '@google'がない場合は Yahoo News を検索
        else:
            search_word = user_message
            search_and_send_yahoo_news(search_word, event)

# Yahoo Newsの検索とメッセージ送信を行う関数
def search_and_send_yahoo_news(search_word, event):
    # 検索語をURLエンコード
    encoded_search_word = urllib.parse.quote(search_word)

    # Yahoo Newsの検索URL
    yahoo_news_search_url = f'https://news.yahoo.co.jp/search?p={encoded_search_word}&ei=utf-8'

    # スクレイピングしてニュースの見出しとURLを取得
    response = requests.get(yahoo_news_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Yahoo NewsのHTML構造に基づいて適切なセレクタを指定
    news_links = soup.find_all('a', class_='newsFeed_item_link')

    # LINEに送信するメッセージを作成
    messages = ["Yahooニュースが見つかりました。\n以下のニュースを送信します。"]
    for link in news_links[:5]:  # 最初の5件のみ処理
        title = link.find('div', class_='newsFeed_item_title').get_text(strip=True)
        url = link['href']
        messages.append(f"{title}\n{url}")

    # LINE Botを通じてメッセージを送信
    send_messages_to_line(messages, event)

# Google Newsの検索とメッセージ送信を行う関数
def search_and_send_google_news(search_word, event):
    # 検索語をURLエンコード
    encoded_search_word = urllib.parse.quote(search_word)

    # Google Newsの検索URL
    google_news_search_url = f'https://news.google.com/search?q={encoded_search_word}&hl=ja&gl=JP&ceid=JP%3Aja'

    # スクレイピングしてニュースの見出しとURLを取得
    response = requests.get(google_news_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提供されたHTML構造に基づいて適切なセレクタを指定
    news_items = soup.select('a.WwrzSb')

    # LINEに送信するメッセージを作成
    messages = ["Googleニュースが見つかりました。\n以下のニュースを送信します。"]
    for item in news_items[:5]:  # 最初の5件のみ処理
        # Google Newsのリンクは相対パスで提供されるため、絶対パスに変換
        url = urllib.parse.urljoin('https://news.google.com/', item['href'])
        # タイトルは親要素から取得
        title = item.text
        messages.append(f"{title}\n{url}")

    # LINE Botを通じてメッセージを送信
    send_messages_to_line(messages, event)
    

# LINEにメッセージを送信する関数
def send_messages_to_line(messages, event):
    # メッセージが5つを超える場合は最初の5つのみを使用
    messages = messages[:5]

    if messages:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                response = line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=message) for message in messages]
                    )
                )
                print(response)  # 応答内容をログに出力
            except Exception as e:
                print(f"Exception when calling LINE Messaging API: {e}")
    else:
        # ニュースが見つからなかった場合の応答メッセージ
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            try:
                response = line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="ニュースが見つかりませんでした。")]
                    )
                )
                print(response)  # 応答内容をログに出力
            except Exception as e:
                print(f"Exception when calling LINE Messaging API: {e}")

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8000)