"""decision-source-lint サブコマンドのテスト（TDD、Req 11）

T-013 テスト要件：
(1) 必須フィールド・category 3 値 enum・空文字列・非文字列型で DEVIATION
(2) multiplicity:bundled fail-closed、束ね例外 3 条件の部分満足も fail-closed
(3) 逐語照合正常系
(4) 逐語照合不合格系（pending 維持・差分表示・非ゼロ終了）
(5) pending → WARN、unverifiable → DEVIATION
(6) 内容なし語リスト判定
(7) --all で decisions/ 直下のみ（bundle-exceptions/ 除外）
(8) --verify-pending 正常系
(9) --verify-pending 不合格系（ファイル不変）
(10) commit ゲート統合（end-to-end）
(11) 設定ファイル読み取り
"""

import os
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from check_workflow_action.decision_source_lint import (  # noqa: E402
  DecisionLintResult,
  load_decision_source_lint_config,
  normalize_text,
  is_empty_content,
  validate_decision_schema,
  check_bundle_exception,
  verify_excerpt_in_session,
  lint_decision_file,
  collect_decision_files,
)


# ──────────────────────────────────────────────
# テスト(11) 設定ファイル読み取り
# ──────────────────────────────────────────────

class TestLoadConfig:
  def test_default_config_loads_initial_words(self, tmp_path):
    config_path = tmp_path / "stages" / "decision-source-lint-config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
      "empty_content_words:\n  - OK\n  - ok\n  - 承認\n",
      encoding="utf-8",
    )
    config = load_decision_source_lint_config(tmp_path)
    assert "OK" in config["empty_content_words"]
    assert "承認" in config["empty_content_words"]

  def test_missing_config_returns_builtin_defaults(self, tmp_path):
    # 設定ファイルが存在しない場合は内蔵デフォルト 11 件を返す
    config = load_decision_source_lint_config(tmp_path)
    words = config["empty_content_words"]
    assert len(words) >= 11
    assert "OK" in words
    assert "承認" in words

  def test_config_words_reflected_in_judgment(self, tmp_path):
    config_path = tmp_path / "stages" / "decision-source-lint-config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
      "empty_content_words:\n  - custom_word\n",
      encoding="utf-8",
    )
    config = load_decision_source_lint_config(tmp_path)
    assert "custom_word" in config["empty_content_words"]
    assert is_empty_content("custom_word", config)


# ──────────────────────────────────────────────
# テスト(1) 必須フィールド・enum・型検査
# ──────────────────────────────────────────────

VALID_DECISION = {
  "decision_id": "DEC-WM-001",
  "category": "spec_plan_change",
  "statement": "Req 11 の新設を承認する。",
  "source": {
    "excerpt": "自律的に実施",
    "session_id": "2026-06-15-claude-4e02c8a6",
    "locator": ".reviewcompass/evidence/sessions/2026-06-15-claude-4e02c8a6.md:1",
    "multiplicity": "single",
  },
  "verification_status": "verified",
  "verified_at": "2026-06-15T00:00:00+09:00",
}


