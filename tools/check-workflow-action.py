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


# 既定のログファイルパス（呼び出し時の cwd 相対、仕様 §8.2）
DEFAULT_LOG_PATH = "docs/logs/workflow-precheck.log"
DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"
DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"
DEFAULT_DISCIPLINE_MAP_PATH = "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"
DEFAULT_CARRY_FORWARD_REGISTER_PATH = "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
DEFAULT_CARRY_FORWARD_SOURCE_PATH = (
  "learning/workflow/carry-forward-register/sources/"
  "reviewcompass-pending-cross-feature-findings.md"
)

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

# ReviewCompass 現行 dogfooding 用の機能順（stages/feature-partitioning/2026-05-24-proposal.md と整合）
FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]

POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
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


def _render_next_action_template(value, next_action):
  """next_action の値で required_input のテンプレートを解決する"""
  if isinstance(value, str):
    replacements = {
      "feature": next_action.get("feature") or "",
      "phase": next_action.get("phase") or "",
      "stage": next_action.get("stage") or "",
      "kind": next_action.get("kind") or "",
    }
    try:
      return value.format(**replacements)
    except (KeyError, ValueError):
      return value
  if isinstance(value, list):
    return [
      _render_next_action_template(item, next_action)
      for item in value
    ]
  if isinstance(value, dict):
    return {
      key: _render_next_action_template(item, next_action)
      for key, item in value.items()
    }
  return value


