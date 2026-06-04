# Dogfooding deployment metrics note

日付：2026-06-03

## 判断

dogfooding 由来の論文用メトリクスは、デプロイ時の本格データ取得として扱う。

現在の実装段では、既存の運用記録を残しておけば足りる。ただし、後で記録から抽出可能かを確認するため、
2026-06-04 時点で最小抽出器 `evaluation/metrics/dogfooding_metrics_extractor.py` を追加した。
これは本格分析ではなく、記録が論文用データへ正規化できるかを確認する入口である。

## 想定データ源

候補となる記録は次のとおり。

- `docs/reviews/reopen-classification-*.md` の reopen 分類記録
- `stages/completed/reopen-procedure-*.yaml` の完了済み reopen 手続き記録
- `docs/logs/workflow-precheck.log` の workflow precheck ログ
- `.reviewcompass/post-write-verification/` の post-write verification manifest
- `docs/notes/review-runs/` の raw / parsed / summary / triage 成果物

## 後続判断

デプロイ時に、これらの記録を論文用データ抽出のための専用 dogfooding event ledger に
正規化するか判断する。候補指標は、上流 reopen 件数、手戻り深さ、失敗または遮断された
workflow check、post-write 所見、triage 結果、修正追跡性など。

## 最小抽出スキーマ

`DogfoodingMetricsExtractor` は、現時点で次を 1 つの dict に正規化する。

- `review_run`: model 数、raw response 数、finding 数、human_required 件数、三段階 triage 件数、重要 cluster 数、decision actor
- `workflow_precheck`: precheck 実行数、verdict 別件数、subcommand 別件数、遮断件数、警告件数、commit 承認失敗件数、in-progress 遮断件数
- `implementation`: 統合結果 status、実行テストコマンド数、decision
- `derivation`: 参照した source artifact と source field

この最小スキーマは、手戻り、失敗、上流遡及、承認待ち、再実行などを扱う専用 event ledger の前段である。
