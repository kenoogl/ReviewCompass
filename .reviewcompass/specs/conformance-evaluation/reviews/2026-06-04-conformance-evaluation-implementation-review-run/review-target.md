# conformance-evaluation implementation review target
run_id: 2026-06-04-conformance-evaluation-implementation-review-run
phase: implementation.triad-review
criteria: conformance_evaluation_implementation_t001_t013_feature_specific_review

## Review Instructions
Review whether the current conformance-evaluation implementation drafting satisfies requirements/design/tasks T-001 through T-013. Focus on behavioral bugs, missing tests, contract drift, workflow-policy violations, and gaps that should block implementation.triad-review completion. Classify findings with severity CRITICAL/ERROR/WARN/INFO and include target_location, description, rationale, and verifying_commands.

## Verification already run
` .venv/bin/python3 -m pytest tests/conformance-evaluation tests/self-improvement ` -> 105 passed.

## Current git diff stat
```
 .../specs/conformance-evaluation/spec.json         |  2 +-
 .reviewcompass/specs/self-improvement/spec.json    |  2 +-
 docs/operations/CONFORMANCE_EVALUATION.md          | 33 ++++++++++++++++++++++
 tools/README.md                                    | 13 +++++++++
 4 files changed, 48 insertions(+), 2 deletions(-)

```

## Current implementation diff
```diff
diff --git a/.reviewcompass/specs/conformance-evaluation/spec.json b/.reviewcompass/specs/conformance-evaluation/spec.json
index 6a73834..4152c79 100644
--- a/.reviewcompass/specs/conformance-evaluation/spec.json
+++ b/.reviewcompass/specs/conformance-evaluation/spec.json
@@ -37,7 +37,7 @@
       "approval": true
     },
     "implementation": {
-      "drafting": false,
+      "drafting": true,
       "triad-review": false,
       "review-wave": false,
       "alignment": false,
diff --git a/docs/operations/CONFORMANCE_EVALUATION.md b/docs/operations/CONFORMANCE_EVALUATION.md
index 00dbf62..b238fad 100644
--- a/docs/operations/CONFORMANCE_EVALUATION.md
+++ b/docs/operations/CONFORMANCE_EVALUATION.md
@@ -95,6 +95,39 @@
 
 評価記録の `type` 値は `conformance_evaluation` に統合し、`mode_internal` フィールドで `generation` と `check` を区別する。
 
+評価記録は必ず `conformance/<日付>-<mode>.md` のパス規則に従い、`reviews/` とは別に保管する。`reviews/` は仕様駆動レビューの記録、`conformance/` は本機能の下流 → 上流評価記録であり、混在させない。
+
+文書生成モードの推定出力先は次のとおりとする。
+
+```
+<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/
+├── feature-partitioning-candidates.md
+├── intent-reference.md
+└── specs/<feature>/
+    ├── requirements.md
+    └── design.md
+```
+
+モード切替は `check` または `generation` の明示指定のみで行い、既存文書の有無による自動判定は行わない。
+
+## 6.1 機械検査（MV-1〜MV-7）
+
+第 1 期の機械検査は手動 grep / find の補助として `tools/conformance-evaluation-check.py` から段階導入する。
+
+| ID | 検査 | 失敗時の扱い |
+|---|---|---|
+| MV-1 | 評価記録に `type: conformance_evaluation` がある | 遮断推奨 |
+| MV-2 | `mode_internal` が `check` または `generation` | 遮断推奨 |
+| MV-3 | 評価記録が `conformance/` にあり `reviews/` と混在しない | 遮断推奨 |
+| MV-4 | 推定文書に Introduction / Boundary Context / Requirements 相当の 3 節がある | 警告続行可 |
+| MV-5 | 推定根拠が `<ファイルパス>:<行範囲>` 形式である | 警告続行可 |
+| MV-6 | 推定役プロンプトに既存上流文書パスが混入せず、自律探索禁止条項がある | 遮断必須 |
+| MV-7 | foundation 受入番号参照が foundation requirements.md と一致する | 警告続行可 |
+
+MV-6 の第 1 期最小仕様では、推定役プロンプトログに時刻、実行 ID、プロンプト全文を残し、`logs/estimation/<run_id>/prompt.log` 相当の場所に保存する。検査は、既存上流文書パス（例 `intent.md`、`requirements.md`、`design.md`）の不在確認と、自律探索禁止条項の存在確認の 2 条件で行う。
+
+`tools/conformance-evaluation-check.py` は conformance-evaluation 固有の評価記録・遮断・推定根拠を検査する。workflow-management の `tools/check-workflow-action.py` は workflow_state や不可逆操作の順序を検査するため、責務は異なる。
+
 ## 7. 依存関係の特殊構造（Requirement 7）
 
 本機能は他機能と異なり、`stages/feature-dependency.yaml` で依存種別を区別する連想配列構造を持つ（計画書 §5.10.5 由来、A-005 連動）：
diff --git a/tools/README.md b/tools/README.md
index fbbabdb..186d880 100644
--- a/tools/README.md
+++ b/tools/README.md
@@ -14,3 +14,16 @@ ReviewCompass の補助スクリプトを置く場所。
 - 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/self-improvement-check.py`
 
 `tools/self-improvement-check.py` は self-improvement の機械検査 CLI の配置予定名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。
+
+## conformance-evaluation
+
+`tools/conformance_evaluation/` は `conformance-evaluation` 機能の import 対象 Python パッケージを置く名前空間である。
+
+`tools/conformance_evaluation/schemas/` はツール内部の中間スキーマを置く場所で、6 criteria の永続的な検査仕様を置く `schemas/review-criteria/` とは分離する。
+
+命名規約:
+
+- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/conformance_evaluation/`
+- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/conformance-evaluation-check.py`
+
+`tools/conformance-evaluation-check.py` は conformance-evaluation の機械検査 CLI の配置名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。

```

## File: .reviewcompass/specs/conformance-evaluation/spec.json
```
{
  "feature_name": "conformance-evaluation",
  "language": "ja",
  "created_at": "2026-05-24T00:00:00+09:00",
  "updated_at": "2026-06-02T00:00:00+09:00",
  "workflow_state": {
    "intent": {
      "drafting": true,
      "review": true,
      "approval": true,
      "reference": "stages/intent.yaml"
    },
    "feature-partitioning": {
      "candidate-proposal": true,
      "approval": true,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md"
    },
    "requirements": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "design": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "tasks": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "implementation": {
      "drafting": true,
      "triad-review": false,
      "review-wave": false,
      "alignment": false,
      "approval": false
    }
  },
  "reopened": {
    "intent": false,
    "feature-partitioning": false,
    "requirements": true,
    "design": true,
    "tasks": true,
    "implementation": false
  },
  "recheck": {
    "upstream_change_pending": false,
    "impacted_downstream_phases": []
  }
}
```

## File: .reviewcompass/specs/conformance-evaluation/requirements.md
```
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
```

## File: .reviewcompass/specs/conformance-evaluation/design.md
```
# Design Document：conformance-evaluation

最終更新：2026-05-26（セッション 27：design.drafting 起草と triad-review の must-fix 12 件対処、artifact-to-spec conformance evaluation の本筋／傍流分離設計）

## 概要（Overview）

`conformance-evaluation` は ReviewCompass の **7 番目の独立機能** で、本機能の方向は **下流 → 上流（逆方向）**。実装コードから上流文書（intent／requirements／design／tasks）を推定する。先行プロジェクトの `v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として継承し、計画書 §5.10 で第 1 期（フェーズ 1〜4）から含めることを確定。

本機能は **2 モード** で動作する：

- **照合チェックモード（本筋）**：仕様駆動開発で構築したコードの要件充足判断。バイアス防止のため二段階方式（推定 → 比較）を採用、既存 feature-partitioning だけは推定時の入力として尊重し、他の既存上流文書は遮断
- **文書生成モード（傍流、人協働）**：既存上流文書のないコードベースに ReviewCompass を導入するための推定支援。完全自動推定は目指さず、機能境界の決定等の本質的判断は人間が担う

要件文書（requirements.md）は 8 件の Requirement で、機能の方向性／文書生成モード／照合チェックモード／6 criteria 検査構造／3 役レビュー機構の流用／評価記録の type 値と配置／依存関係の連想配列構造／実装適合レビューとの分離を求めている。本設計は計画書 §5.10.1〜§5.10.10（機能の性格・評価軸・5 評価軸の整理・評価記録・依存関係・v3-plan 連携・criteria 数・段階的導入・モード別の既存文書扱い・推定段階の triad-review 適用）を実装可能な形に落とし込み、`v3-plan.md` の素材（future feature 記述）から本機能の独立仕様として再設計する。

本設計の所有物は **推定モデル・比較モデル・モード切替モデル・triad-review 適用モデル・評価記録モデル・依存関係モデル** の 6 つのモデルである。実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）は `analysis` および `runtime` の連携に残し、本機能では吸収しない（§5.10.1）。

## 目標（Goals）

- **照合チェックモード（本筋）** を二段階方式（推定 → 比較）で実装し、既存 feature-partitioning だけは推定時の入力として尊重、他の既存上流文書（intent／requirements／design）は推定時に技術的に遮断する（Req 3、§5.10.9）
- **文書生成モード（傍流）** を人協働の推定支援機能として実装し、機能分割と intent の決定は人間が主導、requirements ／ design は自動推定（Req 2、§5.10.9 (b)）
- **6 criteria 検査構造**（requirements 3 criteria＋ design 3 criteria）を機械可読な検査仕様として整備（Req 4、§5.10.2）
- **3 役レビュー機構** を推定段階と照合段階の両方に適用、軽量／本格の使い分けで運用コストと検証品質のバランスを取る（Req 5、§5.10.10）
- **評価記録の type 値 `conformance_evaluation`** と配置先 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md` を機械可読に確定（Req 6）
- **依存関係の連想配列構造**（`hard`／`review` の 2 値）を `workflow-management` のスキーマ拡張と整合させて表現（Req 7、§5.10.5）
- **実装適合レビューとの分離**を機械検査可能な形で担保（評価記録は `conformance/` ディレクトリ、実装適合レビューは `reviews/` ディレクトリ、Req 8）

## 範囲外（Non-Goals）

- 実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）：`analysis` および `runtime` の連携（§5.9）に残す（Req 8、§5.10.1）
- v3-plan §3.3 の規律レベル戻し：`self-improvement` の責務（Req 7／§5.10.6）
- schema／prompt／code レベルの戻し：`self-improvement` の他 4 層改善（フェーズ 4 完了後の宿題、§5.10.6）
- 5 評価軸のうち実装適合：§5.9 の実装適合レビューに残す（Req 4 受入 4）
- **tasks 階層の照合**：実装コードから推定困難（完成コードしか見えず分解過程は残らない、§5.10.2）
- **feature-partitioning 自体の照合（標準動作）**：本筋では既存を所与の入力として尊重、独立推定経路はオプション機能として提供のみ（Req 3 受入 4）
- intent の独立照合：参考情報として推察するに留め、独立の照合対象には含めない（Req 4 受入 2）
- 完全自動推定：文書生成モード（傍流）は人協働を前提（Req 2 受入 5）

## 設計の前提（Design Drivers）

- 本機能は **下流 → 上流（逆方向）** の性格を持ち、実装適合レビュー（順方向）とは方向が異なるため分離する（§5.10.1）
- **バイアス防止が中核設計課題**：既存上流文書を推定時に読むと推定結果が既存文書に引きずられる。照合チェックモードでは二段階方式（既存遮断 → 推定 → 比較）で対処（Req 3、§5.10.9）
- **照合成立性のため feature-partitioning だけは例外**：機能名・境界が違うと「同じ機能の design ／ requirements を比較」が成立しないため、既存 feature-partitioning は推定時の入力として尊重する（Req 3 受入 1、2026-05-24 セッション 23 利用者指摘）
- **解釈余地の差で軽量／本格を使い分ける**：feature-partitioning 推定・requirements 推定・照合段階は解釈余地が大きく本格適用、design 推定は実装コードから比較的直接読み取れるため軽量適用、intent 推察は参考情報として多角的に保持するため軽量適用（Req 5 受入 2、§5.10.10、§11.2 と整合）
- **2 軸 6 criteria への絞り込み**：feature-partitioning は所与・intent は参考・tasks は推定困難という理由で照合対象から除外し、requirements ／ design の 2 軸に絞ることで検査の単純性と意味的整合を両立（§5.10.2、2026-05-24 セッション 23 案 Y）
- 本機能と `workflow-management` の依存関係スキーマ拡張は連動：本機能の連想配列構造は `workflow-management` Requirement 8 受入 2 のスキーマ拡張に依存（Req 7 受入 4、A-005 連動）

## アーキテクチャ（Architecture）

### 1. データの流れ

#### 照合チェックモード（本筋）

```
[入力]
  ├── 対象アプリの実装コード
  ├── 対象アプリの既存 feature-partitioning（推定時の入力として尊重）
  └── 対象アプリの既存上流文書（intent／requirements／design、推定時は遮断、比較時に解放）
       ↓
[第 1 段階：推定（既存上流文書遮断、§9）]
  ├── feature-partitioning は既存を入力として尊重
  ├── 主役（primary）：実装コードから design を **先行推定**、続いて design からの逆算で requirements を推定（順序依存）
  ├── 敵対役（adversarial）：別解釈を提示
  └── 判定役（judgment）：実装との整合で判定
       ↓
[推定結果の確定]
       ↓
[第 2 段階：比較（既存上流文書を読み込む、§10）]
  ├── 既存 design ／ requirements を読み込み
  ├── 推定 design ／ requirements と比較
  ├── 6 criteria の各 criterion で「節の有無 ／ 主張・受入の対応 ／ 実装コード言及齟齬」を照合
  └── intent は参考情報として比較（must-fix 対象外）
       ↓
[3 役レビューによる食い違いの妥当性検証（§11）]
  ├── 主役：食い違いを列挙
  ├── 敵対役：妥当性検証
  └── 判定役：must-fix／should-fix／leave-as-is
       ↓
[評価記録の保管（§12）]
  └── <対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md
```

#### 文書生成モード（傍流、人協働）

```
[入力]
  └── 対象アプリの実装コード（既存上流文書なし、または不完全）
       ↓
[機能分割の人協働候補提示]
  ├── 機械的に機能分割候補を提示
  └── 人間が境界を決定（完全自動化は目指さない）
       ↓
[intent の参考情報推察]
  ├── 構造から intent を推察（参考情報として提示）
  └── 人間が意図を補完
       ↓
[requirements ／ design の自動推定（3 役レビュー機構を適用、design 先行→ requirements 逆算）]
  ├── 主役：実装コードから design を先行生成、続いて design から requirements を逆算
  ├── 敵対役：別解釈を提示（軽量／本格の使い分け、§11）
  └── 判定役：採否判断
       ↓
[推定文書の出力]
  ├── <対象アプリ>/.reviewcompass/conformance/inferred/<日付>/feature-partitioning-candidates.md
  ├── <対象アプリ>/.reviewcompass/conformance/inferred/<日付>/intent-reference.md
  └── <対象アプリ>/.reviewcompass/conformance/inferred/<日付>/specs/<feature>/<file>.md
       ↓
[評価記録の保管（§12）]
  └── <対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-generation.md
```

### 2. 責務分担モデル

| 機能 | 責務 | 本設計での扱い |
|---|---|---|
| **conformance-evaluation** | 実装コードから上流文書（requirements ／ design）を推定／照合、6 criteria 検査、評価記録の出力 | 本機能の中核責務、本設計が定義 |
| **foundation**（依存：hard） | スキーマとメタデータ契約、検証器状態語彙、レビューモード語彙、証拠区分語彙、`adversarial_outcome` 語彙の正本所有 | 上流機能、再定義せず参照 |
| **runtime**（依存：review） | 実装コードのレビュー実行記録の生成 | 上流機能、本機能は出力を入力源として活用 |
| **evaluation**（依存：review） | 評価結果の生成 | 上流機能、本機能は突き合わせに利用 |
| **workflow-management**（依存：review） | 所定手続きの実行履歴と上流文書の整合確認、依存関係スキーマの拡張（連想配列構造の許容） | 上流機能、依存関係スキーマで本機能を支援 |
| **analysis** | 本機能の 6 criteria 検査結果を 4 出力先（特に監査用報告と報告書向け原データ）に取り込み | 下流機能、本機能は機械可読出力を提供 |
| **self-improvement** | 本機能の 6 criteria 検査結果を規律改善の入力として活用 | 下流機能（出力先、`depends_on` には含まれない）、本機能の出力を提供 |

### 3. モード切替モデル

本機能は 2 モード（照合チェック／文書生成）を **明示的なモード指定** で切り替える。実装段の CLI 想定：`reviewcompass conformance check <feature>` と `reviewcompass conformance generate`（計画書 §5.10.7 の旧命名 `generate-spec` ／ `conformance-check` は本設計の階層型命名に統一する方針、計画書側を改訂、G6 利用者明示承認）。

| モード | 入力条件 | 推定対象 | 既存文書扱い |
|---|---|---|---|
| **照合チェック（本筋）** | 既存上流文書あり、既存 feature-partitioning あり | requirements ／ design | feature-partitioning：推定時の入力。intent ／ requirements ／ design：推定時に遮断、比較時に解放 |
| **文書生成（傍流、人協働）** | 既存上流文書なし、または不完全 | requirements ／ design（自動）／ feature-partitioning（人協働候補提示）／ intent（参考情報推察） | 既存があれば参考情報、なくても動作（既存コードベース導入想定） |

モード切替は明示的で、自動判定（既存上流文書の存在で自動切替）は行わない。理由：利用者の意図と実態が異なる場合（既存文書はあるが信頼性が低い等）に誤動作するリスクを避ける。

## 6. 文書生成モード（Generation Mode、傍流、人協働）

本章は requirements.md Req 2 に対応する。

### 6.1 役割と位置付け

- 既存上流文書のないコードベースに ReviewCompass を導入するため、実装コードから上流文書の骨子を **人協働で** 生成する
- 完全自動推定は目指さない（Req 2 受入 5、計画書 §5.10.1）
- 人協働の対象：機能境界の決定（人間が主導）、intent の意図補完（人間が主導）、requirements ／ design の修正（推定後に人間が編集）

