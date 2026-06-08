# Design Document：self-improvement

最終更新：2026-05-26（セッション 27：design.drafting 起草と triad-review の must-fix 13 件対処、章番号体系を 20 章に拡張、workflow 層改善に特化した全面書き直し設計）

## 概要（Overview）

`self-improvement` は ReviewCompass の改善機能の **設計層** であり、第 1 期では **workflow 層改善のみ** を担う。先行プロジェクトの自己改善仕様（130 行 8 要件、主に runtime 層改善向け）は workflow 改善の性格に合わないため、計画書 §5.16 で全面書き直しが確定済み。

本機能の中核責務は **規律と実体の双方向同期** である。規律違反データと実体運用パターンを観察し、「規律を実体に追従させる」か「実体を規律に追従させる」かを判断する。判断結果は提案（YAML 形式）として記述し、3 検証方法で確かめてから利用者監査で承認、採用後は学習データとして履歴保管する。

要件文書（requirements.md）は 8 件の Requirement で、役割と性格／入力源／提案単位／提案構造／検証／承認／履歴ロールバック／効果測定を求めている。本設計は計画書 §5.16.1〜§5.16.12（役割・入力・提案単位・提案構造・検証・承認・履歴ロールバック・効果測定・スコープ・命名・旧モジュール・段階的導入）を実装可能な形に落とし込み、先行プロジェクト `dual-reviewer-self-improvement` の素材設計（526 行、Input Model／Signal Extraction Model／Proposal Model／Replay and Backtest Model 等）から **継承可能な 4 モジュール＋ workflow 改善向けの新規 4 モジュール** として再設計する（計画書 §5.16.11）。

本設計の所有物は **入力モデル・signal_extraction モデル・提案モデル・検証モデル・承認モデル・履歴ロールバックモデル・効果測定モデル** の 7 つのモデルである。規律ファイルの実体変更は `workflow-management` の所定手続き（drafting → review → approval）経由で実行する（A-007 案 2、Requirement 1 受入 4、2026-05-23 利用者承認）。本機能は **規律変更の提案権** を持ち、**実体変更権** は workflow-management に委ねる責務分離の構造を取る。

## 目標（Goals）

- **規律と実体の双方向同期** を設計レベルで具体化：規律違反データと実体運用パターンの両側からの観察、双方向の追従判断、判断結果の提案化を支援する
- **5 種類の提案単位に限定** し、提案対象を本機能が所有する規律のみに絞る（runtime プロンプト・スキーマ等は対象外、計画書 §5.16.3）
- **YAML 形式の提案構造** を機械可読な形で標準化し、`analysis` および利用者監査者が機械的に処理できる形を保つ（Req 4）
- **3 検証方法**（過去データへの遡及シミュレーション／パイロット運用／影響範囲の事前分析）を支え、replay／backtest（runtime 改善向け）を採用せず別形式で代替する（Req 5、§5.16.5）
- **フェーズ境目の利用者監査** で提案をまとめて判断し、session 内の連続承認を強制しない（Req 6 受入 1）
- **履歴の追跡可能性とロールバック可能性** を 4 サブディレクトリ配置（`learning/workflow/` 配下）で担保する（Req 7、§5.16.7）
- **効果測定 7 指標**（§5.9.5 由来 3 指標＋ workflow 改善運用 4 指標）を支え、`analysis` への機械可読出力を提供する（Req 8、§5.16.8）
- **規律変更権と実体変更権の分離** を機械検査可能な形で担保し、自己承認の空洞化（self-improvement が直接ファイル書き換えを行うリスク）を防ぐ（Req 1 受入 4、A-007 案 2、機械検査の具体手段は §17 で定義）

## 範囲外（Non-Goals）

- 他 4 層改善（prompt／policy／schema／runtime）：フェーズ 4 完了後の別計画書、本設計のスコープ外（計画書 §7）
- replay／backtest（runtime 改善向け）：3 つの代替検証手段で代替（§5.16.5、Req 5 受入 4）
- 規律ファイル（`docs/disciplines/discipline_*.md`）の実体書き換え：本機能は提案権のみを持ち、実体変更は workflow-management の所定手続き経由（A-007 案 2、Req 1 受入 4）
- 旧 R6 の論文化からの分離：方針継承のみ、個別の規律ファイルとして立てない（計画書 §5.16.9）
- 外部プロジェクトからの取り込み証跡（旧 R8）：フェーズ 4 完了後、外部プロジェクトとの規律共有時に検討（計画書 §5.16.9）
- runtime プロンプト・schema・config の改修提案：本機能の対象外（Req 3 受入 2）
- `learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリ：他 4 層改善で活用予定、第 1 期では空置き（§5.16.10、Boundary Context Out of scope 由来）
- 規律ファイル所有先パスと実体配置の整合検査：workflow-management の責務（A-007 由来、本機能の Req 1 受入 4 で参照のみ）

## 設計の前提（Design Drivers）

- workflow 改善は **規律と実体の双方向同期** の性格を持ち、runtime 改善で使う replay／backtest（過去入力に対する出力の再現）が使いにくい。規律は「人間が守るべきルール」であり、実体運用との乖離を観察するには時系列の累積データが必要（計画書 §5.16.5）
- LLM が文脈圧力下で規律違反を起こす失敗モード（§5.8 第 1 層の限界）への対処：規律と実体の乖離を能動的に観察し、乖離が累積した段階で提案として記述する（事後的なフィードバックループ）
- **規律変更権と手続き実行権の分離**：自己承認の空洞化（self-improvement が独自に規律を書き換える）を構造的に防ぐため、提案権と実体変更権を異なる機能（self-improvement と workflow-management）に分散させる（A-007 案 2、Req 1 受入 4）
- 学習データの 4 サブディレクトリ配置（`learning/workflow/proposals/`／`approved-updates/`／`rejected-updates/`／`rollback/`）：提案の状態遷移を物理ディレクトリで明示し、機械検査と人間の目視確認の両方を支援
- 他層改善（prompt／policy／schema／runtime）で活用予定の 3 ディレクトリ（`learning/findings/`／`backtests/`／`templates/`）は第 1 期では空置き：将来の拡張余地を残しつつ、第 1 期スコープを `learning/workflow/` のみに限定（§5.16.10）
- 効果測定 7 指標の手動集計を許容（フェーズ 4 第 3 サイクルまで自動化を段階的に進める、Req 8 受入 5）

## アーキテクチャ（Architecture）

### 1. データの流れ

```
[入力源]
  ├── レビュー記録の規律違反検出結果（foundation Req 6 受入 1〜2 由来）
  ├── 規律遵守検査の結果（各規律の evidence_check_method 実行結果）
  ├── フェーズ境目の利用者監査での指摘
  ├── 実体運用で新たに観察された運用パターン
  └── 規律違反の累積データ（docs/discipline-compliance-reports/）
       ↓
[input_model（新規実装、§6）]
  └── 来歴情報（source／location／observation）を付与、時系列保持
       ↓
[signal_extraction（新規実装、§7）]
  └── 規律と実体の乖離を抽出、提案候補を生成
       ↓
[proposal_model（新規実装、§8）]
  └── 5 種類の提案単位に分類、YAML 形式で記述
       ↓
[replay_backtest_model 相当（新規実装、§9）]
  ├── 過去データへの遡及シミュレーション
  ├── パイロット運用（aspirational ステータス）
  └── 影響範囲の事前分析
       ↓
[利用者監査（フェーズ境目、§10）]
  ├── 採用：approved
  ├── 却下：rejected
  └── 後続提案で上書き：superseded（reopen-procedure 5 ステップ準拠）
       ↓
[decision_adoption_model（継承）]
  └── 規律状態管理、workflow-management への手続き入力
       ↓
[workflow-management（外部、所定手続き drafting → review → approval）]
  └── docs/disciplines/ の実体変更を実施
       ↓
[learning_layout（継承、§11）]
  └── learning/workflow/ 配下に履歴保管
       ↓
[rollback_model（継承、§11）]
  └── 必要に応じてロールバック（git 履歴活用）
       ↓
[pipeline_driver（継承）]
  └── 全体パイプライン制御
       ↓
