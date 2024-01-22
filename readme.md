

# Yahoo News Line Bot

このプロジェクトは、Yahoo News、Google News、Brave Searchからニュースを検索し、LINEボットを通じて結果を送信するPythonスクリプトです。

## 前提条件

このプロジェクトを実行するには、Python 3がインストールされている必要があります。また、LINE Messaging APIのアクセストークンとシークレットキーが必要です。

## インストール方法

### Windows

1. Python 3をインストールします。[Python公式サイト](https://www.python.org/downloads/windows/)からインストーラーをダウンロードして実行します。

2. コマンドプロンプトを開き、以下のコマンドを実行して必要なパッケージをインストールします。

```bash
pip install flask waitress line-bot-sdk requests beautifulsoup4
```

### Ubuntu

1. Python 3をインストールします。ターミナルを開き、以下のコマンドを実行します。

```bash
sudo apt update
sudo apt install python3 python3-pip
```

2. 必要なパッケージをインストールします。

```bash
pip3 install flask waitress line-bot-sdk requests beautifulsoup4
```

## 環境変数の設定

### Windows

1. スタートメニューから「システムのプロパティ」を開きます。

2. 「詳細なシステム設定」をクリックし、「環境変数」ボタンをクリックします。

3. 「新規」ボタンをクリックし、以下の環境変数を追加します。

   - 変数名: `LINE_CHANNEL_ACCESS_TOKEN`
   - 変数値: `<あなたのLINEチャネルアクセストークン>`

   - 変数名: `LINE_CHANNEL_SECRET`
   - 変数値: `<あなたのLINEチャネルシークレット>`

4. OKをクリックしてウィンドウを閉じます。

### Ubuntu

1. ターミナルを開き、以下のコマンドを実行して環境変数を設定します。

```bash
export LINE_CHANNEL_ACCESS_TOKEN=<あなたのLINEチャネルアクセストークン>
export LINE_CHANNEL_SECRET=<あなたのLINEチャネルシークレット>
```

2. これらの変数を永続的にするには、`~/.bashrc`または`~/.profile`に上記の行を追加します。

## サーバーの実行方法

1. `yahoonewsline.py`があるディレクトリに移動します。

2. 以下のコマンドを実行してサーバーを起動します。

   - Windows:

   ```bash
   python yahoonewsline.py
   ```

   - Ubuntu:

   ```bash
   python3 yahoonewsline.py
   ```

サーバーが起動すると、デフォルトでポート8000で待機します。LINEプラットフォームのWebhook URLには、このサーバーの公開URLを設定する必要があります。

## LINEボットの使い方

LINEボットにメッセージを送信することで、以下の機能を使用できます。

- `@news`に続けてキーワードを入力してYahoo Newsを検索します。(個人LINEではこれがデフォルトなので@newsをつける必要はありません。)
- `@google`に続けてキーワードを入力してGoogle Newsを検索します。
- `@brave`に続けてキーワードを入力してBrave Searchを検索します。
- `@eh`に続けてキーワードを入力して地震情報を取得します。 
例えば、`@news スポーツ`とメッセージを送ると、Yahoo Newsで「スポーツ」に関連するニュースを検索し、結果を返信します。

##　注意事項
これらのスクリプトは、利用規約に違反する可能性があります。自己責任で使用してください