# tools

ReviewCompass の補助スクリプトを置く場所。

## self-improvement

`tools/self_improvement/` は `self-improvement` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/self_improvement/schemas/` はツール内部の中間スキーマを置く場所で、永続データ正本スキーマの `learning/workflow/schemas/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/self_improvement/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/self-improvement-check.py`

`tools/self-improvement-check.py` は self-improvement の機械検査 CLI の配置予定名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。
