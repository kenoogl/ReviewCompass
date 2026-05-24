# Requirements Document：conformance-evaluation

## Introduction

`conformance-evaluation` は ReviewCompass の **7 番目の独立機能**で、計画書 §5.10 で第 1 期（フェーズ 1〜4）から含めることを確定した。先行プロジェクトの `.kiro/methodology/dual-reviewer-spec-driven-paper/v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として継承する。

本機能の方向は **下流 → 上流（逆方向）**：実装コードから上流文書（intent／requirements／design／tasks）を推定する。上流文書がなくてもよい（既存コードベースへの導入を想定）。

実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）は `analysis` および `runtime` の連携（計画書 §5.9）に残し、本機能では吸収しない。性格が違うため分離する（§5.10.1）。

## Boundary Context

- **In scope（範囲内）**
  - 主要用途 1：文書生成（オンボーディング）—— 既存コードから intent／requirements／design／tasks を推定生成
  - 主要用途 2：照合チェック —— 既存上流文書と推定上流文書を比較し、実装中の意図ずれ・文書連携不足を検出
  - 12 criteria の検査構造（intent／requirements／design／tasks の 4 軸 × 3 criteria）
  - 3 役レビュー機構の流用（主役 → 敵対役 → 判定役、§5.9 規律全般）
  - 評価記録の出力（`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`）
  - v3-plan §3.3 のうち「文書レベルの戻し（intent／requirements／design／tasks）」

- **Out of scope（範囲外）**
  - 実装適合レビュー（§5.9 と `runtime` の連携に残す。本機能では吸収しない）
  - v3-plan §3.3 の規律レベル戻し（`self-improvement` の責務）
  - schema／prompt／code レベルの戻し（`self-improvement` の他 4 層改善、フェーズ 4 完了後の宿題）
  - 5 評価軸のうち実装適合（§5.9 の実装適合レビューに残す）

- **隣接仕様の期待**
  - `foundation`：スキーマとメタデータ契約、検証器状態語彙、レビューモード語彙、証拠区分語彙、`adversarial_outcome` 語彙を再定義せず参照（依存：hard、§5.10.5）
  - `runtime`：実装コードのレビュー実行記録を入力源として活用（依存：review、§5.10.5。本機能が runtime の出力を読む）
  - `evaluation`：評価結果との突き合わせ（依存：review、§5.10.5）
  - `workflow-management`：所定手続きの実行履歴と上流文書の整合確認（依存：review、§5.10.5）
  - `analysis`：本機能の 12 criteria の検査結果を受け取り、4 出力先（特に監査用報告と報告書向け原データ）に取り込む（`analysis` Requirement 8 受入 5 由来）
  - `self-improvement`：本機能の 12 criteria 検査結果を規律改善の入力として提供する（`self-improvement` が本機能の出力を読む方向。`self-improvement` は本機能の `depends_on` には含まれず、出力先として参照される関係。`self-improvement` requirements.md の Boundary Context 隣接期待行と整合）

依存関係の特殊構造（`stages/feature-dependency.yaml`）：他機能は単純リスト構造（`depends_on: [list]`）だが、本機能は依存種別を区別する連想配列構造（`hard`／`review`）を持つ。`workflow-management` Requirement 8 受入 2 のスキーマ拡張で扱う。

## Requirements

### Requirement 1：機能の方向性と前提

**目的（Objective）**：保守担当者と利用者が、本機能の方向（下流 → 上流の逆方向）と前提（上流文書がなくてもよい）を明確に把握できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は実装コードを入力として上流文書（intent／requirements／design／tasks）を推定または照合する逆方向の機能として動作する。
2. 本機能は上流文書が存在しない場合でも動作する（既存コードベースへの導入を想定）。
3. 本機能は実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）を吸収しない。実装適合レビューは `analysis` および `runtime` の連携（§5.9）に残る。
4. 本機能は文書生成モードと照合チェックモードの 2 モードを支える。
5. 本機能は両モードで同一の 12 criteria 構造（Requirement 4 由来）を使う。

### Requirement 2：文書生成モード（オンボーディング）

**目的**：既存プロジェクトへの ReviewCompass 導入を行う利用者が、実装コードから上流文書（intent／requirements／design／tasks）を推定生成し、ReviewCompass の仕様駆動レビューを開始できるようにする。

#### 受入基準

1. 本機能は実装コードを入力として、intent／requirements／design／tasks の各上流文書を推定生成する。**最低限充足条件**：各推定文書は最低限、Introduction／Boundary Context／Requirements（または相当節）の 3 節を含み、実装コードへの参照を最低 1 件含む。詳細な節構成と参照粒度は design 段で確定する。
2. 本機能は推定生成した文書を、`<対象アプリ>/.reviewcompass/specs/<feature>/` の各ファイル（intent.md／requirements.md／design.md／tasks.md）の **推定版**として出力する。既存上流文書がある場合は上書きせず、次のパス規則で出力：`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/inferred/<日付>/<file>.md`（別ディレクトリ方式）。生成記録（受入 5）と並列の `conformance/` 配下に集約する。
3. 本機能は推定の根拠（実装コードのどの部分から推定したか）を実行記録に保持する。
4. 本機能は推定結果に対する人間判断の必要性を明示する（推定はあくまで初版、人間が修正する前提）。
5. 本機能は文書生成モードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-generation.md` として保管する。

