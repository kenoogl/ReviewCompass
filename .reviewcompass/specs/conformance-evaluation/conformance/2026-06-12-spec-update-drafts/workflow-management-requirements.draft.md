---
apply_status: draft_only
target_document: .reviewcompass/specs/workflow-management/requirements.md
contract_ids: [MLE-C-001, MLE-C-002, MLE-C-003, MLE-C-004]
source_conformance_record: ../2026-06-12-completed-followup-conformance.md
change_policy: minimal_existing_spec_change
---

# 草案：workflow-management requirements.md への反映候補

本草案は正本を直接書き換えない。反映は reopen 手続き（triad-review／review-wave／alignment／approval）で行う。

## 1. Requirement 8 への追記候補（additive、MLE-C-001・C-003）

Requirement 8（機能依存マップの一元保管）の受入基準へ次を追加する。

> N. 本機能は feature 一覧と機能順を `feature-dependency.yaml` の `feature_order` キーから解決する。
> 解決の探索順は実行場所基準で `.reviewcompass/feature-dependency.yaml` →
> `stages/feature-dependency.yaml` → `feature-dependency.yaml` とする。
> 開発リポジトリは既存の `stages/` 配置のまま互換とし、対象アプリでは feature-partitioning の
> 承認結果を `.reviewcompass/feature-dependency.yaml` として実体化する
> （設計記録 2026-06-10 §3.5 由来）。
>
> N+1. 本機能は `feature_order` が `depends_on` と矛盾しない順序（依存される機能が先）であること、
> および循環依存がないことを機械検査する。矛盾時は理由つきで指摘し、`next` は
> `kind: unknown`／DEVIATION（fail-closed）を返す。

受入 1 の「`stages/feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする」は、
開発リポジトリにおける記述として維持し、対象アプリ側の解決規則（上記 N）への参照を 1 文追記する。

## 2. Requirement 8 または T-004 対応要件への追記候補（additive、MLE-C-002）

> N+2. 本機能は feature 一覧が解決できない場合（`feature-dependency.yaml` 不在、または
> `feature_order` 未定義）、エラーではなく `next_action.kind: feature_definition_required`
> （verdict OK）を返し、intent／feature-partitioning の実施と、承認された分割結果の
> `feature-dependency.yaml`（`feature_order` キー、依存の根拠と順序の導出を含む）への記録を案内する。

## 3. 語彙調停（semantic_change、MLE-C-004、案 A 採用済み：MLE-DEC-001、2026-06-12 利用者決定）

利用者決定（案 A）：仕様側を実装語彙 `feature_order` へ寄せる。実装・テスト・テンプレート・
配布物は改名しない。具体的な変更候補は次のとおり。

- Requirement 1 受入 4 と Requirement 8 受入 3 の `feature-dependency.yaml#phase_order` 参照を
  `feature-dependency.yaml#feature_order` へ改める。
- 段集合 YAML の参照フィールド名 `feature_order:` はそのまま維持する（参照先キーと同名で
  一致するため、同名異義は解消される。`feature_order_ref` への改名案は不要となり破棄）。
- Requirement 8 へ由来注記を 1 文追加する：
  > 旧称 `phase_order`（計画書 §5.5 および `stages/feature-partitioning/2026-05-24-proposal.md`
  > の表記）は `feature_order` と同一物である。過去記録（レビュー記録・分割提案書・計画書）は
  > 書き換えず、本注記で読み解く。
- 文言追従の対象は本仕様のほか、workflow-management design・tasks、conformance-evaluation の
  requirements（Requirement 7 受入 5）・design（§13.5 ほか）・tasks（T-010 ほか）、
  運用文書 2 件（REOPEN_PROCEDURE.md・CONFORMANCE_EVALUATION.md）に及ぶ
  （reopen handoff package の MLE-HANDOFF-005〜007 と non_reopen_followups を参照）。

T-002 の未実体化契約（schema、7 機能の features 列挙）の扱いは tasks 草案
（workflow-management-tasks.draft.md §2）と同時に決める（語彙は `feature_order` で確定済み）。
