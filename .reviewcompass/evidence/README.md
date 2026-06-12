# evidence/ 区画：証跡記録の置き場

日付付き・事後不変の証跡記録を集約する区画（PLC-DEC-004。設計は
`docs/notes/2026-06-12-document-placement-target-design.md` §2）。
既存の証跡は旧置き場で凍結保全し、**新規生成分からここへ置く**（PLC-DEC-009）。

## 内部構造

| 置き場 | 内容 | 旧置き場（凍結） |
| --- | --- | --- |
| `features/<feature>/reviews/` | feature のレビュー証跡・ポインタ記録 | `.reviewcompass/specs/<feature>/reviews/` |
| `features/<feature>/conformance/` | conformance 評価記録 | `.reviewcompass/specs/<feature>/conformance/` |
| `cross-feature/reviews/` | 機能横断段の記録 | `.reviewcompass/specs/_cross_feature/reviews/` |
| `review-runs/<run-id>/` | API review-run 一式（raw・parsed・triage 等） | `docs/notes/review-runs/`・`docs/experiments/review-runs/`・`.reviewcompass/post-write-review-runs/` |
| `estimation/<run-id>/` | conformance 推定の独立性証跡（prompt.log） | ルート `logs/estimation/` |
| `ledgers/autonomous-parallel/` | 自律並列の計画・実績台帳 | `docs/logs/autonomous-parallel/` |
| `sessions/` | セッション記録（対象アプリ。PLC-DEC-007） | （新設） |

## 命名規約

- 日付付き記録：`YYYY-MM-DD-<slug>.md`。改訂版は前付け `supersedes:` で旧版を指す
- run-id：`<日付>-<内容>-<段>`
- 非 ASCII ファイル名は使わない
