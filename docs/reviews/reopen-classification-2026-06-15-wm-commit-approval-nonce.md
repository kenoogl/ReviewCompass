---
date: 2026-06-15
classifier: codex_main_session
classification: R-0（workflow-management）
trigger_source: 2026-06-15 セッションで、commit 承認レコードを LLM が生成できる構造への対策として staged 内容に束縛した nonce 承認方式を検討。計画メモ `docs/notes/2026-06-15-commit-approval-nonce-sdd-plan.md` を作成し、利用者指示「進めて」により SDD 正規手順へ進む。
feature: workflow-management
finding: commit-approval-nonce
---

## 分類根拠

commit 承認レコードを staged ファイル集合と staged 内容に束縛した nonce 承認方式へ強化する。現状の commit 直前ゲートは `approved_action=commit`、`approved_by=user`、未消費、staged ファイル被覆、staged 内容と一致する `target_sha256` を要求しているが、承認レコード自体を LLM が生成できる構造では、利用者の明示承認と承認レコードの対応が弱い。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は、段集合 YAML による静的検査、所定手続きの階層構造、不可逆操作の直前ゲート、修復手続きの機械強制を担うことである。nonce 承認方式は既存の「不可逆操作の直前ゲート」、特に commit 直前ゲートの強化であり、新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：対象は commit 直前ゲートの承認強化であり、`workflow-management` の contract ownership に含まれる。別 feature の新設や責務境界の再分割は不要。

## 事実

- 既存要件：`.reviewcompass/specs/workflow-management/requirements.md` Requirement 4 受入基準 5 は、commit 承認レコードに `approved_action=commit`、`approved_by=user`、未消費、staged ファイル被覆、staged 内容と一致する `target_sha256` を要求している。
- 既存設計：`.reviewcompass/specs/workflow-management/design.md` §不可逆操作の直前ゲートモデルは、`git commit` の直前ゲートで commit 承認レコードを別入力として読み、staged blob 由来の sha と照合する。
- 既存タスク：`.reviewcompass/specs/workflow-management/tasks.md` T-006 は、不可逆操作の直前ゲート機構として commit 承認レコードの `target_sha256` 正常系／欠落／不一致テストを要求している。
- 試行結果：2026-06-15 の commit `30554aac` では、staged 状態から nonce を作り、利用者が `コミット承認 551A2025` と返した後に承認レコードを作成する運用で commit を実施した。
- 計画メモ：`docs/notes/2026-06-15-commit-approval-nonce-sdd-plan.md` は、`prepare` / `record` / commit gate / consume / secret redaction の実装方針と、TDD で先に失敗テストを書く方針を記録している。
- LLM 非依存方針：本機能は、操縦する LLM、provider、model に依存しない CLI / file contract として設計する。nonce 生成、challenge 保存、approval record 作成、commit gate 判定、consume は staged ファイル集合・staged blob hash・target digest・nonce・expiry・consumed 状態だけを入力にし、model 名や provider 名を判定条件に含めない。LLM ごとの差異は利用者への説明文やプロンプト表現に限定する。
- 保証範囲：本方式は、利用者が UI 上で nonce を発話したことを暗号的に証明するものではない。保証するのは、承認を staged 内容に束縛し、古い承認・別対象の承認・対象差し替え後の commit を fail-closed で防ぐことである。より強い人間発話保証は、将来課題として UI 署名や agent runtime 由来の承認イベントを検討する。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | Requirement 4 の不可逆操作直前ゲートと T-006 の commit gate を所有する。nonce 承認方式の requirements / design / tasks / implementation を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通語彙・共通スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | session 記録や hook 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 自己改善提案や規律本文に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装照合・逸脱検出に変更なし。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements の Requirement 4 に nonce 承認方式の受入基準を追記する。正本本文を修正するため、requirements は drafting 相当の本文修正後に triad-review / review-wave / alignment / approval を再実施する。
- **design**：challenge / approval record / nonce / target digest / expiry / consume / secret redaction の設計を追記する。
- **tasks**：T-006 に nonce 承認方式のテスト要件と実装作業を追記する。
- **implementation**：TDD で失敗テストを先に作成し、commit 承認 nonce 化を実装する。

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。

## 第1過程の実施記録

2026-06-15 に `tools/check-workflow-action.py reopen-start` を実行し、`stages/in-progress/reopen-procedure-2026-06-15-commit-approval-nonce.yaml` を発行した。あわせて `.reviewcompass/specs/workflow-management/spec.json` は次の差し戻し状態へ更新済みである。

- `workflow_state.requirements.alignment=false`
- `workflow_state.requirements.approval=false`
- `recheck.upstream_change_pending=true`
- `recheck.impacted_downstream_phases=["design","tasks","implementation"]`

この状態で第1過程の停止点に入り、差し戻し内容の利用者承認を待つ。
