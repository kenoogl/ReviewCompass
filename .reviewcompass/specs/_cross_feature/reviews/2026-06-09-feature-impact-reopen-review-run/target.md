---
review_target: feature-impact-reopen-decision
date: 2026-06-09
phase: feature-partitioning_reopen_review
status: draft_for_triad_review
---

# Feature Impact Reopen Review Target

## 背景

`intent/INTENT.md` に、次の意図が追加された。

- レビュー収集処理は、規則ファイル照合や固定プロンプトの単純写像ではなく、実際の大規模言語モデルの判断に基づいて発見と判断を生成する。
- プロンプトや規則ファイルなどの事前設定は、収集対象や入力範囲の固定には使ってよいが、観測結果の件数・内容・構造を縛ってはならない。

この intent 変更に対して、既存 feature に受け皿があるか、受け皿がある場合どの既存 feature を reopen 対象にするか、新 feature が必要かを判定する必要がある。

## 現在の機械判定

`tools/check-workflow-action.py next --json` は、次を返している。

- `kind`: `reopen_classification_required`
- `upstream_phase`: `feature-partitioning`
- `feature`: `foundation`
- `phase`: `requirements`
- `stage`: `drafting`
- `reopen_trigger`: `N-0`
- `required_action`: `classify_reopen_and_run_reopen_start`

これは、`stages/feature-partitioning/2026-05-24-proposal.md` が更新され、完了済み requirements より新しいためである。

## 現在の仮判断

既存記録では、新 feature は作成せず、既存 7 feature すべてを reopen 対象とする仮判断になっている。

| Feature | 仮判断 | 理由 |
| --- | --- | --- |
| foundation | reopen existing feature | 固定パターン依存の除外、実行メタデータ、証拠スキーマ、検証成果物分離の共有契約が関係する |
| runtime | reopen existing feature | 実 LLM 呼び出し、プロンプト版追跡、構造化証拠、パターン定義非依存の実行境界が関係する |
| evaluation | reopen existing feature | 収集結果の有効・無効分類、構造化証拠からのメトリクス導出、レビューモード母集団分離が関係する |
| analysis | reopen existing feature | 評価・適合性確認の出力を証拠台帳と主張対応図へ構造化し、実行判断を上書きしない派生層が関係する |
| workflow-management | reopen existing feature | 上流変更を下流工程へ再展開し、不可逆操作前に機械判定する workflow が関係する |
| self-improvement | reopen existing feature | 観測事実と証跡を入力モデルとして保持し、改善提案・履歴・ロールバックへ接続する責務が関係する |
| conformance-evaluation | reopen existing feature | 実装コードからの推定、既存上流文書との比較、契約所有候補と仕様更新草案が関係する |

新 feature 判断:

- `new_feature_decision`: `no_new_feature`
- 理由: 追加 intent は既存 7 feature の責務境界で受けられるため。

## レビューで判定してほしいこと

次の観点で、現在の仮判断が妥当かをレビューする。

1. 既存 7 feature すべてを reopen 対象にする判断は過剰ではないか。
2. 直接 reopen が必要な feature、間接確認のみでよい feature、影響なしでよい featureを分けるべきではないか。
3. 新 feature が必要になる可能性はないか。
4. `feature-partitioning` 変更に対する reopen trigger 候補 `N-0` は妥当か。
5. 3役レビュー後に、人間承認待ちにすべき未確定点はあるか。

## 出力期待

所見がある場合は、feature ごと、または判断ルールごとに、次のどれかを指摘する。

- `must_fix`: このまま reopen-start に進む前に修正が必要。
- `should_fix`: 記録や根拠を補強した方がよい。
- `leave_as_is`: 現在の仮判断でよい。

特に重要なのは、「既存 feature に受け皿がある」から「該当 feature を reopen 対象にする」までの判断が、全フェーズ共通の workflow として妥当かどうかである。
