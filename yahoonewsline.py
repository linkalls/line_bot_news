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
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
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
        # '@brave'という単語で始まるメッセージを処理
        elif user_message.startswith('@brave'):
            search_word = user_message[len('@brave'):].strip()
            search_and_send_brave_search(search_word, event)
            # '@bing'という単語で始まるメッセージを処理
        elif user_message.startswith('@bing'):
            search_word = user_message[len('@bing'):].strip()
            search_and_send_bing_search(search_word, event)

    # 個人LINEの場合
    elif source_type == 'user':
        # '@google'という単語で始まるメッセージを処理
        if user_message.startswith('@google'):
            search_word = user_message[len('@google'):].strip()
            search_and_send_google_news(search_word, event)
            # '@brave'という単語で始まるメッセージを処理
        elif user_message.startswith('@brave'):
            search_word = user_message[len('@brave'):].strip()
            search_and_send_brave_search(search_word, event)
            # '@bing'という単語で始まるメッセージを処理
        elif user_message.startswith('@bing'):
            search_word = user_message[len('@bing'):].strip()
            search_and_send_bing_search(search_word, event)

        # '@googleと@braveがない場合は Yahoo News を検索
        else:
            search_word = user_message
            search_and_send_yahoo_news(search_word, event)

# Yahoo Newsの検索とメッセージ送信を行う関数


def search_and_send_yahoo_news(search_word, event):
    # Yahoo Newsの検索URL
    yahoo_news_search_url = f'https://news.yahoo.co.jp/search?p={
        urllib.parse.quote(search_word)}&ei=utf-8'

    # スクレイピングしてニュースの見出しとURLを取得
    response = requests.get(yahoo_news_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_links = soup.find_all('a', class_='newsFeed_item_link')

    # LINEに送信するメッセージを作成
    if news_links:
        messages = ["Yahooニュースが見つかりました。\n以下のニュースを送信します。"]
        for link in news_links[:4]:  # 最初の4件のみ処理
            title = link.find(
                'div', class_='newsFeed_item_title').get_text(strip=True)
            url = link['href']
            messages.append(f"{title}\n{url}")
    else:
        messages = ["Yahooニュースが見つかりませんでした。"]

    # LINE Botを通じてメッセージを送信
    send_messages_to_line(messages, event)


# Google Newsの検索とメッセージ送信を行う関数
def search_and_send_google_news(search_word, event):
    # Google Newsの検索URL
    google_news_search_url = f'https://news.google.com/search?q={
        urllib.parse.quote(search_word)}&hl=ja&gl=JP&ceid=JP:ja'

    # スクレイピングしてニュースの見出しとURLを取得
    response = requests.get(google_news_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = soup.select('a.WwrzSb')

    # LINEに送信するメッセージを作成
    if news_items:
        messages = ["Googleニュースが見つかりました。\n以下のニュースを送信します。"]
        for item in news_items[:4]:  # 最初の4件のみ処理
            url = urllib.parse.urljoin(
                'https://news.google.com/', item['href'])
            title = item.text
            messages.append(f"{url}")
    else:
        messages = ["Googleニュースが見つかりませんでした。"]

    # LINE Botを通じてメッセージを送信
    send_messages_to_line(messages, event)


def search_and_send_brave_search(search_word, event):
    # Brave SearchのURLを作成
    brave_search_url = f'https://search.brave.com/search?q={
        urllib.parse.quote(search_word)}&country=JP&lang=ja'

# リクエストを送信し、レスポンスを取得
    headers = {
        'Accept-Encoding': 'gzip, deflate'
    }
    response = requests.get(brave_search_url, headers=headers)

    # HTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # 結果の一部を抽出
    results = soup.find_all('a', class_='h svelte-1dihpoi')

    # LINEに送信するメッセージを作成
    if results:
        messages = ["Brave Searchの結果を送信します。"]
        for result in results[:4]:  # 最初の4件のみ処理
            title = result.find(
                'div', class_='url svelte-1dihpoi heading-serpresult').text
            link = result['href']
            messages.append(f"{title}\n{link}")
    else:
        messages = ["Brave Searchの結果が見つかりませんでした。"]

    # LINE Botを通じてメッセージを送信
    send_messages_to_line(messages, event)


def search_and_send_bing_search(search_word, event):
    # Bing検索のURLを作成
    bing_search_url = f'https://www.bing.com/search?q={urllib.parse.quote(search_word)}'

    # リクエストを送信し、レスポンスを取得
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(bing_search_url, headers=headers)

    # HTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # 結果の一部を抽出（Bingの検索結果のHTML構造に基づく）
    h2_results = soup.find_all('h2')

    # LINEに送信するメッセージを作成
    if h2_results:
        messages = ["Bing検索の結果を送信します。"]
        for h2 in h2_results[:4]:  # 最初の4件のみ処理
            link_element = h2.find('a')
            if link_element:
                # タイトルとURLを取得
                title = link_element.get_text(strip=True)
                link = link_element['href']
                # 取得したタイトルとURLをコンソールに出力
              #  print(f"Title: {title}, URL: {link}")
                # タイトルとURLの間に改行を挿入してメッセージに追加
                messages.append(f"{title}\n{link}")
    else:
        messages = ["Bing検索の結果が見つかりませんでした。"]

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
                        messages=[TextMessage(text=message)
                                  for message in messages]
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