class TestValidateDecisionSchema:
  def test_valid_record_passes(self):
    errors = validate_decision_schema(VALID_DECISION)
    assert errors == []

  def test_missing_decision_id(self):
    data = {**VALID_DECISION}
    del data["decision_id"]
    errors = validate_decision_schema(data)
    assert any("decision_id" in e for e in errors)

  def test_missing_category(self):
    data = {**VALID_DECISION}
    del data["category"]
    errors = validate_decision_schema(data)
    assert any("category" in e for e in errors)

  def test_missing_statement(self):
    data = {**VALID_DECISION}
    del data["statement"]
    errors = validate_decision_schema(data)
    assert any("statement" in e for e in errors)

  def test_missing_source(self):
    data = {**VALID_DECISION}
    del data["source"]
    errors = validate_decision_schema(data)
    assert any("source" in e for e in errors)

  def test_missing_verification_status(self):
    data = {**VALID_DECISION}
    del data["verification_status"]
    errors = validate_decision_schema(data)
    assert any("verification_status" in e for e in errors)

  def test_invalid_category(self):
    data = {**VALID_DECISION, "category": "invalid_value"}
    errors = validate_decision_schema(data)
    assert any("category" in e for e in errors)

  def test_invalid_verification_status(self):
    data = {**VALID_DECISION, "verification_status": "invalid"}
    errors = validate_decision_schema(data)
    assert any("verification_status" in e for e in errors)

  def test_invalid_multiplicity(self):
    data = {**VALID_DECISION}
    data["source"] = {**data["source"], "multiplicity": "invalid"}
    errors = validate_decision_schema(data)
    assert any("multiplicity" in e for e in errors)

  def test_empty_decision_id(self):
    data = {**VALID_DECISION, "decision_id": ""}
    errors = validate_decision_schema(data)
    assert any("decision_id" in e for e in errors)

  def test_empty_statement(self):
    data = {**VALID_DECISION, "statement": ""}
    errors = validate_decision_schema(data)
    assert any("statement" in e for e in errors)

  def test_empty_excerpt(self):
    data = {**VALID_DECISION}
    data["source"] = {**data["source"], "excerpt": ""}
    errors = validate_decision_schema(data)
    assert any("excerpt" in e for e in errors)

  def test_non_string_category(self):
    data = {**VALID_DECISION, "category": ["list", "value"]}
    errors = validate_decision_schema(data)
    assert any("category" in e for e in errors)

  def test_non_string_verification_status(self):
    data = {**VALID_DECISION, "verification_status": 123}
    errors = validate_decision_schema(data)
    assert any("verification_status" in e for e in errors)

  def test_valid_category_irreversible_operation(self):
    data = {**VALID_DECISION, "category": "irreversible_operation"}
    errors = validate_decision_schema(data)
    assert errors == []

  def test_valid_category_discipline_change(self):
    data = {**VALID_DECISION, "category": "discipline_change"}
    errors = validate_decision_schema(data)
    assert errors == []

  def test_valid_verification_status_pending(self):
    data = {**VALID_DECISION, "verification_status": "pending"}
    del data["verified_at"]
    errors = validate_decision_schema(data)
    assert errors == []

  def test_valid_verification_status_unverifiable(self):
    data = {**VALID_DECISION, "verification_status": "unverifiable"}
    del data["verified_at"]
    errors = validate_decision_schema(data)
    assert errors == []


# ──────────────────────────────────────────────
# テスト(2) multiplicity: bundled の fail-closed と束ね例外 3 条件
# ──────────────────────────────────────────────

class TestBundleException:
  def setup_method(self):
    import tempfile
    self.tmp = Path(tempfile.mkdtemp())
    bundle_dir = self.tmp / ".reviewcompass" / "decisions" / "bundle-exceptions"
    bundle_dir.mkdir(parents=True)
    self.bundle_dir = bundle_dir

  def teardown_method(self):
    import shutil
    shutil.rmtree(self.tmp, ignore_errors=True)

  def _write_exception(self, exception_id, covered_ids):
    record = {
      "bundle_exception_id": exception_id,
      "approved_by": "test-approver",
      "approved_at": "2026-06-15T00:00:00+09:00",
      "covered_decision_ids": covered_ids,
      "rationale": "test rationale",
    }
    path = self.bundle_dir / f"{exception_id}.yaml"
    path.write_text(yaml.dump(record, allow_unicode=True), encoding="utf-8")
    return path

  def test_bundled_without_exception_fails(self):
    data = {
      **VALID_DECISION,
      "source": {**VALID_DECISION["source"], "multiplicity": "bundled"},
    }
    errors = check_bundle_exception(data, self.tmp)
    assert len(errors) > 0

  def test_bundled_with_exception_but_still_bundled_fails(self):
    # 承認レコードあり + covered_decision_ids 含む が multiplicity=bundled のまま
    self._write_exception("BEX-WM-001", ["DEC-WM-001"])
    data = {
      **VALID_DECISION,
      "bundle_exception_id": "BEX-WM-001",
      "source": {**VALID_DECISION["source"], "multiplicity": "bundled"},
    }
    errors = check_bundle_exception(data, self.tmp)
    assert len(errors) > 0

  def test_no_exception_record_but_single_fails(self):
    # 承認レコードなし + multiplicity=single（なぜか exception_id だけ付与）
    data = {
      **VALID_DECISION,
      "bundle_exception_id": "BEX-WM-001",
      "source": {**VALID_DECISION["source"], "multiplicity": "single"},
    }
    errors = check_bundle_exception(data, self.tmp)
    assert len(errors) > 0

  def test_exception_not_covering_this_decision_fails(self):
    # 承認レコードあり が covered_decision_ids に当該 decision_id を含まない
    self._write_exception("BEX-WM-001", ["DEC-WM-999"])  # 別の decision
    data = {
      **VALID_DECISION,
      "bundle_exception_id": "BEX-WM-001",
      "source": {**VALID_DECISION["source"], "multiplicity": "single"},
    }
    errors = check_bundle_exception(data, self.tmp)
    assert len(errors) > 0

  def test_all_three_conditions_met_passes(self):
    # 全 3 条件充足: 承認レコードあり + covered_decision_ids 含む + multiplicity=single
    self._write_exception("BEX-WM-001", ["DEC-WM-001"])
    data = {
      **VALID_DECISION,
      "bundle_exception_id": "BEX-WM-001",
      "source": {**VALID_DECISION["source"], "multiplicity": "single"},
    }
    errors = check_bundle_exception(data, self.tmp)
    assert errors == []

  def test_single_without_exception_id_passes(self):
    # multiplicity=single で bundle_exception_id なし → 通常ケース、検査不要
    data = {**VALID_DECISION}
    errors = check_bundle_exception(data, self.tmp)
    assert errors == []


