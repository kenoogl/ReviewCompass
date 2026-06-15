"""tools/make-proxy-approval.py の単体テスト。

「事例より正本」改善（候補7・生成ツールの横展開）：proxy_model 裁定レコード
（proxy-approval.yaml・decisions/*.yaml）を過去事例から手で写すのをやめ、正本
（tools/api_providers/review_triage.py の _approval_errors / _proxy_decision_errors）が
受け入れる形を review-run と裁定入力から生成する。

テストは生成物を**正本の検証関数**へ通して合格することを確認する（固定の期待文字列でなく、
正本の判定に対する検証）。TDD 規律に従い実装前に作成。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_make_proxy_approval -v
"""

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "make-proxy-approval.py"
RUN_REL = ".reviewcompass/evidence/review-runs/run-r11"
PROXY_MODEL = "gemini-3.1-pro-preview"
TRIAGE_ACTIONS = ("review_triage_decide", "review_run_triage")


def _load_review_triage():
  """正本 review_triage を読み込む（既存テストと同手口）。"""
  pkg_dir = str(REPO_ROOT / "tools")
  if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)
  spec = importlib.util.spec_from_file_location(
    "review_triage_under_test",
    REPO_ROOT / "tools" / "api_providers" / "review_triage.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _dump(path, data):
  Path(path).parent.mkdir(parents=True, exist_ok=True)
  Path(path).write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _build_run(rundir, items):
  """正本検証に足る最小 review-run（rounds/triage/raw/プロンプト/応答）を組む。

  items: [{suffix, source_model, severity}] から finding_id・raw を生成する。
  """
  rundir = Path(rundir)
  (rundir / "raw").mkdir(parents=True, exist_ok=True)
  (rundir / "parsed").mkdir(parents=True, exist_ok=True)
  models = sorted({it["source_model"] for it in items})
  model_results = []
  for model_id in models:
    raw = rundir / "raw" / f"{model_id}.round-1.txt"
    raw.write_text(f"findings from {model_id}\n", encoding="utf-8")
    raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
    model_results.append({
      "model_id": model_id,
      "provider": "api",
      "role": "primary",
      "raw_path": f"raw/{model_id}.round-1.txt",
      "raw_sha256": raw_sha,
      "parse_status": "parsed",
    })
  _dump(rundir / "rounds.yaml", {
    "round_id": "round-1",
    "purpose": "triad-review",
    "criteria": "r11",
    "model_results": model_results,
  })
  triage_items = []
  for it in items:
    fid = f"{rundir.name}-{it['suffix']}"
    triage_items.append({
      "finding_id": fid,
      "run_id": rundir.name,
      "source_model": it["source_model"],
      "source_round": "round-1",
      "source_raw_path": f"raw/{it['source_model']}.round-1.txt",
      "severity_normalized": it["severity"],
      "target_location": "loc",
      "plain_language_summary": "s",
      "final_label": None,
      "decision_status": "human_required",
    })
  _dump(rundir / "triage.yaml", {
    "run_id": rundir.name, "triage_status": "draft", "items": triage_items})
  _dump(rundir / "model-result-summary.yaml", {
    "run_id": rundir.name,
    "models": [{"model_id": m, "triage_status": "triage_pending"} for m in models]})
  _dump(rundir / "target-manifest.yaml", {"run_id": rundir.name, "target_files": []})
  (rundir / "proxy-adjudication-prompt.md").write_text("# 裁定依頼\n", encoding="utf-8")
  (rundir / "proxy-adjudication-response.txt").write_text("裁定応答\n", encoding="utf-8")
  return {f"{rundir.name}-{it['suffix']}": it for it in items}


def _decisions_input(path, decisions):
  _dump(path, {
    "proxy_model_id": PROXY_MODEL,
    "decision_prompt_path": "proxy-adjudication-prompt.md",
    "raw_response_path": "proxy-adjudication-response.txt",
    "decisions": decisions,
  })


def _run_tool(tmp, *args):
  return subprocess.run(
    [sys.executable, str(TOOL), *args],
    cwd=tmp, capture_output=True, text=True, errors="replace", timeout=30)


class MakeProxyApprovalTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmp)
    self.rt = _load_review_triage()
    self.rundir = Path(self.tmp) / RUN_REL
    self.rundir.mkdir(parents=True, exist_ok=True)

  def _assert_truth_passes(self, important_labels):
    """生成した proxy-approval を正本 _approval_errors に通し、エラー0を確認。"""
    approval_path = self.rundir / "proxy-approval.yaml"
    approval = yaml.safe_load(approval_path.read_text(encoding="utf-8"))
    errors = self.rt._approval_errors(
      approval,
      self.rundir,
      approval_path,
      TRIAGE_ACTIONS,
      list(important_labels.keys()),
      important_labels,
    )
    self.assertEqual(errors, [], f"正本検証でエラー: {errors}")

  def test_important_finding_generates_passing_records(self):
    """ERROR 所見を must-fix にすると decision と proxy-approval が正本検証を通る。"""
    ids = _build_run(self.rundir, [{"suffix": "gpt-5.5-adversarial-001",
                                    "source_model": "gpt-5.5", "severity": "ERROR"}])
    fid = next(iter(ids))
    _decisions_input(Path(self.tmp) / "dec.yaml", [{
      "finding_id": fid, "final_label": "must-fix",
      "rationale": "要件として欠陥のため修正必須",
      "rejected_options": {"should-fix": "改善では足りない", "leave-as-is": "放置不可"}}])
    res = _run_tool(self.tmp, "--review-run-dir", RUN_REL, "--decisions", "dec.yaml")
    self.assertEqual(res.returncode, 0, res.stderr)
    self.assertTrue((self.rundir / "proxy-approval.yaml").is_file())
    self.assertTrue(any((self.rundir / "decisions").glob("*.yaml")))
    self._assert_truth_passes({fid: "must-fix"})

  def test_must_fix_label_on_warn_is_treated_important(self):
    """WARN でも must-fix ラベルなら重要件として decision が生成され正本を通る。"""
    ids = _build_run(self.rundir, [{"suffix": "claude-sonnet-4-6-primary-001",
                                    "source_model": "claude-sonnet-4-6", "severity": "WARN"}])
    fid = next(iter(ids))
    _decisions_input(Path(self.tmp) / "dec.yaml", [{
      "finding_id": fid, "final_label": "must-fix",
      "rationale": "本質的欠陥のため必須",
      "rejected_options": {"should-fix": "不足", "leave-as-is": "不可"}}])
    res = _run_tool(self.tmp, "--review-run-dir", RUN_REL, "--decisions", "dec.yaml")
    self.assertEqual(res.returncode, 0, res.stderr)
    self._assert_truth_passes({fid: "must-fix"})

  def test_non_important_finding_excluded_from_approval(self):
    """INFO→leave-as-is（非重要）は approved_finding_ids/decisions に含めない。"""
    ids = _build_run(self.rundir, [
      {"suffix": "gpt-5.5-adversarial-001", "source_model": "gpt-5.5", "severity": "ERROR"},
      {"suffix": "claude-sonnet-4-6-primary-001", "source_model": "claude-sonnet-4-6",
       "severity": "INFO"}])
    fids = list(ids)
    err_fid = next(f for f in fids if "gpt-5.5" in f)
    info_fid = next(f for f in fids if "claude" in f)
    _decisions_input(Path(self.tmp) / "dec.yaml", [
      {"finding_id": err_fid, "final_label": "must-fix", "rationale": "必須",
       "rejected_options": {"should-fix": "不足", "leave-as-is": "不可"}},
      {"finding_id": info_fid, "final_label": "leave-as-is", "rationale": "情報提供で対処不要"}])
    res = _run_tool(self.tmp, "--review-run-dir", RUN_REL, "--decisions", "dec.yaml")
    self.assertEqual(res.returncode, 0, res.stderr)
    approval = yaml.safe_load((self.rundir / "proxy-approval.yaml").read_text(encoding="utf-8"))
    self.assertIn(err_fid, approval["approved_finding_ids"])
    self.assertNotIn(info_fid, approval["approved_finding_ids"])
    self._assert_truth_passes({err_fid: "must-fix"})

  def test_important_finding_without_rejected_options_fails_closed(self):
    """重要件で rejected_options を欠くと正本検証が落ちるため、ツールは非ゼロで止まる。"""
    ids = _build_run(self.rundir, [{"suffix": "gpt-5.5-adversarial-001",
                                    "source_model": "gpt-5.5", "severity": "ERROR"}])
    fid = next(iter(ids))
    _decisions_input(Path(self.tmp) / "dec.yaml", [{
      "finding_id": fid, "final_label": "must-fix", "rationale": "必須"}])
    res = _run_tool(self.tmp, "--review-run-dir", RUN_REL, "--decisions", "dec.yaml")
    self.assertNotEqual(res.returncode, 0)


if __name__ == "__main__":
  unittest.main()
