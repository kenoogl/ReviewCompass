"""実行時生成物 3 パスの凍結期挙動テスト（wm tasks T-004、3 パス × 5 観点）。

対象契約：workflow-management design §実行時生成物の凍結期（P3 まで）の扱い
- 書き込みは常に新配置（.reviewcompass/runtime/ 配下）
- 旧配置への新規書き込みなし（凍結。効力発生は P1 実装反映コミットと同時）
- 読み取りは新→旧の順のフォールバック（P3 まで）
- 新旧競合時は新配置を採用
- 凍結済み旧成果物の不変性（git 追跡履歴で検出、conformance-evaluation と同一判定規則）

TDD 規律（AGENTS.md）に従い、本テストは実装切替前に作成する。
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
GUARDED = REPO_ROOT / "tools" / "guarded-git-commit.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"

RUNTIME_LOG = ".reviewcompass/runtime/logs/workflow-precheck.log"
LEGACY_LOG = "docs/logs/workflow-precheck.log"
RUNTIME_PROMPT_DIR = ".reviewcompass/runtime/effective-prompts"
LEGACY_PROMPT_DIR = ".reviewcompass/effective-prompts"
RUNTIME_APPROVAL = ".reviewcompass/runtime/approvals/commit-approval.json"
LEGACY_APPROVAL = ".reviewcompass/approvals/commit-approval.json"


def _load_module(path: Path, name: str):
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(name, path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


cwa = _load_module(SCRIPT, "cwa_for_placement_tests")
guarded = _load_module(GUARDED, "guarded_for_placement_tests")
placement_freeze = _load_module(
  REPO_ROOT / "tools" / "check_workflow_action" / "placement_freeze.py",
  "placement_freeze_for_tests",
) if (REPO_ROOT / "tools" / "check_workflow_action" / "placement_freeze.py").exists() else None


def run_script(args, cwd):
  return subprocess.run(
    [sys.executable, str(SCRIPT), *args],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )


def _git(repo: Path, *args: str) -> str:
  result = subprocess.run(
    ["git", "-C", str(repo), *args],
    capture_output=True,
    text=True,
    check=True,
  )
  return result.stdout.strip()


def _git_commit_all(repo: Path, message: str) -> str:
  _git(repo, "add", "-A")
  _git(
    repo,
    "-c", "user.name=test",
    "-c", "user.email=test@example.com",
    "commit", "-m", message,
  )
  return _git(repo, "rev-parse", "HEAD")


def _write_approval(path: Path, marker: str, consumed: bool = False) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(
      {
        "approved_action": "commit",
        "approved_by": "user",
        "consumed": consumed,
        "rationale": marker,
        "target_files": [],
        "target_sha256": {},
        "execution_delegation": {
          "delegated_to": "llm",
          "approved_by": "user",
          "explicit_instruction": "コミット",
        },
      },
      ensure_ascii=False,
      indent=1,
    ),
    encoding="utf-8",
  )


class PrecheckLogPlacementTests(unittest.TestCase):
  """観点 1〜4：検査ログ"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_log_writes_to_runtime_placement_and_not_legacy(self):
    """観点 1・2：--log-path 省略時の既定が新配置で、旧配置に新規書き込みが発生しない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue((cwd / RUNTIME_LOG).is_file(), "新配置へログ追記されるべき")
    self.assertFalse((cwd / LEGACY_LOG).exists(), "旧配置へ新規書き込みしてはならない")

  def test_log_legacy_only_is_preserved_and_runtime_receives_appends(self):
    """観点 3：旧ログのみ存在しても旧は凍結のまま読め、追記は新配置へ行く"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("frozen-legacy-line\n", encoding="utf-8")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(
      legacy.read_text(encoding="utf-8"), "frozen-legacy-line\n",
      "凍結済み旧ログは変更されず読み取り可能であるべき",
    )
    self.assertTrue((cwd / RUNTIME_LOG).is_file())

  def test_log_conflict_appends_only_to_runtime(self):
    """観点 4：新旧両方が存在する競合時、追記は新配置のみ（新が現役の正）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("frozen-legacy-line\n", encoding="utf-8")
    runtime = cwd / RUNTIME_LOG
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime-existing-line\n", encoding="utf-8")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(legacy.read_text(encoding="utf-8"), "frozen-legacy-line\n")
    runtime_lines = runtime.read_text(encoding="utf-8").strip().splitlines()
    self.assertGreater(len(runtime_lines), 1, "新配置のログにのみ追記されるべき")


class PrecheckLogReadResolverTests(unittest.TestCase):
  """観点 3・4：検査ログの読み取り解決（M2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_log_read_falls_back_to_legacy(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy log\n", encoding="utf-8")
    from check_workflow_action.runtime_paths import resolve_precheck_log_read_path
    self.assertEqual(resolve_precheck_log_read_path(cwd), LEGACY_LOG)

  def test_log_read_conflict_prefers_runtime(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy log\n", encoding="utf-8")
    runtime = cwd / RUNTIME_LOG
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime log\n", encoding="utf-8")
    from check_workflow_action.runtime_paths import resolve_precheck_log_read_path
    self.assertEqual(resolve_precheck_log_read_path(cwd), RUNTIME_LOG)


class EffectivePromptPlacementTests(unittest.TestCase):
  """観点 1・3・4：effective prompt"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_effective_prompt_write_path_is_runtime(self):
    """観点 1：生成パスが新配置（runtime 区画）を指す"""
    relative = cwa._effective_prompt_relative_path(
      {"decision_point_refs": [{"group": "next_action_kind", "id": "stage"}]}
    )
    self.assertTrue(
      relative.startswith(RUNTIME_PROMPT_DIR + "/"),
      f"生成先は {RUNTIME_PROMPT_DIR}/ 配下であるべき: {relative}",
    )

  def test_effective_prompt_read_falls_back_to_legacy(self):
    """観点 3：新配置に無く旧配置にあるプロンプトは旧から読める"""
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{RUNTIME_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{LEGACY_PROMPT_DIR}/x.prompt.md")

  def test_effective_prompt_conflict_prefers_runtime(self):
    """観点 4：新旧両方にある場合は新配置を採用する"""
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    runtime = cwd / RUNTIME_PROMPT_DIR / "x.prompt.md"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{RUNTIME_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{RUNTIME_PROMPT_DIR}/x.prompt.md")


class EffectivePromptLegacyFormInputTests(unittest.TestCase):
  """N1：旧形式パス入力でも新→旧の順（新旧競合時は新を正）を適用する"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_legacy_form_input_prefers_runtime_when_both_exist(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    runtime = cwd / RUNTIME_PROMPT_DIR / "x.prompt.md"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{LEGACY_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{RUNTIME_PROMPT_DIR}/x.prompt.md")

  def test_legacy_form_input_returns_legacy_when_runtime_absent(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{LEGACY_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{LEGACY_PROMPT_DIR}/x.prompt.md")

  def test_absolute_path_is_returned_unchanged(self):
    cwd = Path(self.tmpdir)
    absolute = str(cwd / "somewhere" / "x.prompt.md")
    self.assertEqual(
      cwa.resolve_effective_prompt_read_path(cwd, absolute), absolute,
      "絶対パスは変換せずそのまま返すべき",
    )


class CommitApprovalPlacementTests(unittest.TestCase):
  """観点 1〜4：commit 承認記録"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_commit_approval_read_falls_back_to_legacy(self):
    """観点 3：新配置に無い場合は旧配置の承認記録を読む"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    state, errors = cwa.validate_commit_approval(cwd, [])
    self.assertTrue(state["exists"], errors)
    self.assertEqual(state["path"], LEGACY_APPROVAL)

  def test_commit_approval_conflict_prefers_runtime(self):
    """観点 4：新旧両方にある場合は新配置の記録を正とする"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    _write_approval(cwd / RUNTIME_APPROVAL, "runtime-record")
    state, _ = cwa.validate_commit_approval(cwd, [])
    self.assertTrue(state["exists"])
    self.assertEqual(state["path"], RUNTIME_APPROVAL)

  def test_consume_writes_to_runtime_even_when_record_is_legacy(self):
    """観点 1・2：消費（書き込み）は常に新配置へ行き、凍結済み旧記録は変更しない"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    legacy_before = (cwd / LEGACY_APPROVAL).read_text(encoding="utf-8")
    guarded.consume_commit_approval(cwd)
    runtime_path = cwd / RUNTIME_APPROVAL
    self.assertTrue(runtime_path.is_file(), "消費済み記録は新配置へ書かれるべき")
    consumed = json.loads(runtime_path.read_text(encoding="utf-8"))
    self.assertTrue(consumed["consumed"])
    self.assertEqual(
      (cwd / LEGACY_APPROVAL).read_text(encoding="utf-8"), legacy_before,
      "凍結済み旧記録へ書き込んではならない",
    )


class RuntimePlacementFreezeCheckerTests(unittest.TestCase):
  """観点 5：凍結済み旧成果物の不変性（git 追跡履歴判定、ce と同一規則）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_checker_module_exists(self):
    self.assertIsNotNone(
      placement_freeze,
      "tools/check_workflow_action/placement_freeze.py が存在するべき",
    )

  def test_frozen_set_is_not_a_violation(self):
    cwd = Path(self.tmpdir)
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen\n", encoding="utf-8")
    (cwd / LEGACY_PROMPT_DIR).mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("frozen\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [])

  def test_changes_deletions_and_additions_are_violations(self):
    cwd = Path(self.tmpdir)
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen\n", encoding="utf-8")
    (cwd / LEGACY_PROMPT_DIR).mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("frozen\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")

    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("edited\n", encoding="utf-8")
    (cwd / LEGACY_LOG).unlink()
    (cwd / LEGACY_PROMPT_DIR / "new.prompt.md").write_text("violation\n", encoding="utf-8")

    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertTrue(any("x.prompt.md" in v and "frozen_file_changed" in v for v in violations))
    self.assertTrue(
      any("workflow-precheck.log" in v and "deleted_after_freeze" in v for v in violations),
      f"削除は専用種別 deleted_after_freeze で報告されるべき: {violations}",
    )
    self.assertTrue(any("new.prompt.md" in v and "added_after_freeze" in v for v in violations))

  def test_ignored_preexisting_legacy_artifacts_are_not_violations(self):
    """gitignore 対象として現存する旧成果物（凍結済み・未追跡）は誤検知しない（K3）"""
    cwd = Path(self.tmpdir)
    (cwd / ".gitignore").write_text(
      "docs/logs/workflow-precheck.log\n.reviewcompass/approvals/commit-approval.json\n",
      encoding="utf-8",
    )
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen ignored log\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen ignored approval")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [], "ignore された既存旧成果物を違反としてはならない")

  def test_approvals_freeze_scope_is_limited_to_commit_approval_record(self):
    """approvals の凍結対象は契約どおり commit-approval.json 単体に限定する（K4）"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    other = cwd / ".reviewcompass" / "approvals" / "unrelated-record.json"
    other.write_text("{}\n", encoding="utf-8")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [], "契約対象外のファイルを凍結違反としてはならない")


class RunRoleEffectivePromptFallbackTests(unittest.TestCase):
  """K1：effective prompt フォールバックの実運用読み取り経路（run_role の sha 解決）への接続"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_sha_resolution_falls_back_to_legacy_prompt(self):
    import hashlib
    import os
    sys.path.insert(0, str(REPO_ROOT))
    from tools.api_providers import run_role
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt body\n", encoding="utf-8")
    previous = os.getcwd()
    os.chdir(cwd)
    try:
      resolved = run_role._resolve_effective_prompt_sha256(
        f"{RUNTIME_PROMPT_DIR}/x.prompt.md", None
      )
    finally:
      os.chdir(previous)
    expected = hashlib.sha256(legacy.read_bytes()).hexdigest()
    self.assertEqual(resolved, expected, "新配置に無い場合は旧配置のプロンプトから sha を計算するべき")


if __name__ == "__main__":
  unittest.main()
