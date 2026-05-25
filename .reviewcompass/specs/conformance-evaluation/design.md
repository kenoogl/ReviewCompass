# Design Document：conformance-evaluation

最終更新：2026-05-26（セッション 27：design.drafting 起草、要件 8 件に対応、artifact-to-spec conformance evaluation の本筋／傍流分離設計）

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
- **解釈余地の差で軽量／本格を使い分ける**：feature-partitioning 推定・requirements 推定・照合段階は解釈余地が大きく本格適用、design 推定・intent 推察は実装からの導出が比較的直接的で軽量適用（Req 5 受入 2、§5.10.10）
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
  ├── 主役（primary）：実装コードから design ／ requirements を推定
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
[requirements ／ design の自動推定（3 役レビュー機構を適用）]
  ├── 主役：実装コードから生成
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

本機能は 2 モード（照合チェック／文書生成）を **明示的なモード指定** で切り替える。実装段の CLI 想定：`reviewcompass conformance check <feature>` と `reviewcompass conformance generate`。

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
| **requirements** | **自動推定**（人間が修正・補完） | 受入基準・API・例外系などコードから比較的直接導出可能 |
| **design** | **自動推定**（人間が修正・補完） | モジュール構成・接合面・アルゴリズムなどコードから直接読み取れる |
| **tasks** | **対象外** | 完成コードしか見えず分解過程は残らない |

### 6.3 出力先のパス規則

requirements.md Req 2 受入 2 に対応するパス規則：

```
<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/
├── feature-partitioning-candidates.md     # 機械的候補、人間が編集
├── intent-reference.md                    # 参考情報、人間が編集
└── specs/<feature>/
    ├── requirements.md                    # 自動推定、人間が編集
    └── design.md                          # 自動推定、人間が編集
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
   └── 推定結果：design ／ requirements の各機能版

第 2 段階：比較（既存上流文書を読み込む、§10）
   ├── 既存 intent ／ requirements ／ design を読み込み
   ├── 推定 design ／ requirements と比較
   └── 食い違いを列挙
```

### 7.2 既存 feature-partitioning を例外とする理由

機能名・境界が違うと「同じ機能の design ／ requirements を比較」が成立しないため、既存 feature-partitioning だけは推定時の入力に含める（2026-05-24 セッション 23 利用者指摘）。

例：既存上流文書では機能 A／B／C が定義されているが、本機能が独立に推定すると機能 X／Y／Z に分割される可能性がある。これでは「機能 A の design 推定 vs 既存機能 A の design」という対応関係が確立できない。

### 7.3 既存上流文書の遮断手法

requirements.md Req 3 受入 1 の遮断は **技術的手段** で実装する。具体的な遮断手法（実装段で確定）：

| 手法 | 説明 |
|---|---|
| **ファイル読み取り権限の制限** | 推定役プロセスを `chroot` や読み取り権限制限環境で実行、既存上流文書のファイルへのアクセスを物理的に阻止 |
| **推定役プロセスの隔離** | サブエージェント方式の場合、Agent ツールのプロンプトに既存上流文書のパスを含めない、ファイル遮断規律（§5.9.1）を適用 |
| **入力の事前検査** | 推定役へのプロンプトを事前検査し、既存上流文書の内容が混入していないかを grep で確認 |

第 1 期では **サブエージェント方式での遮断（プロンプト制御＋ファイル遮断）** を採用、フェーズ 4 第 2 サイクル以降で chroot 環境での厳格遮断を検討する。

### 7.4 食い違い検出の対応関係

requirements.md Req 3 受入 2 に対応。

6 criteria（Requirement 4 受入 1 由来、2 上流フェーズ × 3 criteria）の各 criterion に基づき、次の **3 対応関係** を比較する：

| 対応関係 | 内容 |
|---|---|
| **節の有無** | 既存文書に対応する節があるか／推定文書に対応する節があるか |
| **節内の主張・受入基準の対応** | 既存文書の主張・受入基準と推定文書の主張・受入基準が意味的に一致するか |
| **実装コードへの言及齟齬** | 既存文書が言及する実装コード箇所と推定文書が言及する実装コード箇所が一致するか |

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

#### requirements conformance（3 criteria）

