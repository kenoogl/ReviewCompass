# learning/workflow/schemas

`self-improvement` と completed 後の workflow learning で使う永続データ正本スキーマを置く場所。

proposal、rollback、metrics など、他機能も参照する保存データのスキーマをここに分離し、データ YAML と混在させない。

## Schemas

- `proposal.schema.json`: discipline 改善 proposal の保存形式。
- `rollback.schema.json`: proposal rollback 記録。
- `metrics.schema.json`: workflow metrics 集計値。
- `carry-forward-register.schema.json`: unresolved / deferred item の持ち越し台帳。
- `normalized-finding.schema.json`: Markdown review と API review-run findings を横断分析するための正規化 schema。
- `tdd-cycle.schema.json`: review finding が failing test へ変換され、implementation で green になったことを記録する event schema。
- `side-track-state.schema.json`: post-write verification、sandbox trial、maintenance などの例外作業を通常 workflow へ復帰可能な状態として表す schema。
- `dogfooding-event-ledger.schema.json`: ReviewCompass 自身の運用から得た review、triage、guard、post-write、TDD、side track event を分析用データへ正規化する ledger schema。
- `model-assignment-cost.schema.json`: review-run の role assignment、elapsed time、retry count、token usage、API cost、finding contribution を同じ粒度で記録する schema。
- `replication-pilot.schema.json`: repository 横断の deployment smoke、data acquisition run、analysis import 結果を記録する schema。fixture / external git の由来、remote URL、確認済み HEAD は `repository_origin` に記録する。
