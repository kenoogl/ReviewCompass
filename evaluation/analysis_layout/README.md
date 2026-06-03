# evaluation analysis layout

このディレクトリは `evaluation` が生成する分析成果物配置の仕様文書を置く。
実体生成物は `experiments/analysis/` 配下に作られ、生実行証拠である
`experiments/runs/<run_id>/` とは分離する。

`layout_spec.yaml` は次を宣言する。

- 分析成果物ルート：`experiments/analysis`
- 必須サブディレクトリ 8 件：`imports`、`manifests`、`classifications`、`metrics`、`comparisons`、`caveats`、`modes`、`roles`
- `analysis_run_manifest.yaml` の必須項目
- 主要な成果物ファミリ

配置仕様は T-001 の正本であり、後続タスクの取り込み器、分類器、
メトリクス抽出器、比較器、報告器はこの配置を前提に出力を分担する。
