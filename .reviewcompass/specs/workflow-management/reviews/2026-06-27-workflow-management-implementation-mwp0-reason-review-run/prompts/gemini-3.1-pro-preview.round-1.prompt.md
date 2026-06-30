prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
implementation

# Criteria
---
criteria_id: wm-implementation-mwp0-reason-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: reason vs reasons separation

## Review Task

Review the target files for: MWP-0 T-020 prior deferred item (b) — reason vs reasons semantic separation.

Primary judgment question:

Is the semantic distinction between the `reason` field inside `next_action` (described in design §5.3 as a common field for all kind values) and the top-level `reasons` array (one of the 5 required fields in the response) sufficiently defined in the schema and upstream design documents, and is the deferred item (b) from T-020 addressed?

Do not combine multiple independent judgments in this prompt. This review covers only the reason vs reasons separation. if/then constraints and kind value separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `design-section-5-2-5-3-excerpt.md` (verbatim excerpt from `.reviewcompass/specs/workflow-management/design.md` §5.2 and §5.3, covering the reason/reasons fields and next_action required field list)

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-reason-upstream-intent

Purpose: T-020 deferred item (b) text for background context.
The authoritative design document content is provided as `design-section-5-2-5-3-excerpt.md` in the review target above.
Use this section for background intent only.

T-020 先送り事項(b):

```
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
```

T-020 完了条件一覧（reason に関連する条件の明示なし）:

```
1. next --json の kind 値域が7値に限定されること
2. commit-preflight サブコマンドが3値の kind を返すこと
3. スキーマの if/then 制約の失敗テストが作成され通過すること
4. WORKFLOW_NAVIGATION.md の更新
5. 廃止表現の統一

先送り事項(b)（reason vs reasons の責務明確化）に対応する完了条件は T-020 完了条件一覧に明示されていない。
```

## Required Checks

1. Check whether `next_action_response.schema.json` defines a `reason` field within `next_action.properties` or `next_action.required`, and whether this matches the intent described in design §5.3 (all-kind common field).
2. Check whether the top-level `reasons` array defined in the schema has a schema-level description or differentiation from the inner `reason` field.
3. Check whether the deferred item (b) from T-020 — "clarify the responsibility difference between the inner reason field and the top-level reasons array in design and implementation" — is addressed by either the schema (`next_action_response.schema.json`) or the design document excerpt (`design-section-5-2-5-3-excerpt.md`).
4. Check whether the presence or absence of `reason` in the schema matches what the design document (`design-section-5-2-5-3-excerpt.md` §5.3 common fields table) specifies. If the schema omits `reason` from `next_action.required` or `next_action.properties` while the design lists it as a common field, determine whether that omission is documented as intentional anywhere in the target files.

## Out Of Scope

