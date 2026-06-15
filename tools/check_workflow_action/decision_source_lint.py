"""decision-source-lint サブコマンドの実装（Req 11、T-013）

設計正本: .reviewcompass/specs/workflow-management/design.md §Req 11 設計モデル §1〜§6
"""

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ──────────────────────────────────────────────
# 定数
# ──────────────────────────────────────────────

DECISIONS_DIR = ".reviewcompass/decisions"
BUNDLE_EXCEPTIONS_DIR = ".reviewcompass/decisions/bundle-exceptions"
SESSIONS_DIR = ".reviewcompass/evidence/sessions"
CONFIG_PATH = "stages/decision-source-lint-config.yaml"

VALID_CATEGORIES = {"irreversible_operation", "discipline_change", "spec_plan_change"}
VALID_VERIFICATION_STATUSES = {"verified", "pending", "unverifiable"}
VALID_MULTIPLICITIES = {"single", "bundled"}

BUILTIN_EMPTY_CONTENT_WORDS = [
  "OK",
  "ok",
  "承認",
  "了解",
  "はい",
  "Yes",
  "yes",
  "LGTM",
  "✓",
  "◯",
  "○",
]

PUNCTUATION_PATTERN = re.compile(r"[。、！？!?,\.。，！？]")


# ──────────────────────────────────────────────
# データクラス
# ──────────────────────────────────────────────

@dataclass
class DecisionLintResult:
  verdict: str  # "OK" | "WARN" | "DEVIATION"
  exit_code: int  # 0 | 1 | 2
  file_path: str = ""
  messages: list = field(default_factory=list)


@dataclass
class VerifyPendingResult:
  exit_code: int  # 0 = all verified or no pending, non-zero = some failed
  updated: list = field(default_factory=list)
  failed: list = field(default_factory=list)
  messages: list = field(default_factory=list)


# ──────────────────────────────────────────────
# テスト(11) 設定ファイル読み取り
# ──────────────────────────────────────────────

def load_decision_source_lint_config(cwd: Path) -> dict:
  """設定ファイルから内容なし語リストを読み込む。
  ファイルが存在しない場合は内蔵デフォルトを返す。
  """
  config_path = Path(cwd) / CONFIG_PATH
  if config_path.exists():
    try:
      data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
      if isinstance(data, dict) and "empty_content_words" in data:
        return data
    except (OSError, yaml.YAMLError):
      pass
  return {"empty_content_words": list(BUILTIN_EMPTY_CONTENT_WORDS)}


# ──────────────────────────────────────────────
# テスト(3)(4) テキスト正規化
# ──────────────────────────────────────────────

def normalize_text(text: str) -> str:
  """逐語照合の前処理：NFC・連続空白→単一スペース・前後除去（design §3）"""
  text = unicodedata.normalize("NFC", text)
  text = re.sub(r"[\s　]+", " ", text)
  return text.strip()


# ──────────────────────────────────────────────
# テスト(6) 内容なし語リスト判定
# ──────────────────────────────────────────────

def is_empty_content(excerpt: str, config: dict) -> bool:
  """句読点除去→スペース区切りトークン化→全トークンがリスト一致で True（design §4）"""
  words = config.get("empty_content_words", [])
  cleaned = PUNCTUATION_PATTERN.sub("", excerpt)
  tokens = [t for t in cleaned.split(" ") if t]
  if not tokens:
    return True
  return all(t in words for t in tokens)


# ──────────────────────────────────────────────
# テスト(1) 決定記録スキーマ検査
# ──────────────────────────────────────────────

