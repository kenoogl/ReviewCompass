"""completion guards for analysis T-011."""
import ast
import json
import re
from pathlib import Path

import yaml

from analysis.caveat_register.mixed_review_mode_detector import LIMITATION_TYPES
from analysis.evidence_register.binding_rules import MATURITY_LABELS
from analysis.fragments.fragment_builder import FRAGMENT_TYPES
from analysis.staleness.staleness_checker import REGENERATION_STATUSES

_WRITE_METHODS = {"write_text", "write_bytes"}
_EVALUATION_PATH_MARKERS = (
  "experiments/analysis/",
  "experiments/conformance/",
  "conformance-evaluation/",
)


def analysis_owned_vocabularies():
  """analysis 所有語彙正本を返す。"""
  return {
    "maturity_label": set(MATURITY_LABELS),
    "limitation_type": set(LIMITATION_TYPES),
    "fragment_type": set(FRAGMENT_TYPES),
    "regeneration_status": set(REGENERATION_STATUSES),
  }


def foundation_vocabularies(repo_root):
  """foundation 正本語彙の実体配置を横断して読み取る。"""
  root = Path(repo_root)
  metadata = yaml.safe_load(
    (root / "runtime" / "foundation" / "metadata_contract.yaml").read_text(
      encoding="utf-8"
    )
  )
  vocabularies = dict(metadata["vocabularies"])
  finding_schema = json.loads(
    (root / "runtime" / "schemas" / "finding.schema.json").read_text(
      encoding="utf-8"
    )
  )
  necessity_schema = json.loads(
    (root / "runtime" / "schemas" / "necessity_judgment.schema.json").read_text(
      encoding="utf-8"
    )
  )
  vocabularies["counter_status"] = finding_schema["properties"]["counter_status"][
    "enum"
  ]
  vocabularies["severity"] = finding_schema["properties"]["severity"]["enum"]
  vocabularies["final_label"] = necessity_schema["properties"]["final_label"]["enum"]
  return vocabularies


def analysis_redefines_foundation_vocabularies(analysis_root, vocabulary_names):
  """analysis schema 内で foundation 語彙を enum 再定義している箇所を返す。"""
  violations = []
  for path in Path(analysis_root).rglob("*.schema.json"):
    schema = json.loads(path.read_text(encoding="utf-8"))
    _collect_enum_redefinitions(
      schema,
      vocabulary_names=set(vocabulary_names),
      path=path,
      pointer=[],
      violations=violations,
    )
  return violations


def covered_requirements(tasks_text):
  """要件追跡表で言及される Requirement 番号を返す。"""
  return {int(match) for match in re.findall(r"Requirement\s+([1-8])", tasks_text)}


def covered_tasks(tasks_text):
  """タスク文書で言及される T-xxx を返す。"""
  return set(re.findall(r"T-\d{3}", tasks_text))


def deferred_verification_rows(tasks_text):
  """DVT の表行を構造化する。"""
  rows = []
  for line in tasks_text.splitlines():
    if not line.startswith("| DVT-"):
      continue
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if len(cells) < 5:
      continue
    trigger = cells[3]
    status = cells[4]
    rows.append(
      {
        "id": cells[0],
        "task": cells[1],
        "item": cells[2],
        "trigger": trigger,
        "status": status,
        "has_deferral_reason": _has_deferral_reason(trigger, status),
      }
    )
  return rows


def completion_criteria(design_text):
  """design.md の完成判定基準 8 項目を抽出する。"""
  marker = "## 完成判定基準"
  start = design_text.index(marker)
  section = design_text[start + len(marker):]
  next_heading = section.find("\n## ")
  if next_heading != -1:
    section = section[:next_heading]
  return [
    line.removeprefix("- ").strip()
    for line in section.splitlines()
    if line.startswith("- ")
  ]


