"""派生出力の識別子連結保持を検査する。"""
from dataclasses import dataclass


@dataclass(frozen=True)
class IdentifierLinkValidationResult:
  """識別子連結検査結果。"""

  ok: bool
  missing_links: list


class IdentifierLinkValidator:
  """派生出力に run_id / target_id があることを検査する。"""

  def validate(self, outputs):
    missing_links = []
    for output in outputs:
      missing_fields = [
        field for field in ("run_id", "target_id") if not output.get(field)
      ]
      if missing_fields:
        missing_links.append({
          "artifact_id": output.get("artifact_id"),
          "missing_fields": missing_fields,
        })
    return IdentifierLinkValidationResult(
      ok=not missing_links,
      missing_links=missing_links,
    )
