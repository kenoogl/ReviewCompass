# Design Document：conformance-evaluation

最終更新：2026-05-26（セッション 27：design.drafting 起草と triad-review の must-fix 12 件対処、artifact-to-spec conformance evaluation の本筋／傍流分離設計）

## 概要（Overview）

`conformance-evaluation` は ReviewCompass の **7 番目の独立機能** で、本機能の方向は **下流 → 上流（逆方向）**。実装コードから上流文書（intent／requirements／design／tasks）を推定する。先行プロジェクトの `v3-plan.md` で future feature として記録されていた「artifact-to-spec conformance evaluation」を独立機能として継承し、計画書 §5.10 で第 1 期（フェーズ 1〜4）から含めることを確定。

本機能は **2 モード** で動作する：

- **照合チェックモード（本筋）**：仕様駆動開発で構築したコードの要件充足判断。バイアス防止のため二段階方式（推定 → 比較）を採用、既存 feature-partitioning だけは推定時の入力として尊重し、他の既存上流文書は遮断
- **文書生成モード（傍流、人協働）**：既存上流文書のないコードベースに ReviewCompass を導入するための推定支援。完全自動推定は目指さず、機能境界の決定等の本質的判断は人間が担う

要件文書（requirements.md）は 12 件の Requirement で、機能の方向性／文書生成モード／照合チェックモード／6 criteria 検査構造／3 役レビュー機構の流用／評価記録の type 値と配置／依存関係の連想配列構造／実装適合レビューとの分離／実装由来契約の所有候補と仕様更新草案／既存システムへの後追い intent 追加時のコード由来差分抽出／completed follow-up prerequisite set の正式化／正本更新の reopen 引き渡しを求めている。本設計は計画書 §5.10.1〜§5.10.10（機能の性格・評価軸・5 評価軸の整理・評価記録・依存関係・v3-plan 連携・criteria 数・段階的導入・モード別の既存文書扱い・推定段階の triad-review 適用）を実装可能な形に落とし込み、`v3-plan.md` の素材（future feature 記述）から本機能の独立仕様として再設計する。

本設計の所有物は **推定モデル・比較モデル・モード切替モデル・triad-review 適用モデル・評価記録モデル・依存関係モデル・契約所有候補モデル・既存システム差分抽出モデル・completed follow-up 前提セットモデル・reopen 引き渡しモデル** の 10 モデルである。実装適合レビュー（順方向、上流文書がある前提でフェーズ終端で実施）は `analysis` および `runtime` の連携に残し、本機能では吸収しない（§5.10.1）。

## 目標（Goals）

