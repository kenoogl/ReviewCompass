"""Machine verification for conformance-evaluation."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone


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
    self.root = Path(root) if root is not None else None

  def check_prompt_isolation(self, *, prompt_text: str, forbidden_paths: list, run_id: str = "manual") -> VerificationResult:
    reasons = []
    for path in forbidden_paths:
      if path in prompt_text:
        reasons.append(f"forbidden upstream path in prompt: {path}")
    if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
      reasons.append("missing autonomous exploration prohibition")
    if self.root is not None:
      log_dir = self.root / "logs" / "estimation" / run_id
      log_dir.mkdir(parents=True, exist_ok=True)
      (log_dir / "prompt.log").write_text(
        "run_id: {run_id}\n"
        "timestamp: {timestamp}\n"
        "prompt_text:\n"
        "{prompt_text}\n"
        "forbidden_paths:\n"
        "{forbidden_paths}\n"
        "status: {status}\n".format(
          run_id=run_id,
          timestamp=datetime.now(timezone.utc).isoformat(),
          prompt_text=prompt_text,
          forbidden_paths="\n".join(f"- {path}" for path in forbidden_paths),
          status="DEVIATION" if reasons else "OK",
        ),
        encoding="utf-8",
      )
    return VerificationResult(
      check_id="MV-6",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="blocking",
    )
