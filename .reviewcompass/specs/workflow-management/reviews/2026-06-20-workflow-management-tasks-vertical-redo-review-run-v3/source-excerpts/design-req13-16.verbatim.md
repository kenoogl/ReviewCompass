## Requirement 13 設計モデル：operation contract 語彙と required_action 対応（Req 13）

Requirement 13 は、`next --json` の選択層が返す唯一 action を、実行層の operation contract へ接続する。Requirement 12 の operation registry / preflight は「操作開始前の read-only 確認」を担い、本節の operation contract は「操作の副作用・承認要否・順序・前提・事後条件」を定義する。

### 1. 共通語彙 schema（Req 13 受入 1〜2）

Phase 1 で追加する schema は次の 5 ファイルである。いずれも JSON Schema Draft 2020-12 を使い、既存実行挙動を変更しない。

| ファイル | 責務 |
|---|---|
| `.reviewcompass/schema/effect_kind.schema.json` | `read`、`write`、`state_mutation`、`external_call` の 4 値を定義する |
| `.reviewcompass/schema/phase_boundary.schema.json` | `none`、`within_phase`、`phase_transition`、`reopen_boundary`、`commit_boundary`、`push_boundary`、`external_boundary` を定義する |
| `.reviewcompass/schema/operation_contract.schema.json` | operation contract の共通構造を定義する |
| `.reviewcompass/schema/workflow_state_snapshot.schema.json` | Requirement 14 の snapshot 構造を定義する |
| `.reviewcompass/schema/language_task_io.schema.json` | Requirement 15 の `language_task` 入出力構造を定義する |

`effect_kind` は副作用の種類だけを表す。承認要否は `approval_required` として独立させ、`read` でも承認が必要な操作、`state_mutation` でも承認不要な判断記録操作を表現できるようにする。

### 2. operation contract schema（Req 13 受入 3〜4、10）

`operation_contract.schema.json` の論理構造は次を最低限とする。

```yaml
schema_version: string
operation_id: string
required_action: string
effect_kind: read | write | state_mutation | external_call
approval_required: boolean
approval_contract_refs: [string]
phase_boundary: none | within_phase | phase_transition | reopen_boundary | commit_boundary | push_boundary | external_boundary
sequence:
  mode: parallel_ok | serial_only
  internal_steps: [object]
actor:
  kind: human | llm | proxy_model | tool | mixed
  source: string
branching:
  has_branches: boolean
  branches: [object]
max_effect_kind: read | write | state_mutation | external_call
preconditions: [object]
postconditions: [object]
state_refs: [string]
registry_refs: [string]
```

`approval_required` は boolean のみを許容する。外部送信承認、human-only gate、または対象 operation 固有の承認 contract への接続は `approval_contract_refs` または branch / internal step の `approval_contract_ref` に分離し、`approval_required` 欄に方針文を入れてはならない。`preconditions` と `postconditions` は `id`、`description`、`check_kind`、`machine_checkable`、`source_ref`、`failure_verdict` を持つ。`machine_checkable=false` の条件を `OK` の根拠にしてはならない。read-only advisory 段階では確認不能を `WARN` 以上、runner-enabled operation では `DEVIATION` として扱う。

### 3. required_action 19語彙の対応表（Req 13 受入 3〜5、7〜8）

19語彙の正本は `.reviewcompass/schema/required_action.schema.json` である。operation contract の物理正本は `stages/operation-contracts.yaml` とし、`stages/operation-registry.yaml` は operation registry / preflight binding の正本として各 `required_action` から `operation_contract` ID と contract digest / schema_version を参照する。

`stages/operation-contracts.yaml` は、最低限 `required_action`、`effect_kind`、`approval_required`、`approval_contract_refs`、`phase_boundary`、`sequence`、実行主体、分岐条件、preconditions / postconditions、side effects、承認要否の集約規則、branch / internal step semantics、max effect、出力・副作用 contract field を持つ。`stages/operation-registry.yaml` は operation id、canonical invocation、workflow binding、required inputs、target identity、sequence mode、worktree / pending / artifact policy、planned outputs の参照・投影・binding hint、contract ID、contract digest、schema_version を持ち、contract field を再定義しない。registry / preflight は contract と state evidence を読み取って確認するだけで、contract 更新、operation 実行、approval consume、workflow state 作成、review-run artifact 作成、artifact mutation、action 独自選択を行わない。

registry / contract の整合検査は次を fail-closed にする。

- registry が参照する contract ID が存在しない
- registry が保持する contract digest または schema_version が contract 正本と一致しない
- registry が `effect_kind`、`approval_required`、`approval_contract_refs`、`phase_boundary`、preconditions / postconditions、side effects、承認要否の集約規則、branch / internal step semantics、max effect、出力・副作用 contract field を複製して二重正本化している
- contract が required_action schema に存在しない語彙を参照している
- required_action schema の語彙が contract に接続されていない

19語彙の operation contract 基線は次とする。各 contract はこの表を最小境界とし、詳細 preconditions / postconditions は `stages/operation-contracts.yaml` でこの基線から弱めずに具体化する。