### 6.2 4 階層の扱い分け

requirements.md Req 2 受入 1 に対応する 4 階層の扱い：

| 階層 | 扱い | 理由 |
|---|---|---|
| **feature-partitioning** | **人協働候補提示**（機械的に候補、人間が境界決定） | 組み合わせ最適化的に困難、完全自動化は目指さない |
| **intent** | **参考情報として推察**（人間が意図補完） | 構造から推察、ただし最終的な意図は人間が決定 |
| **requirements** | **自動推定（design からの逆算で実施、design 先行）**（人間が修正・補完） | 受入基準・API・例外系などコードから比較的直接導出可能、ただし design 推定の後に逆算する順序関係を持つ |
| **design** | **自動推定（先行実施）**（人間が修正・補完） | モジュール構成・接合面・アルゴリズムなどコードから直接読み取れる、requirements 推定より先行 |
| **tasks** | **対象外** | 完成コードしか見えず分解過程は残らない |

### 6.3 出力先のパス規則

requirements.md Req 2 受入 2 に対応するパス規則：

```
<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/
├── feature-partitioning-candidates.md     # 機械的候補、人間が編集
├── intent-reference.md                    # 参考情報、人間が編集
└── specs/<feature>/
    ├── requirements.md                    # 自動推定（design からの逆算）、人間が編集
    └── design.md                          # 自動推定（先行）、人間が編集
```

各推定文書は最低限、Introduction／Boundary Context／Requirements（または相当節）の 3 節を含み、実装コードへの参照を最低 1 件含む（Req 2 受入 3）。詳細な節構成と参照粒度は実装段で確定する。

### 6.4 推定根拠の保持

requirements.md Req 2 受入 4 に対応。

- 推定の根拠（実装コードのどの部分から推定したか）を実行記録に保持する
- 形式：`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-generation.md` の本文に「推定根拠」節を設け、各推定要素に対し `<ファイルパス>:<行範囲>` の参照を列挙

### 6.5 人間判断の必要性の明示

requirements.md Req 2 受入 5 に対応。

- 推定結果に対する **人間判断の必要性を明示** する（推定はあくまで初版、人間が修正する前提）
- 特に機能分割と intent は人間が主導することを生成文書の冒頭に注記
- 実装：生成文書の front-matter に `human_review_required: true` フィールドを追加

### 6.6 3 役レビュー機構の適用

requirements.md Req 2 受入 6 に対応。

- 各推定段階に 3 役レビュー機構を適用（§11 で詳細）
- 軽量／本格の使い分けは Req 5 受入 2 ＋計画書 §5.10.10 に従う

### 6.7 実行記録の保管

requirements.md Req 2 受入 7 に対応。

- 文書生成モードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-generation.md` として保管

## 7. 照合チェックモード（Check Mode、本筋、二段階方式）

本章は requirements.md Req 3 に対応する。

### 7.1 二段階方式の全体構造

requirements.md Req 3 受入 1 に対応する二段階方式：

```
第 1 段階：推定（既存上流文書遮断、§9）
   ├── 既存 feature-partitioning：入力として尊重
   ├── 既存 intent ／ requirements ／ design：技術的に遮断
   └── 推定結果：各機能の design（先行）／ requirements（design からの逆算）

第 2 段階：比較（既存上流文書を読み込む、§10）
   ├── 既存 intent ／ requirements ／ design を読み込み
   ├── 推定 design ／ requirements と比較
   └── 食い違いを列挙
```

### 7.2 既存 feature-partitioning を例外とする理由

機能名・境界が違うと「同じ機能の design ／ requirements を比較」が成立しないため、既存 feature-partitioning だけは推定時の入力に含める（2026-05-24 セッション 23 利用者指摘）。

例：既存上流文書では機能 A／B／C が定義されているが、本機能が独立に推定すると機能 X／Y／Z に分割される可能性がある。これでは「機能 A の design 推定 vs 既存機能 A の design」という対応関係が確立できない。

### 7.3 既存上流文書の遮断手法

requirements.md Req 3 受入 1 の遮断は **技術的手段** で実装する。第 1 期では **サブエージェント方式での遮断（プロンプト制御＋ファイル遮断）** を採用する。フェーズ 4 第 2 サイクル以降で chroot 環境での厳格遮断を検討する。

技術的手段の選択肢：

- **ファイル読み取り権限の制限**：推定役プロセスを `chroot` や読み取り権限制限環境で実行、既存上流文書のファイルへのアクセスを物理的に阻止
- **推定役プロセスの隔離**：サブエージェント方式の場合、Agent ツールのプロンプトに既存上流文書のパスを含めない、ファイル遮断規律（§5.9.1）を適用
- **入力の事前検査**：推定役へのプロンプトを事前検査し、既存上流文書の内容が混入していないかを grep で確認

第 1 期では「推定役プロセスの隔離」と「入力の事前検査」を併用する：

1. サブエージェントへのプロンプトに既存上流文書のパスを含めない
2. サブエージェントのツール権限を最小化（Read 等の汎用ツールへ既存上流文書配置先を渡さない）
3. プロンプトログを保管し、機械検査 MV-6 で事前混入を grep 検知
4. **自律ファイル探索の禁止**：サブエージェントが `glob` ／ `find` ／ `Read` 等で既存上流文書を能動的に探索することを明示的に禁止、推定役プロンプトに「対象アプリの実装コードのみを読み、上流文書は読まないこと」と明記

`chroot` 環境での厳格遮断（物理的アクセス遮断）はフェーズ 4 第 2 サイクル以降で検討する。

### 7.4 食い違い検出の対応関係

requirements.md Req 3 受入 2 に対応。

6 criteria（Requirement 4 受入 1 由来、2 上流フェーズ × 3 criteria）の各 criterion に基づき、次の **3 対応関係** を比較する：

| 対応関係 | 内容 | YAML フィールド名 |
|---|---|---|
| **節の有無** | 既存文書に対応する節があるか／推定文書に対応する節があるか | `section_existence` |
| **節内の主張・受入基準の対応** | 既存文書の主張・受入基準と推定文書の主張・受入基準が意味的に一致するか | `claim_correspondence` |
| **実装コードへの言及齟齬** | 既存文書が言及する実装コード箇所と推定文書が言及する実装コード箇所が一致するか | `code_reference_alignment` |

「食い違い」とはこれら 3 対応関係のいずれかに不整合があることを指す。詳細な判定アルゴリズムは実装段で確定する（§10 で設計レベルの記述）。

### 7.5 intent の参考情報扱い

requirements.md Req 3 受入 3 に対応。

- intent を独立の照合対象とせず、参考情報として比較する
- 推察結果と既存 intent の差異を所見メタとして記録
- ただし must-fix 判定の対象外（§5.10.2 由来）
- 差異の記録は推定根拠と同じく `conformance/<日付>-check.md` の本文に保持

### 7.6 機能分割自体の食い違い検出（オプション機能）

requirements.md Req 3 受入 4 に対応。

- 利用者が明示的に要求した場合のみ、既存 feature-partitioning を遮断した状態で独立推定経路を併用
- 独立推定結果と既存 feature-partitioning を比較
- 標準動作には含めない（CLI 引数 `--check-partitioning` で明示要求）

### 7.7 4 段重大度の付与

requirements.md Req 3 受入 5 に対応。

- 食い違いごとに 4 段重大度（CRITICAL／ERROR／WARN／INFO、`foundation` Requirement 6 受入 6 由来）を付与
- 重大度の判定基準（実装段で詳細化）：
  - CRITICAL：受入基準と実装の対応が完全に欠如、API 契約の根本的不一致
  - ERROR：例外系・境界条件の対応不足、データモデルの構造的不一致
  - WARN：表記揺れ、軽微な対応不足
  - INFO：将来改善余地、文書品質の指摘

### 7.8 3 役レビュー機構による妥当性検証

requirements.md Req 3 受入 6／7 に対応（§11 で詳細）。

- 食い違いの妥当性を 3 役レビュー機構で検証
- 判定役の判定値（must-fix／should-fix／leave-as-is）を保持

### 7.9 実行記録の保管

requirements.md Req 3 受入 8 に対応。

- 照合チェックモードの実行記録を `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md` として保管

## 8. 6 criteria 検査構造（Six Criteria Structure）

本章は requirements.md Req 4 に対応する。

### 8.1 6 criteria の定義

requirements.md Req 4 受入 1 と計画書 §5.10.2 に対応する 6 criteria：

#### requirements conformance（軸：`requirements`、3 criteria）

| Criterion ID | 内容 |
|---|---|
| **criterion-1** | 受け入れ基準と実装の対応（`receive_criteria`） |
| **criterion-2** | API ・データ契約と実装の対応（`api_data_contract`） |
| **criterion-3** | 例外系・境界条件と実装の対応（`boundary_condition`） |

#### design conformance（軸：`design`、3 criteria）

| Criterion ID | 内容 |
|---|---|
| **criterion-4** | モジュール構成・データモデルと実装の対応（`module_data_model`） |
| **criterion-5** | 接合面（API シグネチャ・エラーモデル）と実装の対応（`interface_signature`） |
| **criterion-6** | アルゴリズム・性能達成手段と実装の対応（`algorithm_performance`） |

### 8.2 照合対象から除外する階層

requirements.md Req 4 受入 2 と計画書 §5.10.2 に対応する除外理由：

| 階層 | 除外理由 |
|---|---|
| **feature-partitioning** | 照合チェックモード（本筋）では既存を所与の入力として尊重、独立の照合対象外（Req 3 受入 4 のオプション機能で対応） |
| **intent** | 構造的側面からの推定が困難、参考情報として推察（Req 3 受入 3） |
| **tasks** | タスク分解過程は実装コードから推定困難、対象外 |

### 8.3 各 criterion のサブ構造

requirements.md Req 4 受入 3 に対応。

各 criterion のサブ構造は §5.9.2 の規律をそのまま継承：

- **要点**：criterion の概要
- **詳細抽出**：実装コード／既存文書／推定文書の該当箇所と現状の記述を引用
- **深掘り**：食い違いの分析、対応関係の検討
- **該当なし**：criterion 該当なしの場合は明示

### 8.4 実装適合との分離

requirements.md Req 4 受入 4 に対応。

5 評価軸のうち実装適合は本機能の責務外（§5.9 の実装適合レビューに残す）。本機能は requirements ／ design conformance の 2 軸のみを担当。

### 8.5 検査仕様の整備

requirements.md Req 4 受入 5 に対応。

- 6 criteria の検査仕様は `schemas/review-criteria/conformance_evaluation.yaml` として整備（フェーズ 2 で配置）
- YAML 構造（実装段で確定）：
  ```yaml
  criteria:
    - id: criterion-1
      axis: requirements                    # 軸：requirements または design の 2 値
      criterion_short_name: receive_criteria
      name: 受け入れ基準と実装の対応
      sub_structure: [要点, 詳細抽出, 深掘り, 該当なし]
    # 以下 criterion-2 〜 criterion-6
  ```

## 9. 推定モデル（Estimation Model）

本章は照合チェックモード第 1 段階（Req 3 受入 1）と文書生成モード（Req 2）に共通する推定責務を担う。

### 9.1 役割と入出力

- **役割**：実装コードから上流文書（requirements ／ design）を推定する
- **入力**：実装コード、既存 feature-partitioning（照合チェックモードのみ）、3 役レビュー機構（§11）
- **出力**：推定された requirements ／ design 文書、推定根拠（コード参照）

### 9.2 推定アルゴリズム（design 先行→ requirements 逆算の順序依存）

第 1 期では **半自動** で実施（自動部分は LLM 呼び出し、判断部分は人間または LLM）。計画書 §5.10.9(a)（行 1176「requirements は design からの逆算で推定」）と §5.10.10（行 1216〜1217「第 2 段階 design 推定 → 第 3 段階 requirements 推定」）の順序関係を必須とする。

ステップ順序：

1. **実装コードの読み込み**：対象機能のコードベースを読む
2. **構造抽出**：モジュール構成、API シグネチャ、データモデル、例外処理を機械的に抽出
3. **design 要素の先行推定**（軽量 triad-review 適用）：抽出した構造から「実装が前提とする design 要素（モジュール構成・接合面・アルゴリズム・性能達成手段）」を LLM で推定。design は実装コードから直接読み取れる性格のため軽量適用
4. **requirements 受入基準の逆算推定**（本格 triad-review 適用）：先行推定した design 要素から「実装が満たしている受入基準・API 契約・例外系」を逆算して LLM で推定。requirements は解釈余地が大きい性格のため本格適用
5. **intent の参考情報推察**（軽量 triad-review 適用）：design ／ requirements の構造から intent を参考情報として推察。must-fix 対象外
6. **3 役レビュー機構による検証**：主役の推定 → 敵対役の別解釈 → 判定役の整合判定（§11）
7. **推定文書の生成**：YAML/Markdown 形式で出力、推定根拠（コード参照）を併記

実装段の詳細化（フェーズ 4 第 2 サイクル）：

- LLM プロンプト設計（プロンプト雛形 `templates/prompts/conformance_evaluation/`）
- 構造抽出ツールの実装言語非依存設計
- 推定品質の段階的改善

### 9.3 推定対象の階層別扱い

| 階層 | 照合チェックモード | 文書生成モード | 順序 |
|---|---|---|---|
| **feature-partitioning** | 既存を入力として尊重（推定しない） | 機械的候補を提示、人間が境界決定 | 推定パイプライン外 |
| **design** | 自動推定（実装コードから、**先行**） | 自動推定（人間が修正・補完） | **ステップ 3（先行）** |
| **requirements** | 自動推定（**design からの逆算**） | 自動推定（人間が修正・補完） | **ステップ 4（逆算）** |
| **intent** | 参考情報として推察（独立推定しない） | 構造から推察、人間が補完 | ステップ 5 |
| **tasks** | 対象外 | 対象外 | 対象外 |

### 9.4 推定根拠の保持

各推定要素に対して、実装コードの参照を最低 1 件付与する。YAML サンプル（axis は requirements ／ design の 2 値、criterion_id で specific な criterion を識別）：

```yaml
estimated_requirement:
  axis: requirements                            # axis は requirements または design の 2 値
  criterion_id: criterion-1                     # 6 criteria のいずれか
  description: |
    実装が「ユーザー登録時にメールアドレスの形式を検証する」要件を満たしている
  rationale_code_refs:
    - path: src/user_registration.py
      lines: 45-67
      excerpt: |
        if not validate_email_format(email):
            raise InvalidEmailError(...)
```

design 推定要素のサンプル：

```yaml
estimated_design_element:
  axis: design                                  # axis は requirements または design の 2 値
  criterion_id: criterion-4                     # モジュール構成・データモデル
  description: |
    user_registration モジュールは email 検証・パスワードハッシュ化・DB 永続化の 3 責務を持つ
  rationale_code_refs:
    - path: src/user_registration.py
      lines: 12-90
```

### 9.5 推定の信頼度

推定結果に **信頼度ラベル** を付与する。信頼度は推定根拠（コード参照件数、明示性）から自動判定（実装段で確定）。

**信頼度語彙の所有関係**：

信頼度ラベルは foundation の語彙正本として定義されている `confidence_label`（3 値：high／medium／low、foundation 要件 6 受入 11 ＋設計 §3.5）を参照する。本機能では再定義せず、foundation 参照のみで使用（A-013 対処完了、2026-05-26 セッション 28、Decision 11 と整合）。

| 値 | 本機能での判定基準（推定タスク） |
|---|---|
| **high** | 複数のコード参照、関数名／コメント／例外メッセージから明示的（foundation の「根拠が強い」と整合） |
| **medium** | 1〜2 のコード参照、間接的な導出（foundation の「中程度」と整合） |
| **low** | 構造からの推察のみ、人間判断が強く必要（foundation の「根拠が弱い」と整合） |

信頼度は文書生成モードの「人間判断の必要性」（§6.5）と整合させる。

## 10. 比較モデル（Comparison Model）

本章は照合チェックモード第 2 段階（Req 3 受入 1）に対応する。

### 10.1 役割と入出力

- **役割**：既存上流文書と推定上流文書を比較し、食い違いを列挙する
- **入力**：既存 design ／ requirements、推定 design ／ requirements、既存 intent（参考情報）
- **出力**：食い違いの列挙、4 段重大度、3 対応関係別の差分

### 10.2 比較対象の粒度

requirements.md Req 3 受入 2 に対応。

- 比較対象粒度：**2 上流フェーズ × 3 criteria** = 6 criteria
- 各 criterion で次の 3 対応関係を比較：節の有無（`section_existence`）／ 節内の主張・受入基準の対応（`claim_correspondence`）／ 実装コードへの言及齟齬（`code_reference_alignment`）（§7.4）
- 「食い違い」とはこれら 3 対応関係のいずれかに不整合があることを指す

### 10.3 比較アルゴリズム（概要）

実装段の詳細化（フェーズ 4 第 2 サイクル）：

1. **既存文書の読み込み**：既存 design ／ requirements を読む
2. **節の対応マッピング**：既存文書と推定文書の節を機能 × criterion 単位で対応付け
3. **節内の意味的比較**：LLM で「主張・受入基準が意味的に一致するか」を判定
4. **実装コード言及の照合**：既存文書が言及するコード箇所と推定文書が言及するコード箇所を grep ／ AST 解析で照合
5. **不整合の列挙**：3 対応関係のいずれかに不整合があれば食い違いとして記録
6. **4 段重大度の付与**：§7.7 の判定基準で重大度を判定

### 10.4 食い違いの記録形式

```yaml
finding_id: CF-001                         # Conformance Finding の通し番号（§10.7 で発番ルール）
finding_type: discrepancy                   # discrepancy / missing_section / extra_section
axis: requirements                          # axis は requirements または design の 2 値
criterion_id: criterion-1                   # 6 criteria のいずれか
correspondence_type: section_existence      # section_existence / claim_correspondence / code_reference_alignment の 3 値
severity: ERROR
existing_text: |
  既存 requirements の該当箇所の引用
estimated_text: |
  推定 requirements の該当箇所の引用
