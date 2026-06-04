# self-improvement implementation triad-review target bundle

run_id: 2026-06-04-self-improvement-implementation-review-run

## Review instruction

Review whether the self-improvement implementation, tests, and operation documents satisfy the upstream requirements/design/tasks and the approved workflow. Do not copy review viewpoints from workflow-management merely because its review-run was a prior example. Treat prior review-runs only as evidence for the common review-run artifact structure.

Feature-specific context: self-improvement is generated from ReviewCompass intent and feature-partitioning as a workflow-layer improvement feature. Its responsibility is bidirectional synchronization between discipline and practice. It has proposal authority only; actual discipline file changes must go through workflow-management. Evaluate the implementation around input modeling, signal extraction, proposal generation, verification, approval, rollback, effect measurement, machine verification, interfaces, and traceability.

Focus areas:

1. Upstream traceability: requirements/design/tasks/spec.json are satisfied, especially T-001 through T-011.
2. Authority separation: self-improvement does not directly edit `docs/disciplines/discipline_*.md`; it emits proposals and evidence for workflow-management.
3. Proposal lifecycle: proposal_id allocation, proposal schema, status transitions, superseded/reopen evidence, rollback linkage, and materialization metadata behave as specified.
4. Verification and fail-closed behavior: invalid inputs, unknown enum values, missing required fields, insufficient provenance, and inconclusive machine checks do not pass silently.
5. Feature-specific review-run discipline: this review target was generated from the self-improvement feature context, not by copying workflow-management-specific review criteria.
6. Tests and evidence: pytest coverage maps to T-001..T-011, includes negative cases, and validates machine-checkable completion predicates.
7. Deployment/auditability: autonomous plan/ledger and plan memo preserve enough evidence for post-run audit without relying only on transient conversation context.

Use the output contract in the outer prompt. Findings should be actionable and grounded in the quoted target files. Triage findings into the established three levels. Important findings require a concrete candidate fix plan and approval/proxy decision before implementation.

## FILE: .reviewcompass/specs/self-improvement/requirements.md

```text
# Requirements Document：self-improvement

## Introduction

`self-improvement` は ReviewCompass の改善機能だが、第 1 期では **workflow 層改善のみ**を担う。先行プロジェクトの自己改善仕様（8 要件、主に runtime 層改善向け）は workflow 改善の性格に合わないため、計画書 §5.16 で全面書き直しを確定済み。

workflow 改善は、**規律と実体の乖離を観察し、規律を実体に追従させるか、実体を規律に追従させるかを判断する機能**である（§5.16.1）。他 4 層改善（prompt／policy／schema／runtime）はスコープ外、フェーズ 4 完了後に効果測定機構を含む再設計を別計画書として起こす（計画書 §7）。

## Boundary Context

- **In scope（範囲内）**
  - 規律と実体の乖離の観察（規律違反検出結果、利用者監査での指摘、実体運用パターン）
  - 5 種類の提案単位（新規規律の起案／既存規律の更新／規律のステータス変更／規律の archive 退避／規律間の統廃合）
  - 提案構造の定義（YAML 形式、motivating_evidence／statistical_evidence 等を含む）
  - 3 つの検証方法（過去データへの遡及シミュレーション／パイロット運用／影響範囲の事前分析）
  - フェーズ境目の利用者監査による承認
  - 履歴とロールバック（learning/workflow/ 4 サブディレクトリ）
  - 効果測定 7 指標（§5.9.5 の 3 指標 ＋ workflow 改善運用の 4 指標）

- **Out of scope（範囲外）**
  - 他 4 層改善（prompt／policy／schema／runtime）：フェーズ 4 完了後の別計画書
    - これに伴い、`learning/findings/`／`learning/backtests/`／`learning/templates/` の 3 ディレクトリは第 1 期では空置き（他層改善で活用予定、計画書 §5.16.10 由来）。本機能の第 1 期出力は `learning/workflow/` 配下のみ
  - replay／backtest（runtime 改善向け、workflow 改善では使わない）：別形式の検証で代替（§5.16.5）
  - 論文化からの分離：方針は継承するが、個別の規律ファイルとしては立てない
  - 外部プロジェクトからの取り込み証跡：フェーズ 4 完了後、外部プロジェクトとの規律共有時に検討

- **隣接仕様の期待**
  - `foundation`：規律検査スキーマ、レビューモード語彙、状態軸語彙を再定義せず参照
  - `runtime`：規律遵守検査の結果（レビュー記録の機械検査出力）を入力源として受け取る
  - `evaluation`：規律違反データの集計と評価結果を入力源として受け取る
  - `analysis`：効果測定 7 指標を本機能から受け取る
  - `workflow-management`：規律の昇格・退避・統廃合を所定手続き（drafting → review → approval）に従って実行
  - `conformance-evaluation`：規律遵守検査の上流文書との適合性評価結果を入力源として活用可能

## Requirements

### Requirement 1：役割と性格

**目的（Objective）**：保守担当者が、本機能の責務範囲（規律と実体の双方向同期）を明確に把握できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は workflow 層改善のみを第 1 期スコープとする。他 4 層改善（prompt／policy／schema／runtime）は実施しない。
2. 本機能は規律と実体の乖離を観察し、規律を実体に追従させるか実体を規律に追従させるかを判断する責務を持つ。
3. 本機能はデータの流れを次のとおりとする：入力（規律遵守検査の結果 ＋ 実体観察パターン ＋ 利用者監査での指摘）→ signal 抽出 → 提案構築 → 検証 → 利用者承認 → 採用または却下 → ロールバック → 出力（learning/workflow/ 配下の改善履歴 ＋ docs/disciplines/ の更新）。
4. 本機能は規律の論理的正本所有者であり、規律ファイル（`docs/disciplines/discipline_*.md`）に対する**変更の提案権**を持つ。ただし**規律ファイルの実体変更は `workflow-management` の所定手続き（drafting → review → approval、Requirement 6 由来）経由で実行する**。本機能が直接ファイル書き換えを行うことはなく、承認後に `workflow-management` が手続きとして実体変更を実施する。本調停ルールは案 2（2026-05-23 利用者承認、A-007 由来）として確定。

### Requirement 2：入力（何を見て改善するか）

**目的**：本機能の実装者が、改善活動の入力源を明確に把握し、規律と実体の乖離を網羅的に観察できるようにする。

#### 受入基準

1. 本機能は次を入力源として受け取る：レビュー記録の規律違反検出結果（`foundation` 仕様 Requirement 6 受入 1〜2 の必須メタデータ検査出力）、規律遵守検査の結果（各規律の `evidence_check_method` の実行結果）、フェーズ境目の利用者監査での指摘、実体運用で新たに観察された運用パターン、規律違反の累積データ（時系列、`docs/discipline-compliance-reports/`）。
2. 本機能は入力源ごとに来歴情報（source／location／observation の 3 要素）を保持する。
3. 本機能は入力データの時系列性を保持し、累積データから傾向を抽出できるようにする。
4. 本機能は入力源を再定義せず、上流機能（`runtime`／`evaluation`／`workflow-management`／利用者監査）の出力を直接消費する。

### Requirement 3：提案単位（何を改善するか）

**目的**：本機能の利用者と実装者が、改善提案の対象範囲を 5 種類に限定して扱えるようにする。

#### 受入基準

1. 本機能は提案種別を 5 種類に限定する：`new_discipline`（新規規律の起案）／`update`（既存規律の更新）／`status_change`（規律のステータス変更、enforced ↔ aspirational）／`archive`（規律の archive 退避、撤廃）／`consolidation`（規律間の統廃合）。
2. 本機能は提案対象を本機能が所有する規律のみとする（runtime プロンプト・スキーマ等は対象外）。
3. 本機能は提案種別の組み合わせを許容する。例：新規規律の追加と既存規律の archive 退避を縮減義務として 1 提案にまとめる（§5.8 第 5 層の処理表面積抑制方針）。
4. 本機能は対象規律のパスを `target_discipline_path` フィールドで明示する。
5. 本機能は提案種別ごとに必要な追加情報を定義する（例：archive 退避は撤廃 README 必須、統廃合は対応表必須）。

### Requirement 4：提案の構造

**目的**：本機能の出力消費者（利用者監査者、`analysis`、他機能）が、提案を機械可読な形で扱えるようにする。

#### 受入基準

1. 本機能の提案は YAML 形式で記述し、最低限、`proposal_id`／`proposal_type`／`target_discipline_path`／`motivating_evidence`／`proposed_change`／`expected_effect`／`status` を含む。
2. `motivating_evidence` は配列で、各要素は `source`（`review_record`／`compliance_report`／`user_audit`／`observation_pattern` のいずれか）／`location`（証跡ファイルへの相対パス）／`observation`（30 文字以上の自由記述）の 3 フィールドを持つ。`observation_pattern`（実体運用で新たに観察された運用パターン）は受入 1 の入力源 4（実体運用パターン）に対応する独立の出所種別（設計 §6.2 で確定、2026-05-29 セッション 39 利用者承認の遡及修正 topic-104）。
3. `proposal_type` は Requirement 3 受入 1 の 5 種類のいずれかをとる。
4. `status` は次の 4 値をとる。計画書 §5.16.6 の自然言語語彙との対応も明示する：
   - `pending`：提案レビュー前（計画書「提案レビュー」段に対応）
   - `approved`：承認・採用済み（計画書「承認」「採用」に対応。承認時点で採用扱いとする）
   - `rejected`：却下（計画書「却下」に対応）
   - `superseded`：後続提案に置き換え済み（過去の `approved` が後続の `approved` 提案により上書きされた状態。計画書語彙には対応する語なし、本仕様で独自追加）
5. 本機能は統計的証拠が可能な場合、`statistical_evidence` フィールド（`observed_runs`／`consistent_pattern_ratio` 等）を追加する。

### Requirement 5：検証（採用前にどう試すか）

**目的**：本機能の実装者と利用者が、replay／backtest（runtime 改善向け）が使いにくい workflow 改善において、代替の検証方法で採用前の試行ができるようにする。

#### 受入基準

1. 本機能は次の 3 つの検証方法を支える：
   - **過去データへの遡及シミュレーション**：過去レビュー記録に新規律を当てて違反検出率を計算
   - **パイロット運用**：新規律を `status: aspirational` で一定期間運用、遵守率を観察してから `enforced` 昇格
   - **影響範囲の事前分析**：既存規律との衝突、撤廃予定規律との関係を機械検査
2. 本機能は遡及シミュレーションを支援する対象データ範囲を提案ごとに明示する（例：過去レビュー 17 件、過去遵守検査 30 件）。
3. 本機能はパイロット運用期間を提案ごとに記録し、期間中の遵守率推移を保持する。
4. 本機能は replay／backtest（runtime 改善向け）を採用しない。代替検証手段が機能しない提案は、利用者監査での明示的判断で承認する。

### Requirement 6：承認

**目的**：本機能の運用者が、規律の正式化・退避・統廃合をフェーズ境目で明示承認できるようにする。

#### 受入基準

1. 本機能はフェーズ境目の利用者監査で提案をまとめて判断する。session 内での連続承認を強制しない。
2. 本機能は規律の正式化（aspirational → enforced）に利用者明示承認を必須とする。
3. 本機能は規律の archive 退避に撤廃 README（撤廃理由を記録）を必須とする。
4. 本機能は規律間の統廃合に対応表（何と何が統合されたか）を必須とする。
5. 本機能は提案の 4 状態（pending／approved／rejected／superseded、Requirement 4 受入 4）を明示し、利用者監査での状態遷移を追跡可能にする。

### Requirement 7：履歴とロールバック

**目的**：本機能の利用者と保守担当者が、過去の改善活動を追跡し、誤った採用をロールバックできるようにする。

#### 受入基準

1. 本機能は次のディレクトリ配置で履歴を保管する：
   - `learning/workflow/proposals/<日付>-<id>.yaml`：提案
   - `learning/workflow/approved-updates/<日付>-<id>.yaml`：承認済み
   - `learning/workflow/rejected-updates/<日付>-<id>.yaml`：却下済み
   - `learning/workflow/rollback/<日付>-<id>.yaml`：ロールバック履歴
   - `docs/discipline-compliance-reports/<日付>.yaml`：遵守検査の時系列（§5.9.5 既存）
   - `docs/disciplines/archive/<日付>-<id>/README.md`：撤廃の経緯（軽量 reopen 手続き、2026-05-26 セッション 27 利用者明示承認「候補 1」、実体配置と design.md §10.3／§11.1 に整合）
2. 本機能は次のロールバック方法を支える：archive から復活（撤廃された規律を `docs/disciplines/` に戻す）／ステータス変更を戻す（enforced → aspirational に格下げ）／規律の更新を取り消す（過去版に戻す、git 履歴を活用）。
3. 本機能はロールバック理由を `learning/workflow/rollback/<日付>-<id>.yaml` に保存する。
4. 本機能は履歴の連結を保持し、提案 → 承認 → ロールバックの追跡を可能にする。
5. 本機能はロールバック後の整合性検査（例：撤廃から復活した規律の機械検査）を要求する。

### Requirement 8：効果測定

**目的**：本機能の運用者と監査担当が、改善活動自体の有効性を測定できるようにする。

#### 受入基準

1. 本機能は次の 7 指標を支える：
   - §5.9.5 由来の 3 指標：規律遵守率／昇格件数（aspirational → enforced）／退避件数（規律 → archive）
   - workflow 改善運用の 4 指標：提案件数（種別ごと）／採用率（採用／提案合計）／ロールバック率（ロールバック／採用）／提案から採用までの平均日数
2. 本機能は 7 指標を `phase-review-metric-register.md` の workflow 改善カテゴリとして登録する。
3. 本機能は指標の計算根拠を機械可読な形式で出力し、`analysis` 機能が読み物（運用ダッシュボード／監査用報告等）に取り込めるようにする。
4. 本機能は指標の時系列推移を保持し、改善活動の長期的傾向を追跡可能にする。
5. 本機能は手動集計を許容する（フェーズ 4 第 3 サイクルまで自動化を進める、§5.16.12）。

## Change Intent

本仕様は計画書 §5.16 の全面書き直し方針に従い、先行プロジェクトの自己改善仕様（130 行 8 要件、主に runtime 層改善向け）を **workflow 層改善に特化**した 8 要件として再設計した。

ReviewCompass 固有の追加・変更：

- スコープを workflow 層改善のみに限定（Requirement 1 受入 1、§7 由来）
- 規律と実体の双方向同期を中核責務に設定（Requirement 1 受入 2、§5.16.1 由来）
- 5 種類の提案単位を限定列挙（Requirement 3、§5.16.3 由来）
- 提案構造を YAML フォーマットで標準化（Requirement 4、§5.16.4 由来）
- 検証方法を replay／backtest から 3 つの代替手段に変更（Requirement 5、§5.16.5 由来）
- 効果測定 7 指標を採用（Requirement 8、§5.16.8 由来、§5.9.5 連動）
- 隣接仕様として `workflow-management`／`conformance-evaluation` を追加（Boundary Context 隣接期待、計画書 §3.1 由来）
- 出力先を `learning/workflow/` に限定（Requirement 7 受入 1、§5.16.10 由来）

スコープ外の明示（§5.16.9 由来）：

- 他 4 層改善（prompt／policy／schema／runtime）：フェーズ 4 完了後の別計画書
- 旧 R3 の replay／backtest：workflow 改善では使わない（Requirement 5 受入 4）
- 旧 R6 の論文化からの分離：方針継承のみ、個別規律ファイルは立てない
- 旧 R7 の手動 vs runtime 証跡：規律の出所識別子（source）として `motivating_evidence.source` で吸収
- 旧 R8 の取り込み証跡：フェーズ 4 完了後の宿題

旧実装モジュールとの関係（§5.16.11 由来）：

- 継承可能 4 モジュール：`decision_adoption_model`（規律状態管理）／`rollback_model`（git 連携）／`pipeline_driver`（パイプライン制御）／`learning_layout`（成果物配置）
- 新規実装 4 モジュール：`input_model`（規律違反検出と実体パターン抽出）／`proposal_model`（5 種類の提案種別）／`replay_backtest_model` 相当（過去遡及シミュレーション・パイロット運用・影響範囲分析）／`signal_extraction`（規律遵守検査結果を入力）

機能横断レビューで対処された所見：

- 本機能に関連する所見：
  - A-007（self-improvement と workflow-management の権限分散調停、Requirement 1 受入 4 で対処済み、案 2 採用、2026-05-23 利用者承認）
  - A-008（conformance-evaluation から self-improvement への出力方向、conformance-evaluation 側 Boundary Context 修正で対処済み、2026-05-23、本機能側は変更不要だが整合確認済み）
- 参考：他機能の所見（A-001／A-003／A-004／A-005 とも 2026-05-23 対処済み）の対処履歴は [learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml) を参照

```

## FILE: .reviewcompass/specs/self-improvement/design.md

```text
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

本接合面の最終確定は design レビュー波段（次セッション以降）で workflow-management 設計改訂と合わせて実施する。波及所見として `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に A-003／F-008 を追記済み（本セッション 27 確定）。

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

- **A-003／F-008**：self-improvement の status `approved` 遷移と workflow-management の手続き完了の時系列契約・完了通知形式は本機能の design.md §13.5 で詳細提案を記述したが、workflow-management 側の合意は design レビュー波段で取る。`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記（本セッション 27 確定）

### 19.3 他機能横断の未消化所見

- **A-011（✅ 対処済み、2026-05-26 セッション 28）**：analysis／evaluation 接合面の `roles/role_diff_report.json` 新設は evaluation 設計に反映済み（正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` 166 行）。本機能の §13.3 で参照しており、A-011 消化が本機能の design.alignment の前提だったが、**前提は充足済み**。本欄は topic-103／G-001 で陳腐化記述を更新（2026-05-29 セッション 39）。現時点で §19.3 に未消化の他機能横断所見はない

### 19.4 機能横断レビューで対処済みの所見

- **A-007（既存）**：self-improvement と workflow-management の権限分散調停 → Decision 1（A-007 案 2）として反映済み
- **A-008（既存）**：conformance-evaluation から self-improvement への出力方向 → §13.6 で「conformance-evaluation → self-improvement の方向」として整理済み（2026-05-23）

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

```

## FILE: .reviewcompass/specs/self-improvement/tasks.md

```text
---
spec: self-improvement
phase: tasks
stage: drafting
author:
  identity: claude-code-main-session
  model: claude-sonnet-4-6
  role: drafter
created_at: 2026-05-29
language: ja
---

# Tasks Document：self-improvement

## 概要（Overview）

本文書は `self-improvement`（第 1 期は workflow 層改善のみを担う機能）の実装タスクを列挙する。本機能の中核責務は **規律と実体の双方向同期** であり、規律違反データと実体運用パターンを観察して「規律を実体に追従させる」か「実体を規律に追従させる」かを判断し、提案（YAML 形式）として記述・検証・承認・履歴保管する。規律ファイル（`docs/disciplines/discipline_*.md`）の実体変更は `workflow-management` の所定手続き経由で実施し、本機能は **提案権** のみを持つ（A-007 案 2、Requirement 1 受入 4）。

タスクは設計文書（design.md）の所有モデル単位でまとめる。本機能の所有物は 7 モデル（入力モデル §6 ／ signal_extraction モデル §7 ／ 提案モデル §8 ／ 検証モデル §9 ／ 承認モデル §10 ／ 履歴ロールバックモデル §11 ／ 効果測定モデル §12）に加え、他機能との接合面（§13）・機械検査の具体手段（§17）・テスト戦略（§18）である。計画書 §5.16 の全面書き直し方針に従い、旧 8 モジュールの半分継承・半分新規実装（design §3 旧モジュールとの対応）として再設計する。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの所有モデル領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる（workflow-management T-001〜T-011 の粒度方針を継承）
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む。データの流れ（design §5.1：入力 → signal 抽出 → 提案 → 検証 → 承認 → 履歴 → 効果測定）を依存順の基本とする
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **段階的導入**：第 1 期（フェーズ 1〜3）は手動 grep ／ jq による半自動運用、自動化はフェーズ 4 で段階的に進める（design §17.4 ／ §12.5、Req 8 受入 5）。各タスクの完了条件は第 1 期スコープ（手動運用が機械的に検証可能なこと）で判定する
- **contract consumer 原則**：foundation が所有する語彙正本（規律検査スキーマ・レビューモード語彙・状態軸語彙）を再定義せず参照のみで使用（design §13.1）。入力源は上流機能（runtime ／ evaluation ／ workflow-management ／利用者監査）の出力を直接消費し、本機能内で再定義しない（Req 2 受入 4）
- **権限分離の徹底**：規律ファイルの実体変更は本機能では行わず、承認済み提案を workflow-management に渡すのみ（A-007 案 2）。本機能が `docs/disciplines/discipline_*.md` へ直接書き込まないことを機械検査（MV-1、design §17.1）でゲートする
- **fail-closed の徹底**：機械検査（§17）は検査失敗時に遮断（fail-closed、design §17.3）、本機能の処理を継続させず利用者監査に上げる

`self-improvement` 全体で 11 タスク。

## タスク一覧（Task List）

### T-001：成果物配置の準備

- **対応設計節**：design.md §5.1 データの流れ、§11.1 ディレクトリ配置
- **対応要件**：Requirement 7 受入 1（履歴の 4 サブディレクトリ配置）
- **責務**：リポジトリ内に学習データの物理配置を新設する。`learning/workflow/` 配下の 4 サブディレクトリ（`proposals/` ／ `approved-updates/` ／ `rejected-updates/` ／ `rollback/`）＋効果測定出力先 `metrics/`、第 1 期で空置きの 3 ディレクトリ（`learning/findings/` ／ `learning/backtests/` ／ `learning/templates/`、§5.16.10 由来、他 4 層改善で活用予定）、入力源・出力先の関連ディレクトリ（`docs/discipline-compliance-reports/` ／ `docs/disciplines/archive/`）、検査スクリプト配置先 `tools/`、テスト配置先 `tests/self-improvement/` を新設し、各ディレクトリに配置目的を記す README を置く。空ディレクトリは `.gitkeep` で Git 追跡可能にする（workflow-management T-001 の方針継承）。**スキーマ配置（topic-106／F-007、§11.1）**：永続データの正本スキーマは `learning/workflow/schemas/`、ツール内部の中間スキーマは `tools/self_improvement/schemas/` の専用サブフォルダに分離する（データと混在させない）。**命名規約（topic-105／F-006）**：import 対象の Python パッケージ／モジュールはアンダースコア区切り（`tools/self_improvement/`）、import されない単独実行 CLI スクリプトはハイフン区切り（`tools/self-improvement-check.py`）。この規約を `tools/README.md` に明記する
- **前提タスク**：なし（起点）
- **成果物**：
  - `learning/workflow/proposals/.gitkeep`
  - `learning/workflow/proposals/README.md`（`status: pending` の提案 YAML の配置説明）
  - `learning/workflow/approved-updates/.gitkeep`
  - `learning/workflow/approved-updates/README.md`（`status: approved`／`superseded` の配置説明、workflow-management の手続き入力経路、§13.5）
  - `learning/workflow/rejected-updates/.gitkeep`
  - `learning/workflow/rejected-updates/README.md`
  - `learning/workflow/rollback/.gitkeep`
  - `learning/workflow/rollback/README.md`（ロールバック履歴 YAML の配置説明）
  - `learning/workflow/metrics/.gitkeep`
  - `learning/workflow/metrics/README.md`（効果測定 7 指標の時系列保管先、§12.3）
  - `learning/workflow/schemas/.gitkeep`、`learning/workflow/schemas/README.md`（永続データ正本スキーマ proposal／rollback／metrics の配置説明、topic-106／F-007）
  - `tools/self_improvement/schemas/.gitkeep`（ツール内部スキーマ provenance／signal の配置、topic-106／F-007）
  - `learning/findings/.gitkeep`、`learning/backtests/.gitkeep`、`learning/templates/.gitkeep`（第 1 期空置き、各 README に「他 4 層改善で活用予定、所有権はフェーズ 4 完了後の別計画書で確定」を明記、A-012 注記）
  - `docs/discipline-compliance-reports/README.md`（遵守検査の時系列 YAML の配置説明、入力源 2／5、§5.9.5 既存との整合）
  - `docs/disciplines/archive/README.md`（撤廃 README ＋撤廃規律本体の配置説明。既存の `archive/2026-05-26-consolidation/` と整合）
  - `tools/README.md` への追記（`self-improvement-check.py` の配置先説明、実体はフェーズ 4 第 1 サイクル以降、第 1 期は手動 grep。＋命名規約：パッケージ＝アンダースコア／単独 CLI スクリプト＝ハイフン、topic-105／F-006）
  - `tests/self-improvement/.gitkeep`
- **完了条件**：
  1. `learning/workflow/` 配下の 6 ディレクトリ（proposals／approved-updates／rejected-updates／rollback／metrics／schemas）と各 README が存在し、`.gitkeep` で Git 追跡可能である。スキーマは `schemas/` 専用サブフォルダに分離されている（topic-106／F-007）
  2. 空置き 3 ディレクトリ（findings／backtests／templates）が存在し、各 README に「第 1 期空置き、所有権はフェーズ 4 完了後に確定」が明記されている（A-012 注記）
  3. `docs/discipline-compliance-reports/` ／ `docs/disciplines/archive/` の README が存在し、design §11.1 の配置ツリーと一致する（metrics／schemas を含む）
  4. `tests/self-improvement/.gitkeep` が Git 追跡可能である
  5. `tools/self_improvement/schemas/` が存在し、`tools/README.md` に命名規約（パッケージ＝アンダースコア／単独 CLI スクリプト＝ハイフン、topic-105／F-006）が明記されている
- **テスト要件**：ディレクトリ存在検査（learning/workflow/ 配下 6 ＋ 空置き 3 ＋ 関連 2 ＋ tools/self_improvement/schemas/）、README 存在検査、`.gitkeep` 存在検査、空置き 3 ディレクトリの注記文言の grep 検査、命名規約の grep 検査（tools/README.md、topic-105）

### T-002：入力モデル（Input Model）

- **対応設計節**：design.md §6.1〜§6.4
- **対応要件**：Requirement 2 受入 1〜4
- **責務**：5 種類の入力源（レビュー記録の規律違反検出 ／ 規律遵守検査結果 ／ 利用者監査の指摘 ／ 実体運用パターン ／ 累積データ時系列）を読み込み、来歴情報 3 要素（`source` ／ `location` ／ `observation`）を付与する入力モデルを実装。`source` の値域 4 種（`review_record` ／ `compliance_report` ／ `user_audit` ／ `observation_pattern`）を符号化し、入力源 4（実体運用パターン）を独自 source 値 `observation_pattern` に分離（F-007 対処、design §6.2）。時系列性を保持し累積データから傾向抽出可能にする（傾向抽出自体は signal_extraction T-003 の責務、本タスクは保持と読み出し）。上流機能の出力を直接消費し、入力スキーマを再定義しない（read-only、Req 2 受入 4）
- **前提タスク**：T-001
- **成果物**：
  - `tools/self_improvement/input_model.py`（5 入力源の読み込み ＋ 来歴情報付与 ＋ 時系列保持。第 1 期は手動抽出を補助する半自動実装）
  - `tools/self_improvement/schemas/provenance.schema.json`（来歴情報スキーマ：`source` enum 4 値 ／ `location`（相対パス）／ `observation`（30 文字以上の自由記述）。30 文字未満は結論不能で fail-closed）
- **完了条件**：
  1. 5 種類の入力源すべてに対し、来歴情報 3 要素が付与される
  2. `source` の値域が 4 値（review_record ／ compliance_report ／ user_audit ／ observation_pattern）に enum 制限され、未知の値が fail-closed になることが機械検証される
  3. `observation` の 30 文字以上制約が機械検証される（30 文字未満は DEVIATION）
  4. 入力データが時系列で保持され、`docs/discipline-compliance-reports/` 配下の日付付き YAML から読み出せることが機械検証される
  5. 入力スキーマを本機能内で再定義していない（上流出力の read-only 消費）ことが運用文書に明示される
- **テスト要件**：5 入力源の読み込みテスト、来歴 3 要素付与テスト、`source` 値域テスト（4 値 OK ＋ 未知値 fail-closed）、`observation` 30 文字境界テスト（30 文字未満／以上）、時系列読み出しテスト

### T-003：signal_extraction モデル（Signal Extraction Model）

- **対応設計節**：design.md §7.1〜§7.4
- **対応要件**：Requirement 2 受入 3（傾向抽出）、Requirement 3 受入 1（提案種別の候補生成）
- **責務**：input_model（T-002）の出力から「規律と実体の乖離」を抽出し提案候補を生成する。4 種類の乖離判定（`discipline_absence` 規律不在型 ／ `discipline_violation` 規律違反型 ／ `discipline_obsolete` 規律形骸化型 ／ `discipline_conflict` 規律衝突型、design §7.2）を符号化。抽出アルゴリズム（§7.3）の第 1 期は半自動（grep ベースの軽量検査 ＋ 人間／LLM 判断）。閾値（規律違反型は既定 3 件、形骸化型は既定 5 セッション、design §7.2）を設定可能にする。出力は proposal_model（T-004）への提案候補 YAML（`signal_id` ／ `signal_type` ／ `observed_pattern` ／ `related_disciplines` ／ `proposed_proposal_type` ／ `motivating_evidence_seed`、§7.4）
- **前提タスク**：T-002
- **成果物**：
  - `tools/self_improvement/signal_extraction.py`（4 種乖離判定 ＋ grep ベース半自動抽出 ＋ 閾値設定）
  - `tools/self_improvement/schemas/signal.schema.json`（signal 出力スキーマ：`signal_type` enum 4 値、`related_disciplines`（衝突型／形骸化型で必須）等）
- **完了条件**：
  1. 4 種類の乖離判定（不在型 ／ 違反型 ／ 形骸化型 ／ 衝突型）がそれぞれ正しく分類される
  2. `signal_type` の値域が 4 値に enum 制限され、未知の値が fail-closed になることが機械検証される
  3. 違反型の閾値（既定 3 件）と形骸化型の閾値（既定 5 セッション）が設定可能で、閾値未満では signal を生成しないことが機械検証される
  4. 衝突型・形骸化型では `related_disciplines` が必須（空配列は DEVIATION）であることが機械検証される
  5. 出力 signal が proposal_model（T-004）の入力スキーマに適合する
- **テスト要件**：4 種乖離判定テスト、`signal_type` 値域テスト、閾値テスト（3 件・5 セッションの境界）、`related_disciplines` 必須テスト（衝突型／形骸化型）、§7.4 出力形式適合テスト

### T-004：提案モデル（Proposal Model）

- **対応設計節**：design.md §8.1〜§8.9
- **対応要件**：Requirement 3 受入 1〜5、Requirement 4 受入 1〜5
- **責務**：5 種類の提案単位（`new_discipline` ／ `update` ／ `status_change` ／ `archive` ／ `consolidation`、§8.1）を符号化し、signal_extraction（T-003）の出力から提案 YAML を生成。提案構造（§8.4）の必須フィールド（`proposal_id` ／ `proposal_type` ／ `target_discipline_path` ／ `motivating_evidence` ／ `proposed_change` ／ `expected_effect` ／ `status`）と任意フィールド（`source_discipline_paths`（consolidation で必須）／ `statistical_evidence` ／ `depends_on` ／ `superseded_by` ／ `superseded_at` ／ `reopen_reason` ／ `materialized_at` ／ `materialization_commit_hash`）を定義。proposal_id 発番ルール（§8.5、採番権者 self-improvement、接頭辞 `WP-NNN`／`RB-NNN`、通番リセットなし、3 桁開始 999 超で 4 桁拡張）。status 4 値（pending ／ approved ／ rejected ／ superseded、§8.6）。提案種別ごとの追加要件（§8.8：archive は撤廃 README 必須、consolidation は対応表必須、status_change は遵守率証拠等）。**責務境界（topic-100／G-003、§8.9）**：本タスクは status_change の `statistical_evidence` の **存在検証のみ**を担い、その中身（違反検出率等）の生成は検証モデル T-005 の責務。依存順は T-004 → T-005（データの流れ §5.1）でよく依存逆転ではない
- **前提タスク**：T-003
- **成果物**：
  - `tools/self_improvement/proposal_model.py`（5 種別の提案生成 ＋ proposal_id 採番 ＋ status 管理）
  - `learning/workflow/schemas/proposal.schema.json`（提案 YAML スキーマの正本。スキーマは `schemas/` 専用サブフォルダに配置（topic-106／F-007、§11.1）。必須 7 フィールド ＋ 任意フィールド、`proposal_type` enum 5 値、`status` enum 4 値、`motivating_evidence` の 3 要素必須、`target_discipline_path` に pattern 制約（topic-109）。**self-improvement design §8.4 が正本スキーマ**であり、workflow-management T-010 の `approved_update` スキーマは本ファイルに整合させる側（A-019 解消済＝案1 で workflow-management が §8.4 を参照、DVT-S001 解除済、2026-05-29 セッション40））
  - `docs/operations/`（または design 参照先）への proposal_id 発番ルール記述
