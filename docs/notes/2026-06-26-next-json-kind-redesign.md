# `next --json` の kind 再設計（議論記録）

最終更新：2026-06-26（詳細フィールド設計を追記）。

## 動機

`next --json` の本来の役割は「ワークフロー作業の中のどの地点にいるかを返す」こと。
地点が分かれば次のアクションが機械的に決まり、LLM の手作業が減り動作がセキュアになる。

現状の `kind` 値は41種類あり、次の問題がある：

- 「作業状態」「手続きの内部ステップ追跡」「コミット操作の確認」が同じ `kind` に混在
- `maintenance_in_progress` と `blocking_unit_in_progress` は意味が同じだが別の `kind`
- reopen のサブステップ13種類が `kind` に詰め込まれている

## 決定：7種類への整理

| `kind` | 意味 |
|--------|------|
| `completed` | 全作業完了。次の作業を始められる |
| `in_progress` | 通常の作業中（フェーズ終端のコミット待ちも `stage: commit_stop_point` で表現） |
| `blocking_in_progress` | 本線とは別の作業中。完了後は親または次判定へ戻る |
| `verification_pending` | 書き込み後の検証（post-write verification）待ち |
| `reopen_in_progress` | 再開手続き中（サブステップは詳細フィールドで返す） |
| `feature_definition_required` | プロジェクト立ち上げ時の初期設定未完了（特殊ケース・verdict: OK） |
| `unknown` | 想定外のエラー状態（ファイル破損・整合違反など・verdict: DEVIATION） |

`feature_definition_required` と `unknown` の区別：同じ設定ファイル問題でも、前者は「正常な未完了」（修復方法が明確）、後者は「壊れた異常状態」（調査が必要）。

## 新旧対照表

| 旧 `kind` | 新 `kind` |
|-----------|-----------|
| `stage` | `in_progress` |
| `cross_feature_stage` | `in_progress` |
| `upstream_recheck` | `in_progress`（`upstream_phase` フィールドを追加） |
| `commit_stop_point` | `in_progress`（`stage: commit_stop_point`） |
| `maintenance_in_progress` | `blocking_in_progress` |
| `blocking_unit_in_progress` | `blocking_in_progress` |
| `blocking_unit_required` | `blocking_in_progress` |
| `parent_resume_pending` | `blocking_in_progress` |
| `resume_in_progress` | `blocking_in_progress` |
| `post_write_verification` | `verification_pending` |
| `post_write_policy_violation` | `verification_pending` |
| `post_write_human_decision_required` | `verification_pending` |
| `reopen_in_progress` + サブステップ13種類 | `reopen_in_progress`（詳細はフィールドへ） |
| `completed` | `completed`（変わらず） |
| `feature_definition_required` | `feature_definition_required`（変わらず） |
| `unknown` | `unknown`（変わらず） |
| `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` | `next --json` から除外 → `commit --preflight` へ移動（検討中） |
| `phase_approval_complete` / `human_decision_recorded` / `record_human_decision_failed` | 元から `next --json` の kind ではなかった（別サブコマンドの出力・入れ子フィールド） |
| `next_action_template` / `project_state` / `subthread` / `human` / `operation_prompt` / `lightweight_self_check` | 元から `next --json` の kind ではなかった（コード内部のデータ構造） |

## 詳細フィールドの設計（確定）

### 全 `kind` 共通フィールド

| フィールド | 役割 |
|-----------|------|
| `kind` | 現在地のカテゴリ |
| `required_action` | 次にすべき操作の名前（機械が読む） |
| `reason` | 状態の説明（人間が読む） |

### `in_progress`

| フィールド | 説明 |
|-----------|------|
| `feature` | 対象機能名（cross_feature_stage では `"all_features"` 固定） |
| `phase` | 現在のフェーズ |
| `stage` | 現在のステージ（`commit_stop_point` を含む） |
| `upstream_phase` | 上流フェーズ名（upstream_recheck の場合のみ） |

### `blocking_in_progress`

`blocking_phase` サブフィールドで段階を区別する（3値）：

| `blocking_phase` | 意味 | 統合された旧 `kind` |
|-----------------|------|-------------------|
| `required` | blocking 作業の開始が必要 | `blocking_unit_required` |
| `in_progress` | blocking 作業中 | `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` |
| `return_pending` | blocking 完了・親への復帰待ち | `parent_resume_pending` |

