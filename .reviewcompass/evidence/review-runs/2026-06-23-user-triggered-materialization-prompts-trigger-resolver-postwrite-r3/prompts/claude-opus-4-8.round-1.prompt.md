prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-opus-4-8

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# PTC-4 Trigger Resolver Post-Write Verification Criteria

phase: post_write_verification

## Review Task

Review whether the latest PTC-4 follow-up changes address the accepted behavior-path finding from the prior 3-way review:

Short user continuation requests such as `次へ`, `進める`, and `継続` must mechanically resolve to the plan-to-TODO bridge operation when there is an unmaterialized plan slice.

This review is limited to the PTC-4 trigger resolver / operation prompt selection fix. Do not review unrelated `docs/notes` lightweight self-check policy test failures.

## Source Finding Being Addressed

Prior review run:

`.reviewcompass/evidence/review-runs/2026-06-23-user-triggered-materialization-prompts-postwrite-rerun/`

Same-root accepted finding:

- There was no mechanical trigger resolver mapping short continuation requests (`次へ`, `進める`, `継続`) to `user_initiated_plan_to_todo_bridge`.
- Routing was operator-mediated and only documented inside the effective prompt.
- Regression tests mainly checked prompt text rather than operation prompt selection behavior.
- `DEFAULT_DISCIPLINE_MAP` fallback did not include the new materialization plan source ref.

## Changed Target Files

Review these target files as model-readable materials:

- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`
- `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md`
- `.reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md`
- `tests/tools/test_effective_prompt_contract.py`
- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
- `.reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml`
- `.reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml`

## Required Checks

### Check 1: Mechanical Trigger Resolver Exists

Verify that `operation-prompt --trigger-text <text>` can resolve short continuation requests to an operation without the caller manually passing `user_initiated_plan_to_todo_bridge`.

Report a finding if the new behavior is still operator-mediated.

### Check 2: Correct Routing Condition

Verify that `次へ`, `進める`, and `継続` route to `user_initiated_plan_to_todo_bridge` only when an unmaterialized plan slice is found.

Report a finding if routing ignores materialization state, silently proceeds without a plan, or chooses a direct implementation operation.

### Check 3: Auditable Output

Verify that the JSON output includes enough `trigger_resolution` evidence to explain why the operation was selected, including trigger kind, reason, and candidate plan IDs.

Report a finding if the output is not auditable.

### Check 4: Regression Tests

Verify that tests execute the operation prompt command path and assert the resolved operation, not only prompt text snippets.

Report a finding if tests remain text-only for the core trigger routing claim.

### Check 5: Fallback Discipline Map

Verify that `DEFAULT_DISCIPLINE_MAP` fallback includes the materialization plan source refs for both `user_initiated_plan_to_todo_bridge` and `user_initiated_backlog_todo_execution`.

Report a finding if the fallback can still silently omit the new source materials when the YAML map is unavailable.

### Check 6: Scope Control

Do not treat unrelated broad test failures around `docs/notes` lightweight self-check vs strict post-write verification as part of this fix unless the trigger resolver change directly caused them.

## Finding Policy

Return findings for any unresolved part of the accepted routing / fallback / test coverage cluster.

If the accepted finding is fixed, return no findings.

Strict output contract:

- Output YAML only.
- The top-level YAML must include `findings`.
- If there are no findings, output exactly:

```yaml
findings: []
```

- Do not append free-form rationale outside YAML.
- If rationale is needed for a finding, put it inside that finding's `rationale` field.

Use severity:

- ERROR: short continuation requests can still bypass the bridge mechanically.
- WARN: routing exists but is weakly scoped, weakly tested, or poorly auditable.
- INFO: clarity or maintainability improvements.

## Out of Scope

- Do not review the unrelated `docs/notes` lightweight self-check policy mismatch.
- Do not approve commit or push.
- Do not require triage decisions or approval records as part of this review.


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
tools/check-workflow-action.py
tests/tools/test_check_workflow_action.py
.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml
.reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md
.reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md
tests/tools/test_effective_prompt_contract.py
.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
.reviewcompass/guidance/discipline_llm_as_judge_prompting.md
.reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml
.reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml

# Target document
## tools/check-workflow-action.py

#!/usr/bin/env python3
"""ワークフロー事前検査スクリプト（補助層 C 段階 2）

仕様：.reviewcompass/guidance/WORKFLOW_PRECHECK.md
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
from check_workflow_action import (
  approval_gate,
  commit_approval,
  commit_unit,
  task_quality_check,
  work_backlog,
  work_checklist,
  work_unit_stack,
)
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
DEFAULT_WORKFLOW_STATE_REPAIR_PATH = ".reviewcompass/runtime/repairs/workflow-state-repair.json"
WORKFLOW_STATE_REPAIR_TTL_SECONDS = 3600
DEFAULT_DISCIPLINE_MAP_PATH = ".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml"
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
  ".reviewcompass/guidance/",
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
  ".reviewcompass/guidance/",
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)

LIGHTWEIGHT_SELF_CHECK_DIR_PREFIXES = (
  "docs/notes/",
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
    ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
  ],
  "decision_points": {
    "next_action_kind": [
      {
        "id": "post_write_policy_violation",
        "prompt_source_refs": [
          ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation",
          ".reviewcompass/guidance/discipline_post_write_verification.md",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
        "canonical_effective_prompt_path": (
          ".reviewcompass/guidance/effective-prompts/"
          "next-action-post-write-policy-violation.prompt.md"
        ),
      },
    ],
    "operation_prompt": [
      {
        "id": "commit",
        "prompt_source_refs": [
          ".reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
      },
      {
        "id": "user_initiated_plan_to_todo_bridge",
        "prompt_source_refs": [
          ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
          ".reviewcompass/backlog/todos/todo-2026-06-23-plan-to-todo-checklist-evidence.yaml",
          ".reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml",
          ".reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
        "canonical_effective_prompt_path": (
          ".reviewcompass/guidance/effective-prompts/"
          "user-initiated-plan-to-todo-bridge.prompt.md"
        ),
      },
      {
        "id": "user_initiated_backlog_todo_execution",
        "prompt_source_refs": [
          ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
          ".reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml",
          ".reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
        "canonical_effective_prompt_path": (
          ".reviewcompass/guidance/effective-prompts/"
          "user-initiated-backlog-todo-execution.prompt.md"
        ),
      },
      {
        "id": "user_initiated_task_quality_gate",
        "prompt_source_refs": [
          ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
          ".reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
        "canonical_effective_prompt_path": (
          ".reviewcompass/guidance/effective-prompts/"
          "user-initiated-task-quality-gate.prompt.md"
        ),
      },
      {
        "id": "user_initiated_task_quality_review_materials",
        "prompt_source_refs": [
          ".reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md",
          ".reviewcompass/guidance/discipline_llm_as_judge_prompting.md",
          ".reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml",
        ],
        "effective_prompt_policy": "one_effective_prompt_per_decision_point",
        "canonical_effective_prompt_path": (
          ".reviewcompass/guidance/effective-prompts/"
          "user-initiated-task-quality-review-materials.prompt.md"
        ),
      },
    ],
  },
  "by_kind": {
    "stage": [
      ".reviewcompass/guidance/discipline_workflow_state_truth_source.md",
    ],
    "cross_feature_stage": [
      ".reviewcompass/guidance/discipline_workflow_state_truth_source.md",
    ],
    "commit_stop_point": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_stop_point",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
    "post_write_verification": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification",
      ".reviewcompass/guidance/discipline_post_write_verification.md",
    ],
    "post_write_policy_violation": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation",
      ".reviewcompass/guidance/discipline_post_write_verification.md",
    ],
    "post_write_human_decision_required": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required",
      ".reviewcompass/guidance/discipline_post_write_verification.md",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
    "reopen_in_progress": [
      ".reviewcompass/guidance/REOPEN_PROCEDURE.md",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
    "maintenance_in_progress": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#maintenance_in_progress",
    ],
    "resume_in_progress": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#resume_in_progress",
    ],
    "parent_resume_pending": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending",
    ],
    "blocking_unit_required": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending",
      ".reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md",
    ],
    "commit_unit_stale": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_stop_point",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
    "commit_mixing_risk": [
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_stop_point",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
  },
  "by_stage": {
    "drafting": [
      ".reviewcompass/guidance/REOPEN_PROCEDURE.md",
      ".reviewcompass/guidance/discipline_workflow_state_truth_source.md",
    ],
    "triad-review": [
      ".reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
      ".reviewcompass/guidance/discipline_approval_operation.md",
    ],
    "review-wave": [],
    "alignment": [
      ".reviewcompass/guidance/discipline_workflow_state_truth_source.md",
    ],
    "approval": [
      ".reviewcompass/guidance/discipline_approval_operation.md",
      ".reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set",
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

OPERATION_PROMPT_IDS = [
  "commit",
  "user_initiated_plan_to_todo_bridge",
  "user_initiated_backlog_todo_execution",
  "user_initiated_task_quality_gate",
  "user_initiated_task_quality_review_materials",
]


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
  canonical_paths = []

  for ref in _decision_point_refs_for_next_action(next_action):
    entry = _find_decision_point(catalog, ref["group"], ref["id"])
    if entry is None:
      continue
    refs.append(ref)
    source_refs.extend(entry.get("prompt_source_refs") or [])
    policy = entry.get("effective_prompt_policy")
    if isinstance(policy, str) and policy:
      policies.append(policy)
    canonical_path = entry.get("canonical_effective_prompt_path")
    if isinstance(canonical_path, str) and canonical_path:
      canonical_paths.append(canonical_path)

  if not refs:
    return None

  result = {
    "effective_prompt_policy": (
      policies[0] if policies else "one_effective_prompt_per_decision_point"
    ),
    "decision_point_refs": refs,
    "prompt_source_refs": _dedupe_strings(source_refs),
  }
  if canonical_paths:
    result["canonical_effective_prompt_path"] = canonical_paths[0]
  return result


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
  canonical_path = effective_prompt.get("canonical_effective_prompt_path")
  if isinstance(canonical_path, str) and canonical_path:
    return canonical_path
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


def _resolve_effective_prompt_artifact_path(cwd, relative_path):
  """canonical effective prompt artifact を cwd または ReviewCompass root から解決する"""
  path = Path(relative_path)
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
  canonical_path = effective_prompt.get("canonical_effective_prompt_path")
  if isinstance(canonical_path, str) and canonical_path:
    prompt_path = _resolve_effective_prompt_artifact_path(cwd, canonical_path)
    prompt_text = ""
    loaded = False
    if prompt_path is not None:
      try:
        prompt_text = prompt_path.read_text(encoding="utf-8")
        loaded = True
      except OSError:
        loaded = False
    augmented = dict(effective_prompt)
    augmented["effective_prompt_path"] = canonical_path
    augmented["effective_prompt_sha256"] = _sha256_text(prompt_text)
    augmented["effective_prompt_loaded"] = loaded
    return augmented

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
  result = {
    "effective_prompt_policy": (
      policy if isinstance(policy, str) and policy
      else "one_effective_prompt_per_decision_point"
    ),
    "decision_point_refs": [{"group": group, "id": point_id}],
    "prompt_source_refs": _dedupe_strings(entry.get("prompt_source_refs") or []),
  }
  canonical_path = entry.get("canonical_effective_prompt_path")
  if isinstance(canonical_path, str) and canonical_path:
    result["canonical_effective_prompt_path"] = canonical_path
  return result


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


def _stable_json_digest(data):
  """安定 JSON 表現の sha256 digest を返す"""
  payload = json.dumps(
    data,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
  ).encode("utf-8")
  return hashlib.sha256(payload).hexdigest()


def _workflow_state_repair_path(cwd):
  return Path(cwd) / DEFAULT_WORKFLOW_STATE_REPAIR_PATH


def _iso_utc_now():
  return datetime.now(timezone.utc)


def _isoformat_utc(value):
  return value.astimezone(timezone.utc).isoformat()


def _parse_iso_datetime(value):
  if not isinstance(value, str) or not value:
    return None
  try:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return None
  if parsed.tzinfo is None:
    return None
  return parsed.astimezone(timezone.utc)


def worktree_file_content_hash(cwd, filepath):
  """worktree 内容の hash を返す。削除済み path は DELETED sentinel にする"""
  path = Path(cwd) / filepath
  if not path.exists():
    return "DELETED"
  if not path.is_file():
    return "NON_FILE"
  return hashlib.sha256(path.read_bytes()).hexdigest()


def workflow_repair_target(cwd, paths, mode):
  """repair record が束縛する対象ファイル集合を canonical 化する"""
  entries = []
  for path in sorted(paths):
    if mode == "staged":
      content_hash = staged_file_content_hash(cwd, path)
    else:
      content_hash = worktree_file_content_hash(cwd, path)
    entries.append({
      "path": path,
      "sha256": content_hash,
    })
  target = {
    "algorithm": "workflow-state-repair-v1",
    "entries": entries,
  }
  return {
    "algorithm": "workflow-state-repair-v1",
    "digest": _stable_json_digest(target),
    "target": target,
  }


def load_workflow_state_repair_record(cwd):
  """workflow state repair record を読む"""
  path = _workflow_state_repair_path(cwd)
  state = {
    "path": DEFAULT_WORKFLOW_STATE_REPAIR_PATH,
    "exists": path.exists(),
    "valid": False,
  }
  if not path.exists():
    return state, ["workflow state repair record がありません"]
  try:
    record = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return state, [f"workflow state repair record を読めません: {e}"]
  if not isinstance(record, dict):
    return state, ["workflow state repair record が object ではありません"]
  state.update({
    "repair_id": record.get("repair_id"),
    "repair_kind": record.get("repair_kind"),
    "reason": record.get("reason"),
    "source_ref": record.get("source_ref"),
    "target_files": record.get("target_files") or [],
    "target_digest": record.get("target_digest"),
    "expires_at": record.get("expires_at"),
    "consumed": record.get("consumed"),
  })
  return state, []


def validate_workflow_state_repair_record(cwd, paths, mode):
  """repair record が現在の changed/staged 内容に一致するか検査する"""
  paths = [
    path
    for path in paths
    if path != DEFAULT_WORKFLOW_STATE_REPAIR_PATH
  ]
  state, errors = load_workflow_state_repair_record(cwd)
  if not state.get("exists"):
    return state, errors
  record_path = Path(cwd) / DEFAULT_WORKFLOW_STATE_REPAIR_PATH
  try:
    record = json.loads(record_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return state, errors

  if record.get("schema_version") != "workflow-state-repair-v1":
    errors.append("workflow state repair record の schema_version が不正です")
  if record.get("repair_kind") != "manual_post_write_policy_exception":
    errors.append("workflow state repair record の repair_kind が不正です")
  if record.get("approved_by") != "user":
    errors.append("workflow state repair record の approved_by が user ではありません")
  if record.get("consumed") is True:
    errors.append("workflow state repair record は消費済みです")
  expires_at = _parse_iso_datetime(record.get("expires_at"))
  if expires_at is None:
    errors.append("workflow state repair record の expires_at が不正です")
  elif expires_at < _iso_utc_now():
    errors.append("workflow state repair record は期限切れです")

  current = workflow_repair_target(cwd, paths, mode)
  recorded_digest = record.get("target_digest")
  if not isinstance(recorded_digest, dict):
    errors.append("workflow state repair record の target_digest が object ではありません")
  elif recorded_digest.get("digest") != current["digest"]:
    errors.append("workflow state repair record が現在の変更内容と一致しません")

  target_files = record.get("target_files")
  if target_files != [entry["path"] for entry in current["target"]["entries"]]:
    errors.append("workflow state repair record の target_files が現在の変更集合と一致しません")

  state["current_digest"] = {
    "algorithm": current["algorithm"],
    "digest": current["digest"],
  }
  state["valid"] = not errors
  return state, errors


def validate_commit_unit_record(cwd):
  """commit unit record があれば現在の staged 内容と照合する"""
  path = Path(cwd) / commit_unit.DEFAULT_COMMIT_UNIT_PATH
  if not path.exists():
    state = {
      "exists": False,
      "verdict": "not_configured",
      "path": commit_unit.DEFAULT_COMMIT_UNIT_PATH,
    }
    active_state = work_unit_stack.current(cwd)
    active_unit = active_state.get("current")
    active_work_unit_id = (
      active_unit.get("unit_id") if isinstance(active_unit, dict) else None
    )
    try:
      staged_files = commit_unit._git_cached_files(cwd)
    except RuntimeError:
      staged_files = []
    state["current_state"] = {
      "active_work_unit_id": active_work_unit_id,
      "record_work_unit_id": None,
      "staged_files": staged_files,
    }
    if (
      isinstance(active_unit, dict)
      and active_unit.get("kind") == "blocking"
      and staged_files
    ):
      state["verdict"] = "DEVIATION"
      state["codes"] = ["PARENT_COMMIT_DURING_BLOCKING_UNIT"]
      state["reasons"] = [
        "active blocking unit 中に commit unit なしで staged commit しようとしています: "
        f"active={active_work_unit_id}"
      ]
      return state, [
        "blocking unit 中の親作業 commit は、commit unit で active unit に束縛してください"
      ]
    return state, []
  state = commit_unit.check(cwd)
  state["exists"] = True
  state["path"] = commit_unit.DEFAULT_COMMIT_UNIT_PATH
  active_state = work_unit_stack.current(cwd)
  active_unit = active_state.get("current")
  record = state.get("record") if isinstance(state.get("record"), dict) else {}
  record_work_unit_id = record.get("work_unit_id")
  active_work_unit_id = (
    active_unit.get("unit_id") if isinstance(active_unit, dict) else None
  )
  state.setdefault("current_state", {})
  state["current_state"]["active_work_unit_id"] = active_work_unit_id
  state["current_state"]["record_work_unit_id"] = record_work_unit_id
  if (
    active_work_unit_id
    and record_work_unit_id
    and active_work_unit_id != record_work_unit_id
  ):
    codes = state.setdefault("codes", [])
    reasons = state.setdefault("reasons", [])
    if "WORK_UNIT_COMMIT_UNIT_MISMATCH" not in codes:
      codes.append("WORK_UNIT_COMMIT_UNIT_MISMATCH")
    reasons.append(
      "active work unit と commit unit の work_unit_id が一致しません: "
      f"active={active_work_unit_id}, commit_unit={record_work_unit_id}"
    )
    state["verdict"] = "DEVIATION"
  if state.get("verdict") == "DEVIATION":
    codes = ", ".join(state.get("codes") or [])
    return state, [f"commit unit が現在の staged 内容と一致しません: {codes}"]
  return state, []


def cmd_repair_workflow_state(args):
  """workflow state repair record を作成する"""
  cwd = Path.cwd()
  if args.repair_workflow_state_command != "prepare":
    return 2
  changed_files = list_changed_files(cwd)
  repair_targets = post_write_verification_targets_for_paths(cwd, changed_files)
  if not changed_files:
    payload = {
      "status": "error",
      "error": "repair 対象の未コミット変更がありません",
    }
    if args.json:
      print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
      print(payload["error"], file=sys.stderr)
    return 2
  if not repair_targets:
    payload = {
      "status": "error",
      "error": "post-write-verification 対象を含まないため repair record を作成しません",
    }
    if args.json:
      print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
      print(payload["error"], file=sys.stderr)
    return 2

  now = _iso_utc_now()
  canonical = workflow_repair_target(cwd, changed_files, "changed")
  record = {
    "schema_version": "workflow-state-repair-v1",
    "repair_id": f"repair-{now.strftime('%Y%m%dT%H%M%SZ')}",
    "repair_kind": "manual_post_write_policy_exception",
    "approved_by": "user",
    "created_at": _isoformat_utc(now),
    "expires_at": _isoformat_utc(now + timedelta(seconds=WORKFLOW_STATE_REPAIR_TTL_SECONDS)),
    "ttl_seconds": WORKFLOW_STATE_REPAIR_TTL_SECONDS,
    "reason": args.reason,
    "source_ref": args.source_ref,
    "target_files": [
      entry["path"]
      for entry in canonical["target"]["entries"]
    ],
    "target_digest": {
      "algorithm": canonical["algorithm"],
      "digest": canonical["digest"],
    },
    "target": canonical["target"],
    "consumed": False,
  }
  path = _workflow_state_repair_path(cwd)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  payload = {
    "status": "prepared",
    "path": DEFAULT_WORKFLOW_STATE_REPAIR_PATH,
    "repair_id": record["repair_id"],
    "target_files": record["target_files"],
    "target_digest": record["target_digest"],
  }
  if args.json:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
  else:
    print("prepared")
  return 0


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
    deleted_files = set(list_commit_deleted_files(cwd, commitish))
  except ValueError as e:
    return {
      "commit": commitish,
      "target_files": [],
      "findings": [],
    }, [f"配置非依存 lint 対象 commit を読めません: {e}"]

  target_files = [
    filepath for filepath in changed_files
    if (
      is_deployment_independence_guard_target(filepath)
      and filepath not in deleted_files
    )
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
  repair_state, repair_errors = validate_workflow_state_repair_record(
    cwd,
    staged_files,
    "staged",
  )
  commit_unit_state, commit_unit_errors = validate_commit_unit_record(cwd)
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    staged_files,
    actual_hashes=staged_content_hashes,
  )
  if post_write_errors and repair_state.get("valid") is True:
    post_write_state["manifest_status"] = "repair_exception"
    post_write_state["repair_record"] = repair_state.get("path")
    post_write_errors = []
  elif post_write_errors and repair_state.get("exists"):
    post_write_errors.extend(repair_errors)
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
  if commit_unit_errors:
    deviation_reasons.extend(commit_unit_errors)
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
    "repair_workflow_state": repair_state,
    "commit_unit": commit_unit_state,
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
      action = {
        "kind": "post_write_verification",
        "required_action": "run_post_write_verification",
        "target_files": verification_targets,
        "manifest_status": manifest_state,
        "manifest": manifest.get("_path") if isinstance(manifest, dict) else None,
        "reason": "post-write-verification 対象の未完了変更があります",
      }
      if isinstance(manifest, dict) and manifest.get("codes"):
        action["codes"] = manifest.get("codes")
      return action

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
  repair_state, repair_errors = validate_workflow_state_repair_record(
    cwd,
    changed_files,
    "changed",
  )
  commit_unit_state, commit_unit_errors = validate_commit_unit_record(cwd)
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
    if repair_state.get("valid") is True:
      next_required_action = "prepare_repair_commit"
    else:
      verdict = "DEVIATION"
      allowed_to_stage = False
      allowed_to_prepare_approval = False
      allowed_to_delegate_execution = False
      reasons.append("commit より前に post-write verification を完了してください")
      if repair_state.get("exists"):
        reasons.extend(repair_errors)

  if commit_unit_errors:
    verdict = "DEVIATION"
    allowed_to_stage = False
    allowed_to_prepare_approval = False
    allowed_to_delegate_execution = False
    reasons.extend(commit_unit_errors)

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
    "repair_workflow_state": repair_state,
    "commit_unit": commit_unit_state,
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


def list_commit_deleted_files(cwd, commitish):
  """指定 commit で削除されたファイル一覧を返す"""
  result = subprocess.run(
    ["git", "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", commitish],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise ValueError(result.stderr.strip() or f"commit を読めません: {commitish}")
  deleted = []
  for line in result.stdout.splitlines():
    parts = line.split("\t", 1)
    if len(parts) == 2 and parts[0] == "D" and parts[1]:
      deleted.append(parts[1])
  return sorted(set(deleted))


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
  if path.startswith(("docs/disciplines/", ".reviewcompass/guidance/")):
    non_discipline_targets = [
      target
      for target in verification_targets
      if not target.startswith(("docs/disciplines/", ".reviewcompass/guidance/"))
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


def post_write_unit_binding_matches_current_commit_unit(cwd, manifest):
  """manifest の unit_binding が現在の commit unit と一致するかを返す。

  unit_binding がない旧 manifest、または現在の commit unit がない通常状態は
  互換のため対象外として True を返す。
  """
  binding = manifest.get("unit_binding")
  if binding is None:
    return True
  if not isinstance(binding, dict):
    return False

  current_unit, errors = commit_unit.load(cwd)
  if errors:
    return True
  if not isinstance(current_unit, dict):
    return True

  expected = {
    "work_unit_id": current_unit.get("work_unit_id"),
    "commit_unit_id": current_unit.get("commit_unit_id"),
    "staged_digest": current_unit.get("staged_digest"),
  }
  return binding == expected


def mark_manifest_code(manifest, code):
  """manifest に機械判定用 code を重複なく付与する。"""
  if not isinstance(manifest, dict):
    return manifest
  codes = manifest.setdefault("codes", [])
  if not isinstance(codes, list):
    manifest["codes"] = [code]
    return manifest
  if code not in codes:
    codes.append(code)
  return manifest


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
    if not (
      manifest.get("status") == "completed"
      and coverage_ok
      and review_run_traceability_satisfied(cwd, manifest)
      and unresolved_substantive_count(manifest) == 0
    ):
      continue
    if not post_write_unit_binding_matches_current_commit_unit(cwd, manifest):
      return "pending", mark_manifest_code(manifest, "EVIDENCE_UNIT_MISMATCH")
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
  active_work_unit_state = work_unit_stack.current(cwd)
  active_work_units = active_work_unit_state.get("stack", {}).get("frames", [])
  active_work_unit = active_work_unit_state.get("current")
  if isinstance(active_work_unit, dict):
    next_action = {
      "kind": "blocking_unit_in_progress",
      "required_action": "continue_or_exit_blocking_unit",
      "unit_id": active_work_unit.get("unit_id"),
      "parent_unit_id": active_work_unit.get("parent_unit_id"),
      "title": active_work_unit.get("title"),
      "reason": active_work_unit.get("reason"),
      "return_conditions": active_work_unit.get("return_conditions") or [],
      "feature": None,
      "phase": None,
      "stage": None,
    }
    current_state = {
      "active_work_units": active_work_units,
    }
    reasons = []
    verdict, exit_code = "OK", 0
    next_action = attach_required_context(cwd, next_action)
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
  parent_resume_state = work_unit_stack.resume_pending(cwd)
  parent_resume = parent_resume_state.get("current")
  if isinstance(parent_resume, dict):
    next_action = {
      "kind": "parent_resume_pending",
      "required_action": "resume_parent_unit",
      "parent_unit_id": parent_resume.get("parent_unit_id"),
      "completed_unit_id": parent_resume.get("completed_unit_id"),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "blocking unit 完了後に parent unit へ戻る必要があります",
    }
    current_state = {
      "active_work_units": active_work_units,
      "parent_resume_pending": parent_resume,
    }
    reasons = parent_resume_state.get("reasons", [])
    verdict, exit_code = ("DEVIATION", 2) if reasons else ("OK", 0)
    next_action = attach_required_context(cwd, next_action)
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
  start_request_state = work_unit_stack.start_request(cwd)
  start_request = start_request_state.get("current")
  if isinstance(start_request, dict):
    proposed_unit = start_request.get("proposed_unit")
    if not isinstance(proposed_unit, dict):
      proposed_unit = {}
    next_action = {
      "kind": "blocking_unit_required",
      "required_action": "enter_blocking_unit",
      "unit_id": proposed_unit.get("unit_id"),
      "parent_unit_id": proposed_unit.get("parent_unit_id"),
      "title": proposed_unit.get("title"),
      "reason": proposed_unit.get("reason"),
      "return_conditions": proposed_unit.get("return_conditions") or [],
      "feature": None,
      "phase": None,
      "stage": None,
    }
    current_state = {
      "active_work_units": active_work_units,
      "work_unit_start_request": start_request,
    }
    reasons = start_request_state.get("reasons", [])
    verdict, exit_code = ("DEVIATION", 2) if reasons else ("OK", 0)
    next_action = attach_required_context(cwd, next_action)
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
  commit_unit_state, commit_unit_errors = validate_commit_unit_record(cwd)
  commit_unit_codes = commit_unit_state.get("codes") or []
  post_write_targets_for_commit_unit = list_post_write_verification_targets(cwd)
  post_write_state_for_commit_unit = None
  if post_write_targets_for_commit_unit:
    post_write_state_for_commit_unit, _ = evaluate_post_write_manifest_state(
      cwd,
      post_write_targets_for_commit_unit,
    )
  if (
    commit_unit_state.get("exists")
    and "COMMIT_MIXING_RISK" in commit_unit_codes
    and (
      not post_write_targets_for_commit_unit
      or post_write_state_for_commit_unit == "completed"
    )
  ):
    record = commit_unit_state.get("record")
    if not isinstance(record, dict):
      record = {}
    next_action = {
      "kind": "commit_mixing_risk",
      "required_action": "split_or_refresh_commit_unit",
      "target_files": record.get("target_files") or record.get("allowed_files") or [],
      "extra_staged_files": (
        commit_unit_state.get("current_state", {}).get("extra_staged_files") or []
      ),
      "path": commit_unit_state.get("path"),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "commit unit の allowed files 外の staged file が混入しています",
    }
    current_state = {
      "active_work_units": active_work_units,
      "commit_unit": commit_unit_state,
    }
    reasons = commit_unit_errors
    verdict, exit_code = "OK", 0
    next_action = attach_required_context(cwd, next_action)
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
  if (
    commit_unit_state.get("exists")
    and "STALE_COMMIT_UNIT" in commit_unit_codes
    and (
      not post_write_targets_for_commit_unit
      or post_write_state_for_commit_unit == "completed"
    )
  ):
    record = commit_unit_state.get("record")
    if not isinstance(record, dict):
      record = {}
    next_action = {
      "kind": "commit_unit_stale",
      "required_action": "refresh_commit_unit",
      "target_files": record.get("target_files") or record.get("allowed_files") or [],
      "path": commit_unit_state.get("path"),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "commit unit が現在の staged 内容と一致しません",
    }
    current_state = {
      "active_work_units": active_work_units,
      "commit_unit": commit_unit_state,
    }
    reasons = commit_unit_errors
    verdict, exit_code = "OK", 0
    next_action = attach_required_context(cwd, next_action)
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
            "manifest": manifest.get("_path") if isinstance(manifest, dict) else None,
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification 対象の未コミット変更があります",
          }
          if isinstance(manifest, dict) and manifest.get("codes"):
            next_action["codes"] = manifest.get("codes")
          current_state = {
            "post_write_verification_targets": verification_targets,
            "manifest": manifest,
          }
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


SHORT_CONTINUATION_TRIGGER_TEXTS = {
  "次へ",
  "進める",
  "継続",
}


def _normalize_trigger_text(value):
  return re.sub(r"\s+", "", str(value or "")).strip()


def _plan_has_unmaterialized_slice(data):
  if not isinstance(data, dict) or data.get("kind") != "plan":
    return False
  for item in data.get("execution_slices") or []:
    if not isinstance(item, dict):
      continue
    status = item.get("status")
    if status in {None, "", "not_materialized"}:
      return True
  return False


def _find_unmaterialized_plan_ids(cwd, plan_id=None):
  plan_dir = Path(cwd) / ".reviewcompass" / "backlog" / "plans"
  if not plan_dir.is_dir():
    return []
  plan_ids = []
  for path in sorted(plan_dir.glob("*.yaml")):
    try:
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
      continue
    current_plan_id = str(data.get("id") or path.stem)
    if plan_id is not None and current_plan_id != plan_id:
      continue
    if not _plan_has_unmaterialized_slice(data):
      continue
    plan_ids.append(current_plan_id)
  return plan_ids


def resolve_operation_prompt_from_trigger(cwd, trigger_text, plan_id=None):
  normalized = _normalize_trigger_text(trigger_text)
  if normalized not in SHORT_CONTINUATION_TRIGGER_TEXTS:
    return None, {
      "trigger_text": trigger_text,
      "normalized_trigger_text": normalized,
      "trigger_kind": "unsupported",
      "reason": "unsupported_trigger_text",
      "requested_plan_id": plan_id,
      "candidate_plan_ids": [],
    }

  plan_ids = _find_unmaterialized_plan_ids(cwd, plan_id=plan_id)
  if plan_ids:
    reason = (
      "multiple_unmaterialized_plan_candidates"
      if plan_id is None and len(plan_ids) > 1
      else "unmaterialized_plan_slice"
    )
    return "user_initiated_plan_to_todo_bridge", {
      "trigger_text": trigger_text,
      "normalized_trigger_text": normalized,
      "trigger_kind": "short_continuation",
      "reason": reason,
      "requested_plan_id": plan_id,
      "candidate_plan_ids": plan_ids,
    }

  return None, {
    "trigger_text": trigger_text,
    "normalized_trigger_text": normalized,
    "trigger_kind": "short_continuation",
    "reason": "no_unmaterialized_plan_slice",
    "requested_plan_id": plan_id,
    "candidate_plan_ids": [],
  }


def build_operation_prompt_payload(cwd, operation, trigger_resolution=None):
  """不可逆操作直前に読む prompt 情報を返す"""
  effective_prompt = effective_prompt_for_decision_point(
    cwd,
    "operation_prompt",
    operation,
  )
  if effective_prompt is None:
    return None
  prompt_context = {
    "kind": "operation_prompt",
    "operation": operation,
  }
  payload = {
    "verdict": "OK",
    "exit_code": 0,
    "operation": operation,
    "effective_prompt": materialize_effective_prompt(
      cwd,
      prompt_context,
      effective_prompt,
    ),
  }
  if trigger_resolution is not None:
    payload["trigger_resolution"] = trigger_resolution
  if operation == "commit":
    payload["required_operation_card"] = (
      ".reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card"
    )
  return payload


def cmd_operation_prompt(args):
  """不可逆操作用 prompt selection を出力する"""
  cwd = Path.cwd()
  operation = args.operation
  trigger_resolution = None
  if args.trigger_text:
    resolved_operation, trigger_resolution = resolve_operation_prompt_from_trigger(
      cwd,
      args.trigger_text,
      plan_id=args.plan_id,
    )
    if operation is None:
      operation = resolved_operation
    elif resolved_operation is not None and operation != resolved_operation:
      trigger_resolution["explicit_operation"] = operation
      trigger_resolution["resolved_operation"] = resolved_operation
      trigger_resolution["reason"] = "explicit_operation_overrides_trigger_resolution"

  if operation is None:
    payload = {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "operation": None,
      "trigger_resolution": trigger_resolution,
      "reasons": ["trigger_text から operation prompt を解決できません"],
    }
  else:
    payload = build_operation_prompt_payload(cwd, operation, trigger_resolution)
  if payload is None:
    payload = {
      "verdict": "DEVIATION",
      "exit_code": 2,
      "operation": operation,
      "trigger_resolution": trigger_resolution,
      "reasons": [f"未定義の operation prompt です: {operation}"],
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


def cmd_commit_unit(args):
  """commit unit の freeze / check / stage / suggest / postcondition を実行する"""
  if args.commit_unit_command == "freeze":
    response = commit_unit.freeze(
      Path.cwd(),
      args.work_unit_id,
      args.allowed_file,
    )
  elif args.commit_unit_command == "stage":
    response = commit_unit.stage(
      Path.cwd(),
      args.work_unit_id,
      args.target_file,
      args.message,
      args.rationale,
    )
  elif args.commit_unit_command == "check":
    response = commit_unit.check(Path.cwd())
  elif args.commit_unit_command == "suggest":
    response = commit_unit.suggest(
      Path.cwd(),
      args.backlog_id,
      args.checklist_path,
    )
  elif args.commit_unit_command == "postcondition":
    response = commit_unit.postcondition(Path.cwd())
  elif args.commit_unit_command == "clear":
    response = commit_unit.clear(Path.cwd())
  else:
    return 2

  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    verdict = response.get("verdict") or response.get("status")
    print(f"[VERDICT] {verdict}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
  return 0 if response.get("verdict") == "OK" or response.get("status") in ("frozen", "staged") else 2


def cmd_work_unit(args):
  """work unit の enter/current/exit を実行する"""
  if args.work_unit_command == "enter-blocking":
    response = work_unit_stack.enter_blocking(
      Path.cwd(),
      args.unit_id,
      args.parent_unit_id,
      args.title,
      args.reason,
      args.return_condition,
    )
  elif args.work_unit_command == "preflight-start":
    response = work_unit_stack.preflight_start(
      Path.cwd(),
      args.proposed_unit_id,
      args.title,
      args.reason,
    )
  elif args.work_unit_command == "current":
    response = work_unit_stack.current(Path.cwd())
  elif args.work_unit_command == "exit-blocking":
    response = work_unit_stack.exit_blocking(
      Path.cwd(),
      args.unit_id,
      args.completion_summary,
    )
  elif args.work_unit_command == "resume-parent":
    response = work_unit_stack.resume_parent(Path.cwd())
  else:
    return 2

  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {response.get('verdict')}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    current = response.get("current")
    if isinstance(current, dict):
      print(f"[CURRENT] {current.get('unit_id')} {current.get('title')}")
    else:
      print("[CURRENT] none")
  if args.work_unit_command == "preflight-start":
    return 0
  return 0 if response.get("verdict") == "OK" else 2


def cmd_work_checklist(args):
  """work checklist の実行リストを操作する"""
  if args.work_checklist_command == "start":
    response = work_checklist.start(
      Path.cwd(),
      args.checklist_id,
      args.unit_id,
      args.title,
      args.source_ref,
      args.reason,
    )
  elif args.work_checklist_command == "show":
    response = work_checklist.show(
      Path.cwd(),
      args.checklist_id,
    )
  elif args.work_checklist_command == "add-item":
    response = work_checklist.add_item(
      Path.cwd(),
      args.checklist_id,
      args.item_id,
      args.title,
    )
  elif args.work_checklist_command == "set-status":
    response = work_checklist.set_status(
      Path.cwd(),
      args.checklist_id,
      args.item_id,
      args.status,
    )
  elif args.work_checklist_command == "branch":
    response = work_checklist.branch(
      Path.cwd(),
      args.checklist_id,
      args.item_id,
      args.child_checklist_id,
      args.child_title,
      args.source_ref,
      args.reason,
    )
  elif args.work_checklist_command == "close":
    response = work_checklist.close(
      Path.cwd(),
      args.checklist_id,
      args.completion_summary,
    )
  elif args.work_checklist_command == "audit-runtime-completed":
    response = work_checklist.audit_runtime_completed(
      Path.cwd(),
      repair=args.repair,
    )
  elif args.work_checklist_command == "normalize":
    response = work_checklist.normalize(
      Path.cwd(),
      args.checklist_id,
      location=args.location,
      write=args.write,
    )
  elif args.work_checklist_command == "audit-duplicates":
    response = work_checklist.audit_duplicates(Path.cwd())
  elif args.work_checklist_command == "audit-close-postcondition":
    response = work_checklist.audit_close_postcondition(
      Path.cwd(),
      args.checklist_id,
    )
  elif args.work_checklist_command == "audit-reflection":
    response = work_checklist.audit_reflection(
      Path.cwd(),
      backlog_id=args.backlog_id,
      reference=args.reference,
    )
  else:
    return 2

  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {response.get('verdict')}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    checklist = response.get("checklist")
    if isinstance(checklist, dict):
      print(f"[CHECKLIST] {checklist.get('checklist_id')} {checklist.get('status')}")
    progress = response.get("progress")
    if isinstance(progress, dict):
      print(
        "[PROGRESS] "
        f"done={progress.get('done')} "
        f"active={progress.get('active')} "
        f"pending={progress.get('pending')} "
        f"blocked={progress.get('blocked')} "
        f"total={progress.get('total')}"
      )
    for line in response.get("display_lines", []):
      print(line)
  return 0 if response.get("verdict") == "OK" else 2


def cmd_work_backlog(args):
  """workflow 候補 backlog を操作する"""
  if args.work_backlog_command == "add-plan":
    response = work_backlog.add_plan(
      Path.cwd(),
      args.id,
      args.title,
      args.source_unit_id,
      args.source_ref,
      args.reason,
      body_file=args.body_file,
    )
  elif args.work_backlog_command == "add-issue":
    response = work_backlog.add_issue(
      Path.cwd(),
      args.id,
      args.title,
      args.source_unit_id,
      args.source_ref,
      args.reason,
    )
  elif args.work_backlog_command == "add-todo":
    response = work_backlog.add_todo(
      Path.cwd(),
      args.id,
      args.title,
      args.source_unit_id,
      args.source_ref,
      args.reason,
      body_file=args.body_file,
    )
  elif args.work_backlog_command == "list":
    response = work_backlog.list_items(Path.cwd())
  elif args.work_backlog_command == "show":
    response = work_backlog.show(Path.cwd(), args.id)
  elif args.work_backlog_command == "start-checklist":
    response = work_backlog.start_checklist(
      Path.cwd(),
      args.id,
      args.checklist_id,
      args.unit_id,
      mutation_boundary_confirmed=args.mutation_boundary_confirmed,
    )
  elif args.work_backlog_command == "audit-checklist-bridge":
    response = work_backlog.audit_checklist_bridge(Path.cwd())
  elif args.work_backlog_command == "audit-plan-todo-bridge":
    response = work_backlog.audit_plan_todo_bridge(Path.cwd())
  elif args.work_backlog_command == "plan-todo-bridge":
    response = work_backlog.plan_todo_bridge(
      Path.cwd(),
      args.plan_id,
    )
  elif args.work_backlog_command == "audit-checklist-coverage":
    response = work_backlog.audit_checklist_coverage(
      Path.cwd(),
      args.id,
      args.checklist_id,
    )
  elif args.work_backlog_command == "promote":
    response = work_backlog.promote(
      Path.cwd(),
      args.id,
      args.decision_ref,
      args.reason,
    )
  elif args.work_backlog_command == "complete":
    response = work_backlog.complete(
      Path.cwd(),
      args.id,
      args.decision_ref,
      args.reason,
    )
  elif args.work_backlog_command == "reject":
    response = work_backlog.reject(
      Path.cwd(),
      args.id,
      args.decision_ref,
      args.reason,
    )
  else:
    return 2

  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {response.get('verdict')}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    item = response.get("item")
    if isinstance(item, dict):
      print(f"[BACKLOG] {item.get('id')} {item.get('status')}")
  return 0 if response.get("verdict") == "OK" else 2


def cmd_task_quality_check(args):
  """task/checklist への落とし込み品質を監査する"""
  if args.task_quality_check_command == "audit":
    response = task_quality_check.audit(
      Path.cwd(),
      args.backlog_id,
      args.checklist_id,
    )
  elif args.task_quality_check_command == "prepare-review-materials":
    response = task_quality_check.prepare_review_materials(
      Path.cwd(),
      args.backlog_id,
      args.checklist_id,
      args.output_dir,
    )
  elif args.task_quality_check_command == "prepare-review-criteria":
    response = task_quality_check.prepare_review_criteria(
      Path.cwd(),
      args.materials_path,
      args.review_run_dir,
    )
  else:
    return 2

  if args.json:
    print(json.dumps(response, ensure_ascii=False, indent=2))
  else:
    print(f"[VERDICT] {response.get('verdict')}")
    for reason in response.get("reasons", []):
      print(f"[REASON] {reason}")
    quality = response.get("quality")
    if isinstance(quality, dict):
      print(
        "[QUALITY] "
        f"expected={quality.get('expected_count')} "
        f"actual={quality.get('actual_count')} "
        f"missing={len(quality.get('missing_item_ids', []))} "
        f"duplicates={len(quality.get('duplicate_item_ids', []))} "
        f"empty_titles={len(quality.get('empty_title_item_ids', []))}"
      )
  return 0 if response.get("verdict") == "OK" else 2


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
      "仕様 .reviewcompass/guidance/WORKFLOW_PRECHECK.md）"
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

  rws_state = sub.add_parser(
    "repair-workflow-state",
    help="利用者承認済みの workflow state 修復例外 record を作成する",
  )
  rws_state_sub = rws_state.add_subparsers(
    dest="repair_workflow_state_command",
    required=True,
  )
  rws_prepare = rws_state_sub.add_parser(
    "prepare",
    help="現在の未コミット変更に束縛した修復例外 record を作成する",
    parents=[common_parser],
  )
  rws_prepare.add_argument("--reason", required=True, help="修復例外の理由")
  rws_prepare.add_argument("--source-ref", required=True, help="利用者判断の出典")

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
    nargs="?",
    choices=OPERATION_PROMPT_IDS,
    help="対象操作",
  )
  opp.add_argument(
    "--trigger-text",
    default=None,
    help="利用者発話から operation prompt を機械解決する",
  )
  opp.add_argument(
    "--plan-id",
    default=None,
    help="trigger-text 解決時に対象 plan を明示する",
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

  cu = sub.add_parser(
    "commit-unit",
    help="commit 候補の staged 範囲を freeze / check する",
  )
  cu_sub = cu.add_subparsers(
    dest="commit_unit_command",
    required=True,
  )
  cu_freeze = cu_sub.add_parser(
    "freeze",
    help="現在の staged exact index を commit unit として固定する",
    parents=[common_parser],
  )
  cu_freeze.add_argument("--work-unit-id", required=True, help="紐づける work unit ID")
  cu_freeze.add_argument(
    "--allowed-file",
    action="append",
    default=[],
    help="この commit unit に含めてよいファイル。複数指定可",
  )
  cu_stage = cu_sub.add_parser(
    "stage",
    help="target files だけを stage し commit unit として固定する",
    parents=[common_parser],
  )
  cu_stage.add_argument("--work-unit-id", required=True, help="紐づける work unit ID")
  cu_stage.add_argument(
    "--target-file",
    action="append",
    default=[],
    help="この commit unit で stage するファイル。複数指定可",
  )
  cu_stage.add_argument("--message", required=True, help="commit message 候補")
  cu_stage.add_argument("--rationale", required=True, help="commit rationale 候補")
  cu_sub.add_parser(
    "check",
    help="現在の staged exact index が frozen commit unit と一致するか検査する",
    parents=[common_parser],
  )
  cu_suggest = cu_sub.add_parser(
    "suggest",
    help="backlog/checklist から commit message / rationale 候補を生成する",
    parents=[common_parser],
  )
  cu_suggest.add_argument("--backlog-id", required=True, help="候補生成元の backlog TODO ID")
  cu_suggest.add_argument("--checklist-path", required=True, help="候補生成元の checklist path")
  cu_sub.add_parser(
    "postcondition",
    help="commit 後の clean/head/ahead/push 候補を定型出力する",
    parents=[common_parser],
  )
  cu_sub.add_parser(
    "clear",
    help="commit 後に不要になった commit unit runtime marker を削除する",
    parents=[common_parser],
  )

  wu = sub.add_parser(
    "work-unit",
    help="work unit stack の blocking unit 出入りを記録する",
  )
  wu_sub = wu.add_subparsers(
    dest="work_unit_command",
    required=True,
  )
  wu_enter = wu_sub.add_parser(
    "enter-blocking",
    help="blocking unit に入る宣言を runtime stack へ記録する",
    parents=[common_parser],
  )
  wu_enter.add_argument("--unit-id", required=True, help="開始する blocking unit ID")
  wu_enter.add_argument("--parent-unit-id", required=True, help="戻り先の parent unit ID")
  wu_enter.add_argument("--title", required=True, help="blocking unit の題名")
  wu_enter.add_argument("--reason", required=True, help="blocking unit に入る理由")
  wu_enter.add_argument(
    "--return-condition",
    action="append",
    default=[],
    help="戻る条件。複数指定可",
  )
  wu_preflight = wu_sub.add_parser(
    "preflight-start",
    help="新しい作業を始める前に active unit / resume pending を診断する",
    parents=[common_parser],
  )
  wu_preflight.add_argument("--proposed-unit-id", required=True, help="開始候補 unit ID")
  wu_preflight.add_argument("--title", required=True, help="開始候補作業の題名")
  wu_preflight.add_argument("--reason", required=True, help="開始候補作業の理由")
  wu_sub.add_parser(
    "current",
    help="現在の work unit stack を読む",
    parents=[common_parser],
  )
  wu_exit = wu_sub.add_parser(
    "exit-blocking",
    help="blocking unit を終了し evidence snapshot を残す",
    parents=[common_parser],
  )
  wu_exit.add_argument("--unit-id", required=True, help="終了する blocking unit ID")
  wu_exit.add_argument("--completion-summary", required=True, help="完了内容の要約")
  wu_sub.add_parser(
    "resume-parent",
    help="parent resume pending marker を消費して parent unit へ復帰する",
    parents=[common_parser],
  )

  wc = sub.add_parser(
    "work-checklist",
    help="work unit 内の作業チェックリストを操作する",
  )
  wc_sub = wc.add_subparsers(
    dest="work_checklist_command",
    required=True,
  )
  wc_start = wc_sub.add_parser(
    "start",
    help="作業チェックリストを runtime に作成する",
    parents=[common_parser],
  )
  wc_start.add_argument("--checklist-id", required=True, help="作成する checklist ID")
  wc_start.add_argument("--unit-id", required=True, help="紐づける work unit ID")
  wc_start.add_argument("--title", required=True, help="checklist の題名")
  wc_start.add_argument("--source-ref", required=True, help="作成根拠の参照")
  wc_start.add_argument("--reason", required=True, help="checklist を作成する理由")

  wc_show = wc_sub.add_parser(
    "show",
    help="checklist の進捗と人間向けチェック行を表示する",
    parents=[common_parser],
  )
  wc_show.add_argument("--checklist-id", required=True, help="表示する checklist ID")

  wc_add = wc_sub.add_parser(
    "add-item",
    help="checklist に pending item を追加する",
    parents=[common_parser],
  )
  wc_add.add_argument("--checklist-id", required=True, help="対象 checklist ID")
  wc_add.add_argument("--item-id", required=True, help="追加する item ID")
  wc_add.add_argument("--title", required=True, help="item の題名")

  wc_status = wc_sub.add_parser(
    "set-status",
    help="checklist item の status を更新する",
    parents=[common_parser],
  )
  wc_status.add_argument("--checklist-id", required=True, help="対象 checklist ID")
  wc_status.add_argument("--item-id", required=True, help="対象 item ID")
  wc_status.add_argument(
    "--status",
    required=True,
    choices=sorted(work_checklist.ALLOWED_ITEM_STATUSES),
    help="item status",
  )

  wc_branch = wc_sub.add_parser(
    "branch",
    help="blocked item から child checklist を作成する",
    parents=[common_parser],
  )
  wc_branch.add_argument("--checklist-id", required=True, help="親 checklist ID")
  wc_branch.add_argument("--item-id", required=True, help="親 item ID")
  wc_branch.add_argument("--child-checklist-id", required=True, help="child checklist ID")
  wc_branch.add_argument("--child-title", required=True, help="child checklist の題名")
  wc_branch.add_argument("--source-ref", required=True, help="作成根拠の参照")
  wc_branch.add_argument("--reason", required=True, help="child checklist を作成する理由")

  wc_close = wc_sub.add_parser(
    "close",
    help="checklist を完了し evidence snapshot を残す",
    parents=[common_parser],
  )
  wc_close.add_argument("--checklist-id", required=True, help="完了する checklist ID")
  wc_close.add_argument("--completion-summary", default=None, help="完了内容の要約")

  wc_audit_runtime = wc_sub.add_parser(
    "audit-runtime-completed",
    help="runtime に残った completed checklist を監査する",
    parents=[common_parser],
  )
  wc_audit_runtime.add_argument(
    "--repair",
    action="store_true",
    help="completed runtime checklist を evidence へ移動して runtime から削除する",
  )

  wc_normalize = wc_sub.add_parser(
    "normalize",
    help="checklist の checked / progress を再計算する",
    parents=[common_parser],
  )
  wc_normalize.add_argument("--checklist-id", required=True, help="対象 checklist ID")
  wc_normalize.add_argument(
    "--location",
    choices=["runtime", "evidence"],
    default="runtime",
    help="対象 checklist の配置",
  )
  wc_normalize.add_argument(
    "--write",
    action="store_true",
    help="dry-run ではなく正規化結果を書き戻す",
  )

  wc_sub.add_parser(
    "audit-duplicates",
    help="runtime と evidence の checklist 重複を監査する",
    parents=[common_parser],
  )

  wc_postcondition = wc_sub.add_parser(
    "audit-close-postcondition",
    help="checklist close 後の runtime/evidence postcondition を監査する",
    parents=[common_parser],
  )
  wc_postcondition.add_argument("--checklist-id", required=True, help="対象 checklist ID")

  wc_reflection = wc_sub.add_parser(
    "audit-reflection",
    help="checklist 変更の backlog / reference 反映を監査する",
    parents=[common_parser],
  )
  wc_reflection.add_argument("--backlog-id", default=None, help="対象 backlog item ID")
  wc_reflection.add_argument("--reference", default=None, help="反映先または根拠 reference")

  wb = sub.add_parser(
    "work-backlog",
    help="workflow に乗せる前の計画候補・TODO・不具合を管理する",
  )
  wb_sub = wb.add_subparsers(
    dest="work_backlog_command",
    required=True,
  )
  for command, help_text in [
    ("add-plan", "backlog に plan 候補を追加する"),
    ("add-issue", "backlog に issue 候補を追加する"),
    ("add-todo", "backlog に todo 候補を追加する"),
  ]:
    wb_add = wb_sub.add_parser(
      command,
      help=help_text,
      parents=[common_parser],
    )
    wb_add.add_argument("--id", required=True, help="backlog item ID")
    wb_add.add_argument("--title", required=True, help="backlog item の題名")
    wb_add.add_argument("--source-unit-id", required=True, help="発生元 work unit ID")
    wb_add.add_argument("--source-ref", required=True, help="発生根拠の参照")
    wb_add.add_argument("--reason", required=True, help="候補として保存する理由")
    if command in {"add-plan", "add-todo"}:
      wb_add.add_argument(
        "--body-file",
        help="backlog item に追加する詳細本文 YAML",
      )

  wb_sub.add_parser(
    "list",
    help="backlog index を読む",
    parents=[common_parser],
  )
  wb_show = wb_sub.add_parser(
    "show",
    help="backlog item を読む",
    parents=[common_parser],
  )
  wb_show.add_argument("--id", required=True, help="backlog item ID")

  wb_start_checklist = wb_sub.add_parser(
    "start-checklist",
    help="backlog TODO から runtime checklist を生成する",
    parents=[common_parser],
  )
  wb_start_checklist.add_argument("--id", default=None, help="backlog todo item ID")
  wb_start_checklist.add_argument("--checklist-id", default=None, help="作成する checklist ID")
  wb_start_checklist.add_argument("--unit-id", default=None, help="紐づける work unit ID")
  wb_start_checklist.add_argument(
    "--mutation-boundary-confirmed",
    action="store_true",
    help="runtime checklist 作成という状態変更の直前確認を済ませたことを示す",
  )

  wb_sub.add_parser(
    "audit-checklist-bridge",
    help="backlog TODO と runtime/evidence checklist の接続を監査する",
    parents=[common_parser],
  )
  wb_sub.add_parser(
    "audit-plan-todo-bridge",
    help="backlog plan と TODO/checklist/evidence の接続を監査する",
    parents=[common_parser],
  )
  wb_plan_todo = wb_sub.add_parser(
    "plan-todo-bridge",
    help="backlog plan から TODO/checklist 実行導線を確認する",
    parents=[common_parser],
  )
  wb_plan_todo.add_argument("--plan-id", required=True, help="backlog plan item ID")
  wb_audit_coverage = wb_sub.add_parser(
    "audit-checklist-coverage",
    help="backlog TODO から生成される checklist item の coverage を監査する",
    parents=[common_parser],
  )
  wb_audit_coverage.add_argument("--id", default=None, help="backlog todo item ID")
  wb_audit_coverage.add_argument("--checklist-id", default=None, help="監査対象 checklist ID")

  for command, help_text in [
    ("promote", "backlog item を workflow 候補として昇格する"),
    ("complete", "backlog item を完了扱いにする"),
    ("reject", "backlog item を却下する"),
  ]:
    wb_decide = wb_sub.add_parser(
      command,
      help=help_text,
      parents=[common_parser],
    )
    wb_decide.add_argument("--id", required=True, help="backlog item ID")
    wb_decide.add_argument("--decision-ref", required=True, help="判断根拠の参照")
    wb_decide.add_argument("--reason", required=True, help="判断理由")

  tqc = sub.add_parser(
    "task-quality-check",
    help="backlog TODO から task/checklist への落とし込み品質を監査する",
  )
  tqc_sub = tqc.add_subparsers(
    dest="task_quality_check_command",
    required=True,
  )
  tqc_audit = tqc_sub.add_parser(
    "audit",
    help="backlog TODO と checklist の構造的な対応を監査する",
    parents=[common_parser],
  )
  tqc_audit.add_argument("--backlog-id", required=True, help="backlog todo item ID")
  tqc_audit.add_argument("--checklist-id", required=True, help="監査対象 checklist ID")
  tqc_materials = tqc_sub.add_parser(
    "prepare-review-materials",
    help="task/checklist 品質レビュー用の材料 YAML を生成する",
    parents=[common_parser],
  )
  tqc_materials.add_argument("--backlog-id", required=True, help="backlog todo item ID")
  tqc_materials.add_argument("--checklist-id", required=True, help="監査対象 checklist ID")
  tqc_materials.add_argument("--output-dir", required=True, help="review materials 出力先")
  tqc_criteria = tqc_sub.add_parser(
    "prepare-review-criteria",
    help="task/checklist 品質レビュー用の criteria を生成する",
    parents=[common_parser],
  )
  tqc_criteria.add_argument("--materials-path", required=True, help="review materials YAML")
  tqc_criteria.add_argument("--review-run-dir", required=True, help="criteria 出力先")

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
  elif args.subcommand == "repair-workflow-state":
    sys.exit(cmd_repair_workflow_state(args))
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
  elif args.subcommand == "commit-unit":
    sys.exit(cmd_commit_unit(args))
  elif args.subcommand == "work-unit":
    sys.exit(cmd_work_unit(args))
  elif args.subcommand == "work-checklist":
    sys.exit(cmd_work_checklist(args))
  elif args.subcommand == "work-backlog":
    sys.exit(cmd_work_backlog(args))
  elif args.subcommand == "task-quality-check":
    sys.exit(cmd_task_quality_check(args))
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


## tests/tools/test_check_workflow_action.py

"""ワークフロー事前検査スクリプト tools/check-workflow-action.py の単体テスト

対象仕様：.reviewcompass/guidance/WORKFLOW_PRECHECK.md
対象範囲：spec-set サブコマンド（範囲案 2 のうち、MVP 第 1 ラウンドで先行実装）

TDD 規律（AGENTS.md 入口規律）に従い、本テストはスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_check_workflow_action -v
"""

import json
import hashlib
import importlib
import importlib.util
import os
import pty
import shutil
import subprocess
import sys
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


def _approval_gate_record(**overrides):
  record = {
    "schema_version": "approval-gate-v1",
    "decision_id": "D-001",
    "decision": "approved",
    "decision_scope": "human_only",
    "target_operation_id": "requirements_approval",
    "target_required_action": "phase_approval",
    "target_artifact": ".reviewcompass/specs/foundation/spec.json",
    "target_artifact_digest": "sha256:" + "a" * 64,
    "staged_file_set_digest": None,
    "binding_kind": "artifact_digest",
    "decided_by": "user",
    "decided_at": "2026-06-20T00:00:00+00:00",
    "source_ref": "conversation:user:approval",
    "source_digest": "sha256:" + "b" * 64,
    "rationale": "user approved phase approval",
    "next_action_expectation": "proceed",
    "consumed": False,
  }
  record.update(overrides)
  return record


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


def _load_check_workflow_action_module():
  """hyphenated CLI script をテスト内で import する。"""
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(
    "check_workflow_action_cli",
    SCRIPT,
  )
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


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

  def test_spec_set_blocks_approval_gate_record_when_human_only_actor_is_llm(self):
    """approval-gate-v1 は存在だけでなく human-only actor を検査する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.yaml"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text(
      yaml.safe_dump(
        _approval_gate_record(decided_by="llm"),
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
    self.assertIn("human_only", result.stdout)

  def test_spec_set_allows_valid_approval_gate_human_record(self):
    """valid approval-gate-v1 human record は approval predicate を通過する"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    stages_dir = cwd / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    approval_path = cwd / "docs" / "approvals" / "requirements.yaml"
    approval_path.parent.mkdir(parents=True)
    approval_path.write_text(
      yaml.safe_dump(
        _approval_gate_record(),
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
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      ".reviewcompass/guidance/discipline_workflow_state_truth_source.md",
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
      ".reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
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
      ".reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2",
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
    self.assertIn(".reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2", prompt_text)

  def test_next_fails_closed_when_effective_prompt_source_is_missing(self):
    """effective prompt の元資料が読めない判定点は fail-closed とする"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    map_path = cwd / ".reviewcompass" / "guidance" / "WORKFLOW_DISCIPLINE_MAP.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(
      yaml.safe_dump(
        {
          "default": [".reviewcompass/guidance/WORKFLOW_NAVIGATION.md"],
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

  def test_discipline_map_covers_next_action_kinds_with_effective_prompts(self):
    """next --json が返し得る現在地 kind は effective prompt 判定点を持つ"""
    module = _load_check_workflow_action_module()
    expected_kinds = [
      "stage",
      "cross_feature_stage",
      "commit_stop_point",
      "upstream_recheck",
      "reopen_classification_required",
      "completed",
      "unknown",
      "feature_definition_required",
      "post_write_verification",
      "lightweight_self_check",
      "post_write_policy_violation",
      "post_write_human_decision_required",
      "reopen_in_progress",
      "maintenance_in_progress",
      "resume_in_progress",
      "blocking_unit_in_progress",
      "parent_resume_pending",
      "blocking_unit_required",
      "commit_mixing_risk",
      "commit_unit_stale",
    ]
    sample_overrides = {
      "stage": {
        "feature": "workflow-management",
        "phase": "tasks",
        "stage": "triad-review",
      },
      "cross_feature_stage": {
        "feature": "all_features",
        "phase": "tasks",
        "stage": "review-wave",
      },
      "reopen_in_progress": {
        "required_action": "run_reopen_pending_gate",
      },
    }

    missing = []
    for kind in expected_kinds:
      next_action = {
        "kind": kind,
        "feature": None,
        "phase": None,
        "stage": None,
      }
      next_action.update(sample_overrides.get(kind, {}))
      effective_prompt = module.effective_prompt_for_next_action(
        REPO_ROOT,
        next_action,
      )
      if effective_prompt is None:
        missing.append(kind)
        continue
      self.assertIn(
        {"group": "next_action_kind", "id": kind},
        effective_prompt["decision_point_refs"],
      )
      self.assertTrue(
        effective_prompt["prompt_source_refs"],
        f"{kind} has no prompt_source_refs",
      )

    self.assertEqual([], missing)

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
      ".reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card",
    )
    self.assertNotIn("adapter_card", data)
    self.assertEqual(
      data["effective_prompt"]["decision_point_refs"],
      [{"group": "operation_prompt", "id": "commit"}],
    )
    self.assertIn(
      ".reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card",
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

  def test_operation_prompt_user_initiated_backlog_execution_outputs_canonical_prompt(self):
    """ユーザ指示開始の backlog 実行操作は canonical effective prompt を返す"""
    cwd = Path(self.tmpdir)

    result = run_script(
      ["operation-prompt", "user_initiated_backlog_todo_execution", "--json"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation"], "user_initiated_backlog_todo_execution")
    effective_prompt = data["effective_prompt"]
    self.assertEqual(
      effective_prompt["decision_point_refs"],
      [{"group": "operation_prompt", "id": "user_initiated_backlog_todo_execution"}],
    )
    self.assertEqual(
      effective_prompt["effective_prompt_path"],
      ".reviewcompass/guidance/effective-prompts/"
      "user-initiated-backlog-todo-execution.prompt.md",
    )
    self.assertNotIn(
      ".reviewcompass/runtime/effective-prompts",
      effective_prompt["effective_prompt_path"],
    )
    prompt_path = REPO_ROOT / effective_prompt["effective_prompt_path"]
    self.assertTrue(prompt_path.is_file())
    self.assertTrue(effective_prompt["effective_prompt_loaded"])
    self.assertEqual(
      effective_prompt["effective_prompt_sha256"],
      _sha256_file(prompt_path),
    )

  def test_operation_prompt_trigger_text_routes_short_continuation_to_plan_bridge(self):
    """短い継続要求は未展開 plan がある場合 plan-to-TODO bridge prompt へ解決される"""
    cwd = Path(self.tmpdir)
    plan_dir = cwd / ".reviewcompass" / "backlog" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "plan-2026-06-23-plan-todo-checklist-materialization.yaml").write_text(
      yaml.safe_dump(
        {
          "schema_version": "reviewcompass-backlog-item-v1",
          "id": "plan-2026-06-23-plan-todo-checklist-materialization",
          "kind": "plan",
          "title": "Mechanize plan TODO checklist materialization coverage",
          "status": "candidate",
          "implementation_plan": [
            {"id": "PTC-5", "title": "Tests and regression fixtures"},
          ],
          "execution_slices": [
            {
              "phase_id": "PTC-5",
              "title": "Tests and regression fixtures",
              "status": "not_materialized",
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["operation-prompt", "--trigger-text", "次へ", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["operation"], "user_initiated_plan_to_todo_bridge")
    self.assertEqual(data["trigger_resolution"]["trigger_kind"], "short_continuation")
    self.assertEqual(
      data["trigger_resolution"]["reason"],
      "unmaterialized_plan_slice",
    )
    self.assertIn(
      "plan-2026-06-23-plan-todo-checklist-materialization",
      data["trigger_resolution"]["candidate_plan_ids"],
    )

  def test_operation_prompt_trigger_text_rejects_when_all_plan_slices_materialized(self):
    """未展開 slice がなければ短い継続要求から operation を解決しない"""
    cwd = Path(self.tmpdir)
    plan_dir = cwd / ".reviewcompass" / "backlog" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "plan-done.yaml").write_text(
      yaml.safe_dump(
        {
          "schema_version": "reviewcompass-backlog-item-v1",
          "id": "plan-done",
          "kind": "plan",
          "title": "Done plan",
          "status": "candidate",
          "execution_slices": [
            {"phase_id": "A", "status": "completed"},
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(["operation-prompt", "--trigger-text", "次へ", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIsNone(data["operation"])
    self.assertEqual(
      data["trigger_resolution"]["reason"],
      "no_unmaterialized_plan_slice",
    )

  def test_operation_prompt_trigger_text_reports_multiple_plan_candidates(self):
    """複数 plan 候補がある場合は bridge へ行くが曖昧さを出力する"""
    cwd = Path(self.tmpdir)
    plan_dir = cwd / ".reviewcompass" / "backlog" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    for plan_id in ["plan-one", "plan-two"]:
      (plan_dir / f"{plan_id}.yaml").write_text(
        yaml.safe_dump(
          {
            "schema_version": "reviewcompass-backlog-item-v1",
            "id": plan_id,
            "kind": "plan",
            "title": plan_id,
            "status": "candidate",
            "execution_slices": [
              {"phase_id": "A", "status": "not_materialized"},
            ],
          },
          allow_unicode=True,
          sort_keys=False,
        ),
        encoding="utf-8",
      )

    result = run_script(["operation-prompt", "--trigger-text", "進める", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["operation"], "user_initiated_plan_to_todo_bridge")
    self.assertEqual(
      data["trigger_resolution"]["reason"],
      "multiple_unmaterialized_plan_candidates",
    )
    self.assertEqual(
      data["trigger_resolution"]["candidate_plan_ids"],
      ["plan-one", "plan-two"],
    )

  def test_operation_prompt_trigger_text_can_scope_to_plan_id(self):
    """plan-id 指定時は候補を現在対象 plan に絞る"""
    cwd = Path(self.tmpdir)
    plan_dir = cwd / ".reviewcompass" / "backlog" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    for plan_id in ["plan-one", "plan-two"]:
      (plan_dir / f"{plan_id}.yaml").write_text(
        yaml.safe_dump(
          {
            "schema_version": "reviewcompass-backlog-item-v1",
            "id": plan_id,
            "kind": "plan",
            "title": plan_id,
            "status": "candidate",
            "execution_slices": [
              {"phase_id": "A", "status": "not_materialized"},
            ],
          },
          allow_unicode=True,
          sort_keys=False,
        ),
        encoding="utf-8",
      )

    result = run_script(
      ["operation-prompt", "--trigger-text", "継続", "--plan-id", "plan-two", "--json"],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["operation"], "user_initiated_plan_to_todo_bridge")
    self.assertEqual(data["trigger_resolution"]["reason"], "unmaterialized_plan_slice")
    self.assertEqual(data["trigger_resolution"]["candidate_plan_ids"], ["plan-two"])

  def test_operation_prompt_default_map_keeps_materialization_plan_refs(self):
    """fallback discipline map も plan materialization source refs を保持する"""
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    try:
      spec = importlib.util.spec_from_file_location(
        "check_workflow_action_script",
        SCRIPT,
      )
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)
    finally:
      sys.path.pop(0)
    default_points = module.DEFAULT_DISCIPLINE_MAP["decision_points"]["operation_prompt"]

    refs_by_id = {
      point["id"]: point["prompt_source_refs"]
      for point in default_points
      if point["id"] in {
        "user_initiated_plan_to_todo_bridge",
        "user_initiated_backlog_todo_execution",
      }
    }

    for refs in refs_by_id.values():
      self.assertIn(
        ".reviewcompass/backlog/plans/"
        "plan-2026-06-23-plan-todo-checklist-materialization.yaml",
        refs,
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
      "  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md\n"
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
      [".reviewcompass/guidance/WORKFLOW_NAVIGATION.md", "TODO_NEXT_SESSION.md"],
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
      ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification",
      data["next_action"]["required_disciplines"],
    )
    self.assertIn(
      ".reviewcompass/guidance/discipline_post_write_verification.md",
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
      "    evidence: [.reviewcompass/guidance/REOPEN_PROCEDURE.md]\n"
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

  def test_next_post_write_verification_returns_canonical_effective_prompt(self):
    """post-write-verification 地点では runtime 合成ではなく canonical prompt を返す"""
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
    action = data["next_action"]
    self.assertEqual(action["kind"], "post_write_verification")
    effective_prompt = action["effective_prompt"]
    self.assertEqual(
      effective_prompt["effective_prompt_path"],
      ".reviewcompass/guidance/effective-prompts/"
      "next-action-post-write-verification.prompt.md",
    )
    self.assertNotIn(
      ".reviewcompass/runtime/effective-prompts",
      effective_prompt["effective_prompt_path"],
    )
    self.assertTrue(effective_prompt["effective_prompt_loaded"])

  def test_next_routes_notes_to_lightweight_self_check(self):
    """docs/notes 配下だけなら API post-write ではなく軽量自己精査を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "memo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("作業中メモ\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "lightweight_self_check")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/memo.md"])
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

  def test_next_routes_regular_notes_to_lightweight_self_check(self):
    """docs/notes 直下も軽量自己精査へ回す"""
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
    self.assertEqual(data["next_action"]["kind"], "lightweight_self_check")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/memo.md"])
    effective_prompt_path = cwd / data["next_action"]["effective_prompt"]["effective_prompt_path"]
    effective_prompt_text = effective_prompt_path.read_text(encoding="utf-8")
    self.assertIn("`docs/notes/` 配下", effective_prompt_text)
    self.assertNotIn("既存の `docs/notes/*.md` は", effective_prompt_text)

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

  def test_next_prioritizes_strict_post_write_when_mixed_with_notes(self):
    """軽量メモと strict 対象が混ざる場合は strict post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    working = cwd / "docs" / "notes" / "memo.md"
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
      ["docs/notes/memo.md"],
    )

  def test_next_post_write_verification_target_matrix(self):
    """規律で定義された post-write-verification 対象だけを検出する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_paths = [
      "TODO_NEXT_SESSION.md",
      "docs/experiments/foo.md",
      "docs/operations/foo.md",
      "docs/plan/foo.md",
      "docs/reviews/2026-06-02-audit-foo.md",
      "docs/reviews/reopen-classification-2026-06-02.md",
      "docs/workflow-evidence/future-generated.yaml",
    ]
    non_target_paths = [
      ".reviewcompass/specs/foundation/spec.json",
      "docs/archive/foo.md",
      "docs/notes/foo.md",
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
    for path in ["docs/logs/workflow-precheck.log", "docs/operations/foo.md"]:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/operations/foo.md"])

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

  def test_next_rejects_manifest_when_unit_binding_mismatches_commit_unit(self):
    """manifest の unit binding が現在の commit unit と違えば完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    commit_unit_path = cwd / ".reviewcompass" / "runtime" / "work-units" / "commit-unit.json"
    commit_unit_path.parent.mkdir(parents=True, exist_ok=True)
    commit_unit_path.write_text(
      json.dumps(
        {
          "schema_version": "commit-unit-v1",
          "commit_unit_id": "commit-unit-current",
          "work_unit_id": "unit-current",
          "staged_digest": {
            "algorithm": "commit-unit-v1",
            "digest": "current-digest",
          },
        },
        ensure_ascii=False,
        indent=2,
      )
      + "\n",
      encoding="utf-8",
    )
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
        "unit_binding": {
          "work_unit_id": "unit-old",
          "commit_unit_id": "commit-unit-old",
          "staged_digest": {
            "algorithm": "commit-unit-v1",
            "digest": "old-digest",
          },
        },
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertIn(
      "EVIDENCE_UNIT_MISMATCH",
      data["next_action"]["codes"],
    )

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

  def test_next_post_write_policy_violation_returns_canonical_effective_prompt(self):
    """policy violation 地点では runtime 合成ではなく canonical prompt を返す"""
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
    action = data["next_action"]
    self.assertEqual(action["kind"], "post_write_policy_violation")
    effective_prompt = action["effective_prompt"]
    self.assertEqual(
      effective_prompt["effective_prompt_path"],
      ".reviewcompass/guidance/effective-prompts/"
      "next-action-post-write-policy-violation.prompt.md",
    )
    self.assertNotIn(
      ".reviewcompass/runtime/effective-prompts",
      effective_prompt["effective_prompt_path"],
    )
    self.assertTrue(effective_prompt["effective_prompt_loaded"])

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
    discipline = cwd / ".reviewcompass" / "guidance" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("越境した規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      [".reviewcompass/guidance/discipline_approval_operation.md"],
    )

  def test_next_allows_discipline_post_write_when_it_is_the_only_target(self):
    """規律ファイル単独の変更は post-write-verification 対象として扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    discipline = cwd / ".reviewcompass" / "guidance" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("正式手続き後の規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      [".reviewcompass/guidance/discipline_approval_operation.md"],
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
    in_progress.parent.mkdir(parents=True, exist_ok=True)
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

  def test_reopen_advance_gate_consumes_recorded_approval_record(self):
    """承認済み approval gate を完了したら approval record を再利用不可にする"""
    approval_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "approvals"
      / "req-approval.yaml"
    )
    approval_path.parent.mkdir(parents=True, exist_ok=True)
    approval_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "approval-gate-v1",
          "decision_id": "REQ-APPROVAL-001",
          "decision": "approved",
          "decision_scope": "human_only",
          "target_operation_id": "run_reopen_pending_gate",
          "target_required_action": "run_reopen_pending_gate",
          "target_artifact": ".reviewcompass/specs/workflow-management/requirements.md",
          "target_artifact_digest": "sha256:" + "a" * 64,
          "staged_file_set_digest": None,
          "binding_kind": "artifact_digest",
          "decided_by": "user",
          "decided_at": "2026-06-20T00:00:00+00:00",
          "source_ref": "conversation:user:approval",
          "source_digest": "sha256:" + "b" * 64,
          "rationale": "利用者が approval gate を承認した。",
          "next_action_expectation": "proceed",
          "consumed": False,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-15.yaml"
    )
    in_progress.parent.mkdir(parents=True, exist_ok=True)
    in_progress.write_text(
      yaml.safe_dump(
        {
          "process_id": "reopen-procedure",
          "feature": "workflow-management",
          "step_number": 3,
          "next_step": "第3過程：requirements approval",
          "completed_steps": [],
          "pending_gates": ["stages/requirements.yaml#approval"],
          "completed_gates": [],
          "downstream_impact_decisions": [],
          "current_blocker": {
            "blocker_type": "approval_gate",
            "gate": "stages/requirements.yaml#approval",
            "actor": "human",
            "status": "decision_recorded",
            "approval_record_path": ".reviewcompass/runtime/approvals/req-approval.yaml",
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

    result = run_script(
      [
        "reopen-advance-gate",
        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision", "approved",
        "--feature-scope", "workflow-management",
        "--rationale", "requirements approval を承認済み record に基づいて完了する。",
        "--evidence", ".reviewcompass/runtime/approvals/req-approval.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    record = yaml.safe_load(approval_path.read_text(encoding="utf-8"))
    self.assertIs(record["consumed"], True)
    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertIsNone(state["current_blocker"])

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


class RecordHumanDecisionTests(unittest.TestCase):
  """record-human-decision サブコマンドの承認判断記録"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_blocked_in_progress(self):
    in_progress = (
      Path(self.tmpdir)
      / "stages"
      / "in-progress"
      / "reopen-procedure-2026-06-20.yaml"
    )
    in_progress.parent.mkdir(parents=True, exist_ok=True)
    in_progress.write_text(
      yaml.safe_dump(
        {
          "process_id": "reopen-procedure",
          "feature": "workflow-management",
          "step_number": 3,
          "next_step": "第3過程：連鎖再実施",
          "pending_gates": [
            "stages/requirements.yaml#approval",
          ],
          "current_blocker": {
            "blocker_type": "approval_gate",
            "gate": "stages/requirements.yaml#approval",
            "actor": "human",
            "status": "waiting_for_approval",
            "rationale": "approval gate に到達した。",
            "evidence": [
              ".reviewcompass/specs/workflow-management/requirements.md",
            ],
          },
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )
    return in_progress

  def _write_run_reopen_pending_gate_contract(self):
    contracts_path = Path(self.tmpdir) / "stages" / "operation-contracts.yaml"
    contracts_path.parent.mkdir(parents=True, exist_ok=True)
    contracts_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "operation-contracts-v1",
          "operations": [
            {
              "schema_version": "operation-contract-v1",
              "operation_id": "run_reopen_pending_gate",
              "required_action": "run_reopen_pending_gate",
              "effect_kind": "external_call",
              "approval_required": False,
              "phase_boundary": "within_phase",
              "actor": {"kind": "mixed"},
              "branching": {
                "has_branches": True,
                "branches": [
                  {
                    "branch_id": "approval",
                    "condition": "active_gate=approval",
                    "internal_steps": [
                      {
                        "step_id": "record_approval_stop_point",
                        "effect_kind": "state_mutation",
                        "approval_required": True,
                        "phase_boundary": "within_phase",
                      },
                    ],
                    "max_effect_kind": "state_mutation",
                    "approval_aggregation": True,
                    "human_only_override_applies": True,
                  },
                ],
              },
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

  def _write_target_artifact(self):
    target = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "specs"
      / "workflow-management"
      / "requirements.md"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("承認対象 requirements\n", encoding="utf-8")
    return target

  def _current_staged_file_set_digest(self):
    commit_approval = _load_commit_approval_module()
    canonical = commit_approval.canonical_target(self.tmpdir)
    digest = commit_approval.staged_file_set_digest_from_canonical(canonical)
    return "sha256:" + digest["digest"]

  def test_record_human_decision_saves_record_and_binds_current_blocker(self):
    """人間判断を approval record として保存し blocker に path を結びつける"""
    in_progress = self._write_blocked_in_progress()
    out_path = ".reviewcompass/runtime/approvals/req-approval.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-001",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "requirements_approval",
        "--target-required-action", "phase_approval",
        "--target-artifact", ".reviewcompass/specs/workflow-management/spec.json",
        "--target-artifact-digest", "sha256:" + "a" * 64,
        "--binding-kind", "artifact_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が approval gate を承認した。",
        "--next-action-expectation", "proceed",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")

    record_path = Path(self.tmpdir) / out_path
    self.assertTrue(record_path.exists())
    record = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    self.assertEqual(record["schema_version"], "approval-gate-v1")
    self.assertEqual(record["decision"], "approved")
    self.assertEqual(record["consumed"], False)

    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    blocker = state["current_blocker"]
    self.assertEqual(blocker["status"], "decision_recorded")
    self.assertEqual(blocker["approval_record_path"], out_path)
    self.assertEqual(blocker["gate"], "stages/requirements.yaml#approval")

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    next_data = json.loads(next_result.stdout)
    blocked_by = next_data["next_action"]["blocked_by"]
    self.assertEqual(next_data["next_action"]["required_action"], "wait_for_human_decision")
    self.assertEqual(blocked_by["status"], "decision_recorded")
    self.assertEqual(blocked_by["approval_record_path"], out_path)

  def test_next_allows_pending_approval_gate_when_record_matches_current_digest(self):
    """承認 record が contract と現在 digest に一致すれば approval gate へ進める"""
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    out_path = ".reviewcompass/runtime/approvals/req-approval.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-003",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--binding-kind", "artifact_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が approval gate を承認した。",
        "--next-action-expectation", "proceed",
        "--out", out_path,
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
    self.assertEqual(action["required_action"], "run_reopen_pending_gate")
    self.assertEqual(action["active_gate"], "stages/requirements.yaml#approval")
    self.assertEqual(action["next_pending_gate"], "stages/requirements.yaml#approval")
    self.assertIsNone(action["blocked_by"])
    self.assertEqual(action["approval_record_path"], out_path)

  def test_next_blocks_recorded_approval_when_target_artifact_digest_is_stale(self):
    """承認後に対象 artifact が変わった場合は approval gate へ進めない"""
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    out_path = ".reviewcompass/runtime/approvals/stale-approval.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-004",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--binding-kind", "artifact_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が approval gate を承認した。",
        "--next-action-expectation", "proceed",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    target.write_text("承認後に変更された requirements\n", encoding="utf-8")
    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    next_data = json.loads(next_result.stdout)
    action = next_data["next_action"]
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertEqual(action["blocked_by"]["approval_record_verdict"], "DEVIATION")
    self.assertIn(
      "target_artifact_digest が現在の対象 digest と一致しません",
      "\n".join(action["blocked_by"]["approval_record_reasons"]),
    )

  def test_next_allows_pending_approval_gate_when_staged_file_set_digest_matches(self):
    """staged_file_set_digest が現在 index と一致すれば approval gate へ進める"""
    _init_git_repo(self.tmpdir)
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    _stage_file(self.tmpdir, "notes/staged.txt", "承認時点の staged file\n")
    staged_digest = self._current_staged_file_set_digest()
    out_path = ".reviewcompass/runtime/approvals/staged-approval.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-STAGED-001",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--staged-file-set-digest", staged_digest,
        "--binding-kind", "staged_file_set_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が staged file set を承認した。",
        "--next-action-expectation", "proceed",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "run_reopen_pending_gate")
    self.assertEqual(action["approval_record_path"], out_path)
    self.assertIsNone(action["blocked_by"])

  def test_next_blocks_recorded_approval_when_staged_file_set_digest_is_stale(self):
    """承認後に staged file set が変わった場合は approval gate へ進めない"""
    _init_git_repo(self.tmpdir)
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    _stage_file(self.tmpdir, "notes/staged.txt", "承認時点の staged file\n")
    staged_digest = self._current_staged_file_set_digest()

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-STAGED-002",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--staged-file-set-digest", staged_digest,
        "--binding-kind", "staged_file_set_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が staged file set を承認した。",
        "--next-action-expectation", "proceed",
        "--out", ".reviewcompass/runtime/approvals/staged-stale-approval.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    _stage_file(self.tmpdir, "notes/added-after-approval.txt", "承認後の staged file\n")
    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertEqual(action["blocked_by"]["approval_record_verdict"], "DEVIATION")
    self.assertIn(
      "staged_file_set_digest が現在の staged digest と一致しません",
      "\n".join(action["blocked_by"]["approval_record_reasons"]),
    )

  def test_next_allows_pending_approval_gate_when_both_digests_match(self):
    """both は artifact digest と staged file set digest の両方一致を要求する"""
    _init_git_repo(self.tmpdir)
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    _stage_file(self.tmpdir, "notes/staged.txt", "承認時点の staged file\n")
    staged_digest = self._current_staged_file_set_digest()
    out_path = ".reviewcompass/runtime/approvals/both-approval.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-BOTH-001",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--staged-file-set-digest", staged_digest,
        "--binding-kind", "both",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が artifact と staged file set を承認した。",
        "--next-action-expectation", "proceed",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "run_reopen_pending_gate")
    self.assertEqual(action["approval_record_path"], out_path)
    self.assertIsNone(action["blocked_by"])

  def test_next_blocks_recorded_approval_when_both_binding_has_stale_staged_digest(self):
    """both の staged 側 digest が古い場合は approval gate へ進めない"""
    _init_git_repo(self.tmpdir)
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    _stage_file(self.tmpdir, "notes/staged.txt", "承認時点の staged file\n")
    staged_digest = self._current_staged_file_set_digest()

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-BOTH-002",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--staged-file-set-digest", staged_digest,
        "--binding-kind", "both",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が artifact と staged file set を承認した。",
        "--next-action-expectation", "proceed",
        "--out", ".reviewcompass/runtime/approvals/both-stale-approval.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    _stage_file(self.tmpdir, "notes/added-after-approval.txt", "承認後の staged file\n")
    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "wait_for_human_decision")
    self.assertIn(
      "staged_file_set_digest が現在の staged digest と一致しません",
      "\n".join(action["blocked_by"]["approval_record_reasons"]),
    )

  def test_next_distinguishes_rejected_and_deferred_approval_decisions(self):
    """rejected / deferred は停止理由を区別して対象 gate へ進めない"""
    for decision, expectation in [
      ("rejected", "stay_blocked"),
      ("deferred", "stay_blocked"),
    ]:
      with self.subTest(decision=decision):
        self._write_blocked_in_progress()
        self._write_run_reopen_pending_gate_contract()
        target = self._write_target_artifact()
        target_rel = str(target.relative_to(self.tmpdir))
        target_digest = "sha256:" + _sha256_file(target)

        result = run_script(
          [
            "record-human-decision",
            "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
            "--gate", "stages/requirements.yaml#approval",
            "--decision-id", f"REQ-APPROVAL-{decision}",
            "--decision", decision,
            "--decision-scope", "human_only",
            "--target-operation-id", "run_reopen_pending_gate",
            "--target-required-action", "run_reopen_pending_gate",
            "--target-artifact", target_rel,
            "--target-artifact-digest", target_digest,
            "--binding-kind", "artifact_digest",
            "--decided-by", "user",
            "--decided-at", "2026-06-20T00:00:00+00:00",
            "--source-ref", "conversation:user:approval",
            "--source-digest", "sha256:" + "b" * 64,
            "--rationale", f"利用者判断: {decision}",
            "--next-action-expectation", expectation,
            "--out", f".reviewcompass/runtime/approvals/{decision}.yaml",
            "--json",
          ],
          cwd=self.tmpdir,
        )
        _assert_script_invoked(self, result)
        self.assertEqual(result.returncode, 0, result.stdout)

        next_result = run_script(["next", "--json"], cwd=self.tmpdir)
        _assert_script_invoked(self, next_result)
        self.assertEqual(next_result.returncode, 0, next_result.stdout)
        action = json.loads(next_result.stdout)["next_action"]
        self.assertEqual(action["required_action"], "wait_for_human_decision")
        self.assertEqual(action["blocked_by"]["approval_decision"], decision)
        self.assertEqual(action["blocked_by"]["approval_decision_route"], "stay_blocked")

  def test_next_routes_changes_requested_to_reopen_drafting_when_expectation_is_redraft(self):
    """changes_requested + redraft は同じ phase の drafting へ戻す"""
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    out_path = ".reviewcompass/runtime/approvals/changes-requested.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-005",
        "--decision", "changes_requested",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--binding-kind", "artifact_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が再起草を要求した。",
        "--next-action-expectation", "redraft",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "run_reopen_drafting")
    self.assertEqual(action["active_gate"], "stages/requirements.yaml#drafting")
    self.assertEqual(action["next_drafting_gate"], "stages/requirements.yaml#drafting")
    self.assertEqual(action["approval_record_path"], out_path)
    self.assertIsNone(action["blocked_by"])

  def test_next_routes_changes_requested_to_repair_when_expectation_is_repair(self):
    """changes_requested + repair は workflow state repair 停止へ進む"""
    self._write_blocked_in_progress()
    self._write_run_reopen_pending_gate_contract()
    target = self._write_target_artifact()
    target_rel = str(target.relative_to(self.tmpdir))
    target_digest = "sha256:" + _sha256_file(target)
    out_path = ".reviewcompass/runtime/approvals/changes-requested-repair.yaml"

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-006",
        "--decision", "changes_requested",
        "--decision-scope", "human_only",
        "--target-operation-id", "run_reopen_pending_gate",
        "--target-required-action", "run_reopen_pending_gate",
        "--target-artifact", target_rel,
        "--target-artifact-digest", target_digest,
        "--binding-kind", "artifact_digest",
        "--decided-by", "user",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:user:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "利用者が repair を要求した。",
        "--next-action-expectation", "repair",
        "--out", out_path,
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

    next_result = run_script(["next", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, next_result)
    self.assertEqual(next_result.returncode, 0, next_result.stdout)
    action = json.loads(next_result.stdout)["next_action"]
    self.assertEqual(action["required_action"], "repair_workflow_state")
    self.assertIsNone(action["active_gate"])
    self.assertIsNone(action["phase"])
    self.assertIsNone(action["stage"])
    self.assertEqual(action["approval_record_path"], out_path)
    self.assertIn("changes_requested", "\n".join(action["repair_reasons"]))
    self.assertIsNone(action["blocked_by"])

  def test_record_human_decision_rejects_llm_for_human_only_scope(self):
    """human_only decision は record 操作時点でも LLM actor を拒否する"""
    self._write_blocked_in_progress()

    result = run_script(
      [
        "record-human-decision",
        "--file", "stages/in-progress/reopen-procedure-2026-06-20.yaml",
        "--gate", "stages/requirements.yaml#approval",
        "--decision-id", "REQ-APPROVAL-002",
        "--decision", "approved",
        "--decision-scope", "human_only",
        "--target-operation-id", "requirements_approval",
        "--target-required-action", "phase_approval",
        "--target-artifact", ".reviewcompass/specs/workflow-management/spec.json",
        "--target-artifact-digest", "sha256:" + "a" * 64,
        "--binding-kind", "artifact_digest",
        "--decided-by", "llm",
        "--decided-at", "2026-06-20T00:00:00+00:00",
        "--source-ref", "conversation:assistant:approval",
        "--source-digest", "sha256:" + "b" * 64,
        "--rationale", "LLM が承認した。",
        "--next-action-expectation", "proceed",
        "--out", ".reviewcompass/runtime/approvals/llm-approval.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    self.assertIn("human_only decision", result.stdout)
    self.assertFalse(
      (Path(self.tmpdir) / ".reviewcompass/runtime/approvals/llm-approval.yaml").exists()
    )


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


class CommitUnitIsolationTests(unittest.TestCase):
  """blocking unit 中の commit 候補混線を機械検出する"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _write_and_stage(self, relative_path, text):
    path = Path(self.tmpdir) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subprocess.run(
      ["git", "add", relative_path],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def _freeze_commit_unit(self, allowed_files):
    args = [
      "commit-unit",
      "freeze",
      "--work-unit-id", "unit-blocking-001",
      "--json",
    ]
    for allowed_file in allowed_files:
      args.extend(["--allowed-file", allowed_file])
    result = run_script(args, cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    return result

  def _write_active_blocking_unit(self, unit_id="unit-blocking-001"):
    stack_path = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "work-units"
      / "stack.yaml"
    )
    stack_path.parent.mkdir(parents=True, exist_ok=True)
    stack_path.write_text(
      yaml.safe_dump(
        {
          "schema_version": "work-unit-stack-v1",
          "frames": [
            {
              "unit_id": unit_id,
              "kind": "blocking",
              "parent_unit_id": "main-completed",
              "title": "active",
              "reason": "test",
              "status": "active",
              "return_conditions": ["done"],
            },
          ],
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

  def test_commit_unit_freeze_records_allowed_staged_scope(self):
    """freeze は現在の staged exact index と allowed files を record に固定する"""
    self._write_and_stage("tools/check_workflow_action/blocking_unit.py", "print('x')\n")

    result = self._freeze_commit_unit([
      "tools/check_workflow_action/blocking_unit.py",
    ])

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["status"], "frozen")
    self.assertEqual(data["record"]["work_unit_id"], "unit-blocking-001")
    self.assertEqual(
      data["record"]["staged_files"],
      ["tools/check_workflow_action/blocking_unit.py"],
    )
    self.assertEqual(
      data["record"]["allowed_files"],
      ["tools/check_workflow_action/blocking_unit.py"],
    )

  def test_commit_unit_check_detects_mixing_outside_allowed_files(self):
    """freeze 後に別 unit の staged file が混ざったら COMMIT_MIXING_RISK"""
    self._write_and_stage("tools/check_workflow_action/blocking_unit.py", "print('x')\n")
    freeze = self._freeze_commit_unit([
      "tools/check_workflow_action/blocking_unit.py",
    ])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_and_stage("docs/notes/working/other.md", "別作業\n")

    result = run_script(["commit-unit", "check", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("COMMIT_MIXING_RISK", data["codes"])
    self.assertEqual(data["current_state"]["extra_staged_files"], [
      "docs/notes/working/other.md",
    ])

  def test_commit_unit_check_detects_stale_staged_digest(self):
    """allowed file だけでも staged 内容が変わったら STALE_COMMIT_UNIT"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_and_stage(target, "print('x')\n")
    freeze = self._freeze_commit_unit([target])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_and_stage(target, "print('changed')\n")

    result = run_script(["commit-unit", "check", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("STALE_COMMIT_UNIT", data["codes"])

  def test_commit_preflight_blocks_stale_commit_unit(self):
    """commit-preflight は frozen commit unit から外れた staged 内容を遮断する"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_and_stage(target, "print('x')\n")
    freeze = self._freeze_commit_unit([target])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_and_stage(target, "print('changed')\n")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_stage"])
    self.assertIn(
      "STALE_COMMIT_UNIT",
      data["current_state"]["commit_unit"]["codes"],
    )

  def test_commit_preflight_blocks_commit_unit_for_different_active_work_unit(self):
    """commit-preflight は active work unit と異なる commit unit を遮断する"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_and_stage(target, "print('x')\n")
    freeze = self._freeze_commit_unit([target])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_active_blocking_unit("unit-active-current")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertIn(
      "WORK_UNIT_COMMIT_UNIT_MISMATCH",
      data["current_state"]["commit_unit"]["codes"],
    )

  def test_commit_preflight_blocks_parent_commit_without_commit_unit_during_blocking_unit(self):
    """active blocking unit 中は commit unit なしの親作業 commit を遮断する"""
    _write_specs_for_next(Path(self.tmpdir), {})
    self._write_active_blocking_unit("unit-blocking-001")
    self._write_and_stage("parent-work.txt", "parent change\n")

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_run_guarded_commit"])
    self.assertIn(
      "PARENT_COMMIT_DURING_BLOCKING_UNIT",
      data["current_state"]["commit_unit"]["codes"],
    )

  def test_next_reports_stale_commit_unit_before_normal_workflow(self):
    """next は stale commit unit を通常 workflow より先に停止点として返す"""
    target = "tools/check_workflow_action/blocking_unit.py"
    self._write_and_stage(target, "print('x')\n")
    freeze = self._freeze_commit_unit([target])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_and_stage(target, "print('changed')\n")

    result = run_script(["next", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "commit_unit_stale")
    self.assertEqual(data["next_action"]["required_action"], "refresh_commit_unit")
    self.assertIn(
      "STALE_COMMIT_UNIT",
      data["current_state"]["commit_unit"]["codes"],
    )

  def test_next_reports_commit_mixing_risk_before_normal_workflow(self):
    """next は commit unit 外の staged 混入を通常 workflow より先に返す"""
    self._write_and_stage("tools/check_workflow_action/blocking_unit.py", "print('x')\n")
    freeze = self._freeze_commit_unit([
      "tools/check_workflow_action/blocking_unit.py",
    ])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    self._write_and_stage("docs/notes/working/other.md", "別作業\n")

    result = run_script(["next", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "commit_mixing_risk")
    self.assertEqual(data["next_action"]["required_action"], "split_or_refresh_commit_unit")
    self.assertIn(
      "COMMIT_MIXING_RISK",
      data["current_state"]["commit_unit"]["codes"],
    )
    self.assertEqual(
      data["current_state"]["commit_unit"]["current_state"]["extra_staged_files"],
      ["docs/notes/working/other.md"],
    )

  def test_commit_unit_stage_adds_only_target_files_and_records_message(self):
    """commit-unit stage は target_files だけを stage し message / rationale を固定する"""
    target = Path(self.tmpdir) / "docs" / "target.md"
    other = Path(self.tmpdir) / "docs" / "other.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("target\n", encoding="utf-8")
    other.write_text("other\n", encoding="utf-8")

    result = run_script(
      [
        "commit-unit",
        "stage",
        "--work-unit-id", "unit-blocking-001",
        "--target-file", "docs/target.md",
        "--message", "Record target change",
        "--rationale", "利用者が対象 TODO の実装を承認",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["status"], "staged")
    self.assertEqual(data["record"]["target_files"], ["docs/target.md"])
    self.assertEqual(data["record"]["staged_files"], ["docs/target.md"])
    self.assertEqual(data["record"]["message"], "Record target change")
    self.assertEqual(data["record"]["rationale"], "利用者が対象 TODO の実装を承認")
    staged = subprocess.run(
      ["git", "diff", "--cached", "--name-only"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
      text=True,
    )
    self.assertEqual(staged.stdout.splitlines(), ["docs/target.md"])

  def test_commit_unit_suggest_builds_message_and_rationale_candidates(self):
    """commit-unit suggest は checklist / backlog から短い候補を生成する"""
    checklist = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "evidence"
      / "work-units"
      / "checklists"
      / "checklist-demo.yaml"
    )
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text(
      "checklist_id: checklist-demo\n"
      "source_backlog_item_id: todo-demo\n"
      "completion_summary: commit unit target file staging を実装した\n",
      encoding="utf-8",
    )

    result = run_script(
      [
        "commit-unit",
        "suggest",
        "--backlog-id", "todo-demo",
        "--checklist-path", ".reviewcompass/evidence/work-units/checklists/checklist-demo.yaml",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["message"], "Implement todo-demo")
    self.assertIn("checklist-demo", data["rationale"])
    self.assertIn("commit unit target file staging", data["rationale"])

  def test_commit_unit_postcondition_reports_push_candidate(self):
    """commit-unit postcondition は clean/head/ahead/push 候補を定型出力する"""
    result = run_script(
      [
        "commit-unit",
        "postcondition",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertFalse(data["is_dirty"])
    self.assertRegex(data["head_commit"], r"^[0-9a-f]{40}$")
    self.assertIn("push_candidate", data)

  def test_commit_unit_clear_removes_runtime_marker(self):
    """commit-unit clear は commit 後に不要な runtime marker を削除する"""
    self._write_and_stage("docs/target.md", "target\n")
    freeze = self._freeze_commit_unit(["docs/target.md"])
    self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
    marker = (
      Path(self.tmpdir)
      / ".reviewcompass"
      / "runtime"
      / "work-units"
      / "commit-unit.json"
    )
    self.assertTrue(marker.exists())

    result = run_script(["commit-unit", "clear", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["status"], "cleared")
    self.assertFalse(marker.exists())


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


def _write_completed_post_write_manifest(tmpdir, target_files, target_sha256=None):
  """対象ファイルを覆う完了 post-write manifest を書く"""
  if target_sha256 is None:
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

  def test_repair_workflow_state_prepare_allows_post_write_exception_preflight(self):
    """利用者承認済み repair record があれば post-write pending の stage 準備へ進める"""
    target = Path(self.tmpdir) / "docs" / "operations" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("運用正本\n", encoding="utf-8")
    tool = Path(self.tmpdir) / "tools" / "helper.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("print('repair')\n", encoding="utf-8")

    prepare = run_script(
      [
        "repair-workflow-state",
        "prepare",
        "--reason", "旧 guidance 二重管理解消の手動修復例外",
        "--source-ref", "conversation:user:manual-repair-exception",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, prepare)
    self.assertEqual(prepare.returncode, 0, prepare.stdout)

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertTrue(data["allowed_to_stage"])
    self.assertTrue(data["allowed_to_prepare_approval"])
    self.assertEqual(data["next_required_action"], "prepare_repair_commit")
    self.assertEqual(data["current_state"]["repair_workflow_state"]["valid"], True)

  def test_repair_workflow_state_record_allows_matching_commit(self):
    """repair record と staged 内容が一致すれば post-write 未完了を例外消費する"""
    target = Path(self.tmpdir) / "docs" / "operations" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("運用正本\n", encoding="utf-8")
    tool = Path(self.tmpdir) / "tools" / "helper.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("print('repair')\n", encoding="utf-8")

    prepare = run_script(
      [
        "repair-workflow-state",
        "prepare",
        "--reason", "旧 guidance 二重管理解消の手動修復例外",
        "--source-ref", "conversation:user:manual-repair-exception",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, prepare)
    self.assertEqual(prepare.returncode, 0, prepare.stdout)
    subprocess.run(
      ["git", "add", "docs/operations/policy.md", "tools/helper.py"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_commit_approval(
      self.tmpdir,
      ["docs/operations/policy.md", "tools/helper.py"],
    )

    result = run_script(
      [
        "commit",
        "--rationale", "利用者が手動修復例外として commit を承認",
        "--json",
      ],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["current_state"]["repair_workflow_state"]["valid"], True)
    self.assertEqual(data["current_state"]["post_write_verification"]["manifest_status"], "repair_exception")

  def test_repair_workflow_state_record_rejects_changed_scope(self):
    """repair record 後に差分が増えたら stage 準備を許可しない"""
    target = Path(self.tmpdir) / "docs" / "operations" / "policy.md"
    target.parent.mkdir(parents=True)
    target.write_text("運用正本\n", encoding="utf-8")
    prepare = run_script(
      [
        "repair-workflow-state",
        "prepare",
        "--reason", "旧 guidance 二重管理解消の手動修復例外",
        "--source-ref", "conversation:user:manual-repair-exception",
        "--json",
      ],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, prepare)
    self.assertEqual(prepare.returncode, 0, prepare.stdout)
    Path(self.tmpdir, "docs", "operations", "extra.md").write_text(
      "追加差分\n",
      encoding="utf-8",
    )

    result = run_script(["commit-preflight", "--json"], cwd=self.tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stdout)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertFalse(data["allowed_to_stage"])
    self.assertEqual(data["current_state"]["repair_workflow_state"]["valid"], False)

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
      ".reviewcompass/guidance/WORKFLOW_PRECHECK.md",
      "# WORKFLOW_PRECHECK",
    )
    _write_completed_post_write_manifest(
      self.tmpdir,
      [".reviewcompass/guidance/WORKFLOW_PRECHECK.md"],
    )
    _write_commit_approval(self.tmpdir, [".reviewcompass/guidance/WORKFLOW_PRECHECK.md"])
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

  def test_commit_skips_document_link_lint_for_deleted_staged_markdown(self):
    """削除された staged Markdown は文書リンク lint の読み取り対象にしない"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    source_path = "docs/operations/delete-me.md"
    _stage_file(
      self.tmpdir,
      source_path,
      "# Delete Me\n\n[missing](missing.md#anchor)\n",
    )
    subprocess.run(
      ["git", "commit", "-m", "seed delete target"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "rm", source_path],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_completed_post_write_manifest(
      self.tmpdir,
      [source_path],
      target_sha256={source_path: "DELETED"},
    )
    _write_commit_approval(
      self.tmpdir,
      [source_path],
      target_sha256={source_path: "DELETED"},
    )

    result = run_script(
      ["commit", "--rationale", "削除文書の commit gate テスト"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

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

  def test_push_ignores_deleted_deployment_lint_target(self):
    """push 時の配置非依存 lint は削除済み対象ファイルを読もうとしない"""
    relpath = "docs/operations/legacy.md"
    _stage_file(
      self.tmpdir,
      relpath,
      "旧配置の文書\n",
    )
    subprocess.run(
      ["git", "commit", "-qm", "add legacy guidance"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "rm", "-q", relpath],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    subprocess.run(
      ["git", "commit", "-qm", "remove legacy guidance"],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )
    _write_last_commit_precheck(self.tmpdir)

    result = run_script(
      ["push", "--rationale", "削除済み lint 対象 push のテスト", "--json"],
      cwd=self.tmpdir,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)
    data = json.loads(result.stdout)
    targets = data["current_state"]["deployment_independence_lint"]["target_files"]
    self.assertNotIn(relpath, targets)

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


## .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml

# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
default_prompt_length_bounds:
  min_chars: 400
  max_chars: 20000
  failure_verdict: WARN
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_stop_point
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#feature_definition_required
        - .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: parent_resume_pending
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: blocking_unit_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_required
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: blocking_unit_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_mixing_risk
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_mixing_risk
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_unit_stale
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_unit_stale
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
    - id: post_write_human_decision_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - .reviewcompass/guidance/discipline_post_write_verification.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 1200
        max_chars: 60000
        failure_verdict: DEVIATION
    - id: review-wave
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 400
        max_chars: 12000
        failure_verdict: DEVIATION
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#commit
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#push
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#audit-commit
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - .reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: user_initiated_plan_to_todo_bridge
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/todos/todo-2026-06-23-plan-to-todo-checklist-evidence.yaml
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
        - .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md
    - id: user_initiated_backlog_todo_execution
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
        - .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md
    - id: user_initiated_task_quality_gate
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-task-quality-gate.prompt.md
    - id: user_initiated_task_quality_review_materials
      prompt_source_refs:
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-task-quality-review-materials.prompt.md
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - .reviewcompass/guidance/discipline_post_write_verification.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - .reviewcompass/guidance/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - .reviewcompass/guidance/discipline_yaml_audit.md
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  post_write_verification:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
    - .reviewcompass/guidance/discipline_post_write_verification.md
  lightweight_self_check:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#lightweight_self_check
  parent_resume_pending:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending
  blocking_unit_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_required
  blocking_unit_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_in_progress
  commit_mixing_risk:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_mixing_risk
  commit_unit_stale:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_unit_stale
  post_write_policy_violation:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - .reviewcompass/guidance/discipline_post_write_verification.md
  post_write_human_decision_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - .reviewcompass/guidance/discipline_post_write_verification.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  reopen_in_progress:
    - .reviewcompass/guidance/REOPEN_PROCEDURE.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  maintenance_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#feature_definition_required
    - .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - .reviewcompass/guidance/REOPEN_PROCEDURE.md
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  triad-review:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
    - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  review-wave:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  approval:
    - .reviewcompass/guidance/discipline_approval_operation.md
    - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
    - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt


## .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md

# Effective Prompt: User-Initiated Plan To TODO Bridge

## Decision Point
- group: operation_prompt
- id: user_initiated_plan_to_todo_bridge

## Purpose
ユーザが backlog plan または plan 内の一部作業を実行しようとしたときに読む。plan を実行単位へ変換する直前で、plan から直接実作業に入らず、backlog TODO、runtime checklist、coverage / quality audit、必要時の review materials へ接続する。

## Trigger Boundary
- ユーザが「次へ」「進める」「この plan を進める」など、plan 由来の実作業開始を指示した。
- `next --json` が completed で、次作業を backlog plan から選ぶ状態になった。
- plan の `implementation_plan`、`acceptance_criteria`、remaining work を読んで実装、整理、移行、監査へ入ろうとしている。
- plan の一部 phase / task だけを実行しようとしている。

plan を読むだけ、説明するだけ、優先順位を相談するだけの場合は、この bridge を開始しない。

## Required Inputs
- 対象 plan id または plan path。
- `.reviewcompass/backlog/index.yaml`
- 対象 plan 本文。
- 対応する既存 backlog TODO の有無。
- `operation-prompt --trigger-text <text> --json` から入った場合は `trigger_resolution`。
- `work-backlog plan-todo-bridge --plan-id <plan-id> --json` の出力。
- 現在の work unit stack。

## Trigger Resolution Evidence
- `trigger_resolution.trigger_kind` が `short_continuation` の場合、短い「次へ」「進める」「継続」から bridge に入ったことを示す。
- `trigger_resolution.reason` が `unmaterialized_plan_slice` の場合、未展開 plan slice が bridge 選択理由である。
- `trigger_resolution.reason` が `multiple_unmaterialized_plan_candidates` の場合、複数 plan 候補があるため、`candidate_plan_ids` を利用者に示し、対象 plan を明示してから進む。
- `trigger_resolution.candidate_plan_ids` は候補 plan の一覧であり、TODO 化する plan を一意に決めるための証跡である。
- `trigger_resolution.requested_plan_id` がある場合は、その plan に絞って解決されたことを確認する。

## Artifact Boundaries
- plan は方針、分解案、受け入れ条件、残作業を保持する。実行対象そのものではなく、どこを TODO 化するかを判断する上流材料である。
- TODO は実行対象化した最小の追跡単位である。1 つの TODO は、同じ目的、同じ完了条件、同じ検証単位で閉じる範囲だけを扱う。
- runtime checklist は実行中の進捗証跡である。TODO の task / implementation_plan / todos / red_tests から生成し、作業中の active / pending / done を保持する。
- evidence checklist は完了後の固定証跡である。runtime checklist を後から作業中だったかのように補う場所ではなく、完了時点の checklist と検証結果を残す。
- TODO の execution_history は、完了した checklist_id、evidence_path、completion_summary を TODO 正本へ戻す索引である。

## TODO Conversion Rules
- 同時に完了判定できる範囲だけを 1 TODO にする。複数の独立した成果物、検証、判断待ちを含む場合は TODO を分ける。
- plan の一部だけを実行する場合、TODO には source_plan_id または source_plan_path と、対象 phase / task / acceptance_criteria / red_tests の対応を記録する。
- acceptance_criteria は TODO の完了条件へ落とす。受け入れ条件に対応しない checklist item だけで実作業へ進まない。
- red_tests は実装前の確認項目として TODO または checklist に残す。赤テストが不要な文書作業では lightweight self-check の理由を明示する。
- 既存 TODO がある場合は、対象範囲、完了条件、検証単位が plan の実行範囲を覆るかを確認してから再利用する。
- 対応が曖昧な場合は TODO を新規作成または分割し、曖昧なまま既存 TODO に押し込まない。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `work-backlog plan-todo-bridge --plan-id <plan-id> --json` を実行し、`materialization.summary`、`materialization.slices`、`materialization.next_candidates` を確認する。
3. 未展開 slice がある場合、`materialization.next_candidates` から今回扱う phase を選び、plan 全体完了と一部完了を区別して利用者に示す。
4. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
5. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
6. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
7. 状態変更の直前確認を済ませた場合だけ、`work-backlog start-checklist --id <todo-id> --mutation-boundary-confirmed` で runtime checklist を生成する。
8. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
9. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
10. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
11. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
12. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
13. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

## High-Risk Signals
- plan から複数の独立作業を切り出す必要がある。
- TODO の粒度や順序に迷いがある。
- `task-quality-check audit` が WARN を返した。
- red test の位置づけ、レビュー要否、または実行順序に判断が必要である。
- plan と既存 TODO/checklist の対応が曖昧である。

## LLM Scope
- ユーザの自然言語指示がどの plan 範囲に対応するかを読む。
- 既存 TODO が plan の対象範囲を十分に覆うかを説明する。
- WARN または高リスクの理由を利用者に平易に説明する。
- review materials を作る場合、送信前に認証情報、個人情報、不要な全文ログ、外部送信不可情報が含まれないか確認する。

## Prohibitions
- TODO/checklist がないまま plan から実作業へ進まない。
- `work-backlog plan-todo-bridge` の materialization status を確認せずに、短い「次へ」「進める」から実装へ進まない。
- plan 本文を読まずに path-only で TODO 化しない。
- plan の広い範囲を 1 つの曖昧な TODO に押し込まない。
- 3者レビューを常に必須化しない。
- WARN または高リスクを無視して実作業へ進まない。

## Stop Conditions
- 対象 plan または実行範囲が一意に定まらない。
- 対応 TODO が複数あり、どれを使うべきか判断できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
- WARN または高リスクについて、review materials 作成または明示判断が未了。


## .reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md

# Effective Prompt: User-Initiated Backlog TODO Execution

## Decision Point
- group: operation_prompt
- id: user_initiated_backlog_todo_execution

## Purpose
ユーザが backlog TODO の実行を指示したときに読む。主 workflow の `next --json` から直接開始されない補助処理でも、対象 TODO、runtime checklist、blocking unit、quality gate の接続を固定する。

## Required Inputs
- ユーザが明示した backlog TODO id、または status: promoted の単一 TODO。
- `.reviewcompass/backlog/index.yaml`
- 対象 backlog TODO 本文。
- 対象 TODO から生成または選択した runtime checklist。
- 現在の work unit stack。

## Mechanical Steps
1. `work-unit preflight-start` で active unit と resume pending を確認する。
2. 対象 TODO が未指定の場合、status: promoted の TODO が単一かを確認する。
3. 複数 promoted TODO がある場合は停止し、ユーザに対象 TODO id を確認する。
4. `work-backlog show --id <todo-id> --json` で対象 TODO 本文を読む。
5. 必要なら `work-unit enter-blocking` で blocking unit を開始する。
6. 状態変更の直前確認を済ませた場合だけ、`work-backlog start-checklist --id <todo-id> --mutation-boundary-confirmed` で runtime checklist を作成する。
7. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
8. coverage が DEVIATION の場合は実装へ進まず、TODO/checklist の修正に戻る。
9. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
10. quality が DEVIATION の場合は実装へ進まず、TODO/checklist の修正に戻る。
11. coverage / quality が OK の場合だけ checklist item を active にして作業を進める。

## LLM Scope
- ユーザの自然言語指示がどの TODO に対応するかを読む。
- 複数候補がある場合、勝手に選ばず停止する。
- warning の意味を説明する。

## Prohibitions
- TODO 本文を読まずに path-only で進めない。
- checklist item を LLM 要約だけで作らない。
- `work-backlog audit-checklist-coverage` と `task-quality-check audit` の前に checklist item を active にしない。
- 複数判断を 1 回の API review prompt に詰め込まない。
- blocking unit の出入りを暗黙にしない。

## Stop Conditions
- 対象 TODO が一意に定まらない。
- active unit と新規作業の関係が説明できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。


## tests/tools/test_effective_prompt_contract.py

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _read(path):
  return (ROOT / path).read_text(encoding="utf-8")


def _yaml(path):
  return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _decision_point(group_name, point_id):
  data = _yaml(".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml")
  for item in data["decision_points"][group_name]:
    if item["id"] == point_id:
      return item
  raise AssertionError(f"missing decision point: {group_name}:{point_id}")


def test_workflow_navigation_defines_one_effective_prompt_per_decision_point():
  text = _read(".reviewcompass/guidance/WORKFLOW_NAVIGATION.md")

  assert "判定点ごとに 1 本の effective prompt" in text
  assert "prompt_source_refs" in text
  assert "effective_prompt_path" in text
  assert "effective_prompt_sha256" in text
  assert "effective_prompt_loaded" in text
  assert "複数の元資料" in text
  assert "巨大な共通プロンプト" in text


def test_conformance_reopen_handoff_uses_effective_next_task_prompt():
  for path in [
    ".reviewcompass/specs/conformance-evaluation/requirements.md",
    ".reviewcompass/specs/conformance-evaluation/design.md",
    ".reviewcompass/specs/conformance-evaluation/tasks.md",
  ]:
    text = _read(path)

    assert "next_task_prompt_refs" in text
    assert "effective_next_task_prompt_path" in text
    assert "effective_next_task_prompt_sha256" in text
    assert "effective_next_task_prompt_loaded" in text
    assert "判定点ごとに 1 本" in text


def test_workflow_management_tracks_decision_prompt_map_as_canonical_artifact():
  for path in [
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/specs/workflow-management/tasks.md",
  ]:
    text = _read(path)

    assert "WORKFLOW_DISCIPLINE_MAP.yaml" in text
    assert "判定点" in text
    assert "required_disciplines" in text
    assert "required_inputs" in text
    assert "effective prompt" in text


def test_workflow_management_documents_effective_prompt_runtime_records():
  for path in [
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/specs/workflow-management/tasks.md",
  ]:
    text = _read(path)

    assert "effective_prompt_path" in text
    assert "effective_prompt_sha256" in text
    assert "effective_prompt_loaded" in text
    assert "rounds.yaml" in text


def test_workflow_discipline_map_catalogs_all_current_decision_points():
  data = _yaml(".reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml")
  catalog = data["decision_points"]

  expected = {
    "next_action_kind": {
      "stage",
      "cross_feature_stage",
      "upstream_recheck",
      "reopen_classification_required",
      "completed",
      "unknown",
      "feature_definition_required",
      "post_write_verification",
      "post_write_policy_violation",
      "post_write_human_decision_required",
      "reopen_in_progress",
      "maintenance_in_progress",
      "resume_in_progress",
      "parent_resume_pending",
      "blocking_unit_required",
      "blocking_unit_in_progress",
      "commit_mixing_risk",
      "commit_unit_stale",
      "reopen_started",
      "reopen_start_failed",
      "commit_stop_point",
      "lightweight_self_check",
    },
    "workflow_stage": {
      "candidate-proposal",
      "review",
      "drafting",
      "triad-review",
      "review-wave",
      "alignment",
      "approval",
    },
    "precheck_subcommand": {
      "spec-set",
      "commit",
      "push",
      "autonomous-plan",
      "autonomous-plan-template",
      "autonomous-plan-record-integration",
      "autonomous-ledger-audit",
      "audit-commit",
      "next",
      "reopen-start",
    },
    "reopen_required_action": {
      "classify_and_rollback_flags",
      "repair_canonical_documents",
      "rerun_alignment_approval_chain",
      "run_reopen_pending_gate",
      "run_reopen_drafting",
      "wait_for_human_approval",
      "finalize_reopen",
      "reopen_completed",
      "inspect_reopen_state",
    },
    "review_run_triage_command": {
      "list-pending",
      "decide",
      "manifest-template",
      "write-manifest",
      "assert-apply-fixes-ready",
      "assert-review-report-ready",
      "generate-review-report",
    },
    "post_write_manifest_gate": {
      "post_write_manifest_completed",
      "post_write_manifest_human_required",
      "post_write_manifest_missing_or_invalid",
      "post_write_policy_violation",
    },
    "proxy_model_decision_gate": {
      "user_visible_triage_gate",
      "proxy_decision_prompt",
      "proxy_decision_file",
      "proxy_approval_record",
    },
    "conformance_evaluation_gate": {
      "mv6_prompt_isolation",
      "reopen_handoff_package",
    },
    "yaml_audit_gate": {
      "yaml_audit_scope",
      "yaml_audit_post_write_check",
    },
    "operation_prompt": {
      "commit",
      "user_initiated_plan_to_todo_bridge",
      "user_initiated_backlog_todo_execution",
      "user_initiated_task_quality_gate",
      "user_initiated_task_quality_review_materials",
    },
  }

  assert set(catalog) == set(expected)
  for group_name, expected_ids in expected.items():
    actual = {item["id"] for item in catalog[group_name]}
    assert actual == expected_ids
    for item in catalog[group_name]:
      assert item["effective_prompt_policy"] == "one_effective_prompt_per_decision_point"
      assert item["prompt_source_refs"]


def test_post_write_policy_violation_uses_canonical_effective_prompt_artifact():
  item = _decision_point("next_action_kind", "post_write_policy_violation")

  assert item["canonical_effective_prompt_path"] == (
    ".reviewcompass/guidance/effective-prompts/"
    "next-action-post-write-policy-violation.prompt.md"
  )


def test_post_write_policy_violation_canonical_prompt_contains_operation_boundary():
  item = _decision_point("next_action_kind", "post_write_policy_violation")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "post_write_policy_violation.inspect" in text
  assert "run_post_write_review" in text
  assert "create_post_write_manifest" in text
  assert "next_action.kind == post_write_verification" in text


def test_user_initiated_backlog_execution_uses_canonical_effective_prompt_artifact():
  item = _decision_point("operation_prompt", "user_initiated_backlog_todo_execution")

  assert item["canonical_effective_prompt_path"] == (
    ".reviewcompass/guidance/effective-prompts/"
    "user-initiated-backlog-todo-execution.prompt.md"
  )


def test_user_initiated_plan_to_todo_bridge_uses_canonical_effective_prompt_artifact():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")

  assert item["canonical_effective_prompt_path"] == (
    ".reviewcompass/guidance/effective-prompts/"
    "user-initiated-plan-to-todo-bridge.prompt.md"
  )


def test_user_initiated_plan_to_todo_bridge_prompt_contains_trigger_boundary():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "plan を実行単位へ変換する直前" in text
  assert "work-backlog add-todo" in text
  assert "work-backlog start-checklist" in text
  assert "task-quality-check prepare-review-materials" in text
  assert "WARN または高リスク" in text
  assert "TODO/checklist がないまま plan から実作業へ進まない" in text


def test_user_initiated_plan_to_todo_bridge_prompt_defines_artifact_boundaries():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "## Artifact Boundaries" in text
  assert "plan は方針、分解案、受け入れ条件、残作業を保持する" in text
  assert "TODO は実行対象化した最小の追跡単位" in text
  assert "runtime checklist は実行中の進捗証跡" in text
  assert "evidence checklist は完了後の固定証跡" in text


def test_user_initiated_plan_to_todo_bridge_prompt_defines_todo_conversion_rules():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "## TODO Conversion Rules" in text
  assert "同時に完了判定できる範囲だけを 1 TODO にする" in text
  assert "source_plan_id または source_plan_path" in text
  assert "acceptance_criteria" in text
  assert "red_tests" in text


def test_user_initiated_plan_to_todo_bridge_prompt_requires_materialization_review():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "work-backlog plan-todo-bridge --plan-id" in text
  assert "materialization.summary" in text
  assert "materialization.next_candidates" in text
  assert text.index("work-backlog plan-todo-bridge --plan-id") < text.index("work-backlog add-todo")


def test_user_initiated_plan_to_todo_bridge_prompt_names_trigger_resolution_evidence():
  item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "trigger_resolution" in text
  assert "trigger_kind" in text
  assert "candidate_plan_ids" in text
  assert "multiple_unmaterialized_plan_candidates" in text


def test_user_initiated_backlog_execution_prompt_contains_mechanical_boundary():
  item = _decision_point("operation_prompt", "user_initiated_backlog_todo_execution")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert "work-backlog start-checklist" in text
  assert "work-backlog audit-checklist-coverage" in text
  assert "task-quality-check audit" in text
  assert "複数 promoted TODO" in text


def test_user_initiated_backlog_execution_prompt_requires_quality_before_work():
  item = _decision_point("operation_prompt", "user_initiated_backlog_todo_execution")
  prompt_path = ROOT / item["canonical_effective_prompt_path"]

  text = prompt_path.read_text(encoding="utf-8")

  assert text.index("work-backlog audit-checklist-coverage") < text.index("checklist item を active")
  assert text.index("task-quality-check audit") < text.index("checklist item を active")
  assert "coverage / quality が OK" in text


def test_user_initiated_prompt_map_references_materialization_bridge_plan():
  plan_item = _decision_point("operation_prompt", "user_initiated_plan_to_todo_bridge")
  todo_item = _decision_point("operation_prompt", "user_initiated_backlog_todo_execution")

  for item in [plan_item, todo_item]:
    assert (
      ".reviewcompass/backlog/plans/"
      "plan-2026-06-23-plan-todo-checklist-materialization.yaml"
    ) in item["prompt_source_refs"]


def test_api_review_prompt_quality_requires_behavior_path_materials():
  text = _read(".reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md")

  assert "behavior-path claim" in text
  assert "実行経路 claim" in text
  assert "trigger resolver" in text
  assert "operation preflight" in text
  assert "変更文書だけを target/source にしてはならない" in text


def test_api_review_prompt_quality_requires_review_question_decomposition():
  text = _read(".reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md")

  assert "review question decomposition" in text
  assert "整合性確認だけの一括質問にしない" in text
  assert "要求 claim ごとの required check" in text
  assert "ショートリクエストが bridge を bypass しない" in text


def test_api_review_prompt_quality_rejects_unexplained_single_model_zero_findings():
  text = _read(".reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md")

  assert "single-model findings: []" in text
  assert "根拠説明なしの 0 件" in text
  assert "高リスクまたは実行経路 claim" in text
  assert "3-way" in text


def test_llm_as_judge_prompting_requires_main_preanalysis_before_prompt():
  text = _read(".reviewcompass/guidance/discipline_llm_as_judge_prompting.md")

  assert "main preanalysis" in text
  assert "behavior-path claim" in text
  assert "target / source / out of scope" in text
  assert "変更された成果物だけ" in text


## .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md

# API Review Prompt Quality

最終更新：2026-06-23

本文書は、API 経由の review-run を開始する前に、レビュー用プロンプト自体を品質確認するための運用手順である。

この手順は、特定 feature や特定 phase に閉じない。各 review-run は、この共通手順に phase / gate / feature 固有の上流接続要件を差し込んで使う。

利用者が任意の場面で API review を依頼する場合は、利用者が伝えたレビュー要件を `User Review Requirements` として保持し、criteria 作成・prompt quality review・実 review-run の全段で照合する。

## 1. 目的

API review-run の品質は、モデルや provider だけでなく、プロンプトの作り方に強く依存する。

レビュー用プロンプトの監査は、高リスク時だけの追加確認ではなく、API review-run の標準ゲートである。プロンプトが target / source / scope / output contract を誤ると、その後の raw response、parsed YAML、triage、proxy decision、実装修正がすべて誤った入力に基づく。したがって、prompt audit にかかるコストはレビュー外の余分なコストではなく、レビュー品質を成立させるための本体コストとして扱う。

特に、次の失敗を防ぐ。

- `--target` が実際の審査対象本文ではなく、作成者の要約になっている
- `--criteria-file` と `--target` が同一の author-written summary になっている
- source materials が path-only で、モデルが本文を読めない
- review target / source materials / out of scope が分離されていない
- 上流意図伝達レビューで、上流の目的・責務境界・受入条件・禁止事項が prompt に含まれていない
- 利用者が指定したレビュー目的、重視点、範囲、禁止事項が main によって狭められる、広げられる、または別の問いに置き換えられる
- output contract が曖昧で parser / triage に載らない
- プロンプトが結論を誘導している

## 2. 役割

APIレビュー用プロンプト品質確認は、次の 2 者レビュー体制で行う。

| 役割 | 担当 | 目的 |
|---|---|---|
| main | 操縦中の LLM | API review criteria 素案を作る |
| adversarial | 別モデル | 素案の欠落、誘導、対象違い、材料不足、範囲ミスを探す |
| judgment | 別モデル | adversarial 所見の反映後、その prompt を実 review-run に使ってよいか判定する |

ここでいう 2 者レビュー体制は、作成者である main を除き、adversarial と judgment の 2 者で品質確認する運用を指す。

## 3. 入力分離

API review-run では、criteria と target を分離する。

- `User Review Requirements`: 利用者が指定したレビュー目的、判断対象、重視点、範囲、禁止事項、必要出力
- `--criteria-file`: レビュー目的、背景、上流材料、必須チェック、範囲外、finding policy を含む
- `--target`: 実際に審査する本文

`User Review Requirements` は criteria の上位入力であり、criteria 作成時に失われてはならない。main は、利用者要件を criteria に構造化して写し、どの要件がどの review task / required check / out of scope / finding policy に対応するかを確認できる形にする。

禁止:

- criteria と target に同じ review wrapper / author-written summary を渡す
- target manifest が実審査対象を含まない状態で gate 完了根拠にする
- target 本文を入れず、target の要約だけで review-run を実行する
- 利用者が求めたレビュー範囲を、合意なく狭める、広げる、または別目的の review に置き換える

## 4. User Review Requirements

利用者が任意の場面で review を依頼する場合、main は prompt 作成前に次を整理する。

1. review purpose: 欠陥検出、採否判断、上流接続確認、回帰確認、比較評価など
2. review object: artifact、prompt、設計案、修正案、実装差分など
3. review focus: API設計、互換性、セキュリティ、運用境界、上流要件、実装可能性など
4. scope boundaries: 含める範囲、含めない範囲、まだ判断しない下流工程
5. source materials: 根拠にする要件、設計、過去判断、制約、禁止事項
6. output requirements: findings、severity、採否、懸念点、修正案、比較軸など
7. prohibited actions: commit、push、phase 完了、人間承認代行、未合意の仕様変更など

利用者要件が曖昧な場合でも、main が勝手に確定しない。作業可能な仮定として扱う場合は、criteria に仮定を明記し、prompt quality review で妥当性を確認させる。

## 5. API 送信可能材料の基準

API review-run / proxy_model 判断では、判断に必要な ReviewCompass リポジトリ内の仕様、設計、タスク、レビュー所見、構造化要約、証跡パスを prompt に含めてよい。

これは、次の条件を満たす場合に限る。

1. 利用者が当該 API review-run / proxy_model 判断の実行を明示承認している。
2. API key、token、password、nonce などの秘密値を含めない。
3. メールアドレス、電話番号など個人識別情報を含めない。
4. 第三者との契約上、外部送信できない非公開情報を含めない。
5. 判断に不要な全文ログや周辺ファイルを含めず、判断項目に必要な抜粋または構造化要約に絞る。

単にリポジトリ内の未公開仕様・設計・レビュー要約であることだけを理由に、API 送信を禁止しない。ReviewCompass の API review / proxy_model 運用では、それらは通常のレビュー材料である。

ただし、利用者が外部送信を避ける方針を示した場合、または上記 2〜4 に該当する情報が含まれる場合は、伏字化、抽象化、または外部 API を使わない判断へ切り替える。

## 6. Main が作る criteria の必須要素

criteria file は、少なくとも次を持つ。

1. review task
2. why this review exists
3. user review requirements
4. required disciplines
5. review target
6. source materials
7. required checks
8. out of scope
9. finding policy

source materials は path-only にしない。必要な本文抜粋または構造化要約を、モデルが読める形で criteria に含める。

front matter に path を置く場合は、provenance なのか model-readable material なのかを明示する。

criteria は、利用者要件を単に引用するだけでなく、review task / required checks / out of scope / finding policy へ反映する。

## 6.1 Main Preanalysis

main は criteria 素案を書く前に、対象 review requirement と source materials を直接検討し、判断に必要な材料、判断項目、分割要否、未読資料、機微情報リスクを整理する。

main preanalysis は、prompt 作成のための材料揃えと判断点発見であり、reviewer に対する正解ではない。preanalysis を後続の監査や prompt に含める場合は、仮説・source discovery aid として明示し、reviewer に source materials から独立再構成させる。

main preanalysis には少なくとも次を含める。

- 読んだ source materials と使用目的
- 判断項目と、それぞれの target / source / out of scope
- 複数 prompt に分割すべき独立判断の有無
- prompt に含めるべき model-readable source material
- 送信してはいけない、または最小化すべき機微情報
- 未解決・未読・推測に留まる事項

preanalysis 内の所見は、`open`、`resolved`、`superseded`、`used_for_context` など現在性を区別できる形で扱う。解決済み所見を open な欠陥として prompt bundle に残すと、reviewer を誤誘導するためである。

### 6.2 Behavior-Path Claim の材料選定

review requirement が「あるトリガーから、意図した機械手順へ進むか」「短い利用者指示が gate を bypass しないか」「特定の guard が必ず作動するか」のような behavior-path claim / 実行経路 claim を含む場合、main preanalysis は変更文書だけを target/source にしてはならない。

この場合、source materials には少なくとも次を含める。

- trigger resolver または利用者発話を operation に写像する map
- operation preflight、guard、gate、runner など実行経路上の制御実装
- その経路を固定するテスト、または存在しない場合は「未固定」と分かる証跡
- 変更対象文書、effective prompt、plan / TODO / checklist など経路上の入力成果物
- 期待される停止点、禁止 bypass、許可される次操作

対象が「文書の整合性」ではなく「動作上の強制」なら、変更された guidance / prompt だけを target にした review-run は不足である。文書に要件が書かれていても、trigger resolver、operation preflight、runner、test がその要件を読んでいなければ behavior-path claim は成立しない。

### 6.3 Review Question Decomposition

main は criteria 作成前に review question decomposition を行う。整合性確認だけの一括質問にしない。

分解では、利用者要件または workflow 要件を要求 claim ごとの required check に写す。各 required check は、次を明示する。

1. 何を成立させる claim か
2. どの target / source material で判定するか
3. finding にすべき失敗条件は何か
4. out of scope は何か

例: 「ショートリクエストが bridge を bypass しない」を検証するなら、単に「prompt と map が整合しているか」と聞かない。`次へ`、`進める`、`継続` などの短い発話がどの trigger resolver / operation preflight / effective prompt に到達し、どこで plan materialization status、TODO/checklist coverage、quality audit を確認するかを required check に分解する。

review question が複数 claim を含む場合は、claim ごとに prompt を分けるか、少なくとも required checks を分離して reviewer が各 claim を個別に pass/fail できる形にする。

## 7. Phase 別の上流接続

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` が適用される review では、phase ごとに次を確認する。

| phase | target | source materials |
|---|---|---|
| requirements | `requirements.md` | upstream decision materials, reopen classification, planning notes, user decisions |
| design | `design.md` | `requirements.md` |
| tasks | `tasks.md` | `requirements.md`, `design.md` |
| implementation | implementation artifacts | `requirements.md`, `design.md`, `tasks.md` |

source materials は背景・意図伝達確認のために使う。現在 phase の correctness だけを target として判定し、下流 phase の correctness を同時に判定しない。

利用者が指定した review focus が phase 標準の観点と異なる場合は、両者の関係を criteria に明記する。phase 標準の必須検査を外す必要がある場合は、利用者合意なしに外してはならない。

## 8. Prompt Quality Review

main が criteria 素案を作ったら、実 review-run の前に preanalysis sufficiency audit と prompt quality review を行う。

標準手順は次の順序とする。

1. main preanalysis
2. preanalysis sufficiency audit
3. API review criteria draft
4. prompt quality review
5. 実 review-run
6. raw / parsed / model summary / triage
7. 必要に応じて proxy_model decision

通常の prompt quality review の前に、`templates/review/main_preanalysis_sufficiency_audit_criteria_template.md` を使って preanalysis sufficiency audit を行う。この監査では、reviewer に source materials から judgment item を独立再構成させたうえで、main preanalysis を仮説として比較させる。main preanalysis を正解として渡してはならない。

preanalysis sufficiency audit では、target bundle に次を含める。

- 利用者または workflow の review requirement
- 判断に必要な source materials の本文または構造化抜粋
- main session LLM の preanalysis
- proposed API review criteria または prompt

監査結果の `required_prompt_changes` を反映してから、通常の `templates/review/api_review_prompt_quality_criteria_template.md` による prompt quality review へ進む。

preanalysis sufficiency audit は、次の欠陥を検出するための標準ゲートである。

- source selection の漏れ
- source summary と原文対応の不足
- main preanalysis の stale / resolved 所見による anchoring
- 複数の独立判断を 1 prompt に押し込む粒度誤り
- 誤検出防止文言が、重要な欠陥検出まで抑制する framing bias
- output contract と runner / parser の不一致
- behavior-path claim に必要な trigger resolver / operation preflight / runner / test の欠落
- review question decomposition の不足による、整合性確認だけの一括質問化

review question は 1 prompt につき原則 1 つにする。複数の独立した採否判断、クラスタ判断、設計論点判断を 1 つの prompt に押し込まない。

複数判断がある場合は、判断項目ごとに prompt を分ける。各 prompt は、その判断に必要な source findings、上流材料、対象本文要約、out of scope、output contract だけを持つ。共通背景を入れる場合も、個別判断の焦点を曖昧にしない量に抑える。

adversarial には、`templates/review/api_review_prompt_quality_criteria_template.md` を criteria として渡し、criteria 素案を target としてレビューさせる。

利用者要件がある場合、prompt quality review では次も確認する。

- 利用者要件が criteria に保持されている
- 利用者要件が review task / required checks / out of scope / finding policy に反映されている
- main が利用者要件を合意なく狭めたり広げたりしていない
- 利用者が禁止した操作や判断代行が prompt に混入していない
- 複数の独立判断を 1 prompt に押し込んでおらず、判断項目ごとに注意が分散しない粒度になっている

adversarial の所見を main が反映した後、judgment に同じ quality criteria と adversarial 所見を渡し、使用可否を判定させる。

judgment が `findings: []` を返した場合だけ、実 review-run へ進める。

judgment が finding を返した場合は、prompt を再修正し、必要に応じて再度 judgment へ回す。

高リスクまたは実行経路 claim を含む review では、single-model findings: [] を単独の完了根拠にしない。根拠説明なしの 0 件、特に raw response が `findings: []` のみの場合は、対象材料と問いが狭すぎる可能性を疑い、次のいずれかを行う。

- 3-way の独立 review に切り替える
- reviewer に claim ごとの pass/fail rationale と参照 material を出力させる
- main preanalysis sufficiency audit へ戻り、source selection と review question decomposition をやり直す

## 9. 実 Review-Run

prompt quality review を通過した後、実 review-run を実行する。

複数 prompt に分けた場合は、各 prompt の prompt quality review 通過証跡と実 review-run / proxy decision 結果を判断項目ごとに保存する。一括 summary は後段で作ってよいが、個別判断の raw / parsed / decision 証跡を上書きしない。

実行時には次を確認する。

- `target-manifest.yaml` に実審査対象が入っている
- `rounds.yaml` の criteria は使用可判定済み criteria である
- raw / parsed / model-result-summary / triage が生成されている
- 利用者提示ゲート前に、raw 結果概要、モデル別 summary、同根クラスタ、三段階トリアージ案をまとめる
- 実 review-run の結果を、利用者要件に含まれていない操作承認や phase 完了根拠へ拡張しない

## 10. 成果物配置

推奨配置:

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-prompt-quality-run/
  api-review-criteria.md
  prompt-quality-review-criteria.md
  variant-role-assignment.yaml
  raw/
  parsed/
  prompts/
  rounds.yaml
  model-result-summary.yaml
  prompt-quality-summary.md
```

実 review-run は別ディレクトリに分ける。

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-review-run/
```

prompt-quality-run は、実 review-run の gate 完了根拠ではない。実 review-run の criteria を使ってよいことを示す補助証跡である。

## 11. 今回の事例から得た規則

2026-06-20 の `workflow-management` design triad-review では、旧 run が `review-target.md` を criteria と target の両方に使い、`findings: []` になった。

その後、prompt quality review を挟み、`design.md` を実 target として再実行した v2 run では 15 件の所見が出た。

同日の `workflow-management` implementation Req14 approval gate prompt audit では、preanalysis sufficiency audit により、source summary の原文対応不足と、誤検出防止文言が approval gate bypass 検出を鈍らせる framing bias が検出された。これは、prompt audit が形式確認ではなく、実 review-run の欠陥検出力そのものを左右することを示す。

2026-06-23 の plan-todo-checklist materialization PTC-4 post-write review では、prompt が「updated effective prompts and discipline map の整合性確認」に寄りすぎ、短い `次へ` / `進める` から plan-to-TODO bridge へ到達する実行経路を検証できなかった。target は guidance / effective prompt に寄り、trigger resolver、operation preflight、runner、経路テストを含めなかったため、single-model findings: [] が返っても behavior-path claim の完了根拠としては弱かった。

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む
- behavior-path claim では、変更文書だけでなく trigger resolver / operation preflight / runner / test を source materials に含める
- review question は要求 claim ごとの required check に分解し、整合性確認だけの一括質問にしない
- 高リスクまたは実行経路 claim では、根拠説明なしの single-model findings: [] を完了根拠にしない

## 12. 停止点

prompt quality review は、実 review-run の開始許可であり、次の操作を自動許可しない。

- `spec.json` 更新
- phase / gate 完了
- proxy_model 判断
- design / requirements / tasks / implementation 本文修正
- commit
- push

これらはそれぞれの workflow gate と利用者承認に従う。


## .reviewcompass/guidance/discipline_llm_as_judge_prompting.md

---
name: llm-as-judge-prompting
description: LLM as a Judge（AIモデルを審査者として活用する）シーンでのプロンプト作成ガイドライン
metadata:
  type: feedback
---

# LLM as a Judge：プロンプト作成ガイドライン

## このガイドラインを使う場面

人間が判断しにくい設計上の問いを、複数のAIモデルに独立して審査させるとき。
特に次のような状況で有効である。

- 選択肢の優劣を客観的に評価したいが、人間が当事者に近すぎて判断が難しい
- 設計の欠陥を「見落としなく」洗い出したい
- 修正案が問題を正しく解消しているかを第三者視点で確認したい

## プロンプト作成の手順

### ステップ1：メインのLLMに問題を直接検討させる（材料揃え）

プロンプトを書く前に、まず担当のLLM自身に問題にあたらせる。

ReviewCompass では、この事前検討を main preanalysis と呼ぶ。

目的は2つある。
1. 問題の理解に必要な情報（背景・前提・関連する設計）を特定する
2. 判断のポイント（何が分かれば答えが決まるか）を認識する

この段階で担当LLMが「この情報がないと判断できない」と気づいた内容は、プロンプトに含める情報として確定する。

main preanalysis では、少なくとも次を分けて整理する。

- 判断したい claim
- claim ごとの target / source / out of scope
- 必要な原文または構造化抜粋
- 未読資料、推測、機微情報リスク

特に、あるトリガーから特定の手順へ進むか、guard が bypass されないか、といった behavior-path claim を扱う場合は、変更された成果物だけを材料にしない。trigger resolver、operation preflight、runner、関連テスト、入力成果物を含め、実行経路を reviewer が追えるようにする。

### ステップ2：プロンプトを作成する

ステップ1で揃えた材料を使ってプロンプトを作成する。プロンプトには次の3つの要素が必要である。

**適切な情報：**
問題の背景・現状・関連する設計の記述を含める。
判断に必要な情報が欠けていると、モデルが推測で回答し、的外れな結果になる。

**適切な問い：**
「何を分析してほしいか」を問いとして明示する。
問いは独立した分析を促す形で書く。答えを誘導したり、特定の方向に引っ張ったりしない。

**適切な範囲：**
分析の対象を絞りすぎず、広げすぎず設定する。
広すぎると焦点が定まらない。狭すぎると問題の核心が見えなくなる。

プロンプトを作成したら、送信前に次の確認を行う。

**送信前の確認（機微な情報のチェック）：**
プロンプトを外部のモデルに送信する前に、次の情報が含まれていないか確認する。

- APIキー・アクセストークン・パスワードなどの認証情報
- メールアドレス・電話番号など個人を特定できる情報
- 第三者に公開してはいけないプロジェクト固有の機密情報

含まれている場合は、伏字や仮の値に置き換えてから送信する。

**ReviewCompass 内部資料の扱い：**
ReviewCompass の API review-run / proxy_model 判断では、判断に必要なリポジトリ内の仕様・設計・タスク・レビュー所見・要約・証跡パスを外部 API prompt に含めることがある。これらは、上記の認証情報・個人情報・第三者非公開機密を含まない限り、利用者が API review / proxy_model 判断の実行を明示承認した場合に送信可能なレビュー材料として扱う。

ただし、送信材料は判断に必要な最小範囲に絞る。秘密値、個人情報、契約上外部送信できない第三者情報、不要な全文ログは含めない。外部送信リスクが問題になる場合は、抽象化・伏字化・ローカル判断への切り替えを利用者へ提示する。

### ステップ3：モデルに審査させる

プロンプトをAIモデルに渡し、独立して審査させる。

**複数モデルでの審査（3者レビュー）を推奨：**
同じプロンプトを複数のAIモデルに渡す。モデルが一致して指摘した内容は信頼性が高い。
モデルによって見解が分かれた内容は、設計の曖昧さを示す手がかりになる。
3者が推奨だが、1者のみでも有効である。

**1者への審査（proxy_model）の場合：**
proxy_model（個別の所見の採否判断を別のモデルに委ねる運用）でも、ステップ1〜2の手順は同じである。
プロンプトの品質が採否判断の質に直結するため、材料揃え・問い設計・機微情報チェックを省略しない。

## 避けるべきこと

### 閉じた選択を強制しない

複数の案を比較評価させることは問題ない。問題なのは「AかBかCの中から選べ」という問いの設計である。この形にすると、モデルは「選択モード」になり、選択肢の外にある可能性（新たな案・前提の誤り・全案の否定）が出にくくなる。分析が浅くなる。

問題の状況と比較したい対象を説明し、モデルが枠を超えた分析をできるようにする。必要であれば「選択肢の枠を超えて考えてよい」と明示する。

### プロンプトを考えずに即時投げない

問題を整理する前にすぐAPIに渡すと、情報が不足してモデルが的外れな内容を回答する。担当LLMが問題を理解してから投げることで、回答の質が大きく変わる。

## 発展：複数ターンの活用

1回のレビューで答えが出なかった場合、前の回答を参照しながら2回目のレビューを実施できる。
前の回答で「深掘りすべき論点」が明らかになった場合は、その論点だけに絞った新しいプロンプトを作成する。

複数ターンの場合も、各ターンのプロンプトは「ステップ1〜3」の手順で作成する。
前のターンの回答をそのまま次のプロンプトに貼り付けるのではなく、担当LLMが整理した上で次の問いを設計する。


## .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml

schema_version: reviewcompass-backlog-item-v1
id: plan-2026-06-23-plan-todo-checklist-materialization
kind: plan
title: Mechanize plan TODO checklist materialization coverage
status: candidate
source_unit_id: main-side-conversation
created_at: '2026-06-23T11:37:06.836406+00:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: conversation:user:今は、plan > todo > checklistの動線はあるか
  reason: The existing plan-to-TODO-to-checklist parts exist, but plan-wide slice
    materialization coverage and unmaterialized-slice surfacing are weak; create a
    plan to mechanize the full bridge.
decisions: []
summary: 'backlog plan の各 slice が TODO / checklist / evidence に展開済みかを機械的に追跡し、

  未展開 slice を次の実行候補として可視化する。現状は plan-todo-bridge、

  start-checklist、coverage audit などの部品はあるが、plan 全体の展開完了性を

  強制・監査する制御が弱い。

  '
problem_statement:
- plan から一部 slice だけを TODO 化した場合、残り slice が未展開のまま見落とされやすい。
- linked TODO が 1 件あるだけでは、plan 全体が TODO/checklist 化済みか判断できない。
- execution_slices は手で追記できるが、plan-todo-bridge / audit がその状態を十分に利用していない。
- TODO/checklist/evidence の後追い接続はできるが、実作業前に plan slice から降りる強制力が弱い。
goals:
- plan 内の implementation_plan 各 slice について materialization status を機械的に表示する。
- 未展開 slice を次に TODO 化すべき候補として返す。
- plan → TODO → checklist → evidence の接続が一部完了か全体完了かを区別する。
- 実作業開始前に、対象 slice の TODO/checklist が存在しない場合は停止または明示判断にする。
non_goals:
- 既存 plan の全 slice をこの計画作成時に一括 TODO 化する。
- checklist 実行そのものを自動化する。
- 人の判断が必要な slice 分割や優先順位決定を完全自動化する。
implementation_plan:
- id: PTC-1
  title: Define plan slice materialization contract
  tasks:
  - id: PTC-1A
    title: Define execution_slices schema for plan items
  - id: PTC-1B
    title: Define statuses such as not_materialized, todo_created, checklist_started,
      evidence_recorded, completed
  - id: PTC-1C
    title: Define how source_plan_id, source_plan_slice, checklist_id, and evidence
      path link together
  acceptance:
  - plan の各 implementation_plan item と execution_slices が対応づけられる。
  - GRC-1 のような一部完了が plan 全体完了と区別できる。
- id: PTC-2
  title: Strengthen plan-todo-bridge output
  tasks:
  - id: PTC-2A
    title: Make plan-todo-bridge report every slice status, not only linked TODOs
  - id: PTC-2B
    title: Return next materialization candidates for not_materialized slices
  - id: PTC-2C
    title: Return recommended commands for add-todo and start-checklist without performing
      mutations
  acceptance:
  - plan-todo-bridge の JSON で GRC-2 以降の未展開 slice が明示される。
  - linked TODO がある slice とない slice が区別できる。
- id: PTC-3
  title: Add audit for full plan materialization coverage
  tasks:
  - id: PTC-3A
    title: Extend audit-plan-todo-bridge to detect missing execution_slices entries
  - id: PTC-3B
    title: Detect implementation_plan slice without TODO/checklist/evidence according
      to required phase
  - id: PTC-3C
    title: Decide when partial materialization is OK versus when it is a DEVIATION
  acceptance:
  - audit can report partial materialization without falsely treating the plan as
    complete.
  - high-risk execution cannot proceed from an unmaterialized slice without explicit
    decision.
- id: PTC-4
  title: Integrate with user-triggered execution prompts
  tasks:
  - id: PTC-4A
    title: Update user-initiated plan-to-todo bridge prompt to require materialization
      status review
  - id: PTC-4B
    title: Update backlog TODO execution prompt to verify checklist coverage before
      work starts
  - id: PTC-4C
    title: Add trigger operation entry references so short requests do not bypass
      the bridge
  acceptance:
  - A user request to continue a plan first surfaces unmaterialized slices.
  - The operator is guided to create TODO/checklist before implementation work.
- id: PTC-5
  title: Tests and regression fixtures
  tasks:
  - id: PTC-5A
    title: Add tests for a plan with one completed slice and remaining unmaterialized
      slices
  - id: PTC-5B
    title: Add tests that plan-todo-bridge returns next TODO candidates
  - id: PTC-5C
    title: Add tests that audit detects stale or missing execution_slices links
  acceptance:
  - The guidance relocation plan pattern is covered as a regression case.
red_tests:
- id: PTC-RT-1
  title: Partial plan materialization is visible
  expected: A plan with GRC-1 completed and GRC-2..GRC-6 not_materialized reports
    partial coverage, not plan completion.
- id: PTC-RT-2
  title: Next unmaterialized slice is recommended
  expected: plan-todo-bridge returns GRC-2 as a next materialization candidate when
    GRC-1 is completed.
- id: PTC-RT-3
  title: Work cannot silently start from an unmaterialized slice
  expected: Attempting to start implementation work for a slice without TODO/checklist
    returns a stop reason or explicit decision requirement.
- id: PTC-RT-4
  title: Stale links are detected
  expected: execution_slices entries pointing to missing TODO/checklist/evidence paths
    are reported by audit.
risks_and_mitigations:
- risk: execution_slices becomes another manually maintained field.
  mitigation: derive status from TODO/checklist/evidence where possible and use stored
    fields as links, not sole truth.
- risk: every plan slice being forced to TODO could create too much ceremony.
  mitigation: allow explicit deferred / not_required decisions with rationale, but
    make them visible.
- risk: bridge output mutates state unexpectedly.
  mitigation: keep plan-todo-bridge and audits read-only; mutations remain add-todo
    and start-checklist with explicit boundary confirmation.
recommended_next_step:
  id: PTC-5
  title: Tests and regression fixtures
execution_slices:
- phase_id: PTC-1
  title: Define plan slice materialization contract
  status: completed
  todo_id: todo-2026-06-23-plan-slice-materialization-contract
  todo_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-slice-materialization-contract.yaml
  checklist_id: checklist-todo-2026-06-23-plan-slice-materialization-contract
  checklist_evidence_path: null
  note: >
    Contract documented in .reviewcompass/guidance/WORKFLOW_PRECHECK.md#401-work-backlog-plan-materialization.
    Runtime checklist was generated and completed in the side conversation; no evidence copy has been recorded yet.
- phase_id: PTC-2
  title: Strengthen plan-todo-bridge output
  status: completed
  todo_id: todo-2026-06-23-plan-todo-bridge-output
  todo_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-todo-bridge-output.yaml
  checklist_id: checklist-todo-2026-06-23-plan-todo-bridge-output
  checklist_evidence_path: null
  note: >
    plan-todo-bridge now reports all implementation_plan slices, derived
    materialization status, next not_materialized candidates, and read-only
    recommended add-todo/start-checklist commands.
- phase_id: PTC-3
  title: Add audit for full plan materialization coverage
  status: completed
  todo_id: todo-2026-06-23-plan-materialization-audit
  todo_path: .reviewcompass/backlog/todos/todo-2026-06-23-plan-materialization-audit.yaml
  checklist_id: checklist-todo-2026-06-23-plan-materialization-audit
  checklist_evidence_path: null
  note: >
    audit-plan-todo-bridge now reports plan materialization coverage,
    missing execution_slices entries, and promoted/active plan deviations for
    not_materialized slices.
- phase_id: PTC-4
  title: Integrate with user-triggered execution prompts
  status: completed
  todo_id: todo-2026-06-23-user-triggered-materialization-prompts
  todo_path: .reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml
  checklist_id: checklist-todo-2026-06-23-user-triggered-materialization-prompts
  checklist_evidence_path: null
  note: >
    User-initiated plan and backlog TODO prompts now require materialization
    status, checklist coverage, and quality audit review before implementation
    work starts.
- phase_id: PTC-5
  title: Tests and regression fixtures
  status: not_materialized
  todo_id: null
  checklist_id: null
  note: TODO/checklist 未展開。


## .reviewcompass/backlog/todos/todo-2026-06-23-user-triggered-materialization-prompts.yaml

schema_version: reviewcompass-backlog-item-v1
id: todo-2026-06-23-user-triggered-materialization-prompts
kind: todo
title: Integrate user-triggered materialization prompts
status: completed
source_unit_id: main-side-conversation
created_at: '2026-06-23T12:18:06.849740+00:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml#PTC-4
  reason: PTC-4 is the next not_materialized slice returned by plan-todo-bridge; materialize
    it as a backlog TODO before prompt integration work
decisions:
- decision: completed
  decision_ref: .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md
  reason: Updated user-initiated plan and backlog TODO prompts plus operation prompt
    source references so short continuation requests surface materialization status
    and verify checklist coverage / quality before implementation work.
  decided_at: '2026-06-23T12:20:30.276062+00:00'
source_plan_id: plan-2026-06-23-plan-todo-checklist-materialization
source_plan_path: .reviewcompass/backlog/plans/plan-2026-06-23-plan-todo-checklist-materialization.yaml
source_plan_slice:
  phase_id: PTC-4
  title: Integrate with user-triggered execution prompts
summary: 'user-triggered execution prompts and trigger references must guide the operator
  through plan materialization status before implementation work starts.

  '
problem_statement:
- Short user requests such as "次へ" can bypass the plan-to-TODO-to-checklist bridge
  if the prompt does not require materialization review.
- The plan-to-TODO bridge prompt should surface unmaterialized slices before choosing
  implementation work.
- The backlog TODO execution prompt should verify checklist coverage before work starts.
- Trigger operation references should point short requests toward the bridge instead
  of direct implementation.
implementation_plan:
  phases:
  - id: PTC-4
    title: Integrate with user-triggered execution prompts
    tasks:
    - id: PTC-4A
      title: Update user-initiated plan-to-todo bridge prompt to require materialization
        status review
    - id: PTC-4B
      title: Update backlog TODO execution prompt to verify checklist coverage before
        work starts
    - id: PTC-4C
      title: Add trigger operation entry references so short requests do not bypass
        the bridge
acceptance_criteria:
- A user request to continue a plan first surfaces unmaterialized slices.
- The operator is guided to create TODO/checklist before implementation work.
- Prompt or trigger references point to plan-todo-bridge / audit materialization checks
  before mutation.
red_tests:
- id: PTC-4-RT-1
  title: Plan continuation prompt requires materialization status review
  expected: A prompt or guidance test confirms plan continuation tells the operator
    to inspect materialization status before work starts.
- id: PTC-4-RT-2
  title: Backlog TODO execution prompt requires checklist coverage before work
  expected: A prompt or guidance test confirms TODO execution checks checklist coverage
    before implementation.
- id: PTC-4-RT-3
  title: Short trigger references bridge instead of direct implementation
  expected: A trigger/guidance reference for short continuation requests points to
    the plan-to-TODO/checklist bridge.
non_goals:
- Implementing all PTC-5 regression fixtures.
- Automatically mutating plan slices from prompt text alone.

