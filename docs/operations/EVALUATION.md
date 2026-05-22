# EVALUATION：評価機能の運用文書

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子。design 部分は後続セッションで追加）

本文書は ReviewCompass の `evaluation`（評価機能）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md) を参照する。本文書は読み手向けの解説、仕様文書は機械検査と仕様駆動手続きの正本という関係。

## 1. 役割

`evaluation` は `runtime` が出力したレビュー実行証拠を受け取り、有効・無効に切り分け、比較可能なメトリクスと派生成果物に変換する機能である。`runtime` を動かす責務は持たず、出てきた結果を扱う側にある。

具体的には：

- **有効・無効の機械分離**：メタデータと無効化マーカーに基づき、実行を有効／無効／明示的探索に分類
- **処理方式の比較契約**：`primary`／`adversarial`／`judgment` の 3 処理方式を横断比較
- **メトリクス抽出**：構造化された証拠から再現可能な計算でメトリクスを得る
- **除外と注意点の報告**：何が除外され、その理由を明示。データ品質の問題を隠さない
- **派生成果物の生成**：`self-improvement` と `analysis` が再利用可能な機械可読出力
- **評価準備メタデータの検査**：必須メタデータが欠ければ評価を速やかに失敗
- **フェーズ対応の評価**：`intent`／`requirements`／`design`／`tasks` 別のスライスとメトリクス
- **レビューモードの区別**：手動 dogfooding ／サブエージェント経由／実行時経由を 3 集団として扱う
- **外部証拠束の取り込みと許容判定**：他環境のレビュー実行を中央側で取り込む

## 2. 設計の根本姿勢

- **`foundation` 契約と `runtime` 出力の遵守**：本機能は新たな契約を作らず、既存契約に従って評価を実施
- **黙示的な集計禁止**：無効実行と有効実行、レビューモードの異なる証拠を黙示的に 1 つの集計に潰さない
- **再現可能性**：派生メトリクスから生の証拠への導出経路を保持。後から再計算可能
- **速やかな失敗**：必須メタデータ欠落、規約版／プロンプト版の混在等は標準集計を遮断
- **データ品質の透明性**：除外や注意点を明示し、後続の `analysis` や論文化が品質問題を隠せないようにする

## 3. 10 の要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 有効・無効実行の分離 | 4 分類（valid／invalid／exploratory／analysis_blocked）と、レビューモードとの直交独立性 |
| Requirement 2 | 処理方式の比較契約 | 3 処理方式（primary／adversarial／judgment）の比較、規約版・プロンプト版同一性 |
| Requirement 3 | メトリクス抽出 | 構造化証拠からの計算、導出経路の保持、3 階層（実行／所見／処理方式） |
| Requirement 4 | 除外と注意点の報告 | 除外件数と理由、データ品質と実行時品質の区別 |
| Requirement 5 | 派生成果物の生成 | 構造化出力、実行識別子への連結、無効化された実行に基づく成果物の陳腐化対応 |
| Requirement 6 | 評価準備メタデータの完全性 | 必須メタデータ検査、欠落時の集計拒否、診断情報出力 |
| Requirement 7 | フェーズ対応の評価 | 4 フェーズ（intent／requirements／design／tasks）のスライス対応 |
| Requirement 8 | フェーズ特異な有効性メトリクス | 共有の中核 ＋ フェーズ特異な重ね合わせ |
| Requirement 9 | レビューモードの区別 | 3 経路（manual_dogfooding／subagent_mediated／runtime_mediated）の独立集団扱い |
| Requirement 10 | 外部証拠束の取り込みと許容判定 | 中央側取り込み契約、来歴情報検証、許容状態の管理 |

各要件の受入基準の詳細は [.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md) を参照。

## 4. 直交独立な 2 軸の分類（Requirement 1 受入 6、Requirement 9）

評価では実行を 2 つの独立軸で分類する：

- **実行有効性軸（4 値）**：`valid`／`invalid`／`exploratory`／`analysis_blocked`（計画書 §5.17.3 の正本に従う。`analysis_blocked` は必要入力の不足、または実行未終了、または検証が前提不足で結論不能な場合の状態）
- **レビューモード軸（3 値）**：`manual_dogfooding`／`subagent_mediated`／`runtime_mediated`

両軸は直交独立。たとえば「内容上有効な手動 dogfooding 実行」は実行有効性軸では `valid`、レビューモード軸では `manual_dogfooding`。両軸で別々に分類される。

## 5. 標準比較集団規則（Requirement 9 受入 6）

3 つのレビューモードは独立集団として扱う：

- **`runtime_mediated`**：標準比較セットの中核
- **`manual_dogfooding`**：別集団。標準セットから除外、明示的に別スライスとして含める場合のみ加える
- **`subagent_mediated`**：別集団。同様に独立した第三集団として扱う（計画書 §5.23.12.6 のフェーズ 4 段階移行と整合）

ReviewCompass では先行プロジェクトと異なり、手動 dogfooding は「Phase 1 限定」ではなく恒久運用（§5.23 由来）。

## 6. 取り込み許容の 3 状態（Requirement 10）

外部からの可搬な証拠束を取り込む際、許容状態を 3 つに分類：

- **却下（reject）**：来歴情報不足、規約版不整合などで標準分析に含めない
- **探索的への格下げ（exploratory）**：許容するが標準集計から除外
- **許容（admit）**：標準集計に含める

派生成果物にはどの許容状態の証拠を含むかを必ず明示する。

## 7. 他機能との関係

- **`foundation`**：本機能はスキーマとメタデータ契約に依存（依存：hard）。`review_mode` 語彙、`evidence_class` 語彙、`validator_status` 語彙は `foundation` の正本を参照
- **`runtime`**：本機能は `runtime` の構造化実行証拠を受け取る（一方向の依存）
- **`self-improvement`**：本機能は再利用可能な分析入力を `self-improvement` に渡す
- **`analysis`**：本機能は読み物向け原データを `analysis` に渡す。`analysis` の特定の表現責務（運用ダッシュボード／週次／監査／論文）は本機能では持たない
- **`workflow-management`**：所定手続きの実行結果の評価要求を受ける
- **`conformance-evaluation`**：本機能の評価結果と検証器メタデータは `conformance-evaluation` の入力にもなる

## 8. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加する：

- design.md 抽出に基づく設計の説明（計画書 §5.17 全体）
- 5 段パイプライン構造の継承（§5.17.2）
- 4 状態区分の継承（§5.17.3）
- 3 階層・2 層の指標構造（§5.17.4）
- 比較適格性ノートのスキーマ所有者（§5.17.11）
- 探索的区分のフィールド整合（§5.17.12）

## 9. 関連文書

- 形式仕様：[.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md)
- 計画書 §5.17：[evaluation 機能の継承方針](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 evaluation 行：[抽出対応表](../extraction-mapping.md)
- 機能横断波及所見：[.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)