| required_action | effect_kind | approval_required | phase_boundary | sequence.mode | actor.kind | 分岐 |
|---|---|---:|---|---|---|---|
| `repair_workflow_state` | `state_mutation` | true | `within_phase` | `serial_only` | `tool` | なし |
| `run_post_write_verification` | `external_call` | false | `within_phase` | `serial_only` | `mixed` | なし |
| `wait_for_human_decision` | `read` | false | `none` | `serial_only` | `human` | なし |
| `record_human_decision` | `state_mutation` | false | `within_phase` | `serial_only` | `tool` | なし |
| `run_maintenance` | `state_mutation` | true | `within_phase` | `serial_only` | `mixed` | あり |
| `advance_reopen_after_commit_stop_point` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `commit_stop_point` | `state_mutation` | true | `commit_boundary` | `serial_only` | `human` | なし |
| `draft_reopen_plan_candidates` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `apply_approved_reopen_plan` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `advance_reopen_after_approval_stop_point` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `repair_canonical_documents` | `write` | false | `within_phase` | `serial_only` | `mixed` | なし |
| `run_reopen_drafting` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `run_reopen_pending_gate` | `external_call` | false | `within_phase` | `serial_only` | `mixed` | あり |
| `collect_required_decisions` | `read` | false | `none` | `serial_only` | `tool` | なし |
| `finalize_reopen` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `draft_reopen_classification` | `write` | false | `within_phase` | `serial_only` | `llm` | なし |
| `run_reopen_start` | `state_mutation` | true | `reopen_boundary` | `serial_only` | `tool` | なし |
| `run_workflow_stage` | `state_mutation` | true | `phase_transition` | `serial_only` | `mixed` | あり |
| `completed` | `read` | false | `none` | `parallel_ok` | `tool` | なし |

各 `required_action` の preconditions / postconditions 基線は次とする。`stages/operation-contracts.yaml` はこの基線を弱めず、各 `id` を machine-checkable な check と `source_ref` に展開する。

| required_action | precondition baseline IDs | postcondition baseline IDs |
|---|---|---|
| `repair_workflow_state` | `state_evidence_present`, `repair_plan_bound`, `human_only_repair_authorized` | `state_consistency_restored`, `repair_evidence_saved` |
| `run_post_write_verification` | `changed_targets_detected`, `verification_manifest_bound` | `verification_artifact_saved`, `unresolved_findings_recorded` |
| `wait_for_human_decision` | `pending_human_gate_present`, `target_operation_bound` | `no_state_mutation`, `blocked_state_reported` |
| `record_human_decision` | `pending_gate_present`, `decision_scope_derived`, `binding_digest_matches` | `decision_record_saved`, `target_operation_not_auto_approved` |
| `run_maintenance` | `side_track_frame_present`, `allowed_scope_bound`, `branch_condition_resolved` | `maintenance_evidence_saved`, `return_condition_preserved` |
| `advance_reopen_after_commit_stop_point` | `commit_stop_point_committed`, `worktree_clean`, `reopen_state_bound` | `commit_stop_point_cleared`, `reopen_gate_selector_reenabled` |
| `commit_stop_point` | `staged_content_bound`, `commit_approval_valid`, `post_write_verification_clear` | `commit_created`, `approval_consumed`, `reopen_state_preserved` |
| `draft_reopen_plan_candidates` | `classification_basis_present`, `reopen_scope_bound` | `candidate_plan_saved`, `human_decision_required` |
| `apply_approved_reopen_plan` | `approved_plan_record_present`, `plan_digest_matches`, `human_only_approval_valid` | `reopen_in_progress_record_created`, `active_scope_initialized` |
| `advance_reopen_after_approval_stop_point` | `human_approval_record_valid`, `pending_gate_bound` | `approval_stop_point_cleared`, `next_reopen_step_selected` |
| `repair_canonical_documents` | `target_documents_bound`, `allowed_scope_bound`, `repair_basis_present` | `canonical_documents_updated`, `post_write_verification_required` |
| `run_reopen_drafting` | `active_reopen_scope_present`, `drafting_gate_selected` | `draft_artifact_updated`, `drafting_completed_gate_recorded` |
| `run_reopen_pending_gate` | `active_gate_resolved`, `gate_contract_bound`, `required_evidence_present` | `gate_evidence_saved`, `downstream_impact_recorded_if_needed` |
| `collect_required_decisions` | `open_decision_sources_present`, `decision_records_discoverable` | `required_decision_list_reported`, `no_state_mutation` |
| `finalize_reopen` | `pending_gates_empty`, `active_scope_covered`, `human_only_finalize_approval_valid` | `reopen_record_completed`, `active_scope_closed` |
| `draft_reopen_classification` | `upstream_change_evidence_present`, `affected_feature_scope_known` | `classification_basis_saved`, `reopen_start_decision_required` |
| `run_reopen_start` | `classification_approved`, `target_scope_bound`, `human_only_start_approval_valid` | `reopen_in_progress_record_created`, `spec_flags_updated` |
| `run_workflow_stage` | `stage_contract_bound`, `branch_condition_resolved`, `required_artifacts_available` | `stage_evidence_saved`, `completion_predicate_rechecked` |
| `completed` | `no_pending_required_action`, `workflow_state_consistent` | `completed_report_returned`, `no_state_mutation` |

`run_maintenance`、`run_reopen_pending_gate`、`run_workflow_stage` は branchy operation であり、代表値だけで実行可否を判断してはならない。これらの contract は `effect_kind` に最大副作用、`max_effect_kind` に同じ値またはより強い値を持ち、`branching.branches[]` で各 branch の条件、内部 step、step ごとの `effect_kind`、承認要否、phase boundary を列挙する。

`branching.branches[]` の最低構造は、`branch_id`、`condition`、`internal_steps[]`、`max_effect_kind`、`approval_aggregation`、`human_only_override_applies`、`precondition_ids[]`、`postcondition_ids[]` を持つ。`internal_steps[]` の各要素は、最低限 `step_id`、`effect_kind`、`approval_required`、`approval_contract_ref`、`phase_boundary`、`source_ref` を持つ。`approval_contract_ref` は `none` または `stages/operation-contracts.yaml` 内の承認 contract ID とする。branch 表の「internal steps」は人向け略記であり、operation contract ではこの step 構造へ展開する。

`run_maintenance` の初期 branch は次とする。