[効果測定（7 指標、analysis へ出力、§12）]
```

### 2. 責務分担モデル

| 機能 | 責務 | 本設計での扱い |
|---|---|---|
| **self-improvement** | 規律の論理的正本所有者、変更の提案権、3 検証実施、効果測定 7 指標の集計 | 本機能の中核責務、本設計が定義 |
| **workflow-management** | 規律ファイル `docs/disciplines/discipline_*.md` の実体変更を所定手続き（drafting → review → approval）経由で実行 | 外部機能、本機能は手続き入力を渡すのみ（A-007 案 2、Req 1 受入 4） |
| **foundation** | 規律検査スキーマ、レビューモード語彙、状態軸語彙の正本所有 | 上流機能、再定義せず参照 |
| **runtime** | 規律遵守検査の結果（レビュー記録の機械検査出力）の生成 | 上流機能、本機能は出力を直接消費 |
| **evaluation** | 規律違反データの集計と評価結果の生成 | 上流機能、本機能は出力を直接消費 |
| **analysis** | 効果測定 7 指標を読み物（運用ダッシュボード／監査報告等）に取り込み | 下流機能、本機能は機械可読形式で出力 |
| **conformance-evaluation** | 規律遵守検査の上流文書との適合性評価結果の生成 | 上流機能、本機能は出力を活用可能 |

### 3. 旧モジュールとの対応

計画書 §5.16.11 に従い、旧 dual-reviewer-rebuild の 8 モジュールを次のとおり扱う（言語非依存の設計層として記述、実装言語は将来の実装段で決定）：

| 旧モジュール | 旧規模 | 扱い | 本設計での対応 |
|---|---|---|---|
| `input_model`（647 行） | 大 | **新規実装** | 規律違反検出と実体パターン抽出に特化、Input Model（§6）で再定義 |
| `proposal_model`（542 行） | 大 | **新規実装** | 5 種類の提案種別に特化、Proposal Model（§8）で再定義 |
| `replay_backtest_model`（465 行） | 中 | **新規実装（別形式）** | 過去遡及シミュレーション／パイロット運用／影響範囲分析の 3 手段、Verification Model（§9）で再定義 |
| `signal_extraction`（397 行） | 中 | **新規実装** | 規律遵守検査結果を入力、signal_extraction Model（§7）で再定義 |
| `decision_adoption_model`（323 行） | 中 | 継承可能 | 規律状態管理、Approval Model（§10）で活用 |
| `rollback_model`（303 行） | 中 | 継承可能 | git 連携、History and Rollback Model（§11）で活用 |
| `pipeline_driver`（169 行） | 小 | 継承可能 | パイプライン制御、Architecture §1 で活用 |
| `learning_layout`（156 行） | 小 | 継承可能（調整） | 成果物配置、ディレクトリ構造は `learning/workflow/` 配下に調整（§11） |

つまり 8 モジュールの **半分（後者 4 件）は継承、前者 4 件は workflow 改善向けに新規実装**。継承範囲（どのロジック／データ構造／インターフェースを継承するか）の具体は実装段で詳細化する（現段階では責務領域の継承を意味する）。

## 6. 入力モデル（Input Model）

### 6.1 入力源（5 種類）

requirements.md Req 2 受入 1 に対応する 5 種類の入力源：

| 番号 | 入力源 | 由来 | 形式 |
|---|---|---|---|
| 1 | レビュー記録の規律違反検出結果 | `foundation` Req 6 受入 1〜2 の必須メタデータ検査出力 | レビュー記録の front-matter |
| 2 | 規律遵守検査の結果 | 各規律の `evidence_check_method` の実行結果 | `docs/discipline-compliance-reports/<日付>.yaml` |
| 3 | フェーズ境目の利用者監査での指摘 | 利用者監査者からのフィードバック | 自由記述（手動収集、将来は YAML 化検討） |
| 4 | 実体運用で新たに観察された運用パターン | セッション内の運用記録、コミットメッセージ、TODO の確定事項 | 手動抽出（フェーズ 4 第 3 サイクルで自動化検討） |
| 5 | 規律違反の累積データ（時系列） | `docs/discipline-compliance-reports/` の時系列保管 | YAML（時系列） |

### 6.2 来歴情報の構造

requirements.md Req 2 受入 2 に対応する来歴情報の 3 要素：

```yaml
source: review_record           # review_record / compliance_report / observation_pattern / user_audit
location: foundation/.../review-2026-05-13.md   # 証跡ファイルへの相対パス
observation: |
  「主役 Sonnet・敵対役 Opus・判定役 Opus」が複数レビューで一貫して使われている
  （30 文字以上の自由記述、観察した運用パターンの概要）
```

入力源 5 種類のうち、`source` フィールドの値は次の対応関係を持つ（F-007 対処：入力源 4 を独自 source 値に分離）：

| 入力源 | source 値 |
|---|---|
| 1. レビュー記録の規律違反検出 | `review_record` |
| 2. 規律遵守検査の結果 | `compliance_report` |
| 3. フェーズ境目の利用者監査 | `user_audit` |
| 4. 実体運用パターン（手動抽出） | `observation_pattern`（独自値、入力源 5 と区別） |
| 5. 累積データ（時系列） | `compliance_report` |

### 6.3 時系列性の保持

- 入力データの時系列性を保持し、累積データから傾向を抽出可能にする（Req 2 受入 3）
- `docs/discipline-compliance-reports/` 配下の日付付き YAML（例：`2026-05-26.yaml`）が時系列の正本
- 傾向抽出は signal_extraction の責務（§7）、本モデルは時系列の保持と読み出しを担う

### 6.4 上流機能の出力を直接消費

- 入力源を再定義せず、上流機能（`runtime`／`evaluation`／`workflow-management`／利用者監査）の出力を直接消費する（Req 2 受入 4）
- 入力スキーマの所有者は上流機能、本機能は **読み手** に徹する
- 上流機能の出力形式が変わった場合、本機能の入力モデルも追従するが、独自の再定義は行わない
- ReviewCompass の dogfooding で使う持ち越し台帳など、プロジェクト固有の状態ファイルは一般規律として扱わない。workflow 側へ渡す場合は `required_inputs` の抽象 ID（例：`unresolved_cross_scope_items`）と `source_type`、`read_policy`、resolver の組として表現し、配布先プロジェクトでは別ファイル、外部台帳、または未配置に解決できるようにする。台帳内容そのものの一般化は tasks T-012 で扱い、固有語彙は `evidence_refs` または `project_local_context` に隔離する

## 7. signal_extraction モデル（Signal Extraction Model）

本章は F-004（must-fix）対処として新設（2026-05-26 セッション 27、利用者明示承認「候補 1」）。新規実装 4 モジュールの 1 つで、規律と実体の乖離を能動的に抽出する責務を持つ。

### 7.1 役割と入出力

- **役割**：input_model（§6）の出力から「規律と実体の乖離」を抽出し、提案候補を生成する
- **入力**：input_model が付与した来歴情報付きの 5 種類の入力（§6.1）
- **出力**：proposal_model（§8）への提案候補（規律 ID／実体観察データ／乖離の性格／提案種別の候補）

### 7.2 乖離抽出の判断基準

signal_extraction が「規律と実体の乖離」と判断する基準（4 種類）：

| 種別 | 判断基準 | 例 |
|---|---|---|
| **規律不在型** | 実体運用に定常的パターンがあるが、対応する規律ファイルが存在しない | 主役 Sonnet ／敵対役 Opus ／判定役 Opus のモデル能力配分が複数レビューで一貫している（規律化前） |
| **規律違反型** | 規律違反検出が一定件数（既定 3 件）以上累積している | dominated 案を提示した違反が複数応答で発生 |
| **規律形骸化型** | 規律は存在するが、参照件数がゼロまたは違反検出がゼロのまま長期間（既定 5 セッション以上）が経過 | 旧 23 パターン規律が `discipline_review_judgment_patterns.md` で参照ゼロ |
| **規律衝突型** | 複数規律間で内容が衝突または重複している | 旧 dominant-dominated-options と choice-presentation が同一の「複数案提示」場面に適用される |

### 7.3 抽出アルゴリズム（概要）

第 1 期では **半自動** で実施（自動部分は grep ベースの軽量検査、判断部分は人間または LLM）：

1. **入力読み込み**：input_model の出力（5 種類の入力源の来歴付きデータ）を時系列で読む
2. **パターン認識**：実体運用パターン（入力源 4 と 5）を grep／頻度分析で抽出
3. **規律突き合わせ**：抽出したパターンを `docs/disciplines/` の active 必読／参照層と機械的に突き合わせる
4. **乖離判定**：4 種類の判断基準に分類
5. **提案候補生成**：乖離ごとに `proposed_change` の素案を生成し、proposal_model（§8）に渡す

実装段の詳細化（フェーズ 4 第 1 サイクル）：
- grep パターンの正規化
- 頻度分析の閾値（既定 3 件、5 セッション）の調整
- LLM 呼び出しによる規律衝突検出の高度化

### 7.4 出力形式

signal_extraction の出力は proposal_model（§8）への入力として次の構造を持つ：

```yaml
signal_id: SE-001                              # signal_extraction の通し番号
signal_type: discipline_absence               # discipline_absence / discipline_violation / discipline_obsolete / discipline_conflict
observed_pattern: |
  「主役 Sonnet・敵対役 Opus・判定役 Opus」が複数レビューで一貫
related_disciplines: []                        # 既存規律へのパス、衝突型／形骸化型で必須
proposed_proposal_type: new_discipline         # proposal_model への種別候補
motivating_evidence_seed:                      # proposal_model の motivating_evidence の素材
  - source: review_record
    location: foundation/.../review-2026-05-13.md
    observation: 17 件のレビューでモデル能力配分が一貫
