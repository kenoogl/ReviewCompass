# Requirements Document：conformance-evaluation

## Introduction

`conformance-evaluation` は ReviewCompass の **7 番目の独立機能**で、計画書 §5.10 で第 1 期（フェーズ 1〜4）から含めることを確定した。先行プロジェクトの `.kiro/methodology/dual-reviewer-spec-driven-paper/v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として継承する。

本機能の方向は **下流 → 上流（逆方向）**：実装コードから上流文書（intent／requirements／design／tasks）を推定する。上流文書がなくてもよい（既存コードベースへの導入を想定）。

実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）は `analysis` および `runtime` の連携（計画書 §5.9）に残し、本機能では吸収しない。性格が違うため分離する（§5.10.1）。

## Boundary Context

- **In scope（範囲内）**
  - **主要用途 1（本筋）：照合チェック** —— 仕様駆動開発で構築したコードの要件充足判断。既存上流文書と推定上流文書を比較し、実装中の意図ずれ・文書連携不足を検出（2026-05-24 セッション 23 利用者整理）
  - **主要用途 2（傍流）：文書生成（オンボーディング、リバースエンジニアリング）** —— 既存上流文書のないコードベースに ReviewCompass を導入するため、実装コードから上流文書の骨子を生成。完全自動推定は目指さず、人協働を前提とした推定支援機能（2026-05-24 セッション 23 利用者整理）
  - **6 criteria の検査構造**（requirements／design の 2 軸 × 3 criteria、計画書 §5.10.2 由来、2026-05-24 セッション 23 改訂）
  - 推定段階と照合段階の両方への 3 役レビュー機構の適用（主役 → 敵対役 → 判定役、§5.9 規律全般、§5.10.10 由来）
  - モード別の既存文書扱いルール（照合チェックモードでは既存 feature-partitioning を推定時入力、他は遮断。文書生成モードは人協働、§5.10.9 由来）
  - 評価記録の出力（`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`）
  - v3-plan §3.3 のうち「文書レベルの戻し（本筋：requirements ／ design、参考：intent、計画書 §5.10.6）」

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
  - `analysis`：本機能の 6 criteria の検査結果を受け取り、4 出力先（特に監査用報告と報告書向け原データ）に取り込む（`analysis` Requirement 8 受入 5 由来）
  - `self-improvement`：本機能の 6 criteria 検査結果を規律改善の入力として提供する（`self-improvement` が本機能の出力を読む方向。`self-improvement` は本機能の `depends_on` には含まれず、出力先として参照される関係。`self-improvement` requirements.md の Boundary Context 隣接期待行と整合）

依存関係の特殊構造（`stages/feature-dependency.yaml`）：他機能は単純リスト構造（`depends_on: [list]`）だが、本機能は依存種別を区別する連想配列構造（`hard`／`review`）を持つ。`workflow-management` Requirement 8 受入 2 のスキーマ拡張で扱う。

## Requirements

### Requirement 1：機能の方向性と前提

**目的（Objective）**：保守担当者と利用者が、本機能の方向（下流 → 上流の逆方向）と前提（上流文書がなくてもよい）を明確に把握できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は実装コードを入力として上流文書（**requirements ／ design を中心、intent は参考情報**）を推定または照合する逆方向の機能として動作する。feature-partitioning と tasks は本機能の照合対象外（計画書 §5.10.2 由来、2026-05-24 セッション 23 改訂、案 Y）。
2. 本機能は上流文書が存在しない場合でも動作する（既存コードベースへの導入を想定）。ただしこの場合は **傍流（文書生成モード、人協働）** として扱い、本機能は推定支援に留まる。
3. 本機能は実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）を吸収しない。実装適合レビューは `analysis` および `runtime` の連携（§5.9）に残る。
4. 本機能は **照合チェックモード（本筋）** と **文書生成モード（傍流、人協働）** の 2 モードを支える。各モードの推定プロセスと既存文書扱いは異なる（Requirement 2 ＋ Requirement 3、計画書 §5.10.9 由来）。
5. 本機能は両モードで同一の **6 criteria 構造**（Requirement 4 由来、requirements ／ design の 2 軸 × 3 criteria）を使う。intent は参考情報として推察、照合対象には含めない。

### Requirement 2：文書生成モード（傍流、人協働によるオンボーディング、2026-05-24 セッション 23 全面改訂）

**目的**：既存上流文書のないコードベースに ReviewCompass を導入する利用者が、実装コードから上流文書の骨子を **人協働で** 生成できるようにする。本モードは推定支援機能として位置付け、完全自動推定は目指さない（計画書 §5.10.1 由来、本筋／傍流の区別）。

#### 受入基準

1. 本機能は実装コードを入力として、**requirements ／ design** の骨子を自動推定する。**intent と feature-partitioning は人協働で決定**し、自動推定の対象外（計画書 §5.10.9 (b) 由来）。**tasks は対象外**（実装コードからのタスク分解推定は困難）：
   - **機能分割（feature-partitioning）**：機械的に候補を提示し、人間が境界を決定。組み合わせ最適化的に困難なため完全自動化は目指さない
   - **intent**：構造から参考情報として推察を提示、人間が意図を補完
   - **requirements ／ design**：自動推定し、人間が修正・補完
2. 本機能は推定生成した文書を、次のパス規則で出力する（人協働での編集を前提）：
   - 機能分割候補：`<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/feature-partitioning-candidates.md`
   - intent 参考情報：`<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/intent-reference.md`
   - 各機能の requirements ／ design：`<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/specs/<feature>/<file>.md`
3. 各推定文書は最低限、Introduction／Boundary Context／Requirements（または相当節）の 3 節を含み、実装コードへの参照を最低 1 件含む。詳細な節構成と参照粒度は design 段で確定する。
4. 本機能は推定の根拠（実装コードのどの部分から推定したか）を実行記録に保持する。
5. 本機能は推定結果に対する **人間判断の必要性を明示**する（推定はあくまで初版、人間が修正する前提、特に機能分割と intent は人間が主導）。
6. 本機能は各推定段階に 3 役レビュー機構を適用する（計画書 §5.10.10 由来）。各段階の解釈余地に応じた軽量／本格の使い分けは Requirement 5 ＋ 計画書 §5.10.10 に従う。
7. 本機能は文書生成モードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-generation.md` として保管する。