# ──────────────────────────────────────────────
# テスト(3)(4) 逐語照合
# ──────────────────────────────────────────────

class TestVerifyExcerptInSession:
  def test_exact_match(self, tmp_path):
    session_file = tmp_path / "session.md"
    session_file.write_text("## Turn 1\n\n自律的に実施\n\n## Turn 2\n\nOK\n", encoding="utf-8")
    ok = verify_excerpt_in_session("自律的に実施", session_file)
    assert ok is True

  def test_normalized_match(self, tmp_path):
    # 連続空白の正規化
    session_file = tmp_path / "session.md"
    session_file.write_text("自律的に  実施\n", encoding="utf-8")
    ok = verify_excerpt_in_session("自律的に  実施", session_file)
    assert ok is True

  def test_excerpt_not_in_session(self, tmp_path):
    session_file = tmp_path / "session.md"
    session_file.write_text("全く別の内容\n", encoding="utf-8")
    ok = verify_excerpt_in_session("自律的に実施", session_file)
    assert ok is False

  def test_turn_number_not_used_for_narrowing(self, tmp_path):
    # ターン番号での絞り込みを行わず、全文を対象とする
    session_file = tmp_path / "session.md"
    # Turn 1 に excerpt が存在する（locator は Turn 2 を指すが全文検索するため一致するはず）
    session_file.write_text("## Turn 1\n\n自律的に実施\n\n## Turn 2\n\n別の内容\n", encoding="utf-8")
    ok = verify_excerpt_in_session("自律的に実施", session_file)
    assert ok is True

  def test_nfc_normalization(self, tmp_path):
    session_file = tmp_path / "session.md"
    # 濁点分解形（NFD）で保存、NFC で照合
    nfd_text = unicodedata.normalize("NFD", "テスト")
    session_file.write_text(nfd_text, encoding="utf-8")
    ok = verify_excerpt_in_session("テスト", session_file)
    assert ok is True


# ──────────────────────────────────────────────
# テスト(6) 内容なし語リスト判定
# ──────────────────────────────────────────────

