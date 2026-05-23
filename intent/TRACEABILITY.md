# TRACEABILITY

_作成: 2026-05-21（セッション 17、ReviewCompass 再構築計画書 §5 系と §5.20 抽出対応表に基づく）_
_status: draft v0.1（フェーズ 1 抽出作業の入り口、移管前の素材）_

---

## 1. この文書の役割

この文書は、`ReviewCompass` における上位意図と下位実装の対応関係を追跡するための文書である。

`INTENT.md`・`NON_GOALS.md`・`DESIGN_PRINCIPLES.md` が上位方針を定めても、それがどの運用文書やどの機能仕様に落ちているかが追えなければ、設計変更時に整合性が崩れる。本書は、意図から仕様、仕様から成果物、成果物から証跡までの橋渡しを担う。

本書の目的は次の 3 つである。

- 上位意図がどの文書・仕様・成果物に実装されるかを明示する
- 設計変更時に、どこを見直す必要があるかを特定できるようにする
- 実行・評価・横断分析の責務混線を防ぐ

## 2. 追跡可能性の単位

ReviewCompass では、追跡可能性を次の 5 層で扱う。

1. `intent`（意図）
2. `operations`（運用）
3. `specs`（仕様）
4. `artifacts`（成果物）
5. `evidence`（証跡）

意味：

- **意図**：なぜ作るか・何を避けるか・どんな原則で設計するか
- **運用**：配置・信頼・人間の流れ・無効化規則の運用境界
- **仕様**：機能レベルの要件／設計／タスク
- **成果物**：実行時ファイル・スキーマ・プロンプト雛形・検証スクリプト・分析スクリプト
- **証跡**：実行記録・指標・改善提案・横断分析の出力

補足：

- レビュー実行自体も意図 → 要件 → 設計 → タスクの順で下流へ流れる
- 各レビュー段の内部では機能横断のレビュー波を形成する
- 追跡可能性は成果物だけでなく、レビュー進行に対しても上流から下流への依存を持つ

## 3. 基本規則

- 各主要意図は、少なくとも 1 つ以上の運用文書または仕様に結びつく
- 各仕様は、どの意図を実装しているか説明できなければならない
- 各機能の要件は、どの意図命題を受けているか説明できなければならない
- 各実行に関わる成果物は、対応する仕様を説明できなければならない
- 各証跡成果物は、依拠する方式版・プロンプト版・実行時版を追えなければならない
- 横断分析向け成果物は実行規則の正本になってはならない
- 上流文書または既存仕様に遡上修正が入った場合は、対応段階の機能横断整合を再実施しなければならない
- 上位段階の修正は、完了済みの下流段階を差し戻し、再チェック対象に戻す
- 実装中に仕様差分や共有成果物の競合が見つかった場合は、流れ修復記録に記録し、必要なら上流段階を差し戻す

詳細な修復手続きは、再構築計画書 §5.6（修復手続きの機械強制）と運用文書 `REOPEN_PROCEDURE.md` を参照。

## 4. 意図 → 運用の対応

### 4.1 配置可能なツールを作る（INTENT.md §3.1）

対応先：
- `DEPLOYMENT_MODEL.md`：配置モデル
- `TRUST_BOUNDARY.md`：信頼境界
- `DATA_INVALIDATION_POLICY.md`：無効化規則
- `REPRODUCIBILITY_CONTRACT.md`：再現性契約
- `SYSTEM_BOUNDARY.md`：システム境界

説明：
- リポジトリ内成果物だけで配置するための前提は配置モデルに落ちる
- 何をツール成功とみなすかは信頼境界に落ちる
- 妥当・無効を分離する条件は無効化規則に落ちる

### 4.2 方式のずれを防ぐ（INTENT.md §3.3）

対応先：
- `DATA_INVALIDATION_POLICY.md`
- `REPRODUCIBILITY_CONTRACT.md`
- `EVIDENCE_PROTOCOL.md`：証跡規約
- `FOUNDATION.md`：基盤
- `EVALUATION.md`：評価

説明：
- ずれ防止はメタデータと無効化条件の両方で担保する
- 基盤が必須項目を定義し、評価がそれを使って除外する

### 4.3 実行・評価・横断分析の混線を防ぐ（INTENT.md §3.4）

対応先：
- `SYSTEM_BOUNDARY.md`
- `EVALUATION.md`：評価
- `ANALYSIS.md`：横断分析

説明：
- システム境界で責務境界を固定する
- 横断分析向け出力は analysis 機能に限定する

### 4.4 レビュー記録と内部挙動から継続改善する（INTENT.md §3.5）

対応先：
- `SELF_IMPROVEMENT.md`：自己改善（第 1 期は流れ層のみ）
- `FOUNDATION.md`：基盤
- `EVALUATION.md`：評価