extracted_at: 2026-05-26T05:55:00+09:00
```

## 8. 提案モデル（Proposal Model）

### 8.1 提案単位（5 種類）

requirements.md Req 3 受入 1 に対応する 5 種類の提案単位：

| 提案種別（proposal_type） | 内容 | 例 |
|---|---|---|
| `new_discipline` | 新規規律の起案 | モデル能力配分規律の新設、本セッション 27 の事前検査宣言義務規律の新設 |
| `update` | 既存規律の更新 | 規律本文の語彙統一、項目追加 |
| `status_change` | 規律のステータス変更 | enforced ↔ aspirational の切り替え |
| `archive` | 規律の archive 退避（撤廃） | 23 パターン規律の archive 退避、no-unilateral-action の撤去 |
| `consolidation` | 規律間の統廃合 | 旧 dominant-dominated-options と choice-presentation を統合し discipline_options_presentation.md に集約 |

### 8.2 提案対象の限定

- 提案対象は **本機能が所有する規律のみ**（runtime プロンプト・スキーマ等は対象外、Req 3 受入 2）
- 規律の正本配置：`docs/disciplines/discipline_*.md`
- 範囲外の規律候補（runtime 層）はフェーズ 4 完了後の他層改善で扱う

### 8.3 提案種別の組み合わせ

- 提案種別の組み合わせを許容（Req 3 受入 3）
- 例：新規規律の追加と既存規律の archive 退避を **縮減義務** として 1 提案にまとめる（§5.8 第 5 層の処理表面積抑制方針）
- 実例（本セッション 27）：discipline_options_presentation.md の新設（new_discipline）と旧 dominant-dominated-options ／ choice-presentation の archive 退避（archive ×2）を 1 提案として処理した

### 8.4 提案構造（YAML）

requirements.md Req 4 受入 1〜5 に対応する提案構造（G2／G4／G6 対処を含む）：

```yaml
proposal_id: WP-001                                # 必須、Workflow Proposal の通し番号（§8.5）
proposal_type: new_discipline                      # 必須、5 種類のいずれか
target_discipline_path: docs/disciplines/discipline_model_capability_allocation.md   # 必須、対象規律パス（単数）。pattern 制約 ^docs/disciplines/discipline_.*\.md$ で本機能所有の規律に限定（topic-109／F-014、提案対象の限定を機械強制。MV-1 と併せ二重ゲート）
source_discipline_paths:                           # consolidation のときのみ必須、複数の統合元規律
  - docs/disciplines/archive/2026-05-26-consolidation/discipline_dominant_dominated_options.md
  - docs/disciplines/archive/2026-05-26-consolidation/discipline_choice_presentation.md
motivating_evidence:                               # 必須、配列
  - source: review_record
    location: foundation/.../review-2026-05-13.md
    observation: |
      「主役 Sonnet・敵対役 Opus・判定役 Opus」が複数レビューで一貫して使われている
  - source: compliance_report
    location: docs/discipline-compliance-reports/2026-05-20.yaml
    observation: |
      文書化されていない運用パターンが定常化
proposed_change: |                                 # 必須、提案する変更の本文
  以下の新規規律を作成：
  - 主役と敵対役は必ず異なるモデルを使う（敵対役の独立性確保のため）
  - 判定役は主役または敵対役と同モデル許容
  - 敵対役と判定役には能力配分要件あり
  - 機械検査で確認
expected_effect:                                   # 必須、期待される効果
  - 3 役の独立性が機構として担保される
  - レビュー品質の向上
statistical_evidence:                              # 任意、統計的証拠が可能な場合
  observed_runs: 17
  consistent_pattern_ratio: 100%
depends_on: []                                     # 任意、先行採用が前提の他提案 ID（A-006 対処、将来用途）
superseded_by: null                                # 任意、後続提案で上書きされた場合に WP-NNN を記録（§8.7）
superseded_at: null                                # 任意、ISO 8601 形式（§8.7）
reopen_reason: null                               # 任意、superseded 遷移の理由（§8.7、reopen-procedure 5 ステップの 1 つ）
materialized_at: null                              # 任意、ISO 8601 形式（§13.5 で詳述）
materialization_commit_hash: null                  # 任意、workflow-management の実体変更コミットのハッシュ（§13.5）
status: pending                                    # 必須、4 値のいずれか（§8.6）
```

### 8.5 proposal_id の発番ルール（A-002 対処、本セッション 27 確定）

- **採番権者**：**self-improvement**（提案権を持つ機能が採番）
- **名前空間**：接頭辞で分離
  - `WP-NNN`：Workflow Proposal（本機能の提案）
  - `RB-NNN`：Rollback Proposal（§11）
  - 将来の他層改善で `PP-NNN`：Prompt Proposal 等を追加可能
- **通番リセット**：**なし**（時系列で通番増加、年度／フェーズで振り直さない、git 履歴で時系列が追えるため）
- **通番桁数**：3 桁から開始、999 件を超えたら自動で 4 桁に拡張
- **採番手順**：新規提案作成時に **全 4 ディレクトリ（`learning/workflow/` 配下の `proposals/`／`approved-updates/`／`rejected-updates/`／`rollback/`）を走査した最大番号＋ 1** を採用（topic-99／G-002 対処、2026-05-29 セッション 39）。`proposals/` のみを走査すると、承認・却下・上書きされた提案が §10.5 の git mv で他ディレクトリへ移動した後に番号が `proposals/` から消え、採番が重複して上記「通番リセットなし」の設計意図に反するため。ロールバック採番（RB-NNN、§11）も同様に全 4 ディレクトリ走査の最大番号＋ 1 を採る

### 8.6 status の 4 値と遷移

requirements.md Req 4 受入 4 に対応する status 4 値の遷移（A-007 対処を含む）：

```
pending（提案レビュー前）
   ├── approved（承認・採用済み）
   │     └── superseded（後続提案で上書き、過去の approved が無効化、reopen-procedure 5 ステップ準拠）
   └── rejected（却下）