### Requirement 3：照合チェックモード（本筋、2026-05-24 セッション 23 全面改訂）

**目的**：仕様駆動開発で構築したコードを持つ利用者が、実装が要件を充足しているかを機械的に検証できるようにする。バイアス防止のため二段階方式を採用、既存 feature-partitioning だけは推定時の入力として尊重し、照合成立性を確保する（計画書 §5.10.9 (a) 由来）。

#### 受入基準

1. 本機能は **二段階方式** で実施する：
   - **第 1 段階：推定**：既存 feature-partitioning を入力として尊重しつつ、他の既存上流文書（intent／requirements／design）を遮断した状態で、実装コードから各機能の design ／ requirements を推定（intent は最後に参考情報として推察）
   - **第 2 段階：比較**：第 1 段階完了後、既存上流文書を読み込んで推定結果と比較、食い違いを列挙

   既存 feature-partitioning だけを例外として推定時の入力に含める理由：機能名・境界が違うと「同じ機能の design ／ requirements を比較」が成立しないため（2026-05-24 セッション 23 利用者指摘）。遮断は技術的手段（ファイル読み取り権限の制限、推定役プロセスの隔離、計画書 §5.10.9 由来）で実装する。具体的な遮断手法は design 段で確定する。
2. 本機能は既存上流文書と推定上流文書を比較し、食い違いを列挙する。**比較対象粒度**：2 上流フェーズ × 3 criteria（Requirement 4 受入 1 由来、計 **6 criteria**）の各 criterion に基づき、次の対応関係を比較する：節の有無、節内の主張・受入基準の対応、実装コードへの言及齟齬。「食い違い」とはこれら 3 対応関係のいずれかに不整合があることを指す。詳細な判定アルゴリズムは design 段で確定する。
3. 本機能は intent を独立の照合対象とせず、参考情報として比較する（推察結果と既存 intent の差異を所見メタとして記録、ただし must-fix 判定の対象外、計画書 §5.10.2 由来）。
4. 本機能は機能分割自体の食い違い検出をオプション機能として支援する（計画書 §5.10.9 (c) 由来）。利用者が明示的に要求した場合のみ、既存 feature-partitioning を遮断した状態で独立推定経路を併用、独立推定結果と既存を比較。標準動作には含めない。
5. 本機能は食い違いごとに 4 段重大度（CRITICAL／ERROR／WARN／INFO、`foundation` Requirement 6 受入 6 由来）を付与する。
6. 本機能は食い違いの妥当性を 3 役レビュー機構（Requirement 5）で検証する。推定段階と照合段階の両方に triad-review を適用する（計画書 §5.10.10 由来）。
7. 本機能は判定役の判定値（must-fix／should-fix／leave-as-is、`foundation` 仕様の規律由来）を保持する。
8. 本機能は照合チェックモードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md` として保管する。

### Requirement 4：6 criteria の検査構造（2026-05-24 セッション 23 改訂、案 Y）

**目的**：本機能の実装者と利用者が、2 上流フェーズ × 3 criteria の検査構造を明確に把握できるようにする。

#### 受入基準

1. 本機能は次の **6 criteria** を支える（本筋＝照合チェックモードの中心的な照合対象）：
   - **requirements conformance（3 criteria）**：受け入れ基準と実装の対応／API・データ契約と実装の対応／例外系・境界条件と実装の対応
   - **design conformance（3 criteria）**：モジュール構成・データモデルと実装の対応／接合面（API シグネチャ・エラーモデル）と実装の対応／アルゴリズム・性能達成手段と実装の対応
2. 本機能は照合対象から次を除外する（計画書 §5.10.2 由来、2026-05-24 セッション 23 利用者整理）：
   - **feature-partitioning**：照合チェックモード（本筋）では既存を所与の入力として尊重、独立の照合対象外（機能分割自体の照合は Requirement 3 受入 4 のオプション機能で対応）
   - **intent**：構造的側面からの推定が困難。参考情報として推察し、独立の照合対象外（Requirement 3 受入 3）
   - **tasks**：タスク分解過程は実装コードから推定困難（完成コードしか見えず分解過程は残らない）。対象外
3. 各 criterion のサブ構造（要点／詳細抽出／深掘り／該当なし）は §5.9.2 の規律をそのまま継承する。
4. 5 評価軸のうち実装適合は本機能の責務外（§5.9 の実装適合レビューに残す）。
5. **6 criteria** の検査仕様は `schemas/review-criteria/conformance_evaluation.yaml` として整備する（フェーズ 2 で配置）。

### Requirement 5：3 役レビュー機構の流用（2026-05-24 セッション 23 改訂：推定段階にも適用）

**目的**：本機能の利用者と運用者が、§5.9 のレビュー方法規律を本機能でも一貫して適用できるようにする。本機能では推定段階と照合段階の両方に triad-review を適用する。

#### 受入基準

1. 本機能は 3 役レビュー機構（主役 → 敵対役 → 判定役）を **推定段階と照合段階の両方** で使う：
   - **推定段階**（2026-05-24 セッション 23 追加）：主役（実装コードから推定）→ 敵対役（別解釈を提示）→ 判定役（実装との整合で判定）
   - **文書生成タスク（傍流）**：主役（コードから生成）→ 敵対役（生成文書の誤推定を独立指摘）→ 判定役（採否判断）
   - **照合チェック（本筋）**：主役（食い違いを列挙）→ 敵対役（妥当性検証）→ 判定役（must-fix／should-fix／leave-as-is）
2. 本機能は推定段階の triad-review 適用方針として、解釈余地に応じた **軽量／本格** の使い分けを行う（計画書 §5.10.10 由来）：
   - **本格適用**：3 役それぞれが独立して推定・判定（feature-partitioning 推定（傍流）、requirements 推定、照合段階）
   - **軽量適用**：主役推定の検証として、敵対役が別解釈を 1 つ提示、判定役が比較判定（design 推定、intent 推察）
3. 本機能は §5.9.1 のモデル多様化規律、ファイル遮断規律、β 逐次方式を適用する。
4. 本機能は §5.9.2 の重大度語彙 4 段（CRITICAL／ERROR／WARN／INFO）を適用する。
5. 本機能は §5.9.3 の所見メタデータ必須化（severity／judgment／depth／evidence_type／verifying_commands）を適用する。
6. 本機能は §5.9.6 の 3 方式比較データ取得（`findings_by_method`）を適用する。
7. 本機能はレビューモード語彙（`foundation` Requirement 6 受入 6 由来）を再定義せず参照する（値は `foundation` 正本が定める）。
8. 本機能は §5.9.7 の API 経路と障害対応（タイムアウト・リトライ・部分失敗の検知と扱い）を適用する。本機能は実装コードに対する複数の LLM 呼び出しを伴うため、障害対応戦略を §5.9.7 から流用する（計画書 §5.10.3 行 1051 由来）。

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

本仕様は計画書 §5.10 で第 1 期から含めることを確定した **新規 7 番目機能**で、先行プロジェクトの `v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として書き起こした。**2026-05-24 セッション 23 で利用者考察により本筋／傍流の整理と 2 軸 6 criteria への絞り込みを実施**（論点 A・B 対処、計画書 §5.10 改訂と連動）。