説明：
- 基盤が記録の土台スキーマを定義する
- 評価が測定可能な形に整える
- 自己改善が提案の輪に変換する（第 1 期は規律と実体の双方向同期に特化）

### 4.5 人が全体像を理解できるようにする（INTENT.md §3.6）

対応先：
- `INTENT.md`
- `NON_GOALS.md`
- `DESIGN_PRINCIPLES.md`
- `SYSTEM_BOUNDARY.md`
- 本書自身
- 現在位置可視化機構（再構築計画書 §5.11）

説明：
- 人間理解可能性はツール機能だけではなく文書構造そのものの責務である
- 現在位置可視化機構（`reviewcompass status`／`reviewcompass map` コマンド）は実行時にも追跡を支える

### 4.6 収集処理が事前設定の写像にならない（INTENT.md §3.7）

対応先：
- `REVIEW_PROTOCOL.md`：レビュー方法（再構築計画書 §5.9）
- `RUNTIME.md`：実行時

説明：
- 規律・プロンプトの事前設定は収集対象・入力範囲の固定に使ってよいが、観測結果を縛らない
- 規律ファイルの形骸化（v1 取得処理汚染の経緯）は再構築計画書 §5.9.4 で確定済みの撤廃事項として扱う

## 5. 設計原則 → 仕様の対応

### 5.1 リポジトリ内成果物の徹底（DESIGN_PRINCIPLES.md §2）

主対応仕様：
- `dual-reviewer-foundation`
- `dual-reviewer-runtime`

反映先成果物：
- `schemas/foundation/`：4 段論理契約・メタデータ契約
- `schemas/domain/`：5 共有スキーマ
- `schemas/validators/`：2 検証スキーマ
- `templates/prompts/`：3 役プロンプト雛形
- `templates/config/`：設定雛形

### 5.2 方式の事前固定（DESIGN_PRINCIPLES.md §3）

主対応仕様：
- `dual-reviewer-foundation`
- `dual-reviewer-evaluation`

反映先成果物：
- `REPRODUCIBILITY_CONTRACT.md`
- `EVIDENCE_PROTOCOL.md`
- 実行メタデータスキーマ（20 必須項目、再構築計画書 §5.18.6）

### 5.3 生の証跡の不変性（DESIGN_PRINCIPLES.md §4）

主対応仕様：
- `dual-reviewer-evaluation`
- `dual-reviewer-self-improvement`

反映先成果物：
- 対象アプリ側 `.reviewcompass/specs/<feature>/`：実行記録
- 評価派生成果物：分析・古さ伝播
- 無効化標識：別成果物として重ねる
- 提案成果物：自己改善の輪

### 5.4 信頼境界の分離（DESIGN_PRINCIPLES.md §5）

主対応仕様：
- `dual-reviewer-runtime`
- `dual-reviewer-foundation`

反映先成果物：
- `TRUST_BOUNDARY.md`
- 検証スクリプト
- レビュー出力契約
- 補助層 A（人間代役機構、再構築計画書 §5.12）
- 補助層 B（人間への通知機構、再構築計画書 §5.13）

### 5.5 証跡駆動の変更（DESIGN_PRINCIPLES.md §6）

主対応仕様：
- `dual-reviewer-self-improvement`（第 1 期は流れ層のみ）
- `dual-reviewer-evaluation`

反映先成果物：
- `learning/workflow/proposals/`：提案
- `learning/workflow/approved-updates/`：採用
- `learning/workflow/rejected-updates/`：却下
- `learning/workflow/rollback/`：戻し
- 所見メタデータの evidence_type ラベル（再構築計画書 §5.9.3）

### 5.6 実行・評価・横断分析の分離（DESIGN_PRINCIPLES.md §11）

主対応仕様：
- `dual-reviewer-runtime`
- `dual-reviewer-evaluation`
- `dual-reviewer-analysis`（旧 paper-interface）

反映先成果物：
- 対象アプリ側 `.reviewcompass/specs/<feature>/`：実行
- 評価派生成果物
- 横断分析の 4 つの出力先：論文用・運用ダッシュボード・週次レポート・監査レポート

### 5.7 軽量化方針（DESIGN_PRINCIPLES.md §16、再構築計画書 §5.4）

主対応仕様：
- `dual-reviewer-workflow-management`（旧 implementation-governance）

反映先成果物：
- `stages/` 配下の段集合 YAML（9 ファイル構成、再構築計画書 §5.5）
- 検査スクリプト（証跡ファイルと必須節の存在検査のみ）

### 5.8 conformance-evaluation の組み込み（新規、再構築計画書 §5.10）

主対応仕様：
- `dual-reviewer-conformance-evaluation`

反映先成果物：
- `CONFORMANCE_EVALUATION.md`：正本
- `schemas/review-criteria/conformance_evaluation.yaml`：検査仕様
- 12 観点の構造：意図 3 ＋ 要件 3 ＋ 設計 3 ＋ タスク 3

