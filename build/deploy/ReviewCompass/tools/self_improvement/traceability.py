from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


EXPECTED_TASK_TESTS = {
  "T-001": "tests/self-improvement/test_t001_layout.py",
  "T-002": "tests/self-improvement/test_t002_input_model.py",
  "T-003": "tests/self-improvement/test_t003_signal_extraction.py",
  "T-004": "tests/self-improvement/test_t004_proposal_model.py",
  "T-005": "tests/self-improvement/test_t005_verification_model.py",
  "T-006": "tests/self-improvement/test_t006_approval_model.py",
  "T-007": "tests/self-improvement/test_t007_rollback_model.py",
  "T-008": "tests/self-improvement/test_t008_effect_measurement.py",
  "T-009": "tests/self-improvement/test_t009_machine_verification.py",
  "T-010": "tests/self-improvement/test_t010_interfaces.py",
  "T-011": "tests/self-improvement/test_t011_traceability.py",
  "T-012": "tests/self-improvement/test_t012_carry_forward_register.py",
}


EXPECTED_MODEL_NAMES = {
  "入力モデル",
  "signal_extraction モデル",
  "提案モデル",
  "検証モデル",
  "承認モデル",
  "履歴ロールバック",
  "効果測定",
}


EXPECTED_MODEL_LEVEL_EVIDENCE = {
  "入力モデル": {
    "unit": ("5 種類の入力源", "来歴情報"),
    "integration": ("上流機能", "連結テスト"),
    "acceptance": ("全 5 入力源", "実データ"),
  },
  "signal_extraction モデル": {
    "unit": ("4 種類の乖離判定",),
    "integration": ("input_model 出力", "パイプラインテスト"),
    "acceptance": ("過去レビュー記録", "遵守検査"),
  },
  "提案モデル": {
    "unit": ("YAML スキーマ", "proposal_id", "status 遷移"),
    "integration": ("signal_extraction 出力", "提案 YAML"),
    "acceptance": ("5 種類", "proposal_type"),
  },
  "検証モデル": {
    "unit": ("遡及シミュレーション", "パイロット運用", "影響範囲分析"),
    "integration": ("提案 YAML", "検証実施"),
    "acceptance": ("過去データ", "実証的検証"),
  },
  "承認モデル": {
    "unit": ("4 状態", "reopen-procedure", "5 ステップ"),
    "integration": ("git mv", "workflow-management"),
    "acceptance": ("利用者監査", "シミュレーション"),
  },
  "履歴ロールバック": {
    "unit": ("4 サブディレクトリ", "3 ロールバック方法", "整合性検査"),
    "integration": ("git 履歴", "シンボリックリンク"),
    "acceptance": ("撤廃復活", "シナリオ"),
  },
  "効果測定": {
    "unit": ("7 指標", "grep 集計"),
    "integration": ("全パイプライン", "集計"),
    "acceptance": ("時系列推移", "表示確認"),
  },
}


