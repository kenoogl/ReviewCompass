# 次セッション継続用メモ

最終更新：2026-06-18（Claude セッション 77e272a2）。

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
  - `c9b3e06d Triage all 15 pending-issues-review findings; record 3 design decisions`
  - `f2cd361a Refresh TODO: reflect session results and pending-issues-review findings`
  - `5688d4c5 Add working note on LLM-as-judge prompt quality`
  - `267d4595 Fix session-backfill hook to skip already-imported sessions; fix Unicode filename handling in commit check`
  - `2df06b17 Add session log for 2026-06-17 session d55d02bc`
- 作業ツリーはほぼ clean（進行中セッションログのみ未コミット、フック任せ）。
- `main` は origin/main より 6 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（77e272a2）で完了した主要作業

- **pending-issues-review 全15件のトリアージ完了**
  - 全件 `leave-as-is`。前セッション（eec103c2）で文書修正済みのため再修正不要。
  - GPT ERROR 3件（gpt-001〜003）の承認記録を `.reviewcompass/evidence/review-runs/2026-06-18-pending-issues-review/approval.yaml` に作成。

- **3つの設計判断を設計メモに記録**
  1. **Phase 0/1 分割方針**（§7 item 2）：Phase 0 開始前に必要な最小 Phase 1 作業は `required_action` 19語彙のスキーマ定義と `next --json` 応答スキーマの定義のみ。
  2. **実行担当コマンド**（機械化設計 §8 item 2）：専用新規サブコマンド（例 `run-next`）を作成。`next --json` は判定専用に維持。
  3. **言語タスク入出力スキーマ**（機械化設計 §8 item 4）：枠組みを Phase 1 で定義、判定点ごとの詳細は Phase 4 で定義。

- **post-write 検証とコミット完了**
  - 統合設計メモ変更：Gemini レビュー（0 所見）→ post-write-2026-06-18-008.yaml
  - 機械化設計メモ変更：lightweight self-check → post-write-2026-06-18-239.yaml
  - コミット：`c9b3e06d`

### 前セッション（f2cd361a 時点）の主要作業（参考）

- **統合設計メモ完成**：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
- **機械化設計メモへの3者レビュー指摘を解消**：`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
- **WORKFLOW_NAVIGATION.md の語彙統一**
- **セッション記録フック修正**

### 参考メモ（前セッションから継続）

- `docs/notes/2026-06-17-next-json-effective-prompt-enforcement.md`
  - effective prompt 必読・読了証跡・coverage audit・短文化の方針メモ。
- `docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md`
  - maintenance workflow 遵守・commit sandbox preflight・手続きの比例性の候補。

## 4. 次作業候補

1. **実アプリ pilot**
   - 未着手。対象アプリ root と、対象アプリ側 LLM が参照できる ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。
   - 配布前 smoke は実アプリ pilot 前の必要作業であり、現時点で完了済み扱いにしない。

2. **decision-source-lint の運用開始**
   - 仕組みは実装済み。次に重要決定が発生した時点で `.reviewcompass/decisions/` に構造化決定記録を作る。

完了済みとして候補から外したもの（直近）:

- **`pending-issues-review` の未確定事項への対処**（最優先）
  - 全15件 `leave-as-is` で確定。設計判断3件を記録。`c9b3e06d` でコミット済み。

- **統合設計メモの作成**
  - `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` として完成・コミット済み。
  - effect_kind 4値確定、approval_required の独立属性化、実装順序（Phase 0→1→2〜6）を確定。

- **maintenance workflow protocol の明文化**
  - `98fe84a7 Add maintenance protocol to WORKFLOW_NAVIGATION.md` で完了。

- **conformance 結果の仕様反映（MLE-GAP-001〜006）**
  - `stages/completed/reopen-procedure-2026-06-12.yaml` で完了済み。

- **commit sandbox preflight**
  - `eb028df2 Add commit sandbox preflight` と `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml` で完了済み。

- **作業中メモの `lightweight_self_check` 化**
  - `9d374907 Add working note lightweight self-check` と `stages/completed/maintenance-2026-06-17-lightweight-self-check-location.yaml` で完了済み。

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
