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
        EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES,
        f"commit-preflight の kind '{kind}' は想定外の値。commit-preflight は {sorted(EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES)} の3値のみ返すこと（受入 12）。",
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

  def test_commit_stop_point_invalid_when_blocked_by_null(self):
    """① commit_stop_point: blocked_by が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate=None,
      phase=None,
      stage=None,
      blocked_by=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "commit_stop_point で blocked_by=null は無効であること（受入 11(6)①）")

  def test_commit_stop_point_invalid_when_blocked_by_type_differs(self):
    """① commit_stop_point: blocked_by.type が commit_stop_point 以外なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "commit_stop_point",
      active_gate=None,
      phase=None,
      stage=None,
      blocked_by={"type": "some_blocker"},
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "commit_stop_point で blocked_by.type 不一致は無効であること（受入 11(6)①）")

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

  def test_run_reopen_pending_gate_invalid_when_phase_null(self):
    """② run_reopen_pending_gate: phase が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate",
      active_gate="stages/implementation.yaml#triad-review",
      phase=None,
      stage="triad-review",
      blocked_by=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_pending_gate で phase=null は無効であること（受入 11(6)②）")

  def test_run_reopen_pending_gate_invalid_when_stage_null(self):
    """② run_reopen_pending_gate: stage が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_pending_gate",
      active_gate="stages/implementation.yaml#triad-review",
      phase="implementation",
      stage=None,
      blocked_by=None,
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_pending_gate で stage=null は無効であること（受入 11(6)②）")

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

  def test_run_reopen_drafting_invalid_when_phase_null(self):
    """③ run_reopen_drafting: phase が null なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_drafting",
      active_gate="stages/implementation.yaml#drafting",
      phase=None,
      stage="drafting",
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_drafting で phase=null は無効であること（受入 11(6)③）")

  def test_run_reopen_drafting_invalid_when_stage_is_not_drafting(self):
    """③ run_reopen_drafting: stage が drafting 以外なら無効"""
    schema, resolver = self._make_resolver()
    na = self._minimal_valid_next_action(
      "run_reopen_drafting",
      active_gate="stages/implementation.yaml#drafting",
      phase="implementation",
      stage="triad-review",
    )
    self._assert_invalid(schema, resolver, self._minimal_valid_response(na),
                         "run_reopen_drafting で stage が drafting 以外は無効であること（受入 11(6)③）")

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


class ReasonVsReasonsContractTests(unittest.TestCase):
  """T-020 先送り事項(b): next_action.reason と最上位 reasons の責務差を確認"""

  DESIGN_DOC = REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "design.md"

  def _load_schema(self):
    with open(NEXT_ACTION_SCHEMA, encoding="utf-8") as f:
      return json.load(f)

  def test_next_action_reason_is_defined_as_human_readable_optional_field(self):
    """next_action.reason は人間向け説明として定義され、必須 10 フィールドには含めない"""
    schema = self._load_schema()
    next_action = schema["properties"]["next_action"]
    properties = next_action["properties"]
    self.assertIn(
      "reason",
      properties,
      "next_action.reason は設計 §5.3 の全 kind 共通フィールドとして schema に定義すること。",
    )
    self.assertEqual(
      properties["reason"].get("type"),
      "string",
      "next_action.reason は人間向けの状態説明文字列であること。",
    )
    self.assertIn(
      "人間",
      properties["reason"].get("$comment", ""),
      "next_action.reason の $comment は人間向け説明であることを明示すること。",
    )
    self.assertNotIn(
      "reason",
      next_action.get("required", []),
      "next_action.reason は §5.2 の必須 10 フィールドには含めず、任意フィールドとして扱うこと。",
    )

  def test_top_level_reasons_schema_documents_machine_readable_verdict_reasons(self):
    """最上位 reasons は verdict の根拠配列として next_action.reason と区別する"""
    schema = self._load_schema()
    reasons = schema["properties"]["reasons"]
    self.assertEqual(
      reasons.get("type"),
      "array",
      "最上位 reasons は配列であること。",
    )
    self.assertEqual(
      reasons.get("items", {}).get("type"),
      "string",
      "最上位 reasons は検査・判定理由の文字列配列であること。",
    )
    comment = reasons.get("$comment", "")
    self.assertIn(
      "verdict",
      comment,
      "最上位 reasons の $comment は verdict の根拠であることを明示すること。",
    )
    self.assertIn(
      "next_action.reason",
      comment,
      "最上位 reasons の $comment は next_action.reason との責務差を明示すること。",
    )

  def test_design_documents_reason_vs_reasons_responsibility_difference(self):
    """設計書 §5.2/§5.3 は reason と reasons の責務差を明示する"""
    text = self.DESIGN_DOC.read_text(encoding="utf-8")
    self.assertIn(
      "next_action.reason と最上位 reasons の責務差",
      text,
      "設計書に T-020 先送り事項(b) の責務差説明を追加すること。",
    )
    self.assertIn(
      "verdict",
      text,
      "最上位 reasons が verdict の根拠であることを設計書で説明すること。",
    )
    self.assertIn(
      "人間向け",
      text,
      "next_action.reason が人間向け説明であることを設計書で説明すること。",
    )


if __name__ == "__main__":
  unittest.main()
