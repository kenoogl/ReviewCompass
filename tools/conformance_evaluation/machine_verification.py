"""Machine verification for conformance-evaluation."""
import re
import subprocess
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


# 凍結済み旧配置（P3 まで読み取り互換のみ。新規追加・変更は凍結違反）
LEGACY_RECORD_PATTERN = re.compile(r"^\.reviewcompass/specs/[^/]+/conformance/")
LEGACY_ESTIMATION_LOG_PATTERN = re.compile(r"^logs/estimation/")


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
      log_dir = self.root / ".reviewcompass" / "evidence" / "estimation" / run_id
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

  def check_record_freeze(self, *, freeze_commit: str) -> VerificationResult:
    """評価記録の旧配置に対する凍結違反検出（design §18 凍結期の検査範囲）。

    凍結集合は P1 実装反映コミット時点の git 追跡履歴を正本とし、
    それ以降の旧配置への追加・変更を違反として検出する。
    `_cross_feature` は実 feature ではなく凍結対象外（tasks T-015）。
    """
    reasons = [
      reason
      for path, reason in self._legacy_violations(freeze_commit, LEGACY_RECORD_PATTERN)
      if not self._is_cross_feature_namespace(path)
    ]
    return VerificationResult(
      check_id="MV-3",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="recommended",
    )

  def check_estimation_log_freeze(self, *, freeze_commit: str) -> VerificationResult:
    """推定ログの旧ルート（logs/estimation/）に対する凍結違反検出。

    判定規則は評価記録と同一（P1 実装反映コミット以降の git 追跡履歴を正本とする）。
    """
    reasons = [reason for _, reason in self._legacy_violations(freeze_commit, LEGACY_ESTIMATION_LOG_PATTERN)]
    return VerificationResult(
      check_id="MV-6",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="recommended",
    )

  def check_existing_prompt_logs(self, *, forbidden_paths: list) -> VerificationResult:
    """既存推定ログ（凍結済み旧 logs/estimation/ を含む）への MV-6 の 2 条件適用。

    書き込みは常に新配置だが、読み取り検査は新旧両配置の prompt.log を対象とする
    （tasks T-012「凍結済み旧推定ログも MV-6 の読み取り対象に含める」）。
    """
    reasons = []
    log_roots = [
      self.root / ".reviewcompass" / "evidence" / "estimation",
      self.root / "logs" / "estimation",
    ]
    for log_root in log_roots:
      if not log_root.is_dir():
        continue
      for log_path in sorted(log_root.rglob("prompt.log")):
        prompt_text = self._extract_prompt_text(log_path.read_text(encoding="utf-8"))
        for path in forbidden_paths:
          if path in prompt_text:
            reasons.append(f"forbidden upstream path in log: {log_path}: {path}")
        if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
          reasons.append(f"missing autonomous exploration prohibition: {log_path}")
    return VerificationResult(
      check_id="MV-6",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="blocking",
    )

  @staticmethod
  def _extract_prompt_text(log_text: str) -> str:
    # ログには forbidden_paths 一覧自体が含まれるため、prompt_text 区画だけを検査対象にする
    lines = log_text.splitlines()
    try:
      start = lines.index("prompt_text:") + 1
    except ValueError:
      return log_text
    end = next((i for i in range(start, len(lines)) if lines[i] == "forbidden_paths:"), len(lines))
    return "\n".join(lines[start:end])

  @staticmethod
  def _is_cross_feature_namespace(path: str) -> bool:
    return path.split("/")[:3] == [".reviewcompass", "specs", "_cross_feature"]

  def _legacy_violations(self, freeze_commit: str, pattern: re.Pattern) -> list:
    """(path, reason) の組を返す。

    git ls-tree はワイルドカードを解釈しないため、木全体を列挙して Python 側で絞り込む。
    未追跡の列挙に --exclude-standard を付けない（ignore された旧配置追加も凍結違反として検出する）。
    """
    frozen = self._matching(pattern, "ls-tree", "-r", "--name-only", freeze_commit)
    tracked = self._matching(pattern, "ls-files")
    untracked = self._matching(pattern, "ls-files", "--others")
    changed = self._matching(pattern, "diff", "--name-only", freeze_commit)
    added = sorted((tracked | untracked) - frozen)
    modified = sorted(changed & frozen)
    return (
      [(path, f"added_after_freeze: {path}") for path in added]
      + [(path, f"frozen_file_changed: {path}") for path in modified]
    )

  def _matching(self, pattern: re.Pattern, *args) -> set:
    return {line for line in self._git_lines(*args) if pattern.match(line)}

  def _git_lines(self, *args) -> list:
    result = subprocess.run(
      ["git", "-C", str(self.root), *args],
      capture_output=True,
      text=True,
      check=True,
    )
    return [line for line in result.stdout.splitlines() if line]