def validate_decision_schema(data: Any) -> list:
  """必須フィールド・enum・型を検査し、エラーメッセージのリストを返す（design §1）"""
  errors = []
  if not isinstance(data, dict):
    return ["決定記録がマッピングではありません"]

  # decision_id
  did = data.get("decision_id")
  if not isinstance(did, str) or not did:
    errors.append("decision_id が欠落または空文字列です")

  # category
  cat = data.get("category")
  if cat is None:
    errors.append("category が欠落しています")
  elif not isinstance(cat, str):
    errors.append("category が文字列ではありません")
  elif cat not in VALID_CATEGORIES:
    errors.append(f"category の値が不正です（有効値: {VALID_CATEGORIES}）: {cat!r}")

  # statement
  stmt = data.get("statement")
  if not isinstance(stmt, str) or not stmt:
    errors.append("statement が欠落または空文字列です")

  # source
  source = data.get("source")
  if source is None:
    errors.append("source が欠落しています")
  elif not isinstance(source, dict):
    errors.append("source がマッピングではありません")
  else:
    excerpt = source.get("excerpt")
    if not isinstance(excerpt, str) or not excerpt:
      errors.append("source.excerpt が欠落または空文字列です")
    locator = source.get("locator")
    if not isinstance(locator, str) or not locator:
      errors.append("source.locator が欠落または空文字列です")
    mult = source.get("multiplicity")
    if mult is None:
      errors.append("source.multiplicity が欠落しています")
    elif not isinstance(mult, str):
      errors.append("source.multiplicity が文字列ではありません")
    elif mult not in VALID_MULTIPLICITIES:
      errors.append(f"source.multiplicity の値が不正です（有効値: {VALID_MULTIPLICITIES}）: {mult!r}")

  # verification_status
  vs = data.get("verification_status")
  if vs is None:
    errors.append("verification_status が欠落しています")
  elif not isinstance(vs, str):
    errors.append("verification_status が文字列ではありません")
  elif vs not in VALID_VERIFICATION_STATUSES:
    errors.append(f"verification_status の値が不正です（有効値: {VALID_VERIFICATION_STATUSES}）: {vs!r}")

  return errors


# ──────────────────────────────────────────────
# テスト(2) 束ね例外チェック（design §2）
# ──────────────────────────────────────────────

