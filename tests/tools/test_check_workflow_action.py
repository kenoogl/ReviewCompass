"""ワークフロー事前検査スクリプト tools/check-workflow-action.py の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md
対象範囲：spec-set サブコマンド（範囲案 2 のうち、MVP 第 1 ラウンドで先行実装）

TDD 規律（CLAUDE.md 全体規律）に従い、本テストはスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_check_workflow_action -v
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"


def run_script(args, cwd):
  """check-workflow-action.py をサブプロセスで実行して結果を返す"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def _assert_script_invoked(testcase, result):
  """スクリプトが実際に起動したことを確認する厳密性確保のヘルパー

  Python はスクリプトファイルが存在しないとき exit 2 を返す。これは仕様 §7.1 の
  逸脱判定 exit 2 と一致するため、判定だけでは「スクリプト未実装」と
  「正当な逸脱検出」を区別できない。本ヘルパーは stderr にファイルなし
  エラーが含まれないことを確認することで両者を区別し、実装前の偶然通過を
  防ぐ。実装完了後は無効化されない（実害なく動作し続ける）。
  """
  for marker in ("No such file or directory", "can't open file"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"スクリプトが起動できていない（実装前の状態か）。stderr: {result.stderr}",
    )


class SpecSetExitCodeTests(unittest.TestCase):
  """spec-set サブコマンドの終了コード判定

  仕様 §6.1 spec-set の判定ロジック、§7.1 終了コード体系を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    """fixture を一時ディレクトリにコピーしてそのパスを返す"""
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_approval_with_alignment_true_returns_zero(self):
    """ケース A：requirements の前段がすべて true、approval を true にする → exit 0

    仕様 §6.1 段の依存チェック：alignment=true なら approval=true に進める
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"alignment=true なので approval=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_approval_with_alignment_false_returns_two(self):
    """ケース B：alignment が false で approval を true にする → exit 2

    仕様 §6.1 段の依存チェック：alignment=false なら approval=true は逸脱
    """
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"alignment=false なので approval=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_design_drafting_with_requirements_approved_returns_zero(self):
    """ケース C：requirements.approval=true で design.drafting=true にする → exit 0

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=true なら次フェーズの drafting に進める
    """
    cwd = self._copy_fixture("case-c-approved")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"requirements.approval=true なので design.drafting=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_design_drafting_with_requirements_not_approved_returns_two(self):
    """ケース D：requirements.approval=false で design.drafting=true にする → exit 2

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=false なら次フェーズの drafting は逸脱
    """
    cwd = self._copy_fixture("case-d-design-blocked")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"requirements.approval=false なので design.drafting=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_setting_true_stage_to_false_returns_one(self):
    """ケース E：現状 true の段を false に戻す → exit 1（reopen 警告）

    仕様 §6.1 new-value が false の場合：当該段が true だったら reopen 警告
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 1,
      f"true → false は reopen 警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )


class SpecSetOutputTests(unittest.TestCase):
  """spec-set サブコマンドの出力形式

  仕様 §7.2 人間可読出力、§7.3 JSON 出力を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_deviation_output_contains_verdict_keyword(self):
    """逸脱出力に [VERDICT] DEVIATION が含まれる（仕様 §7.2）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱時の出力に DEVIATION の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )

  def test_ok_output_contains_verdict_keyword(self):
    """通過出力に [VERDICT] OK が含まれる（仕様 §7.2）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "OK", result.stdout,
      f"通過時の出力に OK の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )

  def test_json_output_with_flag_for_ok(self):
    """--json で OK 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["exit_code"], 0)
    self.assertIn("action", data)
    self.assertIn("current_state", data)

  def test_json_output_with_flag_for_deviation(self):
    """--json で DEVIATION 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["exit_code"], 2)
    self.assertGreater(
      len(data["reasons"]), 0,
      "逸脱時は reasons に 1 件以上の理由が含まれるべき",
    )


