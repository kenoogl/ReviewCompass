from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def guidance_path(filename):
  return ROOT / ".reviewcompass" / "guidance" / filename


def test_proxy_model_gate_requires_user_visible_review_run_summary():
  text = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")

  assert "proxy_model 判断依頼前の利用者提示ゲート" in text
  assert "この提示ゲートを完了する前に proxy_model を呼び出してはいけない" in text
  assert "使用 variant 名" in text
  assert "role ごとの path／provider／model" in text
  assert "三段階トリアージ案" in text
  assert "`must-fix` 候補ごとの平易な説明" in text


def test_approval_stage_is_human_only_and_proxy_model_is_limited_to_review_triage():
  guide = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")
  reopen = guidance_path("REOPEN_PROCEDURE.md").read_text(encoding="utf-8")
  design = ROOT / ".reviewcompass" / "specs" / "workflow-management" / "design.md"
  design_text = design.read_text(encoding="utf-8")

  assert "proxy_model は approval 段の代行主体ではなく" in design_text
  assert "人間承認段（actor=human）" in guide
  assert "proxy_model は approval 段の代行主体ではなく" in guide
  assert "review-run 後の重要件判断だけを代行できる" in guide
  assert "approval は人間の承認（actor=human）" in reopen
  assert "actor=human または proxy_model" not in guide
  assert "利用者または別モデル承認" not in guide
  assert "actor=human または proxy_model" not in reopen


def test_workflow_navigation_exposes_triad_review_proxy_gate():
  text = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "`stage` が `triad-review` の場合" in text
  assert "使用 variant と role ごとの path／provider／model" in text
  assert "proxy_model 判断依頼" in text
  assert "三段階トリアージ案" in text
  assert "利用者へ提示して停止" in text


def test_workflow_navigation_defines_work_mode_taxonomy_terms():
  text = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "作業モード分類の用語表" in text
  assert "`current_state`" in text
  assert "`work_class`" in text
  assert "`control_relation`" in text
  assert "`permitted_scope`" in text
  assert "`work_context`" in text
  assert "maintenance は作業区分" in text
  assert "side-track は本線との関係" in text
  assert "blocking unit は親作業に束縛された制御構造" in text
  assert "単一 enum に押し込まない" in text
  assert "work mode taxonomy" in text


def test_workflow_navigation_requires_taxonomy_fields_for_maintenance_yaml():
  text = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "少なくとも `trigger`、`mainline_blocked_by`、`work_class`、`control_relation`" in text
  assert "`work_class: maintenance`" in text
  assert "`control_relation: side-track`" in text


def test_workflow_navigation_classifies_completed_entry_paths():
  text = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "completed からの作業開始分類" in text
  assert "局所的な運用・検査器・手引き補修" in text
  assert "既存正本の意味変更や下流再実施が必要" in text
  assert "既存 feature の責務境界に収まらない新しい責務" in text
  assert "判断が分かれる場合は候補だけを提示し、人間判断を待つ" in text


