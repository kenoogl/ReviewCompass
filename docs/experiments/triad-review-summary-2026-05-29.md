# 三役レビュー（triad-review）集計サマリ — tasks 段 全7機能

作成：2026-05-29（セッション40）。本文書は、各機能の tasks 段 triad-review 記録（`.reviewcompass/specs/<機能>/reviews/<日付>-tasks-triad-review.md`）の front-matter を集計したもの。**7 モデル比較実験（レビューの「裁定の質」）とは別レイヤー**で、三役レビューそのもの＝レビューの「**生成の質**」（発見力・敵対役の有効性・判定分布）を測る。算出スクリプト：`tools/experiments/_aggregate_triad_review_temp.py`。

三役配置：**主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7**（全機能共通、起草者＝メインセッションは3役に入らない＝規律 §0.3 を満たす）。

## 集計表

| 機能 | 主役所見 | 敵対役所見 | 主役 severity(C/E/W/I) | 判定 must/should/leave | 反証 raised/評価済 |
|---|---|---|---|---|---|
| foundation | 12 | 9 | 0/3/6/3 | 10/7/4 | —（FM欠） |
| runtime | 14 | 8 | 0/3/10/1 | 6/10/6 | 5/14 |
| evaluation | 16 | 7 | 0/4/9/3 | 8/11/4 | 3/16 |
| analysis | 16 | 12 | 0/6/10/0 | 13/12/3 | —（FM欠） |
| workflow-management | 20 | 10 | 1/6/13/0 | 9/17/4 | —（FM欠） |
| self-improvement | 16 | 22 | 2/7/6/1 | 5/8/8 | 4/16 |
| conformance-evaluation | 20 | 25 | 2/8/7/3 | 2/9/5 | 7/20 |
| **合計** | **114** | **93** | 5/37/61/11 | 53/74/34 | 19/66 |

（注：敵対役所見は「主役所見への反証付与」＋「独立発見」の合計。反証欄は front-matter に記載のある 4 機能のみ集計。foundation／analysis／workflow-management は本文に counter_status はあるが front-matter 集計欄なし）

## 主要な観察（レビュー生成の質）

1. **発見規模**：主役 114 件・敵対役 93 件、判定 161 件。tasks 段だけで 200 件超の所見を生成。
2. **重大度の偏り**：主役 severity は WARN 61・ERROR 37 が中心、CRITICAL 5・INFO 11 は少数。tasks 段の所見は「中程度の不備」が主体（致命ではないが直すべき）。
3. **判定分布**：must-fix 32%・should-fix 45%・**leave-as-is 21%**。約 2 割が「直さなくてよい」と判定された＝敵対役の反証や判定役の精査が**過剰指摘を削る**役に立っている。
4. **敵対役の有効性（反証率）**：記載 4 機能で 19/66＝**28%**。主役所見の約 3 割に敵対役が反証を立てた。敵対役は形式でなく実質的に機能している。
5. **敵対役の独立発見が後半で増加**：self-improvement（敵対役 22 > 主役 16）・conformance-evaluation（25 > 20）では、敵対役（Opus）が主役（Sonnet）より多く発見。後半機能ほど Opus 敵対役が生産的（あるいは仕様が複雑）。
6. **機能差**：workflow-management は主役 20・should-fix 17 と多く、設計判断を要する論点が多い（7 モデル実験の割れ率の高さ＝§6.14 と整合）。conformance-evaluation は must-fix 2 と少なく、leave-as-is 5＝比較的安定。

## 限界・注意

- **front-matter 集計の欠落**：反証分布（counter）は foundation／analysis／workflow-management の front-matter に欠落（本文の counter_status を手集計すれば補完可能、未実施）。
- **観点は仮設定**：tasks 段の評価観点 7 つは計画書未整備のため本セッション限りの仮設定（各記録の subagent_mediated_caveats 参照）。
- **効果（下流の手戻り低減）は未測定**：本集計は「発見した・裁いた」までで、所見が後続工程の不具合を実際に防いだかは測っていない。
- **これは記録の集計であり実験ではない**：7 モデル比較のような統制された比較ではない。三役の配置は全機能同一（主役 Sonnet／敵対役・判定役 Opus）で、モデル間比較はしていない。

## 7 モデル比較実験との関係

- 本サマリ＝レビューの**生成の質**（所見を見つけ・裁いたか）。
- 7 モデル比較実験（実験ノート `n-model-comparison.md`）＝レビューの**裁定の質**（出た所見の修正方針判定を 7 モデル＋人本人で比較）。
- 外部評価者向けインデックス：`evaluation-index-for-external-review.md` §5a（生成の質）／§2・§3（裁定の質）。
