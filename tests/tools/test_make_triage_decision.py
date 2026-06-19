"""tools/make-triage-decision.py の単体テスト。

「事例より正本」（§4-7 拡大）：トリアージ（所見の仕分け）決定を review-run に記録する
とき、triage.yaml と model-result-summary.yaml を手で2か所そろえる同期ミスを防ぐ。
本ツールは決定を triage.yaml に書き、model-result-summary.yaml の triage_status と件数を
triage から再計算し、全件 decided なら正本 review_run_traceability_satisfied へ通す。

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_make_triage_decision -v
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "make-triage-decision.py"


def _build_review_run(run_dir):
  """最小で整合した review-run（1モデル・1所見・未決定）を作る。"""
  (run_dir / "raw").mkdir(parents=True, exist_ok=True)
  raw = run_dir / "raw" / "m1.round-1.txt"
  raw.write_text("findings:\n  - severity: WARN\n", encoding="utf-8")
  raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()

  (run_dir / "target-manifest.yaml").write_text(
    "run_id: test-run\ntarget_files:\n- path: T.md\n  sha256: x\n", encoding="utf-8")

  rounds = {
    "round_id": "round-1",
    "purpose": "post_write_verification",
    "model_results": [
      {
        "model_id": "m1",
        "raw_path": "raw/m1.round-1.txt",
        "raw_sha256": raw_sha,
        "parse_status": "parsed",
      }
    ],
  }
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(rounds, allow_unicode=True, sort_keys=False), encoding="utf-8")

  triage = {
    "run_id": "test-run",
    "triage_status": "draft",
    "decision_actor": None,
    "decision_actor_type": "human",
    "items": [
      {
        "finding_id": "F1",
        "run_id": "test-run",
        "source_model": "m1",
        "source_round": "round-1",
        "source_raw_path": "raw/m1.round-1.txt",
        "severity_original": "WARN",
        "severity_normalized": "WARN",
        "target_location": "## somewhere",
        "plain_language_summary": "ばらつきの指摘",
        "final_label": None,
        "decision_status": "human_required",
        "decision_actor": None,
        "decision_actor_type": "human",
        "decision_at": None,
        "decision_reason": "モデルの所見理由",
        "applied_files": [],
        "superseded_by": None,
      }
    ],
  }
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False), encoding="utf-8")

  summary = {
    "run_id": "test-run",
    "models": [
      {
        "model_id": "m1",
        "raw_path": "raw/m1.round-1.txt",
        "parse_status": "parsed",
        "triage_status": "triage_pending",
        "findings_count": 1,
        "findings_count_by_severity": {"WARN": 1},
        "must_fix_count": 0,
        "should_fix_count": 0,
        "leave_as_is_count": 0,
        "human_required_count": 0,
      }
    ],
  }
  (run_dir / "model-result-summary.yaml").write_text(
    yaml.safe_dump(summary, allow_unicode=True, sort_keys=False), encoding="utf-8")


class MakeTriageDecisionTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.run_rel = "rr"
    self.run_dir = self.tmp / self.run_rel
    _build_review_run(self.run_dir)

  def _run(self, *extra):
    return subprocess.run(
      [sys.executable, str(TOOL),
       "--review-run-dir", self.run_rel,
       *extra],
      cwd=str(self.tmp), capture_output=True, text=True, errors="replace", timeout=60)

  def _triage(self):
    return yaml.safe_load((self.run_dir / "triage.yaml").read_text(encoding="utf-8"))

  def _summary(self):
    return yaml.safe_load((self.run_dir / "model-result-summary.yaml").read_text(encoding="utf-8"))

  def test_records_leave_as_is_and_is_consistent(self):
    """leave-as-is を記録すると、triage と summary が整合し、正本判定OKで exit 0。"""
    r = self._run("--finding-id", "F1", "--label", "leave-as-is",
                  "--reason", "時点記録で正しい。誤検出として保全。",
                  "--actor", "user", "--decided-at", "2026-06-14T23:50:00+00:00")
    self.assertEqual(r.returncode, 0, f"全件 decided なら正本OKで通る。\nstdout={r.stdout}\nstderr={r.stderr}")
    self.assertEqual(r.stdout.count("\n"), 1)
    self.assertIn("全件 decided", r.stdout)
    item = self._triage()["items"][0]
    self.assertEqual(item["decision_status"], "decided")
    self.assertEqual(item["final_label"], "leave-as-is")
    self.assertEqual(item["decision_actor"], "user")
    self.assertEqual(item["decision_reason"], "時点記録で正しい。誤検出として保全。")
    model = self._summary()["models"][0]
    self.assertEqual(model["triage_status"], "triaged", "summary も triaged に再計算される")
    self.assertEqual(model["leave_as_is_count"], 1)
    self.assertEqual(model["human_required_count"], 0)

  def test_invalid_label_rejected(self):
    """不正なラベルは弾き、ファイルを書き換えない。"""
    r = self._run("--finding-id", "F1", "--label", "bogus", "--reason", "x")
    self.assertNotEqual(r.returncode, 0, f"不正ラベルは弾く。stdout={r.stdout}\nstderr={r.stderr}")
    self.assertEqual(self._triage()["items"][0]["decision_status"], "human_required",
                     "弾いたときは triage を書き換えない")

  def test_unknown_finding_id_rejected(self):
    """存在しない finding_id は弾く。"""
    r = self._run("--finding-id", "NOPE", "--label", "leave-as-is", "--reason", "x")
    self.assertNotEqual(r.returncode, 0, f"未知の finding_id は弾く。stdout={r.stdout}\nstderr={r.stderr}")


if __name__ == "__main__":
  unittest.main()