| branch condition | internal steps | branch max_effect_kind | approval aggregation | approval contract refs | 補足 |
|---|---|---|---|---|---|
| `maintenance_kind=read_only_diagnostic` | 対象資料読取、diagnostic artifact 生成なし、結果表示 | `read` | `all_false` | `none` | 正本 artifact を作らない |
| `maintenance_kind=working_note_or_decision_basis` | working note / decision basis 作成、対象 digest 記録 | `write` | `any(child.approval_required)` | `none` | 正本変更ではなく判断根拠保存 |
| `maintenance_kind=canonical_document_repair` | 対象正本文書読取、利用者または proxy 判断の照合、正本文書更新、post-write verification | `write` | `any(child.approval_required)` | `none` | source-of-truth 文書修正は対象 contract を別途参照する |
| `maintenance_kind=workflow_state_repair` | state evidence 読取、repair plan 照合、workflow state 更新、整合検査 | `state_mutation` | `true` | `repair_workflow_state` | `repair_workflow_state` contract を参照する |
| `maintenance_kind=external_review_or_audit` | prompt 生成、外部 provider 実行、raw / parsed / metadata 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | provider/model は合否条件ではなく実行証跡 |

`run_maintenance` の approval aggregation は `any(child.approval_required)` とする。ただし、子 step が `human_only` decision scope、commit / push / `spec.json` update、phase / gate completion、reopen finalize、approval_required irreversible operation execution を含む場合、proxy_model は承認主体になれない。

`run_maintenance` の branch 内 step 基線は次とする。

| branch condition | step_id | effect_kind | approval_required | approval_contract_ref | phase_boundary | source_ref |
|---|---|---|---:|---|---|---|
| `maintenance_kind=read_only_diagnostic` | `read_target_materials` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_target_materials` |
| `maintenance_kind=read_only_diagnostic` | `present_diagnostic_result` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-present_diagnostic_result` |
| `maintenance_kind=working_note_or_decision_basis` | `read_decision_basis_sources` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_decision_basis_sources` |
| `maintenance_kind=working_note_or_decision_basis` | `write_working_note` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-write_working_note` |
| `maintenance_kind=canonical_document_repair` | `read_canonical_targets` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_canonical_targets` |
| `maintenance_kind=canonical_document_repair` | `apply_canonical_repair` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-apply_canonical_repair` |
| `maintenance_kind=canonical_document_repair` | `require_post_write_verification` | `external_call` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-require_post_write_verification` |
| `maintenance_kind=workflow_state_repair` | `read_state_evidence` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-read_state_evidence` |
| `maintenance_kind=workflow_state_repair` | `apply_state_repair` | `state_mutation` | true | `repair_workflow_state` | `within_phase` | `design.md#req13-run-maintenance-step-apply_state_repair` |
| `maintenance_kind=workflow_state_repair` | `validate_state_consistency` | `read` | false | `none` | `none` | `design.md#req13-run-maintenance-step-validate_state_consistency` |
| `maintenance_kind=external_review_or_audit` | `build_external_prompt` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-build_external_prompt` |
| `maintenance_kind=external_review_or_audit` | `execute_external_review` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-maintenance-step-execute_external_review` |
| `maintenance_kind=external_review_or_audit` | `save_review_artifacts` | `write` | false | `none` | `within_phase` | `design.md#req13-run-maintenance-step-save_review_artifacts` |

`run_workflow_stage` の初期 branch は次とする。

| branch condition | internal steps | branch max_effect_kind | approval aggregation | approval contract refs | 補足 |
|---|---|---|---|---|---|
| `phase=drafting` | source materials 読取、draft artifact 更新、target digest 記録 | `write` | `all_false` | `none` | phase 内の草案更新 |
| `stage=triad-review` | review prompt / target / manifest 作成、API/CLI review 実行、raw / parsed / triage artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | レビュー実行であり gate 完了ではない |
| `stage=review-wave` | cross-feature source 読取、wave summary / impact decision artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | reopen scope と impact scope を混同しない |
| `stage=alignment` | alignment prompt 実行、alignment artifact 保存 | `external_call` | `any(child.approval_required)` | `external_send_approval` | approval ではない |
| `stage=approval` | approval request 表示、人間判断待機、承認記録保存、phase / gate 遷移前検査 | `state_mutation` | `true` | `human_only_phase_gate_approval` | phase / gate completion は human-only |
| `phase_transition=true` | completed gate / next phase state 更新、snapshot 更新、post-transition validation | `state_mutation` | `true` | `human_only_phase_gate_approval` | `phase_boundary=phase_transition` |

`run_workflow_stage` の approval aggregation は、branch 内に human-only decision scope または approval_required operation が含まれる場合 true とし、外部 API review の実行承認と phase / gate 完了承認を別 contract として分離する。

`run_workflow_stage` の branch 内 step 基線は次とする。

| branch condition | step_id | effect_kind | approval_required | approval_contract_ref | phase_boundary | source_ref |
|---|---|---|---:|---|---|---|
| `phase=drafting` | `read_source_materials` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-read_source_materials` |
| `phase=drafting` | `write_draft_artifact` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-write_draft_artifact` |
| `phase=drafting` | `record_target_digest` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-record_target_digest` |
| `stage=triad-review` | `build_review_prompt_manifest` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-build_review_prompt_manifest` |
| `stage=triad-review` | `execute_review_run` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_review_run` |
| `stage=triad-review` | `save_raw_parsed_triage` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_raw_parsed_triage` |
| `stage=review-wave` | `read_cross_feature_sources` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-read_cross_feature_sources` |
| `stage=review-wave` | `execute_or_collect_wave_review` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_or_collect_wave_review` |
| `stage=review-wave` | `save_impact_decisions` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_impact_decisions` |
| `stage=alignment` | `execute_alignment_check` | `external_call` | true | `external_send_approval` | `external_boundary` | `design.md#req13-run-workflow-stage-step-execute_alignment_check` |
| `stage=alignment` | `save_alignment_artifact` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_alignment_artifact` |
| `stage=approval` | `present_approval_request` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-present_approval_request` |
| `stage=approval` | `record_human_approval_decision` | `state_mutation` | true | `human_only_phase_gate_approval` | `within_phase` | `design.md#req13-run-workflow-stage-step-record_human_approval_decision` |
| `stage=approval` | `validate_phase_gate_transition` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-validate_phase_gate_transition` |
| `phase_transition=true` | `update_completed_gate_state` | `state_mutation` | true | `human_only_phase_gate_approval` | `phase_transition` | `design.md#req13-run-workflow-stage-step-update_completed_gate_state` |
| `phase_transition=true` | `save_snapshot` | `write` | false | `none` | `within_phase` | `design.md#req13-run-workflow-stage-step-save_snapshot` |
| `phase_transition=true` | `validate_post_transition_state` | `read` | false | `none` | `none` | `design.md#req13-run-workflow-stage-step-validate_post_transition_state` |

