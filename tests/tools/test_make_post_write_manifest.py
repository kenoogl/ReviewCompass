"""tools/make-post-write-manifest.py の単体テスト。

「事例より正本」改善（案2）：書き込み後検証 manifest を過去事例から手で写すのをやめ、
正本（check-workflow-action.py の evaluate_post_write_manifest_state /
review_run_traceability_satisfied）が「completed」と判定する形を、review-run から生成する。

テストは生成物を**正本の判定関数**に通して結果を確認する。TDD 規律に従い実装前に作成。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_make_post_write_manifest -v
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
TOOL = REPO_ROOT / "tools" / "make-post-write-manifest.py"


def _load_cwa():
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "cwa_under_test_make_post_write_manifest",
    REPO_ROOT / "tools" / "check-workflow-action.py")
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m


def _dump(path, data):
  Path(path).parent.mkdir(parents=True, exist_ok=True)
  Path(path).write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _build_review_run(rundir, triage_items=None, model_id="gemini-3.5-flash"):
  """正本 review_run_traceability_satisfied を満たす最小 review-run を組む。"""
  rundir = Path(rundir)
  (rundir / "raw").mkdir(parents=True, exist_ok=True)
  raw = rundir / "raw" / f"{model_id}.round-1.txt"
  raw.write_text("findings: []\n", encoding="utf-8")
  raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
  _dump(rundir / "rounds.yaml", {
    "round_id": "round-1",
    "purpose": "post_write_verification",
    "criteria": "post_write_verification",
    "model_results": [{
      "model_id": model_id,
      "provider": "gemini-api",
      "role": "primary",
      "raw_path": f"raw/{model_id}.round-1.txt",
      "raw_sha256": raw_sha,
      "parse_status": "parsed",
    }],
  })
  triage_status = "no_findings" if not triage_items else "triaged"
  _dump(rundir / "model-result-summary.yaml", {
    "run_id": rundir.name,
    "models": [{"model_id": model_id, "triage_status": triage_status,
                "findings_count": len(triage_items or [])}],
  })
  _dump(rundir / "triage.yaml", {
    "run_id": rundir.name, "triage_status": triage_status,
    "items": triage_items or [],
  })
  _dump(rundir / "target-manifest.yaml", {"run_id": rundir.name, "target_files": []})
  return model_id


def _run_tool(tmp, *args):
  return subprocess.run(
    [sys.executable, str(TOOL), *args],
    cwd=tmp, capture_output=True, text=True, errors="replace", timeout=30)


class MakePostWriteManifestTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmp)
    self.cwa = _load_cwa()

  def test_no_findings_manifest_is_completed(self):
    """所見0の review-run から生成した manifest を正本が completed と判定する。"""
    rundir = Path(self.tmp) / ".reviewcompass/evidence/review-runs/run1"
    _build_review_run(rundir)
    (Path(self.tmp) / "doc.md").write_text("# 文書\n本文\n", encoding="utf-8")
    out = ".reviewcompass/post-write-verification/post-write-test-001.yaml"
    r = _run_tool(self.tmp,
                  "--review-run-dir", ".reviewcompass/evidence/review-runs/run1",
                  "--target", "doc.md",
                  "--out", out)
    self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
    self.assertEqual(r.stdout.count("\n"), 1)
    self.assertIn("manifest 生成", r.stdout)
    status, _manifest = self.cwa.evaluate_post_write_manifest_state(self.tmp, ["doc.md"])
    self.assertEqual(status, "completed", f"正本判定が completed でない: {status}")

  def test_human_required_is_not_completed(self):
    """未解決の本質的指摘（human_required）があれば completed にしない（fail-closed）。"""
    rundir = Path(self.tmp) / ".reviewcompass/evidence/review-runs/run2"
    _build_review_run(rundir, triage_items=[{
      "source_model": "gemini-3.5-flash",
      "source_raw_path": "raw/gemini-3.5-flash.round-1.txt",
      "decision_status": "human_required",
      "final_label": None,
    }])
    (Path(self.tmp) / "doc2.md").write_text("# 文書2\n", encoding="utf-8")
    out = ".reviewcompass/post-write-verification/post-write-test-002.yaml"
    r = _run_tool(self.tmp,
                  "--review-run-dir", ".reviewcompass/evidence/review-runs/run2",
                  "--target", "doc2.md",
                  "--out", out)
    self.assertNotEqual(r.returncode, 0,
                        "未解決の本質的指摘があれば非ゼロで終了すべき")
    status, _manifest = self.cwa.evaluate_post_write_manifest_state(self.tmp, ["doc2.md"])
    self.assertNotEqual(status, "completed",
                        f"human_required を completed と判定してはいけない: {status}")

  def test_missing_review_run_is_error(self):
    """review-run ディレクトリが無ければエラー（非ゼロ）。"""
    (Path(self.tmp) / "doc3.md").write_text("# 文書3\n", encoding="utf-8")
    r = _run_tool(self.tmp,
                  "--review-run-dir", "does/not/exist",
                  "--target", "doc3.md",
                  "--out", ".reviewcompass/post-write-verification/x.yaml")
    self.assertNotEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")

  def test_summary_out_of_sync_gives_actionable_message(self):
    """triage は decided なのに summary.triage_status が古いと、make-triage-decision
    での再生成を促す分かりやすい案内を出す（『pending』で放り出さない）。"""
    rundir = Path(self.tmp) / ".reviewcompass/evidence/review-runs/run4"
    _build_review_run(rundir, triage_items=[{
      "source_model": "gemini-3.5-flash",
      "source_raw_path": "raw/gemini-3.5-flash.round-1.txt",
      "decision_status": "decided",
      "final_label": "leave-as-is",
    }])
    # summary を古いまま（triage_pending）に上書きして triage との不一致を作る
    _dump(rundir / "model-result-summary.yaml", {
      "run_id": "run4",
      "models": [{"model_id": "gemini-3.5-flash",
                  "triage_status": "triage_pending", "findings_count": 1}],
    })
    (Path(self.tmp) / "doc4.md").write_text("# 文書4\n", encoding="utf-8")
    r = _run_tool(self.tmp,
                  "--review-run-dir", ".reviewcompass/evidence/review-runs/run4",
                  "--target", "doc4.md",
                  "--out", ".reviewcompass/post-write-verification/post-write-test-004.yaml")
    self.assertNotEqual(r.returncode, 0,
                        f"不一致なら非ゼロ。stdout={r.stdout}\nstderr={r.stderr}")
    msg = r.stdout + r.stderr
    self.assertIn("make-triage-decision", msg,
                  f"再生成ツールへの案内が必要。msg={msg}")
    self.assertIn("triage", msg, f"triage との不一致である旨が必要。msg={msg}")


if __name__ == "__main__":
  unittest.main()
