"""review-wave-summary サブコマンドの単体テスト（T-012、Requirement 10）。

TDD 規律（AGENTS.md）に従い、実装前に作成。
対象設計：design.md §review-wave 要約コマンドモデル §1〜§6。
実行：python3 -m unittest tests.tools.test_review_wave_summary -v
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
FEATURES = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def run(args, cwd):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )


def write_spec(cwd, feature, approved=True):
  five = {s: approved for s in ["drafting", "triad-review", "review-wave", "alignment", "approval"]}
  ws = {
    "intent": {"drafting": True, "review": True, "approval": True, "reference": "stages/intent.yaml"},
    "feature-partitioning": {"candidate-proposal": True, "approval": True},
    "requirements": dict(five),
    "design": dict(five),
    "tasks": dict(five),
    "implementation": dict(five),
  }
  d = {
    "feature_name": feature,
    "workflow_state": ws,
    "reopened": {},
    "recheck": {"upstream_change_pending": False, "impacted_downstream_phases": []},
  }
  p = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def write_dep(cwd):
  p = Path(cwd) / "stages" / "feature-dependency.yaml"
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(
    yaml.safe_dump(
      {"feature_order": FEATURES, "features": {f: {"depends_on": []} for f in FEATURES}},
      allow_unicode=True,
    ),
    encoding="utf-8",
  )


def build_repo(cwd):
  for f in FEATURES:
    write_spec(cwd, f)
  write_dep(cwd)


class ReviewWaveSummaryTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())

  def tearDown(self):
    shutil.rmtree(self.tmp, ignore_errors=True)

  def test_json_schema_and_ok(self):
    build_repo(self.tmp)
    r = run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(r.returncode, 0, r.stderr)
    d = json.loads(r.stdout)
    for k in ["schema_version", "status", "features", "triage", "dependencies", "carry_forward", "errors"]:
      self.assertIn(k, d)
    self.assertEqual(d["status"], "ok")
    self.assertEqual(len(d["features"]), 7)
    f0 = d["features"][0]
    self.assertEqual(f0["name"], "foundation")
    self.assertIn("coverage", f0)
    self.assertIn("phases", f0)
    self.assertIn("recheck", f0)
    # phases は phase 名→{stage: bool} のオブジェクト（配列ではない）
    self.assertIsInstance(f0["phases"], dict)
    self.assertIn("requirements", f0["phases"])
    self.assertIsInstance(f0["phases"]["requirements"]["approval"], bool)
    # triage の 3 件数キー
    for k in ["unresolved", "draft", "human_required"]:
      self.assertIn(k, d["triage"])
    self.assertIn("feature_order", d["dependencies"])
    self.assertIn("unmet", d["dependencies"])
    self.assertIn("unresolved", d["carry_forward"])

  def test_missing_feature_dependency_is_insufficient(self):
    for f in FEATURES:
      write_spec(self.tmp, f)
    # feature-dependency.yaml を作らない（必須記録の欠落）
    r = run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(r.returncode, 2)
    d = json.loads(r.stdout)
    self.assertEqual(d["status"], "insufficient")
    self.assertTrue(d["errors"])

  def test_missing_spec_is_insufficient(self):
    build_repo(self.tmp)
    (self.tmp / ".reviewcompass" / "specs" / "runtime" / "spec.json").unlink()
    r = run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(r.returncode, 2)
    self.assertEqual(json.loads(r.stdout)["status"], "insufficient")

  def test_unparseable_triage_is_insufficient(self):
    build_repo(self.tmp)
    tdir = self.tmp / ".reviewcompass" / "evidence" / "review-runs" / "run-x"
    tdir.mkdir(parents=True)
    (tdir / "triage.yaml").write_text("items: [unclosed\n", encoding="utf-8")
    r = run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(r.returncode, 2)
    self.assertEqual(json.loads(r.stdout)["status"], "insufficient")

  def test_absent_triage_is_ok_zero(self):
    build_repo(self.tmp)
    # review-runs ディレクトリなし＝任意記録の非在は ok・0 件
    r = run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(r.returncode, 0, r.stderr)
    d = json.loads(r.stdout)
    self.assertEqual(d["status"], "ok")
    self.assertEqual(d["triage"], {"unresolved": 0, "draft": 0, "human_required": 0})

  def test_triage_counts_axes(self):
    build_repo(self.tmp)
    tdir = self.tmp / ".reviewcompass" / "evidence" / "review-runs" / "run-1"
    tdir.mkdir(parents=True)
    (tdir / "triage.yaml").write_text(
      yaml.safe_dump(
        {
          "run_id": "run-1",
          "triage_status": "draft",
          "items": [
            {"finding_id": "a", "decision_status": "draft"},
            {"finding_id": "b", "decision_status": "human_required"},
            {"finding_id": "c", "decision_status": "decided", "final_label": "should-fix"},
          ],
        },
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    d = json.loads(run(["review-wave-summary", "--json"], self.tmp).stdout)
    # unresolved（item 単位）＝decided 以外＝a, b の 2 件
    self.assertEqual(d["triage"]["unresolved"], 2)
    # human_required（item 単位）＝1 件
    self.assertEqual(d["triage"]["human_required"], 1)
    # draft（run 単位）＝triage_status draft の run が 1 件
    self.assertEqual(d["triage"]["draft"], 1)

  def test_triage_dedup_by_run_id_prefers_evidence(self):
    build_repo(self.tmp)
    # 同一 run_id が新旧両パスに存在 → 新パス（evidence）を採用し 1 ファイルだけ数える
    for rel in [
      ".reviewcompass/evidence/review-runs/dup/triage.yaml",
      ".reviewcompass/specs/_cross_feature/reviews/dup/triage.yaml",
    ]:
      p = self.tmp / rel
      p.parent.mkdir(parents=True, exist_ok=True)
      p.write_text(
        yaml.safe_dump(
          {"run_id": "dup", "triage_status": "decided",
           "items": [{"finding_id": "x", "decision_status": "human_required"}]},
          allow_unicode=True,
        ),
        encoding="utf-8",
      )
    d = json.loads(run(["review-wave-summary", "--json"], self.tmp).stdout)
    # 重複排除で human_required は 1 件（2 件にならない）
    self.assertEqual(d["triage"]["human_required"], 1)

  def test_read_only(self):
    build_repo(self.tmp)
    spec = self.tmp / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    before = spec.read_text()
    run(["review-wave-summary"], self.tmp)
    run(["review-wave-summary", "--json"], self.tmp)
    self.assertEqual(spec.read_text(), before)

  def test_markdown_default(self):
    build_repo(self.tmp)
    r = run(["review-wave-summary"], self.tmp)
    self.assertEqual(r.returncode, 0, r.stderr)
    self.assertIn("review-wave", r.stdout.lower())
    with self.assertRaises(json.JSONDecodeError):
      json.loads(r.stdout)

  def test_save_writes_output_and_read_only(self):
    build_repo(self.tmp)
    out = self.tmp / "summary.json"
    spec = self.tmp / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    before = spec.read_text()
    r = run(["review-wave-summary", "--json", "--out", str(out)], self.tmp)
    self.assertEqual(r.returncode, 0, r.stderr)
    self.assertTrue(out.is_file())
    saved = json.loads(out.read_text(encoding="utf-8"))
    self.assertEqual(saved["status"], "ok")
    # 保存しても spec.json は不変（読み取り専用）
    self.assertEqual(spec.read_text(), before)

  def test_save_default_location(self):
    build_repo(self.tmp)
    r = run(["review-wave-summary", "--save"], self.tmp)
    self.assertEqual(r.returncode, 0, r.stderr)
    saved = self.tmp / ".reviewcompass" / "specs" / "_cross_feature" / "reviews" / "review-wave-summary.md"
    self.assertTrue(saved.is_file())
    self.assertIn("review-wave", saved.read_text(encoding="utf-8").lower())
    # --json --save は .json で保存
    r2 = run(["review-wave-summary", "--json", "--save"], self.tmp)
    self.assertEqual(r2.returncode, 0, r2.stderr)
    saved_json = self.tmp / ".reviewcompass" / "specs" / "_cross_feature" / "reviews" / "review-wave-summary.json"
    self.assertEqual(json.loads(saved_json.read_text(encoding="utf-8"))["status"], "ok")

  def test_dependencies_unmet(self):
    for f in FEATURES:
      write_spec(self.tmp, f, approved=(f != "foundation"))
    # foundation は未承認、runtime/evaluation は foundation に依存
    p = self.tmp / "stages" / "feature-dependency.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    deps = {f: {"depends_on": []} for f in FEATURES}
    deps["runtime"]["depends_on"] = ["foundation"]
    deps["evaluation"]["depends_on"] = ["foundation"]
    p.write_text(yaml.safe_dump({"feature_order": FEATURES, "features": deps}, allow_unicode=True), encoding="utf-8")
    d = json.loads(run(["review-wave-summary", "--json"], self.tmp).stdout)
    unmet_pairs = {(u["feature"], u["depends_on"]) for u in d["dependencies"]["unmet"]}
    self.assertIn(("runtime", "foundation"), unmet_pairs)
    self.assertIn(("evaluation", "foundation"), unmet_pairs)

  def test_carry_forward_count(self):
    build_repo(self.tmp)
    reg = self.tmp / "learning" / "workflow" / "carry-forward-register" / "reviewcompass-import.yaml"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
      yaml.safe_dump(
        {"items": [
          {"id": "A-1", "status": "resolved"},
          {"id": "A-2", "status": "in_progress"},
          {"id": "A-3"},
        ]},
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    d = json.loads(run(["review-wave-summary", "--json"], self.tmp).stdout)
    # resolved 以外（in_progress, 未設定）の 2 件
    self.assertEqual(d["carry_forward"]["unresolved"], 2)

  def test_recheck_reflected(self):
    build_repo(self.tmp)
    spec_path = self.tmp / ".reviewcompass" / "specs" / "workflow-management" / "spec.json"
    sd = json.loads(spec_path.read_text(encoding="utf-8"))
    sd["recheck"] = {"upstream_change_pending": True, "impacted_downstream_phases": ["implementation"]}
    spec_path.write_text(json.dumps(sd, ensure_ascii=False, indent=2), encoding="utf-8")
    d = json.loads(run(["review-wave-summary", "--json"], self.tmp).stdout)
    wm = next(f for f in d["features"] if f["name"] == "workflow-management")
    self.assertTrue(wm["recheck"]["upstream_change_pending"])
    self.assertEqual(wm["recheck"]["impacted_downstream_phases"], ["implementation"])


if __name__ == "__main__":
  unittest.main()