| Criterion | 内容 |
|---|---|
| **Criterion 1** | 受け入れ基準と実装の対応 |
| **Criterion 2** | API ・データ契約と実装の対応 |
| **Criterion 3** | 例外系・境界条件と実装の対応 |

#### design conformance（3 criteria）

| Criterion | 内容 |
|---|---|
| **Criterion 4** | モジュール構成・データモデルと実装の対応 |
| **Criterion 5** | 接合面（API シグネチャ・エラーモデル）と実装の対応 |
| **Criterion 6** | アルゴリズム・性能達成手段と実装の対応 |

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
      axis: requirements
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

### 9.2 推定アルゴリズム（概要）

第 1 期では **半自動** で実施（自動部分は LLM 呼び出し、判断部分は人間または LLM）：

1. **実装コードの読み込み**：対象機能のコードベースを読む
2. **構造抽出**：モジュール構成、API シグネチャ、データモデル、例外処理を機械的に抽出
3. **受入基準の推定**：抽出した構造から「実装が満たしている受入基準」を LLM で推定
4. **design 要素の推定**：抽出した構造から「実装が前提とする design 要素（アルゴリズム・性能達成手段）」を LLM で推定
5. **3 役レビュー機構による検証**：主役の推定 → 敵対役の別解釈 → 判定役の整合判定（§11）
6. **推定文書の生成**：YAML/Markdown 形式で出力、推定根拠（コード参照）を併記

実装段の詳細化（フェーズ 4 第 2 サイクル）：
- LLM プロンプト設計（プロンプト雛形 `templates/prompts/conformance_evaluation/`）
- 構造抽出ツールの実装言語非依存設計
- 推定品質の段階的改善

### 9.3 推定対象の階層別扱い

| 階層 | 照合チェックモード | 文書生成モード |
|---|---|---|
| **feature-partitioning** | 既存を入力として尊重（推定しない） | 機械的候補を提示、人間が境界決定 |
| **intent** | 参考情報として推察（独立推定しない） | 構造から推察、人間が補完 |
| **requirements** | 自動推定（実装コードから） | 自動推定（人間が修正・補完） |
| **design** | 自動推定（実装コードから） | 自動推定（人間が修正・補完） |
| **tasks** | 対象外 | 対象外 |

### 9.4 推定根拠の保持

各推定要素に対して、実装コードの参照を最低 1 件付与する：

```yaml
estimated_requirement:
  axis: receive_criteria                # 受入基準
  description: |
    実装が「ユーザー登録時にメールアドレスの形式を検証する」要件を満たしている
  rationale_code_refs:
    - path: src/user_registration.py
      lines: 45-67
      excerpt: |
        if not validate_email_format(email):
            raise InvalidEmailError(...)
```

### 9.5 推定の信頼度

推定結果に **信頼度ラベル**（high／medium／low）を付与する。信頼度は推定根拠（コード参照件数、明示性）から自動判定（実装段で確定）：

- **high**：複数のコード参照、関数名／コメント／例外メッセージから明示的
- **medium**：1〜2 のコード参照、間接的な導出
- **low**：構造からの推察のみ、人間判断が強く必要

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
- 各 criterion で次の 3 対応関係を比較：節の有無 ／ 節内の主張・受入基準の対応 ／ 実装コードへの言及齟齬（§7.4）
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
finding_id: CF-001                       # Conformance Finding の通し番号
finding_type: discrepancy                # discrepancy / missing_section / extra_section
criterion: criterion-1                   # 6 criteria のいずれか
correspondence_type: receive_criteria_alignment   # 3 対応関係のいずれか
severity: ERROR
existing_text: |
  既存 requirements の該当箇所の引用
estimated_text: |
  推定 requirements の該当箇所の引用
discrepancy_description: |
  食い違いの内容（30 文字以上）
implementation_code_refs:                # 食い違いに関連する実装コード参照
  - path: src/...
    lines: 45-67
judgment_id: JD-001                      # 3 役レビュー後の判定 ID（§11）
```

### 10.5 intent の差異記録

requirements.md Req 3 受入 3 に対応。

- intent の差異は所見メタとして記録、ただし must-fix 判定の対象外
- 記録形式：上記 `finding_id` の `criterion` に `intent-reference`（独立 criterion ではなく参考情報）を設定

### 10.6 比較結果の出力

照合チェックモードの実行記録 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-check.md` に比較結果を出力：

