# tools/api_providers/tests/test_prepare_post_write_review.py
# post-write API 検査前の review-target 生成テスト。

import hashlib
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.prepare_post_write_review import main


def test_prepare_post_write_review_writes_review_target_and_metadata(tmp_path):
  """対象・観点・機微情報確認を review-run 配下に機械生成する。"""
  target = tmp_path / "docs" / "operations" / "WORKFLOW_PRECHECK.md"
  target.parent.mkdir(parents=True)
  target.write_text("commit preflight contract\n", encoding="utf-8")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "commit_instruction_preflight_contract_clearance",
      "--change-summary", "commit 指示後の preflight 契約を文書へ反映した。",
      "--review-question", "commit 指示後、git add より前に preflight が走る契約が明確か。",
    ]
  )

  assert exit_code == 0
  review_target = review_run_dir / "review-target.md"
  metadata_path = review_run_dir / "review-target.yaml"
  assert review_target.is_file()
  assert metadata_path.is_file()
  content = review_target.read_text(encoding="utf-8")
  assert "commit_instruction_preflight_contract_clearance" in content
  assert "git add より前" in content
  assert "Sensitive Information Check" in content
  metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
  assert metadata["criteria_file"] == str(review_target)
  assert metadata["criteria_file_sha256"] == hashlib.sha256(
    review_target.read_bytes()
  ).hexdigest()
  assert metadata["sensitive_information_check"]["status"] == "passed"
  assert metadata["target_files"][0]["sha256"] == hashlib.sha256(
    target.read_bytes()
  ).hexdigest()


def test_prepare_post_write_review_fails_closed_on_secret_like_target(tmp_path):
  """外部 API に送る前に secret らしい対象を止める。"""
  target = tmp_path / "docs" / "operations" / "SECRET.md"
  target.parent.mkdir(parents=True)
  target.write_text("OPENAI_API_KEY=sk-testsecret\n", encoding="utf-8")
  review_run_dir = tmp_path / ".reviewcompass" / "evidence" / "review-runs" / "run"

  exit_code = main(
    [
      "--target", str(target),
      "--review-run-dir", str(review_run_dir),
      "--criteria-id", "secret_check",
      "--change-summary", "secret check",
    ]
  )

  assert exit_code == 2
  assert not (review_run_dir / "review-target.md").exists()
