# learning/workflow/schemas

`self-improvement` と completed 後の workflow learning で使う永続データ正本スキーマを置く場所。

proposal、rollback、metrics など、他機能も参照する保存データのスキーマをここに分離し、データ YAML と混在させない。

## Schemas

- `proposal.schema.json`: discipline 改善 proposal の保存形式。
- `rollback.schema.json`: proposal rollback 記録。
- `metrics.schema.json`: workflow metrics 集計値。
- `carry-forward-register.schema.json`: unresolved / deferred item の持ち越し台帳。
- `normalized-finding.schema.json`: Markdown review と API review-run findings を横断分析するための正規化 schema。D-004 の責務境界と field comparison は `docs/notes/2026-06-09-d004-normalized-finding-schema-checklist.md` を参照する。
- `tdd-cycle.schema.json`: review finding が failing test へ変換され、implementation で green になったことを記録する event schema。D-025 の責務境界は `docs/notes/2026-06-09-d025-tdd-cycle-evidence-checklist.md` を参照する。
- `side-track-state.schema.json`: post-write verification、sandbox trial、maintenance などの例外作業を通常 workflow へ復帰可能な状態として表す schema。D-027 の責務境界は `docs/notes/2026-06-09-d027-side-track-state-model-checklist.md` を参照する。
- `dogfooding-event-ledger.schema.json`: dogfooding 由来の review、triage、guard、post-write、TDD、side track event を論文用データへ正規化する ledger schema。D-008 の責務境界は `docs/notes/2026-06-09-d008-dogfooding-event-ledger-checklist.md` を参照する。
- `model-assignment-cost.schema.json`: review-run の role assignment、elapsed time、retry count、token usage、API cost、finding contribution を同じ粒度で記録する schema。D-019 の責務境界は `docs/notes/2026-06-09-d019-time-cost-model-assignment-checklist.md` を参照する。
- `replication-pilot.schema.json`: D-020 cross-repository replication pilot の deployment smoke、data acquisition run、analysis import 結果を repository 横断で記録する schema。fixture / external git の由来、remote URL、確認済み HEAD は `repository_origin` に記録する。D-020 の責務境界は `docs/notes/2026-06-09-d020-cross-repository-replication-checklist.md` を参照する。