- **完了条件**：
  1. 5 種類の `proposal_type` すべてで提案 YAML が生成され、`proposal_type` の値域が enum 5 値に制限される（未知値は fail-closed）
  2. 必須 7 フィールドの存在が機械検証され、欠落時は DEVIATION（fail-closed）
  3. `motivating_evidence` の各要素が 3 要素（source ／ location ／ observation）を持つことが機械検証される（T-002 の provenance スキーマと整合）
  4. proposal_id 採番（接頭辞分離 ／ 通番リセットなし ／ 3 桁開始 999 超 4 桁拡張）が **全 4 ディレクトリ（`proposals/`／`approved-updates/`／`rejected-updates/`／`rollback/`）を走査した最大番号＋1**（topic-99／G-002、§8.5）で正しく機能し、git mv で移動済みの提案との採番衝突が起きない
  5. `consolidation` で `source_discipline_paths` が必須、`archive` で撤廃 README 参照が必須、`status_change`（aspirational → enforced）で `statistical_evidence` が必須であることが機械検証される（§8.8）
  6. `proposal.schema.json` が design §8.4 の正本記述と一致する（A-019 は workflow-management 側を本スキーマに整合させる方向、本機能側は §8.4 を維持）
  7. `target_discipline_path` が規律フォルダ `docs/disciplines/` 配下を指すことが機械検証される（topic-109／F-014）：`proposal.schema.json` に正規表現 pattern 制約（例 `^docs/disciplines/discipline_.*\.md$`）を実現手段として定義し、かつ本完了条件にもその検証を明記する（案 1 と案 2 の統合）。MV-1 と併せ提案対象の限定を二重にゲートする
- **テスト要件**：種別別追加要件テストは **全 5 種別**を網羅（consolidation ／ archive ／ status_change ／ **update（変更箇所の diff／対照表）／ new_discipline（ドラフト＋関係明示。ただし「関係明示」を機械検証可能な形＝grep 可能なキーワード等に定義してからテスト化する、topic-108／F-012）**）、`proposal_type` 値域テスト、必須 7 フィールド欠落テスト、`motivating_evidence` 3 要素テスト、proposal_id 採番テスト（接頭辞 ／ 通番 ／ 999 超 4 桁拡張の境界 ／ **全 4 ディレクトリ走査での移動済み提案との衝突回避、topic-99**）、`target_discipline_path` の pattern 制約テスト（topic-109／F-014）

### T-005：検証モデル（Verification Model）

- **対応設計節**：design.md §9.1〜§9.5
- **対応要件**：Requirement 5 受入 1〜4
- **責務**：3 つの検証方法（過去データへの遡及シミュレーション §9.2 ／ パイロット運用 §9.3 ／ 影響範囲の事前分析 §9.4）を実装。遡及シミュレーションは対象データ範囲を提案ごとに明示し違反検出率を計算（第 1 期は手動、規律ドラフトを `.draft` 仮配置 → 過去レビュー記録に仮適用 → 集計）。パイロット運用は `status: aspirational` で一定期間運用し遵守率推移を保持、昇格判定閾値 **90%**（A-009、§9.3、利用者明示承認「90%」2026-05-26）。影響範囲の事前分析は既存規律との衝突（名称重複 ／ 内容重複 ／ 参照循環）を内部リンク `[[name]]` の grep で機械検査。replay／backtest は採用せず、3 手段が機能しない提案は利用者監査の明示判断で承認（§9.5、Req 5 受入 4）。**責務境界（topic-100／G-003、§9.2）**：`statistical_evidence` の中身（遡及シミュレーションの違反検出率等）の生成は本タスクの責務であり、T-004（提案モデル）は存在検証のみを担う。依存順 T-004 → T-005 は正しい（提案の型を先に定義し、その型に流す検証手段を後で作る）
- **前提タスク**：T-004
- **成果物**：
  - `tools/self_improvement/verification_model.py`（3 検証手段。第 1 期は手動補助、自動化はフェーズ 4 第 2 サイクル以降）
  - `tools/self_improvement/impact_analysis.py`（`[[name]]` 参照の grep ベース衝突検査、衝突 3 定義の判定）
- **完了条件**：
  1. 遡及シミュレーションが対象データ範囲（例：過去レビュー 17 件）を提案 YAML の `statistical_evidence` に記録し、違反検出率を算出する
  2. パイロット運用が `status: aspirational` 期間の遵守率推移を時系列で保持し、閾値 90% 以上で `enforced` 昇格判定を返すことが機械検証される（90% 未満は昇格不可）
  3. 影響範囲分析が `[[name]]` 参照を grep で全件検出し、衝突 3 定義（名称重複 ／ 内容重複 ／ 参照循環）を判定する
  4. 3 手段が機能しない提案は「利用者監査での明示判断が必要」とマークされ、自動承認されない（fail-closed）
- **テスト要件**：遡及シミュレーション違反検出率算出テスト、パイロット運用閾値テスト（90% 境界：89%／90%／91%）、影響範囲分析の `[[name]]` 検出テスト、衝突 3 定義判定テスト、検証不能提案の利用者監査マークテスト

### T-006：承認モデル（Approval Model）

- **対応設計節**：design.md §10.1〜§10.5
- **対応要件**：Requirement 6 受入 1〜5
- **責務**：フェーズ境目の利用者監査による承認機構を実装。session 内連続承認を強制しない（§10.1）。規律正式化（aspirational → enforced）に利用者明示承認を必須化（§10.2、規律 [[approval-operation]] の明示的肯定発言判定に従う）。status 4 状態遷移を提案 YAML の `status` フィールドで管理し、ディレクトリ間 git mv（pending → proposals/ ／ approved → approved-updates/ ／ rejected → rejected-updates/ ／ superseded は approved-updates/ で status のみ更新、§10.5）。**`superseded` 遷移は reopen-procedure 5 ステップを必須**（§8.7 ／ §10.5、A-007 対処、規律 [[reopen-procedure-for-settled-topics]] 準拠）：宣言 ／ 理由記述（`reopen_reason`）／ 新結論案 ／ 明示承認 ／ 履歴記録（`superseded_by` ／ `superseded_at` ／ `reopen_reason` の追記）
- **前提タスク**：T-004
- **成果物**：
  - `tools/self_improvement/approval_model.py`（4 状態遷移 ＋ git mv ＋ 明示承認判定 ＋ superseded 5 ステップ強制）
- **完了条件**：
  1. 4 状態（pending ／ approved ／ rejected ／ superseded）の遷移が `status` フィールドとディレクトリ配置で機械検証される
  2. 状態遷移時に提案 ID を維持し、git mv で履歴が保持される
  3. `aspirational → enforced` の正式化に利用者明示承認が必須（承認なしは遷移不可）
  4. `superseded` 遷移時に `superseded_by` ／ `superseded_at` ／ `reopen_reason` の 3 フィールドがすべて存在することが機械検証される（MV-4 連動、§17.1）
  5. `superseded` 遷移の利用者明示承認が後続提案 WP-MMM の承認とは別建てで取得されることが運用文書に明示される
- **テスト要件**：4 状態遷移テスト、git mv 履歴保持テスト、明示承認必須テスト（承認あり／なし）、superseded 3 フィールド存在テスト、reopen-procedure 5 ステップ完了テスト

### T-007：履歴とロールバックモデル（History and Rollback Model）

- **対応設計節**：design.md §11.1〜§11.6
- **対応要件**：Requirement 7 受入 1〜5
- **責務**：4 サブディレクトリ配置（T-001 で配置済み）を前提に、3 つのロールバック方法（archive から復活 ／ ステータス変更を戻す ／ 規律更新を取り消す、§11.2）を実装。ロールバック理由を `learning/workflow/rollback/<日付>-<id>.yaml`（`rollback_id`（RB-NNN 採番）／ `target_proposal_id` ／ `rollback_method` ／ `rollback_reason` ／ `rollback_date` ／ `related_artifacts`）に保存（§11.4）。シンボリックリンク再作成手順（§11.3、F-014 対処、memory 配下 `feedback_*.md` が repo 本体を指すリンク構成のロールバック）。履歴の連結（`target_proposal_id` で提案 → 承認 → ロールバックを追跡、§11.5）。整合性検査（撤廃から復活した規律の front-matter スキーマ検査 ／ `[[name]]` 参照衝突 ／ archive README との矛盾確認、§11.6）
- **前提タスク**：T-001、T-006
- **成果物**：
  - `tools/self_improvement/rollback_model.py`（3 ロールバック方法 ＋ RB 採番 ＋ 履歴連結 ＋ 整合性検査）
  - `learning/workflow/schemas/rollback.schema.json`（ロールバック YAML スキーマ：必須フィールド ＋ `rollback_method` enum 3 値（archive_restoration ／ status_downgrade ／ git_revert））
- **完了条件**：
  1. 3 つのロールバック方法が機械検証される（archive 復活 ／ ステータス格下げ ／ git revert）
  2. ロールバック YAML が必須フィールドを持ち、`rollback_method` の値域 3 値が enum 制限される（未知値 fail-closed）
  3. シンボリックリンク再作成手順（§11.3 の 5 ステップ）が文書化され、archive 復活時に memory 配下の `feedback_*.md` リンクの確認／再作成が機械検証される
  4. `target_proposal_id` による提案 → 承認 → ロールバックの履歴連結が機械的に辿れる
  5. 撤廃から復活した規律の整合性検査（front-matter スキーマ ／ `[[name]]` 参照衝突 ／ archive README 矛盾）が実施され、ロールバック後の遵守検査が `docs/discipline-compliance-reports/` に追記される
- **テスト要件**：3 ロールバック方法テスト、`rollback_method` 値域テスト、シンボリックリンク再作成テスト、履歴連結テスト、整合性検査テスト（front-matter ／ 参照衝突 ／ README 矛盾）

### T-008：効果測定モデル（Effect Measurement Model）

- **対応設計節**：design.md §12.1〜§12.6
- **対応要件**：Requirement 8 受入 1〜5
- **責務**：7 指標（§5.9.5 由来 3 指標：規律遵守率 ／ 昇格件数 ／ 退避件数 ＋ workflow 改善運用 4 指標：提案件数（種別ごと）／ 採用率 ／ ロールバック率 ／ 提案から採用までの平均日数、§12.1）を集計。**採用率の分母は `approved + rejected + superseded`（pending は分母から除外、F-013 対処、§8.6 ／ §12.1）**。第 1 期は手動集計（grep ／ wc ／ jq、§12.5）、出力は `learning/workflow/metrics/<日付>.yaml`（機械可読、analysis が読み物に取り込む、§12.3）。時系列推移を保持（§12.4）。`phase-review-metric-register.md` への workflow 改善カテゴリ登録（§12.2、配置はフェーズ 2 以降の宿題 → DVT-S004）。本セッション 27 新設の `options-precheck-log.md` を規律遵守率の特殊形として吸収（§12.6、A-004 対処）
- **前提タスク**：T-004、T-006、T-007
- **成果物**：
  - `tools/self_improvement/effect_measurement.py`（7 指標の集計 ＋ 採用率分母ロジック ＋ 時系列保持）
  - `learning/workflow/schemas/metrics.schema.json`（7 指標の出力スキーマ）
- **完了条件**：
  1. 7 指標すべてが算出され、`learning/workflow/metrics/<日付>.yaml` に機械可読形式で出力される
  2. 採用率が `(approved + superseded) / (approved + rejected + superseded)`（**分子・分母の両方に superseded を含める**、topic-102／F-003、§12.1）で計算されることが機械検証される（pending 除外は F-013 対処）
  3. ロールバック率が `ロールバック件数 / approved 件数` で計算される
  4. 時系列推移が `learning/workflow/metrics/` 配下の日付付き YAML で保持される
  5. 手動集計手順（§12.5 の 4 ステップ：find｜wc / grep｜sort｜uniq / 採用率算出 / metrics 記録）が文書化され再現可能である
- **テスト要件**：7 指標算出テスト、採用率テスト（分子・分母に superseded を含む式の検証＋改善のたびに採用率が下がらないことの確認、pending 除外、topic-102）、ロールバック率テスト、時系列保持テスト、手動集計手順の再現性テスト

### T-009：機械検査の具体手段（Machine Verification）

- **対応設計節**：design.md §17.1〜§17.4
- **対応要件**：Requirement 1 受入 4（権限分離の機械検査）、Goals §2（自己承認の空洞化防止）
- **責務**：4 つの機械検査ポイント（§17.1）を実装。**MV-1**：`docs/disciplines/discipline_*.md` への本機能からの直接書き込みが発生していないこと（git log の changed files grep、A-007 案 2 の遵守）。**MV-2**：提案 YAML の必須フィールド存在（grep ／ jq）。**MV-3**：`materialization_commit_hash` が git log で実在するコミットを指すこと（`git cat-file -e`）。**MV-4**：`status: superseded` の提案に `superseded_by` ／ `superseded_at` ／ `reopen_reason` がすべて存在すること（grep）。第 1 期（フェーズ 1〜3）は手動 grep ／ git コマンド、フェーズ 4 以降に `tools/self-improvement-check.py` として自動化（§17.4、DVT-S003）。検査失敗時は遮断（fail-closed、§17.3）、結果を `learning/workflow/metrics/<日付>.yaml` に追記。workflow-management の `check-workflow-action.py`（補助層 C）とは責務が異なる（§17.2）
- **前提タスク**：T-004、T-006、T-007
- **成果物**：
  - `tools/self-improvement-check.py`（4 検査ポイントの実装。第 1 期は手動 grep の補助スクリプト、自動化はフェーズ 4 第 1〜2 サイクル）
  - `docs/operations/`（または design 参照先）への MV-1〜MV-4 の検査手順記述（手動 grep ／ git コマンドの具体）
- **完了条件**：
  1. MV-1（直接書き込み検出）が git log の changed files grep で `docs/disciplines/discipline_*.md` の本機能コミットを検出し、検出時に DEVIATION を返す
  2. MV-2（必須フィールド存在）が提案 YAML の必須 7 フィールドを検査し、欠落時に DEVIATION を返す（T-004 連動）
  3. MV-3（commit hash 実在）が `git cat-file -e` で `materialization_commit_hash` の実在を検査する。**ただし値が空（null＝未実体化）の場合は正常としてスキップし、非 null のときだけ検査する**（topic-110／G-004、§17.1）。本フィールドは workflow-management が実体変更完了時に書き込むため、第 1 期（workflow-management 未実装）は常に空であり、空を fail-closed で遮断しない（空＝「承認済みだが未実体化」の正常状態）
  4. MV-4（superseded 3 フィールド）が grep で 3 フィールドの存在を検査する（T-006 連動）
  5. 検査失敗時に fail-closed で遮断し、結果が `learning/workflow/metrics/` に追記される
  6. workflow-management の `check-workflow-action.py` との責務分担（§17.2）が運用文書に明示される
- **テスト要件**：MV-1〜MV-4 の各検査テスト（正常系 ／ 異常系。MV-3 は **null スキップ系と非 null 検査系の両方**を含む、topic-110）、fail-closed 遮断テスト、検査結果の metrics 追記テスト、責務分担の文書検査

### T-010：他機能との接合面（Interfaces with Other Features）

- **対応設計節**：design.md §13.1〜§13.6
- **対応要件**：Boundary Context 隣接期待（foundation ／ runtime ／ evaluation ／ analysis ／ workflow-management ／ conformance-evaluation の 6 機能）
- **責務**：6 機能との接合面を consumer 側（読み手）／ producer 側（書き手）として整備。**foundation**（§13.1）：規律検査スキーマ・レビューモード語彙・状態軸語彙を再定義せず参照。**runtime**（§13.2）：規律遵守検査結果を入力消費。**evaluation**（§13.3）：規律違反データ集計・`roles/role_diff_report.json`（A-011 対処済み）を入力消費。**analysis**（§13.4）：効果測定 7 指標を `learning/workflow/metrics/` に出力。**workflow-management**（§13.5）：承認済み提案を `git mv` で `approved-updates/` に配置（手続き入力）、時系列契約（`approved`＝本機能承認時点 ／ `materialized_at`＝workflow-management 完了時点）、完了通知（workflow-management が `materialized_at` ／ `materialization_commit_hash` 追記）、ロールバック責務（未 materialized は本機能が superseded 遷移）。**conformance-evaluation**（§13.6）：適合性評価結果を入力消費、`target_commit`（conformance-evaluation 所有）と `materialization_commit_hash`（本機能所有）の独立性（A-016 対処済み）
- **前提タスク（硬い依存と緩い依存を区別、topic-107／F-009）**：
  - **硬い依存（着手前提＝完了してから着手）**：T-004、T-006
  - **緩い依存（完了検証前提＝起草は先行可だが、完了条件のクローズ前に成果物が揃っている必要がある）**：T-008（完了条件 3 の metrics 出力検証に必要）、T-002（完了条件 2 の evaluation 入力読み取り検証に必要）
  - ※案 1（T-008 を硬い前提に追加）は T-010 を過剰に直列化し、案 2（依存記述を外す）は完了条件と前提の不整合を温存するため、5 モデルが収束した本「硬軟区別」案を採用。起草者が当初見落とした T-002 も対称的に追加した（起草者バイアス補正、統合レビュー記録 §4.2.2）
- **成果物**：
  - `tools/self_improvement/interfaces.py`（producer/consumer 接合面の入出力アダプタ。上流出力の read-only 消費と analysis 向け出力）
  - `learning/workflow/approved-updates/README.md` への workflow-management 手続き入力経路の記述（§13.5、T-001 で配置した README を本タスクで内容確定）
  - **A-019 注記（✅ 解消済み 2026-05-29 セッション40）**：workflow-management T-010 の `approved_update` スキーマが本機能 design §8.4 正本（`target_discipline_path` ／ `status`、`approved_at` なし）と不一致だった件は、案1 で消化済み。本機能側は §8.4 を正本として維持し、workflow-management 側が独自項目名 `approved_at` ／ `target_discipline` を廃止し §8.4 を唯一の定義元として参照する形で整合（DVT-S001 解除済、コミット f17813c）
- **完了条件**：
  1. foundation 語彙正本を再定義せず参照のみで使用していることが機械検証される（本機能内に語彙の独自定義がないことの grep 検査）
  2. evaluation の `roles/role_diff_report.json`（A-011 対処済み）を入力経路として読めることが確認される（T-002 連動、緩い依存）
  3. analysis 向け出力が `learning/workflow/metrics/<日付>.yaml` に機械可読形式で書かれる（T-008 連動、緩い依存）。なお `approved-updates/` 等にはデータ YAML のみが置かれ、スキーマは `schemas/` 専用サブフォルダに分離されているため、workflow-management が `approved-updates/` を読む際の誤参照は起きない（topic-106／F-007・F-015、§11.1）
  4. workflow-management 接合面の時系列契約（`approved` ／ `materialized_at`）が design §13.5 と整合し、`approved-updates/` への `git mv` 配置経路が機械検証される
  5. conformance-evaluation との `target_commit` ／ `materialization_commit_hash` の独立性（A-016）が design §13.6 と整合する
  6. A-019（approved_update スキーマ不一致）が消化済み（案1、2026-05-29 セッション40）。本機能側は §8.4 正本を維持し、workflow-management 側が §8.4 を唯一の定義元として参照する形で整合（DVT-S001 解除済）
- **テスト要件**：foundation 語彙の不再定義テスト（grep）、evaluation 入力読み取りテスト、analysis 出力テスト、workflow-management 時系列契約整合テスト、`git mv` 配置経路テスト（self-improvement 側 producer テスト、consumer 側 workflow-management は機能横断段で対をなす）、conformance-evaluation commit 独立性テスト

### T-011：テスト戦略全体の整備（Test Strategy）

- **対応設計節**：design.md §18.1〜§18.4、§20 起草完了基準
- **対応要件**：本機能全要件の機械的合否判定、要件追跡表（§14）の双方向整合、DVT 解除確認
- **責務**：design.md §18 で定義された 7 モデル × 3 テストレベル（単体 ／ 結合 ／ 受入）をすべて Python テストとして整備、pytest で一括実行可能にする。重点ポイント（§18.2：YAML スキーマ妥当性 ／ 状態遷移（superseded の reopen 5 ステップ MV-4）／ 効果測定指標算出 ／ ロールバック整合性 ／ workflow-management 接合の `materialized_at` 同期）。テストデータ取得元（§18.4：過去レビュー記録 ／ 遵守検査 ／ 規律ファイル ／ 規律 archive）。要件追跡表（design §14）と各タスク本文の対応要件欄の双方向整合チェック（workflow-management T-011 の方針継承）。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化（workflow-management T-011 の方針継承）
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010
- **成果物**：`tests/self-improvement/` 配下のテストファイル群（`test_input_model.py` ／ `test_signal_extraction.py` ／ `test_proposal_model.py` ／ `test_verification.py` ／ `test_approval.py` ／ `test_rollback.py` ／ `test_effect_measurement.py` ／ `test_machine_verification.py` ／ `test_interfaces.py` ／ `test_traceability.py` の 10 ファイル相当）
- **完了条件**：すべての pytest が pass、7 モデル × 3 テストレベルを網羅、foundation 語彙正本の参照のみ使用が機械検証される、提案 YAML スキーマ（§8.4 正本）の妥当性が機械検証される、status 4 状態遷移（特に superseded の reopen 5 ステップ MV-4）が網羅される、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化、workflow-management との接合面の producer/consumer 境界の契約確認（T-010 の producer 側テストと対をなす consumer 側境界テスト、`approved-updates/` への `git mv` 配置の整合確認。A-019 解消（案1、2026-05-29）により共有フィクスチャの内容を §8.4 正本準拠で確定）

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：workflow 層改善のみ | 全タスク（スコープ前提）＋ T-011（機械検証） |
| Requirement 1 受入 2：規律と実体の双方向同期 | T-002（入力）＋ T-003（signal 抽出） |
| Requirement 1 受入 3：データの流れ | T-001〜T-008（パイプライン全体） |
| Requirement 1 受入 4：権限分離（提案権のみ、A-007 案 2） | T-009（MV-1 機械検査）＋ T-010（workflow-management 接合） |
| Requirement 2 受入 1：5 種類の入力源 | T-002 |
| Requirement 2 受入 2：来歴情報 3 要素 | T-002 |
| Requirement 2 受入 3：時系列性と傾向抽出 | T-002（保持）＋ T-003（抽出） |
| Requirement 2 受入 4：上流出力を直接消費 | T-002 ＋ T-010（接合面で再定義しない） |
| Requirement 3 受入 1：提案種別 5 種類 | T-004 ＋ T-003（候補生成） |
| Requirement 3 受入 2：本機能の規律のみ対象 | T-004 |
| Requirement 3 受入 3：提案種別の組み合わせ | T-004 |
| Requirement 3 受入 4：target_discipline_path 明示 | T-004 |
| Requirement 3 受入 5：種別ごとの追加情報 | T-004（§8.8） |
| Requirement 4 受入 1：YAML 必須フィールド | T-004 |
| Requirement 4 受入 2：motivating_evidence 3 要素 | T-002（provenance）＋ T-004 |
| Requirement 4 受入 3：proposal_type 5 種類 | T-004 |
| Requirement 4 受入 4：status 4 値 | T-004 ＋ T-006（遷移） |
| Requirement 4 受入 5：statistical_evidence 任意 | T-004 ＋ T-005（遡及シミュレーション） |
| Requirement 5 受入 1：3 検証方法 | T-005 |
| Requirement 5 受入 2：遡及シミュレーション対象範囲 | T-005 |
| Requirement 5 受入 3：パイロット運用期間と遵守率 | T-005 |
| Requirement 5 受入 4：replay／backtest 不採用 | T-005（§9.5） |
| Requirement 6 受入 1：フェーズ境目の判断 | T-006 |
| Requirement 6 受入 2：aspirational → enforced 明示承認 | T-006 |
| Requirement 6 受入 3：archive 撤廃 README 必須 | T-004（§8.8）＋ T-006 |
| Requirement 6 受入 4：consolidation 対応表必須 | T-004（§8.8）＋ T-006 |
| Requirement 6 受入 5：4 状態の明示 | T-006 |
| Requirement 7 受入 1：4 サブディレクトリ配置 | T-001 |
| Requirement 7 受入 2：3 ロールバック方法 | T-007 |
| Requirement 7 受入 3：ロールバック理由保存 | T-007 |
| Requirement 7 受入 4：履歴の連結 | T-007 |
| Requirement 7 受入 5：整合性検査 | T-007 |
| Requirement 8 受入 1：7 指標 | T-008 |
| Requirement 8 受入 2：phase-review-metric-register 登録 | T-008 ※ 配置はフェーズ 2 以降（DVT-S004） |
| Requirement 8 受入 3：analysis への出力 | T-008 ＋ T-010（接合面） |
| Requirement 8 受入 4：時系列推移 | T-008 |
| Requirement 8 受入 5：手動集計許容 | T-008 |
| Boundary Context 隣接期待（6 機能の接合面） | T-010 |
| 権限分離の機械検査（A-007 案 2） | T-009（MV-1） |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §18 のテスト戦略を T-011 にまとめて継承する。各テストレベルの対応タスクは次のとおり：

- 単体テスト → T-002 ／ T-003 ／ T-004 ／ T-007 ／ T-008 個別 ＋ T-011 統合
- 結合テスト → T-005 ／ T-006 ／ T-009 ／ T-010 個別 ＋ T-011 統合
- 受入テスト → 過去レビュー記録 17 件＋遵守検査 30 件規模の実データ（§18.4）＋ T-011 統合
- 異常系 fixture → 各タスクで fail-closed テスト ＋ T-011 統合
- 境界条件 → T-002（observation 30 文字）／ T-003（閾値 3 件・5 セッション）／ T-005（昇格閾値 90%）／ T-004（proposal_id 999 超）＋ T-011 統合

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-011 のすべてが起草・実装・テスト・コミット完了
- design.md §20 起草完了基準の各項目が T-011 の統合テストで pass
- foundation が所有する語彙正本（規律検査スキーマ ／ レビューモード語彙 ／ 状態軸語彙）を再定義せず参照のみで使用していることが機械検証される（§13.1）
- 規律ファイル（`docs/disciplines/discipline_*.md`）への本機能からの直接書き込みがないこと（MV-1）が機械検証される（A-007 案 2、Req 1 受入 4）
- 提案 YAML スキーマ（design §8.4 正本）の妥当性、status 4 状態遷移（superseded の reopen-procedure 5 ステップ MV-4 を含む）が機械検証される
- 各タスクの成果物配置が design.md §11.1 ディレクトリ配置と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は self-improvement 機能を「workflow 層改善に特化した全面書き直し」（計画書 §5.16）の方針で実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの所有モデル領域。workflow-management T-001〜T-011 の粒度方針を継承
- **所有モデル単位の分離**：design.md の 7 モデル（入力 §6 ／ signal_extraction §7 ／ 提案 §8 ／ 検証 §9 ／ 承認 §10 ／ 履歴ロールバック §11 ／ 効果測定 §12）に T-002〜T-008 を対応付け、機械検査 §17 を T-009、接合面 §13 を T-010、テスト戦略 §18 を T-011 に対応付け
- **依存順の明示**：T-001（配置）→ T-002（入力）→ T-003（signal 抽出）→ T-004（提案）→ T-005（検証）／ T-006（承認）→ T-007（履歴ロールバック）→ T-008（効果測定）→ T-009（機械検査）→ T-010（接合面）→ T-011（統合テスト）の流れを固定。データの流れ（design §5.1）を依存順の基本とする
- **権限分離の徹底**：規律ファイルの実体変更は本機能では行わず、承認済み提案を workflow-management に渡すのみ（A-007 案 2）。MV-1（T-009）で直接書き込みがないことをゲート
- **旧 8 モジュールの半分継承・半分新規**：継承 4（decision_adoption_model ／ rollback_model ／ pipeline_driver ／ learning_layout）は T-006 ／ T-007 ／ T-001 で活用、新規 4（input_model ／ proposal_model ／ replay_backtest_model 相当 ／ signal_extraction）は T-002 ／ T-004 ／ T-005 ／ T-003 で実装（design §3、計画書 §5.16.11）
- **段階的導入**：第 1 期（フェーズ 1〜3）は手動 grep ／ jq の半自動運用、自動化はフェーズ 4 で段階的に進める（design §17.4 ／ §12.5）。各タスク完了条件は第 1 期スコープで判定
- **fail-closed の徹底**：機械検査（§17）は検査失敗時に遮断、結論不能（YAML パースエラー ／ 必須フィールド欠落 ／ 未知の値 ／ 30 文字未満の observation）は必ず DEVIATION
- **contract consumer 原則**：foundation 語彙正本を再定義せず参照のみ（§13.1）、上流機能の出力を直接消費（Req 2 受入 4）。提案 YAML スキーマ（§8.4）は本機能が正本所有
- **テスト戦略の継承**：design §18 の 7 モデル × 3 テストレベルを T-011 で網羅
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：workflow-management T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定事項（A-019 スキーマ整合 ／ 空置き 3 ディレクトリの所有権 ／ 検査スクリプト自動化 ／ phase-review-metric-register 配置 ／ 入力源 3・4 の自動収集）を DVT で集約管理、T-011 完了条件で未解除項目がないことをゲート化（workflow-management T-011 の方針継承）
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。workflow-management T-011 ／ evaluation T-011 ／ analysis T-011 の DVT 同型運用。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-S001 | T-004 ／ T-010 | workflow-management T-010 の `approved_update` 入力スキーマが本機能 design §8.4 正本（`target_discipline_path` ／ `status`、`approved_at` なし）と不一致（A-019）。本機能側は §8.4 を正本維持、整合は workflow-management 側を §8.4 に合わせる方向 | 機能横断段（tasks review-wave）で A-019 を消化、共有フィクスチャを §8.4 正本準拠で確定 | 解除済（2026-05-29 セッション40、A-019 を案1 で消化＝workflow-management T-010 の独自項目名 `approved_at` ／ `target_discipline` を廃止し §8.4 を唯一の定義元として参照。共有フィクスチャは §8.4 正本準拠で確定。コミット f17813c） |
| DVT-S002 | T-001 | 空置き 3 ディレクトリ（`learning/findings/` ／ `learning/backtests/` ／ `learning/templates/`）の所有権（design §11.1 ／ §5.16.10、A-012 注記）。第 1 期は空置き、他 4 層改善で活用予定 | フェーズ 4 完了後の他 4 層改善の別計画書で所有権を確定 | 未解除（フェーズ 4 完了後まで延期） |
| DVT-S003 | T-009 | `tools/self-improvement-check.py` による MV-1〜MV-4 の自動化（design §17.4）。第 1 期（フェーズ 1〜3）は手動 grep ／ git コマンド | フェーズ 4 第 1 サイクル（MV-1／MV-2 自動化）・第 2 サイクル（MV-3／MV-4 自動化）で着手時に T-009 完了条件と整合を再確認 | 未解除（フェーズ 4 以降まで延期） |
| DVT-S004 | T-008 | `phase-review-metric-register.md` の配置（design §12.2）。7 指標を workflow 改善カテゴリとして登録する先のファイルがフェーズ 2 以降の宿題 | フェーズ 2 以降で `docs/operations/phase-review-metric-register.md` の実体配置時に T-008 完了条件と整合を再確認 | 未解除（フェーズ 2 以降まで延期） |
| DVT-S005 | T-002 | 入力源 3（利用者監査の指摘）と入力源 4（実体運用パターン）の自動収集（design §6.1）。第 1 期は手動抽出 | フェーズ 4 第 3 サイクルで自動化検討時に T-002 完了条件と整合を再確認 | 未解除（フェーズ 4 第 3 サイクルまで延期） |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-011 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。既登録の接合面所見 A-019（workflow-management T-010 の `approved_update` スキーマと本機能 §8.4 正本の不一致）は本機能の tasks 段では機能内対処せず、機能横断段で workflow-management 側を §8.4 正本に整合させる方向で消化する（DVT-S001 と連動）。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。

