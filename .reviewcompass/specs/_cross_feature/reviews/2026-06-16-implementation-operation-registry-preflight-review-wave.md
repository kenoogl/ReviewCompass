---
date: 2026-06-16
gate: stages/implementation.yaml#review-wave
feature: workflow-management
reopen: R-0（operation-registry-preflight-unified-design）
decision: no_impact
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-16-implementation-operation-registry-preflight-review-wave-summary.md
---

# implementation review-wave（機能横断段）：operation registry / preflight

reopen R-0（`docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md`）の第3過程、workflow-management implementation フェーズの review-wave。

本 review-wave は、workflow-management の T-014 実装（operation registry / read-only preflight）が、他 feature の implementation 正本または実装責務を再オープンさせるかを確認する。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-16-implementation-operation-registry-preflight-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

summary には過去 review-run 由来の triage unresolved / human_required item 数も表示される。ただし、本 review-wave の横断処理で使う正本は carry-forward register であり、未消化 carry-forward は 0 件である。したがって、過去 item 集計は今回の implementation 正本変更要求ではない。

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態であり、他 feature へ新たな implementation 正本修正を要求するものではない。

## 持ち越し所見（carry-forward register）

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。未消化の carry-forward は 0 件。本 review-wave で新たに消化すべき横断所見はない。

## 実装内容の横断影響

今回の implementation で追加・修正した主な内容は次である。

- `stages/operation-registry.yaml` に初期 operation contract を追加。
- `tools/check-workflow-action.py operation-preflight --operation-id ... --json` を追加。
- `tools/check_workflow_action/operation_registry.py` で registry schema、operation family、LLM/provider/model field 禁止を検査。
- `tools/check_workflow_action/operation_preflight.py` で read-only preflight response を生成。
- CLI option 検査を手書き表ではなく対象 parser の `--help` 由来に変更し、command drift を検出。
- `family_required_checks` を個別 check として実行し、未知 check は `not_implemented` で fail closed。
- deployment/export の planned output で絶対パスと相対 traversal を拒否。
- JSON response に exit-code contract を含め、CLI 側で未知 verdict を明示的に DEVIATION 化。
- `tests/tools/test_operation_registry_preflight.py` で TDD coverage を追加。

全 feature は impact review scope に含める。ただし、implementation 正本を変更する直接所有者は workflow-management であり、他 feature は consumer / derivative として契約変更要否を確認する対象である。

| feature | 影響 | 根拠 |
| --- | --- | --- |
| workflow-management | 自機能（実装追加） | operation registry / preflight の CLI、registry、検査 helper、テストを所有する。 |
| foundation | 正本変更不要 | LLM/provider/model field 禁止や語彙参照は利用し得るが、foundation の語彙・共有型実装を変更しない。 |
| runtime | 正本変更不要 | session record capture は operation family として登録対象だが、今回の実装は read-only preflight 側の入口であり runtime 実装を変更しない。 |
| evaluation | 正本変更不要 | review artifact / triage の preflight を参照し得るが、evaluation の評価ロジックやメトリクス実装を変更しない。 |
| analysis | 正本変更不要 | operation evidence を将来分析入力にできるが、analysis の入出力処理を変更しない。 |
| self-improvement | 正本変更不要 | 手戻り削減候補の集約先として参照し得るが、改善提案ループの実装責務を変更しない。 |
| conformance-evaluation | 正本変更不要 | preflight contract を照合対象にできるが、conformance-evaluation の抽出・判定実装を変更しない。 |

## 判定

- **decision：no_impact**（他 6 機能への implementation 正本修正なし）。
- **carry-forward：未消化 0 件**。
- reopen scope は `workflow-management` のみ、impact review scope は全 feature とする。
- 他 feature の implementation flag を false に戻さない理由は、他 feature が `indirect_check_only` であり、この review-wave で implementation 正本変更不要と判定したためである。
- 今回の実装は workflow-management の operation 操作前チェック入口であり、他 feature の所有コードへ直接変更を要求しない。
