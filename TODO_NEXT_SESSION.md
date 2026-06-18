# 次セッション継続用メモ

最終更新：2026-06-18（Claude セッション cf8204d6）。

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

- `next --json`: `completed`（すべての workflow_state が完了）
- 進行中手続き: reopen R-0（phase1-schema-definitions）の下流作業中（`downstream_impact_decisions` 追跡）
- 直近 commit:
  - `9305bf31 Fix session-record-capture hook: skip capture on non-clear SessionEnd reason`
  - `c85951b0 Finalize reopen R-0 design phase, add tasks T-015, clear post-write verification`
  - `178c597c Add session logs (2026-06-17/18), post-write manifest, and update TODO_NEXT_SESSION.md`
- 未コミット変更なし（クリーン状態）
- `main` は origin/main より 2 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（cf8204d6）で完了した主要作業

- **セッションログ churn 問題の根本修正**（コミット `9305bf31`）
  - `session-record-capture.sh`（セッション終了フック）に `reason` フィールドのチェックを追加
  - `reason` が `"clear"` 以外（例：`"auto_compact"` = コンテキスト圧縮による中間終了）のときは取り込みをスキップ
  - これにより、圧縮後の JSONL 追記で sha256（ハッシュ値）が変化し commit guard（コミット前検査）が「進行中」と誤判定する問題を解消
  - TDD（テスト先行）で実施：新テスト 2 件追加、6 件全通過

### 前セッション（854682f5）の主要作業（参考）

- **reopen R-0 design フェーズ完了**
  - design/triad-review・review-wave・alignment・approval 全段完了
  - design.md §5.2 に6点修正（$ref絶対URI化・verdict禁止・kind enum化ほか）
  - コミット `c85951b0`

- **reopen R-0 tasks フェーズ drafting 完了**
  - tasks.md に T-015（Phase 1 最小スキーマ定義ファイル作成）を追加
  - T-015 の完了条件：`tests/tools/test_phase1_schema_definitions.py` の17テストが全て pass すること

## 4. 次作業候補

1. **tasks/triad-review**
   - tasks.md の T-015 追加部分を対象に API 3者（claude/gpt/gemini）レビューを実施する。
   - 変更規模が小さいので観点は「T-015 の完了条件がテストと整合しているか」「前提タスクの設定が正しいか」を中心にする。

2. **tasks/review-wave → alignment → approval**
   - triad-review 完了後に続けて実施する。

3. **implementation フェーズ（TDD）**
   - T-015 の実装：`.reviewcompass/schema/required_action.schema.json` と `.reviewcompass/schema/next_action_response.schema.json` を作成する。
   - テストは `tests/tools/test_phase1_schema_definitions.py` に既に作成済み（失敗状態）。
   - 作成後に17テスト全 pass を確認。

4. **実アプリ pilot**
   - 未着手。対象アプリ root と ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。

完了済みとして候補から外したもの（直近）:

- **セッションログ churn 修正**（今セッション cf8204d6、コミット `9305bf31`）
- **reopen R-0 design フェーズ全段完了**（セッション 854682f5、コミット `c85951b0`）
- **reopen R-0 tasks drafting 完了**（セッション 854682f5、T-015 追加）
- **reopen R-0 phase1-schema-definitions の requirements フェーズ完了**（コミット `edc006c7`）

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