@dataclass(frozen=True)
class TraceabilityAudit:
  project_root: Path

  @property
  def design_path(self) -> Path:
    return self.project_root / ".reviewcompass/specs/self-improvement/design.md"

  @property
  def tasks_path(self) -> Path:
    return self.project_root / ".reviewcompass/specs/self-improvement/tasks.md"

  def missing_task_tests(self) -> list[str]:
    missing = []
    for task_id, path in EXPECTED_TASK_TESTS.items():
      if not (self.project_root / path).is_file():
        missing.append(task_id)
    return missing

  def model_level_coverage(self) -> dict[str, set[str]]:
    coverage: dict[str, set[str]] = {}
    for row in self._markdown_rows(self.design_path.read_text(), "### 18.1", "### 18.2"):
      cells = self._cells(row)
      if len(cells) != 4:
        continue
      model = re.sub(r"（§\d+）", "", cells[0].replace("**", "")).strip()
      if model in EXPECTED_MODEL_NAMES:
        levels = set()
        expected = EXPECTED_MODEL_LEVEL_EVIDENCE[model]
        if self._cell_matches(cells[1], expected["unit"]):
          levels.add("unit")
        if self._cell_matches(cells[2], expected["integration"]):
          levels.add("integration")
        if self._cell_matches(cells[3], expected["acceptance"]):
          levels.add("acceptance")
        coverage[model] = levels
    return coverage

  def requirements_traceability_issues(self) -> list[str]:
    text = self.tasks_path.read_text()
    issues: list[str] = []
    referenced_tasks: set[str] = set()

    for row in self._markdown_rows(text, "## 要件追跡", "## テスト戦略"):
      cells = self._cells(row)
      if len(cells) != 2 or not self._is_requirement_row(cells[0]):
        continue
      tasks = self._expand_task_ids(cells[1])
      if not tasks:
        issues.append(f"{cells[0]} has no task reference")
      unknown = tasks - set(EXPECTED_TASK_TESTS)
      for task_id in sorted(unknown):
        issues.append(f"{cells[0]} references unknown {task_id}")
      referenced_tasks.update(tasks)

    missing_from_table = set(EXPECTED_TASK_TESTS) - referenced_tasks
    for task_id in sorted(missing_from_table):
      issues.append(f"{task_id} is not referenced by requirements traceability")
    return issues

  def dvt_gate_issues(self) -> list[str]:
    issues: list[str] = []
    for row in self._markdown_rows(self.tasks_path.read_text(), "## 遅延確認事項", "## 機能横断"):
      cells = self._cells(row)
      if not cells or not cells[0].startswith("DVT-"):
        continue
      status = cells[-1]
      if "未解除" in status and "延期" not in status and "フェーズ" not in status:
        issues.append(f"{cells[0]} is unresolved without deferral reason")
    return issues

  def key_regression_coverage(self) -> dict[str, bool]:
    files = {
      "proposal": self._read("tests/self-improvement/test_t004_proposal_model.py"),
      "approval_test": self._read("tests/self-improvement/test_t006_approval_model.py"),
      "approval_model": self._read("tools/self_improvement/approval_model.py"),
      "rollback": self._read("tests/self-improvement/test_t007_rollback_model.py"),
      "effect": self._read("tests/self-improvement/test_t008_effect_measurement.py"),
      "machine": self._read("tests/self-improvement/test_t009_machine_verification.py"),
      "interfaces": self._read("tests/self-improvement/test_t010_interfaces.py"),
      "schema": self._read("learning/workflow/schemas/proposal.schema.json"),
    }
    return {
      "proposal_schema_validity": (
        "proposal_schema_documents_owned_constraints" in files["proposal"]
        and "$schema" in files["schema"]
        and "proposal_type" in files["schema"]
      ),
      "foundation_vocab_reference_only": "foundation" in files["interfaces"] and "redefinition" in files["interfaces"],
      "superseded_reopen_five_steps": self._has_superseded_reopen_five_step_evidence(
        files["approval_model"],
        files["approval_test"],
        files["machine"],
      ),
      "effect_metrics": "adoption_rate" in files["effect"] and "rollback_rate" in files["effect"],
      "rollback_integrity": "restore" in files["rollback"] and "archive" in files["rollback"],
      "workflow_materialized_at_sync": "materialized_at" in files["interfaces"],
    }

  def _read(self, relative_path: str) -> str:
    path = self.project_root / relative_path
    if not path.is_file():
      return ""
    return path.read_text()

  @staticmethod
  def _markdown_rows(text: str, start_heading: str, end_heading: str) -> list[str]:
    in_section = False
    rows = []
    for line in text.splitlines():
      if line.startswith(start_heading):
        in_section = True
        continue
      if in_section and line.startswith(end_heading):
        break
      if in_section and line.startswith("|") and "---" not in line:
        rows.append(line)
    return rows

  @staticmethod
  def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]

  @staticmethod
  def _cell_matches(cell: str, expected_tokens: tuple[str, ...]) -> bool:
    return all(token in cell for token in expected_tokens)

  @staticmethod
  def _is_requirement_row(text: str) -> bool:
    return bool(re.match(r"^Requirement \d+(?:\s|$)", text))

  @staticmethod
  def _expand_task_ids(text: str) -> set[str]:
    task_ids = set(re.findall(r"T-\d{3}", text))
    for start, end in re.findall(r"T-(\d{3})〜T-(\d{3})", text):
      for number in range(int(start), int(end) + 1):
        task_ids.add(f"T-{number:03d}")
    if "全タスク" in text:
      task_ids.update(EXPECTED_TASK_TESTS)
    return task_ids

  @staticmethod
  def _has_superseded_reopen_five_step_evidence(
    approval_model_text: str,
    approval_test_text: str,
    machine_verification_text: str,
  ) -> bool:
    step_inputs = (
      "declaration",
      "reopen_reason",
      "new_conclusion",
      "approval_text",
      "superseded_by",
      "superseded_at",
    )
    history_writes = (
      'proposal["superseded_by"] = superseded_by',
      'proposal["superseded_at"] = superseded_at',
      'proposal["reopen_reason"] = reopen_reason',
    )
    mv4_fields = (
      "check_superseded_fields",
      "superseded_by",
      "superseded_at",
      "reopen_reason",
    )
    return (
      "def supersede" in approval_model_text
      and all(token in approval_model_text for token in step_inputs)
      and "self._require_approval(approval_text)" in approval_model_text
      and all(token in approval_model_text for token in history_writes)
      and all(token in approval_test_text for token in step_inputs)
      and all(token in machine_verification_text for token in mv4_fields)
    )