ReviewCompass 固有の構築：

- 機能の方向（下流 → 上流の逆方向）と前提（上流文書なくてもよい）を Requirement 1 で明示
- **本筋（照合チェック）と傍流（文書生成、人協働）の区別を Requirement 1〜3 で明示**（2026-05-24 セッション 23 改訂、計画書 §5.10.1 由来）
- 文書生成モード（傍流、人協働によるオンボーディング）を Requirement 2 で定義
- 照合チェックモード（本筋、二段階方式、既存 feature-partitioning は推定時入力）を Requirement 3 で定義
- **6 criteria 構造（requirements ／ design の 2 軸 × 3 criteria）を Requirement 4 で定義**（2026-05-24 セッション 23 改訂、計画書 §5.10.2 由来、案 Y）
- 3 役レビュー機構を **推定段階と照合段階の両方** に適用、軽量／本格の使い分けを Requirement 5 で明示（2026-05-24 セッション 23 改訂、計画書 §5.10.10 由来）
- 評価記録の type 値と配置先を Requirement 6 で確定（§5.10.4 由来）
- 依存関係の連想配列構造を Requirement 7 で定義（§5.10.5 由来、A-005 連動）
- 実装適合レビューとの分離を Requirement 8 で明示（§5.10.1 由来）

機能横断レビューで対処された所見：

