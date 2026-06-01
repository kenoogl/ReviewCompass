# FOUNDATION：土台機能の運用文書

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子。design 部分は後続セッションで追加）

本文書は ReviewCompass の `foundation`（土台機能）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/foundation/requirements.md](../../.reviewcompass/specs/foundation/requirements.md) を参照する。本文書は読み手向けの解説、仕様文書は機械検査と仕様駆動手続きの正本という関係。

## 1. 役割

`foundation` は ReviewCompass の他の 6 機能（`runtime`／`evaluation`／`analysis`／`workflow-management`／`self-improvement`／`conformance-evaluation`）が共通して依存する土台契約を提供する。レビューを実際に実行する役は持たず、レビューの実行が成立するために必要な「約束事の集合」を定義する。

具体的には：

- **4 段論理契約**：レビューが「主役検出 → 敵対レビュー → 判定 → 統合」の 4 段で進むことを論理的に定める
- **3 役の抽象化**：レビュー役を抽象名（`primary_reviewer`／`adversarial_reviewer`／`judgment_reviewer`）でのみ参照させ、特定モデル名を埋め込ませない
- **共通スキーマ**：所見・判定・レビュー事例などの構造を 5 つの共通スキーマファイルで定義する
- **プロンプト配置規約**：3 役のプロンプト雛形をリポジトリ内のどこに置くかを定める
- **検証器用メタデータ契約**：レビュー記録の必須メタデータを定義し、有効実行と無効実行を機械的に分離可能にする
- **リポジトリ内資産の規則**：実行時挙動に必要な資産すべてをリポジトリ内に保つことを要求する

## 2. 設計の根本姿勢

- **論理契約のみ、実装は持たない**：4 段の実行順序や再試行制御は `runtime` 機能の責務。foundation は段の同一性と遷移ラベルだけを共有契約として持つ
- **抽象化の徹底**：役名・モデル名・パスをすべて抽象化し、特定ベンダーへの結合を避ける
- **リポジトリ内完結**：運用者の暗黙記憶や外部記憶ファイルに依存しない。すべてリポジトリ内のファイルが正本
- **再現性の確保**：レビューを後から再現するために必要なメタデータ（規約版、プロンプト版、実行時版、対象成果物ハッシュ等）を必須化する

## 3. 7 つの要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | レビュー状態機械 | 4 段論理契約、段の同一性と遷移ラベル、最小実行メタデータ |
| Requirement 2 | 役と設定の抽象化 | 役の抽象名、設定契約、設定の二層モデル（ツール既定 ＋ アプリ上書き） |
| Requirement 3 | 共通スキーマ集合 | 5 スキーマ（`review_case`／`finding`／`impact_score`／`failure_observation`／`necessity_judgment`）、版管理規約 |
| Requirement 4 | プロンプト正本配置 | プロンプト雛形のリポジトリ内配置と版追跡 |
| Requirement 5 | パターン定義依存の除外 | パターン定義ファイル配置規約は本仕様の責務外、レビュー検出は実 LLM 呼び出しによる動的判定 |
| Requirement 6 | 検証器用メタデータ | 必須フィールド一覧、無効化マーカー、レビューモード語彙、来歴項目、証拠区分語彙、検証器状態語彙 |
| Requirement 7 | リポジトリ内資産 | リポジトリ外記憶への定常依存禁止 |

各要件の受入基準の詳細は [.reviewcompass/specs/foundation/requirements.md](../../.reviewcompass/specs/foundation/requirements.md) を参照。

## 4. 設定成果物の二層モデル（Requirement 2 受入 6）

ReviewCompass では設定成果物を次の二層で扱う：

- **ツール本体側**：`runtime/config/reviewcompass.yaml` に既定値を保持
  - 既定モデル割り当て、API 既定接続情報、既定パス、通知既定、代役機構の既定方針など
- **アプリ側**：`<対象アプリ>/.reviewcompass/config.yaml`（`runtime/config/config.yaml.template` から実体化）
  - アプリ側で項目別に上書きしたい値だけを書く
- **マージ規則**：アプリ側で明示された項目がツール既定より優先、明示されていない項目はツール既定を使う

個人利用者が複数アプリ（自分の研究プロジェクト A・B・C）で共通して使う設定は `reviewcompass.yaml` 側に置き、各アプリ固有設定はアプリ側で書く。

## 5. レビューモード語彙（Requirement 6 受入 6）

foundation は次の値を正本として所有する：

- `manual_dogfooding`：人間が手動で 3 役を模倣して作成したレビュー記録
- `runtime_mediated`：実行時機能（フェーズ 4 で実装）が大規模言語モデル呼び出しを伴って作成したレビュー記録
- `subagent_mediated`：Claude Code 内部のサブエージェント機構を用いた 3 役レビュー記録（2026-05-22 正式採用、計画書 §5.23.12 由来）

語彙は今後の経路追加に対応する拡張余地を持つ。

## 6. 来歴項目（Requirement 6 受入 7）

他環境からの取り込みのため、次の項目を必須として継承する：

- `source_repository_id`（採取元リポジトリ識別子）
- `source_revision`（採取時の改訂版識別子）

中央側集約モード（複数アプリからのレビュー記録の集約）の継続価値を踏まえた継承（§5.17.5／§5.18.14）。

## 7. 配置先（ディレクトリ構造）

foundation 由来の成果物は次に配置される（design.md §共有資産配置を正本とする。要件段の旧配置 `schemas/`・`templates/` は design 段で `runtime/` 配下へ統合再編され、本節は 2026-06-01 セッション45 の実装段 T-001 で正本に追従更新した）：

- `runtime/foundation/layer1_framework.yaml`：4 段正式名称と 3 役抽象名の正本
- `runtime/foundation/metadata_contract.yaml`：20 必須メタデータ項目と 4 状態軸の値リスト
- `runtime/schemas/<5 ファイル>.schema.json`：5 共通スキーマ
- `runtime/validators/contracts/<2 ファイル>.schema.json`：検証器用 2 スキーマ
- `runtime/prompts/<段目的>/<役>.prompt.md`：3 役プロンプト雛形
- `runtime/config/reviewcompass.yaml`：ツール本体既定値（2 層モデル下層）
- `runtime/config/<2 ファイル>.template`：アプリ側設定雛形と用語集雛形

## 8. 他機能との関係

foundation はレビュー実行を持たず、他機能の土台になる：

- `runtime` は本機能のスキーマ、プロンプト配置、設定契約、状態機械を取り込む
- `evaluation` は本機能のレビューメタデータ契約とスキーマに依存する
- `self-improvement` は本機能の所見／判定／レビュー事例のスキーマに依存する
- `analysis` は本機能で定義される証拠フィールドを参照する
- `workflow-management` は本機能の状態機械契約と版管理規約に依存する
- `conformance-evaluation` は本機能の検証器用メタデータ契約に依存する

## 9. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加する：

- design.md 抽出に基づく設計の説明（§5.18 継承方針）
- 各スキーマの具体的なフィールド構造の説明
- プロンプト雛形の運用方針
- 検証器の動作仕様

## 10. 関連文書

- 形式仕様：[.reviewcompass/specs/foundation/requirements.md](../../.reviewcompass/specs/foundation/requirements.md)
- 計画書 §5.18：[foundation 機能の継承方針](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §4：[ReviewCompass リポジトリの初期構造案](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 foundation 行：[抽出対応表](../extraction-mapping.md)
