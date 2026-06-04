# learning/workflow/approved-updates

`self-improvement` の `status: approved` または `status: superseded` 提案 YAML を置く場所。

承認済み提案は workflow-management の手続き入力であり、`docs/disciplines/` の実体変更は workflow-management 側で実行する。

`pending` 提案を採用した場合、self-improvement は提案 YAML を `git mv` で `learning/workflow/proposals/` からこのディレクトリへ移す。`approved` は self-improvement による承認時点を表し、`materialized_at` と `materialization_commit_hash` は workflow-management が実体変更を完了した時点で追記する。
