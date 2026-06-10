# runtime/config/

設定成果物の 2 層モデル（要件 2 受入 6）に対応するファイルを置く（design.md §配置決定 4）。

## 配置されるファイル（設定 2 層モデル、T-007）

- `reviewcompass.yaml`：ツール本体の既定値を保持する正本（2 層モデル下層）
- `config.yaml.template`：アプリ側 `<対象アプリ>/.reviewcompass/config.yaml` を生成する雛形（2 層モデル上層の入力）
- `terminology.yaml.template`：用語集の最小契約雛形

## 2 層モデルのマージ規則

アプリ側で明示された項目がツール既定より優先、明示されていない項目はツール既定を使う。

## 関連

- 設計：[.reviewcompass/specs/foundation/design.md](../../.reviewcompass/specs/foundation/design.md) §10 設定と雛形のモデル
- 運用解説：[docs/operations/FOUNDATION.md](../../docs/operations/FOUNDATION.md) §4 設定成果物の二層モデル
