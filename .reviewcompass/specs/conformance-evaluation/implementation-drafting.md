# conformance-evaluation implementation 再確認記録

## 2026-06-08 tasks 再確認への対応

intent の「レビュー収集処理を事前設定の写像にしない」意図に伴い、conformance-evaluation tasks.md の変更を implementation 観点で再確認した。

- T-004 の照合チェックモードは、`tools/conformance_evaluation/check_mode.py`、`tools/conformance_evaluation/machine_verification.py`、`tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-006 の推定モデルは、`tools/conformance_evaluation/estimation_model.py` と `tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-007 の比較モデルは、`tools/conformance_evaluation/comparison_model.py` と `tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-014 の契約所有候補と仕様更新草案は、`tools/conformance_evaluation/contract_ownership.py`、`tests/conformance-evaluation/test_contract_ownership.py`、`tests/conformance-evaluation/test_spec_update_adoption.py` で受けられている

確認結果として、実装済み conformance-evaluation はレビュー収集を事前設定の写像として扱わず、実装コードからの推定、既存上流文書との比較、契約所有候補と仕様更新草案の出力によって、コードと仕様の乖離を構造化して扱う。追加の実装変更は不要。

## 2026-06-09 既存システム後追い intent への対応

追加 intent の目的は、既存の requirements／design／tasks／implementation が存在する状態で intent を追記した場合も、仕様駆動開発として下流工程へ進めることである。

今回の実装では、T-016 の既存システム差分抽出モードを追加した。

- `tools/conformance_evaluation/post_hoc_intent_diff.py` を追加し、追加 intent、feature 分割、既存仕様、実装参照から候補を抽出する
- `tools/conformance_evaluation/schemas/post_hoc_intent_diff.schema.json` を追加し、候補の最低フィールドと分類値域を固定する
- `tests/conformance-evaluation/test_conformance_evaluation.py` に T-016 のテストを追加し、候補抽出、分類値域、tasks 非破壊、評価記録出力を確認する
- `T-013` の traceability smoke を T-016 まで拡張した

ReviewCompass 自身への試行として、`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md` を生成した。

抽出結果は、conformance-evaluation の実装変更候補と workflow-management への下流影響候補である。tasks 本文は直接書き換えず、workflow-management の reopen 手続きへ引き渡す。

### T-016 出力契約

`PostHocIntentDiff` は、後追い intent を実行命令ではなく候補として出力する。候補は次の最低フィールドを持つ。

| field | 意味 |
| --- | --- |
| `feature` | 候補を受ける feature |
| `phase` | 候補が関係する工程。`tasks` も明示的に許可する |
| `classification` | 候補種別 |
| `code_refs` | 判断に使った実装参照 |
| `existing_spec_refs` | 判断に使った既存仕様参照 |
| `reasoning_summary` | なぜその候補になるか |
| `needs_human_decision` | CE 単独では確定できず、人間判断または WM gate 判断が必要か |

classification は `existing_sufficient`、`spec_update_candidate`、`design_conflict_candidate`、`downstream_impact_candidate`、`implementation_change_candidate` の 5 値である。tasks phase の候補は専用分類を増やさず、`phase: tasks` と `classification: downstream_impact_candidate` の組み合わせで表す。これにより、CE は候補抽出に留まり、正式な tasks 反映は workflow-management の reopen gate に委ねる。

`needs_human_decision: true` は「CE の抽出結果だけでは採否を確定しない」ことを表す。`false` の場合でも、`downstream_impact_candidate` は workflow-management の `downstream_impact_decisions` で gate 単位に判断を記録する。CE は reopen YAML へ直接書き戻さない。

### T-016 テスト内訳

今回追加した T-016 の検査は次の 3 件である。

- `test_t016_post_hoc_intent_diff_outputs_candidates_and_record`
- `test_t016_post_hoc_intent_diff_rejects_unknown_classification`
- `test_t016_post_hoc_intent_diff_schema_tracks_classification_contract`

これらは候補抽出、tasks 非破壊、reopen YAML 非破壊、評価記録出力、未知 classification の拒否、schema とコード定数の同期、`phase: tasks` の許可を確認する。

## 検証

- `.venv/bin/python3 -m pytest tests/conformance-evaluation -q`：pass
- `.venv/bin/python3 -m pytest tests/conformance-evaluation/test_conformance_evaluation.py -q`：pass
