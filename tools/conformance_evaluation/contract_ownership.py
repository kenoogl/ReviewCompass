"""Contract ownership map for implementation-derived drift candidates."""
from pathlib import Path
import yaml

from tools.conformance_evaluation.evaluation_record import conformance_dir


class ContractOwnershipMapError(ValueError):
  """Raised when a contract ownership entry violates the local vocabulary."""


OWNER_CANDIDATES = {
  "requirements",
  "design",
  "operations",
  "tool_contract",
  "test_contract",
  "review_evidence",
  "carry_forward",
}

CLASSIFICATIONS = {
  "spec-missing",
  "code-missing",
  "mismatch",
  "implementation-detail",
  "ownership-unclear",
}


class ContractOwnershipMap:
  def __init__(self):
    self.items = []

  @classmethod
  def from_items(cls, items: list):
    ownership_map = cls()
    for item in items:
      ownership_map.add_item(**item)
    return ownership_map

  def add_item(
    self,
    *,
    contract_id: str,
    feature: str,
    classification: str,
    primary_owner_candidate: str,
    secondary_owner_candidate: str,
    contract_refs: list,
    evidence_refs: list,
    related_clusters: list,
    claim: str = "",
    depends_on=None,
  ) -> dict:
    self._validate_classification(classification)
    self._validate_owner(primary_owner_candidate)
    self._validate_owner(secondary_owner_candidate)
    item = {
      "contract_id": contract_id,
      "feature": feature,
      "claim": claim,
      "classification": classification,
      "owner_status": "provisional",
      "primary_owner_candidate": primary_owner_candidate,
      "secondary_owner_candidate": secondary_owner_candidate,
      "contract_refs": list(contract_refs),
      "evidence_refs": list(evidence_refs),
      "source_refs": self._source_refs(contract_refs, evidence_refs),
      "related_clusters": list(related_clusters),
      "depends_on": list(depends_on or []),
    }
    self.items.append(item)
    return item

  def item_by_id(self, contract_id: str) -> dict:
    for item in self.items:
      if item["contract_id"] == contract_id:
        return item
    raise ContractOwnershipMapError(f"unknown_contract_id: {contract_id}")

  def update_candidates(self) -> dict:
    candidates = {}
    for item in self.items:
      for path in item["contract_refs"]:
        if self._is_spec_update_target(path, item):
          candidates.setdefault(path, []).append(item["contract_id"])
    return candidates

  def spec_update_proposals(self) -> list:
    grouped = {}
    for item in self.items:
      for path in item["contract_refs"]:
        if not self._is_spec_update_target(path, item):
          continue
        if path not in grouped:
          grouped[path] = {
            "target_file": path,
            "target_kind": self._source_kind(path),
            "contract_ids": [],
            "claims": [],
            "needs_human_decision": False,
          }
        grouped[path]["contract_ids"].append(item["contract_id"])
        grouped[path]["claims"].append(item["claim"])
        if item["classification"] == "ownership-unclear" or item["primary_owner_candidate"] == "carry_forward":
          grouped[path]["needs_human_decision"] = True
    return list(grouped.values())

  def spec_update_drafts(self) -> list:
    drafts = []
    for proposal in self.spec_update_proposals():
      drafts.append({
        "target_file": proposal["target_file"],
        "target_kind": proposal["target_kind"],
        "apply_status": "draft_only",
        "draft_heading": self._draft_heading(proposal["target_kind"]),
        "draft_bullets": [
          f"- {contract_id}: {claim}"
          for contract_id, claim in zip(proposal["contract_ids"], proposal["claims"])
        ],
        "needs_human_decision": proposal["needs_human_decision"],
      })
    return drafts

  def _validate_owner(self, owner: str) -> None:
    if owner not in OWNER_CANDIDATES:
      raise ContractOwnershipMapError(f"unknown_owner_candidate: {owner}")

  def _validate_classification(self, classification: str) -> None:
    if classification not in CLASSIFICATIONS:
      raise ContractOwnershipMapError(f"unknown_classification: {classification}")

  def _source_refs(self, contract_refs: list, evidence_refs: list) -> list:
    refs = []
    for path in contract_refs:
      refs.append({"path": path, "source_kind": self._source_kind(path)})
    for path in evidence_refs:
      refs.append({"path": path, "source_kind": self._source_kind(path)})
    return refs

  def _source_kind(self, path: str) -> str:
    if path.endswith("/requirements.md") or path.endswith("requirements.md"):
      return "requirements"
    if path.endswith("/design.md") or path.endswith("design.md"):
      return "design"
    if path.endswith("/tasks.md") or path.endswith("tasks.md"):
      return "tasks"
    if path.startswith(".reviewcompass/guidance/"):
      return "operations"
    if path.startswith("docs/operations/") or path.startswith("docs/disciplines/"):
      return "operations"
    if path.startswith("tests/"):
      return "test"
    if path.startswith("tools/"):
      return "implementation"
    if "/reviews/" in path or path.startswith("docs/notes/review-runs/"):
      return "review_evidence"
    if path.startswith("docs/notes/"):
      return "note"
    return "unknown"

  def _is_spec_update_target(self, path: str, item: dict) -> bool:
    if not path.startswith(".reviewcompass/specs/"):
      return False
    owner = item["primary_owner_candidate"]
    if owner == "requirements":
      return path.endswith("/requirements.md")
    if owner == "design":
      return path.endswith("/design.md")
    if owner in {"carry_forward", "test_contract", "tool_contract"}:
      return path.endswith("/tasks.md")
    return False

  def _draft_heading(self, target_kind: str) -> str:
    if target_kind == "requirements":
      return "Implementation-derived requirements candidates"
    if target_kind == "design":
      return "Implementation-derived design candidates"
    if target_kind == "tasks":
      return "Carry-forward implementation drift tasks"
    return "Implementation-derived contract candidates"


