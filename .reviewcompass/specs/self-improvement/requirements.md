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
2. `motivating_evidence` は配列で、各要素は `source`（`review_record`／`compliance_report`／`user_audit` のいずれか）／`location`（証跡ファイルへの相対パス）／`observation`（30 文字以上の自由記述）の 3 フィールドを持つ。
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
- 参考：他機能の所見（A-001／A-003／A-004／A-005 とも 2026-05-23 対処済み）の対処履歴は [.reviewcompass/pending-cross-feature-findings.md](../../pending-cross-feature-findings.md) を参照
