# 次セッション継続用メモ

最終更新：2026-06-19（Codex セッション、`561e5a45` push 済み）。

この TODO は入口メモであり、作業順序の正本ではない。正本は各 feature の `spec.json` と `tools/check-workflow-action.py next --json` の機械判定である。現在は reopen 手続き中なので、`stages/in-progress/reopen-procedure-2026-06-19.yaml`、`docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`、`spec.json` を照合して進める。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を現在位置の機械判定として確認する。
2. 各 feature の `spec.json` と `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md` を照合する。
3. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
4. `git status --short` と `git log --oneline -5` で到達点を確認する。
5. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、`spec.json` と手動進捗表に照らして扱いを判断する。
6. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- 管理状態: `next --json`、`spec.json`、手動進捗表で管理中。
- 手動進捗表: `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
- 進行中手続き: `stages/in-progress/reopen-procedure-2026-06-19.yaml`。
  - 統合設計メモ Requirement 13〜16 反映後の workflow state 差し戻し。
  - 第1過程（判定とフラグ差し戻し）と第2過程（intent / requirements 反映）は完了済み。
  - 第3過程内の requirements triad-review は新規3者レビュー、proxy_model 判断、must-fix / should-fix 反映、post-write verification、gate 完了まで完了。
  - 第3過程内の requirements review-wave / impact check は gate 完了まで完了。
  - requirements alignment は証跡作成、post-write verification、gate 完了まで完了。
  - requirements approval は利用者発言「承認」に基づき gate 完了まで完了。
  - 次は design drafting。`next --json` は `reopen_in_progress` / `required_action: run_reopen_drafting` を返す。
  - reopen R-0（phase1-schema-definitions）は完了済み（`stages/completed/reopen-procedure-2026-06-18.yaml`）。
  - T-015 実装完了（コミット `5d0b7001`）。17テスト全通過・3者レビュー全6件 leave-as-is。
  - `stages/implementation.yaml#alignment`・`#approval` の reopen-advance-gate 記録はスキップ（completed ファイルへの操作が不可のため、利用者判断で省略）。
- 直近 commit:
  - `561e5a45 Minimize high-frequency CLI output`
  - `9fa95e30 Make commit wrapper executable`
  - `44be3f7b Minimize normal precheck output`
  - `5420af3f Narrow push in-progress guard`
  - `edb83ab7 Add current staged commit wrapper`
- `main` と `origin/main` は同期済み。

## 3. 直近の重要メモ

### 今セッション（2026-06-19）で完了した主要作業

- **高頻度 CLI の正常系出力最小化を実装・push 済み**（コミット `561e5a45`）
  - 共通 helper `tools/normal_output.py` を追加
  - `run_review.py` は既定 stdout を 1 行 summary にし、詳細は `review_summary.md` と `--verbose` に分離
  - `run_role.py` は成果物保存先ありの場合に 1 行 summary、保存先なし／`--verbose` では YAML 出力を維持
  - `prepare_post_write_review.py` は `review_target` / `metadata` / `targets` の 1 行 summary に変更
  - `_experiment_n_model.py` に `--out` / `--verbose` を追加し、`--out` 指定時は応答全文をファイルへ保存
  - `commit-from-current-staged.py` / `guarded-git-commit.py` / `make-triage-decision.py` / `make-post-write-manifest.py` の短い成功出力をテストで固定
  - post-write verification: `.reviewcompass/post-write-verification/post-write-2026-06-19-274.yaml`（no findings）

- **正常系出力最小化の共通規律と棚卸しを追加**（コミット `561e5a45`）
  - `docs/disciplines/discipline_normal_output_minimization.md`
  - `docs/notes/working/2026-06-19-normal-output-minimization-tool-inventory.yaml`
  - `docs/notes/working/2026-06-19-normal-output-minimization-implementation-policy.md`
  - 未対応: `tools/experiments/*_temp.py` 群、medium priority の lint / session-record / deployment 系 CLI、既存 redirect 利用箇所の `--out` 置換確認

