# Design Document：self-improvement

最終更新：2026-05-26（セッション 27：design.drafting 起草、要件 8 件に対応、workflow 層改善に特化した全面書き直し設計）

## 概要（Overview）

`self-improvement` は ReviewCompass の改善機能の **設計層** であり、第 1 期では **workflow 層改善のみ** を担う。先行プロジェクトの自己改善仕様（130 行 8 要件、主に runtime 層改善向け）は workflow 改善の性格に合わないため、計画書 §5.16 で全面書き直しが確定済み。

本機能の中核責務は **規律と実体の双方向同期** である。規律違反データと実体運用パターンを観察し、「規律を実体に追従させる」か「実体を規律に追従させる」かを判断する。判断結果は提案（YAML 形式）として記述し、3 検証方法で確かめてから利用者監査で承認、採用後は学習データとして履歴保管する。

要件文書（requirements.md）は 8 件の Requirement で、役割と性格／入力源／提案単位／提案構造／検証／承認／履歴ロールバック／効果測定を求めている。本設計は計画書 §5.16.1〜§5.16.12（役割・入力・提案単位・提案構造・検証・承認・履歴ロールバック・効果測定・スコープ・命名・旧モジュール・段階的導入）を実装可能な形に落とし込み、先行プロジェクト `dual-reviewer-self-improvement` の素材設計（526 行、Input Model／Signal Extraction Model／Proposal Model／Replay and Backtest Model 等）から **継承可能な 4 モジュール＋ workflow 改善向けの新規 4 モジュール** として再設計する（計画書 §5.16.11）。

本設計の所有物は **入力モデル・提案モデル・検証モデル・承認モデル・履歴ロールバックモデル・効果測定モデル** の 6 つのモデルである。規律ファイルの実体変更は `workflow-management` の所定手続き（drafting → review → approval）経由で実行する（A-007 案 2、Requirement 1 受入 4、2026-05-23 利用者承認）。本機能は **規律変更の提案権** を持ち、**実体変更権** は workflow-management に委ねる責務分離の構造を取る。

## 目標（Goals）

- **規律と実体の双方向同期** を設計レベルで具体化：規律違反データと実体運用パターンの両側からの観察、双方向の追従判断、判断結果の提案化を支援する
- **5 種類の提案単位に限定** し、提案対象を本機能が所有する規律のみに絞る（runtime プロンプト・スキーマ等は対象外、計画書 §5.16.3）
- **YAML 形式の提案構造** を機械可読な形で標準化し、`analysis` および利用者監査者が機械的に処理できる形を保つ（Req 4）
- **3 検証方法**（過去データへの遡及シミュレーション／パイロット運用／影響範囲の事前分析）を支え、replay／backtest（runtime 改善向け）を採用せず別形式で代替する（Req 5、§5.16.5）
- **フェーズ境目の利用者監査** で提案をまとめて判断し、session 内の連続承認を強制しない（Req 6 受入 1）
- **履歴の追跡可能性とロールバック可能性** を 4 サブディレクトリ配置（`learning/workflow/` 配下）で担保する（Req 7、§5.16.7）
- **効果測定 7 指標**（§5.9.5 由来 3 指標＋ workflow 改善運用 4 指標）を支え、`analysis` への機械可読出力を提供する（Req 8、§5.16.8）
- **規律変更権と実体変更権の分離** を機械検査可能な形で担保し、自己承認の空洞化（self-improvement が直接ファイル書き換えを行うリスク）を防ぐ（Req 1 受入 4、A-007 案 2）

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
[input_model（新規実装）]
  └── 来歴情報（source／location／observation）を付与、時系列保持
       ↓
[signal_extraction（新規実装）]
  └── 規律と実体の乖離を抽出、提案候補を生成
       ↓
[proposal_model（新規実装）]
  └── 5 種類の提案単位に分類、YAML 形式で記述
       ↓
[replay_backtest_model 相当（新規実装、3 検証手段）]
  ├── 過去データへの遡及シミュレーション
  ├── パイロット運用（aspirational ステータス）
  └── 影響範囲の事前分析
       ↓
