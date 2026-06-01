"""プロンプト解決機構（runtime tasks.md T-006）。

foundation 正本プロンプトと runtime 所有のフェーズ／役上書きプロンプトを 2 階層で解決する。
各段の記録に prompt_artifact_path／prompt_id／prompt_version／role を付与する。
一意解決できない場合は明示的に失敗し、リポジトリ外記憶への依存を禁止する。

解決順序（design.md §プロンプト解決モデル §解決順序）：
1. foundation 正本プロンプトパス（layer1_framework.yaml の asset_locations.prompts 経由）
2. runtime 所有の役／フェーズ上書きパス
3. 一意解決できない場合は明示的に失敗（要件 3 受入 4）

対応設計節：design.md §プロンプト解決モデル、§役と段の対応、§プロンプト上書きの選択
対応要件：Requirement 3（プロンプト解決と版追跡）、Requirement 8 受入 6（複数候補時の選択）
"""
from pathlib import Path

import yaml

_THIS_DIR = Path(__file__).resolve().parent
_DEFAULT_OVERRIDE_CONFIG = _THIS_DIR / "override_paths.yaml"
# repo_root（tests/runtime と同様、runtime/runtime_core/prompt_resolver から 3 階層上）
_DEFAULT_REPO_ROOT = _THIS_DIR.parents[2]


class PromptResolutionError(Exception):
  """プロンプトを一意に解決できない（未知の役・候補不在・あいまい）。"""


class RepoExternalPromptError(Exception):
  """解決パスがリポジトリ（prompts_root）外へ脱出した違反（要件 3 受入 5）。"""


def _parse_front_matter(text):
  """Markdown プロンプトの front-matter（先頭の --- で囲まれた YAML）を解析する。"""
  if not text.startswith("---"):
    return {}
  parts = text.split("---", 2)
  if len(parts) < 3:
    return {}
  return yaml.safe_load(parts[1]) or {}


class PromptResolver:
  """foundation 正本と runtime 上書きを 2 階層で解決するプロンプト解決器。"""

  def __init__(self, repo_root=None, prompts_root=None, override_config_path=None):
    self.repo_root = Path(repo_root or _DEFAULT_REPO_ROOT).resolve()
    config = yaml.safe_load(
      Path(override_config_path or _DEFAULT_OVERRIDE_CONFIG).read_text(encoding="utf-8")
    )
    self._role_step_map = config["role_step_map"]
    self._base_pattern = config["base_path_pattern"]
    self._override_pattern = config["override_path_pattern"]
    self._precedence = config["precedence"]

    if prompts_root is not None:
      self.prompts_root = Path(prompts_root).resolve()
    else:
      # foundation 正本プロンプトの所在を layer1_framework.yaml から解決する。
      framework = yaml.safe_load(
        (self.repo_root / "runtime/foundation/layer1_framework.yaml").read_text(encoding="utf-8")
      )
      prompts_rel = framework["asset_locations"]["prompts"]
      self.prompts_root = (self.repo_root / prompts_rel).resolve()

  def resolve(self, role, phase_profile=None):
    """役（と任意のフェーズプロファイル）からプロンプトを一意解決する。

    返り値：{prompt_artifact_path, prompt_id, prompt_version, role}
    """
    if role not in self._role_step_map:
      raise PromptResolutionError(
        f"未知の役：{role!r}（正本：{list(self._role_step_map.keys())}）"
      )
    step_dir = self._role_step_map[role]

    # 優先順位に従って候補パスを構築する。
    candidates = []
    for kind in self._precedence:
      if kind == "override":
        if phase_profile is None:
          continue
        rel = self._override_pattern.format(
          step_dir=step_dir, phase_profile=phase_profile, role=role
        )
      elif kind == "base":
        rel = self._base_pattern.format(step_dir=step_dir, role=role)
      else:
        continue
      candidates.append(self.prompts_root / rel)

    # リポジトリ外脱出の防御（要件 3 受入 5）。候補パス計算の段階で検査する。
    for candidate in candidates:
      self._assert_within_prompts_root(candidate)

    # 先頭から最初に実在する候補を採る（複数候補時の選択方針、要件 8 受入 6）。
    for candidate in candidates:
      if candidate.is_file():
        return self._build_identity(candidate, role)

    raise PromptResolutionError(
      f"プロンプトを一意解決できない：role={role!r}, phase_profile={phase_profile!r}"
    )

  def _assert_within_prompts_root(self, candidate):
    resolved = candidate.resolve()
    try:
      resolved.relative_to(self.prompts_root)
    except ValueError:
      raise RepoExternalPromptError(
        f"解決パスが prompts_root 外へ脱出：{resolved}（root={self.prompts_root}）"
      )

  def _build_identity(self, path, role):
    front = _parse_front_matter(path.read_text(encoding="utf-8"))
    return {
      "prompt_artifact_path": str(path),
      "prompt_id": front.get("prompt_id"),
      "prompt_version": front.get("version"),
      "role": role,
    }
