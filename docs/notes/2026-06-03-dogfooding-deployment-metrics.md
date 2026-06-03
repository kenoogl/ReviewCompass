# Dogfooding deployment metrics note

日付：2026-06-03

## 判断

dogfooding 由来の論文用メトリクスは、現時点では実装しない。

現在の実装段では、既存の運用記録を残しておけば足りる。一通りの実装ができた後、
ReviewCompass のデプロイ時データ取得として、論文用の dogfooding メトリクスを扱う。

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