def criteria_has_t011_gate(_criterion, tasks_text):
  """design 完成判定基準が T-011 の機械ゲート対象であることを確認する。"""
  return (
    "design.md §完成判定基準の 8 項目すべて" in tasks_text
    and "T-011" in tasks_text
  )


def evaluation_write_violations(source_root):
  """analysis 側から evaluation 成果物へ書く経路を構造検査で返す。"""
  root = Path(source_root)
  paths = [root] if root.is_file() else sorted(root.rglob("*.py"))
  violations = []
  for path in paths:
    if not path.is_file():
      continue
    violations.extend(_evaluation_write_violations_in_file(path))
  return violations


def _evaluation_write_violations_in_file(path):
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  scanner = _EvaluationWriteScanner(path)
  scanner.visit(tree)
  return scanner.violations


class _EvaluationWriteScanner(ast.NodeVisitor):
  def __init__(self, path):
    self.path = path
    self.path_bindings = {}
    self.violations = []

  def visit_Assign(self, node):
    target = _path_target(node.value, self.path_bindings)
    if target:
      for assignee in node.targets:
        if isinstance(assignee, ast.Name):
          self.path_bindings[assignee.id] = target
    self.generic_visit(node)

  def visit_Call(self, node):
    violation = self._write_method_violation(node)
    if violation:
      self.violations.append(violation)
    self.generic_visit(node)

  def _write_method_violation(self, node):
    if not isinstance(node.func, ast.Attribute):
      return None
    if node.func.attr not in _WRITE_METHODS:
      return None
    target = _path_target(node.func.value, self.path_bindings)
    if not target or not _is_evaluation_path(target):
      return None
    return {
      "path": str(self.path),
      "line": node.lineno,
      "target": target,
      "operation": node.func.attr,
    }


def _path_target(node, path_bindings):
  if isinstance(node, ast.Name):
    return path_bindings.get(node.id)
  if isinstance(node, ast.Constant) and isinstance(node.value, str):
    return _normalize_path(node.value)
  if isinstance(node, ast.Call) and _is_path_constructor(node):
    return _path_target_from_call(node, path_bindings)
  if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
    left = _path_target(node.left, path_bindings)
    right = _path_target(node.right, path_bindings)
    if left and right:
      return _normalize_path(f"{left}/{right}")
    if right:
      return right
  return None


def _is_path_constructor(node):
  return (
    isinstance(node.func, ast.Name)
    and node.func.id == "Path"
    and node.args
  )


def _path_target_from_call(node, path_bindings):
  parts = [
    _path_target(argument, path_bindings)
    for argument in node.args
  ]
  parts = [part for part in parts if part]
  if not parts:
    return None
  return _normalize_path("/".join(parts))


def _normalize_path(path):
  return str(path).replace("\\", "/").strip("/")


def _is_evaluation_path(target):
  normalized = f"{_normalize_path(target)}/"
  return any(marker in normalized for marker in _EVALUATION_PATH_MARKERS)


def _collect_enum_redefinitions(schema, *, vocabulary_names, path, pointer, violations):
  if isinstance(schema, dict):
    key = pointer[-1] if pointer else ""
    if key in vocabulary_names and "enum" in schema:
      violations.append(f"{path}:{'/'.join(pointer)}")
    for child_key, child_value in schema.items():
      _collect_enum_redefinitions(
        child_value,
        vocabulary_names=vocabulary_names,
        path=path,
        pointer=[*pointer, child_key],
        violations=violations,
      )
  elif isinstance(schema, list):
    for index, child_value in enumerate(schema):
      _collect_enum_redefinitions(
        child_value,
        vocabulary_names=vocabulary_names,
        path=path,
        pointer=[*pointer, str(index)],
        violations=violations,
      )


def _has_deferral_reason(trigger, status):
  text = f"{trigger} {status}"
  return any(
    keyword in text
    for keyword in (
      "延期",
      "確定",
      "完了",
      "時点",
      "解除トリガー",
      "再確認",
      "再評価",
    )
  )