```

各値の意味と計画書 §5.16.6 の自然言語語彙との対応：

| status 値 | 意味 | 計画書 §5.16.6 の対応 |
|---|---|---|
| `pending` | 提案レビュー前 | 「提案レビュー」段 |
| `approved` | 承認・採用済み（承認時点で採用扱い、ただし実体変更は workflow-management が別途実施） | 「承認」「採用」 |
| `rejected` | 却下 | 「却下」 |
| `superseded` | 後続の `approved` 提案により上書き済み | 計画書語彙に対応なし、本仕様で独自追加 |

採用率 ＝ `(approved + superseded) / (approved + rejected + superseded)`（pending は分母から除外、決定済み提案のうちの採用率を計算する設計意図、F-013 対処）。**分子・分母の両方に `superseded` を含める**（topic-102／F-003 対処、案 2、2026-05-29 セッション 39）：`superseded`（後続提案で上書き済み）は却下されたのではなく一度は採用された提案であり、規律の継続的改善（上書き）のたびに却下なしで採用率が下がる不条理（改善を罰する指標）を避けるため、分子にも算入する。§12.1・§12.5 と一貫させる。

### 8.7 superseded 遷移の reopen-procedure 5 ステップ（A-007 対処、必須）

過去の `approved` 提案を `superseded` に遷移させる場合、規律 [reopen-procedure-for-settled-topics] の 5 ステップを必須とする（active 必読規律の遵守）：

1. **再オープンの宣言**：後続提案の中で「過去の WP-NNN を `superseded` に遷移させる」旨を `proposed_change` に明示宣言
2. **再考の理由を述べる**：`superseded` 遷移の理由を `reopen_reason` フィールドに記述（必須、自由記述）
3. **新しい結論案の提示**：後続提案 WP-MMM 自体が新結論案
4. **明示承認の取得**：`superseded` 遷移そのものに対する利用者明示承認を取得（後続提案 WP-MMM の承認とは別建て）
5. **再オープン履歴の記録**：旧 `approved` 提案 YAML を次のとおり更新
   - `status: approved` → `status: superseded`
   - `superseded_by: WP-MMM`（後続提案の ID）
   - `superseded_at: <ISO 8601>`
   - `reopen_reason: <理由>`

機械検査ポイント（§17）：`status: superseded` の提案 YAML に `superseded_by`／`superseded_at`／`reopen_reason` のすべてが存在することを grep で検査。

### 8.8 提案種別ごとの追加要件

requirements.md Req 3 受入 5 と Req 6 受入 3〜4 に対応する追加要件：

| 提案種別 | 追加要件 |
|---|---|
| `archive` | **撤廃 README 必須**（撤廃理由を `docs/disciplines/archive/<日付>-<id>/README.md` に記録、本セッション 27 の `2026-05-26-consolidation/README.md` が実例） |
| `consolidation` | **対応表必須**（`source_discipline_paths` 配列＋撤廃 README 内の対応表記述、§8.4） |
| `new_discipline` | 提案する規律本文のドラフトと、関連既存規律との関係を明示 |
| `update` | 変更箇所の diff（または変更前後の対照表） |
| `status_change` | ステータス変更の根拠（aspirational → enforced の場合は遵守率の証拠 statistical_evidence、enforced → aspirational の場合は降格理由） |

### 8.9 統計的証拠（任意）

- 統計的証拠が可能な場合、`statistical_evidence` フィールド（`observed_runs`／`consistent_pattern_ratio` 等）を追加する（Req 4 受入 5）
- `status_change`（aspirational → enforced）の場合、`statistical_evidence` で遵守率の証拠を必須付与する（§8.8）
- **責務境界（topic-100／G-003 対処、2026-05-29 セッション 39）**：提案モデル（§8、tasks T-004）は `statistical_evidence` の **存在の検証のみ**を担い、その中身（遡及シミュレーションによる違反検出率等）の**生成は検証モデル（§9.2、tasks T-005）の責務**である。したがってタスク依存順は提案モデル → 検証モデル（T-004 → T-005、データの流れ §5.1「提案 → 検証」どおり）でよく、依存逆転には当たらない。実行時に実際の `status_change` 提案を完成させる際は T-005 の生成物を用いる
- 任意フィールドのため、観察データが不足する初期段階では省略可能

## 9. 検証モデル（Verification Model）

### 9.1 3 つの検証方法

requirements.md Req 5 受入 1 に対応する 3 検証方法：

| 検証方法 | 内容 | 適用例 |
|---|---|---|
| **過去データへの遡及シミュレーション** | 過去レビュー記録に新規律を当てて違反検出率を計算 | モデル能力配分規律を過去レビュー 17 件に当てて遵守率 100% を確認 |
| **パイロット運用** | 新規律を `status: aspirational` で一定期間運用、遵守率を観察してから `enforced` 昇格 | 新規律を 5〜10 セッション運用、遵守率 **90%** 以上なら昇格判定 |
| **影響範囲の事前分析** | 既存規律との衝突、撤廃予定規律との関係を機械検査 | 内部リンク `[[name]]` 形式の参照を grep で全件確認、影響範囲を把握 |

### 9.2 過去データへの遡及シミュレーション

- 対象データ範囲を提案ごとに明示（Req 5 受入 2）
- 例：「過去レビュー 17 件、過去遵守検査 30 件」を対象範囲として提案に併記
- 違反検出率の計算：新規律を仮適用したときに違反となる件数 ／ 対象件数
- 「仮適用」の手順（フェーズ 1〜3 は手動、フェーズ 4 第 2 サイクルで自動化）：
  1. 規律ドラフトを `docs/disciplines/discipline_*.md.draft` として配置（仮配置）
  2. 過去レビュー記録を順に読み、規律ドラフトの基準で違反判定（人間または LLM）
  3. 違反件数と対象件数を集計
  4. 結果を提案 YAML の `statistical_evidence` に記録
- 過去データの取得元：`.reviewcompass/specs/<feature>/reviews/` 配下、`docs/discipline-compliance-reports/` 配下

### 9.3 パイロット運用

- 新規律を `status: aspirational`（機械検査なし、運用目標）で一定期間運用（Req 5 受入 3）
- パイロット運用期間を提案ごとに記録（例：5 セッション、または 2 週間）
- 期間中の遵守率推移を保持（時系列で `docs/discipline-compliance-reports/` に集約）
- 期間終了時に遵守率が **閾値 90%** 以上を満たせば `enforced` 昇格判定（A-009 対処、2026-05-26 セッション 27 利用者明示承認「90%」）
- 閾値 90% は経験則として暫定設定。フェーズ 4 第 3 サイクル以降の運用データで調整。本セッション 27 までに採用した規律（active 必読 12 件＋参照層 3 件）はすでに enforced 扱いのため、本閾値は新規規律の昇格判定に適用される

### 9.4 影響範囲の事前分析

- 既存規律との衝突：内部リンク `[[name]]` 形式の参照を grep で全件確認（本リポジトリの規律ファイルで実用済み、F-011 の事実誤認は敵対役の確認で訂正）
- 撤廃予定規律との関係：archive 対象の規律と新規律の重複範囲を機械検査
- 衝突の定義：（a）名称重複、（b）内容重複（同一場面に適用される規律で文言が異なる）、（c）参照関係の循環
- 機械検査の実装はフェーズ 4 第 1 サイクル以降（フェーズ 1〜3 は手動）

### 9.5 検証不能な提案の扱い

- replay／backtest（runtime 改善向け）を採用しない（Req 5 受入 4）
- 3 つの代替検証手段が機能しない提案は、**利用者監査での明示的判断** で承認する
- 検証不能の根拠を提案の `motivating_evidence` または `proposed_change` に明示

## 10. 承認モデル（Approval Model）

### 10.1 フェーズ境目の利用者監査

- requirements.md Req 6 受入 1 に対応
- session 内での連続承認を強制しない（利用者の負担抑制）
- フェーズ境目（要件 → 設計、設計 → タスク、タスク → 実装等）で提案をまとめて判断
- 判断単位は提案 1 件ずつ、複数提案を 1 ターンで一括承認は許容（明示的肯定発言があれば）
- 承認・却下の発話判定は [approval-operation](../../../docs/disciplines/discipline_approval_operation.md) 規律に従う。却下語彙は「却下」「不採用」「採用しない」「採用しません」「見送り」等の明示的否定発言とし、「採用しません」のような承認語を含む否定形は承認ではなく却下として扱う

### 10.2 規律の正式化（aspirational → enforced）

- requirements.md Req 6 受入 2 に対応
- 利用者明示承認必須
- 承認時点で `status_change` 提案を `approved` に遷移
- 明示承認の判定基準は [approval-operation](../../../docs/disciplines/discipline_approval_operation.md) 規律に従う（「承認します」「OK」「採用」「進めて」「はい」等の明示的肯定発言）

### 10.3 規律の archive 退避

- requirements.md Req 6 受入 3 に対応
- **撤廃 README 必須**（撤廃理由を記録）
- 撤廃 README の配置先：`docs/disciplines/archive/<日付>-<id>/README.md`（A-001 対処、requirements.md 行 125 も同パスに修正済み）
- 撤廃 README の必須内容：退避日、退避ファイル、撤廃理由、利用者明示承認の出典、関連参照

### 10.4 規律間の統廃合

- requirements.md Req 6 受入 4 に対応
- **対応表必須**（何と何が統合されたか）
- 対応表の配置：撤廃 README 内（archive ディレクトリ単位で 1 ファイル）＋提案 YAML の `source_discipline_paths` フィールド（§8.4）
- 統廃合の典型パターン：新規規律 1 件＋ archive 退避 2 件以上（縮減義務、§5.8 第 5 層）

### 10.5 4 状態の遷移管理

- requirements.md Req 6 受入 5 に対応
- 提案の 4 状態（pending／approved／rejected／superseded）を提案 YAML ファイルの `status` フィールドで明示
- 状態遷移時は提案 ID を維持、ディレクトリ間で git mv（履歴保持）
- ディレクトリ間の移動規則：
  - `pending` → `proposals/`
  - `approved` → `approved-updates/`
  - `rejected` → `rejected-updates/`
  - `superseded` → `approved-updates/`（status フィールドのみ更新、配置場所は維持）
- **`superseded` 遷移は reopen-procedure 5 ステップを必須**（§8.7、A-007 対処）

## 11. 履歴とロールバック（History and Rollback Model）

### 11.1 ディレクトリ配置

requirements.md Req 7 受入 1 に対応する 4 サブディレクトリ＋関連 2 箇所：

```
learning/
└── workflow/                            # workflow 改善の履歴保管（第 1 期スコープ）
    ├── proposals/                       # 提案中（status: pending）
    │   └── <日付>-<id>.yaml
    ├── approved-updates/                # 承認済み（status: approved または superseded）
    │   └── <日付>-<id>.yaml
    ├── rejected-updates/                # 却下済み（status: rejected）
    │   └── <日付>-<id>.yaml
    ├── rollback/                        # ロールバック履歴
    │   └── <日付>-<id>.yaml
    ├── metrics/                         # 効果測定 7 指標の時系列出力（§12.3、topic-101／F-005 対処で配置図に追記）
    │   └── <日付>.yaml
    └── schemas/                         # 永続データの正本スキーマ（topic-106／F-007 対処、データと混在させず専用サブフォルダに分離）
        ├── proposal.schema.json
        ├── rollback.schema.json
        └── metrics.schema.json

docs/
├── discipline-compliance-reports/       # 遵守検査の時系列（§5.9.5 既存、本機能の入力源 5）
│   └── <日付>.yaml
└── disciplines/archive/                 # 撤廃の経緯（撤廃 README、A-001 対処）
    └── <日付>-<id>/
        ├── README.md                    # 撤廃 README（必須）
        └── discipline_*.md              # 撤廃対象の規律本体
