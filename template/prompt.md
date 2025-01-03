
# プロンプト

ChatGPT/NotebookLMを使用して各種サイトに記載の情報をこのサイトの形式で抽出するプロンプトのメモ。

## 楽曲情報抽出（ChatGPT）

次のデータから楽曲情報を抽出して

```
（楽曲情報を含むテキストをここに貼る。複数の場合はブロックを分けると良い）
```

次の表を可能な限り埋めてください。分からない所は空欄にしてください。

| 月 | 作品 | ブランド | 曲名 | 種別 | ボーカル | 作詞 | 作曲 | 編曲 | 音源 | その他 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | | | |

- キャラクター名義の場合、キャラクター名とCVの両方を記録してください
- 作編曲 = 作曲+編曲
- その他の欄には楽曲に関連する追加の情報を記入してください
- 月には発売月のみを入れてください（日はいりません）

## 音源リスト抽出（NotebookLM）

このサイトのCDに収録されている楽曲の情報を抽出して次の表を埋めてください。見つからない情報は空欄のままにしてください。

| トラック | 曲名 | ボーカル | 作品 | 種別 | 作詞 | 作曲 | 編曲 | その他 | 年 |
|---|---|---|---|---|---|---|---|---|---|
|||||||||||

- トラック: トラック番号
 - 1桁の数字は頭に0を入れて2桁にしてください
- 種別: OP/EDや挿入歌などの分類
- 年: その楽曲が発表（発売）された年

## 音源ページ作成（NotebookLM）

このページからサウンドトラックの情報について抽出して、次のmarkdwonファイルを完成させてください。見つからない情報は空欄のままにしてください。

```
# 商品名

## 収録曲

| トラック | 曲名 | ボーカル | 種別 | 作詞 | 作曲 | 編曲 | 再生時間 | その他 |
|---|---|---|---|---|---|---|---|---|
||||||||||||

## その他

- 作品/ブランド : Title / Brand
- 購入先
    - [Name](url)
- 視聴 : 
- メディア : (CD|DL|etc...)
- 発売日 : 20yy/MM/dd
```

- トラック: トラック番号
 - 1桁の数字は頭に0を入れて2桁にしてください
- 種別: OP/EDや挿入歌などの分類。わからなければBGMにしてください