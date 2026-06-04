"""Machine verification for conformance-evaluation."""
from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
  OK = "OK"
  DEVIATION = "DEVIATION"


@dataclass(frozen=True)
class VerificationResult:
  check_id: str
  status: VerificationStatus
  reasons: list
  fail_closed: str


class MachineVerification:
  def __init__(self, root=None):
    self.root = root

  def check_prompt_isolation(self, *, prompt_text: str, forbidden_paths: list) -> VerificationResult:
    reasons = []
    for path in forbidden_paths:
      if path in prompt_text:
        reasons.append(f"forbidden upstream path in prompt: {path}")
    if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
      reasons.append("missing autonomous exploration prohibition")
    return VerificationResult(
      check_id="MV-6",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="blocking",
    )