[利用者監査（フェーズ境目）]
  ├── 採用：approved
  ├── 却下：rejected
  └── 後続提案で上書き：superseded
       ↓
[decision_adoption_model（継承）]
  └── 規律状態管理、workflow-management への手続き入力
       ↓
[workflow-management（外部、所定手続き drafting → review → approval）]
  └── docs/disciplines/ の実体変更を実施
       ↓
[learning_layout（継承）]
  └── learning/workflow/ 配下に履歴保管
       ↓
[rollback_model（継承）]
  └── 必要に応じてロールバック（git 履歴活用）
       ↓
[pipeline_driver（継承）]
  └── 全体パイプライン制御
       ↓
[効果測定（7 指標、analysis へ出力）]
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

計画書 §5.16.11 に従い、旧 dual-reviewer-rebuild の 8 モジュールを次のとおり扱う：

| 旧モジュール | 旧規模 | 扱い | 本設計での対応 |
|---|---|---|---|
| `input_model.rb` | 647 行 | **新規実装** | 規律違反検出と実体パターン抽出に特化、Input Model（§6）で再定義 |
| `proposal_model.rb` | 542 行 | **新規実装** | 5 種類の提案種別に特化、Proposal Model（§7）で再定義 |
| `replay_backtest_model.rb` | 465 行 | **新規実装（別形式）** | 過去遡及シミュレーション／パイロット運用／影響範囲分析の 3 手段、Verification Model（§8）で再定義 |
| `signal_extraction.rb` | 397 行 | **新規実装** | 規律遵守検査結果を入力、Architecture §1 のデータフロー内で再定義 |
| `decision_adoption_model.rb` | 323 行 | 継承可能 | 規律状態管理、Approval Model（§9）で活用 |
| `rollback_model.rb` | 303 行 | 継承可能 | git 連携、History and Rollback Model（§10）で活用 |
| `pipeline_driver.rb` | 169 行 | 継承可能 | パイプライン制御、Architecture §1 で活用 |
| `learning_layout.rb` | 156 行 | 継承可能（調整） | 成果物配置、ディレクトリ構造は `learning/workflow/` 配下に調整（§10） |

つまり 8 モジュールの **半分（後者 4 件）は継承、前者 4 件は workflow 改善向けに新規実装**。

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
source: review_record           # review_record / compliance_report / user_audit
location: foundation/.../review-2026-05-13.md   # 証跡ファイルへの相対パス
observation: |
  「主役 Sonnet・敵対役 Opus・判定役 Opus」が複数レビューで一貫して使われている
  （30 文字以上の自由記述、観察した運用パターンの概要）
