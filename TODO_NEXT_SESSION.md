# 次セッション継続用メモ

最終更新：2026-06-17（Claude セッション）。

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
  - `ab160d6b Allow run_review.py in Claude Code settings`
  - `04cee37b Add OK and 承諾 as allowed commit approval instructions`
  - `5c66b963 Add side-track discipline note to TODO candidate 2`
  - `1479ece3 Minimize commit output in WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
  - `102df667 Add one-step commit approval to WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
- 作業ツリーは clean。
- `main` は `origin/main` と同期済み。

## 3. 直近の重要メモ

- `docs/notes/2026-06-17-next-json-unique-state-redesign.md`
  - `next --json` を唯一の状態 / action selector とする設計メモ。
- `docs/notes/2026-06-17-next-json-effective-prompt-enforcement.md`
  - `next --json` 返値に紐づく effective prompt 必読、読了証跡、coverage audit、短文化の締め直しメモ。
- `docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md`
  - maintenance workflow 遵守、commit sandbox `.git/index.lock` preflight、maintenance / reopen / new workflow の使い分け、手続きの比例性の候補。
- `docs/notes/working/2026-06-17-working-note-verification-trigger-policy.md`
  - 作業中メモを API post-write に反復投入せず、配置場所 `docs/notes/working/` で `lightweight_self_check` に分岐する方針と実装メモ。
- `docs/notes/working/2026-06-17-commit-operation-card-and-next-json-prompt-selection.md`
  - commit 直前に読む短い一枚 `COMMIT_OPERATION_CARD.md`、Codex / Claude adapter 分離、`next --json` の不可逆操作用 prompt selection 改修案。
- `stages/completed/maintenance-2026-06-17-lightweight-self-check-location.yaml`
  - 作業中メモの場所ベース lightweight self-check 化、API review 複数 `--target` 証跡化補正まで完了済み。
- `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml`
  - commit sandbox preflight は実装・テスト・設計 / タスク反映まで完了済み。
- `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`
  - completed follow-up conformance は `gap_found`。MLE-GAP-001〜006 の仕様反映は **2026-06-12 に完了済み**（`stages/completed/reopen-procedure-2026-06-12.yaml`・`reopen-procedure-2026-06-12-parse-error-failclosed.yaml`）。

## 4. 次作業候補

1. **`next --json` 一意性と effective prompt 強制の締め直し**
   - `WORKFLOW_DISCIPLINE_MAP.yaml` coverage audit、全 action への `effective_prompt` 付与、読了証跡、アンカー節抽出を行う。
   - 他サブコマンドの JSON は次作業 selector ではない。次作業は必ず再度 `next --json` で決める。
   - `completed` 状態の `prompt_source_refs` に `WORKFLOW_NAVIGATION_FOR_CLAUDE.md` の side track 宣言ルール（§2 規則6）が含まれていない。`DISCIPLINE_MAP` の coverage audit で対応する。

2. **実アプリ pilot**
   - 未着手。対象アプリ root と、対象アプリ側 LLM が参照できる ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。
   - 配布前 smoke は実アプリ pilot 前の必要作業であり、現時点で完了済み扱いにしない。

3. **decision-source-lint の運用開始**
   - 仕組みは実装済み。次に重要決定が発生した時点で `.reviewcompass/decisions/` に構造化決定記録を作る。

完了済みとして候補から外したもの（直近）:

- **maintenance workflow protocol の明文化**
  - `98fe84a7 Add maintenance protocol to WORKFLOW_NAVIGATION.md` で完了。事前調査義務・開始条件（局所かつフィーチャー内閉じ）・3行宣言・TDD主導 vs 文書のみの区別を `WORKFLOW_NAVIGATION.md` に明文化。
  - side track として、コミット体験改善（1回化・出力最小化・承認語追加・run_review.py allow）も実施済み。

- **conformance 結果の仕様反映（MLE-GAP-001〜006）**
  - `stages/completed/reopen-procedure-2026-06-12.yaml` で workflow-management / conformance-evaluation の requirements・design・tasks・implementation 完了済み。
  - `stages/completed/reopen-procedure-2026-06-12-parse-error-failclosed.yaml` で MLE-DEC-005（パースエラー遮断分離）の実装まで完了済み。
  - 2026-06-12 のセッションで完了。TODO の更新漏れにより誤って残存していた。

- **commit sandbox preflight**
  - `eb028df2 Add commit sandbox preflight` と `stages/completed/maintenance-2026-06-17-commit-sandbox-preflight.yaml` で完了済み。
- **作業中メモの `lightweight_self_check` 化**
  - `9d374907 Add working note lightweight self-check` と `stages/completed/maintenance-2026-06-17-lightweight-self-check-location.yaml` で完了済み。
- **commit operation card と不可逆操作 prompt selection の Codex 側反映**
  - `3f9ff253 Add commit operation prompt` で完了済み。
- **Claude 側 adapter 修正**
  - `bc3840e6 Integrate Claude Code adapter into commit operation card` で完了済み。COMMIT_OPERATION_CARD に Claude Code 節を追加し、DISCIPLINE_MAP の adapter 参照をカード1本に集約。adapter_card フィールド廃止。

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