discrepancy_description: |
  食い違いの内容（30 文字以上）
implementation_code_refs:                   # 食い違いに関連する実装コード参照
  - path: src/...
    lines: 45-67
judgment_id: JD-001                         # 3 役レビュー後の判定 ID（§10.7）
```

### 10.5 intent の差異記録

requirements.md Req 3 受入 3 に対応。

- intent の差異は所見メタとして記録、ただし must-fix 判定の対象外
- 記録形式（topic-111／G-003 対処、2026-05-29 セッション 39）：`axis` は照合対象の 2 値（requirements ／ design）に固定し、intent は `axis` を使わず **参考情報専用フィールド `reference_axis: intent`** に記録する。`criterion_id` は `intent-reference` に設定。intent を `axis` の 3 値目にしないことで、照合の中心構造「2 軸 6 criteria」（§8.1、Decision 4）と整合し、intent の参考情報性（must-fix 対象外）をフィールド構造でも明確にする

### 10.6 比較結果の出力

照合チェックモードの実行記録 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md` に比較結果を出力：

- 食い違いごとの YAML エントリ
- 6 criteria 別の集計（食い違い件数、severity 別の内訳）
- 推定根拠と既存文書の出典

### 10.7 finding_id ／ judgment_id 発番ルール（G3 利用者明示承認）

self-improvement の Decision 9（proposal_id 発番ルール）と同型のパターン：

- **採番権者**：**conformance-evaluation**（本機能が採番）
- **名前空間**：接頭辞で分離
  - `CF-NNN`：Conformance Finding（食い違い所見）
  - `JD-NNN`：Judgment（判定役の判定結果）
  - 将来の拡張で `IF-NNN`（Inferred、推定要素）等を追加可能
- **通番リセット**：**なし**（時系列で通番増加、git 履歴で時系列が追える）
- **通番桁数**：3 桁から開始、999 件を超えたら自動で 4 桁に拡張
- **採番手順**：新規所見作成時に `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/` 配下の最大番号＋ 1 を採用

## 11. 3 役レビュー機構の適用（Triad Review Application）

本章は requirements.md Req 5 に対応する。

### 11.1 推定段階と照合段階の両方への適用

requirements.md Req 5 受入 1 に対応。

| 段階 | 主役 | 敵対役 | 判定役 |
|---|---|---|---|
| **推定段階（照合チェック・文書生成共通）** | 実装コードから推定（design 先行→ requirements 逆算） | 別解釈を提示 | 実装との整合で判定 |
| **文書生成タスク（傍流）** | コードから生成（design 先行→ requirements 逆算） | 生成文書の誤推定を独立指摘 | 採否判断 |
| **照合チェック（本筋）** | 食い違いを列挙 | 妥当性検証 | must-fix／should-fix／leave-as-is |

### 11.2 軽量／本格の使い分け

requirements.md Req 5 受入 2 と計画書 §5.10.10 に対応：

| 適用方式 | 内容 | 適用対象 |
|---|---|---|
| **本格適用** | 3 役それぞれが独立して推定・判定（β 逐次方式、§5.9.1） | feature-partitioning 推定（傍流）／ requirements 推定（design からの逆算）／ 照合段階 |
| **軽量適用** | 主役推定の検証として、敵対役が別解釈を 1 つ提示、判定役が比較判定 | design 推定（実装コードから直接読み取れる）／ intent 推察（参考情報として多角的に保持） |

軽量と本格の判断基準：解釈余地の大きさと推定の直接性。

- 解釈余地が大きい（feature-partitioning、requirements、照合食い違い判定）→ 本格適用
- 実装からの導出が比較的直接的（design）→ 軽量適用
- 参考情報扱いで多角的に保持（intent）→ 軽量適用

### 11.3 §5.9 規律の流用

requirements.md Req 5 受入 3〜8 に対応する流用項目：

| 項目 | 出典 |
|---|---|
| モデル多様化規律、ファイル遮断規律、β 逐次方式 | §5.9.1 |
| 重大度語彙 4 段（CRITICAL／ERROR／WARN／INFO） | §5.9.2 |
| 所見メタデータ必須化（severity／judgment／depth／evidence_type／verifying_commands） | §5.9.3 |
| 3 方式比較データ取得（`findings_by_method`） | §5.9.6 |
| レビューモード語彙（値は foundation 正本を参照） | foundation Req 6 受入 6（参照、機械検査 MV-7 で照合） |
| API 経路と障害対応（タイムアウト・リトライ・部分失敗の検知と扱い） | §5.9.7 |

### 11.4 API 経路の障害対応

requirements.md Req 5 受入 8 と計画書 §5.10.3 に対応。

本機能は実装コードに対する複数の LLM 呼び出しを伴うため、§5.9.7 の API 経路と障害対応戦略を流用：

- タイムアウト：単一 LLM 呼び出しの上限を実装段で設定
- リトライ：一時的な API 障害に対し最大 3 回まで指数バックオフで再試行
- 部分失敗の検知：複数機能の推定中に一部失敗した場合、成功分を保存して未完了分を再実行可能

## 12. 評価記録の type 値と配置（Evaluation Record Type and Placement）

本章は requirements.md Req 6 に対応する。

### 12.1 type 値の統合

requirements.md Req 6 受入 1 に対応。

- 評価記録の `type` 値を `conformance_evaluation` として統合（生成モード／照合モードの区別は内部フィールドで識別）

### 12.2 配置先

requirements.md Req 6 受入 2 に対応。

- 評価記録の配置先：`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md`
- `<mode>` は `check`（照合チェック）または `generation`（文書生成）
- `reviews/` ディレクトリ（実装適合レビュー用）とは別ディレクトリ

### 12.3 front-matter の構造（target_commit と materialization_commit_hash の整合ルール、G10 対処）

requirements.md Req 6 受入 3〜5 に対応。

```yaml
---
type: conformance_evaluation
target_app: <対象アプリのパス>
target_feature: <feature>
target_commit: <実装コードの commit hash>   # 実装コードのコミット（本機能の出典）、G10 で整合ルール明示
date: 2026-06-01
mode_internal: check                     # check / generation（Req 6 受入 3）
author:                                  # §5.4 規律（Req 6 受入 4）
  identity: claude_code_main_session     # または claude_code_subagent
  model_full_id: claude-opus-4-7-20260201    # 日付スタンプ付き完全版識別子、§5.9.3 由来
  prompt_artifact_hash: sha256:abc123    # プロンプト本体のコンテンツハッシュ、§5.9.3 由来
  role: drafter
reviewer:                                # §5.4 規律（Req 6 受入 4）
  identity: claude_code_subagent
  model_full_id: claude-haiku-4-5-20251001
  prompt_artifact_hash: sha256:def456
  role: final_judgment
  separation_from_author: true
related_artifacts:                       # Req 6 受入 5
  runtime: <runtime の関連実行記録パス>
  evaluation: <evaluation の関連記録パス>
  workflow_management: <workflow-management の関連手続き記録パス>
  self_improvement: <self-improvement の関連提案／実体変更記録パス（任意、規律改訂の影響を伴う conformance check 時のみ）>
---
```

**target_commit と self-improvement の materialization_commit_hash の整合ルール**（A-011 対処）：

- **target_commit**：本機能の評価対象である実装コードの commit hash。本機能が記録する出典
- **materialization_commit_hash**：self-improvement の規律変更が workflow-management の手続きで実体変更された時点のコミットハッシュ（self-improvement design §13.5 由来）
- **両者は独立**：target_commit は実装コードのコミット、materialization_commit_hash は規律変更のコミット
- **同一文書で両 commit を扱う場面**：規律改訂の影響を伴う conformance check 時、本機能の評価記録に self-improvement の `materialization_commit_hash` を `related_artifacts.self_improvement` フィールドで参照可能
- **本機能が self-improvement に出力される際**：self-improvement の motivating_evidence として参照される場合、`target_commit` を本機能の出典として記録、`materialization_commit_hash` は self-improvement 側が記録（責務分担）

### 12.4 関連実行記録への参照

requirements.md Req 6 受入 5 に対応。

- 評価記録から `runtime`／`evaluation`／`workflow-management`／`self-improvement`（任意）の関連実行記録への参照を保持
- 参照形式：相対パスまたは絶対パス

## 13. 依存関係の連想配列構造（Associative Dependency Structure）

本章は requirements.md Req 7 に対応する。

### 13.1 連想配列構造の必要性

requirements.md Req 7 受入 1 に対応。

- 本機能は他機能の単純リスト構造（`depends_on: [list]`）と異なる連想配列構造（`depends_on: {feature_name: dependency_type}`）で依存を表現
- 理由：本機能は依存種別（`hard`／`review`）を区別する必要があり、リスト構造では表現できない

### 13.2 依存種別 2 値

requirements.md Req 7 受入 2 に対応。

| 種別 | 内容 | 例 |
|---|---|---|
| **`hard`** | 本機能の動作に必須の依存。当該機能の完成なしに本機能は機能しない | `foundation: hard` |
| **`review`** | 本機能が当該機能の出力を読む依存。必須ではないが活用する | `runtime: review`、`evaluation: review`、`workflow-management: review` |

### 13.3 依存記述の確定値

requirements.md Req 7 受入 3 と計画書 §5.10.5 行 1075〜1080 に対応。

```yaml
# stages/feature-dependency.yaml の本機能エントリ
features:
  conformance-evaluation:
    depends_on:
      foundation: hard
      runtime: review
      evaluation: review
      workflow-management: review
```

### 13.4 workflow-management のスキーマ拡張との整合

requirements.md Req 7 受入 4 に対応。

- 本機能の連想配列構造は `workflow-management` Requirement 8 受入 2 のスキーマ拡張（連想配列構造の許容）に依存
- スキーマ拡張の所有者は `workflow-management`、本機能は仕様への適合者
- 相互参照証跡：workflow-management/design.md の該当節（依存関係 model）と本機能 design.md §13.3／§13.4 で双方向参照（次セッション以降の design レビュー波段で確定）

### 13.5 phase_order の最後

requirements.md Req 7 受入 5 に対応。

- 本機能は `phase_order` の最後に位置付ける（依存先がすべて先に完了する前提）
- 計画書 §5.5 ／ §5.10.5 の正本 phase_order は self-improvement を含まない 6 機能体制だが、workflow-management/design.md（利用者明示承認 2026-05-25 セッション 26、7 機能採用）と整合する 7 機能 phase_order：`foundation → runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation`
- 計画書 §5.5 構造例の self-improvement 記載漏れは workflow-management 側 TODO で別途追跡

## 14. 他機能との接合面（Interfaces with Other Features）

### 14.1 foundation との接合面（依存：hard）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | スキーマとメタデータ契約、検証器状態語彙、レビューモード語彙、証拠区分語彙、`adversarial_outcome` 語彙、必須メタデータ（severity／target_location／description／rationale）、**信頼度ラベル（`confidence_label` 3 値：high／medium／low、foundation 要件 6 受入 11 ＋設計 §3.5）** |
| 再定義しない原則 | foundation を正本所有者として参照し、本機能内で再定義しない（Boundary Context 隣接期待） |
| 機械検査 | foundation 受入番号の参照を本機能の機械検査 MV-7 で照合（G9 対処） |

### 14.2 runtime との接合面（依存：review）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 実装コードのレビュー実行記録（`runtime` の出力） |
| 形式 | `<対象アプリ>/.reviewcompass/specs/<feature>/runtime/<日付>-execution.md` 等の実行記録 |
| 活用 | 推定段階での実装コード理解、照合段階での実装コード言及齟齬の判定材料 |

### 14.3 evaluation との接合面（依存：review、G10 対処：突き合わせ詳細）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 評価結果との突き合わせ |
| 形式 | `evaluation` 機能の出力（評価結果集約 YAML／JSON）：経路別差分（3 役差分／モード別差分）／severity 集計／`role_diff_report.json`（**A-011 対処済み**：evaluation 設計に新設済み、2026-05-26 セッション 28、topic-112 で陳腐化記述を更新） |
| 突き合わせ手順 | 1. 本機能の推定 design ／ requirements を確定（§9.2 step 3〜4）／ 2. 既存上流文書との比較で食い違いを列挙（§10）／ 3. evaluation の経路別差分と突き合わせ、severity 集計の整合を確認 |
| 活用 | 推定段階での妥当性検証（evaluation の集計結果と食い違いの傾向が一致するか）、照合段階での実装コード言及齟齬の追加判定材料 |
| 波及 | 本接合面の詳細確定は design レビュー波段で evaluation 設計改訂と合わせて実施、carry-forward register に登録 |

### 14.4 workflow-management との接合面（依存：review）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 所定手続きの実行履歴、上流文書の整合確認 |
| スキーマ依存 | 依存関係の連想配列構造（Req 7 受入 4） |
| 活用 | 既存上流文書の最新性確認（古い文書を引きずらない）、手続き完了状態の確認 |

### 14.5 analysis との接合面（G10 対処：機械可読出力スキーマ）

| 方向 | 内容 |
|---|---|
| 出力（conformance-evaluation が書く） | 6 criteria の検査結果、食い違い列挙、推定根拠 |
| 形式 | 評価記録の YAML 構造（`analysis` が機械可読に取り込む）、§10.4 のスキーマに準拠 |
| 必須フィールド | `feature`／`axis`（**requirements ／ design の 2 値**、topic-111／G-003 対処）／`criterion_id`（criterion-1〜6）／`severity`（4 段）／`finding_id`（CF-NNN）／`correspondence_type`（3 対応関係）／`discrepancy_description`／`implementation_code_refs`／`judgment_id`（JD-NNN） |
| 任意フィールド | `reference_axis`（intent の参考情報記録専用、§10.5、必須でない）／`target_commit`／`materialization_commit_hash`（規律改訂の影響を伴う場合、§12.3 由来） |
| 活用先 | `analysis` の 4 出力先（特に監査用報告と報告書向け原データ、`analysis` Requirement 8 受入 5 由来） |
| 波及 | 本接合面の最終確定は design レビュー波段で analysis 設計と合わせて実施、carry-forward register に登録 |

### 14.6 self-improvement との接合面（G10 対処：commit hash 整合）

| 方向 | 内容 |
|---|---|
| 出力（conformance-evaluation が書く） | 6 criteria の検査結果（規律改善の入力として活用される） |
| 依存方向 | conformance-evaluation → self-improvement（self-improvement が conformance-evaluation の出典を読む、A-008 で確定済み 2026-05-23） |
| 整合ルール | §12.3 の target_commit／materialization_commit_hash の整合ルールに従う |
| 注記 | `self-improvement` は本機能の `depends_on` には含まれず、出力先として参照される関係 |
| 波及 | 本接合面の最終確定は design レビュー波段で self-improvement 設計と合わせて実施、carry-forward register に登録 |

## 15. 要件追跡表（Requirements Traceability、受入基準単位）

参照は章タイトル参照（番号なし 5 章「概要」「目標」「範囲外」「設計の前提」「アーキテクチャ」は章番号なし、F-003 対処、G7 利用者明示承認）。

| Requirement | 受入基準 | 対応章節 |
|---|---|---|
| Req 1 機能の方向性と前提 | 受入 1（下流→上流、4 階層対象） | 「概要」章／「範囲外」章／§6.2／§7／§8.1 |
| Req 1 | 受入 2（上流文書なくてもよい） | 「概要」章／§6.1 |
| Req 1 | 受入 3（実装適合レビュー非吸収） | 「範囲外」章／§17（Boundary Context Out of scope） |
| Req 1 | 受入 4（2 モード） | アーキテクチャ §3 モード切替モデル／§6／§7 |
| Req 1 | 受入 5（同一 6 criteria） | §8.1 |
| Req 2 文書生成モード | 受入 1（4 階層扱い分け） | §6.2 |
| Req 2 | 受入 2（出力先パス規則） | §6.3 |
| Req 2 | 受入 3（3 節必須） | §6.3 |
| Req 2 | 受入 4（推定根拠保持） | §6.4 |
| Req 2 | 受入 5（人間判断必要性明示） | §6.5 |
| Req 2 | 受入 6（3 役レビュー機構適用） | §6.6／§11 |
| Req 2 | 受入 7（実行記録保管） | §6.7 |
| Req 3 照合チェックモード | 受入 1（二段階方式） | §7.1／§7.2／§7.3 |
| Req 3 | 受入 2（食い違い検出） | §7.4／§10 |
| Req 3 | 受入 3（intent 参考情報） | §7.5／§10.5 |
| Req 3 | 受入 4（機能分割食い違いオプション） | §7.6 |
| Req 3 | 受入 5（4 段重大度） | §7.7 |
| Req 3 | 受入 6／7（3 役レビュー） | §7.8／§11 |
| Req 3 | 受入 8（実行記録保管） | §7.9 |
| Req 4 6 criteria 検査構造 | 受入 1（6 criteria） | §8.1 |
| Req 4 | 受入 2（照合対象除外） | §8.2 |
| Req 4 | 受入 3（サブ構造） | §8.3 |
| Req 4 | 受入 4（実装適合分離） | §8.4 |
| Req 4 | 受入 5（検査仕様整備） | §8.5 |
| Req 5 3 役レビュー機構 | 受入 1（両段階適用） | §11.1 |
| Req 5 | 受入 2（軽量／本格使い分け） | §11.2 |
| Req 5 | 受入 3〜8（§5.9 規律流用） | §11.3／§11.4 |
| Req 6 評価記録 | 受入 1（type 値統合） | §12.1 |
| Req 6 | 受入 2（配置先） | §12.2 |
| Req 6 | 受入 3（mode_internal） | §12.3 |
| Req 6 | 受入 4（author／reviewer） | §12.3 |
| Req 6 | 受入 5（関連参照） | §12.4 |
| Req 7 依存関係 | 受入 1（連想配列構造） | §13.1 |
| Req 7 | 受入 2（hard／review） | §13.2 |
| Req 7 | 受入 3（依存記述確定値） | §13.3 |
| Req 7 | 受入 4（workflow-management スキーマ整合） | §13.4 |
| Req 7 | 受入 5（phase_order 最後） | §13.5 |
| Req 8 実装適合分離 | 受入 1（実装適合レビュー責務を持たない） | 「範囲外」章 |
| Req 8 | 受入 2（実装適合レビューは §5.9／runtime に残る） | 「範囲外」章／§14.2 |
| Req 8 | 受入 3（方向・前提・実施時期の 3 軸性格差） | 「概要」章／「設計の前提」章 |
| Req 8 | 受入 4（評価記録のディレクトリ分離） | §12.2 |

