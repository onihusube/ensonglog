# サイト内検索

こちらの検索ボックスを使用してください。

日本語に対して少し癖のある動作をしますが、より短いワードで検索するとヒットしやすいと思います。また、スペース区切りでのAND検索には対応していません。

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
      // 日本語検索クエリを Pagefind インデックスに合わせて分割する。
      //
      // 【背景】
      // Pagefind Extended は charabia (lindera) でインデックスを構築する。
      // ブラウザ側のクエリはスペースで分割 → 各語のプレフィックス検索 →
      // AND 結合で処理されるため、インデックスの単語境界と一致する
      // 検索語を生成する必要がある。
      //
      // 【戦略】
      // ・カタカナ語: Intl.Segmenter で辞書ベース分割しそのまま保持
      //   → charabia の複合語インデックスと直接マッチ (ボーカル, オリジナル)
      // ・漢字・ひらがな: 1 文字ずつ分割
      //   → CI の inject_pagefind_chars.py が各ページの漢字・ひらがなを
      //     個別にインデックス登録しているため、常にプレフィックスマッチする
      // ・ASCII: そのまま保持
      //
      // 例: "ここでまた逢いましょう" → "こ こ で ま た 逢 い ま し ょ う"
      // 例: "彼方の人魚姫" → "彼 方 の 人 魚 姫"
      // 例: "ボーカル" → "ボーカル" (カタカナ複合語を維持)
      // 例: "オリジナルサウンドトラック" → "オリジナル サウンドトラック"
      // ---------------------------------------------------------------
      if (typeof Intl !== 'undefined' && Intl.Segmenter) {
        var segmenter = new Intl.Segmenter('ja', { granularity: 'word' });
        var segments = Array.from(segmenter.segment(term));
        var parts = [];
        for (var i = 0; i < segments.length; i++) {
          var s = segments[i];
          if (!s.isWordLike) continue;
          var w = s.segment;
          // カタカナ語 (長音符ーを含む): compound のまま保持
          if (/^[\u30A1-\u30FA\u30FC]+$/.test(w)) {
            parts.push(w);
          }
          // 漢字・ひらがな・混合: 1文字ずつ分割
          else if (/[\u3041-\u309F\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]/.test(w)) {
            for (var j = 0; j < w.length; j++) {
              parts.push(w[j]);
            }
          }
          // ASCII等: そのまま
          else {
            parts.push(w);
          }
        }
        return parts.join(' ');
      }
      // Intl.Segmenter 非対応ブラウザ用フォールバック: 全CJK文字を個別分割
      return term
        .replace(/([\u3041-\u309F\u30A1-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])/g, ' $1 ')
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