- 食い違いごとの YAML エントリ
- 6 criteria 別の集計（食い違い件数、severity 別の内訳）
- 推定根拠と既存文書の出典

## 11. 3 役レビュー機構の適用（Triad Review Application）

本章は requirements.md Req 5 に対応する。

### 11.1 推定段階と照合段階の両方への適用

requirements.md Req 5 受入 1 に対応。

| 段階 | 主役 | 敵対役 | 判定役 |
|---|---|---|---|
| **推定段階（照合チェック・文書生成共通）** | 実装コードから推定 | 別解釈を提示 | 実装との整合で判定 |
| **文書生成タスク（傍流）** | コードから生成 | 生成文書の誤推定を独立指摘 | 採否判断 |
| **照合チェック（本筋）** | 食い違いを列挙 | 妥当性検証 | must-fix／should-fix／leave-as-is |

### 11.2 軽量／本格の使い分け

requirements.md Req 5 受入 2 と計画書 §5.10.10 に対応：

| 適用方式 | 内容 | 適用対象 |
|---|---|---|
| **本格適用** | 3 役それぞれが独立して推定・判定（β 逐次方式、§5.9.1） | feature-partitioning 推定（傍流）／ requirements 推定 ／ 照合段階 |
| **軽量適用** | 主役推定の検証として、敵対役が別解釈を 1 つ提示、判定役が比較判定 | design 推定 ／ intent 推察 |

軽量と本格の判断基準：解釈余地の大きさ。

- 解釈余地が大きい（feature-partitioning、requirements、照合食い違い判定）→ 本格適用
- 解釈余地が比較的小さい（design はコードから直接読み取れる、intent は参考情報）→ 軽量適用

### 11.3 §5.9 規律の流用

requirements.md Req 5 受入 3〜8 に対応する流用項目：

| 項目 | 出典 |
|---|---|
| モデル多様化規律、ファイル遮断規律、β 逐次方式 | §5.9.1 |
| 重大度語彙 4 段（CRITICAL／ERROR／WARN／INFO） | §5.9.2 |
| 所見メタデータ必須化（severity／judgment／depth／evidence_type／verifying_commands） | §5.9.3 |
| 3 方式比較データ取得（`findings_by_method`） | §5.9.6 |
| レビューモード語彙（`manual_dogfooding`／`runtime_mediated`／`subagent_mediated`） | foundation Req 6 受入 6 |
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

### 12.3 front-matter の構造

requirements.md Req 6 受入 3〜5 に対応。

```yaml
---
type: conformance_evaluation
target_app: <対象アプリのパス>
target_feature: <feature>
target_commit: <実装コードの commit hash>
date: 2026-06-01
mode_internal: check                     # check / generation（Req 6 受入 3）
author:                                  # §5.4 規律（Req 6 受入 4）
  identity: claude_code_main_session     # または claude_code_subagent
  model: claude-opus-4-7
  role: drafter
reviewer:                                # §5.4 規律（Req 6 受入 4）
  identity: claude_code_subagent
  model: claude-haiku-4-5
  role: final_judgment
  separation_from_author: true
related_artifacts:                       # Req 6 受入 5
  runtime: <runtime の関連実行記録パス>
  evaluation: <evaluation の関連記録パス>
  workflow_management: <workflow-management の関連手続き記録パス>
---
```

### 12.4 関連実行記録への参照

requirements.md Req 6 受入 5 に対応。

- 評価記録から `runtime`／`evaluation`／`workflow-management` の関連実行記録への参照を保持
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

### 13.5 phase_order の最後

requirements.md Req 7 受入 5 に対応。

- 本機能は `phase_order` の最後に位置付ける（依存先がすべて先に完了する前提）
- 計画書 §5.5 の phase_order：foundation → runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation

## 14. 他機能との接合面（Interfaces with Other Features）

### 14.1 foundation との接合面（依存：hard）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | スキーマとメタデータ契約、検証器状態語彙、レビューモード語彙、証拠区分語彙、`adversarial_outcome` 語彙、必須メタデータ（severity／target_location／description／rationale） |
| 再定義しない原則 | foundation を正本所有者として参照し、本機能内で再定義しない（Boundary Context 隣接期待） |

