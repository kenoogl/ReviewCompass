# 次セッション継続用メモ

最終更新：2026-06-19（Codex セッション）。

この TODO は入口メモであり、作業順序の正本ではない。正本は各 feature の `spec.json`。現在はシステム自体の改変中であり、`next --json` が正しい現在位置を返す保証はないため、`docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md` と `spec.json` を照合して手動管理する。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. 各 feature の `spec.json` と `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md` を照合する。
2. `.venv/bin/python3 tools/check-workflow-action.py next --json` は参考情報として実行してよいが、現在は正本扱いしない。
3. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
4. `git status --short` と `git log --oneline -5` で到達点を確認する。
5. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、`spec.json` と手動進捗表に照らして扱いを判断する。
6. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- 管理状態: `spec.json` と手動進捗表で管理中。`next --json` は参考扱い。
- 手動進捗表: `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
- 進行中手続き: なし。reopen R-0（phase1-schema-definitions）は完了済み（`stages/completed/reopen-procedure-2026-06-18.yaml`）。
  - T-015 実装完了（コミット `5d0b7001`）。17テスト全通過・3者レビュー全6件 leave-as-is。
  - `stages/implementation.yaml#alignment`・`#approval` の reopen-advance-gate 記録はスキップ（completed ファイルへの操作が不可のため、利用者判断で省略）。
- 直近 commit:
  - `72f98558 Record Claude session logs`
  - `50c6cbda Recover integrated design requirements`
  - `2e9ea5e5 Document Codex guarded commit execution`
  - `6d703791 Add Codex LLM-as-judge prompt hook`
  - `51273eef Update TODO_NEXT_SESSION.md: add incomplete integrated-design requirements memo`
- 未コミット変更なし（クリーン状態。TODO 更新作業中を除く）
- `main` は origin/main より 4 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（2026-06-19）で完了した主要作業

- **統合設計メモの intent／requirements 反映を完了**（コミット `50c6cbda`）
  - `intent/INTENT.md` に裁定負荷を LLM の暗黙判断へ隠さない意図、現在位置と次操作の一意性、workflow-management の責務を追記
  - `.reviewcompass/specs/workflow-management/requirements.md` に Requirement 13〜16 を追加し、operation contract、承認ゲート、側道スタック、状態スナップショット、構造化有効プロンプト、Phase 0〜6 を要件化
  - `implementation_review_independent_3way_codex_operator` で3者 traceability review を実施し、should-fix 候補を反映
  - post-write verification は `post_write_verification_google` で no findings

- **Codex 側の LLM-as-judge prompt hook を追加**（コミット `6d703791`）
  - `3者レビュー` 等の発話で `docs/disciplines/discipline_llm_as_judge_prompting.md` を読む導線を Codex 側にも追加

- **Codex guarded commit 実行方針を文書化**（コミット `2e9ea5e5`）
  - Codex では `guarded-git-commit.py` を最初から sandbox 外で実行する運用を `docs/operations/WORKFLOW_PRECHECK.md` に明記

- **Claude session logs を記録**（コミット `72f98558`）
  - 2026-06-18 Claude セッション 2 件の evidence 層／docs 層を追加

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

1. **未 push 4 commit の push 判断**
   - `main` は origin/main より 4 commit 先行。
   - 対象：`6d703791`、`2e9ea5e5`、`50c6cbda`、`72f98558`。
   - push は不可逆操作として利用者の明示承認と guard を通す。

2. **実アプリ pilot**
   - 未着手。対象アプリ root と ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。

3. **統合設計メモ反映の正式 workflow 段整理**
   - 手動進捗表: `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
   - まず `.reviewcompass/specs/workflow-management/spec.json` の workflow_state と実体を照合する。
   - requirements の formal triad-review は原則として正式段へ進める。ただし、その時点の `spec.json`、実体、利用者判断に従い、新規3者レビューを実施するか、既存 traceability review を正式段の証跡として採用するかを決める。

完了済みとして候補から外したもの（直近）:

- **T-015 実装完了**（2026-06-19 セッション、コミット `5d0b7001`）
- **統合設計メモの要件追記**（Codex セッション、コミット `50c6cbda`）
- **Codex LLM-as-judge prompt hook 追加**（Codex セッション、コミット `6d703791`）
- **Claude session logs 記録**（Codex セッション、コミット `72f98558`）
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
- integrated design manual progress: `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`

過去の詳細履歴は git log、`docs/notes/`、`stages/completed/` を正本とする。
