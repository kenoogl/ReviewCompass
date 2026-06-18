# 次セッション継続用メモ

最終更新：2026-06-18（Claude セッション 854682f5）。

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

- `next --json`: 未コミット変更があるため `post_write_verification` になる見込み（確認推奨）
- 進行中手続き: reopen R-0（phase1-schema-definitions）の下流作業中（`downstream_impact_decisions` 追跡）
- 直近 commit:
  - `edc006c7 Finalize reopen R-0 phase1-schema-definitions: requirements approval & recheck clear`
  - `ee86932f Fix reopen procedure: restore triad-review/review-wave gates and record step-3 stop point`
  - `025603bd Add workflow-management AC10/AC11: required_action and next_action_response schema definitions`
- **未コミット変更（今セッション作成）**：
  - `design.md`（§5.2 の6点修正：$ref絶対URI化・additionalProperties理由区別・verdict禁止・kind enum化ほか）
  - `triage.yaml`（design triad-review 全11件の最終判定記録）
  - `_cross_feature/reviews/2026-06-18-design-review-wave-*.md`（design review-wave 記録）
  - `_cross_feature/reviews/2026-06-18-design-alignment-*.md`（design alignment 記録）
  - `stages/completed/reopen-procedure-2026-06-18.yaml`（design フェーズ完了ステップを追記）
  - `tasks.md`（T-015 追加・タスク数 14→15・要件追跡2行追加）
- `main` は origin/main より 11 commit 先行（未 push）。

## 3. 直近の重要メモ

### 今セッション（854682f5）で完了した主要作業

- **reopen R-0 design フェーズ完了**
  - design/triad-review：3者 API レビュー + 深掘りレビュー実施。クラスタ A/B/C/D/S-1/S-2 の全11件をトリアージ。design.md §5.2 に6点修正を適用（深掘りレビューで承認した Case ウ適用・verdict禁止・kind enum化・additionalProperties理由区別）
  - design/review-wave：他6機能への影響確認、`existing_sufficient`
  - design/alignment：requirements AC10/AC11 との整合確認、`existing_sufficient`
  - design/approval：**利用者が明示承認**（「承認」発言）
  - `reopen-procedure-2026-06-18.yaml` の `downstream_impact_decisions` を更新（design 4段を追記・resolved に変更）

- **reopen R-0 tasks フェーズ drafting 完了**
  - tasks.md に T-015（Phase 1 最小スキーマ定義ファイル作成）を追加
  - タスク数を 14 → 15 に更新、要件追跡表に AC10/AC11 を追加
  - T-015 の完了条件：`tests/tools/test_phase1_schema_definitions.py` の17テストが全て pass すること

### 前セッション（8f34560b）の主要作業（参考）

- **reopen R-0（Phase 1 最小スキーマ定義）requirements フェーズの完了**
  - requirements alignment/approval ゲート通過・第4過程完了・recheck クリア（upstream_change_pending=false）
  - コミット `edc006c7`

## 4. 次作業候補

1. **今セッションの変更をコミット**（§1 起動検査クリア後）
   - §1 起動手順（next --json → post_write_verification など）を完了してから commit に進む。
   - 未コミット変更（設計書修正・トリアージ記録・review-wave/alignment記録・tasks追加）を guard commit で 1 コミットにまとめる。

2. **tasks/triad-review**
   - tasks.md の T-015 追加部分を対象に API 3者レビューを実施する。
   - 変更規模が小さいので観点は「T-015 の完了条件がテストと整合しているか」「前提タスクの設定が正しいか」を中心にする。

3. **tasks/review-wave → alignment → approval**
   - triad-review 完了後に続けて実施する。

4. **implementation フェーズ（TDD）**
   - T-015 の実装：`.reviewcompass/schema/required_action.schema.json` と `.reviewcompass/schema/next_action_response.schema.json` を作成する。
   - テストは `tests/tools/test_phase1_schema_definitions.py` に既に作成済み（失敗状態）。
   - 作成後に17テスト全 pass を確認。

5. **実アプリ pilot**
   - 未着手。対象アプリ root と ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。

完了済みとして候補から外したもの（直近）:

- **reopen R-0 design フェーズ全段完了**（今セッション 854682f5）
- **reopen R-0 tasks drafting 完了**（今セッション 854682f5、T-015 追加）
- **reopen R-0 phase1-schema-definitions の requirements フェーズ完了**（edc006c7）

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