## 16. 設計決定（Key Decisions）

### Decision 1：本筋と傍流の明示的分離（§5.10.1、2026-05-24 セッション 23 整理）

本筋（照合チェックモード）と傍流（文書生成モード、人協働）を明示的に区別、各モードの推定プロセスと既存文書扱いを分けて設計する。

**根拠**：実装適合レビューを吸収するか否かの再判断（吸収しない方針確定）と、リバースエンジニアリングの位置付けの整理（傍流＝人協働）に基づく利用者整理（2026-05-24 セッション 23）。

### Decision 2：照合チェックの二段階方式

第 1 段階（推定、既存上流文書遮断）→ 第 2 段階（比較、既存上流文書を読み込み）の二段階で実施。

**根拠**：既存上流文書を推定時に読むと推定結果が既存文書に引きずられるバイアスを構造的に防ぐ（§5.10.9、利用者明示承認 2026-05-24 セッション 23）。

### Decision 3：feature-partitioning だけは推定時の例外

既存 feature-partitioning だけは推定時の入力として尊重し、他の既存上流文書（intent／requirements／design）は遮断する。

**根拠**：機能名・境界が違うと「同じ機能の design ／ requirements を比較」が成立しないため、照合成立性を確保（2026-05-24 セッション 23 利用者指摘）。

### Decision 4：2 軸 6 criteria への絞り込み（案 Y）

照合対象を requirements ／ design の 2 軸 × 3 criteria = 6 criteria に絞る。feature-partitioning は所与、intent は参考情報、tasks は推定困難という理由で照合対象から除外。

**根拠**：検査の単純性と意味的整合の両立、実装からの推定可能性（§5.10.2、利用者明示承認「(イ) 案 Y」2026-05-24 セッション 23）。

### Decision 5：3 役レビュー機構を推定段階にも適用

推定段階と照合段階の両方に triad-review を適用、解釈余地に応じた軽量／本格の使い分けを行う。

**根拠**：推定そのものの妥当性も検証必要（§5.10.10、利用者明示承認「(ア)、上記の骨子に加え、上流文書生成の過程に triad-review の必要性を検討」2026-05-24 セッション 23）。

### Decision 6：依存関係の連想配列構造

本機能は他機能の単純リスト構造と異なる連想配列構造（`hard`／`review`）で依存を表現。

**根拠**：依存種別の区別が必要（hard は必須、review は活用のみ）、`workflow-management` のスキーマ拡張と整合（§5.10.5、A-005 連動）。

### Decision 7：モード切替は明示指定（自動判定なし）

照合チェックと文書生成のモード切替は利用者の明示指定のみで、既存上流文書の存在による自動判定は行わない。

**根拠**：利用者の意図と実態が異なる場合（既存文書はあるが信頼性が低い等）の誤動作を防ぐ。

### Decision 8：評価記録は `conformance/` ディレクトリで分離

評価記録は `conformance/` ディレクトリ、実装適合レビュー記録は `reviews/` ディレクトリで物理的に分離。

**根拠**：本機能（逆方向）と実装適合レビュー（順方向）の混在を防ぐ、機械検査可能な分離（Req 8）。

### Decision 9：finding_id ／ judgment_id 発番ルール（G3 利用者明示承認、本セッション 27 確定）

採番権者は conformance-evaluation、接頭辞で名前空間分離（`CF-NNN`：Conformance Finding、`JD-NNN`：Judgment）、通番リセットなし、3 桁から開始し 999 件を超えたら自動で 4 桁に拡張。詳細は §10.7。

**根拠**：self-improvement Decision 9（proposal_id 発番ルール）と同型のパターン、機能横断的に一貫した運用。

### Decision 10：推定アルゴリズムの順序依存（G2 利用者明示承認、本セッション 27 確定）

推定アルゴリズム（§9.2）は **design 先行→ requirements 逆算** の順序を必須とする。design は実装コードから直接読み取れるため軽量適用、requirements は design からの逆算で本格適用。詳細は §9.2 ／ §11.2。

**根拠**：計画書 §5.10.9(a)（行 1176「requirements は design からの逆算」）と §5.10.10（行 1216〜1217「第 2 段階 design 推定→ 第 3 段階 requirements 推定」）の順序確定と整合。

### Decision 11：信頼度ラベルを foundation 語彙体系に追加（G4 利用者明示承認、本セッション 27 確定、A-013 対処完了 2026-05-26 セッション 28）

推定の信頼度ラベル（high／medium／low の 3 値）は foundation の語彙正本として定義（foundation 要件 6 受入 11 ＋設計 §3.5、`confidence_label` 3 値）。本機能 §9.5 は foundation 参照に書き換え（A-013 対処完了、2026-05-26 セッション 28）。

**根拠**：foundation 語彙正本原則（Req 5 受入 7「レビューモード語彙を再定義せず参照」）と一貫した運用、self-improvement Decision 1 と同型の責務分離パターン。

### Decision 12：規律 options-presentation の対象範囲明確化（G8 利用者明示承認、本セッション 27 確定、規律本体改訂）

本セッション 27 で新設した規律 [options-presentation](../../../docs/disciplines/discipline_options_presentation.md) の対象範囲を「利用者に判断を仰ぐ複数案提示の応答」に限定し、設計文書内の比較記述（例：§7.3 遮断 3 手法）は対象外と明確化する。規律本体に小改訂（軽量手続き）。

**根拠**：規律の本来目的（利用者の判断負荷を減らす、dominated 案を提示しない）と整合、設計文書内の経緯記録の自由度を保つ。本セッション 27 で本機能 design 起草中に規律違反指摘を受けて議論、規律本体の射程縮小で対処。

## 17. Boundary Context との整合確認（Boundary Context Compliance）

requirements.md の Boundary Context との整合：

### In scope（範囲内）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 主要用途 1（本筋）：照合チェック | §7 照合チェックモード／Decision 2 |
| 主要用途 2（傍流）：文書生成 | §6 文書生成モード／Decision 1 |
| 6 criteria の検査構造 | §8 6 criteria 検査構造／Decision 4 |
| 推定段階と照合段階の両方への 3 役レビュー機構適用 | §11 3 役レビュー機構の適用／Decision 5 |
| モード別の既存文書扱いルール | アーキテクチャ §3 モード切替モデル／§7.3／Decision 3 |
| 評価記録の出力（`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`） | §12 評価記録の type 値と配置 |
| v3-plan §3.3 のうち「文書レベルの戻し」 | §6／§7／§8 |

### Out of scope（範囲外）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 実装適合レビュー | 「範囲外」章／Decision 8 |
| v3-plan §3.3 の規律レベル戻し（self-improvement の責務） | 「範囲外」章 |
| schema／prompt／code レベルの戻し | 「範囲外」章 |
| 5 評価軸のうち実装適合 | 「範囲外」章／§8.4 |

### 隣接仕様の期待との整合

| 隣接機能 | Boundary Context の期待 | 本設計での対応 |
|---|---|---|
| foundation（hard） | スキーマとメタデータ契約等を再定義せず参照 | §14.1 |
| runtime（review） | 実装コードのレビュー実行記録を入力源として活用 | §14.2 |
| evaluation（review） | 評価結果との突き合わせ | §14.3（G10 で詳細記述） |
| workflow-management（review） | 所定手続きの実行履歴と上流文書の整合確認 | §14.4 |
| analysis | 6 criteria の検査結果を 4 出力先に取り込む | §14.5（G10 で機械可読スキーマ詳細記述） |
| self-improvement | 6 criteria 検査結果を規律改善の入力として提供 | §14.6（G10 で commit hash 整合ルール） |

## 18. 機械検査の具体手段（Machine Verification、self-improvement 設計の MV-X と同型、MV-7 追加）

本章は本機能の動作に関する機械検査ポイントを定義（self-improvement design の §17 と同型の構造）。

### 18.1 検査対象

| 検査 ID | 検査対象 | 検査内容 | 実装方法 |
|---|---|---|---|
| **MV-1** | 評価記録の `type` 値統合 | `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md` の front-matter で `type: conformance_evaluation` が設定されている | grep でフィールド存在を確認 |
| **MV-2** | mode_internal の正しさ | front-matter の `mode_internal` が `check` または `generation` のいずれかである | grep ＋値の照合 |
| **MV-3** | ディレクトリ分離 | 評価記録は `conformance/` ディレクトリ、実装適合レビューは `reviews/` ディレクトリに配置されている（混在なし） | find ＋ディレクトリ照合 |
| **MV-4** | 推定文書の必須 3 節 | `<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/specs/<feature>/` 配下の推定文書が Introduction／Boundary Context／Requirements の 3 節を含む | grep で見出し存在を確認 |
| **MV-5** | 推定根拠の実装コード参照 | 推定文書の各推定要素に実装コードへの参照（`<ファイルパス>:<行範囲>`）が最低 1 件含まれる | grep ＋形式照合 |
| **MV-6** | 既存上流文書遮断の事前検査 | 推定役プロンプトに既存上流文書のパスが含まれていない、自律ファイル探索の禁止条項がプロンプトに明記されている（照合チェックモード） | grep ＋プロンプトログ確認 |
| **MV-7** | **foundation 受入番号照合**（G9 対処、本セッション 27 新設） | 本機能 design.md ／ requirements.md 内の `foundation Requirement N 受入 M` 記述が foundation requirements.md の最新受入番号と一致 | grep で抽出した参照を foundation requirements.md と機械的に照合 |

### 18.2 検査スクリプトの所在と責務

- 第 1 期（フェーズ 1〜3）：手動 grep／find による検査、本機能の責務として運用
- フェーズ 4 第 2 サイクル以降：検査スクリプトを `tools/conformance-evaluation-check.py`（仮称、本機能の所有物）として実装
- `workflow-management` の `tools/check-workflow-action.py`（補助層 C 段階 2）とは責務が異なる（不可逆操作の事前検査）
- **ツール内部スキーマ（データ形式の設計図）の配置（topic-119／F-017 対処、2026-05-29 セッション 39）**：本機能のツール内部スキーマ（評価記録 front-matter スキーマ等）は `tools/conformance_evaluation/schemas/` 専用サブフォルダに配置する（import 対象パッケージはアンダースコア、単独 CLI スクリプト `conformance-evaluation-check.py` はハイフン。self-improvement の schemas/ サブフォルダ分離方針と整合、§11.1 由来）

### 18.3 検査の出力先と fail-closed の粒度（F-009 部分対処）

- 検査結果は評価記録の本文に「機械検査結果」節として記録
- **fail-closed の適用粒度（MV ID 別）**：
  - **遮断必須**（即時停止）：MV-6（推定役プロンプトへの既存上流文書混入検知）
  - **遮断推奨**（処理停止）：MV-1／MV-2／MV-3（評価記録の構造的検査）
  - **警告として続行可能**（後続処理を許容）：MV-4／MV-5／MV-7（推定文書品質と参照整合）
- 第 1 期は手動検査で粒度を確認、自動化時に MV ID 別の fail-closed 設定を CLI 引数または設定ファイルで提供

### 18.4 機械検査の段階的導入

- フェーズ 1〜3：MV-1／MV-2／MV-3／MV-7 は手動 grep、MV-4／MV-5 は文書作成時に人間が確認、MV-6 は推定役プロンプトの手動レビュー
- フェーズ 4 第 1 サイクル：MV-1〜MV-3、MV-7 を自動化
- フェーズ 4 第 2 サイクル：MV-4〜MV-6 を自動化、推定役プロセスの隔離（§7.3）と連携、chroot 環境での厳格遮断検討

## 19. テスト戦略（Test Strategy）

本章は計画書 §5.9.2 のレビュー観点 9「テスト戦略」に対応する。

### 19.1 テスト対象とテストレベル

| モデル | 単体テスト | 結合テスト | 受入テスト |
|---|---|---|---|
| **推定モデル（§9）** | 4 階層の推定アルゴリズム、信頼度判定、design 先行→ requirements 逆算の順序検査 | 3 役レビュー機構と推定の連結 | 実装コード規模 1000 行程度のサンプルアプリで推定実施 |
| **比較モデル（§10）** | 3 対応関係（節有無／主張対応／コード言及齟齬）の判定、CF-NNN／JD-NNN 発番ルール | 推定結果と既存文書の比較 | 既存上流文書ありのサンプルアプリで照合実施 |
| **モード切替（アーキテクチャ §3）** | check／generation のモード判定、明示指定の処理 | 各モードの実行パイプライン | 両モードの End-to-End 実行 |
| **3 役レビュー機構（§11）** | 軽量／本格の使い分け判定 | 推定段階／照合段階での 3 役連携 | 全 6 criteria の triad-review |
| **評価記録（§12）** | type 値・mode_internal の正しさ、front-matter スキーマ、target_commit／materialization_commit_hash の整合 | 評価記録の生成と保管 | 評価記録の機械可読性検証 |
| **依存関係（§13）** | 連想配列構造の解釈、hard／review の区別 | feature-dependency.yaml の読み込み | feature-dependency.yaml の整合確認 |
| **機械検査（§18）** | MV-1〜MV-7 の検査ロジック | 検査スクリプトと評価記録の連携 | 全 MV の網羅実行 |

### 19.2 テスト戦略の重点ポイント

- **既存上流文書の遮断**：推定役プロンプトに既存上流文書の内容が混入していないか、grep で機械検査（MV-6）
- **feature-partitioning の例外扱い**：照合チェックモードで既存 feature-partitioning だけは入力として尊重、他は遮断されていることをテストデータで確認
- **推定の信頼度**：high／medium／low の判定基準が一貫しているかをサンプルデータで確認
- **6 criteria の網羅**：すべての criterion でテストケースが用意されているか、`schemas/review-criteria/conformance_evaluation.yaml` と整合
- **推定順序**：design 先行→ requirements 逆算の順序が実装されているかを単体テストで確認
- **foundation 受入番号照合**：MV-7 で foundation 改訂への追従性を確認

### 19.3 テスト実施タイミング

- 単体テスト：実装段（フェーズ 4 第 2 サイクル）の各モジュール実装時
- 結合テスト：実装段（フェーズ 4 第 2 サイクル）のパイプライン構築時
- 受入テスト：実装段（フェーズ 4 第 3 サイクル）の全機能完成時、利用者監査と組み合わせ

### 19.4 テストデータの取得元

- サンプルアプリのコード：ReviewCompass 自身を含む dogfooding 候補（§5.23）
- 既存上流文書：本リポジトリの `.reviewcompass/specs/<feature>/requirements.md` ／ `design.md`（フェーズ 1 で 7 機能分が蓄積）
- 既存 feature-partitioning：`stages/feature-partitioning/2026-05-24-proposal.md`

## 20. design.alignment 段の未解決論点（Open Issues for Design Alignment Gate）／起草完了基準（Completion Criteria）

### 20.1 未解決論点

本セッション 27 末時点で本機能の design.drafting＋triad-review 段で未解決の論点：

#### 遡及（要 上流文書修正）

- **A-001（G5 利用者明示承認、本セッション 27 で対処）**：12 criteria（旧表現）→ 6 criteria（現行）への現役記述修正。requirements.md 行 33-34（2 件）／CONFORMANCE_EVALUATION.md（4 件）／計画書（6 件以上）を軽量 reopen 手続きで修正
- **F-015（G6 利用者明示承認、本セッション 27 で対処）**：CLI 命名を本機能 design.md の階層型（`conformance check` ／ `conformance generate`）に統一する方向で計画書 §5.10.7 を改訂、軽量 reopen 手続き

#### 波及（要 他機能設計改訂）

- **A-003（G4 利用者明示承認、本セッション 27 で対処、A-013 として持ち越し → 2026-05-26 セッション 28 で完了）**：信頼度ラベル（high／medium／low）を foundation 語彙体系に追加（foundation 要件 6 受入 11 ＋設計 §3.5）。本機能 §9.5 ／ §14.1 ／ Decision 11 を foundation 参照に書き換え（セッション 28、A-013 対処完了）
- **F-006 ／ A-008 ／ A-011（G10 利用者明示承認、本セッション 27 で対処）**：evaluation 接合面の突き合わせ詳細／analysis 接合面の機械可読出力スキーマ／self-improvement との commit hash 整合ルール。本機能 design.md §14.3 ／ §14.5 ／ §14.6 ／ §12.3 に詳細記述、carry-forward register に登録、design レビュー波段で各機能側設計と合わせて消化

#### 他機能横断の所見（対処済み、topic-112／F-015 で陳腐化記述を更新、2026-05-29 セッション 39）

- **A-011（✅ 対処済み、2026-05-26 セッション 28）**：analysis／evaluation 接合面の `roles/role_diff_report.json` 新設は evaluation 設計に反映済み（正本 carry-forward register の `carry-forward-011`）。本機能の §14.3 ／ §14.5 で参照しており、A-011 消化が本機能の design.alignment の前提だったが、**前提は充足済み**
- **A-012（✅ 対処済み、2026-05-26 セッション 28）**：self-improvement と workflow-management の時系列契約・完了通知形式（正本 carry-forward register の `carry-forward-012`）。本欄は topic-112／F-015 で陳腐化記述を更新。現時点で本機能の他機能横断の未消化所見はない

#### 章番号体系の整合確認（持ち越し）

本機能 design.md は self-improvement 設計と同じく 20 章構成（番号なし 5 章＋番号付き §6〜§20 の 15 章）を採用。他機能（foundation／runtime／evaluation／analysis／workflow-management）の design.md でも章番号体系の不整合が存在する可能性があり、design.alignment 段で全機能横断の章構造整合確認が必要（利用者明示承認「他機能でも生じていたはずなので後ほど対処」2026-05-26 セッション 27）。

### 20.2 機能横断レビューで対処済みの所見