```

## FILE: .reviewcompass/specs/self-improvement/spec.json

```text
{
  "feature_name": "self-improvement",
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

## FILE: .reviewcompass/specs/self-improvement/reviews/2026-05-22-requirements.md

```text
---
type: requirements_local_review
target: .reviewcompass/specs/self-improvement/requirements.md
date: 2026-05-22
mode: subagent_mediated
session: session-19
author:
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
reviewer:
  identity: claude_code_subagent
  model: claude-haiku-4-5-20251001
  role: final_judgment
  separation_from_author: true
primary:
  provider: claude_code_main_session
  model: claude-opus-4-7
adversarial:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
judgment:
  provider: claude_code_subagent
  model: claude-haiku-4-5-20251001
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 2 }
    count: 3
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 1 }
    count: 2
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 1 }
    count: 3
    judgment_distribution: { must-fix: 2, should-fix: 1, leave-as-is: 2 }
---

# レビュー記録：self-improvement requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

5 観点：要件の網羅性／機能名置換／自己適用前提除去／§5.16 系継承方針の反映／検証可能性。

### 観点 1：要件の網羅性

§5.16.1〜§5.16.8 の 8 構成（役割と性格／入力／提案単位／提案構造／検証／承認／履歴ロールバック／効果測定）を Requirement 1〜8 に対応。§5.16.9 スコープ外、§5.16.10 命名と配置、§5.16.11 旧モジュール関係は Change Intent に統合。所見なし。

### 観点 2：機能名置換の正確性

機能名 `self-improvement` 変更なし（§5.16.10）。本文に `dual-reviewer-*` 残存なし。所見なし。

### 観点 3：自己適用前提の除去完全性

素材の自己適用前提（先行プロジェクト固有の運用文脈）を除去済み。ReviewCompass の workflow 改善として再構成。所見なし。

### 観点 4：計画書 §5.16 系の継承方針の反映

- §5.16.1 役割と性格：Requirement 1 で反映 ✓
- §5.16.2 入力：Requirement 2 で反映 ✓
- §5.16.3 提案単位（5 種類）：Requirement 3 で反映 ✓
- §5.16.4 提案構造：Requirement 4 で反映 ✓
- §5.16.5 検証（3 方法）：Requirement 5 で反映 ✓
- §5.16.6 承認：Requirement 6 で反映 ✓
- §5.16.7 履歴とロールバック：Requirement 7 で反映 ✓
- §5.16.8 効果測定 7 指標：Requirement 8 で反映 ✓
- §5.16.9 スコープ外：Boundary Context Out of scope と Change Intent で反映 ✓
- §5.16.11 旧モジュール関係：Change Intent で反映 ✓
- §5.16.12 段階的導入：Boundary Context Out of scope（フェーズ 4 完了後）と Change Intent で反映 ✓

所見なし。

### 観点 5：要件の検証可能性

- **finding_id**：F-001
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 1
- **description**：Requirement 4 受入 1 で `proposal_id` フィールドを必須化するが、命名規約（例：`WP-001` の `WP` プレフィックス）が未指定
- **rationale**：計画書 §5.16.4 の YAML 例で `proposal_id: WP-001` と書かれているが、`WP` プレフィックス（おそらく workflow proposal の略）の意味と命名規約は本仕様内で未定義。検証可能性のため、最低限の命名規約（例：`WP-` プレフィックス、連番）を明示するか、命名規約は design 段で確定する旨を記述
- **evidence_type**：inference

- **finding_id**：F-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 4 と §Requirement 6 受入 5
- **description**：Requirement 4 受入 4 の 4 状態（`pending`／`approved`／`rejected`／`superseded`）と、Requirement 6 受入 5 で扱われる「4 状態（pending／approved／rejected／superseded）」が同一語彙だが、計画書 §5.16.6 では「提案レビュー／承認／却下／採用」と 4 語彙で記述されている
- **rationale**：「提案レビュー」と `pending`、「承認」と `approved`、「却下」と `rejected`、「採用」と `superseded` の対応が不明確。「承認」が `approved` で「採用」が別の概念か、両者は同義かが本仕様内で曖昧。実装時の解釈差異を招く
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "pending|approved|rejected|superseded|提案レビュー|承認|却下|採用" .reviewcompass/specs/self-improvement/requirements.md`
  - `grep -nA 5 "5.16.6" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：F-003
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Boundary Context Out of scope
- **description**：計画書 §5.16.10 で「`learning/findings/`、`learning/backtests/`、`learning/templates/` は他層改善で使うため第 1 期は空、フェーズ 4 完了後に活用」と明示されているが、本仕様の Out of scope に明示されていない
- **rationale**：第 1 期の workflow 改善は `learning/workflow/` のみを使うが、他ディレクトリの取り扱い（第 1 期は空のまま）は読み手にとって有益な情報。Out of scope または運用文書での明示が望ましい
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "learning/findings\|learning/backtests\|learning/templates" .reviewcompass/specs/self-improvement/requirements.md`

### 該当なし観点

なし。

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 1（F-002）、INFO 2（F-001、F-003）、計 3 件
- evidence_type 別：fact 2、inference 1

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

5 観点：F-001／F-002／F-003 への反論検討 ／ 機能内独立発見 ／ 機能横断独立発見。

### F-001 への反論検討

**主役の主張**：`proposal_id` の命名規約（`WP-` プレフィックスと連番の意味）が本仕様内で未定義。

**反論検討**：

計画書 §5.16.4 の YAML 例に `proposal_id: WP-001` の記述があるが、要件文書の役割は「何を保証するか」の定義であり、「どのように命名するか」の細則は設計文書の責務という原則がある。Requirement 4 受入 1 が求めるのは「`proposal_id` フィールドが存在すること」であり、命名規約の粒度を設計段階で確定させる判断は合理的。計画書 §5.16.4 はあくまで例示であって規範的定義ではなく、`WP-` の由来を要件段で強制しなくても検証可能性を大きく損なわない。

**counter_status**：counter_evidence_raised

**counter_rationale**：命名規約の確定粒度は要件段 vs 設計段の責務分担の問題であり、`proposal_id` フィールドの存在と一意性を要件段で求め、命名則を設計段に委ねることは正当。ただし「設計段で確定する旨を明記すること」という主役の条件付き提案については、明示がなければ計画書 YAML 例を規範と誤解するリスクが残る。重大度 INFO は妥当な評価であり、完全な退却とはしない。

---

### F-002 への反論検討

**主役の主張**：計画書 §5.16.6 の「提案レビュー／承認／却下／採用」と本仕様の `pending／approved／rejected／superseded` の対応が不明確。とくに「採用」と `superseded` の関係。

**反論検討**：

計画書 §5.16.6（行 1918）を実確認：「提案レビュー／承認／却下／採用の 4 状態を明示」。一方、本仕様 Requirement 4 受入 4 の 4 値は `pending／approved／rejected／superseded`。

反論として、`superseded` は計画書の 4 語彙にない独自追加の第 5 状態（後続提案に置き換えられた特殊状態）であり、計画書の「採用」= `approved` という解釈で全体が整合する可能性を検討した。しかしその解釈は本仕様内で一切説明されておらず、`approved`（承認）と `superseded`（後続置き換え）のどちらが計画書「採用」に対応するかが実装者依存のままとなる。`superseded` の英語語義（置き換え・廃止）が「採用」と結びつかないことも読み手の混乱要因として実在する。

**counter_status**：no_counter_evidence_after_challenge

**counter_rationale**：`superseded` が計画書 4 語彙のどれに対応するかについて反論を試みたが、本仕様内では決着がつかない。`approved`（承認）と `superseded`（後続置き換え）が「採用」という自然言語に対してどちらが対応するかが不明確であり、実装時の解釈差異リスクは実質的。主役の WARN 評価を維持。

---

### F-003 への反論検討

**主役の主張**：計画書 §5.16.10 の「`learning/findings/`、`learning/backtests/`、`learning/templates/` は第 1 期は空」が本仕様の Out of scope に記載されていない。

**反論検討**：

「運用文書 SELF_IMPROVEMENT.md に同内容が記載されていれば仕様への記載は不要」という分担論を反論候補として検討した。しかし運用文書（`docs/operations/SELF_IMPROVEMENT.md`）§10「後続セッションでの追加予定」に当該情報の記述はなく、仕様・運用文書のいずれにも欠落している。

**counter_status**：no_counter_evidence_after_challenge

**counter_rationale**：仕様文書・運用文書のどちらにも §5.16.10 の「他 3 ディレクトリは第 1 期空置き」情報が存在しないことを確認。主役の事実認定を覆す根拠なし。仕様の内部矛盾ではなく欠落であり、INFO 相当の評価は妥当。

---

### 独立発見（機能内）

- **finding_id**：A-006（機能内）
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 5
- **description**：`statistical_evidence` フィールドは「統計的証拠が可能な場合」に追加するとあるが、「可能な場合」の判断基準が未定義
- **rationale**：パイロット運用初期など `observed_runs` が 0〜2 件しかない段階でも `statistical_evidence` フィールドを省略するか記入するかの判断が実装者依存になる。Requirement 5 受入 2 で「対象データ範囲を提案ごとに明示する」と定めており、遡及シミュレーションの件数（例：過去 17 件）は提案に記録されるが、`statistical_evidence` との記録場所の重複整理も未定義。
- **evidence_type**：inference

### 独立発見（機能横断）

- **finding_id**：A-007
- **severity**：WARN
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md Requirement 1 受入 4 と Boundary Context 隣接期待
- **description**：Requirement 1 受入 4 で `self-improvement` は「規律ファイルの作成・更新・退避・統廃合の責務を持つ」と定め、Boundary Context 隣接期待では `workflow-management` が「規律の昇格・退避・統廃合を所定手続き（drafting → review → approval）に従って実行」するとある。規律ファイルの変更権と手続き実行権が二機能に分散しており、その調停ルール（`self-improvement` が変更を作成し `workflow-management` が手続きを踏む、あるいは `self-improvement` が直接変更するのか）が本仕様内で明示されていない。
- **rationale**：`workflow-management` の requirements.md（Requirement 2 受入 3、Requirement 6 等）は「変更の手続き実行」を担うとしているが、`self-improvement` が「正本所有者」として直接変更する場合に `workflow-management` の手続きをバイパスするケースが発生するかが不明確。フェーズ 4 実装時に矛盾が顕在化するリスクあり。
- **evidence_type**：fact
- **波及範囲**：self-improvement Req 1 受入 4、workflow-management Req 2 受入 3 および Req 6

---

### 敵対役所見集計

- counter_evidence_raised：1 件（F-001）
- no_counter_evidence_after_challenge：2 件（F-002、F-003）
- 独立発見：機能内 1 件（A-006）、機能横断 1 件（A-007）
- 重大度別（独立発見のみ）：CRITICAL 0、ERROR 0、WARN 1（A-007）、INFO 1（A-006）、計 2 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：leave-as-is
- **rationale**：敵対役の反論が正当。要件段の責務は「フィールド存在と一意性を保証する」であり、命名規約の粒度（`WP-` プレフィックスの由来・形式）は設計段で確定するのが責務分担として妥当。Requirement 4 受入 1 に小注記「命名規約は design 段で確定」を付記する軽微な補強は推奨だが、必須ではない。

- **finding_id**：F-002
- **judgment**：must-fix
- **rationale**：敵対役の反論「`superseded` が計画書の 4 語彙のどれに対応するか不明確」は支持。計画書 §5.16.6 の「提案レビュー／承認／却下／採用」と本仕様の `pending`／`approved`／`rejected`／`superseded` の対応が実装者依存のままになるのは重大。特に `superseded`（置き換え・廃止）と「採用」の対応は自然言語的に不整合。Requirement 4 受入 4 に 4 状態の定義と計画書語彙との対応を明示。

- **finding_id**：F-003
- **judgment**：should-fix
- **rationale**：敵対役が確認した通り、仕様・運用文書のいずれにも欠落。第 1 期 scope は `learning/workflow/` のみで、他 3 ディレクトリ（`learning/findings/`／`learning/backtests/`／`learning/templates/`）の取扱い（フェーズ 4 以降活用、第 1 期は空）は読み手にとって有益。Boundary Context Out of scope または運用文書に追加。

- **finding_id**：A-006
- **judgment**：leave-as-is
- **rationale**：敵対役の指摘「`observed_runs` 0〜2 件段階での判断基準が実装者依存」は妥当だが、INFO 相当の軽微性と、パイロット運用初期での実装判断の必然的な柔軟性を勘案すると、要件段で固定することは適切でない。Requirement 5 受入 2 の「対象データ範囲を提案ごとに明示」で `observed_runs` 件数が記録されれば、後段検証時に基準を事後設定する柔軟性が確保される。

- **finding_id**：A-007
- **judgment**：must-fix（wave-level、learning/workflow/carry-forward-register/reviewcompass-import.yaml に持ち越し済み）
- **rationale**：本所見は既に `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に A-007 として記載済み（敵対役が直接追記）。self-improvement Req 1 受入 4（規律ファイル変更権）と workflow-management Req 2 受入 3／Req 6（手続き実行権）の権限分散が不明確で、機能横断の本質的不整合。個別機能の drafting 段では解決不可、要件 review-wave で両仕様を同時参照して整備する所見として正当。本セッション内で機能内修正は不要。

### 判定役所見集計

- judgment_distribution：must-fix 2 件（F-002 機能内、A-007 機能横断）／should-fix 1 件（F-003 機能内）／leave-as-is 2 件（F-001、A-006）
- 採用所見の重大度別：CRITICAL 0、ERROR 0、WARN 2（F-002、A-007）、INFO 1（F-003）、計 3 件
- 機能内対処（本セッション可能）：2 件（F-002、F-003）
- 機能横断持ち越し：1 件（A-007、既記載済み）
- 不採用：2 件（F-001、A-006）

### 判定の総合所見

主役 3 件のうち 2 件が機能内軽微（INFO×2）と要件内語彙対応不明確（WARN×1）、敵対役独立 2 件のうち 1 件が軽微判断基準未定義（INFO、設計段で対応可）、1 件が機能横断の本質的不整合（WARN）。機能内対処として F-002 の `proposal_state` 語彙対応と F-003 の `learning/` ディレクトリ記載が should-fix〜must-fix で、self-improvement 要件の内部曖昧さを解消する必要。A-007 の規律変更権・手続き実行権の調停ルールは複数機能にまたがる権限設計の根本問題で、要件 review-wave で self-improvement と workflow-management の両仕様を同時参照して整備するのが筋。敵対役の機能横断検知は適切で、learning/workflow/carry-forward-register/reviewcompass-import.yaml への記載は本来的な carry-forward 対象として妥当。

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 対処範囲 |
|---|---|---|---|---|
| F-002 | WARN | must-fix | requirements.md §Req 4 受入 4 | 機能内 |
| F-003 | INFO | should-fix | requirements.md §Boundary Context Out of scope | 機能内 |
| A-007 | WARN | must-fix | self-improvement Req 1 受入 4 ＋ workflow-management Req 2／6 | **機能横断、既持ち越し済み** |

### 残課題と対処方針

**本セッション内で対処（機能内、2 件）**：

- F-002：Requirement 4 受入 4 に 4 状態（`pending`／`approved`／`rejected`／`superseded`）の定義と計画書 §5.16.6 語彙（提案レビュー／承認／却下／採用）との対応を明示
- F-003：Boundary Context Out of scope に「`learning/findings/`／`learning/backtests/`／`learning/templates/` は第 1 期空置き、フェーズ 4 で他層改善時に活用」を追加

**機能横断持ち越し（既記載済み）**：

- A-007：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に既追記済み。要件 review-wave で対処

**leave-as-is**：

- F-001（INFO）：要件段の責務範囲として正当
- A-006（INFO）：パイロット運用の柔軟性を尊重

### サブエージェント方式の効果評価（self-improvement、6 機能目）

- **新パターン**：敵対役が直接 learning/workflow/carry-forward-register/reviewcompass-import.yaml に A-007 を追記（メインセッションを介さず）。ファイル書き込み権限を持つサブエージェントの効率化パターンとして実証
- **§5.16 全面書き直しの検証**：先行プロジェクトの 8 要件から workflow 改善向け 8 要件への再設計を敵対役が機能横断視点（A-007）から検証。再設計の漏れを露出
- **機能横断累積**：A-001／A-003／A-004／A-005／A-007 と 5 件に累積。要件 review-wave での消化対象が拡大

```

## FILE: .reviewcompass/specs/self-improvement/reviews/2026-05-26-design-triad-review.md

```text
---
type: design_triad_review
target: .reviewcompass/specs/self-improvement/design.md
target_commit: dd8eba9
date: 2026-05-26
mode: subagent_mediated
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 449
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 220
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 130
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 12, INFO: 3 }
    count: 19
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 8, INFO: 2 }
    count: 13
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 7, WARN: 20, INFO: 5 }
    count: 32
    judgment_distribution: { must-fix: 13, should-fix: 17, leave-as-is: 2 }
    waterfall_class_distribution: { 機能内対処: 27, 波及: 2, 遡及: 1, 延期: 0, leave-as-is: 2 }
---

# レビュー記録：self-improvement 設計 triad-review

本記録は ReviewCompass の self-improvement 機能の設計文書（design.md、起草時 643 行→ must-fix 反映後 約 950 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。依存マップ順 6/7。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点（要件全件の網羅／アーキテクチャ整合性／データモデル・スキーマ詳細／API 接合面の具体化／アルゴリズム＋性能達成手段／失敗モード処理＋観測性／セキュリティ・プライバシーの具体化／依存選定／テスト戦略／移行戦略）を網羅実施。19 件の所見（ERROR 4／WARN 12／INFO 3）を提示。

主役所見の主要発見：

- F-003（ERROR）：consolidation の複数規律パス YAML フィールド欠如
- F-004（ERROR）：signal_extraction（新規実装）の設計詳細章なし
- F-015（ERROR）：「機械検査可能で担保」の具体検査方法未定義
- F-017（ERROR）：テスト戦略が設計文書全体に欠如
- F-001／F-002／F-005／F-006／F-007／F-008／F-010〜F-014／F-016／F-018／F-019（WARN）：各観点の精緻化対象
- F-009／F-013（INFO）：軽微な改善余地
- F-011（INFO）：grep 確認後に降格、敵対役 counter_evidence で事実誤認確定

主役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（19 件）

敵対役は主役 19 件のすべてに対し 3 値判定（counter_evidence_raised／no_counter_evidence_after_challenge／not_assessed）を付与：

- `counter_evidence_raised`：4 件（F-003／F-005／F-009／F-011）
- `no_counter_evidence_after_challenge`：15 件
- `not_assessed`：0 件

主役 19 件のうち 4 件に反証を提示：

- F-003：consolidation の複数規律対応は「複数提案の組み合わせ運用」で吸収可能と解釈（§7.3）
- F-005：章番号体系の不整合は severity を ERROR → WARN／INFO 減格余地
- F-009：conformance-evaluation の入力ファイル配置先は conformance-evaluation 側の責務
- F-011：`[[name]]` 形式は現用、事実誤認（grep で確認）

### 2.2 独立発見（13 件、A-001〜A-013）

敵対役は強制的差異化（forced-divergence、計画書 §5.15.5）の精神で独立発見 13 件（ERROR 3／WARN 8／INFO 2）を提示。主な独立発見：

- A-001（ERROR、**遡及**）：撤廃 README の配置先が requirements（`docs/archive/disciplines/`）と design（`docs/disciplines/archive/`）で不一致。実体は design 側が正しい
- A-002（ERROR）：proposal_id の発番ルール（採番権者・名前空間・通番リセット規則）未定義
- A-003（ERROR、**波及**）：self-improvement の status `approved` 遷移と workflow-management の手続き完了の時系列衝突
- A-004／A-005／A-006／A-007／A-008／A-009／A-010／A-012（WARN）：options-precheck-log との関係未整理／A-011 持ち越しとの依存／提案間依存フィールド欠落／superseded と reopen-procedure の衝突／計画書 §5.16.12 とのサイクル割当不整合／パイロット運用閾値の根拠不在／入力源 3 の機械可読化方針／空置きディレクトリ所有権者未定義
- A-011／A-013（INFO）：Ruby 拡張子と実装言語未確定／status_change の遵守率証拠と statistical_evidence の接続未定義

敵対役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（32 件）

判定役は主役 19 件＋敵対役独立発見 13 件＝計 32 件のすべてについて、judgment（must-fix／should-fix／leave-as-is）と waterfall_class（機能内対処／波及／遡及／延期／leave-as-is）を判定。

### 3.2 severity 再評定

敵対役の counter_evidence を受けた severity 再評定：

- F-005：WARN 維持（敵対役の WARN 妥当範囲を採用）
- F-009：INFO 維持（敵対役の counter_evidence を採用、leave-as-is）
- F-011：WARN → INFO 降格（敵対役の事実誤認指摘を採用、leave-as-is）
- F-003：ERROR 維持（counter_evidence は救済策の提示で問題自体は残存）

### 3.3 judgment の分布

| judgment | 件数 | 内訳 |
|---|---|---|
| **must-fix** | **13 件** | F-001、F-002、F-003、F-004、F-006、F-008、F-015、F-017、A-001、A-002、A-003、A-007、A-009 |
| **should-fix** | **17 件** | F-005、F-007、F-010、F-012、F-013、F-014、F-016、F-018、F-019、A-004、A-005、A-006、A-008、A-010、A-011、A-012、A-013 |
| **leave-as-is** | **2 件** | F-009、F-011 |
| **合計** | **32 件** | |

### 3.4 waterfall_class の分布

| waterfall_class | 件数 | 内訳 |
|---|---|---|
| **機能内対処** | **27 件** | F-001、F-002、F-003、F-004、F-005、F-006、F-007、F-010、F-012、F-013、F-014、F-015、F-016、F-017、F-018、F-019、A-002、A-004、A-005、A-006、A-007、A-008、A-009、A-010、A-011、A-012、A-013 |
| **波及** | **2 件** | F-008（→ workflow-management 機能設計）、A-003（→ workflow-management 機能設計） |
| **遡及** | **1 件** | A-001（→ requirements.md、軽量 reopen 手続き） |
| **延期** | **0 件** | — |
| **leave-as-is** | **2 件** | F-009、F-011 |
| **合計** | **32 件** | |

### 3.5 severity 別の最終件数（再評定後）

- CRITICAL：0 件
- ERROR：7 件（F-003、F-004、F-015、F-017、A-001、A-002、A-003）
- WARN：20 件
- INFO：5 件（F-009、F-011、F-013、A-011、A-013）

---

## 4. 統合（integration）

### 4.1 must-fix 13 件の対処方針と利用者承認の出典

運営ガイド §3.3 (a-1) 規律（must-fix 議論義務）に従い、must-fix 13 件を 8 グループに分けて 1 件ずつ深掘り議論。各グループで「経緯」「複数候補案」「各案の利点と弱点」「後段で発生し得る問題の深掘り」「推奨案と根拠」を平易な日本語で提示し、利用者明示承認を得てから反映。

| グループ | 所見 | 対処方針 | 利用者承認発言 |
|---|---|---|---|
| G1-1 | F-004 | signal_extraction 専用章を §7（旧 §7 提案モデルは §8 に繰り上げ）として新設 | 「候補 1」 |
| G1-2 | F-015 | 機械検査の具体手段を §17 として新設 | 「候補 1」 |
| G1-3 | F-017 | テスト戦略を §18（Open Issues 直前）として新設 | 「候補 1」 |
| G2 | F-003／F-006 | YAML スキーマに `source_discipline_paths` 配列を追加（consolidation 専用フィールド） | 「候補 1」 |
| G3 | A-001（遡及） | requirements.md 行 125 を実体配置・design.md と整合する `docs/disciplines/archive/<日付>-<id>/README.md` に修正、軽量 reopen 手続き | 「候補 1」 |
| G4 | A-002 | proposal_id：採番権者は self-improvement、接頭辞分離（`WP-NNN` ／ `RB-NNN`）、通番リセットなし、3 桁から 4 桁拡張 | 「候補 1」 |
| G5 | A-003／F-008（波及） | 本機能 design.md §13.5 に時系列契約・完了通知形式を詳細記述、4 状態維持、learning/workflow/carry-forward-register/reviewcompass-import.yaml に A-012 として追記 | 「候補 1」 |
| G6 | A-007 | superseded 遷移時に reopen-procedure 5 ステップを §8.7／§10.5／Decision 6 に明示 | 「候補 1」 |
| G7 | A-009 | パイロット運用閾値を 90% に確定、本セッション 27 利用者明示承認の出典を §9.3／Decision 10 に併記 | 「候補 1、90%」 |
| G8 | F-001／F-002 | §14 要件追跡表を受入基準単位に詳細化（旧 §13 は §14 に繰り上げ） | 「候補 1」 |

### 4.2 反映箇所一覧（design.md、機能内対処 13 件＋遡及 1 件＋波及 2 件）

design.md（643 行 → 約 950 行、+307 行、章番号体系を 17 章 → 20 章に拡張）：

- **新規 §7**：signal_extraction モデル（F-004）
- **§8.4**：YAML スキーマに `source_discipline_paths` 配列、`depends_on`、`superseded_by`／`superseded_at`／`reopen_reason`、`materialized_at`／`materialization_commit_hash` を追加（F-003／F-006／A-002／A-007／A-003／F-008）
- **§8.5**：proposal_id 発番ルール（A-002）
- **§8.7**：superseded 遷移の reopen-procedure 5 ステップ（A-007）
- **§9.3**：パイロット運用閾値 90%、出典併記（A-009）
- **§10.5**：4 状態遷移管理に reopen-procedure 5 ステップを明示（A-007）
- **§13.5**：workflow-management との時系列契約・完了通知形式・ロールバック責務を詳細記述（A-003／F-008）
- **§14**：要件追跡表を受入基準単位に詳細化、全 32 受入基準を §章節と対応（F-001／F-002）
- **新規 §17**：機械検査の具体手段（4 検査ポイント MV-1〜MV-4、F-015）
- **新規 §18**：テスト戦略（5 モデル＋ 7 指標のテスト対象とテストレベル、F-017）
- **§19**：Open Issues に A-001（遡及）／A-003／F-008（波及）／A-011（依存）を明示
- **§20**：起草完了基準を 20 章対応に更新、must-fix 13 件の対処をすべてチェック

requirements.md（A-001 遡及）：

- 行 125 を `docs/archive/disciplines/<日付>/README.md` → `docs/disciplines/archive/<日付>-<id>/README.md` に修正、軽量 reopen 手続きの注記を追記

learning/workflow/carry-forward-register/reviewcompass-import.yaml（A-003／F-008 波及登録）：

- A-012 として追記（self-improvement と workflow-management の時系列契約・完了通知形式、design レビュー波段で消化予定）

### 4.3 should-fix 17 件と leave-as-is 2 件の処理状況

- **should-fix 17 件**：本セッション 27 では原則として反映せず、design.alignment 段以降の改善余地として記録。一部は must-fix 対処に伴って自然に解消（F-005／F-018 は章番号変更で部分対処、F-013 は §8.6 で採用率分母の意図明記、A-011 は §15 Decision 7 で実装言語の将来決定を明記、A-012 は §11.1 で空置きディレクトリ所有権の注記、A-013 は §8.8 で status_change の遵守率証拠を statistical_evidence と接続）
- **leave-as-is 2 件**：F-009（conformance-evaluation 側の責務）／F-011（`[[name]]` 形式は現用、事実誤認）

### 4.4 波及所見の処理

- **A-003／F-008**：本機能 design.md §13.5 で時系列契約・完了通知形式を「提案」として詳細記述。workflow-management 側の合意は design レビュー波段で取る。`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に A-012 として追記済み

### 4.5 関連参照

- 設計文書：[.reviewcompass/specs/self-improvement/design.md](../design.md)
- 要件文書：[.reviewcompass/specs/self-improvement/requirements.md](../requirements.md)
- 計画書 §5.16：[docs/plan/reconstruction-plan-2026-05-21.md](../../../../docs/plan/reconstruction-plan-2026-05-21.md) 行 1957〜2135
- 持ち越し所見：[learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)
- 規律：[docs/disciplines/](../../../../docs/disciplines/)

### 4.6 利用者議論で判明した重要事項（後段への引き継ぎ）

- **章番号変更（リナンバリング）が alignment レビューの対象になる**（利用者指摘 2026-05-26 セッション 27）：本機能 design.md で 17 章 → 20 章への章番号変更を実施。利用者明示承認「案 A」（章番号変更採用、「他機能でも同様の問題が生じていたはずなので後ほど対処」）。design.alignment 段でリナンバリング前後の対応表と他機能の章構造との整合確認が必要、本セッション 27 では本機能のみ対処済み、他機能（foundation／runtime／evaluation／analysis／workflow-management）は別途追跡が必要
- **規律 [options-presentation] の事前検査宣言義務を本 triad-review で実用**（本セッション 27 新設）：複数案提示の場面（G1-1／G1-2／G1-3／G2／G3／G4／G5／G6／G7／G8 の各議論）で (a)(b)(c)(d) を明示宣言、dominated 案を除外して合理案のみを提示する規律を本セッション内で運用、効果測定ログ `docs/discipline-compliance-reports/options-precheck-log.md` への記録は次セッション以降

```

## FILE: .reviewcompass/specs/self-improvement/reviews/2026-05-29-tasks-triad-review.md

```text
---
type: tasks_triad_review
target: .reviewcompass/specs/self-improvement/tasks.md
target_commit: 9794942
target_content_hash: <未計測、セッション 39 起草分（T-001〜T-011）>
date: 2026-05-29
mode: subagent_mediated
session: session-39
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: 約 6
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 3
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 2
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 2, ERROR: 7, WARN: 6, INFO: 1 }
    count: 16
  adversarial:
    by_counter_status: { counter_evidence_raised: 4, no_counter_evidence_after_challenge: 12 }
    independent_findings: { ERROR: 3, WARN: 2, INFO: 1 }
    count: 22
  judgment:
    by_judgment: { must-fix: 5, should-fix: 8, leave-as-is: 8 }
    by_waterfall: { 機能内対処: 6, 遡及: 5, 波及: 0, 延期: 0 }
    論点群数: 15
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation／runtime／evaluation／analysis／workflow-management tasks-triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で言及のみで本体未整備、foundation tasks-triad-review（セッション 30）の仮設定を継承
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）。本記録 §1.2 に主役の事実誤認（A-011 を未解決と誤認）の事後検証結果を明記
  - 3 役の生出力はサブエージェントログ（~/.claude/projects/-Users-Daily-Development-ReviewCompass/<session-id>/subagents/）から復元可能
---

# レビュー記録：self-improvement tasks triad-review

本記録は self-improvement 機能の tasks.md（11 タスク T-001〜T-011、コミット `9794942`）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。16 件の所見（CRITICAL 2／ERROR 7／WARN 6／INFO 1）を提示した。

### 1.1 主役所見一覧（16 件、F-001〜F-016）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | CRITICAL | tasks.md T-010 責務欄、design §19.3 | T-010 が `roles/role_diff_report.json` を「A-011 対処済み」と記述するが design §19.3 は未解決と明示＝偽完了宣言 | fact |
| F-002 | 6：機能横断波及の早期検出 | CRITICAL | T-010 完了条件 2、DVT | A-011 未消化なのに対応する DVT 項目が未登録、T-010 完了条件 2 が機械検証不能のまま実装開始できてしまう | fact |
| F-003 | 4：完了条件の機械判定可能性 | ERROR | design §12.5 手順 3 行571、T-008 完了条件 5 | design §12.5 手順 3 の採用率計算式が `(approved+superseded)/(...)` で §12.1（分子 approved のみ）と矛盾、T-008 完了条件 5 が継承 | fact |
| F-004 | 1：上流仕様の網羅 | ERROR | requirements Req 4 受入 2、design §6.2、T-002 完了条件 2 | requirements は source 値域 3 値だが design §6.2 が observation_pattern 追加で 4 値、差分追跡 DVT がない | fact |
| F-005 | 7：成果物配置と命名の整合 | ERROR | design §11.1 配置ツリー、T-001 完了条件 1・3 | design §11.1 配置ツリーに learning/workflow/metrics/ がない、T-001 完了条件 1（metrics 含む 5 ディレクトリ）と 3（§11.1 と一致）が自己矛盾 | fact |
| F-006 | 7：成果物配置と命名の整合 | ERROR | tools/self_improvement/、tools/self-improvement-check.py | アンダースコアとハイフンで命名規則混在、Python import 問題 | fact |
| F-007 | 7：成果物配置と命名の整合 | ERROR | T-002/T-003 と T-004/T-007/T-008 のスキーマ配置 | スキーマ配置が tools/self_improvement/ と learning/workflow/ に分散、一貫ポリシー不明 | mixed |
| F-008 | 3：依存順の整合性 | ERROR | T-007 前提（T-001、T-006）、design §11.6 | T-007 前提に T-005 がない、§11.6 整合性検査で検証モデル使用の可能性 | mixed |
| F-009 | 3：依存順の整合性 | ERROR | T-010 前提（T-004、T-006） | T-010 前提が T-004/T-006 のみで T-002/T-003/T-008 が欠落、完了条件 3 は T-008 連動と明記 | fact |
| F-010 | 4：完了条件の機械判定可能性 | WARN | T-002 完了条件 5、T-010 完了条件 1 | T-002（運用文書明示＝人手）と T-010（grep 機械検証）が同種原則に異なる検証手段 | fact |
| F-011 | 4：完了条件の機械判定可能性 | WARN | T-001 成果物（tools/README.md 追記） | T-001 成果物に tools/README.md 追記があるが完了条件に検証がない | fact |
| F-012 | 5：テスト要件の妥当性 | WARN | T-004 テスト要件、design §8.8 | §8.8 は update に diff/対照表を要求するが T-004 テスト要件は 3 種別のみ（update/new_discipline 欠落） | fact |
| F-013 | 5：テスト要件の妥当性 | WARN | T-005 テスト要件・完了条件 2 | 90% ちょうどの昇格可否の機械判定基準が曖昧 | mixed |
| F-014 | 2：タスク粒度の妥当性 | WARN | T-004 完了条件、requirements Req 3 受入 2 | target_discipline_path が docs/disciplines/ プレフィックスである機械検証が T-004 完了条件にない | fact |
| F-015 | 6：機能横断波及の早期検出 | WARN | T-004/T-007/T-008 スキーマ配置 | スキーマ 3 つが learning/workflow/ 直下でデータ YAML と混在、workflow-management 接合で誤参照リスク | inference |
| F-016 | 1：上流仕様の網羅 | INFO | tasks.md 要件追跡表末尾 2 行 | 末尾 2 行（Boundary Context／権限分離）が requirements 正式番号体系に対応せず記法相違 | fact |