## 6. 非目標 → 除外の対応

### 6.1 外部からの取り込みは初期対象外（NON_GOALS.md §3.1）

影響：
- `dual-reviewer-evaluation` に外部取り込み要件を入れない
- ただし「中央側集約モードの存廃」は再構築計画書 §5.19.1 のフェーズ 1 着手前必須判断（未決定）
- `dual-reviewer-self-improvement` はリポジトリ内証跡だけを初期入力とする

### 6.2 多事業者の協調学習は初期対象外（NON_GOALS.md §3.2）

影響：
- `dual-reviewer-foundation` は役の抽象名までに留める
- `dual-reviewer-runtime` に事業者連合の処理を入れない
- ただし事業者抽象層の設計余地は残す（再構築計画書 §5.9.1）

### 6.3 配布パッケージ／共有サービスは初期対象外（NON_GOALS.md §3.3／§3.4）

影響：
- 配置モデルは対象アプリのローカルから始める
- 実行時設計で配布の使い心地を優先しない
- ただしコマンドライン道具としての配置は採用（再構築計画書 §5.1）

### 6.4 論文化先行の最適化は対象外（NON_GOALS.md §3.5）

影響：
- `dual-reviewer-analysis`（旧 paper-interface）は利用者であり提供者ではない
- 論文都合の項目追加を基盤に逆流させない
- 論文化作業そのものは別の作業ライン（旧リポジトリの論文化計画）

### 6.5 self-improvement の他 4 層改善は対象外（NON_GOALS.md §3.8）

影響：
- `dual-reviewer-self-improvement` は第 1 期は流れ層のみ
- プロンプト・方針・スキーマ・実行時の改善はフェーズ 4 完了後の宿題

### 6.6 多層防御の第 2〜5 層の本格実装は対象外（NON_GOALS.md §3.9）

影響：
- 第 1 期は第 1 層（軽量版 YAML 検査）のみ
- 補助層 A・B は第 1 層と第 2 層の中間として基本実装
- 第 2〜5 層はフェーズ 4 完了後の宿題

## 7. 仕様 → 成果物の対応

### 7.1 dual-reviewer-foundation（基盤）

想定成果物：
- `schemas/foundation/layer1_framework.yaml`：4 段論理契約・3 役抽象名
- `schemas/foundation/metadata_contract.yaml`：20 必須メタデータ項目・4 状態軸
- `schemas/domain/*.schema.json`：5 共有スキーマ
- `schemas/validators/*.schema.json`：2 検証スキーマ
- `templates/prompts/*/`：3 役プロンプト雛形
- `templates/config/*.template`：設定雛形

詳細は再構築計画書 §5.18。

### 7.2 dual-reviewer-runtime（実行時）

想定成果物：
- 4 段実行（primary_detection／adversarial_review／judgment／integration）
- 3 つの実行方式（primary／adversarial／judgment）の制御
- 実行ごとの 8 グループのファイル群（メタデータ／横断正本／段別生記録／判断／失敗観測／内部正本／検証結果／補助）

詳細は再構築計画書 §5.15。

### 7.3 dual-reviewer-evaluation（評価）

想定成果物：
- 5 段パイプライン（受け取り → 区分け → 指標抽出 → 比較 → 報告）
- 4 状態区分（妥当／無効／探索的／分析不能）
- 3 階層 ＋ 2 層の指標
- バージョン管理 4 軸と古さ伝播

詳細は再構築計画書 §5.17。

### 7.4 dual-reviewer-analysis（横断分析、旧 paper-interface）

想定成果物：
- 5 つの料理パイプライン
- 10 メトリクスカテゴリ
- 4 つの出力先（論文用・運用ダッシュボード・週次レポート・監査レポート）
- 収束過程の可視化

詳細は再構築計画書 §5.14。

### 7.5 dual-reviewer-workflow-management（流れ管理、旧 implementation-governance）

想定成果物：
- `stages/` 配下の段集合 YAML 9 ファイル
- 検査スクリプト（軽量版）
- 修復手続きの機械強制（再構築計画書 §5.6）

詳細は再構築計画書 §5.4〜§5.8。

### 7.6 dual-reviewer-self-improvement（自己改善、第 1 期は流れ層のみ）

想定成果物：
- `learning/workflow/` 配下 4 ディレクトリ（proposals／approved-updates／rejected-updates／rollback）
- 規律ステータスメタデータ（enforced／aspirational／archived）
- 効果測定 7 指標（規律遵守率／昇格件数／退避件数 ＋ 提案件数／採用率／ロールバック率／提案から採用までの日数）

詳細は再構築計画書 §5.16。

### 7.7 dual-reviewer-conformance-evaluation（実装適合評価、新規）

