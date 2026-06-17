from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_proxy_model_gate_requires_user_visible_review_run_summary():
  text = (ROOT / "docs" / "operations" / "SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")

  assert "proxy_model 判断依頼前の利用者提示ゲート" in text
  assert "この提示ゲートを完了する前に proxy_model を呼び出してはいけない" in text
  assert "使用 variant 名" in text
  assert "role ごとの path／provider／model" in text
  assert "三段階トリアージ案" in text
  assert "`must-fix` 候補ごとの平易な説明" in text


def test_workflow_navigation_exposes_triad_review_proxy_gate():
  text = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "`stage` が `triad-review` の場合" in text
  assert "使用 variant と role ごとの path／provider／model" in text
  assert "proxy_model 判断依頼" in text
  assert "三段階トリアージ案" in text
  assert "利用者へ提示して停止" in text


def test_reopen_drafting_is_required_before_triad_review():
  navigation = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")
  reopen = (ROOT / "docs" / "operations" / "REOPEN_PROCEDURE.md").read_text(encoding="utf-8")
  discipline_map = (ROOT / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "`run_reopen_drafting`" in navigation
  assert "`drafting_completed_gates`" in navigation
  assert "triad-review の前に drafting" in reopen
  assert "drafting_completed_gates" in reopen
  assert "reopen_procedure_state" in discipline_map


def test_codex_adapter_exposes_triad_review_proxy_gate():
  text = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION_FOR_CODEX.md").read_text(encoding="utf-8")

  assert "`triad-review` の API review-run を開始する前" in text
  assert "使用 variant と role ごとの path／provider／model" in text
  assert "利用者提示ゲートを完了するまで" in text
  assert "proxy_model 判断依頼" in text


def test_discipline_map_surfaces_user_visible_triad_review_gate():
  text = (ROOT / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "variant/role assignments" in text
  assert "same-root finding clusters" in text
  assert "user-visible triage gate" in text
  assert "variant-role-assignment" in text
  assert "user-visible-triage-gate" in text


def test_cross_feature_stage_artifacts_have_canonical_location():
  navigation = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")
  discipline_map = (ROOT / "docs" / "operations" / "WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert ".reviewcompass/specs/_cross_feature/reviews/" in navigation
  assert "cross_feature_stage_artifacts" in discipline_map
  assert ".reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md" in discipline_map


def test_cross_feature_stage_autonomous_parallel_dependency_gate_is_canonical():
  navigation = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "自律・並列" in navigation
  assert "`autonomous-plan`" in navigation
  assert "`recheck_items` と `stages/feature-dependency.yaml`" in navigation
  assert "読取調査または差分を残さない確認" in navigation
  assert "新しい依存、暗黙依存、未記録依存" in navigation
  assert "機能横断段の実施記録" in navigation


def test_post_write_verification_command_uses_explicit_api_variant():
  navigation = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "--variant post_write_verification_google" in navigation
  post_write_section = navigation.split("### `post_write_verification`", 1)[1].split(
    "### `post_write_policy_violation`",
    1,
  )[0]
  assert "--variant <post-write-api-variant>" in post_write_section


def test_post_write_verification_documents_canonical_api_call_procedure_without_approval_guard():
  navigation = (ROOT / "docs" / "operations" / "WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")
  post_write_section = navigation.split("### `post_write_verification`", 1)[1].split(
    "### `post_write_policy_violation`",
    1,
  )[0]

  assert "API 呼び出し起動手順の正本" in post_write_section
  assert ".venv/bin/python3 tools/api_providers/run_review.py" in post_write_section
  assert "外側から `zsh -c` で包まない" in post_write_section
  assert "entrypoint 内" in post_write_section
  assert "~/.zshrc" in post_write_section
  assert "tools/api_providers/run_review.py" in post_write_section
  assert "ANTHROPIC_API_KEY" in post_write_section
  assert "GEMINI_API_KEY" in post_write_section
  assert "空文字列へ上書き" in post_write_section
  assert "OPENAI_API_KEY" in post_write_section
  assert "上書きされていない" in post_write_section
  assert "review_summary.md" in post_write_section
  assert "rounds.yaml" in post_write_section
  assert "target-manifest.yaml" in post_write_section
  assert "ConnectError" in post_write_section
  assert "sandbox network" in post_write_section
  assert "API key" in post_write_section
  assert "import" in post_write_section
  assert "argparse" in post_write_section
  assert "zsh -c 'source ~/.zshrc && .venv/bin/python3 tools/api_providers/run_review.py" not in post_write_section
  assert "external-api-approval" not in post_write_section
  assert "--external-api-approval-record" not in post_write_section
