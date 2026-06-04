"""Six criteria structure for artifact-to-spec conformance evaluation."""
from dataclasses import dataclass


class CriteriaError(ValueError):
  """Raised when a criterion or axis is outside the conformance contract."""


@dataclass(frozen=True)
class Criterion:
  criterion_id: str
  axis: str
  title: str
  substructure: tuple


SUBSTRUCTURE = ("要点", "詳細抽出", "深掘り", "該当なし")

CRITERIA = (
  Criterion("criterion-1", "requirements", "受け入れ基準と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-2", "requirements", "API・データ契約と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-3", "requirements", "例外系・境界条件と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-4", "design", "モジュール構成・データモデルと実装の対応", SUBSTRUCTURE),
  Criterion("criterion-5", "design", "接合面と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-6", "design", "アルゴリズム・性能達成手段と実装の対応", SUBSTRUCTURE),
)

EXCLUDED_LAYERS = ("feature-partitioning", "intent", "tasks")


def criterion_by_id(criterion_id: str) -> Criterion:
  for criterion in CRITERIA:
    if criterion.criterion_id == criterion_id:
      return criterion
  raise CriteriaError(f"unknown_criterion: {criterion_id}")


def validate_axis(axis: str) -> None:
  if axis not in {"requirements", "design"}:
    raise CriteriaError(f"unknown_axis: {axis}")