- **照合チェックモード（本筋）** を二段階方式（推定 → 比較）で実装し、既存 feature-partitioning だけは推定時の入力として尊重、他の既存上流文書（intent／requirements／design）は推定時に技術的に遮断する（Req 3、§5.10.9）
- **文書生成モード（傍流）** を人協働の推定支援機能として実装し、機能分割と intent の決定は人間が主導、requirements ／ design は自動推定（Req 2、§5.10.9 (b)）
- **6 criteria 検査構造**（requirements 3 criteria＋ design 3 criteria）を機械可読な検査仕様として整備（Req 4、§5.10.2）
- **3 役レビュー機構** を推定段階と照合段階の両方に適用、軽量／本格の使い分けで運用コストと検証品質のバランスを取る（Req 5、§5.10.10）
- **評価記録の type 値 `conformance_evaluation`** と配置先 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-<mode>.md` を機械可読に確定（Req 6）
- **依存関係の連想配列構造**（`hard`／`review` の 2 値）を `workflow-management` のスキーマ拡張と整合させて表現（Req 7、§5.10.5）
- **実装適合レビューとの分離**を機械検査可能な形で担保（評価記録は `conformance/` ディレクトリ、実装適合レビューは `reviews/` ディレクトリ、Req 8）
- **contract ownership map** と **spec update proposals** により、実装由来契約を requirements.md, design.md, tasks.md の更新候補へ分類し、**draft-only spec update artifacts** として出力する（Req 9）
- **既存システム差分抽出モデル**により、後追い intent、既存 feature-partitioning、既存 requirements／design／tasks、実装コードを突き合わせ、仕様追記候補・設計衝突候補・下流影響候補・実装変更候補を証拠付きで出力する（Req 10）
- **completed follow-up 前提セットモデル**により、D-021 / D-004 / D-005 / D-025 / D-027 / D-008 / D-019 / D-020 / D-023 を completed follow-up prerequisite set として扱い、formal completed follow-up outputs としての責務と相互関係を固定する（Req 11）
- **reopen 引き渡しモデル**により、正本更新が必要な gap を `workflow-management` の reopen 手続きへ渡し、`triad-review / review-wave / alignment / approval` を経るまで resolved 扱いにしない（Req 12）

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
| **既存システム差分抽出（後追い intent）** | 既存 requirements／design／tasks／implementation があり、intent が後から追加または修正された | requirements 候補／design 候補／下流影響候補／実装変更候補 | 追加 intent と既存 feature-partitioning は入力として尊重。既存 requirements／design／tasks は比較入力。tasks は参照入力であり、tasks.md の再作成対象ではない |

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

### 7.10 既存システム差分抽出モード（後追い intent）

Requirement 10 に対応する。既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加した場合、本機能は通常の照合チェックを拡張し、追加 intent と既存仕様・実装コードの関係を候補として抽出する。

入力は、追加または修正された intent、既存 feature-partitioning、既存 requirements／design／tasks、実装コードである。既存 feature-partitioning は照合成立性のため入力として尊重する。既存 requirements／design／tasks は比較入力として読むが、tasks は正式な推定・再作成対象にしない。tasks.md は「下流影響の有無を確認する参照入力」であり、本機能が tasks.md 本体を生成したりタスク分解を確定したりしない。

出力は feature ごとの差分候補一覧で、各候補は最低限次のフィールドを持つ：

```yaml
feature: workflow-management
phase: design
classification: design_conflict_candidate
code_refs:
  - tools/check-workflow-action.py:3068
existing_spec_refs:
  - .reviewcompass/specs/workflow-management/design.md
reasoning_summary: |
  追加 intent を満たすためには、reopen 中に triad-review 前の drafting を明示する必要がある。
needs_human_decision: true
```

`classification` は `existing_sufficient`、`spec_update_candidate`、`design_conflict_candidate`、`downstream_impact_candidate`、`implementation_change_candidate` の 5 値を基本とする。根拠が不足する候補、既存設計と衝突する可能性がある候補、または正式な下流更新要否の判断を要する候補は `needs_human_decision: true` とする。

本モードは仕様本文を直接更新しない。仕様更新草案、下流影響候補、実装変更候補を評価記録に保存し、正式な requirements／design／tasks／implementation 更新は `workflow-management` の reopen 手続きで進める。

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

### 13.6 契約所有候補と仕様更新草案（Contract Ownership and Spec Update Drafts）

Requirement 9 に対応する。照合チェックで見つかった実装由来契約は、食い違い所見として記録するだけでなく、どの仕様文書が所有すべきかを provisional に分類する。

contract ownership map は、各契約について `contract_id`、feature、claim、classification、primary_owner_candidate、secondary_owner_candidate、contract_refs、evidence_refs、related_clusters、source_refs を持つ。owner 候補の値域は requirements、design、operations、tool_contract、test_contract、review_evidence、carry_forward とし、classification は spec-missing、code-missing、mismatch、implementation-detail、ownership-unclear を使う。

spec update proposals は、contract ownership map を対象ファイル単位に畳み込んだ候補である。primary owner が requirements の契約は requirements.md、design の契約は design.md、carry_forward／test_contract／tool_contract の契約は tasks.md を主な反映候補にする。対象ファイルごとに `contract_ids`、`claims`、`needs_human_decision` を保持する。

draft-only spec update artifacts は、`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/<日付>-spec-update-drafts/` に Markdown として出力する。front-matter は `apply_status: draft_only`、`target_file`、`target_kind`、`needs_human_decision` を含む。草案は requirements.md, design.md, tasks.md を直接変更せず、人間が採否判断した後に別手続きで仕様本文へ反映する。

### 13.7 既存システム差分候補と workflow-management 引き渡し

Requirement 10 に対応する。本機能は後追い intent 差分候補を評価記録として出力し、`workflow-management` に正式な reopen 手続きの入力として引き渡す。引き渡し対象は候補一覧、候補ごとのコード参照、既存仕様参照、推定理由、人間判断要否、仕様更新草案、下流影響候補、実装変更候補である。

`workflow-management` に渡す候補の最低フィールドは §7.10 の candidate schema と同じく、`feature`、`phase`、`classification`、`code_refs`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` とする。本機能は `classification` を付けるが、どの phase の正本をいつ変更するか、どの gate で止めるか、どの approval を要求するかは `workflow-management` が決める。