### 14.2 runtime との接合面（依存：review）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 実装コードのレビュー実行記録（`runtime` の出力） |
| 形式 | `<対象アプリ>/.reviewcompass/specs/<feature>/runtime/<日付>-execution.md` 等の実行記録 |
| 活用 | 推定段階での実装コード理解、照合段階での実装コード言及齟齬の判定材料 |

### 14.3 evaluation との接合面（依存：review）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 評価結果との突き合わせ |
| 形式 | `evaluation` 機能の出力（評価結果集約 YAML／JSON） |
| 活用 | 食い違いの妥当性検証、評価結果との整合確認 |

### 14.4 workflow-management との接合面（依存：review）

| 方向 | 内容 |
|---|---|
| 入力（conformance-evaluation が読む） | 所定手続きの実行履歴、上流文書の整合確認 |
| スキーマ依存 | 依存関係の連想配列構造（Req 7 受入 4） |
| 活用 | 既存上流文書の最新性確認（古い文書を引きずらない）、手続き完了状態の確認 |

### 14.5 analysis との接合面

| 方向 | 内容 |
|---|---|
| 出力（conformance-evaluation が書く） | 6 criteria の検査結果、食い違い列挙、推定根拠 |
| 形式 | 評価記録の YAML 構造（`analysis` が機械可読に取り込む） |
| 活用先 | `analysis` の 4 出力先（特に監査用報告と報告書向け原データ、`analysis` Requirement 8 受入 5 由来） |

### 14.6 self-improvement との接合面

| 方向 | 内容 |
|---|---|
| 出力（conformance-evaluation が書く） | 6 criteria の検査結果（規律改善の入力として活用される） |
| 依存方向 | conformance-evaluation → self-improvement（self-improvement が conformance-evaluation の出力を読む、A-008 で確定済み 2026-05-23） |
| 注記 | `self-improvement` は本機能の `depends_on` には含まれず、出力先として参照される関係 |

## 15. 要件追跡表（Requirements Traceability、受入基準単位）

| Requirement | 受入基準 | 対応章節 |
|---|---|---|
| Req 1 機能の方向性と前提 | 受入 1（下流→上流、4 階層対象） | §1 概要／§6.2／§7／§8.1 |
| Req 1 | 受入 2（上流文書なくてもよい） | §1 概要／§6.1 |
| Req 1 | 受入 3（実装適合レビュー非吸収） | §3 範囲外／§17（Boundary Context Out of scope） |
| Req 1 | 受入 4（2 モード） | §5.3 モード切替モデル／§6／§7 |
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
| Req 8 実装適合分離 | 受入 1〜4（性格分離、ディレクトリ分離） | §3 範囲外／§12.2 |

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

## 17. Boundary Context との整合確認（Boundary Context Compliance）

requirements.md の Boundary Context との整合：

### In scope（範囲内）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 主要用途 1（本筋）：照合チェック | §7 照合チェックモード／Decision 2 |
| 主要用途 2（傍流）：文書生成 | §6 文書生成モード／Decision 1 |
| 6 criteria の検査構造 | §8 6 criteria 検査構造／Decision 4 |
| 推定段階と照合段階の両方への 3 役レビュー機構適用 | §11 3 役レビュー機構の適用／Decision 5 |
| モード別の既存文書扱いルール | §5.3 モード切替モデル／§7.3／Decision 3 |
| 評価記録の出力（`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`） | §12 評価記録の type 値と配置 |
| v3-plan §3.3 のうち「文書レベルの戻し」 | §6／§7／§8 |

### Out of scope（範囲外）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 実装適合レビュー | §3 範囲外／Decision 8 |
| v3-plan §3.3 の規律レベル戻し（self-improvement の責務） | §3 範囲外 |
| schema／prompt／code レベルの戻し | §3 範囲外 |
| 5 評価軸のうち実装適合 | §3 範囲外／§8.4 |

### 隣接仕様の期待との整合

| 隣接機能 | Boundary Context の期待 | 本設計での対応 |
|---|---|---|
| foundation（hard） | スキーマとメタデータ契約等を再定義せず参照 | §14.1 |
| runtime（review） | 実装コードのレビュー実行記録を入力源として活用 | §14.2 |
| evaluation（review） | 評価結果との突き合わせ | §14.3 |
| workflow-management（review） | 所定手続きの実行履歴と上流文書の整合確認 | §14.4 |
| analysis | 6 criteria の検査結果を 4 出力先に取り込む | §14.5 |
| self-improvement | 6 criteria 検査結果を規律改善の入力として提供 | §14.6 |

