# tools/api_providers/tests/test_review_triage.py
# review-run triage 補助コマンドの TDD テスト。

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.review_triage import main


def _write_review_run(tmp_path):
  run_dir = tmp_path / "review-run"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True)
  raw_file = raw_dir / "claude-sonnet-4-6.round-1.txt"
  raw_file.write_text("raw\n", encoding="utf-8")
  target = tmp_path / "target.md"
  target.write_text("target\n", encoding="utf-8")
  raw_sha = "0" * 64
  target_sha = "1" * 64
  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "target_files": [
          {
            "path": str(target),
            "sha256": target_sha,
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
        "round_id": "round-1",
        "target_files": [
          {
            "path": str(target),
            "sha256": target_sha,
          },
        ],
        "model_results": [
          {
            "model_id": "claude-sonnet-4-6",
            "provider": "anthropic-api",
            "role": "primary",
            "raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "raw_sha256": raw_sha,
            "parse_status": "parsed",
          },
          {
            "model_id": "gpt-5.4",
            "provider": "openai-api",
            "role": "adversarial",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "raw_sha256": "2" * 64,
            "parse_status": "parsed",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "model-result-summary.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "models": [
          {
            "model_id": "claude-sonnet-4-6",
            "raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "parse_status": "parsed",
            "triage_status": "triage_pending",
            "findings_count": 1,
            "must_fix_count": 0,
            "should_fix_count": 0,
            "leave_as_is_count": 0,
            "human_required_count": 1,
          },
          {
            "model_id": "gpt-5.4",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "parse_status": "parsed",
            "triage_status": "no_findings",
            "findings_count": 0,
            "must_fix_count": 0,
            "should_fix_count": 0,
            "leave_as_is_count": 0,
            "human_required_count": 0,
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
        "run_id": run_dir.name,
        "triage_status": "draft",
        "items": [
          {
            "finding_id": "finding-001",
            "source_model": "claude-sonnet-4-6",
            "source_round": "round-1",
            "source_raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "severity_original": "ERROR",
            "severity_normalized": "ERROR",
            "target_location": "target.md",
            "plain_language_summary": "契約違反の可能性",
            "final_label": None,
            "decision_status": "human_required",
            "decision_actor": None,
            "decision_actor_type": "human",
            "decision_at": None,
            "decision_reason": "仕様に影響する",
            "applied_files": [],
            "superseded_by": None,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return run_dir


def test_list_pending_outputs_plain_markdown_with_recommendation(tmp_path, capsys):
  """未判断 item を平易な説明と推薦案付き Markdown で出力する。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(["list-pending", "--review-run-dir", str(run_dir)])

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "finding-001" in output
  assert "契約違反の可能性" in output
  assert "must-fix" in output
  assert "仕様・契約" in output


def test_decide_updates_triage_and_model_summary(tmp_path):
  """人判断を triage と model-result-summary に反映する。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
    ]
  )

  assert exit_code == 0
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  assert item["decision_status"] == "decided"
  assert item["final_label"] == "must-fix"
  assert item["decision_actor"] == "human"
  assert triage["triage_status"] == "decided"

  summary = yaml.safe_load(
    (run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  model = summary["models"][0]
  assert model["triage_status"] == "triaged"
  assert model["must_fix_count"] == 1
  assert model["human_required_count"] == 0


def test_manifest_template_records_review_run_and_unresolved_count(tmp_path, capsys):
  """完了 manifest 雛形を review_run 参照と coverage matrix 付きで出力する。"""
  run_dir = _write_review_run(tmp_path)
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
    ]
  )

  exit_code = main(["manifest-template", "--review-run-dir", str(run_dir)])

  assert exit_code == 0
  manifest = yaml.safe_load(capsys.readouterr().out)
  assert manifest["status"] == "completed"
  assert manifest["unresolved_substantive_findings"] == 0
  assert manifest["review_run"]["path"] == str(run_dir)
  assert manifest["review_run"]["summary_path"].endswith("model-result-summary.yaml")
  assert manifest["required_verifiers"] == ["claude-sonnet-4-6", "gpt-5.4"]
  assert [entry["verifier"] for entry in manifest["verifications"]] == [
    "claude-sonnet-4-6",
    "gpt-5.4",
  ]
  assert manifest["verifications"][0]["target_files"] == manifest["target_files"]
  assert manifest["verifications"][0]["target_sha256"] == manifest["target_sha256"]


def test_manifest_template_fails_when_human_required_remains(tmp_path, capsys):
  """未判断 finding が残る場合は manifest 雛形を出力しない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(["manifest-template", "--review-run-dir", str(run_dir)])

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "human_required" in captured.err


def test_write_manifest_creates_file_after_all_decisions(tmp_path):
  """write-manifest は解決済み review-run から manifest ファイルを書く。"""
  run_dir = _write_review_run(tmp_path)
  output_path = tmp_path / "post-write-2026-06-03-999.yaml"
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
    ]
  )

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 0
  manifest = yaml.safe_load(output_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"
  assert manifest["verifications"][1]["verifier"] == "gpt-5.4"


def test_write_manifest_auto_chooses_next_post_write_name(tmp_path, monkeypatch, capsys):
  """--out auto は .reviewcompass/post-write-verification の次番号へ manifest を書く。"""
  cwd = tmp_path / "repo"
  cwd.mkdir()
  monkeypatch.chdir(cwd)
  existing_dir = cwd / ".reviewcompass" / "post-write-verification"
  existing_dir.mkdir(parents=True)
  (existing_dir / "post-write-2026-06-03-001.yaml").write_text(
    "status: completed\n",
    encoding="utf-8",
  )
  run_dir = _write_review_run(cwd)
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
    ]
  )

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", "auto",
    ]
  )

  assert exit_code == 0
  output = capsys.readouterr().out
  created_path = existing_dir / "post-write-2026-06-03-002.yaml"
  assert str(created_path) in output
  assert created_path.is_file()
  manifest = yaml.safe_load(created_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"
