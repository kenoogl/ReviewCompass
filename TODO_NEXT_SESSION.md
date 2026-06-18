# 次セッション継続用メモ

最終更新：2026-06-18（Claude セッション）。

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
  - `5688d4c5 Add working note on LLM-as-judge prompt quality`
  - `267d4595 Fix session-backfill hook to skip already-imported sessions; fix Unicode filename handling in commit check`
  - `2df06b17 Add session log for 2026-06-17 session d55d02bc`
  - `3aa29ed4 Update design memos and operations docs: effect_kind/approval_required separation`
  - `0c6579d3 Add discipline_llm_as_judge_prompting.md and update README`
- 作業ツリーはほぼ clean（進行中セッションログのみ未コミット、フック任せ）。
- `main` は origin/main より 5 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッションで完了した主要作業

- **統合設計メモ完成**：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
  - D-003（選択層）と機械化設計（実行層）の接続点を整理した正本。
  - `effect_kind`（副作用の種別）は `read / write / state_mutation / external_call` の4値に確定。`irreversible_action` は廃止。
  - `approval_required`（実行前に人間の承認が必要か）は `effect_kind` とは独立した属性として定義。
  - `record_human_decision` は `state_mutation` かつ `approval_required: false`（承認ゲートの内側操作）。

- **機械化設計メモへの3者レビュー指摘を解消**：`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
  - §3.1：`approval_required: true` の具体的な操作リストを明記（`commit_stop_point` 等7種）。
  - §7：D-003 を Phase 0 として位置づけ、実装順序を §4.1 を正本として更新。
  - Phase 2 の `operation-list --json` 属性に `approval_required` を追加。

- **WORKFLOW_NAVIGATION.md の語彙統一**：`docs/operations/WORKFLOW_NAVIGATION.md`
  - `reopen_in_progress` セクションの `required_action` 語彙を正式名称に統一。

- **セッション記録フック修正**：`.claude/hooks/session-record-capture-previous.sh`
  - コンテキスト圧縮による `SessionStart` 再発火で、現セッションが前セッションとして誤取り込みされる問題を修正。
  - 取り込み済みセッション ID を `.reviewcompass/runtime/session-backfill-done/` にマーカーとして記録し、二重取り込みを防止。

### 次セッションの主要課題

**`pending-issues-review` の未確定事項15件**（`human_required`、全件未判定）

レビューラン：`.reviewcompass/evidence/review-runs/2026-06-18-pending-issues-review/`

主な未確定事項（Sonnet primary の所見より）：
1. `alignment` gate の `effect_kind`（`write` か `state_mutation` か複合値か）
2. Phase 0 と Phase 1 の並行作業の分割方針
3. 状態スナップショットの出力タイミング（`next --json` 後の自動出力 vs 専用サブコマンド）
4. D-003 §8 の72シナリオを Phase 6 の監査テストとして使う具体的方法
5. 機械タスクの自動実行担当コマンド（`next --json` 呼び出し側 vs 新規サブコマンド）
6. LLM 裁判官（§5.2）の実行基盤（`run_review.py` 流用 vs 新規スクリプト）
7. 言語タスクの入出力スキーマの具体定義
8. state repair（reopen plan 再コンパイル）の Phase 0 組み込み方法
9. `docs/operations/` から `.reviewcompass/` への実行時参照ファイル移動

これらはすべて設計上の判断事項であり、次セッションで利用者と議論して決める。

### 参考メモ（前セッションから継続）

- `docs/notes/2026-06-17-next-json-effective-prompt-enforcement.md`
  - effective prompt 必読・読了証跡・coverage audit・短文化の方針メモ。
- `docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md`
  - maintenance workflow 遵守・commit sandbox preflight・手続きの比例性の候補。

## 4. 次作業候補

1. **`pending-issues-review` の未確定事項への対処**（最優先）
   - 上記9件（Sonnet）＋GPT/Gemini の追加所見計15件に対し、`review_triage.py decide` で判定を記録する。
   - 設計判断が必要なものは利用者と議論してから決める。
   - 証跡：`.reviewcompass/evidence/review-runs/2026-06-18-pending-issues-review/triage.yaml`

2. **実アプリ pilot**
   - 未着手。対象アプリ root と、対象アプリ側 LLM が参照できる ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。
   - 配布前 smoke は実アプリ pilot 前の必要作業であり、現時点で完了済み扱いにしない。

3. **decision-source-lint の運用開始**
   - 仕組みは実装済み。次に重要決定が発生した時点で `.reviewcompass/decisions/` に構造化決定記録を作る。

完了済みとして候補から外したもの（直近）:

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
