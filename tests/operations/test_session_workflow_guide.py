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
