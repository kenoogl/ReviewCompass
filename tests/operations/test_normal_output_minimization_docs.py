from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_normal_output_minimization_discipline_exists():
  path = ROOT / ".reviewcompass" / "guidance" / "discipline_normal_output_minimization.md"
  text = path.read_text(encoding="utf-8")

  assert "正常系出力最小化" in text
  assert "正常系" in text
  assert "異常系" in text
  assert "`--json`" in text
  assert "非定型処理" in text
  assert "棚卸し" in text


def test_tools_readme_points_to_common_output_contract():
  text = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")

  assert "共通 CLI 出力契約" in text
  assert ".reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md" in text
  assert "2026-06-19-normal-output-minimization-tool-inventory.yaml" in text


def test_normal_output_minimization_inventory_is_machine_readable():
  path = ROOT / "docs" / "notes" / (
    "2026-06-19-normal-output-minimization-tool-inventory.yaml"
  )
  inventory = yaml.safe_load(path.read_text(encoding="utf-8"))

  assert inventory["policy_source"] == (
    "docs/disciplines/discipline_normal_output_minimization.md"
  )
  assert inventory["implementation_policy"] == (
    ".reviewcompass/backlog/plans/plan-2026-06-23-normal-output-minimization-rollout.yaml"
  )
  assert inventory["default_contract"]["ok_human_output"] == "minimal"
  assert inventory["default_contract"]["json_output"] == "complete"

  paths = {entry["path"]: entry for entry in inventory["tools"]}
  assert paths["tools/check-workflow-action.py"]["status"] == "partially_enforced"
  assert paths["tools/commit-from-current-staged.py"]["status"] == "enforced"
  assert paths["tools/api_providers/run_review.py"]["status"] == "enforced"
  assert paths["tools/api_providers/run_role.py"]["status"] == "enforced"
  assert paths["tools/api_providers/run_review.py"]["priority"] == "high"
  assert paths["tools/api_providers/run_role.py"]["priority"] == "high"
  assert paths["tools/experiments/_experiment_n_model.py"]["category"] == "experiment"


def test_normal_output_minimization_policy_records_shared_formatter_strategy():
  path = ROOT / ".reviewcompass" / "backlog" / "plans" / (
    "plan-2026-06-23-normal-output-minimization-rollout.yaml"
  )
  text = path.read_text(encoding="utf-8")

  assert "共通 formatter / 出力ヘルパー" in text
  assert "優先度の高い既存 CLI から薄く接続" in text
  assert "個別対応だけで直すのではなく" in text
  assert "tools/api_providers/run_review.py" in text
  assert "tools/experiments/_experiment_n_model.py" in text