想定成果物：
- 文書生成モード：実装から intent／requirements／design／tasks を推定生成
- 照合モード：既存上流文書との差分検出
- 12 観点の検査仕様
- 3 役レビュー機構を流用

詳細は再構築計画書 §5.10。

## 8. 成果物 → 証跡の対応

### 8.1 実行成果物が生成する証跡

- レビュー記録（front-matter ＋ 所見）
- 発見記録
- 判定記録
- メタデータ記録
- 段別生記録（primary.json／adversarial.json／judgment.json／integration.json）

### 8.2 評価成果物が生成する証跡

- 妥当性報告
- 指標まとめ（3 階層 ＋ 2 層）
- 除外報告
- 注意事項台帳

### 8.3 横断分析成果物が生成する証跡

- 論文用：claim_map.json／evidence_register.json／reporting_fragments.json／figure_source_bundle.json／table_source_bundle.json／paper_caveat_register.json
- 運用ダッシュボード：進捗マトリックス・時系列グラフ・収束カーブ
- 週次レポート：要約・変化のあった項目
- 監査レポート：規律違反件数・archive 退避履歴

### 8.4 自己改善成果物が生成する証跡（第 1 期は流れ層のみ）

- 提案成果物
- 採用記録
- 却下記録
- 戻し記録
- 規律遵守報告

### 8.5 conformance-evaluation 成果物が生成する証跡

- 推定された上流文書（意図／要件／設計／タスクの推定版）
- 既存文書との差分集計
- 12 観点の検査結果

## 9. 変更時の参照手順

### 9.1 意図が変わるとき

見直すもの：
- 運用文書全般
- 影響する機能仕様の要件
- `SYSTEM_BOUNDARY.md`
- 本書
- 影響段階に応じた機能横断整合文書

### 9.2 運用が変わるとき

見直すもの：
- 対応する仕様の要件と設計
- 検証スクリプト
- 実行メタデータ契約
- 無効化規則と評価の流れ
- 影響段階に応じた機能横断整合文書

### 9.3 仕様が変わるとき

見直すもの：
- 対応成果物
- 対応テスト
- 対応証跡契約
- 必要なら上位の意図と原則との整合
- 機能横断の場合は同段階の他機能仕様との整合関門の対象

補足：
- 要件を修正したら要件機能横断整合を再確認または更新する
- 設計を修正したら設計機能横断整合を再確認または更新する
- タスクを修正したらタスク機能横断整合を再確認または更新する
- 意図／運用の修正は、影響下にある完了済みの要件／設計／タスクを差し戻して再確認する

### 9.4 横断分析側の都合で変更したくなったとき

手順：
1. まず横断分析（analysis）だけで吸収できるか検討する
2. 無理なら評価（evaluation）の変更で足りるか検討する
3. 基盤（foundation）／実行時（runtime）を変える場合は意図と原則に照らして正当化できるか確認する

## 10. 現時点の追跡可能性上の優先確認点

現時点で特に追跡を強く意識すべきなのは次である。

- `foundation` 仕様と旧スキーマ・プロンプト雛形の対応（再構築計画書 §5.20.2 foundation 表）
- `runtime` 仕様と旧 `dr-*` スクリプト群の対応（再構築計画書 §5.20.2 runtime 表）
- `evaluation` 仕様と旧 dogfeeding スクリプトの対応（再構築計画書 §5.20.2 evaluation 表）
- `analysis` 仕様と旧 paper-interface 計画の対応（再構築計画書 §5.20.2 analysis 表）
- `workflow-management` 仕様と旧 implementation-governance の対応（再構築計画書 §5.20.2 workflow-management 表）
- `self-improvement` 仕様と旧 review logs ／ comparison artifacts の対応（再構築計画書 §5.20.2 self-improvement 表）
- `conformance-evaluation` 仕様と v3-plan.md の対応（再構築計画書 §5.20.2 conformance-evaluation 表）

詳細な抽出元 → 抽出先の対応表は、再構築計画書 §5.20（抽出対応表の雛形）を参照。

## 11. この文書の完成条件

本書は、少なくとも次を満たすときに有効とみなす。

- 上位意図から仕様への流れを保守者が説明できる
- 仕様変更時に、見直すべき下位成果物と上位文書を特定できる
- 実行・評価・横断分析の責務が本書上で混線していない

## 12. 関連参照

- 再構築計画書：`../../dual-reviewer-spec-driven-paper/reviewcompass-reconstruction-plan-2026-05-21.md`
- 関連意図文書：`INTENT.md`／`NON_GOALS.md`／`DESIGN_PRINCIPLES.md`
- 7 機能体制：再構築計画書 §3.1
- 抽出対応表：再構築計画書 §5.20
- 利用者判断事項（未決定）：再構築計画書 §5.19
- 機能依存マップ：再構築計画書 §5.5（一元化は §5.19.2 の宿題として記録）
