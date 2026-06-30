# 次セッション継続用メモ

最終更新：2026-07-01（Codex ローカル）。最新状態は必ず `git log --oneline -5`、`git status --short --branch`、`.venv/bin/python3 tools/check-workflow-action.py next --json` を直接確認する。

## 1. 現在状態

- `main` は `origin/main` と同期済み。
- 最新 push 済みコミット：`56944d88 Implement workflow mixing preflight`
- 作業ツリーは clean。
- clean 状態の `tools/check-workflow-action.py next --json` は `kind: completed` を返す。
- 全 feature の workflow_state は implementation.approval まで完了済み。

## 2. 直近で完了した作業

- operation registry / preflight plan の ORP-1〜ORP-4 は linked TODO として完了済み。
  - ORP-1：operation registry schema / canonical command inventory 完了。
  - ORP-2：review-run / bundle / manifest / approval record の creation preflight 完了。
  - ORP-3：serial-only operation runner plan 完了。
  - ORP-4：workflow mixing preflight 完了。
- ORP-4 では、`workflow_mixing_preflight` executor を追加し、allowed files、実差分、out-of-scope 差分、pending conflict の解決選択肢を `operation-preflight` 出力へ載せるようにした。
- ORP-4 の TDD 実績：
  - 赤テストコミット：`072785c4 Add workflow mixing preflight red tests`
  - 実装コミット：`56944d88 Implement workflow mixing preflight`
  - 確認済み：focused 3 tests OK、`tests.tools.test_operation_registry_preflight` 21 tests OK、対象 checklist evidence 監査 OK。
- 既知の注意点：
  - `work-backlog audit-checklist-bridge` は、既存の別 TODO `todo-2026-06-24-commit-minimal-progress-output` の古い execution_history 由来で DEVIATION を出す。今回 ORP-4 の evidence 自体は OK。
  - `plan-2026-06-23-operation-registry-preflight.yaml` は plan 本体の `remaining_work` 表示に candidate が残っているが、linked TODO は ORP-1〜ORP-4 すべて completed。

## 3. 残っている未コミット変更

なし。

## 4. 次にやること

`.reviewcompass/backlog/plans/` の `status: candidate` から、次に着手する推奨順は以下。

1. `.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`
   - 副作用のある操作の実行仕様を固める。
   - operation registry / preflight が ORP-4 まで進んだため、次の土台作業として自然。
2. `.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml`
   - commit の停止点と承認 UX をさらに機械化する。
   - 現在の commit runner / approval 導線改善に直結する。
3. `.reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml`
   - 利用者起点の backlog / checklist 導線に effective prompt を付ける。
   - 「次へ」から TODO / checklist へ迷わず進むための補助。
4. `.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml`
   - effective prompt が古くなっていないか監査する。
   - 導線追加後の品質維持に効く。
5. `.reviewcompass/backlog/plans/plan-2026-06-23-normal-output-minimization-rollout.yaml`
   - CLI 出力を必要最小限に揃える。
6. `.reviewcompass/backlog/plans/plan-2026-06-23-working-note-self-check-hardening.yaml`
   - notes / TODO 系の軽量自己検査を強化する。
7. `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-review-prompt-isolation.yaml`
   - post-write review の criteria と target artifact を分離する。
8. `.reviewcompass/backlog/plans/plan-2026-06-23-api-review-run-hardening.yaml`
   - API review-run の prompt と後処理を堅くする。
9. `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-convergence-policy.yaml`
   - post-write verification が収束しない場合の方針を見直す。
10. `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-decision-mechanization.yaml`
    - proxy decision 実行と triage 適用を機械化する。
11. `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-assignment-tuning.yaml`
    - proxy assignment の model 選択や trigger signal を調整する。
12. `.reviewcompass/backlog/plans/plan-2026-06-23-triage-explanation-guard-quality.yaml`
    - triage 説明、重要度、guard 診断を改善する。
13. `.reviewcompass/backlog/plans/plan-2026-06-23-review-wave-recheck-pointer-hardening.yaml`
    - review-wave summary、recheck clearing、review-run pointer を堅くする。
14. `.reviewcompass/backlog/plans/plan-2026-06-23-session-record-operation-hardening.yaml`
    - session record の draft / formalize 操作を強化する。
15. `.reviewcompass/backlog/plans/plan-2026-06-23-autonomous-ledger-auditability.yaml`
    - 自律・並列実行の ledger 監査性を高める。
16. `.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml`
    - blocker 対応用の nested issue stack を追加する。
17. `.reviewcompass/backlog/plans/plan-2026-06-22-blocking-unit-control-improvements.yaml`
    - blocking unit 制御の残り改善。
18. `.reviewcompass/backlog/plans/plan-2026-06-23-deployment-tool-consolidation.yaml`
    - deploy-facing tool と runtime utility を統合する。
19. `.reviewcompass/backlog/plans/plan-2026-06-23-agent-adapter-revision.yaml`
    - 複数実行環境向けに agent adapter を見直す。
20. `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml`
    - 残りの operations / discipline 文書分類と移動。
21. `.reviewcompass/backlog/plans/plan-2026-06-23-reconstruction-cleanup-followups.yaml`
    - reconstruction 後の cleanup / deferred backlog を追跡する。
22. `.reviewcompass/backlog/plans/plan-2026-06-23-feature-quality-followups.yaml`
    - feature-local な品質 follow-up を記録・追跡する。
23. `.reviewcompass/backlog/plans/plan-2026-06-23-false-positive-reversal-metrics.yaml`
    - false-positive reversal の指標を記録する。
24. `.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml`
    - Workflow Navigator WebUI。schema / 操作導線がさらに固まってから着手する。
25. `.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml`
    - entrypoint coverage audit。周辺 TODO は進んでいるため、残差確認・plan close 候補。

最優先は `plan-2026-06-23-action-execution-spec.yaml`。着手時は plan を TODO にし、その後 checklist にして TDD で実行する方針を継続する。

## 5. 参照

- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- ワークフロー操作ガイド：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`
- operation registry / preflight 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`
- action execution spec 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`
- commit stop-point / approval UX 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml`
- user-initiated backlog/checklist effective prompt 計画：`.reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml`
- effective prompt freshness audit 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml`

過去の詳細は git log、`docs/notes/`、`docs/sessions/`、`.reviewcompass/evidence/work-units/checklists/` を正本とする。
