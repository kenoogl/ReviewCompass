# ANALYSIS：分析機能の運用文書

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子。design 部分は後続セッションで追加）

本文書は ReviewCompass の `analysis`（分析機能、旧 `paper-interface`）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/analysis/requirements.md](../../.reviewcompass/specs/analysis/requirements.md) を参照する。

## 1. 役割

`analysis` は `runtime` と `evaluation` の出力を、分析向け成果物に変換する機能である。先行プロジェクトでは「論文向け（paper-interface）」と狭く呼ばれていたが、ReviewCompass では 4 種の出力先（運用ダッシュボード／週次レポート／監査用報告／論文向け原データ）に拡張し、機能名を `analysis` に改称した（計画書 §5.14、§5.15.6）。

具体的には：

- **主張から証拠への写像**：分析向けの言明（claim）から具体的な証拠源へ追跡可能にする
- **分析向けデータ契約**：図表や要約のための安定した入力契約
- **注意点と限界の追跡**：報告で方法論的制約を消さない
- **`runtime` と `evaluation` ロジックからの分離**：報告の都合が下層を歪めない
- **予備証拠と成熟証拠の区別**：報告精度を守る
- **レビューモード由来情報の保持**：3 経路の証拠を区別して報告
- **レビュー収束過程の可視化（新規）**：3 役・3 経路の所見差分を時系列で見せる
- **4 種の出力先への変換**：運用ダッシュボード／週次／監査／論文の各形態へ

## 2. 設計の根本姿勢

- **下層を消費するが支配しない**：本機能は `runtime` 規則や `evaluation` メトリクス定義を変更できない
- **`evaluation` 経由の参照**：生の実行ログへの直接アクセスを禁じ、`evaluation` 出力を経由
- **報告の都合は再現性に従属**：書式上の都合のみでスキーマ変更を強制しない
- **混合の透明性**：成熟度・モデル経路の混合は注意点として可視化
- **`foundation` 語彙の遵守**：証拠区分・レビューモード等は `foundation` 正本を参照

## 3. 8 つの要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 主張から証拠への写像 | 識別子、来歴連結、版付き追跡可能性 |
| Requirement 2 | 分析向けデータ契約 | 図表入力フィールド、再生成支援、陳腐化対応 |
| Requirement 3 | 注意点と限界の追跡 | 注意点メタデータ、3 種の限界区別、黙示昇格の禁止 |
| Requirement 4 | `runtime`／`evaluation` からの分離 | 消費のみ・支配せず、無効化方針の上書き禁止 |
| Requirement 5 | 予備証拠と成熟証拠の区別 | 明示ラベル、混合可視化、統一語彙の使用 |
| Requirement 6 | レビューモード由来情報 | 3 経路の区別（`manual_dogfooding`／`subagent_mediated`／`runtime_mediated`） |
| Requirement 7 | レビュー収束過程の可視化（新規） | 3 役・3 経路の所見差分、時系列・役横断の構造化 |
| Requirement 8 | 4 種の出力先への変換 | 運用ダッシュボード／週次／監査／論文の各加工方針 |

各要件の受入基準の詳細は [.reviewcompass/specs/analysis/requirements.md](../../.reviewcompass/specs/analysis/requirements.md) を参照。

## 4. 4 種の出力先（Requirement 8）

- **運用ダッシュボード**：開発・運用の現状把握。リアルタイム性高、要約レベル中
- **週次レポート**：チームや個人利用者の振り返り。時系列推移と注目所見
- **監査用報告**：規律遵守状況、無効化マーカーの一覧、検証器失敗の追跡
- **論文向け原データ**：研究報告の構造化入力。主張から証拠への完全な追跡

各出力先で必要な情報粒度・要約レベルは異なるが、`evaluation` 経由の証拠への追跡可能性はすべて保持する。

## 5. レビュー収束過程の可視化（Requirement 7、新規）

ReviewCompass 新規追加機能。同一対象に対する 3 役（`primary`／`adversarial`／`judgment`）と 3 経路（`manual_dogfooding`／`subagent_mediated`／`runtime_mediated`）の所見出力が、最終結果に至るまでの過程を可視化する。これにより：

- レビューの内部動態が読み手に伝わる
- 役・経路の差異がメトリクスに反映される
- 3 方式比較データ（`findings_by_method`、計画書 §5.9.6）と組み合わせて新しい分析軸が得られる

## 6. 他機能との関係

- **`evaluation`**：比較準備済みデータを受け取る（依存）。直接 `evaluation` 規則は変更しない
- **`foundation`**：証拠フィールド命名、レビューモード語彙、証拠区分語彙に依存
- **`runtime`**：原則として `evaluation` 経由でアクセス、直接アクセスしない（Requirement 4 受入 1）
- **`self-improvement`**：改善提案と分析叙述を混同しない
- **`workflow-management`**：所定手続きの実行履歴に対する可視化要求を受ける
- **`conformance-evaluation`**：本機能の出力は `conformance-evaluation` の検査入力にもなりうるが、評価判定自体は `conformance-evaluation` の責務

## 7. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加する：

- design.md 抽出に基づく設計の説明（計画書 §5.14 全体）
- 5 つの料理パイプライン（§5.14.2）
- 10 メトリクスカテゴリへの対応（§5.14.3）
- 4 つの出力先の具体的な加工方針（§5.14.4）
- レビュー収束過程の可視化の詳細設計（§5.14.5）
- 主要な発見の構造化（§5.14.6）

## 8. 関連文書

- 形式仕様：[.reviewcompass/specs/analysis/requirements.md](../../.reviewcompass/specs/analysis/requirements.md)
- 計画書 §5.14：[analysis 機能の役割と料理方法](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 analysis 行：[抽出対応表](../extraction-mapping.md)
- 機能横断波及所見：[.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)、[evaluation](EVALUATION.md)