```

入力源 5 種類のうち、`source` フィールドの値は次の対応関係を持つ：

| 入力源 | source 値 |
|---|---|
| 1. レビュー記録の規律違反検出 | `review_record` |
| 2. 規律遵守検査の結果 | `compliance_report` |
| 3. フェーズ境目の利用者監査 | `user_audit` |
| 4. 実体運用パターン | `compliance_report`（discipline-compliance-reports/ に集約） |
| 5. 累積データ（時系列） | `compliance_report` |

### 6.3 時系列性の保持

- 入力データの時系列性を保持し、累積データから傾向を抽出可能にする（Req 2 受入 3）
- `docs/discipline-compliance-reports/` 配下の日付付き YAML（例：`2026-05-26.yaml`）が時系列の正本
- 傾向抽出は signal_extraction の責務、本モデルは時系列の保持と読み出しを担う

### 6.4 上流機能の出力を直接消費

- 入力源を再定義せず、上流機能（`runtime`／`evaluation`／`workflow-management`／利用者監査）の出力を直接消費する（Req 2 受入 4）
- 入力スキーマの所有者は上流機能、本機能は **読み手** に徹する
- 上流機能の出力形式が変わった場合、本機能の入力モデルも追従するが、独自の再定義は行わない

## 7. 提案モデル（Proposal Model）

### 7.1 提案単位（5 種類）

requirements.md Req 3 受入 1 に対応する 5 種類の提案単位：

| 提案種別（proposal_type） | 内容 | 例 |
|---|---|---|
| `new_discipline` | 新規規律の起案 | モデル能力配分規律の新設、本セッション 27 の事前検査宣言義務規律の新設 |
| `update` | 既存規律の更新 | 規律本文の語彙統一、項目追加 |
| `status_change` | 規律のステータス変更 | enforced ↔ aspirational の切り替え |
| `archive` | 規律の archive 退避（撤廃） | 23 パターン規律の archive 退避、no-unilateral-action の撤去 |
| `consolidation` | 規律間の統廃合 | 旧 dominant-dominated-options と choice-presentation を統合し discipline_options_presentation.md に集約 |

### 7.2 提案対象の限定

- 提案対象は **本機能が所有する規律のみ**（runtime プロンプト・スキーマ等は対象外、Req 3 受入 2）
- 規律の正本配置：`docs/disciplines/discipline_*.md`
- 範囲外の規律候補（runtime 層）はフェーズ 4 完了後の他層改善で扱う

### 7.3 提案種別の組み合わせ

- 提案種別の組み合わせを許容（Req 3 受入 3）
- 例：新規規律の追加と既存規律の archive 退避を **縮減義務** として 1 提案にまとめる（§5.8 第 5 層の処理表面積抑制方針）
- 実例（本セッション 27）：discipline_options_presentation.md の新設（new_discipline）と旧 dominant-dominated-options ／ choice-presentation の archive 退避（archive ×2）を 1 提案として処理した

### 7.4 提案構造（YAML）

requirements.md Req 4 受入 1〜5 に対応する提案構造：

```yaml
proposal_id: WP-001                                # 必須、Workflow Proposal の通し番号
proposal_type: new_discipline                      # 必須、5 種類のいずれか
target_discipline_path: docs/disciplines/discipline_model_capability_allocation.md   # 必須、対象規律パス
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
status: pending                                    # 必須、4 値のいずれか
```

### 7.5 status の 4 値

requirements.md Req 4 受入 4 に対応する status 4 値の遷移：

```
pending（提案レビュー前）
   ├── approved（承認・採用済み）
   │     └── superseded（後続提案で上書き、過去の approved が無効化）
   └── rejected（却下）