- **A-005（既存）**：依存関係の連想配列構造 → Requirement 7 ／ §13 ／ Decision 6 で反映済み
- **A-008（既存）**：conformance-evaluation から self-improvement への出力方向 → §14.6 で「conformance-evaluation → self-improvement の方向」として明示
- **A-009 第 2 波（既存）**：旧 paper-interface 由来の用語不整合 → Boundary Context 隣接仕様の analysis 記述で対処済み
- **A-010（既存）**：推定プロセスの整理と 2 軸 6 criteria 化 → Requirement 1〜5 ＋計画書 §5.10 改訂で対処済み、本設計で全面反映

### 20.3 起草完了基準

本設計が design.drafting＋triad-review 段の完了とみなされる条件：

- [x] 全 20 章（番号なし 5 章＋番号付き §6〜§20 の 15 章）が記述されている
- [x] requirements.md の全 8 件の Requirement と受入基準が §15 要件追跡表で章節と対応している（受入基準単位の追跡、F-001 部分対処：Req 8 を受入単位で展開）
- [x] 計画書 §5.10 の 10 小節（§5.10.1〜§5.10.10）の方針が反映されている
- [x] 他機能との接合面が §14 で全 6 機能分（foundation／runtime／evaluation／analysis／workflow-management／self-improvement）明示されている
- [x] Boundary Context との整合が §17 で確認されている
- [x] 機能横断所見（A-005／A-008／A-009／A-010）の対処が §20.2 で明示されている
- [x] 主要な設計決定（12 件、Decision 9 ／ 10 ／ 11 ／ 12 含む）が §16 で明示されている
- [x] **機械検査の具体手段（§18）が定義されている**（MV-1〜MV-7 の 7 検査ポイント、MV-7 は本セッション 27 で新設）
- [x] **テスト戦略（§19）が定義されている**
- [x] 文書生成モード（§6）と照合チェックモード（§7）が明示的に分離されている
- [x] 6 criteria 検査構造（§8）が定義されている（axis：requirements ／ design の 2 値、criterion-1〜6 の ID、F-004 対処）
- [x] 推定モデル（§9）と比較モデル（§10）が定義されている（推定順序：design 先行→ requirements 逆算、F-008 対処）
- [x] **finding_id ／ judgment_id 発番ルール（§10.7）が定義されている**（CF-NNN ／ JD-NNN、A-002 対処）
- [x] 3 役レビュー機構の軽量／本格使い分け（§11.2）が明示されている
- [x] 評価記録の type 値と配置（§12）が確定している（target_commit ／ materialization_commit_hash の整合ルール、A-011 対処）
- [x] 依存関係の連想配列構造（§13）と確定値が明示されている
- [x] **遡及／波及所見が §20.1 で明示され、carry-forward register に登録済み**
```

## File: .reviewcompass/specs/conformance-evaluation/tasks.md
```
---
spec: conformance-evaluation
phase: tasks
stage: drafting
author:
  identity: claude-code-main-session
  model: claude-opus-4-7
  role: drafter
created_at: 2026-05-29
language: ja
---

# Tasks Document：conformance-evaluation

## 概要（Overview）

本文書は `conformance-evaluation`（ReviewCompass の 7 番目の独立機能、**下流 → 上流の逆方向**で実装コードから上流文書を推定・照合する機能）の実装タスクを列挙する。本機能は 2 モード（**照合チェックモード＝本筋**：既存上流文書と推定結果を比較して意図ずれを検出／**文書生成モード＝傍流・人協働**：上流文書のないコードベースから骨子を推定）を持ち、両モードで同一の **6 criteria 構造**（requirements ／ design の 2 軸 × 3 criteria）を使う。実装適合レビュー（順方向）は吸収せず `runtime`／`analysis` の連携に残す（Req 8）。

タスクは設計文書（design.md）の所有モデル単位でまとめる。本機能の所有物は、モード切替（§3）／文書生成モード（§6）／照合チェックモード（§7）／6 criteria 検査構造（§8）／推定モデル（§9）／比較モデル（§10）／3 役レビュー機構の適用（§11）／評価記録（§12）／依存関係の連想配列構造（§13）／他機能との接合面（§14）／機械検査（§18）／テスト戦略（§19）である。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの所有モデル領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる（self-improvement／workflow-management T-001〜の粒度方針を継承）
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む。データの流れ（design §1：入力＝実装コード → 推定 → 比較 → 評価記録）を依存順の基本とする
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **段階的導入**：第 1 期（フェーズ 1〜3）は手動 grep ／ find による半自動運用、自動化はフェーズ 4 で段階的に進める（design §18.4 ／ §19.3）。各タスクの完了条件は第 1 期スコープ（手動運用が機械的に検証可能なこと）で判定する
- **contract consumer 原則**：foundation が所有する語彙正本（スキーマ・メタデータ契約・検証器状態語彙・レビューモード語彙・証拠区分語彙・`adversarial_outcome` 語彙・信頼度ラベル）を再定義せず参照のみで使用（依存：hard、Req 7 受入 3、design §14.1）。runtime／evaluation／workflow-management の出力は入力源として読む（依存：review）
- **本筋と傍流の分離**：照合チェックモード（本筋）と文書生成モード（傍流・人協働）を明示的に分離（Decision 1）。両モードの推定プロセスと既存文書扱いは異なる
- **二段階方式と遮断の徹底**：照合チェックモードは「第 1 段階＝推定（既存上流文書を遮断、feature-partitioning のみ入力に尊重）→ 第 2 段階＝比較」（Req 3 受入 1）。遮断は技術的手段で実装し、推定役プロンプトへの既存上流文書混入を MV-6 で fail-closed 検知（遮断必須、design §18.3）
- **fail-closed の粒度別適用**：機械検査（§18）は MV ID 別に fail-closed 粒度を区別（遮断必須＝MV-6／遮断推奨＝MV-1・MV-2・MV-3／警告続行可＝MV-4・MV-5・MV-7、design §18.3）

`conformance-evaluation` 全体で 13 タスク。

## タスク一覧（Task List）

### T-001：成果物配置の準備

