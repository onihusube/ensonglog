# サイト内検索

上方にある検索窓はその動作に少し癖があり、あまり精度が良くありません。現状googleのインデックスもうまく作成されていないため、より正確な検索にはこの検索ボックスを使用してください。

<link href="/ensonglog/pagefind/pagefind-ui.css" rel="stylesheet">
<script src="/ensonglog/pagefind/pagefind-ui.js"></script>

<div id="pagefind-search" class="pagefind-search-container"></div>

<script>
window.addEventListener('DOMContentLoaded', function() {
  new PagefindUI({
    element: "#pagefind-search",
    showSubResults: true,
    showImages: false,
    processTerm: function(term) {
      // ---------------------------------------------------------------
      // 日本語 CJK 文字をスペースで分割して個別検索語にする。
      //
      // Pagefind Extended はインデックス構築時に charabia (lindera) で
      // 日本語テキストを形態素解析する。漢字の固有名詞は 1 文字ずつ、
      // ひらがな・カタカナは辞書ベースで 2〜6 文字の複合語に分割される。
      //   例: "鈴谷皆人" → ["鈴","谷","皆","人"]
      //   例: "ここでまた逢いましょう" → ["ここ","で","また","逢い","ましょう"]
      //
      // ブラウザ側の検索クエリはスペース区切り → 各語のプレフィックス検索
      // → AND 結合で処理されるため、連続 CJK をスペースで分割する必要がある。
      //
      // 【戦略】
      //  1) 漢字・ひらがな・カタカナを全て 1 文字ずつスペースで分割
      //  2) 小書き仮名 (ょゃゅっ等) と長音符 (ー) は直前の文字に結合
      //     → "ましょう" → "ま しょ う" (しょ=1語), "ボーカル" → "ボー カ ル"
      //     小書き文字は日本語で語頭に立たないため、単独だと
      //     インデックスにマッチせず AND 検索が失敗する。
      //  3) プレフィックス検索により、1 文字でも charabia の複合語にマッチ
      //     例: "こ" → "ここ","こそ"... / "ボー" → "ボーカル"...
      //  4) インデックスにマッチしない語は Pagefind が自動スキップするため、
      //     過剰分割しても AND 検索は壊れない。
      // ---------------------------------------------------------------
      return term
        // 漢字・ひらがな・カタカナを各 1 文字ずつスペースで囲む
        .replace(/([\u3041-\u309F\u30A1-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])/g, ' $1 ')
        // 連続スペースを正規化 (分割で生じた二重スペースを除去)
        .replace(/\s+/g, ' ')
        .trim()
        // 小書き仮名・長音符を直前の文字に結合 (語頭に立たない文字)
        // ぁぃぅぇぉっゃゅょゎゕゖァィゥェォッャュョヮヵヶー
        .replace(/ ([\u3041\u3043\u3045\u3047\u3049\u3063\u3083\u3085\u3087\u308E\u3095\u3096\u30A1\u30A3\u30A5\u30A7\u30A9\u30C3\u30E3\u30E5\u30E7\u30EE\u30F5\u30F6\u30FC])/g, '$1');
    },
    translations: {
      placeholder: "曲名、ボーカル、ブランド名などで検索...",
      zero_results: "「[SEARCH_TERM]」に一致する結果はありませんでした",
      many_results: "[COUNT]件の結果が見つかりました",
      filters: "フィルター",
      clear_search: "クリア",
      load_more: "さらに読み込む"
    }
  });
});
</script>