### Requirement 3：照合チェックモード

**目的**：既存上流文書を持つ利用者が、実装中の意図ずれ・文書連携不足を機械的に検出できるようにする。

#### 受入基準

1. 本機能は既存上流文書と実装コードから推定した上流文書を比較し、食い違いを列挙する。**比較対象粒度**：4 上流フェーズ × 3 criteria（Requirement 4 受入 1 由来、計 12 criteria）の各 criterion に基づき、次の対応関係を比較する：節の有無、節内の主張・受入基準の対応、実装コードへの言及齟齬。「食い違い」とはこれら 3 対応関係のいずれかに不整合があることを指す。詳細な判定アルゴリズムは design 段で確定する。
2. 本機能は食い違いごとに 4 段重大度（CRITICAL／ERROR／WARN／INFO、`foundation` Requirement 6 受入 6 由来）を付与する。
3. 本機能は食い違いの妥当性を 3 役レビュー機構（Requirement 5）で検証する。
4. 本機能は判定役の判定値（must-fix／should-fix／leave-as-is、`foundation` 仕様の規律由来）を保持する。
5. 本機能は照合チェックモードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md` として保管する。

### Requirement 4：12 criteria の検査構造

**目的**：本機能の実装者と利用者が、4 上流フェーズ × 3 criteria の検査構造を明確に把握できるようにする。

#### 受入基準

1. 本機能は次の 12 criteria を支える：
   - **intent conformance（3 criteria）**：目的が実装で保たれているか／制約が実装で守られているか／優先順位が実装で反映されているか
   - **requirements conformance（3 criteria）**：受け入れ基準と実装の対応／API・データ契約と実装の対応／例外系・境界条件と実装の対応
   - **design conformance（3 criteria）**：モジュール構成・データモデルと実装の対応／接合面（API シグネチャ・エラーモデル）と実装の対応／アルゴリズム・性能達成手段と実装の対応
   - **tasks conformance（3 criteria）**：タスク完了基準と実装の対応／依存と順序の遵守状況／横断タスクの実施状況
2. 各 criterion のサブ構造（要点／詳細抽出／深掘り／該当なし）は §5.9.2 の規律をそのまま継承する。
3. 5 評価軸のうち実装適合は本機能の責務外（§5.9 の実装適合レビューに残す）。
4. 12 criteria の検査仕様は `schemas/review-criteria/conformance_evaluation.yaml` として整備する（フェーズ 2 で配置）。

### Requirement 5：3 役レビュー機構の流用

**目的**：本機能の利用者と運用者が、§5.9 のレビュー方法規律を本機能でも一貫して適用できるようにする。

#### 受入基準

1. 本機能は 3 役レビュー機構（主役 → 敵対役 → 判定役）を文書生成モードと照合チェックモードの両方で使う。
   - **文書生成タスク**：主役（コードから生成）→ 敵対役（生成文書の誤推定を独立指摘）→ 判定役（採否判断）
   - **照合チェック**：主役（食い違いを列挙）→ 敵対役（妥当性検証）→ 判定役（must-fix／should-fix／leave-as-is）
2. 本機能は §5.9.1 のモデル多様化規律、ファイル遮断規律、β 逐次方式を適用する。
3. 本機能は §5.9.2 の重大度語彙 4 段（CRITICAL／ERROR／WARN／INFO）を適用する。
4. 本機能は §5.9.3 の所見メタデータ必須化（severity／judgment／depth／evidence_type／verifying_commands）を適用する。
5. 本機能は §5.9.6 の 3 方式比較データ取得（`findings_by_method`）を適用する。
6. 本機能はレビューモード語彙（`manual_dogfooding`／`runtime_mediated`／`subagent_mediated`、`foundation` Requirement 6 受入 6 由来）を再定義せず参照する。
7. 本機能は §5.9.7 の API 経路と障害対応（タイムアウト・リトライ・部分失敗の検知と扱い）を適用する。本機能は実装コードに対する複数の LLM 呼び出しを伴うため、障害対応戦略を §5.9.7 から流用する（計画書 §5.10.3 行 1051 由来）。

### Requirement 6：評価記録の type 値と配置

**目的**：本機能の評価記録と他のレビュー記録を区別可能にし、`analysis`／`self-improvement`／監査担当が機能別に処理できるようにする。

#### 受入基準

1. 本機能は評価記録の `type` 値を `conformance_evaluation` として統合する（生成モード／照合モードの区別は内部フィールドで識別）。
2. 本機能は評価記録の配置先を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md` とする。`reviews/` ディレクトリとは別ディレクトリ。
3. 本機能は評価記録の front-matter に `mode_internal: generation` または `mode_internal: check` を含め、生成モードと照合モードを区別する。
4. 本機能は評価記録の `author` と `reviewer` を §5.4 規律に従って明示する（`workflow-management` Requirement 3 と整合）。
5. 本機能は評価記録から `runtime`／`evaluation`／`workflow-management` の関連実行記録への参照を保持する。