- if/then field constraints — separate criteria
- kind value separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a contradiction that breaks the schema's required field contract.
- Use ERROR for an unaddressed T-020 deferred item (b) where the required clarification is missing from both schema and upstream documents, or for a discrepancy between design §5.3 and the schema that is not intentional and not documented.
- Use WARN for meaningful ambiguity, undocumented intentional omission, or incomplete traceability between design §5.3 and schema.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path` or `path:section`.
- Return `findings: []` only when the reason vs reasons distinction is sufficiently defined and T-020 deferred item (b) is verifiably addressed.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/schema/next_action_response.schema.json
.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/design-section-5-2-5-3-excerpt.md

# Target document
## .reviewcompass/schema/next_action_response.schema.json

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "$comment": "additionalProperties は指定しない（前向き拡張用：将来の実装で新フィールドを追加してもスキーマ改訂なしに対応できるよう、段階的拡張を妨げない）",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "$comment": "additionalProperties は指定しない（後ろ向き互換用：旧バージョンのツールが出力する pending_gates・next_pending_gate 等を許容するため。最上位の前向き拡張とは目的が異なる）",
      "type": "object",
      "required": [
        "kind",
        "required_action",
        "active_gate",
        "feature",
        "phase",
        "stage",
        "required_feature_scope",
        "blocked_by",
        "future_gates",
        "state_refs"
      ],
      "properties": {
        "verdict": false,
        "kind": {
          "type": "string",
          "enum": [
            "in_progress",
            "blocking_in_progress",
            "verification_pending",
            "reopen_in_progress",
            "feature_definition_required",
            "completed",
            "unknown"
          ]
        },
        "required_action": {
          "$ref": "urn:reviewcompass:schema:required_action"
        },
        "active_gate": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "feature": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "phase": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "stage": {
          "oneOf": [{ "type": "string" }, { "type": "null" }]
        },
        "required_feature_scope": {
          "type": "array",
          "items": { "type": "string" }
        },
        "blocked_by": {
          "oneOf": [{ "type": "object" }, { "type": "null" }]
        },
        "future_gates": {
          "type": "array"
        },
        "state_refs": {
          "type": "object"
        },
        "pending_gates": {
          "type": "array"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": { "required_action": { "const": "repair_workflow_state" } },
            "required": ["required_action"]
          },
          "then": {
            "required": ["repair_reasons"],
            "properties": {
              "repair_reasons": {
                "type": "array",
                "minItems": 1
              }
            }
          }
        },
        {
          "if": {
            "properties": { "required_action": { "const": "run_maintenance" } },
            "required": ["required_action"]
          },
          "then": {
            "required": ["action_parameters"],
            "properties": {
              "action_parameters": {
                "type": "object",
                "required": [
                  "maintenance_action",
                  "allowed_scope",
                  "allowed_files",
                  "completion_conditions",
                  "active_stack_frame_id",
                  "parent_frame_id"
                ]
              }
            }
          }
        },
        {
          "$comment": "① commit_stop_point: active_gate/phase/stage はすべて null（受入 11(6)①）",
          "if": {
            "properties": { "required_action": { "const": "commit_stop_point" } },
            "required": ["required_action"]
          },
          "then": {
            "properties": {
              "active_gate": { "type": "null" },
              "phase": { "type": "null" },
              "stage": { "type": "null" }
            }
          }
        },
        {
          "$comment": "② run_reopen_pending_gate: active_gate 非 null、blocked_by=null（受入 11(6)②）",
          "if": {
            "properties": { "required_action": { "const": "run_reopen_pending_gate" } },
            "required": ["required_action"]
          },
          "then": {
            "properties": {
              "active_gate": { "type": "string" },
              "blocked_by": { "type": "null" }
            }
          }
        },
        {
          "$comment": "③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式（受入 11(6)③）",
          "if": {
            "properties": { "required_action": { "const": "run_reopen_drafting" } },
            "required": ["required_action"]
          },
          "then": {
            "properties": {
              "active_gate": {
                "type": "string",
                "pattern": "^stages/.+\\.yaml#drafting$"
              }
            }
          }
        },
        {
          "$comment": "⑤ wait_for_human_decision: blocked_by 非 null かつ type フィールド必須（受入 11(6)⑤）",
          "if": {
            "properties": { "required_action": { "const": "wait_for_human_decision" } },
            "required": ["required_action"]
          },
          "then": {
            "properties": {
              "blocked_by": {
                "type": "object",
                "required": ["type"],
                "properties": {
                  "type": { "type": "string" }
                }
              }
            }
          }
        }
      ]
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}


## .reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/design-section-5-2-5-3-excerpt.md

# design.md §5.2 and §5.3 excerpt
# Source: .reviewcompass/specs/workflow-management/design.md
# Sections: §5.2 (relevant to reason/reasons) and §5.3 (kind detail fields)

## §5.2 next_action_response.schema.json — 最上位構造（抜粋）

**最上位必須フィールド（5つ）**：
- `verdict`（文字列）
- `exit_code`（整数）
- `next_action`（オブジェクト）
- `reasons`（配列）
- `current_state`（オブジェクト）

**`next_action` 必須フィールド（10つ）**：
`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・
`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`

Note: The `reasons` array is a top-level required field. It is not the same as any
field within `next_action`. The design document does not provide an explicit description
of what the `reasons` array contains or how it differs from `next_action`-level fields.

## §5.3 kind 詳細フィールド設計 — 全 kind 共通フィールド（原文）

| フィールド | 役割 |
|-----------|------|
| `kind` | 現在地のカテゴリ（7値） |
| `required_action` | 次にすべき操作の名前（機械が読む） |
| `reason` | 状態の説明（人間が読む） |

Note: The `reason` field is listed here as a `next_action`-level common field. It
is not listed in §5.2's next_action required fields (10 mandatory fields). The design
document does not contain a section that explicitly contrasts `next_action.reason`
with the top-level `reasons` array.

## T-020 先送り事項(b) — 原文

```
next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
```

T-020 完了条件一覧（5項目）には、先送り事項(b) に対応する明示的な検証項目が含まれていない。