`resuming` は廃止。`in_progress`（`unit_id` / `parent_unit_id` が null）として吸収。

| フィールド | `required` | `in_progress` | `return_pending` | 説明 |
|-----------|:---:|:---:|:---:|------|
| `blocking_phase` | ✓ | ✓ | ✓ | 段階の区別 |
| `title` | ✓ | ✓ | — | 作業の名前 |
| `unit_id` | ✓ | ✓ | — | blocking unit の識別子（種別不明時は null） |
| `parent_unit_id` | ✓ | ✓ | ✓ | 親への戻り先 |
| `return_conditions` | ✓ | ✓ | — | 戻る条件（旧 `completion_conditions` と統一） |
| `allowed_scope` | — | ✓ | — | 許可された操作の種類 |
| `allowed_files` | — | ✓ | — | 許可されたファイル |
| `file` | — | ✓ | — | 進行中ファイルのパス（ファイルベース管理の場合） |
| `completed_unit_id` | — | — | ✓ | 完了した unit の識別子 |

廃止するフィールド：`resuming`（`blocking_phase` 値）/ `completion_conditions`（`return_conditions` に統一）/ `process_id`（`blocking_phase` で代替）/ `maintenance_action`（`required_action` で代替）/ `blocked_normal_workflow`（`blocking_phase: in_progress` で暗示）/ `mainline_blocked_by`（`completed` 開始の maintenance に戻り先はないという整理から不要）/ `action_parameters`（他フィールドの重複コピー）/ `active_gate`（maintenance では常に null）

### `verification_pending`

`verification_type` サブフィールドで種類を区別する：

| `verification_type` | 意味 | 次のアクション |
|--------------------|------|--------------|
| `pending` | 検証待ち・未着手 | 検証を実施する |
| `policy_violation` | 禁止変更が混入 | 違反を解消する |
| `human_decision_required` | 未解決の重大所見あり | 人間が判断する |

| フィールド | `pending` | `policy_violation` | `human_decision_required` | 説明 |
|-----------|:---:|:---:|:---:|------|
| `verification_type` | ✓ | ✓ | ✓ | 種類の区別 |
| `target_files` | ✓ | ✓ | ✓ | 検証対象ファイル |
| `manifest` | ✓ | — | ✓ | 封印ファイルのパス |
| `forbidden_files` | — | ✓ | — | ルール違反のファイル |
| `codes` | ✓（任意） | — | — | 検証コード |

### `reopen_in_progress`

廃止するフィールド：`next_drafting_gate`（`active_gate` で代替・手引き改修が必要）/ `feature`（`required_feature_scope` で代替）/ `direct_features` / `indirect_features` / `feature_impact_scope_basis`（手引きに参照なし）

残すフィールド：`file` / `next_step` / `step_number` / `completed_steps` / `pending_gates` / `next_pending_gate` / `active_gate` / `current_blocker` / `required_action` / `blocked_by` / `approval_record_path` / `required_feature_scope` / `phase` / `stage` / `reason` / `repair_reasons`（任意）

## 決定：`commit --preflight` への移動

`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の3種類を `next --json` から除外し、`commit-preflight` サブコマンドの判定に集約する。

根拠：
- `commit-preflight` は既にコミット前の必須確認として手引きに定義されている（手順：commit-preflight → git add → guarded commit）
- これら3種類は「コミット操作の前確認」であり「作業の現在地」ではない
- 利用者の操作手順は変わらない（`commit-preflight` を実行する点は同じ）
- 手引きの `commit_mixing_risk` / `commit_unit_stale` の説明箇所を `commit-preflight` の文脈に移す改修が必要

## 未決定・残作業

- `next_drafting_gate` 廃止に伴う `WORKFLOW_NAVIGATION.md` の手引き改修
- 実装変更の優先順位・着手時期

## 関連

- [2026-06-25-workflow-state-simplification.md](2026-06-25-workflow-state-simplification.md)（前日の状態整理）
- [2026-06-25-work-mode-taxonomy-related-work-index.md](2026-06-25-work-mode-taxonomy-related-work-index.md)（関連作業索引）
- [plan-2026-06-23-maintenance-workflow-protocol.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml)（MWP-0〜MWP-3）
