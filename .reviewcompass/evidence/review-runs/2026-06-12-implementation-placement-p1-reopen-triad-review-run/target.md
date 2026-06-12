# レビュー対象：reopen R-0（placement-p1-path-contracts）conformance-evaluation implementation 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本 reopen の requirements・design・tasks triad-review と同一構成（利用者承認 2026-06-12「承認」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の
第3過程、conformance-evaluation implementation フェーズの triad-review。上流の requirements・design・tasks は
各 gate を完了し利用者承認済み。本レビューの対象は、tasks 確定本文（T-009／T-007／T-012 の凍結期責務・
テスト要件）どおりに TDD で実装した working tree 差分である（未コミット。コミットは利用者指示の停止点）。

確定済み上流契約の要点（実装が満たすべき契約）：

- 配置ルート契約＝`<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`（評価記録・草案・handoff。Req 6 受入 2）
- 書き込みは常に新配置。旧配置 `specs/<feature>/conformance/` への新規書き込みを行わない（凍結契約、design §12.2）
- 読み取りは新配置優先・旧配置フォールバック（P3 まで）。両方に同名記録がある場合は新配置を正とし警告を報告
- 所見 ID（CF-NNN／JD-NNN）採番は凍結期に新旧両配置を合算した走査範囲で最大番号を統合算出（design §10.7）
- MV-1〜MV-3 の検査ルートは新配置を正とし、旧配置の凍結済み既存記録も検査対象。新規記録が旧配置に現れた場合は
  違反として検出（凍結集合の判定は git 追跡履歴が正本：P1 実装反映コミット時点の旧配置在籍ファイルが凍結集合、
  以降の追加・変更は違反。効力発生は実装切替と同時。design §18）
- 推定ログの書き込みは常に新配置 `evidence/estimation/<run_id>/`。旧 `logs/estimation/` への新規追加は凍結違反として
  検出（判定規則は評価記録と同一）。凍結済み旧推定ログは MV-6 の読み取り対象に含める
- `_cross_feature` は実 feature ではない横断名前空間で、配置は `specs/_cross_feature/conformance/` のまま（tasks T-015）

## 2. TDD 経過（実装証跡）

- 赤フェーズ：凍結期契約のテスト 12 件を先行作成し、全件失敗を確認
- 緑フェーズ：実装後、conformance-evaluation スイート 76 件 pass、全テスト（ディレクトリ別）計 894 件 pass、回帰なし
- 実装中の手戻り（reopen 状態ファイルに記録済み）：
  (1) 凍結違反検出の初版を `git ls-tree` のワイルドカード前提で実装 → ls-tree はワイルドカードを解釈せず凍結集合が
  空になり誤検出。木全体を列挙し Python 側で正規表現絞り込みへ修正
  (2) 赤フェーズで contract_ownership の check 記録読み取り 2 テストの更新漏れ → 緑フェーズで発見し追従
  (3) `_cross_feature` 例外を当初 SpecUpdateDraftWriter 内分岐で実装 → check 記録側にも必要と判明し、
  配置リゾルバ `conformance_dir` へ集約

## 3. レビュー観点（6 criteria 構造の implementation 適合）

1. tasks 確定本文（T-009 完了条件・テスト要件 4 件／T-007 完了条件 4／T-012 凍結違反検出・推定ログ凍結期テスト）との対応
2. design §10.7・§12.2・§18 の凍結期契約と実装挙動の一致（特に git 履歴判定の正しさ、効力発生時点の扱い）
3. 旧配置への新規書き込み経路が残っていないか（全ライターの切替漏れ）
4. テストが契約を網羅し、テスト自体が契約を弱めていないか
5. 例外系・境界条件（同名衝突・採番境界・未追跡ファイルの扱い・`_cross_feature`）
6. 運用文書（CONFORMANCE_EVALUATION.md）の記述と実装の整合

## 3.5 round-2 注記：round-1 所見の適用（proxy_model 判断、2026-06-12）

round-1 の 8 所見（6 同根クラスタ）は proxy_model（gemini-3.1-pro-preview、利用者発言「proxy_modelで自律実行」による委任）が
判断し、全クラスタで操縦 LLM の推薦案 A を採用した（証跡 `proxy-decisions/`・`approval-proxy-2026-06-12.yaml`）。
適用内容（TDD：赤 4 件確認 → 緑、全 900 件 pass）：

- C1（must-fix）：未追跡列挙から `--exclude-standard` を撤去し、ignore された旧配置追加も凍結違反として検出。ignored 検出テスト追加
- C4（must-fix）：既存 `prompt.log` を新旧両配置から走査し MV-6 の 2 条件を検査する `check_existing_prompt_logs` を追加（prompt_text 区画のみ検査、遮断必須）。テスト追加
- C2（should-fix）：作業ツリー比較は維持し、freeze 後にコミット済みの変更も検出されることをテストで固定
- C3（should-fix）：`read_record` の `_cross_feature` を `source: cross_feature_namespace` で報告。凍結検査の除外判定をパス成分一致 `_is_cross_feature_namespace` へ強化（feature 配下の `_cross_feature` サブディレクトリは除外されない）。テスト 2 件追加
- C5（should-fix）：凍結ファイルの削除が `frozen_file_changed` として検出されることをテストで固定（「実装が削除を含めない」との round-1 主張は事実誤認と確認済み）
- C6（leave-as-is）：互換終了の正本は配置規約 PLC-DEC-011。運用文書への二重記載はしない

round-2 は適用後差分の収束確認である。

## 3.6 round-3 注記：round-2 所見の適用（proxy_model 判断、2026-06-12）