class SpecUpdateDraftWriter:
  def __init__(self, root: Path):
    self.root = Path(root)

  def write(self, *, feature: str, run_date: str, drafts: list) -> dict:
    draft_dir = conformance_dir(self.root, feature) / f"{run_date}-spec-update-drafts"
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_files = []
    for draft in drafts:
      path = draft_dir / f"{self._safe_target_name(draft['target_file'])}.md"
      path.write_text(self._markdown(draft), encoding="utf-8")
      draft_files.append(str(path))
    return {
      "draft_dir": str(draft_dir),
      "draft_files": draft_files,
    }

  def _safe_target_name(self, target_file: str) -> str:
    safe = target_file.strip("./").replace("/", "-").replace("_", "-")
    safe = safe.replace(".md", "")
    return safe

  def _markdown(self, draft: dict) -> str:
    bullets = "\n".join(draft["draft_bullets"])
    human_decision = "true" if draft["needs_human_decision"] else "false"
    return (
      "---\n"
      f"apply_status: {draft['apply_status']}\n"
      f"target_file: {draft['target_file']}\n"
      f"target_kind: {draft['target_kind']}\n"
      f"needs_human_decision: {human_decision}\n"
      "---\n\n"
      f"# {draft['draft_heading']}\n\n"
      f"{bullets}\n"
    )


def workflow_management_seed_items() -> list:
  contract_refs = [
    ".reviewcompass/specs/workflow-management/requirements.md",
    ".reviewcompass/specs/workflow-management/design.md",
    ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md",
  ]
  common_evidence_refs = [
    "docs/notes/2026-06-08-workflow-management-conformance-drift-audit.md",
    "tools/check-workflow-action.py",
    "tests/tools/test_check_workflow_action.py",
  ]
  return [
    {
      "contract_id": "WM-DRIFT-001",
      "feature": "workflow-management",
      "claim": "next subcommand is the canonical workflow navigation entry point",
      "classification": "spec-missing",
      "primary_owner_candidate": "requirements",
      "secondary_owner_candidate": "design",
      "contract_refs": contract_refs,
      "evidence_refs": common_evidence_refs,
      "related_clusters": ["XDRIFT-002"],
    },
    {
      "contract_id": "WM-DRIFT-002",
      "feature": "workflow-management",
      "claim": "post-write target detection and manifest verification are implementation contracts",
      "classification": "spec-missing",
      "primary_owner_candidate": "requirements",
      "secondary_owner_candidate": "design",
      "contract_refs": contract_refs,
      "evidence_refs": common_evidence_refs,
      "related_clusters": ["XDRIFT-002", "XDRIFT-003", "XDRIFT-005"],
    },
    {
      "contract_id": "WM-DRIFT-005",
      "feature": "workflow-management",
      "claim": "commit approval records require target_sha256 coverage for staged content",
      "classification": "spec-missing",
      "primary_owner_candidate": "requirements",
      "secondary_owner_candidate": "operations",
      "contract_refs": contract_refs,
      "evidence_refs": common_evidence_refs + ["tools/guarded-git-commit.py"],
      "related_clusters": ["XDRIFT-004"],
    },
    {
      "contract_id": "WM-DRIFT-008",
      "feature": "workflow-management",
      "claim": "autonomous plan and ledger contracts are implemented as workflow-management safety contracts",
      "classification": "spec-missing",
      "primary_owner_candidate": "requirements",
      "secondary_owner_candidate": "design",
      "contract_refs": contract_refs,
      "evidence_refs": common_evidence_refs,
      "related_clusters": ["XDRIFT-003", "XDRIFT-005"],
    },
  ]


def load_contract_ownership_items(path) -> list:
  data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  items = data.get("items") if isinstance(data, dict) else None
  if not isinstance(items, list):
    raise ContractOwnershipMapError("missing_items")
  return items
