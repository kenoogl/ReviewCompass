"""Structured effective prompt manifest の生成補助。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def sha256_file(path: str | Path) -> str:
  """ファイル内容の sha256 を `sha256:<hex>` 形式で返す。"""
  return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_artifact(path: str | Path) -> Dict[str, str]:
  """manifest.source_artifacts の 1 要素を作る。"""
  return {
    "path": str(path),
    "sha256": sha256_file(path),
  }


def build_manifest(
  *,
  decision_point: Dict[str, Any],
  source_artifacts: Iterable[Dict[str, Any]],
  required_disciplines: List[str],
  operation_contract: Dict[str, Any],
  expected_output_schema: Dict[str, Any],
  prompt_length: Dict[str, Any],
  preconditions_checked: List[Dict[str, Any]],
  language_task: Dict[str, Any],
  postconditions: List[Dict[str, Any]],
  on_completion: Dict[str, Any],
  schema_version: str = "effective-prompt-manifest-v1",
  extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  """effective prompt manifest の正本語彙を 1 つの mapping にまとめる。"""
  manifest: Dict[str, Any] = {
    "schema_version": schema_version,
    "decision_point": decision_point,
    "source_artifacts": list(source_artifacts),
    "required_disciplines": required_disciplines,
    "operation_contract": operation_contract,
    "expected_output_schema": expected_output_schema,
    "prompt_length": prompt_length,
    "preconditions_checked": preconditions_checked,
    "language_task": language_task,
    "postconditions": postconditions,
    "on_completion": on_completion,
  }
  if extra:
    manifest.update(extra)
  return manifest
