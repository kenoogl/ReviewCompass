# runtime/prompts/

3 役のプロンプト雛形を段目的ディレクトリ配下に役単位で配置する。すべて配布物内の相対パスで解決でき、外部状態に依存しない。

## 配置されるファイル

- `primary_detection/primary_reviewer.prompt.md`：Step A 主役検出
- `adversarial_review/adversarial_reviewer.prompt.md`：Step B 敵対レビュー
- `judgment/judgment_reviewer.prompt.md`：Step C 判定

Step D（`integration`、統合）は追加の大規模言語モデル呼び出しを持たないため、プロンプト成果物は置かない。
