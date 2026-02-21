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
      // CJK 漢字をスペースで分割して個別文字として検索する。
      //
      // Pagefind Extended はインデックス構築時に charabia (lindera) で
      // 日本語テキストを形態素解析するが、辞書に存在しない固有名詞・
      // 人名・作品名などは **1 文字ずつ** に分割されてしまう。
      //   例: "鈴谷皆人" → index: ["鈴", "谷", "皆", "人"]
      //
      // 一方、ブラウザ側の検索クエリはスペース区切りで WASM に送られ、
      // スペースのない漢字列は 1 語として扱われるためインデックスと
      // 一致せずヒットしない。
      //
      // この processTerm で漢字を個別文字に分割することで、インデックス側の
      // 1 文字分割と一致させる。Pagefind の AND 検索ではマッチしなかった
      // 語は無視されるため、charabia が複合語として認識した漢字
      // (例: "作曲", "橋本") も先頭文字のプレフィックス検索で正しくヒットする。
      //
      // カタカナ・ひらがなは charabia の辞書に登録されている複合語が多い
      // (例: "ボーカル", "サプリメント") ため分割しない。
      // ---------------------------------------------------------------
      return term
        .replace(/([\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])/g, ' $1 ')
        .replace(/\s+/g, ' ')
        .trim();
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
