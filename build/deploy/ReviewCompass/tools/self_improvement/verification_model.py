"""Verification model for workflow improvement proposals."""
from typing import Iterable, Mapping


class VerificationModel:
  def __init__(self, *, promotion_threshold: float = 0.9):
    self.promotion_threshold = promotion_threshold

  def run_retrospective_simulation(
    self,
    proposal: dict,
    *,
    target_scope: str,
    records: Iterable[Mapping[str, object]],
  ) -> dict:
    record_list = list(records)
    target_count = len(record_list)
    violation_count = sum(1 for record in record_list if record.get("violates") is True)
    violation_rate = violation_count / target_count if target_count else 0.0
    result = {
      "method": "retrospective_simulation",
      "target_scope": target_scope,
      "target_count": target_count,
      "violation_count": violation_count,
      "violation_rate": violation_rate,
    }
    statistical_evidence = proposal.setdefault("statistical_evidence", {})
    statistical_evidence["retrospective_simulation"] = result
    return result

  def evaluate_pilot_operation(self, compliance_series, *, period=None) -> dict:
    series = [
      self._normalize_compliance_entry(index, entry)
      for index, entry in enumerate(compliance_series, start=1)
    ]
    final_rate = series[-1]["compliance_rate"] if series else 0.0
    decision = "enforce" if final_rate >= self.promotion_threshold else "not_ready"
    return {
      "method": "pilot_operation",
      "period": period,
      "threshold": self.promotion_threshold,
      "compliance_series": series,
      "final_compliance_rate": final_rate,
      "promotion_decision": decision,
    }

  def mark_unverifiable(self, *, proposal_id: str, reason: str) -> dict:
    return {
      "proposal_id": proposal_id,
      "verification_status": "user_audit_required",
      "auto_approval": False,
      "reason": reason,
    }

  def _normalize_compliance_entry(self, index: int, entry) -> dict:
    if isinstance(entry, Mapping):
      return {
        "session": entry.get("session", f"session-{index}"),
        "compliance_rate": float(entry["compliance_rate"]),
      }
    return {
      "session": f"session-{index}",
      "compliance_rate": float(entry),
    }
