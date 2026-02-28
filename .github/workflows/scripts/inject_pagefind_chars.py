#!/usr/bin/env python3
"""inject_pagefind_chars.py

MkDocs ビルド後の HTML に対して、各ページに含まれる CJK 文字を
個別にインデックス化するための隠しテキストを注入するスクリプト。

背景
----
Pagefind Extended は charabia (lindera) で日本語を形態素解析するが、
辞書にない固有名詞は「1文字ずつ」に分割され、既知単語は
「彼方」「逢い」「ましょう」などの複合語として分割される。

ブラウザ側の processTerm が検索クエリを 1 文字ずつに分割して
AND 検索するとき、複合語の **内部文字** (例: 「逢い」の「い」) は
そのページにプレフィックスマッチする独立語が存在しないためヒットしない。

本スクリプトは、各ページの全 CJK 文字をスペース区切りの隠し要素として
注入することで、全文字を個別のインデックスエントリとして登録する。
これにより processTerm の 1 文字分割が常にマッチするようになる。

依存パッケージ
--------------
標準ライブラリのみ (html.parser)。外部パッケージ不要。
"""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path


# CJK 文字の正規表現
# ひらがな (U+3041-U+309F), カタカナ (U+30A1-U+30FF),
# 漢字 (CJK統合漢字 + 拡張A + 互換漢字)
# 日本語クエリを 1 文字分割して検索するため、カタカナも注入対象に含める。
_CJK_RE = re.compile(
    r'[\u3041-\u309F\u30A1-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]'
)

# 注入マーカー (冪等性担保用)
_INJECT_START = '<!-- pagefind-chars-start -->'
_INJECT_END = '<!-- pagefind-chars-end -->'
_INJECT_RE = re.compile(
    re.escape(_INJECT_START) + r'.*?' + re.escape(_INJECT_END),
    re.DOTALL,
)


class _MainTextExtractor(HTMLParser):
    """<main> 要素内のテキストを抽出する簡易パーサー。

    <script>, <style> 等のテキストは除外する。
    """

    _SKIP_TAGS = frozenset({'script', 'style', 'template', 'noscript'})

    def __init__(self) -> None:
        super().__init__()
        self._in_main = 0       # <main> のネスト深さ
        self._skip_depth = 0    # スキップ対象タグのネスト深さ
        self.texts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'main':
            self._in_main += 1
        if self._in_main > 0 and tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._in_main > 0 and tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == 'main' and self._in_main > 0:
            self._in_main -= 1

    def handle_data(self, data: str) -> None:
        if self._in_main > 0 and self._skip_depth == 0:
            self.texts.append(data)


def _extract_cjk_chars(html: str) -> set[str]:
    """HTML の <main> 内テキストからユニークな CJK 文字を抽出する。"""
    parser = _MainTextExtractor()
    parser.feed(html)
    text = ''.join(parser.texts)
    return set(_CJK_RE.findall(text))


def _inject_chars(html: str, chars: set[str]) -> str:
    """</main> の直前に、スペース区切りの CJK 文字を隠し div として注入する。

    各文字はスペースで区切られるため、charabia は個別の単語として認識する。
    """
    # 既存の注入を除去 (冪等性)
    html = _INJECT_RE.sub('', html)

    if not chars:
        return html

    # ソートして決定的な出力にする
    chars_text = ' '.join(sorted(chars))
    inject_html = (
        f'{_INJECT_START}'
        f'<div style="display:none;position:absolute;left:-9999px" '
        f'aria-hidden="true">{chars_text}</div>'
        f'{_INJECT_END}'
    )

    # </main> の直前に挿入
    # 最後の </main> を探す (通常1つだが安全のため最後)
    idx = html.rfind('</main>')
    if idx == -1:
        return html  # <main> がない場合はスキップ

    return html[:idx] + inject_html + '\n' + html[idx:]


def process_file(path: Path) -> bool:
    """単一の HTML ファイルを処理する。変更があれば True を返す。"""
    html = path.read_text(encoding='utf-8')

    # <main> がないファイルはスキップ
    if '<main' not in html:
        return False

    chars = _extract_cjk_chars(html)
    if not chars:
        return False

    new_html = _inject_chars(html, chars)
    if new_html == html:
        return False

    path.write_text(new_html, encoding='utf-8')
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Pagefind 用に CJK 個別文字を HTML に注入する'
    )
    parser.add_argument(
        'site_dir',
        type=Path,
        help='MkDocs ビルド出力ディレクトリ (例: site)',
    )
    args = parser.parse_args()

    site_dir: Path = args.site_dir
    if not site_dir.is_dir():
        parser.error(f'{site_dir} はディレクトリではありません')

    modified = 0
    total = 0
    for html_path in sorted(site_dir.rglob('*.html')):
        total += 1
        if process_file(html_path):
            modified += 1

    print(f'Processed {total} HTML files, injected chars into {modified} files')


if __name__ == '__main__':
    main()