```

各値の意味と計画書 §5.16.6 の自然言語語彙との対応：

| status 値 | 意味 | 計画書 §5.16.6 の対応 |
|---|---|---|
| `pending` | 提案レビュー前 | 「提案レビュー」段 |
| `approved` | 承認・採用済み（承認時点で採用扱い） | 「承認」「採用」 |
| `rejected` | 却下 | 「却下」 |
| `superseded` | 後続の `approved` 提案により上書き済み | 計画書語彙に対応なし、本仕様で独自追加 |

### 7.6 提案種別ごとの追加要件

requirements.md Req 3 受入 5 と Req 6 受入 3〜4 に対応する追加要件：

| 提案種別 | 追加要件 |
|---|---|
| `archive` | **撤廃 README 必須**（撤廃理由を `docs/disciplines/archive/<日付>-<id>/README.md` に記録、本セッション 27 の `2026-05-26-consolidation/README.md` が実例） |
| `consolidation` | **対応表必須**（何と何が統合されたか、`docs/disciplines/archive/<日付>-<id>/README.md` 内に記載） |
| `new_discipline` | 提案する規律本文のドラフトと、関連既存規律との関係を明示 |
| `update` | 変更箇所の diff（または変更前後の対照表） |
| `status_change` | ステータス変更の根拠（aspirational → enforced の場合は遵守率の証拠、enforced → aspirational の場合は降格理由） |

### 7.7 統計的証拠（任意）

- 統計的証拠が可能な場合、`statistical_evidence` フィールド（`observed_runs`／`consistent_pattern_ratio` 等）を追加する（Req 4 受入 5）
- 任意フィールドのため、観察データが不足する初期段階では省略可能
- 蓄積後に追記する場合は提案 ID を維持し、`status` を `pending` から動かさずに更新

## 8. 検証モデル（Verification Model）

### 8.1 3 つの検証方法

requirements.md Req 5 受入 1 に対応する 3 検証方法：

| 検証方法 | 内容 | 適用例 |
|---|---|---|
| **過去データへの遡及シミュレーション** | 過去レビュー記録に新規律を当てて違反検出率を計算 | モデル能力配分規律を過去レビュー 17 件に当てて遵守率 100% を確認 |
| **パイロット運用** | 新規律を `status: aspirational` で一定期間運用、遵守率を観察してから `enforced` 昇格 | 新規律を 5〜10 セッション運用、遵守率 80% 以上なら昇格判定 |
| **影響範囲の事前分析** | 既存規律との衝突、撤廃予定規律との関係を機械検査 | 内部リンク `[[name]]` 形式の参照を grep で全件確認、影響範囲を把握 |

### 8.2 過去データへの遡及シミュレーション

- 対象データ範囲を提案ごとに明示（Req 5 受入 2）
- 例：「過去レビュー 17 件、過去遵守検査 30 件」を対象範囲として提案に併記
- 違反検出率の計算：新規律を仮適用したときに違反となる件数 ／ 対象件数
- 過去データの取得元：`.reviewcompass/specs/<feature>/reviews/` 配下、`docs/discipline-compliance-reports/` 配下

### 8.3 パイロット運用

- 新規律を `status: aspirational`（機械検査なし、運用目標）で一定期間運用（Req 5 受入 3）
- パイロット運用期間を提案ごとに記録（例：5 セッション、または 2 週間）
- 期間中の遵守率推移を保持（時系列で `docs/discipline-compliance-reports/` に集約）
- 期間終了時に遵守率が閾値（既定 80% 以上）を満たせば `enforced` 昇格判定

### 8.4 影響範囲の事前分析

- 既存規律との衝突：内部リンク `[[name]]` 形式の参照を grep で全件確認
- 撤廃予定規律との関係：archive 対象の規律と新規律の重複範囲を機械検査
- 機械検査の実装はフェーズ 4 第 1 サイクル以降（フェーズ 1〜3 は手動）

### 8.5 検証不能な提案の扱い

- replay／backtest（runtime 改善向け）を採用しない（Req 5 受入 4）
- 3 つの代替検証手段が機能しない提案は、**利用者監査での明示的判断** で承認する
- 検証不能の根拠を提案の `motivating_evidence` または `proposed_change` に明示

## 9. 承認モデル（Approval Model）

### 9.1 フェーズ境目の利用者監査

- requirements.md Req 6 受入 1 に対応
- session 内での連続承認を強制しない（利用者の負担抑制）
- フェーズ境目（要件 → 設計、設計 → タスク、タスク → 実装等）で提案をまとめて判断
- 判断単位は提案 1 件ずつ、複数提案を 1 ターンで一括承認は許容（明示的肯定発言があれば）

### 9.2 規律の正式化（aspirational → enforced）

- requirements.md Req 6 受入 2 に対応
- 利用者明示承認必須
- 承認時点で `status_change` 提案を `approved` に遷移
- 明示承認の判定基準は [approval-operation](../../../docs/disciplines/discipline_approval_operation.md) 規律に従う（「承認します」「OK」「採用」「進めて」「はい」等の明示的肯定発言）

### 9.3 規律の archive 退避

- requirements.md Req 6 受入 3 に対応
- **撤廃 README 必須**（撤廃理由を記録）
- 撤廃 README の配置先：`docs/disciplines/archive/<日付>-<id>/README.md`
- 撤廃 README の必須内容：退避日、退避ファイル、撤廃理由、利用者明示承認の出典、関連参照

### 9.4 規律間の統廃合

- requirements.md Req 6 受入 4 に対応
- **対応表必須**（何と何が統合されたか）
- 対応表の配置先：撤廃 README 内（archive ディレクトリ単位で 1 ファイル）
- 統廃合の典型パターン：新規規律 1 件＋ archive 退避 2 件以上（縮減義務、§5.8 第 5 層）

### 9.5 4 状態の遷移管理

- requirements.md Req 6 受入 5 に対応
- 提案の 4 状態（pending／approved／rejected／superseded）を提案 YAML ファイルの `status` フィールドで明示
- 状態遷移時は提案 ID を維持、ディレクトリ間で git mv（履歴保持）
- ディレクトリ間の移動規則：
  - `pending` → `proposals/`
  - `approved` → `approved-updates/`
  - `rejected` → `rejected-updates/`
  - `superseded` → `approved-updates/`（status フィールドのみ更新、配置場所は維持）

## 10. 履歴とロールバック（History and Rollback Model）

### 10.1 ディレクトリ配置

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
    └── rollback/                        # ロールバック履歴
        └── <日付>-<id>.yaml

docs/
├── discipline-compliance-reports/       # 遵守検査の時系列（§5.9.5 既存、本機能の入力源 5）
│   └── <日付>.yaml
└── disciplines/archive/                 # 撤廃の経緯（撤廃 README）
    └── <日付>-<id>/
        ├── README.md                    # 撤廃 README（必須）
        └── discipline_*.md              # 撤廃対象の規律本体
```

`learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリは **第 1 期では空置き**（他 4 層改善で活用予定、§5.16.10）。

### 10.2 ロールバック方法

requirements.md Req 7 受入 2 に対応する 3 つのロールバック方法：

| ロールバック方法 | 内容 | 実装 |
|---|---|---|
| **archive から復活** | 撤廃された規律を `docs/disciplines/` に戻す | `git mv docs/disciplines/archive/<日付>-<id>/discipline_*.md docs/disciplines/`、シンボリックリンク再作成 |
| **ステータス変更を戻す** | `enforced` → `aspirational` に格下げ | 規律本文の front-matter `status` フィールドを更新、`status_change` 提案として記録 |
| **規律の更新を取り消す** | 過去版に戻す | git 履歴を活用（`git checkout <commit> -- docs/disciplines/discipline_*.md`） |

### 10.3 ロールバック理由の保存

- requirements.md Req 7 受入 3 に対応
- ロールバック理由を `learning/workflow/rollback/<日付>-<id>.yaml` に保存
- YAML 構造：
  ```yaml
  rollback_id: RB-001
  target_proposal_id: WP-005           # 元の採用提案
  rollback_method: archive_restoration  # archive_restoration / status_downgrade / git_revert
  rollback_reason: |
    新規律が他規律と衝突、影響範囲が事前分析時に把握できていなかった
  rollback_date: 2026-06-15
  related_artifacts:
    - learning/workflow/approved-updates/2026-06-10-WP-005.yaml
    - docs/disciplines/discipline_*.md
  ```

### 10.4 履歴の連結

- requirements.md Req 7 受入 4 に対応
- 提案 → 承認 → ロールバックの追跡を可能にする
- 連結方法：YAML の `target_proposal_id` フィールドで提案 ID を参照、機械的に辿れる形を保つ

### 10.5 整合性検査

- requirements.md Req 7 受入 5 に対応
- 撤廃から復活した規律の機械検査（既存規律との衝突再確認）
- ロールバック後に必ず遵守検査を再実行（`docs/discipline-compliance-reports/` への追記）

## 11. 効果測定（Effect Measurement Model）

### 11.1 7 指標

requirements.md Req 8 受入 1 に対応する 7 指標：

| カテゴリ | 指標 | 定義 |
|---|---|---|
| §5.9.5 由来 | 規律遵守率 | 規律違反件数 ／ 検査対象件数 |
| §5.9.5 由来 | 昇格件数（aspirational → enforced） | パイロット運用を経て正式化した規律の件数 |
| §5.9.5 由来 | 退避件数（規律 → archive） | 撤廃した規律の件数 |
| workflow 改善運用 | 提案件数（種別ごと） | 5 種別ごとの提案件数 |
| workflow 改善運用 | 採用率（採用 ／ 提案合計） | `approved` ／ （`approved` ＋ `rejected` ＋ `superseded`） |
| workflow 改善運用 | ロールバック率（ロールバック ／ 採用） | ロールバック件数 ／ `approved` 件数 |
| workflow 改善運用 | 提案から採用までの平均日数 | 提案日付と承認日付の差の平均 |

### 11.2 phase-review-metric-register への登録

- requirements.md Req 8 受入 2 に対応
- 7 指標を `phase-review-metric-register.md` の **workflow 改善カテゴリ** として登録
- 登録ファイルの配置：`docs/operations/phase-review-metric-register.md`（フェーズ 2 以降の宿題）

### 11.3 analysis への出力

- requirements.md Req 8 受入 3 に対応
- 指標の計算根拠を機械可読な形式（YAML または JSON）で出力
- `analysis` 機能が読み物（運用ダッシュボード／監査用報告等）に取り込む
- 出力先：`learning/workflow/metrics/<日付>.yaml`（フェーズ 4 第 1 サイクル以降）

### 11.4 時系列推移の保持

- requirements.md Req 8 受入 4 に対応
- 指標の時系列推移を保持し、改善活動の長期的傾向を追跡可能にする
- 時系列の保管先：`learning/workflow/metrics/` 配下の日付付き YAML

### 11.5 手動集計の許容

- requirements.md Req 8 受入 5 に対応
- フェーズ 1〜3：手動集計（grep ／ wc ／ jq を使った半自動化）
- フェーズ 4 第 1 サイクル：input_model と signal_extraction の実装、集計の半自動化
- フェーズ 4 第 3 サイクル：自動化完了（§5.16.12）

### 11.6 本セッション 27 で実装した先行ログ

本セッション 27 で新設した `docs/discipline-compliance-reports/options-precheck-log.md` は、本機能の効果測定の **先行実装** に相当する。複数案提示の事前検査宣言義務（規律 options-presentation）の効果を 3 指標（発火率／違反件数／dominated 除外件数）で計測する仕組みで、本機能の Effect Measurement Model のうち **規律遵守率** の特殊形として位置付ける。

## 12. 他機能との接合面（Interfaces with Other Features）

### 12.1 foundation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律検査スキーマ、レビューモード語彙（`manual_dogfooding`／`subagent_mediated`／`runtime_mediated`）、状態軸語彙（`evidence_class`／`validator_status`）、必須メタデータ（severity／target_location／description／rationale） |
| 再定義しない原則 | foundation を正本所有者として参照し、本機能内で再定義しない（Boundary Context 隣接期待） |

### 12.2 runtime との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律遵守検査の結果（レビュー記録の機械検査出力） |
| 形式 | レビュー記録の front-matter＋本文の構造化部分（`findings_by_method` ／ `severity` 集計 等） |

### 12.3 evaluation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律違反データの集計と評価結果 |
| 形式 | `experiments/<run-id>/` 配下の集約 YAML／JSON、3 役所見差分報告（`roles/role_diff_report.json`、A-011 対処で evaluation 設計に追加予定） |

### 12.4 analysis との接合面

| 方向 | 内容 |
|---|---|
| 出力（self-improvement が書く） | 効果測定 7 指標、提案の状態遷移ログ |
| 形式 | `learning/workflow/metrics/<日付>.yaml`（機械可読）、`analysis` が読み物として再構成 |

### 12.5 workflow-management との接合面

| 方向 | 内容 |
|---|---|
| 出力（self-improvement が書く） | 承認済み提案（`learning/workflow/approved-updates/<日付>-<id>.yaml`）を **手続き入力** として workflow-management に渡す |
| 入力（self-improvement が読む） | workflow-management の所定手続き（drafting → review → approval）の完了通知、実体変更後の規律ファイル |
| 責務分離 | 本機能：規律の論理的正本所有者、変更の **提案権**。workflow-management：規律ファイルの **実体変更権**（A-007 案 2、Req 1 受入 4） |

### 12.6 conformance-evaluation との接合面

| 方向 | 内容 |
|---|---|
| 入力（self-improvement が読む） | 規律遵守検査の上流文書との適合性評価結果（2 軸 6 criteria：requirements ／ design × 3 criteria、計画書 §5.10 由来） |
| 形式 | conformance-evaluation の出力（適合度スコア、不適合箇所の特定） |
| 活用方法 | 規律違反の原因が上流文書（intent ／ requirements ／ design）にある場合、`new_discipline` または `update` 提案の motivating_evidence に conformance-evaluation の出力を含める |
| 依存方向 | conformance-evaluation → self-improvement（self-improvement が conformance-evaluation の出力を読む、A-008 で確定済み 2026-05-23） |

## 13. 要件追跡表（Requirements Traceability）

| Requirement | 対応する設計章 |
|---|---|
| Req 1：役割と性格 | §1 概要／§2 目標／§3 範囲外／§5.2 責務分担モデル（A-007 案 2） |
| Req 2：入力（何を見て改善するか） | §6 入力モデル |
| Req 3：提案単位（何を改善するか） | §7.1 提案単位／§7.2 提案対象の限定／§7.3 提案種別の組み合わせ |
| Req 4：提案の構造 | §7.4 提案構造（YAML）／§7.5 status の 4 値／§7.7 統計的証拠 |
| Req 5：検証（採用前にどう試すか） | §8 検証モデル |
| Req 6：承認 | §9 承認モデル |
| Req 7：履歴とロールバック | §10 履歴とロールバック |
| Req 8：効果測定 | §11 効果測定 |

## 14. 設計決定（Key Decisions）

### Decision 1：規律変更権と実体変更権の分離（A-007 案 2）

self-improvement は規律の論理的正本所有者だが、規律ファイルの実体変更は workflow-management の所定手続き（drafting → review → approval）経由で実行する。本機能は **提案権** のみを持ち、ファイルの直接書き換えは行わない。

**根拠**：自己承認の空洞化を防ぐ（self-improvement が独自に規律を書き換えると、規律変更が起草と判定を兼ねる構造になる）。利用者明示承認 2026-05-23（A-007）。

### Decision 2：スコープを workflow 層に限定

第 1 期は workflow 層改善のみを担当、他 4 層（prompt／policy／schema／runtime）は別計画書で扱う。

**根拠**：runtime 層改善向けの replay／backtest は workflow 改善で使いにくく、性格が異なる（計画書 §5.16.5）。第 1 期で workflow 層を確立してから他層を扱う段階的導入方針（計画書 §7）。

### Decision 3：replay／backtest を採用せず 3 検証方法で代替

過去データへの遡及シミュレーション／パイロット運用／影響範囲の事前分析の 3 つを採用。

**根拠**：規律は「人間が守るべきルール」であり、過去入力に対する出力の再現（replay／backtest）では検証できない。実体運用との乖離を時系列で観察する別形式が必要（計画書 §5.16.5）。

### Decision 4：4 サブディレクトリ配置（learning/workflow/）

proposals／approved-updates／rejected-updates／rollback の 4 サブディレクトリで提案の状態遷移を物理ディレクトリで表現。

**根拠**：機械検査と人間の目視確認の両方を支援、git mv で履歴を保持しながら状態遷移できる構造（§5.16.7、§5.16.10）。

### Decision 5：効果測定 7 指標体系（§5.9.5 由来 3 ＋ workflow 改善運用 4）

§5.9.5 既存の 3 指標を継承しつつ、workflow 改善運用の 4 指標を追加。

**根拠**：規律変更の活動そのものの効果測定が必要、提案 → 承認 → 採用 → ロールバックのパイプライン全体を追跡（計画書 §5.16.8）。

### Decision 6：4 状態体系（pending／approved／rejected／superseded）

提案の状態を 4 値で表現、`superseded` は本仕様の独自追加。

**根拠**：計画書 §5.16.6 の自然言語語彙（提案レビュー／承認／採用／却下）に対応しつつ、後続提案による上書きを表現する状態を追加（過去の `approved` が後続の `approved` で無効化されるケースを区別）。

### Decision 7：旧 8 モジュールの半分継承・半分新規

継承可能 4 件：decision_adoption_model／rollback_model／pipeline_driver／learning_layout
新規実装 4 件：input_model／proposal_model／replay_backtest_model 相当／signal_extraction

**根拠**：旧モジュールの再利用と workflow 改善向けの再設計のバランス（計画書 §5.16.11）。

### Decision 8：縮減義務の運用化（処理表面積抑制）

新規規律の追加時に既存規律 1 件以上の統廃合をセットで提案する縮減義務を運用化（§5.8 第 5 層）。

**根拠**：規律体系の肥大化を構造的に防ぐ。実例：本セッション 27 の discipline_options_presentation.md 新設＋旧 2 件 archive 退避（純増ゼロ）。

## 15. Boundary Context との整合確認（Boundary Context Compliance）

requirements.md の Boundary Context との整合：

### In scope（範囲内）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 規律と実体の乖離の観察 | §3 アーキテクチャ §1 データの流れ／§6 入力モデル |
| 5 種類の提案単位 | §7.1 提案単位 |
| 提案構造の定義（YAML 形式） | §7.4 提案構造（YAML） |
| 3 つの検証方法 | §8 検証モデル |
| フェーズ境目の利用者監査による承認 | §9 承認モデル |
| 履歴とロールバック（learning/workflow/ 4 サブディレクトリ） | §10 履歴とロールバック |
| 効果測定 7 指標（§5.9.5 の 3 指標 ＋ workflow 改善運用の 4 指標） | §11 効果測定 |

### Out of scope（範囲外）の整合

| Boundary Context の記述 | 本設計での対応 |
|---|---|
| 他 4 層改善（prompt／policy／schema／runtime） | §3 範囲外で明示、Decision 2 |
| `learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリは第 1 期で空置き | §10.1 で明示 |
| replay／backtest（runtime 改善向け） | §3 範囲外で明示、Decision 3 |
| 論文化からの分離 | §3 範囲外で明示 |
| 外部プロジェクトからの取り込み証跡 | §3 範囲外で明示 |

