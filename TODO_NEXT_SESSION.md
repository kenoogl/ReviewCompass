# 次セッション継続用メモ

最終更新：2026-06-18（Claude セッション 8f34560b）。

この TODO は入口メモであり、作業順序の正本ではない。正本は常に `.venv/bin/python3 tools/check-workflow-action.py next --json` と各 feature の `spec.json`。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行する。
2. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
3. `git status --short` と `git log --oneline -5` で到達点を確認する。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。
5. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- `next --json`: `completed`
- 進行中手続き: なし
- 直近 commit:
  - `edc006c7 Finalize reopen R-0 phase1-schema-definitions: requirements approval & recheck clear`
  - `ee86932f Fix reopen procedure: restore triad-review/review-wave gates and record step-3 stop point`
  - `025603bd Add workflow-management AC10/AC11: required_action and next_action_response schema definitions`
  - `ff98ffdc Fix TODO_NEXT_SESSION.md: correct numbered list`
  - `c9b3e06d Triage all 15 pending-issues-review findings; record 3 design decisions`
- 作業ツリーはほぼ clean（進行中セッションログのみ未コミット、フック任せ）。
- `main` は origin/main より 11 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（8f34560b）で完了した主要作業

- **reopen R-0（Phase 1 最小スキーマ定義）の完了**
  - requirements alignment ゲート通過（判定: 既存で充分、追記不要）
  - requirements approval ゲート通過（利用者承認済み）
  - 第4過程（最終化）完了：feature_impact_decisions 7 機能分・downstream_impact_decisions 9 gate 分を記録
  - recheck フラグをクリア（upstream_change_pending=false・impacted_downstream_phases=[]）
  - コミット `edc006c7`

- **workflow-management の全段が再び完了状態に**
  - `next --json` が `completed` を返すことを確認
  - Phase 1 スキーマ実装（design/tasks/implementation の再確認）は次の reopen 手続きとして `downstream_impact_decisions` に `affected_update_required` で記録済み

### 前セッション（77e272a2）の主要作業（参考）

- **pending-issues-review 全 15 件のトリアージ完了**
  - 全件 leave-as-is。3 つの設計判断を設計メモに記録。コミット `c9b3e06d`。

## 4. 次作業候補

1. **Phase 1 スキーマ実装（reopen 手続きが必要）**
   - 対象：`reopen-procedure-2026-06-18.yaml` の `downstream_impact_decisions` に `affected_update_required` として記録済みの下流フェーズ。
   - 手順：design recheck → tasks recheck → implementation recheck（TDD）の順。
   - 実装ゴール：`tests/tools/test_phase1_schema_definitions.py` の 17 テストを全て通過させる。
   - 作成するファイル：
     - `.reviewcompass/schema/required_action.schema.json`（AC10：19 語彙の列挙）
     - `.reviewcompass/schema/next_action_response.schema.json`（AC11：`next --json` の応答スキーマ）

2. **実アプリ pilot**
   - 未着手。対象アプリ root と、対象アプリ側 LLM が参照できる ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。
   - 配布前 smoke は実アプリ pilot 前の必要作業であり、現時点で完了済み扱いにしない。

3. **decision-source-lint の運用開始**
   - 仕組みは実装済み。次に重要決定が発生した時点で `.reviewcompass/decisions/` に構造化決定記録を作る。

完了済みとして候補から外したもの（直近）:

- **reopen R-0 phase1-schema-definitions の requirements フェーズ完了**（edc006c7）

- **`pending-issues-review` の未確定事項への対処**
  - 全 15 件 leave-as-is で確定。設計判断 3 件を記録。`c9b3e06d` でコミット済み。

- **統合設計メモの作成**
  - `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` として完成・コミット済み。

- **maintenance workflow protocol の明文化**
  - `98fe84a7 Add maintenance protocol to WORKFLOW_NAVIGATION.md` で完了。

- **conformance 結果の仕様反映（MLE-GAP-001〜006）**
  - `stages/completed/reopen-procedure-2026-06-12.yaml` で完了済み。

- **commit sandbox preflight**
  - `eb028df2` と `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml` で完了済み。

- **作業中メモの lightweight_self_check 化**
  - `9d374907` と `stages/completed/maintenance-2026-06-17-lightweight-self-check-location.yaml` で完了済み。

- **commit operation card と不可逆操作 prompt selection の Codex 側反映**
  - `3f9ff253 Add commit operation prompt` で完了済み。

- **Claude 側 adapter 修正**
  - `bc3840e6 Integrate Claude Code adapter into commit operation card` で完了済み。

## 5. 会話ログ取り込み

- 原則フック任せ。
- Claude は SessionEnd / SessionStart。
- Codex は TODO 更新後の PostToolUse で現セッション下書き保存、次 SessionStart で前セッション下書きを正式化。
- 手動 backfill は終了済みセッション 1 件だけに限定する。
- 一括 backfill は使わない。

## 6. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の詳細履歴は git log、`docs/notes/`、`stages/completed/` を正本とする。