round-2 の 4 所見は proxy_model（gemini-3.1-pro-preview）が判断した（証跡 `proxy-decisions/round-2/`・
`approval-proxy-2026-06-12-round-2.yaml`）。C7=案 B（CLI 自動組み込みは DVT-C003 のフェーズ 4 方針に従い見送り、
運用文書 CONFORMANCE_EVALUATION.md へ凍結検査の手動実行手順〔freeze-commit の解決例と Python 実行例〕を記載、
should-fix。操縦 LLM 推薦の案 A を proxy が棄却）。C9=案 A（凍結ファイルのコミット済み削除も検出されることを
テストへ追加、should-fix）。C8・C10=leave-as-is。適用後も全テスト pass。round-3 は収束確認である。

## 4. 実装差分（git diff、working tree、round-2 所見適用後。reopen 状態ファイルの手続き記録更新は対象外）

```diff
diff --git a/docs/operations/CONFORMANCE_EVALUATION.md b/docs/operations/CONFORMANCE_EVALUATION.md
index e508c674..ad6f6800 100644
--- a/docs/operations/CONFORMANCE_EVALUATION.md
+++ b/docs/operations/CONFORMANCE_EVALUATION.md
@@ -79,23 +79,30 @@
 
 ## 6. 評価記録の配置（Requirement 6）
 
+conformance 成果物（評価記録・spec update 草案・reopen handoff 成果物）の配置ルート契約は `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/` とする（2026-06-12 配置規約 PLC-DEC-003〜005・009〜011 反映）。
+
 ```
-<対象アプリ>/.reviewcompass/specs/<feature>/
-├── intent.md           （仕様文書）
-├── requirements.md
-├── design.md
-├── tasks.md
-├── spec.json
-├── reviews/            （仕様駆動レビューの記録）
-│   └── <日付>-<種別>.md
+<対象アプリ>/.reviewcompass/evidence/features/<feature>/
 └── conformance/        （本機能の評価記録、reviews/ とは別）
     ├── <日付>-generation.md   （文書生成モード）
-    └── <日付>-check.md         （照合チェックモード）
+    ├── <日付>-check.md         （照合チェックモード）
+    └── <日付>-spec-update-drafts/   （仕様更新草案）
 ```
 
 評価記録の `type` 値は `conformance_evaluation` に統合し、`mode_internal` フィールドで `generation` と `check` を区別する。
 
-評価記録は必ず `conformance/<日付>-<mode>.md` のパス規則に従い、`reviews/` とは別に保管する。`reviews/` は仕様駆動レビューの記録、`conformance/` は本機能の下流 → 上流評価記録であり、混在させない。
+評価記録は必ず `conformance/<日付>-<mode>.md` のパス規則に従い、`reviews/` とは別に保管する。`reviews/` は仕様駆動レビューの記録、`conformance/` は本機能の下流 → 上流評価記録であり、分離契約は evidence 配下でも維持する。
+
+### 6.0 凍結期（P3 まで）の新旧配置の扱い
+
+旧配置 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/` の既存記録は旧置き場で凍結保全する（移動しない）。挙動は次のとおり。
+
+- **書き込みは常に新配置**。旧配置への新規書き込みは行わない（凍結契約）
+- **読み取りは新配置優先・旧配置フォールバック**（新 → 旧の順、P3 まで）。両方に同名記録がある場合は新配置を正とし、警告を報告する
+- **採番（CF-NNN ／ JD-NNN）は新旧合算スコープ**で最大番号を統合算出し、旧凍結記録との ID 重複・リセットを防ぐ
+- **凍結集合の判定は git 追跡履歴が正本**：P1 実装反映コミット（書き込み先切替のコミット）時点で旧配置に存在したファイルが凍結集合であり、それ以降の旧配置への追加・変更は凍結違反として検出する（`MachineVerification.check_record_freeze`、遮断推奨）
+- `_cross_feature` は実 feature ではない横断名前空間で、配置は `specs/_cross_feature/conformance/` のまま（凍結対象外、tasks T-015）
+- 互換の終了は P3 の専用 reopen における仕様改訂として扱う（暗黙の終了はない）
 
 文書生成モードの推定出力先は次のとおりとする。
 
@@ -124,7 +131,33 @@
 | MV-6 | 推定役プロンプトに既存上流文書パスが混入せず、自律探索禁止条項がある | 遮断必須 |
 | MV-7 | foundation 受入番号参照が foundation requirements.md と一致する | 警告続行可 |
 
-MV-6 の第 1 期最小仕様では、推定役プロンプトログに時刻、実行 ID、プロンプト全文を残し、`logs/estimation/<run_id>/prompt.log` 相当の場所に保存する。検査は、既存上流文書パス（例 `intent.md`、`requirements.md`、`design.md`）の不在確認と、自律探索禁止条項の存在確認の 2 条件で行う。
+MV-6 の第 1 期最小仕様では、推定役プロンプトログに時刻、実行 ID、プロンプト全文を残し、`<対象アプリ>/.reviewcompass/evidence/estimation/<run_id>/prompt.log` に保存する（旧 `logs/estimation/` からの変更は 2026-06-12 配置規約 PLC-DEC-005・009 反映）。検査は、既存上流文書パス（例 `intent.md`、`requirements.md`、`design.md`）の不在確認と、自律探索禁止条項の存在確認の 2 条件で行う。
+
+凍結期（P3 まで）の推定ログ：既存ログは旧 `logs/estimation/` で凍結し、MV-6 の読み取り対象に含める。書き込みは常に新配置とし、旧ルートへの新規追加は凍結違反として検出する（`MachineVerification.check_estimation_log_freeze`、判定規則は評価記録と同一＝P1 実装反映コミット以降の git 追跡履歴を正本とする）。
+
+凍結検査の手動実行手順（第 1 期。CLI への自動組み込みは DVT-C003 によりフェーズ 4 で扱う）：
+
+1. 凍結境界（P1 実装反映コミット＝書き込み先切替のコミット）を特定する。例：
+
+   ```bash
+   git log --reverse --format=%H -S "evidence/features" -- tools/conformance_evaluation/evaluation_record.py | head -1
+   ```
+
+2. 凍結違反検出（評価記録・推定ログ）と既存推定ログの MV-6 内容検査を実行する。例：
+
+   ```bash
+   PYTHONPATH=. .venv/bin/python3 -c "
+   from tools.conformance_evaluation.machine_verification import MachineVerification
+   mv = MachineVerification('.')
+   fc = '<freeze-commit>'
+   for result in (
+     mv.check_record_freeze(freeze_commit=fc),
+     mv.check_estimation_log_freeze(freeze_commit=fc),
+     mv.check_existing_prompt_logs(forbidden_paths=['intent.md', 'requirements.md', 'design.md']),
+   ):
+     print(result.check_id, result.status.value, result.reasons)
+   "
+   ```
 
 `tools/conformance-evaluation-check.py` は conformance-evaluation 固有の評価記録・遮断・推定根拠を検査する。workflow-management の `tools/check-workflow-action.py` は workflow_state や不可逆操作の順序を検査するため、責務は異なる。
 
