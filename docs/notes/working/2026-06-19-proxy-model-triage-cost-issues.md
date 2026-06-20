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

## 2026-06-20 補足: C1 fix policy 実地運用後の判断

workflow-management design triad-review の C1 対応で、proxy_model を次の用途に使った。

- C1 が `must-fix / blocking / design_level` とされた後、メイン LLM が修正方針を独自確定しないための判断代行
- C1 fix policy prompt の作成
- prompt quality review
- proxy_model による修正方針判断
- 修正後のメイン LLM 再点検

結果として、判断品質には効果があった。proxy_model は「局所修正で足りるが、Requirement 12 / Requirement 13 / XDI の権限境界を揃える必要がある」と判断し、その後の再点検では軽量版 precheck 節に残っていた「語彙と出力契約の正本は運用文書とスクリプト実装」という古い表現を発見できた。

一方で、運用は重すぎた。C1 1 件だけで、prompt 作成、prompt quality review、外部 API 承認レコード、proxy 実行、parser 汎用化、再点検レポートまで広がった。これは C1 のような source-of-truth / workflow authority 境界では価値があったが、通常の所見処理に一般化すると過剰である。

### 補正後の運用方針

proxy_model は標準処理ルートではなく、メイン LLM の判断が独断になりそうな場面の逃がし先として使う。

基本は次の軽量運用にする。

1. メイン LLM が所見と上流資料を読み、通常判断できるものは通常どおり処理する。
2. 判断が割れそう、利用者判断を代替しそう、修正範囲の広狭で迷う、上流接続が微妙なものだけ proxy_model に渡す。
3. proxy_model に渡す場合も、1 論点 1 prompt にする。
4. prompt quality review は原則実施しない。新型 prompt、高リスクで上流接続が複雑、または prompt 品質がすでに問題化した場合だけ実施する。
5. proxy_model の回答は raw / parsed / metadata を保存するが、メイン LLM が結果を軽く照合してから反映する。
6. commit、push、`spec.json` 更新、phase / gate 完了、reopen finalize などの不可逆操作は proxy_model では承認しない。

### proxy_model を使う条件

- メイン LLM が根拠を示しても判断に自信を持てない。
- 利用者判断を勝手に代替しそうである。
- レビュー所見同士が衝突している。
- 修正範囲を広げるか狭めるかで迷う。
- 上流要件・設計との接続が微妙で、誤ると後工程に響く。

### proxy_model を使わない条件

- 単純な文言修正。
- 既存方針に沿った明白な修正。
- 影響範囲が局所的。
- 以前の同型判断があり、今回も同じ基準で処理できる。
- メイン LLM が根拠を示して通常判断できる。

### 高リスク判断の扱い

高リスクという理由だけで、常に proxy_model / prompt quality review / 再点検レポートを実施しない。高リスク判断でも、まずメイン LLM が材料を整理し、通常判断できるかを確認する。

proxy_model に回すのは、リスクが高いだけでなく、判断が曖昧・衝突・独断化しやすい場合である。C1 級の source-of-truth 境界問題では proxy_model の利用価値があるが、C1 で使った重装備を標準化しない。

実務上の標準形は次とする。

```text
メイン判断
→ 迷う箇所だけ proxy_model
→ 必要なら反映
→ 最後に軽く照合
→ 不可逆操作のみ人間承認
```

今回の教訓は、proxy_model を使えばよいということではない。proxy_model は重要判断の独断防止装置であり、通常処理の本線ではない。

## 2026-06-20 補足: design v2 triad-review 後処理の実績

workflow-management design triad-review v2 の後処理では、利用者の明示指示により C1 の fix policy 判断だけ proxy_model を使った。その後の C2 以降は、メイン LLM が triage 所見、上流要求、設計本文、既存 post-fix recheck を読み、設計修正と post-fix recheck 作成を進めた。

結果として、triad-review 後処理の実務処理はメイン LLM に任せられる範囲が広いことが確認できた。具体的には、次はメイン LLM 主導で処理可能だった。

- 所見の読解
- 同根所見のクラスタリング
- 既存設計・上流要件との照合
- 明らかな欠落・矛盾の補修
- 設計本文への修正
- post-fix recheck artifact の作成
- 修正 coverage の棚卸し

一方で、メイン LLM に任せきらない停止点も明確に分ける必要がある。

- 所見の不採用判断
- 「過剰指摘なので対応不要」とする判断
- 複数案の優劣判断
- design gate 完了判断
- phase 移行、`spec.json` 更新、commit / push
- 修正後の統合的な第三者確認

運用上の結論は次のとおり。

```text
triad-review 後処理の実務処理はメイン LLM に任せる。
ただし、採否・完了・不可逆操作は別判断に分離する。
```

標準運用は、メイン LLM がまず所見処理と修正案作成を行い、判断が割れる箇所だけ proxy_model / 第三者 review / 人間判断へ上げる形にする。proxy_model は「常用する判定者」ではなく、メイン LLM の判断が独断化しやすい論点の逃がし先として使う。
