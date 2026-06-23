# 次セッション継続用メモ

最終更新：2026-06-23（Codex セッション。`main` と `origin/main` は同期済み。最新 commit はこのメモに固定せず、必ず `git log --oneline -5` で確認する）。

この TODO は入口メモであり、作業順序の正本ではない。正本は各 feature の `spec.json` と `tools/check-workflow-action.py next --json` の機械判定である。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を現在位置の機械判定として確認する。
2. `git status --short --branch` と `git log --oneline -5` で到達点を確認する。
3. `next_action.effective_prompt.effective_prompt_path` がある場合は、その本文を読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、通常作業へ進まず、その action に従う。
5. commit / push / spec.json workflow_state 変更は不可逆操作として扱い、利用者の明示承認と guard を通す。

## 2. 現在位置

- `main` と `origin/main` は同期済み（起動時に `git status --short --branch` で再確認する）。
- 作業ツリーは clean（起動時に再確認する）。
- 最新 commit はこのメモではなく `git log --oneline -5` を正とする。
- 直近の実装修正系列は、post-write prompt 機械化、guidance 配置整理、旧 guidance 削除、repair 例外実装、push guard 補修、blocking unit / checklist / commit operation 機械化補修、next action effective prompt coverage 監査である。
- `next --json` は `completed`。
- すべての feature / phase / stage の `workflow_state` は完了済み。
- `workflow-management` の Requirement 13〜16 を基点にした reopen R-0 は、requirements / design / tasks / implementation まで完了済み。
- reopen R-0 完了後に発生した post-write prompt 機械化、guidance 配置整理、旧 guidance 削除、repair 例外実装、push guard 補修、blocking unit / checklist / commit operation 機械化補修、next action effective prompt coverage 監査も commit / push 済み。
- `blocking unit production readiness` の blocking unit は完了し、evidence 記録、parent resume、push まで完了済み。
- 進行中ファイルはない。
- 直近 push 済み commit は `865cd1a8 Plan remaining guidance relocation`。起動時には必ず `git log --oneline -5` で再確認する。
- 次の pending gate はない。

## 3. 次作業

次に行う本線 workflow 作業はない。次セッションでは、まず `next --json` と `git status --short --branch` を再確認し、`completed` / clean / synced が維持されていることを確認する。

新しい作業を始める場合：

1. 利用者の新規指示を受ける。
2. `next --json` が `completed` のままか確認する。
3. 必要なら新しい workflow / reopen / maintenance として開始条件を確認する。

現在の有力な次作業候補：

1. `plan-2026-06-23-guidance-relocation-and-docs-classification.yaml` に基づき、残存 `docs/operations` / `docs/disciplines` の inventory / classification table を作る。ファイル移動はまだ行わない。
2. `plan-2026-06-23-entrypoint-coverage-audit.yaml` に基づき、entrypoint coverage audit の ECA-1（現在入口の棚卸し）を始める。
3. `plan-2026-06-23-effective-prompt-freshness-audit.yaml` に基づき、effective prompt freshness audit の EPFA-0 / EPFA-1（現状固定テストと source SHA red test）を始める。
4. `plan-2026-06-23-postwrite-review-prompt-isolation.yaml` に基づき、post-write review の criteria / target 分離設計を詳細化する。

進め方の注意：

- `next --json` が示す停止点を飛ばさない。
- commit / push は利用者の明示指示がある場合だけ実行する。
- triad-review の API review-run 前には、variant と role 割当を機械判定または設定から確定し、必要に応じて利用者に提示して停止する。
- review prompt は、上流資料のパス名だけでなく、必要な本文または要点を含める。単にパスだけを渡さない。
- 平易な進捗説明を使う。内部状態名を主語にせず、「今どの段階か」「何をしたか」「次に何をするか」を先に述べる。
- 直近の改善候補として、commit 後に残る `.reviewcompass/runtime/work-units/commit-unit.json` を手動削除せずに済む `commit-unit clear` 相当の機械処理を検討できる。

## 4. 直近の完了事項

