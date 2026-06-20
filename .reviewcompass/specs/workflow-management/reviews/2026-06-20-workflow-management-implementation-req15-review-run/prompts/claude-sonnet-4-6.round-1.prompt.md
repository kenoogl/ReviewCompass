prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
---
criteria_id: workflow-management-implementation-req15-structured-effective-prompt-transfer-review-criteria
phase: implementation
status: prompt_quality_reviewed_nonblocking_warnings_addressed
---

# workflow-management implementation req15-structured-effective-prompt-transfer API Review Criteria

## Review Task

Review the target for: Req 15 implementation upstream transfer for structured effective prompt and prompt audit.

Primary judgment question:

Does the target satisfy Req 15 implementation upstream transfer for structured effective prompt and prompt audit, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without omission, weakening, contradiction, unsupported addition, or drift?

Do not combine multiple independent judgments in this prompt. If another cluster, finding, artifact, or design-policy judgment is needed, create a separate criteria file and run separate prompt-quality review.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 15 implementation artifacts
- Review focus:
  - language task and machine task separation
  - effective prompt manifest and metadata recording
  - prompt audit fail-closed checks
- Scope boundaries:
  - In scope:
    - Req 15 schemas, implementation, compatibility paths, and focused tests
  - Out of scope:
    - Req 14 approval gate state
    - Req 16 proxy triage decision mechanics
- Output requirements:
  - parser-compatible findings
- Prohibited actions:
  - commit
  - push
  - spec.json update
  - phase completion
- Requirement-to-prompt mapping:
  - Review purpose -> Review Task and Required Checks
  - Review focus -> Required Checks
  - Scope boundaries -> Review Target and Out Of Scope
  - Prohibited actions -> Out Of Scope and Finding Policy

## Generic API Review Core

- Keep criteria and target roles distinct.
- Treat the target files as the only review target.
- Treat source materials as background or intent-transfer evidence, not as targets.
- Do not use path-only source materials as model-readable evidence.
- Ask one non-leading primary judgment question.
- Preserve user review requirements without narrowing, broadening, or replacement.
- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.
- Return parser-compatible findings only.

## Review Target

The authoritative target file set is
`.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req15-review-target-manifest.md`
and the target files supplied by the review runner. The list below is an orientation
copy only; if it diverges from the manifest or runner target set, treat the manifest
and runner target set as authoritative and report the mismatch.

- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/api_providers/run_role.py`
- `tools/api_providers/run_review.py`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_prompt_manifest_rounds_recording.py`
- `tools/api_providers/tests/test_run_role.py`
- `tools/api_providers/tests/test_run_review.py`

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req15-upstream-intent

Purpose: Requirement 15 / design / tasks intent for structured effective prompts and prompt audit.
This is a structured summary of the upstream phase chain, paraphrased from
`.reviewcompass/specs/workflow-management/requirements.md`,
`.reviewcompass/specs/workflow-management/design.md`, and
`.reviewcompass/specs/workflow-management/tasks.md`. Use it as intent-transfer
evidence; do not treat it as a replacement for target files.

- purpose: Treat effective prompts as structured language-task specifications while keeping machine tasks in operation contracts, preflight, runners, and guards.
- responsibility_boundaries:
  - Effective prompt structure owns decision_point, preconditions_checked, language_task, postconditions, and on_completion.
  - language_task owns document_kind, input, output_format, and constraints for the LLM's language work.
  - Machine operations such as commit, push, spec.json mutation, review-run execution, approval consume, and state mutation are not embedded as LLM instructions.
  - Prompt audit checks structure, references, anchors, length bounds, manifest/target consistency, language_task/output/postcondition correspondence, and next action compatibility.
  - LLM judge audit is semantic assistance only and must not automate final approval.
- acceptance_criteria:
  - Effective prompt manifest schema validates required sections and source references.
  - generated prompt metadata preserves compatibility with effective_prompt_path and effective_prompt_sha256 in next_action and review-run rounds.
  - prompt audit rejects missing required structure, broken refs, unknown action kind, review target manifest mismatch, machine task leakage, unverified preconditions, and impossible postconditions.
  - prompt audit findings are structured and do not depend on provider or model identity.
  - run_role.py and run_review.py record effective prompt path and sha256 when provided.
- forbidden_actions:
  - Do not summarize away required source material into path-only prompts when the review requires upstream intent transfer.
  - Do not place machine execution procedures in the language_task as if the LLM should perform them manually.
  - Do not delete existing rounds.yaml compatibility fields while adding manifest metadata.
  - Do not let LLM judge audit act as final approval.
- unresolved_or_design_deferred_items:
  - Phase 6 LLM judge audit is later than the mechanical prompt audit and may remain advisory.
  - Full structured prompt generation for all decision points is Phase 4 scope; compatibility Markdown output may remain during transition.
- intended_target_phase_transfer:
  - Implementation should provide language task schema, effective prompt manifest validation, prompt audit logic, and review-run metadata recording.
  - Implementation review should verify schemas, prompt audit tests, and run_role/run_review compatibility listed in req15-review-target-manifest.md against this intent.

### req15-verification-context

Verification snapshots are smoke evidence only. Passing tests are not proof of
correctness and must not suppress findings. Use the target test files themselves
to evaluate whether the boundaries are meaningfully covered.

- `test_language_task_io_schema.py`: covers language task I/O schema shape and separation of language-facing input/output fields.
- `test_effective_prompt_manifest.py`: covers effective prompt manifest required fields and source-reference metadata.
- `test_prompt_audit.py`: covers fail-closed prompt audit cases for missing structure, broken references, machine-task leakage, and next-action compatibility.
- `test_prompt_manifest_rounds_recording.py`: covers review-run metadata compatibility for effective prompt path / sha256 recording.
- `test_run_role.py` and `test_run_review.py`: cover API provider runner compatibility paths that preserve effective prompt metadata.

### direct-boundary-reference-definition

Req 14 and Req 16 are out of scope except when the Req15 target code or schemas
explicitly name their boundary symbols. Examples of direct boundary references:

- prompt audit code or schema fields that explicitly mention approval gates,
  human-only approval, proxy triage, operation contracts, phase transition, or
  irreversible operation authorization
- run_role.py / run_review.py metadata behavior that explicitly passes evidence
  required by Req16 proxy decision or operation-contract checks

Do not review the full Req14 approval gate implementation or full Req16 proxy
triage mechanics.

## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 15 implementation upstream transfer for structured effective prompt and prompt audit.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that source/digest/prompt length structures are specific enough for later audit:
   - source references are non-empty and traceable to source material or target artifacts
   - digests use explicit sha256-style values where digest binding is claimed
   - prompt length or bound checks identify the measured field, bound source, and failure behavior
   - manifest metadata records path and sha256 without replacing the target content
6. Check that the target does not authorize commit, push, spec.json mutation, phase transition, or gate completion.

## Out Of Scope

- Req 14 approval gate state
- Req 16 proxy triage decision mechanics
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:function`, or `path:section`.
- Return findings: [] only when the target is traceable, correctly scoped, and sufficiently grounded.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/schema/language_task_io.schema.json
.reviewcompass/schema/effective_prompt_manifest.schema.json
tools/check-workflow-action.py
tools/check_workflow_action/effective_prompt_builder.py
tools/check_workflow_action/prompt_audit.py
tools/api_providers/run_role.py
tools/api_providers/run_review.py
tests/workflow-management/test_language_task_io_schema.py
tests/workflow-management/test_effective_prompt_manifest.py
tests/workflow-management/test_prompt_audit.py
tests/workflow-management/test_prompt_manifest_rounds_recording.py
tools/api_providers/tests/test_run_role.py
tools/api_providers/tests/test_run_review.py

# Target document
## .reviewcompass/schema/language_task_io.schema.json

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:language_task_io",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "document_kind",
    "input",
    "output_format",
    "constraints"
  ],
  "properties": {
    "document_kind": {
      "type": "string",
      "minLength": 1
    },
    "input": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "required_files",
        "state_refs",
        "source_refs"
      ],
      "properties": {
        "required_files": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "state_refs": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "source_refs": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "output_format": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "kind",
        "required_sections",
        "schema_ref"
      ],
      "properties": {
        "kind": {
          "type": "string",
          "minLength": 1
        },
        "required_sections": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "schema_ref": {
          "type": [
            "string",
            "null"
          ]
        }
      }
    },
    "constraints": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      }
    }
  }
}


## .reviewcompass/schema/effective_prompt_manifest.schema.json

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:effective_prompt_manifest",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "schema_version",
    "decision_point",
    "source_artifacts",
    "required_disciplines",
    "operation_contract",
    "expected_output_schema",
    "prompt_length",
    "preconditions_checked",
    "language_task",
    "postconditions",
    "on_completion"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "effective-prompt-manifest-v1"
    },
    "decision_point": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "kind",
        "required_action"
      ],
      "properties": {
        "kind": {
          "type": "string",
          "minLength": 1
        },
        "required_action": {
          "type": "string",
          "minLength": 1
        },
        "phase": {
          "type": "string"
        },
        "stage": {
          "type": "string"
        },
        "active_gate": {
          "type": [
            "string",
            "null"
          ]
        }
      }
    },
    "source_artifacts": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": [
          "path",
          "sha256"
        ],
        "properties": {
          "path": {
            "type": "string",
            "minLength": 1
          },
          "sha256": {
            "type": "string",
            "pattern": "^sha256:[0-9a-f]{64}$"
          }
        }
      }
    },
    "required_disciplines": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      }
    },
    "operation_contract": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "operation_id",
        "sha256"
      ],
      "properties": {
        "operation_id": {
          "type": "string",
          "minLength": 1
        },
        "sha256": {
          "type": "string",
          "pattern": "^sha256:[0-9a-f]{64}$"
        }
      }
    },
    "expected_output_schema": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "schema_ref",
        "required_sections"
      ],
      "properties": {
        "schema_ref": {
          "type": [
            "string",
            "null"
          ]
        },
        "required_sections": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "prompt_length": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "min_chars",
        "max_chars",
        "source_ref",
        "failure_verdict"
      ],
      "properties": {
        "min_chars": {
          "type": "integer",
          "minimum": 0
        },
        "max_chars": {
          "type": "integer",
          "minimum": 1
        },
        "source_ref": {
          "type": "string",
          "minLength": 1
        },
        "failure_verdict": {
          "type": "string",
          "enum": [
            "OK",
            "WARN",
            "DEVIATION"
          ]
        }
      }
    },
    "preconditions_checked": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": [
          "id",
          "source",
          "machine_checked",
          "evidence_ref"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "source": {
            "type": "string",
            "minLength": 1
          },
          "machine_checked": {
            "type": "boolean"
          },
          "evidence_ref": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "language_task": {
      "$ref": "#/$defs/language_task"
    },
    "postconditions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": [
          "id",
          "check_kind",
          "source_ref"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "check_kind": {
            "type": "string",
            "minLength": 1
          },
          "source_ref": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "on_completion": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "next_required_action",
        "allowed_followups",
        "forbidden_actions"
      ],
      "properties": {
        "next_required_action": {
          "type": "string",
          "minLength": 1
        },
        "allowed_followups": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "forbidden_actions": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    }
  },
  "$defs": {
    "language_task": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "document_kind",
        "input",
        "output_format",
        "constraints"
      ],
      "properties": {
        "document_kind": {
          "type": "string",
          "minLength": 1
        },
        "input": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "required_files",
            "state_refs",
            "source_refs"
          ],
          "properties": {
            "required_files": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1
              }
            },
            "state_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1
              }
            },
            "source_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1
              }
            }
          }
        },
        "output_format": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "kind",
            "required_sections",
            "schema_ref"
          ],
          "properties": {
            "kind": {
              "type": "string",
              "minLength": 1
            },
            "required_sections": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1
              }
            },
            "schema_ref": {
              "type": [
                "string",
                "null"
              ]
            }
          }
        },
        "constraints": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    }
  }
}


## tools/check-workflow-action.py

#!/usr/bin/env python3
"""ワークフロー事前検査スクリプト（補助層 C 段階 2）

仕様：docs/operations/WORKFLOW_PRECHECK.md
位置付け：計画書 §5.8 補助層 C 共存モデルの段階 2（外部スクリプトによる機械的判定）

呼び出し側（段階 1 LLM または段階 3 フック）から不可逆操作の直前に呼ばれ、
当該操作が現在のワークフロー状態と整合するかを機械的に判定する。判定のみを
行い、状態の書き換えやエスカレーションは行わない。

サブコマンド：
  spec-set <feature> <phase> <stage> <new-value>  spec.json の workflow_state 変更を判定
  commit   --rationale "<理由>"                    git commit を判定
  push     --rationale "<理由>"                    git push を判定

終了コード（仕様 §7.1）：
  0  問題なし、処理続行可
  1  警告あり、呼び出し側の判断で続行可
  2  逸脱検出、呼び出し側が遮断推奨
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

from deployment_independence_lint import lint_text
from document_link_lint import lint_path_texts as lint_document_link_texts


# 既定のログファイルパス（呼び出し時の cwd 相対、仕様 §8.2）
# 実行時生成物 3 パスは runtime 区画へ集約（2026-06-12 配置規約 P1。
# 旧配置は凍結・読み取り互換のみ P3 まで。定数と読み取り解決の正本は
# check_workflow_action/runtime_paths.py、契約の正本は wm design §実行時生成物の凍結期（P3 まで）の扱い）
from check_workflow_action.runtime_paths import (
  DEFAULT_LOG_PATH,
  LEGACY_LOG_PATH,
  DEFAULT_COMMIT_APPROVAL_PATH,
  LEGACY_COMMIT_APPROVAL_PATH,
  DEFAULT_EFFECTIVE_PROMPT_DIR,
  LEGACY_EFFECTIVE_PROMPT_DIR,
  resolve_commit_approval_path,
  resolve_effective_prompt_read_path,
)
from check_workflow_action import approval_gate, commit_approval
from check_workflow_action.implementation_phases import check_phase_plan, load_plan
from check_workflow_action.operation_preflight import run_preflight
from check_workflow_action.operation_contracts import load_contracts, run_contract_check
from check_workflow_action.operation_list import build_operation_list
from check_workflow_action.prompt_audit import audit_manifest, load_manifest as load_prompt_manifest
from check_workflow_action.proxy_triage_decisions import (
  check_decision as check_proxy_triage_decision,
  load_decision as load_proxy_triage_decision,
)
from check_workflow_action.side_track_stack import current as current_side_track_stack
from check_workflow_action.workflow_state_snapshot import build_snapshot

DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"
DEFAULT_DISCIPLINE_MAP_PATH = "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"
DEFAULT_CARRY_FORWARD_REGISTER_PATH = "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
DEFAULT_CARRY_FORWARD_SOURCE_PATH = (
  "learning/workflow/carry-forward-register/sources/"
  "reviewcompass-pending-cross-feature-findings.md"
)
DEPLOYMENT_INDEPENDENCE_GUARD_PREFIXES = (
  "config/",
  "docs/operations/",
  "learning/workflow/deployment-readiness/",
  "learning/workflow/replication-pilots/",
  "learning/workflow/schemas/",
)
DEPLOYMENT_INDEPENDENCE_GUARD_SUFFIXES = (".md", ".yaml", ".yml", ".json")
DOCUMENT_LINK_GUARD_PREFIXES = (
  ".reviewcompass/specs/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
)
DOCUMENT_LINK_GUARD_SUFFIXES = (".md", ".yaml", ".yml")

# 各フェーズの段集合（計画書 §5.5 と §5.24.4 と整合）
PHASE_STAGES = {
  "intent": ["drafting", "review", "approval"],
  "feature-partitioning": ["candidate-proposal", "approval"],
  "requirements": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "design": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "tasks": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "implementation": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
}

# フェーズの依存順（計画書 §5.5）
PHASE_ORDER = [
  "intent",
  "feature-partitioning",
  "requirements",
  "design",
  "tasks",
  "implementation",
]

# 機能横断段（全機能で同じ値を持つフェーズ、計画書 §5.24.4）
CROSS_FEATURE_PHASES = ("intent", "feature-partitioning")

# 既定の機能順（ReviewCompass 開発リポジトリの feature-partitioning 成果物と整合）。
# next サブコマンドでは resolve_feature_order が feature-dependency.yaml の
# feature_order キーから解決した一覧で上書きする（設計記録
# docs/notes/2026-06-10-deployment-multi-llm-entry-design.md §3.5）。
FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]

# feature-dependency.yaml の探索順（対象アプリは .reviewcompass/ に閉じる）
FEATURE_DEPENDENCY_SEARCH_PATHS = (
  ".reviewcompass/feature-dependency.yaml",
  "stages/feature-dependency.yaml",
  "feature-dependency.yaml",
)


def load_feature_dependency(cwd):
  """feature-dependency.yaml を探索順に従って読む。(data, relative_path, load_error) を返す

  load_error は破損・構造異常の種別（unreadable／empty／not_mapping、正常時は None）。
  破損を立ち上げ案内で覆い隠さないため、未定義（キー欠落）と区別する（Req 8 受入 9、MLE-DEC-005）。
  """
  for relative_path in FEATURE_DEPENDENCY_SEARCH_PATHS:
    path = Path(cwd) / relative_path
    if path.is_file():
      try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
      except (OSError, yaml.YAMLError, UnicodeDecodeError):
        # UnicodeDecodeError は OSError ではないため明示的に捕捉する
        # （非 UTF-8 ファイルもクラッシュではなく遮断へ倒す。triad-review gpt-001 対処）
        return None, relative_path, "unreadable"
      if data is None:
        return None, relative_path, "empty"
      if not isinstance(data, dict):
        return None, relative_path, "not_mapping"
      return data, relative_path, None
  return None, None, None


def _feature_dependency_map(features):
  """features 定義から feature → 依存先リストの対応を作る"""
  dependency_map = {}
  if not isinstance(features, dict):
    return dependency_map
  for feature, value in features.items():
    depends_on = value.get("depends_on") if isinstance(value, dict) else None
    if isinstance(depends_on, dict):
      dependency_map[feature] = [dep for dep in depends_on if isinstance(dep, str)]
    elif isinstance(depends_on, list):
      dependency_map[feature] = [dep for dep in depends_on if isinstance(dep, str)]
  return dependency_map


def validate_feature_order_consistency(feature_order, features):
  """feature_order と depends_on の整合（依存先行・循環なし）を調べる"""
  reasons = []
  index_by_feature = {feature: i for i, feature in enumerate(feature_order)}
  dependency_map = _feature_dependency_map(features)

  for feature, deps in dependency_map.items():
    if feature not in index_by_feature:
      continue
    for dep in deps:
      if dep not in index_by_feature:
        reasons.append(
          f"feature_order が depends_on と矛盾しています: {feature} は {dep} に"
          f"依存しますが、{dep} が feature_order にありません"
        )
      elif index_by_feature[dep] > index_by_feature[feature]:
        reasons.append(
          f"feature_order が depends_on と矛盾しています: {feature} は {dep} に"
          f"依存しますが、{dep} が後に並んでいます"
        )

  state = {}

  def _visit(node, stack):
    state[node] = "visiting"
    stack.append(node)
    for dep in dependency_map.get(node, []):
      if state.get(dep) == "visiting":
        cycle = stack[stack.index(dep):] + [dep]
        reasons.append("depends_on に循環依存があります: " + " → ".join(cycle))
      elif state.get(dep) is None:
        _visit(dep, stack)
    stack.pop()
    state[node] = "done"

  for node in list(dependency_map):
    if state.get(node) is None:
      _visit(node, [])

  return reasons


def resolve_feature_order(cwd):
  """feature 一覧を feature-dependency.yaml から解決する

  戻り値 dict：feature_order（解決失敗時 None）、source_path、
  guidance_reason（立ち上げ案内が必要な場合）、consistency_reasons（整合違反）
  """
  data, source_path, load_error = load_feature_dependency(cwd)
  if load_error:
    # 破損・構造異常は未定義と区別して遮断する（Req 8 受入 9、MLE-DEC-005）
    if load_error == "empty":
      reason = (
        f"{source_path} が空です。feature-partitioning の承認結果"
        "（依存の根拠と順序の導出を含む）を feature_order キーに記録してください"
      )
    elif load_error == "not_mapping":
      reason = (
        f"{source_path} の最上位が連想配列ではありません。"
        "ファイルの内容を確認してください"
      )
    else:
      reason = (
        f"{source_path} を YAML として読めません（破損の可能性）。"
        "ファイルの内容を確認してください"
      )
    return {
      "feature_order": None,
      "source_path": source_path,
      "guidance_reason": None,
      "consistency_reasons": [reason],
      "load_error": load_error,
    }

  if data is None:
    return {
      "feature_order": None,
      "source_path": None,
      "guidance_reason": (
        "feature-dependency.yaml が見つかりません。intent と feature-partitioning を"
        "実施し、承認された分割結果（依存の根拠と順序の導出を含む）を "
        ".reviewcompass/feature-dependency.yaml の feature_order に記録してください"
      ),
      "consistency_reasons": [],
    }

  feature_order = data.get("feature_order")
  if (
    not isinstance(feature_order, list)
    or not feature_order
    or not all(isinstance(feature, str) for feature in feature_order)
  ):
    return {
      "feature_order": None,
      "source_path": source_path,
      "guidance_reason": (
        f"{source_path} に feature_order が定義されていません。"
        "feature-partitioning の承認結果（依存の根拠と順序の導出を含む）を "
        "feature_order キーに記録してください"
      ),
      "consistency_reasons": [],
    }

  return {
    "feature_order": feature_order,
    "source_path": source_path,
    "guidance_reason": None,
    "consistency_reasons": validate_feature_order_consistency(
      feature_order,
      data.get("features"),
    ),
  }


def feature_definition_next_state(feature_resolution):
  """feature 一覧が解決できない場合の next 判定一式を返す（解決済みなら None）"""
  if feature_resolution["guidance_reason"]:
    next_action = {
      "kind": "feature_definition_required",
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": feature_resolution["guidance_reason"],
    }
    current_state = {
      "feature_dependency_source": feature_resolution["source_path"],
    }
    return next_action, current_state, [], "OK", 0

  if feature_resolution["consistency_reasons"]:
    if feature_resolution.get("load_error"):
      reason = "feature-dependency.yaml が読めません（破損または内容不正の可能性）"
    else:
      reason = "feature_order と depends_on の整合に問題があります"
    next_action = {
      "kind": "unknown",
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": reason,
    }
    current_state = {
      "feature_dependency_source": feature_resolution["source_path"],
    }
    return (
      next_action,
      current_state,
      list(feature_resolution["consistency_reasons"]),
      "DEVIATION",
      2,
    )

  return None

POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)

LIGHTWEIGHT_SELF_CHECK_DIR_PREFIXES = (
  "docs/notes/working/",
)

AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES = (
  "requires_main_session_review",
  "requires_diff_scope_check",
  "requires_tests",
  "requires_decision_basis_review",
)

AUTONOMOUS_PARALLEL_REQUIRED_OUTPUTS_POLICY = {
  "implementation_diff": "commit_candidate",
  "verification_summary": "required",
  "decision_basis": "preserve_if_used",
  "work_noise": "exclude",
}

AUTONOMOUS_PARALLEL_REQUIRED_HISTORY_FLAGS = (
  "record_task_assignments",
  "record_decision_basis",
  "record_integration_result",
)

REOPEN_TRIGGER_MAP = {
  "I-0": [
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-1": [
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-2": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-3": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-4": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "A-0": [
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-1": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-2": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-3": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "D-0": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "D-1": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "D-2": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "R-0": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
  ],
  "R-1": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
  ],
  "N-0": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
  ],
}

DEFAULT_DISCIPLINE_MAP = {
  "default": [
    "docs/operations/WORKFLOW_NAVIGATION.md",
  ],
  "by_kind": {
    "stage": [
      "docs/disciplines/discipline_workflow_state_truth_source.md",
    ],
    "cross_feature_stage": [
      "docs/disciplines/discipline_workflow_state_truth_source.md",
    ],
    "commit_stop_point": [
      "docs/operations/WORKFLOW_NAVIGATION.md#commit_stop_point",
      "docs/disciplines/discipline_approval_operation.md",
    ],
    "post_write_verification": [
      "docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification",
      "docs/disciplines/discipline_post_write_verification.md",
    ],
    "post_write_policy_violation": [
      "docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation",
      "docs/disciplines/discipline_post_write_verification.md",
    ],
    "post_write_human_decision_required": [
      "docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required",
      "docs/disciplines/discipline_post_write_verification.md",
      "docs/disciplines/discipline_approval_operation.md",
    ],
    "reopen_in_progress": [
      "docs/operations/REOPEN_PROCEDURE.md",
      "docs/disciplines/discipline_approval_operation.md",
    ],
    "maintenance_in_progress": [
      "docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress",
    ],
    "resume_in_progress": [
      "docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress",
    ],
  },
  "by_stage": {
    "drafting": [
      "docs/operations/REOPEN_PROCEDURE.md",
      "docs/disciplines/discipline_workflow_state_truth_source.md",
    ],
    "triad-review": [
      "docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      "docs/disciplines/discipline_approval_operation.md",
    ],
    "review-wave": [],
    "alignment": [
      "docs/disciplines/discipline_workflow_state_truth_source.md",
    ],
    "approval": [
      "docs/disciplines/discipline_approval_operation.md",
      "docs/operations/WORKFLOW_PRECHECK.md#spec-set",
    ],
  },
  "required_inputs": {
    "by_stage": {
      "drafting": [
        {
          "id": "target_feature_documents",
          "role": "stage_entry_context",
          "source_type": "feature_document_set",
          "purpose": (
            "Read the current feature state and phase documents before "
            "updating the phase artifact."
          ),
          "resolver": {
            "kind": "next_action_template",
            "paths": [
              ".reviewcompass/specs/{feature}/spec.json",
              ".reviewcompass/specs/{feature}/requirements.md",
              ".reviewcompass/specs/{feature}/design.md",
              ".reviewcompass/specs/{feature}/tasks.md",
            ],
          },
          "read_policy": "current_feature_documents",
        },
        {
          "id": "reopen_procedure_state",
          "role": "workflow_state_context",
          "source_type": "reopen_in_progress_file",
          "purpose": "Read the reopen state and downstream impact decisions before drafting.",
          "resolver": {
            "kind": "next_action_template",
            "paths": [
              "{file}",
            ],
          },
          "read_policy": "reopen_state",
        },
      ],
      "triad-review": [
        {
          "id": "target_feature_documents",
          "role": "stage_entry_context",
          "source_type": "feature_document_set",
          "purpose": (
            "Read the current feature state and phase documents before "
            "starting triad-review."
          ),
          "resolver": {
            "kind": "next_action_template",
            "paths": [
              ".reviewcompass/specs/{feature}/spec.json",
              ".reviewcompass/specs/{feature}/requirements.md",
              ".reviewcompass/specs/{feature}/design.md",
              ".reviewcompass/specs/{feature}/tasks.md",
            ],
          },
          "read_policy": "current_feature_documents",
        },
        {
          "id": "triad_review_run_artifacts",
          "role": "review_run_context",
          "source_type": "review_run_artifact_set",
          "purpose": (
            "Prepare or read the review-run bundle, raw responses, model "
            "summaries, and three-level triage records for this triad-review."
          ),
          "resolver": {
            "kind": "next_action_template",
            "base_path_pattern": (
              ".reviewcompass/specs/{feature}/reviews/"
              "*-{feature}-{phase}-review-run"
            ),
          },
          "required_artifacts": [
            "review-target.md",
            "raw/",
            "rounds.yaml",
            "model-result-summary.yaml",
            "triage.yaml",
            "raw-review-triage-summary.md",
          ],
          "read_policy": "review_run_bundle_and_triage",
        },
      ],
      "review-wave": [
        {
          "id": "unresolved_cross_scope_items",
          "role": "stage_entry_context",
          "source_type": "carry_forward_register",
          "purpose": (
            "Read unresolved items carried forward from prior reviews or "
            "adjacent scopes before starting this stage."
          ),
          "resolver": {
            "kind": "project_state",
            "path": DEFAULT_CARRY_FORWARD_REGISTER_PATH,
          },
          "read_policy": "unresolved_items_only",
        },
      ],
    },
  },
}


def load_spec_json(cwd, feature):
  """機能の spec.json を読み込んで dict として返す

  見つからない場合は None。
  """
  spec_path = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
  if not spec_path.exists():
    return None
  return json.loads(spec_path.read_text(encoding="utf-8"))


def judge_spec_set(spec_data, phase, stage, new_value):
  """spec-set の判定を行う（仕様 §6.1）

  戻り値：(verdict, exit_code, reasons)
    verdict: "OK" / "WARN" / "DEVIATION"
    exit_code: 0 / 1 / 2
    reasons: 理由文のリスト
  """
  workflow_state = spec_data.get("workflow_state", {})
  phase_state = workflow_state.get(phase, {})
  current_value = phase_state.get(stage)

  if new_value:
    # true に変える場合：依存チェック
    reasons = []
    recheck = spec_data.get("recheck", {})
    if isinstance(recheck, dict):
      impacted = recheck.get("impacted_downstream_phases")
      if (
        recheck.get("upstream_change_pending") is True
        and isinstance(impacted, list)
        and phase in impacted
      ):
        reasons.append(
          f"recheck.upstream_change_pending が true で、"
          f"{phase} が impacted_downstream_phases に含まれています"
          "（reopen 手続きの feature impact 判定と下流影響判定を完了してから true 化してください）"
        )

    # 同フェーズ内の前段がすべて true か
    stages = PHASE_STAGES[phase]
    stage_index = stages.index(stage)
    for prior_stage in stages[:stage_index]:
      if not phase_state.get(prior_stage, False):
        reasons.append(
          f"workflow_state.{phase}.{prior_stage} が false です"
          f"（{stage} の前提が満たされていません）"
        )

    # 上流フェーズの approval が true か（機能横断段は不要）
    if phase not in CROSS_FEATURE_PHASES:
      phase_idx = PHASE_ORDER.index(phase)
      for prior_phase in PHASE_ORDER[:phase_idx]:
        prior_phase_state = workflow_state.get(prior_phase, {})
        if not prior_phase_state.get("approval", False):
          reasons.append(
            f"workflow_state.{prior_phase}.approval が false です"
            f"（上流フェーズの approval が必要）"
          )

    if reasons:
      return "DEVIATION", 2, reasons
    return "OK", 0, []

  else:
    # false に変える場合：reopen 警告（現状 true のときのみ）
    if current_value is True:
      return "WARN", 1, [
        f"{phase}.{stage} を true から false に戻しています"
        f"（reopen 手続き 計画書 §5.6 に従い、feature impact 判定と下流影響判定を記録してください）"
      ]
    return "OK", 0, []


def _stage_ref(phase, stage):
  """stage 定義内の項目を指す表示用ラベルを返す"""
  return f"stages/{phase}.yaml#{stage}"


def _as_list(value):
  """YAML の単一値または list を list に正規化する"""
  if value is None:
    return []
  if isinstance(value, list):
    return value
  return [value]


def _artifact_matches(cwd, feature, entry):
  """stage 定義の artifact_paths を実ファイルへ解決する"""
  matches_by_pattern = []
  for raw_pattern in _as_list(entry.get("artifact_paths")):
    if not isinstance(raw_pattern, str) or not raw_pattern.strip():
      matches_by_pattern.append((str(raw_pattern), []))
      continue
    pattern = raw_pattern.replace("{feature}", feature)
    path = Path(pattern)
    if path.is_absolute():
      base = Path("/")
      relative_pattern = str(path.relative_to(base))
    else:
      base = Path(cwd)
      relative_pattern = pattern
    if any(token in relative_pattern for token in ("*", "?", "[")):
      matches = sorted(p for p in base.glob(relative_pattern) if p.is_file())
    else:
      candidate = base / relative_pattern
      matches = [candidate] if candidate.is_file() else []
    matches_by_pattern.append((raw_pattern, matches))
  return matches_by_pattern


def _artifact_exists_reasons(cwd, feature, phase, stage, entry, predicate_name):
  """artifact_paths の各 pattern について少なくとも 1 ファイル存在するか調べる"""
  artifact_patterns = _as_list(entry.get("artifact_paths"))
  if not artifact_patterns:
    return [
      f"{_stage_ref(phase, stage)}.{predicate_name} は artifact_paths が必要です"
    ]

  reasons = []
  for pattern, matches in _artifact_matches(cwd, feature, entry):
    if not matches:
      reasons.append(
        f"{_stage_ref(phase, stage)}.{predicate_name} が未充足です: {pattern}"
      )
  return reasons


def _section_reasons(cwd, feature, phase, stage, entry, predicate_name):
  """必須節が artifact に含まれるか調べる"""
  existence_reasons = _artifact_exists_reasons(
    cwd,
    feature,
    phase,
    stage,
    entry,
    predicate_name,
  )
  if existence_reasons:
    return existence_reasons

  required_sections = [
    value for value in _as_list(entry.get("required_sections"))
    if isinstance(value, str) and value.strip()
  ]
  if not required_sections:
    return [
      f"{_stage_ref(phase, stage)}.{predicate_name} は required_sections が必要です"
    ]

  reasons = []
  for pattern, matches in _artifact_matches(cwd, feature, entry):
    pattern_satisfied = False
    first_missing = []
    first_path = None
    for path in matches:
      try:
        text = path.read_text(encoding="utf-8")
      except OSError as e:
        reasons.append(f"{path} を読めません: {e}")
        continue
      missing = [section for section in required_sections if section not in text]
      if not missing:
        pattern_satisfied = True
        break
      if first_path is None:
        first_path = path
        first_missing = missing
    if not pattern_satisfied:
      reasons.append(
        f"{_stage_ref(phase, stage)}.{predicate_name} の必須節が不足しています: "
        f"{pattern} ({first_path}): {', '.join(first_missing)}"
      )
  return reasons


def _front_matter_from_markdown(path):
  """Markdown 先頭の YAML front matter を dict として読む"""
  try:
    text = path.read_text(encoding="utf-8")
  except OSError:
    return None
  lines = text.splitlines()
  if not lines or lines[0].strip() != "---":
    return None
  for index in range(1, len(lines)):
    if lines[index].strip() == "---":
      try:
        data = yaml.safe_load("\n".join(lines[1:index]))
      except yaml.YAMLError:
        return None
      return data if isinstance(data, dict) else None
  return None


def _nested_value(data, dotted_key):
  """dict から dotted key の値を取り出す"""
  current = data
  for part in dotted_key.split("."):
    if not isinstance(current, dict) or part not in current:
      return None
    current = current[part]
  return current


def _author_reviewer_reasons(cwd, feature, phase, stage, entry, predicate_name):
  """front matter の author/reviewer 異名規律を調べる"""
  section_reasons = _section_reasons(cwd, feature, phase, stage, entry, predicate_name)
  if section_reasons:
    return section_reasons

  reasons = []
  for pattern, matches in _artifact_matches(cwd, feature, entry):
    pattern_satisfied = False
    for path in matches:
      front_matter = _front_matter_from_markdown(path)
      if front_matter is None:
        continue
      author = _nested_value(front_matter, "author.identity")
      reviewer = _nested_value(front_matter, "reviewer.identity")
      separation = _nested_value(front_matter, "reviewer.separation_from_author")
      if (
        isinstance(author, str)
        and author.strip()
        and isinstance(reviewer, str)
        and reviewer.strip()
        and author != reviewer
        and separation is not False
      ):
        pattern_satisfied = True
        break
    if not pattern_satisfied:
      reasons.append(
        f"{_stage_ref(phase, stage)}.{predicate_name} は author.identity と "
        f"reviewer.identity の異名 front-matter が必要です: {pattern}"
      )
  return reasons


def _all_features_review_ready_reasons(cwd, phase, stage):
  """全機能で drafting と triad-review が完了しているか調べる"""
  reasons = []
  for feature in FEATURE_ORDER:
    spec = load_spec_json(Path(cwd), feature)
    state = {}
    if isinstance(spec, dict):
      state = spec.get("workflow_state", {}).get(phase, {})
    if not isinstance(state, dict):
      reasons.append(f"{feature}.{phase} の workflow_state が見つかりません")
      continue
    for required_stage in ("drafting", "triad-review"):
      if state.get(required_stage) is not True:
        reasons.append(
          f"{_stage_ref(phase, stage)}.all_features_drafting_and_triad_review_completed "
          f"が未充足です: {feature}.{phase}.{required_stage} が true ではありません"
        )
  return reasons


def _alignment_passed_reasons(cwd, feature, phase, stage, entry, predicate_name):
  """整合確認証跡が pass かつ未消化所見 0 件か調べる"""
  existence_reasons = _artifact_exists_reasons(
    cwd,
    feature,
    phase,
    stage,
    entry,
    predicate_name,
  )
  if existence_reasons:
    return existence_reasons

  for _, matches in _artifact_matches(cwd, feature, entry):
    for path in matches:
      data = load_yaml_file(path)
      if isinstance(data, dict):
        verdict = data.get("verdict", data.get("status", data.get("result")))
        unresolved = data.get(
          "unresolved_findings",
          data.get("open_findings", data.get("remaining_findings")),
        )
        if str(verdict).lower() in ("ok", "pass", "passed") and unresolved == 0:
          return []
      try:
        text = path.read_text(encoding="utf-8")
      except OSError:
        continue
      lower_text = text.lower()
      has_pass = "pass" in lower_text or "passed" in lower_text or "ok" in lower_text
      has_zero = (
        "unresolved_findings: 0" in lower_text
        or "open_findings: 0" in lower_text
        or "remaining_findings: 0" in lower_text
        or "未消化所見: 0" in text
      )
      if has_pass and has_zero:
        return []
  return [
    f"{_stage_ref(phase, stage)}.{predicate_name} は pass かつ未消化所見 0 件の"
    "証跡が必要です"
  ]


def _human_approval_reasons(cwd, feature, phase, stage, entry, predicate_name):
  """明示承認証跡と proxy_model 代行可否を調べる"""
  if entry.get("actor") == "proxy_model":
    config = load_yaml_file(Path(cwd) / "reviewcompass.yaml")
    proxy_allowed = False
    if isinstance(config, dict):
      human_proxy = config.get("human_proxy")
      if isinstance(human_proxy, dict):
        proxy_allowed = human_proxy.get("proxy_allowed") is True
    if not proxy_allowed:
      return [
        f"{_stage_ref(phase, stage)}.{predicate_name} は proxy_model 代行許可が"
        "必要です"
      ]

  record_path = entry.get("approval_record_path")
  if isinstance(record_path, str) and record_path.strip():
    resolved_record_path = Path(cwd) / record_path
    if resolved_record_path.is_file():
      return _approval_gate_record_reasons(
        resolved_record_path,
        phase,
        stage,
        predicate_name,
      )
    return [
      f"{_stage_ref(phase, stage)}.{predicate_name} の承認証跡がありません: "
      f"{record_path}"
    ]
  return _artifact_exists_reasons(cwd, feature, phase, stage, entry, predicate_name)


def _approval_gate_record_reasons(record_path, phase, stage, predicate_name):
  """approval-gate-v1 record の場合だけ中身を検査する。"""
  try:
    record = load_yaml_file(record_path)
  except (OSError, yaml.YAMLError) as exc:
    return [f"{record_path} を承認証跡として読めません: {exc}"]

  if not isinstance(record, dict) or record.get("schema_version") != "approval-gate-v1":
    return []

  result = approval_gate.validate_approval_gate_record(record)
  reasons = list(result.get("reasons") or [])

  if record.get("decision") != "approved":
    reasons.append(f"approved 以外の decision は approval predicate を満たしません: {record.get('decision')}")

  if record.get("consumed") is True:
    reasons.append("approval gate record は既に consumed です")

  if record.get("decision_scope") == "human_only" and record.get("decided_by") not in {"user", "human"}:
    reasons.append("human_only decision は人間 actor でのみ承認できます")

  if reasons:
    prefix = f"{_stage_ref(phase, stage)}.{predicate_name}"
    return [f"{prefix} の approval gate record が不正です: {reason}" for reason in reasons]
  return []


def _depends_on_reasons(cwd, phase, stage):
  """feature-dependency.yaml の depends_on 値域を調べる"""
  candidates = [
    Path(cwd) / "stages" / "feature-dependency.yaml",
    Path(cwd) / "feature-dependency.yaml",
  ]
  dependency_path = next((path for path in candidates if path.exists()), None)
  if dependency_path is None:
    return [
      f"{_stage_ref(phase, stage)}.depends_on_resolves_correctly は "
      "feature-dependency.yaml が必要です"
    ]
  data = load_yaml_file(dependency_path)
  if not isinstance(data, dict):
    return [f"{dependency_path} を YAML object として読めません"]

  features = data.get("features", data)
  if not isinstance(features, dict):
    return [f"{dependency_path} の features は object が必要です"]

  reasons = []
  for feature, value in features.items():
    depends_on = value.get("depends_on", []) if isinstance(value, dict) else []
    if depends_on is None:
      continue
    if isinstance(depends_on, list):
      invalid = [item for item in depends_on if not isinstance(item, str)]
      if invalid:
        reasons.append(f"{feature}.depends_on は文字列 list が必要です")
    elif isinstance(depends_on, dict):
      for dep_name, dep_kind in depends_on.items():
        if not isinstance(dep_name, str) or dep_kind not in ("hard", "review"):
          reasons.append(
            f"{feature}.depends_on.{dep_name} は hard または review が必要です"
          )
    else:
      reasons.append(f"{feature}.depends_on は list または object が必要です")
  return reasons


def _string_completion_predicate_reasons(cwd, feature, phase, stage, entry, predicate):
  """正本で定義された文字列 completion_predicate を評価する"""
  if predicate == "artifact_exists":
    return _artifact_exists_reasons(cwd, feature, phase, stage, entry, predicate)
  if predicate == "artifact_exists_and_sections_present":
    return _section_reasons(cwd, feature, phase, stage, entry, predicate)
  if predicate == "artifact_exists_and_sections_present_and_author_reviewer_distinct":
    return _author_reviewer_reasons(cwd, feature, phase, stage, entry, predicate)
  if predicate == "all_features_drafting_and_triad_review_completed":
    return _all_features_review_ready_reasons(cwd, phase, stage)
  if predicate == "cross_spec_alignment_passed":
    return _alignment_passed_reasons(cwd, feature, phase, stage, entry, predicate)
  if predicate == "explicit_human_approval_recorded":
    return _human_approval_reasons(cwd, feature, phase, stage, entry, predicate)
  if predicate == "depends_on_resolves_correctly":
    return _depends_on_reasons(cwd, phase, stage)
  return [
    f"{_stage_ref(phase, stage)}.completion_predicate は未対応です: {predicate}"
  ]


def completion_predicate_reasons(cwd, feature, phase, stage, new_value):
  """completion_predicate を保守的に評価する"""
  if not new_value:
    return []

  stage_definition_path = Path(cwd) / "stages" / f"{phase}.yaml"
  if not stage_definition_path.exists():
    return []

  try:
    stage_definition = load_yaml_file(stage_definition_path)
  except (OSError, yaml.YAMLError) as e:
    return [f"stage 定義 YAML を読めません: {stage_definition_path}: {e}"]

  if not isinstance(stage_definition, dict):
    return []
  stage_entries = stage_definition.get("stages")
  if not isinstance(stage_entries, list):
    return []

  for entry in stage_entries:
    if not isinstance(entry, dict) or entry.get("name") != stage:
      continue
    predicate = entry.get("completion_predicate")
    if predicate is None:
      continue
    if isinstance(predicate, str):
      return _string_completion_predicate_reasons(
        cwd,
        feature,
        phase,
        stage,
        entry,
        predicate,
      )
    if not isinstance(predicate, dict):
      return [
        f"stages/{phase}.yaml#{stage}.completion_predicate は mapping が必要です"
      ]
    predicate_type = predicate.get("type")
    if predicate_type == "file_exists":
      path_value = predicate.get("path")
      if not isinstance(path_value, str) or not path_value.strip():
        return [
          f"stages/{phase}.yaml#{stage}.completion_predicate.path が必要です"
        ]
      if not (Path(cwd) / path_value).is_file():
        return [
          f"stages/{phase}.yaml#{stage}.completion_predicate file_exists が未充足です: "
          f"{path_value}"
        ]
      return []
    else:
      return [
        f"stages/{phase}.yaml#{stage}.completion_predicate type は未対応です: "
        f"{predicate_type}"
      ]
  return []


def format_current_state_text(feature, phase, phase_state):
  """現状を人間可読のテキストとして整形する（仕様 §7.2 サンプル準拠で小文字真偽値）"""
  lines = [f"{feature}.{phase}:"]
  for s in PHASE_STAGES[phase]:
    value = phase_state.get(s, False)
    value_str = "true" if value else "false"
    lines.append(f"  {s}: {value_str}")
  return "\n".join(lines)


def format_human_output(verdict, exit_code, action_str, reasons, current_state_text):
  """人間可読出力を整形する（仕様 §7.2）"""
  if verdict == "OK" and exit_code == 0:
    return f"[OK] {action_str}"
  lines = [
    f"[VERDICT] {verdict}（exit {exit_code}）",
    f"[ACTION] {action_str}",
    "[REASON]",
  ]
  if reasons:
    for r in reasons:
      lines.append(f"  - {r}")
  else:
    lines.append("  - 問題は検出されませんでした")
  lines.append("[CURRENT STATE]")
  for line in current_state_text.splitlines():
    lines.append(f"  {line}")
  return "\n".join(lines)


def format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict):
  """JSON 出力を整形する（仕様 §7.3）"""
  return json.dumps(
    {
      "verdict": verdict,
      "exit_code": exit_code,
      "action": action_dict,
      "reasons": reasons,
      "current_state": current_state_dict,
    },
    ensure_ascii=False,
    indent=2,
  )


def format_next_json_output(verdict, exit_code, next_action, reasons, current_state_dict):
  """next サブコマンドの JSON 出力を整形する"""
  return json.dumps(
    {
      "verdict": verdict,
      "exit_code": exit_code,
      "next_action": next_action,
      "reasons": reasons,
      "current_state": current_state_dict,
    },
    ensure_ascii=False,
    indent=2,
  )


def _dedupe_strings(values):
  """文字列配列を順序保持で重複排除する"""
  seen = set()
  result = []
  for value in values:
    if not isinstance(value, str) or not value:
      continue
    if value in seen:
      continue
    seen.add(value)
    result.append(value)
  return result


def _sha256_text(value):
  """文字列内容の sha256 を返す"""
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _render_next_action_template(value, next_action):
  """next_action の値で required_input のテンプレートを解決する"""
  if isinstance(value, str):
    feature_value = next_action.get("feature") or ""
    if "{feature}" in value and isinstance(feature_value, list):
      rendered = []
      for feature in feature_value:
        replacements = {
          "feature": feature,
          "phase": next_action.get("phase") or "",
          "stage": next_action.get("stage") or "",
          "kind": next_action.get("kind") or "",
          "file": next_action.get("file") or "",
        }
        try:
          rendered.append(value.format(**replacements))
        except (KeyError, ValueError):
          rendered.append(value)
      return rendered
    replacements = {
      "feature": feature_value,
      "phase": next_action.get("phase") or "",
      "stage": next_action.get("stage") or "",
      "kind": next_action.get("kind") or "",
      "file": next_action.get("file") or "",
    }
    try:
      return value.format(**replacements)
    except (KeyError, ValueError):
      return value
  if isinstance(value, list):
    feature_value = next_action.get("feature") or ""
    if (
      isinstance(feature_value, list)
      and value
      and all(isinstance(item, str) for item in value)
      and any("{feature}" in item for item in value)
    ):
      rendered = []
      for feature in feature_value:
        scoped_action = dict(next_action)
        scoped_action["feature"] = feature
        for item in value:
          resolved = _render_next_action_template(item, scoped_action)
          if isinstance(resolved, list):
            rendered.extend(resolved)
          else:
            rendered.append(resolved)
      return rendered
    rendered = []
    for item in value:
      resolved = _render_next_action_template(item, next_action)
      if isinstance(resolved, list):
        rendered.extend(resolved)
      else:
        rendered.append(resolved)
    return rendered
  if isinstance(value, dict):
    return {
      key: _render_next_action_template(item, next_action)
      for key, item in value.items()
    }
  return value


def _load_discipline_map(cwd):
  """next_action 別の直前必読規律マップを読み込む"""
  script_root = Path(__file__).resolve().parents[1]
  candidate_paths = [
    Path(cwd) / DEFAULT_DISCIPLINE_MAP_PATH,
    script_root / DEFAULT_DISCIPLINE_MAP_PATH,
  ]
  for map_path in candidate_paths:
    if not map_path.exists():
      continue
    try:
      loaded = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
      continue
    if isinstance(loaded, dict):
      return loaded
  return DEFAULT_DISCIPLINE_MAP


def _script_root():
  """ReviewCompass スクリプト基準のリポジトリ root を返す"""
  return Path(__file__).resolve().parents[1]


def required_disciplines_for_next_action(cwd, next_action):
  """next_action の直前に読むべき規律・運用文書を返す"""
  discipline_map = _load_discipline_map(cwd)
  result = []
  result.extend(discipline_map.get("default") or [])

  by_kind = discipline_map.get("by_kind") or {}
  if isinstance(by_kind, dict):
    result.extend(by_kind.get(next_action.get("kind")) or [])

  by_stage = discipline_map.get("by_stage") or {}
  if isinstance(by_stage, dict):
    result.extend(by_stage.get(next_action.get("stage")) or [])

  return _dedupe_strings(result)


def _required_input_entries_for_next_action(cwd, next_action):
  """next_action の直前に解決すべき入力定義を返す"""
  discipline_map = _load_discipline_map(cwd)
  required_inputs = discipline_map.get("required_inputs") or {}
  if not isinstance(required_inputs, dict):
    return []

  result = []
  default = required_inputs.get("default") or []
  if isinstance(default, list):
    result.extend(default)

  by_kind = required_inputs.get("by_kind") or {}
  if isinstance(by_kind, dict):
    entries = by_kind.get(next_action.get("kind")) or []
    if isinstance(entries, list):
      result.extend(entries)

  by_stage = required_inputs.get("by_stage") or {}
  if isinstance(by_stage, dict):
    entries = by_stage.get(next_action.get("stage")) or []
    if isinstance(entries, list):
      result.extend(entries)

  return result


def _resolve_required_input(cwd, entry, next_action):
  """入力定義を現プロジェクトの状態に解決する"""
  if not isinstance(entry, dict):
    return None

  resolved = {
    key: value
    for key, value in entry.items()
    if key != "resolver"
  }
  resolver = entry.get("resolver") or {}
  if not isinstance(resolver, dict):
    return resolved

  if resolver.get("kind") == "next_action_template":
    for key, value in resolver.items():
      if key == "kind":
        continue
      resolved[key] = _render_next_action_template(value, next_action)
    return resolved

  if resolver.get("kind") == "static_path_template":
    path = resolver.get("path")
    if isinstance(path, str):
      resolved["path"] = path
    return resolved

  if resolver.get("kind") == "project_state":
    path = resolver.get("path")
    if isinstance(path, str):
      resolved["path"] = path
      if entry.get("source_type") == "carry_forward_register":
        resolved["unresolved_count"] = count_unresolved_carry_forward_items(
          Path(cwd) / path,
        )

  return resolved


def required_inputs_for_next_action(cwd, next_action):
  """next_action の直前に解決すべき抽象入力を返す"""
  result = []
  for entry in _required_input_entries_for_next_action(cwd, next_action):
    resolved = _resolve_required_input(cwd, entry, next_action)
    if resolved is not None:
      result.append(resolved)
  return result


def _find_decision_point(catalog, group, point_id):
  """decision_points から指定 group/id の項目を返す"""
  if not isinstance(catalog, dict):
    return None
  entries = catalog.get(group)
  if not isinstance(entries, list):
    return None
  for entry in entries:
    if isinstance(entry, dict) and entry.get("id") == point_id:
      return entry
  return None


def _decision_point_refs_for_next_action(next_action):
  """next_action から対応する判定点参照を作る"""
  refs = []
  kind = next_action.get("kind")
  if isinstance(kind, str) and kind:
    refs.append({"group": "next_action_kind", "id": kind})

  stage = next_action.get("stage")
  if isinstance(stage, str) and stage:
    refs.append({"group": "workflow_stage", "id": stage})

  required_action = next_action.get("required_action")
  if isinstance(required_action, str) and required_action:
    refs.append({"group": "reopen_required_action", "id": required_action})

  return refs


def effective_prompt_for_next_action(cwd, next_action):
  """next_action に対応する effective prompt 元資料メタデータを返す"""
  discipline_map = _load_discipline_map(cwd)
  catalog = discipline_map.get("decision_points")
  refs = []
  source_refs = []
  policies = []

  for ref in _decision_point_refs_for_next_action(next_action):
    entry = _find_decision_point(catalog, ref["group"], ref["id"])
    if entry is None:
      continue
    refs.append(ref)
    source_refs.extend(entry.get("prompt_source_refs") or [])
    policy = entry.get("effective_prompt_policy")
    if isinstance(policy, str) and policy:
      policies.append(policy)

  if not refs:
    return None

  return {
    "effective_prompt_policy": (
      policies[0] if policies else "one_effective_prompt_per_decision_point"
    ),
    "decision_point_refs": refs,
    "prompt_source_refs": _dedupe_strings(source_refs),
  }


def _sanitize_prompt_path_part(value):
  """effective prompt ファイル名に使える ASCII 文字列へ寄せる"""
  result = []
  for char in str(value):
    if char.isalnum() or char in ("-", "_"):
      result.append(char)
    else:
      result.append("-")
  cleaned = "".join(result).strip("-")
  while "--" in cleaned:
    cleaned = cleaned.replace("--", "-")
  return cleaned or "unknown"


def _effective_prompt_relative_path(effective_prompt):
  """判定点参照から effective prompt の保存先を決める"""
  parts = []
  for ref in effective_prompt.get("decision_point_refs") or []:
    if not isinstance(ref, dict):
      continue
    group = _sanitize_prompt_path_part(ref.get("group", "unknown"))
    point_id = _sanitize_prompt_path_part(ref.get("id", "unknown"))
    parts.append(f"{group}-{point_id}")
  if not parts:
    parts.append("unknown")
  filename = "__".join(parts) + ".prompt.md"
  return str(Path(DEFAULT_EFFECTIVE_PROMPT_DIR) / filename)


def _split_prompt_source_ref(source_ref):
  """source ref を path と anchor に分ける"""
  if "#" not in source_ref:
    return source_ref, None
  path_value, anchor = source_ref.split("#", 1)
  return path_value, anchor or None


def _resolve_prompt_source_path(cwd, source_ref):
  """source ref の実ファイルを cwd または ReviewCompass root から解決する"""
  path_value, _ = _split_prompt_source_ref(source_ref)
  path = Path(path_value)
  if path.is_absolute():
    return path if path.is_file() else None

  candidates = [
    Path(cwd) / path,
    _script_root() / path,
  ]
  return next((candidate for candidate in candidates if candidate.is_file()), None)


def _read_prompt_source(cwd, source_ref):
  """effective prompt 元資料を読む"""
  source_path = _resolve_prompt_source_path(cwd, source_ref)
  if source_path is None:
    return {
      "source_ref": source_ref,
      "loaded": False,
      "content": f"[missing source: {source_ref}]",
    }
  try:
    content = source_path.read_text(encoding="utf-8")
  except OSError as e:
    return {
      "source_ref": source_ref,
      "loaded": False,
      "content": f"[unreadable source: {source_ref}: {e}]",
    }
  return {
    "source_ref": source_ref,
    "loaded": True,
    "content": content,
  }


def _render_effective_prompt_text(next_action, effective_prompt, sources):
  """複数元資料を 1 本の effective prompt 本文へ束ねる"""
  lines = [
    "# Effective Prompt",
    "",
    "## Decision Point",
  ]
  for ref in effective_prompt.get("decision_point_refs") or []:
    lines.append(f"- {ref.get('group')}:{ref.get('id')}")
  lines.extend([
    "",
    "## Next Action",
    json.dumps(next_action, ensure_ascii=False, indent=2),
    "",
    "## Prompt Source Refs",
  ])
  for source_ref in effective_prompt.get("prompt_source_refs") or []:
    lines.append(f"- {source_ref}")
  lines.extend(["", "## Source Contents"])
  for source in sources:
    lines.extend([
      "",
      f"### {source['source_ref']}",
      "",
      source["content"],
    ])
  return "\n".join(lines).rstrip() + "\n"


def materialize_effective_prompt(cwd, next_action, effective_prompt):
  """effective prompt 本文を生成し、パスと sha256 をメタデータへ追記する"""
  sources = [
    _read_prompt_source(cwd, source_ref)
    for source_ref in effective_prompt.get("prompt_source_refs") or []
  ]
  prompt_text = _render_effective_prompt_text(next_action, effective_prompt, sources)
  relative_path = _effective_prompt_relative_path(effective_prompt)
  output_path = Path(cwd) / relative_path
  try:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding="utf-8")
    loaded = all(source["loaded"] for source in sources)
  except OSError:
    loaded = False

  augmented = dict(effective_prompt)
  augmented["effective_prompt_path"] = relative_path
  augmented["effective_prompt_sha256"] = _sha256_text(prompt_text)
  augmented["effective_prompt_loaded"] = loaded
  return augmented


def effective_prompt_for_decision_point(cwd, group, point_id):
  """指定した判定点の effective prompt 元資料メタデータを返す"""
  discipline_map = _load_discipline_map(cwd)
  catalog = discipline_map.get("decision_points")
  entry = _find_decision_point(catalog, group, point_id)
  if entry is None:
    return None
  policy = entry.get("effective_prompt_policy")
  return {
    "effective_prompt_policy": (
      policy if isinstance(policy, str) and policy
      else "one_effective_prompt_per_decision_point"
    ),
    "decision_point_refs": [{"group": group, "id": point_id}],
    "prompt_source_refs": _dedupe_strings(entry.get("prompt_source_refs") or []),
  }


def attach_required_context(cwd, next_action):
  """next_action に直前必読規律と抽象入力を付与する"""
  augmented = dict(next_action)
  augmented["required_disciplines"] = required_disciplines_for_next_action(
    cwd,
    next_action,
  )
  required_inputs = required_inputs_for_next_action(cwd, next_action)
  if required_inputs:
    augmented["required_inputs"] = required_inputs
  effective_prompt = effective_prompt_for_next_action(cwd, augmented)
  if effective_prompt is not None:
    augmented["effective_prompt"] = materialize_effective_prompt(
      cwd,
      augmented,
      effective_prompt,
    )
  return augmented


def append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict):
  """ログを JSON Lines 形式で追記する（仕様 §8.1）"""
  log_path = Path(log_path)
  log_path.parent.mkdir(parents=True, exist_ok=True)

  jst = timezone(timedelta(hours=9))
  entry = {
    "timestamp": datetime.now(jst).isoformat(),
    "action": action_dict,
    "verdict": verdict,
    "exit_code": exit_code,
    "reasons": reasons,
    "current_state": current_state_dict,
  }

  with open(log_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def path_specs_overlap(left, right):
  """allowed_paths の衝突を保守的に判定する"""
  left_value = str(left).rstrip("/")
  right_value = str(right).rstrip("/")
  return (
    left_value == right_value
    or left_value.startswith(right_value + "/")
    or right_value.startswith(left_value + "/")
  )


def tasks_have_dependency(left_task, right_task):
  """2 タスク間に直列化の依存宣言があるかを判定する"""
  left_id = left_task.get("task_id")
  right_id = right_task.get("task_id")
  left_depends_on = set(left_task.get("depends_on") or [])
  right_depends_on = set(right_task.get("depends_on") or [])
  return right_id in left_depends_on or left_id in right_depends_on


def _resolve_plan_path(cwd, base_dir, path_value):
  """plan 内の相対パスを、plan 基準または cwd 基準で解決する。"""
  path = Path(path_value)
  if path.is_absolute():
    return path
  base_candidate = Path(base_dir) / path
  if base_candidate.exists():
    return base_candidate
  return Path(cwd) / path


def validate_autonomous_execution_evidence(plan, cwd, base_dir):
  """自律実行計画が参照する raw/triage または実装証跡を検査する。"""
  reasons = []
  current_state = {
    "review_run_dir": None,
    "required_raw_paths": [],
    "triage_path": None,
    "human_required_count": None,
  }
  evidence = plan.get("execution_evidence")
  if not isinstance(evidence, dict):
    return ["execution_evidence が必要です"], current_state

  review_run_dir_value = evidence.get("review_run_dir")
  if not isinstance(review_run_dir_value, str) or not review_run_dir_value.strip():
    outputs_policy = plan.get("outputs_policy") or {}
    if outputs_policy.get("implementation_diff") == "commit_candidate":
      completed_tasks = evidence.get("completed_tasks")
      if not isinstance(completed_tasks, list) or not completed_tasks:
        reasons.append("execution_evidence.completed_tasks が必要です")
      current_state["completed_tasks"] = completed_tasks or []
      current_state["parallelized_operations"] = evidence.get(
        "parallelized_operations",
        [],
      )
      human_required_count = evidence.get("human_required_count")
      current_state["human_required_count"] = human_required_count
      if not isinstance(human_required_count, int):
        reasons.append("execution_evidence.human_required_count が必要です")
      elif human_required_count:
        reasons.append(
          f"execution_evidence human_required が残っています: {human_required_count}"
        )
      return reasons, current_state
    reasons.append("execution_evidence.review_run_dir が必要です")
    return reasons, current_state

  review_run_dir = _resolve_plan_path(cwd, base_dir, review_run_dir_value)
  current_state["review_run_dir"] = str(review_run_dir_value)
  if not review_run_dir.is_dir():
    reasons.append("execution_evidence.review_run_dir が存在しません")

  required_raw_paths = evidence.get("required_raw_paths")
  if not isinstance(required_raw_paths, list) or not required_raw_paths:
    reasons.append("execution_evidence.required_raw_paths が必要です")
    required_raw_paths = []
  current_state["required_raw_paths"] = required_raw_paths
  for raw_path_value in required_raw_paths:
    if not isinstance(raw_path_value, str) or not raw_path_value.strip():
      reasons.append("execution_evidence.required_raw_paths は文字列配列が必要です")
      continue
    raw_path = review_run_dir / raw_path_value
    if not raw_path.is_file():
      reasons.append(
        f"execution_evidence.required_raw_paths が見つかりません: {raw_path_value}"
      )
      continue
    if raw_path.stat().st_size == 0:
      reasons.append(
        f"execution_evidence.required_raw_paths が空です: {raw_path_value}"
      )

  triage_path_value = evidence.get("triage_path")
  if not isinstance(triage_path_value, str) or not triage_path_value.strip():
    reasons.append("execution_evidence.triage_path が必要です")
    return reasons, current_state
  triage_path = review_run_dir / triage_path_value
  current_state["triage_path"] = triage_path_value
  if not triage_path.is_file():
    reasons.append("execution_evidence.triage_path が見つかりません")
    return reasons, current_state

  triage = load_yaml_file(triage_path)
  if not isinstance(triage, dict):
    reasons.append("execution_evidence.triage_path は YAML mapping が必要です")
    return reasons, current_state
  items = triage.get("items")
  if not isinstance(items, list):
    reasons.append("execution_evidence.triage_path.items は list が必要です")
    return reasons, current_state
  human_required_count = sum(
    1 for item in items
    if isinstance(item, dict) and item.get("decision_status") == "human_required"
  )
  current_state["human_required_count"] = human_required_count
  if evidence.get("require_no_human_required") is True and human_required_count:
    reasons.append(
      f"execution_evidence human_required が残っています: {human_required_count}"
    )
  return reasons, current_state


def validate_autonomous_parallel_plan(plan, cwd=None, base_dir=None):
  """自律・並列モード実行計画を fail-closed で検査する"""
  reasons = []
  cwd = Path(cwd) if cwd is not None else Path.cwd()
  base_dir = Path(base_dir) if base_dir is not None else cwd
  current_state = {
    "mode": None,
    "run_id": None,
    "task_count": 0,
    "parallel_task_count": 0,
    "checked_gates": list(AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES),
    "history_ledger_path": None,
    "execution_evidence": {},
  }

  if not isinstance(plan, dict):
    return reasons + ["plan は YAML mapping である必要があります"], current_state

  current_state["mode"] = plan.get("mode")
  current_state["run_id"] = plan.get("run_id")

  if plan.get("mode") != "autonomous_parallel":
    reasons.append("mode は autonomous_parallel である必要があります")
  if not plan.get("run_id"):
    reasons.append("run_id が必要です")

  authorization = plan.get("authorization")
  if not isinstance(authorization, dict):
    reasons.append("authorization が必要です")
  else:
    approved_by = authorization.get("approved_by")
    if approved_by not in ("user", "proxy_model"):
      reasons.append("authorization.approved_by は user または proxy_model が必要です")
    if not authorization.get("approval_record_path"):
      reasons.append("authorization.approval_record_path が必要です")
    if authorization.get("summary_presented_to_user") is not True:
      reasons.append("authorization.summary_presented_to_user は true が必要です")
    if authorization.get("triage_presented_to_user") is not True:
      reasons.append("authorization.triage_presented_to_user は true が必要です")

  tasks = plan.get("tasks")
  if not isinstance(tasks, list) or not tasks:
    reasons.append("tasks は 1 件以上の list が必要です")
    tasks = []
  current_state["task_count"] = len(tasks)
  current_state["parallel_task_count"] = len([
    task for task in tasks
    if isinstance(task, dict) and not task.get("depends_on")
  ])

  seen_task_ids = set()
  for index, task in enumerate(tasks):
    task_label = task.get("task_id") if isinstance(task, dict) else f"index:{index}"
    if not isinstance(task, dict):
      reasons.append(f"tasks[{index}] は mapping が必要です")
      continue

    task_id = task.get("task_id")
    if not task_id:
      reasons.append(f"tasks[{index}].task_id が必要です")
    elif task_id in seen_task_ids:
      reasons.append(f"tasks[{index}].task_id が重複しています: {task_id}")
    else:
      seen_task_ids.add(task_id)

    if not task.get("source_finding_ids"):
      reasons.append(f"{task_label}.source_finding_ids が必要です")
    if not task.get("allowed_paths"):
      reasons.append(f"{task_label}.allowed_paths が必要です")
    if not task.get("expected_tests"):
      reasons.append(f"{task_label}.expected_tests が必要です")
    stop_conditions = task.get("stop_conditions") or []
    if "important_decision_requires_approval" not in stop_conditions:
      reasons.append(
        f"{task_label}.stop_conditions に important_decision_requires_approval が必要です"
      )

    assignee = task.get("assignee")
    if not isinstance(assignee, dict):
      reasons.append(f"{task_label}.assignee が必要です")
      continue
    assignee_kind = assignee.get("kind")
    worktree_policy = assignee.get("worktree_policy")
    if assignee_kind not in ("main_session", "subthread", "subagent"):
      reasons.append(f"{task_label}.assignee.kind が無効です")
    if assignee_kind in ("subthread", "subagent") and worktree_policy != "separate_worktree":
      reasons.append(
        f"{task_label}.assignee.worktree_policy は separate_worktree が必要です"
      )
    outputs_policy = plan.get("outputs_policy") or {}
    commit_candidate = outputs_policy.get("implementation_diff") == "commit_candidate"
    if (
      assignee_kind == "main_session"
      and worktree_policy == "same_worktree"
      and not commit_candidate
    ):
      if task.get("output_only") is not True or task.get("writes_repo_diff") is not False:
        reasons.append(
          f"{task_label}.output_only は true、writes_repo_diff は false が必要です"
        )

    if "writes_repo_diff" not in task:
      reasons.append(f"{task_label}.writes_repo_diff が必要です")
    if "output_only" not in task:
      reasons.append(f"{task_label}.output_only が必要です")

  evidence_reasons, evidence_state = validate_autonomous_execution_evidence(
    plan,
    cwd,
    base_dir,
  )
  reasons.extend(evidence_reasons)
  current_state["execution_evidence"] = evidence_state

  for left_index, left_task in enumerate(tasks):
    if not isinstance(left_task, dict):
      continue
    for right_task in tasks[left_index + 1:]:
      if not isinstance(right_task, dict):
        continue
      if tasks_have_dependency(left_task, right_task):
        continue
      for left_path in left_task.get("allowed_paths") or []:
        for right_path in right_task.get("allowed_paths") or []:
          if path_specs_overlap(left_path, right_path):
            reasons.append(
              "依存関係のない並列タスクの allowed_paths が衝突しています: "
              f"{left_task.get('task_id')}:{left_path} / "
              f"{right_task.get('task_id')}:{right_path}"
            )

  integration_gate = plan.get("integration_gate")
  if not isinstance(integration_gate, dict):
    reasons.append("integration_gate が必要です")
  else:
    for key in AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES:
      if integration_gate.get(key) is not True:
        reasons.append(f"integration_gate.{key} は true が必要です")

  outputs_policy = plan.get("outputs_policy")
  if not isinstance(outputs_policy, dict):
    reasons.append("outputs_policy が必要です")
  else:
    for key, expected in AUTONOMOUS_PARALLEL_REQUIRED_OUTPUTS_POLICY.items():
      if outputs_policy.get(key) != expected:
        reasons.append(f"outputs_policy.{key} は {expected} が必要です")

  history = plan.get("history")
  if not isinstance(history, dict):
    reasons.append("history が必要です")
  else:
    ledger_path = history.get("ledger_path")
    current_state["history_ledger_path"] = ledger_path
    if not ledger_path:
      reasons.append("history.ledger_path が必要です")
    elif not str(ledger_path).startswith("docs/logs/autonomous-parallel/"):
      reasons.append(
        "history.ledger_path は docs/logs/autonomous-parallel/ 配下が必要です"
      )
    for key in AUTONOMOUS_PARALLEL_REQUIRED_HISTORY_FLAGS:
      if history.get(key) is not True:
        reasons.append(f"history.{key} は true が必要です")
    if history.get("retention") != "preserve":
      reasons.append("history.retention は preserve が必要です")

  return reasons, current_state


def write_autonomous_parallel_ledger(cwd, plan, verdict, exit_code, reasons, current_state):
  """自律・並列モード実行計画の後追い用台帳を書き出す"""
  history = plan.get("history") if isinstance(plan, dict) else None
  if not isinstance(history, dict):
    return
  ledger_path_value = history.get("ledger_path")
  if not ledger_path_value:
    return

  ledger_path = Path(ledger_path_value)
  if ledger_path.is_absolute():
    return
  ledger_path = cwd / ledger_path
  ledger_path.parent.mkdir(parents=True, exist_ok=True)
  existing_ledger = None
  if ledger_path.exists():
    try:
      existing_ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
      existing_ledger = None

  tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else []
  task_ids = [
    task.get("task_id")
    for task in tasks
    if isinstance(task, dict) and task.get("task_id")
  ]
  ledger = {
    "run_id": plan.get("run_id"),
    "mode": plan.get("mode"),
    "verdict": verdict,
    "exit_code": exit_code,
    "reasons": reasons,
    "task_ids": task_ids,
    "authorization": plan.get("authorization"),
    "history": history,
    "integration_gate": plan.get("integration_gate"),
    "outputs_policy": plan.get("outputs_policy"),
    "current_state": current_state,
  }
  existing_snapshot = None
  if isinstance(existing_ledger, dict):
    existing_snapshot = existing_ledger.get("execution_evidence_snapshot")
  if isinstance(existing_snapshot, dict):
    ledger["execution_evidence_snapshot"] = existing_snapshot
  else:
    ledger["execution_evidence_snapshot"] = build_autonomous_execution_snapshot(
      current_state,
      task_ids,
    )
  if (
    isinstance(existing_ledger, dict)
    and isinstance(existing_ledger.get("integration_result"), dict)
  ):
    ledger["integration_result"] = existing_ledger["integration_result"]
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def build_autonomous_parallel_plan_template(run_id):
  """自律・並列モード実行計画の最小テンプレートを返す"""
  return {
    "mode": "autonomous_parallel",
    "run_id": run_id,
    "authorization": {
      "approved_by": "user",
      "approval_record_path": "docs/notes/approval.md",
      "summary_presented_to_user": True,
      "triage_presented_to_user": True,
    },
    "tasks": [
      {
        "task_id": "task-001",
        "source_finding_ids": ["finding-001"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["path/to/target.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["python3 -m pytest path/to/test.py -q"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      }
    ],
    "execution_evidence": {
      "review_run_dir": f"docs/notes/review-runs/{run_id}-review",
      "required_raw_paths": ["raw/model.round-1.txt"],
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
      "ledger_path": f"docs/logs/autonomous-parallel/{run_id}.yaml",
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


def cmd_autonomous_plan_template(args):
  """自律・並列モード実行計画のテンプレートを書き出す"""
  plan = build_autonomous_parallel_plan_template(args.run_id)
  out_path = Path(args.out)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  review_run_dir = Path.cwd() / "docs" / "notes" / "review-runs" / f"{args.run_id}-review"
  raw_dir = review_run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)
  raw_path = raw_dir / "model.round-1.txt"
  raw_path.write_text("template raw response\n", encoding="utf-8")
  (review_run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "model_results": [
          {
            "model_id": "model",
            "raw_path": "raw/model.round-1.txt",
            "raw_sha256": file_sha256(raw_path),
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (review_run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "triage_status": "decided",
        "items": [
          {
            "finding_id": "finding-001",
            "decision_status": "decided",
            "source_raw_path": "raw/model.round-1.txt",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  out_path.write_text(
    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  print(str(out_path))
  return 0


def cmd_autonomous_plan_record_integration(args):
  """自律・並列モード台帳へ統合結果を追記する"""
  ledger_path = Path(args.ledger)
  try:
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
  except OSError as e:
    print(f"error: ledger を読めません: {e}", file=sys.stderr)
    return 2
  except yaml.YAMLError as e:
    print(f"error: ledger を YAML として読めません: {e}", file=sys.stderr)
    return 2

  if not isinstance(ledger, dict):
    print("error: ledger は YAML mapping である必要があります", file=sys.stderr)
    return 2
  if args.status not in ("completed", "blocked", "rejected"):
    print("error: --status は completed / blocked / rejected のいずれかです", file=sys.stderr)
    return 2
  if not args.tests:
    print("error: --tests が必要です", file=sys.stderr)
    return 2
  if not args.decision:
    print("error: --decision が必要です", file=sys.stderr)
    return 2

  ledger["integration_result"] = {
    "status": args.status,
    "tests": args.tests,
    "decision": args.decision,
  }
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  print(str(ledger_path))
  return 0


def validate_autonomous_ledger(ledger):
  """デプロイ後に plan なしで読める自律・並列台帳を検査する"""
  reasons = []
  current_state = {
    "plan_required": False,
    "run_id": None,
    "completed_tasks": [],
    "parallelized_operations": [],
    "human_required_count": None,
    "integration_status": None,
  }

  if not isinstance(ledger, dict):
    return ["ledger は YAML mapping である必要があります"], current_state

  current_state["run_id"] = ledger.get("run_id")
  if ledger.get("mode") != "autonomous_parallel":
    reasons.append("mode は autonomous_parallel である必要があります")
  if ledger.get("verdict") != "OK" or ledger.get("exit_code") != 0:
    reasons.append("ledger verdict/exit_code が OK/0 ではありません")

  snapshot = ledger.get("execution_evidence_snapshot")
  if not isinstance(snapshot, dict):
    reasons.append("execution_evidence_snapshot が必要です")
    snapshot = {}

  completed_tasks = snapshot.get("completed_tasks")
  if not isinstance(completed_tasks, list) or not completed_tasks:
    reasons.append("execution_evidence_snapshot.completed_tasks が必要です")
  current_state["completed_tasks"] = completed_tasks or []

  parallelized_operations = snapshot.get("parallelized_operations")
  if not isinstance(parallelized_operations, list):
    reasons.append("execution_evidence_snapshot.parallelized_operations が必要です")
  current_state["parallelized_operations"] = parallelized_operations or []

  human_required_count = snapshot.get("human_required_count")
  current_state["human_required_count"] = human_required_count
  if not isinstance(human_required_count, int):
    reasons.append("execution_evidence_snapshot.human_required_count が必要です")
  elif human_required_count:
    reasons.append(
      f"execution_evidence_snapshot human_required が残っています: {human_required_count}"
    )

  integration_result = ledger.get("integration_result")
  if not isinstance(integration_result, dict):
    reasons.append("integration_result が必要です")
    integration_result = {}
  current_state["integration_status"] = integration_result.get("status")
  if integration_result.get("status") not in ("completed", "blocked", "rejected"):
    reasons.append("integration_result.status が不正です")
  if not integration_result.get("tests"):
    reasons.append("integration_result.tests が必要です")
  if not integration_result.get("decision"):
    reasons.append("integration_result.decision が必要です")

  return reasons, current_state


def build_autonomous_execution_snapshot(current_state, task_ids):
  """plan なし監査に必要な実行証跡 snapshot を正規化する"""
  evidence = current_state.get("execution_evidence")
  if not isinstance(evidence, dict):
    evidence = {}
  snapshot = dict(evidence)
  if not isinstance(snapshot.get("completed_tasks"), list):
    snapshot["completed_tasks"] = list(task_ids)
  if not isinstance(snapshot.get("parallelized_operations"), list):
    snapshot["parallelized_operations"] = []
  return snapshot


def cmd_autonomous_ledger_audit(args):
  """自律・並列モード台帳を plan なしで監査する"""
  ledger_path = Path(args.ledger_path)
  action_str = f"autonomous-ledger-audit {ledger_path}"
  action_dict = {
    "subcommand": "autonomous-ledger-audit",
    "args": {
      "ledger_path": str(ledger_path),
    },
  }

  try:
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
  except OSError as e:
    reasons = [f"ledger_path を読めません: {e}"]
    current_state_dict = {"ledger_path": str(ledger_path), "plan_required": False}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2
  except yaml.YAMLError as e:
    reasons = [f"ledger_path を YAML として読めません: {e}"]
    current_state_dict = {"ledger_path": str(ledger_path), "plan_required": False}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2

  reasons, current_state_dict = validate_autonomous_ledger(ledger)
  current_state_dict["ledger_path"] = str(ledger_path)
  verdict = "OK" if not reasons else "DEVIATION"
  exit_code = 0 if not reasons else 2
  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))
  return exit_code


def cmd_autonomous_plan(args):
  """自律・並列モード実行計画の事前検査を行う"""
  cwd = Path.cwd()
  plan_path = Path(args.plan_path)
  action_str = f"autonomous-plan {plan_path}"
  action_dict = {
    "subcommand": "autonomous-plan",
    "args": {
      "plan_path": str(plan_path),
    },
  }

  try:
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
  except OSError as e:
    reasons = [f"plan_path を読めません: {e}"]
    current_state_dict = {"plan_path": str(plan_path)}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2
  except yaml.YAMLError as e:
    reasons = [f"plan_path を YAML として読めません: {e}"]
    current_state_dict = {"plan_path": str(plan_path)}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2

  reasons, current_state_dict = validate_autonomous_parallel_plan(
    plan,
    cwd,
    plan_path.parent,
  )
  current_state_dict["plan_path"] = str(plan_path)
  if reasons:
    verdict, exit_code = "DEVIATION", 2
  else:
    verdict, exit_code = "OK", 0

  write_autonomous_parallel_ledger(
    cwd,
    plan,
    verdict,
    exit_code,
    reasons,
    current_state_dict,
  )

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def cmd_spec_set(args):
  """spec-set サブコマンドのエントリポイント

  戻り値：終了コード（0／1／2）
  """
  feature = args.feature
  phase = args.phase
  stage = args.stage
  new_value_str = args.new_value
  rationale = args.rationale

  # 引数妥当性の検査（仕様 §5.1）
  if new_value_str not in ("true", "false"):
    print(
      f"error: new-value は 'true' または 'false' であるべき。受け取り: {new_value_str}",
      file=sys.stderr,
    )
    return 2
  new_value = (new_value_str == "true")

  if phase not in PHASE_STAGES:
    print(
      f"error: phase '{phase}' は無効です。有効値: {', '.join(PHASE_STAGES.keys())}",
      file=sys.stderr,
    )
    return 2

  if stage not in PHASE_STAGES[phase]:
    print(
      f"error: stage '{stage}' は phase '{phase}' で無効です。"
      f"有効値: {', '.join(PHASE_STAGES[phase])}",
      file=sys.stderr,
    )
    return 2

  # spec.json 読み込み
  cwd = Path.cwd()
  spec_data = load_spec_json(cwd, feature)
  if spec_data is None:
    spec_path = cwd / ".reviewcompass" / "specs" / feature / "spec.json"
    print(
      f"error: spec.json が見つかりません。期待パス: {spec_path}",
      file=sys.stderr,
    )
    return 2

  # 判定
  verdict, exit_code, reasons = judge_spec_set(spec_data, phase, stage, new_value)
  predicate_reasons = completion_predicate_reasons(
    cwd,
    feature,
    phase,
    stage,
    new_value,
  )
  if predicate_reasons:
    reasons.extend(predicate_reasons)
    verdict, exit_code = "DEVIATION", 2
  in_progress_files = list_in_progress_files(cwd)
  allow_reopen_gate_change = is_reopen_pending_gate_change_allowed(
    cwd,
    in_progress_files,
    phase,
    stage,
    new_value,
  )
  if in_progress_files and not allow_reopen_gate_change:
    reasons.insert(
      0,
      "stages/in-progress に進行中ファイルがあります: "
      + ", ".join(in_progress_files),
    )
    verdict, exit_code = "DEVIATION", 2
  elif in_progress_files and allow_reopen_gate_change and verdict == "OK":
    reasons.append(
      "reopen 手続き内の pending gate 変更として許可します"
    )
    verdict, exit_code = "WARN", 1

  # 出力の組み立て
  workflow_state = spec_data.get("workflow_state", {})
  phase_state = workflow_state.get(phase, {})
  current_state_text = format_current_state_text(feature, phase, phase_state)
  if in_progress_files:
    current_state_text += (
      "\n進行中ファイル: " + ", ".join(in_progress_files)
    )
  current_state_dict = {
    feature: {phase: phase_state},
    "in_progress_files": in_progress_files,
  }

  action_str = f"spec-set {feature} {phase} {stage} {new_value_str}"
  action_dict = {
    "subcommand": "spec-set",
    "args": {
      "feature": feature,
      "phase": phase,
      "stage": stage,
      "new_value": new_value,
      "rationale": rationale,
    },
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録（仕様 §8、MVP 必須）
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    # ログ書き込み失敗は処理を止めない（警告のみ）
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def count_unresolved_findings(pending_path):
  """機能横断持ち越し所見ファイルから未消化件数を数える（仕様 §6.2）

  「### A-」で始まり「✅」を含まない行を未消化扱いとする。
  ファイルが存在しない場合は 0 を返す。
  """
  if not Path(pending_path).exists():
    return 0
  count = 0
  for line in Path(pending_path).read_text(encoding="utf-8").splitlines():
    if line.startswith("### A-") and "✅" not in line:
      count += 1
  return count


def count_unresolved_carry_forward_items(register_path):
  """抽象持ち越しレジスタから未解決件数を数える"""
  path = Path(register_path)
  if not path.exists():
    return 0
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
  except (OSError, yaml.YAMLError):
    return 0
  if not isinstance(data, dict):
    return 0
  items = data.get("items") or []
  if not isinstance(items, list):
    return 0
  return sum(
    1
    for item in items
    if isinstance(item, dict) and item.get("status") != "resolved"
  )


def classify_staged_file(filepath):
  """staged ファイルを 3 群に分類する（仕様 §6.2）

  戻り値："dangerous" / "caution" / "normal"
  """
  f_lower = filepath.lower()
  if filepath.startswith(".git/") or "secret" in f_lower or "credential" in f_lower:
    return "dangerous"
  if filepath.endswith("spec.json") or filepath.startswith("docs/plan/"):
    return "caution"
  return "normal"


def staged_file_sha256(cwd, filepath):
  """staged blob の sha256 を返す"""
  result = subprocess.run(
    ["git", "show", f":{filepath}"],
    cwd=str(cwd),
    capture_output=True,
  )
  if result.returncode != 0:
    return None
  return hashlib.sha256(result.stdout).hexdigest()


def staged_file_content_hash(cwd, filepath):
  """staged 内容の hash を返す。削除済み staged path は DELETED sentinel にする"""
  sha256 = staged_file_sha256(cwd, filepath)
  return "DELETED" if sha256 is None else sha256


def is_staged_deleted(cwd, filepath):
  """staged path が削除として index に載っているかを返す"""
  return staged_file_content_hash(cwd, filepath) == "DELETED"


def validate_commit_approval(cwd, staged_files):
  """commit 用ユーザ承認レコードを検査する"""
  resolved_relative = resolve_commit_approval_path(cwd)
  approval_path = Path(cwd) / resolved_relative
  approval_state = {
    "path": resolved_relative,
    "exists": approval_path.exists(),
    "valid": False,
    "target_files": [],
    "target_sha256": {},
    "consumed": None,
    "execution_delegation": None,
  }

  if not approval_path.exists():
    return approval_state, [
      f"ユーザ承認レコードがありません（{DEFAULT_COMMIT_APPROVAL_PATH}）"
    ]

  try:
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return approval_state, [f"ユーザ承認レコードを読めません: {e}"]

  if not isinstance(approval, dict):
    return approval_state, ["ユーザ承認レコードの形式が不正です（object ではありません）"]

  target_files = approval.get("target_files")
  if target_files is None:
    target_files = []
  target_sha256 = approval.get("target_sha256")
  approval_state["target_files"] = target_files
  approval_state["target_sha256"] = target_sha256 if isinstance(target_sha256, dict) else {}
  approval_state["consumed"] = approval.get("consumed")
  approval_state["execution_delegation"] = approval.get("execution_delegation")
  if isinstance(approval.get("target_digest"), dict):
    approval_state["target_digest"] = approval.get("target_digest")
  if approval.get("nonce"):
    approval_state["nonce"] = approval.get("nonce")

  errors = []
  if approval.get("approved_action") != "commit":
    errors.append("ユーザ承認レコードの approved_action が commit ではありません")
  if approval.get("approved_by") != "user":
    errors.append("ユーザ承認レコードの approved_by が user ではありません")
  if approval.get("consumed") is True:
    errors.append("ユーザ承認レコードは消費済みです")
  if not isinstance(target_files, list) or not all(isinstance(f, str) for f in target_files):
    errors.append("ユーザ承認レコードの target_files が文字列配列ではありません")
  else:
    approved_set = set(target_files)
    if "*" not in approved_set:
      out_of_scope = [f for f in staged_files if f not in approved_set]
      if out_of_scope:
        errors.append(
          "承認対象外の staged ファイルがあります: " + ", ".join(out_of_scope)
        )
      if staged_files:
        if not isinstance(target_sha256, dict):
          errors.append("ユーザ承認レコードの target_sha256 が object ではありません")
        else:
          for filepath in staged_files:
            expected_sha = target_sha256.get(filepath)
            actual_sha = staged_file_sha256(cwd, filepath)
            if not isinstance(expected_sha, str) or not expected_sha:
              errors.append(
                f"ユーザ承認レコードの target_sha256 に {filepath} がありません"
              )
            elif expected_sha == "DELETED":
              if actual_sha is not None:
                errors.append(
                  f"ユーザ承認レコードの target_sha256 が DELETED ですが、ファイルが削除されていません: "
                  f"{filepath}"
                )
            elif actual_sha != expected_sha:
              errors.append(
                f"ユーザ承認レコードの target_sha256 が staged 内容と一致しません: "
                f"{filepath}"
              )

  if approval.get("nonce"):
    errors.extend(commit_approval.validate(cwd, approval))

  approval_state["valid"] = not errors
  return approval_state, errors


def _print_commit_approval_result(args, payload):
  if args.json:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
  else:
    print(payload["status"])


def cmd_commit_approval(args):
  """commit-approval サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  try:
    if args.commit_approval_command == "prepare":
      payload = commit_approval.prepare(cwd)
    elif args.commit_approval_command == "record":
      if args.source_text_stdin:
        if not sys.stdin.isatty():
          raise ValueError("承認本文は TTY からの対話入力である必要があります")
        source_text = sys.stdin.readline()
      else:
        source_text = None
      payload = commit_approval.record(
        cwd,
        args.nonce,
        source_text=source_text,
        no_source_text=args.no_source_text,
      )
    elif args.commit_approval_command == "delegate-execution":
      if not sys.stdin.isatty():
        raise ValueError("実行代行承認文は TTY からの対話入力である必要があります")
      source_text = sys.stdin.buffer.readline()
      payload = commit_approval.delegate_execution(
        cwd,
        args.nonce,
        source_text,
      )
    elif args.commit_approval_command == "invalidate":
      payload = commit_approval.invalidate(cwd)
    else:
      return 2
  except (OSError, RuntimeError, ValueError) as e:
    if args.json:
      print(
        json.dumps(
          {"status": "error", "error": str(e)},
          ensure_ascii=False,
          sort_keys=True,
        )
      )
    else:
      print(f"error: {e}", file=sys.stderr)
    return 2
  _print_commit_approval_result(args, payload)
  return 0


def validate_commit_execution_delegation(cwd, approval_state, execution_actor):
  """LLM による commit 実行代行が明示承認されているか検査する"""
  if execution_actor == "human":
    return []

  approval_path = Path(cwd) / approval_state.get("path", DEFAULT_COMMIT_APPROVAL_PATH)
  try:
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return [f"commit 実行代行承認の検査前にユーザ承認レコードを読めません: {e}"]
  if not isinstance(approval, dict):
    return ["commit 実行代行承認の検査前にユーザ承認レコードが object ではありません"]

  if approval.get("nonce"):
    return commit_approval.validate_execution_delegation(cwd, approval)

  delegation = approval_state.get("execution_delegation")
  if not isinstance(delegation, dict):
    return [
      "LLM によるコミット実行代行の明示承認がありません"
      f"（{commit_approval.DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH} が必要）"
    ]

  errors = []
  if delegation.get("delegated_to") != "llm":
    errors.append("execution_delegation.delegated_to が llm ではありません")
  if delegation.get("approved_by") != "user":
    errors.append("execution_delegation.approved_by が user ではありません")
  instruction = delegation.get("explicit_instruction")
  if not isinstance(instruction, str) or not _is_commit_execution_delegation_instruction(instruction):
    errors.append(
      "execution_delegation.explicit_instruction に "
      "LLM によるコミット実行代行の明示がありません"
    )
  return errors


def _is_commit_execution_delegation_instruction(instruction):
  """利用者発言が LLM の commit 実行代行を許可しているか判定する"""
  text = "".join(str(instruction).split())
  if not text:
    return False

  # 「次のコミットまで」は commit 停止点までの自律進行であり、commit 実行は含まない。
  if "次のコミットまで" in text and "代行" not in text and "含め" not in text:
    return False

  # 停止点での単発「コミット」は、LLM に commit 実行を依頼する通常指示として扱う。
  if text in ("コミット", "コミットして", "コミットを実行"):
    return True

  # 全自動の場合は commit 代行を含むことが明示されている場合だけ許可する。
  if "自律" in text and "コミット" in text and ("代行" in text or "含め" in text):
    return True

  if "コミット実行" in text and ("代行" in text or "よい" in text or "許可" in text):
    return True

  return False


def _staged_text(cwd, filepath):
  """staged blob を text として読む"""
  result = subprocess.run(
    ["git", "show", f":{filepath}"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  return result.stdout


def is_deployment_independence_guard_target(filepath):
  """D-023 commit guard の対象 staged artifact かを返す"""
  return (
    filepath.endswith(DEPLOYMENT_INDEPENDENCE_GUARD_SUFFIXES)
    and filepath.startswith(DEPLOYMENT_INDEPENDENCE_GUARD_PREFIXES)
  )


def validate_deployment_independence_for_staged_files(cwd, staged_files):
  """D-023 配置非依存 lint を staged 内容に対して実行する"""
  target_files = [
    filepath for filepath in staged_files
    if (
      is_deployment_independence_guard_target(filepath)
      and not is_staged_deleted(cwd, filepath)
    )
  ]
  state = {
    "target_files": target_files,
    "findings": [],
  }
  errors = []
  for filepath in target_files:
    text = _staged_text(cwd, filepath)
    if text is None:
      errors.append(f"配置非依存 lint 対象の staged 内容を読めません: {filepath}")
      continue
    findings = lint_text(filepath, text)
    state["findings"].extend(findings)

  for finding in state["findings"]:
    errors.append(
      "配置非依存 lint 違反: {path}:{line}: {kind}: {value}".format(
        path=finding["path"],
        line=finding["line"],
        kind=finding["kind"],
        value=finding["value"],
      )
    )
  return state, errors


def is_document_link_guard_target(filepath):
  """commit guard で文書リンク lint の対象 staged artifact かを返す"""
  return (
    filepath.endswith(DOCUMENT_LINK_GUARD_SUFFIXES)
    and filepath.startswith(DOCUMENT_LINK_GUARD_PREFIXES)
  )


def validate_document_links_for_staged_files(cwd, staged_files):
  """staged 文書のリンク存在・アンカー・既知の意味的組み合わせを検査する"""
  target_files = [
    filepath for filepath in staged_files
    if is_document_link_guard_target(filepath) and not is_staged_deleted(cwd, filepath)
  ]
  path_texts = {}
  errors = []
  for filepath in target_files:
    text = _staged_text(cwd, filepath)
    if text is None:
      errors.append(f"文書リンク lint 対象の staged 内容を読めません: {filepath}")
      continue
    path_texts[Path(filepath)] = text
  findings = lint_document_link_texts(path_texts, root=Path(cwd))
  state = {
    "target_files": target_files,
    "findings": findings,
  }
  for finding in findings:
    suffix = ""
    if "anchor" in finding:
      suffix += f"#{finding['anchor']}"
    if "expected" in finding:
      suffix += f" expected={finding['expected']}"
    errors.append(
      "文書リンク lint 違反: {path}:{line}: {kind}: {ref} -> {target}{suffix}".format(
        path=finding["path"],
        line=finding["line"],
        kind=finding["kind"],
        ref=finding["ref"],
        target=finding["target"],
        suffix=suffix,
      )
    )
  return state, errors


def commit_file_text(cwd, commitish, path):
  """指定 commit 内のファイル内容を text として返す"""
  result = subprocess.run(
    ["git", "show", f"{commitish}:{path}"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  return result.stdout


def _front_matter_from_text(text):
  """文字列先頭の YAML front matter を dict として読む（staged 内容の判定用）"""
  lines = text.splitlines()
  if not lines or lines[0].strip() != "---":
    return None
  for index in range(1, len(lines)):
    if lines[index].strip() == "---":
      try:
        data = yaml.safe_load("\n".join(lines[1:index]))
      except yaml.YAMLError:
        return None
      return data if isinstance(data, dict) else None
  return None


def _is_session_record_path(path):
  """会話ログの2層記録（層1＝evidence/sessions、層2＝docs/sessions）かを返す"""
  return path.endswith(".md") and (
    path.startswith(".reviewcompass/evidence/sessions/")
    or path.startswith("docs/sessions/")
  )


def _session_record_source_changed(record_text, cwd):
  """セッション記録の元ログが生成時から変化していれば True（＝まだ進行中）。

  判定は frontmatter の source_sha256（生成時の元ログのハッシュ）と、いまの元ログの
  ハッシュの一致で行う。判定不能（frontmatter 無し・source 欄欠落・元ログ無し）は
  False を返し、過剰遮断しない。
  """
  fm = _front_matter_from_text(record_text)
  if not isinstance(fm, dict):
    return False
  source_path = fm.get("source_path")
  stored = fm.get("source_sha256")
  if not source_path or not stored:
    return False
  expanded = Path(str(source_path)).expanduser()
  if not expanded.is_absolute():
    expanded = Path(cwd) / expanded
  if not expanded.exists():
    return False
  try:
    current = hashlib.sha256(expanded.read_bytes()).hexdigest()
  except OSError:
    return False
  return current != stored


def validate_no_in_progress_session_records(cwd, staged_files):
  """進行中セッション（元ログが生成時から変化）の記録が staged にあれば弾く。

  会話ログの記録は終了済みセッションについてだけコミットする。手作業の除外に頼ると
  守り忘れの温床になるため、コミット前検査で機械的に止める歯止め。
  """
  offenders = []
  for path in staged_files:
    if not _is_session_record_path(path):
      continue
    text = commit_file_text(cwd, "", path)
    if text is None:
      continue
    if _session_record_source_changed(text, cwd):
      offenders.append(path)
  errors = []
  if offenders:
    errors.append(
      "進行中セッションの記録はコミットできません"
      "（元の会話ログが生成時から変化＝まだ進行中。終了後に取り込み直すと churn）: "
      + ", ".join(offenders)
    )
  return {"in_progress_records": offenders}, errors


def _porcelain_path(line):
  """git status --porcelain の 1 行からパスを取り出す（リネームは新側）"""
  body = line[3:] if len(line) > 3 else ""
  if " -> " in body:
    body = body.split(" -> ", 1)[1]
  return body.strip().strip('"')


def _status_line_is_in_progress_record(line, cwd):
  """porcelain の 1 行が、進行中セッションの記録（コミット対象外）かを返す。

  進行中の記録は「コミットしない」のが正なので、push 前検査の作業ツリー clean 判定
  でも汚れに数えない。終了済みの記録や通常ファイルは数える（False を返す）。
  """
  path = _porcelain_path(line)
  if not _is_session_record_path(path):
    return False
  target = Path(cwd) / path
  try:
    text = target.read_text(encoding="utf-8")
  except OSError:
    return False
  return _session_record_source_changed(text, cwd)


def _unique_preserving_order(items):
  seen = set()
  result = []
  for item in items:
    if item in seen:
      continue
    seen.add(item)
    result.append(item)
  return result


def cmd_stage(args):
  """git add の前段で、進行中セッション記録だけを機械的に除外する。"""
  cwd = Path.cwd()
  pathspecs = args.paths or ["."]
  status = subprocess.run(
    ["git", "status", "--porcelain", "-uall", "--"] + list(pathspecs),
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if status.returncode != 0:
    payload = {
      "status": "error",
      "staged": [],
      "excluded_in_progress_records": [],
      "error": status.stderr.strip(),
    }
    if args.json:
      print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
      print(f"[VERDICT] DEVIATION（exit 2）\n[REASON]\n  - {payload['error']}")
    return 2

  staged = []
  excluded = []
  for line in status.stdout.splitlines():
    if not line.strip():
      continue
    path = _porcelain_path(line)
    if not path:
      continue
    if _status_line_is_in_progress_record(line, cwd):
      excluded.append(path)
    else:
      staged.append(path)
  staged = _unique_preserving_order(staged)
  excluded = _unique_preserving_order(excluded)

  if staged:
    add_result = subprocess.run(
      ["git", "add", "--"] + staged,
      cwd=str(cwd),
      capture_output=True,
      text=True,
    )
    if add_result.returncode != 0:
      payload = {
        "status": "error",
        "staged": staged,
        "excluded_in_progress_records": excluded,
        "error": add_result.stderr.strip(),
      }
      if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
      else:
        print(f"[VERDICT] DEVIATION（exit 2）\n[REASON]\n  - {payload['error']}")
      return 2

  payload = {
    "status": "staged",
    "staged": staged,
    "excluded_in_progress_records": excluded,
  }
  if args.json:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
  else:
    print("[VERDICT] OK（exit 0）")
    if staged:
      print("[STAGED]\n  - " + "\n  - ".join(staged))
    if excluded:
      print("[EXCLUDED IN-PROGRESS SESSION RECORDS]\n  - " + "\n  - ".join(excluded))
  return 0


def validate_deployment_independence_for_commit(cwd, commitish):
  """D-023 配置非依存 lint を commit 内容に対して実行する"""
  try:
    changed_files = list_commit_changed_files(cwd, commitish)
  except ValueError as e:
    return {
      "commit": commitish,
      "target_files": [],
      "findings": [],
    }, [f"配置非依存 lint 対象 commit を読めません: {e}"]

  target_files = [
    filepath for filepath in changed_files
    if is_deployment_independence_guard_target(filepath)
  ]
  state = {
    "commit": commitish,
    "target_files": target_files,
    "findings": [],
  }
  errors = []
  for filepath in target_files:
    text = commit_file_text(cwd, commitish, filepath)
    if text is None:
      errors.append(f"配置非依存 lint 対象の commit 内容を読めません: {filepath}")
      continue
    findings = lint_text(filepath, text)
    state["findings"].extend(findings)

  for finding in state["findings"]:
    errors.append(
      "配置非依存 lint 違反: {path}:{line}: {kind}: {value}".format(
        path=finding["path"],
        line=finding["line"],
        kind=finding["kind"],
        value=finding["value"],
      )
    )
  return state, errors


def _reopen_completed_files(staged_files):
  """staged された reopen 完了ファイルを返す"""
  return [
    path for path in staged_files
    if (
      path.startswith("stages/completed/reopen-procedure-")
      and path.endswith((".yaml", ".yml"))
    )
  ]


def _reopen_procedure_files(staged_files):
  """staged された reopen 手続きファイルを返す"""
  prefixes = (
    "stages/in-progress/reopen-procedure-",
    "stages/completed/reopen-procedure-",
  )
  return [
    path for path in staged_files
    if path.endswith((".yaml", ".yml")) and path.startswith(prefixes)
  ]


def _maintenance_completed_files(staged_files):
  """staged された maintenance 完了ファイルを返す"""
  return [
    path for path in staged_files
    if (
      path.startswith("stages/completed/maintenance-")
      and path.endswith((".yaml", ".yml"))
    )
  ]


def _staged_spec_files(staged_files):
  """staged された feature spec.json を返す"""
  return [
    path for path in staged_files
    if (
      path.startswith(".reviewcompass/specs/")
      and path.endswith("/spec.json")
    )
  ]


def _staged_canonical_spec_phases(staged_files):
  """staged された feature 正本文書の phase 集合を返す"""
  phases = set()
  for path in staged_files:
    parts = path.split("/")
    if len(parts) != 4:
      continue
    if parts[0] != ".reviewcompass" or parts[1] != "specs":
      continue
    filename = parts[3]
    if not filename.endswith(".md"):
      continue
    phase = filename[:-3]
    if phase in ("requirements", "design", "tasks", "implementation"):
      phases.add(phase)
  return phases


def _stage_gate(phase, stage):
  """phase/stage から gate 参照を作る"""
  return f"stages/{phase}.yaml#{stage}"


def _parse_stage_gate(gate):
  """gate 参照から phase/stage を取り出す"""
  if not isinstance(gate, str):
    return None, None
  if not gate.startswith("stages/") or ".yaml#" not in gate:
    return None, None
  path, stage = gate.split("#", 1)
  phase = path[len("stages/"):-len(".yaml")]
  if phase not in PHASE_STAGES or stage not in PHASE_STAGES[phase]:
    return None, None
  return phase, stage


def _full_reopen_gates_for_changed_phase(phase):
  """正本変更済み phase が完了までに必要とする reopen gate を返す"""
  return [
    _stage_gate(phase, stage)
    for stage in ("triad-review", "review-wave", "alignment", "approval")
    if stage in PHASE_STAGES.get(phase, [])
  ]


def _staged_json(cwd, filepath):
  """staged blob を JSON として読む"""
  text = _staged_text(cwd, filepath)
  if text is None:
    return None, f"{filepath} の staged 内容を読めません"
  try:
    data = json.loads(text)
  except json.JSONDecodeError as e:
    return None, f"{filepath} を JSON として読めません: {e}"
  if not isinstance(data, dict):
    return None, f"{filepath} は JSON object が必要です"
  return data, None


def _spec_has_reopen_marker(spec_data):
  """spec.json に reopen/recheck 進行を示す印があるか判定する"""
  recheck = spec_data.get("recheck")
  if isinstance(recheck, dict):
    if recheck.get("upstream_change_pending") is True:
      return True
    impacted = recheck.get("impacted_downstream_phases")
    if isinstance(impacted, list) and impacted:
      return True
  return False


def validate_reopen_spec_changes_have_procedure(cwd, staged_files):
  """reopen 印付き spec.json commit に reopen 手続きファイルがあるか検査する"""
  if _reopen_procedure_files(staged_files):
    return []

  errors = []
  for filepath in _staged_spec_files(staged_files):
    data, error = _staged_json(cwd, filepath)
    if error:
      errors.append(error)
      continue
    if _spec_has_reopen_marker(data):
      errors.append(
        f"{filepath} は reopen/recheck 印を含むため、"
        "対応する reopen 手続きファイルを同じ commit に含めてください"
      )
  return errors


def _impact_decision_gate_set(data):
  """downstream_impact_decisions から gate 集合を作る"""
  decisions = data.get("downstream_impact_decisions")
  if not isinstance(decisions, list):
    return None, ["downstream_impact_decisions は list が必要です"]

  errors = []
  gates = set()
  allowed_decisions = {
    "affected_update_required",
    "existing_sufficient",
    "no_impact",
    "approved",
    "proxy_approved",
  }
  for index, item in enumerate(decisions):
    prefix = f"downstream_impact_decisions[{index}]"
    if not isinstance(item, dict):
      errors.append(f"{prefix} は object が必要です")
      continue
    gate = item.get("gate")
    if not isinstance(gate, str) or not gate.strip():
      errors.append(f"{prefix}.gate が必要です")
    else:
      gates.add(gate)
    feature_scope = item.get("feature_scope")
    feature_scope_is_string = isinstance(feature_scope, str) and feature_scope.strip()
    feature_scope_is_list = (
      isinstance(feature_scope, list)
      and bool(feature_scope)
      and all(isinstance(v, str) and v.strip() for v in feature_scope)
    )
    if not feature_scope_is_string and not feature_scope_is_list:
      errors.append(f"{prefix}.feature_scope は文字列または空でない文字列 list が必要です")
    decision = item.get("decision")
    if decision not in allowed_decisions:
      errors.append(
        f"{prefix}.decision は {', '.join(sorted(allowed_decisions))} のいずれかが必要です"
      )
    rationale = item.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
      errors.append(f"{prefix}.rationale が必要です")
    evidence = item.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(v, str) and v for v in evidence):
      errors.append(f"{prefix}.evidence は空でない文字列 list が必要です")
  return gates, errors


def _impact_decision_phase_set(decision_gates):
  """判定済み gate から phase 集合を作る"""
  phases = set()
  for gate in decision_gates:
    if not isinstance(gate, str):
      continue
    if not gate.startswith("stages/") or ".yaml#" not in gate:
      continue
    phase = gate[len("stages/"):].split(".yaml#", 1)[0]
    if phase in PHASE_STAGES:
      phases.add(phase)
  return phases


def _validate_evidence_list(value, label):
  """証跡 list の形式を検査する"""
  if not isinstance(value, list) or not value or not all(isinstance(v, str) and v for v in value):
    return [f"{label} は空でない文字列 list が必要です"]
  return []


def _validate_feature_impact_decisions(data):
  """上流変更に対する feature impact 判定を検査する"""
  errors = []
  decisions = data.get("feature_impact_decisions")
  if not isinstance(decisions, list) or not decisions:
    errors.append("feature_impact_decisions は空でない list が必要です")
    decisions = []

  allowed_feature_decisions = {
    "reopen_existing_feature",
    "no_reopen_existing_feature",
    "indirect_check_only",
    "new_feature_required",
  }
  allowed_impact_bases = {
    "implementation_ownership",
    "contract_ownership",
    "consumer_or_derivative_only",
    "no_implementation_impact",
    "new_feature_boundary",
  }
  covered_features = set()
  for index, item in enumerate(decisions):
    prefix = f"feature_impact_decisions[{index}]"
    if not isinstance(item, dict):
      errors.append(f"{prefix} は object が必要です")
      continue
    feature = item.get("feature")
    if (
      not isinstance(feature, str)
      or not feature.strip()
      or (feature not in FEATURE_ORDER and feature != "new_feature")
    ):
      errors.append(f"{prefix}.feature は既存 feature 名または new_feature が必要です")
    elif feature in FEATURE_ORDER:
      covered_features.add(feature)
    decision = item.get("decision")
    if decision not in allowed_feature_decisions:
      errors.append(
        f"{prefix}.decision は {', '.join(sorted(allowed_feature_decisions))} のいずれかが必要です"
      )
    impact_basis = item.get("impact_basis")
    if impact_basis not in allowed_impact_bases:
      errors.append(
        f"{prefix}.impact_basis は {', '.join(sorted(allowed_impact_bases))} のいずれかが必要です"
      )
    rationale = item.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
      errors.append(f"{prefix}.rationale が必要です")
    errors.extend(_validate_evidence_list(item.get("evidence"), f"{prefix}.evidence"))

  missing_features = [feature for feature in FEATURE_ORDER if feature not in covered_features]
  if missing_features:
    errors.append(
      "feature_impact_decisions に既存 feature の判定が不足しています: "
      + ", ".join(missing_features)
    )

  new_feature_decision = data.get("new_feature_decision")
  if not isinstance(new_feature_decision, dict):
    errors.append("new_feature_decision は object が必要です")
    return errors

  allowed_new_feature_decisions = {
    "no_new_feature",
    "new_feature_required",
  }
  decision = new_feature_decision.get("decision")
  if decision not in allowed_new_feature_decisions:
    errors.append(
      "new_feature_decision.decision は "
      + ", ".join(sorted(allowed_new_feature_decisions))
      + " のいずれかが必要です"
    )
  rationale = new_feature_decision.get("rationale")
  if not isinstance(rationale, str) or not rationale.strip():
    errors.append("new_feature_decision.rationale が必要です")
  errors.extend(
    _validate_evidence_list(
      new_feature_decision.get("evidence"),
      "new_feature_decision.evidence",
    )
  )
  return errors


def _validate_reopen_gate_list(data, field_name, filepath):
  """reopen gate list の形式を検査する"""
  value = data.get(field_name, [])
  if value is None:
    value = []
  if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
    return [], [f"{filepath}.{field_name} は文字列 list が必要です"]
  return value, []


def validate_reopen_completion_impact_decisions(cwd, staged_files):
  """reopen 完了時に下流影響判定表があるか検査する"""
  errors = []
  for filepath in _reopen_completed_files(staged_files):
    text = _staged_text(cwd, filepath)
    if text is None:
      errors.append(f"{filepath} の staged 内容を読めません")
      continue
    try:
      data = yaml.safe_load(text)
    except yaml.YAMLError as e:
      errors.append(f"{filepath} を YAML として読めません: {e}")
      continue
    if not isinstance(data, dict):
      errors.append(f"{filepath} は YAML object が必要です")
      continue

    for error in _validate_feature_impact_decisions(data):
      errors.append(f"{filepath}: {error}")

    pending_gates, gate_errors = _validate_reopen_gate_list(
      data,
      "pending_gates",
      filepath,
    )
    completed_gates, completed_gate_errors = _validate_reopen_gate_list(
      data,
      "completed_gates",
      filepath,
    )
    required_gate_trace, required_gate_errors = _validate_reopen_gate_list(
      data,
      "required_gates",
      filepath,
    )
    errors.extend(gate_errors)
    errors.extend(completed_gate_errors)
    errors.extend(required_gate_errors)
    if gate_errors or completed_gate_errors or required_gate_errors:
      continue
    gate_trace = set(pending_gates) | set(completed_gates) | set(required_gate_trace)

    changed_phases = _staged_canonical_spec_phases(staged_files)
    required_gates = []
    for phase in sorted(changed_phases, key=PHASE_ORDER.index):
      required_gates.extend(_full_reopen_gates_for_changed_phase(phase))
    missing_required_gates = [
      gate for gate in required_gates
      if gate not in gate_trace
    ]
    if missing_required_gates:
      errors.append(
        f"{filepath}.pending_gates/completed_gates/required_gates は正本変更済み phase の review gate を含む必要があります: "
        + ", ".join(missing_required_gates)
      )

    impacted_phases = data.get("impacted_downstream_phases")
    if (
      not isinstance(impacted_phases, list)
      or not all(isinstance(v, str) and v in PHASE_STAGES for v in impacted_phases)
    ):
      errors.append(
        f"{filepath}.impacted_downstream_phases は既知フェーズ名の list が必要です"
      )
      impacted_phases = []

    decision_gates, decision_errors = _impact_decision_gate_set(data)
    for error in decision_errors:
      errors.append(f"{filepath}: {error}")
    if decision_gates is None:
      continue

    decision_required_gates = sorted(gate_trace)
    missing = [gate for gate in decision_required_gates if gate not in decision_gates]
    if missing:
      errors.append(
        f"{filepath}.downstream_impact_decisions に pending_gates/completed_gates/required_gates の判定が不足しています: "
        + ", ".join(missing)
      )

    decision_phases = _impact_decision_phase_set(decision_gates)
    uncovered_phases = [
      phase for phase in impacted_phases
      if phase not in decision_phases
    ]
    if uncovered_phases:
      errors.append(
        f"{filepath}.impacted_downstream_phases に対応する gate 判定が不足しています: "
        + ", ".join(uncovered_phases)
      )
  return errors


def git_head_commit(cwd):
  """現在の HEAD commit を返す"""
  result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  return result.stdout.strip()


def validate_last_commit_precheck(cwd, ahead_info):
  """push 前に HEAD の commit 事前検査通過記録を確認する"""
  state = {
    "path": DEFAULT_LAST_COMMIT_PRECHECK_PATH,
    "required": False,
    "exists": False,
    "valid": False,
    "head_commit": git_head_commit(cwd),
    "recorded_head_commit": None,
  }
  if not str(ahead_info).isdigit() or int(ahead_info) <= 0:
    state["valid"] = True
    return state, []

  state["required"] = True
  precheck_path = Path(cwd) / DEFAULT_LAST_COMMIT_PRECHECK_PATH
  state["exists"] = precheck_path.exists()
  if not precheck_path.exists():
    return state, [
      f"push 対象 HEAD の commit 事前検査記録がありません"
      f"（{DEFAULT_LAST_COMMIT_PRECHECK_PATH}）"
    ]

  try:
    record = json.loads(precheck_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return state, [f"commit 事前検査記録を読めません: {e}"]

  if not isinstance(record, dict):
    return state, ["commit 事前検査記録の形式が不正です（object ではありません）"]

  recorded_head = record.get("head_commit")
  state["recorded_head_commit"] = recorded_head
  if record.get("precheck_exit_code") not in (0, 1):
    return state, ["commit 事前検査記録が通過状態ではありません"]
  if recorded_head != state["head_commit"]:
    return state, ["commit 事前検査記録の head_commit が現在の HEAD と一致しません"]

  state["valid"] = True
  return state, []


def cmd_commit(args):
  """commit サブコマンドのエントリポイント（仕様 §6.2）"""
  cwd = Path.cwd()
  rationale = args.rationale

  # git リポジトリ内かの確認
  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  # 未消化所見の確認
  carry_forward_register_path = cwd / DEFAULT_CARRY_FORWARD_REGISTER_PATH
  unresolved_count = count_unresolved_carry_forward_items(carry_forward_register_path)
  in_progress_files = list_in_progress_files(cwd)

  # staged ファイルの取得と分類
  result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "-z"],
    cwd=str(cwd),
    capture_output=True,
    text=False,
  )
  if result.returncode != 0:
    print(f"error: git diff 失敗: {result.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
    return 2

  staged_files = [f.decode("utf-8") for f in result.stdout.split(b"\0") if f]
  dangerous = [f for f in staged_files if classify_staged_file(f) == "dangerous"]
  caution = [f for f in staged_files if classify_staged_file(f) == "caution"]
  normal = [f for f in staged_files if classify_staged_file(f) == "normal"]
  approval_state, approval_errors = validate_commit_approval(cwd, staged_files)
  execution_delegation_errors = validate_commit_execution_delegation(
    cwd,
    approval_state,
    args.execution_actor,
  )
  reopen_spec_errors = validate_reopen_spec_changes_have_procedure(
    cwd,
    staged_files,
  )
  reopen_completion_errors = validate_reopen_completion_impact_decisions(
    cwd,
    staged_files,
  )
  staged_content_hashes = {
    filepath: staged_file_content_hash(cwd, filepath)
    for filepath in staged_files
  }
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    staged_files,
    actual_hashes=staged_content_hashes,
  )
  deployment_lint_state, deployment_lint_errors = (
    validate_deployment_independence_for_staged_files(cwd, staged_files)
  )
  document_link_lint_state, document_link_lint_errors = (
    validate_document_links_for_staged_files(cwd, staged_files)
  )
  in_progress_record_state, in_progress_record_errors = (
    validate_no_in_progress_session_records(cwd, staged_files)
  )

  # decision-source-lint 統合（Req 11 受入 7）
  from check_workflow_action.decision_source_lint import run_decision_source_lint_all
  dsl_result = run_decision_source_lint_all(cwd)

  # 判定（仕様 §6.2）
  reasons = []
  deviation_reasons = []
  if approval_errors:
    deviation_reasons.extend(approval_errors)
  if execution_delegation_errors:
    deviation_reasons.extend(execution_delegation_errors)
  if reopen_spec_errors:
    deviation_reasons.extend(reopen_spec_errors)
  if reopen_completion_errors:
    deviation_reasons.extend(reopen_completion_errors)
  if (
    in_progress_files
    and not is_reopen_stop_point_commit_allowed(cwd, in_progress_files, staged_files)
    and not is_completed_maintenance_commit_allowed(cwd, in_progress_files, staged_files)
  ):
    deviation_reasons.append(
      "stages/in-progress に進行中ファイルがあります: "
      + ", ".join(in_progress_files)
    )
  if dangerous:
    for f in dangerous:
      deviation_reasons.append(f"危険変更: {f}（commit を遮断推奨）")
  if post_write_errors:
    deviation_reasons.extend(post_write_errors)
  if deployment_lint_errors:
    deviation_reasons.extend(deployment_lint_errors)
  if document_link_lint_errors:
    deviation_reasons.extend(document_link_lint_errors)
  if in_progress_record_errors:
    deviation_reasons.extend(in_progress_record_errors)

  # decision-source-lint の DEVIATION 判定を統合
  if dsl_result.exit_code == 2:
    deviation_reasons.extend(
      [f"decision-source-lint: {m}" for m in dsl_result.messages]
    )

  if deviation_reasons:
    reasons.extend(deviation_reasons)
    verdict, exit_code = "DEVIATION", 2
  elif unresolved_count > 0 or caution or dsl_result.exit_code == 1:
    if unresolved_count > 0:
      reasons.append(
        f"未消化所見が {unresolved_count} 件あります"
        f"（{DEFAULT_CARRY_FORWARD_REGISTER_PATH}）"
      )
    for f in caution:
      reasons.append(f"要注意変更: {f}（変更根拠を確認してください）")
    if dsl_result.exit_code == 1:
      reasons.extend(
        [f"decision-source-lint: {m}" for m in dsl_result.messages]
      )
    verdict, exit_code = "WARN", 1
  else:
    verdict, exit_code = "OK", 0

  # 出力の組み立て
  current_state_text = (
    f"未消化所見: {unresolved_count} 件\n"
    f"staged ファイル数: {len(staged_files)} 件\n"
    f"  危険変更: {len(dangerous)} 件\n"
    f"  要注意変更: {len(caution)} 件\n"
    f"  通常変更: {len(normal)} 件\n"
    f"進行中ファイル: {len(in_progress_files)} 件\n"
    f"ユーザ承認レコード: {'有効' if approval_state['valid'] else '無効'}\n"
    f"commit 実行主体: {args.execution_actor}\n"
    f"post-write-verification 対象: {len(post_write_state['target_files'])} 件\n"
    f"post-write-verification 状態: {post_write_state['manifest_status']}\n"
    f"配置非依存 lint 対象: {len(deployment_lint_state['target_files'])} 件\n"
    f"配置非依存 lint 所見: {len(deployment_lint_state['findings'])} 件\n"
    f"文書リンク lint 対象: {len(document_link_lint_state['target_files'])} 件\n"
    f"文書リンク lint 所見: {len(document_link_lint_state['findings'])} 件\n"
    f"進行中セッション記録: {len(in_progress_record_state['in_progress_records'])} 件\n"
    f"decision-source-lint 判定: {dsl_result.verdict}（{len(dsl_result.messages)} 件）"
  )
  current_state_dict = {
    "pending_unresolved_count": unresolved_count,
    "staged_files": {
      "dangerous": dangerous,
      "caution": caution,
      "normal": normal,
    },
    "in_progress_files": in_progress_files,
    "commit_approval": approval_state,
    "execution_actor": args.execution_actor,
    "post_write_verification": post_write_state,
    "deployment_independence_lint": deployment_lint_state,
    "document_link_lint": document_link_lint_state,
    "in_progress_session_records": in_progress_record_state,
  }
  action_str = f"commit (rationale='{rationale}')"
  action_dict = {
    "subcommand": "commit",
    "args": {
      "rationale": rationale,
      "execution_actor": args.execution_actor,
    },
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def _git_cached_files(cwd):
  """staged ファイル一覧を返す。取得失敗時は None を返す。"""
  result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "-z"],
    cwd=str(cwd),
    capture_output=True,
    text=False,
  )
  if result.returncode != 0:
    return None
  return [f.decode("utf-8") for f in result.stdout.split(b"\0") if f]


def _completed_maintenance_files_cover_in_progress(
  cwd,
  in_progress_files,
  completed_files,
  read_text,
):
  """maintenance 完了ファイル群が現在の in-progress reopen を覆うか判定する。"""
  if not in_progress_files:
    return False
  if not completed_files:
    return False

  covered_in_progress = set()
  for filepath in completed_files:
    text = read_text(filepath)
    if text is None:
      return False
    try:
      data = yaml.safe_load(text)
    except yaml.YAMLError:
      return False
    if not isinstance(data, dict):
      return False
    if data.get("process_id") != "maintenance":
      return False
    mainline_blocked_by = data.get("mainline_blocked_by")
    if isinstance(mainline_blocked_by, str):
      covered_in_progress.add(mainline_blocked_by)

  for relative_path in in_progress_files:
    if relative_path not in covered_in_progress:
      return False
    data = load_in_progress_file(cwd, relative_path)
    if data.get("process_id") != "reopen-procedure":
      return False
  return True


def _completed_maintenance_commit_candidate(cwd, in_progress_files, paths):
  """stage 前の path 群から maintenance 完了 commit 候補かを判定する。"""
  completed_files = _maintenance_completed_files(paths)

  def read_worktree_text(filepath):
    try:
      return (Path(cwd) / filepath).read_text(encoding="utf-8")
    except OSError:
      return None

  return _completed_maintenance_files_cover_in_progress(
    cwd,
    in_progress_files,
    completed_files,
    read_worktree_text,
  )


def _commit_preflight_next_action(cwd, in_progress_files):
  """commit 指示入口で見る現在の workflow action を副作用なしに組み立てる。"""
  if in_progress_files:
    return build_in_progress_next_action(cwd, in_progress_files[0])

  verification_targets = list_post_write_verification_targets(cwd)
  if verification_targets:
    manifest_state, manifest = evaluate_post_write_manifest_state(
      cwd,
      verification_targets,
    )
    if manifest_state != "completed":
      return {
        "kind": "post_write_verification",
        "required_action": "run_post_write_verification",
        "target_files": verification_targets,
        "manifest_status": manifest_state,
        "manifest": manifest.get("_path") if isinstance(manifest, dict) else None,
        "reason": "post-write-verification 対象の未完了変更があります",
      }

  specs, missing = load_all_feature_specs(cwd)
  if missing:
    return {
      "kind": "unknown",
      "required_action": "repair_workflow_state",
      "reason": "必要な spec.json が不足しています",
      "missing_features": missing,
    }

  commit_stop_point = resolve_normal_workflow_commit_stop_point_action(cwd, specs)
  if commit_stop_point:
    return commit_stop_point

  return {
    "kind": "commit_candidate",
    "required_action": "prepare_commit",
    "reason": "commit 指示入口で遮断すべき active workflow unit はありません",
  }


def build_commit_instruction_preflight(cwd):
  """利用者の commit 指示直後に使う read-only preflight を返す。"""
  cwd = Path(cwd)
  action = {
    "subcommand": "commit-preflight",
    "args": {},
  }
  if not (cwd / ".git").exists():
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "action": action,
      "reasons": ["git リポジトリではありません"],
      "current_state": {},
      "allowed_to_stage": False,
      "allowed_to_prepare_approval": False,
      "allowed_to_delegate_execution": False,
      "allowed_to_run_guarded_commit": False,
      "next_required_action": None,
    }

  in_progress_files = list_in_progress_files(cwd)
  changed_files = list_changed_files(cwd)
  staged_files = _git_cached_files(cwd)
  if staged_files is None:
    return {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "action": action,
      "reasons": ["staged ファイル一覧を取得できません"],
      "current_state": {"in_progress_files": in_progress_files},
      "allowed_to_stage": False,
      "allowed_to_prepare_approval": False,
      "allowed_to_delegate_execution": False,
      "allowed_to_run_guarded_commit": False,
      "next_required_action": None,
    }

  next_action = _commit_preflight_next_action(cwd, in_progress_files)
  next_required_action = next_action.get("required_action")
  reasons = []
  verdict = "OK"
  allowed_to_stage = True
  allowed_to_prepare_approval = True
  allowed_to_delegate_execution = True

  if in_progress_files:
    if next_required_action == "commit_stop_point":
      pass
    elif _completed_maintenance_commit_candidate(cwd, in_progress_files, changed_files):
      next_required_action = "prepare_completed_maintenance_commit"
    else:
      verdict = "DEVIATION"
      allowed_to_stage = False
      allowed_to_prepare_approval = False
      allowed_to_delegate_execution = False
      reasons.append(
        "stages/in-progress に進行中ファイルがありますが、現在位置は commit stop point ではありません: "
        + ", ".join(in_progress_files)
      )

  if next_action.get("kind") in (
    "post_write_verification",
    "post_write_policy_violation",
    "post_write_human_decision_required",
  ):
    verdict = "DEVIATION"
    allowed_to_stage = False
    allowed_to_prepare_approval = False
    allowed_to_delegate_execution = False
    reasons.append("commit より前に post-write verification を完了してください")

  approval_state, approval_errors = validate_commit_approval(cwd, staged_files)
  execution_delegation_errors = validate_commit_execution_delegation(
    cwd,
    approval_state,
    "llm",
  )
  allowed_to_run_guarded_commit = (
    verdict != "DEVIATION"
    and bool(staged_files)
    and approval_state.get("valid") is True
    and not execution_delegation_errors
  )

  current_state = {
    "changed_files": changed_files,
    "staged_files": staged_files,
    "in_progress_files": in_progress_files,
    "next_action": next_action,
    "commit_approval": approval_state,
    "approval_errors": approval_errors,
    "execution_delegation_errors": execution_delegation_errors,
  }

  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "action": action,
    "reasons": reasons,
    "current_state": current_state,
    "allowed_to_stage": allowed_to_stage,
    "allowed_to_prepare_approval": allowed_to_prepare_approval,
    "allowed_to_delegate_execution": allowed_to_delegate_execution,
    "allowed_to_run_guarded_commit": allowed_to_run_guarded_commit,
    "next_required_action": next_required_action,
  }


def cmd_commit_preflight(args):
  """commit 指示直後に stage / approval 作成可否を read-only 判定する。"""
  response = build_commit_instruction_preflight(Path.cwd())
  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {response['verdict']}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    print(f"[NEXT] {response.get('next_required_action')}")
  return response["exit_code"]


def cmd_push(args):
  """push サブコマンドのエントリポイント（仕様 §6.3）"""
  cwd = Path.cwd()
  rationale = args.rationale

  # git リポジトリ内かの確認
  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  # 作業ツリーの clean 性
  in_progress_files = list_in_progress_files(cwd)
  status_result = subprocess.run(
    # 未追跡はファイル単位で列挙する（-uall）。新規ディレクトリだとディレクトリ単位で
    # まとまり、進行中セッション記録の個別判定ができなくなるのを防ぐ。
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if status_result.returncode != 0:
    print(f"error: git status 失敗: {status_result.stderr}", file=sys.stderr)
    return 2

  # 進行中セッションの記録（コミット対象外）は作業ツリーの汚れに数えない。
  # 「進行中はコミットしない」（コミット側の歯止め）と push 前の clean 要求の矛盾を解く。
  dirty_lines = [
    line for line in status_result.stdout.splitlines()
    if line.strip() and not _status_line_is_in_progress_record(line, cwd)
  ]
  is_dirty = bool(dirty_lines)

  # 直近 5 コミット
  log_result = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  recent_commits = log_result.stdout.strip() if log_result.returncode == 0 else "(取得失敗)"

  # ローカル先行コミット数（origin/main がない場合は情報なし）
  ahead_result = subprocess.run(
    ["git", "rev-list", "--count", "origin/main..HEAD"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  ahead_info = (
    ahead_result.stdout.strip()
    if ahead_result.returncode == 0
    else "(リモート origin/main が未設定または取得失敗)"
  )
  commit_precheck_state, commit_precheck_errors = validate_last_commit_precheck(
    cwd,
    ahead_info,
  )
  deployment_lint_state, deployment_lint_errors = validate_deployment_independence_for_commit(
    cwd,
    "HEAD",
  )

  # 判定（仕様 §6.3）
  reasons = []
  if is_dirty:
    reasons.append("作業ツリーに未コミット変更があります（push 前に commit が必要）")
  if commit_precheck_errors:
    reasons.extend(commit_precheck_errors)
  if deployment_lint_errors:
    reasons.extend(deployment_lint_errors)
  if reasons:
    verdict, exit_code = "DEVIATION", 2
  else:
    verdict, exit_code = "OK", 0

  # 出力の組み立て
  current_state_text = (
    f"作業ツリー: {'dirty' if is_dirty else 'clean'}\n"
    f"進行中ファイル: {len(in_progress_files)} 件\n"
    f"origin/main からの先行コミット数: {ahead_info}\n"
    f"commit 事前検査記録: {'有効' if commit_precheck_state['valid'] else '無効'}\n"
    f"配置非依存 lint 対象: {len(deployment_lint_state['target_files'])} 件\n"
    f"配置非依存 lint 所見: {len(deployment_lint_state['findings'])} 件\n"
    f"直近 5 コミット:\n{recent_commits}"
  )
  current_state_dict = {
    "is_dirty": is_dirty,
    "in_progress_files": in_progress_files,
    "ahead_count": ahead_info,
    "commit_precheck": commit_precheck_state,
    "deployment_independence_lint": deployment_lint_state,
    "recent_commits": recent_commits.splitlines() if recent_commits else [],
  }
  action_str = f"push (rationale='{rationale}')"
  action_dict = {
    "subcommand": "push",
    "args": {"rationale": rationale},
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def list_commit_changed_files(cwd, commitish):
  """指定 commit の変更ファイル一覧を返す"""
  result = subprocess.run(
    ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commitish],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise ValueError(result.stderr.strip() or f"commit を読めません: {commitish}")
  return sorted(set(f for f in result.stdout.splitlines() if f))


def commit_file_sha256(cwd, commitish, path):
  """指定 commit 内のファイル内容 sha256 を返す"""
  result = subprocess.run(
    ["git", "show", f"{commitish}:{path}"],
    cwd=str(cwd),
    capture_output=True,
  )
  if result.returncode != 0:
    return None
  return hashlib.sha256(result.stdout).hexdigest()


def cmd_audit_commit(args):
  """audit-commit サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  commitish = args.commitish

  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  try:
    changed_files = list_commit_changed_files(cwd, commitish)
  except ValueError as e:
    print(f"error: {e}", file=sys.stderr)
    return 2

  post_write_targets = post_write_verification_targets_for_paths(cwd, changed_files)
  commit_hashes = {
    target: commit_file_sha256(cwd, commitish, target)
    for target in post_write_targets
  }
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    post_write_targets,
    commit_hashes,
  )

  if post_write_errors:
    verdict, exit_code = "DEVIATION", 2
    reasons = [
      reason.replace("staged ファイル", "commit 対象ファイル")
      for reason in post_write_errors
    ]
  else:
    verdict, exit_code = "OK", 0
    reasons = []

  current_state_text = (
    f"commit: {commitish}\n"
    f"変更ファイル数: {len(changed_files)} 件\n"
    f"post-write-verification 対象: {len(post_write_targets)} 件\n"
    f"post-write-verification 状態: {post_write_state['manifest_status']}"
  )
  current_state_dict = {
    "commit": commitish,
    "changed_files": changed_files,
    "post_write_targets": post_write_targets,
    "post_write_verification": post_write_state,
  }
  action_str = f"audit-commit {commitish}"
  action_dict = {
    "subcommand": "audit-commit",
    "args": {"commitish": commitish},
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def list_in_progress_files(cwd):
  """stages/in-progress 配下の進行中ファイルを相対パス文字列で返す"""
  in_progress_dir = Path(cwd) / "stages" / "in-progress"
  if not in_progress_dir.exists():
    return []
  files = [p for p in in_progress_dir.iterdir() if p.is_file()]
  return [str(p.relative_to(cwd)) for p in sorted(files)]


def is_reopen_stop_point_commit_allowed(cwd, in_progress_files, staged_files):
  """reopen 手続きの停止点 commit だけは in-progress 同伴を許可する"""
  if not in_progress_files:
    return False
  staged_set = set(staged_files)
  for relative_path in in_progress_files:
    if relative_path not in staged_set:
      return False
    data = load_in_progress_file(cwd, relative_path)
    if data.get("process_id") != "reopen-procedure":
      return False
    if not _is_structured_reopen_commit_stop_point(data):
      return False
  return True


def _int_field(data, name):
  value = data.get(name)
  try:
    return int(value)
  except (TypeError, ValueError):
    return None


def _is_structured_reopen_commit_stop_point(data):
  """人間向け文言ではなく構造フィールドで reopen 停止点を判定する"""
  if data.get("commit_stop_point") is not True:
    return False
  step_number = _int_field(data, "step_number")
  stop_point_step = _int_field(data, "commit_stop_point_step")
  if step_number is None or stop_point_step != step_number:
    return False

  kind = data.get("commit_stop_point_kind")
  if step_number == 2:
    return kind == "canonical_update_complete"

  if step_number == 3:
    gate = data.get("commit_stop_point_gate")
    if not isinstance(gate, str):
      return False
    expected_kind = _commit_stop_point_kind_for_gate(gate)
    if expected_kind is None or kind != expected_kind:
      return False
    return True

  if step_number == 4:
    gate = data.get("commit_stop_point_gate")
    if not isinstance(gate, str):
      return False
    if kind != "approval_complete":
      return False
    expected_kind = _commit_stop_point_kind_for_gate(gate)
    if expected_kind != "approval_complete":
      return False
    phase, _stage = _parse_stage_gate(gate)
    if phase != "implementation":
      return False
    return True

  return False


def _is_structured_reopen_commit_required(data):
  """状態遷移後に残る commit 境界を構造フィールドで判定する"""
  if data.get("commit_required") is not True:
    return False
  if _int_field(data, "step_number") is None:
    return False
  if data.get("commit_required_kind") not in {"stop_point_consumed"}:
    return False
  records = data.get("commit_stop_point_records")
  if not isinstance(records, list) or not records:
    return False
  latest = records[-1]
  if not isinstance(latest, dict):
    return False
  return bool(latest.get("head") and latest.get("kind"))


def _commit_stop_point_kind_for_gate(gate):
  """標準 gate 文字列から構造化 commit stop point kind を返す"""
  phase, stage = _parse_stage_gate(gate)
  if phase is None or stage is None:
    return None
  return {
    "drafting": "drafting_complete",
    "triad-review": "triad_review_complete",
    "review-wave": "review_wave_complete",
    "alignment": "alignment_complete",
    "approval": "approval_complete",
  }.get(stage)


def is_completed_maintenance_commit_allowed(cwd, in_progress_files, staged_files):
  """maintenance 完了 commit だけは本線 in-progress 同伴を許可する"""
  completed_files = _maintenance_completed_files(staged_files)
  return _completed_maintenance_files_cover_in_progress(
    cwd,
    in_progress_files,
    completed_files,
    lambda filepath: _staged_text(cwd, filepath),
  )


def is_reopen_pending_gate_change_allowed(
  cwd,
  in_progress_files,
  phase,
  stage,
  new_value,
):
  """reopen 手続き内の pending gate 変更だけは spec-set 中でも許可する"""
  if len(in_progress_files) != 1:
    return False
  data = load_in_progress_file(cwd, in_progress_files[0])
  if data.get("process_id") != "reopen-procedure":
    return False
  if data.get("current_blocker") is not None:
    return False
  pending_gates = data.get("pending_gates")
  if not isinstance(pending_gates, list):
    return False
  gate = f"stages/{phase}.yaml#{stage}"
  if gate not in pending_gates:
    return False
  step_number = data.get("step_number")
  if step_number in (1, "1"):
    return new_value is False
  if step_number in (3, "3"):
    return new_value is True
  return False


def load_in_progress_file(cwd, relative_path):
  """進行中状態ファイルを YAML として読み込む"""
  path = Path(cwd) / relative_path
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return {}
  return data if isinstance(data, dict) else {}


def resolve_reopen_required_action(next_step, current_blocker, step_number=None):
  """reopen の next_step/current_blocker から要求アクションを返す"""
  if current_blocker:
    return "wait_for_human_decision"
  if step_number in (1, "1"):
    return "classify_and_rollback_flags"
  if step_number in (2, "2"):
    return "repair_canonical_documents"
  if step_number in (3, "3"):
    return "rerun_alignment_approval_chain"
  if step_number in (4, "4"):
    return "finalize_reopen"
  if not next_step:
    return "inspect_reopen_state"
  # 既存の in-progress YAML は next_step の日本語表記を正本として持つ。
  # 将来生成分は step_number を併記し、文字列表記ゆれへの依存を下げる。
  if "第1過程" in next_step:
    return "classify_and_rollback_flags"
  if "第2過程" in next_step:
    return "repair_canonical_documents"
  if "第3過程" in next_step:
    return "rerun_alignment_approval_chain"
  if "第4過程" in next_step:
    return "finalize_reopen"
  if "完了" in next_step:
    return "reopen_completed"
  return "inspect_reopen_state"


def _ordered_known_features(features):
  """既知 feature 順を優先して feature list を返す"""
  feature_set = {
    feature for feature in features
    if isinstance(feature, str) and feature
  }
  ordered = [
    feature for feature in FEATURE_ORDER
    if feature in feature_set
  ]
  extras = sorted(feature_set - set(ordered))
  return ordered + extras


def _as_feature_list(value):
  """YAML 値を feature list に正規化する"""
  if isinstance(value, str):
    return [value]
  if isinstance(value, list):
    return [
      feature for feature in value
      if isinstance(feature, str) and feature
    ]
  return []


def reopen_feature_scope_from_data(data):
  """reopen 手続き YAML から対象 feature scope を機械的に返す"""
  decisions = data.get("feature_impact_decisions")
  if not isinstance(decisions, list) or not decisions:
    features = _as_feature_list(data.get("feature"))
    ordered = _ordered_known_features(features)
    return {
      "required_feature_scope": ordered,
      "direct_features": ordered,
      "indirect_features": [],
      "feature_impact_scope_basis": "feature",
    }

  all_features = []
  direct_features = []
  indirect_features = []
  for decision in decisions:
    if not isinstance(decision, dict):
      continue
    feature = decision.get("feature")
    if not isinstance(feature, str) or not feature:
      continue
    all_features.append(feature)
    decision_value = decision.get("decision")
    if decision_value in ("reopen_existing_feature", "new_feature_required"):
      direct_features.append(feature)
    else:
      indirect_features.append(feature)

  return {
    "required_feature_scope": _ordered_known_features(all_features),
    "direct_features": _ordered_known_features(direct_features),
    "indirect_features": _ordered_known_features(indirect_features),
    "feature_impact_scope_basis": "feature_impact_decisions",
  }


def _reopen_gate_list(data, field_name):
  """reopen 手続きデータの gate list を set で返す"""
  value = data.get(field_name, [])
  if not isinstance(value, list):
    return set()
  return {
    item
    for item in value
    if isinstance(item, str)
  }


def _reopen_drafting_completed(data, phase):
  """指定 phase の reopen drafting 完了記録があるか判定する"""
  drafting_gate = _stage_gate(phase, "drafting")
  completed = set()
  completed.update(_reopen_gate_list(data, "drafting_completed_gates"))
  completed.update(_reopen_gate_list(data, "completed_gates"))
  return drafting_gate in completed


def _resolve_reopen_next_gate(data, pending_gates, current_blocker):
  """reopen の次 gate と、その前に必要な drafting を解決する"""
  if current_blocker or not pending_gates:
    return {
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "required_action": None,
    }

  next_pending_gate = pending_gates[0]
  pending_phase, pending_stage = _parse_stage_gate(next_pending_gate)
  if (
    pending_phase
    and pending_stage == "triad-review"
    and not _reopen_drafting_completed(data, pending_phase)
  ):
    return {
      "next_pending_gate": next_pending_gate,
      "next_drafting_gate": _stage_gate(pending_phase, "drafting"),
      "active_gate": _stage_gate(pending_phase, "drafting"),
      "phase": pending_phase,
      "stage": "drafting",
      "required_action": "run_reopen_drafting",
    }

  return {
    "next_pending_gate": next_pending_gate,
    "next_drafting_gate": None,
    "active_gate": next_pending_gate,
    "phase": pending_phase,
    "stage": pending_stage,
    "required_action": "run_reopen_pending_gate",
  }


def _sha256_digest_for_repo_file(cwd, relative_path):
  """repo-relative ファイルの現在 digest を approval-gate 形式で返す"""
  if not isinstance(relative_path, str) or not relative_path.strip():
    return None
  path = Path(cwd) / relative_path
  digest = file_sha256(path)
  if digest is None:
    return None
  return f"sha256:{digest}"


def _current_staged_file_set_digest(cwd):
  """現在の git index の staged file set digest を approval-gate 形式で返す"""
  try:
    canonical = commit_approval.canonical_target(cwd)
    digest = commit_approval.staged_file_set_digest_from_canonical(canonical)
  except (OSError, RuntimeError, KeyError, TypeError):
    return None
  value = digest.get("digest") if isinstance(digest, dict) else None
  if not isinstance(value, str) or not value:
    return None
  return f"sha256:{value}"


def _approval_branch_effective_contract(operation_contract, gate):
  """active approval gate の branch 条件を反映した有効 contract を返す"""
  phase, stage = _parse_stage_gate(gate)
  if stage != "approval" or not isinstance(operation_contract, dict):
    return operation_contract
  branching = operation_contract.get("branching")
  branches = branching.get("branches") if isinstance(branching, dict) else []
  if not isinstance(branches, list):
    return operation_contract
  approval_branch = None
  for branch in branches:
    if not isinstance(branch, dict):
      continue
    if branch.get("branch_id") == "approval" or branch.get("condition") == "active_gate=approval":
      approval_branch = branch
      break
  if approval_branch is None:
    return operation_contract

  internal_steps = approval_branch.get("internal_steps")
  approval_required = approval_branch.get("approval_aggregation") is True
  if isinstance(internal_steps, list):
    approval_required = approval_required or any(
      isinstance(step, dict) and step.get("approval_required") is True
      for step in internal_steps
    )

  effective = dict(operation_contract)
  effective["effect_kind"] = approval_branch.get(
    "max_effect_kind",
    operation_contract.get("effect_kind"),
  )
  effective["max_effect_kind"] = approval_branch.get(
    "max_effect_kind",
    operation_contract.get("max_effect_kind"),
  )
  effective["approval_required"] = approval_required
  if approval_branch.get("human_only_override_applies") is True:
    effective["actor"] = {"kind": "human", "source": "operation branch human-only override"}
  for step in internal_steps or []:
    if isinstance(step, dict) and step.get("approval_required") is True:
      effective["phase_boundary"] = step.get(
        "phase_boundary",
        effective.get("phase_boundary"),
      )
      break
  return effective


def _approval_gate_record_path(cwd, record_path):
  """approval gate record の repo-relative path を filesystem path に解決する"""
  if not isinstance(record_path, str) or not record_path.strip():
    return None, ["approval_record_path が必要です"]
  relative = Path(record_path)
  if relative.is_absolute() or ".." in relative.parts:
    return None, ["approval_record_path は repo-relative path である必要があります"]
  path = Path(cwd) / relative
  return path, []


def _load_approval_gate_record(cwd, record_path):
  """approval gate record を repo-relative path から読む"""
  path, reasons = _approval_gate_record_path(cwd, record_path)
  if reasons:
    return None, reasons
  try:
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError) as exc:
    return None, [f"approval gate record を読めません: {record_path}: {exc}"]
  if not isinstance(record, dict):
    return None, ["approval gate record は mapping である必要があります"]
  return record, []


def _consume_recorded_approval_gate_record(cwd, current_blocker, gate):
  """gate 完了時に、対応する approval gate record を single-use として消費する"""
  if not isinstance(current_blocker, dict):
    return None, []
  if current_blocker.get("status") != "decision_recorded":
    return None, []
  if current_blocker.get("gate") != gate:
    return None, []

  record_path = current_blocker.get("approval_record_path")
  path, path_reasons = _approval_gate_record_path(cwd, record_path)
  if path_reasons:
    return None, path_reasons
  record, load_reasons = _load_approval_gate_record(cwd, record_path)
  if load_reasons:
    return None, load_reasons
  if record.get("schema_version") != "approval-gate-v1":
    return None, ["approval gate record は schema_version=approval-gate-v1 が必要です"]
  if record.get("decision") != "approved":
    return None, [f"approved 以外の decision は gate 完了に使えません: {record.get('decision')}"]
  if record.get("next_action_expectation") != "proceed":
    return None, [
      "next_action_expectation が proceed ではない approval record は gate 完了に使えません: "
      f"{record.get('next_action_expectation')}"
    ]
  if record.get("consumed") is True:
    return None, ["approval gate record は既に consumed です"]

  record["consumed"] = True
  try:
    path.write_text(
      yaml.safe_dump(record, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
  except OSError as exc:
    return None, [f"approval gate record を consumed に更新できません: {record_path}: {exc}"]
  return record_path, []


def _approval_gate_decision_blocked_by(current_blocker, reasons):
  """approval record 評価失敗を blocked_by に付加する"""
  blocked_by = _reopen_blocked_by_current_blocker(current_blocker)
  blocked_by["approval_record_verdict"] = "DEVIATION"
  blocked_by["approval_record_reasons"] = reasons
  return blocked_by


def _approval_gate_non_approved_blocked_by(current_blocker, record, reasons):
  """非承認 decision の停止理由を blocked_by に付加する"""
  blocked_by = _reopen_blocked_by_current_blocker(current_blocker)
  blocked_by["approval_record_verdict"] = "DECISION_RECORDED"
  blocked_by["approval_decision"] = record.get("decision")
  blocked_by["approval_decision_route"] = record.get("next_action_expectation")
  blocked_by["approval_record_reasons"] = reasons
  return blocked_by


def _non_approval_only_reasons(reasons):
  """allows_target_operation の理由から非承認そのものの理由を除外する"""
  return [
    reason for reason in reasons
    if not str(reason).startswith("approved 以外の decision は不可逆操作を許可しません")
  ]


def _resolve_non_approved_approval_gate_action(record, current_blocker, decision_reasons):
  """approved 以外の approval decision を next action へ写像する"""
  structural_reasons = _non_approval_only_reasons(decision_reasons)
  if structural_reasons:
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _approval_gate_decision_blocked_by(current_blocker, structural_reasons),
    }

  decision = record.get("decision")
  expectation = record.get("next_action_expectation")
  if decision in {"rejected", "deferred"}:
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _approval_gate_non_approved_blocked_by(
        current_blocker,
        record,
        [f"{decision} decision のため対象 operation へ進みません"],
      ),
    }

  if decision == "changes_requested" and expectation == "redraft":
    phase, _stage = _parse_stage_gate(current_blocker.get("gate"))
    drafting_gate = _stage_gate(phase, "drafting") if phase else None
    return {
      "required_action": "run_reopen_drafting",
      "next_pending_gate": current_blocker.get("gate"),
      "next_drafting_gate": drafting_gate,
      "active_gate": drafting_gate,
      "phase": phase,
      "stage": "drafting" if phase else None,
      "approval_record_path": current_blocker.get("approval_record_path"),
      "blocked_by": None,
    }

  if decision == "changes_requested" and expectation == "repair":
    return {
      "required_action": "repair_workflow_state",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "approval_record_path": current_blocker.get("approval_record_path"),
      "repair_reasons": [
        "changes_requested approval decision requested workflow repair: "
        f"{current_blocker.get('approval_record_path')}"
      ],
      "blocked_by": None,
    }

  return {
    "required_action": "wait_for_human_decision",
    "next_pending_gate": None,
    "next_drafting_gate": None,
    "active_gate": None,
    "phase": None,
    "stage": None,
    "blocked_by": _approval_gate_non_approved_blocked_by(
      current_blocker,
      record,
      [f"未対応の approval decision route です: {decision} / {expectation}"],
    ),
  }


def _resolve_recorded_approval_gate_next_action(cwd, data, pending_gates, current_blocker):
  """記録済み approval gate record から reopen の次 action を解決する"""
  if not isinstance(current_blocker, dict):
    return None
  if current_blocker.get("status") != "decision_recorded":
    return None

  record, reasons = _load_approval_gate_record(cwd, current_blocker.get("approval_record_path"))
  if reasons:
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _approval_gate_decision_blocked_by(current_blocker, reasons),
    }

  contracts, _raw_contracts, contract_reasons = load_contracts(Path(cwd))
  operation_contract = contracts.get(record.get("target_operation_id"))
  if operation_contract is None:
    contract_reasons.append(
      f"operation contract が見つかりません: {record.get('target_operation_id')}"
    )
  if contract_reasons:
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _approval_gate_decision_blocked_by(current_blocker, contract_reasons),
    }

  effective_contract = _approval_branch_effective_contract(
    operation_contract,
    current_blocker.get("gate"),
  )
  current_target_digest = None
  if record.get("binding_kind") in {"artifact_digest", "both"}:
    current_target_digest = _sha256_digest_for_repo_file(cwd, record.get("target_artifact"))
  current_staged_digest = None
  if record.get("binding_kind") in {"staged_file_set_digest", "both"}:
    current_staged_digest = _current_staged_file_set_digest(cwd)

  decision = approval_gate.allows_target_operation_with_current_state(
    record,
    effective_contract,
    current_target_artifact_digest=current_target_digest,
    current_staged_file_set_digest=current_staged_digest,
  )
  if record.get("decision") != "approved":
    return _resolve_non_approved_approval_gate_action(
      record,
      current_blocker,
      list(decision.get("reasons") or []),
    )

  if decision.get("allowed") is not True or record.get("next_action_expectation") != "proceed":
    reasons = list(decision.get("reasons") or [])
    if record.get("next_action_expectation") != "proceed":
      reasons.append(
        "next_action_expectation が proceed ではないため対象 operation へ進めません: "
        f"{record.get('next_action_expectation')}"
      )
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _approval_gate_decision_blocked_by(current_blocker, reasons),
    }

  gate_action = _resolve_reopen_next_gate(data, pending_gates, None)
  if gate_action.get("required_action"):
    return {
      **gate_action,
      "approval_record_path": current_blocker.get("approval_record_path"),
      "blocked_by": None,
    }
  return None


def _reopen_blocked_by_current_blocker(current_blocker):
  """current_blocker を next_action の blocked_by に正規化する"""
  blocked_by = {"type": "current_blocker"}
  if isinstance(current_blocker, dict):
    if current_blocker.get("blocker_type"):
      blocked_by["blocker_type"] = current_blocker.get("blocker_type")
    if current_blocker.get("gate"):
      blocked_by["gate"] = current_blocker.get("gate")
    if current_blocker.get("actor"):
      blocked_by["actor"] = current_blocker.get("actor")
    if current_blocker.get("status"):
      blocked_by["status"] = current_blocker.get("status")
    for field in [
      "approval_record_path",
      "decision_id",
      "decision",
      "decided_by",
      "next_action_expectation",
    ]:
      if current_blocker.get(field):
        blocked_by[field] = current_blocker.get(field)
  return blocked_by


def _reopen_commit_stop_point_blocked_by(data):
  """commit_stop_point を next_action の blocked_by に正規化する"""
  blocked_by = {
    "type": "commit_stop_point",
    "step": data.get("commit_stop_point_step"),
    "kind": data.get("commit_stop_point_kind"),
  }
  if data.get("commit_stop_point_gate"):
    blocked_by["gate"] = data.get("commit_stop_point_gate")
  if data.get("commit_stop_point_reason"):
      blocked_by["reason"] = data.get("commit_stop_point_reason")
  return blocked_by


def _reopen_commit_required_blocked_by(data, relative_path):
  """状態遷移後の commit 境界を next_action の blocked_by に正規化する"""
  blocked_by = {
    "type": "commit_required",
    "step": data.get("step_number"),
    "kind": data.get("commit_required_kind"),
    "file": relative_path,
  }
  if data.get("commit_required_reason"):
    blocked_by["reason"] = data.get("commit_required_reason")
  return blocked_by


def select_reopen_next_action_fields(data, pending_gates, cwd=None):
  """reopen state から唯一の required_action と active gate 情報を選ぶ"""
  current_blocker = data.get("current_blocker")
  if current_blocker:
    if cwd is not None:
      recorded_approval_action = _resolve_recorded_approval_gate_next_action(
        cwd,
        data,
        pending_gates,
        current_blocker,
      )
      if recorded_approval_action is not None:
        return recorded_approval_action
    return {
      "required_action": "wait_for_human_decision",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _reopen_blocked_by_current_blocker(current_blocker),
    }

  if data.get("commit_stop_point") is True:
    return {
      "required_action": "commit_stop_point",
      "next_pending_gate": None,
      "next_drafting_gate": None,
      "active_gate": None,
      "phase": None,
      "stage": None,
      "blocked_by": _reopen_commit_stop_point_blocked_by(data),
    }

  gate_action = _resolve_reopen_next_gate(data, pending_gates, current_blocker)
  next_step = data.get("next_step")
  is_step_three = (
    data.get("step_number") in (3, "3")
    or (isinstance(next_step, str) and "第3過程" in next_step)
  )
  if is_step_three and gate_action["required_action"]:
    return {
      **gate_action,
      "blocked_by": None,
    }

  return {
    "required_action": resolve_reopen_required_action(
      data.get("next_step"),
      current_blocker,
      data.get("step_number"),
    ),
    "next_pending_gate": None,
    "next_drafting_gate": None,
    "active_gate": None,
    "phase": None,
    "stage": None,
    "blocked_by": None,
  }


def build_in_progress_next_action(cwd, relative_path):
  """進行中状態ファイルから next_action を作る"""
  data = load_in_progress_file(cwd, relative_path)
  process_id = data.get("process_id")
  if process_id == "maintenance":
    maintenance_action = data.get("required_action", "continue_maintenance")
    return {
      "kind": "maintenance_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "title": data.get("title"),
      "required_action": "run_maintenance",
      "maintenance_action": maintenance_action,
      "blocked_normal_workflow": data.get("blocked_normal_workflow", True),
      "mainline_blocked_by": data.get("mainline_blocked_by"),
      "allowed_scope": data.get("allowed_scope", []),
      "allowed_files": data.get("allowed_files", []),
      "completion_conditions": data.get("completion_conditions", []),
      "action_parameters": {
        "maintenance_action": maintenance_action,
        "allowed_scope": data.get("allowed_scope", []),
        "allowed_files": data.get("allowed_files", []),
        "completion_conditions": data.get("completion_conditions", []),
        "active_stack_frame_id": relative_path,
        "parent_frame_id": data.get("parent_frame_id"),
      },
      "active_gate": None,
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": data.get(
        "reason",
        "maintenance 手続きの進行中状態ファイルがあります",
      ),
    }
  if process_id == "reopen-procedure":
    pending_gates = data.get("pending_gates", [])
    if pending_gates is None:
      pending_gates = []
    action_fields = select_reopen_next_action_fields(data, pending_gates, cwd=cwd)
    feature_scope = reopen_feature_scope_from_data(data)
    action = {
      "kind": "reopen_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "next_step": data.get("next_step"),
      "step_number": data.get("step_number"),
      "completed_steps": data.get("completed_steps", []),
      "pending_gates": pending_gates,
      "next_pending_gate": action_fields["next_pending_gate"],
      "next_drafting_gate": action_fields["next_drafting_gate"],
      "active_gate": action_fields["active_gate"],
      "current_blocker": data.get("current_blocker"),
      "required_action": action_fields["required_action"],
      "blocked_by": action_fields["blocked_by"],
      "approval_record_path": action_fields.get("approval_record_path"),
      "feature": feature_scope["required_feature_scope"],
      "required_feature_scope": feature_scope["required_feature_scope"],
      "direct_features": feature_scope["direct_features"],
      "indirect_features": feature_scope["indirect_features"],
      "feature_impact_scope_basis": feature_scope["feature_impact_scope_basis"],
      "phase": action_fields["phase"],
      "stage": action_fields["stage"],
      "reason": "reopen 手続きの進行中状態ファイルがあります",
    }
    if action_fields.get("repair_reasons") is not None:
      action["repair_reasons"] = action_fields["repair_reasons"]
    return action
  return {
    "kind": "resume_in_progress",
    "file": relative_path,
    "feature": None,
    "phase": None,
    "stage": None,
    "reason": "stages/in-progress に進行中ファイルがあるため、新規作業より優先します",
  }


def parse_git_status_path(line):
  """git status --short の 1 行から変更後パスを取り出す"""
  if len(line) < 4:
    return None
  path = line[3:]
  if " -> " in path:
    path = path.split(" -> ", 1)[1]
  return path.strip()


def list_changed_files(cwd):
  """git status --short から未コミット変更ファイルを返す"""
  if not (Path(cwd) / ".git").exists():
    return []
  result = subprocess.run(
    ["git", "status", "--short", "--untracked-files=all"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return []
  paths = []
  for line in result.stdout.splitlines():
    path = parse_git_status_path(line)
    if path:
      paths.append(path)
  return sorted(set(paths))


def list_untracked_files(cwd):
  """git status --short から未追跡ファイルを返す"""
  if not (Path(cwd) / ".git").exists():
    return []
  result = subprocess.run(
    ["git", "status", "--short", "--untracked-files=all"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return []
  paths = []
  for line in result.stdout.splitlines():
    if line.startswith("?? "):
      path = parse_git_status_path(line)
      if path:
        paths.append(path)
  return sorted(set(paths))


def _is_machine_generated_record(cwd, path):
  """機械生成・出所明記の派生記録（来歴マーカー付き）かを判定する。

  PLC-DEC-007 候補5・書き込み後検証ポリシー：機械生成記録は独立検証ではなく
  「来歴の刻印＋引用元からの再生成突き合わせ（再現性）」で担保するため、
  書き込み後検証の対象外とする。判定は front-matter の generated_by マーカーで行う。
  """
  try:
    full = Path(cwd) / path
    with full.open(encoding="utf-8", errors="replace") as f:
      head = f.read(1000)
  except OSError:
    return False
  if not head.startswith("---\n"):
    return False
  end = head.find("\n---\n", 4)
  block = head[4:end] if end != -1 else head
  return "generated_by: session-record-extractor" in block


def is_post_write_verification_target(path, cwd="."):
  """post-write-verification 規律の対象ファイルかを判定する"""
  if is_lightweight_self_check_target(path):
    return False
  # 機械生成・出所明記の派生記録は性質上、独立検証ではなく再現性で担保するため対象外
  if _is_machine_generated_record(cwd, path):
    return False
  # 機械が吐く捕捉物（API 生出力・parsed・triage、走行台帳、検証結果ログ）は、独立検証
  # ではなく走行・再実行・再生成で担保するため対象外（性質ベース・ディレクトリ単位）。
  # 新規分は .reviewcompass/evidence/ 配下へ置かれる（docs 配下は凍結旧配置）。
  if (
    "/review-runs/" in path
    or path.startswith("docs/logs/autonomous-parallel/")
    or path.startswith("docs/notes/post-write-verification-review/")
  ):
    return False
  if path.startswith("docs/archive/"):
    return False
  # ツール自身の実行ログは正本文書ではないため対象外
  # （discipline_post_write_verification.md の対象定義「正本文書」に実装を合わせる。
  #   docs/logs/ 配下の他ファイル（autonomous-parallel の計画記録等）は対象のまま。
  #   凍結済み旧ログも引き続き対象外）
  if path in (DEFAULT_LOG_PATH, LEGACY_LOG_PATH):
    return False
  if path.startswith("docs/reviews/"):
    name = Path(path).name
    return (
      name.startswith("reopen-classification-")
      or "-audit-" in name
    ) and name.endswith(".md")
  if path.startswith("docs/"):
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_DIR_PREFIXES):
    return True
  return False


def is_lightweight_self_check_target(path):
  """API post-write ではなく軽量自己精査で扱う作業中メモかを返す。"""
  if path == "TODO_NEXT_SESSION.md":
    return True
  return any(path.startswith(prefix) for prefix in LIGHTWEIGHT_SELF_CHECK_DIR_PREFIXES)


def list_post_write_verification_targets(cwd):
  """未コミット変更のうち post-write-verification 対象を返す"""
  changed = list_changed_files(cwd)
  return post_write_verification_targets_for_paths(cwd, changed)


def post_write_verification_targets_for_paths(cwd, paths):
  """path 群から post-write-verification 対象を返す。

  TODO_NEXT_SESSION.md は単独なら軽量自己精査だが、strict 対象と同時に
  変更される場合は同じ strict 検証に同梱する。
  """
  targets = [
    path
    for path in paths
    if is_post_write_verification_target(path, cwd)
  ]
  if targets and "TODO_NEXT_SESSION.md" in paths:
    return _unique_preserving_order(["TODO_NEXT_SESSION.md"] + targets)
  return targets


def list_lightweight_self_check_targets(cwd):
  """未コミット変更のうち軽量自己精査対象を返す。"""
  strict_targets = list_post_write_verification_targets(cwd)
  return [
    path
    for path in list_changed_files(cwd)
    if is_lightweight_self_check_target(path)
    and path not in strict_targets
  ]


def build_lightweight_self_check_next_state(cwd, targets):
  """軽量自己精査対象の next 状態を返す。完了済みなら None。"""
  if not targets:
    return None
  manifest_state, manifest = evaluate_post_write_manifest_state(cwd, targets)
  if manifest_state == "completed":
    return None
  return {
    "next_action": {
      "kind": "lightweight_self_check",
      "required_action": "review_working_note_without_api",
      "target_files": targets,
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "作業中メモ置き場の変更であり、API post-write verification ではなく軽量自己精査を行う",
    },
    "current_state": {
      "lightweight_self_check_targets": targets,
      "manifest_status": manifest_state,
      "manifest": manifest,
    },
  }


def is_forbidden_post_write_pending_change(path, verification_targets):
  """post-write-verification pending 中に禁止する変更かを判定する"""
  if path.startswith("tools/") and path.endswith(".py"):
    return True
  if path.startswith("templates/"):
    return True
  if path.startswith("docs/disciplines/"):
    non_discipline_targets = [
      target
      for target in verification_targets
      if not target.startswith("docs/disciplines/")
    ]
    return bool(non_discipline_targets)
  return False


def list_forbidden_post_write_pending_changes(cwd, verification_targets):
  """post-write-verification pending 中の禁止変更を返す"""
  return [
    path
    for path in list_changed_files(cwd)
    if is_forbidden_post_write_pending_change(path, verification_targets)
  ]


def load_post_write_manifests(cwd):
  """post-write-verification manifest を読み込む"""
  manifest_dir = Path(cwd) / ".reviewcompass" / "post-write-verification"
  if not manifest_dir.exists():
    return []
  manifests = []
  # 同じ対象を覆う manifest が複数ある場合は、ファイル名が新しいものを優先する。
  # 命名は post-write-YYYY-MM-DD-NNN.yaml の辞書順を前提にする。
  for path in sorted(manifest_dir.glob("*.yaml"), reverse=True):
    try:
      data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
      continue
    if isinstance(data, dict):
      data["_path"] = str(path.relative_to(cwd))
      manifests.append(data)
  return manifests


def verifier_requirements_satisfied(manifest):
  """required_verifiers が completed_verifiers で満たされているかを返す（旧形式フォールバック用）"""
  required = set(manifest.get("required_verifiers") or [])
  if not required:
    return False
  completed = set(manifest.get("completed_verifiers") or [])
  return required.issubset(completed)


def coverage_matrix_satisfied(manifest, target_files):
  """verifications[] の各 required_verifier が全 target_files を網羅しているかを確認する

  verifications[] が存在しない場合は None を返す（呼び出し側で旧形式へフォールバック）。
  存在する場合は、required_verifiers の各検証者について verifications[] の中に
  全 target_files を target_files として含むエントリがあるかを確認する。
  """
  verifications = manifest.get("verifications")
  if not isinstance(verifications, list) or not verifications:
    return None

  required = set(manifest.get("required_verifiers") or [])
  if not required:
    return False

  target_set = set(target_files)
  master_sha256 = manifest.get("target_sha256") or {}

  for verifier in required:
    verifier_has_valid_entry = False
    for entry in verifications:
      if entry.get("verifier") != verifier:
        continue
      entry_targets = set(entry.get("target_files") or [])
      if not target_set.issubset(entry_targets):
        continue
      entry_sha256 = entry.get("target_sha256")
      if not isinstance(entry_sha256, dict):
        continue
      sha256_matches = all(
        entry_sha256.get(t) == master_sha256.get(t)
        for t in target_files
      )
      if sha256_matches:
        verifier_has_valid_entry = True
        break
    if not verifier_has_valid_entry:
      return False
  return True


def unresolved_substantive_count(manifest):
  """manifest の未解決本質的指摘件数を整数で返す"""
  value = manifest.get("unresolved_substantive_findings", 0)
  try:
    return int(value)
  except (TypeError, ValueError):
    return 0


def file_sha256(path):
  """ファイル内容の sha256 を返す。読めない場合は None。"""
  try:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
  except OSError:
    return None


def manifest_hashes_match_current_files(cwd, manifest, target_files):
  """manifest の target_sha256 が現在の対象ファイル内容と一致するかを返す"""
  actual_hashes = {
    target: file_sha256(Path(cwd) / target)
    for target in target_files
  }
  return manifest_hashes_match_values(manifest, target_files, actual_hashes)


def manifest_hashes_match_values(manifest, target_files, actual_hashes):
  """manifest の target_sha256 が指定 hash と一致するかを返す"""
  expected = manifest.get("target_sha256")
  if not isinstance(expected, dict) or not expected:
    return False

  for target in target_files:
    expected_hash = expected.get(target)
    if not expected_hash:
      return False
    actual_hash = actual_hashes.get(target)
    if actual_hash != expected_hash:
      return False
  return True


def load_yaml_file(path):
  """YAML ファイルを dict/list として読み込む。読めない場合は None。"""
  try:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return None


def resolve_review_run_path(cwd, run_dir, value):
  """review run 内の相対パスを実ファイルパスへ解決する"""
  if not value:
    return None
  path = Path(value)
  if path.is_absolute():
    return path
  candidate_from_cwd = Path(cwd) / path
  if candidate_from_cwd.exists():
    return candidate_from_cwd
  return Path(run_dir) / path


def review_run_traceability_satisfied(cwd, manifest):
  """review_run 宣言付き manifest の raw/rounds/triage/summary 整合を検査する

  review_run がない旧 manifest は対象外として True を返す。
  """
  review_run = manifest.get("review_run")
  if review_run is None:
    return True
  if not isinstance(review_run, dict):
    return False

  run_path = review_run.get("path")
  if not run_path:
    return False
  run_dir = Path(cwd) / run_path
  if not run_dir.is_dir():
    return False

  target_manifest_path = run_dir / "target-manifest.yaml"
  rounds_path = run_dir / "rounds.yaml"
  triage_path = run_dir / "triage.yaml"
  summary_path = review_run.get("summary_path")
  if summary_path:
    summary_file = resolve_review_run_path(cwd, run_dir, summary_path)
  else:
    summary_file = run_dir / "model-result-summary.yaml"

  required_paths = [
    target_manifest_path,
    rounds_path,
    triage_path,
    summary_file,
  ]
  if any(path is None or not Path(path).is_file() for path in required_paths):
    return False

  rounds = load_yaml_file(rounds_path)
  triage = load_yaml_file(triage_path)
  summary = load_yaml_file(summary_file)
  if not isinstance(rounds, dict):
    return False
  if not isinstance(triage, dict):
    return False
  if not isinstance(summary, dict):
    return False

  model_results = rounds.get("model_results")
  if not isinstance(model_results, list) or not model_results:
    return False

  required_verifiers = set(manifest.get("required_verifiers") or [])
  model_ids = set()
  for result in model_results:
    if not isinstance(result, dict):
      return False
    model_id = result.get("model_id")
    raw_path = result.get("raw_path")
    raw_sha256 = result.get("raw_sha256")
    parse_status = result.get("parse_status")
    if not model_id or not raw_path or not raw_sha256:
      return False
    if parse_status not in ("parsed", "parse_failed"):
      return False

    raw_file = resolve_review_run_path(cwd, run_dir, raw_path)
    if raw_file is None or not raw_file.is_file():
      return False
    if file_sha256(raw_file) != raw_sha256:
      return False
    model_ids.add(model_id)

  if required_verifiers and not required_verifiers.issubset(model_ids):
    return False

  summary_models = summary.get("models")
  if not isinstance(summary_models, list):
    return False
  summary_by_model = {
    item.get("model_id"): item
    for item in summary_models
    if isinstance(item, dict) and item.get("model_id")
  }
  if not model_ids.issubset(set(summary_by_model)):
    return False

  triage_items = triage.get("items")
  if not isinstance(triage_items, list):
    return False
  triaged_models = set()
  for item in triage_items:
    if not isinstance(item, dict):
      return False
    source_model = item.get("source_model")
    source_raw_path = item.get("source_raw_path")
    decision_status = item.get("decision_status")
    final_label = item.get("final_label")
    if source_model:
      triaged_models.add(source_model)
    if source_raw_path:
      raw_file = resolve_review_run_path(cwd, run_dir, source_raw_path)
      if raw_file is None or not raw_file.is_file():
        return False
    if decision_status == "human_required":
      return False
    if decision_status != "decided":
      return False
    if final_label not in ("must-fix", "should-fix", "leave-as-is"):
      return False

  for model_id in model_ids:
    summary_item = summary_by_model[model_id]
    triage_status = summary_item.get("triage_status")
    if model_id not in triaged_models and triage_status != "no_findings":
      return False
    if triage_status not in ("triaged", "no_findings"):
      return False

  return True


def evaluate_post_write_manifest_state(cwd, target_files):
  """対象ファイル群に対する post-write-verification manifest 状態を返す"""
  actual_hashes = {
    target: file_sha256(Path(cwd) / target)
    for target in target_files
  }
  return evaluate_post_write_manifest_state_for_hashes(cwd, target_files, actual_hashes)


def evaluate_post_write_manifest_state_for_hashes(cwd, target_files, actual_hashes):
  """指定 sha256 群に対する post-write-verification manifest 状態を返す"""
  target_set = set(target_files)
  for manifest in load_post_write_manifests(cwd):
    manifest_targets = set(manifest.get("target_files") or [])
    if not target_set.issubset(manifest_targets):
      continue
    if not manifest_hashes_match_values(manifest, target_files, actual_hashes):
      continue
    if unresolved_substantive_count(manifest) > 0:
      return "human_required", manifest
    coverage_ok = coverage_matrix_satisfied(manifest, target_files)
    if coverage_ok is None:
      coverage_ok = verifier_requirements_satisfied(manifest)
    if (
      manifest.get("status") == "completed"
      and coverage_ok
      and review_run_traceability_satisfied(cwd, manifest)
      and unresolved_substantive_count(manifest) == 0
    ):
      return "completed", manifest
  return "pending", None


def validate_post_write_completion_for_targets(cwd, target_files, actual_hashes=None):
  """post-write 対象ファイルの完了 manifest があるか検査する"""
  post_write_targets = post_write_verification_targets_for_paths(cwd, target_files)
  state = {
    "target_files": post_write_targets,
    "manifest_status": "not_applicable" if not post_write_targets else "pending",
    "manifest_path": None,
  }
  if not post_write_targets:
    return state, []

  if actual_hashes is None:
    actual_hashes = {
      target: file_sha256(Path(cwd) / target)
      for target in post_write_targets
    }
  else:
    actual_hashes = {
      target: actual_hashes.get(target)
      for target in post_write_targets
    }

  manifest_status, manifest = evaluate_post_write_manifest_state_for_hashes(
    cwd,
    post_write_targets,
    actual_hashes,
  )
  state["manifest_status"] = manifest_status
  if manifest:
    state["manifest_path"] = manifest.get("_path")
  if manifest_status == "completed":
    return state, []
  if manifest_status == "human_required":
    return state, [
      "post-write-verification に未解決の本質的指摘があります: "
      + ", ".join(post_write_targets)
    ]
  return state, [
    "post-write-verification 未完了の staged ファイルがあります: "
    + ", ".join(post_write_targets)
  ]


def load_all_feature_specs(cwd):
  """ReviewCompass の全 feature spec.json を読み込む"""
  specs = {}
  missing = []
  for feature in FEATURE_ORDER:
    spec_data = load_spec_json(cwd, feature)
    if spec_data is None:
      missing.append(feature)
    else:
      specs[feature] = spec_data
  return specs, missing


def summarize_workflow_state(specs):
  """next 出力用に workflow_state だけを抽出する"""
  return {
    feature: spec_data.get("workflow_state", {})
    for feature, spec_data in specs.items()
  }


def phase_stage_value(specs, feature, phase, stage):
  """workflow_state.<phase>.<stage> の真偽値を返す"""
  return bool(
    specs
    .get(feature, {})
    .get("workflow_state", {})
    .get(phase, {})
    .get(stage, False)
  )


def all_features_stage_true(specs, phase, stage):
  """全 feature で指定 phase/stage が true かを返す"""
  return all(phase_stage_value(specs, feature, phase, stage) for feature in FEATURE_ORDER)


def list_uncommitted_files(cwd):
  """HEAD との差分と未追跡ファイルを相対パスで返す"""
  paths = []
  diff_result = subprocess.run(
    ["git", "diff", "--name-only", "-z", "HEAD", "--"],
    cwd=str(cwd),
    capture_output=True,
    text=False,
  )
  if diff_result.returncode == 0:
    paths.extend(
      p.decode("utf-8")
      for p in diff_result.stdout.split(b"\0")
      if p
    )
  other_result = subprocess.run(
    ["git", "ls-files", "--others", "--exclude-standard", "-z"],
    cwd=str(cwd),
    capture_output=True,
    text=False,
  )
  if other_result.returncode == 0:
    paths.extend(
      p.decode("utf-8")
      for p in other_result.stdout.split(b"\0")
      if p
    )
  return _unique_preserving_order(paths)


def _read_head_json(cwd, relative_path):
  result = subprocess.run(
    ["git", "show", f"HEAD:{relative_path}"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return None
  try:
    return json.loads(result.stdout)
  except json.JSONDecodeError:
    return None


def _workflow_phase_changed_from_head(cwd, feature, phase):
  relative_path = f".reviewcompass/specs/{feature}/spec.json"
  current_path = Path(cwd) / relative_path
  if not current_path.exists():
    return False
  head_data = _read_head_json(cwd, relative_path)
  if head_data is None:
    return False
  try:
    current_data = json.loads(current_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return False
  head_phase = (
    head_data.get("workflow_state", {})
    .get(phase, {})
  )
  current_phase = (
    current_data.get("workflow_state", {})
    .get(phase, {})
  )
  return head_phase != current_phase


def _phase_artifact_changed(dirty_paths, phase):
  artifact_paths = set(_phase_artifact_paths(None, phase))
  return any(path in artifact_paths for path in dirty_paths)


def _cross_feature_phase_dirty(cwd, dirty_paths, phase):
  if _phase_artifact_changed(dirty_paths, phase):
    return True
  for feature in FEATURE_ORDER:
    spec_path = f".reviewcompass/specs/{feature}/spec.json"
    if (
      spec_path in dirty_paths
      and _workflow_phase_changed_from_head(cwd, feature, phase)
    ):
      return True
  return False


def build_commit_stop_point_next_action(phase, dirty_paths):
  """通常 workflow の phase 終端 commit 停止点を返す"""
  return {
    "kind": "commit_stop_point",
    "required_action": "commit_stop_point",
    "feature": None,
    "phase": phase,
    "stage": "approval",
    "reason": f"{phase}.approval 完了後の未コミット変更があるため、次 phase へ進む前に commit が必要です",
    "blocked_by": {
      "type": "workflow_phase_end",
      "phase": phase,
      "stage": "approval",
      "kind": "phase_approval_complete",
      "dirty_paths": dirty_paths,
    },
  }


def resolve_normal_workflow_commit_stop_point_action(cwd, specs):
  """通常 workflow の cross-feature phase 終端停止点を判定する"""
  dirty_paths = list_uncommitted_files(cwd)
  if not dirty_paths:
    return None
  for phase in CROSS_FEATURE_PHASES:
    if not all_features_stage_true(specs, phase, "approval"):
      continue
    if _cross_feature_phase_dirty(cwd, dirty_paths, phase):
      return build_commit_stop_point_next_action(phase, dirty_paths)
  return None


def build_stage_next_action(feature, phase, stage, reason):
  """機能単位 stage の next_action を作る"""
  return {
    "kind": "stage",
    "feature": feature,
    "phase": phase,
    "stage": stage,
    "reason": reason,
  }


def build_cross_stage_next_action(phase, stage, reason):
  """機能横断 stage の next_action を作る"""
  return {
    "kind": "cross_feature_stage",
    "feature": "all_features",
    "phase": phase,
    "stage": stage,
    "reason": reason,
  }


def _max_existing_mtime(cwd, relative_paths):
  """存在する成果物群の最新更新時刻を返す"""
  mtimes = []
  for relative_path in relative_paths:
    if "*" in relative_path:
      mtimes.extend(
        path.stat().st_mtime
        for path in Path(cwd).glob(relative_path)
        if path.exists()
      )
    else:
      path = Path(cwd) / relative_path
      if path.exists():
        mtimes.append(path.stat().st_mtime)
  if not mtimes:
    return None
  return max(mtimes)


def _phase_artifact_paths(feature, phase):
  """phase の代表成果物パスを返す"""
  if phase == "intent":
    return [
      "intent/INTENT.md",
      "intent/DESIGN_PRINCIPLES.md",
      "intent/NON_GOALS.md",
      "intent/TRACEABILITY.md",
    ]
  if phase == "feature-partitioning":
    return [
      "stages/feature-partitioning/2026-05-24-proposal.md",
    ]
  if phase in ("requirements", "design", "tasks"):
    return [
      f".reviewcompass/specs/{feature}/{phase}.md",
    ]
  if phase == "implementation":
    return [
      f".reviewcompass/specs/{feature}/implementation-drafting.md",
      f".reviewcompass/specs/{feature}/reviews/*implementation*.md",
      f".reviewcompass/specs/{feature}/reviews/*implementation*/*.yaml",
      f".reviewcompass/specs/{feature}/reviews/*implementation*/*.md",
    ]
  return []


def build_upstream_recheck_next_action(
  feature,
  upstream_phase,
  downstream_phase,
  downstream_stage,
  reason,
):
  """上流成果物更新に伴う再展開 next_action を作る"""
  return {
    "kind": "upstream_recheck",
    "feature": feature,
    "phase": downstream_phase,
    "stage": downstream_stage,
    "upstream_phase": upstream_phase,
    "reason": reason,
  }


def _reopen_trigger_for_upstream_phase(upstream_phase):
  """上流正本変更の起点 phase から reopen 分類の既定候補を返す"""
  return {
    "intent": "N-0",
    "feature-partitioning": "N-0",
    "requirements": "R-0",
    "design": "D-0",
    "tasks": "A-0",
  }.get(upstream_phase)


def build_reopen_classification_required_next_action(
  feature,
  upstream_phase,
  downstream_phase,
  downstream_stage,
  reason,
):
  """完了済み workflow の上流正本変更に対する reopen 分類要求を作る"""
  return {
    "kind": "reopen_classification_required",
    "feature": feature,
    "phase": downstream_phase,
    "stage": downstream_stage,
    "upstream_phase": upstream_phase,
    "reopen_trigger": _reopen_trigger_for_upstream_phase(upstream_phase),
    "required_action": "classify_reopen_and_run_reopen_start",
    "reason": reason,
  }


def _load_yaml_file(path):
  """YAML ファイルを dict として読む。読めなければ空 dict を返す"""
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except Exception:
    return {}
  return data if isinstance(data, dict) else {}


def _completed_reopen_covers_downstream_phase(cwd, downstream_phase):
  """完了済み reopen が指定 downstream phase の再確認を覆うか判定する"""
  completed_dir = Path(cwd) / "stages" / "completed"
  if not completed_dir.exists():
    return False

  required_gates = {
    f"stages/{downstream_phase}.yaml#alignment",
    f"stages/{downstream_phase}.yaml#approval",
  }
  allowed_decisions = {
    "affected_update_required",
    "existing_sufficient",
    "no_impact",
    "approved",
    "proxy_approved",
  }
  for path in completed_dir.glob("reopen-procedure-*.yaml"):
    data = _load_yaml_file(path)
    if data.get("step_number") != 4:
      continue
    if data.get("current_blocker") not in (None, "null"):
      continue
    impacted = data.get("impacted_downstream_phases")
    if not isinstance(impacted, list) or downstream_phase not in impacted:
      continue
    decisions = data.get("downstream_impact_decisions")
    if not isinstance(decisions, list):
      continue
    covered = set()
    for decision in decisions:
      if not isinstance(decision, dict):
        continue
      if decision.get("decision") not in allowed_decisions:
        continue
      gate = decision.get("gate")
      if gate in required_gates:
        covered.add(gate)
    if required_gates.issubset(covered):
      return True
  return False


def resolve_upstream_recheck_action(cwd):
  """完了済み workflow に対し、上流更新後の reopen 必要性を検出する"""
  intent_mtime = _max_existing_mtime(cwd, _phase_artifact_paths(None, "intent"))
  partitioning_mtime = _max_existing_mtime(
    cwd,
    _phase_artifact_paths(None, "feature-partitioning"),
  )
  if (
    intent_mtime is not None
    and partitioning_mtime is not None
    and intent_mtime > partitioning_mtime
  ):
    return build_reopen_classification_required_next_action(
      None,
      "intent",
      "feature-partitioning",
      "candidate-proposal",
      "完了済み workflow で intent 成果物が feature-partitioning 成果物より新しいため、reopen 分類が必要です",
    )

  if partitioning_mtime is not None:
    for feature in FEATURE_ORDER:
      requirements_mtime = _max_existing_mtime(
        cwd,
        _phase_artifact_paths(feature, "requirements"),
      )
      if (
        requirements_mtime is not None
        and partitioning_mtime > requirements_mtime
        and not _completed_reopen_covers_downstream_phase(cwd, "requirements")
      ):
        return build_reopen_classification_required_next_action(
          feature,
          "feature-partitioning",
          "requirements",
          "drafting",
          f"完了済み workflow で feature-partitioning 成果物が {feature} requirements 成果物より新しいため、reopen 分類が必要です",
        )

  for upstream_phase, downstream_phase in (
    ("requirements", "design"),
    ("design", "tasks"),
    ("tasks", "implementation"),
  ):
    for feature in FEATURE_ORDER:
      upstream_mtime = _max_existing_mtime(
        cwd,
        _phase_artifact_paths(feature, upstream_phase),
      )
      downstream_mtime = _max_existing_mtime(
        cwd,
        _phase_artifact_paths(feature, downstream_phase),
      )
      if (
        upstream_mtime is not None
        and downstream_mtime is not None
        and upstream_mtime > downstream_mtime
        and not _completed_reopen_covers_downstream_phase(cwd, downstream_phase)
      ):
        return build_reopen_classification_required_next_action(
          feature,
          upstream_phase,
          downstream_phase,
          "drafting",
          f"完了済み workflow で {feature} {upstream_phase} 成果物が {downstream_phase} 成果物より新しいため、reopen 分類が必要です",
        )

  return None


def collect_recheck_items(specs, phase):
  """指定 phase に影響する upstream recheck 項目を集める"""
  items = []
  for feature in FEATURE_ORDER:
    recheck = specs.get(feature, {}).get("recheck", {})
    if not recheck.get("upstream_change_pending", False):
      continue
    impacted = recheck.get("impacted_downstream_phases", [])
    if phase in impacted:
      items.append({
        "feature": feature,
        "impacted_downstream_phases": impacted,
      })
  return items


def augment_cross_feature_next_action(cwd, specs, next_action):
  """機能横断段に必要な確認情報を付加する"""
  if next_action.get("kind") != "cross_feature_stage":
    return next_action

  phase = next_action.get("phase")
  stage = next_action.get("stage")
  augmented = dict(next_action)

  recheck_items = collect_recheck_items(specs, phase)
  if recheck_items:
    augmented["recheck_items"] = recheck_items

  if stage == "review-wave":
    augmented["pending_cross_feature_findings"] = {
      "file": DEFAULT_CARRY_FORWARD_SOURCE_PATH,
      "unresolved_count": count_unresolved_carry_forward_items(
        Path(cwd) / DEFAULT_CARRY_FORWARD_REGISTER_PATH,
      ),
    }

  return augmented


def resolve_next_action(specs):
  """ReviewCompass 現行 workflow_state から次に許可される作業を決める"""
  for phase in PHASE_ORDER:
    stages = PHASE_STAGES[phase]

    if phase in CROSS_FEATURE_PHASES:
      for stage in stages:
        if not all_features_stage_true(specs, phase, stage):
          return build_cross_stage_next_action(
            phase,
            stage,
            f"{phase}.{stage} が全 feature で完了していません",
          )
      continue

    for feature in FEATURE_ORDER:
      if not phase_stage_value(specs, feature, phase, "drafting"):
        return build_stage_next_action(
          feature,
          phase,
          "drafting",
          f"{feature} の {phase}.drafting が未完了です",
        )
      if not phase_stage_value(specs, feature, phase, "triad-review"):
        return build_stage_next_action(
          feature,
          phase,
          "triad-review",
          f"{feature} の {phase}.triad-review が未完了です",
        )

    for stage in ("review-wave", "alignment", "approval"):
      if stage in stages and not all_features_stage_true(specs, phase, stage):
        return build_cross_stage_next_action(
          phase,
          stage,
          f"{phase}.{stage} が全 feature で完了していません",
        )

  return {
    "kind": "completed",
    "feature": None,
    "phase": None,
    "stage": None,
    "reason": "すべての workflow_state が完了しています",
  }


def format_next_human_output(verdict, exit_code, next_action, reasons, current_state_dict):
  """next サブコマンドの人間可読出力を整形する"""
  lines = [
    f"[VERDICT] {verdict}（exit {exit_code}）",
    "[NEXT ACTION]",
    f"  kind: {next_action.get('kind')}",
    f"  feature: {next_action.get('feature')}",
    f"  phase: {next_action.get('phase')}",
    f"  stage: {next_action.get('stage')}",
    f"  reason: {next_action.get('reason')}",
    "[REASON]",
  ]
  if reasons:
    for reason in reasons:
      lines.append(f"  - {reason}")
  else:
    lines.append("  - 問題は検出されませんでした")
  lines.append("[CURRENT STATE]")
  lines.append(json.dumps(current_state_dict, ensure_ascii=False, indent=2))
  return "\n".join(lines)


def cmd_next(args):
  """next サブコマンドのエントリポイント"""
  global FEATURE_ORDER
  cwd = Path.cwd()
  feature_resolution = resolve_feature_order(cwd)
  if feature_resolution["feature_order"] is not None:
    FEATURE_ORDER = feature_resolution["feature_order"]
  in_progress_files = list_in_progress_files(cwd)
  maintenance_action = None

  if in_progress_files:
    in_progress_action = build_in_progress_next_action(cwd, in_progress_files[0])
    if in_progress_action.get("kind") != "maintenance_in_progress":
      next_action = in_progress_action
      current_state = {"in_progress_files": in_progress_files}
      reasons = []
      verdict, exit_code = "OK", 0
    else:
      maintenance_action = in_progress_action

  if not in_progress_files or maintenance_action:
    verification_targets = list_post_write_verification_targets(cwd)
    lightweight_targets = list_lightweight_self_check_targets(cwd)
    if verification_targets:
      manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
      if manifest_state == "completed":
        lightweight_state = build_lightweight_self_check_next_state(cwd, lightweight_targets)
        if lightweight_state:
          next_action = lightweight_state["next_action"]
          current_state = lightweight_state["current_state"]
          current_state["post_write_manifest"] = manifest.get("_path")
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = []
          verdict, exit_code = "OK", 0
        elif maintenance_action:
          next_action = maintenance_action
          current_state = {
            "in_progress_files": in_progress_files,
            "post_write_manifest": manifest.get("_path"),
          }
          reasons = []
          verdict, exit_code = "OK", 0
        else:
          feature_state = feature_definition_next_state(feature_resolution)
          if feature_state:
            next_action, current_state, reasons, verdict, exit_code = feature_state
            current_state["post_write_manifest"] = manifest.get("_path")
          else:
            specs, missing = load_all_feature_specs(cwd)
            if missing:
              next_action = {
                "kind": "unknown",
                "feature": None,
                "phase": None,
                "stage": None,
                "reason": "必要な spec.json が不足しています",
              }
              current_state = {"missing_features": missing, "manifest": manifest}
              reasons = [f"{feature} の spec.json が見つかりません" for feature in missing]
              verdict, exit_code = "DEVIATION", 2
            else:
              resolved_action = (
                resolve_normal_workflow_commit_stop_point_action(cwd, specs)
                or resolve_next_action(specs)
              )
              if resolved_action.get("kind") == "completed":
                resolved_action = resolve_upstream_recheck_action(cwd) or resolved_action
              next_action = augment_cross_feature_next_action(
                cwd,
                specs,
                resolved_action,
              )
              current_state = {
                "feature_order": FEATURE_ORDER,
                "workflow_state": summarize_workflow_state(specs),
                "post_write_manifest": manifest.get("_path"),
              }
              reasons = []
              verdict, exit_code = "OK", 0
      else:
        forbidden_files = list_forbidden_post_write_pending_changes(cwd, verification_targets)
        if forbidden_files:
          next_action = {
            "kind": "post_write_policy_violation",
            "target_files": verification_targets,
            "forbidden_files": forbidden_files,
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification pending 中に禁止された変更があります",
          }
          current_state = {
            "post_write_verification_targets": verification_targets,
            "forbidden_files": forbidden_files,
          }
          if lightweight_targets:
            current_state["lightweight_self_check_targets"] = lightweight_targets
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = [
            f"{path} は post-write-verification pending 中に変更してはいけません"
            for path in forbidden_files
          ]
          verdict, exit_code = "DEVIATION", 2
        elif manifest_state == "human_required":
          next_action = {
            "kind": "post_write_human_decision_required",
            "target_files": verification_targets,
            "manifest": manifest.get("_path"),
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification に未解決の本質的指摘があります",
          }
          current_state = {
            "post_write_verification_targets": verification_targets,
            "manifest": manifest,
          }
          if lightweight_targets:
            current_state["lightweight_self_check_targets"] = lightweight_targets
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = ["未解決の本質的指摘について人間判断が必要です"]
          verdict, exit_code = "OK", 0
        else:
          next_action = {
            "kind": "post_write_verification",
            "target_files": verification_targets,
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification 対象の未コミット変更があります",
          }
          current_state = {"post_write_verification_targets": verification_targets}
          if lightweight_targets:
            current_state["lightweight_self_check_targets"] = lightweight_targets
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = []
          verdict, exit_code = "OK", 0
    else:
      lightweight_state = build_lightweight_self_check_next_state(cwd, lightweight_targets)
      if lightweight_state:
        next_action = lightweight_state["next_action"]
        current_state = lightweight_state["current_state"]
        if maintenance_action:
          current_state["in_progress_files"] = in_progress_files
        reasons = []
        verdict, exit_code = "OK", 0
      elif maintenance_action:
        next_action = maintenance_action
        current_state = {"in_progress_files": in_progress_files}
        reasons = []
        verdict, exit_code = "OK", 0
      else:
        feature_state = feature_definition_next_state(feature_resolution)
        if feature_state:
          next_action, current_state, reasons, verdict, exit_code = feature_state
        else:
          specs, missing = load_all_feature_specs(cwd)
          if missing:
            next_action = {
              "kind": "unknown",
              "feature": None,
              "phase": None,
              "stage": None,
              "reason": "必要な spec.json が不足しています",
            }
            current_state = {"missing_features": missing}
            reasons = [f"{feature} の spec.json が見つかりません" for feature in missing]
            verdict, exit_code = "DEVIATION", 2
          else:
            resolved_action = (
              resolve_normal_workflow_commit_stop_point_action(cwd, specs)
              or resolve_next_action(specs)
            )
            if resolved_action.get("kind") == "completed":
              resolved_action = resolve_upstream_recheck_action(cwd) or resolved_action
            next_action = augment_cross_feature_next_action(
              cwd,
              specs,
              resolved_action,
            )
            current_state = {
              "feature_order": FEATURE_ORDER,
              "workflow_state": summarize_workflow_state(specs),
            }
            reasons = []
            verdict, exit_code = "OK", 0

  next_action = attach_required_context(cwd, next_action)
  effective_prompt = next_action.get("effective_prompt")
  if (
    isinstance(effective_prompt, dict)
    and effective_prompt.get("effective_prompt_loaded") is False
  ):
    reasons.append("effective prompt の元資料をすべて読めません")
    verdict, exit_code = "DEVIATION", 2

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))

  action_dict = {"subcommand": "next", "args": {}}
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def build_operation_prompt_payload(cwd, operation):
  """不可逆操作直前に読む prompt 情報を返す"""
  if operation != "commit":
    return None
  effective_prompt = effective_prompt_for_decision_point(
    cwd,
    "operation_prompt",
    "commit",
  )
  if effective_prompt is None:
    return None
  prompt_context = {
    "kind": "operation_prompt",
    "operation": operation,
  }
  return {
    "verdict": "OK",
    "exit_code": 0,
    "operation": "commit",
    "required_operation_card": "docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card",
    "effective_prompt": materialize_effective_prompt(
      cwd,
      prompt_context,
      effective_prompt,
    ),
  }


def cmd_operation_prompt(args):
  """不可逆操作用 prompt selection を出力する"""
  cwd = Path.cwd()
  payload = build_operation_prompt_payload(cwd, args.operation)
  if payload is None:
    payload = {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "operation": args.operation,
      "reasons": [f"未定義の operation prompt です: {args.operation}"],
    }
  if args.json:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {payload['verdict']}（exit {payload['exit_code']}）")
    print(f"[OPERATION] {payload.get('operation')}")
    if payload.get("required_operation_card"):
      print(f"[CARD] {payload['required_operation_card']}")
    if payload.get("adapter_card"):
      print(f"[ADAPTER] {payload['adapter_card']}")
    for reason in payload.get("reasons", []):
      print(f"- {reason}")
  return payload["exit_code"]


def build_reopen_in_progress_data(args, pending_gates):
  """reopen-start で生成する in-progress データを作る"""
  return {
    "process_id": "reopen-procedure",
    "feature": args.feature,
    "classification": args.classification,
    "started_at": f"{args.date}T00:00:00+09:00",
    "trigger": args.trigger,
    "classification_basis": args.basis,
    "completed_steps": [],
    "next_step": "第1過程：判定とフラグ差し戻し",
    "step_number": 1,
    "pending_gates": pending_gates,
    "current_blocker": None,
  }


def write_reopen_in_progress(cwd, date, data):
  """reopen in-progress YAML を書き出す"""
  path = Path(cwd) / "stages" / "in-progress" / f"reopen-procedure-{date}.yaml"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


def cmd_reopen_start(args):
  """reopen-start サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  pending_gates = REOPEN_TRIGGER_MAP.get(args.classification)
  if pending_gates is None:
    verdict, exit_code = "DEVIATION", 2
    reasons = [f"classification {args.classification} は trigger_map に存在しません"]
    next_action = {
      "kind": "reopen_start_failed",
      "classification": args.classification,
      "feature": args.feature,
      "phase": None,
      "stage": None,
      "reason": "未定義の reopen classification です",
    }
    current_state = {"known_classifications": sorted(REOPEN_TRIGGER_MAP.keys())}
  else:
    data = build_reopen_in_progress_data(args, pending_gates)
    path = write_reopen_in_progress(cwd, args.date, data)
    verdict, exit_code = "OK", 0
    reasons = []
    next_action = {
      "kind": "reopen_started",
      "file": str(path.relative_to(cwd)),
      "classification": args.classification,
      "feature": args.feature,
      "pending_gates": pending_gates,
      "phase": None,
      "stage": None,
      "reason": "reopen in-progress ファイルを生成しました",
    }
    current_state = data

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))

  action_dict = {
    "subcommand": "reopen-start",
    "args": {
      "classification": args.classification,
      "feature": args.feature,
      "basis": args.basis,
      "date": args.date,
      "trigger": args.trigger,
    },
  }
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def _write_json_file(path, data):
  """JSON ファイルを安定した形式で書き戻す"""
  path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def _load_reopen_advance_state(cwd, relpath):
  """reopen-advance-gate の対象 YAML を読む"""
  path = Path(cwd) / relpath
  if not path.exists():
    raise ValueError(f"{relpath} が見つかりません")
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except yaml.YAMLError as e:
    raise ValueError(f"{relpath} を YAML として読めません: {e}") from e
  if not isinstance(data, dict):
    raise ValueError(f"{relpath} は YAML object が必要です")
  if data.get("process_id") != "reopen-procedure":
    raise ValueError("process_id が reopen-procedure ではありません")
  return path, data


def _update_reopen_advance_spec(cwd, set_spec):
  """--set-spec 指定があれば spec.json の workflow_state を更新する"""
  if not set_spec:
    return None
  feature, phase, stage, value_text = set_spec
  if value_text not in ("true", "false"):
    raise ValueError("--set-spec の値は true または false が必要です")
  if phase not in PHASE_STAGES or stage not in PHASE_STAGES[phase]:
    raise ValueError("--set-spec の phase/stage が不正です")
  spec_path = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
  if not spec_path.exists():
    raise ValueError(f"{spec_path.relative_to(cwd)} が見つかりません")
  data = json.loads(spec_path.read_text(encoding="utf-8"))
  workflow_state = data.setdefault("workflow_state", {})
  phase_state = workflow_state.setdefault(phase, {})
  phase_state[stage] = (value_text == "true")
  _write_json_file(spec_path, data)
  return str(spec_path.relative_to(cwd))


def _next_step_for_pending_gate(gate):
  """pending gate から人間向け next_step を作る"""
  phase, stage = _parse_stage_gate(gate)
  return f"第3過程：{phase} {stage}"


def _validate_reopen_pending_gate_references(pending_gates):
  """pending_gates の gate 参照が標準形式か検査する"""
  malformed = []
  non_review_gates = []
  review_stages = {"triad-review", "review-wave", "alignment", "approval"}
  for gate in pending_gates:
    phase, stage = _parse_stage_gate(gate)
    if phase is None or stage is None:
      malformed.append(gate)
    elif stage not in review_stages:
      non_review_gates.append(gate)
  if malformed:
    raise ValueError(
      "pending_gates は stages/<phase>.yaml#<stage> 形式の既知 gate が必要です: "
      + ", ".join(malformed)
    )
  if non_review_gates:
    raise ValueError(
      "pending_gates は review 系 gate（triad-review/review-wave/alignment/approval）だけを指定できます: "
      + ", ".join(non_review_gates)
    )


def _set_reopen_gate_commit_stop_point(data, gate):
  """第3過程の review 系 gate 完了後を構造化された停止点コミットにする"""
  kind = _commit_stop_point_kind_for_gate(gate)
  if kind is None or kind == "drafting_complete":
    return
  phase, stage = _parse_stage_gate(gate)
  data["commit_stop_point"] = True
  data["commit_stop_point_step"] = data.get("step_number")
  data["commit_stop_point_kind"] = kind
  data["commit_stop_point_gate"] = gate
  data["commit_stop_point_reason"] = f"{phase} {stage} 完了時点の停止点"


def cmd_reopen_advance_step(args):
  """reopen 第1・第2過程の完了更新を機械処理する"""
  cwd = Path.cwd()
  reasons = []
  try:
    path, data = _load_reopen_advance_state(cwd, args.file)
    from_step = int(args.from_step)
    if from_step not in (1, 2):
      raise ValueError("--from-step は 1 または 2 が必要です")
    if data.get("step_number") not in (from_step, str(from_step)):
      raise ValueError("現在の step_number と --from-step が一致しません")
    if not args.completed_step.strip():
      raise ValueError("--completed-step は空にできません")
    if not args.rationale.strip():
      raise ValueError("--rationale は空にできません")
    evidence = args.evidence or []
    if not evidence:
      raise ValueError("--evidence は 1 件以上必要です")

    completed_steps = data.get("completed_steps")
    if completed_steps is None:
      completed_steps = []
    if not isinstance(completed_steps, list):
      raise ValueError("completed_steps は list が必要です")
    if args.completed_step not in completed_steps:
      completed_steps.append(args.completed_step)
    data["completed_steps"] = completed_steps

    records = data.get("reopen_step_records")
    if records is None:
      records = []
    if not isinstance(records, list):
      raise ValueError("reopen_step_records は list が必要です")
    records.append(
      {
        "from_step": from_step,
        "completed_step": args.completed_step,
        "rationale": args.rationale,
        "evidence": evidence,
      }
    )
    data["reopen_step_records"] = records

    if from_step == 1:
      data["step_number"] = 2
      data["next_step"] = "第2過程：正本修正"
      data["current_blocker"] = None
    else:
      data["step_number"] = 2
      data["next_step"] = "第2過程：停止点コミット"
      data["current_blocker"] = None
      data["commit_stop_point"] = True
      data["commit_stop_point_step"] = 2
      data["commit_stop_point_kind"] = "canonical_update_complete"
      data["commit_stop_point_reason"] = "第2過程の正本修正完了"

    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "reopen_step_advanced",
      "file": args.file,
      "from_step": from_step,
      "phase": None,
      "stage": None,
      "reason": "reopen step を更新しました",
    }
    current_state = {
      "file": args.file,
      "step_number": data["step_number"],
      "next_step": data["next_step"],
      "current_blocker": data.get("current_blocker"),
    }
  except (OSError, ValueError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "reopen_advance_step_failed",
      "file": args.file,
      "from_step": args.from_step,
      "phase": None,
      "stage": None,
      "reason": "reopen step を更新できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def cmd_reopen_advance_after_commit_stop_point(args):
  """reopen 停止点 commit 後に commit_stop_point を消費する"""
  cwd = Path.cwd()
  reasons = []
  try:
    path, data = _load_reopen_advance_state(cwd, args.file)
    if data.get("commit_stop_point") is not True:
      raise ValueError("commit_stop_point=true の reopen 停止点ではありません")
    if not _is_structured_reopen_commit_stop_point(data):
      raise ValueError("構造化された commit_stop_point ではありません")
    current_kind = data.get("commit_stop_point_kind")
    if current_kind != args.kind:
      raise ValueError(
        "commit_stop_point_kind が --kind と一致しません: "
        f"{current_kind} != {args.kind}"
      )
    if not args.head.strip():
      raise ValueError("--head は空にできません")
    evidence = args.evidence or []
    if not evidence:
      raise ValueError("--evidence は 1 件以上必要です")

    records = data.get("commit_stop_point_records")
    if records is None:
      records = []
    if not isinstance(records, list):
      raise ValueError("commit_stop_point_records は list が必要です")
    records.append(
      {
        "step": data.get("commit_stop_point_step"),
        "kind": current_kind,
        "gate": data.get("commit_stop_point_gate"),
        "reason": data.get("commit_stop_point_reason"),
        "head": args.head.strip(),
        "evidence": evidence,
      }
    )
    data["commit_stop_point_records"] = records
    for key in [
      "commit_stop_point",
      "commit_stop_point_step",
      "commit_stop_point_kind",
      "commit_stop_point_gate",
      "commit_stop_point_reason",
    ]:
      data.pop(key, None)

    data["current_blocker"] = None
    pending_gates = data.get("pending_gates")
    if isinstance(pending_gates, list) and pending_gates:
      data["step_number"] = 3
      data["next_step"] = _next_step_for_pending_gate(pending_gates[0])
    else:
      data["step_number"] = 4
      data["next_step"] = "第4過程：完了"

    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "reopen_commit_stop_point_advanced",
      "file": args.file,
      "commit_stop_point_kind": current_kind,
      "head": args.head.strip(),
      "phase": None,
      "stage": None,
      "reason": "reopen commit stop point を消費しました",
    }
    current_state = {
      "file": args.file,
      "step_number": data.get("step_number"),
      "next_step": data.get("next_step"),
      "current_blocker": data.get("current_blocker"),
    }
  except (OSError, ValueError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "reopen_commit_stop_point_advance_failed",
      "file": args.file,
      "commit_stop_point_kind": args.kind,
      "phase": None,
      "stage": None,
      "reason": "reopen commit stop point を消費できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def cmd_reopen_advance_gate(args):
  """reopen 第3過程の pending gate 完了更新を機械処理する"""
  cwd = Path.cwd()
  reasons = []
  try:
    path, data = _load_reopen_advance_state(cwd, args.file)
    pending_gates = data.get("pending_gates")
    if not isinstance(pending_gates, list) or not all(isinstance(v, str) for v in pending_gates):
      raise ValueError("pending_gates は文字列 list が必要です")
    _validate_reopen_pending_gate_references(pending_gates)
    if not pending_gates or pending_gates[0] != args.gate:
      raise ValueError("指定 gate は pending_gates の先頭である必要があります")
    evidence = args.evidence or []
    if not evidence:
      raise ValueError("--evidence は 1 件以上必要です")
    approval_record_consumed_path, consume_reasons = _consume_recorded_approval_gate_record(
      cwd,
      data.get("current_blocker"),
      args.gate,
    )
    if consume_reasons:
      raise ValueError("; ".join(consume_reasons))

    spec_path = _update_reopen_advance_spec(cwd, args.set_spec)

    remaining_gates = pending_gates[1:]
    data["pending_gates"] = remaining_gates
    completed_gates = data.get("completed_gates")
    if completed_gates is None:
      completed_gates = []
    if not isinstance(completed_gates, list):
      raise ValueError("completed_gates は list が必要です")
    if args.gate not in completed_gates:
      completed_gates.append(args.gate)
    data["completed_gates"] = completed_gates

    completed_steps = data.get("completed_steps")
    if completed_steps is None:
      completed_steps = []
    if not isinstance(completed_steps, list):
      raise ValueError("completed_steps は list が必要です")
    if args.completed_step and args.completed_step not in completed_steps:
      completed_steps.append(args.completed_step)
    data["completed_steps"] = completed_steps

    decisions = data.get("downstream_impact_decisions")
    if decisions is None:
      decisions = []
    if not isinstance(decisions, list):
      raise ValueError("downstream_impact_decisions は list が必要です")
    decisions.append(
      {
        "gate": args.gate,
        "feature_scope": args.feature_scope,
        "decision": args.decision,
        "rationale": args.rationale,
        "evidence": evidence,
      }
    )
    data["downstream_impact_decisions"] = decisions
    data["current_blocker"] = None
    if remaining_gates:
      data["next_step"] = _next_step_for_pending_gate(remaining_gates[0])
      data["step_number"] = 3
    else:
      data["next_step"] = "第4過程：完了"
      data["step_number"] = 4
    _set_reopen_gate_commit_stop_point(data, args.gate)

    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "reopen_gate_advanced",
      "file": args.file,
      "gate": args.gate,
      "remaining_gates": remaining_gates,
      "phase": None,
      "stage": None,
      "reason": "reopen pending gate を更新しました",
    }
    current_state = {
      "file": args.file,
      "updated_spec": spec_path,
      "pending_gates": remaining_gates,
      "completed_gates": completed_gates,
      "approval_record_consumed_path": approval_record_consumed_path,
    }
  except (OSError, ValueError, json.JSONDecodeError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "reopen_advance_gate_failed",
      "file": args.file,
      "gate": args.gate,
      "phase": None,
      "stage": None,
      "reason": "reopen pending gate を更新できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def cmd_reopen_set_blocker(args):
  """reopen 第3過程の承認待ち blocker を構造化して設定する"""
  cwd = Path.cwd()
  reasons = []
  try:
    path, data = _load_reopen_advance_state(cwd, args.file)
    pending_gates = data.get("pending_gates")
    if not isinstance(pending_gates, list) or not all(isinstance(v, str) for v in pending_gates):
      raise ValueError("pending_gates は文字列 list が必要です")
    _validate_reopen_pending_gate_references(pending_gates)
    if not pending_gates or pending_gates[0] != args.gate:
      raise ValueError("指定 gate は pending_gates の先頭である必要があります")

    phase, stage = _parse_stage_gate(args.gate)
    if phase is None or stage is None:
      raise ValueError("--gate は stages/<phase>.yaml#<stage> 形式が必要です")
    if stage != "approval":
      raise ValueError("reopen-set-blocker は approval gate だけを対象にできます")
    if not args.rationale.strip():
      raise ValueError("--rationale は空にできません")
    evidence = args.evidence or []
    if not evidence:
      raise ValueError("--evidence は 1 件以上必要です")

    blocker = {
      "blocker_type": "approval_gate",
      "gate": args.gate,
      "actor": args.actor,
      "status": "waiting_for_approval",
      "rationale": args.rationale,
      "evidence": evidence,
    }
    data["current_blocker"] = blocker

    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "reopen_blocker_set",
      "file": args.file,
      "gate": args.gate,
      "phase": phase,
      "stage": stage,
      "reason": "reopen approval blocker を設定しました",
    }
    current_state = {
      "file": args.file,
      "current_blocker": blocker,
    }
  except (OSError, ValueError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "reopen_set_blocker_failed",
      "file": args.file,
      "gate": args.gate,
      "phase": None,
      "stage": None,
      "reason": "reopen approval blocker を設定できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def _approval_record_output_path(cwd, decision_id, out):
  """approval gate record の保存先を repo-relative path として返す"""
  if out:
    relative = Path(out)
  else:
    safe_decision_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", decision_id).strip("-")
    relative = Path(".reviewcompass") / "runtime" / "approvals" / f"{safe_decision_id}.yaml"
  if relative.is_absolute():
    raise ValueError("--out は repo-relative path で指定してください")
  if ".." in relative.parts:
    raise ValueError("--out に親ディレクトリ参照は指定できません")
  if not str(relative).startswith(".reviewcompass/runtime/approvals/"):
    raise ValueError("--out は .reviewcompass/runtime/approvals/ 配下に保存してください")
  return relative, cwd / relative


def cmd_record_human_decision(args):
  """approval gate の人間判断 record を保存して blocker に結びつける"""
  cwd = Path.cwd()
  reasons = []
  record_relative_path = None
  try:
    path, data = _load_reopen_advance_state(cwd, args.file)
    blocker = data.get("current_blocker")
    if not isinstance(blocker, dict):
      raise ValueError("current_blocker が必要です")
    if blocker.get("blocker_type") != "approval_gate":
      raise ValueError("current_blocker.blocker_type は approval_gate である必要があります")
    if blocker.get("gate") != args.gate:
      raise ValueError("--gate は current_blocker.gate と一致する必要があります")
    if blocker.get("status") != "waiting_for_approval":
      raise ValueError("current_blocker.status は waiting_for_approval である必要があります")

    record = {
      "schema_version": "approval-gate-v1",
      "decision_id": args.decision_id,
      "decision": args.decision,
      "decision_scope": args.decision_scope,
      "target_operation_id": args.target_operation_id,
      "target_required_action": args.target_required_action,
      "target_artifact": args.target_artifact,
      "target_artifact_digest": args.target_artifact_digest,
      "staged_file_set_digest": args.staged_file_set_digest,
      "binding_kind": args.binding_kind,
      "decided_by": args.decided_by,
      "decided_at": args.decided_at,
      "source_ref": args.source_ref,
      "source_digest": args.source_digest,
      "rationale": args.rationale,
      "next_action_expectation": args.next_action_expectation,
      "consumed": False,
    }
    validation = approval_gate.validate_approval_gate_record(record)
    if validation.get("verdict") != "OK":
      raise ValueError("; ".join(validation.get("reasons") or ["approval gate record が不正です"]))
    if args.decision_scope == "human_only" and args.decided_by not in {"user", "human"}:
      raise ValueError("human_only decision は人間 actor でのみ記録できます")

    record_relative_path, record_path = _approval_record_output_path(
      cwd,
      args.decision_id,
      args.out,
    )
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
      yaml.safe_dump(record, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    updated_blocker = dict(blocker)
    updated_blocker.update({
      "status": "decision_recorded",
      "approval_record_path": str(record_relative_path),
      "decision_id": args.decision_id,
      "decision": args.decision,
      "decided_by": args.decided_by,
      "next_action_expectation": args.next_action_expectation,
    })
    data["current_blocker"] = updated_blocker
    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "human_decision_recorded",
      "file": args.file,
      "gate": args.gate,
      "approval_record_path": str(record_relative_path),
      "phase": None,
      "stage": None,
      "reason": "approval gate decision を記録しました",
    }
    current_state = {
      "file": args.file,
      "current_blocker": updated_blocker,
      "approval_record_path": str(record_relative_path),
    }
  except (OSError, ValueError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "record_human_decision_failed",
      "file": args.file,
      "gate": args.gate,
      "approval_record_path": str(record_relative_path) if record_relative_path else None,
      "phase": None,
      "stage": None,
      "reason": "approval gate decision を記録できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def _reopen_finalize_feature_impact_items(feature_impacts):
  """--feature-impact 指定を feature_impact_decisions へ変換する"""
  items = []
  for values in feature_impacts or []:
    feature, decision, impact_basis, rationale, evidence = values
    items.append({
      "feature": feature,
      "decision": decision,
      "impact_basis": impact_basis,
      "rationale": rationale,
      "evidence": [evidence],
    })
  return items


def _reopen_finalize_new_feature_decision(values):
  """--new-feature-decision 指定を new_feature_decision へ変換する"""
  decision, rationale, evidence = values
  return {
    "decision": decision,
    "rationale": rationale,
    "evidence": [evidence],
  }


def _completed_reopen_path(cwd, source_path):
  """in-progress reopen path から completed 側 path を返す"""
  in_progress_dir = Path(cwd) / "stages" / "in-progress"
  completed_dir = Path(cwd) / "stages" / "completed"
  try:
    source_path.relative_to(in_progress_dir)
  except ValueError as e:
    raise ValueError("--file は stages/in-progress/ 配下の reopen YAML が必要です") from e
  return completed_dir / source_path.name


def _reopen_feature_spec_path(cwd, data):
  """reopen state の feature に対応する spec.json path を返す"""
  feature = data.get("feature")
  if isinstance(feature, list):
    if len(feature) != 1:
      return None
    feature = feature[0]
  if not isinstance(feature, str) or not feature:
    return None
  return Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"


def _prepare_reopen_feature_recheck_clear(cwd, data):
  """reopen-finalize 時に対象 feature の recheck クリア内容を準備する"""
  spec_path = _reopen_feature_spec_path(cwd, data)
  if spec_path is None or not spec_path.exists():
    return None, None
  try:
    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
  except json.JSONDecodeError as e:
    raise ValueError(f"{spec_path.relative_to(cwd)} を JSON として読めません") from e
  spec_data["recheck"] = {
    "upstream_change_pending": False,
    "impacted_downstream_phases": [],
  }
  spec_text = json.dumps(spec_data, ensure_ascii=False, indent=2) + "\n"
  return spec_path, spec_text


def _write_text_via_replace(path, text):
  """同一 directory 内の一時ファイル経由で text を置換保存する"""
  tmp_path = path.with_name(f".{path.name}.tmp")
  tmp_path.write_text(text, encoding="utf-8")
  tmp_path.replace(path)


def _append_reopen_finalize_step_record(data, completed_step, evidence):
  """reopen 第4過程完了の履歴レコードを不足なく追加する"""
  records = data.get("reopen_step_records")
  if records is None:
    records = []
  if not isinstance(records, list):
    raise ValueError("reopen_step_records は list が必要です")
  if any(record.get("from_step") == 4 for record in records if isinstance(record, dict)):
    data["reopen_step_records"] = records
    return
  record_evidence = [item for item in evidence if item]
  records.append(
    {
      "from_step": 4,
      "completed_step": completed_step,
      "rationale": (
        "全 pending gate が完了し、対象 feature の recheck をクリアしたうえで、"
        "in-progress reopen 記録を completed state として保存した。"
      ),
      "evidence": record_evidence,
    }
  )
  data["reopen_step_records"] = records


def cmd_reopen_finalize(args):
  """reopen 第4過程の完了 YAML 生成と completed 移動を機械処理する"""
  cwd = Path.cwd()
  reasons = []
  try:
    source_path, data = _load_reopen_advance_state(cwd, args.file)
    if data.get("step_number") not in (4, "4"):
      raise ValueError("reopen-finalize は第4過程の state だけを完了化できます")
    pending_gates = data.get("pending_gates")
    if pending_gates not in ([], None):
      raise ValueError("reopen-finalize は pending_gates が空の state だけを完了化できます")
    if data.get("current_blocker") not in (None, "null"):
      raise ValueError("reopen-finalize は current_blocker が無い state だけを完了化できます")

    data["step_number"] = 4
    data["next_step"] = "完了"
    data["pending_gates"] = []
    data["current_blocker"] = None
    data["impacted_downstream_phases"] = args.impacted_downstream_phase or []
    data["feature_impact_decisions"] = _reopen_finalize_feature_impact_items(
      args.feature_impact
    )
    data["new_feature_decision"] = _reopen_finalize_new_feature_decision(
      args.new_feature_decision
    )
    completed_steps = data.get("completed_steps")
    if completed_steps is None:
      completed_steps = []
    if not isinstance(completed_steps, list):
      raise ValueError("completed_steps は list が必要です")
    if args.completed_step and args.completed_step not in completed_steps:
      completed_steps.append(args.completed_step)
    data["completed_steps"] = completed_steps

    impact_errors = _validate_feature_impact_decisions(data)
    if impact_errors:
      raise ValueError("; ".join(impact_errors))
    if (
      not isinstance(data["impacted_downstream_phases"], list)
      or not all(isinstance(v, str) and v in PHASE_STAGES for v in data["impacted_downstream_phases"])
    ):
      raise ValueError("impacted_downstream_phases は既知フェーズ名の list が必要です")

    target_path = _completed_reopen_path(cwd, source_path)
    if target_path.exists():
      raise ValueError(f"{target_path.relative_to(cwd)} は既に存在します")
    completed_step = args.completed_step or "第4過程 完了"
    spec_path, spec_text = _prepare_reopen_feature_recheck_clear(cwd, data)
    spec_evidence = str(spec_path.relative_to(cwd)) if spec_path else None
    _append_reopen_finalize_step_record(
      data,
      completed_step,
      [
        spec_evidence,
        str(target_path.relative_to(cwd)),
      ],
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text_via_replace(
      target_path,
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    )
    source_path.unlink()
    if spec_path and spec_text:
      _write_text_via_replace(spec_path, spec_text)
    verdict, exit_code = "OK", 0
    next_action = {
      "kind": "reopen_finalized",
      "file": str(target_path.relative_to(cwd)),
      "source_file": args.file,
      "phase": None,
      "stage": None,
      "reason": "reopen 完了 YAML を generated completed state として保存しました",
    }
    current_state = {
      "source_file": args.file,
      "completed_file": str(target_path.relative_to(cwd)),
      "feature_impact_count": len(data["feature_impact_decisions"]),
      "impacted_downstream_phases": data["impacted_downstream_phases"],
    }
  except (OSError, ValueError, yaml.YAMLError) as e:
    verdict, exit_code = "DEVIATION", 2
    reasons = [str(e)]
    next_action = {
      "kind": "reopen_finalize_failed",
      "file": args.file,
      "phase": None,
      "stage": None,
      "reason": "reopen 完了 YAML を生成できません",
    }
    current_state = {}

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
  return exit_code


def _feature_all_approved(specs, feature):
  """feature の全 phase で approval=true かを返す（review-wave-summary 用、Req 10）"""
  ws = specs.get(feature, {}).get("workflow_state", {})
  approvals = [
    v.get("approval")
    for v in ws.values()
    if isinstance(v, dict) and "approval" in v
  ]
  return bool(approvals) and all(bool(a) for a in approvals)


def aggregate_triage_for_summary(cwd):
  """triage.yaml 群を走査し件数を集計する（Req 10、design §2 集計規則）

  戻り値：(unresolved, draft, human_required, errors)
  - unresolved／human_required は item 単位、draft は run 単位。
  - 重複排除は run_id（＝ディレクトリ名）単位で、新パス（evidence）を優先。
  - 任意記録の非在（glob ゼロ件）は 0 件として正常。存在して解析不能なら errors に積む。
  """
  cwd = Path(cwd)
  search_bases = [
    cwd / ".reviewcompass" / "evidence" / "review-runs",
    cwd / ".reviewcompass" / "specs" / "_cross_feature" / "reviews",
  ]
  by_run = {}
  for base in search_bases:
    if not base.is_dir():
      continue
    for tpath in sorted(base.glob("*/triage.yaml")):
      run_id = tpath.parent.name
      if run_id not in by_run:
        by_run[run_id] = tpath
  unresolved = human_required = draft = 0
  errors = []
  for run_id in sorted(by_run):
    tpath = by_run[run_id]
    try:
      data = yaml.safe_load(tpath.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError):
      errors.append(f"任意記録の解析不能: {tpath.relative_to(cwd)}")
      continue
    if not isinstance(data, dict):
      errors.append(f"任意記録の構造異常: {tpath.relative_to(cwd)}")
      continue
    if data.get("triage_status") == "draft":
      draft += 1
    items = data.get("items") or []
    if isinstance(items, list):
      for item in items:
        if not isinstance(item, dict):
          continue
        decision_status = item.get("decision_status")
        if decision_status != "decided":
          unresolved += 1
        if decision_status == "human_required":
          human_required += 1
  return unresolved, draft, human_required, errors


def build_review_wave_summary(cwd):
  """review-wave 横断確認の要約データを構築する（Req 10、design §1〜§5）

  戻り値：(summary_dict, exit_code)。exit_code は 0（ok）／2（insufficient）。
  読み取りに徹し、spec.json・triage・phase を書き換えない。
  """
  cwd = Path(cwd)
  errors = []

  # 必須記録：全 feature の spec.json
  specs, missing = load_all_feature_specs(cwd)
  for feature in missing:
    errors.append(f"必須記録の欠落: {feature}/spec.json")

  # 必須記録：feature-dependency.yaml
  dep_data, dep_path, dep_error = load_feature_dependency(cwd)
  if dep_error:
    errors.append(f"必須記録の解析不能: feature-dependency.yaml ({dep_error})")
    feature_order = []
    features_dep = {}
  elif dep_data is None:
    errors.append("必須記録の欠落: feature-dependency.yaml")
    feature_order = []
    features_dep = {}
  else:
    feature_order = dep_data.get("feature_order") or []
    features_dep = dep_data.get("features") or {}

  # features[]：coverage・phases・recheck
  features = []
  for feature in FEATURE_ORDER:
    ws = specs.get(feature, {}).get("workflow_state", {})
    total = 0
    completed = 0
    phases = {}
    for phase, stages in ws.items():
      if not isinstance(stages, dict):
        continue
      phase_stages = {}
      for stage, value in stages.items():
        if stage == "reference":
          continue
        flag = bool(value)
        phase_stages[stage] = flag
        total += 1
        if flag:
          completed += 1
      phases[phase] = phase_stages
    recheck = specs.get(feature, {}).get("recheck", {}) or {}
    features.append({
      "name": feature,
      "coverage": {
        "completed": completed,
        "total": total,
        "all_approved": _feature_all_approved(specs, feature),
      },
      "phases": phases,
      "recheck": {
        "upstream_change_pending": bool(recheck.get("upstream_change_pending", False)),
        "impacted_downstream_phases": list(recheck.get("impacted_downstream_phases", []) or []),
      },
    })

  # triage 件数
  unresolved, draft, human_required, triage_errors = aggregate_triage_for_summary(cwd)
  errors.extend(triage_errors)

  # 依存状況（未充足依存＝上流が all_approved でない）
  unmet = []
  for feature in feature_order:
    entry = features_dep.get(feature, {})
    deps = entry.get("depends_on", []) if isinstance(entry, dict) else []
    dep_names = list(deps.keys()) if isinstance(deps, dict) else list(deps or [])
    for dep in dep_names:
      if not _feature_all_approved(specs, dep):
        unmet.append({"feature": feature, "depends_on": dep})

  # carry-forward 未消化
  carry = count_unresolved_carry_forward_items(cwd / DEFAULT_CARRY_FORWARD_REGISTER_PATH)

  status = "ok" if not errors else "insufficient"
  summary = {
    "schema_version": 1,
    "generated_at": None,
    "status": status,
    "features": features,
    "triage": {
      "unresolved": unresolved,
      "draft": draft,
      "human_required": human_required,
    },
    "dependencies": {"feature_order": list(feature_order), "unmet": unmet},
    "carry_forward": {"unresolved": carry},
    "errors": errors,
  }
  return summary, (0 if status == "ok" else 2)


def render_review_wave_summary_markdown(summary):
  """review-wave 要約を Markdown で描画する（JSON と情報同等、Req 10 受入 3）"""
  triage = summary["triage"]
  deps = summary["dependencies"]
  lines = ["# review-wave 横断確認サマリ", ""]
  lines.append(f"- status: {summary['status']}")
  lines.append(
    f"- triage: unresolved={triage['unresolved']} / draft(run)={triage['draft']}"
    f" / human_required={triage['human_required']}"
    "（unresolved・human_required は item 単位、draft は run 単位）"
  )
  lines.append(f"- carry-forward 未消化: {summary['carry_forward']['unresolved']}")
  lines.append(f"- feature_order: {', '.join(deps['feature_order']) if deps['feature_order'] else '(未解決)'}")
  if deps["unmet"]:
    lines.append("- 未充足依存: " + ", ".join(f"{u['feature']}←{u['depends_on']}" for u in deps["unmet"]))
  else:
    lines.append("- 未充足依存: なし")
  lines.append("")
  lines.append("## feature coverage")
  lines.append("")
  lines.append("| feature | completed/total | all_approved | recheck |")
  lines.append("| --- | --- | --- | --- |")
  for f in summary["features"]:
    cov = f["coverage"]
    rc = f["recheck"]
    if rc["upstream_change_pending"]:
      pending = "pending(" + ",".join(rc["impacted_downstream_phases"]) + ")"
    else:
      pending = "clear"
    lines.append(f"| {f['name']} | {cov['completed']}/{cov['total']} | {cov['all_approved']} | {pending} |")
  if summary["status"] != "ok":
    lines.append("")
    lines.append("## ⚠ 不完全（insufficient）— 完了として扱わないこと")
    for e in summary["errors"]:
      lines.append(f"- {e}")
  return "\n".join(lines) + "\n"


def cmd_decision_source_lint(args):
  """decision-source-lint サブコマンドのエントリポイント（Req 11）"""
  from check_workflow_action.decision_source_lint import (
    run_decision_source_lint_all,
    run_verify_pending,
    lint_decision_file,
    load_decision_source_lint_config,
  )
  cwd = Path.cwd()

  if getattr(args, "verify_pending", False):
    result = run_verify_pending(cwd)
    for msg in result.messages:
      print(msg)
    return result.exit_code

  if getattr(args, "decision_file", None):
    config = load_decision_source_lint_config(cwd)
    path = Path(args.decision_file)
    if not path.is_absolute():
      path = cwd / path
    result = lint_decision_file(path, cwd, config)
    for msg in result.messages:
      print(msg)
    return result.exit_code

  result = run_decision_source_lint_all(cwd)
  for msg in result.messages:
    print(msg)
  return result.exit_code


def cmd_review_wave_summary(args):
  """review-wave-summary サブコマンドのエントリポイント（Req 10）"""
  cwd = Path.cwd()
  summary, exit_code = build_review_wave_summary(cwd)
  if args.json:
    output = json.dumps(summary, ensure_ascii=False, indent=2)
  else:
    output = render_review_wave_summary_markdown(summary)
  print(output)

  out_path = None
  if getattr(args, "out", None):
    out_path = Path(args.out)
  elif getattr(args, "save", False):
    ext = "json" if args.json else "md"
    out_path = (
      cwd / ".reviewcompass" / "specs" / "_cross_feature" / "reviews"
      / f"review-wave-summary.{ext}"
    )
  if out_path is not None:
    try:
      out_path.parent.mkdir(parents=True, exist_ok=True)
      out_path.write_text(
        output if output.endswith("\n") else output + "\n",
        encoding="utf-8",
      )
    except OSError as e:
      print(f"warning: 要約出力の保存に失敗しました: {e}", file=sys.stderr)

  return exit_code


def cmd_operation_preflight(args):
  """operation-preflight サブコマンドのエントリポイント（Req 12）"""
  response = run_preflight(Path.cwd(), args.operation_id)
  verdict = response.get("verdict")
  allowed_verdicts = set(response.get("allowed_verdicts") or [])
  if verdict not in allowed_verdicts:
    response.setdefault("reasons", []).append(f"未知の verdict です: {verdict}")
    response["verdict"] = "DEVIATION"
    verdict = "DEVIATION"
  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {verdict}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    print(f"[ACTION] {response.get('next_step')}")
  if verdict == "OK":
    return 0
  if verdict == "WARN":
    return 1
  return 2


def cmd_operation_contract_check(args):
  """operation-contract-check サブコマンドのエントリポイント（Req 13）"""
  response = run_contract_check(Path.cwd())
  verdict = response.get("verdict")
  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {verdict}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    print("[ACTION] proceed" if verdict == "OK" else "[ACTION] stop")
  return 0 if verdict == "OK" else 2


def cmd_workflow_snapshot(args):
  """workflow-snapshot サブコマンドのエントリポイント（Req 14）"""
  snapshot = build_snapshot(Path.cwd())
  response = {
    "verdict": "OK",
    "operation_mode": "read_only",
    "snapshot": snapshot,
  }
  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print("[VERDICT] OK")
    print(f"[CURRENT] {snapshot.get('current_work', {}).get('title')}")
  return 0


def cmd_side_track_stack(args):
  """side-track-stack サブコマンドのエントリポイント（Req 14）"""
  if args.side_track_stack_command == "current":
    response = current_side_track_stack(args.path)
    if args.json:
      print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
      print(f"[VERDICT] {response.get('verdict')}")
      print(f"[FRAMES] {len(response.get('stack', {}).get('frames', []))}")
    return 0 if response.get("verdict") == "OK" else 2
  return 2


def cmd_prompt_audit(args):
  """prompt-audit サブコマンドのエントリポイント（Req 15）"""
  action_dict = {
    "subcommand": "prompt-audit",
    "args": {
      "prompt_manifest": args.prompt_manifest,
    },
  }
  try:
    manifest = load_prompt_manifest(args.prompt_manifest)
  except (OSError, yaml.YAMLError, ValueError) as e:
    reasons = [f"prompt_manifest を読めません: {e}"]
    current_state = {"prompt_manifest": args.prompt_manifest}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state))
    else:
      print(format_human_output("DEVIATION", 2, "prompt-audit", reasons, json.dumps(current_state)))
    return 2

  result = audit_manifest(manifest)
  if args.json:
    print(
      format_json_output(
        result["verdict"],
        result["exit_code"],
        action_dict,
        result["reasons"],
        result["current_state"],
      )
    )
  else:
    print(
      format_human_output(
        result["verdict"],
        result["exit_code"],
        "prompt-audit",
        result["reasons"],
        json.dumps(result["current_state"], ensure_ascii=False, indent=2),
      )
    )
  return result["exit_code"]


def cmd_implementation_phase_check(args):
  """implementation phase plan を read-only で検査する（Req 16）"""
  action_dict = {
    "subcommand": "implementation-phase-check",
    "args": {
      "feature": args.feature,
    },
  }
  try:
    plan = load_plan(Path.cwd())
  except (OSError, yaml.YAMLError, ValueError) as e:
    reasons = [f"implementation phase plan を読めません: {e}"]
    current_state = {"feature": args.feature}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state))
    else:
      print(format_human_output("DEVIATION", 2, "implementation-phase-check", reasons, json.dumps(current_state)))
    return 2
  result = check_phase_plan(plan, feature=args.feature)
  if args.json:
    print(
      format_json_output(
        result["verdict"],
        result["exit_code"],
        action_dict,
        result["reasons"],
        result["current_state"],
      )
    )
  else:
    print(
      format_human_output(
        result["verdict"],
        result["exit_code"],
        "implementation-phase-check",
        result["reasons"],
        json.dumps(result["current_state"], ensure_ascii=False, indent=2),
      )
    )
  return result["exit_code"]


def cmd_operation_list(args):
  """operation contracts を read-only 一覧として返す（Req 16）"""
  result = build_operation_list(Path.cwd())
  if args.json:
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {result.get('verdict')}")
    print(f"[OPERATIONS] {len(result.get('operations', []))}")
  return result.get("exit_code", 2)


def cmd_proxy_triage_decision_check(args):
  """proxy triage decision を read-only で検査する（Req 16）"""
  action_dict = {
    "subcommand": "proxy-triage-decision-check",
    "args": {
      "run": args.run,
    },
  }
  try:
    decision = load_proxy_triage_decision(args.run)
  except (OSError, yaml.YAMLError, ValueError) as e:
    reasons = [f"proxy triage decision を読めません: {e}"]
    current_state = {"run": args.run}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state))
    else:
      print(format_human_output("DEVIATION", 2, "proxy-triage-decision-check", reasons, json.dumps(current_state)))
    return 2
  result = check_proxy_triage_decision(decision)
  if args.json:
    print(
      format_json_output(
        result["verdict"],
        result["exit_code"],
        action_dict,
        result["reasons"],
        result["current_state"],
      )
    )
  else:
    print(
      format_human_output(
        result["verdict"],
        result["exit_code"],
        "proxy-triage-decision-check",
        result["reasons"],
        json.dumps(result["current_state"], ensure_ascii=False, indent=2),
      )
    )
  return result["exit_code"]


def main():
  # 共通オプション（サブコマンドの前後どちらでも受け取れるよう親パーサに集約、仕様 §4 共通オプション）
  common_parser = argparse.ArgumentParser(add_help=False)
  common_parser.add_argument(
    "--json",
    action="store_true",
    help="出力を JSON 形式に切り替える（仕様 §7.3）",
  )
  common_parser.add_argument(
    "--log-path",
    default=None,
    help=f"ログ書き出し先の上書き（既定 {DEFAULT_LOG_PATH}、仕様 §8.2）",
  )

  parser = argparse.ArgumentParser(
    description=(
      "ワークフロー事前検査スクリプト（補助層 C 段階 2、"
      "仕様 docs/operations/WORKFLOW_PRECHECK.md）"
    ),
    parents=[common_parser],
  )

  sub = parser.add_subparsers(dest="subcommand", required=True)

  # spec-set サブコマンド（仕様 §5.1）
  ss = sub.add_parser(
    "spec-set",
    help="workflow_state の変更を判定する",
    parents=[common_parser],
  )
  ss.add_argument("feature", help="対象機能名（例：foundation／runtime／…）")
  ss.add_argument("phase", help="対象フェーズ（intent／feature-partitioning／requirements 等）")
  ss.add_argument("stage", help="対象段（drafting／triad-review／review-wave／alignment／approval 等）")
  ss.add_argument("new_value", help="設定したい新しい真偽値（true または false）")
  ss.add_argument(
    "--rationale",
    default=None,
    help="この変更を行う理由（任意、ログ記録用、仕様 §5.1）",
  )

  # commit サブコマンド（仕様 §5.2）
  cs = sub.add_parser(
    "commit",
    help="git commit の事前検査を行う",
    parents=[common_parser],
  )
  cs.add_argument(
    "--rationale",
    required=True,
    help="このコミットを行う理由（必須、利用者承認の出典を含めることを推奨、仕様 §5.2）",
  )
  cs.add_argument(
    "--execution-actor",
    choices=["llm", "human"],
    default="llm",
    help=(
      "commit 実行主体。llm の場合は commit 内容承認とは別に "
      "commit-execution-delegation が必要"
    ),
  )

  sub.add_parser(
    "commit-preflight",
    help="commit 指示直後に stage / approval 作成可否を read-only 判定する",
    parents=[common_parser],
  )

  # push サブコマンド（仕様 §5.3）
  ps = sub.add_parser(
    "push",
    help="git push の事前検査を行う",
    parents=[common_parser],
  )
  ps.add_argument(
    "--rationale",
    required=True,
    help="この push を行う理由（必須、利用者承認の出典を含めることを推奨、仕様 §5.3）",
  )

  st = sub.add_parser(
    "stage",
    help="進行中セッション記録を除外して git add する",
    parents=[common_parser],
  )
  st.add_argument(
    "paths",
    nargs="*",
    default=["."],
    help="stage 対象 pathspec（省略時は .）",
  )

  ap = sub.add_parser(
    "autonomous-plan",
    help="自律・並列モード実行計画の事前検査を行う",
    parents=[common_parser],
  )
  ap.add_argument("plan_path", help="検査対象の自律・並列モード実行計画 YAML")

  apt = sub.add_parser(
    "autonomous-plan-template",
    help="自律・並列モード実行計画のテンプレートを書き出す",
    parents=[common_parser],
  )
  apt.add_argument("--run-id", required=True, help="実行計画の run_id")
  apt.add_argument("--out", required=True, help="テンプレート YAML の出力先")

  apr = sub.add_parser(
    "autonomous-plan-record-integration",
    help="自律・並列モード台帳へ統合結果を追記する",
    parents=[common_parser],
  )
  apr.add_argument("--ledger", required=True, help="更新対象の履歴台帳 YAML")
  apr.add_argument("--status", required=True, help="統合結果 completed / blocked / rejected")
  apr.add_argument("--tests", required=True, help="実行したテストまたは未実行理由")
  apr.add_argument("--decision", required=True, help="統合判断の要約")

  ala = sub.add_parser(
    "autonomous-ledger-audit",
    help="自律・並列モード台帳を plan なしで監査する",
    parents=[common_parser],
  )
  ala.add_argument("ledger_path", help="監査対象の自律・並列モード履歴台帳 YAML")

  ac = sub.add_parser(
    "audit-commit",
    help="指定 commit の post-write-verification 漏れを監査する",
    parents=[common_parser],
  )
  ac.add_argument("commitish", help="監査対象 commit（例：HEAD）")

  sub.add_parser(
    "next",
    help="現在の workflow_state から次に許可される作業を返す",
    parents=[common_parser],
  )

  opp = sub.add_parser(
    "operation-prompt",
    help="不可逆操作直前に読む操作カードと effective prompt を返す",
    parents=[common_parser],
  )
  opp.add_argument(
    "operation",
    choices=["commit"],
    help="対象操作",
  )

  rs = sub.add_parser(
    "reopen-start",
    help="reopen classification から in-progress ファイルを生成する",
    parents=[common_parser],
  )
  rs.add_argument("--classification", required=True, help="手戻り種別（例：D-1）")
  rs.add_argument("--feature", required=True, help="対象 feature 名")
  rs.add_argument("--basis", required=True, help="種別判定根拠ファイル")
  rs.add_argument("--date", required=True, help="in-progress ファイル名に使う日付（YYYY-MM-DD）")
  rs.add_argument("--trigger", required=True, help="reopen 起動理由")

  ras = sub.add_parser(
    "reopen-advance-step",
    help="reopen 第1・第2過程の完了更新を機械処理する",
    parents=[common_parser],
  )
  ras.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
  ras.add_argument("--from-step", required=True, choices=["1", "2"], help="完了扱いにする reopen 過程番号")
  ras.add_argument("--completed-step", required=True, help="completed_steps に追加する説明")
  ras.add_argument("--rationale", required=True, help="判断理由")
  ras.add_argument("--evidence", action="append", default=[], help="判断証跡。複数指定可")

  raac = sub.add_parser(
    "reopen-advance-after-commit-stop-point",
    help="reopen 停止点 commit 後に commit_stop_point を消費する",
    parents=[common_parser],
  )
  raac.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
  raac.add_argument("--head", required=True, help="停止点 commit の HEAD commit")
  raac.add_argument("--kind", required=True, help="消費対象の commit_stop_point_kind")
  raac.add_argument("--evidence", action="append", default=[], help="判断証跡。複数指定可")

  rag = sub.add_parser(
    "reopen-advance-gate",
    help="reopen 第3過程の pending gate 完了更新を機械処理する",
    parents=[common_parser],
  )
  rag.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
  rag.add_argument("--gate", required=True, help="完了する gate（例: stages/design.yaml#alignment）")
  rag.add_argument("--decision", required=True, help="downstream_impact_decisions に記録する decision")
  rag.add_argument("--feature-scope", required=True, help="downstream_impact_decisions に記録する feature_scope")
  rag.add_argument("--rationale", required=True, help="判断理由")
  rag.add_argument("--evidence", action="append", default=[], help="判断証跡。複数指定可")
  rag.add_argument("--completed-step", default=None, help="completed_steps に追加する説明")
  rag.add_argument(
    "--set-spec",
    nargs=4,
    metavar=("FEATURE", "PHASE", "STAGE", "VALUE"),
    help="spec.json の workflow_state を同時更新する",
  )

  rsb = sub.add_parser(
    "reopen-set-blocker",
    help="reopen 第3過程の approval 承認待ち blocker を構造化して設定する",
    parents=[common_parser],
  )
  rsb.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
  rsb.add_argument("--gate", required=True, help="承認待ちにする gate（例: stages/design.yaml#approval）")
  rsb.add_argument("--actor", required=True, choices=["human", "proxy_model"], help="承認主体")
  rsb.add_argument("--rationale", required=True, help="判断理由")
  rsb.add_argument("--evidence", action="append", default=[], help="判断証跡。複数指定可")

  rhd = sub.add_parser(
    "record-human-decision",
    help="approval gate の人間判断 record を保存する",
    parents=[common_parser],
  )
  rhd.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
  rhd.add_argument("--gate", required=True, help="判断対象 gate（例: stages/design.yaml#approval）")
  rhd.add_argument("--decision-id", required=True, help="approval gate decision id")
  rhd.add_argument(
    "--decision",
    required=True,
    choices=["approved", "rejected", "deferred", "changes_requested"],
    help="記録する判断",
  )
  rhd.add_argument(
    "--decision-scope",
    required=True,
    choices=["human_only", "proxy_allowed", "advisory_only"],
    help="判断境界",
  )
  rhd.add_argument("--target-operation-id", required=True, help="判断対象 operation_id")
  rhd.add_argument("--target-required-action", required=True, help="判断対象 required_action")
  rhd.add_argument("--target-artifact", required=True, help="判断対象 artifact")
  rhd.add_argument("--target-artifact-digest", default=None, help="判断対象 artifact digest")
  rhd.add_argument("--staged-file-set-digest", default=None, help="判断対象 staged file set digest")
  rhd.add_argument(
    "--binding-kind",
    required=True,
    choices=["artifact_digest", "staged_file_set_digest", "both", "none"],
    help="判断 record の束縛種別",
  )
  rhd.add_argument(
    "--decided-by",
    required=True,
    choices=["user", "human", "proxy_model", "llm"],
    help="判断主体",
  )
  rhd.add_argument("--decided-at", required=True, help="判断時刻")
  rhd.add_argument("--source-ref", required=True, help="判断出典")
  rhd.add_argument("--source-digest", required=True, help="判断出典 digest")
  rhd.add_argument("--rationale", required=True, help="判断理由")
  rhd.add_argument("--next-action-expectation", required=True, help="次 action 期待")
  rhd.add_argument("--out", default=None, help="保存先 approval record path")

  rf = sub.add_parser(
    "reopen-finalize",
    help="reopen 第4過程の完了 YAML 生成と completed 移動を機械処理する",
    parents=[common_parser],
  )
  rf.add_argument("--file", required=True, help="完了対象の reopen in-progress YAML")
  rf.add_argument(
    "--impacted-downstream-phase",
    action="append",
    default=[],
    help="impacted_downstream_phases に記録する phase。複数指定可",
  )
  rf.add_argument(
    "--feature-impact",
    nargs=5,
    action="append",
    metavar=("FEATURE", "DECISION", "IMPACT_BASIS", "RATIONALE", "EVIDENCE"),
    default=[],
    help="feature_impact_decisions に追加する判定。既存 feature ごとに指定する",
  )
  rf.add_argument(
    "--new-feature-decision",
    nargs=3,
    required=True,
    metavar=("DECISION", "RATIONALE", "EVIDENCE"),
    help="new_feature_decision に記録する判定",
  )
  rf.add_argument("--completed-step", default=None, help="completed_steps に追加する説明")

  rws = sub.add_parser(
    "review-wave-summary",
    help="review-wave 横断確認の指標を集計して出力する（Req 10）",
    parents=[common_parser],
  )
  rws.add_argument("--out", default=None, help="要約出力の書き出し先パス（自身の出力のみ。状態は書き換えない）")
  rws.add_argument(
    "--save",
    action="store_true",
    help="既定保存先 .reviewcompass/specs/_cross_feature/reviews/ へ書き出す",
  )

  opf = sub.add_parser(
    "operation-preflight",
    help="operation registry に基づく read-only preflight を行う（Req 12）",
    parents=[common_parser],
  )
  opf.add_argument("--operation-id", required=True, help="preflight 対象の operation_id")

  sub.add_parser(
    "operation-contract-check",
    help="operation contract と required_action / registry 参照の整合を検査する（Req 13）",
    parents=[common_parser],
  )

  sub.add_parser(
    "workflow-snapshot",
    help="現在の workflow-state snapshot を read-only で出力する（Req 14）",
    parents=[common_parser],
  )

  sts = sub.add_parser(
    "side-track-stack",
    help="side track stack を操作する（Req 14）",
  )
  sts_sub = sts.add_subparsers(
    dest="side_track_stack_command",
    required=True,
  )
  sts_current = sts_sub.add_parser(
    "current",
    help="side track stack の現在値を read-only で出力する",
    parents=[common_parser],
  )
  sts_current.add_argument(
    "--path",
    default=None,
    help="side track stack YAML のパス（省略時は既定位置）",
  )

  pa = sub.add_parser(
    "prompt-audit",
    help="effective prompt manifest を read-only で監査する（Req 15）",
    parents=[common_parser],
  )
  pa.add_argument("--prompt-manifest", required=True, help="監査対象 manifest YAML/JSON")

  ipc = sub.add_parser(
    "implementation-phase-check",
    help="workflow-management implementation phase plan を read-only で検査する（Req 16）",
    parents=[common_parser],
  )
  ipc.add_argument("--feature", required=True, help="検査対象 feature")

  sub.add_parser(
    "operation-list",
    help="operation contract を read-only registry として出力する（Req 16）",
    parents=[common_parser],
  )

  ptd = sub.add_parser(
    "proxy-triage-decision-check",
    help="proxy triage decision の構造と coverage を read-only で検査する（Req 16）",
    parents=[common_parser],
  )
  ptd.add_argument("--run", required=True, help="proxy-triage-decision.yaml を含む review-run dir")

  cap = sub.add_parser(
    "commit-approval",
    help="commit 承認 nonce challenge を作成・記録・無効化する",
  )
  cap_sub = cap.add_subparsers(
    dest="commit_approval_command",
    required=True,
  )
  cap_prepare = cap_sub.add_parser("prepare", help="staged 内容に束縛した challenge を作成する")
  cap_prepare.add_argument("--json", action="store_true", help="JSON のみを出力する")
  cap_record = cap_sub.add_parser("record", help="nonce に対応する承認レコードを保存する")
  cap_record.add_argument("--nonce", required=True, help="prepare が出力した nonce")
  source_group = cap_record.add_mutually_exclusive_group(required=True)
  source_group.add_argument(
    "--source-text-stdin",
    action="store_true",
    help="承認本文を TTY stdin から読み、redaction 後に保存する",
  )
  source_group.add_argument(
    "--no-source-text",
    action="store_true",
    help="承認本文を保存しない no-store mode",
  )
  cap_record.add_argument("--json", action="store_true", help="JSON のみを出力する")
  cap_delegate = cap_sub.add_parser(
    "delegate-execution",
    help="nonce に対応する commit 実行代行承認を別レコードに保存する",
  )
  cap_delegate.add_argument("--nonce", required=True, help="prepare が出力した nonce")
  cap_delegate.add_argument(
    "--source-text-stdin",
    action="store_true",
    required=True,
    help="実行代行承認の明示文言を TTY stdin から読む",
  )
  cap_delegate.add_argument("--json", action="store_true", help="JSON のみを出力する")
  cap_invalidate = cap_sub.add_parser("invalidate", help="challenge と承認レコードを無効化する")
  cap_invalidate.add_argument("--json", action="store_true", help="JSON のみを出力する")

  # decision-source-lint サブコマンド（Req 11）
  dsl = sub.add_parser(
    "decision-source-lint",
    help="重要決定の出典検査を行う（Req 11）",
    parents=[common_parser],
  )
  dsl_group = dsl.add_mutually_exclusive_group()
  dsl_group.add_argument(
    "--all",
    dest="all_decisions",
    action="store_true",
    default=False,
    help="decisions/ 直下の全決定記録を検査する（bundle-exceptions/ は除外）",
  )
  dsl_group.add_argument(
    "--verify-pending",
    dest="verify_pending",
    action="store_true",
    default=False,
    help="verification_status: pending の決定を再照合し、合格すれば verified に更新する",
  )
  dsl_group.add_argument(
    "decision_file",
    nargs="?",
    default=None,
    help="指定ファイルのみ検査（省略または --all で全件検査）",
  )

  args = parser.parse_args()

  if args.subcommand == "spec-set":
    sys.exit(cmd_spec_set(args))
  elif args.subcommand == "stage":
    sys.exit(cmd_stage(args))
  elif args.subcommand == "commit":
    sys.exit(cmd_commit(args))
  elif args.subcommand == "commit-preflight":
    sys.exit(cmd_commit_preflight(args))
  elif args.subcommand == "push":
    sys.exit(cmd_push(args))
  elif args.subcommand == "autonomous-plan":
    sys.exit(cmd_autonomous_plan(args))
  elif args.subcommand == "autonomous-plan-template":
    sys.exit(cmd_autonomous_plan_template(args))
  elif args.subcommand == "autonomous-plan-record-integration":
    sys.exit(cmd_autonomous_plan_record_integration(args))
  elif args.subcommand == "autonomous-ledger-audit":
    sys.exit(cmd_autonomous_ledger_audit(args))
  elif args.subcommand == "audit-commit":
    sys.exit(cmd_audit_commit(args))
  elif args.subcommand == "next":
    sys.exit(cmd_next(args))
  elif args.subcommand == "operation-prompt":
    sys.exit(cmd_operation_prompt(args))
  elif args.subcommand == "reopen-start":
    sys.exit(cmd_reopen_start(args))
  elif args.subcommand == "reopen-advance-step":
    sys.exit(cmd_reopen_advance_step(args))
  elif args.subcommand == "reopen-advance-after-commit-stop-point":
    sys.exit(cmd_reopen_advance_after_commit_stop_point(args))
  elif args.subcommand == "reopen-advance-gate":
    sys.exit(cmd_reopen_advance_gate(args))
  elif args.subcommand == "reopen-set-blocker":
    sys.exit(cmd_reopen_set_blocker(args))
  elif args.subcommand == "record-human-decision":
    sys.exit(cmd_record_human_decision(args))
  elif args.subcommand == "reopen-finalize":
    sys.exit(cmd_reopen_finalize(args))
  elif args.subcommand == "review-wave-summary":
    sys.exit(cmd_review_wave_summary(args))
  elif args.subcommand == "operation-preflight":
    sys.exit(cmd_operation_preflight(args))
  elif args.subcommand == "operation-contract-check":
    sys.exit(cmd_operation_contract_check(args))
  elif args.subcommand == "workflow-snapshot":
    sys.exit(cmd_workflow_snapshot(args))
  elif args.subcommand == "side-track-stack":
    sys.exit(cmd_side_track_stack(args))
  elif args.subcommand == "prompt-audit":
    sys.exit(cmd_prompt_audit(args))
  elif args.subcommand == "implementation-phase-check":
    sys.exit(cmd_implementation_phase_check(args))
  elif args.subcommand == "operation-list":
    sys.exit(cmd_operation_list(args))
  elif args.subcommand == "proxy-triage-decision-check":
    sys.exit(cmd_proxy_triage_decision_check(args))
  elif args.subcommand == "commit-approval":
    sys.exit(cmd_commit_approval(args))
  elif args.subcommand == "decision-source-lint":
    sys.exit(cmd_decision_source_lint(args))
  else:
    parser.print_help(sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
  main()


## tools/check_workflow_action/effective_prompt_builder.py

"""Structured effective prompt manifest の生成補助。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def sha256_file(path: str | Path) -> str:
  """ファイル内容の sha256 を `sha256:<hex>` 形式で返す。"""
  return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_artifact(path: str | Path) -> Dict[str, str]:
  """manifest.source_artifacts の 1 要素を作る。"""
  return {
    "path": str(path),
    "sha256": sha256_file(path),
  }


def build_manifest(
  *,
  decision_point: Dict[str, Any],
  source_artifacts: Iterable[Dict[str, Any]],
  required_disciplines: List[str],
  operation_contract: Dict[str, Any],
  expected_output_schema: Dict[str, Any],
  prompt_length: Dict[str, Any],
  preconditions_checked: List[Dict[str, Any]],
  language_task: Dict[str, Any],
  postconditions: List[Dict[str, Any]],
  on_completion: Dict[str, Any],
  schema_version: str = "effective-prompt-manifest-v1",
  extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  """effective prompt manifest の正本語彙を 1 つの mapping にまとめる。"""
  manifest: Dict[str, Any] = {
    "schema_version": schema_version,
    "decision_point": decision_point,
    "source_artifacts": list(source_artifacts),
    "required_disciplines": required_disciplines,
    "operation_contract": operation_contract,
    "expected_output_schema": expected_output_schema,
    "prompt_length": prompt_length,
    "preconditions_checked": preconditions_checked,
    "language_task": language_task,
    "postconditions": postconditions,
    "on_completion": on_completion,
  }
  if extra:
    manifest.update(extra)
  return manifest


## tools/check_workflow_action/prompt_audit.py

"""Effective prompt manifest の read-only 監査。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


MACHINE_ACTION_TERMS = (
  "execute operation",
  "consume approval gate",
  "mutate side-track stack",
  "mutate side track stack",
  "create review-run artifacts",
  "create review run artifacts",
  "git commit",
  "git push",
  "spec-set",
)

STATE_MUTATION_TERMS = (
  "mutate workflow state",
  "update workflow state",
  "write spec.json",
  "spec.json を更新",
  "workflow_state を更新",
)

DIRECT_FOLLOWUP_TERMS = (
  "commit",
  "push",
  "spec-set",
  "spec.json を更新",
)

NEGATION_PREFIXES = (
  "do not ",
  "don't ",
  "never ",
  "no ",
  "禁止",
)


def load_manifest(path: str | Path) -> Dict[str, Any]:
  """YAML/JSON manifest を mapping として読む。"""
  with Path(path).open(encoding="utf-8") as f:
    data = yaml.safe_load(f)
  if not isinstance(data, dict):
    raise ValueError("prompt manifest は YAML mapping である必要があります")
  return data


def audit_manifest(
  manifest: Dict[str, Any],
  *,
  current_next_action: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  """manifest が言語判断用の範囲を越えていないかを判定する。"""
  reasons: List[str] = []
  _audit_language_task(manifest.get("language_task"), reasons)
  _audit_on_completion(manifest.get("on_completion"), reasons, current_next_action)
  verdict = "OK" if not reasons else "DEVIATION"
  return {
    "verdict": verdict,
    "exit_code": 0 if verdict == "OK" else 2,
    "reasons": reasons,
    "current_state": {
      "schema_version": manifest.get("schema_version"),
      "decision_point": manifest.get("decision_point"),
      "on_completion": manifest.get("on_completion"),
    },
  }


def _audit_language_task(language_task: Any, reasons: List[str]) -> None:
  if not isinstance(language_task, dict):
    reasons.append("language_task が mapping ではありません")
    return
  constraints = language_task.get("constraints")
  if not isinstance(constraints, list):
    reasons.append("language_task.constraints が list ではありません")
    return
  for constraint in constraints:
    if not isinstance(constraint, str):
      reasons.append("language_task.constraints は文字列である必要があります")
      continue
    text = _normalized(constraint)
    if _is_negative_constraint(text):
      continue
    if _contains_any(text, MACHINE_ACTION_TERMS) or _contains_any(text, STATE_MUTATION_TERMS):
      reasons.append(
        "language_task.constraints に machine/state mutation instruction が含まれています"
      )
      return


def _audit_on_completion(
  on_completion: Any,
  reasons: List[str],
  current_next_action: Optional[Dict[str, Any]],
) -> None:
  if not isinstance(on_completion, dict):
    reasons.append("on_completion が mapping ではありません")
    return

  allowed_followups = on_completion.get("allowed_followups")
  forbidden_actions = on_completion.get("forbidden_actions")
  if not isinstance(allowed_followups, list) or not isinstance(forbidden_actions, list):
    reasons.append("on_completion allowed_followups/forbidden_actions が list ではありません")
    return

  allowed_texts = [str(value) for value in allowed_followups]
  forbidden_texts = [str(value) for value in forbidden_actions]
  if any(_contains_any(_normalized(value), DIRECT_FOLLOWUP_TERMS) for value in allowed_texts):
    reasons.append("on_completion.allowed_followups に直接操作指示が含まれています")

  normalized_allowed = {_normalized(value) for value in allowed_texts}
  normalized_forbidden = {_normalized(value) for value in forbidden_texts}
  overlap = sorted(normalized_allowed & normalized_forbidden)
  if overlap:
    reasons.append(
      "on_completion allowed_followups と forbidden_actions が矛盾しています: "
      + ", ".join(overlap)
    )

  if current_next_action is None:
    return
  expected = current_next_action.get("required_action")
  actual = on_completion.get("next_required_action")
  if expected and actual != expected:
    reasons.append(
      "on_completion.next_required_action が next_action_compatible ではありません"
    )


def _normalized(value: str) -> str:
  return " ".join(value.lower().split())


def _is_negative_constraint(text: str) -> bool:
  return any(text.startswith(prefix) for prefix in NEGATION_PREFIXES)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
  return any(term in text for term in terms)


## tools/api_providers/run_role.py

"""tools/api_providers/run_role.py

API 経路で 1 役を 1 回実行し、結果を保存する。
出力先がない場合は標準出力に YAML を返す。任意指定の出力先がある場合は
raw / parsed / review-run 成果物を保存し、正常系 human output は 1 行に抑える。
計画書 §5.9.7.1（入出力契約）と §5.23.12.3（プロンプト雛形はフェーズ 4 で整備）を参照。
"""
import argparse
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 直接実行（python3 tools/api_providers/run_role.py）にも import 経由にも対応する。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers.config_loader import (  # noqa: E402
  load_config,
  resolve_connection_settings,
  resolve_default_variant_name,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import (  # noqa: E402
  enable_zshrc_api_key_fallback,
  get_provider,
)
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_data,
)
from tools.normal_output import status_line  # noqa: E402


_PROMPT_TEMPLATE_DIR = Path(__file__).resolve().parent / "prompt_templates"
_PROVIDER_PROMPT_TEMPLATES = {
  "anthropic-api": "anthropic_review.md",
  "openai-api": "openai_review.md",
  "gemini-api": "gemini_review.md",
}


def _render_prompt_template(template: str, values: Dict[str, str]) -> str:
  """元テンプレート上の placeholder だけを 1 回置換する。"""
  pattern = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")

  def replace(match: re.Match) -> str:
    key = match.group(1)
    return values.get(key, match.group(0))

  return pattern.sub(replace, template)


def _select_prompt_template(provider_name: Optional[str]) -> Tuple[str, str]:
  """provider に応じたプロンプトテンプレート ID と本文を返す。"""
  template_file = _PROVIDER_PROMPT_TEMPLATES.get(
    provider_name or "",
    "default_review.md",
  )
  template_path = _PROMPT_TEMPLATE_DIR / template_file
  if not template_path.exists():
    template_file = "default_review.md"
    template_path = _PROMPT_TEMPLATE_DIR / template_file
  return template_file.removesuffix(".md"), template_path.read_text(encoding="utf-8")


def _normalize_target_paths(target_paths: Any) -> List[str]:
  """単一 target と複数 target の入力を list に正規化する。"""
  if isinstance(target_paths, list):
    return [str(path) for path in target_paths]
  return [str(target_paths)]


def _read_target_content(target_paths: List[str]) -> str:
  """target 群を 1 つの review prompt 用本文へ束ねる。"""
  if len(target_paths) == 1:
    return Path(target_paths[0]).read_text(encoding="utf-8")
  parts = []
  for target_path in target_paths:
    target_content = Path(target_path).read_text(encoding="utf-8")
    parts.append(f"## {target_path}\n\n{target_content}")
  return "\n\n".join(parts)


def _target_file_entries(target_paths: List[str]) -> List[Dict[str, str]]:
  """review-run の target_files entry 群を作る。"""
  return [
    {
      "path": target_path,
      "sha256": _sha256_file(Path(target_path)),
    }
    for target_path in target_paths
  ]


def build_prompt(
  target_path: Any,
  phase: str,
  criteria: str,
  prior_finding_paths: List[str],
  provider_name: Optional[str] = None,
  model: Optional[str] = None,
) -> str:
  """対象ファイル内容・段名・観点・前段所見からプロンプト文字列を組み立てる。

  provider ごとの差異を吸収するため、専用テンプレートがあればそれを使う。
  """
  target_paths = _normalize_target_paths(target_path)
  target_content = _read_target_content(target_paths)
  prior_parts = []
  for i, prior_path in enumerate(prior_finding_paths, start=1):
    prior_content = Path(prior_path).read_text(encoding="utf-8")
    prior_parts.append(f"# 前段所見 {i}：\n{prior_content}")

  prompt_id, template = _select_prompt_template(provider_name)
  return _render_prompt_template(
    template,
    {
      "prompt_id": prompt_id,
      "provider_name": provider_name or "unknown-provider",
      "model": model or "unknown-model",
      "phase": phase,
      "criteria": criteria,
      "target_path": "\n".join(target_paths),
      "target_content": target_content,
      "prior_findings": "\n\n".join(prior_parts) if prior_parts else "なし",
    },
  )


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  """プロバイダーを呼び出し、レスポンス文字列・attempts・所要時間を返す。

  send_request 内部のリトライは内側で処理されるため、本層では attempts=1 と記録する。
  詳細な attempts 計測はサブサイクル 4 完成後の改良対象。
  """
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  duration = time.monotonic() - start
  return response_text, 1, duration


def _sha256_text(value: str) -> str:
  """文字列の sha256 を返す。"""
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
  """ファイル内容の sha256 を返す。"""
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_text(path: Path, content: str) -> None:
  """親ディレクトリを作って UTF-8 テキストを書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  """YAML dict を読み込む。存在しない場合は空 dict。"""
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  """YAML dict を UTF-8 で書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _safe_artifact_stem(model: str) -> str:
  """モデル ID を artifact ファイル名に使える最小表記へ変換する。"""
  safe_chars = []
  for char in model:
    if char.isalnum() or char in (".", "-", "_"):
      safe_chars.append(char)
    else:
      safe_chars.append("-")
  return "".join(safe_chars).strip("-") or "model"


def _write_raw_response(raw_out: Optional[str], response_text: str) -> Optional[str]:
  """明示 raw-out があれば provider 生応答を保存し sha256 を返す。"""
  if not raw_out:
    return None
  path = Path(raw_out)
  _write_text(path, response_text)
  return _sha256_file(path)


def _write_parsed_response(parsed_out: Optional[str], formatted_output: str) -> Optional[str]:
  """明示 parsed-out があれば整形済み YAML を保存し sha256 を返す。"""
  if not parsed_out:
    return None
  path = Path(parsed_out)
  _write_text(path, formatted_output)
  return _sha256_file(path)


def _relative_to_run(run_dir: Path, path: Path) -> str:
  """review-run ディレクトリからの相対パスを返す。"""
  try:
    return str(path.relative_to(run_dir))
  except ValueError:
    return str(path)


def _severity_counts(findings: Optional[List[Dict[str, Any]]]) -> Dict[str, int]:
  """所見重大度ごとの件数を返す。"""
  counts: Dict[str, int] = {}
  for finding in findings or []:
    if not isinstance(finding, dict):
      continue
    severity = finding.get("severity") or "UNKNOWN"
    counts[str(severity)] = counts.get(str(severity), 0) + 1
  return counts


def _upsert_by_keys(items: List[Dict[str, Any]], new_item: Dict[str, Any], keys: List[str]) -> None:
  """keys が一致する既存 dict を置き換え、なければ追加する。"""
  for index, item in enumerate(items):
    if all(item.get(key) == new_item.get(key) for key in keys):
      items[index] = new_item
      return
  items.append(new_item)


def update_review_run_artifacts(
  review_run_dir: str,
  *,
  round_id: str,
  target_path: Any,
  phase: str,
  criteria: str,
  role: str,
  provider: str,
  model: str,
  prompt: str,
  response_text: str,
  attempts: int,
  duration_seconds: float,
  parse_status: str,
  findings: Optional[List[Dict[str, Any]]],
  formatted_output: Optional[str],
  effective_prompt_path: Optional[str] = None,
  effective_prompt_sha256: Optional[str] = None,
  prompt_manifest_path: Optional[str] = None,
  prompt_manifest_sha256: Optional[str] = None,
  criteria_source_path: Optional[str] = None,
  criteria_source_sha256: Optional[str] = None,
) -> None:
  """1 回の API 応答を review-run 成果物へ反映する。"""
  run_dir = Path(review_run_dir)
  raw_dir = run_dir / "raw"
  parsed_dir = run_dir / "parsed"
  prompt_dir = run_dir / "prompts"
  model_stem = _safe_artifact_stem(model)
  raw_path = raw_dir / f"{model_stem}.{round_id}.txt"
  parsed_path = parsed_dir / f"{model_stem}.{round_id}.yaml"
  prompt_path = prompt_dir / f"{model_stem}.{round_id}.prompt.md"

  _write_text(prompt_path, prompt)
  prompt_sha256 = _sha256_file(prompt_path)
  _write_text(raw_path, response_text)
  raw_sha256 = _sha256_file(raw_path)
  parsed_sha256 = None
  if formatted_output is not None:
    _write_text(parsed_path, formatted_output)
    parsed_sha256 = _sha256_file(parsed_path)

  target_paths = _normalize_target_paths(target_path)
  target_files = _target_file_entries(target_paths)
  now = datetime.now(timezone.utc).isoformat()

  _dump_yaml(
    run_dir / "target-manifest.yaml",
    {
      "run_id": run_dir.name,
      "target_files": target_files,
    },
  )

  rounds_path = run_dir / "rounds.yaml"
  rounds = _load_yaml_dict(rounds_path)
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  model_result = {
    "model_id": model,
    "provider": provider,
    "role": role,
    "treatment": role,
    "invocation_path": "api",
    "raw_path": _relative_to_run(run_dir, raw_path),
    "raw_sha256": raw_sha256,
    "parsed_path": _relative_to_run(run_dir, parsed_path) if formatted_output is not None else None,
    "parsed_sha256": parsed_sha256,
    "parse_status": parse_status,
    "formatted_by": "parser",
    "formatted_by_actor_type": "orchestrator",
    "formatted_by_actor": "run_role.py",
    "formatted_at": now,
    "follow_up_action": "triage" if parse_status == "parsed" else "format_pending",
    "attempts": attempts,
    "duration_seconds": round(duration_seconds, 3),
    "prompt_path": _relative_to_run(run_dir, prompt_path),
    "prompt_sha256": prompt_sha256,
  }
  _upsert_by_keys(model_results, model_result, ["model_id", "role"])

  rounds_update = {
    "round_id": round_id,
    "purpose": phase,
    "invocation_timestamp": now,
    "target_files": target_files,
    "criteria": criteria,
    "prompt_sha256": prompt_sha256,
    "model_results": model_results,
  }
  if criteria_source_path:
    rounds_update["criteria_source_path"] = criteria_source_path
  if criteria_source_sha256:
    rounds_update["criteria_source_sha256"] = criteria_source_sha256
  if effective_prompt_path:
    rounds_update["effective_prompt_path"] = effective_prompt_path
  if effective_prompt_sha256:
    rounds_update["effective_prompt_sha256"] = effective_prompt_sha256
  if prompt_manifest_path:
    rounds_update["prompt_manifest_path"] = prompt_manifest_path
  if prompt_manifest_sha256:
    rounds_update["prompt_manifest_sha256"] = prompt_manifest_sha256
  rounds.update(rounds_update)
  _dump_yaml(rounds_path, rounds)

  summary_path = run_dir / "model-result-summary.yaml"
  summary = _load_yaml_dict(summary_path)
  summary_models = summary.get("models")
  if not isinstance(summary_models, list):
    summary_models = []
  findings_count = len(findings or [])
  summary_model = {
    "model_id": model,
    "raw_path": _relative_to_run(run_dir, raw_path),
    "parse_status": parse_status,
    "triage_status": "no_findings" if parse_status == "parsed" and findings_count == 0 else "triage_pending",
    "findings_count": findings_count,
    "findings_count_by_severity": _severity_counts(findings),
    "must_fix_count": 0,
    "should_fix_count": 0,
    "leave_as_is_count": 0,
    "human_required_count": 0,
  }
  _upsert_by_keys(summary_models, summary_model, ["model_id"])
  summary.update({
    "run_id": run_dir.name,
    "models": summary_models,
  })
  _dump_yaml(summary_path, summary)


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  """引数解析。計画書 §5.9.7.1 の長オプション 6 種＋ --config に対応。"""
  parser = argparse.ArgumentParser(
    description="API 経路で 1 役を 1 回実行し、結果を保存する。",
  )
  parser.add_argument(
    "--role",
    required=True,
    choices=["primary", "adversarial", "judgment"],
    help="役名（必須）",
  )
  parser.add_argument(
    "--variant",
    default=None,
    help="variant 名。未指定なら default を使う",
  )
  parser.add_argument(
    "--default-variant-for",
    default=None,
    help="operation_defaults から既定 variant を解決する場面名",
  )
  parser.add_argument(
    "--target",
    required=True,
    action="append",
    help="対象文書ファイルパス（必須）",
  )
  parser.add_argument(
    "--phase",
    required=True,
    help="段名（例：requirements_triad_review、必須）",
  )
  parser.add_argument(
    "--criteria",
    default=None,
    help="観点識別子（例：観点-1、必須）",
  )
  parser.add_argument(
    "--criteria-file",
    default=None,
    help="観点本文を含むファイル。指定時は --criteria の代わりに本文を使う",
  )
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  parser.add_argument(
    "--config",
    default="config/api-settings.yaml",
    help="API 設定ファイルパス（既定 config/api-settings.yaml）",
  )
  parser.add_argument(
    "--raw-out",
    default=None,
    help="provider 生応答の保存先。parse 成否に関係なく保存する",
  )
  parser.add_argument(
    "--parsed-out",
    default=None,
    help="整形済み YAML の保存先。parse 成功時のみ保存する",
  )
  parser.add_argument(
    "--review-run-dir",
    default=None,
    help="review-run 成果物ディレクトリ。raw/parsed/rounds/summary を更新する",
  )
  parser.add_argument(
    "--round-id",
    default="round-1",
    help="review-run に記録する round_id",
  )
  parser.add_argument(
    "--effective-prompt-path",
    default=None,
    help="判定点ごとに生成された effective prompt ファイルのパス",
  )
  parser.add_argument(
    "--effective-prompt-sha256",
    default=None,
    help="effective prompt ファイルの sha256。未指定ならファイルから計算する",
  )
  parser.add_argument(
    "--prompt-manifest-path",
    default=None,
    help="構造化 effective prompt manifest ファイルのパス",
  )
  parser.add_argument(
    "--prompt-manifest-sha256",
    default=None,
    help="prompt manifest ファイルの sha256。未指定ならファイルから計算する",
  )
  parser.add_argument(
    "--verbose",
    action="store_true",
    help="成果物保存先がある場合も整形済み YAML を標準出力へ表示する",
  )
  return parser.parse_args(argv)


def _select_variant_name(config: Dict[str, Any], args: argparse.Namespace) -> Optional[str]:
  """明示 variant または場面別既定から実効 variant 名を返す。"""
  if args.variant and args.default_variant_for:
    raise ValueError("--variant と --default-variant-for は同時に指定できません")
  if args.default_variant_for:
    return resolve_default_variant_name(config, args.default_variant_for)
  return args.variant


def _resolve_criteria(args: argparse.Namespace) -> Tuple[str, Optional[str], Optional[str]]:
  """--criteria / --criteria-file から実効 criteria と出典情報を返す。"""
  if bool(args.criteria) == bool(args.criteria_file):
    raise ValueError("--criteria または --criteria-file のどちらか一方を指定してください")
  if args.criteria_file:
    path = Path(args.criteria_file)
    criteria = path.read_text(encoding="utf-8")
    return criteria, str(path), _sha256_file(path)
  return args.criteria, None, None


def _resolve_effective_prompt_sha256(path_value: Optional[str], sha_value: Optional[str]) -> Optional[str]:
  """effective prompt sha256 を明示値またはファイル内容から返す。

  凍結期（P3 まで）は読み取りを新→旧の順でフォールバックする
  （正本は check_workflow_action/runtime_paths.py）。
  """
  if sha_value:
    return sha_value
  if not path_value:
    return None
  from tools.check_workflow_action.runtime_paths import resolve_effective_prompt_read_path

  resolved = resolve_effective_prompt_read_path(Path.cwd(), path_value)
  path = Path(resolved)
  if not path.is_file():
    return None
  return _sha256_file(path)


def _resolve_prompt_manifest_sha256(path_value: Optional[str], sha_value: Optional[str]) -> Optional[str]:
  """prompt manifest sha256 を明示値またはファイル内容から返す。"""
  if sha_value:
    return sha_value
  if not path_value:
    return None
  path = Path(path_value)
  if not path.is_file():
    return None
  return _sha256_file(path)


def _normal_output_fields(
  args: argparse.Namespace,
  *,
  role: str,
  provider: str,
  model: str,
  findings: List[Dict[str, Any]],
) -> Dict[str, Any]:
  """run_role 成功時の短い human output fields を返す。"""
  run_dir = Path(args.review_run_dir) if args.review_run_dir else None
  safe_model = _safe_artifact_stem(model)
  parsed = args.parsed_out
  raw = args.raw_out
  if run_dir:
    parsed = str(run_dir / "parsed" / f"{safe_model}.{args.round_id}.yaml")
    raw = str(run_dir / "raw" / f"{safe_model}.{args.round_id}.txt")
  return {
    "role": role,
    "provider": provider,
    "model": model,
    "findings": len(findings),
    "review_run_dir": args.review_run_dir,
    "raw": raw,
    "parsed": parsed,
  }


def main(argv: Optional[List[str]] = None) -> int:
  """メイン処理。エラー時は標準エラーに理由を書いて非ゼロを返す。"""
  enable_zshrc_api_key_fallback()
  args = _parse_argv(argv)
  try:
    config = load_config(args.config)
    variant_name = _select_variant_name(config, args)
    variant_config = resolve_variant(config, variant_name)
    role_config = resolve_role(variant_config, args.role)
    connection_defaults = config.get("connection", {})
    connection_settings = resolve_connection_settings(role_config, connection_defaults)

    provider_name = role_config["provider"]
    model = role_config["model"]
    provider_cls = get_provider(provider_name)
    provider = provider_cls(
      model=model,
      timeout_seconds=connection_settings.get("timeout_seconds", 60),
      max_retries=connection_settings.get("max_retries", 1),
    )
    criteria, criteria_source_path, criteria_source_sha256 = _resolve_criteria(args)

    prompt = build_prompt(
      args.target,
      args.phase,
      criteria,
      args.prior_finding,
      provider_name=provider_name,
      model=model,
    )
    effective_prompt_sha256 = _resolve_effective_prompt_sha256(
      args.effective_prompt_path,
      args.effective_prompt_sha256,
    )
    prompt_manifest_sha256 = _resolve_prompt_manifest_sha256(
      args.prompt_manifest_path,
      args.prompt_manifest_sha256,
    )
    response_text, attempts, duration_seconds = _call_provider(provider, prompt)
    _write_raw_response(args.raw_out, response_text)
    try:
      parsed_response = parse_response_data(response_text)
      findings = parsed_response["findings"]
    except Exception:
      if args.review_run_dir:
        update_review_run_artifacts(
          args.review_run_dir,
          round_id=args.round_id,
          target_path=args.target,
          phase=args.phase,
          criteria=criteria,
          role=args.role,
          provider=provider_name,
          model=model,
          prompt=prompt,
          response_text=response_text,
          attempts=attempts,
          duration_seconds=duration_seconds,
          parse_status="parse_failed",
          findings=None,
          formatted_output=None,
          effective_prompt_path=args.effective_prompt_path,
          effective_prompt_sha256=effective_prompt_sha256,
          prompt_manifest_path=args.prompt_manifest_path,
          prompt_manifest_sha256=prompt_manifest_sha256,
          criteria_source_path=criteria_source_path,
          criteria_source_sha256=criteria_source_sha256,
        )
      raise
    extra_fields = {
      key: value
      for key, value in parsed_response.items()
      if key != "findings"
    }
    output = format_response(
      role=args.role,
      provider=provider_name,
      model=model,
      attempts=attempts,
      duration_seconds=round(duration_seconds, 3),
      findings=findings,
      extra_fields=extra_fields,
    )
    _write_parsed_response(args.parsed_out, output)
    if args.review_run_dir:
      update_review_run_artifacts(
        args.review_run_dir,
        round_id=args.round_id,
        target_path=args.target,
        phase=args.phase,
        criteria=criteria,
        role=args.role,
        provider=provider_name,
        model=model,
        prompt=prompt,
        response_text=response_text,
        attempts=attempts,
        duration_seconds=duration_seconds,
        parse_status="parsed",
        findings=findings,
        formatted_output=output,
        effective_prompt_path=args.effective_prompt_path,
        effective_prompt_sha256=effective_prompt_sha256,
        prompt_manifest_path=args.prompt_manifest_path,
        prompt_manifest_sha256=prompt_manifest_sha256,
        criteria_source_path=criteria_source_path,
        criteria_source_sha256=criteria_source_sha256,
      )
    has_artifact_sink = bool(args.raw_out or args.parsed_out or args.review_run_dir)
    if args.verbose or not has_artifact_sink:
      sys.stdout.write(output)
    else:
      sys.stdout.write(status_line(
        "OK",
        "run_role",
        _normal_output_fields(
          args,
          role=args.role,
          provider=provider_name,
          model=model,
          findings=findings,
        ),
      ))
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())


## tools/api_providers/run_review.py

"""tools/api_providers/run_review.py

複数 role を同じ review-run ディレクトリへ集約して実行する薄い orchestrator。
raw / parsed / rounds / summary の生成は run_role.py の成果物関数を再利用する。
"""
import argparse
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers.config_loader import (  # noqa: E402
  load_config,
  resolve_connection_settings,
  resolve_default_variant_name,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import (  # noqa: E402
  enable_zshrc_api_key_fallback,
  get_provider,
)
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_data,
)
from tools.api_providers.run_role import (  # noqa: E402
  _resolve_effective_prompt_sha256,
  _resolve_prompt_manifest_sha256,
  build_prompt,
  update_review_run_artifacts,
)
from tools.normal_output import join_values, status_line  # noqa: E402

ROLES = ["primary", "adversarial", "judgment"]
NORMALIZED_SEVERITY = {"CRITICAL", "ERROR", "WARN", "INFO"}
POST_WRITE_DEFAULT_VARIANT = "post_write_verification_google"
VERTICAL_REVIEW_REQUIRED_FIELDS = [
  "purpose",
  "responsibility_boundaries",
  "acceptance_criteria",
  "forbidden_actions",
  "unresolved_or_design_deferred_items",
  "intended_target_phase_transfer",
]


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path: Path) -> str:
  import hashlib

  return hashlib.sha256(path.read_bytes()).hexdigest()


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  return response_text, 1, time.monotonic() - start


def _normalize_severity(value: Any) -> str:
  severity = str(value or "INFO").upper()
  return severity if severity in NORMALIZED_SEVERITY else "INFO"


def _load_parsed_findings(review_run_dir: Path, parsed_path: Optional[str]) -> List[Dict[str, Any]]:
  if not parsed_path:
    return []
  parsed_file = review_run_dir / parsed_path
  data = _load_yaml_dict(parsed_file)
  findings = data.get("findings")
  return findings if isinstance(findings, list) else []


def initialize_triage_draft(review_run_dir: str) -> None:
  """parsed findings から human_required の triage 下書きを生成する。"""
  run_dir = Path(review_run_dir)
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  now = datetime.now(timezone.utc).isoformat()
  items: List[Dict[str, Any]] = []
  for model_result in model_results:
    if not isinstance(model_result, dict):
      continue
    if model_result.get("parse_status") != "parsed":
      continue
    findings = _load_parsed_findings(run_dir, model_result.get("parsed_path"))
    for index, finding in enumerate(findings, start=1):
      if not isinstance(finding, dict):
        continue
      severity_original = finding.get("severity", "INFO")
      items.append({
        "finding_id": (
          f"{run_dir.name}-{model_result.get('model_id')}-"
          f"{model_result.get('role')}-{index:03d}"
        ),
        "run_id": run_dir.name,
        "source_model": model_result.get("model_id"),
        "source_round": rounds.get("round_id"),
        "source_raw_path": model_result.get("raw_path"),
        "source_parsed_path": model_result.get("parsed_path"),
        "severity_original": severity_original,
        "severity_normalized": _normalize_severity(severity_original),
        "target_location": finding.get("target_location"),
        "plain_language_summary": finding.get("description"),
        "final_label": None,
        "decision_status": "human_required",
        "decision_actor": None,
        "decision_actor_type": "human",
        "decision_at": None,
        "decision_reason": finding.get("rationale"),
        "applied_files": [],
        "superseded_by": None,
      })

  _dump_yaml(
    run_dir / "triage.yaml",
    {
      "run_id": run_dir.name,
      "triage_status": "draft",
      "generated_at": now,
      "decision_actor": None,
      "decision_actor_type": "human",
      "items": items,
    },
  )


def write_review_summary_markdown(review_run_dir: str, variant_name: str = "default") -> str:
  """model-result-summary.yaml からユーザ提示用 Markdown を生成する。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  lines = [
    f"# Review run summary: {run_dir.name}",
    "",
    f"variant: {variant_name}",
    "",
    "## Role assignments",
    "",
    "| role | path | provider | model |",
    "| --- | --- | --- | --- |",
  ]
  for item in model_results:
    if not isinstance(item, dict):
      continue
    lines.append(
      "| {role} | {path} | {provider} | {model} |".format(
        role=item.get("role"),
        path=item.get("invocation_path"),
        provider=item.get("provider"),
        model=item.get("model_id"),
      )
    )
  lines.extend([
    "",
    "## Model results",
    "",
    "| model_id | parse_status | triage_status | findings | severity | raw |",
    "| --- | --- | --- | ---: | --- | --- |",
  ])
  for item in models:
    if not isinstance(item, dict):
      continue
    severity_counts = item.get("findings_count_by_severity") or {}
    severity_text = ", ".join(
      f"{key}:{value}" for key, value in sorted(severity_counts.items())
    )
    lines.append(
      "| {model_id} | {parse_status} | {triage_status} | {findings_count} | {severity} | {raw_path} |".format(
        model_id=item.get("model_id"),
        parse_status=item.get("parse_status"),
        triage_status=item.get("triage_status"),
        findings_count=item.get("findings_count", 0),
        severity=severity_text or "-",
        raw_path=item.get("raw_path"),
      )
    )
  lines.extend([
    "",
    "## Next steps",
    "",
    "1. Read raw responses for any parse_failed or triage_pending model.",
    "2. Move finding-level judgments into triage.yaml.",
    "3. Present the variant, role assignments, raw/model summary, same-root clusters, and three-level triage to the user.",
    "4. Stop at the 利用者提示ゲート before asking proxy_model, editing implementation, updating spec.json, or moving phases.",
    "5. Resolve human_required items before treating the run as complete.",
  ])
  content = "\n".join(lines) + "\n"
  (run_dir / "review_summary.md").write_text(content, encoding="utf-8")
  return content


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="3 role API review を同じ review-run に集約して実行する。",
  )
  parser.add_argument("--variant", default=None, help="variant 名。未指定なら default")
  parser.add_argument(
    "--default-variant-for",
    default=None,
    help="operation_defaults から既定 variant を解決する場面名",
  )
  parser.add_argument(
    "--target",
    required=True,
    action="append",
    help="対象文書ファイルパス（複数指定可）",
  )
  parser.add_argument("--phase", required=True, help="段名")
  parser.add_argument("--criteria", default=None, help="観点識別子")
  parser.add_argument(
    "--criteria-file",
    default=None,
    help="観点本文を含むファイル。指定時は --criteria の代わりに本文を使う",
  )
  parser.add_argument("--review-run-dir", required=True, help="review-run 成果物ディレクトリ")
  parser.add_argument("--round-id", default="round-1", help="round ID")
  parser.add_argument("--config", default="config/api-settings.yaml", help="API 設定ファイル")
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  parser.add_argument(
    "--effective-prompt-path",
    default=None,
    help="判定点ごとに生成された effective prompt ファイルのパス",
  )
  parser.add_argument(
    "--effective-prompt-sha256",
    default=None,
    help="effective prompt ファイルの sha256。未指定ならファイルから計算する",
  )
  parser.add_argument(
    "--prompt-manifest-path",
    default=None,
    help="構造化 effective prompt manifest ファイルのパス",
  )
  parser.add_argument(
    "--prompt-manifest-sha256",
    default=None,
    help="prompt manifest ファイルの sha256。未指定ならファイルから計算する",
  )
  parser.add_argument(
    "--verbose",
    action="store_true",
    help="正常系でも review_summary.md の本文を標準出力へ表示する",
  )
  return parser.parse_args(argv)


def _resolve_criteria(args: argparse.Namespace) -> Tuple[str, Optional[str], Optional[str]]:
  """--criteria / --criteria-file から実効 criteria と出典情報を返す。"""
  if bool(args.criteria) == bool(args.criteria_file):
    raise ValueError("--criteria または --criteria-file のどちらか一方を指定してください")
  if args.criteria_file:
    path = Path(args.criteria_file)
    criteria = path.read_text(encoding="utf-8")
    return criteria, str(path), _sha256_file(path)
  return args.criteria, None, None


def _looks_like_vertical_intent_review(criteria: str) -> bool:
  lowered = criteria.lower()
  markers = [
    "vertical intent",
    "intent-transfer",
    "intent transfer",
    "上流意図",
    "意図伝達",
    "upstream purpose",
    "responsibility boundaries",
    "forbidden actions",
  ]
  return any(marker in lowered for marker in markers)


def _source_materials_body(criteria: str) -> str:
  match = re.search(
    r"(?ims)^#{2,6}\s*source materials\s*$\n(?P<body>.*?)(?=^#{2,6}\s|\Z)",
    criteria,
  )
  return match.group("body").strip() if match else ""


def _has_upstream_structured_summary(criteria: str) -> bool:
  lowered = criteria.lower()
  return all(field in lowered for field in VERTICAL_REVIEW_REQUIRED_FIELDS)


def _source_materials_are_paths_only(criteria: str) -> bool:
  body = _source_materials_body(criteria)
  if not body:
    return False
  meaningful_lines = [
    line.strip()
    for line in body.splitlines()
    if line.strip() and not line.strip().startswith("Use these source materials")
  ]
  if not meaningful_lines:
    return False

  path_line_re = re.compile(
    r"^[-*]\s+`?[\w./{}-]+\.(?:md|yaml|yml|json|txt)(?:#[\w./{}-]+)?`?\s*$",
  )
  return all(path_line_re.match(line) for line in meaningful_lines)


def validate_review_prompt_preflight(args: argparse.Namespace, criteria: str) -> List[str]:
  """API 送信前に review prompt の機械的な最低条件を検査する。"""
  if args.phase != "triad-review" or not _looks_like_vertical_intent_review(criteria):
    return []

  errors = []
  has_structured_summary = _has_upstream_structured_summary(criteria)
  if _source_materials_are_paths_only(criteria) and not has_structured_summary:
    errors.append(
      "source materials are listed only as paths; include upstream excerpt or structured summary"
    )
  if not has_structured_summary:
    errors.append(
      "upstream structured summary is missing required fields: "
      + ", ".join(VERTICAL_REVIEW_REQUIRED_FIELDS)
    )
  return errors


def _select_variant_name(args: argparse.Namespace, config: Dict[str, Any]) -> Optional[str]:
  """phase に応じた実効 variant 名を返す。"""
  if args.variant and args.default_variant_for:
    raise ValueError("--variant と --default-variant-for は同時に指定できません")
  if args.default_variant_for:
    return resolve_default_variant_name(config, args.default_variant_for)
  if args.variant == "default":
    return None
  if args.variant:
    return args.variant
  if args.phase == "post_write_verification":
    return POST_WRITE_DEFAULT_VARIANT
  return None


def _roles_for_variant(variant_config: Dict[str, Any]) -> List[str]:
  """variant の required_roles があればそれを使い、なければ 3 役を使う。"""
  required_roles = variant_config.get("required_roles")
  if isinstance(required_roles, list) and required_roles:
    return [role for role in required_roles if isinstance(role, str)]
  return list(ROLES)


def _run_one_role(
  args,
  config: Dict[str, Any],
  variant_name: Optional[str],
  role: str,
) -> int:
  """1 role を実行して review-run 成果物へ反映する。"""
  variant_config = resolve_variant(config, variant_name)
  role_config = resolve_role(variant_config, role)
  connection_defaults = config.get("connection", {})
  connection_settings = resolve_connection_settings(role_config, connection_defaults)

  provider_name = role_config["provider"]
  model = role_config["model"]
  provider_cls = get_provider(provider_name)
  provider = provider_cls(
    model=model,
    timeout_seconds=connection_settings.get("timeout_seconds", 60),
    max_retries=connection_settings.get("max_retries", 1),
  )
  criteria, criteria_source_path, criteria_source_sha256 = _resolve_criteria(args)

  prompt = build_prompt(
    args.target,
    args.phase,
    criteria,
    args.prior_finding,
    provider_name=provider_name,
    model=model,
  )
  effective_prompt_sha256 = _resolve_effective_prompt_sha256(
    args.effective_prompt_path,
    args.effective_prompt_sha256,
  )
  prompt_manifest_sha256 = _resolve_prompt_manifest_sha256(
    args.prompt_manifest_path,
    args.prompt_manifest_sha256,
  )
  response_text, attempts, duration_seconds = _call_provider(provider, prompt)
  try:
    parsed_response = parse_response_data(response_text)
    findings = parsed_response["findings"]
  except Exception:
    update_review_run_artifacts(
      args.review_run_dir,
      round_id=args.round_id,
      target_path=args.target,
      phase=args.phase,
      criteria=criteria,
      role=role,
      provider=provider_name,
      model=model,
      prompt=prompt,
      response_text=response_text,
      attempts=attempts,
      duration_seconds=duration_seconds,
      parse_status="parse_failed",
      findings=None,
      formatted_output=None,
      effective_prompt_path=args.effective_prompt_path,
      effective_prompt_sha256=effective_prompt_sha256,
      prompt_manifest_path=args.prompt_manifest_path,
      prompt_manifest_sha256=prompt_manifest_sha256,
      criteria_source_path=criteria_source_path,
      criteria_source_sha256=criteria_source_sha256,
    )
    return 1

  extra_fields = {
    key: value
    for key, value in parsed_response.items()
    if key != "findings"
  }
  output = format_response(
    role=role,
    provider=provider_name,
    model=model,
    attempts=attempts,
    duration_seconds=round(duration_seconds, 3),
    findings=findings,
    extra_fields=extra_fields,
  )
  update_review_run_artifacts(
    args.review_run_dir,
    round_id=args.round_id,
    target_path=args.target,
    phase=args.phase,
    criteria=criteria,
    role=role,
    provider=provider_name,
    model=model,
    prompt=prompt,
    response_text=response_text,
    attempts=attempts,
    duration_seconds=duration_seconds,
    parse_status="parsed",
    findings=findings,
    formatted_output=output,
    effective_prompt_path=args.effective_prompt_path,
    effective_prompt_sha256=effective_prompt_sha256,
    prompt_manifest_path=args.prompt_manifest_path,
    prompt_manifest_sha256=prompt_manifest_sha256,
    criteria_source_path=criteria_source_path,
    criteria_source_sha256=criteria_source_sha256,
  )
  return 0


def _summary_fields(review_run_dir: str, roles: List[str]) -> Dict[str, Any]:
  """正常系 human output 用の短い summary fields を返す。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []
  model_ids = [
    item.get("model_id")
    for item in models
    if isinstance(item, dict) and item.get("model_id")
  ]
  findings = sum(
    int(item.get("findings_count", 0) or 0)
    for item in models
    if isinstance(item, dict)
  )
  parse_failed = sum(
    1
    for item in models
    if isinstance(item, dict) and item.get("parse_status") == "parse_failed"
  )
  return {
    "review_run_dir": review_run_dir,
    "summary": str(run_dir / "review_summary.md"),
    "roles": len(roles),
    "model_ids": join_values(model_ids),
    "findings": findings,
    "parse_failed": parse_failed,
  }


def main(argv: Optional[List[str]] = None) -> int:
  enable_zshrc_api_key_fallback()
  args = _parse_argv(argv)
  exit_code = 0
  try:
    criteria, _, _ = _resolve_criteria(args)
    preflight_errors = validate_review_prompt_preflight(args, criteria)
    if preflight_errors:
      sys.stderr.write("エラー：vertical intent transfer prompt preflight failed\n")
      for error in preflight_errors:
        sys.stderr.write(f"  - {error}\n")
      return 1

    config = load_config(args.config)
    variant_name = _select_variant_name(args, config)
    variant_config = resolve_variant(config, variant_name)
    roles = _roles_for_variant(variant_config)
    for role in roles:
      role_exit_code = _run_one_role(args, config, variant_name, role)
      if role_exit_code != 0:
        exit_code = 1
    initialize_triage_draft(args.review_run_dir)
    summary_variant_name = variant_name or "default"
    summary_markdown = write_review_summary_markdown(
      args.review_run_dir,
      summary_variant_name,
    )
    if args.verbose:
      sys.stdout.write(summary_markdown)
    else:
      verdict = "OK" if exit_code == 0 else "WARN"
      sys.stdout.write(status_line(
        verdict,
        "run_review",
        _summary_fields(args.review_run_dir, roles),
      ))
    return exit_code
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())


## tests/workflow-management/test_language_task_io_schema.py

"""T-018 language task I/O schema red tests."""

import json
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_TASK_SCHEMA = (
  REPO_ROOT / ".reviewcompass" / "schema" / "language_task_io.schema.json"
)


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def valid_language_task(**overrides):
  task = {
    "document_kind": "review",
    "input": {
      "required_files": ["docs/operations/WORKFLOW_NAVIGATION.md"],
      "state_refs": [".reviewcompass/specs/workflow-management/spec.json"],
      "source_refs": ["docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"],
    },
    "output_format": {
      "kind": "markdown",
      "required_sections": ["Findings", "Decision"],
      "schema_ref": None,
    },
    "constraints": [
      "Do not execute git operations.",
      "Do not mutate workflow state.",
    ],
  }
  task.update(overrides)
  return task


class LanguageTaskIoSchemaTests(unittest.TestCase):
  def test_language_task_io_schema_exists_and_requires_design_vocabulary(self):
    self.assertTrue(LANGUAGE_TASK_SCHEMA.exists(), f"missing schema: {LANGUAGE_TASK_SCHEMA}")
    schema = load_json(LANGUAGE_TASK_SCHEMA)
    self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
    self.assertEqual(schema.get("type"), "object")
    for field in ["document_kind", "input", "output_format", "constraints"]:
      self.assertIn(field, schema.get("required", []), field)

  def test_language_task_io_rejects_unknown_or_machine_action_fields(self):
    schema = load_json(LANGUAGE_TASK_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    valid_errors = list(validator.iter_errors(valid_language_task()))
    self.assertEqual(valid_errors, [])

    unknown_errors = list(validator.iter_errors(valid_language_task(allowed_actions=["commit"])))
    self.assertNotEqual(unknown_errors, [])

    machine_task = valid_language_task()
    machine_task["input"]["operation_execution"] = "git commit"
    machine_errors = list(validator.iter_errors(machine_task))
    self.assertNotEqual(machine_errors, [])


if __name__ == "__main__":
  unittest.main()


## tests/workflow-management/test_effective_prompt_manifest.py

"""T-018 effective prompt manifest red tests."""

import json
import unittest
from pathlib import Path

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = (
  REPO_ROOT / ".reviewcompass" / "schema" / "effective_prompt_manifest.schema.json"
)


def load_json(path):
  with path.open(encoding="utf-8") as f:
    return json.load(f)


def valid_manifest(**overrides):
  manifest = {
    "schema_version": "effective-prompt-manifest-v1",
    "decision_point": {
      "kind": "stage",
      "required_action": "run_workflow_stage",
      "phase": "implementation",
      "stage": "drafting",
      "active_gate": None,
    },
    "source_artifacts": [
      {
        "path": "docs/operations/WORKFLOW_NAVIGATION.md",
        "sha256": "sha256:" + "a" * 64,
      }
    ],
    "required_disciplines": ["docs/operations/WORKFLOW_NAVIGATION.md"],
    "operation_contract": {
      "operation_id": "run_workflow_stage",
      "sha256": "sha256:" + "b" * 64,
    },
    "expected_output_schema": {
      "schema_ref": None,
      "required_sections": ["Findings"],
    },
    "prompt_length": {
      "min_chars": 100,
      "max_chars": 20000,
      "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      "failure_verdict": "WARN",
    },
    "preconditions_checked": [
      {
        "id": "next-json-loaded",
        "source": "next_json",
        "machine_checked": True,
        "evidence_ref": ".reviewcompass/runtime/effective-prompts/example.prompt.md",
      }
    ],
    "language_task": {
      "document_kind": "review",
      "input": {
        "required_files": ["docs/operations/WORKFLOW_NAVIGATION.md"],
        "state_refs": [],
        "source_refs": [],
      },
      "output_format": {
        "kind": "markdown",
        "required_sections": ["Findings"],
        "schema_ref": None,
      },
      "constraints": ["Do not mutate workflow state."],
    },
    "postconditions": [
      {
        "id": "next-action-compatible",
        "check_kind": "next_action_compatible",
        "source_ref": "stages/operation-contracts.yaml",
      }
    ],
    "on_completion": {
      "next_required_action": "run_workflow_stage",
      "allowed_followups": ["prompt-audit"],
      "forbidden_actions": ["commit", "push", "spec-set"],
    },
  }
  manifest.update(overrides)
  return manifest


class EffectivePromptManifestSchemaTests(unittest.TestCase):
  def test_effective_prompt_manifest_covers_source_digests(self):
    self.assertTrue(MANIFEST_SCHEMA.exists(), f"missing schema: {MANIFEST_SCHEMA}")
    schema = load_json(MANIFEST_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    valid_errors = list(validator.iter_errors(valid_manifest()))
    self.assertEqual(valid_errors, [])

    missing_digest = valid_manifest(
      source_artifacts=[{"path": "docs/operations/WORKFLOW_NAVIGATION.md"}]
    )
    self.assertNotEqual(list(validator.iter_errors(missing_digest)), [])

  def test_prompt_length_bounds_are_required_and_structured(self):
    schema = load_json(MANIFEST_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)

    bad_bounds = valid_manifest(
      prompt_length={
        "min_chars": 20000,
        "max_chars": 100,
        "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      }
    )
    errors = list(validator.iter_errors(bad_bounds))
    self.assertNotEqual(errors, [])


if __name__ == "__main__":
  unittest.main()


## tests/workflow-management/test_prompt_audit.py

"""T-018 prompt audit red tests."""

import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


def manifest(**overrides):
  data = {
    "schema_version": "effective-prompt-manifest-v1",
    "decision_point": {"kind": "stage", "required_action": "run_workflow_stage"},
    "source_artifacts": [
      {"path": "docs/operations/WORKFLOW_NAVIGATION.md", "sha256": "sha256:" + "a" * 64}
    ],
    "prompt_length": {
      "min_chars": 100,
      "max_chars": 20000,
      "source_ref": "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#default_prompt_length_bounds",
      "failure_verdict": "WARN",
    },
    "language_task": {
      "document_kind": "review",
      "input": {"required_files": [], "state_refs": [], "source_refs": []},
      "output_format": {"kind": "markdown", "required_sections": ["Findings"], "schema_ref": None},
      "constraints": ["Do not mutate workflow state."],
    },
    "postconditions": [
      {"id": "compat", "check_kind": "next_action_compatible", "source_ref": "contract"}
    ],
    "on_completion": {
      "next_required_action": "run_workflow_stage",
      "allowed_followups": ["prompt-audit"],
      "forbidden_actions": ["commit", "push", "spec-set"],
    },
  }
  data.update(overrides)
  return data


class PromptAuditTests(unittest.TestCase):
  def _module(self):
    return importlib.import_module("check_workflow_action.prompt_audit")

  def test_prompt_audit_rejects_direct_state_mutation_instruction(self):
    module = self._module()
    data = manifest(
      on_completion={
        "next_required_action": "commit_stop_point",
        "allowed_followups": ["spec.json を更新して commit する"],
        "forbidden_actions": [],
      }
    )

    result = module.audit_manifest(data)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("on_completion", "\n".join(result["reasons"]))

  def test_prompt_audit_rejects_machine_execution_steps_beyond_state_mutation(self):
    module = self._module()
    data = manifest()
    data["language_task"]["constraints"] = [
      "Create review-run artifacts.",
      "Consume approval gate.",
      "Mutate side-track stack.",
      "Execute operation.",
    ]

    result = module.audit_manifest(data)

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("machine", "\n".join(result["reasons"]).lower())

  def test_prompt_audit_rejects_on_completion_not_next_action_compatible(self):
    module = self._module()
    data = manifest(
      on_completion={
        "next_required_action": "commit_stop_point",
        "allowed_followups": ["commit"],
        "forbidden_actions": ["commit"],
      }
    )

    result = module.audit_manifest(
      data,
      current_next_action={"required_action": "run_workflow_stage"},
    )

    self.assertEqual(result["verdict"], "DEVIATION")
    self.assertIn("next_action_compatible", "\n".join(result["reasons"]))

  def test_prompt_audit_cli_reads_manifest_json(self):
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "prompt-manifest.yaml"
      path.write_text(yaml.safe_dump(manifest()), encoding="utf-8")

      result = subprocess.run(
        [sys.executable, str(SCRIPT), "prompt-audit", "--prompt-manifest", str(path), "--json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
      )

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")


if __name__ == "__main__":
  unittest.main()


## tests/workflow-management/test_prompt_manifest_rounds_recording.py

"""T-018 prompt manifest rounds recording red tests."""

import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "api_providers"))

from run_role import update_review_run_artifacts  # noqa: E402


class PromptManifestRoundsRecordingTests(unittest.TestCase):
  def test_rounds_records_prompt_manifest_without_removing_text_prompt_fields(self):
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      target = tmp_path / "target.md"
      target.write_text("# Target\n", encoding="utf-8")
      effective_prompt = tmp_path / "effective.prompt.md"
      effective_prompt.write_text("Read the target.", encoding="utf-8")
      prompt_manifest = tmp_path / "effective.prompt.yaml"
      prompt_manifest.write_text("schema_version: effective-prompt-manifest-v1\n", encoding="utf-8")
      run_dir = tmp_path / "review-run"

      update_review_run_artifacts(
        str(run_dir),
        round_id="round-1",
        target_path=str(target),
        phase="design",
        criteria="criteria",
        role="primary",
        provider="local",
        model="model-a",
        prompt="prompt text",
        response_text="- none",
        attempts=1,
        duration_seconds=0.1,
        parse_status="parsed",
        findings=[],
        formatted_output="findings: []\n",
        effective_prompt_path=str(effective_prompt),
        effective_prompt_sha256="sha256:" + "a" * 64,
        prompt_manifest_path=str(prompt_manifest),
        prompt_manifest_sha256="sha256:" + "b" * 64,
      )

      rounds = yaml.safe_load((run_dir / "rounds.yaml").read_text(encoding="utf-8"))
      self.assertEqual(rounds["effective_prompt_path"], str(effective_prompt))
      self.assertEqual(rounds["effective_prompt_sha256"], "sha256:" + "a" * 64)
      self.assertEqual(rounds["prompt_manifest_path"], str(prompt_manifest))
      self.assertEqual(rounds["prompt_manifest_sha256"], "sha256:" + "b" * 64)


if __name__ == "__main__":
  unittest.main()


## tools/api_providers/tests/test_run_role.py

# tools/api_providers/tests/test_run_role.py
# run_role エントリポイントのテスト（サブサイクル 4-C、TDD 先行）。
# 計画書 §5.9.7.1 の入出力契約に準拠する。
# プロバイダーは MagicMock で置換し、in-process でテストする。

import hashlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest
import yaml

from tools.api_providers.run_role import build_prompt, main


# --- fixtures ---


@pytest.fixture
def tmp_target_file(tmp_path):
  target = tmp_path / "target.md"
  target.write_text("対象文書の内容\n要件の本文を記載", encoding="utf-8")
  return target


@pytest.fixture
def tmp_prior_finding(tmp_path):
  prior = tmp_path / "prior.yaml"
  prior.write_text(
    "findings:\n  - severity: WARN\n    description: 前段の所見\n",
    encoding="utf-8",
  )
  return prior


@pytest.fixture
def tmp_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
  adversarial:
    path: api
    provider: anthropic-api
    model: claude-sonnet-4-6
  judgment:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
""",
    encoding="utf-8",
  )
  return config_path


def _make_mock_provider(send_response="findings: []\n", side_effect=None):
  """get_provider をモック化する補助関数。"""
  mock_instance = MagicMock()
  if side_effect is not None:
    mock_instance.send_request.side_effect = side_effect
  else:
    mock_instance.send_request.return_value = send_response
  mock_cls = MagicMock(return_value=mock_instance)
  return mock_cls, mock_instance


# --- 1. build_prompt の正常系 ---


def test_build_prompt_includes_target_content(tmp_target_file):
  """build_prompt の出力に対象文書の内容が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements_triad_review", "観点-1", [])
  assert "対象文書の内容" in prompt
  assert "要件の本文を記載" in prompt


def test_build_prompt_includes_phase(tmp_target_file):
  """build_prompt の出力に段名が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "design_triad_review", "観点-1", [])
  assert "design_triad_review" in prompt


def test_build_prompt_includes_criteria(tmp_target_file):
  """build_prompt の出力に観点識別子が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements", "観点-3", [])
  assert "観点-3" in prompt


def test_build_prompt_includes_prior_finding(tmp_target_file, tmp_prior_finding):
  """build_prompt の出力に前段所見の内容が含まれる。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(tmp_prior_finding)],
  )
  assert "前段の所見" in prompt


def test_build_prompt_includes_multiple_prior_findings(tmp_target_file, tmp_path):
  """build_prompt が複数の前段所見をすべて含む。"""
  p1 = tmp_path / "prior1.yaml"
  p1.write_text(
    "findings:\n  - description: 所見 アルファ\n", encoding="utf-8"
  )
  p2 = tmp_path / "prior2.yaml"
  p2.write_text(
    "findings:\n  - description: 所見 ベータ\n", encoding="utf-8"
  )
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(p1), str(p2)],
  )
  assert "所見 アルファ" in prompt
  assert "所見 ベータ" in prompt


def test_build_prompt_uses_anthropic_specific_template(tmp_target_file):
  """anthropic-api では code fence / review wrapper を禁止する専用テンプレートを使う。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )
  assert "model_id: claude-sonnet-4-6" in prompt
  assert "Do not wrap the YAML in Markdown code fences" in prompt
  assert "Do not use review:" in prompt
  assert "The response must include the top-level key findings" in prompt
  assert "Additional top-level keys are allowed only when the criteria explicitly defines them" in prompt


def test_build_prompt_uses_default_template_for_unknown_provider(tmp_target_file):
  """未知 provider では共通テンプレートへ fallback する。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="unknown-provider",
    model="unknown-model",
  )
  assert "prompt_id: default_review" in prompt
  assert "The response must include the top-level key findings" in prompt
  assert "Additional top-level keys are allowed only when the criteria explicitly defines them" in prompt
  assert "findings: []" in prompt


def test_build_prompt_does_not_replace_placeholders_inside_target_content(tmp_path):
  """対象文書内の template placeholder 文字列は本文として保持する。"""
  target = tmp_path / "target.md"
  target.write_text(
    "# Target\n{{ prior_findings }}\n{{ target_path }}\n",
    encoding="utf-8",
  )

  prompt = build_prompt(
    str(target),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )

  assert "# Target\n{{ prior_findings }}\n{{ target_path }}" in prompt


def test_build_prompt_renders_prior_findings_in_provider_template(
  tmp_target_file,
  tmp_prior_finding,
):
  """provider template 経由でも前段所見がプロンプトへ入る。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [str(tmp_prior_finding)],
    provider_name="openai-api",
    model="gpt-5.4",
  )

  assert "# 前段所見 1" in prompt
  assert "前段の所見" in prompt


# --- 2. main の正常系 ---


def test_main_outputs_formatted_yaml(tmp_target_file, tmp_config, monkeypatch, capsys):
  """main が正常系で整形済み YAML を標準出力に書く。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: テスト所見
    rationale: テスト根拠
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements_triad_review",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code == 0
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["role"] == "primary"
  assert parsed["provider"] == "anthropic-api"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["attempts"] == 1
  assert len(parsed["findings"]) == 1
  assert parsed["findings"][0]["severity"] == "WARN"


def test_main_duration_seconds_is_present(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """main の出力に duration_seconds（所要時間）が含まれる。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert "duration_seconds" in parsed
  assert isinstance(parsed["duration_seconds"], (int, float))
  assert parsed["duration_seconds"] >= 0


# --- 3. main の異常系 ---


def test_main_missing_required_args_raises():
  """必須引数が不足していたら SystemExit（argparse 既定動作）。"""
  with pytest.raises(SystemExit):
    main(["--role", "primary"])  # --target, --phase, --criteria が欠落


def test_main_provider_error_returns_nonzero(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """プロバイダーが例外を投げたら非ゼロ終了、標準エラーに理由を出力。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider(side_effect=RuntimeError("API 呼び出し失敗"))
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code != 0
  captured = capsys.readouterr()
  assert "エラー" in captured.err or "error" in captured.err.lower()


# --- 4. variant 切替 ---


def test_main_uses_variant_when_specified(
  tmp_target_file, tmp_path, monkeypatch, capsys
):
  """--variant が指定されたら variants から役設定を取得する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
variants:
  openai_variant:
    primary:
      path: api
      provider: openai-api
      model: gpt-test
""",
    encoding="utf-8",
  )
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--variant", "openai_variant",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(config_path),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["provider"] == "openai-api"
  assert parsed["model"] == "gpt-test"


def test_main_uses_default_variant_for_operation(
  tmp_target_file, tmp_path, monkeypatch, capsys
):
  """--default-variant-for で場面ごとの既定 variant を取得する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
operation_defaults:
  api_review_prompt_quality:
    variant: prompt_quality_2way
default:
  adversarial:
    path: api
    provider: openai-api
    model: wrong-default
variants:
  prompt_quality_2way:
    required_roles: [adversarial, judgment]
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
""",
    encoding="utf-8",
  )
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "adversarial",
        "--default-variant-for", "api_review_prompt_quality",
        "--target", str(tmp_target_file),
        "--phase", "prompt-quality",
        "--criteria", "観点-1",
        "--config", str(config_path),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["provider"] == "anthropic-api"
  assert parsed["model"] == "claude-sonnet-4-6"


# --- 5. raw / parsed / review-run 成果物 ---


def test_main_writes_raw_out_before_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 失敗時でも --raw-out に provider 生応答を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  raw_out = tmp_path / "raw.txt"
  mock_cls, _ = _make_mock_provider(send_response="not: [valid\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--raw-out", str(raw_out),
      ]
    )

  assert exit_code != 0
  assert raw_out.read_text(encoding="utf-8") == "not: [valid\n"
  captured = capsys.readouterr()
  assert "エラー" in captured.err


def test_main_writes_parsed_out_on_parse_success(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 成功時に --parsed-out へ整形済み YAML を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_response = """
findings:
  - severity: INFO
    target_location: a.md
    description: 指摘なし
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.count("\n") == 1
  assert captured.out.startswith("[OK] run_role ")
  assert f"parsed={parsed_out}" in captured.out
  parsed = yaml.safe_load(parsed_out.read_text(encoding="utf-8"))
  assert parsed["role"] == "primary"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["findings"][0]["severity"] == "INFO"


def test_main_preserves_structured_fields_in_parsed_out(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 成功時に findings 以外の検査結果も --parsed-out へ保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_response = """
verdict: sufficient_with_revisions
independent_reconstruction:
  judgment_items:
    - item_id: req14_approval_gate
      question: 承認ゲートを検査できるか
preanalysis_assessment:
  missing_perspectives:
    - データソース網羅
prompt_sufficiency:
  information: revisions_needed
required_prompt_changes:
  - main preanalysis を仮説として扱う
findings: []
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "adversarial",
        "--target", str(tmp_target_file),
        "--phase", "prompt-quality",
        "--criteria", "preanalysis sufficiency",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
      ]
    )

  assert exit_code == 0
  capsys.readouterr()
  parsed = yaml.safe_load(parsed_out.read_text(encoding="utf-8"))
  assert parsed["role"] == "adversarial"
  assert parsed["verdict"] == "sufficient_with_revisions"
  assert parsed["independent_reconstruction"]["judgment_items"][0]["item_id"] == "req14_approval_gate"
  assert parsed["preanalysis_assessment"]["missing_perspectives"] == ["データソース網羅"]
  assert parsed["prompt_sufficiency"]["information"] == "revisions_needed"
  assert parsed["required_prompt_changes"] == ["main preanalysis を仮説として扱う"]
  assert parsed["findings"] == []


def test_main_updates_review_run_artifacts(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """--review-run-dir 指定時に raw、parsed、rounds、summary、target manifest を生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: 要確認
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  assert captured.out.count("\n") == 1
  assert captured.out.startswith("[OK] run_role ")
  assert "role=primary" in captured.out
  assert "model=claude-opus-4-7" in captured.out
  assert "findings=1" in captured.out
  assert f"review_run_dir={review_run_dir}" in captured.out
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  parsed_path = review_run_dir / "parsed" / "claude-opus-4-7.round-1.yaml"
  assert raw_path.is_file()
  assert parsed_path.is_file()

  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )

  assert target_manifest["target_files"][0]["path"] == str(tmp_target_file)
  model_result = rounds["model_results"][0]
  assert model_result["model_id"] == "claude-opus-4-7"
  assert model_result["raw_path"] == "raw/claude-opus-4-7.round-1.txt"
  assert model_result["parsed_path"] == "parsed/claude-opus-4-7.round-1.yaml"
  assert model_result["parse_status"] == "parsed"
  assert len(model_result["raw_sha256"]) == 64
  assert len(model_result["parsed_sha256"]) == 64

  summary_model = summary["models"][0]
  assert summary_model["model_id"] == "claude-opus-4-7"
  assert summary_model["parse_status"] == "parsed"
  assert summary_model["triage_status"] == "triage_pending"
  assert summary_model["findings_count"] == 1
  assert summary_model["findings_count_by_severity"]["WARN"] == 1


def test_main_verbose_outputs_formatted_yaml_with_artifact_sink(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """--verbose では保存先があっても整形済み YAML を stdout に出す。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_cls, _ = _make_mock_provider(send_response="findings: []\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
        "--verbose",
      ]
    )

  assert exit_code == 0
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["role"] == "primary"
  assert parsed["findings"] == []


def test_main_records_multiple_targets_in_review_run_artifacts(
  tmp_config, tmp_path, monkeypatch
):
  """--target 複数指定時に全対象を manifest と rounds に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  first_target = tmp_path / "first.md"
  second_target = tmp_path / "second.md"
  first_target.write_text("first\n", encoding="utf-8")
  second_target.write_text("second\n", encoding="utf-8")
  review_run_dir = tmp_path / "review-run"
  mock_cls, mock_instance = _make_mock_provider(send_response="findings: []\n")

  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(first_target),
        "--target", str(second_target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
      ]
    )

  assert exit_code == 0
  sent_prompt = mock_instance.send_request.call_args.args[0]
  assert str(first_target) in sent_prompt
  assert str(second_target) in sent_prompt
  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["path"] for item in target_manifest["target_files"]] == [
    str(first_target),
    str(second_target),
  ]
  assert [item["path"] for item in rounds["target_files"]] == [
    str(first_target),
    str(second_target),
  ]


def test_main_records_effective_prompt_metadata_in_rounds(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """effective prompt のパスと sha256 を rounds.yaml に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  effective_prompt = tmp_path / ".reviewcompass" / "effective-prompts" / "stage.prompt.md"
  effective_prompt.parent.mkdir(parents=True)
  effective_prompt.write_text("# Effective Prompt\n\nbody\n", encoding="utf-8")
  mock_cls, _ = _make_mock_provider(send_response="findings: []\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--effective-prompt-path", str(effective_prompt),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["effective_prompt_path"] == str(effective_prompt)
  assert rounds["effective_prompt_sha256"] == hashlib.sha256(
    effective_prompt.read_bytes()
  ).hexdigest()


def test_main_updates_review_run_artifacts_on_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """parse 失敗時も review-run に raw と parse_failed 状態を残す。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_cls, _ = _make_mock_provider(send_response="findings: [broken\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code != 0
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  assert raw_path.read_text(encoding="utf-8") == "findings: [broken\n"

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  model_result = rounds["model_results"][0]
  assert model_result["parse_status"] == "parse_failed"
  assert model_result["parsed_path"] is None
  assert model_result["follow_up_action"] == "format_pending"
  summary_model = summary["models"][0]
  assert summary_model["parse_status"] == "parse_failed"
  assert summary_model["triage_status"] == "triage_pending"


## tools/api_providers/tests/test_run_review.py

# tools/api_providers/tests/test_run_review.py
# 複数モデル review-run orchestrator の TDD テスト。

import sys
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.run_review import main


def _make_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
operation_defaults:
  api_review_prompt_quality:
    variant: prompt_quality_2way
  implementation_review:
    variant: implementation_review_independent_3way_codex_operator
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-sonnet-4-6
  adversarial:
    path: api
    provider: openai-api
    model: gpt-5.4
  judgment:
    path: api
    provider: gemini-api
    model: gemini-3.1-pro-preview
variants:
  prompt_quality_2way:
    context: prompt_quality
    variant_type: two_role
    required_roles: [adversarial, judgment]
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
  post_write_verification_google:
    context: post_write_verification
    variant_type: single_role
    required_roles: [primary]
    primary:
      path: api
      provider: gemini-api
      model: gemini-3.5-flash
  implementation_review_independent_3way_codex_operator:
    context: triad_review
    variant_type: triad
    required_roles: [primary, adversarial, judgment]
    primary:
      path: api
      provider: openai-api
      model: gpt-5.4
    adversarial:
      path: api
      provider: anthropic-api
      model: claude-sonnet-4-6
    judgment:
      path: api
      provider: gemini-api
      model: gemini-3.1-pro-preview
""",
    encoding="utf-8",
  )
  return config_path


def _make_provider_factory(responses):
  """provider 名に応じたモック provider class を返す factory。"""
  def factory(provider_name):
    mock_instance = MagicMock()
    mock_instance.send_request.return_value = responses[provider_name]
    return MagicMock(return_value=mock_instance)

  return factory


def test_run_review_executes_three_roles_and_creates_summary_and_triage(tmp_path, monkeypatch, capsys):
  """3 役を同じ review-run に集約し、summary と triage 下書きを生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": """
findings:
  - severity: ERROR
    target_location: target.md
    description: 契約違反の可能性
    rationale: 仕様に影響する
""",
    "openai-api": "findings: []\n",
    "gemini-api": """
findings:
  - severity: WARN
    target_location: target.md
    description: 説明不足
    rationale: 読み手に補足が必要
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "default",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert output.count("\n") == 1
  assert output.startswith("[OK] run_review ")
  assert f"review_run_dir={review_run_dir}" in output
  assert f"summary={review_run_dir / 'review_summary.md'}" in output
  assert "roles=3" in output
  assert "findings=2" in output
  assert "parse_failed=0" in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))

  assert [item["role"] for item in rounds["model_results"]] == [
    "primary",
    "adversarial",
    "judgment",
  ]
  assert len(summary["models"]) == 3
  assert (review_run_dir / "review_summary.md").is_file()
  assert summary["models"][1]["triage_status"] == "no_findings"
  assert summary["models"][0]["triage_status"] == "triage_pending"

  assert triage["triage_status"] == "draft"
  assert len(triage["items"]) == 2
  assert {item["source_model"] for item in triage["items"]} == {
    "claude-sonnet-4-6",
    "gemini-3.1-pro-preview",
  }
  assert all(item["decision_status"] == "human_required" for item in triage["items"])
  assert all(item["final_label"] is None for item in triage["items"])


def test_run_review_uses_default_variant_for_operation(
  tmp_path,
  monkeypatch,
  capsys,
):
  """場面名から prompt-quality 既定 2 役 variant を解決する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "criteria-draft.md"
  target.write_text("API review criteria draft\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "prompt-quality-run"
  responses = {
    "anthropic-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--default-variant-for", "api_review_prompt_quality",
        "--target", str(target),
        "--phase", "prompt-quality",
        "--criteria", "prompt quality",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "roles=2" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  models = [item["model_id"] for item in rounds["model_results"]]
  assert models == ["claude-sonnet-4-6", "gemini-3.1-pro-preview"]
  assert [item["role"] for item in rounds["model_results"]] == [
    "adversarial",
    "judgment",
  ]
  assert triage["items"] == []
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: prompt_quality_2way" in review_summary
  assert "| adversarial | api | anthropic-api | claude-sonnet-4-6 |" in review_summary
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in review_summary
  assert "proxy_model" in review_summary
  assert "利用者提示ゲート" in review_summary


def test_run_review_uses_default_variant_for_implementation_review(
  tmp_path,
  monkeypatch,
  capsys,
):
  """場面名から implementation-review 既定 3 役 variant を解決する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "implementation.md"
  target.write_text("implementation target\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "implementation-review-run"
  responses = {
    "openai-api": "findings: []\n",
    "anthropic-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--default-variant-for", "implementation_review",
        "--target", str(target),
        "--phase", "triad-review",
        "--criteria", "implementation review",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "roles=3" in output
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  models = [item["model_id"] for item in rounds["model_results"]]
  assert models == ["gpt-5.4", "claude-sonnet-4-6", "gemini-3.1-pro-preview"]
  review_summary = (review_run_dir / "review_summary.md").read_text(encoding="utf-8")
  assert "variant: implementation_review_independent_3way_codex_operator" in review_summary
  assert "| primary | api | openai-api | gpt-5.4 |" in review_summary
  assert "| adversarial | api | anthropic-api | claude-sonnet-4-6 |" in review_summary
  assert "| judgment | api | gemini-api | gemini-3.1-pro-preview |" in review_summary


def test_run_review_verbose_outputs_review_summary(tmp_path, monkeypatch, capsys):
  """--verbose では従来どおり review_summary.md の本文を stdout に出す。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
        "--verbose",
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "variant: post_write_verification_google" in output
  assert "| primary | api | gemini-api | gemini-3.5-flash |" in output
  assert "利用者提示ゲート" in output


def test_run_review_continues_after_one_role_parse_failure(tmp_path, monkeypatch):
  """1 役が parse 失敗しても raw を残し、他役の実行と summary 生成を続ける。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": "findings: [broken\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "default",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 1
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  statuses = {item["model_id"]: item["parse_status"] for item in summary["models"]}
  assert statuses["claude-sonnet-4-6"] == "parse_failed"
  assert statuses["gpt-5.4"] == "parsed"
  assert statuses["gemini-3.1-pro-preview"] == "parsed"
  assert (review_run_dir / "raw" / "claude-sonnet-4-6.round-1.txt").is_file()
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert triage["triage_status"] == "draft"


def test_run_review_uses_post_write_default_variant_when_phase_is_post_write(tmp_path, monkeypatch, capsys):
  """post_write_verification は未指定 variant でも CLI default に落とさない。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert output.startswith("[OK] run_review ")
  assert "roles=1" in output
  assert "gemini-3.5-flash" in output
  assert "claude-code-cli" not in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["role"] for item in rounds["model_results"]] == ["primary"]


def test_run_review_records_multiple_targets_in_review_run_artifacts(tmp_path, monkeypatch):
  """run_review の複数 --target が target-manifest と rounds に残る。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  first_target = tmp_path / "first.md"
  second_target = tmp_path / "second.md"
  first_target.write_text("first\n", encoding="utf-8")
  second_target.write_text("second\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(first_target),
        "--target", str(second_target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert [item["path"] for item in target_manifest["target_files"]] == [
    str(first_target),
    str(second_target),
  ]
  assert [item["path"] for item in rounds["target_files"]] == [
    str(first_target),
    str(second_target),
  ]


def test_run_review_respects_single_role_variant_required_roles(tmp_path, monkeypatch, capsys):
  """single_role variant は required_roles に従い primary だけを実行する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": """
findings:
  - severity: INFO
    target_location: target.md
    description: 軽微な確認事項
    rationale: 補足確認
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert output.startswith("[OK] run_review ")
  assert "roles=1" in output
  assert "model_ids=gemini-3.5-flash" in output
  assert "| adversarial |" not in output
  assert "| judgment |" not in output

  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert len(triage["items"]) == 1
  assert triage["items"][0]["source_model"] == "gemini-3.5-flash"


def test_run_review_preserves_structured_fields_in_parsed_artifact(
  tmp_path,
  monkeypatch,
  capsys,
):
  """run_review でも findings 以外の検査結果を parsed 成果物に保持する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "gemini-api": """
verdict: insufficient
independent_reconstruction:
  judgment_items:
    - item_id: prompt_source_coverage
      question: source から preanalysis を引き出せるか
preanalysis_assessment:
  missing_perspectives:
    - upstream connection
prompt_sufficiency:
  information: insufficient
required_prompt_changes:
  - source を原文として渡す
findings: []
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "prompt-quality",
        "--criteria", "preanalysis sufficiency",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  capsys.readouterr()
  parsed_path = review_run_dir / "parsed" / "gemini-3.5-flash.round-1.yaml"
  parsed = yaml.safe_load(parsed_path.read_text(encoding="utf-8"))
  assert parsed["verdict"] == "insufficient"
  assert parsed["independent_reconstruction"]["judgment_items"][0]["item_id"] == "prompt_source_coverage"
  assert parsed["preanalysis_assessment"]["missing_perspectives"] == ["upstream connection"]
  assert parsed["prompt_sufficiency"]["information"] == "insufficient"
  assert parsed["required_prompt_changes"] == ["source を原文として渡す"]
  assert parsed["findings"] == []


def test_run_review_records_effective_prompt_metadata(tmp_path, monkeypatch, capsys):
  """run_review でも effective prompt のパスと sha256 を rounds.yaml に記録する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  effective_prompt = tmp_path / ".reviewcompass" / "effective-prompts" / "stage.prompt.md"
  effective_prompt.parent.mkdir(parents=True)
  effective_prompt.write_text("# Effective Prompt\n\nbody\n", encoding="utf-8")
  responses = {
    "anthropic-api": "findings: []\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "implementation",
        "--criteria", "criteria",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
        "--effective-prompt-path", str(effective_prompt),
      ]
    )

  assert exit_code == 0
  capsys.readouterr()
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert rounds["effective_prompt_path"] == str(effective_prompt)
  assert len(rounds["effective_prompt_sha256"]) == 64


def test_run_review_uses_criteria_file_and_records_prompt_artifact(
  tmp_path,
  monkeypatch,
):
  """criteria-file の本文を使い、実送信プロンプトを review-run に保存する。"""
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("契約本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Review Target\n\n"
    "commit instruction preflight の契約整合を確認する。\n"
    "git add より前に preflight が走ることを確認する。\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {"gemini-api": "findings: []\n"}

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "post_write_verification_google",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  model_result = rounds["model_results"][0]
  prompt_path = review_run_dir / model_result["prompt_path"]
  assert rounds["criteria"] == criteria_file.read_text(encoding="utf-8")
  assert rounds["criteria_source_path"] == str(criteria_file)
  assert rounds["criteria_source_sha256"] == hashlib.sha256(
    criteria_file.read_bytes()
  ).hexdigest()
  assert prompt_path.is_file()
  assert "git add より前" in prompt_path.read_text(encoding="utf-8")
  assert model_result["prompt_sha256"] == hashlib.sha256(
    prompt_path.read_bytes()
  ).hexdigest()


def test_run_review_blocks_vertical_review_when_source_materials_are_paths_only(
  tmp_path,
  monkeypatch,
  capsys,
):
  """縦方向監査で source materials がパスだけなら API 送信前に遮断する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "requirements.md"
  target.write_text("Requirement 13 本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Requirements Triad Review Target\n\n"
    "## Source Materials\n\n"
    "Use these source materials as upstream decision materials:\n\n"
    "- `docs/reviews/reopen-classification.md`\n"
    "- `docs/notes/integrated-design.md`\n\n"
    "## Required Check\n\n"
    "Check whether upstream purpose, responsibility boundaries, acceptance criteria, "
    "and forbidden actions were inherited into requirements.md.\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  provider_factory = _make_provider_factory({
    "anthropic-api": "findings: []\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  })

  with patch("tools.api_providers.run_review.get_provider", side_effect=provider_factory) as get_provider:
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "triad-review",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  captured = capsys.readouterr()
  assert exit_code == 1
  assert "vertical intent transfer prompt preflight failed" in captured.err
  assert "source materials are listed only as paths" in captured.err
  assert not get_provider.called
  assert not (review_run_dir / "prompts").exists()


def test_run_review_allows_vertical_review_with_structured_upstream_summary(
  tmp_path,
  monkeypatch,
):
  """縦方向監査でも上流要点が実体化されていれば API 送信できる。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "requirements.md"
  target.write_text("Requirement 13 本文\n", encoding="utf-8")
  criteria_file = tmp_path / "review-target.md"
  criteria_file.write_text(
    "# Requirements Vertical Intent Review\n\n"
    "## Source Materials\n\n"
    "- `docs/notes/upstream.md`\n\n"
    "## Upstream Structured Summary\n\n"
    "- purpose: 操作契約を機械可読にし、LLM の推測を減らす。\n"
    "- responsibility_boundaries: registry は read-only consumer、contract が正本。\n"
    "- acceptance_criteria: 19 required_action の effect_kind と approval_required を持つ。\n"
    "- forbidden_actions: source materials をパスだけで扱わない。承認不要操作を勝手に承認済みにしない。\n"
    "- unresolved_or_design_deferred_items: 複合操作の物理表現は design で確定する。\n"
    "- intended_target_phase_transfer: Requirement 13 に正本境界と承認要否を渡す。\n\n"
    "## Required Check\n\n"
    "Check whether upstream purpose, responsibility boundaries, acceptance criteria, "
    "and forbidden actions were inherited into requirements.md.\n",
    encoding="utf-8",
  )
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": "findings: []\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "triad-review",
        "--criteria-file", str(criteria_file),
        "--review-run-dir", str(review_run_dir),
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  assert len(rounds["model_results"]) == 3

