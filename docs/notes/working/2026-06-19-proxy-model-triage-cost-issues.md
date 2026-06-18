# proxy_model トリアージ運用のコスト問題メモ

作成日: 2026-06-19

## 対象

workflow-management requirements triad-review run における proxy_model 判定手順で発生した運用上の問題点を記録する。

対象 run:

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/`

このメモは後日の改善検討用である。triage 判定や workflow state は変更しない。

## 観測された問題

### 1. 最初に不適切なツール経路を使った

最初の proxy_model 実行で `tools/api_providers/run_role.py` を使った。

このツールは role-based review 実行には適しているが、今回の用途には適していなかった。今回の proxy_model の役割は、プロンプト自体を review することではなく、すでにクラスタ化された finding の採否ラベルを判断することだった。

観測された影響:

- モデル出力が、C1-C9 の採否判断ではなく、プロンプトや review task への finding のような形になった。
- その出力は採用しなかった。
- 誤った parsed 出力は削除した。
- proxy_model 呼び出しは `tools/experiments/_experiment_n_model.py` で直接やり直した。

影響:

- 余分なモデル/API コストが発生した。
- 余分な operator 時間が発生した。
- 無効な出力を正式な decision record に混入させるリスクが増えた。

最終結果への影響:

- 最終 triage 結果への混入は確認されていない。
- 最終的な proxy 判断は、直接実行した `_experiment_n_model.py` の出力から採用した。

### 2. apply-fixes readiness guard を早く確認しすぎた

proxy triage decision を記録した後、`review_triage.py assert-apply-fixes-ready --approval-record proxy-approval.yaml` を試した。

この時点で生成されていた approval record は `review_triage_decide` 用であり、fix 適用用ではなかった。そのため、この guard が失敗するのは自然だった。

影響:

- 外部モデルコストは発生していない。
- approval scope と一致しない確認に operator 時間を使った。
- 明示的に説明しないと、proxy_model triage decision 自体に問題があったように誤読される可能性があった。

最終結果への影響:

- triage decision への影響は確認されていない。
- proxy approval は triage decision 記録用として有効である。
- fix 適用時に workflow guard が要求する場合は、別途 apply-fixes 用の承認経路が必要になる可能性がある。

### 3. クラスタ判定を個別 finding へ手動展開する必要があった

proxy_model は C1-C9 のクラスタを判定したが、workflow record は finding ID 単位で decision を保持する。

実際に必要だった作業:

- クラスタ単位のラベルを `proxy-decisions/C1-C9.decisions-input.yaml` に変換する。
- すべての元 finding ID を final label に対応付ける。
- finding ごとに `review_triage.py decide` を実行する。

影響:

- 手作業の負荷が高い。
- 転記ミスの可能性が上がる。
- command history と review artifact が冗長になる。

最終結果への影響:

- 現時点で mapping error は確認されていない。
- 繰り返し使う前に自動化を強める価値がある。

## 改善案

### A. proxy_model の canonical command path を定義する

finding 採否判断の proxy_model では、標準手順を以下に固定する。

1. クラスタ summary を作る。
2. proxy decision prompt を作る。
3. `tools/experiments/_experiment_n_model.py` を直接実行する。
4. raw model output を `proxy-decisions/` 以下に保存する。
5. raw output から `decisions-input.yaml` を作る。
6. `tools/make-proxy-approval.py` を実行する。
7. `review_triage.py decide` で decision を適用する。

この用途では、専用の proxy-decision mode が追加されるまでは `tools/api_providers/run_role.py` を使わない。

### B. proxy-decision 補助ツールを追加する

以下を入力として受け取る helper を追加する。

- cluster summary
- proxy raw output
- cluster-to-finding mapping

出力:

- `decisions-input.yaml`
- 必要であれば `review_triage.py decide` の command list
- すべての finding ID が重複なく 1 回だけ covered されていることの validation

これにより、クラスタ単位の proxy 判断を finding 単位へ展開する手作業を減らせる。

### C. approval scope の確認を operator guidance に追加する

guard 実行前に、approval scope を明示的に確認できるようにする。

- `review_triage_decide` approval は triage decision の記録用である。
- apply-fixes approval は source / requirements artifact の変更用である。

これにより、`assert-apply-fixes-ready` の早すぎる実行が proxy decision failure のように見えることを避けられる。

### D. first-class proxy_model mode を検討する

専用 command または mode として、次を一括で扱えるようにする。

- input: review run directory と cluster summary
- output: proxy raw response、decisions input、approval record、適用済み triage decisions
- constraints: 必要に応じて operator 以外の provider を使う、raw output を保存する、prompt-review 形の誤出力を拒否する

これにより、proxy_model 運用が operator の記憶に依存しにくくなる。

## 未決事項

- `run_role.py` は、専用 mode なしに proxy-decision prompt を受け取った場合、拒否すべきか。
- `make-proxy-approval.py` は、cluster-level decision を直接受け取り、finding ID へ展開できるようにすべきか。
- `review_triage.py decide` は、`decisions-input.yaml` から batch application できるべきか。
- `assert-apply-fixes-ready` は、approval record の action が triage decision 用である場合、より明確なメッセージを出すべきか。

## 現時点の推奨

次に proxy_model を使う前に、canonical command path を関連する workflow または discipline document に記載する。

繰り返し利用する場合は、クラスタ単位の proxy 判断を finding 単位の decision に変換し、coverage validation まで行う helper を優先して整備する。
