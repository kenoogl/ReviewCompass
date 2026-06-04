"""Carry-forward register abstraction for project-local finding ledgers."""
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List, Mapping, Optional

import yaml


FEATURE_NAMES = (
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
)

LOCAL_REFERENCE_PATTERNS = (
  r"\b[A-Za-z-]+ Req [0-9]+",
  r"Requirement [0-9]+",
  r"受入 [0-9]+",
  r"本機能 §[0-9.]+",
  r"設計書 判断 [0-9]+",
  r"T-[0-9]{3}",
  r"§[0-9.]+",
  r"design\.md",
  r"tasks\.md",
)

LEGACY_PENDING_LEDGER_PATH = ".reviewcompass/pending-cross-feature-findings.md"
LEGACY_PENDING_LEDGER_PATTERN = re.compile(
  r"\.reviewcompass/pending-cross-feature-findings\.md"
  r"|(?<!reviewcompass-)pending-cross-feature-findings\.md"
)


@dataclass(frozen=True)
class LegacyReferenceViolation:
  path: str
  line: int
  text: str


def _is_reusable_reference_target(path: Path) -> bool:
  parts = path.parts
  path_text = path.as_posix()
  if path_text == "TODO_NEXT_SESSION.md":
    return True
  if path_text in {
    "docs/extraction-mapping.md",
    "docs/experiments/evaluation-index-for-external-review.md",
    "docs/experiments/n-model-comparison.md",
    "docs/plan/reconstruction-plan-2026-05-21.md",
  }:
    return True
  if parts[:2] == ("docs", "operations"):
    return True
  if parts[:2] == ("docs", "notes"):
    return True
  if (
    len(parts) >= 6
    and parts[0] == ".reviewcompass"
    and parts[1] == "specs"
    and "reviews" in parts
    and path.name == "review-target.md"
  ):
    return True
  if (
    len(parts) == 4
    and parts[0] == ".reviewcompass"
    and parts[1] == "specs"
    and path.name in {"requirements.md", "design.md", "tasks.md"}
  ):
    return True
  return False


def audit_legacy_reference_targets(root: Path) -> List[LegacyReferenceViolation]:
  """Find legacy ledger references in files that may be reused as current input."""
  root = Path(root)
  violations: List[LegacyReferenceViolation] = []
  for path in sorted(root.rglob("*")):
    if not path.is_file() or not _is_reusable_reference_target(path.relative_to(root)):
      continue
    try:
      lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
      continue
    for index, line in enumerate(lines, start=1):
      if LEGACY_PENDING_LEDGER_PATTERN.search(line):
        violations.append(
          LegacyReferenceViolation(
            path=path.relative_to(root).as_posix(),
            line=index,
            text=line.strip(),
          )
        )
  return violations


def _strip_reviewcompass_prefix(path: str) -> str:
  return re.sub(r"^(\.\./)*\.reviewcompass/", "", path)


def _normalize_item_id(legacy_id: str) -> str:
  match = re.search(r"([0-9]+)$", legacy_id)
  if not match:
    return f"carry-forward-{legacy_id.lower()}"
  return f"carry-forward-{int(match.group(1)):03d}"


def _split_sections(markdown: str) -> List[Dict[str, str]]:
  pattern = re.compile(r"^###\s+(A-[0-9]+)：(.+)$", re.MULTILINE)
  matches = list(pattern.finditer(markdown))
  sections = []
  for index, match in enumerate(matches):
    end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
    sections.append(
      {
        "legacy_id": match.group(1),
        "title": match.group(2).strip(),
        "body": markdown[match.end():end].strip(),
      }
    )
  return sections


def _status_from_section(title: str, body: str) -> str:
  if "対処済み" in title or "対処済み" in body:
    return "resolved"
  return "open"


