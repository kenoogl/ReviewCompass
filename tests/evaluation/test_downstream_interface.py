"""T-011 のテスト：下流接合面と pytest 対象設定。"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_includes_evaluation_tests():
  """pytest の通常対象に tests/evaluation が含まれる。"""
  text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
  assert '"tests/evaluation"' in text


def test_downstream_artifact_paths_are_declared_in_layout_spec():
  """4 下流機能が読む代表成果物が layout_spec.yaml に宣言されている。"""
  text = (REPO_ROOT / "evaluation/analysis_layout/layout_spec.yaml").read_text(encoding="utf-8")
  for path in [
    "metrics/run_metrics.json",
    "metrics/finding_metrics.json",
    "metrics/treatment_metrics.json",
    "comparisons/treatment_comparisons.json",
    "comparisons/phase_comparisons.json",
    "caveats/caveat_register.json",
    "modes/mode_diff_report.json",
    "roles/role_diff_report.json",
  ]:
    assert path in text