## 18. 機械検査の具体手段（Machine Verification、self-improvement 設計の MV-X と同型）

本章は本機能の動作に関する機械検査ポイントを定義（self-improvement design の §17 と同型の構造）。

### 18.1 検査対象

| 検査 ID | 検査対象 | 検査内容 | 実装方法 |
|---|---|---|---|
| **MV-1** | 評価記録の `type` 値統合 | `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md` の front-matter で `type: conformance_evaluation` が設定されている | grep でフィールド存在を確認 |
| **MV-2** | mode_internal の正しさ | front-matter の `mode_internal` が `check` または `generation` のいずれかである | grep ＋値の照合 |
| **MV-3** | ディレクトリ分離 | 評価記録は `conformance/` ディレクトリ、実装適合レビューは `reviews/` ディレクトリに配置されている（混在なし） | find ＋ディレクトリ照合 |
| **MV-4** | 推定文書の必須 3 節 | `<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/specs/<feature>/` 配下の推定文書が Introduction／Boundary Context／Requirements の 3 節を含む | grep で見出し存在を確認 |
| **MV-5** | 推定根拠の実装コード参照 | 推定文書の各推定要素に実装コードへの参照（`<ファイルパス>:<行範囲>`）が最低 1 件含まれる | grep ＋形式照合 |
| **MV-6** | 既存上流文書遮断の事前検査 | 推定役プロンプトに既存上流文書のパスが含まれていない（照合チェックモード） | grep ＋プロンプトログ確認 |

### 18.2 検査スクリプトの所在と責務

- 第 1 期（フェーズ 1〜3）：手動 grep／find による検査、本機能の責務として運用
- フェーズ 4 第 2 サイクル以降：検査スクリプトを `tools/conformance-evaluation-check.py`（仮称、本機能の所有物）として実装
- `workflow-management` の `tools/check-workflow-action.py`（補助層 C 段階 2）とは責務が異なる

### 18.3 検査の出力先

- 検査結果は評価記録の本文に「機械検査結果」節として記録
- 検査失敗時は遮断（fail-closed）：本機能の処理が継続できない状態とし、利用者監査に上げる

### 18.4 機械検査の段階的導入

- フェーズ 1〜3：MV-1／MV-2／MV-3 は手動 grep、MV-4／MV-5 は文書作成時に人間が確認、MV-6 は推定役プロンプトの手動レビュー
- フェーズ 4 第 1 サイクル：MV-1〜MV-3 を自動化
- フェーズ 4 第 2 サイクル：MV-4〜MV-6 を自動化、推定役プロセスの隔離（§7.3）と連携

## 19. テスト戦略（Test Strategy）

本章は計画書 §5.9.2 のレビュー観点 9「テスト戦略」に対応する。

### 19.1 テスト対象とテストレベル

| モデル | 単体テスト | 結合テスト | 受入テスト |
|---|---|---|---|
| **推定モデル（§9）** | 4 階層の推定アルゴリズム、信頼度判定 | 3 役レビュー機構と推定の連結 | 実装コード規模 1000 行程度のサンプルアプリで推定実施 |
| **比較モデル（§10）** | 3 対応関係（節有無／主張対応／コード言及齟齬）の判定 | 推定結果と既存文書の比較 | 既存上流文書ありのサンプルアプリで照合実施 |
| **モード切替（§5.3）** | check／generation のモード判定、明示指定の処理 | 各モードの実行パイプライン | 両モードの End-to-End 実行 |
| **3 役レビュー機構（§11）** | 軽量／本格の使い分け判定 | 推定段階／照合段階での 3 役連携 | 全 6 criteria の triad-review |
| **評価記録（§12）** | type 値・mode_internal の正しさ、front-matter スキーマ | 評価記録の生成と保管 | 評価記録の機械可読性検証 |
| **依存関係（§13）** | 連想配列構造の解釈、hard／review の区別 | feature-dependency.yaml の読み込み | feature-dependency.yaml の整合確認 |

### 19.2 テスト戦略の重点ポイント