def _load_discipline_map(cwd):
  """next_action 別の直前必読規律マップを読み込む"""
  map_path = Path(cwd) / DEFAULT_DISCIPLINE_MAP_PATH
  if not map_path.exists():
    return DEFAULT_DISCIPLINE_MAP
  try:
    loaded = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
  except (OSError, yaml.YAMLError):
    return DEFAULT_DISCIPLINE_MAP
  if not isinstance(loaded, dict):
    return DEFAULT_DISCIPLINE_MAP
  return loaded


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
  approval_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
  approval_state = {
    "path": DEFAULT_COMMIT_APPROVAL_PATH,
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
            elif actual_sha != expected_sha:
              errors.append(
                f"ユーザ承認レコードの target_sha256 が staged 内容と一致しません: "
                f"{filepath}"
              )

  approval_state["valid"] = not errors
  return approval_state, errors


def validate_commit_execution_delegation(approval_state, execution_actor):
  """LLM による commit 実行代行が明示承認されているか検査する"""
  if execution_actor == "human":
    return []

  delegation = approval_state.get("execution_delegation")
  if not isinstance(delegation, dict):
    return [
      "LLM によるコミット実行代行の明示承認がありません"
      "（execution_delegation が必要）"
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


def _staged_spec_files(staged_files):
  """staged された feature spec.json を返す"""
  return [
    path for path in staged_files
    if (
      path.startswith(".reviewcompass/specs/")
      and path.endswith("/spec.json")
    )
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
    if not isinstance(feature_scope, str) or not feature_scope.strip():
      errors.append(f"{prefix}.feature_scope が必要です")
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

    pending_gates = data.get("pending_gates")
    if not isinstance(pending_gates, list) or not all(isinstance(v, str) for v in pending_gates):
      errors.append(f"{filepath}.pending_gates は文字列 list が必要です")
      continue

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

    missing = [gate for gate in pending_gates if gate not in decision_gates]
    if missing:
      errors.append(
        f"{filepath}.downstream_impact_decisions に pending_gates の判定が不足しています: "
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
    ["git", "diff", "--cached", "--name-only"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    print(f"error: git diff 失敗: {result.stderr}", file=sys.stderr)
    return 2

  staged_files = [f for f in result.stdout.strip().splitlines() if f]
  dangerous = [f for f in staged_files if classify_staged_file(f) == "dangerous"]
  caution = [f for f in staged_files if classify_staged_file(f) == "caution"]
  normal = [f for f in staged_files if classify_staged_file(f) == "normal"]
  approval_state, approval_errors = validate_commit_approval(cwd, staged_files)
  execution_delegation_errors = validate_commit_execution_delegation(
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

  if deviation_reasons:
    reasons.extend(deviation_reasons)
    verdict, exit_code = "DEVIATION", 2
  elif unresolved_count > 0 or caution:
    if unresolved_count > 0:
      reasons.append(
        f"未消化所見が {unresolved_count} 件あります"
        f"（{DEFAULT_CARRY_FORWARD_REGISTER_PATH}）"
      )
    for f in caution:
      reasons.append(f"要注意変更: {f}（変更根拠を確認してください）")
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
    f"post-write-verification 状態: {post_write_state['manifest_status']}"
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
    ["git", "status", "--porcelain"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if status_result.returncode != 0:
    print(f"error: git status 失敗: {status_result.stderr}", file=sys.stderr)
    return 2

  is_dirty = bool(status_result.stdout.strip())

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

  # 判定（仕様 §6.3）
  reasons = []
  if in_progress_files:
    reasons.append(
      "stages/in-progress に進行中ファイルがあります: "
      + ", ".join(in_progress_files)
    )
  if is_dirty:
    reasons.append("作業ツリーに未コミット変更があります（push 前に commit が必要）")
  if commit_precheck_errors:
    reasons.extend(commit_precheck_errors)
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
    f"直近 5 コミット:\n{recent_commits}"
  )
  current_state_dict = {
    "is_dirty": is_dirty,
    "in_progress_files": in_progress_files,
    "ahead_count": ahead_info,
    "commit_precheck": commit_precheck_state,
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

  post_write_targets = [
    path
    for path in changed_files
    if is_post_write_verification_target(path)
  ]
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
    next_step = data.get("next_step") or ""
    if "停止点コミット" not in next_step:
      return False
  return True


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
    return "wait_for_human_approval"
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


def build_in_progress_next_action(cwd, relative_path):
  """進行中状態ファイルから next_action を作る"""
  data = load_in_progress_file(cwd, relative_path)
  process_id = data.get("process_id")
  if process_id == "maintenance":
    return {
      "kind": "maintenance_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "title": data.get("title"),
      "required_action": data.get("required_action", "continue_maintenance"),
      "blocked_normal_workflow": data.get("blocked_normal_workflow", True),
      "mainline_blocked_by": data.get("mainline_blocked_by"),
      "allowed_scope": data.get("allowed_scope", []),
      "allowed_files": data.get("allowed_files", []),
      "completion_conditions": data.get("completion_conditions", []),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": data.get(
        "reason",
        "maintenance 手続きの進行中状態ファイルがあります",
      ),
    }
  if process_id == "reopen-procedure":
    next_step = data.get("next_step")
    current_blocker = data.get("current_blocker")
    pending_gates = data.get("pending_gates", [])
    if pending_gates is None:
      pending_gates = []
    return {
      "kind": "reopen_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "next_step": next_step,
      "step_number": data.get("step_number"),
      "completed_steps": data.get("completed_steps", []),
      "pending_gates": pending_gates,
      "current_blocker": current_blocker,
      "required_action": resolve_reopen_required_action(
        next_step,
        current_blocker,
        data.get("step_number"),
      ),
      "feature": data.get("feature"),
      "phase": None,
      "stage": None,
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


def is_post_write_verification_target(path):
  """post-write-verification 規律の対象ファイルかを判定する"""
  if path.startswith("docs/archive/"):
    return False
  if path == "TODO_NEXT_SESSION.md":
    return True
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


def list_post_write_verification_targets(cwd):
  """未コミット変更のうち post-write-verification 対象を返す"""
  return [
    path
    for path in list_changed_files(cwd)
    if is_post_write_verification_target(path)
  ]


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
  post_write_targets = [
    path
    for path in target_files
    if is_post_write_verification_target(path)
  ]
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
  cwd = Path.cwd()
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
    if verification_targets:
      manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
      if manifest_state == "completed":
        if maintenance_action:
          next_action = maintenance_action
          current_state = {
            "in_progress_files": in_progress_files,
            "post_write_manifest": manifest.get("_path"),
          }
          reasons = []
          verdict, exit_code = "OK", 0
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
            resolved_action = resolve_next_action(specs)
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
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = []
          verdict, exit_code = "OK", 0
    else:
      if maintenance_action:
        next_action = maintenance_action
        current_state = {"in_progress_files": in_progress_files}
        reasons = []
        verdict, exit_code = "OK", 0
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
          resolved_action = resolve_next_action(specs)
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
      "execution_delegation が必要"
    ),
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

  args = parser.parse_args()

  if args.subcommand == "spec-set":
    sys.exit(cmd_spec_set(args))
  elif args.subcommand == "commit":
    sys.exit(cmd_commit(args))
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
  elif args.subcommand == "reopen-start":
    sys.exit(cmd_reopen_start(args))
  else:
    parser.print_help(sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
  main()