tasks の扱いは境界を固定する。tasks.md は参照入力であり、候補の `phase: tasks` や `classification: downstream_impact_candidate` を出すことはできるが、tasks.md 本体の再作成、タスク分解の確定、正式タスク更新は本機能の責務外である。

### 13.8 Completed follow-up prerequisite set

Requirement 11 に対応する。completed follow-up prerequisite set は、将来計画候補から昇格し、実装・テスト・検証証跡を持つ formal completed follow-up outputs の集合である。対象候補は `D-021 / D-004 / D-005 / D-025 / D-027 / D-008 / D-019 / D-020 / D-023` とする。

このセットは formal completed follow-up outputs の集合である。設計上は、各 output の責務、相互関係、handoff summary との接続を記録し、以後の作業開始判断は本節の範囲外で扱う。

| Gap | Target document | Responsibility |
| --- | --- | --- |
| requirements gap | `.reviewcompass/specs/conformance-evaluation/requirements.md` | completed follow-up prerequisite set の外部可視契約を記録する。 |
| design gap | `.reviewcompass/specs/conformance-evaluation/design.md` | completed follow-up prerequisite set の責務、相互関係、handoff summary との接続を記録する。 |
| handoff summary | `docs/notes/2026-06-09-formal-completed-followup-summary.md` | 実装済み候補一覧、conformance result、残存 gap を保持する。 |

conformance result が `gap_found` の場合でも、候補ごとの実装・テスト・post-write verification・guard 証跡は formal completed follow-up outputs として扱う。ただし requirements gap と design gap は解消済みと見なさず、上表の Target document により明示的に追跡する。

### 13.9 Reopen handoff package

Requirement 12 に対応する。conformance-evaluation は、正本更新が必要な gap を検出した場合でも、requirements.md, design.md, tasks.md を直接書き換えない。正式な正本更新は workflow-management の reopen 手続きに引き渡し、reopen 後の `triad-review / review-wave / alignment / approval` が整合確認を担う。

reopen handoff package は、conformance result と workflow-management の reopen 手続きの間に置く機械可読な引き渡し単位である。最低フィールドは次の通り。