### Requirement 7：依存関係の連想配列構造

**目的**：本機能の実装者と他機能の保守担当が、本機能の特殊な依存関係（依存種別を区別する連想配列構造）を理解できるようにする。

#### 受入基準

1. 本機能は `stages/feature-dependency.yaml` における自身の依存記述を、他機能の単純リスト構造（`depends_on: [list]`）と異なる連想配列構造（`depends_on: {feature_name: dependency_type}`）で表現する。
2. 本機能の依存種別は次の 2 値を区別する：
   - **`hard`**：本機能の動作に必須の依存。当該機能の完成なしに本機能は機能しない（例：`foundation: hard`）
   - **`review`**：本機能が当該機能の出力を読む依存。必須ではないが活用する（例：`runtime: review`、`evaluation: review`、`workflow-management: review`）
3. 本機能の依存記述は計画書 §5.10.5 行 1075〜1080 に確定済み：`foundation: hard`／`runtime: review`／`evaluation: review`／`workflow-management: review`。
4. 本機能は `workflow-management` Requirement 8 受入 2 のスキーマ拡張（連想配列構造の許容）と整合する。
5. 本機能は phase_order の最後に位置付ける（依存先がすべて先に完了する前提）。

### Requirement 8：実装適合レビューとの分離

**目的**：保守担当者が、本機能（下流 → 上流の逆方向）と実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）を混同しないようにする。

#### 受入基準

1. 本機能は実装適合レビューの責務を持たない。
2. 実装適合レビューは §5.9 のレビュー方法と `runtime` の連携（フェーズ終端の検査）に残る。
3. 本機能と実装適合レビューは方向（下流 → 上流 vs 順方向）、前提（上流文書なくてもよい vs 上流文書必須）、実施時期（任意 vs フェーズ終端）で性格が違う。
4. 本機能の実装者は実装適合レビューと混在する成果物を作らない（評価記録は `conformance/` ディレクトリ、実装適合レビュー記録は `reviews/` ディレクトリ）。

## Change Intent

本仕様は計画書 §5.10 で第 1 期から含めることを確定した **新規 7 番目機能**で、先行プロジェクトの `v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として書き起こした。

ReviewCompass 固有の構築：

- 機能の方向（下流 → 上流の逆方向）と前提（上流文書なくてもよい）を Requirement 1 で明示
- 文書生成モード（オンボーディング）を Requirement 2 で定義
- 照合チェックモードを Requirement 3 で定義
- 12 criteria 構造（4 上流フェーズ × 3 criteria）を Requirement 4 で定義（§5.10.2 由来）
- 3 役レビュー機構の流用を Requirement 5 で明示（§5.9 規律全般の適用）
- 評価記録の type 値と配置先を Requirement 6 で確定（§5.10.4 由来）
- 依存関係の連想配列構造を Requirement 7 で定義（§5.10.5 由来、A-005 連動）
- 実装適合レビューとの分離を Requirement 8 で明示（§5.10.1 由来）

機能横断レビューに持ち越す所見（連動）：

- A-005（pending-cross-feature-findings.md §A-005）：本仕様 Requirement 7 で feature-dependency.yaml の連想配列構造を明示し、workflow-management Requirement 8 受入 2 のスキーマ拡張（既セッション内対処済み）と整合させた。本仕様作成により A-005 の conformance-evaluation 側の対処は完了
- 他の機能横断波及所見（A-001／A-003／A-004／A-007）は [.reviewcompass/pending-cross-feature-findings.md](../../pending-cross-feature-findings.md) を参照

v3-plan §3.3 の扱い（§5.10.6 由来）：

- 文書レベルの戻し（intent／requirements／design／tasks）：本機能の主機能（Requirement 2／3）に含まれる
- 規律レベルの戻し：`self-improvement` の workflow 改善（§5.16）が扱う、本機能のスコープ外
- schema／prompt／code レベルの戻し：`self-improvement` の他 4 層改善、フェーズ 4 完了後の宿題、本機能のスコープ外
