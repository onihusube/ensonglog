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
      // ・漢字/ひらがな: 1文字ずつ分割
      //   → 形態素境界差での取りこぼしを防ぐ
      // ・カタカナ連続: 語として保持
      //   → 1文字分割による過剰ヒットを抑える
      // ・ASCII: そのまま保持
      //
      // 例: "妖狐の深夜配信" → "妖 狐 の 深 夜 配 信"
      // 例: "鈴谷皆人" → "鈴 谷 皆 人"
      // 例: "ここでまた逢いましょう" → "こ こ で ま た 逢 い ま し ょ う"
      // 例: "彼方の人魚姫" → "彼 方 の 人 魚 姫"
      // 例: "ボーカル" → "ボーカル"
      // 例: "流星ワールドアクター" → "流 星 ワールドアクター"
      // ---------------------------------------------------------------
      function splitJaPart(text) {
        var out = [];
        var i = 0;
        while (i < text.length) {
          var ch = text[i];
          // カタカナ連続 (長音符ーを含む) は語として保持
          if (/[\u30A1-\u30FA\u30FC]/.test(ch)) {
            var k = i + 1;
            while (k < text.length && /[\u30A1-\u30FA\u30FC]/.test(text[k])) k++;
            out.push(text.slice(i, k));
            i = k;
            continue;
          }
          // 漢字/ひらがなは1文字単位
          if (/[\u3041-\u309F\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]/.test(ch)) {
            out.push(ch);
            i++;
            continue;
          }
          // それ以外はそのまま
          out.push(ch);
          i++;
        }
        return out;
      }

      function isKatakanaWord(text) {
        return /^[\u30A1-\u30FA\u30FC]+$/.test(text);
      }

      function isKanjiWord(text) {
        return /^[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+$/.test(text);
      }

      function mergeShortKatakana(parts) {
        var merged = [];
        var i = 0;
        while (i < parts.length) {
          var token = parts[i];
          if (/^[\u30A1-\u30FA\u30FC]+$/.test(token) && token.length <= 2) {
            var combined = token;
            var j = i + 1;
            while (
              j < parts.length &&
              /^[\u30A1-\u30FA\u30FC]+$/.test(parts[j]) &&
              parts[j].length <= 2
            ) {
              combined += parts[j];
              j++;
            }
            if (j > i + 1) {
              merged.push(combined);
              i = j;
              continue;
            }
          }
          merged.push(token);
          i++;
        }
        return merged;
      }

      if (typeof Intl !== 'undefined' && Intl.Segmenter) {
        var segmenter = new Intl.Segmenter('ja', { granularity: 'word' });
        var segments = Array.from(segmenter.segment(term));
        var parts = [];
        for (var i = 0; i < segments.length; i++) {
          var s = segments[i];
          if (!s.isWordLike) continue;
          var w = s.segment;
          var prev = i > 0 ? segments[i - 1].segment : '';
          var next = i + 1 < segments.length ? segments[i + 1].segment : '';
          var adjacentKatakana = isKatakanaWord(prev) || isKatakanaWord(next);

          // カタカナ隣接の複数漢字語は語として保持 (流星ワールド 等)
          if (isKanjiWord(w) && w.length >= 2 && adjacentKatakana) {
            parts.push(w);
            continue;
          }

          // 日本語を含む場合はスクリプト別に分割
          if (/[\u3041-\u309F\u30A1-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]/.test(w)) {
            var split = splitJaPart(w);
            for (var j = 0; j < split.length; j++) parts.push(split[j]);
          }
          // ASCII等: そのまま
          else {
            parts.push(w);
          }
        }
        return mergeShortKatakana(parts).join(' ');
      }
      // Intl.Segmenter 非対応ブラウザ用フォールバック
      return term
        .replace(/([\u3041-\u309F\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])/g, ' $1 ')
        .replace(/([\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])([\u30A1-\u30FA\u30FC])/g, '$1 $2')
        .replace(/([\u30A1-\u30FA\u30FC])([\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF])/g, '$1 $2')
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
