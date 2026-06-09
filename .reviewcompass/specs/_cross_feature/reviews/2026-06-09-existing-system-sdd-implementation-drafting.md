# 2026-06-09 existing-system SDD implementation drafting

## 対象

追加 intent「既存のシステムに意図を後から追加した場合も、仕様駆動開発の手順に従って下流工程へ進める」に対する implementation 段の起草記録。

## feature 範囲

全 7 feature を確認対象にする。

| feature | 判断 | 理由 |
| --- | --- | --- |
| conformance-evaluation | 実装変更あり | T-016 の既存システム差分抽出モードを実装する |
| workflow-management | 既存実装で受ける | `next` の reopen drafting 判定、`downstream_impact_decisions`、`drafting_completed_gates` は既存実装とテストで受ける |
| foundation | 実装変更なし | 今回は共有語彙または共有 schema 正本の新設ではない |
| runtime | 実装変更なし | LLM 実行基盤の契約変更ではない |
| evaluation | 実装変更なし | 評価メトリクス本体の契約変更ではない |
| analysis | 実装変更なし | T-016 出力を分析成果物へ取り込む段階ではない |
| self-improvement | 実装変更なし | 改善提案・履歴化の契約変更ではない |

## 実装内容

- `tools/conformance_evaluation/post_hoc_intent_diff.py` を追加した
- `tools/conformance_evaluation/schemas/post_hoc_intent_diff.schema.json` を追加した
- `tests/conformance-evaluation/test_conformance_evaluation.py` に T-016 テストを追加した
- `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md` を試行記録として生成した
- `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md` に T-016 実装証跡を追記した

## workflow-management 確認

workflow-management 側は新規コード変更なしで受ける。

- `tools/check-workflow-action.py next --json` は、現在の reopen 状態で `required_action: run_reopen_drafting` を返した
- `tests/tools/test_check_workflow_action.py` の `test_next_reopen_requires_drafting_before_triad_review` が drafting-before-review を検査している
- `tests/tools/test_check_workflow_action.py` には `downstream_impact_decisions` の完了時 coverage 検査がある

対応表：

| XDI-WM-002 要素 | 実装証跡 | テスト証跡 |
| --- | --- | --- |
| CE 候補を即時実行せず reopen 手続きで扱う | `build_in_progress_next_action` / reopen state | `test_next_reads_reopen_in_progress_next_step` |
| review 前に drafting を強制する | `_resolve_reopen_next_gate` | `test_next_reopen_requires_drafting_before_triad_review` |
| feature scope を機械判定する | `reopen_feature_scope_from_data` | `test_next_reopen_uses_feature_impact_decisions_as_review_scope` |
| completed gate の判断記録漏れを遮断する | `validate_reopen_completion_impact_decisions` | `test_commit_blocks_completed_reopen_missing_completed_gate_decision` |
| downstream decision が揃えば完了を許可する | `validate_reopen_completion_impact_decisions` | `test_commit_allows_completed_reopen_with_completed_gate_decisions` |

## indirect feature no-change 確認

| feature | implementation 判断 | 証跡 |
| --- | --- | --- |
| foundation | 共有語彙・共有 schema 正本の新設ではないため変更なし | requirements/design/tasks review-wave で schema 所有は将来共有化時に再判定と記録済み |
| runtime | LLM 実行基盤の provider / prompt / raw 保存契約変更ではないため変更なし | requirements/design/tasks review-wave で直接影響なし |
| evaluation | 評価メトリクスや評価集計の変更ではないため変更なし | tasks review-wave で T-016 出力は analysis/evaluation 取込ではなく WM 伝播入力と判断 |
| analysis | T-016 出力を分析成果物へ取り込む段階ではないため変更なし | tasks review-wave で analysis 消費は今回の reopen chain では発生しないと判断 |
| self-improvement | 改善提案・履歴化の契約変更ではないため変更なし | requirements/design/tasks review-wave で派生層として直接変更不要 |

## 検証

- `.venv/bin/python3 -m pytest tests/conformance-evaluation/test_conformance_evaluation.py -q`：pass
- `.venv/bin/python3 tools/check-workflow-action.py next --json`：implementation drafting を要求

## 次の処理

implementation 正本に相当するコードと実装証跡を起草したため、次は全 7 feature 範囲の implementation triad-review を実施する。