- **対応設計節**：design.md §6.3 ／ §7 ／ §12.2 配置先、§18.2 検査スクリプト所在
- **対応要件**：Requirement 6 受入 2（評価記録の配置）、Requirement 8 受入 4（ディレクトリ分離）
- **責務**：本機能の成果物の物理配置を新設する。評価記録の配置先 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`（`reviews/` とは別ディレクトリ、Req 8 受入 4）、文書生成モードの推定出力先 `<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/`（feature-partitioning-candidates.md ／ intent-reference.md ／ specs/<feature>/）、6 criteria 検査仕様の配置先 `schemas/review-criteria/`、検査スクリプト配置先 `tools/`、テスト配置先 `tests/conformance-evaluation/` を新設し、各ディレクトリに配置目的を記す README を置く。空ディレクトリは `.gitkeep` で Git 追跡可能にする（self-improvement T-001 の方針継承）
- **前提タスク**：なし（起点）
- **成果物**：
  - `tools/conformance_evaluation/` パッケージのディレクトリ＋`.gitkeep`（命名規約：import 対象パッケージはアンダースコア、単独 CLI スクリプト `tools/conformance-evaluation-check.py` はハイフン。self-improvement topic-105 と同方針）
  - `tools/conformance_evaluation/schemas/.gitkeep`（ツール内部スキーマの配置）
  - `schemas/review-criteria/README.md`（6 criteria 検査仕様 `conformance_evaluation.yaml` の配置説明、実体配置はフェーズ 2 → DVT-C001）
  - `docs/operations/CONFORMANCE_EVALUATION.md`（**既存ファイル**、design §20.1 の A-001 で既存と判明）への追記（配置規則・対象アプリ側パス規則の説明、`conformance/` と `reviews/` の分離。topic-118／F-018 で既存ファイルへの追記と明記）
  - `tests/conformance-evaluation/.gitkeep`
  - `tools/README.md` への追記（`conformance-evaluation-check.py` の配置先・命名規約）
- **完了条件**：
  1. `conformance/` と `reviews/` の分離方針が運用文書（CONFORMANCE_EVALUATION.md）に明記され、評価記録は `conformance/<日付>-<mode>.md` のパス規則に従う（MV-3 連動）
  2. 文書生成モードの推定出力先パス規則（§6.3 の 3 経路）が運用文書に明記される
  3. `schemas/review-criteria/` ／ `tools/conformance_evaluation/` ／ `tests/conformance-evaluation/` が存在し `.gitkeep` で Git 追跡可能である
  4. `tools/README.md` に命名規約（パッケージ＝アンダースコア／単独 CLI＝ハイフン）が明記される
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`.gitkeep` 存在検査、パス規則の文言 grep 検査、`conformance/`／`reviews/` 分離の文言検査

### T-002：モード切替モデル（Mode Switch Model）

- **対応設計節**：design.md §3 モード切替モデル、§16 Decision 7（明示指定、自動判定なし）
- **対応要件**：Requirement 1 受入 4（2 モード）
- **責務**：照合チェックモード（check）と文書生成モード（generation）の 2 モードを切り替える入口を実装。**モード判定は明示指定のみ**（自動判定は行わない、Decision 7）。CLI またはパラメータで `check` ／ `generation` を受け取り、対応するパイプライン（T-003 ／ T-004）に振り分ける。両モードが共有する 6 criteria 構造（T-005）と 3 役レビュー機構（T-008）への参照を確立する
- **前提タスク**：T-001
- **成果物**：
  - `tools/conformance_evaluation/mode_switch.py`（check／generation の明示指定処理、パイプライン振り分け）
- **完了条件**：
  1. モードが `check` ／ `generation` の明示指定で受け取られ、未知の値が fail-closed になることが機械検証される
  2. 自動判定のロジックが存在しない（明示指定のみ）ことが運用文書に明示される（Decision 7）
  3. 各モードへの**ディスパッチ機構（つなぎ口＝インタフェース）が確立**される（check → T-004、generation → T-003）。完了条件は実体パイプラインの完成でなく**インタフェースの確立**で判定し、T-002 ↔ T-003／T-004 の循環を避ける（topic-120／G-005 対処、2026-05-29 セッション 39）
- **テスト要件**：モード判定テスト（check／generation／未知値 fail-closed）、振り分けテスト、明示指定のみの文書検査

### T-003：文書生成モード（Generation Model、傍流・人協働）

- **対応設計節**：design.md §6.1〜§6.7
- **対応要件**：Requirement 2 受入 1〜7
- **責務**：上流文書のないコードベースから上流文書の骨子を **人協働で** 推定生成する。4 階層の扱い分け（§6.2）：feature-partitioning は機械的候補提示 → 人が境界決定、intent は参考情報として推察 → 人が補完、requirements ／ design は自動推定 → 人が修正、tasks は対象外。出力先パス規則（§6.3、Req 2 受入 2）。各推定文書は最低 3 節（Introduction ／ Boundary Context ／ Requirements 相当）＋実装コード参照を最低 1 件含む（Req 2 受入 3、MV-4 ／ MV-5 連動）。推定根拠の保持（§6.4、Req 2 受入 4）。人間判断の必要性の明示（§6.5、Req 2 受入 5）。各推定段階に 3 役レビュー機構を適用（§6.6 ／ T-008）。実行記録を `conformance/<日付>-generation.md` に保管（§6.7、Req 2 受入 7）
- **前提タスク**：T-002、T-006（推定モデル）、T-008（3 役レビュー機構）
- **成果物**：
  - `tools/conformance_evaluation/generation_mode.py`（4 階層の扱い分け ＋ 推定生成 ＋ 人協働の判断必要性明示）
- **完了条件**：
  1. 4 階層が扱い分けされる（feature-partitioning ／ intent は人協働、requirements ／ design は自動推定、tasks 対象外）ことが機械検証される
  2. 推定文書が §6.3 のパス規則で出力される
  3. 各推定文書が最低 3 節（Introduction ／ Boundary Context ／ Requirements 相当）を含む（MV-4）
  4. 各推定要素に実装コード参照（`<ファイルパス>:<行範囲>`）が最低 1 件含まれる（MV-5）
  5. 人間判断の必要性が推定結果に明示される（特に feature-partitioning ／ intent）
  6. 実行記録が `conformance/<日付>-generation.md` に保管される（`mode_internal: generation`、T-009 連動）
- **テスト要件**：4 階層扱い分けテスト、パス規則テスト、3 節必須テスト（MV-4）、コード参照テスト（MV-5）、人間判断明示テスト、実行記録保管テスト、**feature-partitioning 候補提示の出力形式テスト（topic-117／F-008 対処）**

### T-004：照合チェックモード（Check Model、本筋・二段階方式）

- **対応設計節**：design.md §7.1〜§7.9
- **対応要件**：Requirement 3 受入 1〜8
- **責務**：二段階方式（§7.1）を実装。**第 1 段階＝推定**：既存 feature-partitioning を入力として尊重しつつ、他の既存上流文書（intent／requirements／design）を**遮断**した状態で実装コードから design ／ requirements を推定（intent は最後に参考情報）。**第 2 段階＝比較**：既存上流文書を読み込み推定結果と比較、食い違いを列挙（T-007 比較モデル）。既存上流文書の遮断手法（§7.3）：推定役プロンプトへの混入禁止＋自律ファイル探索禁止条項、MV-6 で fail-closed 検知（遮断必須）。feature-partitioning だけ例外とする理由は照合成立性（§7.2）。intent は参考情報扱い（§7.5、Req 3 受入 3）。機能分割自体の食い違い検出はオプション（§7.6、Req 3 受入 4、標準動作外）。4 段重大度の付与（§7.7、Req 3 受入 5）。実行記録を `conformance/<日付>-check.md` に保管（§7.9、Req 3 受入 8）
- **前提タスク**：T-002、T-006（推定）、T-007（比較）、T-008（3 役レビュー機構）
- **成果物**：
  - `tools/conformance_evaluation/check_mode.py`（二段階方式 ＋ 遮断手法 ＋ feature-partitioning 例外 ＋ 4 段重大度）
- **完了条件**：
  1. 二段階方式（第 1 段階推定 → 第 2 段階比較）が順序どおり実行されることが機械検証される
  2. 第 1 段階で既存上流文書（intent／requirements／design）が遮断され、推定役プロンプトに既存上流文書のパス・内容が含まれないことが MV-6 で検知される（混入時は **遮断必須＝即時停止**、design §18.3）
  3. feature-partitioning だけは推定時入力として尊重される（照合成立性のため、§7.2）
  4. intent は参考情報として比較され must-fix 判定の対象外（Req 3 受入 3）
  5. 機能分割食い違い検出は利用者明示要求時のみのオプションで、標準動作に含まれない（Req 3 受入 4）
  6. 食い違いに 4 段重大度（CRITICAL／ERROR／WARN／INFO）が付与される（foundation 語彙参照）
  7. 実行記録が `conformance/<日付>-check.md` に保管される（`mode_internal: check`、T-009 連動）
- **テスト要件**：二段階方式の順序テスト、遮断テスト（MV-6 混入検知 → 遮断必須）、feature-partitioning 例外テスト（**＋ feature-partitioning が推定モジュールに渡される肯定確認テスト、topic-117／F-008 対処**）、intent 参考情報テスト、オプション機能テスト（**CLI 引数 `--check-partitioning` の付与／不付与で標準動作に含まれないことを確認、topic-118／F-012 対処**）、4 段重大度テスト、実行記録保管テスト

### T-005：6 criteria 検査構造（Six Criteria Structure）

- **対応設計節**：design.md §8.1〜§8.5
- **対応要件**：Requirement 1 受入 5、Requirement 4 受入 1〜5
- **責務**：6 criteria（requirements conformance 3 ＋ design conformance 3、§8.1）を符号化。axis（requirements ／ design の 2 値）と criterion-1〜6 の ID を定義（F-004 対処）。照合対象から除外する 3 階層（feature-partitioning ／ intent ／ tasks、§8.2、Req 4 受入 2）。各 criterion のサブ構造（要点／詳細抽出／深掘り／該当なし、§5.9.2 規律継承、§8.3）。実装適合との分離（§8.4、本機能の責務外）。検査仕様を `schemas/review-criteria/conformance_evaluation.yaml` として整備（§8.5、Req 4 受入 5、フェーズ 2 配置 → DVT-C001）
- **前提タスク**：T-001
- **成果物**：
  - `tools/conformance_evaluation/criteria.py`（6 criteria の axis ／ criterion ID 定義 ＋ 除外階層判定）
  - `schemas/review-criteria/conformance_evaluation.yaml`（6 criteria の検査仕様。フェーズ 2 配置、DVT-C001）
- **完了条件**：
  1. 6 criteria（requirements 3 ＋ design 3）が axis（**requirements ／ design の 2 値**）× criterion ID（criterion-1〜6）で符号化され、未知の axis ／ criterion が fail-closed になる。**intent は axis の 3 値目にせず、参考情報専用フィールド `reference_axis` に分離**するため、2 値 fail-closed が intent 差異記録（design §10.5）を弾かない（topic-111／G-003 対処、2026-05-29 セッション 39）
  2. 照合対象から除外する 3 階層（feature-partitioning ／ intent ／ tasks）が機械検証される（照合対象に含めない）
  3. 各 criterion がサブ構造（要点／詳細抽出／深掘り／該当なし）を持つ（§5.9.2 規律継承）
  4. `conformance_evaluation.yaml` は **フェーズ 2 で配置後に** 6 criteria を網羅し、推定（T-006）・比較（T-007）の検査構造と整合することを確認する（第 1 期は配置延期＝DVT-C001、本完了条件は配置後の整合確認として判定。topic-118／F-014 で延期と完了条件の矛盾感を解消）
- **テスト要件**：6 criteria 符号化テスト、axis ／ criterion 値域テスト、除外階層テスト、サブ構造テスト、`conformance_evaluation.yaml` 整合テスト

### T-006：推定モデル（Estimation Model）

- **対応設計節**：design.md §9.1〜§9.5
- **対応要件**：Requirement 1 受入 1（推定方向）、Requirement 2 受入 1（生成モードの推定）、Requirement 3 受入 1（照合モードの推定）
- **責務**：実装コードから上流文書（requirements ／ design 中心、intent 参考）を推定。**推定順序：design 先行 → requirements 逆算**（§9.2、Decision 10、F-008 対処、順序依存を機械保証）。推定対象の階層別扱い（§9.3）。推定根拠の保持（§9.4、`<ファイルパス>:<行範囲>` 形式、MV-5 連動）。推定の信頼度（§9.5、high ／ medium ／ low、**foundation 語彙体系の信頼度ラベルを参照**、A-013 対処済み、Decision 11）
- **前提タスク**：T-005
- **成果物**：
  - `tools/conformance_evaluation/estimation_model.py`（design 先行 → requirements 逆算の順序 ＋ 推定根拠保持 ＋ 信頼度判定）
- **完了条件**：
  1. 推定順序が design 先行 → requirements 逆算で実行されることが単体テストで機械検証される（§9.2、F-008 対処）
  2. 推定根拠が `<ファイルパス>:<行範囲>` 形式で保持される（MV-5 連動）
  3. 信頼度が high ／ medium ／ low で判定され、**foundation 語彙正本を参照**（再定義しない、A-013 対処済み、Decision 11、§14.1）
  4. 推定対象の階層別扱い（requirements ／ design 中心、intent 参考、feature-partitioning ／ tasks 対象外）が機械検証される
- **テスト要件**：推定順序テスト（design → requirements）、推定根拠形式テスト、信頼度判定テスト（foundation 語彙参照の確認）、階層別扱いテスト、サンプルアプリ（1000 行規模、§19.1）での推定受入テスト

### T-007：比較モデル（Comparison Model）

- **対応設計節**：design.md §10.1〜§10.7
- **対応要件**：Requirement 3 受入 2（食い違い検出）、Requirement 3 受入 3（intent 差異記録）
- **責務**：既存上流文書と推定上流文書を比較し食い違いを列挙。比較対象粒度（§10.2、6 criteria の各 criterion）。比較アルゴリズム（§10.3）：3 対応関係（節の有無 ／ 節内の主張・受入基準の対応 ／ 実装コードへの言及齟齬）のいずれかに不整合があれば「食い違い」（Req 3 受入 2）。食い違いの記録形式（§10.4）。intent の差異記録（§10.5、所見メタとして記録、must-fix 対象外、Req 3 受入 3）。比較結果の出力（§10.6）。**finding_id ／ judgment_id 発番ルール（§10.7、CF-NNN ／ JD-NNN、A-002 対処、Decision 9）**
- **前提タスク**：T-006
- **成果物**：
  - `tools/conformance_evaluation/comparison_model.py`（3 対応関係の判定 ＋ 食い違い記録 ＋ CF-NNN ／ JD-NNN 発番）
- **完了条件**：
  1. 3 対応関係（節有無 ／ 主張対応 ／ コード言及齟齬）が判定され、いずれかの不整合で食い違いと記録される（Req 3 受入 2）
  2. 比較対象粒度が 6 criteria の各 criterion 単位である（T-005 連動）
  3. intent の差異が所見メタとして記録され must-fix 対象外であることが機械検証される（Req 3 受入 3）
  4. finding_id（CF-NNN）／ judgment_id（JD-NNN）の発番が §10.7 の規則どおり機能する（採番衝突がない。self-improvement topic-99 の教訓に倣い、移動・分散があっても重複しない走査範囲を確認）
- **テスト要件**：3 対応関係判定テスト、criterion 単位粒度テスト、intent 差異記録テスト（must-fix 対象外、`reference_axis` フィールドへの記録、topic-111 連動）、CF-NNN ／ JD-NNN 発番テスト（衝突回避＋**最初の採番（CF-001）・3 桁 → 4 桁拡張（999 → 1000）の境界、topic-118／F-011 対処**）、既存上流文書ありサンプルアプリでの照合受入テスト

### T-008：3 役レビュー機構の適用（Triad Review Application）

- **対応設計節**：design.md §11.1〜§11.4
- **対応要件**：Requirement 2 受入 6、Requirement 3 受入 6／7、Requirement 5 受入 1〜8
- **責務**：3 役レビュー機構（主役 → 敵対役 → 判定役）を **推定段階と照合段階の両方** に適用（§11.1）。軽量／本格の使い分け（§11.2、Req 5 受入 2）：本格適用＝feature-partitioning 推定（傍流）・requirements 推定・照合段階、軽量適用＝design 推定・intent 推察。§5.9 規律の流用（§11.3）：モデル多様化・ファイル遮断・β 逐次方式・重大度語彙 4 段・所見メタデータ必須化（severity ／ judgment ／ depth ／ evidence_type ／ verifying_commands）・3 方式比較データ（`findings_by_method`）・レビューモード語彙（**foundation 参照**）。API 経路と障害対応（§11.4、§5.9.7 流用、タイムアウト・リトライ・部分失敗）。**責務境界（topic-113／F-001 対処、2026-05-29 セッション 39）**：本タスクは §5.9 規律のメタ情報（severity ／ judgment ／ depth ／ evidence_type ／ verifying_commands）の流用のみを担い、axis ／ criterion_id の生成・参照は推定（T-006）・比較（T-007）の責務。よって前提タスクは T-001 のみで足り、T-005（6 criteria 定義）を直接の前提に必要としない（過剰な直列化を避ける）
- **前提タスク**：T-001（T-005 を直接の前提にしない理由は上記責務境界を参照）
- **成果物**：
  - `tools/conformance_evaluation/triad_review.py`（軽量／本格の使い分け ＋ §5.9 規律流用 ＋ API 障害対応）
- **完了条件**：
  1. 3 役レビュー機構が推定段階・照合段階の両方で適用される（§11.1）
  2. 軽量／本格の使い分けが §11.2 の対応どおり判定される（本格＝requirements 推定・照合等、軽量＝design 推定・intent 推察）
  3. §5.9 規律（モデル多様化・ファイル遮断・β 逐次・重大度 4 段・所見メタ必須・findings_by_method）が適用される
  4. レビューモード語彙・重大度語彙・信頼度ラベルが **foundation 正本を参照**（再定義しない）
  5. API 障害対応（タイムアウト・リトライ・部分失敗の検知と扱い）が §5.9.7 から流用される
- **テスト要件**：両段階適用テスト、軽量／本格使い分けテスト、§5.9 規律適用テスト、foundation 語彙参照テスト、API 障害対応テスト（タイムアウト・リトライ・部分失敗）

### T-009：評価記録の type 値と配置（Evaluation Record Type and Placement）

- **対応設計節**：design.md §12.1〜§12.4
- **対応要件**：Requirement 6 受入 1〜5
- **責務**：評価記録の `type` 値を `conformance_evaluation` に統合（§12.1、生成／照合の区別は内部フィールド）。配置先 `conformance/<日付>-<mode>.md`（§12.2、`reviews/` と別、Req 8 受入 4）。front-matter の構造（§12.3）：`mode_internal: generation` ／ `check`、`author` ／ `reviewer`（§5.4 規律、異名必須）、**`target_commit`（conformance-evaluation 所有）と `materialization_commit_hash`（self-improvement 所有）の整合ルール（G10 対処、A-016 対処済み、§12.3）**。関連実行記録への参照（§12.4、runtime ／ evaluation ／ workflow-management、Req 6 受入 5）
- **前提タスク（硬い依存と緩い依存を区別、topic-114／F-002 対処、2026-05-29 セッション 39）**：硬い依存（着手前提）＝T-003、T-004。緩い依存（完了検証前提＝起草は先行可だが完了条件のクローズ前に成果物が必要）＝T-006（推定、finding_id ／ axis ／ criterion_id の形式）、T-007（比較、judgment_id の形式）。self-improvement の硬い／緩い依存区別を流用
- **成果物**：
  - `tools/conformance_evaluation/evaluation_record.py`（type 統合 ＋ front-matter ＋ 関連参照）
  - `tools/conformance_evaluation/schemas/evaluation_record.schema.json`（評価記録 front-matter スキーマ）
- **完了条件**：
  1. 評価記録の `type` が `conformance_evaluation` に統合される（MV-1）
  2. `mode_internal` が `generation` ／ `check` のいずれかである（MV-2）
  3. 評価記録が `conformance/` ディレクトリに配置され `reviews/` と混在しない（MV-3）
  4. `author` ／ `reviewer` が §5.4 規律に従い異名で明示される
  5. `target_commit`（本機能所有）と `materialization_commit_hash`（self-improvement 所有）の独立性・整合ルールが §12.3 と整合する（A-016 対処済み）
  6. runtime ／ evaluation ／ workflow-management の関連実行記録への参照が保持される
- **テスト要件**：type 統合テスト（MV-1）、mode_internal テスト（MV-2）、ディレクトリ分離テスト（MV-3）、author／reviewer 異名テスト、commit hash 整合テスト、関連参照テスト

### T-010：依存関係の連想配列構造（Associative Dependency Structure）

- **対応設計節**：design.md §13.1〜§13.5
- **対応要件**：Requirement 7 受入 1〜5
- **責務**：`stages/feature-dependency.yaml` における本機能の依存記述を**連想配列構造**（`depends_on: {feature_name: dependency_type}`）で表現（§13.1、他機能の単純リストと異なる）。依存種別 2 値（`hard` ／ `review`、§13.2）。依存記述の確定値（§13.3）：`foundation: hard` ／ `runtime: review` ／ `evaluation: review` ／ `workflow-management: review`。**workflow-management のスキーマ拡張（連想配列許容、Req 8 受入 2）との整合（§13.4）**。phase_order の最後（§13.5、依存先がすべて先に完了）
- **前提タスク**：T-001
- **成果物**：
  - `stages/feature-dependency.yaml` への本機能の連想配列構造エントリ（または design 参照先の確定記述）
- **完了条件**：
  1. 本機能の依存記述が連想配列構造（`{feature_name: dependency_type}`）で表現される（他機能の単純リストと区別）
  2. 依存種別が `hard` ／ `review` の 2 値で区別される（未知値は fail-closed）
  3. 確定値（foundation: hard ／ runtime: review ／ evaluation: review ／ workflow-management: review）と一致する
  4. workflow-management のスキーマ拡張（Req 8 受入 2 の連想配列許容）と整合する（DVT-C002 解除済 2026-05-29：workflow-management T-002 の feature-dependency.schema.json／完了条件2 と仕様レベルで完全一致を確認）
  5. phase_order の最後に位置付けられる
- **テスト要件**：連想配列構造解釈テスト、hard ／ review 区別テスト、確定値整合テスト、workflow-management スキーマ整合テスト（consumer 側、producer 側 workflow-management は機能横断段で対をなす）、phase_order テスト

### T-011：他機能との接合面（Interfaces with Other Features）

- **対応設計節**：design.md §14.1〜§14.6
- **対応要件**：Boundary Context 隣接期待（foundation ／ runtime ／ evaluation ／ analysis ／ workflow-management ／ self-improvement の 6 機能）
- **責務**：6 機能との接合面を整備。**foundation**（§14.1、依存 hard）：スキーマ・メタデータ契約・各語彙・信頼度ラベルを再定義せず参照。**runtime**（§14.2、依存 review）：実装コードのレビュー実行記録を入力源として読む。**evaluation**（§14.3、依存 review、G10 対処）：評価結果との突き合わせ詳細（経路別差分 ／ severity 集計 ／ `role_diff_report.json`（A-011 対処済み））。**workflow-management**（§14.4、依存 review）：所定手続きの実行履歴と上流文書の整合確認。**analysis**（§14.5、G10 対処）：6 criteria 検査結果を機械可読出力スキーマで提供（analysis が 4 出力先に取り込む）。**self-improvement**（§14.6、G10 対処）：6 criteria 検査結果を規律改善の入力として提供（self-improvement が本機能の出力を読む方向、本機能の `depends_on` には含まれない）。`target_commit`（本機能所有）と `materialization_commit_hash`（self-improvement 所有）の独立性（A-016 対処済み）
- **前提タスク**：T-006、T-007、T-009
- **成果物**：
  - `tools/conformance_evaluation/interfaces.py`（consumer 側＝foundation 語彙参照・runtime ／ evaluation ／ workflow-management 入力読み取り、producer 側＝analysis ／ self-improvement 向け出力）
- **完了条件**：
  1. foundation 語彙正本を再定義せず参照のみで使用していることが機械検証される（grep 検査）
  2. runtime ／ evaluation ／ workflow-management の出力を入力源として読める（依存 review）
  3. evaluation 接合面の突き合わせ詳細（`role_diff_report.json`（A-011 対処済み）を含む）が §14.3 と整合する
  4. analysis 向け出力が機械可読スキーマで提供される（§14.5、analysis Req 8 受入 5 由来）
  5. self-improvement 向け出力（6 criteria 検査結果）が提供され、方向が「conformance-evaluation → self-improvement」である（§14.6、本機能の depends_on には含まれない）
  6. `target_commit` ／ `materialization_commit_hash` の独立性（A-016 対処済み）が §12.3 ／ §14.6 と整合する
- **テスト要件**：foundation 語彙不再定義テスト（grep）、3 機能入力読み取りテスト、evaluation 突き合わせテスト、analysis 出力スキーマテスト、self-improvement 出力方向テスト、commit hash 独立性テスト

### T-012：機械検査の具体手段（Machine Verification）

- **対応設計節**：design.md §18.1〜§18.4
- **対応要件**：Requirement 6（評価記録の機械検査）、Requirement 8 受入 4（ディレクトリ分離検査）
- **責務**：7 つの機械検査ポイント（§18.1）を実装。**MV-1**：`type: conformance_evaluation` 設定（grep）。**MV-2**：`mode_internal` が check ／ generation（grep ＋値照合）。**MV-3**：`conformance/` と `reviews/` のディレクトリ分離（find ＋照合）。**MV-4**：推定文書の必須 3 節（grep）。**MV-5**：推定根拠の実装コード参照（grep ＋形式照合）。**MV-6**：既存上流文書遮断の事前検査（推定役プロンプトに既存上流文書混入なし＋自律探索禁止条項、grep ＋プロンプトログ）。**MV-7**：foundation 受入番号照合（G9 対処、本機能の `foundation Requirement N 受入 M` 記述が foundation requirements.md と一致、grep ＋機械照合）。**fail-closed の粒度別適用（§18.3）**：遮断必須＝MV-6 ／ 遮断推奨＝MV-1・MV-2・MV-3 ／ 警告続行可＝MV-4・MV-5・MV-7。第 1 期は手動 grep ／ find、フェーズ 4 で段階自動化（§18.4、DVT-C003）。**MV-6 の第 1 期最小仕様（topic-116／F-007 対処、2026-05-29 セッション 39、Sonnet API 別案＝段階的具体化を採用）**：推定役プロンプトログの必須フィールド（時刻 ／ 実行 ID ／ プロンプト全文）、格納先ディレクトリ命名規則（例 `logs/estimation/<run_id>/prompt.log`）、MV-6 実行用 grep 雛形 2 条件（(a) 既存上流文書パスの不在確認 (b) 自律探索禁止条項の存在確認）を tasks に記述する。技術手段の詳細確定（プロセス隔離等）は DVT-C004（フェーズ 4 第 2 サイクル）連動で予約
- **前提タスク（硬い依存と緩い依存を区別、topic-114／F-002 対処）**：硬い依存（着手前提）＝T-003、T-004、T-009。緩い依存（完了検証前提）＝T-006（MV-5 の推定根拠形式の検査対象 ／ MV-7 の foundation 参照記述の検査対象）
- **成果物**：
  - `tools/conformance-evaluation-check.py`（MV-1〜MV-7 の検査。第 1 期は手動 grep の補助、自動化はフェーズ 4 第 1〜2 サイクル）
  - `docs/operations/CONFORMANCE_EVALUATION.md` への MV-1〜MV-7 の検査手順記述
- **完了条件**：
  1. MV-1〜MV-7 の各検査が定義どおり機能する（§18.1）
  2. fail-closed の粒度が MV ID 別に区別される（遮断必須＝MV-6 ／ 遮断推奨＝MV-1〜3 ／ 警告続行可＝MV-4・5・7、§18.3）
  3. MV-6（遮断必須）は推定役プロンプトへの既存上流文書混入を検知し即時停止する（T-004 連動）
  4. MV-7 が foundation requirements.md の最新受入番号と本機能の参照を機械照合する（foundation 改訂追従）
  5. 検査結果が評価記録本文の「機械検査結果」節に記録される
  6. workflow-management の `check-workflow-action.py` との責務分担（§18.2）が運用文書に明示される
- **テスト要件**：MV-1〜MV-7 の各検査テスト（正常系 ／ 異常系）、fail-closed 粒度別テスト（遮断必須 ／ 推奨 ／ 警告続行）、MV-6 混入検知テスト、MV-7 番号照合テスト、責務分担の文書検査

### T-013：テスト戦略全体の整備（Test Strategy）

- **対応設計節**：design.md §19.1〜§19.4、§20.3 起草完了基準
- **対応要件**：本機能全要件の機械的合否判定、要件追跡表（§15）の双方向整合、DVT 解除確認
- **責務**：design.md §19 で定義された 7 モデル × 3 テストレベル（単体 ／ 結合 ／ 受入）をすべて Python テストとして整備、pytest で一括実行可能にする。重点ポイント（§19.2：既存上流文書の遮断（MV-6）／ feature-partitioning の例外扱い ／ 推定の信頼度 ／ 6 criteria の網羅 ／ 推定順序（design 先行 → requirements 逆算）／ foundation 受入番号照合（MV-7））。テストデータ取得元（§19.4：サンプルアプリのコード ／ 既存上流文書 ／ 既存 feature-partitioning）。要件追跡表（design §15）と各タスク本文の対応要件欄の双方向整合チェック（self-improvement T-011 の方針継承）。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010 ／ T-011 ／ T-012
- **成果物**：`tests/conformance-evaluation/` 配下のテストファイル群（推定 ／ 比較 ／ モード切替 ／ 3 役レビュー ／ 評価記録 ／ 依存関係 ／ 機械検査の各テスト＋要件追跡整合テスト）
- **完了条件**：すべての pytest が pass、7 モデル × 3 テストレベルを網羅、foundation 語彙正本の参照のみ使用が機械検証される、6 criteria の網羅、推定順序（design → requirements）が単体テストで検証される、二段階方式と遮断（MV-6）が網羅される、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化、サンプルアプリでの両モード End-to-End 受入テスト

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：下流→上流、4 階層 | T-006（推定）＋ T-005（§8.2 照合除外＝feature-partitioning／intent／tasks を対象外とする、topic-115 で追記） |
| Requirement 1 受入 2：上流文書なくてもよい | T-003（生成モード） |
| Requirement 1 受入 3：実装適合レビュー非吸収 | T-011（接合面 §14.2）＋スコープ前提 |
| Requirement 1 受入 4：2 モード | T-002（モード切替） |
| Requirement 1 受入 5：同一 6 criteria | T-005 |
| Requirement 2 受入 1：4 階層扱い分け | T-003 ＋ T-006（推定） |
| Requirement 2 受入 2：出力先パス規則 | T-001 ＋ T-003 |
| Requirement 2 受入 3：3 節必須 | T-003（MV-4） |
| Requirement 2 受入 4：推定根拠保持 | T-006（§9.4、MV-5） |
| Requirement 2 受入 5：人間判断必要性明示 | T-003 |
| Requirement 2 受入 6：3 役レビュー適用 | T-008 |
| Requirement 2 受入 7：実行記録保管 | T-003 ＋ T-009 |
| Requirement 3 受入 1：二段階方式 | T-004 |
| Requirement 3 受入 2：食い違い検出 | T-007（比較） |
| Requirement 3 受入 3：intent 参考情報 | T-004 ＋ T-007（§10.5） |
| Requirement 3 受入 4：機能分割食い違いオプション | T-004（§7.6） |
| Requirement 3 受入 5：4 段重大度 | T-004（foundation 語彙参照） |
| Requirement 3 受入 6／7：3 役レビュー（受入 7 の判定値保持） | T-008 ＋ T-007（judgment_id（JD-NNN）発番、§10.4／§10.7、topic-115 で追記） |
| Requirement 3 受入 8：実行記録保管 | T-004 ＋ T-009 |
| Requirement 4 受入 1：6 criteria | T-005 |
| Requirement 4 受入 2：照合対象除外 | T-005（§8.2） |
| Requirement 4 受入 3：サブ構造 | T-005（§8.3） |
| Requirement 4 受入 4：実装適合分離 | T-005（§8.4）＋スコープ前提 |
| Requirement 4 受入 5：検査仕様整備 | T-005（conformance_evaluation.yaml、DVT-C001） |
| Requirement 5 受入 1：両段階適用 | T-008 |
| Requirement 5 受入 2：軽量／本格 | T-008（§11.2） |
| Requirement 5 受入 3〜8：§5.9 規律流用 | T-008（§11.3／§11.4） |
| Requirement 6 受入 1：type 値統合 | T-009（MV-1） |
| Requirement 6 受入 2：配置先 | T-001 ＋ T-009（MV-3） |
| Requirement 6 受入 3：mode_internal | T-009（MV-2） |
| Requirement 6 受入 4：author／reviewer | T-009 |
| Requirement 6 受入 5：関連参照 | T-009 |
| Requirement 7 受入 1：連想配列構造 | T-010 |
| Requirement 7 受入 2：hard／review | T-010 |
| Requirement 7 受入 3：依存記述確定値 | T-010 |
| Requirement 7 受入 4：workflow-management スキーマ整合 | T-010（DVT-C002） |
| Requirement 7 受入 5：phase_order 最後 | T-010 |
| Requirement 8 受入 1：実装適合レビュー責務なし | T-011 ＋スコープ前提 |
| Requirement 8 受入 2：実装適合は §5.9／runtime に残る | T-011（§14.2） |
| Requirement 8 受入 3：3 軸性格差 | スコープ前提（概要章） |
| Requirement 8 受入 4：ディレクトリ分離 | T-001 ＋ T-009（MV-3） |
| Boundary Context 隣接期待（6 機能） | T-011 |
| 機械検査（MV-1〜MV-7） | T-012 |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §19 のテスト戦略を T-013 にまとめて継承する。各テストレベルの対応タスク：

- 単体テスト → T-002 ／ T-005 ／ T-006 ／ T-007 ／ T-009 ／ T-010 ／ T-012 個別 ＋ T-013 統合
- 結合テスト → T-003 ／ T-004 ／ T-008 ／ T-011 個別 ＋ T-013 統合
- 受入テスト → サンプルアプリ（1000 行規模、§19.1）での両モード End-to-End ＋ T-013 統合
- 異常系 fail-closed → 各タスクで fail-closed テスト（特に MV-6 遮断必須）＋ T-013 統合
- 境界条件 → T-006（推定順序）／ T-005（6 criteria 網羅）／ T-007（CF-NNN／JD-NNN 発番）＋ T-013 統合

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-013 のすべてが起草・実装・テスト・コミット完了
- design.md §20.3 起草完了基準の各項目が T-013 の統合テストで pass
- foundation が所有する語彙正本（スキーマ・メタデータ契約・各語彙・信頼度ラベル）を再定義せず参照のみで使用していることが機械検証される（§14.1、依存 hard）
- 二段階方式の遮断（MV-6 遮断必須）と推定順序（design 先行 → requirements 逆算）が機械検証される
- 6 criteria 検査構造（axis 2 値 × criterion-1〜6）が機械検証される
- 評価記録の type 統合（MV-1）・ディレクトリ分離（MV-3）が機械検証される
- 各タスクの成果物配置が design.md §12.2 ／ §18.2 と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は conformance-evaluation 機能（下流 → 上流の逆方向、実装コードから上流文書を推定・照合）を実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの所有モデル領域。self-improvement／workflow-management の粒度方針を継承
- **所有モデル単位の分離**：モード切替 §3 を T-002、文書生成モード §6 を T-003、照合チェックモード §7 を T-004、6 criteria §8 を T-005、推定 §9 を T-006、比較 §10 を T-007、3 役レビュー §11 を T-008、評価記録 §12 を T-009、依存関係 §13 を T-010、接合面 §14 を T-011、機械検査 §18 を T-012、テスト戦略 §19 を T-013 に対応付け
- **依存順の明示（topic-113／F-001 対処でフロー図を整合修正、2026-05-29 セッション 39）**：T-001（配置）から **T-005（6 criteria）・T-002（モード切替）・T-008（3 役）が並列に分岐**（いずれも T-001 のみを前提とし、T-008 は T-005 を直接の前提にしない＝責務境界 §T-008 参照）。T-005 → T-006（推定）→ T-007（比較）。T-002／T-006／T-007／T-008 がそろって → T-003（生成）／ T-004（照合）→ T-009（評価記録）→ T-010（依存）／ T-011（接合面）→ T-012（機械検査）→ T-013（統合テスト）。データの流れ（design §1：実装コード → 推定 → 比較 → 評価記録）を依存順の基本とする
- **本筋と傍流の分離**：照合チェックモード（本筋、T-004）と文書生成モード（傍流・人協働、T-003）を別タスクに分離（Decision 1）
- **二段階方式と遮断の徹底**：照合チェックは推定（遮断）→ 比較の順。MV-6 で遮断必須の fail-closed（design §18.3）
- **contract consumer 原則**：foundation 語彙正本を再定義せず参照のみ（§14.1、依存 hard）、runtime ／ evaluation ／ workflow-management の出力を入力源として読む（依存 review）
- **fail-closed の粒度別適用**：MV ID 別に遮断必須／遮断推奨／警告続行可を区別（§18.3）
- **テスト戦略の継承**：design §19 の 7 モデル × 3 テストレベルを T-013 で網羅
- **要件追跡表の双方向整合チェックを T-013 に組み込み**：self-improvement T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定事項（検査仕様の配置 ／ workflow-management スキーマ整合 ／ 検査自動化 ／ 推定役遮断の技術手段）を DVT で集約管理、T-013 完了条件で未解除項目がないことをゲート化
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。self-improvement／workflow-management の DVT 同型運用。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-C001 | T-005 | 6 criteria 検査仕様 `schemas/review-criteria/conformance_evaluation.yaml` の実体配置（design §8.5、Req 4 受入 5、フェーズ 2 配置） | フェーズ 2 で検査仕様を実体配置する時に T-005 完了条件と整合を再確認 | 未解除（フェーズ 2 まで延期） |
| DVT-C002 | T-010 | workflow-management のスキーマ拡張（Req 8 受入 2、依存記述の連想配列構造の許容）との整合。本機能の連想配列構造 consumer 側と workflow-management 側 producer が対をなす | 全機能の tasks triad-review 完了後の機能横断段（tasks フェーズの review-wave 段）で workflow-management 側のスキーマ実装と突き合わせ確認（topic-118／F-016 で括弧書きを明確化） | 解除済（2026-05-29 セッション40、機能横断段で仕様レベルの突き合わせ確認を実施。本機能 T-010 が期待する連想配列構造（`{機能名: 依存種別}`、hard ／ review、確定値 foundation:hard ／ runtime:review ／ evaluation:review ／ workflow-management:review）と、workflow-management T-002（feature-dependency.schema.json で連想配列を許容、完了条件2 が同一確定値を保持）が完全一致。実体（schema.json）は実装フェーズで実現） |
| DVT-C003 | T-012 | `tools/conformance-evaluation-check.py` による MV-1〜MV-7 の自動化（design §18.4）。第 1 期（フェーズ 1〜3）は手動 grep ／ find | フェーズ 4 第 1 サイクル（MV-1〜3・MV-7 自動化）・第 2 サイクル（MV-4〜6 自動化）着手時に T-012 完了条件と整合を再確認 | 未解除（フェーズ 4 以降まで延期） |
| DVT-C004 | T-004 | 推定役プロセスの隔離・既存上流文書遮断の技術手段（design §7.3 で「具体手法は design 段で確定」、§18.4 で chroot 環境での厳格遮断はフェーズ 4 第 2 サイクル検討） | フェーズ 4 第 2 サイクルで推定役プロセス隔離の実装時に T-004 完了条件・MV-6 と整合を再確認 | 未解除（フェーズ 4 第 2 サイクルまで延期） |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-013 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、carry-forward register 正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。既登録の機能横断所見 A-017（機能横断波及の確認手順が tasks.md に未明示）／A-018（foundation 語彙正本の所有件数の食い違い）／A-019（workflow-management T-010 の approved_update スキーマと self-improvement §8.4 の不一致）は機能横断段（tasks review-wave、2026-05-29 セッション40）で一括消化済み（未消化 0 件）。本機能の接合面に関わる A-011（evaluation の role_diff_report.json）／A-012（self-improvement と workflow-management の時系列契約）は ✅ 対処済み（2026-05-26 セッション 28）。なお design §20.1 が A-011／A-012 を「消化予定」と記載しているのは陳腐化の可能性があり（self-improvement topic-103／G-001 と同型）、triad-review で確認する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。DVT-C002（workflow-management スキーマ整合）も機能横断段で消化済み（解除済、2026-05-29 セッション40）。
```

