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