```

`learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリは **第 1 期では空置き**（他 4 層改善で活用予定、§5.16.10）。空置きディレクトリの所有権はフェーズ 4 完了後の他層改善計画書で確定する（A-012 注記）。

**スキーマファイルの配置方針（topic-106／F-007 対処、2026-05-29 セッション 39）**：スキーマ（データ形式の設計図）は「正本性」で配置を分ける。(a) ツール内部の中間スキーマ（`provenance.schema.json`／`signal.schema.json`）は処理ツールに近い `tools/self_improvement/schemas/` 配下、(b) 永続データの正本スキーマ（`proposal.schema.json`／`rollback.schema.json`／`metrics.schema.json`）はデータに近い `learning/workflow/schemas/` 配下。いずれも各データのサブディレクトリ直下に混在させず `schemas/` 専用サブフォルダに分離し、`workflow-management` が `approved-updates/` 等を読む際の誤参照リスクを構造的に排除する（F-015 連動）。

### 11.2 ロールバック方法

requirements.md Req 7 受入 2 に対応する 3 つのロールバック方法：

| ロールバック方法 | 内容 | 実装 |
|---|---|---|
| **archive から復活** | 撤廃された規律を `docs/disciplines/` に戻す | `git mv docs/disciplines/archive/<日付>-<id>/discipline_*.md docs/disciplines/`、シンボリックリンク再作成（§11.3） |
| **ステータス変更を戻す** | `enforced` → `aspirational` に格下げ | 規律本文の front-matter `status` フィールドを更新、`status_change` 提案として記録 |
| **規律の更新を取り消す** | 過去版に戻す | git 履歴を活用（`git checkout <commit> -- docs/disciplines/discipline_*.md`） |

### 11.3 シンボリックリンク再作成手順（F-014 対処）

memory 配下の `feedback_*.md` が repo 本体（`docs/disciplines/discipline_*.md`）を指すシンボリックリンク構成（MEMORY.md 記録）に対するロールバック手順：

1. archive から復活する規律ファイル名を確認（例：`discipline_xxx.md`）
2. memory 配下に対応する `feedback_xxx.md` シンボリックリンクが存在するか確認
3. 存在しない場合は新規作成：`ln -s /Users/Daily/Development/ReviewCompass/docs/disciplines/discipline_xxx.md ~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/feedback_xxx.md`
4. 存在する場合（archive 退避時にリンクを保持していた場合）は確認のみ
5. memory/MEMORY.md の active 必読／参照層／archive 一覧を更新

### 11.4 ロールバック理由の保存

- requirements.md Req 7 受入 3 に対応
- ロールバック理由を `learning/workflow/rollback/<日付>-<id>.yaml` に保存
- YAML 構造：
  ```yaml
  rollback_id: RB-001                  # Rollback Proposal の通し番号（§8.5）
  target_proposal_id: WP-005           # 元の採用提案
  rollback_method: archive_restoration  # archive_restoration / status_downgrade / git_revert
  rollback_reason: |
    新規律が他規律と衝突、影響範囲が事前分析時に把握できていなかった
  rollback_date: 2026-06-15
  related_artifacts:
    - learning/workflow/approved-updates/2026-06-10-WP-005.yaml
    - docs/disciplines/discipline_*.md
  ```

### 11.5 履歴の連結

- requirements.md Req 7 受入 4 に対応
- 提案 → 承認 → ロールバックの追跡を可能にする
- 連結方法：YAML の `target_proposal_id` フィールドで提案 ID を参照、機械的に辿れる形を保つ

### 11.6 整合性検査

- requirements.md Req 7 受入 5 に対応
- 撤廃から復活した規律の機械検査：
  1. 復活した規律ファイルの YAML front-matter が現行スキーマと整合するか（必須フィールド存在検査）
  2. 既存規律との内部リンク `[[name]]` 形式の参照衝突を grep で確認
  3. archive 経緯 README の記述と矛盾しないか確認
- ロールバック後の遵守検査再実行：`docs/discipline-compliance-reports/<日付>.yaml` に追記

## 12. 効果測定（Effect Measurement Model）

### 12.1 7 指標

requirements.md Req 8 受入 1 に対応する 7 指標：

| カテゴリ | 指標 | 定義 |
|---|---|---|
| §5.9.5 由来 | 規律遵守率 | 規律違反件数 ／ 検査対象件数 |
| §5.9.5 由来 | 昇格件数（aspirational → enforced） | パイロット運用を経て正式化した規律の件数 |
| §5.9.5 由来 | 退避件数（規律 → archive） | 撤廃した規律の件数 |
| workflow 改善運用 | 提案件数（種別ごと） | 5 種別ごとの提案件数 |
| workflow 改善運用 | 採用率（採用 ／ 提案合計） | （`approved` ＋ `superseded`） ／ （`approved` ＋ `rejected` ＋ `superseded`）。分子・分母の両方に `superseded` を含める（topic-102／F-003 対処、案 2）。pending は分母から除外（F-013 対処） |
| workflow 改善運用 | ロールバック率（ロールバック ／ 採用） | ロールバック件数 ／ `approved` 件数 |
| workflow 改善運用 | 提案から採用までの平均日数 | 提案日付と承認日付の差の平均 |

### 12.2 phase-review-metric-register への登録

- requirements.md Req 8 受入 2 に対応
- 7 指標を `phase-review-metric-register.md` の **workflow 改善カテゴリ** として登録
- 登録ファイルの配置：`docs/operations/phase-review-metric-register.md`（フェーズ 2 以降の宿題）

### 12.3 analysis への出力

- requirements.md Req 8 受入 3 に対応
- 指標の計算根拠を機械可読な形式（YAML または JSON）で出力
- `analysis` 機能が読み物（運用ダッシュボード／監査用報告等）に取り込む
- 出力先：`learning/workflow/metrics/<日付>.yaml`（フェーズ 4 第 1 サイクル以降）
- フェーズ 1〜3 の手動集計時の保管場所：同じ `learning/workflow/metrics/<日付>.yaml`（手動でも自動でも同じ配置先）

### 12.4 時系列推移の保持

- requirements.md Req 8 受入 4 に対応
- 指標の時系列推移を保持し、改善活動の長期的傾向を追跡可能にする
- 時系列の保管先：`learning/workflow/metrics/` 配下の日付付き YAML

### 12.5 手動集計の許容

- requirements.md Req 8 受入 5 に対応
- フェーズ 1〜3：手動集計（grep ／ wc ／ jq を使った半自動化）
- 手動集計の具体手順：
  1. `learning/workflow/proposals/` `approved-updates/` `rejected-updates/` `rollback/` 配下の YAML 件数を `find ... | wc -l` で集計
  2. `status` 値を `grep "status:" ... | sort | uniq -c` で集計
  3. 採用率を `(approved + superseded) / (approved + rejected + superseded)` で算出（分子・分母の両方に `superseded` を含める。§8.6・§12.1 と一貫。topic-102／F-003 で確定した正式な式、案 2、2026-05-29 セッション 39）
  4. 結果を `learning/workflow/metrics/<日付>.yaml` に記録
- フェーズ 4 第 1 サイクル：input_model と signal_extraction の実装、集計の半自動化
- フェーズ 4 第 3 サイクル：自動化完了（§5.16.12）

### 12.6 本セッション 27 で実装した先行ログ

本セッション 27 で新設した `docs/discipline-compliance-reports/options-precheck-log.md` は、本機能の効果測定の **先行実装** に相当する。複数案提示の事前検査宣言義務（規律 options-presentation）の効果を 3 指標（発火率／違反件数／dominated 除外件数）で計測する仕組みで、本機能の Effect Measurement Model のうち **規律遵守率** の特殊形として位置付ける。

7 指標との対応関係：

| options-precheck-log の指標 | 7 指標との対応 |
|---|---|
| 発火率 | 規律遵守率の特殊形（事前検査宣言の遵守率） |
| 違反件数 | 規律遵守率の補助指標 |
| dominated 除外件数 | 規律機能の積極証拠（直接対応する 7 指標なし、補助指標） |

将来 7 指標体系に取り込む際、options-precheck-log は規律遵守率カテゴリの一部として吸収する方針（A-004 対処）。

## 13. 他機能との接合面（Interfaces with Other Features）

### 13.1 foundation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律検査スキーマ、レビューモード語彙（値は foundation 正本を参照、再定義しない）、状態軸語彙（`evidence_class`／`validator_status`）、必須メタデータ（severity／target_location／description／rationale） |
| 再定義しない原則 | foundation を正本所有者として参照し、本機能内で再定義しない（Boundary Context 隣接期待） |

### 13.2 runtime との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律遵守検査の結果（レビュー記録の機械検査出力） |
| 形式 | レビュー記録の front-matter＋本文の構造化部分（`findings_by_method` ／ `severity` 集計 等） |

