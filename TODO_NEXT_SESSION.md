# 次セッション継続用メモ

最終更新：2026-06-30（Codex ローカル）。最新状態は必ず `git log --oneline -5`、`git status --short --branch`、`.venv/bin/python3 tools/check-workflow-action.py next --json` を直接確認する。

## 1. 現在状態

- `main` は `origin/main` と同期済みの想定。
- 最新 push 済みコミット：`3ec542be Add operation trigger resolver`
- clean 状態の `tools/check-workflow-action.py next --json` は `kind: completed` を返す想定。
- 全 feature の workflow_state は implementation.approval まで完了済み。
- この TODO 更新コミット後の作業ツリーは clean の想定。

## 2. 直近で完了した作業

- MWP-0 A/B/C 論点は実装・テスト・コミット済み。
  - A：if/then 制約補完（`80943687` / `b978abd4`）
  - B：commit-preflight の kind 分離（`c8ead8fb`）
  - C：`next_action.reason` と最上位 `reasons` の責務差明確化（`e3e5b55a` / `0da4f15a`）
- workflow-management implementation の review-wave / alignment / approval は完了済み。
- approval 段の human-only 境界記述を修正済み（`72e2d720`）。
- sandbox / 非TTY 環境の guarded commit issue を完了済み（`102e9611`）。
- post-write target 判定を workflow specs 除外へ整合済み（`eef7cd7a`）。
- 旧試行の未追跡 post-write review-run と manifest は削除済み。
- TODO とセッション記録の現状反映をコミット・push 済み（`94582f51`）。
- maintenance workflow protocol plan は MWP-0 から MWP-3 まで完了し、plan / index とも completed へ更新済み（`b13d97ee`）。
- entrypoint coverage 系 TODO 群は完了済み。
  - entrypoint inventory / registry schema / coverage audit / freshness bridge / mechanized action link audit は完了済み。
- trigger operation entry TODO は完了済み。
  - `operation-trigger-resolve` により、`コミット` / `プッシュ` / `次へ` などの短い操作語から read-only に operation entry を解決できる。
  - 最新 push 済みコミットは `3ec542be Add operation trigger resolver`。

## 3. 残っている未コミット変更

この TODO 更新コミット後はなし。

## 4. 次にやること

`.reviewcompass/backlog/plans/` の `status: candidate` から、次に着手する推奨順は以下。

1. `.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`
   - 操作レジストリと preflight 契約を作る。
   - 直近の `operation-trigger-resolve` の次に自然な土台作業。
2. `.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`
   - 副作用のある操作の実行仕様を固める。
   - commit / push / next の安全導線を他操作へ広げる土台。
3. `.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml`
   - commit の停止点と承認 UX をさらに機械化する。
   - 現在の commit wrapper / approval 導線改善に直結する。
4. `.reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml`
   - 利用者起点の backlog / checklist 導線に effective prompt を付ける。
   - 「次へ」から TODO / checklist へ迷わず進むための補助。
5. `.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml`
   - effective prompt が古くなっていないか監査する。
   - 導線追加後の品質維持に効く。
6. `.reviewcompass/backlog/plans/plan-2026-06-23-normal-output-minimization-rollout.yaml`
   - CLI 出力を必要最小限に揃える。
   - 日々の `次へ` / `コミット` 運用を見やすくする。
7. `.reviewcompass/backlog/plans/plan-2026-06-23-working-note-self-check-hardening.yaml`
   - notes / TODO 系の軽量自己検査を強化する。
   - 重い post-write review を避けたい箇所の精度改善。
8. `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-review-prompt-isolation.yaml`
   - post-write review の criteria と target artifact を分離する。
   - レビュー品質と再現性を改善する。
9. `.reviewcompass/backlog/plans/plan-2026-06-23-api-review-run-hardening.yaml`
   - API review-run の prompt と後処理を堅くする。
   - 外部レビュー経路を安定化する。
10. `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-convergence-policy.yaml`
    - post-write verification が収束しない場合の方針を見直す。
    - repair 例外や policy violation と関係が深い。
11. `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-decision-mechanization.yaml`
    - proxy decision 実行と triage 適用を機械化する。
12. `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-assignment-tuning.yaml`
    - proxy assignment の model 選択や trigger signal を調整する。
13. `.reviewcompass/backlog/plans/plan-2026-06-23-triage-explanation-guard-quality.yaml`
    - triage 説明、重要度、guard 診断を改善する。
14. `.reviewcompass/backlog/plans/plan-2026-06-23-review-wave-recheck-pointer-hardening.yaml`
    - review-wave summary、recheck clearing、review-run pointer を堅くする。
15. `.reviewcompass/backlog/plans/plan-2026-06-23-session-record-operation-hardening.yaml`
    - session record の draft / formalize 操作を強化する。
16. `.reviewcompass/backlog/plans/plan-2026-06-23-autonomous-ledger-auditability.yaml`
    - 自律・並列実行の ledger 監査性を高める。
17. `.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml`
    - blocker 対応用の nested issue stack を追加する。
18. `.reviewcompass/backlog/plans/plan-2026-06-22-blocking-unit-control-improvements.yaml`
    - blocking unit 制御の残り改善。広めなので単独で切る。
19. `.reviewcompass/backlog/plans/plan-2026-06-23-deployment-tool-consolidation.yaml`
    - deploy-facing tool と runtime utility を統合する。
20. `.reviewcompass/backlog/plans/plan-2026-06-23-agent-adapter-revision.yaml`
    - 複数実行環境向けに agent adapter を見直す。
21. `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml`
    - 残りの operations / discipline 文書分類と移動。過去作業の整理寄り。
22. `.reviewcompass/backlog/plans/plan-2026-06-23-reconstruction-cleanup-followups.yaml`
    - reconstruction 後の cleanup / deferred backlog を追跡する。
23. `.reviewcompass/backlog/plans/plan-2026-06-23-feature-quality-followups.yaml`
    - feature-local な品質 follow-up を記録・追跡する。
24. `.reviewcompass/backlog/plans/plan-2026-06-23-false-positive-reversal-metrics.yaml`
    - false-positive reversal の指標を記録する。分析寄り。
25. `.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml`
    - Workflow Navigator WebUI。schema / 操作導線がさらに固まってから着手する。
26. `.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml`
    - entrypoint coverage audit。周辺 TODO は進んでいるため、残差確認・plan close 候補。

最優先は `plan-2026-06-23-operation-registry-preflight.yaml`。着手時は plan を TODO にし、その後 checklist にして実行する方針を継続する。

## 5. 参照

- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- ワークフロー操作ガイド：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`
- 入口 coverage audit 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-entrypoint-coverage-audit.yaml`
- operation registry / preflight 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`
- action execution spec 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`
- commit stop-point / approval UX 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml`
- user-initiated backlog/checklist effective prompt 計画：`.reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml`
- effective prompt freshness audit 計画：`.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml`
- kind 再設計メモ：`docs/notes/2026-06-26-next-json-kind-redesign.md`
- A 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run/`
- B 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run/`
- C 観点レビュー記録：`.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
