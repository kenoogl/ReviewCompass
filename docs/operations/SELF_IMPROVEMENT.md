# SELF_IMPROVEMENT：自己改善機能の運用文書（workflow 改善版）

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子）

本文書は ReviewCompass の `self-improvement`（自己改善機能、第 1 期は workflow 層改善のみ）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/self-improvement/requirements.md](../../.reviewcompass/specs/self-improvement/requirements.md) を参照する。

## 1. 役割

`self-improvement` は ReviewCompass の改善機能だが、第 1 期では **workflow 層改善のみ**を担う（計画書 §7、§5.16）。先行プロジェクトの自己改善仕様（8 要件、主に runtime 層改善向け）は workflow 改善の性格に合わないため、計画書 §5.16 で全面書き直し済み。

workflow 改善は次を中核責務とする：

- **規律と実体の双方向同期**：規律と実体の乖離を観察し、規律を実体に追従させるか、実体を規律に追従させるかを判断
- **規律の正本所有**：規律ファイル（`docs/disciplines/discipline_*.md`）の作成・更新・退避・統廃合
- **5 種類の改善提案**：新規規律起案／既存規律更新／ステータス変更／archive 退避／規律間統廃合
- **3 つの検証方法**：過去遡及シミュレーション／パイロット運用／影響範囲事前分析
- **効果測定 7 指標**：規律遵守率／昇格件数／退避件数 ＋ 提案件数／採用率／ロールバック率／提案から採用までの平均日数

## 2. 設計の根本姿勢

- **第 1 期は workflow 層のみ**：他 4 層改善（prompt／policy／schema／runtime）はフェーズ 4 完了後の別計画書
- **規律と実体の双方向同期**：単に規律を増やすのではなく、実体観察と規律改定を両方向で扱う
- **縮減義務との連動**：新規規律追加と既存規律削減のセット（§5.8 第 5 層の処理表面積抑制方針）
- **replay/backtest 非採用**：workflow 改善には 3 つの代替検証手段（遡及シミュレーション／パイロット運用／影響範囲分析）
- **フェーズ境目の利用者監査**：session 内の連続承認を強制せず、フェーズ境目でまとめて判断

## 3. 8 つの要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 役割と性格 | workflow 層改善のみ、規律と実体の双方向同期 |
| Requirement 2 | 入力 | 5 種類の入力源、来歴 3 要素 |
| Requirement 3 | 提案単位 | 5 種類の提案種別、組み合わせ許容 |
| Requirement 4 | 提案の構造 | YAML 形式、必須フィールド、4 状態 |
| Requirement 5 | 検証 | 3 つの代替手段（replay/backtest 非採用） |
| Requirement 6 | 承認 | フェーズ境目の利用者監査、4 状態明示 |
| Requirement 7 | 履歴とロールバック | learning/workflow/ 4 サブディレクトリ、ロールバック方法 |
| Requirement 8 | 効果測定 | 7 指標（§5.9.5 の 3 ＋ workflow 運用 4） |

各要件の受入基準の詳細は [.reviewcompass/specs/self-improvement/requirements.md](../../.reviewcompass/specs/self-improvement/requirements.md) を参照。

## 4. データの流れ（Requirement 1 受入 3）

```
[入力]
- レビュー記録の規律違反検出結果（foundation Req 6 由来）
- 規律遵守検査の結果（各規律の evidence_check_method）
- フェーズ境目の利用者監査での指摘
- 実体運用で観察された運用パターン
- 規律違反の累積データ（discipline-compliance-reports）
   ↓
[workflow 改善] signal 抽出 → 提案構築 → 検証 → 利用者承認 → 採用または却下 → ロールバック
   ↓
[出力]
- learning/workflow/ 配下の改善履歴
- docs/disciplines/ の規律更新
```

## 5. 5 種類の提案種別（Requirement 3）

- **`new_discipline`**：新規規律の起案（例：本セッションで発見したモデル多様化を `discipline_model_diversification.md` として新設）
- **`update`**：既存規律の更新（例：所見の必須要素を「箇所/現状/問題/修正後」→「severity/target_location/description/rationale」に修正）
- **`status_change`**：規律のステータス変更（enforced ↔ aspirational の切り替え）
- **`archive`**：規律の archive 退避、撤廃（例：23 パターンの archive 退避）
- **`consolidation`**：規律間の統廃合（新規規律追加と既存規律削減のセット、§5.8 第 5 層の縮減義務）

## 6. 3 つの検証方法（Requirement 5）

replay／backtest は runtime 改善向けで workflow 改善では使わない。代替の 3 つの検証手段：

- **過去データへの遡及シミュレーション**：過去レビュー記録に新規律を当てて違反検出率を計算（例：モデル多様化規律を過去 17 件に当てると遵守率 100%）
- **パイロット運用**：新規律を `status: aspirational` で一定期間運用、遵守率を観察してから `enforced` 昇格
- **影響範囲の事前分析**：既存規律との衝突、撤廃予定規律との関係を機械検査

## 7. 効果測定 7 指標（Requirement 8）

§5.9.5 由来の 3 指標：

- 規律遵守率
- 昇格件数（aspirational → enforced）
- 退避件数（規律 → archive）

workflow 改善運用の 4 指標：

- 提案件数（種別ごと）
- 採用率（採用 / 提案合計）
- ロールバック率（ロールバック / 採用）
- 提案から採用までの平均日数

`phase-review-metric-register.md` の workflow 改善カテゴリとして登録。

## 8. 他機能との関係

- **`foundation`**：規律検査スキーマ、レビューモード語彙、状態軸語彙を参照（依存）
- **`runtime`**：規律遵守検査の結果（レビュー記録の機械検査出力）を入力源とする
- **`evaluation`**：規律違反データの集計と評価結果を入力源とする
- **`analysis`**：効果測定 7 指標を本機能から受け取る
- **`workflow-management`**：規律の昇格・退避・統廃合を所定手続き（drafting → review → approval）に従って実行
- **`conformance-evaluation`**：規律遵守検査の上流文書との適合性評価結果を入力源として活用可能

## 9. 旧実装モジュールとの関係（§5.16.11 由来）

旧 dual-reviewer-rebuild の 8 モジュールのうち、workflow 改善向けに使えるのは半分（後者 4 件）：

- **継承可能（4 件）**：`decision_adoption_model`（規律状態管理）／`rollback_model`（git 連携）／`pipeline_driver`（パイプライン制御）／`learning_layout`（成果物配置）
- **新規実装（4 件）**：`input_model`（規律違反検出と実体パターン抽出）／`proposal_model`（5 種類の提案種別）／`replay_backtest_model` 相当（3 つの代替検証手段）／`signal_extraction`（規律遵守検査結果を入力）

## 10. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加：

- design.md 抽出に基づく設計の説明（計画書 §5.16 全体）
- 各受入基準の機械検査方針
- 旧モジュール継承部分の具体的な再利用設計
- フェーズ 4 第 1〜3 サイクルでの段階的実装計画（§5.16.12）

## 11. 関連文書

- 形式仕様：[.reviewcompass/specs/self-improvement/requirements.md](../../.reviewcompass/specs/self-improvement/requirements.md)
- 計画書 §5.16：[self-improvement の workflow 改善仕様](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.9.5：効果測定 3 指標
- 計画書 §5.20.2 self-improvement 行：[抽出対応表](../extraction-mapping.md)
- 機能横断波及所見：[.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)、[evaluation](EVALUATION.md)、[analysis](ANALYSIS.md)、[workflow-management](WORKFLOW_MANAGEMENT.md)
