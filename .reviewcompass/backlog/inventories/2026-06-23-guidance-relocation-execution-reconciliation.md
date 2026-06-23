# Guidance Relocation Execution Reconciliation

作成日: 2026-06-23

対象計画: `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml`

## Scope

この表は `guidance-relocation-and-docs-classification` の plan / TODO / runtime checklist / completed stage の整合を確認するための棚卸しである。

この作業では文書移動、旧 path 削除、参照更新、テスト追加、backlog status 補正は行わない。実作業の前に、どの slice が完了済みで、どの slice が未実行かを一意に定める。

## Finding

この plan は「最初の slice だけが TODO 化され、残りが未展開だった」例ではない。GRC-1 から GRC-6 までの TODO と runtime checklist は展開済みである。

ただし、管理面には不整合がある。

- plan の `execution_slices` は GRC-1 だけを保持しており、GRC-2 以降の materialized TODO/checklist を反映していない。
- GRC-2 と GRC-3 は completed stage が存在するが、backlog TODO と runtime checklist は `candidate` / `pending` のままである。
- GRC-4 以降は TODO/checklist は存在するが、completed stage は確認できない。
- GRC-3 implementation は active consumer 参照を guidance 側へ寄せているが、GRC-4 の「文書移動」や GRC-5 の「旧 path 削除」を完了したものではない。

## Reconciliation Table

| Slice | Plan title | TODO | Runtime checklist | Completed stage evidence | Reconciled execution state | Required follow-up |
|---|---|---|---|---|---|---|
| GRC-1 | Inventory and classification only | `todo-2026-06-23-guidance-relocation-inventory` is `completed` | Evidence checklist exists under `.reviewcompass/evidence/work-units/checklists/` | `stages/completed/maintenance-2026-06-23-guidance-relocation-inventory.yaml` | Completed and reconciled | None for execution state |
| GRC-2 | Reference and consumer audit | `todo-2026-06-23-guidance-reference-consumer-audit` is still `candidate` | Runtime checklist exists but all items are `pending` | `stages/completed/maintenance-2026-06-23-guidance-reference-consumer-audit.yaml` | Completed in maintenance, but backlog/checklist state is stale | Reconcile TODO/checklist status or record explicit exception |
| GRC-3 | Red tests and audit tests | `todo-2026-06-23-guidance-relocation-red-tests` is still `candidate` | Runtime checklist exists but all items are `pending` | `stages/completed/maintenance-2026-06-23-guidance-relocation-red-tests.yaml`; `stages/completed/maintenance-2026-06-23-guidance-relocation-red-tests-implementation.yaml` | Red tests completed; implementation follow-up completed for active consumer references | Reconcile TODO/checklist status; do not treat as GRC-4/GRC-5 completion |
| GRC-4 | Move deploy-facing and runtime-facing docs | `todo-2026-06-23-guidance-relocation-move-docs` is `candidate` | Runtime checklist exists, all items `pending` | Not found | Not started | Execute only after GRC-2/GRC-3 state is reconciled |
| GRC-5 | Delete or demote old paths | `todo-2026-06-23-guidance-relocation-old-path-cleanup` is `candidate` | Runtime checklist exists, all items `pending` | Not found | Not started | Execute after GRC-4 move/split decisions |
| GRC-6 | Post-write review and final audit | `todo-2026-06-23-guidance-relocation-final-audit` is `candidate` | Runtime checklist exists, all items `pending` | Not found | Not started | Execute after relocation and cleanup changes |

## Source Evidence

| Evidence type | Path |
|---|---|
| Plan | `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml` |
| GRC-1 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-inventory.yaml` |
| GRC-2 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-reference-consumer-audit.yaml` |
| GRC-3 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-red-tests.yaml` |
| GRC-4 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-move-docs.yaml` |
| GRC-5 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-old-path-cleanup.yaml` |
| GRC-6 TODO | `.reviewcompass/backlog/todos/todo-2026-06-23-guidance-relocation-final-audit.yaml` |
| GRC-1 inventory | `.reviewcompass/backlog/inventories/2026-06-23-guidance-relocation-docs-classification.md` |
| GRC-2 audit | `.reviewcompass/backlog/inventories/2026-06-23-guidance-reference-consumer-audit.md` |
| GRC-1 completed stage | `stages/completed/maintenance-2026-06-23-guidance-relocation-inventory.yaml` |
| GRC-2 completed stage | `stages/completed/maintenance-2026-06-23-guidance-reference-consumer-audit.yaml` |
| GRC-3 red-test completed stage | `stages/completed/maintenance-2026-06-23-guidance-relocation-red-tests.yaml` |
| GRC-3 implementation completed stage | `stages/completed/maintenance-2026-06-23-guidance-relocation-red-tests-implementation.yaml` |

## Operational Conclusion

次に戻る地点は GRC-4 ではなく、まず GRC-2/GRC-3 の管理状態補正である。完了証跡と TODO/checklist 状態が食い違っているため、このまま `next` や checklist ベースで進むと、実行済み slice を未実行として再開する可能性がある。

GRC-2/GRC-3 の補正が完了した後、実作業上の次地点は GRC-4 `Move deploy-facing and runtime-facing docs` になる。
