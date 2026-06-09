---
date: 2026-06-09
classifier: codex_main_session
classification: N-0
trigger_source: intent 追記後の利用者確認により、追加 intent の目的が「既存システムに対して仕様駆動開発を実行し、コード由来の仕様ずれを検出・仕様化・実装まで進める機能追加」であると再確認された。
feature:
  - conformance-evaluation
  - workflow-management
finding: existing-system-sdd-code-derived-drift-capability
---

## 分類根拠

2026-06-08 に `intent/INTENT.md` へ「レビュー収集処理が事前設定の写像にならない」意図を追記した後、いったんは既存 requirements で受けられるため追加実装不要と整理した。

しかし 2026-06-09 の利用者確認により、この intent の本来の目的は、既存の仕様書とコードがある状態で、あとから intent を追加した場合にも仕様駆動開発を上流からやり直し、既存設計との衝突を確認しながら、必要な requirements／design／tasks／implementation へ進める機能を追加することだと確認された。

したがって、前回の「既存仕様で受け止め済み、下流修正不要」という結論は不十分である。本件は intent 由来の再オープンとして `N-0` を継続しつつ、既存システムへの後追い intent 追加を本線作業として扱う。

## 事実

- 既存の `conformance-evaluation` requirements には、実装コードから上流文書を推定し、既存 requirements／design と比較する方向性がある。
- ただし、今回必要なのは抽象的な方向性だけではなく、既存システムに後追いで intent を追加したときに、既存設計との衝突を見ながら下流工程へ進め、実装由来の仕様ずれ候補を証拠付きで取り出す具体的な機能である。
- `stages/feature-partitioning/2026-05-24-proposal.md` は、`conformance-evaluation` を実装コードからの推定、既存上流文書との比較、契約所有候補、仕様更新草案の実装上の所有 feature としている。
- ワークフロー面では、後追い intent 追加を「既存 requirements に似た記述があるから終了」として扱うと、仕様駆動開発の下流処理が抜ける。したがって `workflow-management` 側にも、既存システムでの後追い intent 追加時の処理方針を反映する必要がある。

## feature impact 判定

| feature | 判定 | 判定軸 | 理由 |
|---|---|---|---|
| conformance-evaluation | reopen_existing_feature | implementation_ownership | 実装コードから requirements／design 候補と差分候補を抽出し、既存仕様と照合する機能本体の所有 feature であるため |
| workflow-management | reopen_existing_feature | contract_ownership | 既存システムに intent を後追い追加した場合も、仕様駆動開発として下流工程へ進める手続きの正本を持つため |
| foundation | indirect_check_only | consumer_or_derivative_only | 証拠区分やメタデータ語彙は参照されるが、今回の主変更は語彙正本そのものではないため |
| runtime | indirect_check_only | consumer_or_derivative_only | LLM 実行基盤は利用され得るが、今回の主変更はコード由来仕様差分の抽出・手続き化であるため |
| evaluation | indirect_check_only | consumer_or_derivative_only | 評価結果を参照する可能性はあるが、今回の主変更は評価メトリクス本体ではないため |
| analysis | indirect_check_only | consumer_or_derivative_only | conformance-evaluation の出力を後段で読む側であり、今回の所有 feature ではないため |
| self-improvement | indirect_check_only | consumer_or_derivative_only | ワークフロー改善の入力を読む側であり、今回の所有 feature ではないため |

## 再実施対象

`N-0` として intent 由来の再オープンで扱う。ただし intent 文書そのものは既に追記済みであり、今回の実作業は下流への仕様駆動開発である。

- `conformance-evaluation`：requirements、design、tasks、implementation を再実施対象とする。
- `workflow-management`：requirements、design、tasks、implementation を再実施対象とする。
- 他 feature：現時点では indirect check のみ。下流作業中に共有契約変更が必要と判明した場合は、その時点で feature impact 判定を追加する。

## spec.json 差し戻し

`conformance-evaluation/spec.json` と `workflow-management/spec.json` について、次を差し戻す。

- `workflow_state.requirements.alignment`／`approval`：`true` → `false`
- `workflow_state.design.alignment`／`approval`：`true` → `false`
- `workflow_state.tasks.alignment`／`approval`：`true` → `false`
- `workflow_state.implementation.alignment`／`approval`：`true` → `false`
- `recheck.upstream_change_pending`：`false` → `true`
- `recheck.impacted_downstream_phases`：`[]` → `["requirements", "design", "tasks", "implementation"]`

`reopened` は履歴フラグとして既にすべて `true` のため維持する。

## 停止点

第1過程として、分類・feature impact・差し戻し範囲を記録し、`stages/in-progress/` に進行中状態を発行する。次は、この差し戻し範囲を人が承認する。
