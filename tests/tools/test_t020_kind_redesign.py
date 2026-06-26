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


if __name__ == "__main__":
  unittest.main()
