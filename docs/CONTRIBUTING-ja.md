# GoogleHomeCLI 貢献ルール

[概要](README-ja.md#概要) | [使用方法](README-ja.md#使用方法) | [コマンド](README-ja.md#コマンド) | [設定](README-ja.md#設定) | 貢献ルール | [セキュリティー](SECURITY-ja.md) | [必要なパッケージ](../requirements.txt) | [賛辞](README-ja.md#賛辞)

<details>
<summary>目次</summary>

- [GoogleHomeCLI 貢献ルール](#googlehomecli-貢献ルール)
  - [概要](#概要)
    - [Issue, Pull Request のマナー](#issue-pull-request-のマナー)
    - [コミットのマナー](#コミットのマナー)
    - [参照](#参照)

</details>

For contributors in English, click [here](CONTRIBUTING.md).

## 概要

このリポジトリでは貢献者として適切に貢献するために、以下のルールを制定しています。

### Issue, Pull Request のマナー

- なるべく重複している Issue を作らないようにしましょう。
  重複している Issue には\[duplicate\]ラベルと Issue 言及がされるので、気付いたらちゃんと閉じてよね！
- Issue で質問する時は**賢い質問**を心掛けましょう。
  質問する際は\[question\]ラベルを付けて頂くと、開発者が質問を見つけやすくなります (もちろん皆さんが回答しても問題ありません)。
- `develop`にダイレクトにコミットできない場合は、Pull Request は**フォーク先のブランチ**からしましょう。
  リポジトリでは**基本**ブランチを`mastre`、`develop`の二つのみにしています。
- Pull Request のベースは必ず`develop`ブランチを選びましょう。
  `master`はリリースされてからそのままの安定したソースコードのみ残しています。
- Pull Request や Issue はなるべくテンプレートを使用するようにしましょう。
  英語のテンプレートしか用意していませんが、日本語でも英語でも、ロシア語でも中国語でもグジャラト語でもなんでも大丈夫です。解読に遅れが生じること以外は問題ございません。

### コミットのマナー

- **docs**以外ではあまり変なコミット名を使わないようにしましょう。
  別にちょっと遊ぶだけなら大丈夫です。開発者までもが遊んでいるので。それが PSAC ｸｵﾘﾃｨ。
- GPG キーが使えるなら遠慮せず使って大丈夫です。
- 確認できる場合はコミット前にスクリプトの構文エラーを修正し、正常に動作するか確認しましょう。
  もし見落としがあった場合はその修正コミットを行ってください。
  > **注意: 修正コミットで大きな変更は加えないようにしましょう。**

### 参照

- [行動規範](CODE-OF-CONDUCT-ja.md)
