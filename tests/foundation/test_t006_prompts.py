"""T-006 のテスト：プロンプト雛形 3 件。

対応タスク：foundation tasks.md T-006
対応設計節：design.md §6 プロンプト成果物モデル、§配置決定 3
対応要件：Requirement 4（プロンプトの正本配置）

テスト要件（tasks.md T-006 より）：
- 3 ファイルの frontmatter 解析テスト
- 必須項目 6 件の存在テスト
- role / step 値の整合テスト（step は 3 値の enum 検証を含む、topic-16 A-006）
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / "runtime/prompts"

# (相対パス, 期待 role, 期待 step) の対応（design.md §配置決定 3）
PROMPT_SPECS = [
  ("primary_detection/primary_reviewer.prompt.md", "primary_reviewer", "primary_detection"),
  ("adversarial_review/adversarial_reviewer.prompt.md", "adversarial_reviewer", "adversarial_review"),
  ("judgment/judgment_reviewer.prompt.md", "judgment_reviewer", "judgment"),
]

# frontmatter 必須 6 項目（design.md §6）
REQUIRED_FRONTMATTER_KEYS = [
  "prompt_id", "version", "role", "step", "language", "source_ref",
]

# step キーの値域（Step D integration はプロンプトを持たない）
STEP_ENUM = ["primary_detection", "adversarial_review", "judgment"]


def _parse_frontmatter(rel_path):
  """*.prompt.md の先頭 frontmatter（--- で囲まれた YAML 区画）を解析して返す。"""
  path = PROMPTS_DIR / rel_path
  if not path.is_file():
    pytest.fail(f"プロンプト雛形が存在しない：{rel_path}")
  text = path.read_text(encoding="utf-8")
  if not text.startswith("---"):
    pytest.fail(f"frontmatter が --- で始まっていない：{rel_path}")
  # 先頭の --- から次の --- までを取り出す
  parts = text.split("---", 2)
  if len(parts) < 3:
    pytest.fail(f"frontmatter の区切り（---）が 2 つ揃っていない：{rel_path}")
  return yaml.safe_load(parts[1])


@pytest.mark.parametrize("rel_path,_role,_step", PROMPT_SPECS)
def test_frontmatter_parses(rel_path, _role, _step):
  """3 ファイルの frontmatter が YAML として解析可能で辞書である。"""
  fm = _parse_frontmatter(rel_path)
  assert isinstance(fm, dict), f"frontmatter が辞書でない：{rel_path}"


@pytest.mark.parametrize("rel_path,_role,_step", PROMPT_SPECS)
def test_frontmatter_required_keys(rel_path, _role, _step):
  """frontmatter が必須 6 項目をすべて持つ。"""
  fm = _parse_frontmatter(rel_path)
  for key in REQUIRED_FRONTMATTER_KEYS:
    assert key in fm, f"{rel_path} の frontmatter に必須項目が欠落：{key}"


@pytest.mark.parametrize("rel_path,role,step", PROMPT_SPECS)
def test_role_and_step_consistency(rel_path, role, step):
  """各プロンプトの role / step が正本の組み合わせと一致する。"""
  fm = _parse_frontmatter(rel_path)
  assert fm.get("role") == role, f"{rel_path} の role が一致しない：{fm.get('role')}"
  assert fm.get("step") == step, f"{rel_path} の step が一致しない：{fm.get('step')}"


@pytest.mark.parametrize("rel_path,_role,_step", PROMPT_SPECS)
def test_step_value_in_enum(rel_path, _role, _step):
  """step キーの値が 3 値の enum に含まれる（topic-16 A-006）。"""
  fm = _parse_frontmatter(rel_path)
  assert fm.get("step") in STEP_ENUM, (
    f"{rel_path} の step が enum 外：{fm.get('step')}"
  )
