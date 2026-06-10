# tools

ReviewCompass の補助スクリプトを置く場所。

## self-improvement

`tools/self_improvement/` は `self-improvement` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/self_improvement/schemas/` はツール内部の中間スキーマを置く場所で、永続データ正本スキーマの `learning/workflow/schemas/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/self_improvement/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/self-improvement-check.py`

`tools/self-improvement-check.py` は self-improvement の機械検査 CLI の配置予定名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。

## conformance-evaluation

`tools/conformance_evaluation/` は `conformance-evaluation` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/conformance_evaluation/schemas/` はツール内部の中間スキーマを置く場所で、6 criteria の永続的な検査仕様を置く `schemas/review-criteria/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/conformance_evaluation/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/conformance-evaluation-check.py`

`tools/conformance-evaluation-check.py` は conformance-evaluation の機械検査 CLI の配置名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。

## deployment independence

`tools/deployment_independence_lint.py` は D-023 の配置非依存性 lint である。Markdown / YAML / JSON 成果物に混入したローカル絶対パスを検出し、外部 URL と明示された一時監査パスは除外する。

実行例:

```bash
.venv/bin/python3 tools/deployment_independence_lint.py --json docs/operations learning/workflow/schemas config
```

## document links

`tools/document_link_lint.py` は Markdown リンクと `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` の `prompt_source_refs` を検査する。ファイル不存在、アンカー不存在に加え、`WORKFLOW_PRECHECK.md` の薄い運用契約を読む判定点が詳細仕様 `WORKFLOW_PRECHECK_DETAILS.md` を併読していない場合を検出する。`tools/check-workflow-action.py commit` は staged 文書に対してこの検査を実行し、所見があれば DEVIATION とする。

実行例:

```bash
.venv/bin/python3 tools/document_link_lint.py --json docs/operations docs/disciplines .reviewcompass/specs/workflow-management/design.md .reviewcompass/specs/workflow-management/tasks.md
```
