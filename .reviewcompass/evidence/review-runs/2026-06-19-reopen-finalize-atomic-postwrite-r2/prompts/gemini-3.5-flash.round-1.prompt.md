prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
reopen_finalize_atomic_recheck_and_record_post_write_check

# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

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

If there are no findings, return exactly:

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
tools/check-workflow-action.py
tests/tools/test_check_workflow_action.py
docs/operations/WORKFLOW_PRECHECK.md
docs/operations/WORKFLOW_PRECHECK_DETAILS.md
docs/operations/REOPEN_PROCEDURE.md
.reviewcompass/specs/workflow-management/spec.json
stages/completed/reopen-procedure-2026-06-19.yaml

# Target document
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
from check_workflow_action import commit_approval
from check_workflow_action.operation_preflight import run_preflight

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
    if (Path(cwd) / record_path).is_file():
      return []
    return [
      f"{_stage_ref(phase, stage)}.{predicate_name} の承認証跡がありません: "
      f"{record_path}"
    ]
  return _artifact_exists_reasons(cwd, feature, phase, stage, entry, predicate_name)


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
  effective_prompt = effective_prompt_for_next_action(cwd, next_action)
  if effective_prompt is not None:
    augmented["effective_prompt"] = materialize_effective_prompt(
      cwd,
      next_action,
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
    if is_deployment_independence_guard_target(filepath)
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
    if is_document_link_guard_target(filepath)
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
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    staged_files,
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


def select_reopen_next_action_fields(data, pending_gates):
  """reopen state から唯一の required_action と active gate 情報を選ぶ"""
  current_blocker = data.get("current_blocker")
  if current_blocker:
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
    action_fields = select_reopen_next_action_fields(data, pending_gates)
    feature_scope = reopen_feature_scope_from_data(data)
    return {
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
      "feature": feature_scope["required_feature_scope"],
      "required_feature_scope": feature_scope["required_feature_scope"],
      "direct_features": feature_scope["direct_features"],
      "indirect_features": feature_scope["indirect_features"],
      "feature_impact_scope_basis": feature_scope["feature_impact_scope_basis"],
      "phase": action_fields["phase"],
      "stage": action_fields["stage"],
      "reason": "reopen 手続きの進行中状態ファイルがあります",
    }
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
  elif args.subcommand == "reopen-finalize":
    sys.exit(cmd_reopen_finalize(args))
  elif args.subcommand == "review-wave-summary":
    sys.exit(cmd_review_wave_summary(args))
  elif args.subcommand == "operation-preflight":
    sys.exit(cmd_operation_preflight(args))
  elif args.subcommand == "commit-approval":
    sys.exit(cmd_commit_approval(args))
  elif args.subcommand == "decision-source-lint":
    sys.exit(cmd_decision_source_lint(args))
  else:
    parser.print_help(sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
  main()


## tests/tools/test_check_workflow_action.py

"""ワークフロー事前検査スクリプト tools/check-workflow-action.py の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md
対象範囲：spec-set サブコマンド（範囲案 2 のうち、MVP 第 1 ラウンドで先行実装）

TDD 規律（AGENTS.md 入口規律）に従い、本テストはスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_check_workflow_action -v
"""

import json
import hashlib
import importlib
import os
import pty
import shutil
import subprocess
import tempfile
import tty
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from tools.api_providers.review_triage import write_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"

FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def run_script(args, cwd):
  """check-workflow-action.py をサブプロセスで実行して結果を返す"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def run_script_with_tty_stdin(args, cwd, input_text):
  """stdin だけ PTY にして check-workflow-action.py を実行する"""
  if not input_text.endswith("\n"):
    input_text += "\n"
  master_fd, slave_fd = pty.openpty()
  try:
    tty.setraw(slave_fd)
    process = subprocess.Popen(
      ["python3", str(SCRIPT)] + list(args),
      cwd=str(cwd),
      stdin=slave_fd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
    )
    os.close(slave_fd)
    slave_fd = None
    os.write(master_fd, input_text.encode("utf-8"))
    stdout, stderr = process.communicate(timeout=10)
    return subprocess.CompletedProcess(
      ["python3", str(SCRIPT)] + list(args),
      process.returncode,
      stdout,
      stderr,
    )
  finally:
    if slave_fd is not None:
      os.close(slave_fd)
    if master_fd is not None:
      os.close(master_fd)


def _write_spec(cwd, feature, implementation_state):
  """next サブコマンド用の最小 spec.json を作る"""
  spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
  spec_dir.mkdir(parents=True, exist_ok=True)
  complete_five_stage = {
    "drafting": True,
    "triad-review": True,
    "review-wave": True,
    "alignment": True,
    "approval": True,
  }
  workflow_state = {
    "intent": {
      "drafting": True,
      "review": True,
      "approval": True,
      "reference": "stages/intent.yaml",
    },
    "feature-partitioning": {
      "candidate-proposal": True,
      "approval": True,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    },
    "requirements": dict(complete_five_stage),
    "design": dict(complete_five_stage),
    "tasks": dict(complete_five_stage),
    "implementation": dict(implementation_state),
  }
  spec = {
    "feature_name": feature,
    "language": "ja",
    "created_at": "2026-06-02T00:00:00+09:00",
    "updated_at": "2026-06-02T00:00:00+09:00",
    "workflow_state": workflow_state,
    "reopened": {},
    "recheck": {
      "upstream_change_pending": False,
      "impacted_downstream_phases": [],
    },
  }
  (spec_dir / "spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )


def _write_specs_for_next(cwd, states_by_feature):
  """指定されない feature は implementation 未着手として spec.json を作る"""
  untouched = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  _write_feature_dependency(
    cwd,
    "stages/feature-dependency.yaml",
    feature_order=list(FEATURE_ORDER),
  )
  for feature in FEATURE_ORDER:
    _write_spec(cwd, feature, states_by_feature.get(feature, untouched))


def _write_cross_feature_specs(
  cwd,
  intent_state,
  feature_partitioning_state,
  downstream_state=None,
):
  """cross-feature phase の状態を直接指定した spec.json を全 feature に作る"""
  downstream = downstream_state or {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  _write_feature_dependency(
    cwd,
    "stages/feature-dependency.yaml",
    feature_order=list(FEATURE_ORDER),
  )
  for feature in FEATURE_ORDER:
    spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = {
      "feature_name": feature,
      "language": "ja",
      "created_at": "2026-06-02T00:00:00+09:00",
      "updated_at": "2026-06-02T00:00:00+09:00",
      "workflow_state": {
        "intent": dict(intent_state),
        "feature-partitioning": dict(feature_partitioning_state),
        "requirements": dict(downstream),
        "design": dict(downstream),
        "tasks": dict(downstream),
        "implementation": dict(downstream),
      },
      "reopened": {},
      "recheck": {
        "upstream_change_pending": False,
        "impacted_downstream_phases": [],
      },
    }
    (spec_dir / "spec.json").write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )


def _write_phase_artifact(cwd, relative_path, text, timestamp):
  """phase 成果物を指定時刻で作る"""
  path = Path(cwd) / relative_path
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")
  os.utime(path, (timestamp, timestamp))


def _write_completed_phase_artifacts(cwd, timestamp=1000):
  """next 再展開検査用の完了済み成果物一式を作る"""
  _write_phase_artifact(cwd, "intent/INTENT.md", "intent\n", timestamp)
  _write_phase_artifact(
    cwd,
    "stages/feature-partitioning/2026-05-24-proposal.md",
    "feature partitioning\n",
    timestamp,
  )
  for feature in FEATURE_ORDER:
    for phase in ("requirements", "design", "tasks"):
      _write_phase_artifact(
        cwd,
        f".reviewcompass/specs/{feature}/{phase}.md",
        f"{feature} {phase}\n",
        timestamp,
      )
    _write_phase_artifact(
      cwd,
      f".reviewcompass/specs/{feature}/implementation-drafting.md",
      f"{feature} implementation drafting\n",
      timestamp,
    )


def _write_post_write_manifest(cwd, manifest_name, content):
  """post-write-verification manifest を作る"""
  manifest_dir = Path(cwd) / ".reviewcompass" / "post-write-verification"
  manifest_dir.mkdir(parents=True, exist_ok=True)
  (manifest_dir / manifest_name).write_text(
    yaml.safe_dump(content, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path):
  """ファイル内容の sha256 を返す"""
  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _staged_sha256_file(cwd, path):
  """staged blob 内容の sha256 を返す"""
  result = subprocess.run(
    ["git", "show", f":{path}"],
    cwd=str(cwd),
    check=True,
    capture_output=True,
  )
  return hashlib.sha256(result.stdout).hexdigest()


def _write_review_run(cwd, run_id, models, omit_summary=False, omit_triage_model=None):
  """post-write review run の最小成果物を作る"""
  run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)

  target = Path(cwd) / "docs" / "notes" / "review-target.md"
  target.parent.mkdir(parents=True, exist_ok=True)
  if not target.exists():
    target.write_text("レビュー対象\n", encoding="utf-8")

  model_results = []
  triage_items = []
  summary_models = []
  for model in models:
    raw_path = raw_dir / f"{model}.round-1.txt"
    raw_path.write_text(f"{model} raw response\n", encoding="utf-8")
    raw_sha = _sha256_file(raw_path)
    model_results.append({
      "model_id": model,
      "provider": f"{model}-provider",
      "role": model,
      "treatment": model,
      "invocation_path": "api",
      "raw_path": f"raw/{model}.round-1.txt",
      "raw_sha256": raw_sha,
      "parsed_path": None,
      "parsed_sha256": None,
      "parse_status": "parse_failed",
      "follow_up_action": "triage",
    })
    if model != omit_triage_model:
      triage_items.append({
        "finding_id": f"{run_id}-{model}-001",
        "source_model": model,
        "source_round": f"{run_id}-round-1",
        "source_raw_path": f"raw/{model}.round-1.txt",
        "source_parsed_path": None,
        "severity_original": "INFO",
        "severity_normalized": "INFO",
        "final_label": "leave-as-is",
        "decision_status": "decided",
        "target_location": "docs/notes/review-target.md",
        "plain_language_summary": "問題なし。",
        "decision_reason": "テスト用の完了記録。",
        "applied_files": [],
        "superseded_by": None,
      })
    summary_models.append({
      "model_id": model,
      "raw_path": f"raw/{model}.round-1.txt",
      "parse_status": "parse_failed",
      "triage_status": "triaged",
      "findings_count": 1,
      "must_fix_count": 0,
      "should_fix_count": 0,
      "leave_as_is_count": 1,
      "human_required_count": 0,
    })

  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
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
        "round_id": f"{run_id}-round-1",
        "purpose": "post_write_verification",
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
          },
        ],
        "model_results": model_results,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "items": triage_items,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  if not omit_summary:
    (run_dir / "model-result-summary.yaml").write_text(
      yaml.safe_dump(
        {
          "run_id": run_id,
          "models": summary_models,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

  return run_dir


def _assert_script_invoked(testcase, result):
  """スクリプトが実際に起動したことを確認する厳密性確保のヘルパー

  Python はスクリプトファイルが存在しないとき exit 2 を返す。これは仕様 §7.1 の
  逸脱判定 exit 2 と一致するため、判定だけでは「スクリプト未実装」と
  「正当な逸脱検出」を区別できない。本ヘルパーは stderr にファイルなし
  エラーが含まれないことを確認することで両者を区別し、実装前の偶然通過を
  防ぐ。実装完了後は無効化されない（実害なく動作し続ける）。
  """
  for marker in ("No such file or directory", "can't open file"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"スクリプトが起動できていない（実装前の状態か）。stderr: {result.stderr}",
    )


def _write_autonomous_parallel_plan(cwd, overrides=None):
  """自律・並列モード実行計画の最小正常形を作る"""
  overrides = overrides or {}
  run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / "ap-001-review"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)
  raw_path = raw_dir / "gpt-5.4.round-1.txt"
  raw_path.write_text("raw response\n", encoding="utf-8")
  raw_sha = _sha256_file(raw_path)
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "model_results": [
          {
            "model_id": "gpt-5.4",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "raw_sha256": raw_sha,
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
        "triage_status": "decided",
        "items": [
          {
            "finding_id": "finding-a",
            "decision_status": "decided",
            "source_raw_path": "raw/gpt-5.4.round-1.txt",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  plan = {
    "mode": "autonomous_parallel",
    "run_id": "ap-001",
    "authorization": {
      "approved_by": "user",
      "approval_record_path": "docs/notes/approval.md",
      "summary_presented_to_user": True,
      "triage_presented_to_user": True,
    },
    "tasks": [
      {
        "task_id": "task-a",
        "source_finding_ids": ["finding-a"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/a.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_a.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      },
      {
        "task_id": "task-b",
        "source_finding_ids": ["finding-b"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/b.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_b.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      },
    ],
    "execution_evidence": {
      "review_run_dir": "docs/notes/review-runs/ap-001-review",
      "required_raw_paths": ["raw/gpt-5.4.round-1.txt"],
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
      "ledger_path": "docs/logs/autonomous-parallel/ap-001.yaml",
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
  for key, value in overrides.items():
    if value is None:
      plan.pop(key, None)
    else:
      plan[key] = value

  path = Path(cwd) / "autonomous-parallel-plan.yaml"
  path.write_text(
    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


class AutonomousParallelPlanTests(unittest.TestCase):
  """自律・並列モード実行計画の機械ガード"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def test_valid_plan_returns_zero(self):
    """正常な実行計画は OK になる"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["task_count"], 2)

  def test_valid_plan_writes_history_ledger(self):
    """正常な実行計画は後追い用の履歴台帳を書き出す"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    self.assertTrue(ledger_path.exists())
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["run_id"], "ap-001")
    self.assertEqual(ledger["verdict"], "OK")
    self.assertEqual(ledger["task_ids"], ["task-a", "task-b"])
    self.assertEqual(ledger["history"]["record_decision_basis"], True)

  def test_missing_authorization_returns_two(self):
    """人間または proxy_model の承認記録がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"authorization": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("authorization", "\n".join(data["reasons"]))

  def test_subthread_without_separate_worktree_returns_two(self):
    """別スレッド実装が分離 worktree でなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][0]["assignee"]["worktree_policy"] = "same_repo_write"
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("separate_worktree", "\n".join(data["reasons"]))

  def test_overlapping_parallel_paths_returns_two(self):
    """依存関係のない並列タスクが同じパスを書く場合は逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][1]["allowed_paths"] = ["src/a.py"]
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("allowed_paths", "\n".join(data["reasons"]))

  def test_missing_execution_evidence_returns_two(self):
    """raw/triage 証跡への参照がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"execution_evidence": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("execution_evidence", "\n".join(data["reasons"]))

  def test_missing_required_raw_path_returns_two(self):
    """required_raw_paths の raw が欠けていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    (cwd / "docs" / "notes" / "review-runs" / "ap-001-review" / "raw" / "gpt-5.4.round-1.txt").unlink()

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("required_raw_paths", "\n".join(data["reasons"]))

  def test_human_required_triage_returns_two(self):
    """未判断 triage item が残っていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    triage_path = cwd / "docs" / "notes" / "review-runs" / "ap-001-review" / "triage.yaml"
    triage = yaml.safe_load(triage_path.read_text(encoding="utf-8"))
    triage["items"][0]["decision_status"] = "human_required"
    triage_path.write_text(
      yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("human_required", "\n".join(data["reasons"]))

  def test_main_session_parallel_writer_requires_output_only_boundary(self):
    """main_session/same_worktree の並列タスクは出力専用でなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][0]["assignee"] = {
      "kind": "main_session",
      "worktree_policy": "same_worktree",
    }
    plan["tasks"][0]["writes_repo_diff"] = True
    plan["tasks"][0]["output_only"] = False
    plan["outputs_policy"]["implementation_diff"] = "forbidden"
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("output_only", "\n".join(data["reasons"]))

  def test_main_session_same_worktree_commit_candidate_writer_is_allowed_when_serialized(self):
    """commit_candidate の直列 main_session 実装タスクは履歴付きで許可する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    for index, task in enumerate(plan["tasks"]):
      task["assignee"] = {
        "kind": "main_session",
        "worktree_policy": "same_worktree",
      }
      task["writes_repo_diff"] = True
      task["output_only"] = False
      if index > 0:
        task["depends_on"] = [plan["tasks"][index - 1]["task_id"]]
    plan["execution_evidence"] = {
      "completed_tasks": ["task-a", "task-b"],
      "parallelized_operations": ["context_reads", "verification_checks"],
      "human_required_count": 0,
    }
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["execution_evidence"]["human_required_count"], 0)

  def test_missing_integration_gate_returns_two(self):
    """統合ゲートが不足していれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {
        "integration_gate": {
          "requires_main_session_review": True,
          "requires_diff_scope_check": True,
          "requires_tests": True,
        },
      },
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("requires_decision_basis_review", "\n".join(data["reasons"]))

  def test_missing_history_returns_two(self):
    """履歴保存設定がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"history": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("history", "\n".join(data["reasons"]))

  def test_template_command_writes_valid_autonomous_plan(self):
    """テンプレート生成コマンドはそのまま検査可能な実行計画を書く"""
    cwd = Path(self.tmpdir)
    out_path = cwd / "plan.yaml"

    result = run_script(
      [
        "autonomous-plan-template",
        "--run-id", "ap-template-001",
        "--out", str(out_path),
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(out_path.exists())

    plan = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    self.assertEqual(plan["mode"], "autonomous_parallel")
    self.assertEqual(plan["run_id"], "ap-template-001")
    self.assertEqual(
      plan["history"]["ledger_path"],
      "docs/logs/autonomous-parallel/ap-template-001.yaml",
    )

    check = run_script(["autonomous-plan", str(out_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

  def test_record_integration_updates_history_ledger(self):
    """統合結果記録コマンドは既存台帳に統合結果を追記する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["integration_result"]["status"], "completed")
    self.assertEqual(
      ledger["integration_result"]["decision"],
      "main_session accepted scoped diff",
    )
    self.assertEqual(
      ledger["integration_result"]["tests"],
      "python3 -m unittest tests.tools.test_check_workflow_action -v",
    )
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["completed_tasks"],
      ["task-a", "task-b"],
    )

  def test_autonomous_plan_preserves_existing_integration_result(self):
    """autonomous-plan 再実行は既存の統合結果を消さない"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)

    recheck = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, recheck)
    self.assertEqual(recheck.returncode, 0, recheck.stderr)
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["integration_result"]["status"], "completed")
    self.assertEqual(
      ledger["integration_result"]["decision"],
      "main_session accepted scoped diff",
    )

  def test_autonomous_plan_preserves_existing_execution_evidence_snapshot(self):
    """autonomous-plan 再実行は実行後証跡 snapshot を巻き戻さない"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"].append(
      {
        "task_id": "task-c",
        "source_finding_ids": ["finding-c"],
        "assignee": {
          "kind": "main_session",
          "worktree_policy": "same_worktree",
        },
        "allowed_paths": ["src/c.py"],
        "forbidden_paths": [".git/"],
        "depends_on": ["task-b"],
        "expected_tests": ["pytest tests/test_c.py"],
        "stop_conditions": ["important_decision_requires_approval"],
        "writes_repo_diff": True,
        "output_only": False,
      }
    )
    plan["execution_evidence"] = {
      "completed_tasks": ["task-a", "task-b", "task-c"],
      "parallelized_operations": ["context_reads", "ledger_audit"],
      "human_required_count": 0,
    }
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    stale_plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    stale_plan["execution_evidence"]["completed_tasks"] = ["task-a", "task-b"]
    stale_plan["execution_evidence"]["parallelized_operations"] = ["context_reads"]
    plan_path.write_text(
      yaml.safe_dump(stale_plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    recheck = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, recheck)
    self.assertEqual(recheck.returncode, 0, recheck.stderr)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["completed_tasks"],
      ["task-a", "task-b", "task-c"],
    )
    self.assertEqual(
      ledger["execution_evidence_snapshot"]["parallelized_operations"],
      ["context_reads", "ledger_audit"],
    )

  def test_autonomous_ledger_audit_passes_without_plan_file(self):
    """デプロイ後監査は plan なしで ledger 単独から判定する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan_path.unlink()

    audit = run_script(["autonomous-ledger-audit", str(ledger_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, audit)
    self.assertEqual(audit.returncode, 0, audit.stderr)
    data = json.loads(audit.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["plan_required"], False)

  def test_autonomous_ledger_audit_requires_execution_snapshot(self):
    """台帳単独監査は実行後 snapshot が欠けていれば逸脱にする"""
    cwd = Path(self.tmpdir)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(
      yaml.safe_dump(
        {
          "run_id": "ap-001",
          "mode": "autonomous_parallel",
          "verdict": "OK",
          "exit_code": 0,
          "task_ids": ["task-a"],
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

    audit = run_script(["autonomous-ledger-audit", str(ledger_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, audit)
    self.assertEqual(audit.returncode, 2)
    data = json.loads(audit.stdout)
    self.assertIn("execution_evidence_snapshot", "\n".join(data["reasons"]))


class SpecSetExitCodeTests(unittest.TestCase):
  """spec-set サブコマンドの終了コード判定

  仕様 §6.1 spec-set の判定ロジック、§7.1 終了コード体系を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    """fixture を一時ディレクトリにコピーしてそのパスを返す"""
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_approval_with_alignment_true_returns_zero(self):
    """ケース A：requirements の前段がすべて true、approval を true にする → exit 0

    仕様 §6.1 段の依存チェック：alignment=true なら approval=true に進める
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"alignment=true なので approval=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_spec_set_blocks_when_in_progress_file_exists(self):
    """stages/in-progress が非空なら spec-set は不可逆操作として exit 2"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_spec_set_allows_reopen_pending_gate_rollback(self):
    """reopen 第1過程の pending gate 差し戻しは in-progress 中でも許可する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-09.yaml").write_text(
      "process_id: reopen-procedure\n"
      "step_number: 1\n"
      "next_step: 第1過程：判定とフラグ差し戻し\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("reopen", result.stdout)

  def test_spec_set_allows_reopen_pending_gate_completion(self):
    """reopen 第3過程の pending gate 完了は in-progress 中でも許可する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-09.yaml").write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("[VERDICT] WARN", result.stdout)
    self.assertNotIn("[VERDICT] DEVIATION", result.stdout)

  def test_spec_set_blocks_unimplemented_completion_predicate(self):
    """file_exists completion_predicate の対象ファイルがなければ true にしない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": {
                "type": "file_exists",
                "path": "docs/approvals/requirements.md",
              },
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("completion_predicate", result.stdout)

  def test_spec_set_allows_file_exists_completion_predicate_when_file_exists(self):
    """file_exists completion_predicate の対象ファイルがあれば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("承認証跡\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": {
                "type": "file_exists",
                "path": "docs/approvals/requirements.md",
              },
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_artifact_exists_when_artifact_missing(self):
    """artifact_exists は証跡ファイル欠落時に true 化を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "completion_predicate": "artifact_exists",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("artifact_exists", result.stdout)

  def test_spec_set_allows_artifact_exists_when_artifact_exists(self):
    """artifact_exists は証跡ファイル存在時に通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("承認証跡\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "completion_predicate": "artifact_exists",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_sections_predicate_when_section_missing(self):
    """artifact_exists_and_sections_present は必須節欠落時に遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("# Introduction\n\n本文\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "required_sections": ["Introduction", "Decision"],
              "completion_predicate": "artifact_exists_and_sections_present",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("Decision", result.stdout)

  def test_spec_set_allows_sections_predicate_when_sections_present(self):
    """artifact_exists_and_sections_present は証跡と必須節が揃えば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.md"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text(
      "# Introduction\n\n本文\n\n## Decision\n\n承認\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": ["docs/approvals/requirements.md"],
              "required_sections": ["Introduction", "Decision"],
              "completion_predicate": "artifact_exists_and_sections_present",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_author_reviewer_predicate_when_identity_matches(self):
    """author/reviewer 異名述語は同一 identity を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    review_path = (
      cwd / ".reviewcompass" / "specs" / "foundation" / "reviews"
      / "2026-06-04-requirements-triad-review.md"
    )
    review_path.parent.mkdir(parents=True)
    review_path.write_text(
      "---\n"
      "author:\n"
      "  identity: main-session\n"
      "reviewer:\n"
      "  identity: main-session\n"
      "  separation_from_author: false\n"
      "---\n"
      "# 主役レビュー\n\n# 敵対役レビュー\n\n# 判定役レビュー\n\n# 統合\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": [
                ".reviewcompass/specs/{feature}/reviews/*-requirements-triad-review.md",
              ],
              "required_sections": [
                "主役レビュー",
                "敵対役レビュー",
                "判定役レビュー",
                "統合",
              ],
              "completion_predicate": (
                "artifact_exists_and_sections_present_and_author_reviewer_distinct"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("author.identity", result.stdout)

  def test_spec_set_allows_author_reviewer_predicate_when_identity_distinct(self):
    """author/reviewer 異名述語は異なる identity なら通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    review_path = (
      cwd / ".reviewcompass" / "specs" / "foundation" / "reviews"
      / "2026-06-04-requirements-triad-review.md"
    )
    review_path.parent.mkdir(parents=True)
    review_path.write_text(
      "---\n"
      "author:\n"
      "  identity: main-session\n"
      "reviewer:\n"
      "  identity: independent-reviewer\n"
      "  separation_from_author: true\n"
      "---\n"
      "# 主役レビュー\n\n# 敵対役レビュー\n\n# 判定役レビュー\n\n# 統合\n",
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "artifact_paths": [
                ".reviewcompass/specs/{feature}/reviews/*-requirements-triad-review.md",
              ],
              "required_sections": [
                "主役レビュー",
                "敵対役レビュー",
                "判定役レビュー",
                "統合",
              ],
              "completion_predicate": (
                "artifact_exists_and_sections_present_and_author_reviewer_distinct"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_all_features_predicate_when_feature_incomplete(self):
    """全機能 drafting/triad-review 述語は未完了 feature があれば遮断する"""
    cwd = Path(self.tmpdir) / "all-features-incomplete"
    cwd.mkdir()
    _write_specs_for_next(cwd, {})
    spec_path = cwd / ".reviewcompass" / "specs" / "runtime" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["workflow_state"]["requirements"]["triad-review"] = False
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "review-wave",
              "completion_predicate": (
                "all_features_drafting_and_triad_review_completed"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "review-wave", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("runtime.requirements.triad-review", result.stdout)

  def test_spec_set_allows_all_features_predicate_when_features_complete(self):
    """全機能 drafting/triad-review 述語は全 feature 完了時に通過する"""
    cwd = Path(self.tmpdir) / "all-features-complete"
    cwd.mkdir()
    _write_specs_for_next(cwd, {})
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "review-wave",
              "completion_predicate": (
                "all_features_drafting_and_triad_review_completed"
              ),
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "review-wave", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_alignment_predicate_when_unresolved_findings_exist(self):
    """cross_spec_alignment_passed は未消化所見があれば遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    report_path = cwd / "docs" / "alignment" / "requirements.yaml"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
      yaml.safe_dump(
        {"status": "pass", "unresolved_findings": 1},
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "alignment",
              "artifact_paths": ["docs/alignment/requirements.yaml"],
              "completion_predicate": "cross_spec_alignment_passed",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("未消化所見 0 件", result.stdout)

  def test_spec_set_allows_alignment_predicate_when_passed(self):
    """cross_spec_alignment_passed は pass かつ未消化所見 0 件なら通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    report_path = cwd / "docs" / "alignment" / "requirements.yaml"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
      yaml.safe_dump(
        {"status": "pass", "unresolved_findings": 0},
        allow_unicode=True,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "alignment",
              "artifact_paths": ["docs/alignment/requirements.yaml"],
              "completion_predicate": "cross_spec_alignment_passed",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_human_approval_predicate_when_record_missing(self):
    """explicit_human_approval_recorded は承認証跡欠落時に遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "approval_record_path": "docs/approvals/requirements.yaml",
              "completion_predicate": "explicit_human_approval_recorded",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("承認証跡", result.stdout)

  def test_spec_set_allows_human_approval_predicate_when_record_exists(self):
    """explicit_human_approval_recorded は承認証跡があれば通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.yaml"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text("approved_by: user\n", encoding="utf-8")
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "approval_record_path": "docs/approvals/requirements.yaml",
              "completion_predicate": "explicit_human_approval_recorded",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_spec_set_blocks_depends_on_predicate_when_kind_invalid(self):
    """depends_on_resolves_correctly は不正な依存種別を遮断する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "feature-dependency.yaml").write_text(
      yaml.safe_dump(
        {"features": {"runtime": {"depends_on": {"foundation": "optional"}}}},
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": "depends_on_resolves_correctly",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("hard または review", result.stdout)

  def test_spec_set_allows_depends_on_predicate_when_kind_valid(self):
    """depends_on_resolves_correctly は list/object の正しい依存構造を通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "feature-dependency.yaml").write_text(
      yaml.safe_dump(
        {
          "features": {
            "foundation": {"depends_on": []},
            "runtime": {"depends_on": {"foundation": "hard"}},
            "evaluation": {"depends_on": ["runtime"]},
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    (stages_dir / "requirements.yaml").write_text(
      yaml.safe_dump(
        {
          "phase": "requirements",
          "stages": [
            {
              "name": "approval",
              "completion_predicate": "depends_on_resolves_correctly",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_approval_with_alignment_false_returns_two(self):
    """ケース B：alignment が false で approval を true にする → exit 2

    仕様 §6.1 段の依存チェック：alignment=false なら approval=true は逸脱
    """
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"alignment=false なので approval=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_design_drafting_with_requirements_approved_returns_zero(self):
    """ケース C：requirements.approval=true で design.drafting=true にする → exit 0

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=true なら次フェーズの drafting に進める
    """
    cwd = self._copy_fixture("case-c-approved")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"requirements.approval=true なので design.drafting=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_design_drafting_with_requirements_not_approved_returns_two(self):
    """ケース D：requirements.approval=false で design.drafting=true にする → exit 2

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=false なら次フェーズの drafting は逸脱
    """
    cwd = self._copy_fixture("case-d-design-blocked")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"requirements.approval=false なので design.drafting=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_setting_impacted_recheck_phase_to_true_returns_two(self):
    """recheck pending の影響対象 phase は spec-set true で完了扱いにできない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"] = {
      "upstream_change_pending": True,
      "impacted_downstream_phases": ["requirements"],
    }
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("recheck", result.stdout)

  def test_setting_true_stage_to_false_returns_one(self):
    """ケース E：現状 true の段を false に戻す → exit 1（reopen 警告）

    仕様 §6.1 new-value が false の場合：当該段が true だったら reopen 警告
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 1,
      f"true → false は reopen 警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_setting_upstream_stage_to_false_with_downstream_true_returns_one(self):
    """上流段を false に戻す時、下流段が true のままでも reopen 警告に留める"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["workflow_state"]["requirements"]["approval"] = True
    spec["workflow_state"]["design"]["drafting"] = True
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )

    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("reopen", result.stdout)


class SpecSetOutputTests(unittest.TestCase):
  """spec-set サブコマンドの出力形式

  仕様 §7.2 人間可読出力、§7.3 JSON 出力を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_deviation_output_contains_verdict_keyword(self):
    """逸脱出力に [VERDICT] DEVIATION が含まれる（仕様 §7.2）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱時の出力に DEVIATION の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )

  def test_ok_output_contains_verdict_keyword(self):
    """通過出力は最小の OK 行だけにする（仕様 §7.2）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "OK", result.stdout,
      f"通過時の出力に OK の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )
    self.assertNotIn("[CURRENT STATE]", result.stdout)
    self.assertNotIn("[REASON]", result.stdout)

  def test_json_output_with_flag_for_ok(self):
    """--json で OK 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["exit_code"], 0)
    self.assertIn("action", data)
    self.assertIn("current_state", data)

  def test_json_output_with_flag_for_deviation(self):
    """--json で DEVIATION 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["exit_code"], 2)
    self.assertGreater(
      len(data["reasons"]), 0,
      "逸脱時は reasons に 1 件以上の理由が含まれるべき",
    )


class SpecSetLoggingTests(unittest.TestCase):
  """ログ取得（MVP 必須、仕様 §8）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_log_file_is_appended_after_invocation(self):
    """スクリプト実行後にログファイルが追記される（仕様 §8.1 JSON Lines 形式）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    self.assertFalse(log_path.exists(), "事前にログファイルは存在しない前提")
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    self.assertTrue(
      log_path.exists(),
      "スクリプト実行後にログファイルが作成されるべき",
    )
    log_content = log_path.read_text()
    self.assertGreater(
      len(log_content.strip()), 0,
      "ログに 1 行以上記録されるべき",
    )
    log_entry = json.loads(log_content.strip().splitlines()[0])
    self.assertIn("timestamp", log_entry)
    self.assertIn("action", log_entry)
    self.assertIn("verdict", log_entry)
    self.assertIn("exit_code", log_entry)

  def test_rationale_is_recorded_in_log(self):
    """spec-set で --rationale を渡すとログに記録される（仕様 §5.1）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    rationale = "利用者承認「ア」によりテストとして起動"
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--rationale", rationale,
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    log_entry = json.loads(log_path.read_text().strip().splitlines()[0])
    self.assertEqual(
      log_entry["action"]["args"]["rationale"], rationale,
      "ログの action.args.rationale に渡した値が記録されるべき",
    )


class SpecSetArgumentValidationTests(unittest.TestCase):
  """引数妥当性の検査（仕様 §5.1）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_invalid_feature_name_returns_nonzero(self):
    """存在しない機能名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "nonexistent-feature", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しない feature は判定不能で非 0 終了すべき",
    )

  def test_invalid_phase_returns_nonzero(self):
    """無効なフェーズ名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "nonexistent-phase", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しないフェーズは判定不能で非 0 終了すべき",
    )

  def test_invalid_value_returns_nonzero(self):
    """true／false 以外の値 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "maybe"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "true／false 以外の値は引数エラーで非 0 終了すべき",
    )


class NextNavigationTests(unittest.TestCase):
  """next サブコマンドのワークフローナビゲーション判定"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _commit_cross_feature_baseline(
    self,
    cwd,
    intent_state,
    feature_partitioning_state,
  ):
    _init_git_repo(cwd)
    _write_cross_feature_specs(cwd, intent_state, feature_partitioning_state)
    subprocess.run(
      ["git", "add", "."],
      cwd=str(cwd),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "cross feature baseline"],
      cwd=str(cwd),
      check=True,
      capture_output=True,
    )

  def test_next_returns_commit_stop_point_after_intent_approval_dirty(self):
    """通常 workflow の intent.approval 完了直後は次 phase へ進まず commit 停止点を返す"""
    cwd = Path(self.tmpdir)
    intent_before = {
      "drafting": True,
      "review": True,
      "approval": False,
      "reference": "stages/intent.yaml",
    }
    feature_partitioning = {
      "candidate-proposal": False,
      "approval": False,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    }
    self._commit_cross_feature_baseline(cwd, intent_before, feature_partitioning)
    intent_after = dict(intent_before)
    intent_after["approval"] = True
    _write_cross_feature_specs(cwd, intent_after, feature_partitioning)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "commit_stop_point")
    self.assertEqual(action["required_action"], "commit_stop_point")
    self.assertEqual(action["blocked_by"]["type"], "workflow_phase_end")
    self.assertEqual(action["blocked_by"]["phase"], "intent")
    self.assertEqual(action["blocked_by"]["stage"], "approval")
    self.assertEqual(action["blocked_by"]["kind"], "phase_approval_complete")

  def test_next_returns_commit_stop_point_after_feature_partitioning_approval_dirty(self):
    """通常 workflow の feature-partitioning.approval 完了直後は requirements へ進まず commit 停止点を返す"""
    cwd = Path(self.tmpdir)
    intent_complete = {
      "drafting": True,
      "review": True,
      "approval": True,
      "reference": "stages/intent.yaml",
    }
    partitioning_before = {
      "candidate-proposal": True,
      "approval": False,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    }
    self._commit_cross_feature_baseline(cwd, intent_complete, partitioning_before)
    partitioning_after = dict(partitioning_before)
    partitioning_after["approval"] = True
    _write_cross_feature_specs(cwd, intent_complete, partitioning_after)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "commit_stop_point")
    self.assertEqual(action["required_action"], "commit_stop_point")
    self.assertEqual(action["blocked_by"]["type"], "workflow_phase_end")
    self.assertEqual(action["blocked_by"]["phase"], "feature-partitioning")
    self.assertEqual(action["blocked_by"]["stage"], "approval")
    self.assertEqual(action["blocked_by"]["kind"], "phase_approval_complete")

  def test_next_continues_after_cross_feature_commit_stop_point_is_clean(self):
    """phase 終端が既に commit 済みなら停止点を返し続けない"""
    cwd = Path(self.tmpdir)
    intent_complete = {
      "drafting": True,
      "review": True,
      "approval": True,
      "reference": "stages/intent.yaml",
    }
    feature_partitioning = {
      "candidate-proposal": False,
      "approval": False,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    }
    self._commit_cross_feature_baseline(cwd, intent_complete, feature_partitioning)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "cross_feature_stage")
    self.assertEqual(data["next_action"]["phase"], "feature-partitioning")
    self.assertEqual(data["next_action"]["stage"], "candidate-proposal")

  def test_next_returns_evaluation_implementation_drafting_after_runtime_triad_review(self):
    """runtime triad-review 完了後は evaluation implementation drafting を返す"""
    cwd = Path(self.tmpdir)
    runtime_done = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    foundation_done = dict(runtime_done)
    _write_specs_for_next(
      cwd,
      {
        "foundation": foundation_done,
        "runtime": runtime_done,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "evaluation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertIn(
      "docs/operations/WORKFLOW_NAVIGATION.md",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      "docs/disciplines/discipline_workflow_state_truth_source.md",
      data["next_action"]["required_disciplines"],
    )

  def test_next_completed_from_external_app_root_fixture(self):
    """ReviewCompass repo 外の対象 app root でも completed を判定できる"""
    cwd = Path(self.tmpdir) / "external-app"
    cwd.mkdir()
    done = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(
      cwd,
      {feature: done for feature in FEATURE_ORDER},
    )
    _write_completed_phase_artifacts(cwd)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "completed")
    self.assertEqual(data["next_action"]["reason"], "すべての workflow_state が完了しています")
    self.assertFalse((REPO_ROOT / ".reviewcompass" / "specs" / "external-app").exists())

  def test_next_detects_intent_update_requires_reopen_classification(self):
    """完了済み workflow で intent が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      "intent/INTENT.md",
      "intent updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["phase"], "feature-partitioning")
    self.assertEqual(data["next_action"]["stage"], "candidate-proposal")
    self.assertEqual(data["next_action"]["upstream_phase"], "intent")
    self.assertEqual(data["next_action"]["reopen_trigger"], "N-0")
    self.assertEqual(
      data["next_action"]["reason"],
      "完了済み workflow で intent 成果物が feature-partitioning 成果物より新しいため、reopen 分類が必要です",
    )

  def test_next_detects_requirements_update_requires_reopen_classification(self):
    """完了済み workflow で requirements が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      ".reviewcompass/specs/foundation/requirements.md",
      "foundation requirements updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "design")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(data["next_action"]["upstream_phase"], "requirements")
    self.assertEqual(data["next_action"]["reopen_trigger"], "R-0")

  def test_next_does_not_redetect_completed_feature_partitioning_reopen(self):
    """完了済み reopen が同じ feature-partitioning→requirements を覆うなら再要求しない"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      "stages/feature-partitioning/2026-05-24-proposal.md",
      "feature partitioning updated\n",
      timestamp=2000,
    )
    completed = cwd / "stages" / "completed" / "reopen-procedure-2026-06-09.yaml"
    completed.parent.mkdir(parents=True, exist_ok=True)
    completed.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "next_step: （完了。再オープン手続き終了）\n"
      "current_blocker: null\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: requirements alignment を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"],
      "reopen_classification_required",
      data["next_action"],
    )

  def test_next_detects_tasks_update_requires_reopen_classification(self):
    """完了済み workflow で tasks が新しければ reopen 分類を要求する"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_completed_phase_artifacts(cwd, timestamp=1000)
    _write_phase_artifact(
      cwd,
      ".reviewcompass/specs/foundation/tasks.md",
      "foundation tasks updated\n",
      timestamp=2000,
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_classification_required")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(data["next_action"]["upstream_phase"], "tasks")
    self.assertEqual(data["next_action"]["reopen_trigger"], "A-0")

  def test_next_triad_review_reports_review_run_disciplines(self):
    """triad-review 直前に読むべき review-run/proxy 規律を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(
      cwd,
      {
        "foundation": {
          "drafting": True,
          "triad-review": False,
          "review-wave": False,
          "alignment": False,
          "approval": False,
        },
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    self.assertIn(
      "docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      data["next_action"]["required_disciplines"],
    )
    self.assertEqual(
      data["next_action"]["effective_prompt"]["effective_prompt_policy"],
      "one_effective_prompt_per_decision_point",
    )
    self.assertIn(
      {"group": "next_action_kind", "id": "stage"},
      data["next_action"]["effective_prompt"]["decision_point_refs"],
    )
    self.assertIn(
      {"group": "workflow_stage", "id": "triad-review"},
      data["next_action"]["effective_prompt"]["decision_point_refs"],
    )
    self.assertIn(
      "docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      data["next_action"]["effective_prompt"]["prompt_source_refs"],
    )
    prompt_path = cwd / data["next_action"]["effective_prompt"]["effective_prompt_path"]
    self.assertTrue(prompt_path.is_file())
    self.assertEqual(
      data["next_action"]["effective_prompt"]["effective_prompt_sha256"],
      _sha256_file(prompt_path),
    )
    self.assertTrue(
      data["next_action"]["effective_prompt"]["effective_prompt_loaded"],
    )
    prompt_text = prompt_path.read_text(encoding="utf-8")
    self.assertIn("# Effective Prompt", prompt_text)
    self.assertIn("docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2", prompt_text)

  def test_next_fails_closed_when_effective_prompt_source_is_missing(self):
    """effective prompt の元資料が読めない判定点は fail-closed とする"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    map_path = cwd / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(
      yaml.safe_dump(
        {
          "default": ["docs/operations/WORKFLOW_NAVIGATION.md"],
          "decision_points": {
            "next_action_kind": [
              {
                "id": "stage",
                "prompt_source_refs": ["docs/missing-effective-prompt-source.md"],
                "effective_prompt_policy": "one_effective_prompt_per_decision_point",
              }
            ]
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(
      data["next_action"]["effective_prompt"]["effective_prompt_loaded"],
    )
    self.assertIn(
      "effective prompt の元資料をすべて読めません",
      data["reasons"],
    )

  def test_operation_prompt_commit_outputs_card_and_effective_prompt(self):
    """commit 直前の操作 prompt は共通カードのみを参照し adapter_card フィールドを持たない"""
    cwd = Path(self.tmpdir)

    result = run_script(["operation-prompt", "commit", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation"], "commit")
    self.assertEqual(
      data["required_operation_card"],
      "docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card",
    )
    self.assertNotIn("adapter_card", data)
    self.assertEqual(
      data["effective_prompt"]["decision_point_refs"],
      [{"group": "operation_prompt", "id": "commit"}],
    )
    self.assertIn(
      "docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card",
      data["effective_prompt"]["prompt_source_refs"],
    )
    self.assertNotIn(
      "docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md#3-commit",
      data["effective_prompt"]["prompt_source_refs"],
    )
    prompt_path = cwd / data["effective_prompt"]["effective_prompt_path"]
    self.assertTrue(prompt_path.is_file())
    self.assertTrue(data["effective_prompt"]["effective_prompt_loaded"])
    self.assertEqual(
      data["effective_prompt"]["effective_prompt_sha256"],
      _sha256_file(prompt_path),
    )

  def test_next_triad_review_reports_target_and_review_run_inputs(self):
    """triad-review 直前に読む対象文書と review-run 成果物を抽象入力として返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(
      cwd,
      {
        "foundation": {
          "drafting": True,
          "triad-review": False,
          "review-wave": False,
          "alignment": False,
          "approval": False,
        },
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "foundation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    required_inputs = {
      item["id"]: item
      for item in data["next_action"]["required_inputs"]
    }
    self.assertEqual(
      required_inputs["target_feature_documents"]["paths"],
      [
        ".reviewcompass/specs/foundation/spec.json",
        ".reviewcompass/specs/foundation/requirements.md",
        ".reviewcompass/specs/foundation/design.md",
        ".reviewcompass/specs/foundation/tasks.md",
      ],
    )
    self.assertEqual(
      required_inputs["triad_review_run_artifacts"]["base_path_pattern"],
      ".reviewcompass/specs/foundation/reviews/*-foundation-implementation-review-run",
    )
    self.assertEqual(
      required_inputs["triad_review_run_artifacts"]["required_artifacts"],
      [
        "review-target.md",
        "raw/",
        "rounds.yaml",
        "model-result-summary.yaml",
        "triage.yaml",
        "raw-review-triage-summary.md",
        "variant-role-assignment",
        "user-visible-triage-gate",
      ],
    )

  def test_next_review_wave_reports_recheck_and_pending_findings(self):
    """review-wave では recheck と抽象入力としての未消化所見情報を返す"""
    cwd = Path(self.tmpdir)
    implementation_ready = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    _write_specs_for_next(
      cwd,
      {feature: dict(implementation_ready) for feature in FEATURE_ORDER},
    )
    foundation_spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    foundation_spec = json.loads(foundation_spec_path.read_text(encoding="utf-8"))
    foundation_spec["recheck"] = {
      "upstream_change_pending": True,
      "impacted_downstream_phases": ["implementation"],
    }
    foundation_spec_path.write_text(
      json.dumps(foundation_spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    pending_path = (
      cwd / "learning" / "workflow" / "carry-forward-register" / "sources"
      / "reviewcompass-pending-cross-feature-findings.md"
    )
    pending_path.parent.mkdir(parents=True)
    pending_path.write_text(
      "# 機能横断レビューで扱う所見の集約\n\n"
      "### A-001：未消化の波及所見\n",
      encoding="utf-8",
    )
    register_path = (
      cwd / "learning" / "workflow" / "carry-forward-register" / "reviewcompass-import.yaml"
    )
    register_path.parent.mkdir(parents=True, exist_ok=True)
    register_path.write_text(
      yaml.safe_dump(
        {
          "register_id": "carry-forward-register",
          "schema_version": 1,
          "source_type": "carry_forward_register",
          "items": [
            {
              "item_id": "carry-forward-001",
              "scope": "cross_scope",
              "source_feature": "foundation",
              "target_feature_or_phase": ["runtime"],
              "finding_summary": "未消化の波及所見",
              "status": "open",
              "decision_needed": False,
              "decision_reasons": [],
              "carry_forward_reason": "review-wave で消化する",
              "resolution": None,
              "evidence_refs": [],
              "project_local_context": {"legacy_id": "A-001"},
            }
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "cross_feature_stage")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "review-wave")
    self.assertEqual(
      data["next_action"]["recheck_items"],
      [
        {
          "feature": "foundation",
          "impacted_downstream_phases": ["implementation"],
        }
      ],
    )
    self.assertEqual(
      data["next_action"]["pending_cross_feature_findings"]["unresolved_count"],
      1,
    )
    self.assertEqual(
      data["next_action"]["pending_cross_feature_findings"]["file"],
      "learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md",
    )
    self.assertNotIn(
      ".reviewcompass/pending-cross-feature-findings.md",
      data["next_action"]["required_disciplines"],
    )
    required_inputs = {
      item["id"]: item
      for item in data["next_action"]["required_inputs"]
    }
    self.assertEqual(
      required_inputs["cross_feature_stage_artifacts"]["path"],
      ".reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md",
    )
    self.assertEqual(
      required_inputs["unresolved_cross_scope_items"],
      {
        "id": "unresolved_cross_scope_items",
        "role": "stage_entry_context",
        "source_type": "carry_forward_register",
        "purpose": (
          "Read unresolved items carried forward from prior reviews or "
          "adjacent scopes before starting this stage."
        ),
        "read_policy": "unresolved_items_only",
        "path": "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
        "unresolved_count": 1,
      },
    )

  def test_next_prioritizes_in_progress_file(self):
    """進行中ファイルがあれば新規作業ではなく resume を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process-2026-06-02.yaml").write_text(
      "process_id: manual-process\n"
      "next_step: 第3過程：連鎖再実施\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "resume_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/manual-process-2026-06-02.yaml",
    )

  def test_next_reads_maintenance_in_progress(self):
    """maintenance の進行中ファイルがあれば通常ワークフローより優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "reason: Codex 稼働前に Claude 前提の入口記述を整理する\n"
      "required_action: inspect_remaining_claude_assumptions\n"
      "blocked_normal_workflow: true\n"
      "mainline_blocked_by: conformance-evaluation feature-partitioning confirmation\n"
      "allowed_scope:\n"
      "  - docs/operations/\n"
      "  - TODO_NEXT_SESSION.md\n"
      "allowed_files:\n"
      "  - docs/operations/WORKFLOW_NAVIGATION.md\n"
      "  - TODO_NEXT_SESSION.md\n"
      "completion_conditions:\n"
      "  - Codex 新規セッションで TODO から開始できる\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "maintenance_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml",
    )
    self.assertEqual(data["next_action"]["process_id"], "maintenance")
    self.assertEqual(data["next_action"]["title"], "Codex adapter migration")
    self.assertTrue(data["next_action"]["blocked_normal_workflow"])
    self.assertEqual(
      data["next_action"]["mainline_blocked_by"],
      "conformance-evaluation feature-partitioning confirmation",
    )
    self.assertEqual(
      data["next_action"]["allowed_scope"],
      ["docs/operations/", "TODO_NEXT_SESSION.md"],
    )
    self.assertEqual(
      data["next_action"]["allowed_files"],
      ["docs/operations/WORKFLOW_NAVIGATION.md", "TODO_NEXT_SESSION.md"],
    )
    self.assertEqual(
      data["next_action"]["completion_conditions"],
      ["Codex 新規セッションで TODO から開始できる"],
    )
    self.assertEqual(data["next_action"]["required_action"], "run_maintenance")
    self.assertIsNone(data["next_action"]["active_gate"])
    self.assertIsNone(data["next_action"]["feature"])
    self.assertIsNone(data["next_action"]["phase"])
    self.assertIsNone(data["next_action"]["stage"])
    self.assertEqual(
      data["next_action"]["maintenance_action"],
      "inspect_remaining_claude_assumptions",
    )

  def test_next_prioritizes_post_write_over_maintenance(self):
    """maintenance 中でも書き込み後検証対象があれば post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "required_action: inspect_remaining_claude_assumptions\n",
      encoding="utf-8",
    )
    target = cwd / "docs" / "notes" / "codex-maintenance.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("maintenance 中の検証対象文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/notes/codex-maintenance.md"],
    )
    self.assertIn(
      "docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      "docs/disciplines/discipline_post_write_verification.md",
      data["next_action"]["required_disciplines"],
    )
    self.assertEqual(
      data["current_state"]["in_progress_files"],
      ["stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml"],
    )

  def test_next_reads_reopen_in_progress_next_step(self):
    """reopen の進行中ファイルから next_step と required_action を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "started_at: 2026-06-02T00:00:00+09:00\n"
      "completed_steps: [\"第1過程：判定とフラグ差し戻し\", \"第2過程：正本修正\"]\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["process_id"], "reopen-procedure")
    self.assertEqual(data["next_action"]["next_step"], "第3過程：連鎖再実施")
    self.assertEqual(data["next_action"]["required_action"], "run_reopen_pending_gate")
    self.assertEqual(data["next_action"]["next_pending_gate"], "stages/requirements.yaml#alignment")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "alignment")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      ["stages/requirements.yaml#alignment", "stages/requirements.yaml#approval"],
    )

  def test_next_reopen_prefers_step_number_over_next_step_text(self):
    """reopen は next_step の表記ゆれより step_number を優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第三工程：表記ゆれ\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["step_number"], 3)
    self.assertEqual(data["next_action"]["required_action"], "run_reopen_pending_gate")
    self.assertEqual(data["next_action"]["next_pending_gate"], "stages/requirements.yaml#alignment")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "alignment")

  def test_next_reopen_commit_stop_point_blocks_pending_gate(self):
    """reopen 停止点では pending_gates が残っても commit_stop_point だけを返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-16.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "commit_stop_point")
    self.assertIsNone(action["active_gate"])
    self.assertIsNone(action["next_pending_gate"])
    self.assertIsNone(action["phase"])
    self.assertIsNone(action["stage"])
    self.assertEqual(action["blocked_by"]["type"], "commit_stop_point")

  def test_next_reopen_reports_first_pending_gate_as_unique_task(self):
    """reopen 第3過程は drafting 完了後に pending_gates 先頭を次タスクとして返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "  - stages/requirements.yaml#review-wave\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "drafting_completed_gates:\n"
      "  - stages/requirements.yaml#drafting\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(
      data["next_action"]["next_pending_gate"],
      "stages/requirements.yaml#triad-review",
    )
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "triad-review")
    self.assertEqual(
      data["next_action"]["required_action"],
      "run_reopen_pending_gate",
    )
    self.assertEqual(
      data["next_action"]["active_gate"],
      "stages/requirements.yaml#triad-review",
    )
    self.assertIsNone(data["next_action"]["blocked_by"])

  def test_next_reopen_requires_drafting_before_triad_review(self):
    """reopen 第3過程は triad-review の前に phase drafting を一意に返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/design.yaml#triad-review\n"
      "  - stages/design.yaml#review-wave\n"
      "  - stages/design.yaml#alignment\n"
      "  - stages/design.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "run_reopen_drafting")
    self.assertEqual(action["next_pending_gate"], "stages/design.yaml#triad-review")
    self.assertEqual(action["next_drafting_gate"], "stages/design.yaml#drafting")
    self.assertEqual(action["active_gate"], "stages/design.yaml#drafting")
    self.assertEqual(action["phase"], "design")
    self.assertEqual(action["stage"], "drafting")
    required_inputs = {
      item["id"]: item
      for item in action["required_inputs"]
    }
    self.assertEqual(
      required_inputs["reopen_procedure_state"]["paths"],
      ["stages/in-progress/reopen-procedure-2026-06-02.yaml"],
    )

  def test_next_reopen_uses_feature_impact_decisions_as_review_scope(self):
    """reopen のレビュー対象 feature は feature_impact_decisions から機械的に返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "feature:\n"
      "  - conformance-evaluation\n"
      "  - workflow-management\n"
      "next_step: 第3過程：連鎖再実施\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "current_blocker: null\n"
      "feature_impact_decisions:\n"
      "  - feature: conformance-evaluation\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: direct\n"
      "    evidence: [intent/INTENT.md]\n"
      "  - feature: workflow-management\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: contract_ownership\n"
      "    rationale: direct\n"
      "    evidence: [docs/operations/REOPEN_PROCEDURE.md]\n"
      "  - feature: foundation\n"
      "    decision: indirect_check_only\n"
      "    impact_basis: consumer_or_derivative_only\n"
      "    rationale: indirect\n"
      "    evidence: [.reviewcompass/specs/foundation/requirements.md]\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(
      action["required_feature_scope"],
      ["foundation", "workflow-management", "conformance-evaluation"],
    )
    self.assertEqual(
      action["direct_features"],
      ["workflow-management", "conformance-evaluation"],
    )
    self.assertEqual(action["indirect_features"], ["foundation"])
    required_inputs = {
      item["id"]: item
      for item in action["required_inputs"]
    }
    self.assertEqual(
      required_inputs["target_feature_documents"]["paths"],
      [
        ".reviewcompass/specs/foundation/spec.json",
        ".reviewcompass/specs/foundation/requirements.md",
        ".reviewcompass/specs/foundation/design.md",
        ".reviewcompass/specs/foundation/tasks.md",
        ".reviewcompass/specs/workflow-management/spec.json",
        ".reviewcompass/specs/workflow-management/requirements.md",
        ".reviewcompass/specs/workflow-management/design.md",
        ".reviewcompass/specs/workflow-management/tasks.md",
        ".reviewcompass/specs/conformance-evaluation/spec.json",
        ".reviewcompass/specs/conformance-evaluation/requirements.md",
        ".reviewcompass/specs/conformance-evaluation/design.md",
        ".reviewcompass/specs/conformance-evaluation/tasks.md",
      ],
    )

  def test_next_reopen_human_blocker_requires_wait(self):
    """reopen の current_blocker があれば人間承認待ちを返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: stages/requirements.yaml#approval（人間承認待ち）\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["required_action"], "wait_for_human_decision")
    self.assertIsNone(data["next_action"]["active_gate"])
    self.assertIsNone(data["next_action"]["next_pending_gate"])
    self.assertIsNone(data["next_action"]["phase"])
    self.assertIsNone(data["next_action"]["stage"])
    self.assertEqual(data["next_action"]["blocked_by"]["type"], "current_blocker")
    self.assertEqual(
      data["next_action"]["current_blocker"],
      "stages/requirements.yaml#approval（人間承認待ち）",
    )

  def test_next_reopen_structured_blocker_requires_wait(self):
    """構造化された reopen blocker も承認待ちとして返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker:\n"
      "  blocker_type: approval_gate\n"
      "  gate: stages/requirements.yaml#approval\n"
      "  actor: human\n"
      "  status: waiting_for_approval\n"
      "  rationale: approval gate に到達した。\n"
      "  evidence:\n"
      "    - .reviewcompass/specs/workflow-management/requirements.md\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    action = data["next_action"]
    self.assertEqual(action["kind"], "reopen_in_progress")
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertIsNone(action["active_gate"])
    self.assertIsNone(action["next_pending_gate"])
    self.assertIsNone(action["phase"])
    self.assertIsNone(action["stage"])
    self.assertEqual(action["blocked_by"]["type"], "current_blocker")
    self.assertEqual(
      action["current_blocker"]["gate"],
      "stages/requirements.yaml#approval",
    )
    self.assertEqual(action["current_blocker"]["actor"], "human")
    self.assertEqual(action["current_blocker"]["status"], "waiting_for_approval")

  def test_next_prioritizes_post_write_verification_for_target_doc_changes(self):
    """対象 docs 文書の未コミット変更があれば post-write-verification を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_routes_working_notes_to_lightweight_self_check(self):
    """docs/notes/working 配下だけなら API post-write ではなく軽量自己精査を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "working" / "memo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("作業中メモ\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "lightweight_self_check")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/working/memo.md"])
    self.assertEqual(
      data["next_action"]["required_action"],
      "review_working_note_without_api",
    )

  def test_next_routes_todo_only_to_lightweight_self_check(self):
    """TODO_NEXT_SESSION.md 単独変更は API post-write ではなく軽量自己精査を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "TODO_NEXT_SESSION.md"
    target.write_text("# TODO\n\n次作業: design drafting\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "lightweight_self_check")
    self.assertEqual(data["next_action"]["target_files"], ["TODO_NEXT_SESSION.md"])
    self.assertEqual(
      data["next_action"]["required_action"],
      "review_working_note_without_api",
    )

  def test_next_keeps_regular_notes_as_post_write_targets(self):
    """docs/notes 直下は混在配置なので従来どおり post-write 対象にする"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "memo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("通常メモ\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/memo.md"])

  def test_next_includes_todo_in_strict_post_write_when_mixed_with_strict_target(self):
    """TODO と strict 対象が混ざる場合は TODO も strict post-write に同梱する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    todo = cwd / "TODO_NEXT_SESSION.md"
    strict = cwd / "docs" / "operations" / "policy.md"
    strict.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("# TODO\n", encoding="utf-8")
    strict.write_text("運用正本\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["TODO_NEXT_SESSION.md", "docs/operations/policy.md"],
    )

  def test_next_prioritizes_strict_post_write_when_mixed_with_working_notes(self):
    """軽量メモと strict 対象が混ざる場合は strict post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    working = cwd / "docs" / "notes" / "working" / "memo.md"
    strict = cwd / "docs" / "operations" / "policy.md"
    working.parent.mkdir(parents=True, exist_ok=True)
    strict.parent.mkdir(parents=True, exist_ok=True)
    working.write_text("作業中メモ\n", encoding="utf-8")
    strict.write_text("運用正本\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/operations/policy.md"])
    self.assertEqual(
      data["current_state"]["lightweight_self_check_targets"],
      ["docs/notes/working/memo.md"],
    )

  def test_next_post_write_verification_target_matrix(self):
    """規律で定義された post-write-verification 対象だけを検出する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_paths = [
      "TODO_NEXT_SESSION.md",
      "docs/experiments/foo.md",
      "docs/notes/foo.md",
      "docs/operations/foo.md",
      "docs/plan/foo.md",
      "docs/reviews/2026-06-02-audit-foo.md",
      "docs/reviews/reopen-classification-2026-06-02.md",
      "docs/workflow-evidence/future-generated.yaml",
    ]
    non_target_paths = [
      ".reviewcompass/specs/foundation/spec.json",
      "docs/archive/foo.md",
      "docs/reviews/2026-06-02-impl-triad-review.md",
      "docs/reviews/audit-summary.md",
      # (い) 機械が吐く捕捉物はディレクトリ単位で対象外（走行・再実行・再生成で担保）
      "docs/logs/autonomous-parallel/run.yaml",
      "docs/notes/review-runs/r1/raw/gemini.round-1.txt",
      "docs/notes/post-write-verification-review/result-google-r1.yaml",
    ]
    for path in target_paths + non_target_paths:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], sorted(target_paths))

  def test_next_excludes_own_precheck_log_from_post_write_targets(self):
    """ツール自身の実行ログ（docs/logs/workflow-precheck.log）は post-write 対象にしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    for path in ["docs/logs/workflow-precheck.log", "docs/notes/foo.md"]:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/foo.md"])

  def test_next_with_only_precheck_log_change_skips_post_write(self):
    """実行ログ単独の未コミット変更では post-write 判定にしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    log_path = cwd / "docs" / "logs" / "workflow-precheck.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("log\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertNotEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_uses_completed_post_write_manifest_to_return_to_workflow(self):
    """完了 manifest が対象ファイルを覆う場合は通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "foundation")

  def test_next_does_not_report_policy_violation_after_manifest_completion(self):
    """完了 manifest がある場合は pending 中の禁止混在として扱わない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 検証完了後の通常実装変更\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")

  def test_next_does_not_complete_manifest_after_target_content_changes(self):
    """manifest 作成後に対象ファイルが変わった場合は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    target.write_text("検証後に追記された正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_does_not_complete_manifest_with_empty_required_verifiers(self):
    """required_verifiers が空の manifest は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証者未指定の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "required_verifiers": [],
        "completed_verifiers": [],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_requires_human_decision_for_unresolved_substantive_findings(self):
    """manifest に未解決の本質的指摘があれば人間判断待ちを返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("本質的指摘ありの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_uses_latest_post_write_manifest_when_multiple_exist(self):
    """同一対象の manifest が複数ある場合はファイル名が新しいものを優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("複数 manifest の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-002.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(
      data["next_action"]["manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-02-002.yaml",
    )

  def test_next_deviation_when_new_runner_created_during_post_write_verification(self):
    """post-write-verification pending 中の新規 runner 作成は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 独自検証 runner\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["tools/post_write_verify_new_policy.py"],
    )

  def test_next_deviation_when_template_changes_during_post_write_verification(self):
    """post-write-verification pending 中の template 変更は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    template = cwd / "templates" / "todo" / "TODO_NEXT_SESSION.template.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("再発防止としてのテンプレート変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["templates/todo/TODO_NEXT_SESSION.template.md"],
    )

  def test_next_deviation_when_discipline_change_is_mixed_with_other_post_write_target(self):
    """post-write-verification pending 中に規律変更が混ざる場合は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("越境した規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_allows_discipline_post_write_when_it_is_the_only_target(self):
    """規律ファイル単独の変更は post-write-verification 対象として扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("正式手続き後の規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_ignores_workflow_stage_spec_changes_for_post_write_verification(self):
    """.reviewcompass/specs 配下は post-write-verification ではなく通常 workflow で扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    spec_doc = cwd / ".reviewcompass" / "specs" / "foundation" / "requirements.md"
    spec_doc.write_text("ワークフロー段で検証される文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertNotEqual(data["next_action"]["kind"], "post_write_verification")


class PostWriteCoverageMatrixTests(unittest.TestCase):
  """manifest の verifications[] による coverage matrix チェック"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_with_full_coverage_and_matching_sha256(self):
    """verifications[] で全検証者が全ファイルを見て sha256 も一致した manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"全検証者が全ファイルを見て sha256 一致の manifest は通常ワークフローに戻るべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_verifications_lack_per_entry_sha256(self):
    """verifications[] に per-entry target_sha256 がない manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            # target_sha256 が意図的に欠落
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] 内の per-entry target_sha256 が欠落した manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_entry_sha256_mismatches_master(self):
    """verifications[] の sha256 がマスターと不一致の場合は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": "deadbeef" * 8,  # 不正な sha256
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] エントリの sha256 がマスターと不一致の manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_covers_only_partial_files(self):
    """分業（検証者ごとに異なるファイルのみ）の manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-b.md"],
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "分業（各検証者が全ファイルを見ていない）は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      f"分業の manifest は post_write_verification を継続すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_falls_back_to_completed_verifiers_without_verifications_field(self):
    """verifications[] がない旧形式 manifest は completed_verifiers でフォールバック判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "legacy-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("旧形式の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/legacy-policy.md"],
        "target_sha256": {
          "docs/notes/legacy-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] なし旧形式は completed_verifiers で完了判定し通常ワークフローに戻るべき",
    )


class PostWriteReviewRunTraceabilityTests(unittest.TestCase):
  """review_run 宣言付き manifest の raw/rounds/triage/summary 機械検査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_manifest_for_review_run(self, cwd, run_id):
    changed_targets = ["docs/notes/review-target.md"]
    run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
    for path in sorted(run_dir.rglob("*")):
      if path.is_file():
        changed_targets.append(str(path.relative_to(cwd)))
    models = ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"]
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": changed_targets,
        "target_sha256": {
          path: _sha256_file(Path(cwd) / path)
          for path in changed_targets
        },
        "required_verifiers": models,
        "completed_verifiers": models,
        "unresolved_substantive_findings": 0,
        "review_run": {
          "path": f"docs/notes/review-runs/{run_id}",
          "summary_path": f"docs/notes/review-runs/{run_id}/model-result-summary.yaml",
        },
      },
    )

  def test_next_accepts_manifest_when_review_run_traceability_is_complete(self):
    """raw、rounds、triage、summary が全モデル分そろう manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "traceability-complete"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_run の raw/rounds/triage/summary がそろう manifest は完了すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_review_summary_is_missing(self):
    """summary artifact がない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-summary"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_summary=True,
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "モデル別 summary artifact がない review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_required_model_raw_is_missing(self):
    """required_verifiers の raw が欠ける review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-raw"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    (run_dir / "raw" / "gpt-5.4.round-1.txt").unlink()
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "required_verifiers の raw ファイルが欠ける review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_model_is_absent_from_triage(self):
    """rounds にいるモデルが triage に出ていない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-triage-model"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_triage_model="gpt-5.4",
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "rounds にいるモデルが triage に出ていない review_run は完了扱いしてはいけない",
    )


class PostWriteReviewRunEndToEndTests(unittest.TestCase):
  """review-run から manifest 生成、next 完了認定までの統合テスト"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_generated_from_review_triage_helper(self):
    """review_triage.write_manifest が生成した厳格 manifest で next が通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "e2e-review-run"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    manifest_path = (
      cwd
      / ".reviewcompass"
      / "post-write-verification"
      / "post-write-2026-06-03-999.yaml"
    )

    write_manifest(str(run_dir), str(manifest_path))
    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_triage.write_manifest 生成 manifest は next で完了認定されるべき。"
      f"next_action: {data['next_action']}",
    )
    self.assertEqual(
      data["current_state"]["post_write_manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-03-999.yaml",
    )


class ReopenStartTests(unittest.TestCase):
  """reopen-start サブコマンドの trigger_map 解決と in-progress 生成"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_reopen_start_generates_in_progress_file_for_d_1(self):
    """D-1 から pending_gates を解決して in-progress YAML を生成する"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "D-1",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "design で requirements の不整合を検出",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "reopen_started")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      [
        "stages/requirements.yaml#alignment",
        "stages/requirements.yaml#approval",
        "stages/design.yaml#alignment",
        "stages/design.yaml#approval",
      ],
    )
    in_progress = cwd / "stages" / "in-progress" / "reopen-procedure-2026-06-02.yaml"
    self.assertTrue(in_progress.exists())
    generated = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(generated["process_id"], "reopen-procedure")
    self.assertEqual(generated["classification"], "D-1")
    self.assertEqual(generated["feature"], "runtime")
    self.assertEqual(generated["next_step"], "第1過程：判定とフラグ差し戻し")

  def test_reopen_start_invalid_classification_returns_deviation(self):
    """未定義 classification は fail-closed で逸脱"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "Z-9",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "invalid",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")


class ReopenAdvanceGateTests(unittest.TestCase):
  """reopen-advance-gate サブコマンドの進行中 gate 更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_spec(self):
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "workflow-management"
      / "spec.json"
    )
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(
      json.dumps(
        {
          "feature_name": "workflow-management",
          "workflow_state": {
            "requirements": {
              "drafting": True,
              "triad-review": True,
              "review-wave": True,
              "alignment": False,
              "approval": False,
            }
          },
        },
        ensure_ascii=False,
        indent=2,
      )
      + "\n",
      encoding="utf-8",
    )
    return spec_path

  def test_reopen_advance_gate_updates_spec_and_in_progress_state(self):
    """pending gate 完了時の spec.json と reopen YAML 更新を機械処理する"""
    spec_path = self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", ".reviewcompass/specs/_cross_feature/reviews/alignment.md",
        "--completed-step", "第3過程：requirements alignment 実施",
        "--set-spec", "workflow-management", "requirements", "alignment", "true",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    self.assertTrue(spec["workflow_state"]["requirements"]["alignment"])
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["pending_gates"], ["stages/requirements.yaml#approval"])
    self.assertEqual(state["completed_gates"], ["stages/requirements.yaml#alignment"])
    self.assertEqual(
      state["downstream_impact_decisions"][0]["gate"],
      "stages/requirements.yaml#alignment",
    )
    self.assertEqual(state["next_step"], "第3過程：requirements approval")

  def test_reopen_advance_gate_records_review_gate_commit_stop_point(self):
    """review 系 gate 完了後は構造化された停止点コミット状態にする"""
    cases = [
      (
        "stages/requirements.yaml#triad-review",
        "stages/requirements.yaml#review-wave",
        3,
        "triad_review_complete",
      ),
      (
        "stages/design.yaml#review-wave",
        "stages/design.yaml#alignment",
        3,
        "review_wave_complete",
      ),
      (
        "stages/tasks.yaml#alignment",
        "stages/tasks.yaml#approval",
        3,
        "alignment_complete",
      ),
      (
        "stages/implementation.yaml#approval",
        None,
        4,
        "approval_complete",
      ),
    ]
    for gate, next_gate, expected_step, expected_kind in cases:
      with self.subTest(gate=gate):
        in_progress = (
          Path(self.tmpdir)
          / "stages"
          / "in-progress"
          / "reopen-procedure-2026-06-15.yaml"
        )
        in_progress.parent.mkdir(parents=True, exist_ok=True)
        in_progress.write_text(
          "process_id: reopen-procedure\n"
          "feature: workflow-management\n"
          "step_number: 3\n"
          f"next_step: 第3過程：{gate}\n"
          "completed_steps: []\n"
          "pending_gates:\n"
          f"  - {gate}\n"
          + (f"  - {next_gate}\n" if next_gate else "")
          +
          "completed_gates: []\n"
          "downstream_impact_decisions: []\n"
          "current_blocker: null\n",
          encoding="utf-8",
        )

        result = run_script(
          [
            "reopen-advance-gate",
            "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
            "--gate", gate,
            "--decision", "existing_sufficient",
            "--feature-scope", "workflow-management",
            "--rationale", "gate 完了後の停止点コミットを記録する。",
            "--evidence", "reviews/evidence.md",
            "--json",
          ],
          cwd=self.tmpdir,
        )

        _assert_script_invoked(self, result)
        self.assertEqual(result.returncode, 0, result.stdout)
        state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
        self.assertIs(state["commit_stop_point"], True)
        self.assertEqual(state["commit_stop_point_step"], expected_step)
        self.assertEqual(state["commit_stop_point_kind"], expected_kind)
        self.assertEqual(state["commit_stop_point_gate"], gate)

  def test_reopen_advance_gate_blocks_nonleading_pending_gate(self):
    """pending_gates の先頭以外を飛ばして完了できない"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision", "approved",
        "--feature-scope", "workflow-management",
        "--rationale", "approval を先に進める。",
        "--evidence", "approval.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("先頭", result.stdout)

  def test_reopen_advance_gate_rejects_missing_evidence(self):
    """根拠なしの pending gate 更新は拒否する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)

  def test_reopen_advance_gate_rejects_malformed_pending_gate(self):
    """pending_gates の全要素が標準 gate 形式でなければ拒否する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - requirements approval\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", "alignment.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("pending_gates", result.stdout)
    self.assertIn("stages/<phase>.yaml#<stage>", result.stdout)

  def test_reopen_advance_gate_rejects_drafting_pending_gate(self):
    """pending_gates は review 系 gate に限定する"""
    self._write_spec()
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements alignment\n"
      "completed_steps: []\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#drafting\n"
      "completed_gates: []\n"
      "downstream_impact_decisions: []\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--decision", "existing_sufficient",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements alignment は既存で受けられる。",
        "--evidence", "alignment.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("pending_gates", result.stdout)
    self.assertIn("review 系 gate", result.stdout)


class ReopenAdvanceStepTests(unittest.TestCase):
  """reopen-advance-step サブコマンドの第1・第2過程更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_in_progress(self, *, step_number, next_step, pending_gates=None):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    if pending_gates is None:
      pending_gates = [
        "stages/requirements.yaml#alignment",
        "stages/requirements.yaml#approval",
      ]
    in_progress.write_text(
      yaml.safe_dump(
        {
          "process_id": "reopen-procedure",
          "feature": "workflow-management",
          "step_number": step_number,
          "next_step": next_step,
          "completed_steps": [],
          "pending_gates": pending_gates,
          "current_blocker": None,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    return in_progress

  def test_reopen_advance_step_one_records_evidence_and_moves_to_step_two(self):
    """第1過程の完了を記録し第2過程へ進める"""
    in_progress = self._write_in_progress(
      step_number=1,
      next_step="第1過程：判定とフラグ差し戻し",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類と rollback flags を記録した。",
        "--evidence", "docs/reviews/reopen-classification-2026-06-16.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 2)
    self.assertEqual(state["next_step"], "第2過程：正本修正")
    self.assertIn("第1過程：判定とフラグ差し戻し完了", state["completed_steps"])
    self.assertEqual(state["reopen_step_records"][0]["from_step"], 1)
    self.assertEqual(
      state["reopen_step_records"][0]["evidence"],
      ["docs/reviews/reopen-classification-2026-06-16.md"],
    )

  def test_reopen_advance_step_two_records_commit_stop_point(self):
    """第2過程の完了を記録し停止点コミット状態へ進める"""
    in_progress = self._write_in_progress(
      step_number=2,
      next_step="第2過程：正本修正",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "2",
        "--completed-step", "第2過程：正本修正完了",
        "--rationale", "正本文書の修正を完了した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 2)
    self.assertEqual(state["next_step"], "第2過程：停止点コミット")
    self.assertIsNone(state["current_blocker"])
    self.assertIs(state["commit_stop_point"], True)
    self.assertEqual(state["commit_stop_point_step"], 2)
    self.assertEqual(
      state["commit_stop_point_kind"],
      "canonical_update_complete",
    )
    self.assertEqual(state["commit_stop_point_reason"], "第2過程の正本修正完了")
    self.assertIn("第2過程：正本修正完了", state["completed_steps"])
    self.assertEqual(state["reopen_step_records"][0]["from_step"], 2)

  def test_reopen_advance_step_rejects_missing_evidence(self):
    """根拠なしの reopen step 更新は拒否する"""
    self._write_in_progress(
      step_number=1,
      next_step="第1過程：判定とフラグ差し戻し",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類した。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)

  def test_reopen_advance_step_rejects_current_step_mismatch(self):
    """現在 step と --from-step が一致しなければ拒否する"""
    self._write_in_progress(
      step_number=2,
      next_step="第2過程：正本修正",
    )

    result = run_script(
      [
        "reopen-advance-step",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--from-step", "1",
        "--completed-step", "第1過程：判定とフラグ差し戻し完了",
        "--rationale", "分類した。",
        "--evidence", "docs/reviews/reopen-classification-2026-06-16.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("step_number", result.stdout)


class ReopenAdvanceAfterCommitStopPointTests(unittest.TestCase):
  """reopen-advance-after-commit-stop-point サブコマンドの停止点消費"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _write_in_progress(self, *, kind="approval_complete"):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-19.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      yaml.safe_dump(
        {
          "process_id": "reopen-procedure",
          "feature": "workflow-management",
          "step_number": 3,
          "next_step": "第3過程：tasks triad-review",
          "completed_steps": [
            "design approval gate 完了（利用者発言『承認』に基づく明示承認）",
          ],
          "pending_gates": [
            "stages/tasks.yaml#triad-review",
            "stages/tasks.yaml#review-wave",
          ],
          "completed_gates": [
            "stages/design.yaml#approval",
          ],
          "current_blocker": None,
          "commit_stop_point": True,
          "commit_stop_point_step": 3,
          "commit_stop_point_kind": kind,
          "commit_stop_point_gate": "stages/design.yaml#approval",
          "commit_stop_point_reason": "design approval 完了時点の停止点",
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    return in_progress

  def test_reopen_advance_after_commit_stop_point_consumes_stop_point(self):
    """停止点消費だけでは追加 commit を強制せず次の gate へ進める"""
    in_progress = self._write_in_progress()
    subprocess.run(
      ["git", "add", "-A"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "add reopen stop point"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(
      [
        "reopen-advance-after-commit-stop-point",
        "--file", "stages/in-progress/reopen-procedure-2026-06-19.yaml",
        "--head", "75411eb282475636719c2f79a4f372922ef57ba3",
        "--kind", "approval_complete",
        "--evidence", ".reviewcompass/post-write-verification/post-write-2026-06-19-281.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertNotIn("commit_stop_point", state)
    self.assertNotIn("commit_stop_point_kind", state)
    self.assertEqual(
      state["commit_stop_point_records"][0]["head"],
      "75411eb282475636719c2f79a4f372922ef57ba3",
    )
    self.assertEqual(
      state["commit_stop_point_records"][0]["kind"],
      "approval_complete",
    )
    self.assertNotIn("commit_required", state)
    self.assertNotIn("commit_required_kind", state)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    next_data = json.loads(next_result.stdout)
    action = next_data["next_action"]
    self.assertEqual(action["required_action"], "run_reopen_drafting")
    self.assertEqual(action["active_gate"], "stages/tasks.yaml#drafting")
    self.assertEqual(action["next_pending_gate"], "stages/tasks.yaml#triad-review")
    self.assertIsNone(action["blocked_by"])

    preflight = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, preflight)
    self.assertEqual(preflight.returncode, 2, preflight.stdout)
    preflight_data = json.loads(preflight.stdout)
    self.assertEqual(preflight_data["next_required_action"], "run_reopen_drafting")
    self.assertFalse(preflight_data["allowed_to_stage"])

    subprocess.run(
      ["git", "add", "-A"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "consume reopen stop point"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    clean_next = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, clean_next)
    self.assertEqual(clean_next.returncode, 0, clean_next.stdout)
    clean_data = json.loads(clean_next.stdout)
    action = clean_data["next_action"]
    self.assertEqual(action["required_action"], "run_reopen_drafting")
    self.assertEqual(action["active_gate"], "stages/tasks.yaml#drafting")
    self.assertEqual(action["next_pending_gate"], "stages/tasks.yaml#triad-review")

  def test_reopen_advance_after_commit_stop_point_rejects_kind_mismatch(self):
    """停止点 kind が一致しなければ消費しない"""
    in_progress = self._write_in_progress(kind="review_wave_complete")

    result = run_script(
      [
        "reopen-advance-after-commit-stop-point",
        "--file", "stages/in-progress/reopen-procedure-2026-06-19.yaml",
        "--head", "75411eb282475636719c2f79a4f372922ef57ba3",
        "--kind", "approval_complete",
        "--evidence", "post-write.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit_stop_point_kind", result.stdout)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertIs(state["commit_stop_point"], True)
    self.assertEqual(state["commit_stop_point_kind"], "review_wave_complete")


class ReopenSetBlockerTests(unittest.TestCase):
  """reopen-set-blocker サブコマンドの承認待ち blocker 構造化"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_in_progress(self, pending_gates=None):
    if pending_gates is None:
      pending_gates = [
        "stages/requirements.yaml#approval",
        "stages/design.yaml#alignment",
      ]
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    lines = [
      "process_id: reopen-procedure",
      "feature: workflow-management",
      "step_number: 3",
      "next_step: 第3過程：連鎖再実施",
      "pending_gates:",
    ]
    lines.extend([f"  - {gate}" for gate in pending_gates])
    lines.append("current_blocker: null")
    in_progress.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return in_progress

  def test_reopen_set_blocker_writes_structured_approval_blocker(self):
    """先頭 approval gate の承認待ち blocker を構造化して保存する"""
    in_progress = self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--actor", "human",
        "--rationale", "approval gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(
      state["current_blocker"],
      {
        "blocker_type": "approval_gate",
        "gate": "stages/requirements.yaml#approval",
        "actor": "human",
        "status": "waiting_for_approval",
        "rationale": "approval gate に到達した。",
        "evidence": [
          ".reviewcompass/specs/workflow-management/requirements.md",
        ],
      },
    )

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    next_data = json.loads(next_result.stdout)
    action = next_data["next_action"]
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertEqual(action["blocked_by"]["type"], "current_blocker")
    self.assertEqual(action["blocked_by"]["gate"], "stages/requirements.yaml#approval")

  def test_legacy_commit_required_does_not_mask_approval_blocker(self):
    """旧 commit_required が残っても approval blocker を commit_stop_point に戻さない"""
    in_progress = self._write_in_progress()
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    state["commit_stop_point_records"] = [
      {
        "step": 3,
        "kind": "alignment_complete",
        "gate": "stages/requirements.yaml#alignment",
        "head": "abc123",
      },
    ]
    state["commit_required"] = True
    state["commit_required_kind"] = "stop_point_consumed"
    state["commit_required_reason"] = "legacy bookkeeping commit boundary"
    in_progress.write_text(
      yaml.safe_dump(state, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    _init_git_repo(self.tmpdir)
    subprocess.run(
      ["git", "add", "-A"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "add legacy commit required state"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--actor", "human",
        "--rationale", "approval gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    next_data = json.loads(next_result.stdout)
    action = next_data["next_action"]
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertEqual(action["blocked_by"]["type"], "current_blocker")
    self.assertEqual(action["blocked_by"]["gate"], "stages/requirements.yaml#approval")

  def test_reopen_set_blocker_rejects_non_head_gate(self):
    """pending_gates 先頭ではない gate の blocker 設定は拒否する"""
    self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/design.yaml#alignment",
        "--actor", "human",
        "--rationale", "approval gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/design.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("先頭", result.stdout)

  def test_reopen_set_blocker_rejects_non_approval_gate(self):
    """approval 以外の gate には承認待ち blocker を設定しない"""
    self._write_in_progress(pending_gates=["stages/requirements.yaml#alignment"])

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#alignment",
        "--actor", "human",
        "--rationale", "alignment gate に到達した。",
        "--evidence", ".reviewcompass/specs/workflow-management/requirements.md",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("approval", result.stdout)

  def test_reopen_set_blocker_rejects_missing_evidence(self):
    """根拠なしの blocker 設定は拒否する"""
    self._write_in_progress()

    result = run_script(
      [
        "reopen-set-blocker",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--actor", "proxy_model",
        "--rationale", "proxy_model 承認待ち。",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("evidence", result.stdout)


class ReopenFinalizeTests(unittest.TestCase):
  """reopen-finalize サブコマンドの完了 YAML 機械更新"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_ready_in_progress(self):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-16.yaml"
    )
    in_progress.parent.mkdir(parents=True)
    in_progress.write_text(
      "process_id: reopen-procedure\n"
      "feature: workflow-management\n"
      "step_number: 4\n"
      "next_step: 第4過程：完了\n"
      "completed_steps:\n"
      "  - 第3過程：requirements approval 実施\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: alignment 済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/alignment.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: approval 済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/approval.md\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )
    return in_progress

  def _write_workflow_management_spec_with_recheck(self):
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "workflow-management"
      / "spec.json"
    )
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(
      json.dumps(
        {
          "feature_name": "workflow-management",
          "workflow_state": {},
          "reopened": {
            "intent": True,
            "feature-partitioning": True,
            "requirements": True,
            "design": True,
            "tasks": True,
            "implementation": True,
          },
          "recheck": {
            "upstream_change_pending": True,
            "impacted_downstream_phases": ["tasks", "implementation"],
          },
        },
        ensure_ascii=False,
        indent=2,
      )
      + "\n",
      encoding="utf-8",
    )
    return spec_path

  def _feature_impact_args(self):
    args = []
    for feature in FEATURE_ORDER:
      args.extend([
        "--feature-impact",
        feature,
        "reopen_existing_feature",
        "contract_ownership",
        f"{feature} の契約影響を確認した。",
        f".reviewcompass/specs/{feature}/requirements.md",
      ])
    return args

  def test_reopen_finalize_moves_in_progress_to_completed_with_required_decisions(self):
    """第4過程の完了 YAML を構造化入力から生成し in-progress を残さない"""
    in_progress = self._write_ready_in_progress()

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--completed-step", "第4過程：reopen 完了",
        "--json",
      ]
      + self._feature_impact_args(),
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertFalse(in_progress.exists())
    completed = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-16.yaml"
    )
    self.assertTrue(completed.exists())
    state = yaml.safe_load(completed.read_text(encoding="utf-8"))
    self.assertEqual(state["step_number"], 4)
    self.assertEqual(state["next_step"], "完了")
    self.assertEqual(state["pending_gates"], [])
    self.assertEqual(state["current_blocker"], None)
    self.assertEqual(state["impacted_downstream_phases"], ["requirements"])
    self.assertEqual(len(state["feature_impact_decisions"]), len(FEATURE_ORDER))
    self.assertEqual(state["new_feature_decision"]["decision"], "no_new_feature")
    self.assertIn("第4過程：reopen 完了", state["completed_steps"])

  def test_reopen_finalize_clears_feature_recheck_and_records_step_four(self):
    """reopen-finalize は完了予定状態を一括反映し recheck と第4過程履歴を整合させる"""
    in_progress = self._write_ready_in_progress()
    spec_path = self._write_workflow_management_spec_with_recheck()

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--completed-step", "第4過程 完了",
        "--json",
      ]
      + self._feature_impact_args(),
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    self.assertFalse(in_progress.exists())
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    self.assertEqual(
      spec["recheck"],
      {"upstream_change_pending": False, "impacted_downstream_phases": []},
    )
    completed = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-16.yaml"
    )
    state = yaml.safe_load(completed.read_text(encoding="utf-8"))
    step_four_records = [
      record for record in state["reopen_step_records"]
      if record["from_step"] == 4
    ]
    self.assertEqual(len(step_four_records), 1)
    self.assertIn("recheck をクリア", step_four_records[0]["rationale"])
    self.assertIn(str(spec_path.relative_to(self.tmpdir)), step_four_records[0]["evidence"])

  def test_reopen_finalize_blocks_before_step_four(self):
    """第4過程に到達していない reopen state は完了化できない"""
    in_progress = self._write_ready_in_progress()
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    state["step_number"] = 3
    state["pending_gates"] = ["stages/requirements.yaml#approval"]
    in_progress.write_text(
      yaml.safe_dump(state, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--json",
      ]
      + self._feature_impact_args(),
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("第4過程", result.stdout)
    self.assertTrue(in_progress.exists())

  def test_reopen_finalize_requires_all_feature_impact_decisions(self):
    """全 feature の impact 判定が無ければ完了 YAML を生成しない"""
    in_progress = self._write_ready_in_progress()
    incomplete_feature_args = self._feature_impact_args()[:-6]

    result = run_script(
      [
        "reopen-finalize",
        "--file", "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "--impacted-downstream-phase", "requirements",
        "--new-feature-decision",
        "no_new_feature",
        "既存 feature で受けられる。",
        "stages/feature-partitioning/2026-05-24-proposal.md",
        "--json",
      ]
      + incomplete_feature_args,
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)
    self.assertTrue(in_progress.exists())


def _init_git_repo(tmpdir):
  """temp dir に git リポジトリを初期化し、初回コミットと .reviewcompass 構造を準備する

  commit／push サブコマンドのテスト用ヘルパー。
  """
  for cmd in [
    ["git", "init", "-q", "-b", "main"],
    ["git", "config", "user.email", "test@example.com"],
    ["git", "config", "user.name", "Test User"],
    ["git", "config", "commit.gpgsign", "false"],
  ]:
    subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
  # 初回コミット（空でないリポジトリにする）
  (Path(tmpdir) / ".gitignore").write_text("")
  subprocess.run(
    ["git", "add", ".gitignore"], cwd=str(tmpdir), check=True, capture_output=True
  )
  subprocess.run(
    ["git", "commit", "-qm", "initial"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # carry-forward register 構造を準備
  register_dir = Path(tmpdir) / "learning" / "workflow" / "carry-forward-register"
  source_dir = register_dir / "sources"
  source_dir.mkdir(parents=True)
  source_file = source_dir / "reviewcompass-pending-cross-feature-findings.md"
  source_file.write_text("# 機能横断レビューで扱う所見の集約\n")
  register_file = register_dir / "reviewcompass-import.yaml"
  _set_pending_findings(register_file, unresolved_count=0, resolved_count=0)
  # register と source もコミットして作業ツリーを clean な初期状態にする
  subprocess.run(
    [
      "git",
      "add",
      "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
      "learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md",
    ],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add carry-forward register"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  return register_file


def _set_pending_findings(register_file, unresolved_count=0, resolved_count=0):
  """抽象レジスタに未消化／対処済み所見を設定する"""
  items = []
  for i in range(unresolved_count):
    items.append({
      "item_id": f"carry-forward-{i+1:03d}",
      "scope": "cross_scope",
      "source_feature": "foundation",
      "target_feature_or_phase": ["runtime"],
      "finding_summary": "テスト用未消化所見",
      "status": "open",
      "decision_needed": False,
      "decision_reasons": [],
      "carry_forward_reason": "テスト用",
      "resolution": None,
      "evidence_refs": [],
      "project_local_context": {"legacy_id": f"A-{i+1:03d}"},
    })
  for i in range(resolved_count):
    n = unresolved_count + i + 1
    items.append({
      "item_id": f"carry-forward-{n:03d}",
      "scope": "cross_scope",
      "source_feature": "foundation",
      "target_feature_or_phase": ["runtime"],
      "finding_summary": "テスト用対処済み所見",
      "status": "resolved",
      "decision_needed": False,
      "decision_reasons": [],
      "carry_forward_reason": "テスト用",
      "resolution": "テスト用対処済み",
      "evidence_refs": [],
      "project_local_context": {"legacy_id": f"A-{n:03d}"},
    })
  register_file.write_text(
    yaml.safe_dump(
      {
        "register_id": "carry-forward-register",
        "schema_version": 1,
        "source_type": "carry_forward_register",
        "items": items,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )


def _stage_file(tmpdir, relpath, content):
  """ファイルを作成して git add 状態にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


def _write_commit_approval(
  tmpdir,
  target_files,
  consumed=False,
  target_sha256=None,
  include_target_sha256=True,
  include_execution_delegation=True,
  execution_instruction="コミット",
):
  """commit 事前検査用のユーザ承認レコードを書く（書き込みは常に新配置＝runtime 区画）"""
  approval_dir = Path(tmpdir) / ".reviewcompass" / "runtime" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  approval_path = approval_dir / "commit-approval.json"
  if target_sha256 is None:
    target_sha256 = {
      relpath: _sha256_file(Path(tmpdir) / relpath)
      for relpath in target_files
      if (Path(tmpdir) / relpath).exists()
    }
  approval = {
    "approved_action": "commit",
    "approved_by": "user",
    "approved_at": "2026-06-03T00:00:00+09:00",
    "rationale": "利用者がコミットを明示承認",
    "target_files": target_files,
    "expires_after_commit": True,
    "consumed": consumed,
  }
  if include_execution_delegation:
    approval["execution_delegation"] = {
      "delegated_to": "llm",
      "approved_by": "user",
      "approved_at": "2026-06-03T00:00:00+09:00",
      "explicit_instruction": execution_instruction,
      "rationale": "利用者が LLM によるコミット実行代行を明示承認",
    }
  if include_target_sha256:
    approval["target_sha256"] = target_sha256
  approval_path.write_text(
    json.dumps(approval, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  return approval_path


def _read_commit_approval(tmpdir):
  """runtime 区画の commit 承認レコードを読む"""
  approval_path = (
    Path(tmpdir)
    / ".reviewcompass"
    / "runtime"
    / "approvals"
    / "commit-approval.json"
  )
  return json.loads(approval_path.read_text(encoding="utf-8"))


def _prepare_commit_approval(tmpdir):
  """commit-approval prepare を実行して JSON を返す"""
  result = run_script(["commit-approval", "prepare", "--json"], cwd=tmpdir)
  if result.returncode != 0:
    raise AssertionError(result.stdout + result.stderr)
  return json.loads(result.stdout)


def _record_commit_approval(tmpdir, nonce, source_text=None, extra_args=None):
  """commit-approval record を実行して JSON を返す"""
  args = [
    "commit-approval",
    "record",
    "--nonce", nonce,
    "--json",
  ]
  input_text = None
  if source_text is None:
    args.append("--no-source-text")
  else:
    args.append("--source-text-stdin")
    input_text = source_text
  if extra_args:
    args.extend(extra_args)
  if input_text is not None:
    return run_script_with_tty_stdin(args, tmpdir, input_text)
  return subprocess.run(
    ["python3", str(SCRIPT)] + args,
    cwd=str(tmpdir),
    capture_output=True,
    text=True,
    timeout=10,
  )


def _delegate_commit_execution(tmpdir, nonce, source_text="コミット\n", extra_args=None):
  """commit-approval delegate-execution を実行して JSON を返す"""
  args = [
    "commit-approval",
    "delegate-execution",
    "--nonce", nonce,
    "--source-text-stdin",
    "--json",
  ]
  if extra_args:
    args.extend(extra_args)
  return run_script_with_tty_stdin(args, tmpdir, source_text)


def _read_commit_execution_delegation(tmpdir):
  """runtime 区画の commit 実行代行承認レコードを読む"""
  delegation_path = (
    Path(tmpdir)
    / ".reviewcompass"
    / "runtime"
    / "approvals"
    / "commit-execution-delegation.json"
  )
  return json.loads(delegation_path.read_text(encoding="utf-8"))


def _load_commit_approval_module():
  """tools/check_workflow_action/commit_approval.py をスクリプト実行時と同じ path で読む"""
  tools_path = str(REPO_ROOT / "tools")
  if tools_path not in os.sys.path:
    os.sys.path.insert(0, tools_path)
  return importlib.import_module("check_workflow_action.commit_approval")


def _write_completed_post_write_manifest(tmpdir, target_files):
  """対象ファイルを覆う完了 post-write manifest を書く"""
  target_sha256 = {
    relpath: _sha256_file(Path(tmpdir) / relpath)
    for relpath in target_files
  }
  _write_post_write_manifest(
    tmpdir,
    "post-write-2026-06-03-999.yaml",
    {
      "status": "completed",
      "target_files": target_files,
      "target_sha256": target_sha256,
      "required_verifiers": ["google"],
      "completed_verifiers": ["google"],
      "unresolved_substantive_findings": 0,
    },
  )


def _write_last_commit_precheck(tmpdir, head_commit=None):
  """push 事前検査用の直近 commit 検査通過記録を書く"""
  if head_commit is None:
    result = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      cwd=str(tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )
    head_commit = result.stdout.strip()
  approval_dir = Path(tmpdir) / ".git" / "reviewcompass"
  approval_dir.mkdir(parents=True, exist_ok=True)
  precheck_path = approval_dir / "last-commit-precheck.json"
  precheck_path.write_text(
    json.dumps(
      {
        "head_commit": head_commit,
        "precheck_command": "tools/check-workflow-action.py commit",
        "precheck_exit_code": 0,
        "recorded_at": "2026-06-03T00:00:00+09:00",
      },
      ensure_ascii=False,
      indent=2,
    ),
    encoding="utf-8",
  )
  return precheck_path


class CommitExitCodeTests(unittest.TestCase):
  """commit サブコマンドの終了コード判定（仕様 §6.2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_preflight_blocks_reopen_in_progress_before_staging(self):
    """reopen 途中で停止点でなければ stage / approval 作成前に遮断する"""
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-19.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements review-wave\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#review-wave\n",
      encoding="utf-8",
    )

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_stage"])
    self.assertFalse(data["allowed_to_prepare_approval"])
    self.assertFalse(data["allowed_to_delegate_execution"])
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertEqual(data["next_required_action"], "run_reopen_pending_gate")
    self.assertIn("commit stop point", "\n".join(data["reasons"]))

  def test_commit_preflight_allows_reopen_commit_stop_point_before_staging(self):
    """構造化 reopen 停止点なら commit 処理の準備に進める"""
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-19.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：design triad-review 完了\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 3\n"
      "commit_stop_point_kind: triad_review_complete\n"
      "commit_stop_point_gate: stages/design.yaml#triad-review\n"
      "commit_stop_point_reason: design triad-review 完了時点の停止点\n",
      encoding="utf-8",
    )

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertTrue(data["allowed_to_stage"])
    self.assertTrue(data["allowed_to_prepare_approval"])
    self.assertTrue(data["allowed_to_delegate_execution"])
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertEqual(data["next_required_action"], "commit_stop_point")

  def test_commit_preflight_allows_completed_maintenance_without_reopen_state_change(self):
    """maintenance 完了 commit 候補は本線 reopen state を変えずに準備できる"""
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-19.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：requirements review-wave\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#review-wave\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-19.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "add reopen in-progress"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    maintenance_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "maintenance-2026-06-19-review-target.yaml"
    )
    maintenance_path.parent.mkdir(parents=True)
    maintenance_path.write_text(
      "process_id: maintenance\n"
      "title: review target preflight\n"
      "mainline_blocked_by: stages/in-progress/reopen-procedure-2026-06-19.yaml\n"
      "completed_actions:\n"
      "  - side track completed\n",
      encoding="utf-8",
    )

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertTrue(data["allowed_to_stage"])
    self.assertTrue(data["allowed_to_prepare_approval"])
    self.assertEqual(data["next_required_action"], "prepare_completed_maintenance_commit")

  def test_commit_preflight_blocks_post_write_pending_before_staging(self):
    """post-write 未完了なら stage / approval 作成前に遮断する"""
    target = Path(self.tmpdir) / "docs" / "operations" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("運用正本\n", encoding="utf-8")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_stage"])
    self.assertFalse(data["allowed_to_prepare_approval"])
    self.assertFalse(data["allowed_to_delegate_execution"])
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertEqual(data["next_required_action"], "run_post_write_verification")

  def test_commit_preflight_allows_normal_workflow_phase_end_stop_point(self):
    """通常 workflow の phase 終端停止点でも commit 準備に進める"""
    intent_before = {
      "drafting": True,
      "review": True,
      "approval": False,
      "reference": "stages/intent.yaml",
    }
    feature_partitioning = {
      "candidate-proposal": False,
      "approval": False,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    }
    _write_cross_feature_specs(
      self.tmpdir,
      intent_before,
      feature_partitioning,
    )
    subprocess.run(
      ["git", "add", ".reviewcompass/specs", "stages/feature-dependency.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "cross feature baseline"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    intent_after = dict(intent_before)
    intent_after["approval"] = True
    _write_cross_feature_specs(
      self.tmpdir,
      intent_after,
      feature_partitioning,
    )

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertTrue(data["allowed_to_stage"])
    self.assertTrue(data["allowed_to_prepare_approval"])
    self.assertTrue(data["allowed_to_delegate_execution"])
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertEqual(data["next_required_action"], "commit_stop_point")
    self.assertEqual(data["current_state"]["next_action"]["kind"], "commit_stop_point")

  def test_commit_with_no_pending_and_normal_changes_returns_zero(self):
    """未消化所見 0 件 + 通常変更 + ユーザ承認あり → exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    result = run_script(
      ["commit", "--rationale", "テスト用 commit、利用者承認の出典あり"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"未消化所見なし＋通常変更のみは通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_llm_commit_without_execution_delegation_returns_two(self):
    """LLM 実行では通常の commit 承認だけでは exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_execution_delegation=False,
    )

    result = run_script(
      ["commit", "--rationale", "内容承認のみで LLM commit しようとするテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_rejects_autonomous_until_next_commit_instruction(self):
    """次のコミットまで自律実行は commit 停止点到達指示であり代行承認ではない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="次のコミットまで自律実行",
    )

    result = run_script(
      ["commit", "--rationale", "次のコミットまで自律実行の誤解釈防止テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_rejects_autonomous_instruction_without_commit(self):
    """自律実行して、だけでは commit 実行代行承認にならない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="自律実行して",
    )

    result = run_script(
      ["commit", "--rationale", "自律実行して単独の誤解釈防止テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("コミット実行代行", result.stdout)

  def test_llm_commit_accepts_autonomous_with_commit_delegation_instruction(self):
    """コミット代行も含めて自律実行なら LLM commit を許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      execution_instruction="コミット代行も含めて自律実行",
    )

    result = run_script(
      ["commit", "--rationale", "コミット代行込みの自律実行テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_human_commit_precheck_allows_content_approval_without_delegation(self):
    """人間実行としての事前検査なら実行代行承認は不要"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_execution_delegation=False,
    )

    result = run_script(
      [
        "commit",
        "--rationale", "人間が commit する前の内容承認チェック",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_prepare_outputs_nonce_challenge_json(self):
    """commit-approval prepare は staged 内容に束縛した challenge JSON を出力する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")

    result = run_script(["commit-approval", "prepare", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    payload = json.loads(result.stdout)
    self.assertEqual(payload["status"], "prepared")
    self.assertEqual(payload["target_files"], ["notes.md"])
    self.assertRegex(payload["nonce"], r"^[0-9a-f]{32,}$")
    self.assertEqual(payload["target_digest"]["algorithm"], "commit-approval-v1")

  def test_commit_approval_prepare_invalidates_malformed_stale_delegation(self):
    """prepare は古い壊れた delegation を新しい承認フローの邪魔にしない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    stale_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text(
      json.dumps({
        "schema_version": 1,
        "approved_action": "commit_execution_delegation",
        "expires_at": "not-a-timestamp",
        "consumed": False,
        "invalidated": False,
      }, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")

    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stdout)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "承認")

  def test_commit_approval_record_no_source_json_validates_for_commit(self):
    """prepare→record --no-source-text は commit 検査で通る nonce 承認を作る"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text=None,
    )
    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    record_payload = json.loads(record_result.stdout)
    self.assertEqual(record_payload["status"], "recorded")
    approval = _read_commit_approval(self.tmpdir)
    self.assertEqual(approval["source_omission_reason"], "source_not_provided")
    self.assertEqual(approval["attestation_type"], "staged_content_nonce_binding")
    self.assertEqual(
      approval["guarantee_scope"],
      "staged_content_binding_not_ui_utterance_proof",
    )

    result = run_script(
      [
        "commit",
        "--rationale", "nonce 承認の commit 検査",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_record_rejects_piped_source_text(self):
    """内容承認本文は pipe では保存できない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    result = subprocess.run(
      [
        "python3", str(SCRIPT),
        "commit-approval", "record",
        "--nonce", challenge["nonce"],
        "--source-text-stdin",
        "--json",
      ],
      cwd=str(self.tmpdir),
      input="コミット\n",
      capture_output=True,
      text=True,
      timeout=10,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("TTY", result.stdout)

  def test_commit_approval_record_does_not_embed_execution_delegation_by_default(self):
    """nonce 承認 record は staged 内容承認だけを保存し、実行代行承認を既定で混ぜない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertNotIn("execution_delegation", approval)

  def test_commit_approval_delegate_execution_writes_separate_record(self):
    """実行代行承認は commit-approval とは別ファイルに保存する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    payload = json.loads(delegate_result.stdout)
    self.assertEqual(payload["status"], "delegated")
    self.assertEqual(
      payload["delegation_path"],
      ".reviewcompass/runtime/approvals/commit-execution-delegation.json",
    )
    approval = _read_commit_approval(self.tmpdir)
    self.assertNotIn("execution_delegation", approval)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["approved_action"], "commit_execution_delegation")
    self.assertEqual(delegation["delegated_action"], "commit")
    self.assertEqual(delegation["delegated_to"], "llm")
    self.assertEqual(delegation["approved_by"], "user")
    self.assertEqual(delegation["nonce"], challenge["nonce"])
    self.assertEqual(delegation["explicit_instruction"], "コミット")
    self.assertRegex(delegation["instruction_sha256"], r"^[0-9a-f]{64}$")
    self.assertEqual(
      delegation["attestation_type"],
      "commit_execution_delegation_nonce_binding",
    )
    self.assertEqual(
      delegation["guarantee_scope"],
      "stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof",
    )
    self.assertFalse(delegation["consumed"])
    self.assertFalse(delegation["invalidated"])
    self.assertNotIn("llm", delegation)
    self.assertNotIn("provider", delegation)
    self.assertNotIn("model", delegation)

  def test_commit_approval_delegate_execution_rejects_piped_source_text(self):
    """実行代行承認本文は pipe では保存できない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    result = subprocess.run(
      [
        "python3", str(SCRIPT),
        "commit-approval", "delegate-execution",
        "--nonce", challenge["nonce"],
        "--source-text-stdin",
        "--json",
      ],
      cwd=str(self.tmpdir),
      input="コミット\n",
      capture_output=True,
      text=True,
      timeout=10,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("TTY", result.stdout)

  def test_commit_approval_delegate_execution_accepts_approval_instruction(self):
    """2回目入力の「承認」を commit 実行代行承認として受け入れる"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "承認")

  def test_llm_commit_accepts_separate_execution_delegation_record(self):
    """LLM commit 実行は別ファイルの実行代行承認がある場合だけ通す"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    result_without_delegation = run_script(
      ["commit", "--rationale", "内容承認だけで LLM commit しようとするテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result_without_delegation)
    self.assertEqual(result_without_delegation.returncode, 2, result_without_delegation.stdout)
    self.assertIn("commit-execution-delegation", result_without_delegation.stdout)

    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)

    result_with_delegation = run_script(
      ["commit", "--rationale", "別ファイル実行代行承認付き commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result_with_delegation)
    self.assertEqual(result_with_delegation.returncode, 0, result_with_delegation.stdout)

  def test_commit_approval_delegate_execution_accepts_ok_instruction(self):
    """「OK」を commit 実行代行承認として受け入れる"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="OK\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "ok")

  def test_commit_approval_delegate_execution_accepts_shoudaku_instruction(self):
    """「承諾」を commit 実行代行承認として受け入れる"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="承諾\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation = _read_commit_execution_delegation(self.tmpdir)
    self.assertEqual(delegation["explicit_instruction"], "承諾")

  def test_commit_approval_delegate_execution_rejects_crlf_instruction(self):
    """実行代行承認の stdin は CR/CRLF を許容しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)

    delegate_result = _delegate_commit_execution(
      self.tmpdir,
      challenge["nonce"],
      source_text="コミット\r\n",
    )

    _assert_script_invoked(self, delegate_result)
    self.assertEqual(delegate_result.returncode, 2, delegate_result.stdout)
    self.assertIn("source text", delegate_result.stdout)

  def test_commit_rejects_tampered_execution_delegation_record(self):
    """実行代行承認レコードの target_digest が改ざんされていれば遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["target_digest"]["digest"] = "0" * 64
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認改ざん遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-execution-delegation", result.stdout)

  def test_commit_approval_delegate_execution_rejects_malformed_existing_delegation(self):
    """壊れた未消費 delegation record が既にある場合は上書きせず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["expires_at"] = "not-a-timestamp"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    duplicate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, duplicate_result)
    self.assertEqual(duplicate_result.returncode, 2, duplicate_result.stdout)
    self.assertIn("commit-execution-delegation", duplicate_result.stdout)

  def test_commit_rejects_execution_delegation_with_unknown_field(self):
    """delegation record に unknown field が混入したら commit gate で遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["unexpected_field"] = "unexpected"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認 unknown field 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("不明フィールド", result.stdout)

  def test_commit_rejects_execution_delegation_with_identity_field(self):
    """delegation record に LLM/provider/model 系 field が混入したら遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
    self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
    delegation["model"] = "gpt-test"
    delegation_path.write_text(
      json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "実行代行承認 identity field 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("model", result.stdout)

  def test_commit_approval_delegate_execution_redaction_failure_does_not_write_record(self):
    """delegate_execution の redaction failure は record を作らず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    delegation_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-execution-delegation.json"
    )
    commit_approval = _load_commit_approval_module()
    original_redact_source = commit_approval._redact_source

    def fail_redaction(_source_text):
      return None, "redaction_failed", ["forced failure"]

    commit_approval._redact_source = fail_redaction
    try:
      with self.assertRaisesRegex(ValueError, "redaction"):
        commit_approval.delegate_execution(
          Path(self.tmpdir),
          challenge["nonce"],
          "コミット\n",
        )
    finally:
      commit_approval._redact_source = original_redact_source

    self.assertFalse(delegation_path.exists())

  def test_nonce_commit_rejects_embedded_execution_delegation_without_separate_record(self):
    """nonce 承認では embedded execution_delegation があっても別 record なしなら遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["execution_delegation"] = {
      "delegated_to": "llm",
      "approved_by": "user",
      "explicit_instruction": "コミット",
    }
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "nonce 承認 embedded delegation bypass 遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-execution-delegation", result.stdout)

  def test_commit_approval_record_source_text_is_redacted(self):
    """stdin 承認本文は機微情報除去後に保存される"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text="承認します OPENAI_API_KEY=sk-proj-SECRET1234567890abcdef",
    )

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertIn("source_text_redacted", approval)
    self.assertNotIn("source_omission_reason", approval)
    self.assertNotIn("sk-proj-", approval["source_text_redacted"])
    self.assertIn("[除去:", approval["source_text_redacted"])

    result = run_script(
      [
        "commit",
        "--rationale", "redacted source 付き nonce 承認の commit 検査",
        "--execution-actor", "human",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_approval_record_residual_secret_omits_source(self):
    """redaction 後に秘密候補が残る場合は承認本文を保存しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)

    record_result = _record_commit_approval(
      self.tmpdir,
      challenge["nonce"],
      source_text="Aa0" * 20,
    )

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval = _read_commit_approval(self.tmpdir)
    self.assertEqual(approval["source_omission_reason"], "residual_secret_detected")
    self.assertNotIn("source_text_redacted", approval)
    self.assertIn("redaction_findings", approval)

  def test_commit_approval_record_rejects_malformed_challenge_target_files(self):
    """challenge の target_files が文字列配列でなければ補完せず fail-closed"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    challenge_record["target_files"] = "notes.md"
    challenge_path.write_text(
      json.dumps(challenge_record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 2, record_result.stdout)
    self.assertIn("target_files", record_result.stdout)

  def test_commit_approval_record_rejects_uppercase_challenge_target_digest(self):
    """challenge target_digest は小文字 hex の正規形だけを受け付ける"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    challenge_record["target_digest"]["digest"] = "A" * 64
    challenge_path.write_text(
      json.dumps(challenge_record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])

    _assert_script_invoked(self, record_result)
    self.assertEqual(record_result.returncode, 2, record_result.stdout)
    self.assertIn("target_digest digest", record_result.stdout)

  def test_commit_approval_rejects_staged_change_after_record(self):
    """record 後に staged 内容が変わったら nonce 承認は使えない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 承認時点")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    _stage_file(self.tmpdir, "notes.md", "# commit 実行時点")

    result = run_script(
      ["commit", "--rationale", "nonce 承認後の差分変更遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("commit-approval", result.stdout)

  def test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails(self):
    """legacy fallback の nonce 承認が失敗しても旧記録は凍結し runtime 側だけ invalidated にする"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 承認時点")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    runtime_approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    legacy_approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "approvals"
      / "commit-approval.json"
    )
    legacy_approval_path.parent.mkdir(parents=True)
    legacy_approval_path.write_text(
      runtime_approval_path.read_text(encoding="utf-8"),
      encoding="utf-8",
    )
    legacy_before = legacy_approval_path.read_text(encoding="utf-8")
    runtime_approval_path.unlink()
    _stage_file(self.tmpdir, "notes.md", "# commit 実行時点")

    result = run_script(
      ["commit", "--rationale", "legacy nonce fallback invalidation"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertEqual(legacy_approval_path.read_text(encoding="utf-8"), legacy_before)
    runtime_approval = json.loads(runtime_approval_path.read_text(encoding="utf-8"))
    self.assertTrue(runtime_approval["invalidated"])
    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    self.assertTrue(challenge_record["invalidated"])

  def test_commit_approval_rejects_expired_record(self):
    """expires_at を過ぎた nonce 承認は使えない"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["expires_at"] = (
      datetime.now(timezone.utc) - timedelta(seconds=1)
    ).isoformat()
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "期限切れ nonce 承認遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("期限切れ", result.stdout)

  def test_commit_approval_rejects_llm_metadata_fields(self):
    """nonce 承認 record に LLM/provider/model 系フィールドがあれば遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
    challenge = _prepare_commit_approval(self.tmpdir)
    record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
    self.assertEqual(record_result.returncode, 0, record_result.stderr)
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval.json"
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["model"] = "gpt-test"
    approval_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "LLM メタデータ混入遮断"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("model", result.stdout)

  def test_commit_approval_prepare_preserves_staged_gitlink_entry(self):
    """gitlink は削除扱いにせず mode/object_id を canonical target に残す"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    head = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    ).stdout.strip()
    subprocess.run(
      ["git", "update-index", "--add", "--cacheinfo", f"160000,{head},vendor/lib"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )

    challenge = _prepare_commit_approval(self.tmpdir)

    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    entries = challenge_record["target"]["entries"]
    self.assertEqual(challenge["target_files"], ["vendor/lib"])
    self.assertEqual(entries[0]["path"], "vendor/lib")
    self.assertEqual(entries[0]["mode"], "160000")
    self.assertEqual(entries[0]["object_id"], head)
    self.assertNotEqual(entries[0]["sha256"], "DELETED")

  def test_commit_approval_prepare_includes_rename_source_deletion(self):
    """rename は destination だけでなく source deletion も canonical target に含める"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "old.md", "# old name")
    subprocess.run(
      ["git", "commit", "-qm", "add old.md"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )
    subprocess.run(
      ["git", "mv", "old.md", "new.md"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )

    challenge = _prepare_commit_approval(self.tmpdir)

    challenge_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "commit-approval-challenge.json"
    )
    challenge_record = json.loads(challenge_path.read_text(encoding="utf-8"))
    entries_by_path = {
      entry["path"]: entry
      for entry in challenge_record["target"]["entries"]
    }
    self.assertEqual(challenge["target_files"], ["new.md", "old.md"])
    self.assertEqual(entries_by_path["old.md"]["status"], "D")
    self.assertEqual(entries_by_path["old.md"]["object_id"], "DELETED")
    self.assertEqual(entries_by_path["new.md"]["status"], "R")

  def test_commit_blocks_when_in_progress_file_exists(self):
    """stages/in-progress が非空なら commit は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    in_progress_dir = Path(self.tmpdir) / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )

    result = run_script(
      ["commit", "--rationale", "in-progress 遮断テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_allows_completed_maintenance_without_staging_mainline_reopen_state(self):
    """maintenance 完了 commit は本線 reopen state を同伴 stage しなくても許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    reopen_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-09.yaml"
    )
    reopen_path.parent.mkdir(parents=True)
    reopen_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 3\n"
      "next_step: 第3過程：stages/requirements.yaml#triad-review 再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#triad-review\n",
      encoding="utf-8",
    )
    maintenance_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "maintenance-2026-06-09-reopen-guard.yaml"
    )
    maintenance_path.parent.mkdir(parents=True)
    maintenance_path.write_text(
      "process_id: maintenance\n"
      "title: reopen guard\n"
      "mainline_blocked_by: stages/in-progress/reopen-procedure-2026-06-09.yaml\n"
      "completed_actions:\n"
      "  - guarded side track completed\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/maintenance-2026-06-09-reopen-guard.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/maintenance-2026-06-09-reopen-guard.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "maintenance side track 完了 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_allows_reopen_stop_point_when_in_progress_file_is_staged(self):
    """第2過程の commit 停止点は構造フィールドで通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：正本修正完了\n"
      "step_number: 2\n"
      "current_blocker: null\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_reopen_stop_point_text_without_structured_fields(self):
    """next_step の文言だけでは reopen 停止点 commit を許可しない"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "旧式 next_step 停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_blocks_reopen_stop_point_without_structured_kind(self):
    """commit_stop_point=true でも構造化 kind がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-08.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第2過程：停止点コミット\n"
      "step_number: 2\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_reason: 第2過程の正本修正完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-08.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-08.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "構造化不足の停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_allows_reopen_explicit_commit_stop_point_field(self):
    """next_step を壊さず commit_stop_point=true で reopen 停止点 commit を許可する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：implementation triad-review\n"
      "step_number: 3\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 3\n"
      "commit_stop_point_kind: drafting_complete\n"
      "commit_stop_point_gate: stages/implementation.yaml#drafting\n"
      "commit_stop_point_reason: 文言に依存しない人間向け説明\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-15.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-15.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 明示 commit_stop_point commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_allows_reopen_review_gate_commit_stop_point(self):
    """第3過程の review 系 gate 完了停止点は構造フィールドで通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# review gate 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：tasks approval\n"
      "step_number: 3\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 3\n"
      "commit_stop_point_kind: approval_complete\n"
      "commit_stop_point_gate: stages/tasks.yaml#approval\n"
      "commit_stop_point_reason: tasks approval 完了時点の停止点\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-15.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-15.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen review gate 停止点 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_allows_normal_workflow_cross_feature_phase_end(self):
    """通常 workflow の cross-feature phase 終端差分は通常 commit guard で通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    intent_before = {
      "drafting": True,
      "review": True,
      "approval": False,
      "reference": "stages/intent.yaml",
    }
    feature_partitioning = {
      "candidate-proposal": False,
      "approval": False,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    }
    _write_cross_feature_specs(
      self.tmpdir,
      intent_before,
      feature_partitioning,
    )
    subprocess.run(
      ["git", "add", ".reviewcompass/specs", "stages/feature-dependency.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "cross feature baseline"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    intent_after = dict(intent_before)
    intent_after["approval"] = True
    _write_cross_feature_specs(
      self.tmpdir,
      intent_after,
      feature_partitioning,
    )
    subprocess.run(
      ["git", "add", ".reviewcompass/specs"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    staged = subprocess.run(
      ["git", "diff", "--cached", "--name-only"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    ).stdout.splitlines()
    _write_commit_approval(self.tmpdir, staged)

    result = run_script(
      ["commit", "--rationale", "通常 workflow phase 終端 commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("[VERDICT] WARN", result.stdout)
    self.assertNotIn("[VERDICT] DEVIATION", result.stdout)

  def test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason(self):
    """commit_stop_point=true でも正当な implementation drafting 停止点でなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# reopen 停止点の記録")
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：implementation triad-review\n"
      "step_number: 3\n"
      "commit_stop_point: true\n"
      "commit_stop_point_reason: 手順外の停止点\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/reopen-procedure-2026-06-15.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        "notes.md",
        "stages/in-progress/reopen-procedure-2026-06-15.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "不正な commit_stop_point commit"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/in-progress", result.stdout)

  def test_commit_blocks_completed_reopen_without_impact_decisions(self):
    """reopen 完了 commit は下流影響判定表がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("downstream_impact_decisions", result.stdout)

  def test_commit_allows_completed_reopen_with_impact_decisions(self):
    """reopen 完了 commit は全 pending gate の下流影響判定表があれば通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: 既存要件で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: alignment 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響判定ありテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_completed_reopen_missing_completed_gate_decision(self):
    """完了済み gate は pending_gates から外れていても判定表で覆う必要がある"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions: []\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了済み gate 判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("completed_gates", result.stdout)
    self.assertIn("stages/requirements.yaml#triad-review", result.stdout)

  def test_commit_allows_completed_reopen_with_completed_gate_decisions(self):
    """完了済み gate の判定表があれば pending_gates が空でも通過する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates: []\n"
      "completed_gates:\n"
      "  - stages/requirements.yaml#triad-review\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#triad-review\n"
      "    feature_scope:\n"
      "      - foundation\n"
      "      - runtime\n"
      "      - evaluation\n"
      "      - analysis\n"
      "      - workflow-management\n"
      "      - self-improvement\n"
      "      - conformance-evaluation\n"
      "    decision: approved\n"
      "    rationale: triad-review 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/_cross_feature/reviews/summary.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了済み gate 判定ありテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_completed_reopen_missing_review_gates_after_canonical_change(self):
    """正本変更済み phase の reopen 完了は review 系 gate 不足を遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      ".reviewcompass/specs/foundation/requirements.md",
      "# Requirements\n\nUpdated requirements body.\n",
    )
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    impact_basis: implementation_ownership\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: 既存要件で受けられることを確認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "  - gate: stages/requirements.yaml#approval\n"
      "    feature_scope: all_features\n"
      "    decision: approved\n"
      "    rationale: alignment 判定を承認した。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      [
        "git",
        "add",
        ".reviewcompass/specs/foundation/requirements.md",
        "stages/completed/reopen-procedure-2026-06-09.yaml",
      ],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      [
        ".reviewcompass/specs/foundation/requirements.md",
        "stages/completed/reopen-procedure-2026-06-09.yaml",
      ],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の review gate 不足テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("stages/requirements.yaml#triad-review", result.stdout)
    self.assertIn("stages/requirements.yaml#review-wave", result.stdout)

  def test_commit_blocks_completed_reopen_without_feature_impact_basis(self):
    """feature impact 判定は任意フェーズで判定軸を明示しなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    feature_impact_decisions = "".join(
      f"  - feature: {feature}\n"
      "    decision: reopen_existing_feature\n"
      "    rationale: 既存 feature で受けるため reopen 対象にする。\n"
      "    evidence:\n"
      f"      - .reviewcompass/specs/{feature}/requirements.md\n"
      for feature in FEATURE_ORDER
    )
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/design.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - design\n"
      "feature_impact_decisions:\n"
      f"{feature_impact_decisions}"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/design.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: design は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/design.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 判定軸欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("impact_basis", result.stdout)

  def test_commit_blocks_completed_reopen_with_partial_feature_impact_decisions(self):
    """feature impact 判定は既存 feature 全件を覆わなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "feature_impact_decisions:\n"
      "  - feature: foundation\n"
      "    decision: reopen_existing_feature\n"
      "    rationale: foundation は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "new_feature_decision:\n"
      "  decision: no_new_feature\n"
      "  rationale: 既存 feature で受けられる。\n"
      "  evidence:\n"
      "    - stages/feature-partitioning/2026-05-24-proposal.md\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 網羅不足テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)

  def test_commit_blocks_completed_reopen_without_feature_impact_decisions(self):
    """reopen 完了 commit は feature impact 判定がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の feature impact 判定欠落テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("feature_impact_decisions", result.stdout)

  def test_commit_blocks_completed_reopen_when_impacted_phase_is_uncovered(self):
    """reopen 完了 commit は影響フェーズを覆う gate 判定がなければ遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    completed_path = (
      Path(self.tmpdir)
      / "stages"
      / "completed"
      / "reopen-procedure-2026-06-09.yaml"
    )
    completed_path.parent.mkdir(parents=True)
    completed_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 4\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "impacted_downstream_phases:\n"
      "  - requirements\n"
      "  - design\n"
      "downstream_impact_decisions:\n"
      "  - gate: stages/requirements.yaml#alignment\n"
      "    feature_scope: all_features\n"
      "    decision: existing_sufficient\n"
      "    rationale: requirements は確認済み。\n"
      "    evidence:\n"
      "      - .reviewcompass/specs/foundation/requirements.md\n"
      "next_step: 完了\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/completed/reopen-procedure-2026-06-09.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["stages/completed/reopen-procedure-2026-06-09.yaml"],
    )

    result = run_script(
      ["commit", "--rationale", "reopen 完了の影響フェーズ漏れテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("impacted_downstream_phases", result.stdout)

  def test_commit_blocks_reopen_marked_spec_without_reopen_procedure(self):
    """reopen 印のある spec.json 変更は reopen 手続きファイルなしでは遮断する"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _write_spec(
      self.tmpdir,
      "foundation",
      {
        "drafting": False,
        "triad-review": False,
        "review-wave": False,
        "alignment": False,
        "approval": False,
      },
    )
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "foundation"
      / "spec.json"
    )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"]["upstream_change_pending"] = True
    spec["recheck"]["impacted_downstream_phases"] = ["requirements"]
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    relpath = ".reviewcompass/specs/foundation/spec.json"
    subprocess.run(
      ["git", "add", relpath],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(self.tmpdir, [relpath])

    result = run_script(
      ["commit", "--rationale", "reopen 印 spec の手続きファイル必須テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("reopen 手続き", result.stdout)

  def test_commit_allows_reopen_marked_spec_with_reopen_procedure(self):
    """reopen 印のある spec.json 変更は reopen 手続きファイルがあれば逸脱ではない"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _write_spec(
      self.tmpdir,
      "foundation",
      {
        "drafting": False,
        "triad-review": False,
        "review-wave": False,
        "alignment": False,
        "approval": False,
      },
    )
    spec_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "foundation"
      / "spec.json"
    )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["recheck"]["upstream_change_pending"] = True
    spec["recheck"]["impacted_downstream_phases"] = ["requirements"]
    spec_path.write_text(
      json.dumps(spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    in_progress_path = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-09.yaml"
    )
    in_progress_path.parent.mkdir(parents=True)
    in_progress_path.write_text(
      "process_id: reopen-procedure\n"
      "step_number: 2\n"
      "next_step: 第2過程：停止点コミット\n"
      "commit_stop_point: true\n"
      "commit_stop_point_step: 2\n"
      "commit_stop_point_kind: canonical_update_complete\n",
      encoding="utf-8",
    )
    relpaths = [
      ".reviewcompass/specs/foundation/spec.json",
      "stages/in-progress/reopen-procedure-2026-06-09.yaml",
    ]
    subprocess.run(
      ["git", "add"] + relpaths,
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(self.tmpdir, relpaths)

    result = run_script(
      ["commit", "--rationale", "reopen 印 spec と手続きファイルのテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertNotEqual(result.returncode, 2, result.stdout)

  def test_commit_with_pending_findings_returns_one(self):
    """未消化所見 1 件以上 → exit 1（警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=1)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    result = run_script(
      ["commit", "--rationale", "未消化所見ありの場面のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"未消化所見ありは警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "WARN", result.stdout,
      f"警告判定の出力に WARN が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_with_spec_json_change_returns_one(self):
    """spec.json の変更含む → exit 1（要注意変更の警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      ".reviewcompass/specs/foundation/spec.json",
      '{"feature_name":"foundation"}',
    )
    _write_commit_approval(self.tmpdir, [".reviewcompass/specs/foundation/spec.json"])
    result = run_script(
      ["commit", "--rationale", "spec.json 更新のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"spec.json 変更は要注意変更として警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_plan_doc_change_returns_one(self):
    """計画書（docs/plan/ 配下）の変更含む → exit 1"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "docs/plan/test-plan.md", "# テスト計画")
    _write_completed_post_write_manifest(self.tmpdir, ["docs/plan/test-plan.md"])
    _write_commit_approval(self.tmpdir, ["docs/plan/test-plan.md"])
    result = run_script(
      ["commit", "--rationale", "計画書追加のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"docs/plan/ 配下の変更は要注意で警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_credential_file_returns_two(self):
    """ファイル名に credentials を含む変更 → exit 2（危険変更）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "credentials.json", '{"key":"dummy"}')
    _write_commit_approval(self.tmpdir, ["credentials.json"])
    result = run_script(
      ["commit", "--rationale", "credentials を含むファイルのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"credentials を含むファイル名は危険変更として逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_blocks_deployable_artifact_with_absolute_path(self):
    """deployable artifact にローカル絶対パスが混入した commit は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    relpath = "learning/workflow/deployment-readiness/bad.json"
    _stage_file(
      self.tmpdir,
      relpath,
      '{"path": "/Users/Daily/Development/ReviewCompass/config.yaml"}\n',
    )
    _write_commit_approval(self.tmpdir, [relpath])

    result = run_script(
      ["commit", "--rationale", "配置非依存 lint guard のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("配置非依存", result.stdout)
    self.assertIn(relpath, result.stdout)

  def test_commit_without_user_approval_returns_two(self):
    """ユーザ承認レコードなし → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_script(
      ["commit", "--rationale", "承認なし commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"承認レコードなしの commit は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn("ユーザ承認レコード", result.stdout)

  def test_commit_with_consumed_user_approval_returns_two(self):
    """消費済み承認レコード → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"], consumed=True)
    result = run_script(
      ["commit", "--rationale", "消費済み承認のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("消費済み", result.stdout)

  def test_commit_with_approval_scope_mismatch_returns_two(self):
    """承認対象と staged ファイルが一致しない → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["other.md"])
    result = run_script(
      ["commit", "--rationale", "承認対象不一致のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("承認対象外", result.stdout)

  def test_commit_with_missing_approval_target_sha256_returns_two(self):
    """承認レコードに target_sha256 がなければ exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(
      self.tmpdir,
      ["notes.md"],
      include_target_sha256=False,
    )
    result = run_script(
      ["commit", "--rationale", "承認 sha256 欠落のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("target_sha256", result.stdout)

  def test_commit_with_stale_approval_target_sha256_returns_two(self):
    """承認後に staged 内容が変わったら exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# 承認時点")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    _stage_file(self.tmpdir, "notes.md", "# 実行時点")
    result = run_script(
      ["commit", "--rationale", "古い承認レコードのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("sha256", result.stdout)

  def test_commit_with_deleted_file_and_deleted_sentinel_passes(self):
    """削除ファイルが staged で、承認レコードが "DELETED" sentinel を使えば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    # ファイルを作成してコミット済みにする
    _stage_file(self.tmpdir, "delete_me.md", "# 削除予定ファイル")
    subprocess.run(
      ["git", "commit", "-qm", "add delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # ファイルを削除してステージ
    subprocess.run(
      ["git", "rm", "-q", "delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # "DELETED" sentinel を使った承認レコード
    _write_commit_approval(
      self.tmpdir,
      ["delete_me.md"],
      target_sha256={"delete_me.md": "DELETED"},
    )
    result = run_script(
      ["commit", "--rationale", "削除ファイルを含むコミットのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(result.returncode, 2,
                        f"削除ファイル + DELETED sentinel は exit 2 にならないはず\n{result.stdout}")

  def test_commit_with_deleted_file_without_deleted_sentinel_returns_two(self):
    """削除ファイルに "DELETED" でない sha256 が指定されていれば exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "delete_me.md", "# 削除予定ファイル")
    subprocess.run(
      ["git", "commit", "-qm", "add delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    subprocess.run(
      ["git", "rm", "-q", "delete_me.md"],
      cwd=self.tmpdir, check=True, capture_output=True,
    )
    # 意図的に "DELETED" でないハッシュを指定
    _write_commit_approval(
      self.tmpdir,
      ["delete_me.md"],
      target_sha256={"delete_me.md": "not_the_deleted_sentinel"},
    )
    result = run_script(
      ["commit", "--rationale", "削除ファイル sha256 不一致のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)

  def test_commit_with_post_write_target_without_manifest_returns_two(self):
    """post-write 対象文書が staged され、完了 manifest がなければ exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "docs/notes/policy.md", "# 運用メモ")
    _write_commit_approval(self.tmpdir, ["docs/notes/policy.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 未検証の遮断テスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("post-write-verification 未完了", result.stdout)

  def test_commit_with_post_write_target_and_completed_manifest_returns_zero(self):
    """post-write 対象文書が staged されても完了 manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "docs/notes/policy.md", "# 運用メモ")
    _write_completed_post_write_manifest(self.tmpdir, ["docs/notes/policy.md"])
    _write_commit_approval(self.tmpdir, ["docs/notes/policy.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"完了 manifest がある post-write 対象 commit は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_operations_doc_and_completed_manifest_returns_zero(self):
    """docs/operations 配下の対象文書も completed manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      "docs/operations/WORKFLOW_PRECHECK.md",
      "# WORKFLOW_PRECHECK",
    )
    _write_completed_post_write_manifest(
      self.tmpdir,
      ["docs/operations/WORKFLOW_PRECHECK.md"],
    )
    _write_commit_approval(self.tmpdir, ["docs/operations/WORKFLOW_PRECHECK.md"])
    result = run_script(
      ["commit", "--rationale", "operations 文書検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_blocks_operations_doc_with_wrong_anchor_link(self):
    """文書リンクのアンカー誤りがある staged 文書は exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    source_path = "docs/operations/link-source.md"
    target_path = "docs/operations/link-target.md"
    _stage_file(
      self.tmpdir,
      source_path,
      "# Link Source\n\n[対象](link-target.md#missing-anchor)\n",
    )
    _stage_file(
      self.tmpdir,
      target_path,
      "# Existing Anchor\n",
    )
    _write_completed_post_write_manifest(self.tmpdir, [source_path, target_path])
    _write_commit_approval(self.tmpdir, [source_path, target_path])

    result = run_script(
      ["commit", "--rationale", "文書リンク検査の commit gate テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("文書リンク lint", result.stdout)
    self.assertIn("missing_anchor", result.stdout)

  def test_commit_checks_staged_document_link_content(self):
    """worktree が修正済みでも staged 文書にリンク誤りがあれば exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    source_path = "docs/operations/link-source.md"
    target_path = "docs/operations/link-target.md"
    _stage_file(
      self.tmpdir,
      source_path,
      "# Link Source\n\n[対象](link-target.md#missing-anchor)\n",
    )
    _stage_file(
      self.tmpdir,
      target_path,
      "# Existing Anchor\n",
    )
    source = Path(self.tmpdir) / source_path
    source.write_text(
      "# Link Source\n\n[対象](link-target.md#existing-anchor)\n",
      encoding="utf-8",
    )
    _write_completed_post_write_manifest(self.tmpdir, [source_path, target_path])
    staged_hash = {
      source_path: _staged_sha256_file(self.tmpdir, source_path),
      target_path: _staged_sha256_file(self.tmpdir, target_path),
    }
    _write_commit_approval(
      self.tmpdir,
      [source_path, target_path],
      target_sha256=staged_hash,
    )

    result = run_script(
      ["commit", "--rationale", "staged 文書リンク検査のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("文書リンク lint", result.stdout)
    self.assertIn("missing_anchor", result.stdout)

  def test_commit_rationale_is_required(self):
    """commit に --rationale なし → 非 0 終了（仕様 §5.2 必須）"""
    _stage_file(self.tmpdir, "notes.md", "test")
    result = run_script(["commit"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class PushExitCodeTests(unittest.TestCase):
  """push サブコマンドの終了コード判定（仕様 §6.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_push_with_clean_tree_returns_zero(self):
    """作業ツリーが clean → exit 0"""
    result = run_script(
      ["push", "--rationale", "clean な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"作業ツリー clean は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_push_allows_clean_tree_when_in_progress_file_exists(self):
    """stages/in-progress があっても clean なら push は遮断しない"""
    in_progress_dir = Path(self.tmpdir) / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process.yaml").write_text(
      "next_step: human approval\n",
      encoding="utf-8",
    )
    subprocess.run(
      ["git", "add", "stages/in-progress/manual-process.yaml"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "add in-progress marker"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(
      ["push", "--rationale", "in-progress 遮断テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    self.assertIn("OK", result.stdout)
    self.assertNotIn("[CURRENT STATE]", result.stdout)

  def test_push_with_dirty_tree_returns_two(self):
    """作業ツリーが dirty（未追跡ファイルあり）→ exit 2"""
    (Path(self.tmpdir) / "untracked.md").write_text("# 未追跡")
    result = run_script(
      ["push", "--rationale", "dirty な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"作業ツリー dirty は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_push_with_ahead_commit_without_commit_precheck_record_returns_two(self):
    """先行 commit があり、直前 commit 検査記録がなければ exit 2"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _stage_file(self.tmpdir, "notes.md", "# push 対象")
    subprocess.run(
      ["git", "commit", "-qm", "add push target"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(
      ["push", "--rationale", "commit 検査記録なし push のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("last-commit-precheck", result.stdout)

  def test_push_with_ahead_commit_and_matching_commit_precheck_record_returns_zero(self):
    """先行 commit の HEAD と直前 commit 検査記録が一致すれば exit 0"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _stage_file(self.tmpdir, "notes.md", "# push 対象")
    subprocess.run(
      ["git", "commit", "-qm", "add push target"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_last_commit_precheck(self.tmpdir)

    result = run_script(
      ["push", "--rationale", "commit 検査記録あり push のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_push_blocks_ahead_deployable_artifact_with_absolute_path(self):
    """先行 commit の deployable artifact にローカル絶対パスがあれば push は exit 2"""
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    relpath = "learning/workflow/deployment-readiness/bad.json"
    _stage_file(
      self.tmpdir,
      relpath,
      '{"path": "/Users/Daily/Development/ReviewCompass/config.yaml"}\n',
    )
    subprocess.run(
      ["git", "commit", "-qm", "add bad deployable artifact"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_last_commit_precheck(self.tmpdir)

    result = run_script(
      ["push", "--rationale", "push 配置非依存 lint guard のテスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("配置非依存", result.stdout)
    self.assertIn(relpath, result.stdout)

  def test_push_rationale_is_required(self):
    """push に --rationale なし → 非 0 終了（仕様 §5.3 必須）"""
    result = run_script(["push"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class AuditCommitTests(unittest.TestCase):
  """audit-commit サブコマンドの post-write 遡及監査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _commit_file(self, relpath, content, message):
    _stage_file(self.tmpdir, relpath, content)
    subprocess.run(
      ["git", "commit", "-qm", message],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def test_audit_commit_detects_post_write_target_without_manifest(self):
    """指定 commit に post-write 対象があり manifest がなければ exit 2"""
    self._commit_file("docs/notes/policy.md", "# 運用メモ", "add policy note")
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("docs/notes/policy.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_detects_root_commit_post_write_target_without_manifest(self):
    """root commit の post-write 対象追加も監査対象に含める"""
    tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, tmpdir)
    for cmd in [
      ["git", "init", "-q", "-b", "main"],
      ["git", "config", "user.email", "test@example.com"],
      ["git", "config", "user.name", "Test User"],
      ["git", "config", "commit.gpgsign", "false"],
    ]:
      subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
    _stage_file(tmpdir, "docs/notes/policy.md", "# root policy")
    subprocess.run(
      ["git", "commit", "-qm", "root todo"],
      cwd=str(tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(["audit-commit", "HEAD", "--json"], cwd=tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("docs/notes/policy.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_accepts_post_write_target_with_matching_manifest(self):
    """指定 commit の post-write 対象を覆う manifest があれば exit 0"""
    self._commit_file("docs/notes/policy.md", "# 運用メモ", "add policy note")
    _write_completed_post_write_manifest(self.tmpdir, ["docs/notes/policy.md"])
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"matching manifest should pass.\nstdout: {result.stdout}\nstderr: {result.stderr}",
    )


class CommitPushOutputTests(unittest.TestCase):
  """commit／push の JSON 出力検査（仕様 §7.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_json_output(self):
    """commit に --json で JSON 出力に切り替わる"""
    _write_commit_approval(self.tmpdir, [])
    result = run_script(
      ["commit", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "commit",
      "JSON 出力の action.subcommand は 'commit' であるべき",
    )
    self.assertIn("commit_approval", data["current_state"])

  def test_push_json_output(self):
    """push に --json で JSON 出力に切り替わる"""
    result = run_script(
      ["push", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "push",
      "JSON 出力の action.subcommand は 'push' であるべき",
    )


def _write_feature_dependency(cwd, relative_path, feature_order=None, features=None):
  """feature-dependency.yaml を指定パスに作る"""
  path = Path(cwd) / relative_path
  path.parent.mkdir(parents=True, exist_ok=True)
  data = {}
  if feature_order is not None:
    data["feature_order"] = feature_order
  if features is not None:
    data["features"] = features
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _write_app_spec(cwd, feature, requirements_drafting=False):
  """対象アプリ想定の最小 spec.json（intent と feature-partitioning のみ完了）を作る"""
  spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
  spec_dir.mkdir(parents=True, exist_ok=True)
  untouched_five_stage = {
    "drafting": requirements_drafting,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  untouched_rest = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  spec = {
    "feature_name": feature,
    "language": "ja",
    "created_at": "2026-06-11T00:00:00+09:00",
    "updated_at": "2026-06-11T00:00:00+09:00",
    "workflow_state": {
      "intent": {
        "drafting": True,
        "review": True,
        "approval": True,
        "reference": "stages/intent.yaml",
      },
      "feature-partitioning": {
        "candidate-proposal": True,
        "approval": True,
        "reference": "stages/feature-partitioning/2026-06-11-proposal.md",
      },
      "requirements": dict(untouched_five_stage),
      "design": dict(untouched_rest),
      "tasks": dict(untouched_rest),
      "implementation": dict(untouched_rest),
    },
    "reopened": {},
    "recheck": {
      "upstream_change_pending": False,
      "impacted_downstream_phases": [],
    },
  }
  (spec_dir / "spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )


class FeatureOrderGeneralizationTests(unittest.TestCase):
  """feature 一覧の外出し（feature-dependency.yaml の feature_order キー）

  設計記録：docs/notes/2026-06-10-deployment-multi-llm-entry-design.md §3.5
  side track 記録：stages/in-progress/maintenance-2026-06-11-feature-order-generalization.yaml
  TDD 規律に従い、実装前に作成。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _next_json(self):
    result = run_script(["next", "--json"], cwd=self.tmpdir)
    self.assertNotEqual(result.stdout.strip(), "", f"stderr: {result.stderr}")
    return result, json.loads(result.stdout)

  def test_next_uses_feature_order_from_reviewcompass_dir(self):
    """対象アプリ独自の feature 構成を .reviewcompass/feature-dependency.yaml から読む"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a", "appfeat-b"],
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")
    self.assertEqual(data["next_action"]["phase"], "requirements")
    self.assertEqual(data["next_action"]["stage"], "drafting")
    self.assertEqual(
      data["current_state"]["feature_order"], ["appfeat-a", "appfeat-b"],
    )

  def test_reviewcompass_dir_takes_priority_over_stages(self):
    """.reviewcompass/ の定義が stages/ より優先される"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=["other-feat"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")
    self.assertEqual(data["current_state"]["feature_order"], ["appfeat-a"])

  def test_stages_fallback_is_used_without_reviewcompass_file(self):
    """.reviewcompass/ になければ stages/feature-dependency.yaml を使う（開発リポジトリ互換）"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")

  def test_root_fallback_is_used_without_stages_file(self):
    """stages/ にもなければ直下の feature-dependency.yaml を使う"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "feature-dependency.yaml",
      feature_order=["appfeat-a"],
    )
    _write_app_spec(cwd, "appfeat-a")
    result, data = self._next_json()
    self.assertEqual(data["next_action"]["feature"], "appfeat-a")

  def test_missing_file_returns_bootstrap_guidance(self):
    """feature-dependency.yaml がない場合は立ち上げ案内を返す（エラーにしない）"""
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "feature_definition_required")
    reason = data["next_action"]["reason"]
    self.assertIn("feature-dependency.yaml が見つかりません", reason)
    self.assertIn("intent", reason)
    self.assertIn("feature-partitioning", reason)
    self.assertIn(".reviewcompass/feature-dependency.yaml", reason)

  def test_missing_key_returns_bootstrap_guidance_with_distinct_reason(self):
    """ファイルはあるが feature_order キーがない場合は、理由を区別して案内する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      features={"appfeat-b": {"depends_on": {"appfeat-a": "hard"}}},
    )
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(result.returncode, 0)
    self.assertEqual(data["next_action"]["kind"], "feature_definition_required")
    reason = data["next_action"]["reason"]
    self.assertIn("feature_order", reason)
    self.assertIn("定義されていません", reason)
    self.assertNotIn("見つかりません", reason)

  def test_unreadable_file_is_deviation(self):
    """ファイルはあるが YAML として読めない場合は案内ではなく遮断する（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    broken = cwd / "stages" / "feature-dependency.yaml"
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("feature_order: [unclosed\n", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_empty_file_is_deviation_with_record_prompting_reason(self):
    """空ファイルは遮断し、理由で feature_order の記録を促す（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    empty = cwd / "stages" / "feature-dependency.yaml"
    empty.parent.mkdir(parents=True, exist_ok=True)
    empty.write_text("", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("空", reasons)
    self.assertIn("feature_order", reasons)
    self.assertIn("記録", reasons)

  def test_undecodable_file_is_deviation(self):
    """UTF-8 として読めないファイルも遮断する（Req 8 受入 9、MLE-DEC-005。デコード失敗の fail-closed）"""
    cwd = Path(self.tmpdir)
    binary = cwd / "stages" / "feature-dependency.yaml"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_bytes(b"\xff\xfe\x00broken\x80binary")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_non_mapping_top_level_is_deviation(self):
    """最上位が連想配列でないファイルは遮断する（Req 8 受入 9、MLE-DEC-005）"""
    cwd = Path(self.tmpdir)
    bad = cwd / "stages" / "feature-dependency.yaml"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("- foundation\n- runtime\n", encoding="utf-8")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("stages/feature-dependency.yaml", reasons)
    self.assertIn("内容を確認", reasons)

  def test_order_contradicting_dependency_is_deviation(self):
    """依存される機能が後ろに並ぶ feature_order は逸脱として理由つきで指摘する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-b", "appfeat-a"],
      features={"appfeat-b": {"depends_on": {"appfeat-a": "hard"}}},
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    self.assertEqual(data["next_action"]["kind"], "unknown")
    reasons = " ".join(data["reasons"])
    self.assertIn("feature_order が depends_on と矛盾", reasons)
    self.assertIn("appfeat-a", reasons)
    self.assertIn("appfeat-b", reasons)

  def test_cyclic_dependency_is_deviation(self):
    """depends_on の循環依存は逸脱として検出する"""
    cwd = Path(self.tmpdir)
    _write_feature_dependency(
      cwd,
      ".reviewcompass/feature-dependency.yaml",
      feature_order=["appfeat-a", "appfeat-b"],
      features={
        "appfeat-a": {"depends_on": {"appfeat-b": "hard"}},
        "appfeat-b": {"depends_on": {"appfeat-a": "hard"}},
      },
    )
    _write_app_spec(cwd, "appfeat-a")
    _write_app_spec(cwd, "appfeat-b")
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(result.returncode, 2)
    reasons = " ".join(data["reasons"])
    self.assertIn("循環", reasons)

  def test_dev_repo_stages_file_defines_seven_features(self):
    """開発リポジトリの stages/feature-dependency.yaml が 7 機能の feature_order を持つ"""
    data = yaml.safe_load(
      (REPO_ROOT / "stages" / "feature-dependency.yaml").read_text(encoding="utf-8"),
    )
    self.assertEqual(data.get("feature_order"), FEATURE_ORDER)

  def test_completed_state_is_preserved_with_file_based_order(self):
    """ファイル由来の feature_order でも全機能完了の判定は従来どおり completed"""
    cwd = Path(self.tmpdir)
    complete = {
      "drafting": True,
      "triad-review": True,
      "review-wave": True,
      "alignment": True,
      "approval": True,
    }
    _write_specs_for_next(cwd, {feature: dict(complete) for feature in FEATURE_ORDER})
    _write_feature_dependency(
      cwd,
      "stages/feature-dependency.yaml",
      feature_order=list(FEATURE_ORDER),
    )
    result, data = self._next_json()
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "completed")


if __name__ == "__main__":
  unittest.main()


## docs/operations/WORKFLOW_PRECHECK.md

# WORKFLOW_PRECHECK：ワークフロー事前検査の運用契約

本文書は `tools/check-workflow-action.py` と関連ラッパーの運用契約を定める。詳細な引数、判定条件、出力構造、テスト観点は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md) を参照する。仕様の変更には人の明示承認が必要である。

## 1. 目的

ワークフロー事前検査は、不可逆操作の直前に現在のワークフロー状態との整合を機械判定するための仕組みである。

対象となる不可逆操作：

1. spec.json の `workflow_state` 変更
2. git commit
3. git push

## 2. 役割分担

ワークフロー事前検査は、次の 3 段階で扱う。

- **段階 1**：LLM または作業者が、不可逆操作の直前に本スクリプトを呼び出し、結果を解釈する
- **段階 2**：本スクリプトが、状態を読み取り、判定結果を返す
- **段階 3**：実行環境の hook 連携が、呼び忘れを機械的に遮断する

段階 2 は判定だけを行う。承認取得、状態変更、人への問い合わせ、強制遮断は行わない。

## 3. 適用範囲

本スクリプトは次を対象とする。

- `spec-set`：spec.json の workflow_state 変更前検査
- `commit-preflight`：commit 指示直後、stage / approval 作成前の read-only 入口検査
- `commit-approval`：staged 内容に束縛した commit approval challenge、内容承認、実行代行承認、無効化の記録
- `commit`：commit 前検査
- `push`：push 前検査
- `audit-commit`：commit 済み変更に対する post-write-verification 監査
- `reopen-advance-step`：reopen 第1・第2過程の完了更新
- `reopen-advance-gate`：reopen 中の pending gate 完了更新
- `reopen-set-blocker`：reopen 中の approval 承認待ち blocker 設定
- `reopen-finalize`：reopen 第4過程の完了 YAML 生成と completed 移動
- `autonomous-plan`：自律・並列実行計画の開始前検査
- `autonomous-plan-template`：自律・並列実行計画テンプレート生成
- `autonomous-plan-record-integration`：自律・並列実行の統合結果記録
- `commit-from-current-staged.py`：現在の staged index に束縛した approval 作成と guarded commit を 1 コマンドで連続実行するラッパー
- `guarded-git-commit.py`：commit 前検査つき git commit ラッパー

対象外：

- 仕様文書ファイルの編集前検査
- 計画文書の編集前検査
- 応答テキストだけの妥当性判定

適用範囲を拡張する場合は、本文書を改訂して人の明示承認を受ける。

## 4. 呼び出し契約

基本形：

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit-preflight
tools/check-workflow-action.py commit-approval prepare --json
tools/check-workflow-action.py commit-approval record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]
tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin [--json]
tools/check-workflow-action.py commit-approval invalidate [--json]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
tools/check-workflow-action.py reopen-set-blocker --file <path> --gate stages/<phase>.yaml#approval --actor human|proxy_model --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

commit は人の職掌範囲である。利用者が commit を指示した直後は、Git index への追加（`git add`）、commit approval challenge、approval record、execution delegation record、guarded commit のいずれを作る前にも、まず `commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、commit できない理由、何も作らず止めたこと、次に許可されている workflow action だけを短く報告する。利用者の単発 commit 指示は staged 内容承認と LLM commit 実行代行承認として扱える。`--execution-actor llm` の場合も、この直近の利用者発話を実行代行の明示承認の出典にできるが、LLM が利用者発話なしに承認文を生成してはならない。実行時は直接 `git commit` ではなく、原則として `tools/commit-from-current-staged.py` を使う。

`tools/commit-from-current-staged.py` は TTY からの対話的な承認 1 行を必須とし、pipe / heredoc / redirect など非 TTY 入力、空入力、許可文言外の入力なら challenge 作成前に停止する。承認 1 行は直近の利用者発話または利用者による対話入力に限る。利用者の単発 commit 指示を転送する場合、その 1 行を staged 内容承認と LLM commit 実行代行承認の source として記録する。LLM が `printf` 等で生成して渡してはならず、LLM が利用者発話なしに承認文を生成してはならない。承認文を確認した後、古い runtime approval/delegation を無効化し、現在の staged exact index の digest で challenge を作り、同一プロセス内で approval / execution delegation を記録してから `tools/guarded-git-commit.py` を呼び出す。これにより、古い approval の残存、nonce の手写し、challenge 作成後の別操作、空 stdin 実行、LLM 生成承認文の混入を標準導線から外す。

nonce 方式の commit approval を低レベル手順として使う場合、commit 準備は逐次手順として扱う。stage 後に `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を実行し、返された nonce で `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を起動する。`commit-approval prepare` と `commit --json` precheck を並列に実行しない。challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まず、guarded commit に直近の利用者発話で明示された commit 指示を 1 行として渡す。`--approval-source-text-line-stdin` は TTY からの対話入力だけを受け付け、空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行してはいけない。

Codex の `workspace-write` sandbox では、`commit-from-current-staged.py` または `guarded-git-commit.py` が最終的に `.git/index.lock` へ書き込む段階で sandbox に拒否され得る。このため Codex から commit を実行する場合は、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

commit 実行時のユーザー向け報告は、guard や precheck の詳細出力をそのまま貼らず、結論だけを短く伝える。成功時は commit hash と commit message、必要なら検証コマンドだけを報告する。失敗時は停止理由を 1〜3 点に要約し、承認再作成、staged 対象の見直し、post-write 未完了など、次に必要な操作だけを示す。詳細ログは必要時に参照できる状態に留め、通常の進行報告には含めない。

<a id="spec-set"></a>

### 4.1 spec-set

`spec-set` は、spec.json の `workflow_state` を変更する直前に呼び出す。段順序、上流フェーズ完了、reopen pending、機能横断段の整合を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#spec-set) を参照する。

<a id="commit"></a>

### 4.2 commit

`commit` は、git commit の直前に呼び出す。承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。

`commit-preflight` は `commit` より前、利用者の commit 指示直後に呼び出す。現在の workflow action が commit operation に入ってよい状態かを read-only で判定し、stage や approval 作成に進んでよいかを返す。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit-preflight) を参照する。

<a id="push"></a>

### 4.3 push

`push` は、git push の直前に呼び出す。作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#push) を参照する。

<a id="audit-commit"></a>

### 4.4 audit-commit

`audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を監査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#audit-commit) を参照する。

<a id="reopen-start"></a>

### 4.5 reopen-start

reopen 開始時は、上流正本変更の影響範囲を分類し、必要な reopen 手続き記録を作成してから通常ワークフローへ戻す。commit 時には、reopen 手続き記録と spec.json の recheck 状態の整合を検査する。詳細は [REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) と [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。

<a id="reopen-advance-step"></a>

### 4.6 reopen-advance-step

`reopen-advance-step` は、reopen 第1過程または第2過程の完了を記録し、次の state へ進めるときに呼び出す。`--from-step` は現在の `step_number` と一致していなければならず、判断理由と証跡なしの更新は拒否する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-step) を参照する。

<a id="reopen-advance-gate"></a>

### 4.7 reopen-advance-gate

`reopen-advance-gate` は、reopen 第3過程で pending gate を 1 件完了扱いへ進めるときに呼び出す。対象 gate、判断、根拠、必要な `spec.json` 更新を構造化入力で受け取り、reopen 手続き記録の `pending_gates`、`completed_gates`、`downstream_impact_decisions`、`completed_steps` を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-gate) を参照する。

<a id="reopen-set-blocker"></a>

### 4.8 reopen-set-blocker

`reopen-set-blocker` は、reopen 第3過程で pending gate の先頭が approval gate に到達し、human または proxy_model の承認待ちで停止するときに呼び出す。対象 gate、承認主体、理由、根拠を構造化入力で受け取り、`current_blocker` を構造化 object として設定する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-set-blocker) を参照する。

<a id="reopen-finalize"></a>

### 4.9 reopen-finalize

`reopen-finalize` は、reopen 第4過程で in-progress 手続き YAML を completed 側へ移すときに呼び出す。feature impact 判定、new feature 判定、影響 phase を構造化入力で受け取り、完了 YAML に必要な項目を機械更新する。対象 feature の `spec.json` が存在する場合は recheck クリアと第4過程完了履歴の追加も同じ操作で行う。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-finalize) を参照する。

## 5. 判定契約

終了コード：

- `0`：問題なし。処理続行可
- `1`：警告あり。呼び出し側の判断で続行可
- `2`：逸脱検出。呼び出し側は停止する

主要な判定対象：

- `spec-set` は、段順序、上流フェーズ完了、reopen pending、機能横断段の整合を検査する
- `commit-preflight` は、commit operation 入口で stage / approval 作成へ進んでよい workflow 状態かを検査する
- `commit-approval` は、staged exact index に束縛した nonce challenge、内容承認、実行代行承認、無効化を記録する
- `commit` は、承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する
- `push` は、作業ツリーの clean 性、ローカル先行コミット数、commit 事前検査記録、push 先を検査する。`stages/in-progress/` が存在するだけでは遮断しない
- `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
- `reopen-advance-step` は、現在 step と `--from-step` の一致、完了説明、判断理由、証跡を検査する
- `reopen-advance-gate` は、pending gate 文字列が review 系 gate の正規形であること、先頭の pending gate だけを完了扱いに進めること、根拠なし更新を検査する
- `reopen-set-blocker` は、pending gate 先頭の approval gate だけに、根拠つきの構造化 blocker を設定できることを検査する
- `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査し、対象 feature の recheck クリアと第4過程完了履歴追加を一括で行う
- `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する

## 6. 出力とログ

既定出力は人間可読形式とし、少なくとも次を含める。

- 判定結果
- 対象サブコマンド
- 判定理由
- 必要な現在状態の要約

`--json` 指定時は、機械処理向けに同等の情報を構造化して出力する。

判定ログは JSON Lines 形式で記録する。既定パスは `.reviewcompass/runtime/logs/workflow-precheck.log` とし、`--log-path` で上書きできる。旧 `docs/logs/workflow-precheck.log` は legacy path として扱う。

## 7. テスト契約

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。

最低限、次の系統を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更の検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `reopen-advance-step`、`reopen-advance-gate`、`reopen-set-blocker`、`reopen-finalize` の構造更新と fail-closed 検査
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

## 8. 配置

主要ファイル：

- `tools/check-workflow-action.py`
- `tools/guarded-git-commit.py`
- `tests/tools/test_check_workflow_action.py`
- `docs/operations/WORKFLOW_PRECHECK.md`

補助モジュールを分割する場合は `tools/workflow_precheck/` 配下に置く。

## 9. 段階 1・段階 3 との接続

段階 1 は、不可逆操作の直前に本スクリプトを呼び出す。

- spec.json の `workflow_state` 変更直前：`spec-set`
- git commit 直前：`commit` または `guarded-git-commit.py`
- git push 直前：`push`

段階 3 の hook 連携は、同じ判定を実行環境側で自動発動する。導入時は人の明示承認を必須とする。


## docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# WORKFLOW_PRECHECK 詳細仕様

本文書は `tools/check-workflow-action.py`、`tools/commit-from-current-staged.py`、`tools/guarded-git-commit.py` の詳細仕様を定める。運用時に読む短い契約は [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md) を正とし、本書は実装・保守・テストで必要な詳細を補う。

## 1. サブコマンド

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit-preflight
tools/check-workflow-action.py commit-approval prepare --json
tools/check-workflow-action.py commit-approval record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]
tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin [--json]
tools/check-workflow-action.py commit-approval invalidate [--json]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
tools/check-workflow-action.py reopen-set-blocker --file <path> --gate stages/<phase>.yaml#approval --actor human|proxy_model --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

<a id="spec-set"></a>

## 2. spec-set

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `<feature>` | 必須 | 対象機能名。`stages/feature-dependency.yaml` の `features` キーと一致する |
| `<phase>` | 必須 | 対象フェーズ |
| `<stage>` | 必須 | 対象段。フェーズにより有効値が異なる |
| `<new-value>` | 必須 | `true` または `false` |
| `--rationale` | 任意 | 変更理由。ログ記録用であり判定値には影響しない |

`<new-value>` が `true` の場合、次を検査する。

- 同フェーズ内で当該段より前の段が完了していること
- 上流フェーズの最終段が完了していること
- `recheck.upstream_change_pending=true` の影響対象 phase を完了扱いに戻していないこと
- `intent` と `feature-partitioning` のような機能横断段で、単一 feature だけを不整合に変えていないこと

`<new-value>` が `false` の場合、reopen 手続きの一部として原則許容する。ただし、完了済み段を戻す場合は警告を返す。

<a id="commit"></a>

## 3. commit

<a id="commit-preflight"></a>

### 3.0 commit-preflight

`commit-preflight` は、利用者が commit を指示した直後、stage / approval challenge / approval record / execution delegation record / guarded commit のいずれかを作る前に実行する read-only 入口検査である。利用者の単発 commit 指示は staged 内容承認と LLM commit 実行代行承認の出典にできるが、LLM が利用者発話なしに承認文を生成してはならない。

出力は少なくとも次を持つ。

- `verdict`: `OK` または `DEVIATION`
- `allowed_to_stage`
- `allowed_to_prepare_approval`
- `allowed_to_delegate_execution`
- `allowed_to_run_guarded_commit`
- `next_required_action`
- `reasons`
- `current_state.next_action`

判定順序：

1. `stages/in-progress/` がある場合、現在位置が構造化された reopen `commit_stop_point` かを確認する。
2. `commit_stop_point` でない reopen / maintenance / resume 途中状態なら `DEVIATION` とし、stage / approval 作成へ進まない。
3. ただし、本線 reopen 中に対応する `stages/completed/maintenance-*.yaml` が未コミット差分にあり、その `mainline_blocked_by` が全 in-progress reopen を覆う場合は、maintenance 完了 commit 候補として stage / approval 作成を許可する。この場合、本線 `stages/in-progress/reopen-*.yaml` は commit 対象に含めない。side-track 完了 commit のために本線 state を人工的に変更しない。
4. post-write-verification 対象の未完了変更がある場合は `DEVIATION` とし、stage / approval 作成へ進まない。
5. 通常 workflow の phase 終端停止点、reopen の構造化停止点、maintenance 完了 commit 候補では stage / approval 作成を許可する。
6. `allowed_to_run_guarded_commit` は、staged ファイルがあり、commit approval と execution delegation が現在の staged 内容に対して有効な場合だけ `true` にする。

`DEVIATION` の場合、LLM は stage、approval challenge、approval record、execution delegation record、guarded commit のいずれにも進まない。

### 3.1 commit-approval

`commit-approval` は、`commit-preflight` が commit 準備を許可した後、Git index への追加（`git add`）済みの staged exact index に束縛して approval 系 record を作る。

サブコマンド：

| サブコマンド | 役割 |
|---|---|
| `prepare --json` | staged exact index から nonce challenge を作る |
| `record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]` | nonce に対応する commit 内容承認を保存する |
| `delegate-execution --nonce <nonce> --source-text-stdin [--json]` | LLM による commit 実行代行承認を保存する |
| `invalidate [--json]` | challenge と承認レコードを無効化する |

`prepare` 後は staged index を変更しない。内容承認と実行代行承認は同じ nonce / target digest に束縛され、guarded commit で照合される。

### 3.2 commit

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | commit 理由。人による承認の出典を含めることを推奨する |
| `--execution-actor` | 任意 | commit 実行主体。`llm` または `human`。既定は `llm` |

`--execution-actor llm` の場合、通常の commit 内容承認とは別に、LLM による実行代行承認を必要とする。

承認レコードの最小形：

```json
{
  "approved_action": "commit",
  "approved_by": "user",
  "approved_at": "2026-06-03T00:00:00+09:00",
  "rationale": "人がコミットを明示承認",
  "target_files": ["path/to/file.md"],
  "execution_delegation": {
    "delegated_to": "llm",
    "approved_by": "user",
    "approved_at": "2026-06-03T00:00:00+09:00",
    "explicit_instruction": "コミット",
    "rationale": "人が単発 commit 実行を明示指示"
  },
  "expires_after_commit": true,
  "consumed": false
}
```

判定対象：

- commit 承認レコード（新配置 `.reviewcompass/runtime/approvals/commit-approval.json`、旧配置 `.reviewcompass/approvals/commit-approval.json`）が存在し、形式が正しく、未消費であること。読み取りは新→旧の順で解決する
- staged ファイルが `target_files` の範囲内であること
- LLM 実行時は `execution_delegation` があること
- staged ファイルに post-write-verification 対象がある場合、現在 sha256 を覆う completed manifest があること
- staged された `spec.json` に reopen 印がある場合、同じ commit に reopen 手続き記録が含まれること
- reopen 完了記録が含まれる場合、feature impact 判定、下流影響判定、影響フェーズ網羅が記録されていること
- 持ち越し所見の件数を確認し、未消化所見があれば警告すること
- staged ファイルを通常変更、要注意変更、危険変更に分類すること
- staged 文書の Markdown リンク、アンカー、既知の意味的組み合わせを `tools/document_link_lint.py` で検査すること

危険変更がある場合は逸脱とする。要注意変更は警告とする。

`tools/commit-from-current-staged.py` は、TTY からの対話的な stdin 承認 1 行を検査してから `commit_approval.prepare()` を呼び、現在の staged exact index に束縛した challenge を作る。古い runtime approval/delegation は `prepare()` により invalidated になる。返された nonce は同じ process 内で内容承認と実行代行承認に使い、子プロセスへ承認文を pipe しない。stdin 承認文が非 TTY、空、UTF-8 でない、複数行、または許可文言外の場合は challenge 作成前に停止する。承認文は直近の利用者発話または利用者による対話入力に限る。利用者の単発 commit 指示を使う場合、その 1 行を staged 内容承認と LLM commit 実行代行承認の source として扱い、LLM が `printf` 等で生成して渡してはならない。LLM が利用者発話なしに承認文を生成してはならない。

`tools/guarded-git-commit.py` は `commit --execution-actor llm` を先に実行し、exit 2 なら commit しない。exit 1 は既定では停止し、人の判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、期限付き承認レコードは消費済みにする。

通常 workflow の `intent.approval` / `feature-partitioning.approval` 完了後の停止点は、`next --json` が `kind: commit_stop_point` として検出する。これらは `stages/in-progress/` を使わない通常 commit であるため、commit guard 側では特別な in-progress 例外を要求せず、通常どおり承認レコード、staged 範囲、post-write-verification、文書 lint を検査する。

通常の nonce challenge 付き commit 手順は、次の順序で逐次実行する。

1. `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行し、`OK` を確認する。
2. `git add ...` で対象を stage する。
3. `.venv/bin/python3 tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"` を TTY で起動し、直近の利用者発話で明示された commit 指示を 1 行として渡す。

低レベル手順として `commit-approval prepare` と `guarded-git-commit.py --approval-nonce` を直接使う場合も、`commit-approval prepare` と `commit --json` precheck を並列化しない。`prepare` 後の challenge は staged exact index と承認状態に束縛されるため、guarded commit 以外の承認系コマンドを挟まない。`--approval-source-text-line-stdin` は TTY からの対話入力だけを受け付ける。直近の利用者発話で明示された commit 指示を承認 1 行として渡し、空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行してはいけない。

<a id="next"></a>

## 3-a. next

`next --json` は通常 workflow の次 action を返す前に、cross-feature phase 終端の未コミット変更を確認する。

判定：

- `intent.approval` が全 feature で `true` であり、`intent` phase の workflow_state または intent 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: intent` を返す
- `feature-partitioning.approval` が全 feature で `true` であり、`feature-partitioning` phase の workflow_state または feature-partitioning 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: feature-partitioning` を返す
- 対象 phase の終端変更が commit 済みで作業ツリーが clean な場合、停止点を返し続けず、次 phase の通常 action へ進む
- post-write-verification、lightweight self-check、reopen/maintenance/resume の in-progress は従来どおり通常 workflow の停止点判定より優先する

<a id="push"></a>

## 4. push

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | push 理由。人による承認の出典を含めることを推奨する |

判定対象：

- 作業ツリーが clean であること
- `origin/main` からのローカル先行コミット数を出力すること
- 直近コミットの題名要約を出力すること
- ローカル先行 commit がある場合、HEAD に対応する commit 事前検査記録があること
- `origin/main` 以外への push が要求されていれば警告すること

作業ツリーが dirty の場合、HEAD の commit 事前検査記録がない場合、または deployable artifact の配置非依存 lint が失敗する場合は逸脱とする。`stages/in-progress/` が存在するだけでは push を遮断しない。in-progress は次 action 判定の状態であり、clean な作業ツリー上の push 済み候補 commit を危険にする直接条件ではない。

<a id="audit-commit"></a>

## 5. audit-commit

`audit-commit <commit-ish>` は、指定 commit の変更ファイルを読み、post-write-verification 対象だけを抽出する。

判定：

- 対象なし：OK
- 対象あり、commit 内ファイル内容 sha256 を覆う completed manifest がある：OK
- 対象あり、manifest がない、sha256 不一致、coverage matrix 不足、または未解決本質的指摘がある：逸脱
- `<commit-ish>` が解決できない：逸脱

この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。

<a id="reopen-advance-step"></a>

## 6. reopen-advance-step

`reopen-advance-step` は、reopen 手続きファイルの第1過程・第2過程を機械的に進める更新コマンドである。第1過程の完了では第2過程の正本修正へ進め、第2過程の完了では停止点コミット状態へ進める。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--from-step` | 必須 | 完了扱いにする過程番号。`1` または `2` |
| `--completed-step` | 必須 | `completed_steps` に追記する完了ステップ |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--from-step` は `1` または `2` のみを許可する
- 対象 YAML の `step_number` は `--from-step` と一致する必要がある。不一致は逸脱とする
- `--completed-step`、`--rationale`、`--evidence` が空の更新は逸脱とする
- `completed_steps` に `--completed-step` を追記する
- `reopen_step_records` に `from_step`、`completed_step`、`rationale`、`evidence` を追記する
- `--from-step 1` の成功時は `step_number: 2`、`next_step: 第2過程：正本修正`、`current_blocker: null` を保存する
- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: null`、`commit_stop_point: true`、`commit_stop_point_step: 2`、`commit_stop_point_kind: canonical_update_complete`、`commit_stop_point_reason: 第2過程の正本修正完了` を保存する
- commit guard は構造化された停止点だけを許可する。第2過程は `canonical_update_complete`、第3過程は `drafting_complete` または review 系 gate 完了（`triad_review_complete` / `review_wave_complete` / `alignment_complete` / `approval_complete`）、第4過程は implementation approval 完了の `approval_complete` を許可する。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-advance-gate"></a>

## 7. reopen-advance-gate

`reopen-advance-gate` は、reopen 手続きファイルの `pending_gates` を 1 件進める更新コマンドである。`spec-set` は in-progress reopen が存在する状態を通常作業として遮断するため、reopen 第3過程の gate 完了更新では本コマンドを使う。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 完了扱いにする gate。`pending_gates` 内と同じ文字列で指定する。標準の gate 文字列は `stages/<phase>.yaml#<stage>` 形式。例：`stages/requirements.yaml#alignment` |
| `--decision` | 必須 | 下流影響判断 |
| `--feature-scope` | 必須 | 判断対象の feature |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |
| `--set-spec` | 任意 | `FEATURE PHASE STAGE VALUE` の 4 値で `spec.json` も同時更新する。指定は 1 回のみ。`VALUE` は `true` または `false` |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate（`triad-review`／`review-wave`／`alignment`／`approval`）として解釈できる必要がある。壊れた gate 文字列や `drafting` gate が 1 件でもあれば逸脱とする
- `--evidence` が 1 件も無い更新は逸脱とする
- 完了した gate を `pending_gates` から除去し、`completed_gates` へ追加する
- `downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を追記する
- `--completed-step` があれば `completed_steps` へ追記する
- `--set-spec` があれば、対象 feature の `spec.json` の該当 workflow_state を同時更新する
- gate 完了後は `current_blocker` を `null` にする。本コマンドは approval gate の承認待ち blocker を新規作成しない
- 残る pending gate があれば `step_number: 3` を維持し、`next_step` を次 gate に更新する。無ければ `step_number: 4` と `next_step: 第4過程：完了` へ進める
- 完了した gate について、`commit_stop_point: true`、`commit_stop_point_step`、`commit_stop_point_kind`、`commit_stop_point_gate`、`commit_stop_point_reason` を保存する。kind は `triad-review` → `triad_review_complete`、`review-wave` → `review_wave_complete`、`alignment` → `alignment_complete`、`approval` → `approval_complete` とする。これにより requirements / design / tasks / implementation の各 review 系 gate 完了後を再開可能な停止点コミットとして扱う。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-set-blocker"></a>

## 8. reopen-set-blocker

`reopen-set-blocker` は、reopen 第3過程で approval gate の承認待ちに到達したとき、`current_blocker` を構造化して設定する更新コマンドである。承認待ちを自由記述で手編集する代わりに、対象 gate、承認主体、理由、根拠を機械可読に保存する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 承認待ちにする gate。`pending_gates` 先頭と同じ `stages/<phase>.yaml#approval` 形式 |
| `--actor` | 必須 | 承認主体。`human` または `proxy_model` |
| `--rationale` | 必須 | 承認待ちにする理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate として解釈できる必要がある
- `--gate` は `approval` gate でなければならない。`alignment` など approval 以外への blocker 設定は逸脱とする
- `--actor` は `human` または `proxy_model` のみを許可する
- `--rationale`、`--evidence` が空の更新は逸脱とする
- 成功時は `current_blocker` に `blocker_type: approval_gate`、`gate`、`actor`、`status: waiting_for_approval`、`rationale`、`evidence` を保存する
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-finalize"></a>

## 9. reopen-finalize

`reopen-finalize` は、reopen 第4過程で `stages/in-progress/` の手続き YAML を `stages/completed/` へ移す更新コマンドである。完了 YAML の必須項目を手編集で埋める代わりに、構造化引数から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases`、`completed_steps` を更新する。対象 feature の `spec.json` が存在する場合は、同じ操作で `recheck.upstream_change_pending=false`、`recheck.impacted_downstream_phases=[]` にクリアし、第4過程完了の `reopen_step_records` も追加する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | `stages/in-progress/` 配下の reopen 手続き YAML |
| `--impacted-downstream-phase` | 必須 | `impacted_downstream_phases` に記録する phase。複数指定可 |
| `--feature-impact` | 必須 | `FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE` の 5 値で feature impact 判定を追加する。既存 feature すべてについて指定する |
| `--new-feature-decision` | 必須 | `DECISION RATIONALE EVIDENCE` の 3 値で new feature 判定を記録する |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- 対象 YAML は `stages/in-progress/` 配下でなければならない
- `step_number` は `4`、`pending_gates` は空、`current_blocker` は `null` でなければならない
- `--feature-impact` は既存 feature すべてを覆う必要がある
- feature impact の `decision`、`impact_basis`、`rationale`、`evidence` は commit 前検査の完了 YAML 検査と同じ条件で検査する
- `--new-feature-decision` は `decision`、`rationale`、`evidence` を必須とする
- `--impacted-downstream-phase` は既知 phase 名だけを許可する
- 成功時は `step_number: 4`、`next_step: 完了`、`pending_gates: []`、`current_blocker: null` を保存し、対象 feature の `spec.json` の recheck をクリアし、第4過程完了の `reopen_step_records` を追加したうえで、同名ファイルを `stages/completed/` へ作成して元の in-progress ファイルを削除する
- completed 側に同名ファイルが既にある場合は上書きせず DEVIATION とする
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="autonomous-plan"></a>
<a id="autonomous-plan-template"></a>
<a id="autonomous-plan-record-integration"></a>
<a id="autonomous-ledger-audit"></a>

## 10. autonomous-plan 系

`autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。

- `mode: autonomous_parallel`
- `run_id`
- `authorization.approved_by`
- レビュー結果サマリと三段階トリアージの提示済み記録
- 各 task の `source_finding_ids`、`allowed_paths`、`expected_tests`、停止条件
- 並列 task 間の `allowed_paths` 衝突がないこと
- `integration_gate` の確認項目
- 作業ノイズを本線 repo に取り込まない出力方針
- 履歴台帳パス、タスク割当記録、判断根拠記録、統合結果記録、保存方針

検査に通った場合も、通らなかった場合も、台帳パスが妥当なら判定履歴を記録する。

`autonomous-plan-template` は最小テンプレートを生成する。`autonomous-plan-record-integration` は統合後に既存の履歴台帳へ `integration_result` を追記する。

## 11. 出力形式

終了コード：

- `0`：問題なし
- `1`：警告あり
- `2`：逸脱検出

人間可読出力は、正常系では判定結果と対象サブコマンドだけの最小出力にする。判定理由や現在状態の詳細は、逸脱・警告・非定型処理・調査が必要な場合だけ表示する。

JSON 出力は、少なくとも次のキーを含む。

```json
{
  "verdict": "OK | WARN | DEVIATION",
  "exit_code": 0,
  "action": {
    "subcommand": "commit",
    "args": {}
  },
  "reasons": [],
  "current_state": {}
}
```

## 12. ログ

判定ログは JSON Lines 形式で記録する。`--json` 出力と同等の構造に `timestamp` を追加する。

既定パス：

- `.reviewcompass/runtime/logs/workflow-precheck.log`（旧 `docs/logs/workflow-precheck.log` からの変更は
  2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。旧ログは凍結、読み取り互換は P3 まで）

`--log-path` でテスト用の隔離パスへ上書きできる。

### 12.1 実行時生成物の凍結期（P3 まで）の扱い

検査ログ・effective prompt（`.reviewcompass/runtime/effective-prompts/`、旧 `.reviewcompass/effective-prompts/`）・
commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.json`、旧 `.reviewcompass/approvals/commit-approval.json`）の
3 パスは、書き込みを常に新配置（runtime 区画、原則 git 無視）へ行い、読み取りは新→旧の順でフォールバックする
（新旧競合時は新配置を正とする）。契約の正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
定数と読み取り解決の実装正本は `tools/check_workflow_action/runtime_paths.py`。

凍結検査の手動実行手順（ゲートへの自動統合は行わず、手動運用とする）：

1. 凍結境界（P1 実装反映コミット＝書き込み先切替のコミット）を特定する。例：

   ```bash
   git log --reverse --format=%H -S "runtime/logs/workflow-precheck" -- tools/check_workflow_action/runtime_paths.py | head -1
   ```

2. 旧 3 パスへの凍結違反（追加・変更・削除）を検出する。例：

   ```bash
   PYTHONPATH=. .venv/bin/python3 -c "
   from tools.check_workflow_action.placement_freeze import check_runtime_placement_freeze
   for v in check_runtime_placement_freeze('.', '<freeze-commit>'):
     print(v)
   "
   ```

   注記：ReviewCompass 自身では旧 3 パスは gitignore 対象（未追跡）のため、git 履歴で不変性を立証できるのは
   旧配置を追跡している構成（対象アプリ等）に限る。未追跡の旧成果物の凍結は書き込み経路のテスト
   （`tests/tools/test_runtime_placement_freeze.py`）で担保する。

## 13. テスト観点

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `reopen-advance-step` の第1・第2過程更新、根拠なし更新拒否、現在 step 不一致拒否
- `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
- `reopen-set-blocker` の構造化 blocker 設定、非先頭 gate 拒否、非 approval gate 拒否、根拠なし更新拒否
- `reopen-finalize` の完了 YAML 生成、in-progress 削除、第4過程未到達と feature impact 不足の拒否
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。


## docs/operations/REOPEN_PROCEDURE.md

# REOPEN_PROCEDURE：再オープン手続きの運用手順

最終更新：2026-06-10（現行の運用手順として更新）

## 0. 位置づけ

本文書は ReviewCompass の再オープン手続き（やり直し）を実行可能な手順にした運用文書である。運用時は本文書を手順の入口とし、形式的な契約は [workflow-management design](../../.reviewcompass/specs/workflow-management/design.md)、[workflow-management tasks](../../.reviewcompass/specs/workflow-management/tasks.md)、および [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md) の reopen 関連記述と整合させる。

本手順は、現在の 5 段ワークフロー（drafting → triad-review → review-wave → alignment → approval）を前提とする。

## 1. いつ使うか

下流の段（triad-review／review-wave／alignment／approval）で、上流フェーズ（過去フェーズ）の修正が必要な「遡及（そきゅう）所見」を発見したとき。同じフェーズの他機能への影響（波及）は機能横断段（review-wave）で扱い、本手続きの対象外。所見の波及種別の判断は [SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md) を参照する。

## 2. 4 過程の実行手順

再オープン手続きは 4 過程で扱う。各過程は「停止せず連続実行できる作業の単位」で、人の承認点または commit 停止点で締める。

### 第1過程：判定とフラグ差し戻し（actor=llm、自律で連続実行）

1. 遡及所見を発見し、下流の作業を停止する
2. 手戻り種別を判定する（N／R／D／A／I × 深さ）
3. 上流変更を既存 feature の責務境界へ写像し、feature impact を判定する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で行う
   - 既存 feature に受け皿がある場合：該当 feature ごとに `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only` のいずれかを判定する
   - 既存 feature に受け皿がない場合：`new_feature_required` として新 feature 候補を作る
   - 判定の主軸は、文書内の挿入箇所ではなく、実装上の所有責務である。変更が実装責務または契約正本を変え得る feature は direct impact として扱い、出力を読むだけ、派生物を作るだけ、手続きを確認するだけの feature は indirect check として扱う
   - 各 feature impact 判定には `impact_basis` を記録する。値は `implementation_ownership`、`contract_ownership`、`consumer_or_derivative_only`、`no_implementation_impact`、`new_feature_boundary` のいずれかとする
   - 判定が重要、曖昧、広範囲の場合は 3 役レビューに送る
4. trigger_map で再実施対象の段を決定する（依存順＝`feature-dependency.yaml#feature_order`。旧称 phase_order）
5. 種別判定と feature impact 判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に記録する。形式は既存の `docs/reviews/reopen-classification-*.md` の記録例に合わせる
6. 進行中状態ファイル `stages/in-progress/reopen-procedure-<日付>.yaml` を発行する
7. spec.json のフラグを差し戻す：
   - 上流：`reopened.<上流>=true`、上流の修正対象段（alignment／approval）を `false` に
   - 下流：`recheck.upstream_change_pending=true`、`impacted_downstream_phases` に下流確認対象を列挙する。下流段を `false` に戻すか、完了扱いのまま影響なし／間接確認のみとするかは feature impact 判定と下流影響判定で決める
   - 上流段を `false` に戻しても、同フェーズ後段または下流フェーズ段を機械的にすべて `false` にする必要はない。ただし完了 commit までに、残した段を含む feature impact 判定と下流影響判定を手続き記録へ明示する
   - 複数段を実際に差し戻す場合は、下流側から上流側へ `false` にすると作業状態を読みやすい。影響なしと判定した段は `true` のまま残してよい
   - `recheck.upstream_change_pending=true` または空でない `impacted_downstream_phases` を含む `spec.json` 変更は、対応する `stages/in-progress/reopen-procedure-*.yaml` と同じ停止点 commit に含める

→ **停止点：フラグ差し戻しの内容（手戻り種別・再実施範囲・差し戻し）を人が承認する**（この時点ではコミットしない）

### 第2過程：正本修正（actor=human または llm）

8. 上流フェーズの正本（仕様文書の該当箇所）を修正する

→ **停止点：コミット**（第1過程のフラグ差し戻しと本過程の正本修正をまとめて 1 コミット）

### 第3過程：連鎖再実施（依存順、各 approval で停止）

9. 依存順に上流 → 下流の各フェーズで：
   - `pending_gates` は review 系 gate（triad-review／review-wave／alignment／approval）の処理順を表す。phase の正本本文を更新する必要があり、先頭 gate が triad-review の場合、triad-review の前に drafting を実施する。drafting 完了後は `drafting_completed_gates` に `stages/<phase>.yaml#drafting` を記録し、その後に triad-review へ進む
   - 正本本文（`.reviewcompass/specs/<feature>/<phase>.md`）を実質修正した phase は、triad-review → review-wave → alignment → approval の順に再実施する。これは requirements／design／tasks／implementation のいずれでも同じ
   - 正本本文を修正していない phase は、trigger_map の pending gate に従って alignment（整合チェック）から再確認してよい
   - 上流変更に対する下流影響判定を `downstream_impact_decisions` に記録する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で必須とする
   - 「既存で受けられる」「修正不要」と判断する場合も、判定対象 gate、feature 範囲、判断、理由、証跡を記録する。修正不要は reopen を省略する理由ではなく、reopen 後の影響判定結果としてのみ扱う
   - 波及あり → triad-review に戻して対処（機能内対処または機能横断段へ）
   - 波及なし → approval へ
   - approval は人の承認（actor=human または proxy_model）

→ **停止点：各フェーズの approval（人の承認）。全フェーズ完了後にコミット**

### 第4過程：完了（連続実行）

10. 整合性の最終確認（上流の変更が下流に正しく伝わったか）
11. `reopen-finalize` で recheck をクリアする（`upstream_change_pending=false`、`impacted_downstream_phases=[]`）、第4過程完了履歴を追加する、進行中状態ファイルを `stages/completed/` へ移動する、の 3 点を一括で行う。`reopened.<上流>` は `true` のまま残す（履歴）。

→ **停止点：コミット**

第4過程の完了 commit では、`stages/completed/reopen-procedure-*.yaml` に `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` と、`pending_gates` の各 gate を覆う `downstream_impact_decisions` が必要である。`feature_impact_decisions` は、既存 feature ごとに `feature`、`decision`、`impact_basis`、`rationale`、`evidence` を持つ。`decision` は `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only`、`new_feature_required` のいずれかとする。`impact_basis` は `implementation_ownership`、`contract_ownership`、`consumer_or_derivative_only`、`no_implementation_impact`、`new_feature_boundary` のいずれかとする。`new_feature_decision.decision` は `no_new_feature` または `new_feature_required` とする。`downstream_impact_decisions` の各判定は最低限、`gate`、`feature_scope`、`decision`、`rationale`、`evidence` を持つ。`decision` は `affected_update_required`、`existing_sufficient`、`no_impact`、`approved`、`proxy_approved` のいずれかとする。`impacted_downstream_phases` に列挙した各フェーズには、対応する `downstream_impact_decisions[].gate` を少なくとも 1 件記録する。完了 commit に正本本文の変更が含まれる phase は、`pending_gates` に triad-review／review-wave／alignment／approval をすべて含め、drafting を実施した phase は `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` を含める。

## 3. 手戻り種別と trigger_map

種別記号は N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ（どこまで上流に戻るか）で表す。trigger_map（全 15 種）は種別から再実施対象段を返す。trigger_map の alignment／approval-only は、該当 phase の正本本文を修正しない再確認に限る。正本本文を修正した phase は、その phase の triad-review／review-wave／alignment／approval を再実施対象に加える。

## 4. 状態遷移の早見表

| 発見した問題 | 修正フェーズ | 主なアクション |
|---|---|---|
| 要件の問題 | requirements | requirements を修正 → 下流（design／tasks／implementation）を reopen 対象に → 依存順に連鎖再実施 |
| 設計の問題 | design | design を修正 → 下流（tasks／implementation）を reopen 対象に → 連鎖再実施 |
| タスクの問題 | tasks | tasks を修正 → 下流（implementation）を reopen 対象に → 連鎖再実施 |
| 意図の問題 | intent | intent を修正 → 全機能の下流（requirements 以降）を reopen 対象に → 連鎖再実施 |

本表は代表例である。実際の再実施対象は、手戻り種別、trigger_map、正本本文を修正した phase、feature impact 判定、下流影響判定を合わせて決める。

## 5. spec.json の更新

`reopened` は 6 フェーズ（intent／feature-partitioning／requirements／design／tasks／implementation）を対象とする。intent と feature-partitioning は機能横断段のため、これらの `reopened` は全機能で同じ値になる。commit 時には [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) の reopen 検査により、recheck 印付き spec.json と reopen 手続き記録の対応、完了時の feature impact 判定、下流影響判定、影響フェーズ網羅が確認される。

## 6. 記録の確実性について

本手続きの各ステップを LLM が忘れず実行する保証はない（ワークフロー記録全般が持つ脆さ）。本手続きでは、第1過程の承認、各 commit、各 approval を停止点として人の確認を挟む。また、`tools/check-workflow-action.py` の `reopen-start`、`spec-set`、`commit`、`next` の各判定で、記録漏れや手順逸脱を検出可能にする。

## 7. 関連参照

- [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md)（reopen-start と commit 前検査の運用契約）
- [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md)（reopen 関連の commit 検査詳細）
- [WORKFLOW_NAVIGATION.md](WORKFLOW_NAVIGATION.md)（`reopen_in_progress`、`reopen_classification_required`、`stage` の読み方）
- [SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md)（所見提示、判断停止、作業完了時報告の運用）
- [workflow-management design](../../.reviewcompass/specs/workflow-management/design.md)（reopen 機械強制モデル、後追い intent の下流再展開モデル）
- [workflow-management tasks](../../.reviewcompass/specs/workflow-management/tasks.md)（T-007、T-008、XDI-WM-002）
- `tools/check-workflow-action.py`（`reopen-start`、`spec-set`、`commit`、`next` の実装）


## .reviewcompass/specs/workflow-management/spec.json

{
  "feature_name": "workflow-management",
  "language": "ja",
  "created_at": "2026-05-24T00:00:00+09:00",
  "updated_at": "2026-06-19T00:00:00+09:00",
  "workflow_state": {
    "intent": {
      "drafting": true,
      "review": true,
      "approval": true,
      "reference": "stages/intent.yaml"
    },
    "feature-partitioning": {
      "candidate-proposal": true,
      "approval": true,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md"
    },
    "requirements": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "design": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "tasks": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "implementation": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    }
  },
  "reopened": {
    "intent": true,
    "feature-partitioning": true,
    "requirements": true,
    "design": true,
    "tasks": true,
    "implementation": true
  },
  "recheck": {
    "upstream_change_pending": false,
    "impacted_downstream_phases": []
  }
}


## stages/completed/reopen-procedure-2026-06-19.yaml

process_id: reopen-procedure
feature: workflow-management
classification: R-0
started_at: '2026-06-19T00:00:00+09:00'
trigger: 統合設計メモ Requirement 13〜16 反映後の workflow state 実体差し戻し
classification_basis: docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
completed_steps:
- R-0 判定確定・spec.json フラグ差し戻し完了（requirements.triad-review/review-wave/alignment/approval
  → false、design/tasks/implementation 全段 → false、recheck.upstream_change_pending →
  true、impacted_downstream_phases → design/tasks/implementation）
- intent/INTENT.md と requirements.md に統合設計メモを反映済み（commit 50c6cbda）
- requirements triad-review gate 完了（新規3者レビュー、proxy_model 判断、C1〜C7反映、post-write verification
  no findings）
- requirements review-wave gate 完了（全 feature impact check、workflow-management 以外 existing_sufficient、post-write
  verification no findings）
- requirements alignment gate 完了（intent / requirements / triad-review / review-wave
  / workflow_state 整合、post-write verification no findings）
- requirements approval gate 完了（利用者発言『承認』に基づく明示承認）
- design drafting 完了（Requirement 13〜16 を design.md へ展開し、operation contract、承認ゲート、side
  track stack、workflow-state snapshot、structured effective prompt、proxy_model triage
  decision 機械処理化、Phase 0〜6 を設計化）
- design triad-review gate 完了（3者レビュー、利用者承認 triage、C2/C3反映、post-write verification
  no findings）
- design review-wave gate 完了（全 feature impact check、workflow-management 以外 existing_sufficient、post-write
  verification no findings）
- design alignment gate 完了（requirements Requirement 13〜16 / design / triad-review
  / review-wave / workflow_state 整合、post-write verification no findings）
- design approval gate 完了（利用者発言『承認』に基づく明示承認）
- tasks drafting 完了（Requirement 13〜16 を T-016〜T-019 として tasks.md へ展開）
- tasks triad-review gate 完了（proxy_model 判断、C1〜C4反映、post-write verification no findings）
- tasks review-wave gate 完了（全 feature impact check、workflow-management 以外 existing_sufficient、post-write
  verification no findings）
- tasks alignment gate 完了（requirements Requirement 13〜16 / design / tasks / triad-review
  / review-wave / workflow_state 整合、post-write verification no findings）
- tasks approval gate 完了（利用者発言『承認』に基づく明示承認）
- implementation drafting 完了（Requirement 13〜16 / T-016〜T-019 を implementation-drafting.md
  へ展開）
- implementation triad-review gate 完了（proxy_model 判断、C1〜C6反映、post-write verification
  no findings）
- implementation review-wave gate 完了（全 feature impact check、workflow-management 以外
  existing_sufficient、post-write verification no findings）
- implementation alignment gate 完了（requirements Requirement 13〜16 / design / tasks
  / implementation drafting / triad-review / review-wave / workflow_state 整合、post-write
  verification no findings）
- implementation approval gate 完了（利用者発言『承認』に基づく明示承認）
- 第4過程 完了（recheck をクリアし、reopen 完了記録を generated completed state として保存）
next_step: 完了
step_number: 4
pending_gates: []
completed_gates:
- stages/requirements.yaml#triad-review
- stages/requirements.yaml#review-wave
- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
- stages/design.yaml#triad-review
- stages/design.yaml#review-wave
- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#triad-review
- stages/tasks.yaml#review-wave
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval
- stages/implementation.yaml#triad-review
- stages/implementation.yaml#review-wave
- stages/implementation.yaml#alignment
- stages/implementation.yaml#approval
drafting_completed_gates:
- stages/requirements.yaml#drafting
- stages/design.yaml#drafting
- stages/tasks.yaml#drafting
- stages/implementation.yaml#drafting
current_blocker: null
side_track_records:
- completed_maintenance: stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml
  rationale: post-write API review の criteria / review-target 生成を機械化する局所改善を、本線 design
    drafting 再開前の maintenance commit として記録した。reopen gate 状態は変更しない。
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-268.yaml
  - .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite/review_summary.md
reopen_step_records:
- from_step: 1
  completed_step: R-0 判定確定・spec.json フラグ差し戻し完了（requirements.triad-review/review-wave/alignment/approval
    → false、design/tasks/implementation 全段 → false、recheck.upstream_change_pending
    → true、impacted_downstream_phases → design/tasks/implementation）
  rationale: 利用者承認済み（2026-06-19 Codex セッション、「承認」発言）。分類根拠：docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
  evidence:
  - docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
  - .reviewcompass/specs/workflow-management/spec.json
- from_step: 2
  completed_step: intent/INTENT.md と requirements.md に統合設計メモを反映済み（commit 50c6cbda）
  rationale: Requirement 13〜16、Change Intent、XDI-WM-005、および intent 追記は commit 50c6cbda
    で反映済み。次は正式 requirements triad-review から再実施する。
  evidence:
  - 50c6cbda
  - intent/INTENT.md
  - .reviewcompass/specs/workflow-management/requirements.md
- from_step: 3
  completed_step: requirements triad-review の proxy_model 判定結果を requirements と関連記録へ反映済み
  rationale: C1/C2 must-fix と C3〜C7 should-fix を requirements.md へ反映し、review-response.md
    に反映内容を記録した。C8/C9 は proxy_model 判定どおり leave-as-is とした。requirements triad-review
    gate 自体は post-write verification 後に完了記録する。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/proxy-decision-summary.md
- from_step: 3
  completed_step: requirements review-wave gate 完了（全 feature impact check、workflow-management
    以外 existing_sufficient）
  rationale: requirements review-wave / impact check を実施し、workflow-management 以外の
    feature は consumer / derivative として現行正本で受けられるため requirements 正本変更不要と判断した。post-write
    verification は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-256.yaml
- from_step: 3
  completed_step: design drafting 完了（Requirement 13〜16 を design.md へ展開）
  rationale: requirements approval 済みの Requirement 13〜16 を workflow-management design.md
    へ展開し、operation contract 語彙、required_action 対応、承認ゲート、side track stack、workflow-state
    snapshot、structured effective prompt、proxy_model triage decision 機械処理化、Phase 0〜6
    の段階的実装順序を設計化した。次は design triad-review gate。
  evidence:
  - .reviewcompass/specs/workflow-management/design.md
  - docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md
- from_step: 3
  completed_step: design triad-review gate 完了
  rationale: design triad-review を実施し、C1 leave-as-is、C2/C3 should-fix のトリアージ案を利用者発言「承認」に基づき確定した。
    C2/C3 は design.md の完成判定基準へ反映済み。post-write verification は gemini-3.5-flash no findings。
    次は design review-wave / impact check。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/raw-review-triage-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-276.yaml
- from_step: 3
  completed_step: design review-wave gate 完了（全 feature impact check、workflow-management
    以外 existing_sufficient）
  rationale: design review-wave / impact check を実施し、workflow-management 以外の feature
    は consumer / derivative として現行正本で受けられるため design 正本変更不要と判断した。post-write verification
    は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-278.yaml
- from_step: 3
  completed_step: design alignment gate 完了
  rationale: design alignment を実施し、requirements Requirement 13〜16、design、triad-review
    対処、review-wave 判定、workflow_state / reopen 記録が整合していると確認した。design 内の追加修正は不要で、tasks
    / implementation への recheck は維持する。post-write verification は gemini-3.5-flash no
    findings。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-279.yaml
- from_step: 3
  completed_step: tasks drafting 完了（Requirement 13〜16 を T-016〜T-019 として tasks.md へ展開）
  rationale: design approval 済みの Requirement 13〜16 を workflow-management tasks.md
    へ展開し、operation contract 語彙、承認ゲート・side track stack・workflow-state snapshot、構造化有効プロンプト、Phase
    0〜6 と proxy_model triage decision 機械処理化を T-016〜T-019 として追加した。要件追跡、テスト戦略、完成判定、変更意図、XDI-WM-005
    も更新済み。 次は tasks triad-review gate。
  evidence:
  - .reviewcompass/specs/workflow-management/tasks.md
- from_step: 3
  completed_step: implementation triad-review gate 完了
  rationale: implementation triad-review を実施し、proxy_model 判断により C1/C2 must-fix、C3〜C6
    should-fix、C7 leave-as-is を確定した。C1〜C6 は implementation-drafting.md と review-response.md
    に反映済みで、post-write verification は gemini-3.5-flash findings 0。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-286.yaml
  - .reviewcompass/specs/workflow-management/implementation-drafting.md
- from_step: 3
  completed_step: implementation review-wave gate 完了（全 feature impact check、workflow-management
    以外 existing_sufficient）
  rationale: implementation review-wave summary が status ok、carry-forward 未消化 0、workflow-management
    以外 existing_sufficient を示し、post-write verification post-write-2026-06-19-287 で
    findings 0 を確認したため、他 feature の implementation 正本変更は不要と判定する。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-287.yaml
- from_step: 3
  completed_step: implementation alignment gate 完了
  rationale: implementation alignment を実施し、requirements Requirement 13〜16、design、tasks、implementation
    drafting、triad-review 対処、review-wave 判定、workflow_state / reopen 記録が整合していると確認した。implementation
    内の追加修正は不要で、approval は未完了として維持する。post-write verification は gemini-3.5-flash findings
    0。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-288.yaml
- from_step: 3
  completed_step: requirements alignment gate 完了
  rationale: requirements alignment で intent、requirements、triad-review 対処、review-wave 判定、workflow_state
    / reopen 記録の整合を確認し、requirements 内の追加修正は不要と判断した。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-258.yaml
- from_step: 3
  completed_step: requirements approval gate 完了
  rationale: 利用者が 2026-06-19 Codex セッションで「承認」と明示し、requirements drafting、triad-review、review-wave、alignment
    が完了済みであるため、requirements phase を承認済みとして扱った。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-approval.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-259.yaml
- from_step: 3
  completed_step: design approval gate 完了
  rationale: 利用者が 2026-06-19 Codex セッションで「承認」と明示し、design drafting、triad-review、review-wave、alignment
    が完了済みであるため、design phase を承認済みとして扱った。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-reopen-alignment.md
- from_step: 3
  completed_step: tasks triad-review gate 完了
  rationale: tasks triad-review を実施し、proxy_model 判断により C1〜C3 must-fix、C4 should-fix、C5
    leave-as-is を確定した。C1〜C4 は tasks.md と review-response.md に反映済みである。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-282.yaml
- from_step: 3
  completed_step: tasks review-wave gate 完了
  rationale: tasks review-wave summary が status ok、carry-forward 未消化 0、workflow-management 以外 clear
    を示し、他 feature の tasks 正本変更は不要と判断した。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-283.yaml
- from_step: 3
  completed_step: tasks alignment gate 完了
  rationale: tasks alignment で requirements、design、tasks、triad-review 対処、review-wave 判定、workflow_state
    / reopen 記録の整合を確認し、tasks 内の追加修正は不要と判断した。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- from_step: 3
  completed_step: tasks approval gate 完了
  rationale: 利用者が 2026-06-19 Codex セッションで「承認」と明示し、tasks drafting、triad-review、review-wave、alignment
    が完了済みであるため、tasks phase を承認済みとして扱った。
  evidence:
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- from_step: 3
  completed_step: implementation drafting 完了
  rationale: Requirement 13〜16 / T-016〜T-019 を implementation-drafting.md へ展開した。
  evidence:
  - .reviewcompass/specs/workflow-management/implementation-drafting.md
- from_step: 3
  completed_step: implementation approval gate 完了
  rationale: 利用者が 2026-06-19 Codex セッションで「承認」と明示し、implementation drafting、triad-review、review-wave、alignment
    が完了済みであるため、implementation phase を承認済みとして扱った。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-reopen-alignment.md
- from_step: 4
  completed_step: 第4過程 完了（recheck をクリアし、reopen 完了記録を generated completed state として保存）
  rationale: 全 pending gate が完了し、workflow-management spec.json の recheck をクリアしたうえで、in-progress
    reopen 記録を completed state として保存した。
  evidence:
  - .reviewcompass/specs/workflow-management/spec.json
  - stages/completed/reopen-procedure-2026-06-19.yaml
downstream_impact_decisions:
- gate: stages/requirements.yaml#triad-review
  feature_scope: workflow-management
  decision: proxy_approved
  rationale: 新規3者レビューを実施し、proxy_model 判断により C1/C2 must-fix、C3-C7 should-fix、C8/C9
    leave-as-is を確定した。C1-C7 は requirements.md と review-response.md に反映済みで、post-write
    verification は gemini-3.5-flash no findings。利用者の『次へ』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-254.yaml
  - .reviewcompass/specs/workflow-management/requirements.md
- gate: stages/requirements.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: requirements review-wave / impact check を実施し、workflow-management 以外の
    feature は consumer / derivative として現行正本で受けられるため requirements 正本変更不要と判断した。post-write
    verification は gemini-3.5-flash no findings。利用者の『進めて』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-256.yaml
- gate: stages/requirements.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: requirements alignment を実施し、intent、requirements、triad-review 対処、review-wave
    判定、workflow_state / reopen 記録が整合していると確認した。requirements 内の追加修正は不要で、design/tasks/implementation
    への recheck は維持する。post-write verification は gemini-3.5-flash no findings。利用者の『次へ』指示に基づき
    gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-258.yaml
- gate: stages/requirements.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が 2026-06-19 Codex セッションで『承認』と明示し、requirements drafting、triad-review、review-wave、alignment
    が完了済みであるため、統合設計メモ反映の requirements phase を承認済みとして扱う。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-259.yaml
- gate: stages/design.yaml#triad-review
  feature_scope: workflow-management
  decision: approved
  rationale: design triad-review を実施し、利用者承認に基づき C1 は leave-as-is、C2/C3 は should-fix
    とした。C2/C3 は design.md へ反映済みで、post-write verification は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/raw-review-triage-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-276.yaml
- gate: stages/design.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: design review-wave / impact check を実施し、workflow-management 以外の feature
    は consumer / derivative として現行正本で受けられるため design 正本変更不要と判断した。post-write verification
    は gemini-3.5-flash no findings。利用者の『次へ』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-278.yaml
- gate: stages/design.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: design alignment を実施し、requirements Requirement 13〜16、design、triad-review
    対処、review-wave 判定、workflow_state / reopen 記録が整合していると確認した。design 内の追加修正は不要で、tasks
    / implementation への recheck は維持する。post-write verification は gemini-3.5-flash no
    findings。利用者の『次へ』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-279.yaml
- gate: stages/design.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が 2026-06-19 Codex セッションで『承認』と明示し、design drafting、triad-review、review-wave、alignment
    が完了済みであるため、統合設計メモ反映の design phase を承認済みとして扱う。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-279.yaml
- gate: stages/tasks.yaml#triad-review
  feature_scope: workflow-management
  decision: proxy_approved
  rationale: tasks triad-review を実施し、proxy_model 判断により C1〜C3 must-fix、C4 should-fix、C5
    leave-as-is を確定した。C1〜C4 は tasks.md と review-response.md に反映済みで、post-write verification
    は gemini-3.5-flash findings 0。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-282.yaml
  - .reviewcompass/specs/workflow-management/tasks.md
- gate: stages/tasks.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: tasks review-wave summary が status ok、carry-forward 未消化 0、workflow-management
    以外 clear を示し、post-write verification post-write-2026-06-19-283 で findings 0 を確認したため、他
    feature の tasks 正本変更は不要と判定する。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-283.yaml
- gate: stages/tasks.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: tasks alignment を実施し、requirements Requirement 13〜16、design、tasks T-016〜T-019、triad-review
    対処、review-wave 判定、workflow_state / reopen 記録が整合していると確認した。tasks 内の追加修正は不要で、implementation
    への recheck は維持する。post-write verification は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- gate: stages/tasks.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が 2026-06-19 Codex セッションで『承認』と明示し、tasks drafting、triad-review、review-wave、alignment
    が完了済みであるため、統合設計メモ反映の tasks phase を承認済みとして扱う。
  evidence:
  - .reviewcompass/specs/workflow-management/tasks.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- gate: stages/implementation.yaml#triad-review
  feature_scope: workflow-management
  decision: proxy_approved
  rationale: implementation triad-review を実施し、proxy_model 判断により C1/C2 must-fix、C3〜C6
    should-fix、C7 leave-as-is を確定した。C1〜C6 は implementation-drafting.md と review-response.md
    に反映済みで、post-write verification は gemini-3.5-flash findings 0。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-286.yaml
  - .reviewcompass/specs/workflow-management/implementation-drafting.md
- gate: stages/implementation.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: implementation review-wave summary が status ok、carry-forward 未消化 0、workflow-management
    以外 existing_sufficient を示し、post-write verification post-write-2026-06-19-287 で
    findings 0 を確認したため、他 feature の implementation 正本変更は不要と判定する。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-287.yaml
- gate: stages/implementation.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: implementation alignment を実施し、requirements Requirement 13〜16、design、tasks、implementation
    drafting、triad-review 対処、review-wave 判定、workflow_state / reopen 記録が整合していると確認した。implementation
    内の追加修正は不要で、approval は未完了として維持する。post-write verification は gemini-3.5-flash findings
    0。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-288.yaml
- gate: stages/implementation.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が 2026-06-19 Codex セッションで『承認』と明示し、implementation drafting、triad-review、review-wave、alignment
    が完了済みであるため、統合設計メモ反映の implementation phase を承認済みとして扱う。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-288.yaml
commit_stop_point_records:
- step: 3
  kind: approval_complete
  gate: stages/design.yaml#approval
  reason: design approval 完了時点の停止点
  head: 75411eb282475636719c2f79a4f372922ef57ba3
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-281.yaml
- step: 3
  kind: triad_review_complete
  gate: stages/tasks.yaml#triad-review
  reason: tasks triad-review 完了時点の停止点
  head: 0178dbdcd50688ed2a91439899967aa73d5b4da8
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-282.yaml
- step: 3
  kind: review_wave_complete
  gate: stages/tasks.yaml#review-wave
  reason: tasks review-wave 完了時点の停止点
  head: 3827cf61b739617dca4825dd84b0b18f17358147
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-283.yaml
- step: 3
  kind: alignment_complete
  gate: stages/tasks.yaml#alignment
  reason: tasks alignment 完了時点の停止点
  head: a6bf8f44
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- step: 3
  kind: approval_complete
  gate: stages/tasks.yaml#approval
  reason: tasks approval 完了時点の停止点
  head: 6e364b86
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-284.yaml
- step: 4
  kind: approval_complete
  gate: stages/implementation.yaml#approval
  reason: implementation approval 完了時点の停止点
  head: 363b3decdc6a803824979488a64605e555b9bdaa
  evidence:
  - 363b3decdc6a803824979488a64605e555b9bdaa
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-approval.md
commit_required: true
commit_required_kind: stop_point_consumed
commit_required_reason: reopen commit stop point 消費完了時点の停止点
impacted_downstream_phases:
- requirements
- design
- tasks
- implementation
feature_impact_decisions:
- feature: foundation
  decision: no_reopen_existing_feature
  impact_basis: no_implementation_impact
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
- feature: runtime
  decision: no_reopen_existing_feature
  impact_basis: consumer_or_derivative_only
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
- feature: evaluation
  decision: no_reopen_existing_feature
  impact_basis: consumer_or_derivative_only
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
- feature: analysis
  decision: no_reopen_existing_feature
  impact_basis: consumer_or_derivative_only
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
- feature: workflow-management
  decision: reopen_existing_feature
  impact_basis: implementation_ownership
  rationale: 統合設計メモ Requirement 13〜16 を workflow-management の requirements/design/tasks/implementation
    に反映済み
  evidence:
  - .reviewcompass/specs/workflow-management/implementation-drafting.md
- feature: self-improvement
  decision: no_reopen_existing_feature
  impact_basis: consumer_or_derivative_only
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
- feature: conformance-evaluation
  decision: no_reopen_existing_feature
  impact_basis: consumer_or_derivative_only
  rationale: review-wave で workflow-management 以外は既存仕様で受けられると確認済み
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
new_feature_decision:
  decision: no_new_feature
  rationale: 既存 feature workflow-management の手戻りとして完結し、新規 feature は不要
  evidence:
  - docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md