def _clean_summary(title: str) -> str:
  summary = _sanitize_general_text(re.sub(r"\s*✅.*$", "", title).strip())
  if summary and _contains_local_reference(summary):
    cleaned = re.sub(r"本機能 §[0-9.]+", "", summary)
    cleaned = re.sub(r"設計書 判断 [0-9]+", "", cleaned)
    cleaned = re.sub(r"T-[0-9]{3}", "", cleaned)
    cleaned = re.sub(r"§[0-9.]+", "", cleaned)
    cleaned = re.sub(r"\b[A-Za-z-]+ Req [0-9]+", "", cleaned)
    cleaned = re.sub(r"Requirement [0-9]+", "", cleaned)
    cleaned = re.sub(r"受入 [0-9]+", "", cleaned)
    cleaned = re.sub(r"design\.md|tasks\.md", "", cleaned)
    cleaned = re.sub(r"^[\sと／・、の]+", "", cleaned)
    cleaned = re.sub(r"[\sと／・、の]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "ローカル参照"
  return summary


def _sanitize_general_text(text: Optional[str]) -> Optional[str]:
  if text is None:
    return None
  sanitized = _strip_reviewcompass_prefix(text)
  sanitized = re.sub(r"（利用者明示承認[^）]*セッション\s*[0-9]+[^）]*）", "", sanitized)
  sanitized = re.sub(r"利用者明示承認[^。]*（[0-9]{4}-[0-9]{2}-[0-9]{2} セッション\s*[0-9]+）", "", sanitized)
  sanitized = re.sub(r"セッション\s*[0-9]+", "", sanitized)
  sanitized = re.sub(r"\s+", " ", sanitized)
  return sanitized.strip()


def _local_references(text: Optional[str]) -> List[str]:
  if text is None:
    return []
  references = []
  for pattern in LOCAL_REFERENCE_PATTERNS:
    for match in re.finditer(pattern, text):
      value = match.group(0)
      if value not in references:
        references.append(value)
  return references


def _contains_local_reference(text: Optional[str]) -> bool:
  return bool(_local_references(text))


def _abstract_reason(text: Optional[str]) -> Optional[str]:
  if text is None:
    return None
  if not _contains_local_reference(text):
    return text
  lowered = text.lower()
  if "時系列契約" in text or "完了通知" in text:
    return "時系列契約と完了通知形式を整合させる"
  if "スキーマ" in text:
    return "共有スキーマと利用側の入力契約を整合させる"
  if "語彙" in text or "値" in text or "受入" in text or "Req" in text or "Requirement" in text:
    return "関連仕様の値と時系列契約を整合させる"
  if "出力" in text or "入力" in text:
    return "機能間の入出力契約を整合させる"
  if "design.md" in lowered or "tasks.md" in lowered or "§" in text:
    return "関連仕様の記述を整合させる"
  return "ローカル参照を証跡に隔離し、一般化した対応方針へ置き換える"


def _extract_detected_session(body: str) -> Optional[str]:
  match = re.search(r"セッション\s*[0-9]+", body)
  return match.group(0) if match else None


def _extract_features_from_scope(body: str) -> List[str]:
  features = []
  for match in re.finditer(r"\*\*([^*]+)\*\*：", body):
    feature = match.group(1)
    if feature in FEATURE_NAMES and feature not in features:
      features.append(feature)
  return features


def _extract_source_feature(body: str, targets: List[str]) -> Optional[str]:
  detection_match = re.search(r"\*\*検出\*\*：([^\n]+)", body)
  detection_text = detection_match.group(1) if detection_match else ""
  for feature in FEATURE_NAMES:
    if feature in detection_text:
      return feature
  if targets:
    return targets[0]
  return None


def _extract_carry_forward_reason(body: str) -> Optional[str]:
  match = re.search(r"\*\*対処方針\*\*：([^\n]+)", body)
  if match:
    return _abstract_reason(_sanitize_general_text(match.group(1).strip()))
  match = re.search(r"\*\*対処内容\*\*：([^\n]+)", body)
  if match:
    return _abstract_reason(_sanitize_general_text(match.group(1).strip()))
  return None


def _extract_evidence_refs(body: str) -> List[Dict[str, str]]:
  refs = []
  for label, path in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body):
    refs.append(
      {
        "label": label,
        "path": _strip_reviewcompass_prefix(path),
      }
    )
  return refs


def _decision_reasons(
  *,
  source_feature: Optional[str],
  targets: List[str],
  carry_forward_reason: Optional[str],
) -> List[str]:
  reasons = []
  if source_feature is None:
    reasons.append("missing_source_feature")
  if not targets:
    reasons.append("missing_target_feature_or_phase")
  if carry_forward_reason is None:
    reasons.append("missing_carry_forward_reason")
  return reasons


def parse_pending_markdown(markdown: str) -> Dict[str, object]:
  """Parse a project-local markdown ledger into an abstract register."""
  items = []
  for section in _split_sections(markdown):
    targets = _extract_features_from_scope(section["body"])
    source_feature = _extract_source_feature(section["body"], targets)
    carry_forward_reason = _extract_carry_forward_reason(section["body"])
    reasons = _decision_reasons(
      source_feature=source_feature,
      targets=targets,
      carry_forward_reason=carry_forward_reason,
    )
    status = _status_from_section(section["title"], section["body"])
    item = {
      "item_id": _normalize_item_id(section["legacy_id"]),
      "scope": "cross_scope",
      "source_feature": source_feature,
      "target_feature_or_phase": targets,
      "finding_summary": _clean_summary(section["title"]),
      "status": status,
      "decision_needed": bool(reasons),
      "decision_reasons": reasons,
      "carry_forward_reason": carry_forward_reason,
      "resolution": carry_forward_reason if status == "resolved" else None,
      "evidence_refs": _extract_evidence_refs(section["body"]),
      "project_local_context": {
        "legacy_id": section["legacy_id"],
        "detected_session": _extract_detected_session(section["body"]),
      },
    }
    items.append(item)
  return {
    "register_id": "carry-forward-register",
    "schema_version": 1,
    "source_type": "carry_forward_register",
    "items": items,
  }


def general_field_local_reference_violations(register: Mapping[str, object]) -> List[str]:
  """Return item ids whose general decision fields still contain local references."""
  items = register.get("items", [])
  if not isinstance(items, list):
    return ["register.items"]
  violations = []
  general_fields = (
    "finding_summary",
    "carry_forward_reason",
    "resolution",
  )
  for item in items:
    if not isinstance(item, Mapping):
      continue
    for field in general_fields:
      if _contains_local_reference(str(item.get(field) or "")):
        item_id = str(item.get("item_id") or "<unknown>")
        violations.append(f"{item_id}.{field}")
  return violations


def count_unresolved_items(register: Mapping[str, object]) -> int:
  items = register.get("items", [])
  if not isinstance(items, list):
    return 0
  return sum(
    1
    for item in items
    if isinstance(item, Mapping) and item.get("status") != "resolved"
  )


class CarryForwardRegister:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def import_markdown(self, source_path: Path) -> Dict[str, object]:
    return parse_pending_markdown(Path(source_path).read_text(encoding="utf-8"))

  def write_import(self, source_path: Path, out_path: Path) -> Path:
    register = self.import_markdown(source_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
      yaml.safe_dump(register, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return out_path