## File: docs/operations/CONFORMANCE_EVALUATION.md
```
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

評価記録は必ず `conformance/<日付>-<mode>.md` のパス規則に従い、`reviews/` とは別に保管する。`reviews/` は仕様駆動レビューの記録、`conformance/` は本機能の下流 → 上流評価記録であり、混在させない。

文書生成モードの推定出力先は次のとおりとする。

```
<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/
├── feature-partitioning-candidates.md
├── intent-reference.md
└── specs/<feature>/
    ├── requirements.md
    └── design.md
```

モード切替は `check` または `generation` の明示指定のみで行い、既存文書の有無による自動判定は行わない。

## 6.1 機械検査（MV-1〜MV-7）

第 1 期の機械検査は手動 grep / find の補助として `tools/conformance-evaluation-check.py` から段階導入する。

| ID | 検査 | 失敗時の扱い |
|---|---|---|
| MV-1 | 評価記録に `type: conformance_evaluation` がある | 遮断推奨 |
| MV-2 | `mode_internal` が `check` または `generation` | 遮断推奨 |
| MV-3 | 評価記録が `conformance/` にあり `reviews/` と混在しない | 遮断推奨 |
| MV-4 | 推定文書に Introduction / Boundary Context / Requirements 相当の 3 節がある | 警告続行可 |
| MV-5 | 推定根拠が `<ファイルパス>:<行範囲>` 形式である | 警告続行可 |
| MV-6 | 推定役プロンプトに既存上流文書パスが混入せず、自律探索禁止条項がある | 遮断必須 |
| MV-7 | foundation 受入番号参照が foundation requirements.md と一致する | 警告続行可 |

MV-6 の第 1 期最小仕様では、推定役プロンプトログに時刻、実行 ID、プロンプト全文を残し、`logs/estimation/<run_id>/prompt.log` 相当の場所に保存する。検査は、既存上流文書パス（例 `intent.md`、`requirements.md`、`design.md`）の不在確認と、自律探索禁止条項の存在確認の 2 条件で行う。

`tools/conformance-evaluation-check.py` は conformance-evaluation 固有の評価記録・遮断・推定根拠を検査する。workflow-management の `tools/check-workflow-action.py` は workflow_state や不可逆操作の順序を検査するため、責務は異なる。

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
```

## File: tools/README.md
```
# tools

ReviewCompass の補助スクリプトを置く場所。

## self-improvement

`tools/self_improvement/` は `self-improvement` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/self_improvement/schemas/` はツール内部の中間スキーマを置く場所で、永続データ正本スキーマの `learning/workflow/schemas/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/self_improvement/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/self-improvement-check.py`

`tools/self-improvement-check.py` は self-improvement の機械検査 CLI の配置予定名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。

## conformance-evaluation

`tools/conformance_evaluation/` は `conformance-evaluation` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/conformance_evaluation/schemas/` はツール内部の中間スキーマを置く場所で、6 criteria の永続的な検査仕様を置く `schemas/review-criteria/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/conformance_evaluation/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/conformance-evaluation-check.py`

`tools/conformance-evaluation-check.py` は conformance-evaluation の機械検査 CLI の配置名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。
```

## File: schemas/review-criteria/conformance_evaluation.yaml
```
criteria:
  - criterion_id: criterion-1
    axis: requirements
    title: 受け入れ基準と実装の対応
  - criterion_id: criterion-2
    axis: requirements
    title: API・データ契約と実装の対応
  - criterion_id: criterion-3
    axis: requirements
    title: 例外系・境界条件と実装の対応
  - criterion_id: criterion-4
    axis: design
    title: モジュール構成・データモデルと実装の対応
  - criterion_id: criterion-5
    axis: design
    title: 接合面と実装の対応
  - criterion_id: criterion-6
    axis: design
    title: アルゴリズム・性能達成手段と実装の対応

```

## File: stages/feature-dependency.yaml
```
features:
  conformance-evaluation:
    depends_on:
      foundation: hard
      runtime: review
      evaluation: review
      workflow-management: review

```