def check_bundle_exception(data: dict, cwd: Path) -> list:
  """multiplicity: bundled の場合に束ね例外 3 条件を確認する。
  条件を満たさない場合はエラーメッセージのリストを返す。
  multiplicity: single の場合は常に [] を返す。
  """
  source = data.get("source", {})
  mult = source.get("multiplicity")

  if mult != "bundled":
    # single の場合: bundle_exception_id が付いていたら余分な例外 ID = エラー
    bex_id = data.get("bundle_exception_id")
    if bex_id:
      # 承認レコードが存在するかチェック（存在しなければエラー）
      exceptions_dir = Path(cwd) / BUNDLE_EXCEPTIONS_DIR
      record_path = exceptions_dir / f"{bex_id}.yaml"
      if not record_path.exists():
        return [f"bundle_exception_id {bex_id!r} が指定されているが承認レコードが存在しません"]
      # 存在する場合: covered_decision_ids に decision_id が含まれているか確認
      try:
        record = yaml.safe_load(record_path.read_text(encoding="utf-8"))
      except (OSError, yaml.YAMLError):
        return [f"bundle_exception_id {bex_id!r} の承認レコードを読み込めません"]
      decision_id = data.get("decision_id", "")
      covered = record.get("covered_decision_ids", [])
      if decision_id not in covered:
        return [f"承認レコード {bex_id!r} の covered_decision_ids に {decision_id!r} が含まれていません"]
    return []

  # multiplicity: bundled の場合: 3 条件すべてを確認
  errors = []
  bex_id = data.get("bundle_exception_id")
  decision_id = data.get("decision_id", "")

  if not bex_id:
    errors.append(
      "multiplicity: bundled ですが bundle_exception_id が設定されていません（束ね例外承認が必要）"
    )
    return errors

  exceptions_dir = Path(cwd) / BUNDLE_EXCEPTIONS_DIR
  record_path = exceptions_dir / f"{bex_id}.yaml"

  # (a) 承認レコードが存在する
  if not record_path.exists():
    errors.append(f"bundle_exception_id {bex_id!r} の承認レコードが存在しません")
    return errors

  try:
    record = yaml.safe_load(record_path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    errors.append(f"bundle_exception_id {bex_id!r} の承認レコードを読み込めません")
    return errors

  # (b) covered_decision_ids に含まれる
  covered = record.get("covered_decision_ids", [])
  if decision_id not in covered:
    errors.append(
      f"承認レコード {bex_id!r} の covered_decision_ids に {decision_id!r} が含まれていません"
    )

  # (c) multiplicity が single でなければならない（bundled のままなのでエラー）
  errors.append(
    "multiplicity が bundled のままです。例外承認後に各決定の multiplicity を single に更新してください"
  )

  return errors


# ──────────────────────────────────────────────
# テスト(3)(4) 逐語照合（design §3）
# ──────────────────────────────────────────────

def verify_excerpt_in_session(excerpt: str, session_path: Path) -> bool:
  """転写ファイル全文に対して正規化後の excerpt が含まれるかを検索する。"""
  try:
    content = session_path.read_text(encoding="utf-8")
  except OSError:
    return False
  norm_content = normalize_text(content)
  norm_excerpt = normalize_text(excerpt)
  return norm_excerpt in norm_content


# ──────────────────────────────────────────────
# テスト(7) decisions/ 直下のファイル収集（bundle-exceptions/ 除外）
# ──────────────────────────────────────────────

def collect_decision_files(cwd: Path) -> list:
  """decisions/ 直下の YAML ファイルのみを返す（bundle-exceptions/ サブディレクトリは除外）"""
  decisions_dir = Path(cwd) / DECISIONS_DIR
  if not decisions_dir.exists():
    return []
  return [
    f
    for f in decisions_dir.iterdir()
    if f.is_file() and f.suffix in (".yaml", ".yml")
    and f.parent == decisions_dir
  ]


# ──────────────────────────────────────────────
# 1 ファイルの lint（design §1〜§4）
# ──────────────────────────────────────────────

def lint_decision_file(path: Path, cwd: Path, config: dict) -> DecisionLintResult:
  """1 つの決定記録 YAML を lint する。"""
  messages = []

  # YAML パース
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError) as e:
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=[f"YAML パースエラー: {e}"],
    )

  if not isinstance(data, dict):
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=["決定記録がマッピングではありません"],
    )

  # スキーマ検査
  schema_errors = validate_decision_schema(data)
  if schema_errors:
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=schema_errors,
    )

  source = data["source"]
  excerpt = source.get("excerpt", "")
  mult = source.get("multiplicity", "")
  vs = data.get("verification_status", "")

  # 束ね例外チェック
  bundle_errors = check_bundle_exception(data, cwd)
  if bundle_errors:
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=bundle_errors,
    )

  # pending: WARN（確定済みとして扱わない、commit 遮断しない）
  if vs == "pending":
    return DecisionLintResult(
      verdict="WARN",
      exit_code=1,
      file_path=str(path),
      messages=["verification_status が pending です（未確認の決定、commit は遮断しない）"],
    )

  # unverifiable: DEVIATION
  if vs == "unverifiable":
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=["verification_status が unverifiable です（照合不能、commit を遮断）"],
    )

  # 内容なし語リスト判定
  if is_empty_content(excerpt, config):
    return DecisionLintResult(
      verdict="DEVIATION",
      exit_code=2,
      file_path=str(path),
      messages=[f"source.excerpt が内容なし語のみで構成されています: {excerpt!r}"],
    )

  # 逐語照合（verification_status: verified の場合のみ照合を実施）
  if vs == "verified":
    locator = source.get("locator", "")
    # locator からパス部分を取得（{パス}:{ターン番号} の形式）
    session_path_str = locator.split(":")[0] if ":" in locator else locator
    session_path = Path(cwd) / session_path_str

    if not session_path.exists():
      return DecisionLintResult(
        verdict="DEVIATION",
        exit_code=2,
        file_path=str(path),
        messages=[f"転写ファイルが存在しません: {session_path_str}"],
      )

    if not verify_excerpt_in_session(excerpt, session_path):
      norm_excerpt = normalize_text(excerpt)
      return DecisionLintResult(
        verdict="DEVIATION",
        exit_code=2,
        file_path=str(path),
        messages=[
          f"逐語照合不合格: source.excerpt が転写ファイルに見つかりません",
          f"  excerpt (正規化後): {norm_excerpt!r}",
          f"  転写ファイル: {session_path_str}",
        ],
      )

  return DecisionLintResult(
    verdict="OK",
    exit_code=0,
    file_path=str(path),
    messages=[],
  )


