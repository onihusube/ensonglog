# 検索について

上方にある検索窓（MkDocs組み込み検索）はその動作に少し癖があり、あまり精度が良くありません。より正確な検索には以下の検索ボックスを使用してください。

## サイト内検索（Pagefind）

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

---

## 外部検索（DuckDuckGo）

上記の検索で見つからない場合は、DuckDuckGoのサイト内検索も利用できます（結果は新しいタブで開きます）。

<div style="margin: 1em 0;">
  <form id="duckduckgo-search" onsubmit="searchDuckDuckGo(event)" style="display: flex; gap: 0.5em;">
    <input type="text" id="ddg-query" placeholder="サイト内検索（DuckDuckGo）" style="flex: 1; padding: 0.5em; border-radius: 0.5em; border: 1px solid #ccc;">
    <button type="submit" style="padding: 0.5em 1em; border-radius: 0.5em; border: none; background-color: #4CAF50; color: white; cursor: pointer;">
      検索
    </button>
  </form>
</div>

<script>
function searchDuckDuckGo(event) {
  event.preventDefault();
  const query = document.getElementById('ddg-query').value.trim();
  if (!query) return;
  const site = 'site:onihusube.github.io/ensonglog';
  const url = 'https://duckduckgo.com/?kp=-2&q=' + encodeURIComponent(site + ' ' + query);
  window.open(url, '_blank');
}
</script>
