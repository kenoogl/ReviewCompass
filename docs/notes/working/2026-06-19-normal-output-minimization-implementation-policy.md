# 正常系出力最小化の実装方針メモ

作成日: 2026-06-19

## 背景

`tools/check-workflow-action.py` の正常系出力は局所的に最小化した。一方、利用者から「全 CLI / 全ツールへ広げるなら、別途『正常系出力最小化』の共通規律と各ツールの棚卸し」と指示があり、共通規律と棚卸しを追加した。

その後、「これは個別対応しないといけないのか？」という確認があった。本メモは、その回答として合意した対応方針を後で検討できるよう記録する。

## 結論

全 CLI / 全 tool を完全に個別対応だけで進めるべきではない。

推奨は二段構えである。

1. 共通 formatter / 出力ヘルパーを作る。
2. 既存 CLI は優先度順に薄く接続する。

## 方針 1: 共通 formatter / 出力ヘルパー

`OK` / `WARN` / `DEVIATION` / `--json` / `--verbose` の出し分けを共通化する。

各 CLI は、人間向け文章を直接組み立てるのではなく、次のような判定データを返す。

- `verdict`
- `action`
- `summary`
- `reasons`
- `current_state`
- `artifacts`
- `next_action`

表示は共通 formatter に寄せる。

この形にすると、新規 tool は最初から同じ出力規律に乗せられる。既存 tool の改修も、「結果データを formatter に渡す」薄い接続に寄せられる。

## 方針 2: 既存 CLI は優先度順に接続

既存 CLI を一括変換すると、出力契約の破壊やデバッグ情報の欠落が起きやすい。

そのため、`docs/notes/working/2026-06-19-normal-output-minimization-tool-inventory.yaml` の `priority: high` から順に接続する。

優先対象:

- `tools/api_providers/run_review.py`
- `tools/api_providers/run_role.py`
- `tools/api_providers/prepare_post_write_review.py`
- `tools/api_providers/review_triage.py`
- `tools/commit-from-current-staged.py`
- `tools/guarded-git-commit.py`
- `tools/experiments/_experiment_n_model.py`

`tools/experiments/*_temp.py` のような一時 script 群は、正規 workflow に出てくるものだけ個別 entry に昇格してから対応する。

## テスト方針

各 CLI の接続時は、次を最低限テストする。

- 正常系 human output が短いこと。
- 異常系 human output に停止理由と次 action が残ること。
- `--json` が詳細情報を保持すること。
- `--verbose` がある tool では、詳細出力が必要時だけ出ること。

## 未決事項

- 共通 formatter をどの module に置くか。
- 既存の `tools/check-workflow-action.py` 内 formatter を切り出すか、新規 helper として作るか。
- `verdict` の語彙を全 tool で `OK` / `WARN` / `DEVIATION` に統一するか、tool 固有の成功・失敗語彙を許すか。
- stdout / stderr の使い分けをどこまで統一するか。

## 次の推奨

次に実装するなら、まず共通 formatter の最小 API を作り、`tools/commit-from-current-staged.py` または `tools/api_providers/run_review.py` のどちらか 1 つへ接続する。

commit 系は利用者体験に直結し、API review 系は出力量が大きいため、どちらも効果が高い。
