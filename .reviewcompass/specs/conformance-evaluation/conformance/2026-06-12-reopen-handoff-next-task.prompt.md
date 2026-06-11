# Effective Next Task Prompt

## Decision Point
- reopen_handoff:2026-06-12-multi-llm-entry-followup

## 次タスク方針

本プロンプトは、conformance 記録
`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`
の gap（MLE-GAP-001〜006）を正本仕様へ反映するための reopen 引き渡しの方針を 1 本に束ねたものである。

1. 変更方針は `change_policy: minimal_existing_spec_change`。原則 `change_type: additive` を優先し、
   既存項目の意味をできるだけ変更しない。ただし既存項目を絶対に変更してはならないわけではない。
2. 既存 requirements／design／tasks の意味変更が必要な場合（本件では MLE-GAP-003 の
   `feature_order`／`phase_order` 語彙調停）は `change_type: semantic_change` とし、
   `existing_contract_changed: true`、`human_escalation_required: true` を要求する。
   利用者が調停案（requirements 草案 §3 の案 A／B／C）を選択するまで反映を開始しない。
3. 反映は workflow-management の reopen 手続きで行う。reopen の起動・spec.json の workflow_state
   変更・commit・push は不可逆操作であり、利用者の明示承認を必要とする。
4. 反映順序は requirements → design → tasks。各 phase は reopen 後の
   `triad-review / review-wave / alignment / approval` を完了するまで、対応する gap を
   resolved 扱いにしない（conformance-evaluation Requirement 12 受入 4）。
5. tasks.md 本体の推定・再作成やタスク分解の確定は行わない。`phase: tasks` の反映要否は
   reopen 手続きの中で判断する（同 受入 5）。
6. evaluation 仕様への MLE-C-007 の昇格要否、配布テンプレート契約（MLE-C-005・C-006）の
   所有者確定、MLE-GAP-006 の根本対応可否は、人間判断（needs_human_decision: true）である。
7. 運用文書（WORKFLOW_NAVIGATION.md・WORKFLOW_DISCIPLINE_MAP.yaml）の更新は reopen 対象外だが、
   post-write 検証を伴う。仕様反映と同じ趣旨の変更として整合させる。

## Prompt Source Refs
- .reviewcompass/specs/conformance-evaluation/requirements.md（Requirement 9・12）
- .reviewcompass/specs/conformance-evaluation/design.md §13.9
- docs/operations/WORKFLOW_NAVIGATION.md（reopen_classification_required／共通禁止事項）
- .reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-spec-update-drafts/