- **統合設計メモの intent／requirements 反映を完了**（コミット `50c6cbda`）
  - `intent/INTENT.md` に裁定負荷を LLM の暗黙判断へ隠さない意図、現在位置と次操作の一意性、workflow-management の責務を追記
  - `.reviewcompass/specs/workflow-management/requirements.md` に Requirement 13〜16 を追加し、operation contract、承認ゲート、側道スタック、状態スナップショット、構造化有効プロンプト、Phase 0〜6 を要件化
  - `implementation_review_independent_3way_codex_operator` で3者 traceability review を実施し、should-fix 候補を反映
  - post-write verification は `post_write_verification_google` で no findings

- **統合設計メモ反映用の workflow state 差し戻しを開始**（未コミット）
  - `docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md` を作成
  - `stages/in-progress/reopen-procedure-2026-06-19.yaml` を発行
  - `.reviewcompass/specs/workflow-management/spec.json` を requirements triad-review から再開する状態へ差し戻し

- **requirements triad-review を実施し proxy_model 判断・反映・gate 完了まで完了**（未コミット）
  - review run: `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/`
  - proxy_model: `gemini-3.1-pro-preview`
  - final labels: C1/C2 must-fix、C3〜C7 should-fix、C8/C9 leave-as-is
  - C1〜C7 は `.reviewcompass/specs/workflow-management/requirements.md` と review run の `review-response.md` に反映済み
  - post-write verification: `.reviewcompass/post-write-verification/post-write-2026-06-19-254.yaml`（no findings）
  - `stages/requirements.yaml#triad-review` は `reopen-advance-gate` で完了済み

- **requirements review-wave / impact check を実施**（未コミット）
  - artifact: `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md`
  - summary: `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md`
  - decision: workflow-management 以外は `existing_sufficient`
  - post-write verification: `.reviewcompass/post-write-verification/post-write-2026-06-19-256.yaml`（no findings）
  - `stages/requirements.yaml#review-wave` は `reopen-advance-gate` で完了済み
  - 次は requirements alignment

- **requirements alignment を実施**（未コミット）
  - artifact: `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md`
  - decision: `existing_sufficient`
  - post-write verification: `.reviewcompass/post-write-verification/post-write-2026-06-19-258.yaml`（no findings）
  - `stages/requirements.yaml#alignment` は `reopen-advance-gate` で完了済み

- **requirements approval を完了**（未コミット）
  - artifact: `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-approval.md`
  - decision: `approved`
  - approval source: 利用者発言「承認」
  - post-write verification: no findings
  - `stages/requirements.yaml#approval` は `reopen-advance-gate` で完了済み
  - 次は design drafting

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

1. **統合設計メモ反映の design drafting（推奨）**
   - 手続き: `stages/in-progress/reopen-procedure-2026-06-19.yaml`
   - 手動進捗表: `docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
   - `next --json`: `kind: reopen_in_progress`、`required_action: run_reopen_drafting`
   - 新規3者レビュー、proxy_model 判断、C1/C2 must-fix と C3〜C7 should-fix の requirements 反映、post-write verification、gate 完了は完了済み。
   - requirements review-wave / impact check は gate 完了まで完了。
   - requirements alignment は gate 完了まで完了。
   - requirements approval は利用者発言「承認」に基づき gate 完了済み。
   - 次に Requirement 13〜16 を `.reviewcompass/specs/workflow-management/design.md` へ展開する。

2. **正常系出力最小化の残件確認（side track 候補）**
   - `_experiment_n_model.py` の既存 shell redirect 利用箇所を `--out` に置換できるか確認する。
   - medium priority の lint / session-record / deployment 系 CLI を共通 formatter へ接続するか判断する。
   - 本線ではないため、着手する場合は maintenance / side track として扱う。

3. **実アプリ pilot**
   - 未着手。対象アプリ root と ReviewCompass 配布物配置先を決めるところから始める。
   - 正本: `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` §8、§9、§19、および `docs/operations/DEPLOYMENT.md` §8。

完了済みとして候補から外したもの（直近）:

- **未 push 5 commit の push**（Codex セッション、`origin/main` へ push 済み）
- **高頻度 CLI の正常系出力最小化**（Codex セッション、コミット `561e5a45`、push 済み）
- **統合設計メモ反映の正式 workflow 段整理開始**（Codex セッション、reopen 分類・spec.json 差し戻し実施中）
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
