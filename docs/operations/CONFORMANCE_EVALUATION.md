# CONFORMANCE_EVALUATION：適合性評価機能の運用文書

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子。design 部分は後続セッションで追加）

本文書は ReviewCompass の `conformance-evaluation`（適合性評価機能、新規 7 番目機能）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/conformance-evaluation/requirements.md](../../.reviewcompass/specs/conformance-evaluation/requirements.md) を参照する。

## 1. 役割

`conformance-evaluation` は **下流（実装コード）から上流文書（intent／requirements／design／tasks）を推定または照合する逆方向の機能**である。先行プロジェクトの `v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を、ReviewCompass の独立機能として第 1 期から含めることを計画書 §5.10 で確定した。

主な性格：

- **方向**：下流 → 上流（逆方向）
- **前提**：上流文書がなくてもよい（既存コードベースへの導入を想定）
- **主要用途 1：文書生成（オンボーディング）**：既存コードから上流文書を推定生成し、ReviewCompass を既存プロジェクトに導入
- **主要用途 2：照合チェック**：既存上流文書と推定上流文書を比較し、実装中の意図ずれ・文書連携不足を検出
- **実装適合レビューとは分離**：実装適合レビュー（順方向、フェーズ終端）は `runtime` と §5.9 に残し、本機能は吸収しない

## 2. 設計の根本姿勢

- **下流から上流の推定**：実装コードを最新の真実とみなし、上流文書を推定または更新する
- **既存導入の許容**：上流文書がない既存プロジェクトに ReviewCompass を導入する経路を提供
- **3 役レビュー機構の流用**：§5.9 の規律全般を本機能でも適用
- **実装適合レビューとの混同回避**：方向・前提・実施時期が異なるため、明確に分離

## 3. 8 つの要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 機能の方向性と前提 | 下流 → 上流、上流文書なくてもよい、2 モード |
| Requirement 2 | 文書生成モード（オンボーディング） | 既存コードから上流文書を推定生成、推定根拠保持 |
| Requirement 3 | 照合チェックモード | 既存上流文書と推定上流文書の比較、食い違い列挙 |
| Requirement 4 | 6 criteria の検査構造 | 2 上流フェーズ × 3 criteria（requirements／design 各 3、intent は参考情報、feature-partitioning と tasks は対象外、2026-05-24 セッション 23 改訂） |
| Requirement 5 | 3 役レビュー機構の流用 | 主役 → 敵対役 → 判定役、§5.9 規律全般を適用 |
| Requirement 6 | 評価記録の type 値と配置 | `conformance_evaluation` type、`conformance/` ディレクトリ |
| Requirement 7 | 依存関係の連想配列構造 | `hard`／`review` の依存種別、phase_order の最後 |
| Requirement 8 | 実装適合レビューとの分離 | 方向・前提・実施時期の違い、責務分担 |

各要件の受入基準の詳細は [.reviewcompass/specs/conformance-evaluation/requirements.md](../../.reviewcompass/specs/conformance-evaluation/requirements.md) を参照。

## 4. 6 criteria の検査構造（Requirement 4、2026-05-24 セッション 23 改訂）

2 上流フェーズ × 3 criteria の総計 **6 件**：

- **requirements conformance（3 criteria）**：
  - 受け入れ基準と実装の対応
  - API・データ契約と実装の対応
  - 例外系・境界条件と実装の対応
- **design conformance（3 criteria）**：
  - モジュール構成・データモデルと実装の対応
  - 接合面（API シグネチャ・エラーモデル）と実装の対応
  - アルゴリズム・性能達成手段と実装の対応

照合対象から除外する階層（2026-05-24 セッション 23 改訂、案 Y）：

- **feature-partitioning**：照合チェックモード（本筋）では既存を所与の入力として尊重、独立の照合対象外
- **intent**：構造的側面からの推定が困難、参考情報として推察（独立の照合対象外）
- **tasks**：タスク分解過程は実装コードから推定困難、対象外

実装適合（5 番目の評価軸）は §5.9 の実装適合レビューに残し、本機能では扱わない。

## 5. 2 モードの使い分け

### 文書生成モード（オンボーディング、Requirement 2）

- 既存プロジェクトに ReviewCompass を導入する初回利用
- 実装コードから intent／requirements／design／tasks の各文書を推定生成
- 出力は推定版として明示（既存上流文書がある場合は上書きしない）
- 推定の根拠（実装コードのどの部分から推定したか）を実行記録に保持
- 推定はあくまで初版、人間が修正する前提

### 照合チェックモード（Requirement 3）

- 既存上流文書を持つプロジェクトでの定期的または随時の検査
- 既存上流文書と実装コードから推定した上流文書を比較
- 食い違いを 4 段重大度（CRITICAL／ERROR／WARN／INFO）で列挙
- 3 役レビュー機構（主役 → 敵対役 → 判定役）で妥当性検証
- 判定役の判定値（must-fix／should-fix／leave-as-is）を保持

## 6. 評価記録の配置（Requirement 6）

```
<対象アプリ>/.reviewcompass/specs/<feature>/
├── intent.md           （仕様文書）
├── requirements.md
├── design.md
├── tasks.md
├── spec.json
├── reviews/            （仕様駆動レビューの記録）
│   └── <日付>-<種別>.md
└── conformance/        （本機能の評価記録、reviews/ とは別）
    ├── <日付>-generation.md   （文書生成モード）
    └── <日付>-check.md         （照合チェックモード）