- Requirement 13〜16 を基点に、requirements/design/tasks/implementation を縦方向意図監査の結果へ合わせて再生成・修正。
- requirements triad-review を実施し、API 版 gpt-5.5 proxy_model 判定で C1〜C3 を should-fix として反映、C4 は leave-as-is。
- requirements review-wave を実施し、他 feature の requirements 正本変更は不要と確認。
- requirements alignment を完了し、Requirement 13〜16 と design/tasks の追跡、triad-review 修正反映、review-wave 影響確認を記録。
- design / tasks / implementation の triad-review、review-wave、alignment、approval を完了。
- implementation review-run の Req15 / Req16 API レビュー結果を同根クラスタへ整理し、triage 案と traceability report を保存。
- API レビュー用 prompt の品質課題を受け、汎用コア + カスタマイズ、main preanalysis、prompt audit、variant default 機械判定の考え方を整理・実装。
- `workflow-management` implementation approval 完了により、全 workflow_state が `completed` になった。
- Codex の commit 実行環境と利用者向け報告文の規律を明確化。
- commit 中の進行報告最小化規律を追加。
- commit 操作機械処理化の残作業は `.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml` に移した。
- post-write prompt 機械化では、判定点ごとの canonical effective prompt を固定し、`next --json` から読む prompt を機械的に決める方向へ補修した。
- guidance 配置整理では、`.reviewcompass/guidance` を正本として参照更新し、旧 `docs/operations` / `docs/disciplines` の guidance 重複を削除した。
- 旧 guidance 削除は通常の post-write 制約と衝突したため、今回限りの手動修復例外を機械的に扱う `repair-workflow-state prepare` 経路を追加した。
- push 前 lint が削除済み deployable artifact を読もうとして止まる問題を修正し、削除ファイルは配置非依存 lint の commit 内容読み取り対象から除外した。
- `blocking unit production readiness` の作業として、work-unit entry/exit/resume、commit-unit freeze/check、staged digest、stale/mixing 検出、work unit と commit unit の束縛、evidence unit mismatch 検出、blocking unit 中の parent commit 禁止を整備した。
- `PARENT_COMMIT_DURING_BLOCKING_UNIT` により、active blocking unit 中に commit unit なしで親作業 commit を進める経路を遮断するようにした。
- `EVIDENCE_UNIT_MISMATCH` により、post-write manifest の `unit_binding` が現在の commit unit と一致しない場合に理由コードを返すようにした。
- `blocking unit production readiness` の runtime checklist は全 37 項目を完了確認し、`.reviewcompass/evidence/work-units/blocking-units/unit-2026-06-22-blocking-unit-production-readiness.yaml` に完了 evidence を保存した。
- `main` を `origin/main` へ push 済み。正確な終端 commit は `git log --oneline -5` と `git status --short --branch` を正とする。
- deploy-facing tool の重複整理は `.reviewcompass/backlog/plans/plan-2026-06-23-deployment-tool-consolidation.yaml` に将来計画として記録した。
- `next --json` が返し得る `next_action.kind` と effective prompt の接続を監査し、`parent_resume_pending`、`blocking_unit_required`、`blocking_unit_in_progress`、`commit_mixing_risk`、`commit_unit_stale` の map 接続漏れを補修した。
- post-write API review で出た指摘は proxy mode で検査し、criteria / target 分離問題は `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-review-prompt-isolation.yaml` に split-out、manifest / human_required 文言は `WORKFLOW_NAVIGATION.md` に反映した。
- 修正後の post-write verification は実 target 2ファイルを指定した v3 review-run で findings 0 を確認し、`.reviewcompass/post-write-verification/post-write-2026-06-23-005.yaml` に正しい target manifest を保存した。
- entrypoint coverage audit の構想は `.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml` に記録した。
- 残存 `docs/operations` / `docs/disciplines` の分類・移動・検査計画は `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml` に記録した。前回の guidance 移動失敗を踏まえ、次は inventory / classification table を先に作り、移動はまだ行わない。

## 5. 参照

- workflow navigation: `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`
- session guide: `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md`
- discipline map: `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml`
- workflow-management tasks: `.reviewcompass/specs/workflow-management/tasks.md`
- workflow-management spec: `.reviewcompass/specs/workflow-management/spec.json`

過去の詳細履歴は git log、`docs/notes/`、`docs/archive/todo/`、`docs/sessions/` を正本とする。