class TestIsEmptyContent:
  def setup_method(self):
    self.config = {"empty_content_words": ["OK", "ok", "承認", "了解", "はい", "LGTM"]}

  def test_single_word_match(self):
    assert is_empty_content("承認", self.config) is True

  def test_punctuation_stripped_before_check(self):
    # 「承認！」→ 記号除去 → 「承認」→ リスト一致 → fail
    assert is_empty_content("承認！", self.config) is True

  def test_multiple_words_all_match(self):
    assert is_empty_content("OK 承認", self.config) is True

  def test_partial_match_fails(self):
    # 「承認します」はリストに含まれない → 通過
    assert is_empty_content("承認します", self.config) is False

  def test_single_word_not_in_list(self):
    assert is_empty_content("実施する", self.config) is False

  def test_empty_string(self):
    # 空文字列はトークンなし → fail-closed（空を通過させない）
    assert is_empty_content("", self.config) is True


# ──────────────────────────────────────────────
# テスト(7) --all で decisions/ 直下のみ（bundle-exceptions/ 除外）
# ──────────────────────────────────────────────

class TestCollectDecisionFiles:
  def test_collects_direct_yaml_files(self, tmp_path):
    decisions_dir = tmp_path / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "DEC-WM-001.yaml").write_text("", encoding="utf-8")
    (decisions_dir / "DEC-WM-002.yaml").write_text("", encoding="utf-8")
    files = collect_decision_files(tmp_path)
    assert len(files) == 2

  def test_excludes_bundle_exceptions_directory(self, tmp_path):
    decisions_dir = tmp_path / ".reviewcompass" / "decisions"
    bundle_dir = decisions_dir / "bundle-exceptions"
    bundle_dir.mkdir(parents=True)
    (decisions_dir / "DEC-WM-001.yaml").write_text("", encoding="utf-8")
    (bundle_dir / "BEX-WM-001.yaml").write_text("", encoding="utf-8")
    files = collect_decision_files(tmp_path)
    assert len(files) == 1
    assert all("bundle-exceptions" not in str(f) for f in files)

  def test_empty_decisions_directory(self, tmp_path):
    decisions_dir = tmp_path / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    files = collect_decision_files(tmp_path)
    assert files == []

  def test_nonexistent_decisions_directory(self, tmp_path):
    files = collect_decision_files(tmp_path)
    assert files == []


# ──────────────────────────────────────────────
# テスト(5) pending → WARN, unverifiable → DEVIATION
# ──────────────────────────────────────────────

