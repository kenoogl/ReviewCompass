# レビュー結果：Claim D

## D-1（blocked_by.type の不統一）
- **所見**：問題あり
- **重大度**：must-fix

`required_action=commit_stop_point` を返すパスが2つあり、`blocked_by.type` が異なる：
- 通常ワークフロー経由：`"workflow_phase_end"`
- reopen 経由：`"commit_stop_point"`

設計書 line 355, 506 はいずれも `blocked_by.type="commit_stop_point"` を要求しており、reopen 限定の記述ではない。`"workflow_phase_end"` は設計違反。スキーマへの `blocked_by.type` 制約追加は正しい方向だが、先に実装を統一する必要がある。

## D-2（②③の phase/stage と active_gate の一致）
- **所見**：問題なし（技術的制約として許容）
- **重大度**：leave-as-is

JSON Schema Draft 2020-12 の標準機能では「フィールド A の値がフィールド B の値を正規表現で分解した部分と等しい」という参照制約を表現できない（`$data` ポインターは非標準拡張）。省略は技術的制約による合理的判断。ランタイム検証関数として実装内に持たせることが代替案。

## D-3（スキーマ①と build_commit_stop_point_next_action の矛盾）
- **所見**：問題あり
- **重大度**：must-fix

設計書・スキーマ・テストが `required_action=commit_stop_point` のとき `phase=null, stage=null` を要求しているが、実装は `phase=<フェーズ名>, stage="approval"` を返す。設計書 line 353 は「通常ワークフローの commit stop point は active workflow unit を持たない」と明記しており、通常ワークフロー経由も null を要求している。**実装が設計書を見落とした**ことによる実装誤り。

テストは「スキーマがこの制約を持つか」を確認するデータ（reopen 経由想定）を投入しており、通常ワークフロー経由の実際の出力は検証していない。この乖離も問題。

## 横断的観察

D-1 と D-3 は同一根本原因（`build_commit_stop_point_next_action` が設計書を見落とした）から来ており、修正は 1 箇所に集中する。

## 提案

`build_commit_stop_point_next_action` を修正：

```python
return {
  "kind": "in_progress",
  "required_action": "commit_stop_point",
  "feature": None,
  "phase": None,           # null に変更
  "stage": None,           # null に変更
  "active_gate": None,
  "reason": ...,
  "blocked_by": {
    "type": "commit_stop_point",      # "workflow_phase_end" から変更
    "kind": "phase_approval_complete",
    "phase": phase,                   # 情報は blocked_by 内に保持
    "stage": "approval",
    "dirty_paths": dirty_paths,
  },
}
```

加えて、通常ワークフロー経由の実際の出力をスキーマ検証するテストを追加する。
