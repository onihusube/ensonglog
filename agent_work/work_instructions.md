# 作業指示書

このディレクトリ（`agent_work`）をカレントディレクトリとします。以下のステップに従って作業を行ってください。

## Step1 このディレクトリ内の`music_info.md`から楽曲情報を抽出する

`music_info.md`にはたとえば次のように、楽曲とそれが関連するゲームの情報が任意の形式で記録されています。

```
四畳半の天使 - 温玉ことこと
https://www.youtube.com/watch?v=8LzKyQgcOto

いちごクライシス! 主題歌

Ensemble: スタジオつらら
Producer: ﾖｯｼｬ!!E.J.R
Lyricist, Composer: 江尻拓斗
作編曲: ﾖｯｼｬ!!E.J.R

いちごクライシス!(非18禁) (けむり工房(同人)) (2025-09-04)

配信: https://sndo.ffm.to/dxw4eqa
音源: 主題歌入り音楽CD
```
```
Nintendo Switch用ソフト「カルタグラ」オープニングムービー
https://www.youtube.com/watch?v=6mLcuPYDlLI

カルタグラ(NS) (PROTOTYPE) (2026-02-05)

OP
曲名	恋獄
歌	霜月はるか
作曲	MANYO
作詞	六浦館
コーラス	霜月はるか／真理絵
```
```
【GAL原创op】-“请别落泪，至少我爱过一场”-_哔哩哔哩_bilibili
https://bilibili.com/video/BV1CQZxBdE62/
《第零封情书》主题曲《帧帧》
作曲：金色海洋
作词：杏子haki
演唱/pv：樱野悠

第零封情书

リリース日:
2026年2月14日
開発元:
樱野悠
パブリッシャー:
悠悠球工作室
```
```
【リビドー・アバンちゅ～る】

＼＼　ED楽曲を少しだけ公開！　／／

ED主題歌「Overflowing with Love for you.」
歌唱：柊木環希(
@tamaki_hiiragi
)
作詞：ハラユカ。 from STRIKERS(
@ibukuroko
)
作編曲：西坂恭平 from STRIKERS(
@NishizakaKyohei
)

Guitar/Bass/Piano：西坂恭平 from STRIKERS
Drums：KAMIYAMA(RIGEL)
Drums Recording：SOUND STUDIO 玉響

https://x.com/ensemble_sweet/status/2047586339340656656
```

これらをパースして楽曲情報を抽出してください。

## Step2 楽曲情報を表にまとめる

Step1で抽出した楽曲情報から、次の表を可能な限り埋めてください。分からない所は空欄にしてください。

| 月 | 作品 | ブランド | 曲名 | 種別 | ボーカル | 作詞 | 作曲 | 編曲 | 音源 | その他 | 試聴 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MM<!--/dd--> | | | | | | | | | | | [ページ名](url) |

- キャラクター名義の場合、キャラクター名とCVの両方を記録する
- 作編曲 = 作曲+編曲
- その他の欄には楽曲に関連する追加の情報を記入する
  - 楽器やミキシング担当等の追加の情報はここに入れる
  - 情報を落とすくらいならとりあえずここに入れる
  - その他の欄では、情報の区切り文字に`, `を使用する
- 月のMMには発売月を入れ、日の情報があればコメント（<!--/dd-->）の中のddに入れる
  - 1桁の数字は頭に0を入れて2桁にする
- 試聴の欄にはYoutubeの動画等へのリンクを入れる（分かれば）
- Markdownの表にインデントのために余計なスペースを挿入しない

`../docs/top/explanatory_note.md`に試聴リンクの表示方法があるので参照すること。

例えばStep1のサンプルデータは次のようになります。

```
| 月 | 作品 | ブランド | 曲名 | 種別 | ボーカル | 作詞 | 作曲 | 編曲 | 音源 | その他 | 試聴 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09<!--/04--> | いちごクライシス! | けむり工房 | 四畳半の天使 | 主題歌 | 温玉ことこと | 江尻拓斗 | 江尻拓斗 | ﾖｯｼｬ!!E.J.R | 主題歌入り音楽CD [🎵🔗](https://sndo.ffm.to/dxw4eqa) | Ensemble：スタジオつらら, Producer：ﾖｯｼｬ!!E.J.R |  |
| 02<!--/05--> | カルタグラ (Nintendo Switch) | PROTOTYPE | 恋獄 | OP | 霜月はるか | 六浦館 | MANYO | MANYO |  | コーラス：霜月はるか／真理絵 | [:fontawesome-brands-youtube:](https://www.youtube.com/watch?v=6mLcuPYDlLI) |
| 02<!--/14--> | 第零封情书 | 悠悠球工作室 | 帧帧 | 主題歌 | 樱野悠 | 杏子haki | 金色海洋 |  |  |  | [B站](https://bilibili.com/video/BV1CQZxBdE62/) |
|  | リビドー・アバンちゅ～る |  | Overflowing with Love for you. | ED | 柊木環希 | ハラユカ。 | 西坂恭平 | 西坂恭平 |  | Guitar/Bass/Piano：西坂恭平, Drums：KAMIYAMA | [:fontawesome-brands-twitter:](https://x.com/ensemble_sweet/status/2047586339340656656) |
```

`../docs/2025/楽曲.md`にはさらに出力例があります。

## Step3 表を`temp_work.md`に書き出す

ファイルが空ではない場合は末尾に追記してください。

## Step4 作業結果を確認する

- [ ] `music_info.md`にはデータがあるのに`temp_work.md`に書き出した表には含まれていないような楽曲情報が無いこと
- [ ] 表の各行について、列要素のずれがないこと
    - 特に、末尾の"音源、 その他、 試聴"の部分についてずれていないか注意する
    - **ずれていることが非常に多い**
