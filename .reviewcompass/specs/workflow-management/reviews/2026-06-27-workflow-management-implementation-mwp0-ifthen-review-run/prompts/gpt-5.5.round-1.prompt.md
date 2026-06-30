prompt_id: openai_review
provider: openai-api
model_id: gpt-5.5

# Task
Review the target document for the requested phase and criteria.

# Phase
implementation

# Criteria
---
criteria_id: wm-implementation-mwp0-ifthen-2026-06-27
phase: implementation
stage: triad-review
---

# workflow-management implementation review — MWP-0: if/then constraint completeness

## Review Task

Review the target files for: MWP-0 T-020 if/then constraint completeness.

Primary judgment question:

Do the if/then constraints added to `next_action_response.schema.json` in allOf entries ①②③⑤ implement all field constraints specified in 受入 11(6)①②③⑤ without omission, weakening, or unsupported addition, and does the test class `SchemaIfThenConstraintTests` sufficiently cover the specified constraints?

Do not combine multiple independent judgments in this prompt. This review covers only if/then constraint completeness. Kind value separation and reason/reasons separation are reviewed in separate criteria.

## Review Target

The authoritative target is the file set supplied by the review runner.

- `.reviewcompass/schema/next_action_response.schema.json`
- `tests/tools/test_t020_kind_redesign.py`

Do not treat this criteria file or any author-written summary as a substitute for the target files.

## Source Materials

### mwp0-if-then-upstream-intent

Purpose: Requirement 2 / design / tasks intent for if/then field constraints on required_action values.
Use as intent-transfer evidence and background only. Do not treat as a replacement for target files.

受入 11(6) — required_action 値ごとのフィールド制約（原文）:

```
① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時（T-015 実装済み、本レビュー対象外）
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時（T-015 実装済み、本レビュー対象外）

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

設計 §5.2 — if/then 制約の配置方針:

```
受入 11(6) の制約①②③⑤は if/then 構文で next_action の allOf 内に定義する（MWP-0 T-020 の責務）。
```

T-020 先送り事項(a) — 完了条件 3:

```
(a) 受入 11(6)①②③⑤の required_action 値ごとのフィールド制約を next_action_response.schema.json の
    if/then 構文で定義する（④の repair_reasons と⑥の action_parameters は T-015 完了条件2で対処済みのため除外）。

完了条件 3: スキーマの if/then 制約（先送り事項(a)）の失敗テストが作成され、実装で通過する。
```

## Required Checks

1. Check each of ①②③⑤ in the allOf section: does the if/then entry enforce all and only the constraints stated in 受入 11(6) for that required_action value?
2. Check the SchemaIfThenConstraintTests class in the test file: does it cover the failure cases for each constraint clause stated in 受入 11(6)①②③⑤?
3. Check that the constraints for ④ and ⑥ (T-015 implemented) are present but are not weakened or removed by the new entries.
4. Check that no if/then entry adds constraints not specified in 受入 11(6) or design §5.2.

## Out Of Scope

- Kind value separation (7 values vs 3 values) — separate criteria
- reason vs reasons semantic separation — separate criteria
- Commit, push, spec.json update, phase completion, or human approval delegation

## Finding Policy

- Use CRITICAL for a constraint that bypasses a required_action boundary or allows a forbidden state.
- Use ERROR for a missing constraint clause, a weakened constraint, or a test gap that leaves a constraint unverifiable.
- Use WARN for meaningful ambiguity, weak traceability between requirement and schema clause, or partial coverage.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:allOf[n]`, or `path:class.method`.
- Return `findings: []` only when every constraint in 受入 11(6)①②③⑤ is fully and accurately implemented and tested.


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
tests/tools/test_t020_kind_redesign.py

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


## tests/tools/test_t020_kind_redesign.py