| Field | Meaning |
| --- | --- |
| `source_conformance_record` | gap を検出した conformance 記録への参照。 |
| `gap_ids` | 引き渡し対象の gap または finding ID。 |
| `target_feature` | reopen 対象 feature。 |
| `target_phase` | reopen 対象 phase。requirements / design / tasks / implementation のいずれか。 |
| `target_documents` | 更新候補の正本文書。 |
| `proposed_update_refs` | draft-only spec update artifacts または提案本文への参照。 |
| `needs_human_decision` | 人間判断が必要かどうか。 |
| `change_policy` | 既存項目をできるだけ変更しない方針。値は `minimal_existing_spec_change`。 |
| `change_type` | 更新候補の型。`additive` または `semantic_change`。 |
| `existing_contract_changed` | 既存 requirements/design/tasks の意味変更を含むかどうか。 |
| `human_escalation_required` | 既存項目の意味変更または判断困難な分類を人間判断へ上げるかどうか。 |
| `downstream_reopen_required` | semantic_change により下流 phase の reopen が必要かどうか。 |
| `downstream_reopen_phases` | downstream reopen_required が true の場合の対象 phase。 |
| `next_task_prompt_refs` | 次タスク effective prompt を作るために参照した複数の元資料。 |
| `effective_next_task_prompt_path` | 判定点ごとに 1 本へ束ね、実際に LLM へ読ませる次タスク effective prompt のパス。 |
| `effective_next_task_prompt_sha256` | 読み込んだ次タスク effective prompt 内容の sha256。 |
| `effective_next_task_prompt_loaded` | 次タスク effective prompt を読み込んだかどうか。 |

機械判定は、reopen handoff package の存在、必須フィールド、対象 phase、対象文書、source conformance record への参照、reopen 後の `triad-review / review-wave / alignment / approval` 完了証跡の有無を確認できる。さらに、次タスクプロンプトの元資料参照が存在し、判定点ごとに 1 本の `effective_next_task_prompt_path` が指定され、`effective_next_task_prompt_sha256` が現在内容と一致し、`effective_next_task_prompt_loaded: true` であることを確認する。レビュー判断の意味的妥当性は機械判定だけでは確定せず、reopen 後の通常 review に委ねる。

LLM への方針指示は `change_policy: minimal_existing_spec_change` として固定する。通常は `change_type: additive` を優先し、既存項目の意味変更を避ける。ただし既存項目を絶対に変更してはならないわけではない。既存 requirements/design/tasks の意味変更が必要な場合、または additive で足りるか判断できない場合は `change_type: semantic_change` とし、semantic_change の場合は `human_escalation_required: true`、`existing_contract_changed: true` を要求する。semantic_change が下流実装のやり直しを必要としうる場合は、`downstream_reopen_required: true` と `downstream_reopen_phases` に tasks / implementation などの候補を記録する。この方針は package フィールドだけでなく、機械判定時に読み込む次タスク effective prompt にも含める。`effective_next_task_prompt_loaded: true` は、そのプロンプトが読み込まれたことを示す。