### 1.2 主役の注目発見と、メインセッションによる事後検証

主役は最も危険な所見として F-001／F-002（A-011 の「偽完了宣言」と DVT 未登録）、F-003（採用率計算式の矛盾）、F-005（metrics 配置の自己矛盾）を挙げた。

**メインセッション（起草者 Opus 4.7）による事後検証**（計画書 §5.23.12.7 準拠）：主役の F-001／F-002 は「design §19.3 で A-011 が未解決と明示されている」という事実主張に依拠しているが、これは **前提誤り**である。横断所見の正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` 166 行で **A-011 は「✅ 対処済み（2026-05-26、セッション 28）」** と明記され、evaluation 設計に `roles/role_diff_report.json` が実際に新設済み。A-016 も同 247 行で対処済み。tasks.md（2026-05-29 起草）の「A-011／A-016 対処済み」は **最新の正本に従った正しい記述**である。陳腐化しているのは design.md §13.3（611 行）と §19.3（923 行）であって tasks ではない（敵対役 G-001 が正しく指摘）。よって主役の CRITICAL 認定 2 件は前提誤りで、判定役により leave-as-is とされた。

これは **起草者・主役バイアスの一例**：主役が design 本文（陳腐化済み）だけを根拠に最重大認定を下し、横断所見の正本を参照しなかった。敵対役が正本を参照して反証を成立させた。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への counter_status 付与（16 件）

counter_evidence_raised（反証あり）は 4 件（F-001／F-002／F-008／F-013）、残り 12 件は no_counter_evidence_after_challenge（同意）。

| 主役 ID | counter_status | 要旨 |
|---|---|---|
| F-001 | counter_evidence_raised | A-011 は実際は対処済み（正本 166 行）。tasks の記述は正しく、偽完了でない。陳腐化は design 側（G-001）。CRITICAL 過大 |
| F-002 | counter_evidence_raised | F-001 と同根。A-011 対処済みのため「未消化なのに DVT 未登録」の前提が崩れる。CRITICAL 過大 |
| F-003 | no_counter_evidence_after_challenge | §12.1 と §12.5 手順 3 で分子が矛盾、所見妥当。ERROR 維持 |
| F-004 | no_counter_evidence_after_challenge | source 3 値→4 値の差分追跡 DVT がない、所見妥当。ただし severity は WARN 寄り（上位互換拡張への下流追従漏れ） |
| F-005 | no_counter_evidence_after_challenge | §11.1 ツリーに metrics/ がなく T-001 完了条件 1 と 3 が両立不能、所見妥当。ERROR 維持 |
| F-006 | no_counter_evidence_after_challenge | 命名混在は事実。ただし機能的に両立可（パッケージ＝アンダースコア／CLI スクリプト＝ハイフン）、WARN 相当に緩和余地 |
| F-007 | no_counter_evidence_after_challenge | スキーマ配置分散の一貫ポリシー記述がない、所見妥当 |
| F-008 | counter_evidence_raised | §11.6 整合性検査は front-matter 検査／`[[name]]` grep／archive README 確認の 3 点で T-005 検証モデルを呼ばない。T-005 を前提に加える根拠は薄い。ERROR 過大 |
| F-009 | no_counter_evidence_after_challenge | T-010 完了条件 3 が T-008 連動と明記なのに前提に T-008 欠落、所見妥当。ERROR 維持 |
| F-010 | no_counter_evidence_after_challenge | 主役の対比はやや不正確だが、同種原則への検証手段の割れは事実。WARN 維持 |
| F-011 | no_counter_evidence_after_challenge | tools/README.md 追記の完了条件検証なし、所見妥当。WARN 維持 |
| F-012 | no_counter_evidence_after_challenge | §8.8 全 5 種別のテスト網羅に対し T-004 は 3 種別のみ、所見妥当。WARN 維持 |
| F-013 | counter_evidence_raised | §9.3 と T-005 完了条件 2 が「90% 以上で昇格」と明記済み。90% は昇格可で一意、曖昧性なし。WARN 不要 |
| F-014 | no_counter_evidence_after_challenge | target_discipline_path プレフィックスの機械検証が T-004 完了条件にない、所見妥当。WARN 維持 |
| F-015 | no_counter_evidence_after_challenge | スキーマとデータの混在で誤参照懸念に合理性。WARN が妥当 |
| F-016 | no_counter_evidence_after_challenge | 末尾 2 行の記法相違は事実。INFO 妥当 |

### 2.2 敵対役の独立所見（6 件、G-001〜G-006）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| G-001 | 設計の内部整合 | ERROR | design §13.3 行611、§19.3 行923、tasks T-010 | design がA-011 対処後も未更新で陳腐化（「追加予定」「消化予定」「前提」）。tasks は正しく「対処済み」と書くため真逆。正すべきは design 本文 | cross_document_inconsistency |
| G-002 | 検証可能性 | ERROR | design §8.5 行302、T-004 完了条件 4 | proposal_id 採番「proposals/ の最大番号＋1」だが approved/rejected は git mv で別ディレクトリへ移動（§10.5）。proposals/ には pending しか残らず採番衝突。全 4 ディレクトリ走査すべき | logical_defect |
| G-003 | 設計と要件の対応 | ERROR | T-004 完了条件 5、T-005 完了条件 1、requirements Req 4 受入 5 | T-004（statistical_evidence 必須化）前提に T-005（生成）がない。status_change 必須化と生成責務の依存逆転。T-004 単独では埋められない | dependency_inversion |
| G-004 | 段階的導入の妥当性 | WARN | T-009 MV-3、design §17.1、§13.5 | MV-3（materialization_commit_hash 実在検査）の書き込み主体は workflow-management。第 1 期は常に null で vacuously pass。null 時の扱い未定義 | spec_gap |
| G-005 | 設計の内部整合 | WARN | T-001 成果物、§11.1 | findings/backtests/templates の README パスが個別列挙されず（.gitkeep のみ）、完了条件 2 と粒度不一致 | inconsistency |
| G-006 | 実装可能性 | INFO | T-009、F-006 補足 | F-006 命名混在は意図的に説明可能（パッケージ vs CLI スクリプト）。ERROR を WARN へ緩和余地 | severity_mitigation |

### 2.3 敵対役の総評

1. 主役の CRITICAL 2 件（F-001／F-002）は前提事実が誤り。真の問題は design 本文の陳腐化（G-001）。論点の主体を tasks から design へ移す必要がある。
2. proposal_id 採番ロジックの論理欠陥（G-002）。主役が誰も突いていない実装レベルの確定バグ。
3. statistical_evidence の供給と必須検証の依存逆転（G-003）＋ metrics ディレクトリ自己矛盾（F-005）。tasks 着手前に design §11.1／§8.5／§8.9 の修正が必要。

---

## 3. 判定役判定（judgment、Opus 4.7）

判定役は主役 16 件＋敵対役独立 6 件＝22 件を 15 論点群に集約し、最終判定を下した。

### 3.1 最終判定表

| 論点ID群 | 判定 | 対処文書 | waterfall分類 | 判定理由（要約） |
|---|---|---|---|---|
| F-001 / F-002 / G-001 | F-001・F-002 は leave-as-is、**G-001 は must-fix** | design.md（§13.3 行611・§19.3 行923） | 遡及 | A-011/A-016 は対処済み（正本 166/247 行）。tasks の記述は正しく偽完了でない。陳腐化は design 本文（G-001）。tasks 完了基準が要求する design §20 整合検査が破綻するため design の遡及修正が必要 |
| F-003 | **must-fix** | design.md（§12.5 手順 3 行571） | 遡及 | §12.1・§8.6・T-008 完了条件 2 は分子 approved のみ。§12.5 手順 3 だけ分子 approved+superseded。矛盾式が手動集計運用に流入。design §12.5 を修正必須 |
| F-004 | should-fix | tasks.md（DVT 追記） | 機能内対処 | source 3 値→4 値の差分が DVT 未登録。下流が上流拡張に追従する正方向で内部整合は取れているため延期・追跡で足る |
| F-005 | **must-fix** | design.md（§11.1 配置ツリー 行453-472） | 遡及 | §11.1 ツリーに metrics/ がないが §12.3 等が使用。T-001 完了条件 1（metrics 必須）と 3（§11.1 と一致）が衝突し配置検査が必ず失敗。§11.1 に metrics/ 追記必要 |
| F-006 / G-006 | should-fix | tasks.md（命名規約明文化） | 機能内対処 | パッケージ＝アンダースコア／CLI スクリプト＝ハイフンとして両立可。ERROR は過大、文書化不足が実体 |
| F-007 / F-015 | should-fix | tasks.md（配置ポリシー明文化） | 機能内対処 | ツール内部スキーマ＝tools 配下／データ正本スキーマ＝learning 配下の分離方針を一文で確定すべき |
| F-008 | leave-as-is | — | — | 敵対役反証成立。§11.6 整合性検査は T-005 検証モデルを呼ばない。ERROR 過大 |
| F-009 | should-fix | tasks.md（T-010 前提タスク） | 機能内対処 | T-010 完了条件 3 が T-008 連動なのに前提に欠落。ただし T-010 は T-008 完了を厳密に待たず起草可能、依存順の明示漏れに留まる |
| F-010 | leave-as-is | — | — | T-002 と T-010 は検証対象が異なる（運用宣言 vs 語彙 grep）。同種原則への異手段でなく対象差 |
| F-011 | leave-as-is | — | — | tools/README.md は既存ファイルへの追記で本機能の正本成果物でない。完了条件外でも実害なし |
| F-012 | should-fix | tasks.md（T-004 テスト要件） | 機能内対処 | §8.8 全 5 種別のテスト網羅が望ましい。update/new_discipline のテスト追加。実装段で補える |
| F-013 | leave-as-is | — | — | 敵対役反証成立。§9.3・T-005 完了条件 2 とも「90% 以上で昇格」と明記、90% は昇格可で一意。曖昧性なし |
| F-014 | should-fix | tasks.md（T-004 完了条件） | 機能内対処 | target_discipline_path プレフィックスの機械検証を完了条件に一項目追加 |
| F-016 | leave-as-is | — | — | 末尾 2 行は横断的観点の追記で意図的。T-011 の双方向整合チェックが正式番号体系で検査するため実害なし |
| G-002 | **must-fix** | design.md（§8.5 行302）＋ tasks.md（T-004 完了条件 4） | 遡及 | proposals/ には pending しか残らず採番衝突（ID 重複）。「通番リセットなし」の設計意図とも矛盾。全 4 ディレクトリ走査が必要。ID 重複は履歴連結（T-007）を破壊するため致命的 |
| G-003 | **must-fix** | tasks.md（T-004／T-005 依存順）＋ design.md（責務記述） | 遡及 | T-004 が必須化する statistical_evidence の生成責務は T-005。依存順 T-004→T-005 では status_change 提案が T-004 段階で完成不能。生成責務の前後関係を整理 |
| G-004 | should-fix | tasks.md（T-009 MV-3）＋ design.md（§17.1） | 機能内対処 | MV-3 は第 1 期は常に null で vacuously pass。null 時の扱い（スキップか fail-closed か）を一文で確定 |
| G-005 | leave-as-is | — | — | 責務本文と完了条件 2・テスト要件でカバー済み。粒度不一致は表記レベルで実害なし |

### 3.2 by_judgment 集計

- **must-fix：5 件**（F-003 / F-005 / G-001 / G-002 / G-003）
- **should-fix：8 件**（F-004 / F-006＝G-006 / F-007＝F-015 / F-009 / F-012 / F-014 / G-004）
- **leave-as-is：8 件**（F-001 / F-002 / F-008 / F-010 / F-011 / F-013 / F-016 / G-005）

### 3.3 判定役の総括（実装段前に必ず対処すべき must-fix）

最優先（実装が確実に破綻する論理欠陥）：
1. **G-002（採番衝突）**：design §8.5 と T-004 完了条件 4 を「全 4 ディレクトリ走査の最大番号＋1」に修正。
2. **G-003（依存逆転）**：T-004 が必須化する statistical_evidence の生成責務（T-005）との前後関係を明示。

design 本文の整合修正（tasks は正しいが上流が矛盾）：
3. **F-005（metrics 配置）**：design §11.1 ツリーに learning/workflow/metrics/ を追記。
4. **F-003（採用率計算式）**：design §12.5 手順 3 の分子を approved のみに修正。
5. **G-001（design 陳腐化）**：design §13.3・§19.3 を A-011/A-016 対処済みに合わせて更新。

---

## 4. 統合節（メインセッションによる集約）

### 4.1 must-fix 5 件の対処方針案（利用者議論用、各案に後段影響）

本節は規律 [must-fix-discussion-obligation] に従い、各 must-fix に対処方針の選択肢と後段影響を整理する。**確定は利用者議論を経てから**であり、本節は議論の素材である。

#### must-fix-1：G-002 採番衝突

- **事実**：design §8.5 行302「採番手順：proposals/ 配下の最大番号＋1」。§10.5 行441-444 で approved→approved-updates/、rejected→rejected-updates/、superseded→approved-updates/ へ git mv。proposals/ には pending のみ残る。
- **案 1（推奨）**：採番の走査対象を全 4 ディレクトリ（proposals/approved-updates/rejected-updates/rollback/）に拡張。design §8.5 と tasks T-004 完了条件 4 の両方を修正。
  - 後段影響：T-004 実装で全ディレクトリ走査が必要、T-009 MV 検査の対象範囲も整合。履歴連結（T-007）の ID 一意性が保たれる。
- **案 2**：採番台帳ファイル（`learning/workflow/.id-counter`）を単一の真実源として導入し、ディレクトリ走査をやめる。
  - 後段影響：新規ファイルの追加と並行更新の競合管理が必要。第 1 期手動運用には過剰。
- 私の評価：案 1 が最小修正で設計意図（通番リセットなし）に忠実。案 2 は将来の自動化で再検討余地。

#### must-fix-2：G-003 依存逆転

- **事実**：§8 行357 status_change は statistical_evidence 必須。§9.2 行381 で T-005 が statistical_evidence を生成・記録。tasks 依存順は T-004→T-005。
- **論点の整理**：T-004 は提案モデル（スキーマ＋検証ロジック）を**作る**タスク、T-005 は検証手段を**作る**タスク。コードを組む順序としては T-004→T-005 で破綻しない（T-004 は「status_change 提案に statistical_evidence が無ければ DEVIATION」と検証するだけで、値の中身は生成しない）。一方、実行時に実際の status_change 提案を完成させるには T-005 の生成物が要る。
- **案 1**：依存順は現状維持（T-004→T-005）とし、tasks に「T-004 は statistical_evidence の存在検証のみ、生成は T-005 の責務」と責務境界を一文明記。design 側も §8.9／§9.2 の責務分担を明確化。
  - 後段影響：最小修正。実装は現行依存順で進む。
- **案 2**：T-004 の前提タスクに T-005 を追加（T-005→T-004 に逆転）。
  - 後段影響：データの流れ（§5.1：提案→検証）と逆行し、依存順の基本原則を崩す。提案モデルが検証モデルに依存する不自然な構造。
- 私の評価：案 1 が妥当。判定役は「依存逆転」と強く表現したが、ビルド順序とランタイムのデータ流れを分離すれば現行順序で問題ない。責務境界の明文化で解消する論点。**判定役が must-fix にやや過大評価した可能性があり、議論で確認したい**。

#### must-fix-3：F-005 metrics 配置欠落

- **事実**：design §11.1 ツリー行453-472 に metrics/ がない。§12.3 行555・§12.4・§17.3 が learning/workflow/metrics/ を使用。T-001 完了条件 1（5 ディレクトリに metrics 含む）と完了条件 3（§11.1 と一致）が衝突。
- **案 1（推奨）**：design §11.1 ツリーに `metrics/` を追記（§12.3 の使用と整合）。
  - 後段影響：T-001 完了条件の衝突解消。最小修正で章間整合が回復。
- 私の評価：単純な記載漏れの遡及修正。異論の余地が小さい。

#### must-fix-4：F-003 採用率計算式の矛盾

- **事実**：§12.1 行540 と §8.6 行324 は採用率＝approved／(approved+rejected+superseded)（分子 approved）。§12.5 手順 3 行571 だけ `(approved+superseded)/(...)`（分子に superseded を含む）。
- **論点**：superseded（後続提案で上書きされた過去の承認）を「採用」に数えるか。§8.6 の定義意図（superseded は無効化された過去の承認）からは分子に含めない（§12.1 が正）のが自然。
- **案 1（推奨）**：§12.5 手順 3 の分子を approved のみに修正し、§12.1 に統一。
  - 後段影響：T-008 完了条件 5（§12.5 の 4 ステップ再現）が正しい式を継承。
- **案 2**：逆に §12.1 を §12.5 に合わせ分子を approved+superseded にする。
  - 後段影響：superseded を採用に数える意味づけが必要。F-013 対処（pending 除外）の議論時の設計意図と整合しない。dominated。
- 私の評価：案 1。§12.1 が複数箇所で一貫しており、§12.5 のみの孤立した誤記と判断。

#### must-fix-5：G-001 design 本文の陳腐化

- **事実**：design §13.3 行611「A-011 対処で evaluation 設計に追加予定」「design.alignment は A-011 消化に依存」、§19.3 行923「A-011（既存、design レビュー波段で消化予定）」「A-011 消化が design.alignment の前提」。正本では A-011/A-016 ともセッション 28 で対処済み。
- **案 1（推奨）**：design §13.3・§19.3 を「A-011 対処済み（セッション 28、evaluation に role_diff_report.json 新設済み）」に更新。§19.3 の「design.alignment の前提」記述も「対処済みのため前提充足」へ。
  - 後段影響：tasks の「対処済み」記述と design 本文が整合。design.alignment 段（将来）での前提充足確認がスムーズ。
- 私の評価：遡及修正だが正本に合わせるだけで異論の余地が小さい。なお design は design.approval まで完了済みのため、この修正は**確定済み design への遡及修正**であり、再オープン手続き（軽量、§5.23.13）の要否を利用者と確認する必要がある。

### 4.2 利用者議論履歴

#### 4.2.1 7 モデル比較実験の概要（セッション 39、2026-05-29）

12 論点群を topic-99〜110 に展開し、7 モデル（Opus 4.7 起草者／Sonnet 4.6 CLI／Sonnet 4.6 API／GPT-5.5／GPT-5.4／Gemini-3.5-flash／Gemini-3.1-pro）で評価。プロンプトは推奨案を含めない方針（起草者バイアス防止）。集計スクリプト `_aggregate_self_improvement_eval_temp.py`。

結果：**完全一致 4 件（topic-99／100／105／110、いずれも案 1）、割れ 8 件**。

| topic | 所見 | 種別 | 分布 | 備考 |
|---|---|---|---|---|
| 99 | G-002 | must | 全 7 案 1 | 完全一致 |
| 100 | G-003 | must | 全 7 案 1 | 完全一致。起草者の「must-fix 過大評価の疑い」に対し全モデルが案 1（軽い責務境界明記）を選択、案 2（依存逆転）は誰も採らず |
| 101 | F-005 | must | 案 1×5／別案×2 | 別案＝案 1＋再オープン手続き＋全体点検（実質案 1） |
| 102 | F-003 | must | 案 1×6／別案×1 | **枠組み伝染バイアス検出**（§4.2.3） |
| 103 | G-001 | must | 案 1×4／深掘×1／質問×1／別案×1 | 非決定・別案いずれも案 1＋再オープン手続き＋全体点検（実質案 1） |
| 104 | F-004 | should | 案 1×6／案 2×1 | 案 2＝要件を 4 値に更新（遡及） |
| 105 | F-006 | should | 全 7 案 1 | 完全一致 |
| 106 | F-007 | should | 案 1×4／案 2×1／別案×2 | 別案＝schemas/ 専用サブ階層（案 1 の精緻化） |
| 107 | F-009 | should | 案 1×2／別案×5 | **起草者バイアス検出**（§4.2.2） |
| 108 | F-012 | should | 案 1×6／別案×1 | 別案＝案 1＋new_discipline テストの検証可能形定義 |
| 109 | F-014 | should | 案 1×3／案 2×2／別案×2 | 別案＝案 1 と案 2 の統合（目的と手段） |
| 110 | G-004 | should | 全 7 案 1 | 完全一致 |

#### 4.2.2 topic-107（F-009）— 起草者バイアスの検出と補正

起草者（Opus、メインセッション）は案 1（T-010 の前提に T-008 を追加）を選んだが、**5 モデルが独立に同じ別案に収束**：前提を「硬い依存（着手前提）」と「緩い依存（完了検証前提）」に区別し、T-008 だけでなく**起草者が見落とした T-002 も緩い依存として追加**する。案 1（過剰直列化）と案 2（不整合の隠蔽）の両方の弱点を回避。利用者は起草者案 1 を撤回し**別案を採用**（人評価 `topic-107-human.yaml`、2026-05-29「はい」）。

#### 4.2.3 topic-102（F-003）— 枠組み伝染バイアスの検出と補正

採用率の計算式。6 モデル（起草者含む）が案 1（§12.5 を分子 approved のみに統一）を選んだが、これは**起草者がプロンプト深掘り欄に「§12.5 だけが孤立した誤記」「§12.1 が設計意図に合う」と自説の結論を書き込んだため、6 モデルが案 1 に誘導された**結果である。Gemini-3.5-flash だけが枠組みを破り「分子 approved のみ・分母に superseded を含めると、改善（上書き）のたびに却下なしで採用率が下がる不条理（悪いインセンティブ）」を提起。利用者は「他はどうなのか」と問い返したうえで少数派を採用し、**案 2（superseded を分子・分母の両方に含める：採用率＝(approved＋superseded)÷(approved＋rejected＋superseded)）に確定**（人評価 `topic-102-human.yaml`、2026-05-29）。superseded は却下されたのではなく一度は採用されたものであり、self-improvement の目的（規律の継続的改善）を罰する指標は目的と矛盾する、という判断。**多数決なら不条理な式が通っていた**。

#### 4.2.4 方法論上の発見：枠組み伝染バイアスと再発防止ガイドライン

topic-102 と topic-107 の対比（同一実験内の自然対照）から、**起草者が問題文に書いた枠組み・結論がレビューするモデル群に伝染する**現象を実証的に検出した。結論を押し付けた topic（102）は 6 モデルが同調し、押し付けなかった topic（107）は 5 モデルが自由に発想してより良い別案を出した。検出機構は 4 種（深掘り欄への自説結論注入／評価語／事実の片面提示／二択アンカリング）。

利用者指示（2026-05-29「重要な議論なので、記録に残し、今後のプロンプト作成時のガイドラインにすること」）により、実験ノート `docs/experiments/n-model-comparison.md` §3.4.2 に「セッション 39 の追加教訓：枠組み伝染バイアス」として再発防止ガイドライン（深掘り欄は事実としての後段影響だけ／両面に切れる事実の併記／前提を疑う別案の明示的歓迎／起草後の自己検査 7〜9 項目）を追記した。

#### 4.2.5 全 12 topic の利用者確定結果

利用者議論（2026-05-29 セッション 39）で 12 件すべてを確定。人本人判定を `tools/experiments/results/topic-NN-human.yaml` に保存（12 件）。

| topic | 所見 | 確定 | 主な反映先 |
|---|---|---|---|
| 99 | G-002 採番衝突 | 案 1（全 4 ディレクトリ走査） | design §8.5 ＋ tasks T-004 |
| 100 | G-003 依存逆転 | 案 1（責務境界明記、実装順維持） | design §8.9 ＋ tasks T-004／T-005 |
| 101 | F-005 metrics 配置 | 案 1（§11.1 に追記）＋再オープン＋全体点検 | design §11.1 |
| 102 | F-003 採用率 | **案 2**（superseded を分子分母両方に） | design §8.6・§12.1・§12.5 ＋ tasks T-008 |
| 103 | G-001 陳腐化 | 案 1（§13.3・§19.3 更新）＋再オープン＋全体点検 | design §13.3・§19.3 |
| 104 | F-004 source 差分 | **案 2**（要件を 4 値に更新） | requirements Req 4 受入 2 |
| 105 | F-006 命名 | 案 1（命名規約明記） | tasks T-001 |
| 106 | F-007 スキーマ配置 | 案 1＋schemas/ 専用サブフォルダ | design §11.1 ＋ tasks T-001／T-004 |
| 107 | F-009 前提 | **別案**（hard/soft 区別＋T-002 追加） | tasks T-010 |
| 108 | F-012 テスト | 案 1＋new_discipline は検証可能形を先に定義 | tasks T-004 |
| 109 | F-014 path 検証 | **別案**（案 1 と案 2 を統合） | design §8.4 ＋ tasks T-004 |
| 110 | G-004 MV-3 | 案 1（空値スキップ） | design §17.1 ＋ tasks T-009 |

起草者・多数決と利用者判断が分かれた 3 件：topic-107（起草者バイアス、§4.2.2）／topic-102（枠組み伝染バイアス、§4.2.3）／topic-104（少数派採用、6 モデル案 1 に対し利用者は案 2）。

### 4.3 反映箇所

確定 12 件を上流順（要件 → 設計 → tasks）に反映。承認済みの requirements／design は A-2 再オープン手続き（`docs/reviews/reopen-classification-2026-05-29.md`、進行中状態 `stages/in-progress/reopen-procedure-2026-05-29.yaml`）で修正。

**requirements.md**
- Req 4 受入 2：source 値域を 3 値 → 4 値（`observation_pattern` 追加、topic-104）

**design.md**
- §8.4：target_discipline_path に pattern 制約注記（topic-109）
- §8.5：採番手順を全 4 ディレクトリ走査に（topic-99）
- §8.9：status_change の statistical_evidence 責務境界（生成は §9.2／T-005）を明記（topic-100）
- §8.6・§12.1・§12.5：採用率を (approved＋superseded)／(approved＋rejected＋superseded) に統一（topic-102、案 2）
- §11.1：配置図に metrics/ と schemas/ を追記、スキーマ配置方針（正本性で分離＋schemas/ サブフォルダ）を記述（topic-101・topic-106）
- §13.3（619 行）・§19.3（931 行）：A-011／A-016 を「対処済み」に更新（topic-103、全体点検で他に陳腐化なしを確認）
- §17.1：MV-3 に「materialization_commit_hash が空なら正常スキップ」を明記（topic-110）

**tasks.md**
- T-001：schemas/ サブフォルダの配置・命名規約（topic-105・topic-106）、完了条件・テスト要件更新
- T-004：採番全 4 ディレクトリ（topic-99）、責務境界（topic-100）、スキーマパス schemas/（topic-106）、全 5 種別テスト（topic-108）、target_discipline_path pattern 完了条件・テスト（topic-109）
- T-005：statistical_evidence 生成責務の明記（topic-100）
- T-008：採用率式を案 2 に（topic-102）
- T-009：MV-3 空値スキップ（topic-110）
- T-010：前提タスクを硬い依存／緩い依存に区別＋T-002 追加（topic-107）、schemas/ による誤参照排除注記（topic-106）
- 全スキーマパスを `schemas/` サブフォルダに統一（topic-106 整合）

**全体点検（topic-101／103 条件）**：requirements・design を点検し、§11.1・§13.3・§19.3 以外に同種の配置漏れ・陳腐化記述がないことを確認（design §19.3 は「未消化なし」に更新済み）。

### 4.3 反映箇所

（確定した対処を tasks.md／design.md のどこに反映したかをここに記録する。）

*（未記入：利用者議論で確定後に追記）*

### 4.4 機能横断段への持ち越し

- A-019（workflow-management T-010 の approved_update スキーマと self-improvement §8.4 正本の不一致）：本機能の tasks 段では機能内対処せず、DVT-S001 で追跡。機能横断段（tasks review-wave）で workflow-management 側を §8.4 に整合させる方向で消化。
- 本 triad-review で新たな機能横断波及所見は検出されなかった（must-fix 5 件はすべて self-improvement 内の tasks.md／design.md で完結する遡及・機能内対処）。

```

## FILE: docs/operations/SELF_IMPROVEMENT.md

```text
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
- 機能横断波及所見：[learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)、[evaluation](EVALUATION.md)、[analysis](ANALYSIS.md)、[workflow-management](WORKFLOW_MANAGEMENT.md)

```

## FILE: docs/operations/SELF_IMPROVEMENT_MACHINE_VERIFICATION.md

```text
# Self-Improvement Machine Verification

`tools/self-improvement-check.py` は self-improvement が所有する workflow 改善提案の安全検査を担当する。

## Scope

- `MV-1`: self-improvement による `docs/disciplines/discipline_*.md` 直接書き込みを検出する。
- `MV-2`: 提案 YAML の必須 7 フィールドを検査する。
- `MV-3`: `materialization_commit_hash` が null の場合は未実体化として正常にスキップし、非 null の場合だけ `git cat-file -e` で実在を検査する。
- `MV-4`: `status: superseded` の提案に `superseded_by`、`superseded_at`、`reopen_reason` があることを検査する。

## Responsibility Boundary

`tools/check-workflow-action.py` は全体 workflow の段階遷移、commit / push 事前検査、post-write verification を担当する。

`tools/self-improvement-check.py` は self-improvement の提案 YAML と workflow 改善履歴に閉じた検査を担当する。規律ファイル本体の変更を実行せず、直接書き込みを `MV-1` で fail-closed にする。

## Manual Commands

- `python3 tools/self-improvement-check.py mv1 --actor-feature self-improvement --changed-file docs/disciplines/discipline_x.md --json`
- `python3 tools/self-improvement-check.py all --actor-feature self-improvement --proposal-path learning/workflow/approved-updates/WP-001.yaml --metric-date 2026-06-04 --json`

検査結果は `learning/workflow/metrics/<日付>-machine-verification.yaml` に記録する。

```

## FILE: docs/operations/SESSION_WORKFLOW_GUIDE.md

```text
# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-04（review-run 後の proxy_model 判断代行手順を正本化、セッション記録の作成手順を正本化）／2026-06-03（Codex adapter migration：Claude Code 固定の作業環境記述を adapter 方針へ整理）／2026-05-30（セッション 41：§4.2 モデル割り当てを計画書 §5.9.1・実態に整合。「主役＝メインセッション」の誤記を訂正し、メイン LLM は 3 役のいずれにもならないことを明記、モデル能力配分規律へ更新）／2026-05-23（セッション 21：用語「遡及／波及」の二軸的定義への訂正、段集合の責務分離による 5 段化を反映）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。セッション 19 で発覚した「ワークフロー把握不足のまま着手」「用語混同（遡及／波及）」等の失態と検討不足を踏まえ、次セッション以降が同じ失敗を繰り返さないよう手順と判断指針を明示する。

本文書は運用文書（`docs/operations/` 配下）であり、計画書（`docs/plan/`）の方針を**実行可能な手順**に落とし込んだもの。計画書の改定なしに本文書だけを更新できる位置付け。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。確認なしの着手は失態の原因となる（セッション 19 §0 の経験）。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **計画書 §5.4〜§5.7**（ワークフロー手続き）
   - §5.4：軽量化方針（思想は継承、実装は 1／10）
   - §5.5：9 ファイル体制と段階層構造（drafting → triad-review → review-wave → alignment → approval の 5 段、責務分離による 5 段化が確定済み 2026-05-23。計画書改定は第 2 段階で実施）
   - §5.6：reopen 手続きの機械強制（手戻り種別の二次元表記）
   - §5.7：session 跨ぎ時の状態管理（`stages/in-progress/`）

3. **計画書 §5.23 と §5.23.12**（dogfooding ／ サブエージェント方式）
   - §5.23：手動 dogfooding 計画
   - §5.23.12：サブエージェント方式（中間経路、`subagent_mediated`）の運用条件

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見）
   - 機能横断波及所見の未消化件数と内容を把握
   - 要件 review-wave／alignment／approval で対処予定の件（過去のセッション 19 で旧 alignment-gate として実施した分は完了済み）

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ triad-review ／ review-wave ／ alignment ／ approval の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造（責務分離による 5 段化、2026-05-23 利用者明示承認）

```
intent 層（人間担当）
  ↓