### 隣接仕様の期待との整合

| 隣接機能 | Boundary Context の期待 | 本設計での対応 |
|---|---|---|
| foundation | 規律検査スキーマ等を再定義せず参照 | §12.1 で明示 |
| runtime | 規律遵守検査の結果を入力源として受け取る | §12.2 で明示 |
| evaluation | 規律違反データの集計と評価結果を入力源として受け取る | §12.3 で明示 |
| analysis | 効果測定 7 指標を本機能から受け取る | §12.4 で明示 |
| workflow-management | 規律の昇格・退避・統廃合を所定手続きに従って実行 | §5.2 責務分担モデル／§9 承認モデル／§12.5 で明示 |
| conformance-evaluation | 規律遵守検査の上流文書との適合性評価結果を入力源として活用可能 | §12.6 で明示 |

## 16. design.alignment 段の未解決論点（Open Issues for Design Alignment Gate）

本セッション 27 末時点で本機能の design.drafting 段で未解決の論点は **なし**。

機能横断レビューで対処済みの所見（A-007／A-008）：

- **A-007**：self-improvement と workflow-management の権限分散調停 → Decision 1（A-007 案 2）として本設計に反映済み（Req 1 受入 4 由来）
- **A-008**：conformance-evaluation から self-improvement への出力方向 → §12.6 で「conformance-evaluation → self-improvement の方向」として整理済み（A-008 対処、2026-05-23）