def test_reopen_drafting_is_required_before_triad_review():
  navigation = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")
  reopen = guidance_path("REOPEN_PROCEDURE.md").read_text(encoding="utf-8")
  discipline_map = guidance_path("WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "`run_reopen_drafting`" in navigation
  assert "`drafting_completed_gates`" in navigation
  assert "triad-review の前に drafting" in reopen
  assert "drafting_completed_gates" in reopen
  assert "reopen_procedure_state" in discipline_map


def test_codex_adapter_exposes_triad_review_proxy_gate():
  text = (
    ROOT / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION_FOR_CODEX.md"
  ).read_text(encoding="utf-8")

  assert "`triad-review` の API review-run を開始する前" in text
  assert "使用 variant と role ごとの path／provider／model" in text
  assert "利用者提示ゲートを完了するまで" in text
  assert "proxy_model 判断依頼" in text


def test_discipline_map_surfaces_user_visible_triad_review_gate():
  text = guidance_path("WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "variant/role assignments" in text
  assert "same-root finding clusters" in text
  assert "user-visible triage gate" in text
  assert "variant-role-assignment" in text
  assert "user-visible-triage-gate" in text


def test_requirements_vertical_review_scope_is_not_downstream_review():
  guide = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")
  discipline_map = guidance_path("WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "requirements review" in guide
  assert "上流判断材料 → requirements.md" in guide
  assert "design.md / tasks.md は参照資料であり、審査対象ではない" in guide
  assert "review target / source materials / out of scope" in guide
  assert "requirements:" in discipline_map
  assert "upstream_decision_materials" in discipline_map
  assert "review_target: requirements.md" in discipline_map
  assert "downstream_artifacts_not_review_target" in discipline_map


def test_vertical_review_prompt_must_materialize_upstream_content():
  guide = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")
  discipline_map = guidance_path("WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert "source materials をパス名だけで列挙してはならない" in guide
  assert "上流本文または要点抽出" in guide
  assert "上流資料を読んでいない場合は review-run を開始してはならない" in guide
  assert "prompt_materialization_contract" in discipline_map
  assert "source_materials_must_not_be_path_only" in discipline_map
  assert "upstream_excerpt_or_structured_summary" in discipline_map
  assert "block_review_run_when_upstream_material_unread" in discipline_map


def test_cross_feature_stage_artifacts_have_canonical_location():
  navigation = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")
  discipline_map = guidance_path("WORKFLOW_DISCIPLINE_MAP.yaml").read_text(encoding="utf-8")

  assert ".reviewcompass/specs/_cross_feature/reviews/" in navigation
  assert "cross_feature_stage_artifacts" in discipline_map
  assert ".reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md" in discipline_map


def test_cross_feature_stage_autonomous_parallel_dependency_gate_is_canonical():
  navigation = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "自律・並列" in navigation
  assert "`autonomous-plan`" in navigation
  assert "`recheck_items` と `stages/feature-dependency.yaml`" in navigation
  assert "読取調査または差分を残さない確認" in navigation
  assert "新しい依存、暗黙依存、未記録依存" in navigation
  assert "機能横断段の実施記録" in navigation


def test_post_write_verification_command_uses_explicit_api_variant():
  navigation = guidance_path("WORKFLOW_NAVIGATION.md").read_text(encoding="utf-8")

  assert "--variant post_write_verification_google" in navigation
  post_write_section = navigation.split("### `post_write_verification`", 1)[1].split(
    "### `post_write_policy_violation`",
    1,
  )[0]
  assert "--variant <post-write-api-variant>" in post_write_section


def test_post_write_verification_documents_canonical_api_call_procedure_without_approval_guard():
  for navigation_path in [
    guidance_path("WORKFLOW_NAVIGATION.md"),
  ]:
    navigation = navigation_path.read_text(encoding="utf-8")
    post_write_section = navigation.split("### `post_write_verification`", 1)[1].split(
      "### `post_write_policy_violation`",
      1,
    )[0]

    assert "API 呼び出し起動手順の正本" in post_write_section
    assert ".venv/bin/python3 tools/api_providers/prepare_post_write_review.py" in post_write_section
    assert ".venv/bin/python3 tools/api_providers/run_review.py" in post_write_section
    assert "--criteria-file" in post_write_section
    assert "review-target.md" in post_write_section
    assert "--source-material" in post_write_section
    assert "--prompt-manifest-path" in post_write_section
    assert "prompt-manifest.yaml" in post_write_section
    assert "source materials" in post_write_section
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
    assert "prompts/" in post_write_section
  assert "target-manifest.yaml" in post_write_section
  assert "ConnectError" in post_write_section
  assert "sandbox network" in post_write_section
  assert "API key" in post_write_section
  assert "import" in post_write_section
  assert "argparse" in post_write_section
  assert "zsh -c 'source ~/.zshrc && .venv/bin/python3 tools/api_providers/run_review.py" not in post_write_section
  assert "external-api-approval" not in post_write_section
  assert "--external-api-approval-record" not in post_write_section


def test_codex_commit_sandbox_external_wrapper_is_starting_condition():
  precheck = guidance_path("WORKFLOW_PRECHECK.md").read_text(encoding="utf-8")
  details = guidance_path("WORKFLOW_PRECHECK_DETAILS.md").read_text(encoding="utf-8")
  codex = (
    ROOT / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION_FOR_CODEX.md"
  ).read_text(encoding="utf-8")
  card = guidance_path("COMMIT_OPERATION_CARD.md").read_text(encoding="utf-8")

  for text in (precheck, details, codex, card):
    assert "commit wrapper 本体を最初から sandbox 外" in text
    assert "先に sandbox 内で失敗させてから再実行" in text


def test_sandbox_non_tty_guarded_commit_issue_is_closed_by_commit_card_contract():
  card = guidance_path("COMMIT_OPERATION_CARD.md").read_text(encoding="utf-8")
  issue = (
    ROOT
    / ".reviewcompass"
    / "backlog"
    / "issues"
    / "issue-2026-06-24-sandbox-guarded-commit-blocked.yaml"
  ).read_text(encoding="utf-8")
  index = (ROOT / ".reviewcompass" / "backlog" / "index.yaml").read_text(
    encoding="utf-8")

  assert "status: completed" in issue
  assert "擬似端末（PTY" in card
  assert "直近の利用者発話で明示された commit 指示の一行だけを流す" in card
  assert "commit wrapper 本体を最初から sandbox 外" in card
  assert "wrapper を経由せず承認レコードを内部関数で自作する" in card
  assert "issue-2026-06-24-sandbox-guarded-commit-blocked" in index
  assert "status: completed" in index.split(
    "issue-2026-06-24-sandbox-guarded-commit-blocked", 1)[1].split(
      "created_at:", 1)[0]


def test_user_facing_reports_avoid_translation_style_japanese():
  guide = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")

  assert "翻訳調の名詞句" in guide
  assert "内部状態名や英語の道具名を見出しや主語にしない" in guide
  assert "利用者が次に何をすればよいかを自然な日本語の文で示す" in guide


def test_codex_commit_message_does_not_require_japanese_imperative_form():
  codex = (
    ROOT / ".reviewcompass" / "guidance" / "WORKFLOW_NAVIGATION_FOR_CODEX.md"
  ).read_text(encoding="utf-8")

  assert "変更の目的が伝わる短い日本語" in codex
  assert "命令形" not in codex


def test_commit_progress_reports_hide_internal_repreparation_steps():
  guide = guidance_path("SESSION_WORKFLOW_GUIDE.md").read_text(encoding="utf-8")
  card = guidance_path("COMMIT_OPERATION_CARD.md").read_text(encoding="utf-8")

  for text in (guide, card):
    assert "承認内容を作り直す" in text
    assert "承認済みの対象範囲内" in text
    assert "コミット対象が増えた" in text
    assert "再承認が必要" in text
    assert "短く報告" in text