```

評価記録の `type` 値は `conformance_evaluation` に統合し、`mode_internal` フィールドで `generation` と `check` を区別する。

## 7. 依存関係の特殊構造（Requirement 7）

本機能は他機能と異なり、`stages/feature-dependency.yaml` で依存種別を区別する連想配列構造を持つ（計画書 §5.10.5 由来、A-005 連動）：

```yaml
conformance-evaluation:
  depends_on:
    foundation: hard       # 必須依存
    runtime: review        # 読む依存
    evaluation: review     # 読む依存
    workflow-management: review  # 読む依存
```

phase_order の最後に位置付ける。

## 8. 実装適合レビューとの分離（Requirement 8）

本機能と実装適合レビューの違い：

| 観点 | 本機能（conformance-evaluation） | 実装適合レビュー（§5.9） |
|---|---|---|
| 方向 | 下流 → 上流（逆方向） | 順方向（intent → ... → implementation） |
| 前提 | 上流文書なくてもよい | 上流文書必須 |
| 実施時期 | 任意（オンボーディング／随時） | フェーズ終端 |
| 担当機能 | 本機能 | `runtime` と §5.9 |
| 評価記録 | `conformance/` ディレクトリ | `reviews/` ディレクトリ |

## 9. v3-plan §3.3 の取り扱い（§5.10.6 由来）

「実装で得た知見の文書への戻し」の責務分担：

- **文書レベルの戻し（intent／requirements／design／tasks）**：本機能の主機能（Requirement 2／3）
- **規律レベルの戻し**：`self-improvement` の workflow 改善（§5.16）
- **schema／prompt／code レベルの戻し**：`self-improvement` の他 4 層改善、フェーズ 4 完了後の宿題

## 10. 他機能との関係

- **`foundation`**：スキーマ・メタデータ契約・各種語彙正本を参照（依存：hard）
- **`runtime`**：実装コードのレビュー実行記録を入力源として活用（依存：review）
- **`evaluation`**：評価結果との突き合わせ（依存：review）
- **`workflow-management`**：所定手続きの実行履歴と上流文書の整合確認（依存：review）
- **`analysis`**：本機能の 6 criteria の検査結果を受け取り、4 出力先に取り込む（`analysis` Requirement 8 受入 5 由来）
- **`self-improvement`**：規律レベル戻しを受け取り、規律改善の入力とする

## 11. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加：

- design.md 抽出に基づく設計の説明（計画書 §5.10 全体 ＋ v3-plan.md からの追加抽出）
- 6 criteria の検査仕様（`schemas/review-criteria/conformance_evaluation.yaml`、フェーズ 2 で配置）
- 文書生成モードと照合チェックモードのコマンド設計（フェーズ 3 スタブ）
- フェーズ 4 第 3 サイクルでの実装計画（§5.10.7）

## 12. 関連文書

- 形式仕様：[.reviewcompass/specs/conformance-evaluation/requirements.md](../../.reviewcompass/specs/conformance-evaluation/requirements.md)
- 計画書 §5.10：[conformance-evaluation 機能の組み込み](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.9：レビュー方法（流用元）
- 計画書 §5.20.2 conformance-evaluation 行：[抽出対応表](../extraction-mapping.md)
- 元計画：素材リポジトリ `.kiro/methodology/dual-reviewer-spec-driven-paper/v3-plan.md`
- 機能横断波及所見：正本 [reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)、[evaluation](EVALUATION.md)、[analysis](ANALYSIS.md)、[workflow-management](WORKFLOW_MANAGEMENT.md)、[self-improvement](SELF_IMPROVEMENT.md)