- 本機能に関連する所見：
  - A-005（feature-dependency 連想配列構造、Requirement 7 で対処済み、workflow-management Requirement 8 受入 2 のスキーマ拡張と整合、2026-05-23）
  - A-008（conformance-evaluation から self-improvement への出力方向、Boundary Context 隣接仕様の self-improvement 記述で対処済み、2026-05-23）
  - A-009 第 2 波（旧 paper-interface 由来の用語不整合、Boundary Context 隣接仕様の analysis 記述 行 32 で「論文向け原データ」→「報告書向け原データ」修正済み、2026-05-24 セッション 23）
  - A-010 論点 A・B 対処（推定プロセスの整理と 2 軸 6 criteria 化、本仕様 Requirement 1〜5 ＋ Boundary Context と計画書 §5.10 改訂で対処済み、2026-05-24 セッション 23 軽量 reopen、利用者承認に基づく改訂）
- 参考：他機能の所見（A-001／A-003／A-004／A-007 とも 2026-05-23 対処済み）の対処履歴は carry-forward register 正本 [reviewcompass-import.yaml](../../../learning/workflow/carry-forward-register/reviewcompass-import.yaml) を参照

v3-plan §3.3 の扱い（§5.10.6 由来、2026-05-24 セッション 23 改訂で本筋／傍流に整理）：

- **本筋（照合チェック）**：requirements ／ design レベルの戻し（6 criteria）が主機能、intent は参考情報、feature-partitioning と tasks は対象外
- **傍流（文書生成、オンボーディング）**：requirements ／ design は自動推定、intent と feature-partitioning は人協働で決定、tasks は対象外
- 規律レベルの戻し：`self-improvement` の workflow 改善（§5.16）が扱う、本機能のスコープ外
- schema／prompt／code レベルの戻し：`self-improvement` の他 4 層改善、フェーズ 4 完了後の宿題、本機能のスコープ外