# ──────────────────────────────────────────────
# テスト(10) --all: 全ファイルの lint
# ──────────────────────────────────────────────

def run_decision_source_lint_all(cwd: Path) -> DecisionLintResult:
  """decisions/ 直下の全ファイルを lint し、最悪の verdict を返す。"""
  config = load_decision_source_lint_config(cwd)
  files = collect_decision_files(cwd)

  if not files:
    return DecisionLintResult(verdict="OK", exit_code=0, messages=["決定記録が 0 件（正常）"])

  worst_exit = 0
  worst_verdict = "OK"
  all_messages = []

  verdict_order = {"OK": 0, "WARN": 1, "DEVIATION": 2}
  for path in sorted(files):
    result = lint_decision_file(path, cwd, config)
    all_messages.extend([f"{result.file_path}: {m}" for m in result.messages])
    if verdict_order.get(result.verdict, 0) > verdict_order.get(worst_verdict, 0):
      worst_verdict = result.verdict
      worst_exit = result.exit_code

  return DecisionLintResult(
    verdict=worst_verdict,
    exit_code=worst_exit,
    messages=all_messages,
  )


# ──────────────────────────────────────────────
# テスト(8)(9) --verify-pending
# ──────────────────────────────────────────────

def run_verify_pending(cwd: Path) -> VerifyPendingResult:
  """verification_status: pending の決定を再照合し、合格すれば verified に更新する。"""
  from datetime import datetime, timezone

  config = load_decision_source_lint_config(cwd)
  files = collect_decision_files(cwd)
  updated = []
  failed = []
  messages = []

  for path in sorted(files):
    try:
      data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
      continue

    if not isinstance(data, dict):
      continue
    if data.get("verification_status") != "pending":
      continue

    # 照合
    source = data.get("source", {})
    excerpt = source.get("excerpt", "")
    locator = source.get("locator", "")
    session_path_str = locator.split(":")[0] if ":" in locator else locator
    session_path = Path(cwd) / session_path_str

    if not session_path.exists():
      messages.append(f"{path.name}: 転写ファイルが存在しません: {session_path_str}")
      failed.append(str(path))
      continue

    if verify_excerpt_in_session(excerpt, session_path):
      now = datetime.now(tz=timezone.utc).isoformat()
      data["verification_status"] = "verified"
      data["verified_at"] = now
      # 安全な書き込み（一時ファイル経由）
      tmp_path = path.with_suffix(".tmp")
      try:
        tmp_path.write_text(
          yaml.dump(data, allow_unicode=True, default_flow_style=False),
          encoding="utf-8",
        )
        tmp_path.replace(path)
        updated.append(str(path))
        messages.append(f"{path.name}: verified に更新しました")
      except OSError as e:
        if tmp_path.exists():
          tmp_path.unlink()
        messages.append(f"{path.name}: ファイル書き込みに失敗しました: {e}")
        failed.append(str(path))
    else:
      norm_excerpt = normalize_text(excerpt)
      messages.append(
        f"{path.name}: 逐語照合不合格（pending のまま）: excerpt={norm_excerpt!r}"
      )
      failed.append(str(path))

  exit_code = 1 if failed else 0
  return VerifyPendingResult(
    exit_code=exit_code,
    updated=updated,
    failed=failed,
    messages=messages,
  )
