# tools/api_providers/tests/test_prepare_api_review_criteria.py
# workflow next_action 由来の API review criteria 生成テスト。

import hashlib
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.prepare_api_review_criteria import main


NEXT_ACTION_RESPONSE = {
  "verdict": "OK",
  "next_action": {
    "kind": "stage",
    "feature": "workflow-management",
    "phase": "implementation",
    "stage": "triad-review",
    "required_inputs": [
      {
        "id": "target_feature_documents",
        "paths": [
          ".reviewcompass/specs/workflow-management/requirements.md",
          ".reviewcompass/specs/workflow-management/design.md",
          ".reviewcompass/specs/workflow-management/tasks.md",
        ],
      },
      {
        "id": "vertical_intent_transfer_check",
        "phase_chains": {
          "implementation": [
            "requirements.md",
            "design.md",
            "tasks.md",
            "implementation",
          ],
        },
        "prompt_materialization_contract": {
          "source_materials_must_not_be_path_only": True,
          "required_prompt_material": [
            "upstream_excerpt_or_structured_summary",
            "target_phase_artifact_excerpt",
            "review_target",
            "out_of_scope",
          ],
          "upstream_summary_fields": [
            "purpose",
            "responsibility_boundaries",
            "acceptance_criteria",
            "forbidden_actions",
            "unresolved_or_design_deferred_items",
            "intended_target_phase_transfer",
          ],
        },
      },
    ],
    "effective_prompt": {
      "effective_prompt_path": ".reviewcompass/runtime/effective-prompts/triad.prompt.md",
      "effective_prompt_sha256": "abc123",
    },
  },
}


def test_prepare_api_review_criteria_writes_criteria_and_metadata(tmp_path, capsys):
  next_action_file = tmp_path / "next.json"
  next_action_file.write_text(
    json.dumps(NEXT_ACTION_RESPONSE, ensure_ascii=False),
    encoding="utf-8",
  )
  source_materials_file = tmp_path / "source-materials.yaml"
  source_materials_file.write_text(
    yaml.safe_dump(
      {
        "source_materials": [
          {
            "key": "workflow-management-upstream",
            "purpose": "implementation triad-review upstream intent",
            "purpose_field": "preserve approval and proxy boundaries",
            "responsibility_boundaries": [
              "proxy_model cannot satisfy human_only approval"
            ],
            "acceptance_criteria": [
              "criteria includes model-readable upstream intent"
            ],
            "forbidden_actions": ["do not pass only paths as evidence"],
            "unresolved_or_design_deferred_items": ["none"],
            "intended_target_phase_transfer": [
              "implementation keeps approval/proxy separation"
            ],
          }
        ]
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  review_run_dir = tmp_path / "review-run"

  exit_code = main(
    [
      "--next-action-file", str(next_action_file),
      "--review-run-dir", str(review_run_dir),
      "--source-materials-file", str(source_materials_file),
      "--topic", "approval-gate-transfer",
      "--target", "tools/check-workflow-action.py",
      "--judgment-item", "approval gate upstream transfer",
      "--review-purpose", "upstream transfer check",
      "--review-object", "implementation artifact",
      "--review-focus", "vertical intent transfer",
      "--in-scope", "approval gate implementation",
      "--out-of-scope", "spec.json phase movement",
    ]
  )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.startswith("[OK] prepare_api_review_criteria ")
  criteria_path = review_run_dir / "review-criteria.md"
  metadata_path = review_run_dir / "review-criteria.yaml"
  assert criteria_path.is_file()
  assert metadata_path.is_file()
  criteria = criteria_path.read_text(encoding="utf-8")
  assert "workflow-management-implementation-approval-gate-transfer-review-criteria" in criteria
  assert "requirements.md -> design.md -> tasks.md -> implementation" in criteria
  assert "do not pass only paths as evidence" in criteria
  metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
  assert metadata["criteria_file"] == str(criteria_path)
  assert metadata["criteria_file_sha256"] == hashlib.sha256(
    criteria_path.read_bytes()
  ).hexdigest()
  assert metadata["effective_prompt_path"] == ".reviewcompass/runtime/effective-prompts/triad.prompt.md"
  assert metadata["recommended_run_review_args"]["phase"] == "triad-review"
  assert metadata["recommended_run_review_args"]["criteria_file"] == str(criteria_path)


def test_prepare_api_review_criteria_fails_when_source_material_is_unstructured(
  tmp_path,
  capsys,
):
  next_action_file = tmp_path / "next.json"
  next_action_file.write_text(
    json.dumps(NEXT_ACTION_RESPONSE, ensure_ascii=False),
    encoding="utf-8",
  )
  source_materials_file = tmp_path / "source-materials.yaml"
  source_materials_file.write_text(
    yaml.safe_dump(
      {
        "source_materials": [
          {
            "key": "workflow-management-upstream",
            "purpose": "implementation triad-review upstream intent",
            "content": "- `.reviewcompass/specs/workflow-management/requirements.md`\n",
          }
        ]
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "--next-action-file", str(next_action_file),
      "--review-run-dir", str(tmp_path / "review-run"),
      "--source-materials-file", str(source_materials_file),
      "--topic", "approval-gate-transfer",
      "--target", "tools/check-workflow-action.py",
      "--judgment-item", "approval gate upstream transfer",
      "--review-purpose", "upstream transfer check",
      "--review-object", "implementation artifact",
      "--review-focus", "vertical intent transfer",
      "--in-scope", "approval gate implementation",
    ]
  )

  assert exit_code == 1
  assert "path-only" in capsys.readouterr().err
