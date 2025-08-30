# 検索について

上方にある検索窓はその動作に少し癖があり、あまり精度が良くありません。現状googleのインデックスもうまく作成されていないため、より正確な検索にはこの検索ボックスを使用してください（結果は新しいタブで開きます）。

<div style="margin: 1em 0;">
  <form id="duckduckgo-search" onsubmit="searchDuckDuckGo(event)" style="display: flex; gap: 0.5em;">
    <input type="text" id="ddg-query" placeholder="サイト内検索" style="flex: 1; padding: 0.5em; border-radius: 0.5em; border: 1px solid #ccc;">
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
