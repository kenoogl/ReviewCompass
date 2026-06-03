"""evidence_class と maturity_label の束縛規則。"""
from pathlib import Path

import yaml


MATURITY_LABELS = {"mature", "preliminary", "exploratory"}

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FOUNDATION_CONTRACT = _REPO_ROOT / "runtime" / "foundation" / "metadata_contract.yaml"


def foundation_vocabulary(name):
  """foundation metadata contract の語彙を参照する。"""
  payload = yaml.safe_load(_FOUNDATION_CONTRACT.read_text(encoding="utf-8"))
  return set(payload["vocabularies"][name])


def maturity_for_evidence(evidence_class, *, eligible_for_standard_comparison):
  """evidence_class から maturity_label を返す。報告対象外は None。"""
  if evidence_class == "valid":
    if eligible_for_standard_comparison:
      return "mature"
    return "preliminary"
  if evidence_class == "exploratory":
    return "exploratory"
  if evidence_class in {"invalid", "analysis_blocked"}:
    return None
  raise ValueError(f"unknown evidence_class: {evidence_class}")


def preliminary_caveat_ref():
  """exploratory evidence に自動付与する caveat 参照。"""
  return {
    "ref_type": "caveat_entry",
    "target_path": "shared/caveat_register.json",
    "target_id": "preliminary-evidence",
  }

