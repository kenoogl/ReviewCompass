# runtime/prompts/

3 役のプロンプト雛形を段目的ディレクトリ配下に役単位で配置する（design.md §配置決定 3）。すべてリポジトリ相対パスで解決でき、外部状態に依存しない（要件 4 受入 4）。

## 配置されるファイル（3 役プロンプト雛形、T-006）

- `primary_detection/primary_reviewer.prompt.md`：Step A 主役検出
- `adversarial_review/adversarial_reviewer.prompt.md`：Step B 敵対レビュー
- `judgment/judgment_reviewer.prompt.md`：Step C 判定

Step D（`integration`、統合）は追加の大規模言語モデル呼び出しを持たないため、プロンプト成果物は置かない。

本機能ではプロンプトの正本配置と識別規則のみ定義し、本文は最小限の雛形とする（本文整備はフェーズ 4 対象、計画書 §5.23.12.3）。

## 関連

- 設計：[.reviewcompass/specs/foundation/design.md](../../.reviewcompass/specs/foundation/design.md) §6 プロンプト成果物モデル