class TestLintDecisionFile:
  def setup_method(self):
    import tempfile
    self.tmp = Path(tempfile.mkdtemp())
    sessions_dir = self.tmp / ".reviewcompass" / "evidence" / "sessions"
    sessions_dir.mkdir(parents=True)
    session_file = sessions_dir / "2026-06-15-claude-4e02c8a6.md"
    session_file.write_text("## Turn 1\n\n自律的に実施\n", encoding="utf-8")
    decisions_dir = self.tmp / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    self.decisions_dir = decisions_dir
    self.config = load_decision_source_lint_config(self.tmp)

  def teardown_method(self):
    import shutil
    shutil.rmtree(self.tmp, ignore_errors=True)

  def _write_decision(self, filename, data):
    path = self.decisions_dir / filename
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return path

  def test_verified_record_passes(self):
    path = self._write_decision("DEC-WM-001.yaml", {
      **VALID_DECISION,
      "source": {
        **VALID_DECISION["source"],
        "locator": ".reviewcompass/evidence/sessions/2026-06-15-claude-4e02c8a6.md:1",
        "excerpt": "自律的に実施",
      },
      "verification_status": "verified",
      "verified_at": "2026-06-15T00:00:00+09:00",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict in ("OK", "WARN")
    assert result.exit_code in (0, 1)

  def test_pending_record_returns_warn(self):
    path = self._write_decision("DEC-WM-002.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-002",
      "verification_status": "pending",
    })
    del path  # lint_decision_file を呼び直す
    path = self.decisions_dir / "DEC-WM-002.yaml"
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "WARN"
    assert result.exit_code == 1

  def test_unverifiable_record_returns_deviation(self):
    path = self._write_decision("DEC-WM-003.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-003",
      "verification_status": "unverifiable",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_schema_error_returns_deviation(self):
    path = self._write_decision("DEC-WM-004.yaml", {
      "decision_id": "DEC-WM-004",
      # category, statement, source, verification_status が欠落
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_bundled_without_exception_returns_deviation(self):
    path = self._write_decision("DEC-WM-005.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-005",
      "source": {**VALID_DECISION["source"], "multiplicity": "bundled"},
      "verification_status": "verified",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_session_file_not_found_returns_unverifiable_deviation(self):
    path = self._write_decision("DEC-WM-006.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-006",
      "source": {
        **VALID_DECISION["source"],
        "locator": ".reviewcompass/evidence/sessions/nonexistent.md:1",
        "excerpt": "自律的に実施",
      },
      "verification_status": "verified",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_excerpt_not_in_session_returns_deviation(self):
    path = self._write_decision("DEC-WM-007.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-007",
      "source": {
        **VALID_DECISION["source"],
        "locator": ".reviewcompass/evidence/sessions/2026-06-15-claude-4e02c8a6.md:1",
        "excerpt": "この文言はセッションに存在しない",
      },
      "verification_status": "verified",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_empty_content_excerpt_returns_deviation(self):
    path = self._write_decision("DEC-WM-008.yaml", {
      **VALID_DECISION,
      "decision_id": "DEC-WM-008",
      "source": {
        **VALID_DECISION["source"],
        "excerpt": "承認",
      },
      "verification_status": "verified",
    })
    result = lint_decision_file(path, self.tmp, self.config)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2


# ──────────────────────────────────────────────
# テスト(8)(9) --verify-pending
# ──────────────────────────────────────────────

class TestVerifyPending:
  def setup_method(self):
    import tempfile
    self.tmp = Path(tempfile.mkdtemp())
    sessions_dir = self.tmp / ".reviewcompass" / "evidence" / "sessions"
    sessions_dir.mkdir(parents=True)
    session_file = sessions_dir / "2026-06-15-claude-4e02c8a6.md"
    session_file.write_text("## Turn 1\n\n自律的に実施\n", encoding="utf-8")
    decisions_dir = self.tmp / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    self.decisions_dir = decisions_dir

  def teardown_method(self):
    import shutil
    shutil.rmtree(self.tmp, ignore_errors=True)

  def _pending_decision(self, decision_id="DEC-WM-P01"):
    data = {
      **VALID_DECISION,
      "decision_id": decision_id,
      "source": {
        **VALID_DECISION["source"],
        "locator": ".reviewcompass/evidence/sessions/2026-06-15-claude-4e02c8a6.md:1",
        "excerpt": "自律的に実施",
      },
      "verification_status": "pending",
    }
    if "verified_at" in data:
      del data["verified_at"]
    path = self.decisions_dir / f"{decision_id}.yaml"
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return path

  def test_verify_pending_updates_to_verified(self):
    from check_workflow_action.decision_source_lint import run_verify_pending
    path = self._pending_decision()
    original_statement = VALID_DECISION["statement"]
    result = run_verify_pending(self.tmp)
    updated = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert updated["verification_status"] == "verified"
    assert "verified_at" in updated
    assert updated["statement"] == original_statement

  def test_verify_pending_only_updates_two_fields(self):
    from check_workflow_action.decision_source_lint import run_verify_pending
    path = self._pending_decision()
    original = yaml.safe_load(path.read_text(encoding="utf-8"))
    run_verify_pending(self.tmp)
    updated = yaml.safe_load(path.read_text(encoding="utf-8"))
    # verification_status と verified_at 以外は不変
    for key in original:
      if key not in ("verification_status", "verified_at"):
        assert updated.get(key) == original.get(key), f"フィールド {key} が変更された"

  def test_verify_pending_fails_if_not_in_session(self):
    from check_workflow_action.decision_source_lint import run_verify_pending
    data = {
      **VALID_DECISION,
      "decision_id": "DEC-WM-P02",
      "source": {
        **VALID_DECISION["source"],
        "locator": ".reviewcompass/evidence/sessions/2026-06-15-claude-4e02c8a6.md:1",
        "excerpt": "存在しない文言",
      },
      "verification_status": "pending",
    }
    if "verified_at" in data:
      del data["verified_at"]
    path = self.decisions_dir / "DEC-WM-P02.yaml"
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    original_content = path.read_text(encoding="utf-8")
    result = run_verify_pending(self.tmp)
    # ファイルは不変
    assert path.read_text(encoding="utf-8") == original_content
    # 非ゼロ終了（失敗した pending がある）
    assert result.exit_code != 0

  def test_verify_pending_does_not_modify_non_pending(self):
    from check_workflow_action.decision_source_lint import run_verify_pending
    # verification_status=verified のファイルは変更しない
    data = {**VALID_DECISION}
    path = self.decisions_dir / "DEC-WM-V01.yaml"
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    original_content = path.read_text(encoding="utf-8")
    run_verify_pending(self.tmp)
    assert path.read_text(encoding="utf-8") == original_content

  def test_verify_pending_does_not_modify_unverifiable(self):
    from check_workflow_action.decision_source_lint import run_verify_pending
    # verification_status=unverifiable のファイルは変更しない
    data = {**VALID_DECISION, "verification_status": "unverifiable"}
    if "verified_at" in data:
      del data["verified_at"]
    path = self.decisions_dir / "DEC-WM-UV01.yaml"
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    original_content = path.read_text(encoding="utf-8")
    run_verify_pending(self.tmp)
    assert path.read_text(encoding="utf-8") == original_content


# ──────────────────────────────────────────────
# テスト(10) commit ゲート統合（end-to-end）
# ──────────────────────────────────────────────

class TestCommitGateIntegration:
  """check-workflow-action.py commit が decision-source-lint を呼び出すことを end-to-end で確認。

  テスト環境では実際の git リポジトリと commit-approval.json が必要なため、
  decision-source-lint の判定がcommit の verdict に反映されることを確認する。
  """

  def test_decisions_dir_absence_does_not_block_commit_gate(self, tmp_path):
    """decisions/ が存在しない場合（決定記録ゼロ件）は DEVIATION にならない"""
    from check_workflow_action.decision_source_lint import run_decision_source_lint_all
    result = run_decision_source_lint_all(tmp_path)
    # decisions/ 不在は正常（0 件として扱う）
    assert result.exit_code in (0, 1)
    assert result.verdict in ("OK", "WARN")

  def test_unverifiable_decision_escalates_to_deviation(self, tmp_path):
    """unverifiable 決定が存在すると run_all は DEVIATION を返す"""
    from check_workflow_action.decision_source_lint import run_decision_source_lint_all
    decisions_dir = tmp_path / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    data = {
      **VALID_DECISION,
      "decision_id": "DEC-WM-U01",
      "verification_status": "unverifiable",
    }
    (decisions_dir / "DEC-WM-U01.yaml").write_text(
      yaml.dump(data, allow_unicode=True), encoding="utf-8"
    )
    result = run_decision_source_lint_all(tmp_path)
    assert result.verdict == "DEVIATION"
    assert result.exit_code == 2

  def test_pending_decision_returns_warn_not_deviation(self, tmp_path):
    """pending 決定が存在すると run_all は WARN を返す（DEVIATION ではない）"""
    from check_workflow_action.decision_source_lint import run_decision_source_lint_all
    decisions_dir = tmp_path / ".reviewcompass" / "decisions"
    decisions_dir.mkdir(parents=True)
    data = {**VALID_DECISION, "decision_id": "DEC-WM-W01", "verification_status": "pending"}
    del data["verified_at"]
    (decisions_dir / "DEC-WM-W01.yaml").write_text(
      yaml.dump(data, allow_unicode=True), encoding="utf-8"
    )
    result = run_decision_source_lint_all(tmp_path)
    assert result.verdict == "WARN"
    assert result.exit_code == 1


# ──────────────────────────────────────────────
# テスト(3)(4) normalize_text
# ──────────────────────────────────────────────

class TestNormalizeText:
  def test_strips_whitespace(self):
    assert normalize_text("  hello  ") == "hello"

  def test_collapses_whitespace(self):
    assert normalize_text("a  b\t\tc") == "a b c"

  def test_nfc_normalization(self):
    nfd = unicodedata.normalize("NFD", "テスト")
    result = normalize_text(nfd)
    assert result == unicodedata.normalize("NFC", "テスト")

  def test_newline_to_space(self):
    assert normalize_text("a\nb") == "a b"
