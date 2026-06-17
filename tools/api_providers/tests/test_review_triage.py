# tools/api_providers/tests/test_review_triage.py
# review-run triage 補助コマンドの TDD テスト。

import sys
import hashlib
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.review_triage import _is_post_write_target, main


def _write_review_run(tmp_path):
  run_dir = tmp_path / "review-run"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True)
  raw_file = raw_dir / "claude-sonnet-4-6.round-1.txt"
  raw_file.write_text("raw\n", encoding="utf-8")
  target = tmp_path / "target.md"
  target.write_text("target\n", encoding="utf-8")
  raw_sha = hashlib.sha256(raw_file.read_bytes()).hexdigest()
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


def _write_review_run_approval(run_dir, action, finding_ids=None, final_labels=None):
  """review-run 用のユーザ承認レコードを書く"""
  approval_path = run_dir / "approval.json"
  approval_path.write_text(
    yaml.safe_dump(
      {
        "approved_action": action,
        "approved_by": "user",
        "review_run_id": run_dir.name,
        "summary_presented_to_user": True,
        "triage_presented_to_user": True,
        "approved_finding_ids": finding_ids or ["finding-001"],
        "approved_final_labels": final_labels or {"finding-001": "must-fix"},
        "consumed": False,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return approval_path


def _write_proxy_decision(run_dir, finding_id="finding-001", final_label="must-fix"):
  """proxy_model 判断レコードと raw を review-run 配下に書く。"""
  decision_dir = run_dir / "proxy-decisions"
  decision_dir.mkdir()
  prompt_path = decision_dir / f"{finding_id}.prompt.md"
  prompt_path.write_text("proxy prompt with options and source raw\n", encoding="utf-8")
  raw_path = decision_dir / f"{finding_id}.raw.txt"
  raw_path.write_text("proxy raw response\n", encoding="utf-8")
  decision_path = decision_dir / f"{finding_id}.decision.yaml"
  decision_path.write_text(
    yaml.safe_dump(
      {
        "finding_id": finding_id,
        "approved_by": "proxy_model",
        "proxy_model_id": "gemini-3.1-pro-preview",
        "decision_prompt_path": f"proxy-decisions/{finding_id}.prompt.md",
        "source_raw_paths": ["raw/claude-sonnet-4-6.round-1.txt"],
        "candidate_options": [
          {
            "id": "option_1",
            "summary": "修正する",
          },
          {
            "id": "option_2",
            "summary": "延期する",
          },
        ],
        "selected_option": "option_1",
        "final_label": final_label,
        "rationale": "契約違反を防ぐため採用する",
        "rejected_options": {
          "option_2": "後続で手戻りが大きい",
        },
        "raw_response_path": f"proxy-decisions/{finding_id}.raw.txt",
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return decision_path


def _write_proxy_approval(run_dir, action, decision_path, final_label="must-fix"):
  """review-run 用の proxy_model 承認レコードを書く。"""
  approval_path = run_dir / "approval-proxy.yaml"
  approval_path.write_text(
    yaml.safe_dump(
      {
        "approved_action": action,
        "approved_by": "proxy_model",
        "proxy_model_id": "gemini-3.1-pro-preview",
        "review_run_id": run_dir.name,
        "summary_presented_to_user": True,
        "triage_presented_to_user": True,
        "approved_finding_ids": ["finding-001"],
        "approved_final_labels": {"finding-001": final_label},
        "proxy_decisions": {
          "finding-001": str(decision_path.relative_to(run_dir)),
        },
        "consumed": False,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return approval_path


def test_is_post_write_target_includes_prompt_and_agent_md_candidates():
  """レビュー挙動・agent 挙動を変える md は post-write 対象に含める。"""
  target_paths = [
    "AGENTS.md",
    "intent/INTENT.md",
    "intent/DESIGN_PRINCIPLES.md",
    "templates/todo/TODO_NEXT_SESSION.template.md",
    "templates/review/manual_dogfooding_review_template.md",
    "runtime/prompts/primary_detection/primary_reviewer.prompt.md",
    "runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md",
    "runtime/prompts/judgment/judgment_reviewer.prompt.md",
    "tools/api_providers/prompt_templates/anthropic_review.md",
    "tools/api_providers/prompt_templates/openai_review.md",
    "docs/logs/autonomous-parallel/run.yaml",
    "docs/workflow-evidence/future-generated.yaml",
    ".reviewcompass/specs/workflow-management/design.md",
  ]

  assert all(_is_post_write_target(path) for path in target_paths)


def test_is_post_write_target_excludes_structured_templates_for_separate_audit():
  """構造化 template は md post-write ではなく別監査へ寄せる。"""
  excluded_paths = [
    "config/api-settings.yaml",
    ".reviewcompass/specs/workflow-management/yaml-audit-spec.yaml",
    "runtime/config/config.yaml.template",
    "runtime/schemas/finding.schema.json",
    "templates/specs/spec.json.template",
  ]

  assert not any(_is_post_write_target(path) for path in excluded_paths)


def test_is_post_write_target_excludes_working_notes_for_lightweight_check():
  """docs/notes/working は strict post-write ではなく軽量自己精査へ回す。"""
  assert not _is_post_write_target(
    "docs/notes/working/2026-06-17-working-note-verification-trigger-policy.md"
  )
  assert _is_post_write_target("docs/notes/2026-06-17-regular-note.md")


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
  approval_path = _write_review_run_approval(run_dir, "review_triage_decide")

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(approval_path),
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


def test_decide_keeps_triage_draft_when_other_draft_item_remains(tmp_path):
  """個別 item に draft が残る限り triage_status は decided にしない。"""
  run_dir = _write_review_run(tmp_path)
  approval_path = _write_review_run_approval(run_dir, "review_triage_decide")
  triage_path = run_dir / "triage.yaml"
  triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
  second_item = dict(triage["items"][0])
  second_item.update({
    "finding_id": "finding-002",
    "severity_original": "WARN",
    "severity_normalized": "WARN",
    "final_label": "should-fix",
    "decision_status": "draft",
    "decision_actor": "main_session_llm_draft",
    "decision_actor_type": "llm_draft",
  })
  triage["items"].append(second_item)
  triage_path.write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0
  triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
  assert triage["triage_status"] == "draft"
  summary = yaml.safe_load(
    (run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  assert summary["models"][0]["triage_status"] == "triage_pending"


def test_list_pending_includes_draft_items(tmp_path, capsys):
  """draft item も未完了 triage として一覧に出す。"""
  run_dir = _write_review_run(tmp_path)
  triage_path = run_dir / "triage.yaml"
  triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
  triage["items"][0]["finding_id"] = "finding-draft"
  triage["items"][0]["severity_original"] = "WARN"
  triage["items"][0]["severity_normalized"] = "WARN"
  triage["items"][0]["final_label"] = "should-fix"
  triage["items"][0]["decision_status"] = "draft"
  triage_path.write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(["list-pending", "--review-run-dir", str(run_dir)])

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "finding-draft" in output
  assert "should-fix" in output


def test_decide_blocks_important_finding_without_user_approval(tmp_path, capsys):
  """ERROR / must-fix 相当の重要件は承認レコードなしでは decide できない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "codex",
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "approval" in captured.err
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert triage["items"][0]["decision_status"] == "human_required"


def test_manifest_template_records_review_run_and_unresolved_count(tmp_path, capsys):
  """完了 manifest 雛形を review_run 参照と coverage matrix 付きで出力する。"""
  run_dir = _write_review_run(tmp_path)
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "manifest-template",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(manifest_approval),
    ]
  )

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
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
      "--approval-record", str(manifest_approval),
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
  today = date.today().isoformat()
  (existing_dir / f"post-write-{today}-001.yaml").write_text(
    "status: completed\n",
    encoding="utf-8",
  )
  run_dir = _write_review_run(cwd)
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", "auto",
      "--approval-record", str(manifest_approval),
    ]
  )

  assert exit_code == 0
  output = capsys.readouterr().out
  created_path = existing_dir / f"post-write-{today}-002.yaml"
  assert str(created_path) in output
  assert created_path.is_file()
  manifest = yaml.safe_load(created_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"


def test_write_manifest_blocks_important_decisions_without_approval(tmp_path, capsys):
  """重要件を含む review-run は manifest 生成時にも承認レコードを要求する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "codex"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  output_path = tmp_path / "post-write-2026-06-03-999.yaml"

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 1
  assert not output_path.exists()
  captured = capsys.readouterr()
  assert "approval" in captured.err


def test_assert_apply_fixes_ready_blocks_when_human_required_remains(tmp_path, capsys):
  """未判断 finding が残る間は修正適用へ進めない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "human_required" in captured.err


def test_assert_apply_fixes_ready_requires_user_approval_for_fix_labels(tmp_path, capsys):
  """must-fix / should-fix の修正適用は利用者承認なしでは進めない。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "human"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "approval" in captured.err


def test_assert_apply_fixes_ready_passes_after_user_approval(tmp_path):
  """修正対象 finding が利用者承認済みなら修正適用へ進める。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "human"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  approval_path = _write_review_run_approval(
    run_dir,
    "review_run_apply_fixes",
    finding_ids=["finding-001"],
    final_labels={"finding-001": "must-fix"},
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0


def test_assert_apply_fixes_ready_passes_after_proxy_model_approval(tmp_path):
  """proxy_model の判断証跡が揃っていれば修正適用へ進める。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0


def test_assert_apply_fixes_ready_blocks_proxy_approval_without_raw(tmp_path, capsys):
  """proxy decision の raw response が欠ける場合は fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  (run_dir / "proxy-decisions" / "finding-001.raw.txt").unlink()
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "raw_response_path" in captured.err


def test_assert_apply_fixes_ready_blocks_proxy_approval_without_options(tmp_path, capsys):
  """proxy に提示した候補案セットが欠ける場合は fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
  decision.pop("candidate_options")
  decision_path.write_text(
    yaml.safe_dump(decision, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "candidate_options" in captured.err


def test_assert_apply_fixes_ready_blocks_proxy_approval_with_tampered_source_raw(tmp_path, capsys):
  """proxy decision の元 review raw が改変されていれば fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  (run_dir / "raw" / "claude-sonnet-4-6.round-1.txt").write_text(
    "tampered raw\n",
    encoding="utf-8",
  )
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "source_raw_paths sha256 mismatch" in captured.err


def _write_autonomous_report_artifacts(run_dir):
  """自動実行テスト報告に必要な最小成果物を書く。"""
  (run_dir / "must-fix-clusters.md").write_text(
    "# Must-fix clusters\n\n## WM-IMPL-MF-001\n",
    encoding="utf-8",
  )
  (run_dir / "must-fix-clusters.yaml").write_text(
    yaml.safe_dump(
      {
        "clusters": [
          {
            "cluster_id": "WM-IMPL-MF-001",
            "title": "raw response と triage 完了を機械確認できない",
            "plain_explanation": "レビュー結果が本当に揃ったかを機械確認できない。",
            "candidate_options": [
              {
                "option_id": "A",
                "summary": "raw と triage を開始前に機械検査する",
                "tradeoff": "実装量は増えるが取りこぼしを防げる",
              },
              {
                "option_id": "B",
                "summary": "文書規律だけで必須化する",
                "tradeoff": "軽いが機械的には防げない",
              },
            ],
            "recommended_option": "A",
            "recommended_reason": "同じ見落としを機械的に防げるため。",
            "proposed_final_label": "must-fix",
            "source_raw_paths": ["raw/claude-sonnet-4-6.round-1.txt"],
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "proxy-decision-summary.md").write_text(
    "# Proxy decision summary\n\n- WM-IMPL-MF-001: option A\n",
    encoding="utf-8",
  )
  report_path = run_dir / "autonomous-execution-report.md"
  report_path.write_text(
    "# 自動実行テスト報告\n\n"
    "## 生じた問題\n\n- raw / triage の自己申告化\n\n"
    "## 対応したこと\n\n- raw / triage を機械確認\n\n"
    "## 残った課題\n\n- completion_predicate の本格評価\n",
    encoding="utf-8",
  )
  ledger_path = run_dir / "autonomous-ledger.yaml"
  ledger_path.write_text(
    yaml.safe_dump(
      {
        "mode": "autonomous_parallel",
        "verdict": "OK",
        "exit_code": 0,
        "run_id": run_dir.name,
        "execution_evidence_snapshot": {
          "completed_tasks": ["target-bundle", "api-primary", "aggregate-review-run"],
          "parallelized_operations": ["api_review_calls"],
          "human_required_count": 0,
        },
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
  return report_path, ledger_path


def test_assert_review_report_ready_requires_plain_cluster_explanation(
  tmp_path,
  capsys,
):
  """重要所見 cluster に平易な説明がなければ fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  clusters_path = run_dir / "must-fix-clusters.yaml"
  clusters = yaml.safe_load(clusters_path.read_text(encoding="utf-8"))
  clusters["clusters"][0].pop("plain_explanation")
  clusters_path.write_text(
    yaml.safe_dump(clusters, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "plain_explanation" in captured.err


def test_assert_review_report_ready_requires_candidate_options(tmp_path, capsys):
  """重要所見 cluster に候補案がなければ fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  clusters_path = run_dir / "must-fix-clusters.yaml"
  clusters = yaml.safe_load(clusters_path.read_text(encoding="utf-8"))
  clusters["clusters"][0]["candidate_options"] = [
    {
      "option_id": "A",
      "summary": "raw と triage を機械検査する",
    },
  ]
  clusters_path.write_text(
    yaml.safe_dump(clusters, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "candidate_options" in captured.err


def test_assert_review_report_ready_requires_recommended_option(tmp_path, capsys):
  """重要所見 cluster に推薦案と理由がなければ fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  clusters_path = run_dir / "must-fix-clusters.yaml"
  clusters = yaml.safe_load(clusters_path.read_text(encoding="utf-8"))
  clusters["clusters"][0].pop("recommended_reason")
  clusters_path.write_text(
    yaml.safe_dump(clusters, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "recommended_reason" in captured.err


def test_assert_review_report_ready_requires_cluster_in_proxy_summary(
  tmp_path,
  capsys,
):
  """重要所見 cluster が proxy summary に出ていなければ fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  (run_dir / "proxy-decision-summary.md").write_text(
    "# Proxy decision summary\n\n- other-cluster: option A\n",
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "proxy-decision-summary.md missing cluster" in captured.err


def test_assert_review_report_ready_requires_ledger_execution_snapshot(
  tmp_path,
  capsys,
):
  """自動実行報告は plan なし監査に必要な ledger snapshot を要求する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
  ledger.pop("execution_evidence_snapshot")
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "ledger.execution_evidence_snapshot" in captured.err


def test_assert_review_report_ready_requires_finding_fix_traceability(
  tmp_path,
  capsys,
):
  """accepted finding は commit / tests / changed_files の trace を要求する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)
  triage_path = run_dir / "triage.yaml"
  triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
  triage["items"][0]["decision_status"] = "decided"
  triage["items"][0]["final_label"] = "must-fix"
  triage_path.write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "ledger.finding_fix_traceability is required" in captured.err


def test_assert_review_report_ready_requires_report_artifacts(tmp_path, capsys):
  """自動実行テスト報告の成果物が不足していれば fail-closed する。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(run_dir / "autonomous-execution-report.md"),
      "--ledger-path", str(run_dir / "autonomous-ledger.yaml"),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "must-fix-clusters.md" in captured.err
  assert "autonomous-execution-report.md" in captured.err


def test_assert_review_report_ready_passes_when_report_artifacts_exist(tmp_path, capsys):
  """自動実行テスト報告の成果物が揃えば通過する。"""
  run_dir = _write_review_run(tmp_path)
  report_path, ledger_path = _write_autonomous_report_artifacts(run_dir)

  exit_code = main(
    [
      "assert-review-report-ready",
      "--review-run-dir", str(run_dir),
      "--report-path", str(report_path),
      "--ledger-path", str(ledger_path),
    ]
  )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "review_report_ready: true" in output


def test_generate_review_report_writes_single_traceability_report(tmp_path, capsys):
  """review-run の raw/triage/重要所見/採用案/実装結果を一枚の report にまとめる。"""
  run_dir = _write_review_run(tmp_path)
  _write_autonomous_report_artifacts(run_dir)
  triage_path = run_dir / "triage.yaml"
  triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
  triage["items"][0]["decision_status"] = "decided"
  triage["items"][0]["final_label"] = "must-fix"
  triage_path.write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  ledger_path = run_dir / "autonomous-ledger.yaml"
  ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
  ledger["finding_fix_traceability"] = [
    {
      "finding_id": "finding-001",
      "resolution_commit": "fc30479",
      "changed_files": ["tools/check-workflow-action.py"],
      "test_refs": ["tests/tools/test_check_workflow_action.py"],
    },
  ]
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  output_path = run_dir / "generated-review-report.md"

  exit_code = main(
    [
      "generate-review-report",
      "--review-run-dir", str(run_dir),
      "--ledger-path", str(ledger_path),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 0
  assert str(output_path) in capsys.readouterr().out
  text = output_path.read_text(encoding="utf-8")
  assert "# Review Run Traceability Report" in text
  assert "## Raw Responses" in text
  assert "claude-sonnet-4-6" in text
  assert "raw/claude-sonnet-4-6.round-1.txt" in text
  assert "## Model Findings" in text
  assert "human_required_count" in text
  assert "## Three-Level Triage" in text
  assert "must-fix" in text
  assert "## Important Findings" in text
  assert "WM-IMPL-MF-001" in text
  assert "## Adopted Options" in text
  assert "option A" in text
  assert "## Finding-to-Fix Matrix" in text
  assert "finding-001" in text
  assert "fc30479" in text
  assert "tests/tools/test_check_workflow_action.py" in text
  assert "## Implementation Result" in text
  assert "accepted" in text


def test_generate_review_report_requires_ready_inputs(tmp_path, capsys):
  """入力成果物が不足した report 生成は fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  output_path = run_dir / "generated-review-report.md"

  exit_code = main(
    [
      "generate-review-report",
      "--review-run-dir", str(run_dir),
      "--ledger-path", str(run_dir / "autonomous-ledger.yaml"),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "must-fix-clusters.md" in captured.err
  assert not output_path.exists()