単純操作で承認を必須とする action は次を基線とする。

- `commit_stop_point`
- `apply_approved_reopen_plan`
- `run_reopen_start`
- `advance_reopen_after_commit_stop_point`
- `advance_reopen_after_approval_stop_point`
- `finalize_reopen`
- `repair_workflow_state`

`run_reopen_pending_gate` は active gate で分岐する。

| active gate | effect_kind | approval_required | 補足 |
|---|---|---|---|
| `triad-review` | `external_call` | false | review-run と proxy decision の承認境界は別 contract で扱う |
| `review-wave` | `external_call` | false | 横断 impact check の証跡生成を含む |
| `alignment` | `write` | false | LLM が整合確認 artifact を生成する |
| `approval` | `state_mutation` | true | 承認要求を構造化し、人間判断待ちへ渡す。proxy_model は human-only approval を代行しない |

`run_reopen_drafting` は drafting 正本の更新であり、`run_reopen_pending_gate` とは分離する。`run_maintenance` と `run_workflow_stage` は複合操作として扱い、内部 operation または stage 種別により `effect_kind` と `approval_required` が変わる。代表値だけで確定せず、`branching.branches[]` に分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持たせる。

### 4. 複合操作の schema 表現（Req 13 受入 8〜9）

複合 operation は `effect_kind` を単一 enum のまま保持し、`max_effect_kind` に最大副作用を置く。複数副作用の詳細は `sequence.internal_steps[]` と `branching.branches[]` に展開する。これにより、既存の単一値 schema を保ちながら、`run_maintenance` や `run_workflow_stage` の内部差異を LLM の推測に戻さない。

`record_human_decision` は承認対象 operation ではなく、判断記録 operation とする。`effect_kind=state_mutation`、`approval_required=false`、`phase_boundary=within_phase` とし、記録対象は `target_operation_id`、`target_required_action`、`target_artifact_digest` または `staged_file_set_digest` で束縛する。`record_human_decision` の完了だけでは、対象 operation の `approval_required=true` を満たさない。承認として対象 operation を進められるかどうかは、Requirement 14 §1 の approval gate record にある `decision_scope`、`binding_kind`、digest 束縛、および対象 operation contract から導出した human-only / proxy-allowed 判定で決まる。

### 5. registry / preflight の read-only 境界（Req 13 受入 11〜12）

operation preflight は `stages/operation-registry.yaml` を入口にし、参照先 `stages/operation-contracts.yaml` の preconditions / postconditions / side effects / approval_required を読み取る。preflight の責務は「開始前に確認すること」であり、contract 正本、workflow state、approval record、side track stack、snapshot、review-run artifact を作成・更新しない。

read-only diagnostic 表示では、contract 参照欠落、digest drift、schema_version mismatch、確認不能 precondition、正本 field 重複、未接続 `required_action` mapping を `WARN` 以上にしてよい。ただし、その状態を operation が安全に束縛済みまたは実行可能である根拠にしてはならない。runner-enabled operation では同じ状態を `DEVIATION` とし、operation 実行を開始しない。

## Requirement 14 設計モデル：承認ゲート、側道スタック、状態スナップショット（Req 14）

Requirement 14 は、判断記録、側道作業、現在状態の可視化を、会話文脈ではなく機械可読状態として扱う。

### 1. 承認ゲート record（Req 14 受入 1〜3）

承認ゲートは `wait_for_human_decision` と `record_human_decision` のペアとして扱う。判断 record の最低構造は次とする。

```yaml
schema_version: string
decision_id: string
decision: approved | rejected | deferred | changes_requested
decision_scope: human_only | proxy_allowed | advisory_only
target_operation_id: string
target_required_action: string
target_artifact: string | null
target_artifact_digest: string | null  # binding_kind=artifact_digest / both では必須
staged_file_set_digest: string | null  # binding_kind=staged_file_set_digest / both では必須
binding_kind: artifact_digest | staged_file_set_digest | both | none
decided_by: user | proxy_model
decided_at: string
source_ref: string
source_digest: string
rationale: string
next_action_expectation: proceed | stay_blocked | redraft | repair
consumed: boolean
```

`approved` 以外の判断は対象不可逆操作へ進めない。`rejected` は停止維持、`deferred` は待機、`changes_requested` は再起草または repair へ分岐する。分岐を選ぶ責務は `next --json` に置き、LLM が会話上の雰囲気で選ばない。