### 13.3 evaluation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律違反データの集計と評価結果 |
| 形式 | `experiments/<run-id>/` 配下の集約 YAML／JSON、3 役所見差分報告（`roles/role_diff_report.json`、**A-011 対処済み**（2026-05-26 セッション 28、evaluation 設計に新設済み）。本機能の design.alignment 前提は充足済み。topic-103／G-001 で陳腐化記述を更新、2026-05-29 セッション 39） |

### 13.4 analysis との接合面

| 方向 | 内容 |
|---|---|
| 出力（self-improvement が書く） | 効果測定 7 指標、提案の状態遷移ログ |
| 形式 | `learning/workflow/metrics/<日付>.yaml`（機械可読）、`analysis` が読み物として再構成 |

### 13.5 workflow-management との接合面（A-003／F-008 対処、本セッション 27 確定）

時系列契約と完了通知の形式を詳細に定義する。

#### 時系列契約

| 時点 | 本機能の状態 | workflow-management の状態 |
|---|---|---|
| 提案作成 | `pending`（`proposals/` 配下） | — |
| 提案レビュー承認 | `approved`（`approved-updates/` 配下に git mv） | 手続き入力として参照可能 |
| 手続き開始 | 維持（`approved`） | drafting → review → approval を実施 |
| 手続き完了 | 維持（`approved`、`materialized_at`／`materialization_commit_hash` 追記） | docs/disciplines/ の実体変更コミット完了 |
| 整合性検査 | 維持（`approved`、遵守検査再実行） | — |

`approved` ＝ 本機能の提案レビュー承認時点。実体変更未完了でも本機能内では確定。`materialized_at` ＝ workflow-management の手続き完了時点（本機能の status は変えず、補助フィールドとして追記）。

#### 渡し方の形式

承認済み提案 YAML を `git mv` で `learning/workflow/approved-updates/` に配置（pending → approved）。workflow-management はこのディレクトリを所定手続きの input として読む。

#### 完了通知の形式

workflow-management が手続き完了時に `approved-updates/<日付>-<id>.yaml` に次のフィールドを追記：

```yaml
materialized_at: 2026-06-10T12:34:56+09:00       # ISO 8601 形式、workflow-management が記録
materialization_commit_hash: a1b2c3d4...          # 実体変更コミットのハッシュ
```

本機能は git log の grep（または `materialized_at` フィールドの存在検査）で完了確認可能。

#### 整合性検査タイミング

`materialized_at` 記録後に遵守検査再実行（§11.6 と整合）。整合性検査が通過したら本機能の処理は完了。

#### ロールバック責務

`approved` だが未 `materialized` の状態でロールバックが必要になった場合：本機能が `superseded` に遷移させ（§8.7 の 5 ステップを踏む）、workflow-management に通知（実体変更が未完なので git revert は不要）。

`materialized` 後のロールバックは §11.2 の 3 方法（archive から復活／ステータス変更を戻す／更新を取り消す）を適用。

#### 波及対応

本接合面の最終確定は design レビュー波段（次セッション以降）で workflow-management 設計改訂と合わせて実施する。波及所見として carry-forward register に A-003／F-008 由来の項目を登録済み（本セッション 27 確定）。

### 13.6 conformance-evaluation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律遵守検査の上流文書との適合性評価結果（2 軸 6 criteria：requirements ／ design × 3 criteria、計画書 §5.10 由来） |
| 形式 | conformance-evaluation の出力（適合度スコア、不適合箇所の特定）。出力ファイルの配置先は conformance-evaluation 側の責務、本機能は出力が確定次第読む |
| 活用方法 | 規律違反の原因が上流文書（intent ／ requirements ／ design）にある場合、`new_discipline` または `update` 提案の motivating_evidence に conformance-evaluation の出力を含める |
| 依存方向 | conformance-evaluation → self-improvement（self-improvement が conformance-evaluation の出力を読む、A-008 で確定済み 2026-05-23） |
| commit hash 整合ルール（A-016 対処） | conformance-evaluation §12.3 と整合。`target_commit`（conformance-evaluation 所有）と `materialization_commit_hash`（本機能 §13.5 所有）は独立。詳細は本節サブセクション参照 |

#### target_commit と materialization_commit_hash の独立性（A-016 対処、2026-05-26 セッション 28 確定）

本接合面の commit hash の整合ルールは conformance-evaluation §12.3 で詳細定義されており、本機能はこの合意点を受け入れる。

**両 commit の所有関係**：

- **target_commit**（conformance-evaluation 所有）：conformance-evaluation の評価対象である実装コードの commit hash。conformance-evaluation が記録する出典
- **materialization_commit_hash**（本機能 §13.5 所有）：本機能の規律変更が workflow-management の手続きで実体変更された時点のコミットハッシュ。本機能が §13.5 で記録
- **両者は独立**：target_commit は実装コードのコミット、materialization_commit_hash は規律変更のコミット

**同一文書で両 commit を扱う場面**：

規律改訂の影響を伴う conformance check 時、conformance-evaluation の評価記録に本機能の `materialization_commit_hash` が `related_artifacts.self_improvement` フィールドで参照される（conformance-evaluation §12.3 由来）。

**本機能が conformance-evaluation 結果を取り込む場面**：

本機能の motivating_evidence として conformance-evaluation の評価結果を参照する場合、`target_commit` は conformance-evaluation の出典として記録、`materialization_commit_hash` は本機能側が §13.5 の手続きで記録（責務分担）。

## 14. 要件追跡表（Requirements Traceability、受入基準単位、F-001／F-002 対処）

requirements.md の Requirement と各受入基準を本設計の章節に紐付ける。

| Requirement | 受入基準 | 対応章節 |
|---|---|---|
| Req 1 役割と性格 | 受入 1（workflow 層限定） | §1 概要／§2 目標／§3 範囲外 |
| Req 1 | 受入 2（双方向同期責務） | §1 概要／§5.1 データの流れ |
| Req 1 | 受入 3（データの流れ） | §5.1 データの流れ |
| Req 1 | 受入 4（権限分離、A-007 案 2） | §5.2 責務分担モデル／§15 Decision 1 |
| Req 2 入力 | 受入 1（入力源 5 種類） | §6.1 |
| Req 2 | 受入 2（来歴情報 3 要素） | §6.2 |
| Req 2 | 受入 3（時系列性） | §6.3 |
| Req 2 | 受入 4（上流出力を直接消費） | §6.4 |
| Req 3 提案単位 | 受入 1（5 種類） | §8.1 |
| Req 3 | 受入 2（本機能の規律のみ） | §8.2 |
| Req 3 | 受入 3（組み合わせ） | §8.3 |
| Req 3 | 受入 4（target_discipline_path） | §8.4 |
| Req 3 | 受入 5（種別ごとの追加情報） | §8.8 |
| Req 4 提案の構造 | 受入 1（YAML 必須フィールド） | §8.4 |
| Req 4 | 受入 2（motivating_evidence 3 要素） | §8.4 |
| Req 4 | 受入 3（proposal_type 5 種類） | §8.4／§8.1 |
| Req 4 | 受入 4（status 4 値） | §8.6 |
| Req 4 | 受入 5（statistical_evidence 任意） | §8.9 |
| Req 5 検証 | 受入 1（3 検証方法） | §9.1 |
| Req 5 | 受入 2（遡及シミュレーション対象範囲） | §9.2 |
| Req 5 | 受入 3（パイロット運用期間） | §9.3 |
| Req 5 | 受入 4（replay／backtest 不採用） | §9.5 |
| Req 6 承認 | 受入 1（フェーズ境目の判断） | §10.1 |
| Req 6 | 受入 2（aspirational → enforced 明示承認） | §10.2 |
| Req 6 | 受入 3（archive 撤廃 README 必須） | §10.3 |
| Req 6 | 受入 4（consolidation 対応表必須） | §10.4／§8.4 |
| Req 6 | 受入 5（4 状態の明示） | §10.5／§8.6 |
| Req 7 履歴ロールバック | 受入 1（4 サブディレクトリ配置） | §11.1 |
| Req 7 | 受入 2（3 ロールバック方法） | §11.2 |
| Req 7 | 受入 3（ロールバック理由保存） | §11.4 |
| Req 7 | 受入 4（履歴の連結） | §11.5 |
| Req 7 | 受入 5（整合性検査） | §11.6 |
| Req 8 効果測定 | 受入 1（7 指標） | §12.1 |
| Req 8 | 受入 2（phase-review-metric-register 登録） | §12.2 |
| Req 8 | 受入 3（analysis への出力） | §12.3 |
| Req 8 | 受入 4（時系列推移） | §12.4 |
| Req 8 | 受入 5（手動集計許容） | §12.5 |

## 15. 設計決定（Key Decisions）

### Decision 1：規律変更権と実体変更権の分離（A-007 案 2）

self-improvement は規律の論理的正本所有者だが、規律ファイルの実体変更は workflow-management の所定手続き（drafting → review → approval）経由で実行する。本機能は **提案権** のみを持ち、ファイルの直接書き換えは行わない。機械検査は §17 で具体定義（F-015 対処）。