機能分離（§3.1 で 7 機能体制を確定済み）
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
```

旧記述（drafting → review-wave → alignment-gate の 3 段）は次の 2 段階の改定により旧式化：

- alignment-gate を alignment（LLM 自動判定）と approval（人間または別モデル承認）の 2 段に分割
- drafting と triad-review を別段に分離（責務分離）

合計で 5 段化（drafting／triad-review／review-wave／alignment／approval）。計画書 §5.5 の改定は第 2 段階で実施し、それまでは本ガイドラインの 5 段記述が運用上の正本。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見の集約・対処、および **7 モデル比較実験の 2 回目（同根問題評価）と同根問題集約**（2026-05-27 セッション 34 追記、(ニ) (Q2) 採用、2026-05-28 セッション 35 で 2 回方式に訂正）。7 モデル比較実験は **2 回方式** で実施し、1 回目は機能ごとの triad-review 段で機能内 must-fix／should-fix を評価して機能内対処を完了させ、2 回目（本段）は全機能の triad-review 完了後に機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を評価して一貫した対処方針で全該当機能の仕様文書に反映する。詳細は計画書 §5.5 機能横断段の作業内容 ／ §5.9.6 N モデル比較実験の実施タイミングを参照
- **alignment**：LLM 自動判定による整合確認段（旧 alignment-gate を分割した前半、actor=llm）
- **approval**：人間または別モデル（§5.12 人間代役機構）による承認段（旧 alignment-gate を分割した後半、actor=human または proxy_model）

drafting と triad-review を別段にする理由：誰が何をしたかを段単位で明確に記録するため。草案作成者と判定者を分ける規律（§5.4）が段の構造上で機械検査可能になる。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者または別モデル承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に持ち越して **次の機能の drafting に進む**。これがセッション 19 の中盤で確立された運用パターン。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け（二軸的定義、2026-05-23 訂正）

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

セッション 19 中盤で、私（メインセッション）が「foundation の遡及修正」と表現したことを利用者が「波及であり alignment wave の範囲」と訂正した。これは A-001 が **同フェーズ内（要件段）の他機能（foundation／runtime）への影響** であって、上流フェーズへの修正ではない、という意味だった。私はこれを「遡及は悪、波及は善」と誤一般化していたが、後のセッションで利用者から再訂正があり、本ガイドラインを二軸的定義に書き直した（2026-05-23）。

### 3.2 修正案件の 4 種別（＋ 2 補助種別）

レビューで露出する所見は次の種別に分類する：

| 種別 | 内容 | 例 |
|---|---|---|
| **機能内対処** | 当該機能の仕様修正のみで完結 | 表現修正、機能内の語彙不統一訂正 |
| **波及（同フェーズ・横方向）** | 同フェーズ内の他機能の仕様修正も必要 | A-001：foundation 要件と runtime 要件の `not_run` 欠落 |
| **遡及（上流フェーズ・縦方向）** | 上流フェーズの仕様修正が必要 | 設計段で「要件段の Req 6 受入 8 に矛盾あり」と発見 |
| **遡及 ＋ 波及（縦 ＋ 横）** | 上流フェーズの複数機能に影響 | 設計段で発見した要件段の不整合が複数機能の要件文書に波及 |

補助種別：

- **leave-as-is（修正不要）**：判定役が「修正不要」と判断したもの、対処せず記録のみ
- **延期**：「将来フェーズで対処」と判定役が明示したもの（例：F-004 の配置時対処）

### 3.3 種別ごとの処理段と方法

#### (a) 機能内対処

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順（2026-05-25 セッション 25 規律、深掘り議論の義務化）

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM または人間）が独自判断で仕様文書を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**手順**：

1. must-fix 所見を 1 件ずつ取り上げる。複数所見が論理的に連動する場合は連動単位でまとめる（例：F-001 と F-007 が同一事象を別観点で扱う場合）
2. 各所見について、対処方針の提案を次の構造で平易に説明する：
   - その判断が必要になった経緯（要件文書や上流文書からの導出）
   - 候補案の列挙（必ず複数）
   - 各候補案の利点と弱点
   - **後段で発生し得る問題の深掘り**：下流仕様（他機能の design／tasks／implementation）、対象アプリへの配置可能性、機械検証時の挙動、実装フェーズの運用、将来の拡張性
   - 推奨案とその根拠
3. 「現状維持」を推奨する場合も、現状維持の弱点を検証してから示す
4. 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
5. 利用者の判断を得てから、仕様文書を 1 件ずつ Edit で修正する
6. 各修正後に grep または Read で機械的に照合し、反映を確認する
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の出典・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、計画書非配置、要件 7（リポジトリ内資産の規則）との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

本規律の出典：2026-05-25 セッション 25 の foundation／design must-fix 対処での手順違反事例（利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」と「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」）。詳細は当該セッションのレビュー記録 [.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md](../../.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md) を参照。

##### (a-2) review-run 後の proxy_model 判断代行手順

API 経由の review-run 後に、人間の個別判断を proxy_model が代行する場合も、メインセッション LLM が重要件を独自に確定して実装へ進むことを禁ずる。proxy_model 代行は「人間判断を省略する」ものではなく、判断主体を別モデルへ移す運用である。

**役割分担**：

1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

**重要件の判定閾値**：

- `must-fix`、`ERROR`、`CRITICAL` は必ず重要件として扱う
- `should-fix` でも、上流仕様、データ契約、機械ガード、証跡保持、ワークフロー権限境界、複数モデルの同根指摘に関わるものは重要件として扱う
- 同根指摘とは、複数モデルの所見が同じ対象ファイル・同じ出力契約・同じ機械ガード・同じ証跡・同じ原因に触れているものをいう。表現が異なっても、対象または原因が一致する場合は同根として扱う
- 正本削除、機械ガード削除、重要件閾値の引き下げ、承認証跡の削除、検証対象範囲の縮小は、コミット等と同じく人間の明示承認を要する不可逆操作として扱う
- 判断に迷うものは重要件側に倒し、proxy_model 判断または人間判断へ回す

**proxy_model への入力証跡**：

- proxy_model へ渡す判断材料には、メインセッション LLM の要約だけでなく、元 review raw への参照または抜粋を必ず含める
- `proxy-decisions/<finding-id>.prompt.md` に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `proxy-decisions/<finding-id>.decision.yaml` には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-decisions/<finding-id>.prompt.md`：proxy_model に渡した判断材料
- `proxy-decisions/<finding-id>.raw.txt`：proxy_model の生応答
- `proxy-decisions/<finding-id>.decision.yaml`：採用案、判断理由、最終ラベル、棄却案理由
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record

**並列化可能な単位**：

- proxy_model への判断依頼は、同根所見クラスタ単位で並列化できる
- TDD 実装は、互いに同じファイルを更新しない実装単位、または入出力契約が独立しているタスク単位で並列化できる
- 共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列で扱う
- 生成物、共有 helper、推移的契約、同じ出力 manifest、同じ traceability 出力を共有する修正は直列で扱う
- 並列実装の統合前に、メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する
- 並列処理で新しい判断問題が出た場合、その単位は停止し、proxy_model 判断または人間判断へ戻す
- 承認済み finding の実装中に見つけた未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施しない。必要なら新しい判断問題として停止する

**実装サブ担当 LLM の扱い**：

- 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う
- 同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する
- メインセッション LLM は、対象 finding、proxy decision、触ってよいファイル、期待テスト、禁止事項、停止条件を実装サブ担当へ渡す
- 実装サブ担当は、指定範囲外のファイル変更、判断変更、コミット、プッシュ、spec.json 更新、フェーズ移行を行わない
- 実装サブ担当が新しい判断問題、上流仕様への疑義、許可ファイル外の修正必要性を見つけた場合、その作業単位を停止してメインセッション LLM に戻す

**別スレッド生成物の扱い**：

- 別スレッド・分離 worktree で発生した生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する
- 実装差分は、メインセッション LLM が確認したうえで本線 worktree への取り込み候補にする
- 検証結果と判断根拠は、必要な要約だけを review-run、session record、または docs/notes に保存する
- 判断に影響した失敗試行、失敗パッチ、途中ログは work_noise から decision_basis へ昇格し、メインセッション LLM が要約または該当箇所を保存する
- 作業ノイズは本線 repo に取り込まない。作業ログ、一時メモ、途中のテスト出力、失敗パッチ案は原則としてサブ worktree 側に閉じる
- 本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点とする

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：triad-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ triad-review 完了後に開始）
- **方法**：
  1. triad-review 段で波及と判定されたら **当該機能では対処せず**、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ triad-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の各所見項目、消化後は「✅ 対処済み（日付）」追記

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（triad-review／review-wave／alignment／approval のいずれか）
- **処理方法**：**reopen 手続き（10 ステップ、§5.6）** を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第 7 ステップで `stages/reopen-procedure.yaml` の trigger_map（再実施対象段の決定表）を参照して機械決定。actor=human の段（approval 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの alignment ＋ approval を再実施
  4. **第 4 段階**：下流フェーズの alignment ＋ approval を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ `learning/workflow/carry-forward-register/reviewcompass-import.yaml` の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（triad-review 段で実施）

triad-review 段の判定役は、各所見について次の振り分けを行う：

```
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（triad-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → learning/workflow/carry-forward-register/reviewcompass-import.yaml に追記、review-wave 段で処理
  ├── YES（上流フェーズに戻る必要あり、単機能） → reopen 手続きを起動
  └── YES（上流フェーズに戻る必要あり、複数機能） → reopen ＋ 上流の review-wave で集約処理
  
別判定：
  ├── 修正不要 → leave-as-is（記録のみ）
  └── 将来フェーズで対処 → 延期（チェックリスト追記）
```

### 3.5 段ごとの露出と処理段の対応表

| 段 | 主に露出する所見 | 当該段内で処理する所見 | 次段に持ち越す所見 |
|---|---|---|---|
| drafting | 起草中の自己発見 | 機能内（草案に直接反映） | なし |
| triad-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| alignment | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approval | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の triad-review 段で発見されたら、即時 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／alignment／approval の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 採用根拠（計画書 §5.23.12 由来）

- メインセッションが主役、サブエージェントが敵対役・判定役を担う中間経路
- 手動 dogfooding と実行時経由の中間に位置
- フェーズ 1 から運用可能、追加料金なし（セッション 19 で実証）

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）はすべて独立したサブエージェントが担い、**メイン LLM（コンシェルジュ＝起草者）は 3 役のいずれにもならない**（計画書 §5.9.1、起草者と判定者の分離規律 §0.3）。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担う。

各役のモデルは `reviewcompass.yaml` で指定する。**推奨既定**：主役 Opus 4.7 ／ 敵対役 Sonnet 4.6 ／ 判定役 Opus 4.7（計画書 §5.9.1）。利用者が yaml で変更可能。

**モデル能力配分の規律（計画書 §5.9.1、2026-05-25 セッション 25 の foundation／design triad-review 実験により制定）**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

旧規律「3 役で異なるモデルファミリーを使う（モデル多様化）」「同モデル使用は禁止」は **撤回された**。モデル多様化単独ではバイアス低減効果が限定的で、能力配分の方が重要と判明したため（実験記録 [../notes/2026-05-25-triad-review-model-allocation-experiment.md](../notes/2026-05-25-triad-review-model-allocation-experiment.md) 由来）。

**実態の配置例**：foundation tasks triad-review（2026-05-26）では「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（実験(エ)継続、design triad-review と同配置）。いずれの役もサブエージェントで、メインセッション（起草者 Opus 4.7）は 3 役のいずれにも入っていない。

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **計画書引用は事後検証**：サブエージェントの計画書引用には §番号誤りが発生しうる（セッション 19 で実証）。メインセッションが grep で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や `learning/workflow/carry-forward-register/reviewcompass-import.yaml` への直接追記を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。Claude Code では Agent ツールの `model` パラメータで `"sonnet"`／`"haiku"` を指定していた。Codex や外部 API 経由では、各 adapter の手引きと `config/api-settings.yaml` の provider 設定を参照する

### 4.4 レビュー記録の必須フィールド（§5.4 起草者と判定者の分離）

レビュー記録の front-matter に次を必須化：

```yaml
author:
  identity: <adapter_main_session>
  model: <model-id>
  role: drafter
reviewer:
  identity: <adapter_reviewer_session>
  model: <model-id>
  role: final_judgment
  separation_from_author: true
```

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。

Claude Code 運用時の例では `claude_code_main_session` / `claude_code_subagent` を使っていた。Codex 運用時は `codex_main_session`、外部 API 検証者、または各 adapter が定義する識別子を使う。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できること。

### 4.5 mode 値（計画書 §5.23.12.5 由来）

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **計画書方針変更**：計画書の節追加・修正（例：§5.18.13 への記述追加、§5.23.12 新節）
- **大規模再設計**：素材から大幅に削減・再構成する場合（例：workflow-management の 156 行 9 要件 → 8 要件）
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須（計画書 §5.19.6 由来）
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない（2026-05-31 セッション 42 追記）

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **計画書方針変更**：計画書の該当節に決定日付付きで記載
- **機能横断対処方針**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

### 5.4 セッション記録の作成規律

原則として毎セッション、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` を作成または更新する。特に、重要な判断・承認・レビュー結果・修正経緯が発生した場合は必須とする。これは会話全文の逐語ログではなく、後で経緯を確認できる要約記録とする。

`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とする。同日の複数セッションでも番号を進め、同じ番号を再利用しない。
1 session につき 1 ファイルとし、同一 session 内で重要判断が複数回発生した場合は同じファイルへ追記する。重要判断ごとに別番号を消費しない。
並行セッションや未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。
コンテキスト切れや中断により当該 LLM が記録できない場合、次セッションが草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

最低限、次を記録する：

- このセッションで実施した作業
- 利用者が承認した判断と、その対象
- API レビューや独立検証の結果と三段階トリアージ
- 修正した主要ファイルと検証結果
- 失敗・見落とし・再発防止に必要な気づき
- 次セッションへの引き継ぎ

推奨見出しは既存 session 記録と同型とし、最低限次を含める：

1. サマリ（このセッションでやったこと）
2. 気づき・特筆点
3. コミット一覧（該当する場合）
4. 次セッションへの引き継ぎ

`TODO_NEXT_SESSION.md` は次セッション向けの入口メモであり、詳細な経緯記録の正本ではない。詳細経緯は `docs/sessions/` に残し、TODO には必要な参照だけを置く。

## 6. コミット規律

### 6.1 コミット単位

- **計画書更新 ＋ 基盤整備**：1〜2 コミット（セッション冒頭の方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順（計画書 §3.1 phase_order）に従う：

1. foundation
2. runtime
3. evaluation
4. analysis
5. workflow-management
6. self-improvement
7. conformance-evaluation

### 6.3 コミットメッセージ規律

- **平易な日本語**：英語技術用語の連発を避け、完全な日本語の文で書く
- **題名**：機能名 ＋ 作業種別（例：「foundation 機能の requirements 抽出と 3 役レビュー」）
- **本文**：作成・更新ファイルの列挙、主な反映内容、機能横断所見の持ち越し有無
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。Claude Code 運用時の履歴では `Claude Opus 4.7 (1M context) <noreply@anthropic.com>` を使っていたが、Codex 運用では自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 用語ガイド

### 7.1 「遡及」と「波及」（二軸的定義、2026-05-23 訂正）

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 7.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 7.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に集約、review-wave／alignment／approval の機能横断段で対処

### 7.4 サブエージェント関連

- **メインセッション**：作業の入口となる LLM session。草案作成とレビュー結果の取りまとめを担い、3 役レビューの判定者とは分離する
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。Claude Code では Agent ツール経由、Codex 運用では adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

### 7.5 計画書の節番号

- 計画書（`docs/plan/reconstruction-plan-2026-05-21.md`）の節番号は §X.Y 形式
- 引用時は **メインセッションで grep 確認**してから記述（サブエージェントの §番号誤り対策）

## 8. セッション 19 で得られた教訓（参考）

本ガイドラインは次の経験を反映している：

### 8.1 ワークフロー確認の失態

セッション 19 開始時、私（メインセッション）は計画書 §5.4〜§5.7 を読まずに foundation requirements の抽出を始めた。中盤で利用者が「ワークフローを再度読む」と指摘し、intent 段の所在（過去セッションで作成済み）、dogfeeding の §5.23 での既存記述、機能横断レビューの段位置（review-wave／alignment-gate）を確認することになった。**着手前の必読フロー（§1）はこの失態の再発防止策**。

### 8.2 用語混同（遡及／波及）

セッション 19 中盤で A-001（foundation の `not_run` 欠落）発見時、私が「foundation の遡及修正」と表現した。利用者が「遡及ではなく波及。本来は alignment wave の範囲」と訂正。**§3.1 の用語の使い分けはこの訂正を反映**。

### 8.3 機能横断波及所見の集約管理ファイルの新設

A-001 発見時、利用者の指示で `learning/workflow/carry-forward-register/reviewcompass-import.yaml` を新設して集約管理する運用パターンが確立した。これ以降、A-003／A-004／A-005／A-007／A-008 が同ファイルに追記され、要件 review-wave で一括消化された。

### 8.4 サブエージェントの計画書引用誤り

セッション 19 中盤、敵対役（Sonnet 4.6）が計画書 §5.18.11 を引用したが、実体は §5.18.2 周辺の別箇所だった（引用内容自体は正当）。**§4.3 の事後検証はこの経験を反映**。

### 8.5 サブエージェントの直接書き込みパターン

セッション 19 後半、敵対役が自発的に `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に直接追記するパターンを確立。メインセッションを介さない効率化として、後続セッションでも継続予定。

### 8.6 利用者判断の見極め不足

セッション 19 中で、サブエージェント方式の正式採用、A-007 の権限調停（案 1／案 2）、解釈論点 α／う など、利用者判断が必要な論点が複数発生した。**§5 の利用者判断必須項目はこの経験を反映**。

## 9. 関連文書

- 計画書：[../plan/reconstruction-plan-2026-05-21.md](../plan/reconstruction-plan-2026-05-21.md)（§5.4〜§5.8 ワークフロー、§5.23／§5.23.12 dogfooding／サブエージェント方式、§5.19.6 利用者判断の運用ルール）
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：[../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書であり、計画書の改定なしに更新可能
- 各セッションの経験から新たな教訓が得られた場合、§8 に追記
- 規律変更（§2〜§7）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新

```

## FILE: docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md