human-only decision と proxy-allowed decision は approval gate record の `decision_scope` で区別する。`decision_scope` は最低限 `human_only`、`proxy_allowed`、`advisory_only` の 3 値とする。`decision_scope` は record 作成者が任意に選ぶ値ではなく、`target_required_action` から解決した operation contract の `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、および human-only override set から機械的に導出する。record 内の `decision_scope` が contract から導出した値と一致しない場合は形式不正として fail-closed にする。

`binding_kind` も operation contract から導出する。正本文書・review artifact・approval artifact・proxy decision artifact を対象にする operation は `target_artifact_digest` を必須にする。commit / staged content / apply-fixes / state mutation のうち git index に束縛される operation は `staged_file_set_digest` を必須にする。両方を参照する operation は `binding_kind=both` とし、両 digest を必須にする。`binding_kind=none` は `wait_for_human_decision`、`collect_required_decisions`、`completed` のような read-only / wait-only operation に限る。`approval_required=true`、human-only override set、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize の対象 record では `binding_kind=none` を禁止する。必要な digest が欠落、null、または現在の対象 digest と不一致の場合、`record_human_decision` は成功せず、`next --json` は対象 operation へ進めない。

binding 条件は次のとおりとする。record schema はこの表を条件付き必須として実装し、両 digest を独立 optional として扱ってはならない。

| binding_kind | 必須 digest | null を許す digest | 対象 operation |
|---|---|---|---|
| `artifact_digest` | `target_artifact_digest` | `staged_file_set_digest` | 正本文書、review artifact、approval artifact、proxy decision artifact を対象にする判断 |
| `staged_file_set_digest` | `staged_file_set_digest` | `target_artifact_digest` | commit / push / staged content / git index に束縛される判断 |
| `both` | `target_artifact_digest` と `staged_file_set_digest` | なし | artifact と staged 内容の両方を対象にする判断 |
| `none` | なし | `target_artifact_digest`、`staged_file_set_digest` | read-only / wait-only operation のみ。承認済み不可逆操作には使えない |

`decided_by`、`decided_at`、`source_ref`、`source_digest` は常に必須である。`source_digest` は判断根拠として提示・保存した source text または source artifact の SHA-256 hex とし、source が保存不能な場合でも omission reason を持つ source evidence artifact の digest を記録する。actor、timestamp、source、target operation、required_action、binding digest のいずれかが欠落する record は、承認 record ではなく形式不正として扱う。

`decided_by=proxy_model` かつ `decision_scope=human_only` の record は承認として扱わず、`next --json` は対象不可逆操作へ進めない。`decided_by=proxy_model` かつ `decision_scope=proxy_allowed` の record は、finding triage や修正方針判断の証跡としてのみ使える。`decision_scope=advisory_only` は補助的判断であり、対象 operation の `approval_required=true` を満たさない。

human-only decision の初期集合は次とする。

- commit
- push
- `spec.json` 更新
- phase approval
- reopen finalize
- `approval_required=true` の不可逆 operation 実行許可

human-only override set は operation contract より強い。ある operation が `approval_required=false` と書かれていても、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize、または approval-required irreversible operation execution に該当する branch では `decision_scope=human_only` とする。

proxy_model は finding triage、同根 cluster の採否案、補助的な整合判断を代行できる。ただし proxy_model decision は human-only decision の承認主体を置換しない。

### 2. side track stack（Req 14 受入 4〜7）

side track は stack frame として `stages/in-progress/side-track-stack.yaml` または後継 runtime state に保持する。初期実装では既存の `process_id: maintenance` 進行中ファイルを互換入力として扱い、Phase 3 以降で stack schema へ寄せる。

frame の最低構造は次とする。

```yaml
frame_id: string
kind: maintenance | follow_up | blocker_repair | dependent_issue
parent_frame_id: string | null
pushed_by: user | llm | tool
title: string
spawned_from:
  required_action: string
  active_gate: string | null
  state_file: string | null
allowed_scope: string
allowed_files: [string]
completion_conditions: [string]
return_to:
  required_action: string
  active_gate: string | null
  state_refs: [string]
staged_file_set: [string]
staged_file_digest: string
pushed_at: string
max_depth: integer
```

push 時、pop 直前、commit / push 直前に `staged_file_set` と `staged_file_digest` を採取して照合する。top frame 以外の pop、`allowed_files` 外の staged 変更、親子 frame の未許可 overlap、push 時点からの予期しない digest 変化、pop 時の digest / set 不一致は、Phase 3 では `WARN` 以上、Phase 5 では `DEVIATION` または `repair_workflow_state` とする。`max_depth` は既定 2 で、Phase 3 は警告、Phase 5 はブロックする。

side track stack の read-only 操作は `current` / `inspect` とし、stack state を書き換えない。mutating 操作は `push` / `pop` / `repair` とし、operation contract の preconditions / postconditions を通す。`push` は新 frame を top に追加し、`pop` は top frame だけを閉じる。pop 後に `return_to` が解決できない、または staged file set が本線復帰条件を満たさない場合、`next --json` は通常作業に戻さず `repair_workflow_state` または同等の停止状態を返す。

### 3. workflow-state snapshot（Req 14 受入 8〜10）

`.reviewcompass/runtime/workflow-state-snapshot.yaml` は `next --json` の副産物であり、正本ではない。正本は常に `next --json` と state refs である。snapshot が古い、手動更新された、または直近 `next --json` と照合できない場合は信頼しない。

snapshot の最低構造は次とする。

```yaml
schema_version: string
generated_by: tools/check-workflow-action.py
generated_at: string
source_next_action_sha256: string
current_work:
  required_action: string
  title: string
  outer_node: string | null
  inner_node: string | null
  active_gate: string | null
active_side_tracks: [object]
git_tree_summary:
  clean: boolean
  staged_files: [string]
  unstaged_files: [string]
