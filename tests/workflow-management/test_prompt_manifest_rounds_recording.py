"""T-018 prompt manifest rounds recording red tests."""

import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "api_providers"))

from run_role import update_review_run_artifacts  # noqa: E402


class PromptManifestRoundsRecordingTests(unittest.TestCase):
  def test_rounds_records_prompt_manifest_without_removing_text_prompt_fields(self):
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      target = tmp_path / "target.md"
      target.write_text("# Target\n", encoding="utf-8")
      effective_prompt = tmp_path / "effective.prompt.md"
      effective_prompt.write_text("Read the target.", encoding="utf-8")
      prompt_manifest = tmp_path / "effective.prompt.yaml"
      prompt_manifest.write_text("schema_version: effective-prompt-manifest-v1\n", encoding="utf-8")
      run_dir = tmp_path / "review-run"

      update_review_run_artifacts(
        str(run_dir),
        round_id="round-1",
        target_path=str(target),
        phase="design",
        criteria="criteria",
        role="primary",
        provider="local",
        model="model-a",
        prompt="prompt text",
        response_text="- none",
        attempts=1,
        duration_seconds=0.1,
        parse_status="parsed",
        findings=[],
        formatted_output="findings: []\n",
        effective_prompt_path=str(effective_prompt),
        effective_prompt_sha256="sha256:" + "a" * 64,
        prompt_manifest_path=str(prompt_manifest),
        prompt_manifest_sha256="sha256:" + "b" * 64,
      )

      rounds = yaml.safe_load((run_dir / "rounds.yaml").read_text(encoding="utf-8"))
      self.assertEqual(rounds["effective_prompt_path"], str(effective_prompt))
      self.assertEqual(rounds["effective_prompt_sha256"], "sha256:" + "a" * 64)
      self.assertEqual(rounds["prompt_manifest_path"], str(prompt_manifest))
      self.assertEqual(rounds["prompt_manifest_sha256"], "sha256:" + "b" * 64)


if __name__ == "__main__":
  unittest.main()
