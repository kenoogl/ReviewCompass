# 次セッション継続用メモ

最終更新：2026-06-19（Claude セッション）。

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
- 進行中手続き: なし。reopen R-0（phase1-schema-definitions）は完了済み（`stages/completed/reopen-procedure-2026-06-18.yaml`）。
  - T-015 実装完了（コミット `5d0b7001`）。17テスト全通過・3者レビュー全6件 leave-as-is。
  - `stages/implementation.yaml#alignment`・`#approval` の reopen-advance-gate 記録はスキップ（completed ファイルへの操作が不可のため、利用者判断で省略）。
- 直近 commit:
  - `5d0b7001 Implement T-015: create required_action and next_action_response JSON Schema files`
  - `4c0c8323 Add session log for 2026-06-18 session 854682f5`
  - `d8638a63 Complete tasks/triad-review for reopen R-0 phase1-schema-definitions: update T-015 completion criteria`
- 未コミット変更なし（クリーン状態）
- `main` は origin/main より 4 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（2026-06-19）で完了した主要作業

- **T-015 実装完了**（コミット `5d0b7001`）
  - `.reviewcompass/schema/required_action.schema.json`・`.reviewcompass/schema/next_action_response.schema.json` を TDD で作成
  - `tests/tools/test_phase1_schema_definitions.py` 17テスト全通過
  - 3者レビュー（claude-sonnet-4-6／gpt-5.5／gemini-3.1-pro-preview）全6件 leave-as-is
  - `stages/implementation.yaml#alignment`・`#approval` の reopen-advance-gate 記録はスキップ（利用者判断）

- **reopen R-0 tasks フェーズ完了**（コミット `d8638a63`、前セッション cf8204d6 継続）
  - tasks/triad-review を2ラウンド・3モデルで実施
  - T-015 完了条件を3点修正
  - tasks triad-review → review-wave → alignment → approval の全4ゲート完了

### 前セッション（cf8204d6 前半）の主要作業（参考）

- **セッションログ churn 問題の根本修正**（コミット `9305bf31`）
  - `session-record-capture.sh` に `reason` フィールドのチェックを追加、`"clear"` 以外は取り込みをスキップ
  - TDD で実施：新テスト 2 件追加、6 件全通過

## 4. 次作業候補

1. **実アプリ pilot**（最優先）
   - 未着手。対象アプリ root と ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。

完了済みとして候補から外したもの（直近）:

- **T-015 実装完了**（2026-06-19 セッション、コミット `5d0b7001`）
- **reopen R-0 tasks フェーズ全段完了**（セッション cf8204d6 継続、コミット `d8638a63`）
- **セッションログ churn 修正**（cf8204d6、コミット `9305bf31`）
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
