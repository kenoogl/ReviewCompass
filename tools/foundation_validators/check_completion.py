"""check_completion.py：完成判定基準の自動実行（foundation T-010）。

design.md §完成判定基準の 6 項目を自動実行し、合否を判定する統合スクリプト。
T-009 のテスト群（pytest）と T-008 の符号化規約検証をまとめて実行する。
出力は design.md §完成判定レポートの YAML スキーマに準拠する。

6 項目（design.md §完成判定基準）：
  1: テスト戦略の全項目通過
  2: 本機能資産の配置先が §共有資産配置で一意に解決
  3: メタデータ項目の責務分離が §3 で宣言
  4: 無効化と検証が生証拠を汚さない成果物分離が §8 で定義
  5: 6 つの下流仕様が取り込む成果物が §下流仕様への影響で追跡可能
  6: §判断 7 語彙正本すべての所有関係が §3 と §4 で宣言、参照禁止対象が明示

使い方：python3 check_completion.py [<repo_root>]
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DESIGN_REL = ".reviewcompass/specs/foundation/design.md"
TASKS_REL = ".reviewcompass/specs/foundation/tasks.md"
TESTS_DIR_REL = "tests/foundation"

# 項目 2：配置先で一意に解決されるべき主要成果物（design.md §共有資産配置）
EXPECTED_ARTIFACTS = [
  "runtime/foundation/layer1_framework.yaml",
  "runtime/foundation/metadata_contract.yaml",
  "runtime/schemas/review_case.schema.json",
  "runtime/schemas/finding.schema.json",
  "runtime/schemas/impact_score.schema.json",
  "runtime/schemas/failure_observation.schema.json",
  "runtime/schemas/necessity_judgment.schema.json",
  "runtime/validators/contracts/validator_result.schema.json",
  "runtime/validators/contracts/invalidation_marker.schema.json",
  "runtime/prompts/primary_detection/primary_reviewer.prompt.md",
  "runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md",
  "runtime/prompts/judgment/judgment_reviewer.prompt.md",
  "runtime/config/reviewcompass.yaml",
  "runtime/config/config.yaml.template",
  "runtime/config/terminology.yaml.template",
]


def check_bidirectional_traceability(text):
  """要件追跡表（要件→タスク）と各タスク本文の対応要件欄（タスク→要件）の双方向整合を検査する。

  違反のエラーリストを返す（空なら整合）。
  """
  errors = []
  marker = "## 要件追跡"
  if marker not in text:
    return ["要件追跡表（## 要件追跡）が見つからない"]
  body, table = text.split(marker, 1)

  body_reqs = set()
  for line in body.splitlines():
    if "対応要件" in line:
      body_reqs.update(re.findall(r"Requirement\s*(\d+)", line))
  table_reqs = set(re.findall(r"Requirement\s*(\d+)", table))

  for r in sorted(body_reqs - table_reqs, key=int):
    errors.append(f"Requirement {r} がタスク本文にあるが要件追跡表にない")
  for r in sorted(table_reqs - body_reqs, key=int):
    errors.append(f"Requirement {r} が要件追跡表にあるがタスク本文の対応要件欄にない")
  return errors


def _criterion(cid, name, ok, details):
  return {
    "criterion_id": cid,
    "name": name,
    "status": "pass" if ok else "fail",
    "details": details,
  }


def _check_tests_pass(repo_root):
  """項目 1：テスト戦略の全項目通過。pytest を tests/foundation に対して実行する。

  T-010 自身のテスト（test_t010_completion.py）は本関数を呼ぶため、自己参照（無限再帰）を
  避けて除外する。
  """
  tests_dir = repo_root / TESTS_DIR_REL
  self_test = tests_dir / "test_t010_completion.py"
  cmd = [
    sys.executable, "-m", "pytest", str(tests_dir),
    f"--ignore={self_test}", "-q",
  ]
  try:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
  except Exception as exc:  # noqa: BLE001
    return False, f"pytest 実行に失敗：{exc}"
  ok = proc.returncode == 0
  tail = (proc.stdout or "").strip().splitlines()
  summary = tail[-1] if tail else ""
  return ok, f"pytest（T-010自身は自己参照のため除外）：{summary}"


def run_completion_check(repo_root):
  """6 項目を判定し、design.md のレポート YAML スキーマに準拠した dict を返す。"""
  repo_root = Path(repo_root)
  design_text = (repo_root / DESIGN_REL).read_text(encoding="utf-8")

  # 実体照合用にメタデータ契約とスキーマを読む（P-003 対処：文字列照合だけに頼らない）
  def _safe_yaml(rel):
    try:
      with (repo_root / rel).open(encoding="utf-8") as f:
        return yaml.safe_load(f)
    except Exception:  # noqa: BLE001
      return {}

  def _safe_json(rel):
    try:
      with (repo_root / rel).open(encoding="utf-8") as f:
        return json.load(f)
    except Exception:  # noqa: BLE001
      return {}

  meta = _safe_yaml("runtime/foundation/metadata_contract.yaml")
  finding_schema = _safe_json("runtime/schemas/finding.schema.json")
  necessity_schema = _safe_json("runtime/schemas/necessity_judgment.schema.json")

  results = []

  # 項目 1：テスト戦略の全項目通過
  ok1, detail1 = _check_tests_pass(repo_root)
  results.append(_criterion(1, "テスト戦略の全項目通過", ok1, detail1))

  # 項目 2：配置先が §共有資産配置で一意に解決
  missing = [a for a in EXPECTED_ARTIFACTS if not (repo_root / a).is_file()]
  results.append(_criterion(
    2, "配置先が共有資産配置で一意に解決",
    not missing,
    "全成果物が配置済み" if not missing else f"欠落：{missing}",
  ))

  # 項目 3：メタデータ責務分離が §3 で宣言され、metadata_contract に実在（P-003 強化）
  sep_terms = ["run_status", "validator_status", "human_signoff_status", "evidence_class"]
  sep_decl = meta.get("responsibility_separation", {}) if isinstance(meta, dict) else {}
  ok3 = (all(t in design_text for t in sep_terms) and "責務分離" in design_text
         and all(axis in sep_decl for axis in sep_terms))
  results.append(_criterion(
    3, "メタデータ責務分離が §3 宣言かつ実体に存在", ok3,
    "4 状態軸の責務分離が design.md と metadata_contract.yaml の双方にある" if ok3
    else "責務分離の宣言または実体（metadata_contract.responsibility_separation）が不足",
  ))

  # 項目 4：無効化と検証の成果物分離が §8 で定義
  ok4 = "検証と無効化のモデル" in design_text and "生証拠" in design_text
  results.append(_criterion(
    4, "無効化と検証の成果物分離が §8 で定義", ok4,
    "§8 検証と無効化のモデルが記載" if ok4 else "§8 の記載が不足",
  ))

  # 項目 5：6 下流仕様が取り込む成果物が追跡可能
  ok5 = "下流仕様への影響" in design_text
  results.append(_criterion(
    5, "下流仕様が取り込む成果物が追跡可能", ok5,
    "§下流仕様への影響が記載" if ok5 else "§下流仕様への影響の記載が不足",
  ))

  # 項目 6：§判断 7 語彙正本が §3／§4 で宣言され、実体（metadata と enum）に存在（P-003 強化）
  vocabs = meta.get("vocabularies", {}) if isinstance(meta, dict) else {}
  meta_vocab_ok = all(
    v in vocabs and vocabs[v]
    for v in ["validator_status", "evidence_class", "review_mode", "confidence_label"]
  )

  def _enum(schema, prop):
    return (schema.get("properties", {}).get(prop, {}) or {}).get("enum")

  enum_ok = (
    bool(_enum(finding_schema, "counter_status"))
    and bool(_enum(finding_schema, "severity"))
    and bool(_enum(necessity_schema, "final_label"))
  )
  ok6 = "判断 7" in design_text and "再定義" in design_text and meta_vocab_ok and enum_ok
  results.append(_criterion(
    6, "語彙正本の所有関係宣言と 7 語彙の実体存在", ok6,
    "§判断 7・参照禁止の記載と 7 語彙の実体（metadata 4 種＋スキーマ enum 3 種）を確認" if ok6
    else "語彙正本の宣言または実体が不足",
  ))

  # target_commit を取得（失敗時は unknown）
  try:
    proc = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      capture_output=True, text=True, cwd=str(repo_root),
    )
    target_commit = proc.stdout.strip() if proc.returncode == 0 else "unknown"
  except Exception:  # noqa: BLE001
    target_commit = "unknown"

  return {
    "overall_pass": all(c["status"] == "pass" for c in results),
    "target_commit": target_commit,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "criteria_results": results,
  }


def main(argv):
  """完成判定を実行し、YAML レポートを標準出力に整形出力する。overall_pass なら 0。"""
  repo_root = Path(argv[0]) if argv else Path(__file__).resolve().parents[2]
  report = run_completion_check(repo_root)
  print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
  return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