class SpecSetLoggingTests(unittest.TestCase):
  """ログ取得（MVP 必須、仕様 §8）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_log_file_is_appended_after_invocation(self):
    """スクリプト実行後にログファイルが追記される（仕様 §8.1 JSON Lines 形式）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    self.assertFalse(log_path.exists(), "事前にログファイルは存在しない前提")
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    self.assertTrue(
      log_path.exists(),
      "スクリプト実行後にログファイルが作成されるべき",
    )
    log_content = log_path.read_text()
    self.assertGreater(
      len(log_content.strip()), 0,
      "ログに 1 行以上記録されるべき",
    )
    log_entry = json.loads(log_content.strip().splitlines()[0])
    self.assertIn("timestamp", log_entry)
    self.assertIn("action", log_entry)
    self.assertIn("verdict", log_entry)
    self.assertIn("exit_code", log_entry)

  def test_rationale_is_recorded_in_log(self):
    """spec-set で --rationale を渡すとログに記録される（仕様 §5.1）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    rationale = "利用者承認「ア」によりテストとして起動"
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--rationale", rationale,
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    log_entry = json.loads(log_path.read_text().strip().splitlines()[0])
    self.assertEqual(
      log_entry["action"]["args"]["rationale"], rationale,
      "ログの action.args.rationale に渡した値が記録されるべき",
    )


class SpecSetArgumentValidationTests(unittest.TestCase):
  """引数妥当性の検査（仕様 §5.1）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_invalid_feature_name_returns_nonzero(self):
    """存在しない機能名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "nonexistent-feature", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しない feature は判定不能で非 0 終了すべき",
    )

  def test_invalid_phase_returns_nonzero(self):
    """無効なフェーズ名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "nonexistent-phase", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しないフェーズは判定不能で非 0 終了すべき",
    )

  def test_invalid_value_returns_nonzero(self):
    """true／false 以外の値 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "maybe"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "true／false 以外の値は引数エラーで非 0 終了すべき",
    )


def _init_git_repo(tmpdir):
  """temp dir に git リポジトリを初期化し、初回コミットと .reviewcompass 構造を準備する

  commit／push サブコマンドのテスト用ヘルパー。
  """
  for cmd in [
    ["git", "init", "-q", "-b", "main"],
    ["git", "config", "user.email", "test@example.com"],
    ["git", "config", "user.name", "Test User"],
    ["git", "config", "commit.gpgsign", "false"],
  ]:
    subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
  # 初回コミット（空でないリポジトリにする）
  (Path(tmpdir) / ".gitignore").write_text("")
  subprocess.run(
    ["git", "add", ".gitignore"], cwd=str(tmpdir), check=True, capture_output=True
  )
  subprocess.run(
    ["git", "commit", "-qm", "initial"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # .reviewcompass 構造を準備（pending ファイルの土台）
  pending_dir = Path(tmpdir) / ".reviewcompass"
  pending_dir.mkdir()
  pending_file = pending_dir / "pending-cross-feature-findings.md"
  pending_file.write_text("# 機能横断レビューで扱う所見の集約\n")
  return pending_file


def _set_pending_findings(pending_file, unresolved_count=0, resolved_count=0):
  """pending ファイルに未消化／対処済み所見を設定する"""
  lines = ["# 機能横断レビューで扱う所見の集約\n"]
  for i in range(unresolved_count):
    lines.append(f"\n### A-{i+1:03d}：テスト用未消化所見\n")
    lines.append("詳細内容...\n")
  for i in range(resolved_count):
    n = unresolved_count + i + 1
    lines.append(f"\n### A-{n:03d}：テスト用対処済み所見 ✅ 対処済み（2026-05-25）\n")
    lines.append("詳細内容...\n")
  pending_file.write_text("".join(lines))


def _stage_file(tmpdir, relpath, content):
  """ファイルを作成して git add 状態にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


class CommitExitCodeTests(unittest.TestCase):
  """commit サブコマンドの終了コード判定（仕様 §6.2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_with_no_pending_and_normal_changes_returns_zero(self):
    """未消化所見 0 件 + 通常変更のみ → exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_script(
      ["commit", "--rationale", "テスト用 commit、利用者承認の出典あり"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"未消化所見なし＋通常変更のみは通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_pending_findings_returns_one(self):
    """未消化所見 1 件以上 → exit 1（警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=1)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_script(
      ["commit", "--rationale", "未消化所見ありの場面のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"未消化所見ありは警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "WARN", result.stdout,
      f"警告判定の出力に WARN が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_with_spec_json_change_returns_one(self):
    """spec.json の変更含む → exit 1（要注意変更の警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      ".reviewcompass/specs/foundation/spec.json",
      '{"feature_name":"foundation"}',
    )
    result = run_script(
      ["commit", "--rationale", "spec.json 更新のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"spec.json 変更は要注意変更として警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_plan_doc_change_returns_one(self):
    """計画書（docs/plan/ 配下）の変更含む → exit 1"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "docs/plan/test-plan.md", "# テスト計画")
    result = run_script(
      ["commit", "--rationale", "計画書追加のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"docs/plan/ 配下の変更は要注意で警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_credential_file_returns_two(self):
    """ファイル名に credentials を含む変更 → exit 2（危険変更）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "credentials.json", '{"key":"dummy"}')
    result = run_script(
      ["commit", "--rationale", "credentials を含むファイルのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"credentials を含むファイル名は危険変更として逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_rationale_is_required(self):
    """commit に --rationale なし → 非 0 終了（仕様 §5.2 必須）"""
    _stage_file(self.tmpdir, "notes.md", "test")
    result = run_script(["commit"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class PushExitCodeTests(unittest.TestCase):
  """push サブコマンドの終了コード判定（仕様 §6.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_push_with_clean_tree_returns_zero(self):
    """作業ツリーが clean → exit 0"""
    result = run_script(
      ["push", "--rationale", "clean な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"作業ツリー clean は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_push_with_dirty_tree_returns_two(self):
    """作業ツリーが dirty（未追跡ファイルあり）→ exit 2"""
    (Path(self.tmpdir) / "untracked.md").write_text("# 未追跡")
    result = run_script(
      ["push", "--rationale", "dirty な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"作業ツリー dirty は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_push_rationale_is_required(self):
    """push に --rationale なし → 非 0 終了（仕様 §5.3 必須）"""
    result = run_script(["push"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class CommitPushOutputTests(unittest.TestCase):
  """commit／push の JSON 出力検査（仕様 §7.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_json_output(self):
    """commit に --json で JSON 出力に切り替わる"""
    result = run_script(
      ["commit", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "commit",
      "JSON 出力の action.subcommand は 'commit' であるべき",
    )

  def test_push_json_output(self):
    """push に --json で JSON 出力に切り替わる"""
    result = run_script(
      ["push", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "push",
      "JSON 出力の action.subcommand は 'push' であるべき",
    )


if __name__ == "__main__":
  unittest.main()