機能横断の未消化所見（A-011）は analysis／evaluation の接合面に関するもので、本機能とは独立。design レビュー波段で消化予定。

## 17. 起草完了基準（Completion Criteria）

本設計が design.drafting 段の完了とみなされる条件：

- [x] 全 17 章（§1〜§17）が記述されている
- [x] requirements.md の全 8 件の Requirement が §13 要件追跡表で章と対応している
- [x] 計画書 §5.16 の 12 小節（§5.16.1〜§5.16.12）の方針が反映されている
- [x] 他機能との接合面が §12 で全 6 機能分（foundation／runtime／evaluation／analysis／workflow-management／conformance-evaluation）明示されている
- [x] Boundary Context との整合が §15 で確認されている
- [x] 機能横断所見（A-007／A-008）の対処が §16 で明示されている
- [x] 主要な設計決定（8 件）が §14 で明示されている

本設計の triad-review 段（次セッション以降）で扱う観点（Design 観点 10 件、計画書 §5.9.2 由来）：

1. 設計と要件の対応
2. 設計の内部整合
3. 設計の他機能との整合
4. 設計の正本との整合
5. 検証可能性
6. 実装可能性
7. 段階的導入の妥当性
8. 拡張余地と将来宿題
9. テスト戦略
10. リスクと残余課題
