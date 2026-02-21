#!/usr/bin/env python3
"""inject_pagefind_ja.py

MkDocs でビルドした HTML に対して、Pagefind の日本語検索精度を向上させるための
隠しテキストスパンを注入するスクリプト。

背景
----
Pagefind は HTML を静的にインデックス化する全文検索ライブラリだが、
日本語のように単語境界が空白で区切られない言語では形態素解析なしに
適切な検索トークンを生成できない。本スクリプトは以下の戦略を組み合わせて
検索用テキストを生成し、``data-pagefind-body`` 属性を持つ hidden スパンとして
各 td / th / p / li 要素に追記する。

  1. **Sudachi 形態素解析** (短単位 A モード) による語彙レベルの分割
  2. **CJK バイグラム** (2 文字 N-gram) による文字レベルの網羅
  3. **ASCII 単語抽出** (正規表現) によるアルファベット・数字トークン
  4. 原文そのもの (正規化後) もトークンとして含める

冪等性
------
再実行しても重複注入しないよう、既存の注入スパン (``data-pagefind-ja-injected``
属性で識別) を先に除去してから新しいスパンを追加する。

依存パッケージ
--------------
- beautifulsoup4
- sudachipy
- sudachidict_core (または full / small)
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup
from sudachipy import SplitMode
from sudachipy import dictionary

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------

# サイトディレクトリ内の処理対象 HTML を検索するグロブパターン
HTML_GLOB = "**/*.html"

# 検索テキストを注入する対象 CSS セレクタ。
# MkDocs が生成するテーブル・段落・リスト要素全体をカバーする。
TARGET_SELECTOR = "main td, main th, main p, main li, article td, article th, article p, article li"
BODY_SCOPE_SELECTORS = ("main", "article", "body")

# 注入済みスパンを識別するための属性名。
# 再実行時にこの属性を持つスパンを除去することで冪等性を担保する。
INJECTED_ATTR = "data-pagefind-ja-injected"

# ---------------------------------------------------------------------------
# モジュールレベルの正規表現 (コンパイルコストを1回に抑える)
# ---------------------------------------------------------------------------

# 連続する空白文字 (全角スペース・タブ・改行を含む) を単一の半角スペースに正規化するパターン
_ws_re = re.compile(r"\s+")

# CJK 文字の連続チャンクを抽出するパターン。バイグラム生成の単位として使用する。
#
# 範囲説明:
#   一-龯  : CJK 統合漢字 基本面 (U+4E00–U+9FAF)
#   ぁ-ん  : ひらがな (U+3041–U+3093)
#   ァ-ヺ  : カタカナ (U+30A1–U+30FA)
#             ※ ァ-ン (U+30A1–U+30F3) だけでは ヴ(U+30F4)・ヵ(U+30F5)・ヶ(U+30F6) が抜けるため
#             ヺ(U+30FA) まで拡張している
#   ー     : 長音符 (U+30FC) ※ ァ-ヺ の範囲外なので個別に追加
#   ヽヾ   : カタカナ反復仮名 (U+30FD–U+30FE)
_cjk_chunk_re = re.compile(r"[一-龯ぁ-んァ-ヺーヽヾ]+")

# ASCII 単語を抽出するパターン。
# 先頭が英数字で始まり、以降は英数字・アポストロフィ・ピリオド・アンダースコア・
# プラス・ハイフンを許容する。バージョン番号 (1.2.3)・略語 (don't) 等を1トークンとして扱う。
# 注意: 文字クラス末尾の `-` はリテラルのハイフンとして扱われる (範囲演算子ではない)。
_ascii_word_re = re.compile(r"[A-Za-z0-9][A-Za-z0-9'._+-]*")

# Sudachi が形態素として返す記号類で、検索トークンとして不要なもの。
# 音楽データベース固有の記号 (♪ ★ 〇 等) もここで除外する。
_PUNCT_SKIP: frozenset[str] = frozenset({
    # 括弧類
    "（", "）", "(", ")", "[", "]", "【", "】", "「", "」", "『", "』",
    # 区切り・記号
    "-", "―", "—", "〜", "~", "・", "／", "/", "、", "。",
    ",", ".", ":", "：", ";", "；",
    # 音楽データベースに頻出する装飾記号
    "♪", "★", "☆", "♦", "♥", "♡", "◆", "◇", "●", "○", "■", "□",
    "…", "‥", "※",
})


# ---------------------------------------------------------------------------
# SearchTextBuilder
# ---------------------------------------------------------------------------

class SearchTextBuilder:
    """HTML テキストノードから Pagefind 向け検索テキストを構築するクラス。

    1 インスタンスにつき 1 つの Sudachi 辞書接続を保持する。
    複数ファイルを処理する場合は同じインスタンスを使い回すことでコストを削減できる。
    """

    def __init__(self) -> None:
        # Sudachi 辞書を初期化してトークナイザを生成する。
        # Dictionary() はデフォルト辞書 (sudachidict_core 等) を自動検出する。
        # create() は辞書オブジェクトからトークナイザインスタンスを生成する。
        self.tokenizer = dictionary.Dictionary().create()

    # ------------------------------------------------------------------
    # 内部ユーティリティ
    # ------------------------------------------------------------------

    def normalize_whitespace(self, text: str) -> str:
        """連続する空白文字を単一の半角スペースに正規化し、前後の空白を除去する。

        全角スペース・タブ・改行も ``\\s`` にマッチするため一括処理される。
        """
        return _ws_re.sub(" ", text).strip()

    def sudachi_tokens(self, text: str) -> list[str]:
        """Sudachi 形態素解析 (短単位 A モード) でテキストをトークン分割する。

        SplitMode.A は最短単位分割で、複合語を細かく分解するため
        部分一致検索に適している。

        記号類 (_PUNCT_SKIP) および空文字列は除外する。
        ひらがな・カタカナ単体の助詞・助動詞なども表層形のまま返す (フィルタしない)。

        Args:
            text: 正規化済みの入力テキスト。

        Returns:
            記号を除いた表層形のリスト。
        """
        tokens: list[str] = []
        for morpheme in self.tokenizer.tokenize(text, SplitMode.A):
            surface = morpheme.surface().strip()
            if not surface:
                continue
            # 明示リストに含まれる記号はスキップ
            if surface in _PUNCT_SKIP:
                continue
            # Unicode 一般カテゴリが "Po" (Punctuation, other) または
            # "So" (Symbol, other) の1文字トークンもスキップする。
            # これにより _PUNCT_SKIP に載っていない装飾記号も除外できる。
            if len(surface) == 1 and unicodedata.category(surface) in ("Po", "So", "Ps", "Pe"):
                continue
            tokens.append(surface)
        return tokens

    def cjk_bigrams(self, text: str) -> list[str]:
        """CJK 文字連続チャンクからバイグラム (2 文字 N-gram) を生成する。

        Sudachi の辞書にない固有名詞・アルバム名・アーティスト名でも
        部分文字列検索が機能するよう、文字レベルのフォールバックとして使用する。

        例: "交響曲" → ["交響", "響曲"]
            "ヴォーカル" → ["ヴォ", "オー", "ーカ", "カル"]
            "あ" → [] (1文字チャンクは除外)

        Args:
            text: 正規化済みの入力テキスト。

        Returns:
            重複を含む可能性があるバイグラムのリスト (呼び出し元が重複除去する)。
        """
        grams: list[str] = []
        for chunk in _cjk_chunk_re.findall(text):
            if len(chunk) < 2:
                # 1 文字チャンクはバイグラムを作れないためスキップ
                continue
            if len(chunk) == 2:
                # ちょうど 2 文字ならそのまま 1 つのバイグラム
                grams.append(chunk)
                continue
            # 3 文字以上: スライディングウィンドウで隣接 2 文字を全列挙
            grams.extend(chunk[i : i + 2] for i in range(len(chunk) - 1))
        return grams

    def ascii_words(self, text: str) -> list[str]:
        """ASCII 英数字トークンを抽出する。

        バージョン番号 (``v1.2.3``)・略語 (``don't``)・ファイル名 (``foo.mp3``) 等を
        1 トークンとして扱うため、英数字以外の一部の文字も継続文字として許容する。

        Args:
            text: 正規化済みの入力テキスト。

        Returns:
            マッチした ASCII 単語のリスト。
        """
        return _ascii_word_re.findall(text)

    # ------------------------------------------------------------------
    # 公開 API
    # ------------------------------------------------------------------

    def build(self, text: str) -> str:
        """テキストから検索用トークンを生成し、改行区切りの文字列として返す。

        処理フロー:
          1. 空白正規化 → 空なら即 "" を返す
          2. 原文全体・Sudachi トークン・CJK バイグラム・ASCII 単語 を候補リストに集める
          3. 大文字小文字を無視した重複除去 (casefold) を行いながら順序を維持
          4. 改行 (``\\n``) で結合して返す

        戻り値は ``data-pagefind-body`` を持つ hidden スパンに埋め込まれる。
        Pagefind はこのスパンのテキストも検索インデックスに含める。

        Args:
            text: HTML ノードから抽出した生テキスト。

        Returns:
            改行区切りで連結した検索トークン文字列。テキストが空の場合は ""。
        """
        original = self.normalize_whitespace(text)
        if not original:
            return ""

        # 各戦略からトークン候補を収集する。
        # original を先頭に置くことで、原文フレーズ検索も機能するようにする。
        candidates: list[str] = [original]
        candidates.extend(self.sudachi_tokens(original))
        candidates.extend(self.cjk_bigrams(original))
        candidates.extend(self.ascii_words(original))

        # 重複除去しながら順序を維持する (dict は Python 3.7+ で挿入順を保証)。
        # casefold により大文字・小文字・全角・半角の差異を吸収する。
        seen: set[str] = set()
        merged: list[str] = []
        for token in candidates:
            # sudachi_tokens の出力は surface().strip() 済みだが、
            # ascii_words や cjk_bigrams の出力に念のため正規化をかける。
            # original は既に normalize_whitespace 済みだが、ループ内で統一的に処理する。
            normalized = self.normalize_whitespace(token)
            if not normalized:
                continue
            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            merged.append(normalized)

        return "\n".join(merged)


def ensure_pagefind_body_scope(soup: BeautifulSoup) -> bool:
    for selector in BODY_SCOPE_SELECTORS:
        root = soup.select_one(selector)
        if root is None:
            continue
        if root.has_attr("data-pagefind-body"):
            return False
        root["data-pagefind-body"] = ""
        return True
    return False


# ---------------------------------------------------------------------------
# HTML 処理
# ---------------------------------------------------------------------------

def add_hidden_search_text(html_path: Path, builder: SearchTextBuilder) -> bool:
    """HTML ファイルに日本語検索用の隠しスパンを注入する。

    処理手順:
      1. HTML を読み込んで BeautifulSoup でパース
      2. TARGET_SELECTOR に一致する全ノードを走査
      3. 既存の注入スパン (INJECTED_ATTR 属性を持つもの) を除去 (冪等性確保)
      4. ノードのテキストから検索テキストを生成
      5. 生成できた場合のみ hidden スパンを追記
      6. 変更があった場合 (スパンの追加 or 除去) のみファイルに書き戻す

    注意事項:
      - BeautifulSoup の ``html.parser`` はドキュメント全体を再シリアライズする。
        DOCTYPE 宣言や void 要素 (``<br>``, ``<meta>`` 等) の出力形式が
        元のファイルと微妙に異なる場合がある。
        ``lxml`` パーサーの方が高速かつ忠実だが、追加依存が必要になるため
        標準ライブラリのみで動作する ``html.parser`` を採用している。
      - ``data-pagefind-body`` 属性を hidden スパンに付与することで、
        Pagefind がインデックス対象外と判定した要素内でも検索テキストが
        確実にインデックスされる。

    Args:
        html_path: 処理対象の HTML ファイルパス。
        builder:   検索テキスト生成器。

    Returns:
        ファイルを書き換えた場合は True、変更なしの場合は False。

    Raises:
        OSError: ファイルの読み書きに失敗した場合。
    """
    raw = html_path.read_text(encoding="utf-8")
    # html.parser は標準ライブラリのため追加インストール不要。
    # lxml を使う場合は BeautifulSoup(raw, "lxml") に変更する (高速・高精度だが要 pip install)。
    soup = BeautifulSoup(raw, "html.parser")
    # スパンの追加だけでなく除去が発生した場合もファイル書き戻しが必要なため、
    # 除去フラグと追加フラグを分けて管理する。
    removed_any = False
    added_any = False
    scope_changed = ensure_pagefind_body_scope(soup)

    for node in soup.select(TARGET_SELECTOR):
        # --- 冪等性: 前回の注入スパンを除去 ---
        old_spans = node.select(f"span[{INJECTED_ATTR}]")
        if old_spans:
            for old in old_spans:
                old.decompose()
            removed_any = True

        # --- テキスト抽出と検索テキスト生成 ---
        # stripped_strings は子孫ノードのテキストを空白除去しながら一括取得する。
        # 注入スパン自体も子孫だが、上で decompose() 済みなので含まれない。
        text = " ".join(node.stripped_strings)
        search_text = builder.build(text)
        if not search_text:
            # テキストが空 (画像のみのセルなど) はスパンを追加しない
            continue

        # --- hidden スパンの構築 ---
        hidden = soup.new_tag("span")
        # 再実行時の識別子: 次回スクリプト実行時にこのスパンを検出・除去するために使用
        hidden[INJECTED_ATTR] = ""
        # 見た目は維持しつつ、DOM上は存在させてPagefindの対象にする
        hidden["style"] = (
            "position:absolute;left:-10000px;top:auto;width:1px;height:1px;"
            "overflow:hidden;white-space:pre;"
        )
        hidden["aria-hidden"] = "true"
        hidden.string = search_text
        node.append(hidden)
        added_any = True

    # スパンの追加または除去が発生した場合のみファイルを書き戻す。
    # 変更がなければ不要な書き込みを避けてパフォーマンスを向上させる。
    changed = added_any or removed_any or scope_changed
    if not changed:
        return False

    html_path.write_text(str(soup), encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする。"""
    parser = argparse.ArgumentParser(
        description="Inject hidden Japanese search text for Pagefind indexing"
    )
    parser.add_argument(
        "--site-dir",
        default="site",
        help="Directory that contains built MkDocs HTML files (default: site)",
    )
    parser.add_argument(
        "--glob",
        default=HTML_GLOB,
        help=f"Glob pattern under --site-dir for HTML files (default: {HTML_GLOB})",
    )
    return parser.parse_args()


def main() -> int:
    """エントリポイント。処理したファイル数を標準出力して終了コードを返す。

    Returns:
        0 (正常終了)。異常時は例外を送出する。
    """
    args = parse_args()
    site_dir = Path(args.site_dir)

    if not site_dir.exists():
        raise FileNotFoundError(f"site directory not found: {site_dir}")

    # SearchTextBuilder は Sudachi 辞書への接続を内包するため、
    # 全ファイル共通で 1 インスタンスを再利用してコストを削減する。
    builder = SearchTextBuilder()

    updated = 0
    for html_path in site_dir.glob(args.glob):
        if not html_path.is_file():
            continue
        try:
            if add_hidden_search_text(html_path, builder):
                updated += 1
        except (OSError, UnicodeDecodeError) as exc:
            # 1 ファイルの失敗で全体を止めず、警告として記録して続行する。
            print(f"WARNING: skipped {html_path}: {exc}")

    print(f"Injected Pagefind JA search text into {updated} HTML files")
    return 0


if __name__ == "__main__":
    # raise SystemExit(n) により sys.exit(n) と同等の終了コードをプロセスに返す。
    # この呼び出し形式は pylint / mypy のフォールスルー警告を回避する慣用形。
    raise SystemExit(main())
