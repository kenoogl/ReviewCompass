"""ワークフロー事前検査スクリプト tools/check-workflow-action.py の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md
対象範囲：spec-set サブコマンド（範囲案 2 のうち、MVP 第 1 ラウンドで先行実装）

TDD 規律（AGENTS.md 入口規律）に従い、本テストはスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_check_workflow_action -v
"""

import json
import hashlib
import importlib
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from tools.api_providers.review_triage import write_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"

FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def run_script(args, cwd):
  """check-workflow-action.py をサブプロセスで実行して結果を返す"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def _write_spec(cwd, feature, implementation_state):
  """next サブコマンド用の最小 spec.json を作る"""
  spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
  spec_dir.mkdir(parents=True, exist_ok=True)
  complete_five_stage = {
    "drafting": True,
    "triad-review": True,
    "review-wave": True,
    "alignment": True,
    "approval": True,
  }
  workflow_state = {
    "intent": {
      "drafting": True,
      "review": True,
      "approval": True,
      "reference": "stages/intent.yaml",
    },
    "feature-partitioning": {
      "candidate-proposal": True,
      "approval": True,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    },
    "requirements": dict(complete_five_stage),
    "design": dict(complete_five_stage),
    "tasks": dict(complete_five_stage),
    "implementation": dict(implementation_state),
  }
  spec = {
    "feature_name": feature,
    "language": "ja",
    "created_at": "2026-06-02T00:00:00+09:00",
    "updated_at": "2026-06-02T00:00:00+09:00",
    "workflow_state": workflow_state,
    "reopened": {},
    "recheck": {
      "upstream_change_pending": False,
      "impacted_downstream_phases": [],
    },
  }
  (spec_dir / "spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )


def _write_specs_for_next(cwd, states_by_feature):
  """指定されない feature は implementation 未着手として spec.json を作る"""
  untouched = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  _write_feature_dependency(
    cwd,
    "stages/feature-dependency.yaml",
    feature_order=list(FEATURE_ORDER),
  )
  for feature in FEATURE_ORDER:
    _write_spec(cwd, feature, states_by_feature.get(feature, untouched))


def _write_phase_artifact(cwd, relative_path, text, timestamp):
  """phase 成果物を指定時刻で作る"""
  path = Path(cwd) / relative_path
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")
  os.utime(path, (timestamp, timestamp))


def _write_completed_phase_artifacts(cwd, timestamp=1000):
  """next 再展開検査用の完了済み成果物一式を作る"""
  _write_phase_artifact(cwd, "intent/INTENT.md", "intent\n", timestamp)
  _write_phase_artifact(
    cwd,
    "stages/feature-partitioning/2026-05-24-proposal.md",
    "feature partitioning\n",
    timestamp,
  )
  for feature in FEATURE_ORDER:
    for phase in ("requirements", "design", "tasks"):
      _write_phase_artifact(
        cwd,
        f".reviewcompass/specs/{feature}/{phase}.md",
        f"{feature} {phase}\n",
        timestamp,
      )
    _write_phase_artifact(
      cwd,
      f".reviewcompass/specs/{feature}/implementation-drafting.md",
      f"{feature} implementation drafting\n",
      timestamp,
    )


def _write_post_write_manifest(cwd, manifest_name, content):
  """post-write-verification manifest を作る"""
  manifest_dir = Path(cwd) / ".reviewcompass" / "post-write-verification"
  manifest_dir.mkdir(parents=True, exist_ok=True)
  (manifest_dir / manifest_name).write_text(
    yaml.safe_dump(content, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path):
  """ファイル内容の sha256 を返す"""
  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _staged_sha256_file(cwd, path):
  """staged blob 内容の sha256 を返す"""
  result = subprocess.run(
    ["git", "show", f":{path}"],
    cwd=str(cwd),
    check=True,
    capture_output=True,
  )
  return hashlib.sha256(result.stdout).hexdigest()


def _write_review_run(cwd, run_id, models, omit_summary=False, omit_triage_model=None):
  """post-write review run の最小成果物を作る"""
  run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)

  target = Path(cwd) / "docs" / "notes" / "review-target.md"
  target.parent.mkdir(parents=True, exist_ok=True)
  if not target.exists():
    target.write_text("レビュー対象\n", encoding="utf-8")

  model_results = []
  triage_items = []
  summary_models = []
  for model in models:
    raw_path = raw_dir / f"{model}.round-1.txt"
    raw_path.write_text(f"{model} raw response\n", encoding="utf-8")
    raw_sha = _sha256_file(raw_path)
    model_results.append({
      "model_id": model,
      "provider": f"{model}-provider",
      "role": model,
      "treatment": model,
      "invocation_path": "api",
      "raw_path": f"raw/{model}.round-1.txt",
      "raw_sha256": raw_sha,
      "parsed_path": None,
      "parsed_sha256": None,
      "parse_status": "parse_failed",
      "follow_up_action": "triage",
    })
    if model != omit_triage_model:
      triage_items.append({
        "finding_id": f"{run_id}-{model}-001",
        "source_model": model,
        "source_round": f"{run_id}-round-1",
        "source_raw_path": f"raw/{model}.round-1.txt",
        "source_parsed_path": None,
        "severity_original": "INFO",
        "severity_normalized": "INFO",
        "final_label": "leave-as-is",
        "decision_status": "decided",
        "target_location": "docs/notes/review-target.md",
        "plain_language_summary": "問題なし。",
        "decision_reason": "テスト用の完了記録。",
        "applied_files": [],
        "superseded_by": None,
      })
    summary_models.append({
      "model_id": model,
      "raw_path": f"raw/{model}.round-1.txt",
      "parse_status": "parse_failed",
      "triage_status": "triaged",
      "findings_count": 1,
      "must_fix_count": 0,
      "should_fix_count": 0,
      "leave_as_is_count": 1,
      "human_required_count": 0,
    })

  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "round_id": f"{run_id}-round-1",
        "purpose": "post_write_verification",
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
          },
        ],
        "model_results": model_results,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "items": triage_items,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  if not omit_summary:
    (run_dir / "model-result-summary.yaml").write_text(
      yaml.safe_dump(
        {
          "run_id": run_id,
          "models": summary_models,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

  return run_dir


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


def _write_autonomous_parallel_plan(cwd, overrides=None):
  """自律・並列モード実行計画の最小正常形を作る"""
  overrides = overrides or {}
  run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / "ap-001-review"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)
  raw_path = raw_dir / "gpt-5.4.round-1.txt"
  raw_path.write_text("raw response\n", encoding="utf-8")
  raw_sha = _sha256_file(raw_path)
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "model_results": [
          {
            "model_id": "gpt-5.4",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "raw_sha256": raw_sha,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "triage_status": "decided",
        "items": [
          {
            "finding_id": "finding-a",
            "decision_status": "decided",
            "source_raw_path": "raw/gpt-5.4.round-1.txt",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  plan = {
    "mode": "autonomous_parallel",
    "run_id": "ap-001",
    "authorization": {
      "approved_by": "user",
      "approval_record_path": "docs/notes/approval.md",
      "summary_presented_to_user": True,
      "triage_presented_to_user": True,
    },
    "tasks": [
      {
        "task_id": "task-a",
        "source_finding_ids": ["finding-a"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/a.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_a.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      },
      {
        "task_id": "task-b",
        "source_finding_ids": ["finding-b"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/b.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_b.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      },
    ],
    "execution_evidence": {
      "review_run_dir": "docs/notes/review-runs/ap-001-review",
      "required_raw_paths": ["raw/gpt-5.4.round-1.txt"],
      "triage_path": "triage.yaml",
      "require_no_human_required": True,
    },
    "integration_gate": {
      "requires_main_session_review": True,
      "requires_diff_scope_check": True,
      "requires_tests": True,
      "requires_decision_basis_review": True,
    },
    "history": {
      "ledger_path": "docs/logs/autonomous-parallel/ap-001.yaml",
      "record_task_assignments": True,
      "record_decision_basis": True,
      "record_integration_result": True,
      "retention": "preserve",
    },
    "outputs_policy": {
      "implementation_diff": "commit_candidate",
      "verification_summary": "required",
      "decision_basis": "preserve_if_used",
      "work_noise": "exclude",
    },
  }
  for key, value in overrides.items():
    if value is None:
      plan.pop(key, None)
    else:
      plan[key] = value

  path = Path(cwd) / "autonomous-parallel-plan.yaml"
  path.write_text(
    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


class AutonomousParallelPlanTests(unittest.TestCase):
  """自律・並列モード実行計画の機械ガード"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_valid_plan_returns_zero(self):
    """正常な実行計画は OK になる"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["task_count"], 2)

  def test_valid_plan_writes_history_ledger(self):
    """正常な実行計画は後追い用の履歴台帳を書き出す"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    self.assertTrue(ledger_path.exists())
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["run_id"], "ap-001")
    self.assertEqual(ledger["verdict"], "OK")
    self.assertEqual(ledger["task_ids"], ["task-a", "task-b"])
    self.assertEqual(ledger["history"]["record_decision_basis"], True)

  def test_missing_authorization_returns_two(self):
    """人間または proxy_model の承認記録がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"authorization": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("authorization", "\n".join(data["reasons"]))

  def test_subthread_without_separate_worktree_returns_two(self):
    """別スレッド実装が分離 worktree でなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][0]["assignee"]["worktree_policy"] = "same_repo_write"
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("separate_worktree", "\n".join(data["reasons"]))

  def test_overlapping_parallel_paths_returns_two(self):
    """依存関係のない並列タスクが同じパスを書く場合は逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][1]["allowed_paths"] = ["src/a.py"]
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("allowed_paths", "\n".join(data["reasons"]))

  def test_missing_execution_evidence_returns_two(self):
    """raw/triage 証跡への参照がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"execution_evidence": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("execution_evidence", "\n".join(data["reasons"]))

  def test_missing_required_raw_path_returns_two(self):
    """required_raw_paths の raw が欠けていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    (cwd / "docs" / "notes" / "review-runs" / "ap-001-review" / "raw" / "gpt-5.4.round-1.txt").unlink()

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("required_raw_paths", "\n".join(data["reasons"]))

  def test_human_required_triage_returns_two(self):
    """未判断 triage item が残っていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    triage_path = cwd / "docs" / "notes" / "review-runs" / "ap-001-review" / "triage.yaml"
    triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
    triage["items"][0]["decision_status"] = "human_required"
    triage_path.write_text(
      yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("human_required", "\n".join(data["reasons"]))

  def test_main_session_parallel_writer_requires_output_only_boundary(self):
    """main_session/same_worktree の並列タスクは出力専用でなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][0]["assignee"] = {
      "kind": "main_session",
      "worktree_policy": "same_worktree",
    }
    plan["tasks"][0]["writes_repo_diff"] = True
    plan["tasks"][0]["output_only"] = False
    plan["outputs_policy"]["implementation_diff"] = "forbidden"
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("output_only", "\n".join(data["reasons"]))

  def test_main_session_same_worktree_commit_candidate_writer_is_allowed_when_serialized(self):
    """commit_candidate の直列 main_session 実装タスクは履歴付きで許可する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    for index, task in enumerate(plan["tasks"]):
      task["assignee"] = {
        "kind": "main_session",
        "worktree_policy": "same_worktree",
      }
      task["writes_repo_diff"] = True
      task["output_only"] = False
      if index > 0:
        task["depends_on"] = [plan["tasks"][index - 1]["task_id"]]
    plan["execution_evidence"] = {
      "completed_tasks": ["task-a", "task-b"],
      "parallelized_operations": ["context_reads", "verification_checks"],
      "human_required_count": 0,
    }
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["execution_evidence"]["human_required_count"], 0)

  def test_missing_integration_gate_returns_two(self):
    """統合ゲートが不足していれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {
        "integration_gate": {
          "requires_main_session_review": True,
          "requires_diff_scope_check": True,
          "requires_tests": True,
        },
      },
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("requires_decision_basis_review", "\n".join(data["reasons"]))

  def test_missing_history_returns_two(self):
    """履歴保存設定がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"history": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("history", "\n".join(data["reasons"]))

  def test_template_command_writes_valid_autonomous_plan(self):
    """テンプレート生成コマンドはそのまま検査可能な実行計画を書く"""
    cwd = Path(self.tmpdir)
    out_path = cwd / "plan.yaml"

    result = run_script(
      [
        "autonomous-plan-template",
        "--run-id", "ap-template-001",
        "--out", str(out_path),
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(out_path.exists())

    plan = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    self.assertEqual(plan["mode"], "autonomous_parallel")
    self.assertEqual(plan["run_id"], "ap-template-001")
    self.assertEqual(
      plan["history"]["ledger_path"],
      "docs/logs/autonomous-parallel/ap-template-001.yaml",
    )

    check = run_script(["autonomous-plan", str(out_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

  def test_record_integration_updates_history_ledger(self):
    """統合結果記録コマンドは既存台帳に統合結果を追記する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["integration_result"]["status"], "completed")
    self.assertEqual(
      ledger["integration_result"]["decision"],
      "main_session accepted scoped diff",
    )
    self.assertEqual(
      ledger["integration_result"]["tests"],
      "python3 -m unittest tests.tools.test_check_workflow_action -v",
    )
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["completed_tasks"],
      ["task-a", "task-b"],
    )

  def test_autonomous_plan_preserves_existing_integration_result(self):
    """autonomous-plan 再実行は既存の統合結果を消さない"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)

    recheck = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, recheck)
    self.assertEqual(recheck.returncode, 0, recheck.stderr)
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["integration_result"]["status"], "completed")
    self.assertEqual(
      ledger["integration_result"]["decision"],
      "main_session accepted scoped diff",
    )

  def test_autonomous_plan_preserves_existing_execution_evidence_snapshot(self):
    """autonomous-plan 再実行は実行後証跡 snapshot を巻き戻さない"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"].append(
      {
        "task_id": "task-c",
        "source_finding_ids": ["finding-c"],
        "assignee": {
          "kind": "main_session",
          "worktree_policy": "same_worktree",
        },
        "allowed_paths": ["src/c.py"],
        "forbidden_paths": [".git/"],
        "depends_on": ["task-b"],
        "expected_tests": ["pytest tests/test_c.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      }
    )
    plan["execution_evidence"] = {
      "completed_tasks": ["task-a", "task-b", "task-c"],
      "parallelized_operations": ["context_reads", "ledger_audit"],
      "human_required_count": 0,
    }
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    stale_plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    stale_plan["execution_evidence"]["completed_tasks"] = ["task-a", "task-b"]
    stale_plan["execution_evidence"]["parallelized_operations"] = ["context_reads"]
    plan_path.write_text(
      yaml.safe_dump(stale_plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    recheck = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, recheck)
    self.assertEqual(recheck.returncode, 0, recheck.stderr)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["completed_tasks"],
      ["task-a", "task-b", "task-c"],
    )
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["parallelized_operations"],
      ["context_reads", "ledger_audit"],
    )

  def test_autonomous_ledger_audit_passes_without_plan_file(self):
    """デプロイ後監査は plan なしで ledger 単独から判定する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan_path.unlink()

    audit = run_script(["autonomous-ledger-audit", str(ledger_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, audit)
    self.assertEqual(audit.returncode, 0, audit.stderr)
    data = json.loads(audit.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["plan_required"], False)

  def test_autonomous_ledger_audit_requires_execution_snapshot(self):
    """台帳単独監査は実行後 snapshot が欠けていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(
      yaml.safe_dump(
        {
          "run_id": "ap-001",
          "mode": "autonomous_parallel",
          "verdict": "OK",
          "exit_code": 0,
          "task_ids": ["task-a"],
          "integration_result": {
            "status": "completed",
            "tests": "pytest",
            "decision": "accepted",
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    audit = run_script(["autonomous-ledger-audit", str(ledger_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, audit)
    self.assertEqual(audit.returncode, 2)
    data = json.loads(audit.stdout)
    self.assertIn("execution_evidence_snapshot", "\n".join(data["reasons"]))


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

  def test_spec_set_blocks_when_in_progress_file_exists(self):
    """stages/in-progress が非空なら spec-set は不可逆操作として exit 2"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_spec_set_allows_reopen_pending_gate_rollback(self):
    """reopen 第1過程の pending gate 差し戻しは in-progress 中でも許可する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-09.yaml").write_text(
      "process_id: reopen-procedure\n"
      "step_number: 1\n"
      "next_step: 第1過程：判定とフラグ差し戻し\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("reopen", result.stdout)

  def test_spec_set_allows_reopen_pending_gate_completion(self):
    """reopen 第3過程の pending gate 完了は in-progress 中でも許可する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-09.yaml").write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_unimplemented_completion_predicate(self):
    """file_exists completion_predicate の対象ファイルがなければ true にしない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": {
                "type": "file_exists",
                "path": "docs/approvals/requirements.md",
              },
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("completion_predicate", result.stdout)

  def test_spec_set_allows_file_exists_completion_predicate_when_file_exists(self):
    """file_exists completion_predicate の対象ファイルがあれば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("承認証跡\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": {
                "type": "file_exists",
                "path": "docs/approvals/requirements.md",
              },
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_artifact_exists_when_artifact_missing(self):
    """artifact_exists は証跡ファイル欠落時に true 化を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "completion_predicate": "artifact_exists",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("artifact_exists", result.stdout)

  def test_spec_set_allows_artifact_exists_when_artifact_exists(self):
    """artifact_exists は証跡ファイル存在時に通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("承認証跡\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "completion_predicate": "artifact_exists",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_sections_predicate_when_section_missing(self):
    """artifact_exists_and_sections_present は必須節欠落時に遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("# Introduction\n\n本文\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "required_sections": ["Introduction", "Decision"],
              "completion_predicate": "artifact_exists_and_sections_present",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("Decision", result.stdout)

  def test_spec_set_allows_sections_predicate_when_sections_present(self):
    """artifact_exists_and_sections_present は証跡と必須節が揃えば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text(
      "# Introduction\n\n本文\n\n## Decision\n\n承認\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "required_sections": ["Introduction", "Decision"],
              "completion_predicate": "artifact_exists_and_sections_present",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_author_reviewer_predicate_when_identity_matches(self):
    """author/reviewer 異名述語は同一 identity を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    review_path = (
      cwd / ".reviewcompass" / "specs" / "foundation" / "reviews"
      / "2026-06-04-requirements-triad-review.md"
    )
    review_path.parent.mkdir(parents=True)
    review_path.write_text(
      "---\n"
      "author:\n"
      "  identity: main-session\n"
      "reviewer:\n"
      "  identity: main-session\n"
      "  separation_from_author: false\n"
      "---\n"
      "# 主役レビュー\n\n# 敵対役レビュー\n\n# 判定役レビュー\n\n# 統合\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": [
                ".reviewcompass/specs/{feature}/reviews/*-requirements-triad-review.md",
              ],
              "required_sections": [
                "主役レビュー",
                "敵対役レビュー",
                "判定役レビュー",
                "統合",
              ],
              "completion_predicate": (
                "artifact_exists_and_sections_present_and_author_reviewer_distinct"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("author.identity", result.stdout)

  def test_spec_set_allows_author_reviewer_predicate_when_identity_distinct(self):
    """author/reviewer 異名述語は異なる identity なら通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    review_path = (
      cwd / ".reviewcompass" / "specs" / "foundation" / "reviews"
      / "2026-06-04-requirements-triad-review.md"
    )
    review_path.parent.mkdir(parents=True)
    review_path.write_text(
      "---\n"
      "author:\n"
      "  identity: main-session\n"
      "reviewer:\n"
      "  identity: independent-reviewer\n"
      "  separation_from_author: true\n"
      "---\n"
      "# 主役レビュー\n\n# 敵対役レビュー\n\n# 判定役レビュー\n\n# 統合\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": [
                ".reviewcompass/specs/{feature}/reviews/*-requirements-triad-review.md",
              ],
              "required_sections": [
                "主役レビュー",
                "敵対役レビュー",
                "判定役レビュー",
                "統合",
              ],
              "completion_predicate": (
                "artifact_exists_and_sections_present_and_author_reviewer_distinct"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_all_features_predicate_when_feature_incomplete(self):
    """全機能 drafting/triad-review 述語は未完了 feature があれば遮断する"""
    cwd = Path(self.tmpdir) / "all-features-incomplete"
    cwd.mkdir()
    _write_specs_for_next(cwd, {})
    spec_path = cwd / ".reviewcompass" / "specs" / "runtime" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["workflow_state"]["requirements"]["triad-review"] = False
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "review-wave",
              "completion_predicate": (
                "all_features_drafting_and_triad_review_completed"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "review-wave", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("runtime.requirements.triad-review", result.stdout)

  def test_spec_set_allows_all_features_predicate_when_features_complete(self):
    """全機能 drafting/triad-review 述語は全 feature 完了時に通過する"""
    cwd = Path(self.tmpdir) / "all-features-complete"
    cwd.mkdir()
    _write_specs_for_next(cwd, {})
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "review-wave",
              "completion_predicate": (
                "all_features_drafting_and_triad_review_completed"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "review-wave", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_alignment_predicate_when_unresolved_findings_exist(self):
    """cross_spec_alignment_passed は未消化所見があれば遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    report_path = cwd / "docs" / "alignment" / "requirements.yaml"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
      yaml.safe_dump(
        {"status": "pass", "unresolved_findings": 1},
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "alignment",
              "artifact_paths": ["docs/alignment/requirements.yaml"],
              "completion_predicate": "cross_spec_alignment_passed",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("未消化所見 0 件", result.stdout)

  def test_spec_set_allows_alignment_predicate_when_passed(self):
    """cross_spec_alignment_passed は pass かつ未消化所見 0 件なら通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    report_path = cwd / "docs" / "alignment" / "requirements.yaml"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
      yaml.safe_dump(
        {"status": "pass", "unresolved_findings": 0},
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "alignment",
              "artifact_paths": ["docs/alignment/requirements.yaml"],
              "completion_predicate": "cross_spec_alignment_passed",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_human_approval_predicate_when_record_missing(self):
    """explicit_human_approval_recorded は承認証跡欠落時に遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "approval_record_path": "docs/approvals/requirements.yaml",
              "completion_predicate": "explicit_human_approval_recorded",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("承認証跡", result.stdout)

  def test_spec_set_allows_human_approval_predicate_when_record_exists(self):
    """explicit_human_approval_recorded は承認証跡があれば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.yaml"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("approved_by: user\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "approval_record_path": "docs/approvals/requirements.yaml",
              "completion_predicate": "explicit_human_approval_recorded",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_depends_on_predicate_when_kind_invalid(self):
    """depends_on_resolves_correctly は不正な依存種別を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "feature-dependency.yaml").write_text(
      yaml.safe_dump(
        {"features": {"runtime": {"depends_on": {"foundation": "optional"}}}},
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": "depends_on_resolves_correctly",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("hard または review", result.stdout)

  def test_spec_set_allows_depends_on_predicate_when_kind_valid(self):
    """depends_on_resolves_correctly は list/object の正しい依存構造を通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "feature-dependency.yaml").write_text(
      yaml.safe_dump(
        {
          "features": {
            "foundation": {"depends_on": []},
            "runtime": {"depends_on": {"foundation": "hard"}},
            "evaluation": {"depends_on": ["runtime"]},
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": "depends_on_resolves_correctly",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

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

  def test_setting_impacted_recheck_phase_to_true_returns_two(self):
    """recheck pending の影響対象 phase は spec-set true で完了扱いにできない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"] = {
      "upstream_change_pending": True,
      "impacted_downstream_phases": ["requirements"],
    }
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("recheck", result.stdout)

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

  def test_setting_upstream_stage_to_false_with_downstream_true_returns_one(self):
    """上流段を false に戻す時、下流段が true のままでも reopen 警告に留める"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["workflow_state"]["requirements"]["approval"] = True
    spec["workflow_state"]["design"]["drafting"] = True
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("reopen", result.stdout)


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


class NextNavigationTests(unittest.TestCase):
  """next サブコマンドのワークフローナビゲーション判定"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_returns_evaluation_implementation_drafting_after_runtime_triad_review(self):
    """runtime triad-review 完了後は evaluation implementation drafting を返す"""
    cwd = Path(self.tmpdir)
    runtime_done = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    foundation_done = dict(runtime_done)
    _write_specs_for_next(
      cwd,
      {
        "foundation": foundation_done,
        "runtime": runtime_done,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "evaluation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertIn(
      "docs/operations/WORKFLOW_NAVIGATION.md",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      "docs/disciplines/discipline_workflow_state_truth_source.md",
      data["next_action"]["required_disciplines"],
    )

  def test_next_completed_from_external_app_root_fixture(self):
    """ReviewCompass repo 外の対象 app root でも completed を判定できる"""
    cwd = Path(self.tmpdir) / "external-app"
    cwd.mkdir()
    done = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(
      cwd,
      {feature: done for feature in FEATURE_ORDER},
    )
    _write_completed_phase_artifacts(cwd)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "completed")
    self.assertEqual(data["next_action"]["reason"], "すべての workflow_state が完了しています")
    self.assertFalse((REPO_ROOT / ".reviewcompass" / "specs" / "external-app").exists())

  def test_next_detects_intent_update_requires_reopen_classification(self):
    """完了済み workflow で intent が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      "intent/INTENT.md",
      "intent updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["phase"], "feature-partitioning")
    self.assertEqual(data["next_action"]["stage"], "candidate-proposal")
    self.assertEqual(data["next_action"]["upstream_phase"], "intent")
    self.assertEqual(data["next_action"]["reopen_trigger"], "N-0")
    self.assertEqual(
      data["next_action"]["reason"],
      "完了済み workflow で intent 成果物が feature-partitioning 成果物より新しいため、reopen 分類が必要です",
    )

  def test_next_detects_requirements_update_requires_reopen_classification(self):
    """完了済み workflow で requirements が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      ".reviewcompass/specs/foundation/requirements.md",
      "foundation requirements updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "design")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(data["next_action"]["upstream_phase"], "requirements")
    self.assertEqual(data["next_action"]["reopen_trigger"], "R-0")

  def test_next_does_not_redetect_completed_feature_partitioning_reopen(self):
    """完了済み reopen が同じ feature-partitioning→requirements を覆うなら再要求しない"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      "stages/feature-partitioning/2026-05-24-proposal.md",
      "feature partitioning updated\n",
      timestamp=2000,
    )
    completed = cwd / "stages" / "completed" / "reopen-procedure-2026-06-09.yaml"
    completed.parent.mkdir(parents=True, exist_ok=True)
    completed.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "next_step: （完了。再オープン手続き終了）\n"
      "current_blocker: null\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: requirements alignment を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"],
      "reopen_classification_required",
      data["next_action"],
    )

  def test_next_detects_tasks_update_requires_reopen_classification(self):
    """完了済み workflow で tasks が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      ".reviewcompass/specs/foundation/tasks.md",
      "foundation tasks updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(data["next_action"]["upstream_phase"], "tasks")
    self.assertEqual(data["next_action"]["reopen_trigger"], "A-0")

  def test_next_triad_review_reports_review_run_disciplines(self):
    """triad-review 直前に読むべき review-run/proxy 規律を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(
      cwd,
      {
        "foundation": {
          "drafting": True,
          "triad-review": False,
          "review-wave": False,
          "alignment": False,
          "approval": False,
        },
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    self.assertIn(
      "docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      data["next_action"]["required_disciplines"],
    )
    self.assertEqual(
      data["next_action"]["effective_prompt"]["effective_prompt_policy"],
      "one_effective_prompt_per_decision_point",
    )
    self.assertIn(
      {"group": "next_action_kind", "id": "stage"},
      data["next_action"]["effective_prompt"]["decision_point_refs"],
    )
    self.assertIn(
      {"group": "workflow_stage", "id": "triad-review"},
      data["next_action"]["effective_prompt"]["decision_point_refs"],
    )
    self.assertIn(
      "docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      data["next_action"]["effective_prompt"]["prompt_source_refs"],
    )
    prompt_path = cwd / data["next_action"]["effective_prompt"]["effective_prompt_path"]
    self.assertTrue(prompt_path.is_file())
    self.assertEqual(
      data["next_action"]["effective_prompt"]["effective_prompt_sha256"],
      _sha256_file(prompt_path),
    )
    self.assertTrue(
      data["next_action"]["effective_prompt"]["effective_prompt_loaded"],
    )
    prompt_text = prompt_path.read_text(encoding="utf-8")
    self.assertIn("# Effective Prompt", prompt_text)
    self.assertIn("docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2", prompt_text)

  def test_next_fails_closed_when_effective_prompt_source_is_missing(self):
    """effective prompt の元資料が読めない判定点は fail-closed とする"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    map_path = cwd / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(
      yaml.safe_dump(
        {
          "default": ["docs/operations/WORKFLOW_NAVIGATION.md"],
          "decision_points": {
            "next_action_kind": [
              {
                "id": "stage",
                "prompt_source_refs": ["docs/missing-effective-prompt-source.md"],
                "effective_prompt_policy": "one_effective_prompt_per_decision_point",
              }
            ]
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(
      data["next_action"]["effective_prompt"]["effective_prompt_loaded"],
    )
    self.assertIn(
      "effective prompt の元資料をすべて読めません",
      data["reasons"],
    )

  def test_next_triad_review_reports_target_and_review_run_inputs(self):
    """triad-review 直前に読む対象文書と review-run 成果物を抽象入力として返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(
      cwd,
      {
        "foundation": {
          "drafting": True,
          "triad-review": False,
          "review-wave": False,
          "alignment": False,
          "approval": False,
        },
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    required_inputs = {
      item["id"]: item
      for item in data["next_action"]["required_inputs"]
    }
    self.assertEqual(
      required_inputs["target_feature_documents"]["paths"],
      [
        ".reviewcompass/specs/foundation/spec.json",
        ".reviewcompass/specs/foundation/requirements.md",
        ".reviewcompass/specs/foundation/design.md",
        ".reviewcompass/specs/foundation/tasks.md",
      ],
    )
    self.assertEqual(
      required_inputs["triad_review_run_artifacts"]["base_path_pattern"],
      ".reviewcompass/specs/foundation/reviews/*-foundation-implementation-review-run",
    )
    self.assertEqual(
      required_inputs["triad_review_run_artifacts"]["required_artifacts"],
      [
        "review-target.md",
        "raw/",
        "rounds.yaml",
        "model-result-summary.yaml",
        "triage.yaml",
        "raw-review-triage-summary.md",
        "variant-role-assignment",
        "user-visible-triage-gate",
      ],
    )

  def test_next_review_wave_reports_recheck_and_pending_findings(self):
    """review-wave では recheck と抽象入力としての未消化所見情報を返す"""
    cwd = Path(self.tmpdir)
    implementation_ready = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    _write_specs_for_next(
      cwd,
      {feature: dict(implementation_ready) for feature in FEATURE_ORDER},
    )
    foundation_spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    foundation_spec = json.loads(foundation_spec_path.read_text(encoding="utf-8"))
    foundation_spec["recheck"] = {
      "upstream_change_pending": True,
      "impacted_downstream_phases": ["implementation"],
    }
    foundation_spec_path.write_text(
      json.dumps(foundation_spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    pending_path = (
      cwd / "learning" / "workflow" / "carry-forward-register" / "sources"
      / "reviewcompass-pending-cross-feature-findings.md"
    )
    pending_path.parent.mkdir(parents=True)
    pending_path.write_text(
      "# 機能横断レビューで扱う所見の集約\n\n"
      "### A-001：未消化の波及所見\n",
      encoding="utf-8",
    )
    register_path = (
      cwd / "learning" / "workflow" / "carry-forward-register" / "reviewcompass-import.yaml"
    )
    register_path.parent.mkdir(parents=True, exist_ok=True)
    register_path.write_text(
      yaml.safe_dump(
        {
          "register_id": "carry-forward-register",
          "schema_version": 1,
          "source_type": "carry_forward_register",
          "items": [
            {
              "item_id": "carry-forward-001",
              "scope": "cross_scope",
              "source_feature": "foundation",
              "target_feature_or_phase": ["runtime"],
              "finding_summary": "未消化の波及所見",
              "status": "open",
              "decision_needed": False,
              "decision_reasons": [],
              "carry_forward_reason": "review-wave で消化する",
              "resolution": None,
              "evidence_refs": [],
              "project_local_context": {"legacy_id": "A-001"},
            }
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "cross_feature_stage")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "review-wave")
    self.assertEqual(
      data["next_action"]["recheck_items"],
      [
        {
          "feature": "foundation",
          "impacted_downstream_phases": ["implementation"],
        }
      ],
    )
    self.assertEqual(
      data["next_action"]["pending_cross_feature_findings"]["unresolved_count"],
      1,
    )
    self.assertEqual(
      data["next_action"]["pending_cross_feature_findings"]["file"],
      "learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md",
    )
    self.assertNotIn(
      ".reviewcompass/pending-cross-feature-findings.md",
      data["next_action"]["required_disciplines"],
    )
    required_inputs = {
      item["id"]: item
      for item in data["next_action"]["required_inputs"]
    }
    self.assertEqual(
      required_inputs["cross_feature_stage_artifacts"]["path"],
      ".reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md",
    )
    self.assertEqual(
      required_inputs["unresolved_cross_scope_items"],
      {
        "id": "unresolved_cross_scope_items",
        "role": "stage_entry_context",
        "source_type": "carry_forward_register",
        "purpose": (
          "Read unresolved items carried forward from prior reviews or "
          "adjacent scopes before starting this stage."
        ),
        "read_policy": "unresolved_items_only",
        "path": "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
        "unresolved_count": 1,
      },
    )

  def test_next_prioritizes_in_progress_file(self):
    """進行中ファイルがあれば新規作業ではなく resume を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process-2026-06-02.yaml").write_text(
      "process_id: manual-process\n"
      "next_step: 第3過程：連鎖再実施\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "resume_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/manual-process-2026-06-02.yaml",
    )

  def test_next_reads_maintenance_in_progress(self):
    """maintenance の進行中ファイルがあれば通常ワークフローより優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "reason: Codex 稼働前に Claude 前提の入口記述を整理する\n"
      "required_action: inspect_remaining_claude_assumptions\n"
      "blocked_normal_workflow: true\n"
      "mainline_blocked_by: conformance-evaluation feature-partitioning confirmation\n"
      "allowed_scope:\n"
      "  - docs/operations/\n"
      "  - TODO_NEXT_SESSION.md\n"
      "allowed_files:\n"
      "  - docs/operations/WORKFLOW_NAVIGATION.md\n"
      "  - TODO_NEXT_SESSION.md\n"
      "completion_conditions:\n"
      "  - Codex 新規セッションで TODO から開始できる\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "maintenance_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml",
    )
    self.assertEqual(data["next_action"]["process_id"], "maintenance")
    self.assertEqual(data["next_action"]["title"], "Codex adapter migration")
    self.assertTrue(data["next_action"]["blocked_normal_workflow"])
    self.assertEqual(
      data["next_action"]["mainline_blocked_by"],
      "conformance-evaluation feature-partitioning confirmation",
    )
    self.assertEqual(
      data["next_action"]["allowed_scope"],
      ["docs/operations/", "TODO_NEXT_SESSION.md"],
    )
    self.assertEqual(
      data["next_action"]["allowed_files"],
      ["docs/operations/WORKFLOW_NAVIGATION.md", "TODO_NEXT_SESSION.md"],
    )
    self.assertEqual(
      data["next_action"]["completion_conditions"],
      ["Codex 新規セッションで TODO から開始できる"],
    )
    self.assertEqual(data["next_action"]["required_action"], "run_maintenance")
    self.assertIsNone(data["next_action"]["active_gate"])
    self.assertIsNone(data["next_action"]["feature"])
    self.assertIsNone(data["next_action"]["phase"])
    self.assertIsNone(data["next_action"]["stage"])
    self.assertEqual(
      data["next_action"]["maintenance_action"],
      "inspect_remaining_claude_assumptions",
    )

  def test_next_prioritizes_post_write_over_maintenance(self):
    """maintenance 中でも書き込み後検証対象があれば post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "required_action: inspect_remaining_claude_assumptions\n",
      encoding="utf-8",
    )
    target = cwd / "docs" / "notes" / "codex-maintenance.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("maintenance 中の検証対象文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/notes/codex-maintenance.md"],
    )
    self.assertIn(
      "docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      "docs/disciplines/discipline_post_write_verification.md",
      data["next_action"]["required_disciplines"],
    )
    self.assertEqual(
      data["current_state"]["in_progress_files"],
      ["stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml"],
    )

  def test_next_reads_reopen_in_progress_next_step(self):
    """reopen の進行中ファイルから next_step と required_action を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "started_at: 2026-06-02T00:00:00+09:00\n"
      "completed_steps: [\"第1過程：判定とフラグ差し戻し\", \"第2過程：正本修正\"]\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["process_id"], "reopen-procedure")
    self.assertEqual(data["next_action"]["next_step"], "第3過程：連鎖再実施")
    self.assertEqual(data["next_action"]["required_action"], "run_reopen_pending_gate")
    self.assertEqual(data["next_action"]["next_pending_gate"], "stages/requirements.yaml#alignment")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "alignment")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      ["stages/requirements.yaml#alignment", "stages/requirements.yaml#approval"],
    )

  def test_next_reopen_prefers_step_number_over_next_step_text(self):
    """reopen は next_step の表記ゆれより step_number を優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第三工程：表記ゆれ\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["step_number"], 3)
    self.assertEqual(data["next_action"]["required_action"], "run_reopen_pending_gate")
    self.assertEqual(data["next_action"]["next_pending_gate"], "stages/requirements.yaml#alignment")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "alignment")

  def test_next_reopen_commit_stop_point_blocks_pending_gate(self):
    """reopen 停止点では pending_gates が残っても commit_stop_point だけを返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-16.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "commit_stop_point")
    self.assertIsNone(action["active_gate"])
    self.assertIsNone(action["next_pending_gate"])
    self.assertIsNone(action["phase"])
    self.assertIsNone(action["stage"])
    self.assertEqual(action["blocked_by"]["type"], "commit_stop_point")

  def test_next_reopen_reports_first_pending_gate_as_unique_task(self):
    """reopen 第3過程は drafting 完了後に pending_gates 先頭を次タスクとして返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "  - stages/requirements.yaml#review-wave\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "drafting_completed_gates:\n"
      "  - stages/requirements.yaml#drafting\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(
      data["next_action"]["next_pending_gate"],
      "stages/requirements.yaml#triad-review",
    )
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    self.assertEqual(
      data["next_action"]["required_action"],
      "run_reopen_pending_gate",
    )
    self.assertEqual(
      data["next_action"]["active_gate"],
      "stages/requirements.yaml#triad-review",
    )
    self.assertIsNone(data["next_action"]["blocked_by"])

  def test_next_reopen_requires_drafting_before_triad_review(self):
    """reopen 第3過程は triad-review の前に phase drafting を一意に返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/design.yaml#triad-review\n"
      "  - stages/design.yaml#review-wave\n"
      "  - stages/design.yaml#alignment\n"
      "  - stages/design.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "run_reopen_drafting")
    self.assertEqual(action["next_pending_gate"], "stages/design.yaml#triad-review")
    self.assertEqual(action["next_drafting_gate"], "stages/design.yaml#drafting")
    self.assertEqual(action["active_gate"], "stages/design.yaml#drafting")
    self.assertEqual(action["phase"], "design")
    self.assertEqual(action["stage"], "drafting")
    required_inputs = {
      item["id"]: item
      for item in action["required_inputs"]
    }
    self.assertEqual(
      required_inputs["reopen_procedure_state"]["paths"],
      ["stages/in-progress/reopen-procedure-2026-06-02.yaml"],
    )

  def test_next_reopen_uses_feature_impact_decisions_as_review_scope(self):
    """reopen のレビュー対象 feature は feature_impact_decisions から機械的に返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "feature:\n"
      "  - conformance-evaluation\n"
      "  - workflow-management\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "current_blocker: null\n"
      "feature_impact_decisions:\n"
      "  - feature: conformance-evaluation\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: direct\n"
      "    evidence: [intent/INTENT.md]\n"
      "  - feature: workflow-management\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: contract_ownership\n"
      "    rationale: direct\n"
      "    evidence: [docs/operations/REOPEN_PROCEDURE.md]\n"
      "  - feature: foundation\n"
      "    decision: indirect_check_only\n"
      "    impact_basis: consumer_or_derivative_only\n"
      "    rationale: indirect\n"
      "    evidence: [.reviewcompass/specs/foundation/requirements.md]\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(
      action["required_feature_scope"],
      ["foundation", "workflow-management", "conformance-evaluation"],
    )
    self.assertEqual(
      action["direct_features"],
      ["workflow-management", "conformance-evaluation"],
    )
    self.assertEqual(action["indirect_features"], ["foundation"])
    required_inputs = {
      item["id"]: item
      for item in action["required_inputs"]
    }
    self.assertEqual(
      required_inputs["target_feature_documents"]["paths"],
      [
        ".reviewcompass/specs/foundation/spec.json",
        ".reviewcompass/specs/foundation/requirements.md",
        ".reviewcompass/specs/foundation/design.md",
        ".reviewcompass/specs/foundation/tasks.md",
        ".reviewcompass/specs/workflow-management/spec.json",
        ".reviewcompass/specs/workflow-management/requirements.md",
        ".reviewcompass/specs/workflow-management/design.md",
        ".reviewcompass/specs/workflow-management/tasks.md",
        ".reviewcompass/specs/conformance-evaluation/spec.json",
        ".reviewcompass/specs/conformance-evaluation/requirements.md",
        ".reviewcompass/specs/conformance-evaluation/design.md",
        ".reviewcompass/specs/conformance-evaluation/tasks.md",
      ],
    )

  def test_next_reopen_human_blocker_requires_wait(self):
    """reopen の current_blocker があれば人間承認待ちを返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: stages/requirements.yaml#approval（人間承認待ち）\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["required_action"], "wait_for_human_decision")
    self.assertIsNone(data["next_action"]["active_gate"])
    self.assertIsNone(data["next_action"]["next_pending_gate"])
    self.assertIsNone(data["next_action"]["phase"])
    self.assertIsNone(data["next_action"]["stage"])
    self.assertEqual(data["next_action"]["blocked_by"]["type"], "current_blocker")
    self.assertEqual(
      data["next_action"]["current_blocker"],
      "stages/requirements.yaml#approval（人間承認待ち）",
    )

  def test_next_reopen_structured_blocker_requires_wait(self):
    """構造化された reopen blocker も承認待ちとして返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker:\n"
      "  blocker_type: approval_gate\n"
      "  gate: stages/requirements.yaml#approval\n"
      "  actor: human\n"
      "  status: waiting_for_approval\n"
      "  rationale: approval gate に到達した。\n"
      "  evidence:\n"
      "    - .reviewcompass/specs/workflow-management/requirements.md\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertIsNone(action["active_gate"])
    self.assertIsNone(action["next_pending_gate"])
    self.assertIsNone(action["phase"])
    self.assertIsNone(action["stage"])
    self.assertEqual(action["blocked_by"]["type"], "current_blocker")
    self.assertEqual(
      action["current_blocker"]["gate"],
      "stages/requirements.yaml#approval",
    )
    self.assertEqual(action["current_blocker"]["actor"], "human")
    self.assertEqual(action["current_blocker"]["status"], "waiting_for_approval")

  def test_next_prioritizes_post_write_verification_for_target_doc_changes(self):
    """対象 docs 文書の未コミット変更があれば post-write-verification を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_routes_working_notes_to_lightweight_self_check(self):
    """docs/notes/working 配下だけなら API post-write ではなく軽量自己精査を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "working" / "memo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("作業中メモ\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "lightweight_self_check")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/working/memo.md"])
    self.assertEqual(
      data["next_action"]["required_action"],
      "review_working_note_without_api",
    )

  def test_next_keeps_regular_notes_as_post_write_targets(self):
    """docs/notes 直下は混在配置なので従来どおり post-write 対象にする"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "memo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("通常メモ\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/memo.md"])

  def test_next_prioritizes_strict_post_write_when_mixed_with_working_notes(self):
    """軽量メモと strict 対象が混ざる場合は strict post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    working = cwd / "docs" / "notes" / "working" / "memo.md"
    strict = cwd / "TODO_NEXT_SESSION.md"
    working.parent.mkdir(parents=True, exist_ok=True)
    working.write_text("作業中メモ\n", encoding="utf-8")
    strict.write_text("# TODO\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["TODO_NEXT_SESSION.md"])
    self.assertEqual(
      data["current_state"]["lightweight_self_check_targets"],
      ["docs/notes/working/memo.md"],
    )

  def test_next_post_write_verification_target_matrix(self):
    """規律で定義された post-write-verification 対象だけを検出する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_paths = [
      "TODO_NEXT_SESSION.md",
      "docs/experiments/foo.md",
      "docs/notes/foo.md",
      "docs/operations/foo.md",
      "docs/plan/foo.md",
      "docs/reviews/2026-06-02-audit-foo.md",
      "docs/reviews/reopen-classification-2026-06-02.md",
      "docs/workflow-evidence/future-generated.yaml",
    ]
    non_target_paths = [
      ".reviewcompass/specs/foundation/spec.json",
      "docs/archive/foo.md",
      "docs/reviews/2026-06-02-impl-triad-review.md",
      "docs/reviews/audit-summary.md",
      # (い) 機械が吐く捕捉物はディレクトリ単位で対象外（走行・再実行・再生成で担保）
      "docs/logs/autonomous-parallel/run.yaml",
      "docs/notes/review-runs/r1/raw/gemini.round-1.txt",
      "docs/notes/post-write-verification-review/result-google-r1.yaml",
    ]
    for path in target_paths + non_target_paths:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], sorted(target_paths))

  def test_next_excludes_own_precheck_log_from_post_write_targets(self):
    """ツール自身の実行ログ（docs/logs/workflow-precheck.log）は post-write 対象にしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    for path in ["docs/logs/workflow-precheck.log", "docs/notes/foo.md"]:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/foo.md"])

  def test_next_with_only_precheck_log_change_skips_post_write(self):
    """実行ログ単独の未コミット変更では post-write 判定にしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    log_path = cwd / "docs" / "logs" / "workflow-precheck.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("log\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertNotEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_uses_completed_post_write_manifest_to_return_to_workflow(self):
    """完了 manifest が対象ファイルを覆う場合は通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "foundation")

  def test_next_does_not_report_policy_violation_after_manifest_completion(self):
    """完了 manifest がある場合は pending 中の禁止混在として扱わない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 検証完了後の通常実装変更\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")

  def test_next_does_not_complete_manifest_after_target_content_changes(self):
    """manifest 作成後に対象ファイルが変わった場合は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    target.write_text("検証後に追記された正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_does_not_complete_manifest_with_empty_required_verifiers(self):
    """required_verifiers が空の manifest は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証者未指定の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "required_verifiers": [],
        "completed_verifiers": [],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_requires_human_decision_for_unresolved_substantive_findings(self):
    """manifest に未解決の本質的指摘があれば人間判断待ちを返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("本質的指摘ありの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_uses_latest_post_write_manifest_when_multiple_exist(self):
    """同一対象の manifest が複数ある場合はファイル名が新しいものを優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("複数 manifest の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-002.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(
      data["next_action"]["manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-02-002.yaml",
    )

  def test_next_deviation_when_new_runner_created_during_post_write_verification(self):
    """post-write-verification pending 中の新規 runner 作成は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 独自検証 runner\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["tools/post_write_verify_new_policy.py"],
    )

  def test_next_deviation_when_template_changes_during_post_write_verification(self):
    """post-write-verification pending 中の template 変更は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    template = cwd / "templates" / "todo" / "TODO_NEXT_SESSION.template.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("再発防止としてのテンプレート変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["templates/todo/TODO_NEXT_SESSION.template.md"],
    )

  def test_next_deviation_when_discipline_change_is_mixed_with_other_post_write_target(self):
    """post-write-verification pending 中に規律変更が混ざる場合は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("越境した規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_allows_discipline_post_write_when_it_is_the_only_target(self):
    """規律ファイル単独の変更は post-write-verification 対象として扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("正式手続き後の規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_ignores_workflow_stage_spec_changes_for_post_write_verification(self):
    """.reviewcompass/specs 配下は post-write-verification ではなく通常 workflow で扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    spec_doc = cwd / ".reviewcompass" / "specs" / "foundation" / "requirements.md"
    spec_doc.write_text("ワークフロー段で検証される文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertNotEqual(data["next_action"]["kind"], "post_write_verification")


class PostWriteCoverageMatrixTests(unittest.TestCase):
  """manifest の verifications[] による coverage matrix チェック"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_with_full_coverage_and_matching_sha256(self):
    """verifications[] で全検証者が全ファイルを見て sha256 も一致した manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"全検証者が全ファイルを見て sha256 一致の manifest は通常ワークフローに戻るべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_verifications_lack_per_entry_sha256(self):
    """verifications[] に per-entry target_sha256 がない manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            # target_sha256 が意図的に欠落
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] 内の per-entry target_sha256 が欠落した manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_entry_sha256_mismatches_master(self):
    """verifications[] の sha256 がマスターと不一致の場合は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": "deadbeef" * 8,  # 不正な sha256
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] エントリの sha256 がマスターと不一致の manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_covers_only_partial_files(self):
    """分業（検証者ごとに異なるファイルのみ）の manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-b.md"],
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "分業（各検証者が全ファイルを見ていない）は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      f"分業の manifest は post_write_verification を継続すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_falls_back_to_completed_verifiers_without_verifications_field(self):
    """verifications[] がない旧形式 manifest は completed_verifiers でフォールバック判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "legacy-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("旧形式の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/legacy-policy.md"],
        "target_sha256": {
          "docs/notes/legacy-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] なし旧形式は completed_verifiers で完了判定し通常ワークフローに戻るべき",
    )


class PostWriteReviewRunTraceabilityTests(unittest.TestCase):
  """review_run 宣言付き manifest の raw/rounds/triage/summary 機械検査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_manifest_for_review_run(self, cwd, run_id):
    changed_targets = ["docs/notes/review-target.md"]
    run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
    for path in sorted(run_dir.rglob("*")):
      if path.is_file():
        changed_targets.append(str(path.relative_to(cwd)))
    models = ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"]
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": changed_targets,
        "target_sha256": {
          path: _sha256_file(Path(cwd) / path)
          for path in changed_targets
        },
        "required_verifiers": models,
        "completed_verifiers": models,
        "unresolved_substantive_findings": 0,
        "review_run": {
          "path": f"docs/notes/review-runs/{run_id}",
          "summary_path": f"docs/notes/review-runs/{run_id}/model-result-summary.yaml",
        },
      },
    )

  def test_next_accepts_manifest_when_review_run_traceability_is_complete(self):
    """raw、rounds、triage、summary が全モデル分そろう manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "traceability-complete"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_run の raw/rounds/triage/summary がそろう manifest は完了すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_review_summary_is_missing(self):
    """summary artifact がない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-summary"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_summary=True,
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "モデル別 summary artifact がない review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_required_model_raw_is_missing(self):
    """required_verifiers の raw が欠ける review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-raw"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    (run_dir / "raw" / "gpt-5.4.round-1.txt").unlink()
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "required_verifiers の raw ファイルが欠ける review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_model_is_absent_from_triage(self):
    """rounds にいるモデルが triage に出ていない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-triage-model"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_triage_model="gpt-5.4",
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "rounds にいるモデルが triage に出ていない review_run は完了扱いしてはいけない",
    )


class PostWriteReviewRunEndToEndTests(unittest.TestCase):
  """review-run から manifest 生成、next 完了認定までの統合テスト"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_generated_from_review_triage_helper(self):
    """review_triage.write_manifest が生成した厳格 manifest で next が通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "e2e-review-run"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    manifest_path = (
      cwd
      / ".reviewcompass"
      / "post-write-verification"
      / "post-write-2026-06-03-999.yaml"
    )

    write_manifest(str(run_dir), str(manifest_path))
    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_triage.write_manifest 生成 manifest は next で完了認定されるべき。"
      f"next_action: {data['next_action']}",
    )
    self.assertEqual(
      data["current_state"]["post_write_manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-03-999.yaml",
    )


class ReopenStartTests(unittest.TestCase):
  """reopen-start サブコマンドの trigger_map 解決と in-progress 生成"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_reopen_start_generates_in_progress_file_for_d_1(self):
    """D-1 から pending_gates を解決して in-progress YAML を生成する"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "D-1",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "design で requirements の不整合を検出",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "reopen_started")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      [
        "stages/requirements.yaml#alignment",
        "stages/requirements.yaml#approval",
        "stages/design.yaml#alignment",
        "stages/design.yaml#approval",
      ],
    )
    in_progress = cwd / "stages" / "in-progress" / "reopen-procedure-2026-06-02.yaml"
    self.assertTrue(in_progress.exists())
    generated = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(generated["process_id"], "reopen-procedure")
    self.assertEqual(generated["classification"], "D-1")
    self.assertEqual(generated["feature"], "runtime")
    self.assertEqual(generated["next_step"], "第1過程：判定とフラグ差し戻し")

  def test_reopen_start_invalid_classification_returns_deviation(self):
    """未定義 classification は fail-closed で逸脱"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "Z-9",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "invalid",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")


class ReopenAdvanceGateTests(unittest.TestCase):
  """reopen-advance-gate サブコマンドの進行中 gate 更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_spec(self):
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "workflow-management"
      / "spec.json"
    )
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(
      json.dumps(
        {
          "feature_name": "workflow-management",
          "workflow_state": {
            "requirements": {
              "drafting": True,
              "triad-review": True,
              "review-wave": True,
              "alignment": False,
              "approval": False,
            }
          },
        },
        ensure_ascii=False,
        indent=2,
      )
      + "\n",
      encoding="utf-8",
    )
    return spec_path

  def test_reopen_advance_gate_updates_spec_and_in_progress_state(self):
    """pending gate 完了時の spec.json と reopen YAML 更新を機械処理する"""
    spec_path = self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", ".reviewcompass/specs/_cross_feature/reviews/alignment.md",
        "--completed-step", "第3過程：requirements alignment 実施",
        "--set-spec", "workflow-management", "requirements", "alignment", "true",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    self.assertTrue(spec["workflow_state"]["requirements"]["alignment"])
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["pending_gates"], ["stages/requirements.yaml#approval"])
    self.assertEqual(state["completed_gates"], ["stages/requirements.yaml#alignment"])
    self.assertEqual(
      state["downstream_impact_decisions"][0]["gate"],
      "stages/requirements.yaml#alignment",
    )
    self.assertEqual(state["next_step"], "第3過程：requirements approval")

  def test_reopen_advance_gate_blocks_nonleading_pending_gate(self):
    """pending_gates の先頭以外を飛ばして完了できない"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision", "approved",
        "--feature-scope", "workflow-management",
        "--rationale", "approval を先に進める。",
        "--evidence", "approval.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("先頭", result.stdout)

  def test_reopen_advance_gate_rejects_missing_evidence(self):
    """根拠なしの pending gate 更新は拒否する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)

  def test_reopen_advance_gate_rejects_malformed_pending_gate(self):
    """pending_gates の全要素が標準 gate 形式でなければ拒否する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - requirements approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", "alignment.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("pending_gates", result.stdout)
    self.assertIn("stages/<phase>.yaml#<stage>", result.stdout)

  def test_reopen_advance_gate_rejects_drafting_pending_gate(self):
    """pending_gates は review 系 gate に限定する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#drafting\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", "alignment.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("pending_gates", result.stdout)
    self.assertIn("review 系 gate", result.stdout)


class ReopenAdvanceStepTests(unittest.TestCase):
  """reopen-advance-step サブコマンドの第1・第2過程更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_in_progress(self, *, step_number, next_step, pending_gates=None):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    if pending_gates is None:
      pending_gates = [
        "stages/requirements.yaml#alignment",
        "stages/requirements.yaml#approval",
      ]
    in_progress.write_text(
      yaml.safe_dump(
        {
          "process_id": "reopen-procedure",
          "feature": "workflow-management",
          "step_number": step_number,
          "next_step": next_step,
          "completed_steps": [],
          "pending_gates": pending_gates,
          "current_blocker": None,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    return in_progress

  def test_reopen_advance_step_one_records_evidence_and_moves_to_step_two(self):
    """第1過程の完了を記録し第2過程へ進める"""
    in_progress = self._write_in_progress(
      step_number=1,
      next_step="第1過程：判定とフラグ差し戻し",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類と rollback flags を記録した。",
        "--evidence", "docs/reviews/reopen-classification-2026-06-16.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 2)
    self.assertEqual(state["next_step"], "第2過程：正本修正")
    self.assertIn("第1過程：判定とフラグ差し戻し完了", state["completed_steps"])
    self.assertEqual(state["reopen_step_records"][0]["from_step"], 1)
    self.assertEqual(
      state["reopen_step_records"][0]["evidence"],
      ["docs/reviews/reopen-classification-2026-06-16.md"],
    )

  def test_reopen_advance_step_two_records_commit_stop_point(self):
    """第2過程の完了を記録し停止点コミット状態へ進める"""
    in_progress = self._write_in_progress(
      step_number=2,
      next_step="第2過程：正本修正",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "2",
        "--completed-step", "第2過程：正本修正完了",
        "--rationale", "正本文書の修正を完了した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 2)
    self.assertEqual(state["next_step"], "第2過程：停止点コミット")
    self.assertIsNone(state["current_blocker"])
    self.assertIs(state["commit_stop_point"], True)
    self.assertEqual(state["commit_stop_point_step"], 2)
    self.assertEqual(
      state["commit_stop_point_kind"],
      "canonical_update_complete",
    )
    self.assertEqual(state["commit_stop_point_reason"], "第2過程の正本修正完了")
    self.assertIn("第2過程：正本修正完了", state["completed_steps"])
    self.assertEqual(state["reopen_step_records"][0]["from_step"], 2)

  def test_reopen_advance_step_rejects_missing_evidence(self):
    """根拠なしの reopen step 更新は拒否する"""
    self._write_in_progress(
      step_number=1,
      next_step="第1過程：判定とフラグ差し戻し",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類した。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)

  def test_reopen_advance_step_rejects_current_step_mismatch(self):
    """現在 step と --from-step が一致しなければ拒否する"""
    self._write_in_progress(
      step_number=2,
      next_step="第2過程：正本修正",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類した。",
        "--evidence", "docs/reviews/reopen-classification-2026-06-16.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("step_number", result.stdout)


class ReopenSetBlockerTests(unittest.TestCase):
  """reopen-set-blocker サブコマンドの承認待ち blocker 構造化"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_in_progress(self, pending_gates=None):
    if pending_gates is None:
      pending_gates = [
        "stages/requirements.yaml#approval",
        "stages/design.yaml#alignment",
      ]
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    lines = [
      "process_id: reopen-procedure",
      "feature: workflow-management",
      "step_number: 3",
      "next_step: 第3過程：連鎖再実施",
      "pending_gates:",
    ]
    lines.extend([f"  - {gate}" for gate in pending_gates])
    lines.append("current_blocker: null")
    in_progress.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return in_progress

  def test_reopen_set_blocker_writes_structured_approval_blocker(self):
    """先頭 approval gate の承認待ち blocker を構造化して保存する"""
    in_progress = self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--actor", "human",
        "--rationale", "approval gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(
      state["current_blocker"],
      {
        "blocker_type": "approval_gate",
        "gate": "stages/requirements.yaml#approval",
        "actor": "human",
        "status": "waiting_for_approval",
        "rationale": "approval gate に到達した。",
        "evidence": [
          ".reviewcompass/specs/workflow-management/requirements.md",
        ],
      },
    )

  def test_reopen_set_blocker_rejects_non_head_gate(self):
    """pending_gates 先頭ではない gate の blocker 設定は拒否する"""
    self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/design.yaml#alignment",
        "--actor", "human",
        "--rationale", "approval gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/design.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("先頭", result.stdout)

  def test_reopen_set_blocker_rejects_non_approval_gate(self):
    """approval 以外の gate には承認待ち blocker を設定しない"""
    self._write_in_progress(pending_gates=["stages/requirements.yaml#alignment"])

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--actor", "human",
        "--rationale", "alignment gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("approval", result.stdout)

  def test_reopen_set_blocker_rejects_missing_evidence(self):
    """根拠なしの blocker 設定は拒否する"""
    self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--actor", "proxy_model",
        "--rationale", "proxy_model 承認待ち。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)


class ReopenFinalizeTests(unittest.TestCase):
  """reopen-finalize サブコマンドの完了 YAML 機械更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_ready_in_progress(self):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 4\n"
      "next_step: 第4過程：完了\n"
      "completed_steps:\n"
      "  - 第3過程：requirements approval 実施\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: alignment 済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/alignment.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: approval 済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/approval.md\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )
    return in_progress

  def _feature_impact_args(self):
    args = []
    for feature in FEATURE_ORDER:
      args.extend([
        "--feature-impact",
        feature,
        "reopen_existing_feature",
        "contract_ownership",
        f"{feature} の契約影響を確認した。",
        f".reviewcompass/specs/{feature}/requirements.md",
      ])
    return args

  def test_reopen_finalize_moves_in_progress_to_completed_with_required_decisions(self):
    """第4過程の完了 YAML を構造化入力から生成し in-progress を残さない"""
    in_progress = self._write_ready_in_progress()

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--completed-step", "第4過程：reopen 完了",
        "--json",
      ]
      + self._feature_impact_args(),
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertFalse(in_progress.exists())
    completed = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-16.yaml"
    )
    self.assertTrue(completed.exists())
    state = yaml.safe_load(completed.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 4)
    self.assertEqual(state["next_step"], "完了")
    self.assertEqual(state["pending_gates"], [])
    self.assertEqual(state["current_blocker"], None)
    self.assertEqual(state["impacted_downstream_phases"], ["requirements"])
    self.assertEqual(len(state["feature_impact_decisions"]), len(FEATURE_ORDER))
    self.assertEqual(state["new_feature_decision"]["decision"], "no_new_feature")
    self.assertIn("第4過程：reopen 完了", state["completed_steps"])

  def test_reopen_finalize_blocks_before_step_four(self):
    """第4過程に到達していない reopen state は完了化できない"""
    in_progress = self._write_ready_in_progress()
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    state["step_number"] = 3
    state["pending_gates"] = ["stages/requirements.yaml#approval"]
    in_progress.write_text(
      yaml.safe_dump(state, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--json",
      ]
      + self._feature_impact_args(),
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("第4過程", result.stdout)
    self.assertTrue(in_progress.exists())

  def test_reopen_finalize_requires_all_feature_impact_decisions(self):
    """全 feature の impact 判定が無ければ完了 YAML を生成しない"""
    in_progress = self._write_ready_in_progress()
    incomplete_feature_args = self._feature_impact_args()[:-6]

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--json",
      ]
      + incomplete_feature_args,
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)
    self.assertTrue(in_progress.exists())


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
  # carry-forward register 構造を準備
  register_dir = Path(tmpdir) / "learning" / "workflow" / "carry-forward-register"
  source_dir = register_dir / "sources"
  source_dir.mkdir(parents=True)
  source_file = source_dir / "reviewcompass-pending-cross-feature-findings.md"
  source_file.write_text("# 機能横断レビューで扱う所見の集約\n")
  register_file = register_dir / "reviewcompass-import.yaml"
  _set_pending_findings(register_file, unresolved_count=0, resolved_count=0)
  # register と source もコミットして作業ツリーを clean な初期状態にする
  subprocess.run(
    [
      "git",
      "add",
      "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
      "learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md",
    ],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add carry-forward register"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  return register_file


def _set_pending_findings(register_file, unresolved_count=0, resolved_count=0):
  """抽象レジスタに未消化／対処済み所見を設定する"""
  items = []
  for i in range(unresolved_count):
    items.append({
      "item_id": f"carry-forward-{i+1:03d}",
      "scope": "cross_scope",
      "source_feature": "foundation",
      "target_feature_or_phase": ["runtime"],
      "finding_summary": "テスト用未消化所見",
      "status": "open",
      "decision_needed": False,
      "decision_reasons": [],
      "carry_forward_reason": "テスト用",
      "resolution": None,
      "evidence_refs": [],
      "project_local_context": {"legacy_id": f"A-{i+1:03d}"},
    })
  for i in range(resolved_count):
    n = unresolved_count + i + 1
    items.append({
      "item_id": f"carry-forward-{n:03d}",
      "scope": "cross_scope",
      "source_feature": "foundation",
      "target_feature_or_phase": ["runtime"],
      "finding_summary": "テスト用対処済み所見",
      "status": "resolved",
      "decision_needed": False,
      "decision_reasons": [],
      "carry_forward_reason": "テスト用",
      "resolution": "テスト用対処済み",
      "evidence_refs": [],
      "project_local_context": {"legacy_id": f"A-{n:03d}"},
    })
  register_file.write_text(
    yaml.safe_dump(
      {
        "register_id": "carry-forward-register",
        "schema_version": 1,
        "source_type": "carry_forward_register",
        "items": items,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )


def _stage_file(tmpdir, relpath, content):
  """ファイルを作成して git add 状態にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


def _write_commit_approval(
  tmpdir,
  target_files,
  consumed=False,
  target_sha256=None,
  include_target_sha256=True,
  include_execution_delegation=True,
  execution_instruction="コミット",
):
  """commit 事前検査用のユーザ承認レコードを書く（書き込みは常に新配置＝runtime 区画）"""
  approval_dir = Path(tmpdir) / ".reviewcompass" / "runtime" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  approval_path = approval_dir / "commit-approval.json"
  if target_sha256 is None:
    target_sha256 = {
      relpath: _sha256_file(Path(tmpdir) / relpath)
      for relpath in target_files
      if (Path(tmpdir) / relpath).exists()
    }
  approval = {
    "approved_action": "commit",
    "approved_by": "user",
    "approved_at": "2026-06-03T00:00:00+09:00",
    "rationale": "利用者がコミットを明示承認",
    "target_files": target_files,
    "expires_after_commit": True,
    "consumed": consumed,
  }
  if include_execution_delegation:
    approval["execution_delegation"] = {
      "delegated_to": "llm",
      "approved_by": "user",
      "approved_at": "2026-06-03T00:00:00+09:00",
      "explicit_instruction": execution_instruction,
      "rationale": "利用者が LLM によるコミット実行代行を明示承認",
    }
  if include_target_sha256:
    approval["target_sha256"] = target_sha256
  approval_path.write_text(
    json.dumps(approval, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  return approval_path


def _read_commit_approval(tmpdir):
  """runtime 区画の commit 承認レコードを読む"""
  approval_path = (
    Path(tmpdir)
    / ".reviewcompass"
    / "runtime"
    / "approvals"
    / "commit-approval.json"
  )
  return json.loads(approval_path.read_text(encoding="utf-8"))


def _prepare_commit_approval(tmpdir):
  """commit-approval prepare を実行して JSON を返す"""
  result = run_script(["commit-approval", "prepare", "--json"], cwd=tmpdir)
  if result.returncode != 0:
    raise AssertionError(result.stdout + result.stderr)
  return json.loads(result.stdout)


def _record_commit_approval(tmpdir, nonce, source_text=None, extra_args=None):
  """commit-approval record を実行して JSON を返す"""
  args = [
    "commit-approval",
    "record",
    "--nonce", nonce,
    "--json",
  ]
  input_text = None
  if source_text is None:
    args.append("--no-source-text")
  else:
    args.append("--source-text-stdin")
    input_text = source_text
  if extra_args:
    args.extend(extra_args)
  return subprocess.run(
    ["python3", str(SCRIPT)] + args,
    cwd=str(tmpdir),
    input=input_text,
    capture_output=True,
    text=True,
    timeout=10,
  )


def _delegate_commit_execution(tmpdir, nonce, source_text="コミット\n", extra_args=None):
  """commit-approval delegate-execution を実行して JSON を返す"""
  args = [
    "commit-approval",
    "delegate-execution",
    "--nonce", nonce,
    "--source-text-stdin",
    "--json",
  ]
  if extra_args:
    args.extend(extra_args)
  return subprocess.run(
    ["python3", str(SCRIPT)] + args,
    cwd=str(tmpdir),
    input=source_text,
    capture_output=True,
    text=True,
    timeout=10,
  )


def _read_commit_execution_delegation(tmpdir):
  """runtime 区画の commit 実行代行承認レコードを読む"""
  delegation_path = (
    Path(tmpdir)
    / ".reviewcompass"
    / "runtime"
    / "approvals"
    / "commit-execution-delegation.json"
  )
  return json.loads(delegation_path.read_text(encoding="utf-8"))


def _load_commit_approval_module():
  """tools/check_workflow_action/commit_approval.py をスクリプト実行時と同じ path で読む"""
  tools_path = str(REPO_ROOT / "tools")
  if tools_path not in os.sys.path:
    os.sys.path.insert(0, tools_path)
  return importlib.import_module("check_workflow_action.commit_approval")


def _write_completed_post_write_manifest(tmpdir, target_files):
  """対象ファイルを覆う完了 post-write manifest を書く"""
  target_sha256 = {
    relpath: _sha256_file(Path(tmpdir) / relpath)
    for relpath in target_files
  }
  _write_post_write_manifest(
    tmpdir,
    "post-write-2026-06-03-999.yaml",
    {
      "status": "completed",
      "target_files": target_files,
      "target_sha256": target_sha256,
      "required_verifiers": ["google"],
      "completed_verifiers": ["google"],
      "unresolved_substantive_findings": 0,
    },
  )


def _write_last_commit_precheck(tmpdir, head_commit=None):
  """push 事前検査用の直近 commit 検査通過記録を書く"""
  if head_commit is None:
    result = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      cwd=str(tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )
    head_commit = result.stdout.strip()
  approval_dir = Path(tmpdir) / ".git" / "reviewcompass"
  approval_dir.mkdir(parents=True, exist_ok=True)
  precheck_path = approval_dir / "last-commit-precheck.json"
  precheck_path.write_text(
    json.dumps(
      {
        "head_commit": head_commit,
        "precheck_command": "tools/check-workflow-action.py commit",
        "precheck_exit_code": 0,
        "recorded_at": "2026-06-03T00:00:00+09:00",
      },
      ensure_ascii=False,
      indent=2,
    ),
    encoding="utf-8",
  )
  return precheck_path


class CommitExitCodeTests(unittest.TestCase):
  """commit サブコマンドの終了コード判定（仕様 §6.2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_with_no_pending_and_normal_changes_returns_zero(self):
    """未消化所見 0 件 + 通常変更 + ユーザ承認あり → exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
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

  def test_llm_commit_without_execution_delegation_returns_two(self):
    """LLM 実行では通常の commit 承認だけでは exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_execution_delegation=False,
    )

    result = run_script(
      ["commit", "--rationale", "内容承認のみで LLM commit しようとするテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_rejects_autonomous_until_next_commit_instruction(self):
    """次のコミットまで自律実行は commit 停止点到達指示であり代行承認ではない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="次のコミットまで自律実行",
    )

    result = run_script(
      ["commit", "--rationale", "次のコミットまで自律実行の誤解釈防止テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_rejects_autonomous_instruction_without_commit(self):
    """自律実行して、だけでは commit 実行代行承認にならない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="自律実行して",
    )

    result = run_script(
      ["commit", "--rationale", "自律実行して単独の誤解釈防止テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_accepts_autonomous_with_commit_delegation_instruction(self):
    """コミット代行も含めて自律実行なら LLM commit を許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="コミット代行も含めて自律実行",
    )

    result = run_script(
      ["commit", "--rationale", "コミット代行込みの自律実行テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_human_commit_precheck_allows_content_approval_without_delegation(self):
    """人間実行としての事前検査なら実行代行承認は不要"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_execution_delegation=False,
    )

    result = run_script(
      [
        "commit",
        "--rationale", "人間が commit する前の内容承認チェック",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_prepare_outputs_nonce_challenge_json(self):
    """commit-approval prepare は staged 内容に束縛した challenge JSON を出力する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")

    result = run_script(["commit-approval", "prepare", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    payload = json.loads(result.stdout)
    self.assertEqual(payload["status"], "prepared")
    self.assertEqual(payload["target_files"], ["notes.md"])
    self.assertRegex(payload["nonce"], r"^[0-9a-f]{32,}$")
    self.assertEqual(payload["target_digest"]["algorithm"], "commit-approval-v1")

  def test_commit_approval_prepare_invalidates_malformed_stale_delegation(self):
    """prepare は古い壊れた delegation を新しい承認フローの邪魔にしない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    stale_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text(
      json.dumps({
        "schema_version": 1,
        "approved_action": "commit_execution_delegation",
        "expires_at": "not-a-timestamp",
        "consumed": False,
        "invalidated": False,
      }, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")

    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stdout)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "承認")

  def test_commit_approval_record_no_source_json_validates_for_commit(self):
    """prepare→record --no-source-text は commit 検査で通る nonce 承認を作る"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text=None,
    )
    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    record_payload = json.loads(record_result.stdout)
    self.assertEqual(record_payload["status"], "recorded")
    approval = _read_commit_approval(self.tmpdir)
    self.assertEqual(approval["source_omission_reason"], "source_not_provided")
    self.assertEqual(approval["attestation_type"], "staged_content_nonce_binding")
    self.assertEqual(
      approval["guarantee_scope"],
      "staged_content_binding_not_ui_utterance_proof",
    )

    result = run_script(
      [
        "commit",
        "--rationale", "nonce 承認の commit 検査",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_record_does_not_embed_execution_delegation_by_default(self):
    """nonce 承認 record は staged 内容承認だけを保存し、実行代行承認を既定で混ぜない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertNotIn("execution_delegation", approval)

  def test_commit_approval_delegate_execution_writes_separate_record(self):
    """実行代行承認は commit-approval とは別ファイルに保存する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    payload = json.loads(delegate_result.stdout)
    self.assertEqual(payload["status"], "delegated")
    self.assertEqual(
      payload["delegation_path"],
      ".reviewcompass/runtime/approvals/commit-execution-delegation.json",
    )
    approval = _read_commit_approval(self.tmpdir)
    self.assertNotIn("execution_delegation", approval)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["approved_action"], "commit_execution_delegation")
    self.assertEqual(delegation["delegated_action"], "commit")
    self.assertEqual(delegation["delegated_to"], "llm")
    self.assertEqual(delegation["approved_by"], "user")
    self.assertEqual(delegation["nonce"], challenge["nonce"])
    self.assertEqual(delegation["explicit_instruction"], "コミット")
    self.assertRegex(delegation["instruction_sha256"], r"^[0-9a-f]{64}$")
    self.assertEqual(
      delegation["attestation_type"],
      "commit_execution_delegation_nonce_binding",
    )
    self.assertEqual(
      delegation["guarantee_scope"],
      "stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof",
    )
    self.assertFalse(delegation["consumed"])
    self.assertFalse(delegation["invalidated"])
    self.assertNotIn("llm", delegation)
    self.assertNotIn("provider", delegation)
    self.assertNotIn("model", delegation)

  def test_commit_approval_delegate_execution_accepts_approval_instruction(self):
    """2回目入力の「承認」を commit 実行代行承認として受け入れる"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "承認")

  def test_llm_commit_accepts_separate_execution_delegation_record(self):
    """LLM commit 実行は別ファイルの実行代行承認がある場合だけ通す"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    result_without_delegation = run_script(
      ["commit", "--rationale", "内容承認だけで LLM commit しようとするテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result_without_delegation)
    self.assertEqual(result_without_delegation.returncode, 2, result_without_delegation.stdout)
    self.assertIn("commit-execution-delegation", result_without_delegation.stdout)

    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)

    result_with_delegation = run_script(
      ["commit", "--rationale", "別ファイル実行代行承認付き commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result_with_delegation)
    self.assertEqual(result_with_delegation.returncode, 0, result_with_delegation.stdout)

  def test_commit_approval_delegate_execution_rejects_crlf_instruction(self):
    """実行代行承認の stdin は CR/CRLF を許容しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="コミット\r\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 2, delegate_result.stdout)
    self.assertIn("source text", delegate_result.stdout)

  def test_commit_rejects_tampered_execution_delegation_record(self):
    """実行代行承認レコードの target_digest が改ざんされていれば遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["target_digest"]["digest"] = "0" * 64
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認改ざん遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-execution-delegation", result.stdout)

  def test_commit_approval_delegate_execution_rejects_malformed_existing_delegation(self):
    """壊れた未消費 delegation record が既にある場合は上書きせず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["expires_at"] = "not-a-timestamp"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    duplicate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, duplicate_result)
    self.assertEqual(duplicate_result.returncode, 2, duplicate_result.stdout)
    self.assertIn("commit-execution-delegation", duplicate_result.stdout)

  def test_commit_rejects_execution_delegation_with_unknown_field(self):
    """delegation record に unknown field が混入したら commit gate で遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["unexpected_field"] = "unexpected"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認 unknown field 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("不明フィールド", result.stdout)

  def test_commit_rejects_execution_delegation_with_identity_field(self):
    """delegation record に LLM/provider/model 系 field が混入したら遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["model"] = "gpt-test"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認 identity field 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("model", result.stdout)

  def test_commit_approval_delegate_execution_redaction_failure_does_not_write_record(self):
    """delegate_execution の redaction failure は record を作らず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    commit_approval = _load_commit_approval_module()
    original_redact_source = commit_approval._redact_source

    def fail_redaction(_source_text):
      return None, "redaction_failed", ["forced failure"]

    commit_approval._redact_source = fail_redaction
    try:
      with self.assertRaisesRegex(ValueError, "redaction"):
        commit_approval.delegate_execution(
          Path(self.tmpdir),
          challenge["nonce"],
          "コミット\n",
        )
    finally:
      commit_approval._redact_source = original_redact_source

    self.assertFalse(delegation_path.exists())

  def test_nonce_commit_rejects_embedded_execution_delegation_without_separate_record(self):
    """nonce 承認では embedded execution_delegation があっても別 record なしなら遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["execution_delegation"] = {
      "delegated_to": "llm",
      "approved_by": "user",
      "explicit_instruction": "コミット",
    }
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "nonce 承認 embedded delegation bypass 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-execution-delegation", result.stdout)

  def test_commit_approval_record_source_text_is_redacted(self):
    """stdin 承認本文は機微情報除去後に保存される"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認します OPENAI_API_KEY=sk-proj-SECRET1234567890abcdef",
    )

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertIn("source_text_redacted", approval)
    self.assertNotIn("source_omission_reason", approval)
    self.assertNotIn("sk-proj-", approval["source_text_redacted"])
    self.assertIn("[除去:", approval["source_text_redacted"])

    result = run_script(
      [
        "commit",
        "--rationale", "redacted source 付き nonce 承認の commit 検査",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_record_residual_secret_omits_source(self):
    """redaction 後に秘密候補が残る場合は承認本文を保存しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text="Aa0" * 20,
    )

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertEqual(approval["source_omission_reason"], "residual_secret_detected")
    self.assertNotIn("source_text_redacted", approval)
    self.assertIn("redaction_findings", approval)

  def test_commit_approval_record_rejects_malformed_challenge_target_files(self):
    """challenge の target_files が文字列配列でなければ補完せず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    challenge_record["target_files"] = "notes.md"
    challenge_path.write_text(
      json.dumps(challenge_record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 2, record_result.stdout)
    self.assertIn("target_files", record_result.stdout)

  def test_commit_approval_record_rejects_uppercase_challenge_target_digest(self):
    """challenge target_digest は小文字 hex の正規形だけを受け付ける"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    challenge_record["target_digest"]["digest"] = "A" * 64
    challenge_path.write_text(
      json.dumps(challenge_record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 2, record_result.stdout)
    self.assertIn("target_digest digest", record_result.stdout)

  def test_commit_approval_rejects_staged_change_after_record(self):
    """record 後に staged 内容が変わったら nonce 承認は使えない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 承認時点")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    _stage_file(self.tmpdir, "notes.md", "# commit 実行時点")

    result = run_script(
      ["commit", "--rationale", "nonce 承認後の差分変更遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-approval", result.stdout)

  def test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails(self):
    """legacy fallback の nonce 承認が失敗しても旧記録は凍結し runtime 側だけ invalidated にする"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 承認時点")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    runtime_approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    legacy_approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "approvals"
      / "commit-approval.json"
    )
    legacy_approval_path.parent.mkdir(parents=True)
    legacy_approval_path.write_text(
      runtime_approval_path.read_text(encoding="utf-8"),
      encoding="utf-8",
    )
    legacy_before = legacy_approval_path.read_text(encoding="utf-8")
    runtime_approval_path.unlink()
    _stage_file(self.tmpdir, "notes.md", "# commit 実行時点")

    result = run_script(
      ["commit", "--rationale", "legacy nonce fallback invalidation"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertEqual(legacy_approval_path.read_text(encoding="utf-8"), legacy_before)
    runtime_approval = json.loads(runtime_approval_path.read_text(encoding="utf-8"))
    self.assertTrue(runtime_approval["invalidated"])
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    self.assertTrue(challenge_record["invalidated"])

  def test_commit_approval_rejects_expired_record(self):
    """expires_at を過ぎた nonce 承認は使えない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["expires_at"] = (
      datetime.now(timezone.utc) - timedelta(seconds=1)
    ).isoformat()
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "期限切れ nonce 承認遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("期限切れ", result.stdout)

  def test_commit_approval_rejects_llm_metadata_fields(self):
    """nonce 承認 record に LLM/provider/model 系フィールドがあれば遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["model"] = "gpt-test"
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "LLM メタデータ混入遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("model", result.stdout)

  def test_commit_approval_prepare_preserves_staged_gitlink_entry(self):
    """gitlink は削除扱いにせず mode/object_id を canonical target に残す"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    head = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    ).stdout.strip()
    subprocess.run(
      ["git", "update-index", "--add", "--cacheinfo", f"160000,{head},vendor/lib"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )

    challenge = _prepare_commit_approval(self.tmpdir)

    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    entries = challenge_record["target"]["entries"]
    self.assertEqual(challenge["target_files"], ["vendor/lib"])
    self.assertEqual(entries[0]["path"], "vendor/lib")
    self.assertEqual(entries[0]["mode"], "160000")
    self.assertEqual(entries[0]["object_id"], head)
    self.assertNotEqual(entries[0]["sha256"], "DELETED")

  def test_commit_approval_prepare_includes_rename_source_deletion(self):
    """rename は destination だけでなく source deletion も canonical target に含める"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "old.md", "# old name")
    subprocess.run(
      ["git", "commit", "-qm", "add old.md"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )
    subprocess.run(
      ["git", "mv", "old.md", "new.md"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )

    challenge = _prepare_commit_approval(self.tmpdir)

    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    entries_by_path = {
      entry["path"]: entry
      for entry in challenge_record["target"]["entries"]
    }
    self.assertEqual(challenge["target_files"], ["new.md", "old.md"])
    self.assertEqual(entries_by_path["old.md"]["status"], "D")
    self.assertEqual(entries_by_path["old.md"]["object_id"], "DELETED")
    self.assertEqual(entries_by_path["new.md"]["status"], "R")

  def test_commit_blocks_when_in_progress_file_exists(self):
    """stages/in-progress が非空なら commit は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    in_progress_dir = Path(self.tmpdir) / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "in-progress 遮断テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_allows_completed_maintenance_with_mainline_reopen_in_progress(self):
    """本線 reopen 中でも対応する maintenance 完了 commit は許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    reopen_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-09.yaml"
    )
    reopen_path.parent.mkdir(parents=True)
    reopen_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：stages/requirements.yaml#triad-review 再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n",
      encoding="utf-8",
    )
    maintenance_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "maintenance-2026-06-09-reopen-guard.yaml"
    )
    maintenance_path.parent.mkdir(parents=True)
    maintenance_path.write_text(
      "process_id: maintenance\n"
      "title: reopen guard\n"
      "mainline_blocked_by: stages/in-progress/reopen-procedure-2026-06-09.yaml\n"
      "completed_actions:\n"
      "  - guarded side track completed\n",
      encoding="utf-8",
    )
    subprocess.run(
      [
        "git",
        "add",
        "stages/in-progress/reopen-procedure-2026-06-09.yaml",
        "stages/completed/maintenance-2026-06-09-reopen-guard.yaml",
      ],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "stages/in-progress/reopen-procedure-2026-06-09.yaml",
        "stages/completed/maintenance-2026-06-09-reopen-guard.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "maintenance side track 完了 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_allows_reopen_stop_point_when_in_progress_file_is_staged(self):
    """第2過程の commit 停止点は構造フィールドで通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：正本修正完了\n"
      "step_number: 2\n"
      "current_blocker: null\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_reopen_stop_point_text_without_structured_fields(self):
    """next_step の文言だけでは reopen 停止点 commit を許可しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "旧式 next_step 停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_blocks_reopen_stop_point_without_structured_kind(self):
    """commit_stop_point=true でも構造化 kind がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "構造化不足の停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_allows_reopen_explicit_commit_stop_point_field(self):
    """next_step を壊さず commit_stop_point=true で reopen 停止点 commit を許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：implementation triad-review\n"
      "step_number: 3\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 3\n"
      "commit_stop_point_kind: drafting_complete\n"
      "commit_stop_point_gate: stages/implementation.yaml#drafting\n"
      "commit_stop_point_reason: 文言に依存しない人間向け説明\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-15.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-15.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 明示 commit_stop_point commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason(self):
    """commit_stop_point=true でも正当な implementation drafting 停止点でなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：implementation triad-review\n"
      "step_number: 3\n"
      "commit_stop_point: true\n"
      "commit_stop_point_reason: 手順外の停止点\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-15.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-15.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "不正な commit_stop_point commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_blocks_completed_reopen_without_impact_decisions(self):
    """reopen 完了 commit は下流影響判定表がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("downstream_impact_decisions", result.stdout)

  def test_commit_allows_completed_reopen_with_impact_decisions(self):
    """reopen 完了 commit は全 pending gate の下流影響判定表があれば通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: 既存要件で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: alignment 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響判定ありテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_completed_reopen_missing_completed_gate_decision(self):
    """完了済み gate は pending_gates から外れていても判定表で覆う必要がある"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions: []\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了済み gate 判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("completed_gates", result.stdout)
    self.assertIn("stages/requirements.yaml#triad-review", result.stdout)

  def test_commit_allows_completed_reopen_with_completed_gate_decisions(self):
    """完了済み gate の判定表があれば pending_gates が空でも通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#triad-review\n"
      "    feature_scope:\n"
      "      - foundation\n"
      "      - runtime\n"
      "      - evaluation\n"
      "      - analysis\n"
      "      - workflow-management\n"
      "      - self-improvement\n"
      "      - conformance-evaluation\n"
      "    decision: approved\n"
      "    rationale: triad-review 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/summary.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了済み gate 判定ありテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_completed_reopen_missing_review_gates_after_canonical_change(self):
    """正本変更済み phase の reopen 完了は review 系 gate 不足を遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      ".reviewcompass/specs/foundation/requirements.md",
      "# Requirements\n\nUpdated requirements body.\n",
    )
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: 既存要件で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: alignment 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      [
        "git",
        "add",
        ".reviewcompass/specs/foundation/requirements.md",
        "stages/completed/reopen-procedure-2026-06-09.yaml",
      ],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        ".reviewcompass/specs/foundation/requirements.md",
        "stages/completed/reopen-procedure-2026-06-09.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の review gate 不足テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/requirements.yaml#triad-review", result.stdout)
    self.assertIn("stages/requirements.yaml#review-wave", result.stdout)

  def test_commit_blocks_completed_reopen_without_feature_impact_basis(self):
    """feature impact 判定は任意フェーズで判定軸を明示しなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/design.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - design\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/design.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: design は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/design.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 判定軸欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("impact_basis", result.stdout)

  def test_commit_blocks_completed_reopen_with_partial_feature_impact_decisions(self):
    """feature impact 判定は既存 feature 全件を覆わなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      "  - feature: foundation\n"
      "    decision: reopen_existing_feature\n"
      "    rationale: foundation は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 網羅不足テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)

  def test_commit_blocks_completed_reopen_without_feature_impact_decisions(self):
    """reopen 完了 commit は feature impact 判定がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)

  def test_commit_blocks_completed_reopen_when_impacted_phase_is_uncovered(self):
    """reopen 完了 commit は影響フェーズを覆う gate 判定がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "  - design\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響フェーズ漏れテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("impacted_downstream_phases", result.stdout)

  def test_commit_blocks_reopen_marked_spec_without_reopen_procedure(self):
    """reopen 印のある spec.json 変更は reopen 手続きファイルなしでは遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _write_spec(
      self.tmpdir,
      "foundation",
      {
        "drafting": False,
        "triad-review": False,
        "review-wave": False,
        "alignment": False,
        "approval": False,
      },
    )
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "foundation"
      / "spec.json"
    )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"]["upstream_change_pending"] = True
    spec["recheck"]["impacted_downstream_phases"] = ["requirements"]
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    relpath = ".reviewcompass/specs/foundation/spec.json"
    subprocess.run(
      ["git", "add", relpath],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(self.tmpdir, [relpath])

    result = run_script(
      ["commit", "--rationale", "reopen 印 spec の手続きファイル必須テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("reopen 手続き", result.stdout)

  def test_commit_allows_reopen_marked_spec_with_reopen_procedure(self):
    """reopen 印のある spec.json 変更は reopen 手続きファイルがあれば逸脱ではない"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _write_spec(
      self.tmpdir,
      "foundation",
      {
        "drafting": False,
        "triad-review": False,
        "review-wave": False,
        "alignment": False,
        "approval": False,
      },
    )
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "foundation"
      / "spec.json"
    )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"]["upstream_change_pending"] = True
    spec["recheck"]["impacted_downstream_phases"] = ["requirements"]
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-09.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 2\n"
      "next_step: 第2過程：停止点コミット\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n",
      encoding="utf-8",
    )
    relpaths = [
      ".reviewcompass/specs/foundation/spec.json",
      "stages/in-progress/reopen-procedure-2026-06-09.yaml",
    ]
    subprocess.run(
      ["git", "add"] + relpaths,
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(self.tmpdir, relpaths)

    result = run_script(
      ["commit", "--rationale", "reopen 印 spec と手続きファイルのテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertNotEqual(result.returncode, 2, result.stdout)

  def test_commit_with_pending_findings_returns_one(self):
    """未消化所見 1 件以上 → exit 1（警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=1)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
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
    _write_commit_approval(self.tmpdir, [".reviewcompass/specs/foundation/spec.json"])
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
    _write_completed_post_write_manifest(self.tmpdir, ["docs/plan/test-plan.md"])
    _write_commit_approval(self.tmpdir, ["docs/plan/test-plan.md"])
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
    _write_commit_approval(self.tmpdir, ["credentials.json"])
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

  def test_commit_blocks_deployable_artifact_with_absolute_path(self):
    """deployable artifact にローカル絶対パスが混入した commit は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    relpath = "learning/workflow/deployment-readiness/bad.json"
    _stage_file(
      self.tmpdir,
      relpath,
      '{"path": "/Users/Daily/Development/ReviewCompass/config.yaml"}\n',
    )
    _write_commit_approval(self.tmpdir, [relpath])

    result = run_script(
      ["commit", "--rationale", "配置非依存 lint guard のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("配置非依存", result.stdout)
    self.assertIn(relpath, result.stdout)

  def test_commit_without_user_approval_returns_two(self):
    """ユーザ承認レコードなし → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_script(
      ["commit", "--rationale", "承認なし commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"承認レコードなしの commit は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn("ユーザ承認レコード", result.stdout)

  def test_commit_with_consumed_user_approval_returns_two(self):
    """消費済み承認レコード → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"], consumed=True)
    result = run_script(
      ["commit", "--rationale", "消費済み承認のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("消費済み", result.stdout)

  def test_commit_with_approval_scope_mismatch_returns_two(self):
    """承認対象と staged ファイルが一致しない → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["other.md"])
    result = run_script(
      ["commit", "--rationale", "承認対象不一致のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("承認対象外", result.stdout)

  def test_commit_with_missing_approval_target_sha256_returns_two(self):
    """承認レコードに target_sha256 がなければ exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_target_sha256=False,
    )
    result = run_script(
      ["commit", "--rationale", "承認 sha256 欠落のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("target_sha256", result.stdout)

  def test_commit_with_stale_approval_target_sha256_returns_two(self):
    """承認後に staged 内容が変わったら exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# 承認時点")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    _stage_file(self.tmpdir, "notes.md", "# 実行時点")
    result = run_script(
      ["commit", "--rationale", "古い承認レコードのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("sha256", result.stdout)

  def test_commit_with_deleted_file_and_deleted_sentinel_passes(self):
    """削除ファイルが staged で、承認レコードが "DELETED" sentinel を使えば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    # ファイルを作成してコミット済みにする
    _stage_file(self.tmpdir, "delete_me.md", "# 削除予定ファイル")
    subprocess.run(
      ["git", "commit", "-qm", "add delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # ファイルを削除してステージ
    subprocess.run(
      ["git", "rm", "-q", "delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # "DELETED" sentinel を使った承認レコード
    _write_commit_approval(
      self.tmpdir,
      ["delete_me.md"],
      target_sha256={"delete_me.md": "DELETED"},
    )
    result = run_script(
      ["commit", "--rationale", "削除ファイルを含むコミットのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(result.returncode, 2,
                        f"削除ファイル + DELETED sentinel は exit 2 にならないはず\n{result.stdout}")

  def test_commit_with_deleted_file_without_deleted_sentinel_returns_two(self):
    """削除ファイルに "DELETED" でない sha256 が指定されていれば exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "delete_me.md", "# 削除予定ファイル")
    subprocess.run(
      ["git", "commit", "-qm", "add delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    subprocess.run(
      ["git", "rm", "-q", "delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # 意図的に "DELETED" でないハッシュを指定
    _write_commit_approval(
      self.tmpdir,
      ["delete_me.md"],
      target_sha256={"delete_me.md": "not_the_deleted_sentinel"},
    )
    result = run_script(
      ["commit", "--rationale", "削除ファイル sha256 不一致のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)

  def test_commit_with_post_write_target_without_manifest_returns_two(self):
    """post-write 対象文書が staged され、完了 manifest がなければ exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "TODO_NEXT_SESSION.md", "# 次セッション")
    _write_commit_approval(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 未検証の遮断テスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("post-write-verification 未完了", result.stdout)

  def test_commit_with_post_write_target_and_completed_manifest_returns_zero(self):
    """post-write 対象文書が staged されても完了 manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "TODO_NEXT_SESSION.md", "# 次セッション")
    _write_completed_post_write_manifest(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    _write_commit_approval(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"完了 manifest がある post-write 対象 commit は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_operations_doc_and_completed_manifest_returns_zero(self):
    """docs/operations 配下の対象文書も completed manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      "docs/operations/WORKFLOW_PRECHECK.md",
      "# WORKFLOW_PRECHECK",
    )
    _write_completed_post_write_manifest(
      self.tmpdir,
      ["docs/operations/WORKFLOW_PRECHECK.md"],
    )
    _write_commit_approval(self.tmpdir, ["docs/operations/WORKFLOW_PRECHECK.md"])
    result = run_script(
      ["commit", "--rationale", "operations 文書検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_operations_doc_with_wrong_anchor_link(self):
    """文書リンクのアンカー誤りがある staged 文書は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    source_path = "docs/operations/link-source.md"
    target_path = "docs/operations/link-target.md"
    _stage_file(
      self.tmpdir,
      source_path,
      "# Link Source\n\n[対象](link-target.md#missing-anchor)\n",
    )
    _stage_file(
      self.tmpdir,
      target_path,
      "# Existing Anchor\n",
    )
    _write_completed_post_write_manifest(self.tmpdir, [source_path, target_path])
    _write_commit_approval(self.tmpdir, [source_path, target_path])

    result = run_script(
      ["commit", "--rationale", "文書リンク検査の commit gate テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("文書リンク lint", result.stdout)
    self.assertIn("missing_anchor", result.stdout)

  def test_commit_checks_staged_document_link_content(self):
    """worktree が修正済みでも staged 文書にリンク誤りがあれば exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    source_path = "docs/operations/link-source.md"
    target_path = "docs/operations/link-target.md"
    _stage_file(
      self.tmpdir,
      source_path,
      "# Link Source\n\n[対象](link-target.md#missing-anchor)\n",
    )
    _stage_file(
      self.tmpdir,
      target_path,
      "# Existing Anchor\n",
    )
    source = Path(self.tmpdir) / source_path
    source.write_text(
      "# Link Source\n\n[対象](link-target.md#existing-anchor)\n",
      encoding="utf-8",
    )
    _write_completed_post_write_manifest(self.tmpdir, [source_path, target_path])
    staged_hash = {
      source_path: _staged_sha256_file(self.tmpdir, source_path),
      target_path: _staged_sha256_file(self.tmpdir, target_path),
    }
    _write_commit_approval(
      self.tmpdir,
      [source_path, target_path],
      target_sha256=staged_hash,
    )

    result = run_script(
      ["commit", "--rationale", "staged 文書リンク検査のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("文書リンク lint", result.stdout)
    self.assertIn("missing_anchor", result.stdout)

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

  def test_push_blocks_when_in_progress_file_exists(self):
    """stages/in-progress が非空なら push は exit 2"""
    in_progress_dir = Path(self.tmpdir) / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )

    result = run_script(
      ["push", "--rationale", "in-progress 遮断テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

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

  def test_push_with_ahead_commit_without_commit_precheck_record_returns_two(self):
    """先行 commit があり、直前 commit 検査記録がなければ exit 2"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _stage_file(self.tmpdir, "notes.md", "# push 対象")
    subprocess.run(
      ["git", "commit", "-qm", "add push target"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(
      ["push", "--rationale", "commit 検査記録なし push のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("last-commit-precheck", result.stdout)

  def test_push_with_ahead_commit_and_matching_commit_precheck_record_returns_zero(self):
    """先行 commit の HEAD と直前 commit 検査記録が一致すれば exit 0"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _stage_file(self.tmpdir, "notes.md", "# push 対象")
    subprocess.run(
      ["git", "commit", "-qm", "add push target"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_last_commit_precheck(self.tmpdir)

    result = run_script(
      ["push", "--rationale", "commit 検査記録あり push のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_push_blocks_ahead_deployable_artifact_with_absolute_path(self):
    """先行 commit の deployable artifact にローカル絶対パスがあれば push は exit 2"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    relpath = "learning/workflow/deployment-readiness/bad.json"
    _stage_file(
      self.tmpdir,
      relpath,
      '{"path": "/Users/Daily/Development/ReviewCompass/config.yaml"}\n',
    )
    subprocess.run(
      ["git", "commit", "-qm", "add bad deployable artifact"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_last_commit_precheck(self.tmpdir)

    result = run_script(
      ["push", "--rationale", "push 配置非依存 lint guard のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("配置非依存", result.stdout)
    self.assertIn(relpath, result.stdout)

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


class AuditCommitTests(unittest.TestCase):
  """audit-commit サブコマンドの post-write 遡及監査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _commit_file(self, relpath, content, message):
    _stage_file(self.tmpdir, relpath, content)
    subprocess.run(
      ["git", "commit", "-qm", message],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def test_audit_commit_detects_post_write_target_without_manifest(self):
    """指定 commit に post-write 対象があり manifest がなければ exit 2"""
    self._commit_file("TODO_NEXT_SESSION.md", "# 次セッション", "add todo")
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("TODO_NEXT_SESSION.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_detects_root_commit_post_write_target_without_manifest(self):
    """root commit の post-write 対象追加も監査対象に含める"""
    tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, tmpdir)
    for cmd in [
      ["git", "init", "-q", "-b", "main"],
      ["git", "config", "user.email", "test@example.com"],
      ["git", "config", "user.name", "Test User"],
      ["git", "config", "commit.gpgsign", "false"],
    ]:
      subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
    _stage_file(tmpdir, "TODO_NEXT_SESSION.md", "# root todo")
    subprocess.run(
      ["git", "commit", "-qm", "root todo"],
      cwd=str(tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(["audit-commit", "HEAD", "--json"], cwd=tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("TODO_NEXT_SESSION.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_accepts_post_write_target_with_matching_manifest(self):
    """指定 commit の post-write 対象を覆う manifest があれば exit 0"""
    self._commit_file("TODO_NEXT_SESSION.md", "# 次セッション", "add todo")
    _write_completed_post_write_manifest(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"matching manifest should pass.\nstdout: {result.stdout}\nstderr: {result.stderr}",
    )


class CommitPushOutputTests(unittest.TestCase):
  """commit／push の JSON 出力検査（仕様 §7.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_json_output(self):
    """commit に --json で JSON 出力に切り替わる"""
    _write_commit_approval(self.tmpdir, [])
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
    self.assertIn("commit_approval", data["current_state"])

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


def _write_feature_dependency(cwd, relative_path, feature_order=None, features=None):
  """feature-dependency.yaml を指定パスに作る"""
  path = Path(cwd) / relative_path
  path.parent.mkdir(parents=True, exist_ok=True)
  data = {}
  if feature_order is not None:
    data["feature_order"] = feature_order
  if features is not None:
    data["features"] = features
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _write_app_spec(cwd, feature, requirements_drafting=False):
  """対象アプリ想定の最小 spec.json（intent と feature-partitioning のみ完了）を作る"""
  spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
  spec_dir.mkdir(parents=True, exist_ok=True)
  untouched_five_stage = {
    "drafting": requirements_drafting,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  untouched_rest = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  spec = {
    "feature_name": feature,
    "language": "ja",
    "created_at": "2026-06-11T00:00:00+09:00",
    "updated_at": "2026-06-11T00:00:00+09:00",
    "workflow_state": {
      "intent": {
        "drafting": True,
        "review": True,
        "approval": True,
        "reference": "stages/intent.yaml",
      },
      "feature-partitioning": {
        "candidate-proposal": True,
        "approval": True,
        "reference": "stages/feature-partitioning/2026-06-11-proposal.md",
      },
      "requirements": dict(untouched_five_stage),
      "design": dict(untouched_rest),
      "tasks": dict(untouched_rest),
      "implementation": dict(untouched_rest),
    },
    "reopened": {},
    "recheck": {
      "upstream_change_pending": False,
      "impacted_downstream_phases": [],
    },
  }
  (spec_dir / "spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )


class FeatureOrderGeneralizationTests(unittest.TestCase):
  """feature 一覧の外出し（feature-dependency.yaml の feature_order キー）

  設計記録：docs/notes/2026-06-10-deployment-multi-llm-entry-design.md §3.5
  side track 記録：stages/in-progress/maintenance-2026-06-11-feature-order-generalization.yaml
  TDD 規律に従い、実装前に作成。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _next_json(self):
    result = run_script(["next", "--json"], cwd=self.tmpdir)
    self.assertNotEqual(result.stdout.strip(), "", f"stderr: {result.stderr}")
    return result, json.loads(result.stdout)

  def test_next_uses_feature_order_from_reviewcompass_dir(self):
    """対象アプリ独自の feature 構成を .reviewcompass/feature-dependency.yaml から読む"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a", "appfeat-b"],
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(
      data["current_state"]["feature_order"], ["appfeat-a", "appfeat-b"],
    )

  def test_reviewcompass_dir_takes_priority_over_stages(self):
    """.reviewcompass/ の定義が stages/ より優先される"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=["other-feat"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")
    self.assertEqual(data["current_state"]["feature_order"], ["appfeat-a"])

  def test_stages_fallback_is_used_without_reviewcompass_file(self):
    """.reviewcompass/ になければ stages/feature-dependency.yaml を使う（開発リポジトリ互換）"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")

  def test_root_fallback_is_used_without_stages_file(self):
    """stages/ にもなければ直下の feature-dependency.yaml を使う"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")

  def test_missing_file_returns_bootstrap_guidance(self):
    """feature-dependency.yaml がない場合は立ち上げ案内を返す（エラーにしない）"""
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "feature_definition_required")
    reason = data["next_action"]["reason"]
    self.assertIn("feature-dependency.yaml が見つかりません", reason)
    self.assertIn("intent", reason)
    self.assertIn("feature-partitioning", reason)
    self.assertIn(".reviewcompass/feature-dependency.yaml", reason)

  def test_missing_key_returns_bootstrap_guidance_with_distinct_reason(self):
    """ファイルはあるが feature_order キーがない場合は、理由を区別して案内する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      features={"appfeat-b": {"depends_on": {"appfeat-a": "hard"}}},
    )
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "feature_definition_required")
    reason = data["next_action"]["reason"]
    self.assertIn("feature_order", reason)
    self.assertIn("定義されていません", reason)
    self.assertNotIn("見つかりません", reason)

  def test_unreadable_file_is_deviation(self):
    """ファイルはあるが YAML として読めない場合は案内ではなく遮断する（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    broken = cwd / "stages" / "feature-dependency.yaml"
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("feature_order: [unclosed\n", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_empty_file_is_deviation_with_record_prompting_reason(self):
    """空ファイルは遮断し、理由で feature_order の記録を促す（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    empty = cwd / "stages" / "feature-dependency.yaml"
    empty.parent.mkdir(parents=True, exist_ok=True)
    empty.write_text("", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("空", reasons)
    self.assertIn("feature_order", reasons)
    self.assertIn("記録", reasons)

  def test_undecodable_file_is_deviation(self):
    """UTF-8 として読めないファイルも遮断する（Req 8 受入 9、MLE-DEC-005。デコード失敗の fail-closed）"""
    cwd = Path(self.tmpdir)
    binary = cwd / "stages" / "feature-dependency.yaml"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_bytes(b"\xff\xfe\x00broken\x80binary")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_non_mapping_top_level_is_deviation(self):
    """最上位が連想配列でないファイルは遮断する（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    bad = cwd / "stages" / "feature-dependency.yaml"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("- foundation\n- runtime\n", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_order_contradicting_dependency_is_deviation(self):
    """依存される機能が後ろに並ぶ feature_order は逸脱として理由つきで指摘する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-b", "appfeat-a"],
      features={"appfeat-b": {"depends_on": {"appfeat-a": "hard"}}},
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("feature_order が depends_on と矛盾", reasons)
    self.assertIn("appfeat-a", reasons)
    self.assertIn("appfeat-b", reasons)

  def test_cyclic_dependency_is_deviation(self):
    """depends_on の循環依存は逸脱として検出する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a", "appfeat-b"],
      features={
        "appfeat-a": {"depends_on": {"appfeat-b": "hard"}},
        "appfeat-b": {"depends_on": {"appfeat-a": "hard"}},
      },
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    reasons = " ".join(data["reasons"])
    self.assertIn("循環", reasons)

  def test_dev_repo_stages_file_defines_seven_features(self):
    """開発リポジトリの stages/feature-dependency.yaml が 7 機能の feature_order を持つ"""
    data = yaml.safe_load(
      (REPO_ROOT / "stages" / "feature-dependency.yaml").read_text(encoding="utf-8"),
    )
    self.assertEqual(data.get("feature_order"), FEATURE_ORDER)

  def test_completed_state_is_preserved_with_file_based_order(self):
    """ファイル由来の feature_order でも全機能完了の判定は従来どおり completed"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=list(FEATURE_ORDER),
    )
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "completed")


if __name__ == "__main__":
  unittest.main()
