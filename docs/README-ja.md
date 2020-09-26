GoogleHomeCLI
=============

[概要](#概要) | [使用方法](#使用方法) | [コマンド](#コマンド) | [必要なパッケージ](../requirements.txt) | [賛辞](#賛辞)

## 概要

Google Home(ChromeCast)をコマンドラインで操作できるPythonで動く~~物体~~物質です。  
Python3をメインに開発しています。Python2はサポートしていません。  
このスクリプト(そういえば物質って言っていた気ｇ)は内部コマンドラインを実装しています。

## 使用方法

スクリプトを使用するには`python3`が使用可能である必要があります。

1. リポジトリをクローンします。  
   `git`コマンドがない場合は直接zipをダウンロードし、展開します。  
   HTTPS でクローンする場合:
   ```bash
   $ git clone https://github.com/P2P-Develop/GoogleHomeCLI --depth 1
   ```
   SSH でクローンする場合:
   ```bash
   $ git clone git@github.com:P2P-Develop/GoogleHomeCLI --depth 1
   ```
   [Github CLI](https://github.com/cli/cli) でクローンする場合:
   ```bash
   $ gh repo clone P2P-Develop/GoogleHomeCLI --depth 1
   ```

2. クローンしたリポジトリにアクセスします。  
   ```bash
   $ cd GoogleHomeCLI
   ```

3. 以下のコマンドを実行し、必要なライブラリをインストールします。
   ```bash
   $ python3 -m pip install -r requirements.txt
   ```

4. 以下のコマンドを実行し、スクリプトを起動します。  
   ```bash
   $ python3 src/home.py
   ```

## コマンド

### exit

スクリプトを終了します。  
^Cでも終了することができます。

#### エイリアス

- bye
- stop

### list

スクリプトが認識しているデバイスを表示します。

#### エイリアス

- device
- devices
- ls

### kill

プロセスを抹消します。

### status

接続しているデバイスのステータスを表示します。

#### エイリアス

- show

### reconnect

デバイスに再接続します。

#### エイリアス

- rc

### use \<id|name\>

指定したIDまたは名前のデバイスを選択します。

#### エイリアス

- select

### play \<path|link\>

指定したローカルファイルまたはYoutubeリンクをデバイスから再生します。

#### エイリアス

- sound
- music
- p

## 賛辞

- [Erik Cederstrand](https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python) - Youtube URLからIDを取得する適切な方法。