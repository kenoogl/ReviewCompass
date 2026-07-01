---
date: 2026-07-01
classifier: codex
classification: R-0（workflow-management）
trigger_source: 利用者指示「reopen開始」。候補1 `plan-2026-07-01-backlog-entry-lane-routing` は、backlog を entry lane と見なした既存判断、plan -> TODO -> checklist の既存導線、TODO を backlog materialization として扱う運用を開き直すもの。
feature: workflow-management
finding: backlog-candidate-routing
---

## 分類根拠

候補1は、backlog / TODO / checklist / reopen / maintenance / autonomous execution / `next --json` / commit preflight の運用前提を見直す。具体的には、backlog を作業レーンまたは実行入口として扱わず「候補置き場」とし、作業レーンを SDD workflow / reopen / maintenance として再整理する。また、TODO を backlog materialization の標準中間物として使わず、maintenance は checklist 直行、それ以外は SDD workflow または reopen に送る方針を検討する。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は、ワークフロー進行、不可逆操作、状態遷移、手続き記録、機械的な事前検査を扱うことである。backlog 候補の扱いと TODO 導線の見直しは、この既存意図内の運用契約変更であり、新しい意図を導入しない。
- feature-partitioning（機能分割）：対象は workflow-management が所有する backlog 候補、操作導線、reopen/maintenance 手続き、`next --json`、commit preflight 周辺の契約であり、既存 feature 境界で受けられる。新 feature は不要。

## 事実

- 対象 plan：`.reviewcompass/backlog/plans/plan-2026-07-01-backlog-entry-lane-routing.yaml`
- 同 plan は、旧 `plan-2026-07-01-backlog-text-format-resilience.yaml` を吸収済みである。
- 同 plan は、backlog を candidate holding area、作業レーンを SDD workflow / reopen / maintenance と定義している。
- 同 plan は、TODO を backlog materialization step として使わない方針を含む。
- 同 plan は、既存 TODO-only 候補を plan record に戻す作業、既実装の TODO 前提関数・運用規律・機械処理の調査修正を含む。
- 利用者確認により、候補1は maintenance 直行ではなく、既存判断の開き直しとして reopen に送る方が自然と判断した。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | backlog 候補、TODO/checklist 導線、reopen/maintenance 手続き、`next --json`、commit preflight、自律実行トリガーの運用契約を所有する。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通基盤の意図・機能境界を変更しない。 |
| runtime | indirect_check_only | consumer_or_derivative_only | session/handoff は手続きとして言及されるが、runtime の契約変更は現時点で不要。design 段または review-wave/alignment で、session/handoff の正本変更が不要であることを確認する。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価・レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | indirect_check_only | consumer_or_derivative_only | 自律実行の証跡・候補提示に関係し得るが、主契約は workflow-management 側で扱う。design 段または review-wave/alignment で、self-improvement 正本変更が不要であることを確認する。 |
| conformance-evaluation | indirect_check_only | consumer_or_derivative_only | 逸脱検出や照合観点で確認対象になり得るが、主契約は workflow-management 側で扱う。design 段または review-wave/alignment で、conformance-evaluation 正本変更が不要であることを確認する。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に backlog 候補置き場、SDD workflow / reopen / maintenance のレーン整理、TODO 非使用、maintenance checklist 直行条件、TODO-only 候補の plan 返却、既実装影響調査の受入基準を追加または更新する。
- **design**：SDD workflow と reopen の分類規則、backlog candidate routing、TODO 廃止後の機械処理、`next --json` / autonomous trigger / commit preflight との接続を設計する。
- **tasks**：既存 TODO 棚卸し、旧 TODO 前提関数の調査、不要関数・変更すべき運用規律・機械処理の修正タスクを定義する。
- **implementation**：TDD に従い、必要なテスト・実装修正・移行処理を行う。

impacted_downstream_phases：design／tasks／implementation。

## 第1過程停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。

## 現在の停止点

利用者承認後、requirements.md に backlog candidate routing の受入基準を追加した。現在は in-progress ファイル `stages/in-progress/reopen-procedure-2026-07-01.yaml` の `next_step` が示すとおり、第2過程「正本修正完了」の停止点コミット待ちである。
