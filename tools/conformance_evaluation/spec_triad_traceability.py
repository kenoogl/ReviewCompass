from pathlib import Path


SPEC_TRIAD = ("requirements", "design", "tasks")


class SpecTriadTraceabilityChecker:
  def __init__(self, root):
    self.root = Path(root)

  def check(self, contract_feature_map):
    missing_refs = []
    checked_refs = 0

    for contract_id, feature in contract_feature_map.items():
      for spec_name in SPEC_TRIAD:
        checked_refs += 1
        path = Path(".reviewcompass") / "specs" / feature / f"{spec_name}.md"
        full_path = self.root / path
        text = full_path.read_text(encoding="utf-8") if full_path.exists() else ""
        if contract_id not in text:
          missing_refs.append(f"{path.as_posix()}: {contract_id}")

    return {
      "ok": not missing_refs,
      "checked_refs": checked_refs,
      "missing_refs": missing_refs,
    }