```text
# proxy review 判断代行と並列実装の正本化計画メモ

作成日：2026-06-04

## 目的

API review-run 後に、メインセッション LLM が raw レビューを集約して三段階トリアージし、重要件の判断を proxy_model が代行し、実装作業を必要に応じて別スレッド・分離 worktree へ切り出せるようにする。

本メモは、会話上の運用案を正本と機械ガードへ落とすための計画メモである。正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様であり、本メモは作業計画と段階導入の記録に限定する。

## 正本化する事項

1. メインセッション LLM は raw review を読み、モデル別要約、同根所見集約、三段階トリアージ下書き、候補案、推薦案を作る。
2. proxy_model は重要件について、採用案、判断理由、棄却案理由、最終ラベルを決める。
3. 機械ガードは proxy decision、raw response、候補案、採用案、判断理由、triage との整合を検査する。
4. 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う。
5. 別スレッド生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する。
6. 作業ノイズは本線 repo に取り込まない。
7. コミット、プッシュ、spec.json 更新、フェーズ移行は人間の明示承認を要求し、proxy_model は代行しない。

## 今回の実装範囲

- `review_triage.py` の approval record 検査で `approved_by: proxy_model` を扱う。
- proxy approval では `proxy_decisions` に finding ごとの decision file を要求する。
- decision file には `approved_by: proxy_model`、`proxy_model_id`、`decision_prompt_path`、`source_raw_paths`、`candidate_options`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を要求する。
- `raw_response_path` の実体が存在しなければ fail-closed にする。
- `decision_prompt_path` と `source_raw_paths` の実体が存在しなければ fail-closed にする。
- `candidate_options` が空または欠落していれば fail-closed にする。
- `approved_final_labels` と decision file の `final_label` が一致しなければ fail-closed にする。

## 今回はまだ実装しない事項

- 別スレッド作成や分離 worktree 作成の自動化。
- サブ担当への依頼テンプレート生成。
- サブ担当差分の許可ファイル外変更検査。
- triage / proxy decision / diff / test result の統合照合コマンド。

これらは、proxy approval gate が安定した後に段階的に追加する。

## 追加対応：自律・並列モード実行前ガード

自律・並列モードは、実装を始める前に実行計画 YAML を作り、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で機械検査する。

このガードは、次の事項を fail-closed で検査する。

1. 実行計画が `mode: autonomous_parallel` と `run_id` を持つ。
2. 人間または `proxy_model` の承認記録があり、レビュー結果サマリと三段階トリアージが利用者へ提示済みである。
3. 各タスクに `source_finding_ids`、担当、許可パス、期待テスト、停止条件がある。
4. 別スレッドまたはサブ担当へ渡すタスクは `separate_worktree` を使う。
5. 依存関係のない並列タスクが同じ `allowed_paths` を更新しない。
6. 統合ゲートとして、メインセッション確認、差分範囲確認、テスト確認、判断根拠確認を要求する。
7. 生成物分類として、実装差分、検証結果、判断根拠、作業ノイズの扱いを明示し、作業ノイズは本線 repo へ取り込まない。
8. `history.ledger_path` を `docs/logs/autonomous-parallel/` 配下に置き、task 割当、判断根拠、統合結果を後から追えるようにする。

重要件の修正は、レビュー結果の三段階トリアージ後に、候補案、推薦案、判断理由を提示し、承認または proxy decision が記録されるまで実装に進めない。自律実行中でも、`important_decision_requires_approval` が停止条件として各タスクに入っていない計画は逸脱とする。

## 追加対応：実装差分型の自律・並列実行ログ

API review-run 型の自律・並列実行は raw response、triage、model-result-summary を証跡にする。一方、実装差分型の自律実行では、API raw/triage が存在しないことがある。この場合は `outputs_policy.implementation_diff: commit_candidate` を明示し、`execution_evidence.completed_tasks`、`execution_evidence.parallelized_operations`、`execution_evidence.human_required_count` を証跡にする。

今回の self-improvement implementation.drafting では、次の形で実装差分型をテストした。

1. T-001：成果物配置の準備
2. T-002：入力モデル
3. T-003：signal_extraction モデル

実装はメインセッション LLM が同一 worktree で直列に行い、並列化は仕様・リポジトリ文脈の読み取り、テスト、workflow gate 確認など、同時実行しても差分衝突しない作業に限定した。`docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml` と同名 ledger に task 割当、完了タスク、並列化した操作、検証結果、統合判断を記録した。

このテストで、既存の `autonomous-plan` ガードが API review-run 型だけを想定し、実装差分型の `commit_candidate` を機械判定できないことが分かった。そのため、`tools/check-workflow-action.py autonomous-plan` を拡張し、`implementation_diff: commit_candidate` の場合は raw/triage 証跡の代わりに実装証跡を検査するようにした。これにより、実装差分型でも `human_required_count: 0`、完了タスク、統合ゲートを機械的に確認できる。

確認済みテスト：

- `python3 -m pytest tests/self-improvement -q`
- `python3 -m unittest tests.tools.test_check_workflow_action -v`
- `python3 tools/check-workflow-action.py autonomous-plan docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml --json`
- `git diff --check`

残る次作業は self-improvement T-004（提案モデル）である。5 種類の proposal、必須 7 フィールド、proposal_id 採番、`proposal.schema.json`、種別ごとの追加要件を TDD で実装する。重要判断や不可逆操作が出た場合だけ停止し、通常の実装・検証は自律的に進める。コミット、プッシュ、spec.json 更新、フェーズ移行は引き続き人間の明示承認を必要とする。

## 追加対応：デプロイ後監査の正本を ledger にする

自律・並列モードでは、`*-plan.yaml` は実行前に「これからどう進めるか」を検査するための artifact である。デプロイ後に必ず提供されるとは限らないため、事後監査の正本にしてはいけない。事後監査の正本は `docs/logs/autonomous-parallel/*.yaml` の ledger とする。

この境界を機械的に守るため、`autonomous-plan` は ledger に `execution_evidence_snapshot` を保存する。snapshot には、plan なしで監査するために必要な `completed_tasks`、`parallelized_operations`、`human_required_count` を含める。既存 ledger に snapshot がある場合、古い plan を再実行しても snapshot を巻き戻さない。

また、`tools/check-workflow-action.py autonomous-ledger-audit <ledger.yaml>` を追加し、plan ファイルなしで次を検査できるようにする。

1. ledger が `mode: autonomous_parallel`、`verdict: OK`、`exit_code: 0` を持つ。
2. `execution_evidence_snapshot.completed_tasks` が空でない。
3. `execution_evidence_snapshot.parallelized_operations` が配列である。
4. `execution_evidence_snapshot.human_required_count` が 0 である。
5. `integration_result.status`、`integration_result.tests`、`integration_result.decision` が存在する。

これにより、実行前検査は plan、デプロイ後監査は ledger という責務分離を明確にし、計画ファイルが消えても履歴確認できる状態を保つ。

## 追加対応：同種問題の横展開

上記修正後に、同じ「デプロイ後に一時 artifact がないと監査できない」問題が他にもないか精査した。結果、過去の workflow-management 自律・並列実行 ledger と review-run 報告 ready 判定に同種の穴があった。

対応内容：

1. `docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml` に `execution_evidence_snapshot` を補完し、`autonomous-ledger-audit` で plan なし監査できる状態にした。
2. `tools/api_providers/review_triage.py assert-review-report-ready` で、`ledger.integration_result` だけでなく `ledger.execution_evidence_snapshot` も要求するようにした。
3. `evaluation/metrics/dogfooding_metrics_extractor.py` が `ledger.execution_evidence_snapshot` から `completed_task_count`、`parallelized_operation_count`、`human_required_count` を抽出するようにした。
4. `.reviewcompass/specs/workflow-management/implementation-drafting.md` に、ledger がデプロイ後監査正本であること、`execution_evidence_snapshot` と `autonomous-ledger-audit` を使うことを追記した。

後続課題：

- `authorization.approval_record_path` が `conversation:` を指す場合、デプロイ後に会話ログが同梱されないと承認内容を再確認できない。急ぎの遮断条件ではないが、次の監査性強化では `authorization_snapshot` を ledger に保存することを検討する。

## 追加対応：review-run bundle は先例コピーではなく機能固有生成にする

implementation.triad-review の review-run 準備では、既存の workflow-management review-run をそのままコピー元にしない。workflow-management の実例は、raw response 保存、三段階トリアージ、plan/ledger、review summary、target manifest などの成果物構造が実際に動いた検証済みサンプルとして参照する。一方、レビュー観点、対象ファイル集合、重要所見の判定基準は、対象機能の intent、feature-partitioning、requirements、design、tasks から生成する。

理由は、機能軸そのものが intent から feature-partitioning を経て生成されるためである。開発するアプリが変われば、機能名、責務、隣接機能、受入基準、必要な証跡、テスト観点が変わる。したがって、review-run のひな形は特定機能の内容を持たず、フェーズ処理として不変な骨格だけを持つべきである。

共通骨格に入れる事項：

- `run_id`、対象 feature、phase/stage
- review target bundle と source manifest
- 3 役レビューの raw response 保存
- parsed、model-result-summary、triage、review summary の保存
- 三段階トリアージ
- 重要件は候補案、推薦案、判断理由を示し、承認または proxy decision の証跡ができるまで実装修正に進めないこと
- 自律・並列実行 plan/ledger と、事後監査用の ledger snapshot
- 人間判断、proxy_model 判断、不可逆操作の境界

機能ごとに生成する事項：

- レビュー観点
- 対象ファイル集合
- requirements/design/tasks/spec.json との対応
- 実装ファイルとテストファイルの対応
- 失敗時の影響と重要度
- 並列化できる作業単位
- 実装後に測るメトリクス

self-improvement implementation.triad-review では、workflow-management の guard 中心の観点を持ち込まず、規律と実体の双方向同期、提案権と実体変更権の分離、入力モデル、signal 抽出、提案、検証、承認、rollback、効果測定、機械検査、他機能接合、T-001〜T-011 の traceability を中心に review target bundle を作る。

```

## FILE: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml

```text
mode: autonomous_parallel
run_id: 2026-06-04-self-improvement-implementation-drafting
authorization:
  approved_by: user
  approval_record_path: conversation:2026-06-04:self-improvement-autonomous-parallel-test
  summary_presented_to_user: true
  triage_presented_to_user: true
tasks:
  - task_id: t001-layout
    source_finding_ids:
      - self-improvement-T-001
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - learning/workflow/
      - learning/findings/
      - learning/backtests/
      - learning/templates/
      - docs/discipline-compliance-reports/README.md
      - docs/disciplines/archive/README.md
      - tools/README.md
      - tools/self_improvement/schemas/.gitkeep
      - tests/self-improvement/.gitkeep
      - tests/self-improvement/test_t001_layout.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on: []
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t001_layout.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t002-input-model
    source_finding_ids:
      - self-improvement-T-002
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/input_model.py
      - tools/self_improvement/schemas/provenance.schema.json
      - tests/self-improvement/test_t002_input_model.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t002_input_model.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t003-signal-extraction
    source_finding_ids:
      - self-improvement-T-003
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/signal_extraction.py
      - tools/self_improvement/schemas/signal.schema.json
      - tests/self-improvement/test_t003_signal_extraction.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t002-input-model
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t003_signal_extraction.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t004-proposal-model
    source_finding_ids:
      - self-improvement-T-004
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/proposal_model.py
      - learning/workflow/schemas/proposal.schema.json
      - tests/self-improvement/test_t004_proposal_model.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
      - t003-signal-extraction
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t004_proposal_model.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t005-verification-model
    source_finding_ids:
      - self-improvement-T-005
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/verification_model.py
      - tools/self_improvement/impact_analysis.py
      - tests/self-improvement/test_t005_verification_model.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t004-proposal-model
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t005_verification_model.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t006-approval-model
    source_finding_ids:
      - self-improvement-T-006
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/approval_model.py
      - tests/self-improvement/test_t006_approval_model.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t004-proposal-model
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t006_approval_model.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t007-rollback-model
    source_finding_ids:
      - self-improvement-T-007
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/rollback_model.py
      - learning/workflow/schemas/rollback.schema.json
      - tests/self-improvement/test_t007_rollback_model.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
      - t006-approval-model
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t007_rollback_model.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t008-effect-measurement
    source_finding_ids:
      - self-improvement-T-008
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/effect_measurement.py
      - learning/workflow/schemas/metrics.schema.json
      - tests/self-improvement/test_t008_effect_measurement.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
      - t004-proposal-model
      - t006-approval-model
      - t007-rollback-model
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t008_effect_measurement.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t009-machine-verification
    source_finding_ids:
      - self-improvement-T-009
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self-improvement-check.py
      - tools/self_improvement/machine_verification.py
      - docs/operations/SELF_IMPROVEMENT_MACHINE_VERIFICATION.md
      - tests/self-improvement/test_t009_machine_verification.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t004-proposal-model
      - t006-approval-model
      - t007-rollback-model
      - t008-effect-measurement
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t009_machine_verification.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t010-interfaces
    source_finding_ids:
      - self-improvement-T-010
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/interfaces.py
      - learning/workflow/approved-updates/README.md
      - tests/self-improvement/test_t010_interfaces.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
      - t002-input-model
      - t004-proposal-model
      - t006-approval-model
      - t008-effect-measurement
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t010_interfaces.py -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
  - task_id: t011-test-strategy
    source_finding_ids:
      - self-improvement-T-011
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - tools/self_improvement/traceability.py
      - tests/self-improvement/test_t011_traceability.py
    forbidden_paths:
      - .git/
      - docs/disciplines/discipline_*.md
    depends_on:
      - t001-layout
      - t002-input-model
      - t003-signal-extraction
      - t004-proposal-model
      - t005-verification-model
      - t006-approval-model
      - t007-rollback-model
      - t008-effect-measurement
      - t009-machine-verification
      - t010-interfaces
    expected_tests:
      - python3 -m pytest tests/self-improvement/test_t011_traceability.py -q
      - python3 -m pytest tests/self-improvement -q
    stop_conditions:
      - irreversible_operation_requires_user
      - important_decision_requires_approval
    writes_repo_diff: true
    output_only: false
integration_gate:
  requires_main_session_review: true
  requires_diff_scope_check: true
  requires_tests: true
  requires_decision_basis_review: true
history:
  ledger_path: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting.yaml
  record_task_assignments: true
  record_decision_basis: true
  record_integration_result: true
  retention: preserve
outputs_policy:
  implementation_diff: commit_candidate
  verification_summary: required
  decision_basis: preserve_if_used
  work_noise: exclude
execution_evidence:
  completed_tasks:
    - t001-layout
    - t002-input-model
    - t003-signal-extraction
    - t004-proposal-model
    - t005-verification-model
    - t006-approval-model
    - t007-rollback-model
    - t008-effect-measurement
    - t009-machine-verification
    - t010-interfaces
    - t011-test-strategy
  parallelized_operations:
    - spec_and_repository_context_reads
    - local_test_and_workflow_gate_checks
    - traceability_and_dvt_audit
  human_required_count: 0

```

## FILE: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting.yaml

```text
run_id: 2026-06-04-self-improvement-implementation-drafting
mode: autonomous_parallel
verdict: OK
exit_code: 0
reasons: []
task_ids:
- t001-layout
- t002-input-model
- t003-signal-extraction
- t004-proposal-model
- t005-verification-model
- t006-approval-model
- t007-rollback-model
- t008-effect-measurement
- t009-machine-verification
- t010-interfaces
- t011-test-strategy
authorization:
  approved_by: user
  approval_record_path: conversation:2026-06-04:self-improvement-autonomous-parallel-test
  summary_presented_to_user: true
  triage_presented_to_user: true
history:
  ledger_path: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting.yaml
  record_task_assignments: true
  record_decision_basis: true
  record_integration_result: true
  retention: preserve
integration_gate:
  requires_main_session_review: true
  requires_diff_scope_check: true
  requires_tests: true
  requires_decision_basis_review: true
outputs_policy:
  implementation_diff: commit_candidate
  verification_summary: required
  decision_basis: preserve_if_used
  work_noise: exclude
current_state:
  mode: autonomous_parallel
  run_id: 2026-06-04-self-improvement-implementation-drafting
  task_count: 11
  parallel_task_count: 1
  checked_gates:
  - requires_main_session_review
  - requires_diff_scope_check
  - requires_tests
  - requires_decision_basis_review
  history_ledger_path: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting.yaml
  execution_evidence:
    review_run_dir: null
    required_raw_paths: &id001 []
    triage_path: null
    human_required_count: 0
    completed_tasks: &id002
    - t001-layout
    - t002-input-model
    - t003-signal-extraction
    - t004-proposal-model
    - t005-verification-model
    - t006-approval-model
    - t007-rollback-model
    - t008-effect-measurement
    - t009-machine-verification
    - t010-interfaces
    - t011-test-strategy
    parallelized_operations: &id003
    - spec_and_repository_context_reads
    - local_test_and_workflow_gate_checks
    - traceability_and_dvt_audit
  plan_path: docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml
execution_evidence_snapshot:
  review_run_dir: null
  required_raw_paths: *id001
  triage_path: null
  human_required_count: 0
  completed_tasks: *id002
  parallelized_operations: *id003
integration_result:
  status: completed
  tests: python3 -m pytest tests/self-improvement -q; python3 -m unittest tests.tools.test_check_workflow_action.AutonomousParallelPlanTests
    -v; python3 tools/check-workflow-action.py autonomous-plan docs/logs/autonomous-parallel/2026-06-04-self-improvement-implementation-drafting-plan.yaml
    --json; git diff --check
  decision: Self-improvement implementation drafting advanced through T-011 test strategy.
    Task tests, 7 model x 3 level coverage, requirements traceability, DVT deferral
    reasons, proposal schema validity, foundation reference-only contract, superseded
    reopen evidence, effect metrics, rollback integrity, and workflow-management materialized_at
    sync are covered by tests.

```

## FILE: tools/README.md

```text
# tools

ReviewCompass の補助スクリプトを置く場所。

## self-improvement

`tools/self_improvement/` は `self-improvement` 機能の import 対象 Python パッケージを置く名前空間である。

`tools/self_improvement/schemas/` はツール内部の中間スキーマを置く場所で、永続データ正本スキーマの `learning/workflow/schemas/` とは分離する。

命名規約:

- パッケージ／モジュールはアンダースコア区切りにする。例: `tools/self_improvement/`
- 単独実行 CLI スクリプトはハイフン区切りにする。例: `tools/self-improvement-check.py`

`tools/self-improvement-check.py` は self-improvement の機械検査 CLI の配置予定名である。第 1 期では手動 grep の補助から開始し、フェーズ 4 以降に段階的に自動化する。

```

## FILE: tools/self-improvement-check.py

```text
#!/usr/bin/env python3
"""CLI wrapper for self-improvement machine verification."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from tools.self_improvement.machine_verification import (
  MachineVerification,
  VerificationStatus,
)


def _commit_exists(commit_hash: str) -> bool:
  return subprocess.run(
    ["git", "cat-file", "-e", f"{commit_hash}^{{commit}}"],
    capture_output=True,
    text=True,
  ).returncode == 0


def _format(checks):
  verdict = (
    VerificationStatus.DEVIATION
    if any(check.status == VerificationStatus.DEVIATION for check in checks)
    else VerificationStatus.OK
  )
  return {
    "verdict": verdict.value,
    "checks": [check.to_dict() for check in checks],
  }


def main(argv=None):
  parser = argparse.ArgumentParser()
  sub = parser.add_subparsers(dest="command", required=True)

  mv1 = sub.add_parser("mv1")
  mv1.add_argument("--actor-feature", required=True)
  mv1.add_argument("--changed-file", action="append", default=[])
  mv1.add_argument("--json", action="store_true")

  all_cmd = sub.add_parser("all")
  all_cmd.add_argument("--actor-feature", required=True)
  all_cmd.add_argument("--changed-file", action="append", default=[])
  all_cmd.add_argument("--proposal-path", action="append", default=[])
  all_cmd.add_argument("--metric-date", required=True)
  all_cmd.add_argument("--json", action="store_true")

  args = parser.parse_args(argv)
  verifier = MachineVerification(Path.cwd())

  if args.command == "mv1":
    output = _format([
      verifier.check_direct_discipline_writes(
        changed_files=args.changed_file,
        actor_feature=args.actor_feature,
      )
    ])
  else:
    output = verifier.run_all(
      changed_files=args.changed_file,
      actor_feature=args.actor_feature,
      proposal_paths=[Path(path) for path in args.proposal_path],
      metric_date=args.metric_date,
      commit_exists=_commit_exists,
    )

  if args.json:
    print(json.dumps(output, ensure_ascii=False, indent=2))
  else:
    print(output["verdict"])
    for check in output["checks"]:
      for reason in check["reasons"]:
        print(f"- {check['check_id']}: {reason}")
  return 2 if output["verdict"] == "DEVIATION" else 0


if __name__ == "__main__":
  raise SystemExit(main())

```

## FILE: tools/self_improvement/input_model.py

```text
"""Input model for self-improvement workflow observations."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import yaml


SOURCE_VALUES = (
  "review_record",
  "compliance_report",
  "user_audit",
  "observation_pattern",
)
MIN_OBSERVATION_LENGTH = 30


class ProvenanceError(ValueError):
  """Raised when provenance cannot be trusted."""


@dataclass(frozen=True)
class InputRecord:
  provenance: Mapping[str, str]
  payload: Mapping[str, object]


def build_provenance(*, source: str, location: str, observation: str) -> dict:
  if source not in SOURCE_VALUES:
    raise ProvenanceError(f"unknown_source: {source}")
  if len(observation) < MIN_OBSERVATION_LENGTH:
    raise ProvenanceError("short_observation")
  if not location:
    raise ProvenanceError("missing_location")
  return {
    "source": source,
    "location": location,
    "observation": observation,
  }


class InputModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def load_sources(
    self,
    *,
    review_records: Iterable[Path],
    compliance_reports_dir: Optional[Path],
    user_audits: Iterable[Path],
    observation_patterns: Iterable[Path],
  ) -> List[InputRecord]:
    records: List[InputRecord] = []
    records.extend(self.load_files(review_records, source="review_record"))
    if compliance_reports_dir is not None:
      records.extend(self.load_compliance_reports(compliance_reports_dir))
    records.extend(self.load_files(user_audits, source="user_audit"))
    records.extend(self.load_files(observation_patterns, source="observation_pattern"))
    return records

  def load_compliance_reports(self, reports_dir: Path) -> List[InputRecord]:
    report_paths = sorted(Path(reports_dir).glob("*.yaml"))
    return self.load_files(report_paths, source="compliance_report")

  def load_files(self, paths: Iterable[Path], *, source: str) -> List[InputRecord]:
    records: List[InputRecord] = []
    for path in paths:
      records.extend(self._load_file(Path(path), source=source))
    return records

  def _load_file(self, path: Path, *, source: str) -> List[InputRecord]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("records", [])
    if not isinstance(entries, list):
      raise ProvenanceError(f"records_must_be_list: {path}")
    return [self._record_from_entry(entry, source=source) for entry in entries]

  def _record_from_entry(self, entry: Mapping[str, object], *, source: str) -> InputRecord:
    if not isinstance(entry, Mapping):
      raise ProvenanceError("record_must_be_mapping")
    location = str(entry.get("location") or "")
    observation = str(entry.get("observation") or "")
    provenance = build_provenance(
      source=source,
      location=location,
      observation=observation,
    )
    return InputRecord(provenance=provenance, payload=dict(entry))

```

## FILE: tools/self_improvement/signal_extraction.py

```text
"""Signal extraction for self-improvement workflow proposals."""
from pathlib import Path
from typing import Iterable, List, Mapping


SIGNAL_TYPES = (
  "discipline_absence",
  "discipline_violation",
  "discipline_obsolete",
  "discipline_conflict",
)

PROPOSAL_TYPE_BY_SIGNAL = {
  "discipline_absence": "new_discipline",
  "discipline_violation": "update",
  "discipline_obsolete": "archive",
  "discipline_conflict": "consolidation",
}


class SignalError(ValueError):
  """Raised when a signal cannot be trusted."""


def build_signal(
  *,
  signal_id: str,
  signal_type: str,
  observed_pattern: str,
  related_disciplines: Iterable[str],
  motivating_evidence_seed: Iterable[Mapping[str, object]],
) -> dict:
  related = list(related_disciplines)
  if signal_type not in SIGNAL_TYPES:
    raise SignalError(f"unknown_signal_type: {signal_type}")
  if signal_type in {"discipline_obsolete", "discipline_conflict"} and not related:
    raise SignalError("missing_related_disciplines")
  return {
    "signal_id": signal_id,
    "signal_type": signal_type,
    "observed_pattern": observed_pattern,
    "related_disciplines": related,
    "proposed_proposal_type": PROPOSAL_TYPE_BY_SIGNAL[signal_type],
    "motivating_evidence_seed": list(motivating_evidence_seed),
  }


class SignalExtractor:
  def __init__(self, *, violation_threshold: int = 3, obsolete_sessions_threshold: int = 5):
    self.violation_threshold = violation_threshold
    self.obsolete_sessions_threshold = obsolete_sessions_threshold

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def extract(self, candidates: Iterable[Mapping[str, object]]) -> List[dict]:
    signals: List[dict] = []
    for candidate in candidates:
      signal_type = self._classify(candidate)
      if signal_type is None:
        continue
      signals.append(self._build_from_candidate(candidate, signal_type))
    return signals

  def _classify(self, candidate: Mapping[str, object]):
    conflicting_disciplines = list(candidate.get("conflicting_disciplines") or [])
    if len(conflicting_disciplines) >= 2:
      return "discipline_conflict"

    matching_discipline = candidate.get("matching_discipline")
    sessions_without_reference = int(candidate.get("sessions_without_reference") or 0)
    if matching_discipline and sessions_without_reference >= self.obsolete_sessions_threshold:
      return "discipline_obsolete"

    evidence_count = int(candidate.get("evidence_count") or 0)
    if matching_discipline and evidence_count >= self.violation_threshold:
      return "discipline_violation"
    if not matching_discipline and evidence_count > 0:
      return "discipline_absence"
    return None

  def _build_from_candidate(self, candidate: Mapping[str, object], signal_type: str) -> dict:
    related = self._related_disciplines(candidate, signal_type)
    return build_signal(
      signal_id=str(candidate["signal_id"]),
      signal_type=signal_type,
      observed_pattern=str(candidate["observed_pattern"]),
      related_disciplines=related,
      motivating_evidence_seed=list(candidate.get("motivating_evidence_seed") or []),
    )

  def _related_disciplines(self, candidate: Mapping[str, object], signal_type: str) -> List[str]:
    if signal_type == "discipline_conflict":
      return list(candidate.get("conflicting_disciplines") or [])
    if signal_type == "discipline_obsolete":
      return list(candidate.get("related_disciplines") or [])
    matching_discipline = candidate.get("matching_discipline")
    return [str(matching_discipline)] if matching_discipline else []

```

## FILE: tools/self_improvement/proposal_model.py

```text
"""Proposal model for self-improvement workflow updates."""
import re
from pathlib import Path
from typing import Iterable, Mapping, Optional

import yaml


PROPOSAL_TYPES = (
  "new_discipline",
  "update",
  "status_change",
  "archive",
  "consolidation",
)
STATUS_VALUES = (
  "pending",
  "approved",
  "rejected",
  "superseded",
)
REQUIRED_FIELDS = (
  "proposal_id",
  "proposal_type",
  "target_discipline_path",
  "motivating_evidence",
  "proposed_change",
  "expected_effect",
  "status",
)
WORKFLOW_DIRECTORIES = (
  "proposals",
  "approved-updates",
  "rejected-updates",
  "rollback",
)
TARGET_DISCIPLINE_PATTERN = re.compile(r"^docs/disciplines/discipline_.*\.md$")
ID_PATTERN = re.compile(r"^(?P<prefix>[A-Z]+)-(?P<number>[0-9]+)$")


class ProposalError(ValueError):
  """Raised when a proposal cannot be trusted."""


def validate_proposal(proposal: Mapping[str, object]) -> None:
  missing = [field for field in REQUIRED_FIELDS if field not in proposal]
  if missing:
    raise ProposalError(f"missing_required_fields: {missing}")

  proposal_type = proposal["proposal_type"]
  if proposal_type not in PROPOSAL_TYPES:
    raise ProposalError(f"unknown_proposal_type: {proposal_type}")
  status = proposal["status"]
  if status not in STATUS_VALUES:
    raise ProposalError(f"unknown_status: {status}")
  target_path = str(proposal["target_discipline_path"])
  if not TARGET_DISCIPLINE_PATTERN.match(target_path):
    raise ProposalError(f"invalid_target_discipline_path: {target_path}")

  evidence = proposal["motivating_evidence"]
  if not isinstance(evidence, list) or not evidence:
    raise ProposalError("invalid_motivating_evidence")
  for item in evidence:
    if not isinstance(item, Mapping):
      raise ProposalError("invalid_motivating_evidence")
    if set(item) < {"source", "location", "observation"}:
      raise ProposalError("invalid_motivating_evidence")

  _validate_type_specific(proposal_type, proposal)


def _validate_type_specific(proposal_type: str, proposal: Mapping[str, object]) -> None:
  proposed_change = proposal.get("proposed_change")
  if not isinstance(proposed_change, Mapping):
    raise ProposalError("invalid_proposed_change")

  if proposal_type == "new_discipline":
    if not proposed_change.get("draft_discipline"):
      raise ProposalError("missing_draft_discipline")
    if not proposed_change.get("relationship_notes"):
      raise ProposalError("missing_relationship_notes")
  elif proposal_type == "update":
    if not proposed_change.get("change_diff"):
      raise ProposalError("missing_change_diff")
  elif proposal_type == "status_change":
    if not proposal.get("statistical_evidence"):
      raise ProposalError("missing_statistical_evidence")
  elif proposal_type == "archive":
    if not proposed_change.get("archive_readme_path"):
      raise ProposalError("missing_archive_readme_path")
  elif proposal_type == "consolidation":
    source_paths = proposal.get("source_discipline_paths")
    if not isinstance(source_paths, list) or not source_paths:
      raise ProposalError("missing_source_discipline_paths")
    if not proposed_change.get("mapping_table"):
      raise ProposalError("missing_mapping_table")


class ProposalModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def create_proposal(
    self,
    *,
    proposal_type: str,
    target_discipline_path: str,
    signal: Mapping[str, object],
    proposed_change: Mapping[str, object],
    expected_effect: str,
    source_discipline_paths: Optional[Iterable[str]] = None,
    statistical_evidence: Optional[Mapping[str, object]] = None,
  ) -> dict:
    if proposal_type not in PROPOSAL_TYPES:
      raise ProposalError(f"unknown_proposal_type: {proposal_type}")

    proposal = {
      "proposal_id": self.next_proposal_id("WP"),
      "proposal_type": proposal_type,
      "target_discipline_path": target_discipline_path,
      "motivating_evidence": list(signal.get("motivating_evidence_seed") or []),
      "proposed_change": dict(proposed_change),
      "expected_effect": expected_effect,
      "status": "pending",
    }
    if source_discipline_paths is not None:
      proposal["source_discipline_paths"] = list(source_discipline_paths)
    if statistical_evidence is not None:
      proposal["statistical_evidence"] = dict(statistical_evidence)

    validate_proposal(proposal)
    return proposal

  def next_proposal_id(self, prefix: str) -> str:
    max_number = 0
    for proposal_id in self._iter_existing_ids():
      match = ID_PATTERN.match(proposal_id)
      if not match or match.group("prefix") != prefix:
        continue
      max_number = max(max_number, int(match.group("number")))
    next_number = max_number + 1
    width = 3 if next_number <= 999 else len(str(next_number))
    return f"{prefix}-{next_number:0{width}d}"

  def _iter_existing_ids(self):
    workflow_root = self.root / "learning" / "workflow"
    for directory in WORKFLOW_DIRECTORIES:
      for path in sorted((workflow_root / directory).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping) and isinstance(data.get("proposal_id"), str):
          yield data["proposal_id"]

```

## FILE: tools/self_improvement/verification_model.py

```text
"""Verification model for workflow improvement proposals."""
from typing import Iterable, Mapping


class VerificationModel:
  def __init__(self, *, promotion_threshold: float = 0.9):
    self.promotion_threshold = promotion_threshold

  def run_retrospective_simulation(
    self,
    proposal: dict,
    *,
    target_scope: str,
    records: Iterable[Mapping[str, object]],
  ) -> dict:
    record_list = list(records)
    target_count = len(record_list)
    violation_count = sum(1 for record in record_list if record.get("violates") is True)
    violation_rate = violation_count / target_count if target_count else 0.0
    result = {
      "method": "retrospective_simulation",
      "target_scope": target_scope,
      "target_count": target_count,
      "violation_count": violation_count,
      "violation_rate": violation_rate,
    }
    statistical_evidence = proposal.setdefault("statistical_evidence", {})
    statistical_evidence["retrospective_simulation"] = result
    return result

  def evaluate_pilot_operation(self, compliance_series, *, period=None) -> dict:
    series = [
      self._normalize_compliance_entry(index, entry)
      for index, entry in enumerate(compliance_series, start=1)
    ]
    final_rate = series[-1]["compliance_rate"] if series else 0.0
    decision = "enforce" if final_rate >= self.promotion_threshold else "not_ready"
    return {
      "method": "pilot_operation",
      "period": period,
      "threshold": self.promotion_threshold,
      "compliance_series": series,
      "final_compliance_rate": final_rate,
      "promotion_decision": decision,
    }

  def mark_unverifiable(self, *, proposal_id: str, reason: str) -> dict:
    return {
      "proposal_id": proposal_id,
      "verification_status": "user_audit_required",
      "auto_approval": False,
      "reason": reason,
    }

  def _normalize_compliance_entry(self, index: int, entry) -> dict:
    if isinstance(entry, Mapping):
      return {
        "session": entry.get("session", f"session-{index}"),
        "compliance_rate": float(entry["compliance_rate"]),
      }
    return {
      "session": f"session-{index}",
      "compliance_rate": float(entry),
    }

```

## FILE: tools/self_improvement/impact_analysis.py

```text
"""Impact analysis helpers for discipline references."""
import re
from pathlib import Path

import yaml


INTERNAL_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


class ImpactAnalyzer:
  def __init__(self, root: Path):
    self.root = Path(root)

  def detect_internal_links(self):
    results = []
    for path in self._discipline_paths():
      links = INTERNAL_LINK_PATTERN.findall(path.read_text(encoding="utf-8"))
      if links:
        results.append({
          "path": self._relative(path),
          "links": links,
        })
    return results

  def analyze_conflicts(self):
    metadata = {
      self._relative(path): self._read_metadata(path)
      for path in self._discipline_paths()
    }
    links_by_path = {
      self._relative(path): INTERNAL_LINK_PATTERN.findall(path.read_text(encoding="utf-8"))
      for path in self._discipline_paths()
    }
    return {
      "name_duplicates": self._duplicates(metadata, "name"),
      "content_overlaps": self._duplicates(metadata, "applies_to"),
      "reference_cycles": self._reference_cycles(links_by_path),
    }

  def _discipline_paths(self):
    return sorted((self.root / "docs" / "disciplines").glob("discipline_*.md"))

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))

  def _read_metadata(self, path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
      return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
      return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}

  def _duplicates(self, metadata, key):
    by_value = {}
    for path, values in metadata.items():
      value = values.get(key)
      if value:
        by_value.setdefault(value, []).append(path)
    return [
      {
        key: value,
        "paths": paths,
      }
      for value, paths in sorted(by_value.items())
      if len(paths) > 1
    ]

  def _reference_cycles(self, links_by_path):
    cycles = []
    normalized = {
      path: {self._link_to_path(link) for link in links}
      for path, links in links_by_path.items()
    }
    for path, linked_paths in sorted(normalized.items()):
      for linked_path in sorted(linked_paths):
        if linked_path <= path:
          continue
        if path in normalized.get(linked_path, set()):
          cycles.append({"paths": [path, linked_path]})
    return cycles

  def _link_to_path(self, link: str) -> str:
    name = link if link.endswith(".md") else f"{link}.md"
    return f"docs/disciplines/{name}"

```

## FILE: tools/self_improvement/approval_model.py

```text
"""Approval model for workflow proposal state transitions."""
from pathlib import Path

import yaml


APPROVAL_WORDS = ("承認", "OK", "採用", "進めて", "はい")
REJECTION_WORDS = ("却下", "不採用", "reject")


class ApprovalError(ValueError):
  """Raised when an approval transition is not permitted."""


class ApprovalModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  def approve(self, proposal_path: Path, *, approval_text: str) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "pending", "approved")
    self._require_approval(approval_text)
    if self._is_enforcement_status_change(proposal):
      self._require_approval(approval_text)
    proposal["status"] = "approved"
    target = self.root / "learning" / "workflow" / "approved-updates" / proposal_path.name
    return self._write_transition(proposal_path, target, proposal, "pending", "approved")

  def reject(self, proposal_path: Path, *, approval_text: str) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "pending", "rejected")
    self._require_rejection(approval_text)
    proposal["status"] = "rejected"
    target = self.root / "learning" / "workflow" / "rejected-updates" / proposal_path.name
    return self._write_transition(proposal_path, target, proposal, "pending", "rejected")

  def supersede(
    self,
    proposal_path: Path,
    *,
    superseded_by: str,
    superseded_at: str,
    reopen_reason: str,
    approval_text: str,
    declaration: bool,
    new_conclusion: bool,
  ) -> dict:
    proposal_path = Path(proposal_path)
    proposal = self._read(proposal_path)
    self._require_transition(proposal, "approved", "superseded")
    self._require_approval(approval_text)
    if not all([declaration, new_conclusion, superseded_by, superseded_at, reopen_reason]):
      raise ApprovalError("missing_reopen_fields")
    proposal["status"] = "superseded"
    proposal["superseded_by"] = superseded_by
    proposal["superseded_at"] = superseded_at
    proposal["reopen_reason"] = reopen_reason
    self._write(proposal_path, proposal)
    return {
      "proposal_id": proposal["proposal_id"],
      "from_status": "approved",
      "to_status": "superseded",
      "source_path": self._relative(proposal_path),
      "target_path": self._relative(proposal_path),
      "move_operation": "none_status_only",
    }

  def _read(self, path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
      raise ApprovalError("proposal_must_be_mapping")
    return data

  def _write(self, path: Path, proposal: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def _write_transition(
    self,
    source: Path,
    target: Path,
    proposal: dict,
    from_status: str,
    to_status: str,
  ) -> dict:
    self._write(target, proposal)
    if source != target and source.exists():
      source.unlink()
    return {
      "proposal_id": proposal["proposal_id"],
      "from_status": from_status,
      "to_status": to_status,
      "source_path": self._relative(source),
      "target_path": self._relative(target),
      "move_operation": "git_mv_required",
    }

  def _require_transition(self, proposal: dict, from_status: str, to_status: str) -> None:
    if proposal.get("status") != from_status:
      raise ApprovalError(
        f"invalid_transition: {proposal.get('status')} -> {to_status}"
      )

  def _require_approval(self, text: str) -> None:
    if not any(word in text for word in APPROVAL_WORDS):
      raise ApprovalError("explicit_user_approval_required")

  def _require_rejection(self, text: str) -> None:
    if not any(word in text for word in REJECTION_WORDS):
      raise ApprovalError("explicit_user_rejection_required")

  def _is_enforcement_status_change(self, proposal: dict) -> bool:
    proposed_change = proposal.get("proposed_change") or {}
    return (
      proposal.get("proposal_type") == "status_change"
      and proposed_change.get("from") == "aspirational"
      and proposed_change.get("to") == "enforced"
    )

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))

```

## FILE: tools/self_improvement/rollback_model.py

```text
"""Rollback history model for workflow improvement proposals."""
import re
from pathlib import Path
from typing import Mapping

import yaml

from tools.self_improvement.impact_analysis import INTERNAL_LINK_PATTERN


ROLLBACK_METHODS = (
  "archive_restoration",
  "status_downgrade",
  "git_revert",
)
REQUIRED_FIELDS = (
  "rollback_id",
  "target_proposal_id",
  "rollback_method",
  "rollback_reason",
  "rollback_date",
  "related_artifacts",
)
RB_PATTERN = re.compile(r"^RB-(?P<number>[0-9]+)$")


class RollbackError(ValueError):
  """Raised when a rollback record cannot be trusted."""


def validate_rollback_record(record: Mapping[str, object]) -> None:
  missing = [field for field in REQUIRED_FIELDS if field not in record]
  if missing:
    raise RollbackError(f"missing_required_fields: {missing}")
  method = record["rollback_method"]
  if method not in ROLLBACK_METHODS:
    raise RollbackError(f"unknown_rollback_method: {method}")
  if not isinstance(record["related_artifacts"], list):
    raise RollbackError("related_artifacts_must_be_list")


class RollbackModel:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def create_rollback_record(
    self,
    *,
    target_proposal_id: str,
    rollback_method: str,
    rollback_reason: str,
    rollback_date: str,
    related_artifacts: list,
  ) -> dict:
    record = {
      "rollback_id": self.next_rollback_id(),
      "target_proposal_id": target_proposal_id,
      "rollback_method": rollback_method,
      "rollback_reason": rollback_reason,
      "rollback_date": rollback_date,
      "related_artifacts": list(related_artifacts),
    }
    validate_rollback_record(record)
    path = (
      self.root
      / "learning"
      / "workflow"
      / "rollback"
      / f"{rollback_date}-{record['rollback_id']}.yaml"
    )
    self._write_yaml(path, record)
    return record

  def next_rollback_id(self) -> str:
    max_number = 0
    rollback_root = self.root / "learning" / "workflow" / "rollback"
    for path in sorted(rollback_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if not isinstance(data, Mapping):
        continue
      match = RB_PATTERN.match(str(data.get("rollback_id", "")))
      if match:
        max_number = max(max_number, int(match.group("number")))
    next_number = max_number + 1
    width = 3 if next_number <= 999 else len(str(next_number))
    return f"RB-{next_number:0{width}d}"

  def symlink_recreation_plan(self, *, memory_link: str, repo_target: str) -> dict:
    checks = [
      "confirm_memory_link_path",
      "confirm_repo_target_exists",
      "remove_stale_link_if_needed",
      "create_symbolic_link",
      "verify_link_resolves_to_repo_target",
    ]
    return {
      "memory_link": memory_link,
      "repo_target": repo_target,
      "steps": [
        {
          "step": index,
          "action": action,
          "machine_check": True,
        }
        for index, action in enumerate(checks, start=1)
      ],
    }

  def trace_history(self, proposal_id: str) -> dict:
    proposal = self._find_proposal(proposal_id)
    rollbacks = []
    rollback_root = self.root / "learning" / "workflow" / "rollback"
    for path in sorted(rollback_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if isinstance(data, Mapping) and data.get("target_proposal_id") == proposal_id:
        rollbacks.append({
          "path": self._relative(path),
          "rollback_id": data.get("rollback_id"),
          "rollback_method": data.get("rollback_method"),
        })
    return {
      "proposal": proposal,
      "rollbacks": rollbacks,
    }

  def check_archive_restoration_integrity(
    self,
    *,
    restored_discipline_path: str,
    archive_readme_path: str,
    report_date: str,
  ) -> dict:
    restored_path = self.root / restored_discipline_path
    archive_path = self.root / archive_readme_path
    text = restored_path.read_text(encoding="utf-8")
    metadata = self._front_matter(text)
    links = INTERNAL_LINK_PATTERN.findall(text)
    archive_text = archive_path.read_text(encoding="utf-8") if archive_path.exists() else ""
    result = {
      "check": "archive_restoration_integrity",
      "restored_discipline_path": restored_discipline_path,
      "archive_readme_path": archive_readme_path,
      "front_matter_valid": all(metadata.get(field) for field in ("name", "status")),
      "internal_links": links,
      "archive_readme_consistent": metadata.get("name", "") in archive_text,
    }
    report_path = (
      self.root
      / "docs"
      / "discipline-compliance-reports"
      / f"{report_date}-rollback.yaml"
    )
    self._write_yaml(report_path, result)
    return result

  def _find_proposal(self, proposal_id: str) -> dict:
    for directory in ("proposals", "approved-updates", "rejected-updates"):
      root = self.root / "learning" / "workflow" / directory
      for path in sorted(root.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping) and data.get("proposal_id") == proposal_id:
          return {
            "path": self._relative(path),
            "status": data.get("status"),
          }
    raise RollbackError(f"proposal_not_found: {proposal_id}")

  def _front_matter(self, text: str) -> dict:
    if not text.startswith("---"):
      return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
      return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}

  def _write_yaml(self, path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))

```

## FILE: tools/self_improvement/effect_measurement.py

```text
"""Effect measurement for workflow improvement proposals."""
from datetime import date
from pathlib import Path
from typing import Mapping

import yaml


PROPOSAL_DIRECTORIES = (
  "proposals",
  "approved-updates",
  "rejected-updates",
)
PROPOSAL_TYPES = (
  "new_discipline",
  "update",
  "status_change",
  "archive",
  "consolidation",
)


class EffectMeasurement:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  @staticmethod
  def manual_aggregation_steps() -> list:
    return [
      {"id": "find_wc", "description": "find と wc で対象 YAML 件数を数える"},
      {"id": "grep_sort_uniq", "description": "grep、sort、uniq で種別と状態を集計する"},
      {"id": "adoption_rate_calculation", "description": "approved、rejected、superseded から採用率を算出する"},
      {"id": "metrics_record", "description": "learning/workflow/metrics/<日付>.yaml に記録する"},
    ]

  def calculate_metrics(self, *, metric_date: str) -> dict:
    proposals = self._load_proposals()
    rollback_count = len(self._load_rollbacks())
    approved_count = self._count_status(proposals, "approved")
    rejected_count = self._count_status(proposals, "rejected")
    superseded_count = self._count_status(proposals, "superseded")
    adoption_denominator = approved_count + rejected_count + superseded_count
    adoption_rate = (
      (approved_count + superseded_count) / adoption_denominator
      if adoption_denominator
      else 0.0
    )
    rollback_rate = rollback_count / approved_count if approved_count else 0.0

    metrics = {
      "metric_date": metric_date,
      "discipline_compliance_rate": self._discipline_compliance_rate(),
      "promotion_count": self._promotion_count(proposals),
      "archive_count": self._archive_count(proposals),
      "proposal_counts_by_type": self._proposal_counts_by_type(proposals),
      "adoption_rate": adoption_rate,
      "adoption_rate_formula": "(approved + superseded) / (approved + rejected + superseded)",
      "rollback_rate": rollback_rate,
      "average_days_to_adoption": self._average_days_to_adoption(proposals),
      "manual_aggregation_steps": self.manual_aggregation_steps(),
    }
    return metrics

  def write_metrics(self, *, metric_date: str = None) -> Path:
    metric_date = metric_date or date.today().isoformat()
    metrics = self.calculate_metrics(metric_date=metric_date)
    metrics["manual_aggregation_steps"] = [
      step["id"] for step in self.manual_aggregation_steps()
    ]
    path = self.root / "learning" / "workflow" / "metrics" / f"{metric_date}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(metrics, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )
    return path

  def _load_proposals(self) -> list:
    proposals = []
    workflow_root = self.root / "learning" / "workflow"
    for directory in PROPOSAL_DIRECTORIES:
      for path in sorted((workflow_root / directory).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, Mapping):
          proposals.append(dict(data))
    return proposals

  def _load_rollbacks(self) -> list:
    rollback_root = self.root / "learning" / "workflow" / "rollback"
    rollbacks = []
    for path in sorted(rollback_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if isinstance(data, Mapping):
        rollbacks.append(dict(data))
    return rollbacks

  def _discipline_compliance_rate(self) -> float:
    checked = 0
    violations = 0
    report_root = self.root / "docs" / "discipline-compliance-reports"
    for path in sorted(report_root.glob("*.yaml")):
      data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
      if not isinstance(data, Mapping):
        continue
      checked += int(data.get("checked_count") or 0)
      violations += int(data.get("violation_count") or 0)
    if checked == 0:
      return 0.0
    return (checked - violations) / checked

  def _promotion_count(self, proposals: list) -> int:
    return sum(
      1
      for proposal in proposals
      if proposal.get("status") == "approved"
      and proposal.get("proposal_type") == "status_change"
      and (proposal.get("proposed_change") or {}).get("from") == "aspirational"
      and (proposal.get("proposed_change") or {}).get("to") == "enforced"
    )

  def _archive_count(self, proposals: list) -> int:
    return sum(
      1
      for proposal in proposals
      if proposal.get("proposal_type") == "archive"
      and proposal.get("status") in ("approved", "superseded")
    )

  def _proposal_counts_by_type(self, proposals: list) -> dict:
    counts = {}
    for proposal in proposals:
      proposal_type = proposal.get("proposal_type")
      if proposal_type in PROPOSAL_TYPES:
        counts[proposal_type] = counts.get(proposal_type, 0) + 1
    return dict(sorted(counts.items()))

  def _count_status(self, proposals: list, status: str) -> int:
    return sum(1 for proposal in proposals if proposal.get("status") == status)

  def _average_days_to_adoption(self, proposals: list) -> float:
    durations = []
    for proposal in proposals:
      if proposal.get("status") not in ("approved", "superseded"):
        continue
      submitted_at = proposal.get("submitted_at")
      approved_at = proposal.get("approved_at")
      if not submitted_at or not approved_at:
        continue
      durations.append(
        (date.fromisoformat(approved_at) - date.fromisoformat(submitted_at)).days
      )
    return sum(durations) / len(durations) if durations else 0.0

```

## FILE: tools/self_improvement/machine_verification.py

```text
"""Machine verification checks for self-improvement workflow safety."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Mapping

import yaml

from tools.self_improvement.proposal_model import ProposalError, validate_proposal


class VerificationStatus(str, Enum):
  OK = "OK"
  DEVIATION = "DEVIATION"


@dataclass(frozen=True)
class VerificationResult:
  check_id: str
  status: VerificationStatus
  reasons: list
  details: dict

  def to_dict(self) -> dict:
    return {
      "check_id": self.check_id,
      "status": self.status.value,
      "reasons": self.reasons,
      "details": self.details,
    }


class MachineVerification:
  def __init__(self, root: Path = None):
    self.root = Path(root) if root is not None else Path.cwd()

  def check_direct_discipline_writes(
    self,
    *,
    changed_files: Iterable[str],
    actor_feature: str,
  ) -> VerificationResult:
    changed = list(changed_files)
    violations = [
      path for path in changed
      if actor_feature == "self-improvement"
      and path.startswith("docs/disciplines/discipline_")
      and path.endswith(".md")
    ]
    if violations:
      return VerificationResult(
        check_id="MV-1",
        status=VerificationStatus.DEVIATION,
        reasons=[f"self-improvement direct discipline write detected: {path}" for path in violations],
        details={"changed_files": changed},
      )
    return VerificationResult(
      check_id="MV-1",
      status=VerificationStatus.OK,
      reasons=[],
      details={"changed_files": changed},
    )

  def check_proposal_required_fields(self, proposal_paths: Iterable[Path]) -> VerificationResult:
    reasons = []
    checked_paths = []
    for path in proposal_paths:
      checked_paths.append(str(path))
      proposal = self._load_yaml(Path(path))
      try:
        validate_proposal(proposal)
      except ProposalError as exc:
        reasons.append(f"{path}: {exc}")
    return self._result("MV-2", reasons, {"checked_paths": checked_paths})

  def check_materialization_commit_hashes(
    self,
    proposal_paths: Iterable[Path],
    *,
    commit_exists: Callable[[str], bool],
  ) -> VerificationResult:
    reasons = []
    checked_hashes = []
    skipped_null_count = 0
    for path in proposal_paths:
      proposal = self._load_yaml(Path(path))
      commit_hash = proposal.get("materialization_commit_hash")
      if commit_hash in (None, ""):
        skipped_null_count += 1
        continue
      checked_hashes.append(commit_hash)
      if not commit_exists(str(commit_hash)):
        reasons.append(f"{path}: materialization_commit_hash not found: {commit_hash}")
    return self._result(
      "MV-3",
      reasons,
      {
        "checked_hashes": checked_hashes,
        "skipped_null_count": skipped_null_count,
      },
    )

  def check_superseded_fields(self, proposal_paths: Iterable[Path]) -> VerificationResult:
    reasons = []
    checked_paths = []
    for path in proposal_paths:
      proposal = self._load_yaml(Path(path))
      if proposal.get("status") != "superseded":
        continue
      checked_paths.append(str(path))
      missing = [
        field for field in ("superseded_by", "superseded_at", "reopen_reason")
        if not proposal.get(field)
      ]
      if missing:
        reasons.append(f"{path}: missing superseded fields: {', '.join(missing)}")
    return self._result("MV-4", reasons, {"checked_paths": checked_paths})

  def run_all(
    self,
    *,
    changed_files: Iterable[str],
    actor_feature: str,
    proposal_paths: Iterable[Path],
    metric_date: str,
    commit_exists: Callable[[str], bool],
  ) -> dict:
    proposal_path_list = list(proposal_paths)
    checks = [
      self.check_direct_discipline_writes(
        changed_files=changed_files,
        actor_feature=actor_feature,
      ),
      self.check_proposal_required_fields(proposal_path_list),
      self.check_materialization_commit_hashes(
        proposal_path_list,
        commit_exists=commit_exists,
      ),
      self.check_superseded_fields(proposal_path_list),
    ]
    verdict = (
      VerificationStatus.DEVIATION
      if any(check.status == VerificationStatus.DEVIATION for check in checks)
      else VerificationStatus.OK
    )
    summary = {
      "verdict": verdict.value,
      "checks": [check.to_dict() for check in checks],
    }
    self._write_metrics(metric_date, summary)
    return summary

  def _result(self, check_id: str, reasons: list, details: dict) -> VerificationResult:
    status = VerificationStatus.DEVIATION if reasons else VerificationStatus.OK
    return VerificationResult(
      check_id=check_id,
      status=status,
      reasons=reasons,
      details=details,
    )

  def _load_yaml(self, path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
      return {}
    return dict(data)

  def _write_metrics(self, metric_date: str, summary: dict) -> None:
    path = (
      self.root
      / "learning"
      / "workflow"
      / "metrics"
      / f"{metric_date}-machine-verification.yaml"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      yaml.safe_dump(summary, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

```

## FILE: tools/self_improvement/interfaces.py

```text
"""Interfaces between self-improvement and adjacent features."""
import json
from pathlib import Path

import yaml

from tools.self_improvement.effect_measurement import EffectMeasurement


def foundation_reference_contract() -> dict:
  return {
    "discipline_check_schema": "foundation",
    "review_mode_vocabulary": "foundation",
    "state_axis_vocabulary": "foundation",
    "policy": "reference_only_no_redefinition",
  }


def assert_commit_fields_are_independent(
  *,
  target_commit: str,
  materialization_commit_hash: str,
) -> dict:
  return {
    "target_commit_owner": "conformance-evaluation",
    "materialization_commit_hash_owner": "self-improvement",
    "independent": target_commit != materialization_commit_hash,
  }


class InterfaceAdapter:
  def __init__(self, root: Path):
    self.root = Path(root)

  @staticmethod
  def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

  def read_evaluation_role_diff_report(self, report_path: Path) -> dict:
    return json.loads(Path(report_path).read_text(encoding="utf-8"))

  def write_analysis_metrics(self, *, metric_date: str) -> Path:
    return EffectMeasurement(self.root).write_metrics(metric_date=metric_date)

  def workflow_management_input_contract(self, proposal_path: Path) -> dict:
    proposal_path = Path(proposal_path)
    proposal = yaml.safe_load(proposal_path.read_text(encoding="utf-8")) or {}
    target = (
      self.root
      / "learning"
      / "workflow"
      / "approved-updates"
      / proposal_path.name
    )
    return {
      "proposal_id": proposal["proposal_id"],
      "approved_state_owner": "self-improvement",
      "materialization_owner": "workflow-management",
      "source_path": self._relative(proposal_path),
      "approved_updates_path": self._relative(target),
      "move_operation": "git_mv_required",
      "approved_means": "self_improvement_approval_time",
      "materialized_at_means": "workflow_management_completion_time",
    }

  def _relative(self, path: Path) -> str:
    return str(path.relative_to(self.root))

```

## FILE: tools/self_improvement/traceability.py

```text
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


EXPECTED_TASK_TESTS = {
  "T-001": "tests/self-improvement/test_t001_layout.py",
  "T-002": "tests/self-improvement/test_t002_input_model.py",
  "T-003": "tests/self-improvement/test_t003_signal_extraction.py",
  "T-004": "tests/self-improvement/test_t004_proposal_model.py",
  "T-005": "tests/self-improvement/test_t005_verification_model.py",
  "T-006": "tests/self-improvement/test_t006_approval_model.py",
  "T-007": "tests/self-improvement/test_t007_rollback_model.py",
  "T-008": "tests/self-improvement/test_t008_effect_measurement.py",
  "T-009": "tests/self-improvement/test_t009_machine_verification.py",
  "T-010": "tests/self-improvement/test_t010_interfaces.py",
  "T-011": "tests/self-improvement/test_t011_traceability.py",
}


EXPECTED_MODEL_NAMES = {
  "入力モデル",
  "signal_extraction モデル",
  "提案モデル",
  "検証モデル",
  "承認モデル",
  "履歴ロールバック",
  "効果測定",
}


@dataclass(frozen=True)
class TraceabilityAudit:
  project_root: Path

  @property
  def design_path(self) -> Path:
    return self.project_root / ".reviewcompass/specs/self-improvement/design.md"

  @property
  def tasks_path(self) -> Path:
    return self.project_root / ".reviewcompass/specs/self-improvement/tasks.md"

  def missing_task_tests(self) -> list[str]:
    missing = []
    for task_id, path in EXPECTED_TASK_TESTS.items():
      if not (self.project_root / path).is_file():
        missing.append(task_id)
    return missing

  def model_level_coverage(self) -> dict[str, set[str]]:
    coverage: dict[str, set[str]] = {}
    for row in self._markdown_rows(self.design_path.read_text(), "### 18.1", "### 18.2"):
      cells = self._cells(row)
      if len(cells) != 4:
        continue
      model = re.sub(r"（§\d+）", "", cells[0].replace("**", "")).strip()
      if model in EXPECTED_MODEL_NAMES:
        levels = set()
        if cells[1]:
          levels.add("unit")
        if cells[2]:
          levels.add("integration")
        if cells[3]:
          levels.add("acceptance")
        coverage[model] = levels
    return coverage

  def requirements_traceability_issues(self) -> list[str]:
    text = self.tasks_path.read_text()
    issues: list[str] = []
    referenced_tasks: set[str] = set()

    for row in self._markdown_rows(text, "## 要件追跡", "## テスト戦略"):
      cells = self._cells(row)
      if len(cells) != 2 or not cells[0].startswith("Requirement"):
        continue
      tasks = self._expand_task_ids(cells[1])
      if not tasks:
        issues.append(f"{cells[0]} has no task reference")
      unknown = tasks - set(EXPECTED_TASK_TESTS)
      for task_id in sorted(unknown):
        issues.append(f"{cells[0]} references unknown {task_id}")
      referenced_tasks.update(tasks)

    missing_from_table = set(EXPECTED_TASK_TESTS) - referenced_tasks
    for task_id in sorted(missing_from_table):
      issues.append(f"{task_id} is not referenced by requirements traceability")
    return issues

  def dvt_gate_issues(self) -> list[str]:
    issues: list[str] = []
    for row in self._markdown_rows(self.tasks_path.read_text(), "## 遅延確認事項", "## 機能横断"):
      cells = self._cells(row)
      if not cells or not cells[0].startswith("DVT-"):
        continue
      status = cells[-1]
      if "未解除" in status and "延期" not in status and "フェーズ" not in status:
        issues.append(f"{cells[0]} is unresolved without deferral reason")
    return issues

  def key_regression_coverage(self) -> dict[str, bool]:
    files = {
      "proposal": self._read("tests/self-improvement/test_t004_proposal_model.py"),
      "approval": self._read("tests/self-improvement/test_t006_approval_model.py"),
      "rollback": self._read("tests/self-improvement/test_t007_rollback_model.py"),
      "effect": self._read("tests/self-improvement/test_t008_effect_measurement.py"),
      "machine": self._read("tests/self-improvement/test_t009_machine_verification.py"),
      "interfaces": self._read("tests/self-improvement/test_t010_interfaces.py"),
      "schema": self._read("learning/workflow/schemas/proposal.schema.json"),
    }
    return {
      "proposal_schema_validity": (
        "proposal_schema_documents_owned_constraints" in files["proposal"]
        and "$schema" in files["schema"]
        and "proposal_type" in files["schema"]
      ),
      "foundation_vocab_reference_only": "foundation" in files["interfaces"] and "redefinition" in files["interfaces"],
      "superseded_reopen_five_steps": all(
        token in files["approval"] or token in files["machine"]
        for token in ["superseded_by", "superseded_at", "reopen_reason", "five"]
      ),
      "effect_metrics": "adoption_rate" in files["effect"] and "rollback_rate" in files["effect"],
      "rollback_integrity": "restore" in files["rollback"] and "archive" in files["rollback"],
      "workflow_materialized_at_sync": "materialized_at" in files["interfaces"],
    }

  def _read(self, relative_path: str) -> str:
    path = self.project_root / relative_path
    if not path.is_file():
      return ""
    return path.read_text()

  @staticmethod
  def _markdown_rows(text: str, start_heading: str, end_heading: str) -> list[str]:
    in_section = False
    rows = []
    for line in text.splitlines():
      if line.startswith(start_heading):
        in_section = True
        continue
      if in_section and line.startswith(end_heading):
        break
      if in_section and line.startswith("|") and "---" not in line:
        rows.append(line)
    return rows

  @staticmethod
  def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]

  @staticmethod
  def _expand_task_ids(text: str) -> set[str]:
    task_ids = set(re.findall(r"T-\d{3}", text))
    for start, end in re.findall(r"T-(\d{3})〜T-(\d{3})", text):
      for number in range(int(start), int(end) + 1):
        task_ids.add(f"T-{number:03d}")
    if "全タスク" in text:
      task_ids.update(EXPECTED_TASK_TESTS)
    return task_ids

```

## FILE: tools/self_improvement/schemas/provenance.schema.json

```text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewcompass.local/schemas/self-improvement/provenance.schema.json",
  "title": "Self Improvement Provenance",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "source",
    "location",
    "observation"
  ],
  "properties": {
    "source": {
      "type": "string",
      "enum": [
        "review_record",
        "compliance_report",
        "user_audit",
        "observation_pattern"
      ]
    },
    "location": {
      "type": "string",
      "minLength": 1
    },
    "observation": {
      "type": "string",
      "minLength": 30
    }
  }
}

```

## FILE: tools/self_improvement/schemas/signal.schema.json

```text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewcompass.local/schemas/self-improvement/signal.schema.json",
  "title": "Self Improvement Signal",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "signal_id",
    "signal_type",
    "observed_pattern",
    "related_disciplines",
    "proposed_proposal_type",
    "motivating_evidence_seed"
  ],
  "required_for_obsolete_or_conflict": [
    "related_disciplines"
  ],
  "properties": {
    "signal_id": {
      "type": "string",
      "pattern": "^SE-[0-9]{3,}$"
    },
    "signal_type": {
      "type": "string",
      "enum": [
        "discipline_absence",
        "discipline_violation",
        "discipline_obsolete",
        "discipline_conflict"
      ]
    },
    "observed_pattern": {
      "type": "string",
      "minLength": 1
    },
    "related_disciplines": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "proposed_proposal_type": {
      "type": "string",
      "enum": [
        "new_discipline",
        "update",
        "archive",
        "consolidation"
      ]
    },
    "motivating_evidence_seed": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  }
}

```

## FILE: learning/workflow/schemas/proposal.schema.json

```text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewcompass.local/schemas/self-improvement/proposal.schema.json",
  "title": "Self Improvement Workflow Proposal",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "proposal_id",
    "proposal_type",
    "target_discipline_path",
    "motivating_evidence",
    "proposed_change",
    "expected_effect",
    "status"
  ],
  "properties": {
    "proposal_id": {
      "type": "string",
      "pattern": "^(WP|RB)-[0-9]{3,}$"
    },
    "proposal_type": {
      "type": "string",
      "enum": [
        "new_discipline",
        "update",
        "status_change",
        "archive",
        "consolidation"
      ]
    },
    "target_discipline_path": {
      "type": "string",
      "pattern": "^docs/disciplines/discipline_.*\\.md$"
    },
    "source_discipline_paths": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^docs/disciplines/discipline_.*\\.md$"
      }
    },
    "motivating_evidence": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "source",
          "location",
          "observation"
        ],
        "properties": {
          "source": {
            "type": "string"
          },
          "location": {
            "type": "string"
          },
          "observation": {
            "type": "string"
          }
        }
      }
    },
    "proposed_change": {
      "type": "object"
    },
    "expected_effect": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "pending",
        "approved",
        "rejected",
        "superseded"
      ]
    },
    "statistical_evidence": {
      "type": "object"
    },
    "depends_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "superseded_by": {
      "type": "string"
    },
    "superseded_at": {
      "type": "string"
    },
    "reopen_reason": {
      "type": "string"
    },
    "materialized_at": {
      "type": "string"
    },
    "materialization_commit_hash": {
      "type": [
        "string",
        "null"
      ]
    }
  }
}

```

## FILE: learning/workflow/schemas/rollback.schema.json

```text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewcompass.local/schemas/self-improvement/rollback.schema.json",
  "title": "Self Improvement Rollback Record",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "rollback_id",
    "target_proposal_id",
    "rollback_method",
    "rollback_reason",
    "rollback_date",
    "related_artifacts"
  ],
  "properties": {
    "rollback_id": {
      "type": "string",
      "pattern": "^RB-[0-9]{3,}$"
    },
    "target_proposal_id": {
      "type": "string",
      "pattern": "^WP-[0-9]{3,}$"
    },
    "rollback_method": {
      "type": "string",
      "enum": [
        "archive_restoration",
        "status_downgrade",
        "git_revert"
      ]
    },
    "rollback_reason": {
      "type": "string",
      "minLength": 1
    },
    "rollback_date": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "related_artifacts": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}

```

## FILE: learning/workflow/schemas/metrics.schema.json

```text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewcompass.local/schemas/self-improvement/metrics.schema.json",
  "title": "Self Improvement Workflow Metrics",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "metric_date",
    "discipline_compliance_rate",
    "promotion_count",
    "archive_count",
    "proposal_counts_by_type",
    "adoption_rate",
    "rollback_rate",
    "average_days_to_adoption",
    "manual_aggregation_steps"
  ],
  "properties": {
    "metric_date": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "discipline_compliance_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "promotion_count": {
      "type": "integer",
      "minimum": 0
    },
    "archive_count": {
      "type": "integer",
      "minimum": 0
    },
    "proposal_counts_by_type": {
      "type": "object"
    },
    "adoption_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "rollback_rate": {
      "type": "number",
      "minimum": 0
    },
    "average_days_to_adoption": {
      "type": "number",
      "minimum": 0
    },
    "manual_aggregation_steps": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}

```

## FILE: learning/workflow/proposals/README.md

```text
# learning/workflow/proposals

`self-improvement` の `status: pending` 提案 YAML を置く場所。

ここに置かれる提案は、規律ファイルを直接変更するものではなく、workflow-management の手続きへ渡す前の候補である。

```

## FILE: learning/workflow/approved-updates/README.md

```text
# learning/workflow/approved-updates

`self-improvement` の `status: approved` または `status: superseded` 提案 YAML を置く場所。

承認済み提案は workflow-management の手続き入力であり、`docs/disciplines/` の実体変更は workflow-management 側で実行する。

`pending` 提案を採用した場合、self-improvement は提案 YAML を `git mv` で `learning/workflow/proposals/` からこのディレクトリへ移す。`approved` は self-improvement による承認時点を表し、`materialized_at` と `materialization_commit_hash` は workflow-management が実体変更を完了した時点で追記する。

```

## FILE: learning/workflow/rejected-updates/README.md

```text
# learning/workflow/rejected-updates

`self-improvement` の `status: rejected` 提案 YAML を置く場所。

却下理由を保持し、同じ規律変更案を後で再評価するときの参照証跡にする。

```

## FILE: learning/workflow/rollback/README.md

```text
# learning/workflow/rollback

`self-improvement` のロールバック履歴 YAML を置く場所。

`rollback_id`、対象提案、ロールバック方法、理由、関連成果物を記録し、提案から承認、取り消しまで追跡できるようにする。

```

## FILE: learning/workflow/metrics/README.md

```text
# learning/workflow/metrics

`self-improvement` の効果測定 7 指標を時系列 YAML として置く場所。

analysis 機能が読み取れる機械可読形式で、規律遵守率、昇格件数、退避件数、提案件数、採用率、ロールバック率、提案から採用までの平均日数を記録する。

```

## FILE: learning/workflow/schemas/README.md

```text
# learning/workflow/schemas

`self-improvement` の永続データ正本スキーマを置く場所。

proposal、rollback、metrics など、他機能も参照する保存データのスキーマをここに分離し、データ YAML と混在させない。

```

## FILE: learning/findings/README.md

```text
# learning/findings

第 1 期空置き、所有権はフェーズ 4 完了後に確定。

他 4 層改善で活用予定の findings 置き場であり、workflow 層 self-improvement の第 1 期出力先ではない。

```

## FILE: learning/backtests/README.md

```text
# learning/backtests

第 1 期空置き、所有権はフェーズ 4 完了後に確定。

他 4 層改善で活用予定の backtests 置き場であり、workflow 層 self-improvement の第 1 期では使用しない。

```

## FILE: learning/templates/README.md

```text
# learning/templates

第 1 期空置き、所有権はフェーズ 4 完了後に確定。

他 4 層改善で活用予定の templates 置き場であり、workflow 層 self-improvement の第 1 期では使用しない。

```

## FILE: tests/self-improvement/test_t001_layout.py

```text
"""self-improvement T-001 成果物配置のテスト。"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


WORKFLOW_DIRS = [
  "learning/workflow/proposals",
  "learning/workflow/approved-updates",
  "learning/workflow/rejected-updates",
  "learning/workflow/rollback",
  "learning/workflow/metrics",
  "learning/workflow/schemas",
]

FUTURE_LAYER_DIRS = [
  "learning/findings",
  "learning/backtests",
  "learning/templates",
]


def _read(path):
  return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_t001_workflow_directories_have_readme_and_gitkeep():
  """learning/workflow 配下 6 ディレクトリは README と .gitkeep を持つ。"""
  for relpath in WORKFLOW_DIRS:
    directory = REPO_ROOT / relpath
    assert directory.is_dir(), relpath
    assert (directory / ".gitkeep").is_file(), relpath
    readme = directory / "README.md"
    assert readme.is_file(), relpath
    text = readme.read_text(encoding="utf-8")
    assert relpath in text
    assert "self-improvement" in text


def test_t001_future_layer_directories_are_marked_as_phase1_empty():
  """他 4 層用の空置き 3 ディレクトリは第 1 期空置き注記を持つ。"""
  required = "第 1 期空置き、所有権はフェーズ 4 完了後に確定"
  for relpath in FUTURE_LAYER_DIRS:
    directory = REPO_ROOT / relpath
    assert directory.is_dir(), relpath
    assert (directory / ".gitkeep").is_file(), relpath
    text = (directory / "README.md").read_text(encoding="utf-8")
    assert required in text


def test_t001_related_directories_have_readmes():
  """関連ディレクトリは配置目的 README を持つ。"""
  compliance = _read("docs/discipline-compliance-reports/README.md")
  archive = _read("docs/disciplines/archive/README.md")
  assert "docs/discipline-compliance-reports/" in compliance
  assert "遵守検査" in compliance
  assert "docs/disciplines/archive/" in archive
  assert "撤廃" in archive


def test_t001_tools_namespace_and_naming_policy_are_present():
  """tools 配下の self-improvement namespace と命名規約が存在する。"""
  schemas_dir = REPO_ROOT / "tools" / "self_improvement" / "schemas"
  assert schemas_dir.is_dir()
  assert (schemas_dir / ".gitkeep").is_file()
  text = _read("tools/README.md")
  assert "tools/self_improvement/" in text
  assert "tools/self-improvement-check.py" in text
  assert "パッケージ／モジュールはアンダースコア" in text
  assert "単独実行 CLI スクリプトはハイフン" in text


def test_t001_tests_directory_is_tracked():
  """tests/self-improvement は .gitkeep で追跡可能にする。"""
  tests_dir = REPO_ROOT / "tests" / "self-improvement"
  assert tests_dir.is_dir()
  assert (tests_dir / ".gitkeep").is_file()

```

## FILE: tests/self-improvement/test_t002_input_model.py

```text
"""T-002 のテスト：入力モデルと来歴情報。

対応タスク：self-improvement tasks.md T-002
対応設計節：design.md §6.1〜§6.4
対応要件：Requirement 2 受入 1〜4
"""
import json

import pytest
import yaml

from tools.self_improvement.input_model import (
  InputModel,
  ProvenanceError,
  build_provenance,
)


LONG_OBSERVATION = "規律違反の観察内容が十分な長さで記録され、原因と場面を後から追跡できる"


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t002_builds_provenance_with_required_three_fields():
  provenance = build_provenance(
    source="review_record",
    location="reviews/2026-06-04-review.yaml",
    observation=LONG_OBSERVATION,
  )

  assert provenance == {
    "source": "review_record",
    "location": "reviews/2026-06-04-review.yaml",
    "observation": LONG_OBSERVATION,
  }


def test_t002_rejects_unknown_source_fail_closed():
  with pytest.raises(ProvenanceError, match="unknown_source"):
    build_provenance(
      source="runtime_report",
      location="reports/runtime.yaml",
      observation=LONG_OBSERVATION,
    )


def test_t002_rejects_short_observation_fail_closed():
  with pytest.raises(ProvenanceError, match="short_observation"):
    build_provenance(
      source="user_audit",
      location="audits/user.md",
      observation="短すぎる観察",
    )


def test_t002_loads_all_five_input_sources_with_provenance(tmp_path):
  _write_yaml(
    tmp_path / "reviews" / "review.yaml",
    {"records": [{"location": "reviews/review.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-03.yaml",
    {"records": [{"location": "docs/discipline-compliance-reports/2026-06-03.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "audits" / "user.yaml",
    {"records": [{"location": "audits/user.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "observations" / "pattern.yaml",
    {"records": [{"location": "observations/pattern.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04.yaml",
    {"records": [{"location": "docs/discipline-compliance-reports/2026-06-04.yaml", "observation": LONG_OBSERVATION}]},
  )

  records = InputModel(tmp_path).load_sources(
    review_records=[tmp_path / "reviews" / "review.yaml"],
    compliance_reports_dir=tmp_path / "docs" / "discipline-compliance-reports",
    user_audits=[tmp_path / "audits" / "user.yaml"],
    observation_patterns=[tmp_path / "observations" / "pattern.yaml"],
  )

  sources = [record.provenance["source"] for record in records]
  assert sources.count("review_record") == 1
  assert sources.count("compliance_report") == 2
  assert sources.count("user_audit") == 1
  assert sources.count("observation_pattern") == 1
  assert all(set(record.provenance) == {"source", "location", "observation"} for record in records)


def test_t002_compliance_reports_are_loaded_in_timeline_order(tmp_path):
  reports_dir = tmp_path / "docs" / "discipline-compliance-reports"
  _write_yaml(
    reports_dir / "2026-06-04.yaml",
    {"records": [{"location": "late.yaml", "observation": LONG_OBSERVATION}]},
  )
  _write_yaml(
    reports_dir / "2026-06-03.yaml",
    {"records": [{"location": "early.yaml", "observation": LONG_OBSERVATION}]},
  )

  records = InputModel(tmp_path).load_compliance_reports(reports_dir)

  assert [record.provenance["location"] for record in records] == ["early.yaml", "late.yaml"]


def test_t002_provenance_schema_documents_owned_constraints():
  schema = json.loads(
    (InputModel.project_root() / "tools" / "self_improvement" / "schemas" / "provenance.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["source"]["enum"] == [
    "review_record",
    "compliance_report",
    "user_audit",
    "observation_pattern",
  ]
  assert schema["properties"]["observation"]["minLength"] == 30
  assert schema["required"] == ["source", "location", "observation"]

```

## FILE: tests/self-improvement/test_t003_signal_extraction.py

```text
"""T-003 のテスト：signal_extraction モデル。

対応タスク：self-improvement tasks.md T-003
対応設計節：design.md §7.1〜§7.4
対応要件：Requirement 2 受入 3、Requirement 3 受入 1
"""
import json

import pytest

from tools.self_improvement.signal_extraction import (
  SignalError,
  SignalExtractor,
  build_signal,
)


EVIDENCE = [
  {
    "source": "review_record",
    "location": "reviews/2026-06-04.yaml",
    "observation": "規律と実体の乖離が複数回観察され、提案候補の根拠として十分である",
  }
]


def test_t003_classifies_four_signal_types():
  extractor = SignalExtractor()

  signals = extractor.extract([
    {
      "signal_id": "SE-001",
      "observed_pattern": "実体運用に定常的パターンがあるが対応規律がない",
      "matching_discipline": None,
      "evidence_count": 1,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-002",
      "observed_pattern": "同じ規律違反が閾値以上に累積している",
      "matching_discipline": "docs/disciplines/discipline_options.md",
      "evidence_count": 3,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-003",
      "observed_pattern": "規律はあるが長期間参照されていない",
      "matching_discipline": "docs/disciplines/discipline_old.md",
      "related_disciplines": ["docs/disciplines/discipline_old.md"],
      "sessions_without_reference": 5,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-004",
      "observed_pattern": "複数規律が同じ場面に衝突して適用される",
      "conflicting_disciplines": [
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
      "motivating_evidence_seed": EVIDENCE,
    },
  ])

  assert [signal["signal_type"] for signal in signals] == [
    "discipline_absence",
    "discipline_violation",
    "discipline_obsolete",
    "discipline_conflict",
  ]
  assert [signal["proposed_proposal_type"] for signal in signals] == [
    "new_discipline",
    "update",
    "archive",
    "consolidation",
  ]


def test_t003_respects_violation_and_obsolete_thresholds():
  extractor = SignalExtractor(violation_threshold=3, obsolete_sessions_threshold=5)

  signals = extractor.extract([
    {
      "signal_id": "SE-001",
      "observed_pattern": "違反がまだ閾値未満であり提案候補にしない",
      "matching_discipline": "docs/disciplines/discipline_options.md",
      "evidence_count": 2,
      "motivating_evidence_seed": EVIDENCE,
    },
    {
      "signal_id": "SE-002",
      "observed_pattern": "参照なし期間がまだ閾値未満であり提案候補にしない",
      "matching_discipline": "docs/disciplines/discipline_old.md",
      "related_disciplines": ["docs/disciplines/discipline_old.md"],
      "sessions_without_reference": 4,
      "motivating_evidence_seed": EVIDENCE,
    },
  ])

  assert signals == []


def test_t003_requires_related_disciplines_for_obsolete_and_conflict():
  with pytest.raises(SignalError, match="missing_related_disciplines"):
    build_signal(
      signal_id="SE-001",
      signal_type="discipline_conflict",
      observed_pattern="衝突型には関連規律が必要で、空配列なら遮断する",
      related_disciplines=[],
      motivating_evidence_seed=EVIDENCE,
    )


def test_t003_rejects_unknown_signal_type_fail_closed():
  with pytest.raises(SignalError, match="unknown_signal_type"):
    build_signal(
      signal_id="SE-001",
      signal_type="runtime_issue",
      observed_pattern="未知の signal_type は fail-closed として処理を止める",
      related_disciplines=[],
      motivating_evidence_seed=EVIDENCE,
    )


def test_t003_signal_schema_documents_owned_constraints():
  schema = json.loads(
    (SignalExtractor.project_root() / "tools" / "self_improvement" / "schemas" / "signal.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["signal_type"]["enum"] == [
    "discipline_absence",
    "discipline_violation",
    "discipline_obsolete",
    "discipline_conflict",
  ]
  assert "related_disciplines" in schema["required_for_obsolete_or_conflict"]

```

## FILE: tests/self-improvement/test_t004_proposal_model.py

```text
"""T-004 のテスト：提案モデル。

対応タスク：self-improvement tasks.md T-004
対応設計節：design.md §8.1〜§8.9
対応要件：Requirement 3 受入 1〜5、Requirement 4 受入 1〜5
"""
import json

import pytest
import yaml

from tools.self_improvement.proposal_model import (
  ProposalError,
  ProposalModel,
  validate_proposal,
)


EVIDENCE = [
  {
    "source": "review_record",
    "location": "reviews/2026-06-04.yaml",
    "observation": "提案の根拠として十分な長さの観察記録があり、後から追跡できる",
  }
]


BASE_SIGNAL = {
  "signal_id": "SE-001",
  "signal_type": "discipline_absence",
  "observed_pattern": "実体運用に定常的なパターンがある",
  "related_disciplines": [],
  "motivating_evidence_seed": EVIDENCE,
}


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t004_generates_all_five_proposal_types(tmp_path):
  model = ProposalModel(tmp_path)

  proposals = [
    model.create_proposal(
      proposal_type="new_discipline",
      target_discipline_path="docs/disciplines/discipline_new.md",
      signal=BASE_SIGNAL,
      proposed_change={"draft_discipline": "新規規律本文", "relationship_notes": "既存規律との関係"},
      expected_effect="規律不在を解消する",
    ),
    model.create_proposal(
      proposal_type="update",
      target_discipline_path="docs/disciplines/discipline_update.md",
      signal=BASE_SIGNAL,
      proposed_change={"change_diff": "- old\n+ new"},
      expected_effect="既存規律を実体に合わせる",
    ),
    model.create_proposal(
      proposal_type="status_change",
      target_discipline_path="docs/disciplines/discipline_status.md",
      signal=BASE_SIGNAL,
      proposed_change={"from": "aspirational", "to": "enforced"},
      expected_effect="正式化判断を記録する",
      statistical_evidence={"compliance_rate": 0.9},
    ),
    model.create_proposal(
      proposal_type="archive",
      target_discipline_path="docs/disciplines/discipline_old.md",
      signal=BASE_SIGNAL,
      proposed_change={"archive_readme_path": "docs/disciplines/archive/README.md"},
      expected_effect="撤廃済み規律を分離する",
    ),
    model.create_proposal(
      proposal_type="consolidation",
      target_discipline_path="docs/disciplines/discipline_merged.md",
      signal=BASE_SIGNAL,
      proposed_change={"mapping_table": "old -> merged"},
      expected_effect="重複規律を統合する",
      source_discipline_paths=[
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
    ),
  ]

  assert [proposal["proposal_type"] for proposal in proposals] == [
    "new_discipline",
    "update",
    "status_change",
    "archive",
    "consolidation",
  ]
  assert all(proposal["status"] == "pending" for proposal in proposals)
  assert all(proposal["proposal_id"].startswith("WP-") for proposal in proposals)


def test_t004_rejects_unknown_proposal_type_fail_closed(tmp_path):
  model = ProposalModel(tmp_path)

  with pytest.raises(ProposalError, match="unknown_proposal_type"):
    model.create_proposal(
      proposal_type="runtime_prompt",
      target_discipline_path="docs/disciplines/discipline_prompt.md",
      signal=BASE_SIGNAL,
      proposed_change={},
      expected_effect="範囲外の変更",
    )


def test_t004_validates_required_fields_and_target_pattern():
  proposal = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "runtime/prompts/main.md",
    "motivating_evidence": EVIDENCE,
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "改善する",
    "status": "pending",
  }

  with pytest.raises(ProposalError, match="invalid_target_discipline_path"):
    validate_proposal(proposal)

  del proposal["expected_effect"]
  with pytest.raises(ProposalError, match="missing_required_fields"):
    validate_proposal(proposal)


def test_t004_requires_motivating_evidence_three_fields():
  proposal = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": [{"source": "review_record", "location": "reviews/x.yaml"}],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "改善する",
    "status": "pending",
  }

  with pytest.raises(ProposalError, match="invalid_motivating_evidence"):
    validate_proposal(proposal)


def test_t004_allocates_next_id_across_four_workflow_directories(tmp_path):
  for directory, proposal_id in [
    ("proposals", "WP-001"),
    ("approved-updates", "WP-099"),
    ("rejected-updates", "WP-100"),
    ("rollback", "RB-002"),
  ]:
    _write_yaml(
      tmp_path / "learning" / "workflow" / directory / f"{proposal_id}.yaml",
      {"proposal_id": proposal_id},
    )

  assert ProposalModel(tmp_path).next_proposal_id("WP") == "WP-101"
  assert ProposalModel(tmp_path).next_proposal_id("RB") == "RB-003"


def test_t004_extends_id_width_after_999(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-999.yaml",
    {"proposal_id": "WP-999"},
  )

  assert ProposalModel(tmp_path).next_proposal_id("WP") == "WP-1000"


def test_t004_enforces_type_specific_requirements(tmp_path):
  model = ProposalModel(tmp_path)

  with pytest.raises(ProposalError, match="missing_change_diff"):
    model.create_proposal(
      proposal_type="update",
      target_discipline_path="docs/disciplines/discipline_update.md",
      signal=BASE_SIGNAL,
      proposed_change={},
      expected_effect="改善する",
    )
  with pytest.raises(ProposalError, match="missing_source_discipline_paths"):
    model.create_proposal(
      proposal_type="consolidation",
      target_discipline_path="docs/disciplines/discipline_merged.md",
      signal=BASE_SIGNAL,
      proposed_change={"mapping_table": "old -> merged"},
      expected_effect="統合する",
    )


def test_t004_proposal_schema_documents_owned_constraints():
  schema = json.loads(
    (ProposalModel.project_root() / "learning" / "workflow" / "schemas" / "proposal.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["proposal_type"]["enum"] == [
    "new_discipline",
    "update",
    "status_change",
    "archive",
    "consolidation",
  ]
  assert schema["properties"]["status"]["enum"] == [
    "pending",
    "approved",
    "rejected",
    "superseded",
  ]
  assert schema["properties"]["target_discipline_path"]["pattern"] == "^docs/disciplines/discipline_.*\\.md$"
  assert schema["required"] == [
    "proposal_id",
    "proposal_type",
    "target_discipline_path",
    "motivating_evidence",
    "proposed_change",
    "expected_effect",
    "status",
  ]

```

## FILE: tests/self-improvement/test_t005_verification_model.py

```text
"""T-005 のテスト：検証モデル。

対応タスク：self-improvement tasks.md T-005
対応設計節：design.md §9.1〜§9.5
対応要件：Requirement 5 受入 1〜4
"""
from tools.self_improvement.impact_analysis import ImpactAnalyzer
from tools.self_improvement.verification_model import VerificationModel


def test_t005_retrospective_simulation_records_scope_and_violation_rate():
  proposal = {"proposal_id": "WP-001", "statistical_evidence": {}}
  records = [
    {"record_id": "r1", "violates": True},
    {"record_id": "r2", "violates": False},
    {"record_id": "r3", "violates": True},
    {"record_id": "r4", "violates": False},
  ]

  result = VerificationModel().run_retrospective_simulation(
    proposal,
    target_scope="past reviews: 4 records",
    records=records,
  )

  assert result["method"] == "retrospective_simulation"
  assert result["target_scope"] == "past reviews: 4 records"
  assert result["target_count"] == 4
  assert result["violation_count"] == 2
  assert result["violation_rate"] == 0.5
  assert proposal["statistical_evidence"]["retrospective_simulation"] == result


def test_t005_pilot_operation_threshold_89_90_91_percent():
  model = VerificationModel()

  assert model.evaluate_pilot_operation([0.89])["promotion_decision"] == "not_ready"
  assert model.evaluate_pilot_operation([0.90])["promotion_decision"] == "enforce"
  assert model.evaluate_pilot_operation([0.91])["promotion_decision"] == "enforce"


def test_t005_pilot_operation_preserves_time_series():
  result = VerificationModel().evaluate_pilot_operation(
    [
      {"session": "s1", "compliance_rate": 0.88},
      {"session": "s2", "compliance_rate": 0.92},
    ],
    period="2 sessions",
  )

  assert result["method"] == "pilot_operation"
  assert result["period"] == "2 sessions"
  assert result["threshold"] == 0.9
  assert result["compliance_series"] == [
    {"session": "s1", "compliance_rate": 0.88},
    {"session": "s2", "compliance_rate": 0.92},
  ]
  assert result["final_compliance_rate"] == 0.92


def test_t005_impact_analysis_detects_internal_links(tmp_path):
  discipline = tmp_path / "docs" / "disciplines" / "discipline_a.md"
  discipline.parent.mkdir(parents=True)
  discipline.write_text(
    "# A\n\n関連：[[discipline_b]] と [[discipline_c]]\n",
    encoding="utf-8",
  )

  result = ImpactAnalyzer(tmp_path).detect_internal_links()

  assert result == [
    {
      "path": "docs/disciplines/discipline_a.md",
      "links": ["discipline_b", "discipline_c"],
    }
  ]


def test_t005_impact_analysis_classifies_three_conflict_definitions(tmp_path):
  discipline_a = tmp_path / "docs" / "disciplines" / "discipline_a.md"
  discipline_b = tmp_path / "docs" / "disciplines" / "discipline_b.md"
  discipline_a.parent.mkdir(parents=True)
  discipline_a.write_text(
    "---\nname: shared-name\napplies_to: review\n---\n[[discipline_b]]\n同じ場面の規律\n",
    encoding="utf-8",
  )
  discipline_b.write_text(
    "---\nname: shared-name\napplies_to: review\n---\n[[discipline_a]]\n異なる文言の規律\n",
    encoding="utf-8",
  )

  conflicts = ImpactAnalyzer(tmp_path).analyze_conflicts()

  assert conflicts["name_duplicates"] == [
    {
      "name": "shared-name",
      "paths": [
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
    }
  ]
  assert conflicts["content_overlaps"] == [
    {
      "applies_to": "review",
      "paths": [
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
    }
  ]
  assert conflicts["reference_cycles"] == [
    {
      "paths": [
        "docs/disciplines/discipline_a.md",
        "docs/disciplines/discipline_b.md",
      ],
    }
  ]


def test_t005_unverifiable_proposal_requires_user_audit():
  result = VerificationModel().mark_unverifiable(
    proposal_id="WP-999",
    reason="3 つの検証手段がいずれも機能しない提案",
  )

  assert result == {
    "proposal_id": "WP-999",
    "verification_status": "user_audit_required",
    "auto_approval": False,
    "reason": "3 つの検証手段がいずれも機能しない提案",
  }

```

## FILE: tests/self-improvement/test_t006_approval_model.py

```text
"""T-006 のテスト：承認モデル。

対応タスク：self-improvement tasks.md T-006
対応設計節：design.md §10.1〜§10.5
対応要件：Requirement 6 受入 1〜5
"""
from pathlib import Path

import pytest
import yaml

from tools.self_improvement.approval_model import ApprovalError, ApprovalModel


def _write_proposal(path, proposal):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_yaml(path):
  return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _base_proposal(proposal_id="WP-001", status="pending"):
  return {
    "proposal_id": proposal_id,
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": [
      {
        "source": "review_record",
        "location": "reviews/2026-06-04.yaml",
        "observation": "承認モデルの状態遷移を検証するための十分な長さの観察記録",
      }
    ],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "規律を更新する",
    "status": status,
  }


def test_t006_approves_pending_proposal_with_explicit_user_approval(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-001.yaml"
  _write_proposal(source, _base_proposal())

  result = ApprovalModel(tmp_path).approve(source, approval_text="承認します")

  target = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  assert result == {
    "proposal_id": "WP-001",
    "from_status": "pending",
    "to_status": "approved",
    "source_path": "learning/workflow/proposals/WP-001.yaml",
    "target_path": "learning/workflow/approved-updates/WP-001.yaml",
    "move_operation": "git_mv_required",
  }
  assert not source.exists()
  assert _read_yaml(target)["status"] == "approved"


def test_t006_rejects_pending_proposal_with_explicit_user_rejection(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-002.yaml"
  _write_proposal(source, _base_proposal("WP-002"))

  result = ApprovalModel(tmp_path).reject(source, approval_text="却下します")

  target = tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-002.yaml"
  assert result["to_status"] == "rejected"
  assert result["target_path"] == "learning/workflow/rejected-updates/WP-002.yaml"
  assert _read_yaml(target)["status"] == "rejected"


def test_t006_blocks_status_change_to_enforced_without_explicit_approval(tmp_path):
  source = tmp_path / "learning" / "workflow" / "proposals" / "WP-003.yaml"
  proposal = _base_proposal("WP-003")
  proposal["proposal_type"] = "status_change"
  proposal["proposed_change"] = {"from": "aspirational", "to": "enforced"}
  proposal["statistical_evidence"] = {"compliance_rate": 0.9}
  _write_proposal(source, proposal)

  with pytest.raises(ApprovalError, match="explicit_user_approval_required"):
    ApprovalModel(tmp_path).approve(source, approval_text="よさそう")


def test_t006_superseded_transition_requires_reopen_five_step_fields(tmp_path):
  source = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-004.yaml"
  _write_proposal(source, _base_proposal("WP-004", status="approved"))

  with pytest.raises(ApprovalError, match="missing_reopen_fields"):
    ApprovalModel(tmp_path).supersede(
      source,
      superseded_by="WP-005",
      superseded_at="2026-06-04T12:00:00+09:00",
      reopen_reason="後続提案で上書きする必要がある",
      approval_text="承認します",
      declaration=False,
      new_conclusion=True,
    )


def test_t006_superseded_transition_records_required_three_fields(tmp_path):
  source = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-004.yaml"
  _write_proposal(source, _base_proposal("WP-004", status="approved"))

  result = ApprovalModel(tmp_path).supersede(
    source,
    superseded_by="WP-005",
    superseded_at="2026-06-04T12:00:00+09:00",
    reopen_reason="後続提案で上書きする必要がある",
    approval_text="承認します",
    declaration=True,
    new_conclusion=True,
  )

  proposal = _read_yaml(source)
  assert result["to_status"] == "superseded"
  assert result["target_path"] == "learning/workflow/approved-updates/WP-004.yaml"
  assert proposal["status"] == "superseded"
  assert proposal["superseded_by"] == "WP-005"
  assert proposal["superseded_at"] == "2026-06-04T12:00:00+09:00"
  assert proposal["reopen_reason"] == "後続提案で上書きする必要がある"


def test_t006_rejects_invalid_state_transition(tmp_path):
  source = tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-006.yaml"
  _write_proposal(source, _base_proposal("WP-006", status="rejected"))

  with pytest.raises(ApprovalError, match="invalid_transition"):
    ApprovalModel(tmp_path).approve(source, approval_text="承認します")

```

## FILE: tests/self-improvement/test_t007_rollback_model.py

```text
"""T-007 のテスト：履歴とロールバックモデル。

対応タスク：self-improvement tasks.md T-007
対応設計節：design.md §11.1〜§11.6
対応要件：Requirement 7 受入 1〜5
"""
import json
from pathlib import Path

import pytest
import yaml

from tools.self_improvement.rollback_model import (
  RollbackError,
  RollbackModel,
  validate_rollback_record,
)


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _read_yaml(path):
  return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_t007_creates_three_rollback_method_records(tmp_path):
  model = RollbackModel(tmp_path)

  records = [
    model.create_rollback_record(
      target_proposal_id="WP-001",
      rollback_method="archive_restoration",
      rollback_reason="archive から規律を復活する",
      rollback_date="2026-06-04",
      related_artifacts=["docs/disciplines/archive/README.md"],
    ),
    model.create_rollback_record(
      target_proposal_id="WP-002",
      rollback_method="status_downgrade",
      rollback_reason="enforced から aspirational に戻す",
      rollback_date="2026-06-04",
      related_artifacts=["learning/workflow/approved-updates/WP-002.yaml"],
    ),
    model.create_rollback_record(
      target_proposal_id="WP-003",
      rollback_method="git_revert",
      rollback_reason="規律更新 commit を取り消す",
      rollback_date="2026-06-04",
      related_artifacts=["commit:abc123"],
    ),
  ]

  assert [record["rollback_method"] for record in records] == [
    "archive_restoration",
    "status_downgrade",
    "git_revert",
  ]
  assert [record["rollback_id"] for record in records] == ["RB-001", "RB-002", "RB-003"]
  assert (tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-003.yaml").is_file()


def test_t007_rejects_unknown_rollback_method_fail_closed():
  with pytest.raises(RollbackError, match="unknown_rollback_method"):
    validate_rollback_record({
      "rollback_id": "RB-001",
      "target_proposal_id": "WP-001",
      "rollback_method": "manual_fix",
      "rollback_reason": "未知の方法",
      "rollback_date": "2026-06-04",
      "related_artifacts": [],
    })


def test_t007_next_rb_id_scans_existing_rollback_records(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-03-RB-099.yaml",
    {"rollback_id": "RB-099"},
  )

  assert RollbackModel(tmp_path).next_rollback_id() == "RB-100"


def test_t007_symlink_recreation_plan_has_five_steps(tmp_path):
  plan = RollbackModel(tmp_path).symlink_recreation_plan(
    memory_link="memory/feedback_x.md",
    repo_target="docs/disciplines/discipline_x.md",
  )

  assert [step["step"] for step in plan["steps"]] == [1, 2, 3, 4, 5]
  assert plan["memory_link"] == "memory/feedback_x.md"
  assert plan["repo_target"] == "docs/disciplines/discipline_x.md"
  assert all(step["machine_check"] for step in plan["steps"])


def test_t007_traces_proposal_approval_and_rollback_history(tmp_path):
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml",
    {"proposal_id": "WP-001", "status": "approved"},
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {
      "rollback_id": "RB-001",
      "target_proposal_id": "WP-001",
      "rollback_method": "status_downgrade",
      "rollback_reason": "戻す",
      "rollback_date": "2026-06-04",
      "related_artifacts": [],
    },
  )

  trace = RollbackModel(tmp_path).trace_history("WP-001")

  assert trace["proposal"]["path"] == "learning/workflow/approved-updates/WP-001.yaml"
  assert trace["proposal"]["status"] == "approved"
  assert trace["rollbacks"] == [
    {
      "path": "learning/workflow/rollback/2026-06-04-RB-001.yaml",
      "rollback_id": "RB-001",
      "rollback_method": "status_downgrade",
    }
  ]


def test_t007_archive_restoration_integrity_checks_and_report(tmp_path):
  restored = tmp_path / "docs" / "disciplines" / "discipline_restored.md"
  restored.parent.mkdir(parents=True)
  restored.write_text(
    "---\nname: restored\nstatus: enforced\n---\n# Restored\n[[discipline_related]]\n",
    encoding="utf-8",
  )
  archive_readme = tmp_path / "docs" / "disciplines" / "archive" / "README.md"
  archive_readme.parent.mkdir(parents=True)
  archive_readme.write_text("restored rollback approved\n", encoding="utf-8")

  result = RollbackModel(tmp_path).check_archive_restoration_integrity(
    restored_discipline_path="docs/disciplines/discipline_restored.md",
    archive_readme_path="docs/disciplines/archive/README.md",
    report_date="2026-06-04",
  )

  report = tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04-rollback.yaml"
  assert result["front_matter_valid"] is True
  assert result["internal_links"] == ["discipline_related"]
  assert result["archive_readme_consistent"] is True
  assert _read_yaml(report)["check"] == "archive_restoration_integrity"


def test_t007_rollback_schema_documents_owned_constraints():
  schema = json.loads(
    (RollbackModel.project_root() / "learning" / "workflow" / "schemas" / "rollback.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["properties"]["rollback_method"]["enum"] == [
    "archive_restoration",
    "status_downgrade",
    "git_revert",
  ]
  assert schema["required"] == [
    "rollback_id",
    "target_proposal_id",
    "rollback_method",
    "rollback_reason",
    "rollback_date",
    "related_artifacts",
  ]

```

## FILE: tests/self-improvement/test_t008_effect_measurement.py

```text
"""T-008 のテスト：効果測定モデル。

対応タスク：self-improvement tasks.md T-008
対応設計節：design.md §12.1〜§12.6
対応要件：Requirement 8 受入 1〜5
"""
import json
from pathlib import Path

import yaml

from tools.self_improvement.effect_measurement import EffectMeasurement


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _proposal(proposal_id, proposal_type, status, **extra):
  proposal = {
    "proposal_id": proposal_id,
    "proposal_type": proposal_type,
    "status": status,
  }
  proposal.update(extra)
  return proposal


def test_t008_calculates_all_seven_metrics(tmp_path):
  _write_yaml(
    tmp_path / "docs" / "discipline-compliance-reports" / "2026-06-04.yaml",
    {"checked_count": 10, "violation_count": 2},
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml",
    _proposal(
      "WP-001",
      "status_change",
      "approved",
      proposed_change={"from": "aspirational", "to": "enforced"},
      submitted_at="2026-06-01",
      approved_at="2026-06-04",
    ),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "approved-updates" / "WP-002.yaml",
    _proposal("WP-002", "archive", "superseded", submitted_at="2026-06-02", approved_at="2026-06-04"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rejected-updates" / "WP-003.yaml",
    _proposal("WP-003", "update", "rejected"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "proposals" / "WP-004.yaml",
    _proposal("WP-004", "new_discipline", "pending"),
  )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {"rollback_id": "RB-001", "target_proposal_id": "WP-001"},
  )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["metric_date"] == "2026-06-04"
  assert metrics["discipline_compliance_rate"] == 0.8
  assert metrics["promotion_count"] == 1
  assert metrics["archive_count"] == 1
  assert metrics["proposal_counts_by_type"] == {
    "archive": 1,
    "new_discipline": 1,
    "status_change": 1,
    "update": 1,
  }
  assert metrics["adoption_rate"] == 2 / 3
  assert metrics["rollback_rate"] == 1.0
  assert metrics["average_days_to_adoption"] == 2.5


def test_t008_adoption_rate_counts_superseded_as_adopted_and_excludes_pending(tmp_path):
  proposals = [
    ("approved-updates", "WP-001", "update", "approved"),
    ("approved-updates", "WP-002", "update", "superseded"),
    ("rejected-updates", "WP-003", "update", "rejected"),
    ("proposals", "WP-004", "update", "pending"),
  ]
  for directory, proposal_id, proposal_type, status in proposals:
    _write_yaml(
      tmp_path / "learning" / "workflow" / directory / f"{proposal_id}.yaml",
      _proposal(proposal_id, proposal_type, status),
    )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["adoption_rate"] == 2 / 3
  assert metrics["adoption_rate_formula"] == "(approved + superseded) / (approved + rejected + superseded)"


def test_t008_rollback_rate_uses_approved_count(tmp_path):
  for proposal_id in ["WP-001", "WP-002"]:
    _write_yaml(
      tmp_path / "learning" / "workflow" / "approved-updates" / f"{proposal_id}.yaml",
      _proposal(proposal_id, "update", "approved"),
    )
  _write_yaml(
    tmp_path / "learning" / "workflow" / "rollback" / "2026-06-04-RB-001.yaml",
    {"rollback_id": "RB-001", "target_proposal_id": "WP-001"},
  )

  metrics = EffectMeasurement(tmp_path).calculate_metrics(metric_date="2026-06-04")

  assert metrics["rollback_rate"] == 0.5


def test_t008_writes_metrics_as_time_series_yaml(tmp_path):
  path = EffectMeasurement(tmp_path).write_metrics(metric_date="2026-06-04")

  assert path == tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04.yaml"
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  assert data["metric_date"] == "2026-06-04"
  assert set(data["manual_aggregation_steps"]) == {
    "find_wc",
    "grep_sort_uniq",
    "adoption_rate_calculation",
    "metrics_record",
  }


def test_t008_manual_aggregation_steps_are_reproducible():
  steps = EffectMeasurement.manual_aggregation_steps()

  assert steps == [
    {"id": "find_wc", "description": "find と wc で対象 YAML 件数を数える"},
    {"id": "grep_sort_uniq", "description": "grep、sort、uniq で種別と状態を集計する"},
    {"id": "adoption_rate_calculation", "description": "approved、rejected、superseded から採用率を算出する"},
    {"id": "metrics_record", "description": "learning/workflow/metrics/<日付>.yaml に記録する"},
  ]


def test_t008_metrics_schema_documents_owned_constraints():
  schema = json.loads(
    (EffectMeasurement.project_root() / "learning" / "workflow" / "schemas" / "metrics.schema.json")
    .read_text(encoding="utf-8")
  )

  assert schema["required"] == [
    "metric_date",
    "discipline_compliance_rate",
    "promotion_count",
    "archive_count",
    "proposal_counts_by_type",
    "adoption_rate",
    "rollback_rate",
    "average_days_to_adoption",
    "manual_aggregation_steps",
  ]

```

## FILE: tests/self-improvement/test_t009_machine_verification.py

```text
"""T-009 のテスト：機械検査の具体手段。

対応タスク：self-improvement tasks.md T-009
対応設計節：design.md §17.1〜§17.4
対応要件：Requirement 1 受入 4
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

from tools.self_improvement.machine_verification import (
  MachineVerification,
  VerificationStatus,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "self-improvement-check.py"


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _proposal(**overrides):
  data = {
    "proposal_id": "WP-001",
    "proposal_type": "update",
    "target_discipline_path": "docs/disciplines/discipline_update.md",
    "motivating_evidence": [
      {
        "source": "review_record",
        "location": "reviews/2026-06-04.yaml",
        "observation": "機械検査のために十分な長さを持つ観察記録",
      }
    ],
    "proposed_change": {"change_diff": "- old\n+ new"},
    "expected_effect": "規律更新の効果",
    "status": "approved",
    "materialization_commit_hash": None,
  }
  data.update(overrides)
  return data


def test_t009_mv1_detects_direct_discipline_write_fail_closed():
  result = MachineVerification().check_direct_discipline_writes(
    changed_files=[
      "docs/disciplines/discipline_update.md",
      "learning/workflow/proposals/WP-001.yaml",
    ],
    actor_feature="self-improvement",
  )

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-1"
  assert "docs/disciplines/discipline_update.md" in result.reasons[0]


def test_t009_mv1_allows_non_discipline_files():
  result = MachineVerification().check_direct_discipline_writes(
    changed_files=["learning/workflow/proposals/WP-001.yaml"],
    actor_feature="self-improvement",
  )

  assert result.status == VerificationStatus.OK


def test_t009_mv2_detects_missing_required_proposal_field(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  proposal = _proposal()
  del proposal["expected_effect"]
  _write_yaml(proposal_path, proposal)

  result = MachineVerification(tmp_path).check_proposal_required_fields([proposal_path])

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-2"
  assert "missing_required_fields" in result.reasons[0]


def test_t009_mv3_skips_null_materialization_commit_hash(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(materialization_commit_hash=None))

  result = MachineVerification(tmp_path).check_materialization_commit_hashes(
    [proposal_path],
    commit_exists=lambda commit: False,
  )

  assert result.status == VerificationStatus.OK
  assert result.details["skipped_null_count"] == 1


def test_t009_mv3_detects_missing_non_null_commit_hash(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(materialization_commit_hash="deadbeef"))

  result = MachineVerification(tmp_path).check_materialization_commit_hashes(
    [proposal_path],
    commit_exists=lambda commit: False,
  )

  assert result.status == VerificationStatus.DEVIATION
  assert "deadbeef" in result.reasons[0]


def test_t009_mv4_requires_superseded_three_fields(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  _write_yaml(proposal_path, _proposal(status="superseded", superseded_by="WP-002"))

  result = MachineVerification(tmp_path).check_superseded_fields([proposal_path])

  assert result.status == VerificationStatus.DEVIATION
  assert result.check_id == "MV-4"
  assert "superseded_at" in result.reasons[0]
  assert "reopen_reason" in result.reasons[0]


def test_t009_fail_closed_summary_and_metrics_append(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "approved-updates" / "WP-001.yaml"
  proposal = _proposal()
  del proposal["expected_effect"]
  _write_yaml(proposal_path, proposal)

  summary = MachineVerification(tmp_path).run_all(
    changed_files=["learning/workflow/approved-updates/WP-001.yaml"],
    actor_feature="self-improvement",
    proposal_paths=[proposal_path],
    metric_date="2026-06-04",
    commit_exists=lambda commit: True,
  )

  metrics = yaml.safe_load(
    (tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04-machine-verification.yaml")
    .read_text(encoding="utf-8")
  )
  assert summary["verdict"] == "DEVIATION"
  assert metrics["verdict"] == "DEVIATION"
  assert metrics["checks"][1]["check_id"] == "MV-2"


def test_t009_cli_returns_json_and_exit_two_for_deviation(tmp_path):
  result = subprocess.run(
    [
      sys.executable,
      str(SCRIPT),
      "mv1",
      "--actor-feature",
      "self-improvement",
      "--changed-file",
      "docs/disciplines/discipline_update.md",
      "--json",
    ],
    cwd=tmp_path,
    capture_output=True,
    text=True,
    timeout=10,
  )

  assert result.returncode == 2
  data = json.loads(result.stdout)
  assert data["verdict"] == "DEVIATION"
  assert data["checks"][0]["check_id"] == "MV-1"


def test_t009_responsibility_document_exists():
  doc = REPO_ROOT / "docs" / "operations" / "SELF_IMPROVEMENT_MACHINE_VERIFICATION.md"

  text = doc.read_text(encoding="utf-8")
  assert "MV-1" in text
  assert "MV-2" in text
  assert "MV-3" in text
  assert "MV-4" in text
  assert "check-workflow-action.py" in text
  assert "self-improvement-check.py" in text

```

## FILE: tests/self-improvement/test_t010_interfaces.py

```text
"""T-010 のテスト：他機能との接合面。

対応タスク：self-improvement tasks.md T-010
対応設計節：design.md §13.1〜§13.6
対応要件：Boundary Context 隣接期待
"""
import json

import yaml

from tools.self_improvement.interfaces import (
  InterfaceAdapter,
  assert_commit_fields_are_independent,
  foundation_reference_contract,
)


def _write_yaml(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def test_t010_foundation_vocabularies_are_referenced_not_redefined():
  contract = foundation_reference_contract()

  assert contract == {
    "discipline_check_schema": "foundation",
    "review_mode_vocabulary": "foundation",
    "state_axis_vocabulary": "foundation",
    "policy": "reference_only_no_redefinition",
  }
  assert "api_mediated" not in json.dumps(contract, ensure_ascii=False)
  assert "runtime_mediated" not in json.dumps(contract, ensure_ascii=False)


def test_t010_reads_evaluation_role_diff_report(tmp_path):
  report_path = tmp_path / "evaluation" / "roles" / "role_diff_report.json"
  report_path.parent.mkdir(parents=True)
  report_path.write_text(
    json.dumps({"report_id": "role-diff-001", "items": [{"role": "primary"}]}),
    encoding="utf-8",
  )

  result = InterfaceAdapter(tmp_path).read_evaluation_role_diff_report(report_path)

  assert result == {"report_id": "role-diff-001", "items": [{"role": "primary"}]}


def test_t010_writes_analysis_metrics_output(tmp_path):
  path = InterfaceAdapter(tmp_path).write_analysis_metrics(metric_date="2026-06-04")

  assert path == tmp_path / "learning" / "workflow" / "metrics" / "2026-06-04.yaml"
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  assert data["metric_date"] == "2026-06-04"
  assert "adoption_rate" in data


def test_t010_workflow_management_contract_and_git_mv_path(tmp_path):
  proposal_path = tmp_path / "learning" / "workflow" / "proposals" / "WP-001.yaml"
  _write_yaml(
    proposal_path,
    {
      "proposal_id": "WP-001",
      "status": "approved",
      "target_discipline_path": "docs/disciplines/discipline_update.md",
      "materialized_at": None,
      "materialization_commit_hash": None,
    },
  )

  contract = InterfaceAdapter(tmp_path).workflow_management_input_contract(proposal_path)

  assert contract == {
    "proposal_id": "WP-001",
    "approved_state_owner": "self-improvement",
    "materialization_owner": "workflow-management",
    "source_path": "learning/workflow/proposals/WP-001.yaml",
    "approved_updates_path": "learning/workflow/approved-updates/WP-001.yaml",
    "move_operation": "git_mv_required",
    "approved_means": "self_improvement_approval_time",
    "materialized_at_means": "workflow_management_completion_time",
  }


def test_t010_conformance_target_commit_is_independent_from_materialization_commit():
  result = assert_commit_fields_are_independent(
    target_commit="abc123",
    materialization_commit_hash="def456",
  )

  assert result == {
    "target_commit_owner": "conformance-evaluation",
    "materialization_commit_hash_owner": "self-improvement",
    "independent": True,
  }


def test_t010_approved_updates_readme_documents_workflow_management_route():
  text = (
    InterfaceAdapter.project_root()
    / "learning"
    / "workflow"
    / "approved-updates"
    / "README.md"
  ).read_text(encoding="utf-8")

  assert "workflow-management" in text
  assert "git mv" in text
  assert "materialized_at" in text
  assert "materialization_commit_hash" in text

```

## FILE: tests/self-improvement/test_t011_traceability.py

```text
from pathlib import Path

import pytest

from tools.self_improvement.traceability import (
  EXPECTED_MODEL_NAMES,
  EXPECTED_TASK_TESTS,
  TraceabilityAudit,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def audit():
  return TraceabilityAudit(ROOT)


def test_t011_expected_task_tests_are_present(audit):
  assert audit.missing_task_tests() == []
  assert sorted(EXPECTED_TASK_TESTS) == [f"T-{index:03d}" for index in range(1, 12)]


def test_t011_seven_models_have_all_three_test_levels(audit):
  coverage = audit.model_level_coverage()

  assert sorted(coverage) == sorted(EXPECTED_MODEL_NAMES)
  for levels in coverage.values():
    assert levels == {"unit", "integration", "acceptance"}


def test_t011_requirements_traceability_is_bidirectional(audit):
  assert audit.requirements_traceability_issues() == []


def test_t011_dvt_unresolved_items_have_deferral_reasons(audit):
  assert audit.dvt_gate_issues() == []


def test_t011_key_regression_surfaces_are_covered(audit):
  assert audit.key_regression_coverage() == {
    "proposal_schema_validity": True,
    "foundation_vocab_reference_only": True,
    "superseded_reopen_five_steps": True,
    "effect_metrics": True,
    "rollback_integrity": True,
    "workflow_materialized_at_sync": True,
  }

```