diff --git a/tests/conformance-evaluation/test_conformance_evaluation.py b/tests/conformance-evaluation/test_conformance_evaluation.py
index c692b8d0..d65ec38d 100644
--- a/tests/conformance-evaluation/test_conformance_evaluation.py
+++ b/tests/conformance-evaluation/test_conformance_evaluation.py
@@ -1,6 +1,7 @@
 from pathlib import Path
 import json
 import re
+import subprocess
 
 import pytest
 import yaml
@@ -24,6 +25,27 @@ from tools.conformance_evaluation.triad_review import TriadReviewPolicy
 ROOT = Path(__file__).resolve().parents[2]
 
 
+def _git(repo: Path, *args: str) -> str:
+  result = subprocess.run(
+    ["git", "-C", str(repo), *args],
+    capture_output=True,
+    text=True,
+    check=True,
+  )
+  return result.stdout.strip()
+
+
+def _git_commit_all(repo: Path, message: str) -> str:
+  _git(repo, "add", "-A")
+  _git(
+    repo,
+    "-c", "user.name=test",
+    "-c", "user.email=test@example.com",
+    "commit", "-m", message,
+  )
+  return _git(repo, "rev-parse", "HEAD")
+
+
 def test_t001_layout_and_operation_docs_are_present():
   assert (ROOT / "tools" / "conformance_evaluation" / ".gitkeep").is_file()
   assert (ROOT / "tools" / "conformance_evaluation" / "schemas" / ".gitkeep").is_file()
@@ -67,7 +89,9 @@ def test_t003_generation_outputs_human_reviewable_documents(tmp_path):
     assert "Requirements" in text
     assert "src/billing.py:1-20" in text
     assert "human_review_required: true" in text
-  assert (tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-generation.md").is_file()
+  assert (
+    tmp_path / ".reviewcompass" / "evidence" / "features" / "billing" / "conformance" / "2026-06-04-generation.md"
+  ).is_file()
 
 
 def test_t004_check_mode_enforces_two_stage_isolation(tmp_path):
@@ -84,7 +108,9 @@ def test_t004_check_mode_enforces_two_stage_isolation(tmp_path):
   assert result["intent_policy"] == "reference_only"
   assert result["partitioning_check"] == "standard_disabled"
   assert result["findings"][0]["severity"] == "INFO"
-  record_path = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-check.md"
+  record_path = (
+    tmp_path / ".reviewcompass" / "evidence" / "features" / "billing" / "conformance" / "2026-06-04-check.md"
+  )
   assert record_path.is_file()
   record_text = record_path.read_text(encoding="utf-8")
   assert "## 食い違い所見" in record_text
@@ -176,6 +202,38 @@ def test_t007_comparison_records_mismatches_and_ids():
   )["finding_id"] == "CF-1000"
 
 
+def test_t007_frozen_period_numbering_merges_legacy_and_new_scopes(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  (legacy_dir / "2026-06-01-check.md").write_text(
+    "finding_id: CF-007\njudgment_id: JD-007\n",
+    encoding="utf-8",
+  )
+  model = ComparisonModel.for_feature(tmp_path, "billing")
+  finding = model.compare_one(
+    criterion_id="criterion-1",
+    existing={"section": "A", "claim": "x", "code_refs": ["src/a.py:1"]},
+    inferred={"section": "B", "claim": "x", "code_refs": ["src/a.py:1"]},
+  )
+  assert finding["finding_id"] == "CF-008"
+  assert finding["judgment_id"] == "JD-008"
+
+  new_dir = tmp_path / ".reviewcompass" / "evidence" / "features" / "billing" / "conformance"
+  new_dir.mkdir(parents=True)
+  (new_dir / "2026-06-12-check.md").write_text(
+    "finding_id: CF-012\njudgment_id: JD-008\n",
+    encoding="utf-8",
+  )
+  merged_model = ComparisonModel.for_feature(tmp_path, "billing")
+  merged_finding = merged_model.compare_one(
+    criterion_id="criterion-1",
+    existing={"section": "A", "claim": "x", "code_refs": ["src/a.py:1"]},
+    inferred={"section": "B", "claim": "x", "code_refs": ["src/a.py:1"]},
+  )
+  assert merged_finding["finding_id"] == "CF-013"
+  assert merged_finding["judgment_id"] == "JD-009"
+
+
 def test_t008_triad_review_policy_applies_stage_and_intensity():
   policy = TriadReviewPolicy()
   assert policy.intensity_for("requirements_estimation") == "full"
@@ -223,6 +281,74 @@ def test_t009_evaluation_record_front_matter_and_placement(tmp_path):
     )
 
 