- **既存上流文書の遮断**：推定役プロンプトに既存上流文書の内容が混入していないか、grep で機械検査（MV-6）
- **feature-partitioning の例外扱い**：照合チェックモードで既存 feature-partitioning だけは入力として尊重、他は遮断されていることをテストデータで確認
- **推定の信頼度**：high／medium／low の判定基準が一貫しているかをサンプルデータで確認
- **6 criteria の網羅**：すべての criterion でテストケースが用意されているか、`schemas/review-criteria/conformance_evaluation.yaml` と整合

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

本セッション 27 末時点で本機能の design.drafting 段で未解決の論点：

- **章番号体系の整合確認**：本機能 design.md は self-improvement 設計と同じく 20 章構成（番号なし 5 章＋番号付き §6〜§20 の 15 章）を採用。他機能（foundation／runtime／evaluation／analysis／workflow-management）の design.md でも章番号体系の不整合が存在する可能性があり、design.alignment 段で全機能横断の章構造整合確認が必要（self-improvement 設計の reviews 記録 §4.6 と連動、利用者明示承認「他機能でも生じていたはずなので後ほど対処」2026-05-26 セッション 27）
- **A-005／A-008／A-009／A-010**：既に対処済み（要件段で対処、design 段では追加対処なし）
- **本機能の triad-review 段**：次セッション 28 以降で実施予定、現時点では未着手

### 20.2 機能横断レビューで対処済みの所見

- **A-005（既存）**：依存関係の連想配列構造 → Requirement 7／§13／Decision 6 で反映済み
- **A-008（既存）**：conformance-evaluation から self-improvement への出力方向 → §14.6 で「conformance-evaluation → self-improvement の方向」として明示
- **A-009 第 2 波（既存）**：旧 paper-interface 由来の用語不整合 → Boundary Context 隣接仕様の analysis 記述で対処済み
- **A-010（既存）**：推定プロセスの整理と 2 軸 6 criteria 化 → Requirement 1〜5 ＋計画書 §5.10 改訂で対処済み、本設計で全面反映

### 20.3 起草完了基準

本設計が design.drafting 段の完了とみなされる条件：

- [x] 全 20 章（番号なし 5 章＋番号付き §6〜§20 の 15 章）が記述されている
- [x] requirements.md の全 8 件の Requirement と受入基準が §15 要件追跡表で章節と対応している（受入基準単位の追跡）
- [x] 計画書 §5.10 の 10 小節（§5.10.1〜§5.10.10）の方針が反映されている
- [x] 他機能との接合面が §14 で全 6 機能分（foundation／runtime／evaluation／analysis／workflow-management／self-improvement）明示されている
- [x] Boundary Context との整合が §17 で確認されている
- [x] 機能横断所見（A-005／A-008／A-009／A-010）の対処が §20.2 で明示されている
- [x] 主要な設計決定（8 件）が §16 で明示されている
- [x] **機械検査の具体手段（§18）が定義されている**（self-improvement 設計の §17 と同型）
- [x] **テスト戦略（§19）が定義されている**（self-improvement 設計の §18 と同型）
- [x] 文書生成モード（§6）と照合チェックモード（§7）が明示的に分離されている
- [x] 6 criteria 検査構造（§8）が定義されている
- [x] 推定モデル（§9）と比較モデル（§10）が定義されている
- [x] 3 役レビュー機構の軽量／本格使い分け（§11.2）が明示されている
- [x] 評価記録の type 値と配置（§12）が確定している
- [x] 依存関係の連想配列構造（§13）と確定値が明示されている

本設計の triad-review 段（次セッション 28 以降で実施予定）で扱う観点（Design 観点 10 件、計画書 §5.9.2 由来）：

1. 設計と要件の対応 → §15 要件追跡表
2. 設計の内部整合 → §5 アーキテクチャ／§14 他機能との接合面
3. 設計の他機能との整合 → §14 他機能との接合面
4. 設計の正本との整合 → §17 Boundary Context との整合確認
5. 検証可能性 → §18 機械検査の具体手段／§19 テスト戦略
6. 実装可能性 → §16 設計決定／§9 推定モデル／§10 比較モデル
7. 段階的導入の妥当性 → §18.4 機械検査の段階的導入／§19.3 テスト実施タイミング
8. 拡張余地と将来宿題 → §3 範囲外／§20.1 未解決論点
9. テスト戦略 → §19 テスト戦略
10. リスクと残余課題 → §20.1 未解決論点
