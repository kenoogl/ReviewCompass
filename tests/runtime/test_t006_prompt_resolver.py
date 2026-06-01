"""T-006 のテスト：プロンプト解決機構。

対応タスク：runtime tasks.md T-006
対応設計節：design.md §プロンプト解決モデル、§フェーズ対応レビュープロファイル
          §プロンプト上書きの選択
対応要件：Requirement 3（プロンプト解決と版追跡）、Requirement 8 受入 6（複数候補時の選択）

テスト要件（tasks.md T-006 より）：
- 正常解決テスト
- 複数候補時の選択テスト
- 一意解決失敗時の失敗テスト（リポジトリ外パスの拒否を含む）
"""
from pathlib import Path

import pytest

from runtime_core.prompt_resolver.resolver import (
  PromptResolver,
  PromptResolutionError,
  RepoExternalPromptError,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OVERRIDE_PATHS = REPO_ROOT / "runtime/runtime_core/prompt_resolver/override_paths.yaml"


def test_override_paths_config_exists():
  """override_paths.yaml が存在する（成果物）。"""
  assert OVERRIDE_PATHS.is_file(), f"存在しない：{OVERRIDE_PATHS}"


def test_resolve_foundation_base_prompt():
  """正常解決：foundation 正本プロンプトを役名から解決する（完了条件 1）。"""
  resolver = PromptResolver(repo_root=REPO_ROOT)
  result = resolver.resolve(role="primary_reviewer")
  assert result["role"] == "primary_reviewer"
  assert result["prompt_id"] == "primary_reviewer"
  assert result["prompt_version"] == "B1.0"
  # 解決パスが実在するリポジトリ内ファイル
  assert Path(result["prompt_artifact_path"]).is_file()
  assert "primary_detection/primary_reviewer.prompt.md" in result["prompt_artifact_path"]


def test_resolve_records_required_identity_fields():
  """各役の解決結果が識別子 4 項目を持つ（design.md §プロンプト識別子の記録）。"""
  resolver = PromptResolver(repo_root=REPO_ROOT)
  for role in ("primary_reviewer", "adversarial_reviewer", "judgment_reviewer"):
    result = resolver.resolve(role=role)
    for key in ("prompt_artifact_path", "prompt_id", "prompt_version", "role"):
      assert key in result, f"{role} の解決結果に {key} が欠落"


def test_resolve_unknown_role_fails():
  """未知の役は明示的失敗（完了条件 3）。"""
  resolver = PromptResolver(repo_root=REPO_ROOT)
  with pytest.raises(PromptResolutionError):
    resolver.resolve(role="unknown_reviewer")


def test_resolve_no_candidate_fails(tmp_path):
  """候補プロンプトが存在しない場合は明示的失敗（完了条件 3）。"""
  # 空の prompts_root を与える（base も override も存在しない）
  (tmp_path / "primary_detection").mkdir(parents=True)
  resolver = PromptResolver(repo_root=tmp_path, prompts_root=tmp_path)
  with pytest.raises(PromptResolutionError):
    resolver.resolve(role="primary_reviewer")


def test_override_takes_precedence_over_base(tmp_path):
  """複数候補時：phase 上書きが foundation 正本より優先される（完了条件 2）。"""
  # base
  base_dir = tmp_path / "primary_detection"
  base_dir.mkdir(parents=True)
  base_file = base_dir / "primary_reviewer.prompt.md"
  base_file.write_text(
    "---\nprompt_id: primary_reviewer\nversion: BASE\nrole: primary_reviewer\n---\nbase",
    encoding="utf-8",
  )
  # override（design 用）
  override_dir = base_dir / "overrides" / "design"
  override_dir.mkdir(parents=True)
  override_file = override_dir / "primary_reviewer.prompt.md"
  override_file.write_text(
    "---\nprompt_id: primary_reviewer_design\nversion: OVR\nrole: primary_reviewer\n---\noverride",
    encoding="utf-8",
  )
  resolver = PromptResolver(repo_root=tmp_path, prompts_root=tmp_path)
  result = resolver.resolve(role="primary_reviewer", phase_profile="design")
  assert result["prompt_version"] == "OVR", "override が優先されていない"
  assert "overrides/design" in result["prompt_artifact_path"]


def test_no_override_falls_back_to_base(tmp_path):
  """phase 上書きが無い場合は foundation 正本に解決される。"""
  base_dir = tmp_path / "primary_detection"
  base_dir.mkdir(parents=True)
  (base_dir / "primary_reviewer.prompt.md").write_text(
    "---\nprompt_id: primary_reviewer\nversion: BASE\nrole: primary_reviewer\n---\nbase",
    encoding="utf-8",
  )
  resolver = PromptResolver(repo_root=tmp_path, prompts_root=tmp_path)
  result = resolver.resolve(role="primary_reviewer", phase_profile="design")
  assert result["prompt_version"] == "BASE"


def test_repo_external_path_rejected(tmp_path):
  """リポジトリ外へ脱出するパスを拒否する（完了条件 3、リポジトリ外パス拒否）。"""
  base_dir = tmp_path / "primary_detection"
  base_dir.mkdir(parents=True)
  (base_dir / "primary_reviewer.prompt.md").write_text(
    "---\nprompt_id: x\nversion: v\nrole: primary_reviewer\n---\nx",
    encoding="utf-8",
  )
  resolver = PromptResolver(repo_root=tmp_path, prompts_root=tmp_path)
  # phase_profile に脱出パスを与えると override パス計算がリポジトリ外を指す
  with pytest.raises(RepoExternalPromptError):
    resolver.resolve(role="primary_reviewer", phase_profile="../../../../etc")
