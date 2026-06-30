# workflow-management implementation review — MWP-0: if/then constraint completeness

run_id: 2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run
criteria_id: wm-implementation-mwp0-ifthen-2026-06-27
phase: implementation
stage: triad-review
variant: implementation_review_independent_3way

## Change Summary

MWP-0 T-020 の先送り事項(a) として、`next_action_response.schema.json` の `next_action.allOf` に `required_action` 値ごとの条件付きフィールド制約（JSON Schema Draft 2020-12 の if/then 構文）を追加した。対象は受入 11(6)①②③⑤ の4種類。④と⑥は T-015 で実装済みのため除外。

## Review Question

`next_action_response.schema.json` に追加された if/then 制約（①②③⑤）が、要件（受入 11(6)①②③⑤）の仕様を漏れなく・正確に実装しているかを独立して分析してほしい。あなたが気づいた問題・疑問を率直に示してほしい。

分析は上記1点に限定せず、スキーマとテストに関して問題と判断したことは自由に指摘してよい。

## Scope / Out of Scope

**対象**：
- `next_action_response.schema.json` の `allOf` 内 if/then 制約（①②③⑤の4つ）
- `tests/tools/test_t020_kind_redesign.py` の `SchemaIfThenConstraintTests` クラス
- 受入 11(6)①②③⑤ との整合

**対象外**：
- ④ `repair_workflow_state` の `repair_reasons` 制約（T-015 実装済み）
- ⑥ `run_maintenance` の `action_parameters` 制約（T-015 実装済み）
- kind 値分離（別プロンプトで審査）
- reason vs reasons 責務分離（別プロンプトで審査）
- commit / push / spec.json 更新 / phase 完了 / 人間承認代行

---

## SOURCE MATERIAL: 要件（受入 11(6)）

```text
【Requirement 2 受入 11(6)】
required_action の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、
スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。

① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時：active_gate=null・phase=null・stage=null・repair_reasons に修復理由を含める（T-015 実装済み）
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時：action_parameters に 6 フィールド必須（T-015 実装済み）

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

## SOURCE MATERIAL: 設計（design §5.2）

```text
【design §5.2 — if/then 制約の定義場所】
受入 11(6) の制約①②③⑤は if/then 構文で next_action の allOf 内に定義する（MWP-0 T-020 の責務）。
スキーマ全体の必須フィールドは 5 つ（verdict・exit_code・next_action・reasons・current_state）。
next_action 必須フィールドは 10 つ：kind・required_action・active_gate・feature・phase・stage・
required_feature_scope・blocked_by・future_gates・state_refs
```

---

## FILE: .reviewcompass/schema/next_action_response.schema.json（allOf 部分を抜粋）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "next_action": {
      "type": "object",
      "required": [
        "kind", "required_action", "active_gate", "feature", "phase", "stage",
        "required_feature_scope", "blocked_by", "future_gates", "state_refs"
      ],
      "properties": {
        "verdict": false,
        "kind": {
          "type": "string",
          "enum": [
            "in_progress", "blocking_in_progress", "verification_pending",
            "reopen_in_progress", "feature_definition_required", "completed", "unknown"
          ]
        },
        "active_gate": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "phase": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "stage": { "oneOf": [{ "type": "null" }, { "type": "string" }] },
        "blocked_by": { "oneOf": [{ "type": "object" }, { "type": "null" }] }
      },
      "allOf": [
        {
          "if": { "properties": { "required_action": { "const": "repair_workflow_state" } }, "required": ["required_action"] },
          "then": { "required": ["repair_reasons"], "properties": { "repair_reasons": { "type": "array", "minItems": 1 } } }
        },
        {
          "if": { "properties": { "required_action": { "const": "run_maintenance" } }, "required": ["required_action"] },
          "then": { "required": ["action_parameters"], "properties": { "action_parameters": { "type": "object", "required": ["maintenance_action","allowed_scope","allowed_files","completion_conditions","active_stack_frame_id","parent_frame_id"] } } }
        },
        {
          "$comment": "① commit_stop_point: active_gate/phase/stage はすべて null（受入 11(6)①）",
          "if": { "properties": { "required_action": { "const": "commit_stop_point" } }, "required": ["required_action"] },
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
          "if": { "properties": { "required_action": { "const": "run_reopen_pending_gate" } }, "required": ["required_action"] },
          "then": {
            "properties": {
              "active_gate": { "type": "string" },
              "blocked_by": { "type": "null" }
            }
          }
        },
        {
          "$comment": "③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式（受入 11(6)③）",
          "if": { "properties": { "required_action": { "const": "run_reopen_drafting" } }, "required": ["required_action"] },
          "then": {
            "properties": {
              "active_gate": { "type": "string", "pattern": "^stages/.+\\.yaml#drafting$" }
            }
          }
        },
        {
          "$comment": "⑤ wait_for_human_decision: blocked_by 非 null かつ type フィールド必須（受入 11(6)⑤）",
          "if": { "properties": { "required_action": { "const": "wait_for_human_decision" } }, "required": ["required_action"] },
          "then": {
            "properties": {
              "blocked_by": {
                "type": "object",
                "required": ["type"],
                "properties": { "type": { "type": "string" } }
              }
            }
          }
        }
      ]
    }
  }
}
```

## FILE: tests/tools/test_t020_kind_redesign.py（SchemaIfThenConstraintTests クラス）