**根拠**：自己承認の空洞化を防ぐ。利用者明示承認 2026-05-23（A-007）。

### Decision 2：スコープを workflow 層に限定

第 1 期は workflow 層改善のみを担当、他 4 層（prompt／policy／schema／runtime）は別計画書で扱う。

**根拠**：runtime 層改善向けの replay／backtest は workflow 改善で使いにくく、性格が異なる（計画書 §5.16.5）。段階的導入方針（計画書 §7、§5.16.12）。

### Decision 3：replay／backtest を採用せず 3 検証方法で代替

過去データへの遡及シミュレーション／パイロット運用／影響範囲の事前分析の 3 つを採用。

**根拠**：規律は「人間が守るべきルール」であり、過去入力に対する出力の再現（replay／backtest）では検証できない（計画書 §5.16.5）。

### Decision 4：4 サブディレクトリ配置（learning/workflow/）

proposals／approved-updates／rejected-updates／rollback の 4 サブディレクトリで提案の状態遷移を物理ディレクトリで表現。

**根拠**：機械検査と人間の目視確認の両方を支援、git mv で履歴を保持しながら状態遷移できる構造（§5.16.7、§5.16.10）。

### Decision 5：効果測定 7 指標体系（§5.9.5 由来 3 ＋ workflow 改善運用 4）

§5.9.5 既存の 3 指標を継承しつつ、workflow 改善運用の 4 指標を追加。

**根拠**：規律変更の活動そのものの効果測定が必要、提案 → 承認 → 採用 → ロールバックのパイプライン全体を追跡（計画書 §5.16.8）。

### Decision 6：4 状態体系（pending／approved／rejected／superseded）と reopen-procedure 5 ステップ準拠

提案の状態を 4 値で表現、`superseded` は本仕様の独自追加。`superseded` 遷移は規律 reopen-procedure-for-settled-topics の 5 ステップを必須とする（A-007 対処、§8.7）。

**根拠**：計画書 §5.16.6 の自然言語語彙に対応しつつ後続提案による上書きを表現、規律 reopen-procedure を機械的に担保。

### Decision 7：旧 8 モジュールの半分継承・半分新規

継承可能 4 件：decision_adoption_model／rollback_model／pipeline_driver／learning_layout
新規実装 4 件：input_model／proposal_model／replay_backtest_model 相当／signal_extraction

**根拠**：旧モジュールの再利用と workflow 改善向けの再設計のバランス（計画書 §5.16.11）。実装言語は将来の実装段で決定（A-011 対処）。

### Decision 8：縮減義務の運用化（処理表面積抑制）

新規規律の追加時に既存規律 1 件以上の統廃合をセットで提案する縮減義務を運用化（§5.8 第 5 層）。

**根拠**：規律体系の肥大化を構造的に防ぐ。実例：本セッション 27 の discipline_options_presentation.md 新設＋旧 2 件 archive 退避（純増ゼロ）。

### Decision 9：proposal_id の発番ルール（A-002 対処、本セッション 27 確定）

採番権者は self-improvement、接頭辞で名前空間を分離（`WP-NNN` ／ `RB-NNN` 等）、通番リセットなし、3 桁から開始し 999 件を超えたら自動で 4 桁に拡張。

**根拠**：A-007 案 2 と整合（採番は提案権を持つ機能の責務）。

### Decision 10：パイロット運用閾値 90%（A-009 対処、本セッション 27 確定）

新規律の `aspirational → enforced` 昇格判定の閾値を遵守率 **90% 以上** とする。経験則として暫定設定、フェーズ 4 第 3 サイクル以降の運用データで調整。

**根拠**：規律 approval-operation の確定記述には承認出典併記の規律に従い、利用者明示承認「90%」（2026-05-26 セッション 27）を出典として記録。

## 16. Boundary Context との整合確認（Boundary Context Compliance）

requirements.md の Boundary Context との整合：

### In scope（範囲内）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 規律と実体の乖離の観察 | §5 アーキテクチャ §1 データの流れ／§6 入力モデル／§7 signal_extraction モデル |
| 5 種類の提案単位 | §8.1 提案単位 |
| 提案構造の定義（YAML 形式） | §8.4 提案構造（YAML） |
| 3 つの検証方法 | §9 検証モデル |
| フェーズ境目の利用者監査による承認 | §10 承認モデル |
| 履歴とロールバック（learning/workflow/ 4 サブディレクトリ） | §11 履歴とロールバック |
| 効果測定 7 指標（§5.9.5 の 3 指標 ＋ workflow 改善運用の 4 指標） | §12 効果測定 |

