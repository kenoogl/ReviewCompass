"""T-001 のテスト：実行ディレクトリ構造と命名規約。

対応タスク：runtime tasks.md T-001
対応設計節：design.md §実行成果物配置、§配置の根拠、§配置の運用ルール
対応要件：Requirement 1 受入 6（実行ディレクトリ配置と段ファイル命名の所有）、
          Requirement 4 受入 1（foundation スキーマ準拠の実行レベル証拠出力）

テスト要件（tasks.md T-001 より）：
- 配置仕様 YAML の解析テスト
- 必須サブディレクトリ宣言の存在検査（6 件＝steps／decisions／
  failures/failure_observations／validation／derived ＋ ルート）
"""
from pathlib import Path

import pytest
import yaml

# リポジトリルート（tests/runtime/ から 2 階層上）
REPO_ROOT = Path(__file__).resolve().parents[2]

LAYOUT_SPEC = REPO_ROOT / "runtime/runtime_core/run_layout/layout_spec.yaml"
LAYOUT_README = REPO_ROOT / "runtime/runtime_core/run_layout/README.md"
RUNTIME_DOC = REPO_ROOT / "docs/operations/RUNTIME.md"

# design.md §実行成果物配置で正本とされた必須ディレクトリ 6 件
# （5 サブディレクトリ ＋ ルート「.」、tasks.md T-001 完了条件 1）
EXPECTED_REQUIRED_DIRS = {
  ".",
  "steps",
  "decisions",
  "failures/failure_observations",
  "validation",
  "derived",
}

# design.md §実行成果物配置のルート直下ファイル
EXPECTED_ROOT_FILES = {"run_manifest.yaml", "review_case.json"}


def _load_layout_spec():
  if not LAYOUT_SPEC.is_file():
    pytest.fail(f"配置仕様 YAML が存在しない：{LAYOUT_SPEC}")
  with LAYOUT_SPEC.open(encoding="utf-8") as f:
    return yaml.safe_load(f)


def test_layout_spec_exists():
  """layout_spec.yaml が存在する（成果物）。"""
  assert LAYOUT_SPEC.is_file(), f"layout_spec.yaml が存在しない：{LAYOUT_SPEC}"


def test_layout_readme_exists():
  """run_layout/README.md が存在する（成果物）。"""
  assert LAYOUT_README.is_file(), f"README.md が存在しない：{LAYOUT_README}"


def test_runtime_operations_doc_exists():
  """docs/operations/RUNTIME.md が存在する（成果物）。"""
  assert RUNTIME_DOC.is_file(), f"RUNTIME.md が存在しない：{RUNTIME_DOC}"


def test_layout_spec_is_parseable():
  """配置仕様 YAML が解析可能（テスト要件：YAML 解析テスト）。"""
  spec = _load_layout_spec()
  assert isinstance(spec, dict), "layout_spec.yaml がマッピングとして解析できない"


def test_layout_spec_declares_required_directories():
  """必須ディレクトリ 6 件が宣言されている（完了条件 1）。"""
  spec = _load_layout_spec()
  declared = {entry["path"] for entry in spec["required_directories"]}
  assert declared == EXPECTED_REQUIRED_DIRS, (
    f"必須ディレクトリの宣言が design.md §実行成果物配置 と一致しない：{declared}"
  )


def test_layout_spec_required_directory_count_is_6():
  """必須ディレクトリの宣言件数が 6 件（完了条件 1）。"""
  spec = _load_layout_spec()
  assert len(spec["required_directories"]) == 6, (
    "必須ディレクトリの宣言件数が 6 件でない"
  )


def test_layout_spec_each_directory_has_purpose():
  """各必須ディレクトリ宣言に配置目的（purpose）が記されている。"""
  spec = _load_layout_spec()
  for entry in spec["required_directories"]:
    assert entry.get("purpose"), f"配置目的が欠落：{entry.get('path')}"


def test_layout_spec_declares_root_files():
  """ルート直下ファイル（run_manifest.yaml／review_case.json）が宣言されている。"""
  spec = _load_layout_spec()
  declared = set(spec["root_files"])
  assert declared == EXPECTED_ROOT_FILES, (
    f"ルート直下ファイルの宣言が design.md と一致しない：{declared}"
  )


def test_layout_spec_declares_run_root():
  """実行ルートのパターン（experiments/runs/<run_id>）が宣言されている。"""
  spec = _load_layout_spec()
  assert "experiments/runs/" in spec.get("run_root", ""), (
    "run_root に experiments/runs/ のパターンが宣言されていない"
  )


def test_runtime_doc_describes_immutable_raw_evidence():
  """RUNTIME.md に生証拠不変の運用ルールが記述されている（完了条件 2）。"""
  text = RUNTIME_DOC.read_text(encoding="utf-8")
  assert "生証拠" in text and "不変" in text, (
    "RUNTIME.md に生証拠不変の運用ルール記述がない"
  )


def test_runtime_doc_describes_derived_separation():
  """RUNTIME.md に派生分離の運用ルールが記述されている（完了条件 2）。"""
  text = RUNTIME_DOC.read_text(encoding="utf-8")
  assert "派生" in text and "分離" in text, (
    "RUNTIME.md に派生分離の運用ルール記述がない"
  )


def test_runtime_doc_describes_review_case_single_truth():
  """RUNTIME.md に review_case.json 唯一の横断正本の運用ルールが記述されている（完了条件 2）。"""
  text = RUNTIME_DOC.read_text(encoding="utf-8")
  assert "review_case.json" in text and "横断正本" in text, (
    "RUNTIME.md に review_case.json 唯一の横断正本の記述がない"
  )