+def _write_minimal_record(model, *, feature: str, run_date: str) -> Path:
+  return model.write_record(
+    feature=feature,
+    mode_internal="check",
+    run_date=run_date,
+    author="primary",
+    reviewer="judgment",
+    target_commit="abc123",
+    materialization_commit_hash=None,
+    related_records=[],
+    body="## 機械検査結果\nOK\n",
+  )
+
+
+def test_t009_record_write_targets_new_evidence_placement(tmp_path):
+  model = EvaluationRecordModel(tmp_path)
+  path = _write_minimal_record(model, feature="billing", run_date="2026-06-12")
+  assert path == (
+    tmp_path / ".reviewcompass" / "evidence" / "features" / "billing" / "conformance" / "2026-06-12-check.md"
+  )
+  assert path.is_file()
+
+
+def test_t009_record_write_never_creates_legacy_placement(tmp_path):
+  model = EvaluationRecordModel(tmp_path)
+  _write_minimal_record(model, feature="billing", run_date="2026-06-12")
+  assert not (tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance").exists()
+
+
+def test_t009_record_read_falls_back_to_frozen_legacy(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  (legacy_dir / "2026-06-01-check.md").write_text("legacy body\n", encoding="utf-8")
+  model = EvaluationRecordModel(tmp_path)
+  record = model.read_record(feature="billing", file_name="2026-06-01-check.md")
+  assert record["source"] == "legacy_frozen"
+  assert record["text"] == "legacy body\n"
+  assert record["path"] == legacy_dir / "2026-06-01-check.md"
+  assert record["warnings"] == []
+
+
+def test_t009_cross_feature_read_reports_namespace_source(tmp_path):
+  namespace_dir = tmp_path / ".reviewcompass" / "specs" / "_cross_feature" / "conformance"
+  namespace_dir.mkdir(parents=True)
+  (namespace_dir / "2026-06-12-check.md").write_text("cross feature body\n", encoding="utf-8")
+  model = EvaluationRecordModel(tmp_path)
+  record = model.read_record(feature="_cross_feature", file_name="2026-06-12-check.md")
+  assert record["source"] == "cross_feature_namespace"
+  assert record["path"] == namespace_dir / "2026-06-12-check.md"
+  assert record["warnings"] == []
+
+
+def test_t009_record_read_prefers_new_and_warns_on_duplicate(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  (legacy_dir / "2026-06-12-check.md").write_text("legacy body\n", encoding="utf-8")
+  new_dir = tmp_path / ".reviewcompass" / "evidence" / "features" / "billing" / "conformance"
+  new_dir.mkdir(parents=True)
+  (new_dir / "2026-06-12-check.md").write_text("evidence body\n", encoding="utf-8")
+  model = EvaluationRecordModel(tmp_path)
+  record = model.read_record(feature="billing", file_name="2026-06-12-check.md")
+  assert record["source"] == "evidence"
+  assert record["text"] == "evidence body\n"
+  assert record["path"] == new_dir / "2026-06-12-check.md"
+  assert len(record["warnings"]) == 1
+  assert "specs/billing/conformance" in record["warnings"][0]
+
+
 def test_t010_dependency_shape_matches_feature_dependency():
   import yaml
 
@@ -255,8 +381,9 @@ def test_t012_machine_verification_mv6_is_blocking(tmp_path):
     run_id="run-001",
   )
   assert ok.status == VerificationStatus.OK
-  prompt_log = tmp_path / "logs" / "estimation" / "run-001" / "prompt.log"
+  prompt_log = tmp_path / ".reviewcompass" / "evidence" / "estimation" / "run-001" / "prompt.log"
   assert prompt_log.is_file()
+  assert not (tmp_path / "logs" / "estimation").exists()
   log_text = prompt_log.read_text(encoding="utf-8")
   assert "run_id: run-001" in log_text
   assert "prompt_text:" in log_text
@@ -270,6 +397,172 @@ def test_t012_machine_verification_mv6_is_blocking(tmp_path):
   assert bad.fail_closed == "blocking"
 
 
+def test_t012_record_freeze_violations_detected_from_git_history(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  frozen_record = legacy_dir / "2026-06-01-check.md"
+  frozen_record.write_text("type: conformance_evaluation\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  verifier = MachineVerification(tmp_path)
+  ok = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert ok.check_id == "MV-3"
+  assert ok.status == VerificationStatus.OK
+  assert ok.fail_closed == "recommended"
+
+  (legacy_dir / "2026-06-13-check.md").write_text("type: conformance_evaluation\n", encoding="utf-8")
+  added = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert added.status == VerificationStatus.DEVIATION
+  assert any("2026-06-13-check.md" in reason for reason in added.reasons)
+  assert all("2026-06-01-check.md" not in reason for reason in added.reasons)
+
+  (legacy_dir / "2026-06-13-check.md").unlink()
+  frozen_record.write_text("type: conformance_evaluation\nedited: true\n", encoding="utf-8")
+  modified = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert modified.status == VerificationStatus.DEVIATION
+  assert any("2026-06-01-check.md" in reason for reason in modified.reasons)
+
+
+def test_t012_estimation_log_freeze_contract(tmp_path):
+  legacy_log_dir = tmp_path / "logs" / "estimation" / "frozen-run"
+  legacy_log_dir.mkdir(parents=True)
+  (legacy_log_dir / "prompt.log").write_text("frozen\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  verifier = MachineVerification(tmp_path)
+  verifier.check_prompt_isolation(
+    prompt_text="Implementation only. 自律探索禁止: existing upstream docs must not be read.",
+    forbidden_paths=["requirements.md", "design.md", "intent.md"],
+    run_id="run-101",
+  )
+  assert (tmp_path / ".reviewcompass" / "evidence" / "estimation" / "run-101" / "prompt.log").is_file()
+  ok = verifier.check_estimation_log_freeze(freeze_commit=freeze_commit)
+  assert ok.status == VerificationStatus.OK
+
+  new_legacy_dir = tmp_path / "logs" / "estimation" / "new-run"
+  new_legacy_dir.mkdir(parents=True)
+  (new_legacy_dir / "prompt.log").write_text("violation\n", encoding="utf-8")
+  bad = verifier.check_estimation_log_freeze(freeze_commit=freeze_commit)
+  assert bad.status == VerificationStatus.DEVIATION
+  assert any("new-run" in reason for reason in bad.reasons)
+  assert bad.fail_closed == "recommended"
+
+
+def test_t012_ignored_legacy_additions_are_freeze_violations(tmp_path):
+  legacy_log_dir = tmp_path / "logs" / "estimation" / "frozen-run"
+  legacy_log_dir.mkdir(parents=True)
+  (legacy_log_dir / "prompt.log").write_text("frozen\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  (tmp_path / ".gitignore").write_text("ignored-run/\n", encoding="utf-8")
+  ignored_dir = tmp_path / "logs" / "estimation" / "ignored-run"
+  ignored_dir.mkdir(parents=True)
+  (ignored_dir / "prompt.log").write_text("violation\n", encoding="utf-8")
+
+  verifier = MachineVerification(tmp_path)
+  result = verifier.check_estimation_log_freeze(freeze_commit=freeze_commit)
+  assert result.status == VerificationStatus.DEVIATION
+  assert any("ignored-run" in reason for reason in result.reasons)
+
+
+def test_t012_committed_changes_after_freeze_are_violations(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  frozen_record = legacy_dir / "2026-06-01-check.md"
+  frozen_record.write_text("type: conformance_evaluation\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  frozen_record.write_text("type: conformance_evaluation\nedited: true\n", encoding="utf-8")
+  _git_commit_all(tmp_path, "edit frozen record after freeze")
+
+  verifier = MachineVerification(tmp_path)
+  result = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert result.status == VerificationStatus.DEVIATION
+  assert any(reason.startswith("frozen_file_changed:") for reason in result.reasons)
+
+
+def test_t012_frozen_record_deletion_is_detected(tmp_path):
+  legacy_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance"
+  legacy_dir.mkdir(parents=True)
+  frozen_record = legacy_dir / "2026-06-01-check.md"
+  frozen_record.write_text("type: conformance_evaluation\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  frozen_record.unlink()
+
+  verifier = MachineVerification(tmp_path)
+  result = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert result.status == VerificationStatus.DEVIATION
+  assert any("frozen_file_changed: " in reason and "2026-06-01-check.md" in reason for reason in result.reasons)
+
+  _git_commit_all(tmp_path, "delete frozen record after freeze")
+  committed = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert committed.status == VerificationStatus.DEVIATION
+  assert any("frozen_file_changed: " in reason and "2026-06-01-check.md" in reason for reason in committed.reasons)
+
+
+def test_t012_cross_feature_exclusion_uses_path_components(tmp_path):
+  namespace_dir = tmp_path / ".reviewcompass" / "specs" / "_cross_feature" / "conformance"
+  namespace_dir.mkdir(parents=True)
+  (namespace_dir / "2026-06-01-check.md").write_text("cross feature\n", encoding="utf-8")
+  _git(tmp_path, "init")
+  freeze_commit = _git_commit_all(tmp_path, "P1 placement switch")
+
+  (namespace_dir / "2026-06-13-check.md").write_text("namespace ok\n", encoding="utf-8")
+  evil_dir = tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "_cross_feature"
+  evil_dir.mkdir(parents=True)
+  (evil_dir / "evil.md").write_text("violation\n", encoding="utf-8")
+
+  verifier = MachineVerification(tmp_path)
+  result = verifier.check_record_freeze(freeze_commit=freeze_commit)
+  assert result.status == VerificationStatus.DEVIATION
+  assert any("billing/conformance/_cross_feature/evil.md" in reason for reason in result.reasons)
+  assert all("specs/_cross_feature/conformance" not in reason for reason in result.reasons)
+
+
+def test_t012_existing_prompt_logs_content_check(tmp_path):
+  frozen_dir = tmp_path / "logs" / "estimation" / "frozen-run"
+  frozen_dir.mkdir(parents=True)
+  (frozen_dir / "prompt.log").write_text(
+    "run_id: frozen-run\n"
+    "timestamp: 2026-06-08T00:00:00+00:00\n"
+    "prompt_text:\n"
+    "Implementation only. Do not read existing upstream documents.\n"
+    "forbidden_paths:\n"
+    "- requirements.md\n"
+    "status: OK\n",
+    encoding="utf-8",
+  )
+  verifier = MachineVerification(tmp_path)
+  clean = verifier.check_existing_prompt_logs(forbidden_paths=["requirements.md", "design.md"])
+  assert clean.check_id == "MV-6"
+  assert clean.status == VerificationStatus.OK
+  assert clean.fail_closed == "blocking"
+
+  bad_dir = tmp_path / ".reviewcompass" / "evidence" / "estimation" / "bad-run"
+  bad_dir.mkdir(parents=True)
+  (bad_dir / "prompt.log").write_text(
+    "run_id: bad-run\n"
+    "timestamp: 2026-06-12T00:00:00+00:00\n"
+    "prompt_text:\n"
+    "Please read requirements.md before estimating.\n"
+    "forbidden_paths:\n"
+    "- requirements.md\n"
+    "status: OK\n",
+    encoding="utf-8",
+  )
+  bad = verifier.check_existing_prompt_logs(forbidden_paths=["requirements.md", "design.md"])
+  assert bad.status == VerificationStatus.DEVIATION
+  assert any("bad-run" in reason and "requirements.md" in reason for reason in bad.reasons)
+  assert any("missing autonomous exploration prohibition" in reason and "bad-run" in reason for reason in bad.reasons)
+  assert all("frozen-run" not in reason for reason in bad.reasons)
+
+
 def test_t013_traceability_smoke():
   tasks_text = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")
   for index in range(1, 17):
diff --git a/tests/conformance-evaluation/test_contract_ownership.py b/tests/conformance-evaluation/test_contract_ownership.py
index 71de3561..ba45d426 100644
--- a/tests/conformance-evaluation/test_contract_ownership.py
+++ b/tests/conformance-evaluation/test_contract_ownership.py
@@ -277,7 +277,8 @@ def test_spec_update_draft_writer_materializes_markdown_without_applying(tmp_pat
   expected_path = (
     tmp_path
     / ".reviewcompass"
-    / "specs"
+    / "evidence"
+    / "features"
     / "workflow-management"
     / "conformance"
     / "2026-06-08-spec-update-drafts"
@@ -507,7 +508,8 @@ def test_check_pipeline_can_emit_contract_ownership_candidates(tmp_path):
   record_path = (
     tmp_path
     / ".reviewcompass"
-    / "specs"
+    / "evidence"
+    / "features"
     / "workflow-management"
     / "conformance"
     / "2026-06-08-check.md"
@@ -596,7 +598,8 @@ def test_check_pipeline_includes_spec_update_proposals(tmp_path):
   record_path = (
     tmp_path
     / ".reviewcompass"
-    / "specs"
+    / "evidence"
+    / "features"
     / "workflow-management"
     / "conformance"
     / "2026-06-08-check.md"
@@ -629,7 +632,7 @@ def test_check_pipeline_can_materialize_spec_update_draft_files(tmp_path):
 
   draft_result = result["contract_ownership"]["spec_update_draft_files"]
   assert draft_result["draft_dir"].endswith(
-    ".reviewcompass/specs/workflow-management/conformance/2026-06-08-spec-update-drafts"
+    ".reviewcompass/evidence/features/workflow-management/conformance/2026-06-08-spec-update-drafts"
   )
   assert len(draft_result["draft_files"]) == 1
   draft_path = Path(draft_result["draft_files"][0])
diff --git a/tools/conformance_evaluation/check_mode.py b/tools/conformance_evaluation/check_mode.py
index 14d9230f..f42c8fde 100644
--- a/tools/conformance_evaluation/check_mode.py
+++ b/tools/conformance_evaluation/check_mode.py
@@ -38,7 +38,7 @@ class CheckPipeline:
     if isolation.status == VerificationStatus.DEVIATION:
       raise ValueError("; ".join(isolation.reasons))
     estimate = EstimationModel().estimate(implementation_refs)
-    comparison = ComparisonModel().compare_one(
+    comparison = ComparisonModel.for_feature(self.root, feature).compare_one(
       criterion_id="criterion-1",
       existing={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
       inferred={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
diff --git a/tools/conformance_evaluation/comparison_model.py b/tools/conformance_evaluation/comparison_model.py
index 40cd9a83..74f4fe59 100644
--- a/tools/conformance_evaluation/comparison_model.py
+++ b/tools/conformance_evaluation/comparison_model.py
@@ -1,5 +1,12 @@
 """Comparison model for inferred and existing upstream documents."""
+import re
+from pathlib import Path
+
 from tools.conformance_evaluation.criteria import criterion_by_id
+from tools.conformance_evaluation.evaluation_record import (
+  conformance_dir,
+  legacy_conformance_dir,
+)
 
 
 class ComparisonModel:
@@ -7,6 +14,34 @@ class ComparisonModel:
     self.finding_counter = 0
     self.judgment_counter = 0
 
+  @classmethod
+  def for_feature(cls, root: Path, feature: str) -> "ComparisonModel":
+    """既存記録の最大番号から採番を継続する（design §10.7）。
+
+    凍結期（P3 まで）は新配置と凍結された旧配置を合算した走査範囲で
+    最大番号を統合算出し、旧凍結記録との ID 重複・リセットを防ぐ。
+    """
+    model = cls()
+    scan_roots = {
+      conformance_dir(root, feature),
+      legacy_conformance_dir(root, feature),
+    }
+    for scan_root in scan_roots:
+      if not scan_root.is_dir():
+        continue
+      for path in scan_root.rglob("*"):
+        if not path.is_file():
+          continue
+        try:
+          text = path.read_text(encoding="utf-8")
+        except UnicodeDecodeError:
+          continue
+        for match in re.finditer(r"\bCF-(\d+)\b", text):
+          model.finding_counter = max(model.finding_counter, int(match.group(1)))
+        for match in re.finditer(r"\bJD-(\d+)\b", text):
+          model.judgment_counter = max(model.judgment_counter, int(match.group(1)))
+    return model
+
   @staticmethod
   def format_next_id(prefix: str, number: int) -> str:
     width = 3 if number <= 999 else len(str(number))
diff --git a/tools/conformance_evaluation/contract_ownership.py b/tools/conformance_evaluation/contract_ownership.py
index e7c733b7..efedac23 100644
--- a/tools/conformance_evaluation/contract_ownership.py
+++ b/tools/conformance_evaluation/contract_ownership.py
@@ -2,6 +2,8 @@
 from pathlib import Path
 import yaml
 
+from tools.conformance_evaluation.evaluation_record import conformance_dir
+
 
 class ContractOwnershipMapError(ValueError):
   """Raised when a contract ownership entry violates the local vocabulary."""
@@ -183,14 +185,7 @@ class SpecUpdateDraftWriter:
     self.root = Path(root)
 
   def write(self, *, feature: str, run_date: str, drafts: list) -> dict:
-    draft_dir = (
-      self.root
-      / ".reviewcompass"
-      / "specs"
-      / feature
-      / "conformance"
-      / f"{run_date}-spec-update-drafts"
-    )
+    draft_dir = conformance_dir(self.root, feature) / f"{run_date}-spec-update-drafts"
     draft_dir.mkdir(parents=True, exist_ok=True)
     draft_files = []
     for draft in drafts:
diff --git a/tools/conformance_evaluation/evaluation_record.py b/tools/conformance_evaluation/evaluation_record.py
index c1c9f027..a1171eca 100644
--- a/tools/conformance_evaluation/evaluation_record.py
+++ b/tools/conformance_evaluation/evaluation_record.py
@@ -7,6 +7,21 @@ class RecordError(ValueError):
   """Raised when an evaluation record would violate the front-matter contract."""
 
 
+def conformance_dir(root: Path, feature: str) -> Path:
+  """書き込み正本の配置ルート（Req 6 受入 2、2026-06-12 配置規約）。
+
+  `_cross_feature` は実 feature ではない横断名前空間で、配置は specs 配下のまま（tasks T-015）。
+  """
+  if feature == "_cross_feature":
+    return Path(root) / ".reviewcompass" / "specs" / feature / "conformance"
+  return Path(root) / ".reviewcompass" / "evidence" / "features" / feature / "conformance"
+
+
+def legacy_conformance_dir(root: Path, feature: str) -> Path:
+  """凍結済み旧配置。読み取り互換（P3 まで）専用で、新規書き込みは禁止。"""
+  return Path(root) / ".reviewcompass" / "specs" / feature / "conformance"
+
+
 class EvaluationRecordModel:
   def __init__(self, root: Path):
     self.root = Path(root)
@@ -28,14 +43,7 @@ class EvaluationRecordModel:
       raise RecordError(f"unknown_mode_internal: {mode_internal}")
     if author == reviewer:
       raise RecordError("author_reviewer_must_be_distinct")
-    path = (
-      self.root
-      / ".reviewcompass"
-      / "specs"
-      / feature
-      / "conformance"
-      / f"{run_date}-{mode_internal}.md"
-    )
+    path = conformance_dir(self.root, feature) / f"{run_date}-{mode_internal}.md"
     path.parent.mkdir(parents=True, exist_ok=True)
     runtime_records = "\n".join(f"    - {item}" for item in related_records) or "    []"
     self_improvement = materialization_commit_hash or ""
@@ -57,3 +65,28 @@ class EvaluationRecordModel:
     )
     path.write_text(text, encoding="utf-8")
     return path
+
+  def read_record(self, *, feature: str, file_name: str) -> dict:
+    """新配置優先・旧配置フォールバックの読み取り（design §12.2、P3 まで）。"""
+    new_path = conformance_dir(self.root, feature) / file_name
+    legacy_path = legacy_conformance_dir(self.root, feature) / file_name
+    if new_path.is_file():
+      warnings = []
+      if legacy_path != new_path and legacy_path.is_file():
+        warnings.append(
+          f"duplicate_record_in_frozen_legacy_placement: {legacy_path}（新配置を正とする）"
+        )
+      return {
+        "path": new_path,
+        "text": new_path.read_text(encoding="utf-8"),
+        "source": "cross_feature_namespace" if feature == "_cross_feature" else "evidence",
+        "warnings": warnings,
+      }
+    if legacy_path.is_file():
+      return {
+        "path": legacy_path,
+        "text": legacy_path.read_text(encoding="utf-8"),
+        "source": "legacy_frozen",
+        "warnings": [],
+      }
+    raise RecordError(f"record_not_found: {feature}/{file_name}")
diff --git a/tools/conformance_evaluation/machine_verification.py b/tools/conformance_evaluation/machine_verification.py
index 6d42832a..288b956f 100644
--- a/tools/conformance_evaluation/machine_verification.py
+++ b/tools/conformance_evaluation/machine_verification.py
@@ -1,4 +1,6 @@
 """Machine verification for conformance-evaluation."""
+import re
+import subprocess
 from dataclasses import dataclass
 from enum import Enum
 from pathlib import Path
@@ -18,6 +20,11 @@ class VerificationResult:
   fail_closed: str
 
 
+# 凍結済み旧配置（P3 まで読み取り互換のみ。新規追加・変更は凍結違反）
+LEGACY_RECORD_PATTERN = re.compile(r"^\.reviewcompass/specs/[^/]+/conformance/")
+LEGACY_ESTIMATION_LOG_PATTERN = re.compile(r"^logs/estimation/")
+
+
 class MachineVerification:
   def __init__(self, root=None):
     self.root = Path(root) if root is not None else None
@@ -30,7 +37,7 @@ class MachineVerification:
     if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
       reasons.append("missing autonomous exploration prohibition")
     if self.root is not None:
-      log_dir = self.root / "logs" / "estimation" / run_id
+      log_dir = self.root / ".reviewcompass" / "evidence" / "estimation" / run_id
       log_dir.mkdir(parents=True, exist_ok=True)
       (log_dir / "prompt.log").write_text(
         "run_id: {run_id}\n"
@@ -54,3 +61,107 @@ class MachineVerification:
       reasons=reasons,
       fail_closed="blocking",
     )
+
+  def check_record_freeze(self, *, freeze_commit: str) -> VerificationResult:
+    """評価記録の旧配置に対する凍結違反検出（design §18 凍結期の検査範囲）。
+
+    凍結集合は P1 実装反映コミット時点の git 追跡履歴を正本とし、
+    それ以降の旧配置への追加・変更を違反として検出する。
+    `_cross_feature` は実 feature ではなく凍結対象外（tasks T-015）。
+    """
+    reasons = [
+      reason
+      for path, reason in self._legacy_violations(freeze_commit, LEGACY_RECORD_PATTERN)
+      if not self._is_cross_feature_namespace(path)
+    ]
+    return VerificationResult(
+      check_id="MV-3",
+      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
+      reasons=reasons,
+      fail_closed="recommended",
+    )
+
+  def check_estimation_log_freeze(self, *, freeze_commit: str) -> VerificationResult:
+    """推定ログの旧ルート（logs/estimation/）に対する凍結違反検出。
+
+    判定規則は評価記録と同一（P1 実装反映コミット以降の git 追跡履歴を正本とする）。
+    """
+    reasons = [reason for _, reason in self._legacy_violations(freeze_commit, LEGACY_ESTIMATION_LOG_PATTERN)]
+    return VerificationResult(
+      check_id="MV-6",
+      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
+      reasons=reasons,
+      fail_closed="recommended",
+    )
+
+  def check_existing_prompt_logs(self, *, forbidden_paths: list) -> VerificationResult:
+    """既存推定ログ（凍結済み旧 logs/estimation/ を含む）への MV-6 の 2 条件適用。
+
+    書き込みは常に新配置だが、読み取り検査は新旧両配置の prompt.log を対象とする
+    （tasks T-012「凍結済み旧推定ログも MV-6 の読み取り対象に含める」）。
+    """
+    reasons = []
+    log_roots = [
+      self.root / ".reviewcompass" / "evidence" / "estimation",
+      self.root / "logs" / "estimation",
+    ]
+    for log_root in log_roots:
+      if not log_root.is_dir():
+        continue
+      for log_path in sorted(log_root.rglob("prompt.log")):
+        prompt_text = self._extract_prompt_text(log_path.read_text(encoding="utf-8"))
+        for path in forbidden_paths:
+          if path in prompt_text:
+            reasons.append(f"forbidden upstream path in log: {log_path}: {path}")
+        if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
+          reasons.append(f"missing autonomous exploration prohibition: {log_path}")
+    return VerificationResult(
+      check_id="MV-6",
+      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
+      reasons=reasons,
+      fail_closed="blocking",
+    )
+
+  @staticmethod
+  def _extract_prompt_text(log_text: str) -> str:
+    # ログには forbidden_paths 一覧自体が含まれるため、prompt_text 区画だけを検査対象にする
+    lines = log_text.splitlines()
+    try:
+      start = lines.index("prompt_text:") + 1
+    except ValueError:
+      return log_text
+    end = next((i for i in range(start, len(lines)) if lines[i] == "forbidden_paths:"), len(lines))
+    return "\n".join(lines[start:end])
+
+  @staticmethod
+  def _is_cross_feature_namespace(path: str) -> bool:
+    return path.split("/")[:3] == [".reviewcompass", "specs", "_cross_feature"]
+
+  def _legacy_violations(self, freeze_commit: str, pattern: re.Pattern) -> list:
+    """(path, reason) の組を返す。
+
+    git ls-tree はワイルドカードを解釈しないため、木全体を列挙して Python 側で絞り込む。
+    未追跡の列挙に --exclude-standard を付けない（ignore された旧配置追加も凍結違反として検出する）。
+    """
+    frozen = self._matching(pattern, "ls-tree", "-r", "--name-only", freeze_commit)
+    tracked = self._matching(pattern, "ls-files")
+    untracked = self._matching(pattern, "ls-files", "--others")
+    changed = self._matching(pattern, "diff", "--name-only", freeze_commit)
+    added = sorted((tracked | untracked) - frozen)
+    modified = sorted(changed & frozen)
+    return (
+      [(path, f"added_after_freeze: {path}") for path in added]
+      + [(path, f"frozen_file_changed: {path}") for path in modified]
+    )
+
+  def _matching(self, pattern: re.Pattern, *args) -> set:
+    return {line for line in self._git_lines(*args) if pattern.match(line)}
+
+  def _git_lines(self, *args) -> list:
+    result = subprocess.run(
+      ["git", "-C", str(self.root), *args],
+      capture_output=True,
+      text=True,
+      check=True,
+    )
+    return [line for line in result.stdout.splitlines() if line]
diff --git a/tools/conformance_evaluation/post_hoc_intent_diff.py b/tools/conformance_evaluation/post_hoc_intent_diff.py
index dfb3d92b..6bab7e67 100644
--- a/tools/conformance_evaluation/post_hoc_intent_diff.py
+++ b/tools/conformance_evaluation/post_hoc_intent_diff.py
@@ -1,6 +1,8 @@
 """Post-hoc intent difference extraction for existing systems."""
 from pathlib import Path
 
+from tools.conformance_evaluation.evaluation_record import conformance_dir
+
 
 class PostHocIntentDiffError(ValueError):
   """Raised when post-hoc intent diff input or output is invalid."""
@@ -198,14 +200,7 @@ class PostHocIntentDiff:
     feature_partitioning: str,
     candidates: list,
   ) -> Path:
-    path = (
-      self.root
-      / ".reviewcompass"
-      / "specs"
-      / "conformance-evaluation"
-      / "conformance"
-      / f"{run_date}-post-hoc-intent-diff.md"
-    )
+    path = conformance_dir(self.root, "conformance-evaluation") / f"{run_date}-post-hoc-intent-diff.md"
     path.parent.mkdir(parents=True, exist_ok=True)
     path.write_text(
       self._record_text(
```
