# ワークフロー状態のシンプル化（議論記録）

最終更新：2026-06-25。

## 出発点

MWP-0（`plan-2026-06-23-maintenance-workflow-protocol.yaml`）が提案した5軸分類
（`current_state` / `work_class` / `control_relation` / `permitted_scope` / `work_context`）
は分析ツールとして整理されているが、作業者の認知負荷が高い。シンプルにする必要がある。

## 議論の結論

### 状態の整理

機械が返す状態は4種類に整理できる。

| 状態 | 意味 |
|------|------|
| `completed` | 全て完了。次の作業を始められる |
| `in_progress` | 通常の作業中 |
| `in_progress`（blocking） | 本線をブロック中、または脇道の作業中。完了後は親または次判定へ戻る |
| `verification_pending` | 書き込み後の検証（post-write verification）待ち |

### maintenance と side-track の扱い

- `maintenance`（保守作業）と `side-track`（脇道）は**作業の内容・立ち位置の説明**であり、状態の種類ではない
- 「本筋だとしても、他の作業がなければ side-track に入って戻る。その間、他の作業がないのだから本質的には同じ」
- → `maintenance` と `side-track` を別々に状態として管理する必要はない

### `maintenance_in_progress` と `blocking_unit_in_progress` の統合根拠

現在の実装では：

- `blocking_unit_in_progress`：作業スタック（`work_unit_stack`）で管理。親の `unit_id` が明示され、機械が戻り先を把握する
- `maintenance_in_progress`：`stages/in-progress/maintenance-*.yaml` ファイルで管理。戻り先（`mainline_blocked_by`）を人間がファイルに書く

この差は「戻り先を機械が持つか人間が書くか」だが、次の理由で統合できる：

1. `completed` 状態から始まった maintenance には戻るべき親作業が存在しない → `mainline_blocked_by` を書く意味がない
2. 戻り先がある場合（進行中の親作業をブロックしている場合）は `blocking_unit_in_progress` と同じ構造

→ **`maintenance_in_progress` は `blocking_unit_in_progress`（blocking 付きの `in_progress`）に統合できる**

## 現状の実装との差分

現在の `next --json` は `kind` の値が30種類以上ある
（`maintenance_in_progress`、`blocking_unit_in_progress`、`reopen_in_progress`……）。

この議論は実装変更の提案ではなく概念整理の記録である。実装を変える場合は別途作業として扱う。

## 関連

- [plan-2026-06-23-maintenance-workflow-protocol.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml)（MWP-0〜MWP-3）
- [2026-06-25-work-mode-taxonomy-related-work-index.md](2026-06-25-work-mode-taxonomy-related-work-index.md)（関連作業索引）