### Out of scope（範囲外）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 他 4 層改善（prompt／policy／schema／runtime） | §3 範囲外で明示、Decision 2 |
| `learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリは第 1 期で空置き | §11.1 で明示、A-012 対処済み |
| replay／backtest（runtime 改善向け） | §3 範囲外で明示、Decision 3 |
| 論文化からの分離 | §3 範囲外で明示 |
| 外部プロジェクトからの取り込み証跡 | §3 範囲外で明示 |

### 隣接仕様の期待との整合

| 隣接機能 | Boundary Context の期待 | 本設計での対応 |
|---|---|---|
| foundation | 規律検査スキーマ等を再定義せず参照 | §13.1 で明示 |
| runtime | 規律遵守検査の結果を入力源として受け取る | §13.2 で明示 |
| evaluation | 規律違反データの集計と評価結果を入力源として受け取る | §13.3 で明示 |
| analysis | 効果測定 7 指標を本機能から受け取る | §13.4 で明示 |
| workflow-management | 規律の昇格・退避・統廃合を所定手続きに従って実行 | §5.2 責務分担モデル／§10 承認モデル／§13.5 で明示 |
| conformance-evaluation | 規律遵守検査の上流文書との適合性評価結果を入力源として活用可能 | §13.6 で明示 |

## 17. 機械検査の具体手段（Machine Verification, F-015 対処、本セッション 27 新設）

本章は Goals §2 と Decision 1 の「機械検査可能な形で担保し、自己承認の空洞化を防ぐ」の宣言を実装可能な手段で裏付ける。

### 17.1 検査対象

本機能の動作に関する 4 つの機械検査ポイント：

| 検査 ID | 検査対象 | 検査内容 | 実装方法 |
|---|---|---|---|
| **MV-1** | `docs/disciplines/` への直接書き込み検出 | self-improvement モジュールから `docs/disciplines/discipline_*.md` への直接書き込みが発生していないこと（A-007 案 2 の遵守） | git log で本機能関連コミットの changed files に `docs/disciplines/discipline_*.md` が含まれないことを grep で検査 |
| **MV-2** | 提案 YAML の必須フィールド存在 | `learning/workflow/proposals/` `approved-updates/` 配下の YAML が必須フィールド（proposal_id／proposal_type／target_discipline_path／motivating_evidence／proposed_change／expected_effect／status）を持つ | grep または jq でフィールド存在を確認 |
| **MV-3** | 提案 ID と実体変更コミットの対応 | `approved-updates/` 配下の YAML の `materialization_commit_hash` が、git log で実在するコミットを指していること。**ただし値が空（null＝未実体化）の場合は正常としてスキップし、値があるときだけ実在検査する**（topic-110／G-004 対処、2026-05-29 セッション 39）。本フィールドは workflow-management が実体変更完了時に書き込む（§13.5）ため、第 1 期（workflow-management 未実装）は常に空であり、空を `fail-closed` で遮断すると過剰遮断になる。空は「承認済みだが未実体化」の正常状態として扱う | `materialization_commit_hash` が非 null のときのみ `git cat-file -e <hash>` で存在検査、null はスキップ |
| **MV-4** | superseded 遷移の reopen-procedure 5 ステップ完了 | `status: superseded` の提案 YAML に `superseded_by`／`superseded_at`／`reopen_reason` のすべてが存在すること | grep で 3 フィールドの存在を検査 |

### 17.2 検査スクリプトの所在と責務分担

- 第 1 期（フェーズ 1〜3）：手動 grep ／ jq による検査、本機能の責務として運用
- フェーズ 4 第 1 サイクル以降：検査スクリプトを `tools/self-improvement-check.py`（仮称、本機能の所有物）として実装
- workflow-management の `tools/check-workflow-action.py`（補助層 C 段階 2）とは責務が異なる：
  - check-workflow-action.py：不可逆操作（spec.json 変更／commit／push）の事前検査、所有者は workflow-management
  - self-improvement-check.py：本機能の提案・承認・ロールバックの整合検査、所有者は本機能

### 17.3 検査の出力先

- 検査結果は `learning/workflow/metrics/<日付>.yaml` に追記（§12 効果測定と連動）
- 検査失敗時は遮断（fail-closed）：本機能の処理が継続できない状態とし、利用者監査に上げる

### 17.4 機械検査の段階的導入

- フェーズ 1〜3：MV-1／MV-2／MV-4 は手動 grep、MV-3 は git コマンドの手動実行
- フェーズ 4 第 1 サイクル：MV-1／MV-2 を自動化
- フェーズ 4 第 2 サイクル：MV-3／MV-4 を自動化
- フェーズ 4 第 3 サイクル：効果測定 7 指標との連携、検査失敗時の通知機構（§5.13 補助層 B）と統合

## 18. テスト戦略（Test Strategy, F-017 対処、本セッション 27 新設）

本章は計画書 §5.9.2 のレビュー観点 9「テスト戦略」に対応する。

### 18.1 テスト対象とテストレベル

| モデル | 単体テスト | 結合テスト | 受入テスト |
|---|---|---|---|
| **入力モデル（§6）** | 5 種類の入力源ごとの読み込みテスト、来歴情報 3 要素の付与テスト | 上流機能（runtime ／ evaluation）出力との連結テスト | 全 5 入力源を網羅した実データでの取り込み |
| **signal_extraction モデル（§7）** | 4 種類の乖離判定（規律不在型／違反型／形骸化型／衝突型）の判定テスト | input_model 出力を入力としたパイプラインテスト | 過去レビュー記録 17 件＋遵守検査 30 件規模のデータで乖離抽出 |
| **提案モデル（§8）** | YAML スキーマ妥当性検査、proposal_id 採番ルール、status 遷移（4 値） | signal_extraction 出力から提案 YAML 生成 | 5 種類すべての proposal_type を網羅した提案作成 |
| **検証モデル（§9）** | 遡及シミュレーション／パイロット運用／影響範囲分析の各検証手段の単体テスト | 提案 YAML を入力とした検証実施 | 過去データでの実証的検証 |
| **承認モデル（§10）** | 4 状態の遷移正確性、reopen-procedure 5 ステップ完了検査 | 承認後の git mv 動作、workflow-management への手続き入力提供 | フェーズ境目の利用者監査シミュレーション |
| **履歴ロールバック（§11）** | 4 サブディレクトリ配置、3 ロールバック方法、整合性検査 | git 履歴との連携、シンボリックリンク再作成 | 撤廃復活シナリオの完走 |
| **効果測定（§12）** | 7 指標の算出、grep 集計の再現性 | input_model 〜 ロールバックの全パイプラインを通じた集計 | 時系列推移の表示確認 |

### 18.2 テスト戦略の重点ポイント

- **YAML スキーマ妥当性**：jsonschema または同等のツールで提案 YAML を機械検査（フェーズ 4 第 1 サイクル以降）
- **状態遷移**：pending → approved／rejected／superseded の各経路を網羅、特に superseded 遷移の reopen-procedure 5 ステップ完了確認（MV-4）
- **効果測定指標の算出**：grep カウントの再現性、採用率／ロールバック率の計算式
- **ロールバック整合性**：archive 復活時の遵守検査再実行（MV-3／MV-4）
- **workflow-management との接合**：提案 YAML の手続き入力としての妥当性、`materialized_at` の同期（§13.5）

### 18.3 テスト実施タイミング

- 単体テスト：実装段（フェーズ 4 第 1 サイクル以降）の各モジュール実装時
- 結合テスト：実装段（フェーズ 4 第 2 サイクル）のパイプライン構築時
- 受入テスト：実装段（フェーズ 4 第 3 サイクル）の全機能完成時、利用者監査と組み合わせ

### 18.4 テストデータの取得元

- 過去レビュー記録：`.reviewcompass/specs/<feature>/reviews/` 配下（フェーズ 1 で 7 機能の requirements／design レビュー記録が蓄積）
- 過去遵守検査：`docs/discipline-compliance-reports/<日付>.yaml`（フェーズ 1 末で蓄積開始）
- 規律ファイル：`docs/disciplines/discipline_*.md`（現在 active 必読＋参照層＝合計 15 件相当）
- 規律 archive：`docs/disciplines/archive/<日付>-<id>/`（本セッション 27 で初回データ追加）

## 19. design.alignment 段の未解決論点（Open Issues for Design Alignment Gate）

本セッション 27 末時点で本機能の design.drafting 段で未解決の論点：

### 19.1 遡及（要 requirements 修正）

- **A-001（本セッション 27 確定対処）**：requirements.md 行 125 の撤廃 README 配置先（`docs/archive/disciplines/`）を実体配置・design.md と整合する `docs/disciplines/archive/<日付>-<id>/` に修正。軽量 reopen 手続きで対処（利用者明示承認「候補 1」2026-05-26）

### 19.2 波及（要 workflow-management 設計改訂）

- **A-003／F-008**：self-improvement の status `approved` 遷移と workflow-management の手続き完了の時系列契約・完了通知形式は本機能の design.md §13.5 で詳細提案を記述したが、workflow-management 側の合意は design レビュー波段で取る。carry-forward register に登録（本セッション 27 確定）

### 19.3 他機能横断の未消化所見

- **A-011（✅ 対処済み、2026-05-26 セッション 28）**：analysis／evaluation 接合面の `roles/role_diff_report.json` 新設は evaluation 設計に反映済み（正本 carry-forward register の `carry-forward-011`）。本機能の §13.3 で参照しており、A-011 消化が本機能の design.alignment の前提だったが、**前提は充足済み**。本欄は topic-103／G-001 で陳腐化記述を更新（2026-05-29 セッション 39）。現時点で §19.3 に未消化の他機能横断所見はない

### 19.4 機能横断レビューで対処済みの所見

- **A-007（既存）**：self-improvement と workflow-management の権限分散調停 → Decision 1（A-007 案 2）として反映済み
- **A-008（既存）**：conformance-evaluation から self-improvement への出力方向 → §13.6 で「conformance-evaluation → self-improvement の方向」として整理済み（2026-05-23）
- **2026-06-08 の requirements 再確認への対応**：intent の「レビュー収集処理を事前設定の写像にしない」意図は、§6 入力モデル、§7 signal_extraction モデル、§8 提案モデル、§11 履歴とロールバックで受けられるため、設計構造の追加は不要と確認

## 20. 起草完了基準（Completion Criteria）

本設計が design.drafting 段の完了とみなされる条件：

- [x] 全 20 章（番号なし 5 章＋番号付き §6〜§20 の 15 章）が記述されている
- [x] requirements.md の全 8 件の Requirement と受入基準が §14 要件追跡表で章節と対応している（受入基準単位の追跡、F-001／F-002 対処）
- [x] 計画書 §5.16 の 12 小節（§5.16.1〜§5.16.12）の方針が反映されている
- [x] 他機能との接合面が §13 で全 6 機能分（foundation／runtime／evaluation／analysis／workflow-management／conformance-evaluation）明示されている
- [x] Boundary Context との整合が §16 で確認されている
- [x] 機能横断所見（A-007／A-008）の対処が §15 Decision 1／§13.6 で明示されている
- [x] 主要な設計決定（10 件、A-002／A-009 対処を含む）が §15 で明示されている
- [x] **機械検査の具体手段（§17）が定義されている**（F-015 対処）
- [x] **テスト戦略（§18）が定義されている**（F-017 対処）
- [x] signal_extraction モデル（§7）の専用章が存在する（F-004 対処）
- [x] consolidation の複数規律パスフィールド `source_discipline_paths` が §8.4 に存在する（F-003／F-006 対処）
- [x] proposal_id 発番ルールが §8.5／Decision 9 で確定（A-002 対処）
- [x] superseded 遷移の reopen-procedure 5 ステップが §8.7／§10.5／Decision 6 で明示（A-007 対処）
- [x] パイロット運用閾値 90% と利用者明示承認の出典が §9.3／Decision 10 で記録（A-009 対処）
- [x] workflow-management との時系列契約・完了通知形式が §13.5 で詳細記述（A-003／F-008 対処、波及登録済み）

本設計の triad-review 段（本セッション 27 末で完了予定）で扱った観点（Design 観点 10 件、計画書 §5.9.2 由来）：

1. 設計と要件の対応 → §14 要件追跡表
2. 設計の内部整合 → §5 アーキテクチャ／§13 他機能との接合面
3. 設計の他機能との整合 → §13 他機能との接合面
4. 設計の正本との整合 → §16 Boundary Context との整合確認
5. 検証可能性 → §17 機械検査の具体手段／§18 テスト戦略
6. 実装可能性 → §15 設計決定（旧 8 モジュールとの関係）
7. 段階的導入の妥当性 → §17.4 機械検査の段階的導入／§18.3 テスト実施タイミング
8. 拡張余地と将来宿題 → §3 範囲外／§19 Open Issues
9. テスト戦略 → §18 テスト戦略
10. リスクと残余課題 → §19 Open Issues

## 実装由来契約の波及トレース

- `XDI-SI-001`：approval guard、rejection guard、`proposal_id`、carry-forward guard は、proposal model、approval model、carry-forward register の設計境界にまたがる。詳細な要件採用は requirements.md §実装由来契約を正本とし、本 design.md は設計層から追跡可能であることを示す。