"""T-020: kind 7値スキーマ更新と commit-preflight サブコマンドの TDD テスト

対象タスク: .reviewcompass/specs/workflow-management/tasks.md §T-020
対象要件: Requirement 2 受入 12（MWP-0 2026-06-27）

TDD 規律に従い、実装前にこのテストを作成した。
テストはすべて失敗状態でコミットし、実装でパスさせる。
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
NEXT_ACTION_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "next_action_response.schema.json"
COMMIT_PREFLIGHT_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "commit_preflight_response.schema.json"

EXPECTED_NEXT_KIND_VALUES = frozenset([
  "completed",
  "in_progress",
  "blocking_in_progress",
  "verification_pending",
  "reopen_in_progress",
  "feature_definition_required",
  "unknown",
])

EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES = frozenset([
  "commit_candidate",
  "commit_mixing_risk",
  "commit_unit_stale",
])


def run_script(args, cwd):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def _init_git_repo(tmpdir):
  subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)
  subprocess.run(
    ["git", "config", "user.email", "test@example.com"],
    cwd=tmpdir, check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "config", "user.name", "Test"],
    cwd=tmpdir, check=True, capture_output=True,
  )
  (Path(tmpdir) / ".gitkeep").write_text("", encoding="utf-8")
  subprocess.run(["git", "add", ".gitkeep"], cwd=tmpdir, check=True, capture_output=True)
  subprocess.run(
    ["git", "commit", "-m", "init"],
    cwd=tmpdir, check=True, capture_output=True,
  )


class NextActionSchemaKindValueTests(unittest.TestCase):
  """next_action_response.schema.json の kind enum が7値に限定されていることを確認"""

  def test_schema_kind_enum_has_exactly_seven_values(self):
    """next_action_response.schema.json の kind enum は7値のみ"""
    with open(NEXT_ACTION_SCHEMA, encoding="utf-8") as f:
      schema = json.load(f)
    kind_enum = (
      schema
      .get("properties", {})
      .get("next_action", {})
      .get("properties", {})
      .get("kind", {})
      .get("enum", [])
    )
    self.assertEqual(
      frozenset(kind_enum),
      EXPECTED_NEXT_KIND_VALUES,
      f"kind enum は {sorted(EXPECTED_NEXT_KIND_VALUES)} のみであること。"
      f"実際の値: {sorted(kind_enum)}",
    )

  def test_schema_kind_enum_excludes_commit_related_values(self):
    """next_action_response.schema.json の kind enum にコミット関連値が含まれないこと"""
    with open(NEXT_ACTION_SCHEMA, encoding="utf-8") as f:
      schema = json.load(f)
    kind_enum = set(
      schema
      .get("properties", {})
      .get("next_action", {})
      .get("properties", {})
      .get("kind", {})
      .get("enum", [])
    )
    for forbidden in EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES:
      self.assertNotIn(
        forbidden,
        kind_enum,
        f"next_action_response.schema.json の kind enum に {forbidden} が含まれている。"
        "コミット関連の kind は commit_preflight_response.schema.json に移動すること。",
      )

  def test_schema_kind_enum_excludes_old_14_values(self):
    """旧 14 値の詳細 kind が next_action_response.schema.json に残っていないこと"""
    old_values_to_remove = [
      "stage",
      "cross_feature_stage",
      "upstream_recheck",
      "maintenance_in_progress",
      "blocking_unit_in_progress",
      "blocking_unit_required",
      "parent_resume_pending",
      "resume_in_progress",
      "post_write_verification",
      "post_write_policy_violation",
      "post_write_human_decision_required",
      "reopen_classification_required",
      "lightweight_self_check",
      "post_write_human_decision_required",
    ]
    with open(NEXT_ACTION_SCHEMA, encoding="utf-8") as f:
      schema = json.load(f)
    kind_enum = set(
      schema
      .get("properties", {})
      .get("next_action", {})
      .get("properties", {})
      .get("kind", {})
      .get("enum", [])
    )
    for old_value in old_values_to_remove:
      self.assertNotIn(
        old_value,
        kind_enum,
        f"旧 kind 値 '{old_value}' が next_action_response.schema.json に残っている。"
        "7値への整理で除去すること。",
      )


class CommitPreflightSchemaTests(unittest.TestCase):
  """commit_preflight_response.schema.json の存在と kind 値域を確認"""

  def test_commit_preflight_schema_file_exists(self):
    """commit_preflight_response.schema.json が存在すること"""
    self.assertTrue(
      COMMIT_PREFLIGHT_SCHEMA.exists(),
      f"{COMMIT_PREFLIGHT_SCHEMA} が存在しない。T-020 責務2で新規作成が必要。",
    )

  def test_commit_preflight_schema_kind_enum_has_exactly_three_values(self):
    """commit_preflight_response.schema.json の kind enum は3値のみ"""
    self.assertTrue(
      COMMIT_PREFLIGHT_SCHEMA.exists(),
      "commit_preflight_response.schema.json が存在しない",
    )
    with open(COMMIT_PREFLIGHT_SCHEMA, encoding="utf-8") as f:
      schema = json.load(f)
    kind_enum = set(
      schema
      .get("properties", {})
      .get("next_action", {})
      .get("properties", {})
      .get("kind", {})
      .get("enum", [])
    )
    self.assertEqual(
      kind_enum,
      EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES,
      f"commit-preflight の kind enum は {sorted(EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES)} のみであること。"
      f"実際の値: {sorted(kind_enum)}",
    )


class NextActionKindBehaviorTests(unittest.TestCase):
  """next --json が旧 commit 関連 kind を返さないことを確認"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _write_staged(self, relative_path, text):
    path = Path(self.tmpdir) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subprocess.run(
      ["git", "add", relative_path],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def _freeze_commit_unit(self, allowed_files):
    args = [
      "commit-unit", "freeze",
      "--work-unit-id", "unit-blocking-001",
      "--json",
    ]
    for f in allowed_files:
      args.extend(["--allowed-file", f])
    return run_script(args, cwd=self.tmpdir)

  def test_next_does_not_return_commit_unit_stale(self):
    """stale commit unit 状態で next --json が commit_unit_stale を返さないこと"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_staged(target, "print('x')\n")
    self._freeze_commit_unit([target])
    self._write_staged(target, "print('changed')\n")

    result = run_script(["next", "--json"], cwd=self.tmpdir)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"],
      "commit_unit_stale",
      "next --json は commit_unit_stale を返してはならない。"
      "commit-preflight サブコマンドに移動済みのはず。",
    )

  def test_next_does_not_return_commit_mixing_risk(self):
    """commit unit 混入状態で next --json が commit_mixing_risk を返さないこと"""
    self._write_staged("tools/check_workflow_action/blocking_unit.py", "print('x')\n")
    self._freeze_commit_unit(["tools/check_workflow_action/blocking_unit.py"])
    self._write_staged("docs/notes/working/other.md", "別作業\n")

    result = run_script(["next", "--json"], cwd=self.tmpdir)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"],
      "commit_mixing_risk",
      "next --json は commit_mixing_risk を返してはならない。"
      "commit-preflight サブコマンドに移動済みのはず。",
    )

  def test_next_returns_only_seven_kind_values(self):
    """next --json が返す kind は7値のいずれかであること"""
    result = run_script(["next", "--json"], cwd=self.tmpdir)

    self.assertEqual(result.returncode in (0, 2), True, result.stderr)
    data = json.loads(result.stdout)
    kind = data["next_action"]["kind"]
    self.assertIn(
      kind,
      EXPECTED_NEXT_KIND_VALUES,
      f"next --json の kind '{kind}' は7値のいずれかであること。",
    )


class CommitPreflightKindBehaviorTests(unittest.TestCase):
  """commit-preflight --json がコミット関連 kind を返すことを確認"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _write_staged(self, relative_path, text):
    path = Path(self.tmpdir) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subprocess.run(
      ["git", "add", relative_path],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def _freeze_commit_unit(self, allowed_files):
    args = [
      "commit-unit", "freeze",
      "--work-unit-id", "unit-blocking-001",
      "--json",
    ]
    for f in allowed_files:
      args.extend(["--allowed-file", f])
    return run_script(args, cwd=self.tmpdir)

  def test_commit_preflight_returns_commit_unit_stale_when_stale(self):
    """stale commit unit 状態で commit-preflight --json が commit_unit_stale を返すこと"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_staged(target, "print('x')\n")
    self._freeze_commit_unit([target])
    self._write_staged(target, "print('changed')\n")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"],
      "commit_unit_stale",
      "commit-preflight --json は stale 状態で commit_unit_stale を返すこと。",
    )

  def test_commit_preflight_returns_commit_mixing_risk_when_mixing(self):
    """commit unit 混入状態で commit-preflight --json が commit_mixing_risk を返すこと"""
    self._write_staged("tools/check_workflow_action/blocking_unit.py", "print('x')\n")
    self._freeze_commit_unit(["tools/check_workflow_action/blocking_unit.py"])
    self._write_staged("docs/notes/working/other.md", "別作業\n")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"],
      "commit_mixing_risk",
      "commit-preflight --json は混入状態で commit_mixing_risk を返すこと。",
    )

  def test_commit_preflight_kind_is_always_commit_related(self):
    """commit-preflight --json が返す kind は常にコミット関連3値のいずれかであること"""
    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    self.assertIn(result.returncode, (0, 2), result.stderr)
    data = json.loads(result.stdout)
    kind = data.get("next_action", {}).get("kind")
    if kind is not None:
      self.assertIn(
        kind,
        EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES | {"post_write_verification", "unknown"},
        f"commit-preflight の kind '{kind}' は想定外の値。",
      )


class SchemaIfThenConstraintTests(unittest.TestCase):
  """next_action_response.schema.json の if/then 制約（受入 11(6) ①②③⑤）を確認

  先送り事項 (a)：MWP-0 T-020 完了条件 3。

  TDD 規律に従い、実装前にこのテストを作成した。
  実装前はすべて失敗状態（schema が制約を持たないためバリデーションを通過してしまう）。
  実装（if/then 追加）でテストをパスさせる。
  """

  REQUIRED_ACTION_SCHEMA = REPO_ROOT / ".reviewcompass" / "schema" / "required_action.schema.json"

  def _make_resolver(self):
    import jsonschema
    from jsonschema import RefResolver
    schema_dir = REPO_ROOT / ".reviewcompass" / "schema"
    store = {}
    for f in schema_dir.glob("*.schema.json"):
      with open(f) as fp:
        s = json.load(fp)
      if "$id" in s:
        store[s["$id"]] = s
    with open(NEXT_ACTION_SCHEMA) as fp:
      root_schema = json.load(fp)
    resolver = RefResolver.from_schema(root_schema, store=store)
    return root_schema, resolver

  def _minimal_valid_next_action(self, required_action, **overrides):
    """全必須フィールドを含む最小有効 next_action。条件に応じてフィールドを override できる"""
    base = {
      "kind": "in_progress",
      "required_action": required_action,
      "active_gate": None,
      "feature": None,
      "phase": None,
      "stage": None,
      "required_feature_scope": [],
      "blocked_by": None,
      "future_gates": [],
      "state_refs": {},
    }
    base.update(overrides)
    return base

  def _minimal_valid_response(self, next_action):
    return {
      "verdict": "OK",
      "exit_code": 0,
      "next_action": next_action,
      "reasons": [],
      "current_state": {},
    }

  def _assert_valid(self, schema, resolver, data, msg=""):
    import jsonschema
    try:
      jsonschema.validate(data, schema, resolver=resolver)
    except jsonschema.ValidationError as e:
      self.fail(f"期待していた有効データが schema 検証失敗: {e.message}. {msg}")

  def _assert_invalid(self, schema, resolver, data, msg=""):
    import jsonschema
    with self.assertRaises(
      jsonschema.ValidationError,
      msg=f"期待していた無効データが schema 検証を通過してしまった。{msg}",
    ):
      jsonschema.validate(data, schema, resolver=resolver)

  # ① commit_stop_point の制約
  def test_commit_stop_point_valid_when_all_null(self):
    """① commit_stop_point: active_gate/phase/stage がすべて null なら有効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate=None,
      phase=None,
      stage=None,
      blocked_by={"type": "commit_stop_point"},
    )
    self._assert_valid(schema, resolver, self._minimal_valid_response(na),
                       "commit_stop_point に全 null は有効であること")

  def test_commit_stop_point_invalid_when_active_gate_nonnull(self):
    """① commit_stop_point: active_gate が非 null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate="stages/implementation.yaml#drafting",
      phase=None,
      stage=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "commit_stop_point で active_gate が非 null は無効であること（受入 11(6)①）")

  def test_commit_stop_point_invalid_when_phase_nonnull(self):
    """① commit_stop_point: phase が非 null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate=None,
      phase="implementation",
      stage=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "commit_stop_point で phase が非 null は無効であること（受入 11(6)①）")

  def test_commit_stop_point_invalid_when_stage_nonnull(self):
    """① commit_stop_point: stage が非 null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate=None,
      phase=None,
      stage="drafting",
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "commit_stop_point で stage が非 null は無効であること（受入 11(6)①）")

  # ② run_reopen_pending_gate の制約
  def test_run_reopen_pending_gate_valid_with_nonnull_active_gate(self):
    """② run_reopen_pending_gate: active_gate が非 null なら有効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate",
      active_gate="stages/implementation.yaml#triad-review",
      phase="implementation",
      stage="triad-review",
      blocked_by=None,
    )
    self._assert_valid(schema, resolver, self._minimal_valid_response(na),
                       "run_reopen_pending_gate に non-null active_gate は有効であること")

  def test_run_reopen_pending_gate_invalid_when_active_gate_null(self):
    """② run_reopen_pending_gate: active_gate が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate",
      active_gate=None,
      phase=None,
      stage=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_pending_gate で active_gate=null は無効であること（受入 11(6)②）")

  def test_run_reopen_pending_gate_invalid_when_blocked_by_nonnull(self):
    """② run_reopen_pending_gate: blocked_by が非 null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate",
      active_gate="stages/implementation.yaml#triad-review",
      phase="implementation",
      stage="triad-review",
      blocked_by={"type": "some_blocker"},
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_pending_gate で blocked_by 非 null は無効であること（受入 11(6)②）")

  # ③ run_reopen_drafting の制約
  def test_run_reopen_drafting_valid_with_drafting_active_gate(self):
    """③ run_reopen_drafting: active_gate が stages/<phase>.yaml#drafting 形式なら有効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_drafting",
      active_gate="stages/implementation.yaml#drafting",
      phase="implementation",
      stage="drafting",
    )
    self._assert_valid(schema, resolver, self._minimal_valid_response(na),
                       "run_reopen_drafting に drafting 形式 active_gate は有効であること")

  def test_run_reopen_drafting_invalid_when_active_gate_not_drafting(self):
    """③ run_reopen_drafting: active_gate が drafting 形式でないなら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_drafting",
      active_gate="stages/implementation.yaml#triad-review",
      phase="implementation",
      stage="drafting",
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_drafting で active_gate が #drafting 形式でないは無効であること（受入 11(6)③）")

  def test_run_reopen_drafting_invalid_when_active_gate_null(self):
    """③ run_reopen_drafting: active_gate が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_drafting",
      active_gate=None,
      phase="implementation",
      stage="drafting",
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_drafting で active_gate=null は無効であること（受入 11(6)③）")

  # ⑤ wait_for_human_decision の制約
  def test_wait_for_human_decision_valid_with_blocked_by_type(self):
    """⑤ wait_for_human_decision: blocked_by に type フィールドがあれば有効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "wait_for_human_decision",
      blocked_by={"type": "reopen_approval_required"},
    )
    self._assert_valid(schema, resolver, self._minimal_valid_response(na),
                       "wait_for_human_decision に blocked_by.type あり は有効であること")

  def test_wait_for_human_decision_invalid_when_blocked_by_null(self):
    """⑤ wait_for_human_decision: blocked_by が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "wait_for_human_decision",
      blocked_by=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "wait_for_human_decision で blocked_by=null は無効であること（受入 11(6)⑤）")

  def test_wait_for_human_decision_invalid_when_blocked_by_lacks_type(self):
    """⑤ wait_for_human_decision: blocked_by に type フィールドがなければ無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "wait_for_human_decision",
      blocked_by={"reason": "some reason"},
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "wait_for_human_decision で blocked_by に type なしは無効であること（受入 11(6)⑤）")


if __name__ == "__main__":
  unittest.main()