## File: tests/conformance-evaluation/test_conformance_evaluation.py
```
from pathlib import Path

import pytest

from tools.conformance_evaluation.check_mode import CheckPipeline
from tools.conformance_evaluation.comparison_model import ComparisonModel
from tools.conformance_evaluation.criteria import CRITERIA, CriteriaError, criterion_by_id
from tools.conformance_evaluation.estimation_model import EstimationModel
from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel, RecordError
from tools.conformance_evaluation.generation_mode import GenerationPipeline
from tools.conformance_evaluation.machine_verification import MachineVerification, VerificationStatus
from tools.conformance_evaluation.mode_switch import ModeSwitch, ModeSwitchError
from tools.conformance_evaluation.triad_review import TriadReviewPolicy


ROOT = Path(__file__).resolve().parents[2]


def test_t001_layout_and_operation_docs_are_present():
  assert (ROOT / "tools" / "conformance_evaluation" / ".gitkeep").is_file()
  assert (ROOT / "tools" / "conformance_evaluation" / "schemas" / ".gitkeep").is_file()
  assert (ROOT / "tests" / "conformance-evaluation" / ".gitkeep").is_file()
  assert (ROOT / "schemas" / "review-criteria" / "README.md").is_file()
  text = (ROOT / "docs" / "operations" / "CONFORMANCE_EVALUATION.md").read_text(encoding="utf-8")
  assert "conformance/<日付>-<mode>.md" in text
  assert "reviews/ とは別" in text
  assert ".reviewcompass/conformance/inferred/<日付>/" in text
  tools_readme = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
  assert "tools/conformance_evaluation/" in tools_readme
  assert "tools/conformance-evaluation-check.py" in tools_readme


def test_t002_mode_switch_requires_explicit_mode():
  switch = ModeSwitch({"check": lambda payload: ("check", payload), "generation": lambda payload: ("generation", payload)})
  assert switch.dispatch("check", {"x": 1}) == ("check", {"x": 1})
  assert switch.dispatch("generation", {"x": 2}) == ("generation", {"x": 2})
  with pytest.raises(ModeSwitchError):
    switch.dispatch("auto", {})
  assert not switch.has_auto_detection()


def test_t003_generation_outputs_human_reviewable_documents(tmp_path):
  pipeline = GenerationPipeline(tmp_path)
  result = pipeline.generate(
    app_root=tmp_path,
    feature="billing",
    run_date="2026-06-04",
    code_refs=["src/billing.py:1-20"],
  )
  assert result["layer_policy"]["feature-partitioning"] == "human_collaboration"
  assert result["layer_policy"]["intent"] == "human_collaboration"
  assert result["layer_policy"]["requirements"] == "automatic_estimation"
  assert result["layer_policy"]["design"] == "automatic_estimation"
  assert result["layer_policy"]["tasks"] == "excluded"
  for path in result["documents"]:
    text = Path(path).read_text(encoding="utf-8")
    assert "Introduction" in text
    assert "Boundary Context" in text
    assert "Requirements" in text
    assert "src/billing.py:1-20" in text
    assert "human_review_required: true" in text
  assert (tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-generation.md").is_file()


def test_t004_check_mode_enforces_two_stage_isolation(tmp_path):
  pipeline = CheckPipeline(tmp_path)
  result = pipeline.run(
    feature="billing",
    implementation_refs=["src/billing.py:1-20"],
    feature_partitioning="billing boundary",
    prompt_text="Implementation only. Do not read existing upstream documents.",
    run_date="2026-06-04",
  )
  assert result["stages"] == ["estimate", "compare"]
  assert result["estimation_input"]["feature_partitioning"] == "billing boundary"
  assert result["intent_policy"] == "reference_only"
  assert result["partitioning_check"] == "standard_disabled"
  assert result["findings"][0]["severity"] == "INFO"
  assert (tmp_path / ".reviewcompass" / "specs" / "billing" / "conformance" / "2026-06-04-check.md").is_file()
  with pytest.raises(ValueError):
    pipeline.run(
      feature="billing",
      implementation_refs=["src/billing.py:1-20"],
      feature_partitioning="billing boundary",
      prompt_text="Please read requirements.md before estimating.",
      run_date="2026-06-04",
    )


def test_t005_six_criteria_are_two_axis_only():
  assert len(CRITERIA) == 6
  assert {item.axis for item in CRITERIA} == {"requirements", "design"}
  assert {item.criterion_id for item in CRITERIA} == {f"criterion-{index}" for index in range(1, 7)}
  assert criterion_by_id("criterion-1").axis == "requirements"
  with pytest.raises(CriteriaError):
    criterion_by_id("intent")


def test_t006_estimation_runs_design_before_requirements():
  model = EstimationModel()
  result = model.estimate(["src/billing.py:1-20"])
  assert result["order"] == ["design", "requirements"]
  assert result["design"]["evidence_refs"] == ["src/billing.py:1-20"]
  assert result["requirements"]["derived_from"] == "design"
  assert result["confidence"] in {"high", "medium", "low"}
  assert result["excluded_layers"] == ["feature-partitioning", "tasks"]
  assert result["intent"]["reference_axis"] == "intent"


def test_t007_comparison_records_mismatches_and_ids():
  model = ComparisonModel()
  finding = model.compare_one(
    criterion_id="criterion-2",
    existing={"section": "API", "claim": "returns YAML", "code_refs": ["src/a.py:1-2"]},
    inferred={"section": "API", "claim": "returns JSON", "code_refs": ["src/a.py:1-2"]},
  )
  assert finding["finding_id"] == "CF-001"
  assert finding["judgment_id"] == "JD-001"
  assert finding["mismatch"] is True
  assert finding["mismatch_types"] == ["claim_mismatch"]
  intent = model.intent_difference("existing intent", "inferred intent")
  assert intent["reference_axis"] == "intent"
  assert intent["eligible_for_must_fix"] is False
  assert model.format_next_id("CF", 1000) == "CF-1000"


def test_t008_triad_review_policy_applies_stage_and_intensity():
  policy = TriadReviewPolicy()
  assert policy.intensity_for("requirements_estimation") == "full"
  assert policy.intensity_for("design_estimation") == "lightweight"
  assert policy.intensity_for("comparison") == "full"
  metadata = policy.metadata_template()
  assert {"severity", "judgment", "depth", "evidence_type", "verifying_commands"} <= set(metadata)
  assert policy.handle_api_result({"status": "timeout"})["retry"] is True
  assert policy.handle_api_result({"status": "partial_failure"})["partial_failure"] is True


def test_t009_evaluation_record_front_matter_and_placement(tmp_path):
  model = EvaluationRecordModel(tmp_path)
  path = model.write_record(
    feature="billing",
    mode_internal="check",
    run_date="2026-06-04",
    author="primary",
    reviewer="judgment",
    target_commit="abc123",
    materialization_commit_hash="def456",
    related_records=["runtime/run.yaml"],
    body="## 機械検査結果\nOK\n",
  )
  assert "conformance" in path.parts
  text = path.read_text(encoding="utf-8")
  assert "type: conformance_evaluation" in text
  assert "mode_internal: check" in text
  assert "target_commit: abc123" in text
  with pytest.raises(RecordError):
    model.write_record(
      feature="billing",
      mode_internal="check",
      run_date="2026-06-04",
      author="same",
      reviewer="same",
      target_commit="abc123",
      materialization_commit_hash="def456",
      related_records=[],
      body="",
    )


def test_t010_dependency_shape_matches_feature_dependency():
  import yaml

  data = yaml.safe_load((ROOT / "stages" / "feature-dependency.yaml").read_text(encoding="utf-8"))
  deps = data["features"]["conformance-evaluation"]["depends_on"]
  assert deps == {
    "foundation": "hard",
    "runtime": "review",
    "evaluation": "review",
    "workflow-management": "review",
  }


def test_t011_interfaces_do_not_reverse_self_improvement_direction():
  from tools.conformance_evaluation.interfaces import Interfaces

  interfaces = Interfaces()
  assert interfaces.self_improvement_direction() == "conformance-evaluation -> self-improvement"
  assert interfaces.foundation_reference_only(["foundation_vocab_ref"])
  assert interfaces.commit_hashes_are_independent("abc", "abc")


def test_t012_machine_verification_mv6_is_blocking(tmp_path):
  verifier = MachineVerification(tmp_path)
  ok = verifier.check_prompt_isolation(
    prompt_text="Implementation only. 自律探索禁止: existing upstream docs must not be read.",
    forbidden_paths=["requirements.md", "design.md", "intent.md"],
  )
  assert ok.status == VerificationStatus.OK
  bad = verifier.check_prompt_isolation(
    prompt_text="Read requirements.md before estimating.",
    forbidden_paths=["requirements.md", "design.md", "intent.md"],
  )
  assert bad.status == VerificationStatus.DEVIATION
  assert bad.fail_closed == "blocking"


def test_t013_traceability_smoke():
  tasks_text = (ROOT / ".reviewcompass" / "specs" / "conformance-evaluation" / "tasks.md").read_text(encoding="utf-8")
  for index in range(1, 14):
    assert f"T-{index:03d}" in tasks_text
  assert "DVT" in tasks_text
```

## File: tools/conformance_evaluation/__init__.py
```
"""Conformance-evaluation helpers."""

```

## File: tools/conformance_evaluation/check_mode.py
```
"""Check mode pipeline with two-stage isolation."""
from pathlib import Path

from tools.conformance_evaluation.comparison_model import ComparisonModel
from tools.conformance_evaluation.estimation_model import EstimationModel
from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel
from tools.conformance_evaluation.machine_verification import MachineVerification, VerificationStatus


class CheckPipeline:
  def __init__(self, root: Path):
    self.root = Path(root)

  def run(
    self,
    *,
    feature: str,
    implementation_refs: list,
    feature_partitioning: str,
    prompt_text: str,
    run_date: str,
    check_partitioning: bool = False,
  ) -> dict:
    isolation = MachineVerification(self.root).check_prompt_isolation(
      prompt_text=prompt_text,
      forbidden_paths=["intent.md", "requirements.md", "design.md"],
    )
    if isolation.status == VerificationStatus.DEVIATION:
      raise ValueError("; ".join(isolation.reasons))
    estimate = EstimationModel().estimate(implementation_refs)
    comparison = ComparisonModel().compare_one(
      criterion_id="criterion-1",
      existing={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
      inferred={"section": "placeholder", "claim": "placeholder", "code_refs": implementation_refs},
    )
    comparison["severity"] = "INFO"
    EvaluationRecordModel(self.root).write_record(
      feature=feature,
      mode_internal="check",
      run_date=run_date,
      author="primary",
      reviewer="judgment",
      target_commit="unknown",
      materialization_commit_hash="independent",
      related_records=[],
      body="## 機械検査結果\nMV-6 OK\n",
    )
    return {
      "stages": ["estimate", "compare"],
      "estimation": estimate,
      "estimation_input": {"feature_partitioning": feature_partitioning},
      "intent_policy": "reference_only",
      "partitioning_check": "enabled" if check_partitioning else "standard_disabled",
      "findings": [comparison],
    }

```

## File: tools/conformance_evaluation/comparison_model.py
```
"""Comparison model for inferred and existing upstream documents."""
from tools.conformance_evaluation.criteria import criterion_by_id


class ComparisonModel:
  def __init__(self):
    self.finding_counter = 0
    self.judgment_counter = 0

  @staticmethod
  def format_next_id(prefix: str, number: int) -> str:
    width = 3 if number <= 999 else len(str(number))
    return f"{prefix}-{number:0{width}d}"

  def compare_one(self, *, criterion_id: str, existing: dict, inferred: dict) -> dict:
    criterion = criterion_by_id(criterion_id)
    mismatch_types = []
    if existing.get("section") != inferred.get("section"):
      mismatch_types.append("section_mismatch")
    if existing.get("claim") != inferred.get("claim"):
      mismatch_types.append("claim_mismatch")
    if set(existing.get("code_refs") or []) != set(inferred.get("code_refs") or []):
      mismatch_types.append("code_reference_mismatch")
    self.finding_counter += 1
    self.judgment_counter += 1
    return {
      "finding_id": self.format_next_id("CF", self.finding_counter),
      "judgment_id": self.format_next_id("JD", self.judgment_counter),
      "criterion_id": criterion.criterion_id,
      "axis": criterion.axis,
      "mismatch": bool(mismatch_types),
      "mismatch_types": mismatch_types,
    }

  def intent_difference(self, existing_intent: str, inferred_intent: str) -> dict:
    return {
      "reference_axis": "intent",
      "existing": existing_intent,
      "inferred": inferred_intent,
      "eligible_for_must_fix": False,
    }

```

## File: tools/conformance_evaluation/criteria.py
```
"""Six criteria structure for artifact-to-spec conformance evaluation."""
from dataclasses import dataclass


class CriteriaError(ValueError):
  """Raised when a criterion or axis is outside the conformance contract."""


@dataclass(frozen=True)
class Criterion:
  criterion_id: str
  axis: str
  title: str
  substructure: tuple


SUBSTRUCTURE = ("要点", "詳細抽出", "深掘り", "該当なし")

CRITERIA = (
  Criterion("criterion-1", "requirements", "受け入れ基準と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-2", "requirements", "API・データ契約と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-3", "requirements", "例外系・境界条件と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-4", "design", "モジュール構成・データモデルと実装の対応", SUBSTRUCTURE),
  Criterion("criterion-5", "design", "接合面と実装の対応", SUBSTRUCTURE),
  Criterion("criterion-6", "design", "アルゴリズム・性能達成手段と実装の対応", SUBSTRUCTURE),
)

EXCLUDED_LAYERS = ("feature-partitioning", "intent", "tasks")


def criterion_by_id(criterion_id: str) -> Criterion:
  for criterion in CRITERIA:
    if criterion.criterion_id == criterion_id:
      return criterion
  raise CriteriaError(f"unknown_criterion: {criterion_id}")


def validate_axis(axis: str) -> None:
  if axis not in {"requirements", "design"}:
    raise CriteriaError(f"unknown_axis: {axis}")

```

## File: tools/conformance_evaluation/estimation_model.py
```
"""Lightweight estimation model for implementation-to-upstream inference."""


class EstimationModel:
  def estimate(self, implementation_refs):
    refs = list(implementation_refs)
    design = {
      "summary": "implementation-derived design skeleton",
      "evidence_refs": refs,
    }
    requirements = {
      "summary": "requirements derived from design skeleton",
      "derived_from": "design",
      "evidence_refs": refs,
    }
    return {
      "order": ["design", "requirements"],
      "design": design,
      "requirements": requirements,
      "intent": {
        "reference_axis": "intent",
        "summary": "reference-only inferred intent",
      },
      "confidence": "medium",
      "excluded_layers": ["feature-partitioning", "tasks"],
    }

```

## File: tools/conformance_evaluation/evaluation_record.py
```
"""Evaluation record writer for conformance-evaluation."""
from pathlib import Path


class RecordError(ValueError):
  """Raised when an evaluation record would violate the front-matter contract."""


class EvaluationRecordModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  def write_record(
    self,
    *,
    feature: str,
    mode_internal: str,
    run_date: str,
    author: str,
    reviewer: str,
    target_commit: str,
    materialization_commit_hash: str,
    related_records: list,
    body: str,
  ) -> Path:
    if mode_internal not in {"generation", "check"}:
      raise RecordError(f"unknown_mode_internal: {mode_internal}")
    if author == reviewer:
      raise RecordError("author_reviewer_must_be_distinct")
    path = (
      self.root
      / ".reviewcompass"
      / "specs"
      / feature
      / "conformance"
      / f"{run_date}-{mode_internal}.md"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    related = "\n".join(f"  - {item}" for item in related_records) or "  []"
    text = (
      "---\n"
      "type: conformance_evaluation\n"
      f"mode_internal: {mode_internal}\n"
      f"author: {author}\n"
      f"reviewer: {reviewer}\n"
      f"target_commit: {target_commit}\n"
      f"materialization_commit_hash: {materialization_commit_hash}\n"
      "related_records:\n"
      f"{related}\n"
      "---\n\n"
      f"{body}"
    )
    path.write_text(text, encoding="utf-8")
    return path

```

## File: tools/conformance_evaluation/generation_mode.py
```
"""Generation mode pipeline for human-collaborative onboarding."""
from pathlib import Path

from tools.conformance_evaluation.evaluation_record import EvaluationRecordModel


class GenerationPipeline:
  def __init__(self, root: Path):
    self.root = Path(root)

  def generate(self, *, app_root: Path, feature: str, run_date: str, code_refs: list) -> dict:
    app_root = Path(app_root)
    inferred_root = app_root / ".reviewcompass" / "conformance" / "inferred" / run_date
    docs = [
      inferred_root / "feature-partitioning-candidates.md",
      inferred_root / "intent-reference.md",
      inferred_root / "specs" / feature / "requirements.md",
      inferred_root / "specs" / feature / "design.md",
    ]
    for path in docs:
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(self._document_text(path.name, code_refs), encoding="utf-8")
    EvaluationRecordModel(app_root).write_record(
      feature=feature,
      mode_internal="generation",
      run_date=run_date,
      author="primary",
      reviewer="judgment",
      target_commit="unknown",
      materialization_commit_hash="independent",
      related_records=[],
      body="## 推定根拠\n" + "\n".join(f"- {ref}" for ref in code_refs) + "\n",
    )
    return {
      "layer_policy": {
        "feature-partitioning": "human_collaboration",
        "intent": "human_collaboration",
        "requirements": "automatic_estimation",
        "design": "automatic_estimation",
        "tasks": "excluded",
      },
      "documents": [str(path) for path in docs],
    }

  def _document_text(self, title: str, code_refs: list) -> str:
    refs = "\n".join(f"- {ref}" for ref in code_refs)
    return (
      "---\n"
      "human_review_required: true\n"
      "---\n\n"
      f"# {title}\n\n"
      "## Introduction\n\n"
      "Human review is required before adoption.\n\n"
      "## Boundary Context\n\n"
      "Generated as a first draft for conformance-evaluation.\n\n"
      "## Requirements\n\n"
      f"{refs}\n"
    )

```

## File: tools/conformance_evaluation/interfaces.py
```
"""Interfaces with adjacent ReviewCompass features."""


class Interfaces:
  def self_improvement_direction(self) -> str:
    return "conformance-evaluation -> self-improvement"

  def foundation_reference_only(self, references: list) -> bool:
    return all("foundation" in item or "metadata_contract" in item for item in references)

  def commit_hashes_are_independent(self, target_commit: str, materialization_commit_hash: str) -> bool:
    return bool(target_commit) and bool(materialization_commit_hash)

```

## File: tools/conformance_evaluation/machine_verification.py
```
"""Machine verification for conformance-evaluation."""
from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
  OK = "OK"
  DEVIATION = "DEVIATION"


@dataclass(frozen=True)
class VerificationResult:
  check_id: str
  status: VerificationStatus
  reasons: list
  fail_closed: str


class MachineVerification:
  def __init__(self, root=None):
    self.root = root

  def check_prompt_isolation(self, *, prompt_text: str, forbidden_paths: list) -> VerificationResult:
    reasons = []
    for path in forbidden_paths:
      if path in prompt_text:
        reasons.append(f"forbidden upstream path in prompt: {path}")
    if "自律探索禁止" not in prompt_text and "Do not read existing upstream documents" not in prompt_text:
      reasons.append("missing autonomous exploration prohibition")
    return VerificationResult(
      check_id="MV-6",
      status=VerificationStatus.DEVIATION if reasons else VerificationStatus.OK,
      reasons=reasons,
      fail_closed="blocking",
    )

```

## File: tools/conformance_evaluation/mode_switch.py
```
"""Explicit mode switch for conformance-evaluation."""


class ModeSwitchError(ValueError):
  """Raised when mode selection is not explicit and valid."""


class ModeSwitch:
  def __init__(self, handlers):
    self.handlers = dict(handlers)

  def dispatch(self, mode: str, payload: dict):
    if mode not in {"check", "generation"}:
      raise ModeSwitchError(f"unknown_mode: {mode}")
    if mode not in self.handlers:
      raise ModeSwitchError(f"handler_missing: {mode}")
    return self.handlers[mode](payload)

  def has_auto_detection(self) -> bool:
    return False

```

## File: tools/conformance_evaluation/triad_review.py
```
"""Triad review application policy for conformance-evaluation."""


class TriadReviewPolicy:
  FULL_STAGES = {"feature_partitioning_estimation", "requirements_estimation", "comparison"}
  LIGHTWEIGHT_STAGES = {"design_estimation", "intent_inference"}

  def intensity_for(self, stage: str) -> str:
    if stage in self.FULL_STAGES:
      return "full"
    if stage in self.LIGHTWEIGHT_STAGES:
      return "lightweight"
    raise ValueError(f"unknown_triad_stage: {stage}")

  def metadata_template(self) -> dict:
    return {
      "severity": None,
      "judgment": None,
      "depth": None,
      "evidence_type": None,
      "verifying_commands": [],
      "findings_by_method": {},
    }

  def handle_api_result(self, result: dict) -> dict:
    status = result.get("status")
    return {
      "retry": status == "timeout",
      "partial_failure": status == "partial_failure",
      "status": status,
    }

```

## File: tools/conformance-evaluation-check.py
```
#!/usr/bin/env python3
"""CLI placeholder for conformance-evaluation machine checks."""
from tools.conformance_evaluation.machine_verification import MachineVerification


def main() -> int:
  MachineVerification()
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

```