post_write_manifest_summary: object
workflow_state_summary: object
```

`current_work.outer_node` は reopen / maintenance / workflow / post-write などの外側の状態、`inner_node` は phase / stage / gate などの内側の単位を表す。UI や人向け報告は snapshot を読んでよいが、操作可否は `next --json` と operation preflight で再確認する。

### 4. read-only / mutating 操作の保存先（Req 14 受入 11〜12）

approval gate record、side track stack、workflow-state snapshot は次の保存先を基線とする。

| 対象 | 保存先 | 正本性 | read-only 操作 | mutating 操作 |
|---|---|---|---|---|
| approval gate record | `.reviewcompass/runtime/approvals/` 配下または後継 approval state | 承認判断の正本 | inspect | record / consume / invalidate |
| side track stack | `stages/in-progress/side-track-stack.yaml` または後継 runtime state | side track 状態の正本 | current / inspect | push / pop / repair |
| workflow-state snapshot | `.reviewcompass/runtime/workflow-state-snapshot.yaml` | 可視化・監査補助、正本ではない | snapshot / inspect | save snapshot のみ。操作許可は変更しない |

read-only 操作と mutating 操作を同じ operation として扱ってはならない。mutating 操作は Requirement 13 の operation contract に接続し、approval_required、preconditions、postconditions、side effects を明示する。

## Requirement 15 設計モデル：構造化有効プロンプトと監査（Req 15）

Requirement 15 は、有効プロンプトを「LLM が行う言語タスクの仕様」として構造化する。機械タスクは operation contract、preflight、runner、guard が担う。

### 1. structured effective prompt schema（Req 15 受入 1〜4）

既存の `.reviewcompass/runtime/effective-prompts/*.prompt.md` は互換出力として維持する。Phase 4 では、同じ判定点から構造化 YAML または JSON を生成し、Markdown prompt はその人向けレンダリングとして扱う。

```yaml
schema_version: string
decision_point:
  kind: string
  required_action: string
  phase: string | null
  stage: string | null
  active_gate: string | null
prompt_length:
  min_chars: integer
  max_chars: integer
  source_ref: string
  failure_verdict: WARN | DEVIATION
preconditions_checked:
  - id: string
    source: next_json | operation_preflight | schema_validation | manifest_validation
    machine_checked: true
    evidence_ref: string
language_task:
  document_kind: design | requirements | tasks | review | alignment | approval | report
  input:
    required_files: [string]
    state_refs: [string]
    source_refs: [string]
  output_format:
    kind: markdown | yaml | json
    required_sections: [string]
    schema_ref: string | null
  constraints: [string]
postconditions:
  - id: string
    check_kind: section_exists | schema_valid | target_set_matches | next_action_compatible | manual_review_required
    source_ref: string
on_completion:
  next_required_action: string | null
  allowed_followups: [string]
  forbidden_actions: [string]
```

`preconditions_checked` は機械が確認済みの条件だけを参照する。LLM がこれから確認する事項をここに置いてはならない。`language_task` は生成または判断する文章の範囲を表し、commit、push、spec.json 更新、review-run 実行などの機械操作手順を埋め込まない。

`prompt_length` は、判定点ごとの長さ上下限を構造化 prompt に写した監査用フィールドである。正本は `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#decision_points` の各判定点に置く `prompt_length_bounds` とし、個別判定点に未設定の場合は同ファイルの `default_prompt_length_bounds` を使う。上下限は `min_chars`、`max_chars`、`failure_verdict` を持ち、`min_chars` と `max_chars` は正の整数かつ `min_chars < max_chars` でなければならない。`failure_verdict` は範囲外 prompt の第1層機械検査 verdict であり、未設定値を runner が推測してはならない。

長さ基準の設定主体は workflow-management の設計・規律マップ更新手続きであり、task 個別の review-run や prompt generator が場当たり的に決めてはならない。上下限の変更は Requirement 13〜15 の責務境界を変えるため、通常の design / tasks / implementation 連鎖で扱う。

### 2. 第1層機械検査（Req 15 受入 5）

有効プロンプト検査は次を確認する。

- 参照先ファイルとアンカーが存在する
- `decision_point`、`preconditions_checked`、`language_task`、`postconditions`、`on_completion` が存在する
- `prompt_length` が `WORKFLOW_DISCIPLINE_MAP.yaml` の `prompt_length_bounds` または `default_prompt_length_bounds` と一致し、長さがその上下限内にある。範囲外の場合は当該 bounds の `failure_verdict` を返す
- DISCIPLINE_MAP または後継 registry に未登録の action kind を使っていない
- review target manifest と review-run target が一致する
- `language_task.output_format` と `postconditions` が対応している
- `preconditions_checked` が機械確認済み条件だけを参照している
- `on_completion` が operation contract の postconditions と次 action に矛盾しない

staged file set とのコミット混線、side track depth、operation preflight の pending conflict は Requirement 12・14 の責務であり、有効プロンプト検査はその結果を参照するだけにする。

### 3. LLM judge audit（Req 15 受入 6〜7）

Phase 6 では、構造化有効プロンプト、該当する `WORKFLOW_NAVIGATION.md` 節、operation contract を入力として LLM judge audit を実行できるようにする。出力は schema 適合 JSON または同等の構造化形式とし、最低限 `gap_id`、`severity`、`prompt_ref`、`contract_ref`、`finding`、`recommended_action`、`blocks_approval` を持つ。

LLM judge audit は意味的な不足を見つける補助であり、最終承認を自動化しない。既知 gap fixture には、必須構造節欠落、機械タスクの prompt 内残留、preconditions の網羅不足、postconditions の確認不能性を含める。

## Requirement 16 設計モデル：段階的実装計画 Phase 0〜6（Req 16）

Requirement 16 は、選択層と実行層の機械化を一度に混ぜず、既存挙動を壊さない順序で実装するための計画である。

### 1. Phase anchor と順序（Req 16 受入 1〜10）

| Phase | 主対象 | 完了条件 |
|---|---|---|
| Phase 0 | D-003 選択層 | 19段階優先順位、`required_action` 唯一化、invariant 検査、mechanical workflow-state repair detection、reopen plan compiler / `reopen-recompile` 相当が TDD で通る |
| Phase 1 | 語彙・schema | `.reviewcompass/schema/` の required_action / next_action / operation contract / effect_kind / phase_boundary / snapshot / language task schema が meta-schema 検証を通る |
| Phase 2 | read-only registry | `check-workflow-action.py operation-list --json` または同等が operation contract を読み取り専用で返す |
| Phase 3 | advisory preflight | `operation-preflight <id> --json` または同等が pending conflict、side track depth、commit mixing、prompt 機械検査を `WARN` 以上で返す |
| Phase 4 | structured effective prompt | 全判定点で構造化 prompt と既存 Markdown prompt を生成し、互換 path を維持する |
| Phase 5 | mechanical blocking | Phase 3 の警告対象のうち serial_only 違反、承認欠落、side track depth 超過、commit mixing を `DEVIATION` で止める |
| Phase 6 | LLM judge audit | 構造化 prompt と運用文書を入力に gap を構造化出力する。承認自動化はしない |

Phase 0 の安定 anchor は `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` の D-003 とする。ただし Phase 0 完了条件は working note の節番号に依存させず、本設計の次の 6 失敗テストを tasks / implementation の受入単位へ写す。

1. `commit_stop_point=true` の reopen state では、`pending_gates` が残っていても `required_action=commit_stop_point`、`active_gate=null`、`phase=null`、`stage=null` を返す。
2. `current_blocker` がある reopen state では、`pending_gates` が残っていても `required_action=wait_for_human_decision`、`active_gate=null` を返す。
3. 正本変更済み phase が `canonical_update_phases` にあるのに `future_gates` / `pending_gates` が full gate を含まない場合、`verdict=DEVIATION`、`required_action=repair_workflow_state` を返す。
4. 第3過程で active gate がある場合だけ、`phase` / `stage` が非 null になる。
5. commit stop point commit 後、worktree clean で HEAD が当該 stop point を含む場合、`required_action=advance_reopen_after_commit_stop_point` を返し、同じ commit stop point を再提示しない。
6. `required_action` ごとの JSON 相互排他 schema を fixture で検証する。

mechanical workflow-state repair detection は Phase 0 の完了条件である。`next --json` は、reopen state の `active_reopen_scope` / `active_impact_review_scope`、`pending_gates`、`completed_gates`、`drafting_completed_gates`、`downstream_impact_decisions`、commit stop point、`current_blocker`、`spec.json` workflow_state の間に矛盾を検出した場合、通常 action へ進まず `required_action=repair_workflow_state` と `verdict=DEVIATION` を返す。Phase 0 は、この repair detection が少なくとも上記 6 失敗テストの 3 番と active scope 欠落・矛盾ケースで TDD 検証されるまで完了扱いにしない。

Phase 1 のうち `required_action.schema.json` と `next_action_response.schema.json` は Phase 0 開始をブロックする最小前提として先行済みである。他の operation contract 系 schema は Phase 0 と並行可能だが、Phase 2 へ進む前にはそろえる。

各 Phase の終了時は、`next --json` が通常作業へ戻れる状態、または明示された停止状態を返すことを確認する。Phase をまたいだ途中状態を単一 commit に混在させない。

### 2. reopen scope と impact review scope（Req 16 受入 11〜12）

本改訂の active reopen scope は `workflow-management` の requirements から design / tasks / implementation への連鎖再実施である。active scope の正本は `stages/in-progress/reopen-procedure-*.yaml` の `active_reopen_scope` と `active_impact_review_scope` である。`spec.json.reopened` は過去に上流を reopen した履歴フラグとして保持され得るため、現在の active reopen scope と同一視しない。

`active_reopen_scope` は正本を再オープンして workflow_state flag を false に戻した feature / phase / gate 範囲を持つ。`active_impact_review_scope` は、正本変更の有無を確認する consumer / derivative feature / phase / gate 範囲を持つが、当該 feature の workflow_state flag を自動で false に戻す根拠ではない。`next --json` は reopen 中にこの in-progress record を必ず読み、scope が欠落・不整合・stale の場合は `repair_workflow_state` を返す。

初期化は reopen 第1過程で行う。trigger_map と分類根拠から両 scope を生成し、利用者承認後に in-progress record へ固定する。更新は gate 完了記録と downstream impact decision の追加に限定し、scope の拡張・縮小は新しい利用者判断または `repair_workflow_state` を必要とする。終了は reopen 第4過程で行い、全 pending gate が解消し、active scope 全件が completed gate または downstream impact decision で覆われた場合だけ in-progress record を `stages/completed/` へ移す。

operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の機械処理化は、他 feature が consumer / derivative として参照し得る。正本 reopen 対象を `workflow-management` に限定する場合でも、review-wave では foundation、runtime、evaluation、analysis、self-improvement、conformance-evaluation への正本変更要否と consumer 契約影響を確認し、reopen scope と impact review scope を混同せず記録する。

### 3. proxy_model triage decision の機械処理化

proxy_model triage decision は、review-run 後の重要件判断を一括化しても、finding ごとの traceability と承認 scope を失わないための operation family として扱う。対象 operation は次を初期集合とする。

- `proxy_triage_prepare_input`：raw response、parsed finding、同根 cluster、候補案を読み、proxy_model 入力 bundle を作る。
- `proxy_triage_record_cluster_decision`：cluster 単位の proxy raw response と decision を保存する。
- `proxy_triage_expand_findings`：cluster-level decision を finding-level decision へ展開する。
- `proxy_triage_validate_coverage`：triage 対象 finding ID が decision file で過不足なく覆われているか検査する。
- `proxy_triage_apply_batch`：coverage validation が通った finding-level decision だけを `triage.yaml` へ batch 適用する。

proxy_model triage decision の適用前には、human-required predicate を必ず評価する。predicate は provider / model 名を見ず、次の証跡だけを読む。

1. proxy 適用対象 finding / cluster coverage と raw / parsed / prompt 証跡
2. approval gate record の `decision_scope`、`decision`、`decided_by`、`target_operation_id`、`target_required_action`、`binding_kind`、digest 束縛
3. operation contract の `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、human-only override set
4. review-wave impact evidence の未解決状態
5. downstream impact decisions と active reopen scope / impact review scope の整合

triage item の `decision_status`、`final_label`、`decision_actor_type` は適用対象の状態確認と二重適用防止には使ってよいが、human-required predicate の正本にはしない。human-required predicate の正本は approval gate record と operation contract、および review-wave / downstream impact evidence である。

human-required predicate は `proxy_triage_evaluate_human_required` という read-only internal check として扱う。入力は、対象 finding / cluster IDs、finding-to-operation mapping、関連 approval gate record、対象 operation contract、review-wave impact evidence、active reopen scope / impact review scope とする。出力は最低限、`verdict`、`blocks_proxy_apply`、`blocking_reasons[]`、`checked_records[]`、`checked_contracts[]`、`source_refs[]` を持つ。`blocks_proxy_apply=true` の場合、後続の `proxy_triage_apply_batch` は `DEVIATION` とし、`triage.yaml` を更新しない。

`未解決 approval gate` は、対象 finding / cluster または対象 operation に紐づく approval gate record のうち、`decision` が `approved` ではない、`consumed=false` のまま対象 operation に未反映、`decision_scope=human_only`、binding digest 不一致、または `next_action_expectation` が `proceed` 以外のものを指す。record が欠落していて、対象 operation contract が `approval_required=true`、human-only override set、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize、または approval-required irreversible operation execution に該当する場合も、未解決 approval gate と同等に扱う。

`approval_required=true の対象 operation` は、finding-to-operation mapping から得た `target_operation_id` / `target_required_action` を `stages/operation-contracts.yaml` の operation contract に解決し、その contract の `approval_required=true`、または branch 内部 step の approval aggregation が true になるものを指す。mapping が欠落、複数候補で一意に解決不能、contract 参照欠落、contract digest / schema_version drift の場合は、proxy が安全に適用可能とは扱わず `blocks_proxy_apply=true` とする。

predicate の評価順序は次の固定順とする。

1. coverage と証跡存在を検査し、対象 finding / cluster、raw、parsed、prompt、proxy raw、decision file、mapping が過不足なくそろわない場合は `DEVIATION`。
2. finding-to-operation mapping から対象 operation contract を解決し、一意に解決できない場合は `DEVIATION`。
3. 対象 operation contract と human-only override set から `approval_required`、`phase_boundary`、`effect_kind`、`actor.kind`、approval aggregation を評価する。
4. 関連 approval gate record の `decision_scope`、`decision`、`decided_by`、`binding_kind`、digest、`consumed`、`next_action_expectation` を検査する。
5. review-wave impact evidence、downstream impact decisions、active reopen scope / impact review scope の未解決・矛盾を検査する。
6. 3〜5 のいずれかが human-required を示す場合は、triage item の `decision_status`、`final_label`、`decision_actor_type`、proxy decision の selected option に関係なく `blocks_proxy_apply=true` とする。

優先順位は次のとおりとする。

1. `decision_scope=human_only`、未解決 approval gate、`approval_required=true` の対象 operation、未解決 review-wave impact evidence は、proxy_model の判断より常に優先し、proxy apply を止める。
2. 必須証跡が欠落、競合、または対象 finding / cluster coverage を満たさない場合は `DEVIATION` とする。
3. triage 上の `leave-as-is`、`proxy_approved`、または proxy_model の selected decision は、1 の human-required 証跡を打ち消さない。
4. 1〜3 を通過し、かつ finding / cluster coverage が完全な場合だけ、proxy decision を finding-level decision へ展開できる。

`proxy_triage_apply_batch` の operation contract は、preconditions に次を持つ。

- `proxy_triage_validate_coverage` が成功している
- `proxy_triage_evaluate_human_required` が成功し、`blocks_proxy_apply=false` を返している
- すべての対象 finding に raw response、parsed finding、decision prompt、proxy raw response、cluster/finding mapping が存在する
- 対象 finding / cluster に紐づく approval gate record が存在する場合、その `decision_scope` は `proxy_allowed` または `advisory_only` であり、`human_only` ではない
- 対象 operation contract の `approval_required` が true、または human-only override set に該当する場合、proxy apply を停止する
- review-wave impact evidence、downstream impact decisions、active reopen scope / impact review scope に未解決または矛盾がない

これらの preconditions のいずれかが満たされない場合、`proxy_triage_apply_batch` は `DEVIATION` とし、triage.yaml を更新しない。

cluster-level decision は保存してよいが、実装修正や manifest 作成の承認単位は finding-level decision とする。`proxy_triage_expand_findings` は、cluster ID、含まれる finding IDs、採用案、棄却案理由、final label、source raw paths、decision prompt path、proxy raw path を finding ごとに複製し、各 finding decision に `cluster_decision_id` を保持する。

coverage validation は次を fail-closed にする。

- triage 対象 finding ID が decision file に存在しない
- decision file に triage 対象外 finding ID が混入している
- cluster decision の finding set と展開後 finding decisions が一致しない
- `final_label`、採用案、判断理由、source raw paths、decision prompt path、proxy raw path のいずれかが欠落している
- `review_triage_decide` approval と apply-fixes approval の scope が一致しない

approval scope は `approval_record.scope` で区別する。`review_triage_decide` は triage label の採否だけを許可し、仕様文書・実装・spec.json・workflow_state の変更は許可しない。apply-fixes は対象 finding IDs、対象ファイル、期待する変更種別を別 record として持つ。batch 適用は triage decision の一括反映に限り、修正実装を同時に行わない。

