# runtime/schemas/

生証拠スキーマの単一配置（design.md §配置決定 2）。`runtime` と `evaluation` がパス解決で迷わないよう、共通スキーマをここに集約する。

## 配置されるファイル（5 つの共通スキーマ、T-004）

- `review_case.schema.json`：レビュー事例（Step D 統合レビュー記録の正本兼用）
- `finding.schema.json`：所見
- `impact_score.schema.json`：影響度評価
- `failure_observation.schema.json`：失敗観察
- `necessity_judgment.schema.json`：必要性判定

## 関連

- 設計：[.reviewcompass/specs/foundation/design.md](../../.reviewcompass/specs/foundation/design.md) §4 共有スキーマの関係
