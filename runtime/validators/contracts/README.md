# runtime/validators/contracts/

検証器実装のコードとは分けて、検証成果物の形状だけを `foundation` が固定する（design.md §配置決定 5）。生証拠は不変、検証結果と無効化標識は別成果物とする方針を符号化する。

## 配置されるファイル（検証器側契約スキーマ、T-005）

- `validator_result.schema.json`：検証器結果の形状
- `invalidation_marker.schema.json`：無効化標識の形状

## 関連

- 設計：[.reviewcompass/specs/foundation/design.md](../../.reviewcompass/specs/foundation/design.md) §8 検証と無効化のモデル