```python
class SchemaIfThenConstraintTests(unittest.TestCase):
  """next_action_response.schema.json の if/then 制約（受入 11(6) ①②③⑤）を確認"""

  # ① commit_stop_point の制約
  def test_commit_stop_point_valid_when_all_null(self):
    """① commit_stop_point: active_gate/phase/stage がすべて null なら有効"""
    na = self._minimal_valid_next_action(
      "commit_stop_point", active_gate=None, phase=None, stage=None,
      blocked_by={"type": "commit_stop_point"},
    )
    self._assert_valid(...)

  def test_commit_stop_point_invalid_when_active_gate_nonnull(self):
    """① commit_stop_point: active_gate が非 null なら無効"""
    na = self._minimal_valid_next_action(
      "commit_stop_point", active_gate="stages/implementation.yaml#drafting",
      phase=None, stage=None,
    )
    self._assert_invalid(...)

  def test_commit_stop_point_invalid_when_phase_nonnull(self):
    """① commit_stop_point: phase が非 null なら無効"""
    na = self._minimal_valid_next_action(
      "commit_stop_point", active_gate=None, phase="implementation", stage=None,
    )
    self._assert_invalid(...)

  def test_commit_stop_point_invalid_when_stage_nonnull(self):
    """① commit_stop_point: stage が非 null なら無効"""
    na = self._minimal_valid_next_action(
      "commit_stop_point", active_gate=None, phase=None, stage="drafting",
    )
    self._assert_invalid(...)

  # ② run_reopen_pending_gate の制約
  def test_run_reopen_pending_gate_valid_with_nonnull_active_gate(self):
    """② run_reopen_pending_gate: active_gate が非 null なら有効"""
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate", active_gate="stages/implementation.yaml#triad-review",
      phase="implementation", stage="triad-review", blocked_by=None,
    )
    self._assert_valid(...)

  def test_run_reopen_pending_gate_invalid_when_active_gate_null(self):
    """② run_reopen_pending_gate: active_gate が null なら無効"""
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate", active_gate=None, phase=None, stage=None,
    )
    self._assert_invalid(...)

  def test_run_reopen_pending_gate_invalid_when_blocked_by_nonnull(self):
    """② run_reopen_pending_gate: blocked_by が非 null なら無効"""
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate", active_gate="stages/implementation.yaml#triad-review",
      phase="implementation", stage="triad-review", blocked_by={"type": "some_blocker"},
    )
    self._assert_invalid(...)

  # ③ run_reopen_drafting の制約
  def test_run_reopen_drafting_valid_with_drafting_active_gate(self):
    """③ run_reopen_drafting: active_gate が stages/<phase>.yaml#drafting 形式なら有効"""
    na = self._minimal_valid_next_action(
      "run_reopen_drafting", active_gate="stages/implementation.yaml#drafting",
      phase="implementation", stage="drafting",
    )
    self._assert_valid(...)

  def test_run_reopen_drafting_invalid_when_active_gate_not_drafting(self):
    """③ run_reopen_drafting: active_gate が drafting 形式でないなら無効"""
    na = self._minimal_valid_next_action(
      "run_reopen_drafting", active_gate="stages/implementation.yaml#triad-review",
      phase="implementation", stage="drafting",
    )
    self._assert_invalid(...)

  def test_run_reopen_drafting_invalid_when_active_gate_null(self):
    """③ run_reopen_drafting: active_gate が null なら無効"""
    na = self._minimal_valid_next_action(
      "run_reopen_drafting", active_gate=None, phase="implementation", stage="drafting",
    )
    self._assert_invalid(...)

  # ⑤ wait_for_human_decision の制約
  def test_wait_for_human_decision_valid_with_blocked_by_type(self):
    """⑤ wait_for_human_decision: blocked_by に type フィールドがあれば有効"""
    na = self._minimal_valid_next_action(
      "wait_for_human_decision", blocked_by={"type": "reopen_approval_required"},
    )
    self._assert_valid(...)

  def test_wait_for_human_decision_invalid_when_blocked_by_null(self):
    """⑤ wait_for_human_decision: blocked_by が null なら無効"""
    na = self._minimal_valid_next_action(
      "wait_for_human_decision", blocked_by=None,
    )
    self._assert_invalid(...)

  def test_wait_for_human_decision_invalid_when_blocked_by_lacks_type(self):
    """⑤ wait_for_human_decision: blocked_by に type フィールドがなければ無効"""
    na = self._minimal_valid_next_action(
      "wait_for_human_decision", blocked_by={"reason": "some reason"},
    )
    self._assert_invalid(...)
```

注意：テスト用の `_minimal_valid_next_action` ヘルパーは `blocked_by` パラメータを受け取る。
`test_commit_stop_point_valid_when_all_null` では `blocked_by={"type": "commit_stop_point"}` を渡しているが、
これは有効ケースのヘルパー呼び出しであり、スキーマがこの値を強制しているかどうかとは別問題である。

## Output Contract

所見は次の形式で出力してほしい。

```yaml
findings:
  - id: <連番（F-001 など）>
    severity: must-fix | should-fix | leave-as-is
    target: <対象ファイル名または箇所>
    summary: <1行の説明（日本語）>
    detail: <具体的な問題の説明。要件・設計の原文を引用して根拠を示す>
    suggestion: <修正の方向性（あれば）>
```

所見がない場合は `findings: []` を返してほしい。
