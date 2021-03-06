# GoogleHomeCLI

[概要](#概要) | [使用方法](#使用方法) | [コマンド](#コマンド) | [設定](#設定) | [必要なパッケージ](../requirements.txt) | [賛辞](#賛辞)

<details>
<summary>目次</summary>

- [GoogleHomeCLI](#googlehomecli)
  - [概要](#概要)
  - [使用方法](#使用方法)
  - [インタラクティブコメント](#インタラクティブコメント)
  - [コマンド](#コマンド)
    - [`echo`](#echo)
    - [`tts`](#tts)
      - [エイリアス](#エイリアス)
    - [`exit`](#exit)
      - [エイリアス](#エイリアス-1)
    - [`list`](#list)
      - [エイリアス](#エイリアス-2)
    - [`kill`](#kill)
    - [`status`](#status)
      - [エイリアス](#エイリアス-3)
    - [`reconnect`](#reconnect)
      - [エイリアス](#エイリアス-4)
    - [`use <id|name>`](#use-idname)
      - [エイリアス](#エイリアス-5)
    - [`play <path|link>`](#play-pathlink)
      - [エイリアス](#エイリアス-6)
  - [設定](#設定)
  - [賛辞](#賛辞)

</details>

## 概要

Google Home(ChromeCast)をコマンドラインで操作できる Python で動く~~物体~~物質です。
Python3 をメインに開発しています。Python2 はサポートしていません。
このスクリプト(そういえば物質って言っていた気ｇ)は内部コマンドラインを実装しています。
このプロジェクトは、[行動規範](CODE-OF-CONDUCT.md)でリリースされていることに注意してください。 このプロジェクトに参加することにより、あなたはその条件に従うことに同意するものとします。

## 使用方法

スクリプトを使用するには Python3 が使用可能である必要があります。

1. リポジトリをクローンします。
   `git`コマンドがない場合は直接 zip をダウンロードし、展開します。

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
   $ pipenv install
   ```

4. 以下のコマンドを実行し、スクリプトを起動します。
   ```bash
   $ pipenv run start
   ```

## インタラクティブコメント

GoogleHomeCLI はインタラクティブコメントをサポートしています。
`#`、`//`、`"`からなる三つのシンボルを使用できます。
これらのシンボルから始まっていない場合はコメントとして認識されません。

## コマンド

### `echo`

コンソールに文字を表示します。
クォーテーションで囲まれている場合は展開されます。優先順位は`"`、`'`、\`です。
閉じるのを忘れないようにしてください。実行時にエラーが発生します。

### `tts`

Text-To-Speech をデバイスから再生します。
[`echo`](#echo) 同様クォーテーションもサポートしています。

#### エイリアス

- `speak`
- `speech`
- `talk`

### `exit`

スクリプトを終了します。
^C でも終了することができます。

#### エイリアス

- `bye`
- `stop`

### `list`

スクリプトが認識しているデバイスを表示します。

#### エイリアス

- `device`
- `devices`
- `ls`

### `kill`

プロセスを抹消します。

### `status`

接続しているデバイスのステータスを表示します。

#### エイリアス

- `show`

### `reconnect`

デバイスに再接続します。

#### エイリアス

- `rc`

### `use <id|name>`

指定した ID または名前のデバイスを選択します。

#### エイリアス

- `select`

### `play <path|link>`

指定したローカルファイルまたは Youtube リンクを選択したデバイスから再生します。

#### エイリアス

- `sound`
- `music`
- `p`

## 設定

GoogleHomeCLI には設定ファイルが付属しています。
ファイル名は[`config.yml`](../src/config.yml)で、設定ファイルが見つからない場合は**動作しますが**エラーが発生します。
設定は以下の通りです。

|  名前  | デフォルト値 | 説明                                                                 |
| :----: | :----------: | :------------------------------------------------------------------- |
| prompt |     "> "     | コマンドを待機するときに表示される最初のプレフィックスを設定します。 |

## 賛辞

- [Erik Cederstrand](https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python) - Youtube URL から ID を取得する適切な方法。