tasks の扱いは境界を固定する。tasks は照合対象外であり、tasks.md 本体の推定・再作成やタスク分解の確定は行わない。一方で、下流影響または実装変更候補がタスク更新を必要とする場合、`phase: tasks` の reopen 候補として package に含めることはできる。tasks.md の正式更新は `workflow-management` の reopen 手続きで判断する。

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
| 出力（workflow-management が読む） | 後追い intent 差分候補、仕様更新草案、下流影響候補、実装変更候補。正式更新は workflow-management の reopen 手続きが所有 |

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
| Req 9 実装由来契約の所有候補と仕様更新草案 | 受入 1（contract ownership map） | §13.6 |
| Req 9 | 受入 2（owner による反映候補分類） | §13.6 |
| Req 9 | 受入 3（spec update proposals） | §13.6 |
| Req 9 | 受入 4（draft-only artifacts） | §13.6 |
| Req 9 | 受入 5（人間判断要否） | §13.6 |
| Req 10 既存システムへの後追い intent 追加時のコード由来差分抽出 | 受入 1（追加 intent と既存仕様・実装コードを入力） | §7.10 |
| Req 10 | 受入 2（requirements/design/下流影響/実装変更候補の抽出） | §7.10／§13.7 |
| Req 10 | 受入 3（候補の最小フィールドと classification） | §7.10 |
| Req 10 | 受入 4（追加 intent と候補の関係記録） | §7.10 |
| Req 10 | 受入 5（固定チェックリストのみで生成しない） | §7.10／§9.4 |
| Req 10 | 受入 6（評価記録の出力構造） | §7.10／§12／§13.7 |
| Req 10 | 受入 7（仕様本文を直接更新しない） | §13.7／§14.4 |
| Req 10 | 受入 8（ReviewCompass 自身の試行実行） | §20.2／§20.3 |

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
- **2026-06-08 の requirements 再確認への対応**：intent の「レビュー収集処理を事前設定の写像にしない」意図は、§7 照合チェックモード、§9 推定モデル、§10 比較モデル、§13.6 契約所有候補と仕様更新草案で受けられるため、設計構造の追加は不要と確認
- **2026-06-09 の後追い intent 追加への対応**：既存システムに intent を後から追加した場合のコード由来差分抽出は、§7.10 既存システム差分抽出モード、§13.7 workflow-management 引き渡し、§14.4 接合面に反映した。これは 2026-06-09 の pre-drafting gap audit で確認された design drafting 漏れへの本線対処である
- **2026-06-09 の completed follow-up 前提セット正式化**：D-021 / D-004 / D-005 / D-025 / D-027 / D-008 / D-019 / D-020 / D-023 は completed follow-up prerequisite set として §13.8 に反映した。handoff summary は `docs/notes/2026-06-09-formal-completed-followup-summary.md` とする
- **2026-06-09 の reopen 引き渡し方針正式化**：正本更新が必要な gap は §13.9 の reopen handoff package として `workflow-management` の reopen 手続きへ渡し、`triad-review / review-wave / alignment / approval` 完了前に resolved 扱いにしない。tasks は `phase: tasks` 候補として扱えるが、tasks.md 本体の推定・再作成やタスク分解の確定は行わない。既存項目の意味変更は `minimal_existing_spec_change` 方針の下で `semantic_change` と分類し、人間判断へエスカレーションする

### 20.3 起草完了基準

本設計が design.drafting＋triad-review 段の完了とみなされる条件：

- [x] 全 20 章（番号なし 5 章＋番号付き §6〜§20 の 15 章）が記述されている
- [x] requirements.md の全 12 件の Requirement と受入基準が §15 要件追跡表で章節と対応している（受入基準単位の追跡、F-001 部分対処：Req 8 を受入単位で展開、Req 9 を §13.6 に追加、Req 10 を §7.10／§13.7 に追加、Req 12 を §13.9 に追加）
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

## 実装由来契約の波及トレース

- `XDI-CE-001`：cross-feature drift clustering と contract ownership outputs は、design.md §13.6 の契約所有候補と仕様更新草案の派生運用として追跡する。follow-up implementation decision の正本は tasks.md T-015 とし、本 design.md は設計層から追跡可能であることを示す。
- `XDI-CE-002`：既存システムに後追いで intent を追加した場合のコード由来仕様差分抽出、既存設計との衝突確認、仕様更新草案、下流影響候補、実装変更候補の分離は、design.md §7.10 の既存システム差分抽出モード、§13.7 の workflow-management 引き渡し、§14.4 の接合面で追跡する。tasks.md 本体の推定は本機能の責務外であり、正式な tasks 反映は workflow-management の reopen 手続きに委ねる。
- `XDI-CE-003`：completed follow-up prerequisite set、formal completed follow-up outputs、requirements gap／design gap の Target document、各 output の責務と相互関係は design.md §13.8 で追跡する。handoff summary は `docs/notes/2026-06-09-formal-completed-followup-summary.md` とする。
- `XDI-CE-004`：正本更新が必要な gap の reopen 引き渡し、reopen handoff package、`triad-review / review-wave / alignment / approval` 完了前に resolved 扱いにしない制約、`phase: tasks` 候補の境界、`minimal_existing_spec_change`、`additive`／`semantic_change` 分類、`existing_contract_changed`、`human_escalation_required`、`downstream_reopen_required`、`next_task_prompt_refs`、`effective_next_task_prompt_path`、`effective_next_task_prompt_sha256`、`effective_next_task_prompt_loaded` は design.md §13.9 で追跡する。
