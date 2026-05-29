---
spec: evaluation
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-27
language: ja
---

# Tasks Document：evaluation

## 概要（Overview）

本文書は `evaluation`（評価機能）の実装タスクを列挙する。`evaluation` は `foundation` の共有資産層と `runtime` の実行成果物の上に位置する評価層であり、有効・無効実行の分離、処理方式比較、メトリクス抽出、フェーズ対応評価、レビューモード差分・3 役所見差分、陳腐化伝播履行、外部証拠束の取り込みと許容判定を担う。タスクは設計文書（design.md）の責務領域単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。

タスクの依存順は design.md §全体構造で固定された 5 段（intake → classification → metric extraction → comparison → reporting）と、§分析成果物配置の生成順序に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの責務領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：実装機能は単体テスト（pytest）で検証可能とする。言語モデル呼び出しは含まないため、固定入力から決定的に再現可能であることを徹底する
- **contract consumer 原則**：evaluation は foundation の語彙正本（6 件）と runtime の語彙正本（3 件）を再定義せず参照のみで使用する（design.md §判断 8 準拠）。本機能所有の正本（admission 3 値、陳腐化伝播履行手段の選択ロジック）は本機能で確定する

`evaluation` 全体で 11 タスク。

## タスク一覧（Task List）

### T-001：分析成果物配置の構造と命名規約

- **対応設計節**：design.md §分析成果物配置、§配置の根拠
- **対応要件**：Requirement 5 受入 1、3（派生成果物の生成と機械可読出力、生実行証拠保管からの分離。受入 2 ＝識別子連結保持は T-006 を主担当として責務分担、要件追跡表参照）
- **責務**：仕様文書の配置先＝ `evaluation/analysis_layout/`、実体生成物の配置先＝ `experiments/analysis/`。`experiments/analysis/` 配下のディレクトリ構造（`imports/` ／ `manifests/` ／ `classifications/` ／ `metrics/` ／ `comparisons/` ／ `caveats/` ／ `modes/` ／ `roles/`）を仕様文書として新設し（実体の物理ディレクトリ作成は実行時に T-002 取り込み器が `bundle_id` ／ `run_id` ごとに行う、本タスクは仕様文書と配置運用ルールの定義のみ）、各サブディレクトリに配置目的を記す README を置く。生実行証拠（`experiments/runs/<run_id>/`）と分析成果物（`experiments/analysis/`）の分離原則を `docs/operations/EVALUATION.md` に記述
- **前提タスク**：なし（起点、foundation T-001 と runtime T-001 完了を前提とする外部依存あり）
- **成果物**：
  - `evaluation/analysis_layout/README.md`（分析成果物配置の解説）
  - `evaluation/analysis_layout/layout_spec.yaml`（配置仕様の機械可読版）
  - `docs/operations/EVALUATION.md`（配置運用ルールを記述、または該当節を追記）
- **完了条件**：
  1. 配置仕様 YAML が解析可能で、必須サブディレクトリ 8 件（`imports`／`manifests`／`classifications`／`metrics`／`comparisons`／`caveats`／`modes`／`roles`）が宣言されている
  2. 配置の運用ルール（生実行証拠と分析成果物の分離、`analysis_run_manifest.yaml` の必須項目、版被覆記録）が `docs/operations/EVALUATION.md` に記述された上で、README または EVALUATION.md の人間レビューで承認されていること（承認の記録方法は foundation tasks T-001 ／ runtime tasks T-001 と同じ運用に従う）
- **テスト要件**：配置仕様 YAML の解析テスト、必須サブディレクトリ宣言の存在検査

### T-002：取り込み器（intake）と物理配置

- **対応設計節**：design.md §取り込みモデル、§可搬証拠束の取り込み、§取り込み時の物理配置
- **対応要件**：Requirement 10 受入 1（中央側取り込み契約）、Requirement 10 受入 5（取り込み証拠の派生成果物保持）
- **責務**：runtime が `exports/<bundle_id>/` に輸出した可搬証拠束を中央側で読み込み、`experiments/analysis/imports/bundles/<bundle_id>/run/<run_id>/...` に物理配置する。runtime の輸出構造（`exports/<bundle_id>/run/<run_id>/...`）をそのまま中央側で継承し、構造の対称性を保つ。物理コピー前にチェックサム照合を実施（T-003 の許容判定と連携）。`imports/ingestion_register.json` に取り込み履歴（design.md §取り込み登録 行 489-498 が定める必須 8 項目：`bundle_id` ／ `run_id` ／ `source_repository_id` ／ `source_revision` ／ `review_mode` ／ `ingested_at` ／ `ingestion_status` ／ `missing_fields`）を記録
- **前提タスク**：T-001（配置先の準備）
- **成果物**：
  - `evaluation/intake/bundle_intake.py`（中央側取り込み本体）
  - `evaluation/intake/physical_placement.py`（`exports/<bundle_id>/` → `imports/bundles/<bundle_id>/` の物理コピーと構造継承）
  - `evaluation/intake/ingestion_register_writer.py`（`ingestion_register.json` 生成）
- **完了条件**：可搬証拠束が `imports/bundles/<bundle_id>/run/<run_id>/` に物理コピーされる、`ingestion_register.json` に 8 必須項目を含む取り込み履歴が追記される、runtime 輸出構造との対称性が保たれる（操作的判定：輸出前後のディレクトリツリーのパス構造ハッシュ照合または ls 結果の差分が空であることを検査）
- **テスト要件**：固定 `exports/<bundle_id>/` 入力に対する物理配置の決定的テスト、`ingestion_register.json` 追記テスト、構造対称性検証テスト

### T-003：取り込み許容判定器（admission）

- **対応設計節**：design.md §取り込み証拠の許容判定状態、§判断 7
- **対応要件**：Requirement 10 受入 2（来歴情報検証）、Requirement 10 受入 3（手動 dogfooding 区別）、Requirement 10 受入 4（許容規則による却下／格下げ／許容）、Requirement 10 受入 5（許容状態の保持）
- **責務**：本機能所有の 3 値正本（`admitted_standard` ／ `admitted_exploratory` ／ `rejected`）を確定し、`imports/admission_register.json` に許容判定結果を記録。`bundle_manifest.yaml` の必須来歴情報（`source_repository_id` ／ `source_revision`、foundation Requirement 6 受入 7 由来）を検証。チェックサム照合を実施（`checksums/bundle_checksums.json` と比較）。design.md §テスト戦略の 7 つの境界入力ケース（不在／全欠落／読み取り不能／一部欠落／版不整合／全条件揃い／チェックサム不一致）を網羅
- **前提タスク**：T-002（取り込み後の `bundle_manifest.yaml` が前提）
- **成果物**：
  - `evaluation/admission/admission_classifier.py`（3 値判定本体）
  - `evaluation/admission/admission_vocab.yaml`（`admitted_standard` ／ `admitted_exploratory` ／ `rejected` の 3 値正本）
  - `evaluation/admission/checksum_verifier.py`（チェックサム照合）
  - `evaluation/admission/admission_register_writer.py`（`admission_register.json` 生成）
- **完了条件**：3 値正本 YAML が解析可能で 3 値が宣言されている、7 つの境界入力ケースすべてで決定的な判定が出る、チェックサム不一致時に `rejected` に分類される、`admission_register.json` に判定結果が追記される
- **テスト要件**：**単体検証（モック環境）**：境界 7 ケース全件（不在 ／ 全欠落 ／ 読み取り不能 ／ 一部欠落 ／ 版不整合 ／ 全条件揃い ／ チェックサム不一致、design.md §テスト戦略の網羅）を単体テストで網羅、3 値正本ファイルの値テスト、チェックサム照合テスト。T-011 との関係：T-003 単体（モック）と T-011 経路統合（実環境）は意図的二層検証であり、二重実装ではない

### T-004：実行分類器（run classifier）

- **対応設計節**：design.md §分類モデル §1 分類状態、§2 分類規則、§3 欠落と無効の区別、§4 設計上の段省略と障害欠損の弁別
- **対応要件**：Requirement 1 受入 1〜6（4 値分類、無効実行の既定除外、件数と理由の保持、欠落と無効の区別、自由記述非要求、レビューモード直交独立軸）
- **責務**：foundation `evidence_class` 4 値正本（`valid` ／ `invalid` ／ `exploratory` ／ `analysis_blocked`）を再定義せず参照のみで使用、実行の分類を `classifications/run_classification_index.json` に出力。runtime の `step_outcome` 3 値（`executed` ／ `skipped_by_treatment` ／ `failed`）を参照し、設計上の段省略（treatment 起因）と実行時失敗を弁別。design.md §4 の 5 ステップ段省略整合チェック手順を実装
- **前提タスク**：T-002（取り込み済み実行成果物が前提）、T-003（許容判定済み bundle の選別）
- **成果物**：
  - `evaluation/classifier/run_classifier.py`（4 値分類本体）
  - `evaluation/classifier/step_omission_validator.py`（段省略整合チェック、design.md §4 の 5 ステップ手順を実装）
  - `evaluation/classifier/run_classification_writer.py`（`run_classification_index.json` 生成）
- **完了条件**：固定入力に対し 4 値分類が決定的に出る、`evidence_class` 4 値の foundation 正本を再定義せず参照する、段省略と障害欠損の弁別が決定的、レビューモード分類（`manual_dogfooding` ／ `runtime_mediated` ／ `subagent_mediated`）と直交独立軸として扱われる
- **テスト要件**：4 値分類の境界テスト、段省略整合チェックの 5 ステップ手順テスト、レビューモードとの直交独立性テスト、foundation 4 値正本の参照のみ使用の機械検証

### T-005：評価準備メタデータ検査器と不十分性診断

- **対応設計節**：design.md §評価準備メタデータの検査、§必須メタデータ検査、§不十分性の診断情報、§致命的失敗と探索的部分分析の区別
- **対応要件**：Requirement 6 受入 1〜5（必須メタデータ検査、欠落時の集計拒否、不十分性診断情報の出力、致命的失敗と探索的部分分析の区別、自由記述発明禁止）
- **責務**：標準集計の前に必須メタデータ（実行識別子・版情報など）を検査。欠落があれば標準集計を拒否し、`classifications/insufficient_metadata_report.json` に 5 項目（`run_id` ／ `missing_fields` ／ `evidence_class` ／ `affected_derived_artifacts` ／ `detected_at`）を記録。致命的失敗と探索的部分分析を foundation `evidence_class` 4 値正本で区別（`analysis_blocked` ＝必要入力の不足／実行未終了／検証が前提不足で結論不能）
- **前提タスク**：T-004（4 値分類済み実行が前提）
- **成果物**：
  - `evaluation/readiness/metadata_validator.py`（必須メタデータ検査）
  - `evaluation/readiness/required_fields_schema.yaml`（必須メタデータ項目集合）
  - `evaluation/readiness/insufficient_metadata_writer.py`（`insufficient_metadata_report.json` 生成、5 項目）
- **完了条件**：必須メタデータ欠落時に標準集計が拒否される、`insufficient_metadata_report.json` の 5 項目が機械的に出力される、致命的失敗と `analysis_blocked` が foundation 正本 4 値に基づき区別される
- **テスト要件**：必須メタデータ欠落時の拒否テスト、`insufficient_metadata_report.json` 出力テスト、致命的失敗と `analysis_blocked` の弁別テスト

### T-006：メトリクス抽出器（metric extractor）

- **対応設計節**：design.md §メトリクスモデル §1 メトリクス階層、§2 中核層と phase 重ね合わせ層、§3 最小メトリクス集合、§4 派生規則、§5 派生メトリクスの導出経路保持、§6 再計算許容性
- **対応要件**：Requirement 3 受入 1〜5（最小メトリクス集合、構造化証拠からの計算、導出経路保持、再計算許容性、レベル分離）、Requirement 8 受入 1〜5（フェーズ特異な有効性メトリクスの許容、中核層＋重ね合わせ層、phase 別等価性非仮定、phase 特異選択の明示、将来拡張互換性）、**Requirement 5 受入 2**（派生出力から実行識別子と対象識別子への連結保持、本タスクが識別子連結の機械検証機構の主担当、T-007 ／ T-009 は本タスクの機構を利用）、**Requirement 5 受入 4**（self-improvement と analysis 両者による下流消費を支える）、**Requirement 5 受入 5**（評価ロジック変更時の成果物版管理可視化、`analysis_run_manifest.yaml` の生成を担う）、**Requirement 2 受入 6**（規約版混在検出の機械検証根拠、`analysis_run_manifest.yaml` の `protocol_version_coverage` ／ `prompt_set_version_coverage` を出力）
- **責務**：実行レベル／所見レベル／処理方式レベルのメトリクスを分離して抽出。中核メトリクス層（共有）と phase 重ね合わせ層（フェーズ特異）の二層構造を実装。foundation `counter_status` 3 値正本（`counter_evidence_raised` ／ `no_counter_evidence_after_challenge` ／ `not_assessed`）を再定義せず参照し、所見レベル中核メトリクスとして集計、処理方式レベルに反証発生率指標を生成。導出経路を成果物に保持。**識別子連結保持の機械検証機構の主担当**（Req 5 受入 2、T-007 ／ T-009 は本機構を前提として利用）。**`manifests/analysis_run_manifest.yaml` の生成**（design.md §分析成果物配置 行 117 ／ 行 517-527 で必須宣言、9 項目：`analysis_logic_version` ／ `protocol_version_coverage` ／ `runtime_version_coverage` ／ `prompt_set_version_coverage` ／ `analysis_run_id` ／ `input_run_set` ／ `analysis_started_at` ／ `analysis_completed_at` ／ `output_artifact_ids`、Req 5 受入 5 ／ Req 2 受入 6 の機械検証根拠）
- **前提タスク**：T-004（分類済み実行が前提）、T-005（メタデータ検査通過済み）
- **成果物**：
  - `evaluation/metrics/run_metrics_extractor.py`（実行レベル）
  - `evaluation/metrics/finding_metrics_extractor.py`（所見レベル、`counter_status` 集計を含む）
  - `evaluation/metrics/treatment_metrics_extractor.py`（処理方式レベル、反証発生率指標を含む）
  - `evaluation/metrics/core_layer_definition.yaml`（中核メトリクス層の定義）
  - `evaluation/metrics/phase_overlay_definition.yaml`（phase 別重ね合わせ層の定義）
  - `evaluation/metrics/identifier_link_validator.py`（識別子連結保持の機械検証機構の主担当実装、Req 5 受入 2、T-007 ／ T-009 は本機構を前提として利用）
  - `evaluation/manifests/analysis_run_manifest_writer.py`（`manifests/analysis_run_manifest.yaml` を生成、9 項目を機械的出力、Req 5 受入 5 ／ Req 2 受入 6）
- **完了条件**：3 レベル（実行／所見／処理方式）のメトリクスが分離して出力される、`counter_status` 3 値の foundation 正本を再定義せず参照する、中核層と重ね合わせ層が分離した成果物として生成される、導出経路が成果物に保持される、**識別子連結保持機構が機械検証可能（派生出力すべてに `run_id` ／ `target_id` が保持されていることを検査）**、**`manifests/analysis_run_manifest.yaml` が 9 項目を含む構造化形式で出力される**
- **テスト要件**：3 レベル分離テスト、`counter_status` 集計テスト、反証発生率指標テスト、中核層と重ね合わせ層の分離テスト、導出経路保持テスト、識別子連結保持の機械検証テスト、`analysis_run_manifest.yaml` 9 項目出力テスト

### T-007：比較器（comparison builder）

- **対応設計節**：design.md §比較モデル §1 処理方式比較、§2 フェーズ対応比較、§3 有効母集団規則、§4 レビューモード母集団規則
- **対応要件**：Requirement 2 受入 1〜6（処理方式比較契約、`primary`／`adversarial`／`judgment` 比較、段省略と実行時失敗の区別、処理方式同一性可視化、不整合検出、規約版・プロンプト版同一性）、Requirement 7 受入 1〜5（フェーズプロファイル同一性保持、フェーズ対応スライス、フェーズ横断比較、design ／ tasks 仮説検証、フェーズ別未分化潰し防止）、**Requirement 9 受入 6**（標準比較集団規則、3 集団扱い：`manual_dogfooding` 別集団、`subagent_mediated` 第三集団扱い）
- **責務**：treatment 比較（`comparisons/treatment_comparisons.json`）と phase 対応比較（`comparisons/phase_comparisons.json`）を実装。有効母集団規則（valid のみ）とレビューモード母集団規則（`manual_dogfooding` 別集団、`subagent_mediated` 第三集団扱い）を適用。比較セット内の規約版・プロンプト版混在を検出
- **前提タスク**：T-006（メトリクス抽出済み。T-006 が提供する識別子連結保持機構を前提として利用、二重実装しない、Req 5 受入 2 関連）
- **成果物**：
  - `evaluation/comparison/treatment_comparison_builder.py`
  - `evaluation/comparison/phase_comparison_builder.py`
  - `evaluation/comparison/valid_population_rule.py`（有効母集団規則）
  - `evaluation/comparison/mode_population_rule.py`（レビューモード母集団規則）
  - `evaluation/comparison/version_consistency_validator.py`（規約版・プロンプト版混在検出）
- **完了条件**：treatment 比較と phase 比較が独立成果物として出力される、有効母集団規則が決定的に適用される（操作的判定：treatment_comparisons.json ／ phase_comparisons.json の `included_runs[]` から `evidence_class != valid`（invalid ／ analysis_blocked）の実行が 0 件であることを機械検査）、レビューモード 3 集団扱いが反映される、規約版・プロンプト版混在が検出される
- **テスト要件**：treatment 比較テスト、phase 対応比較テスト、有効母集団規則テスト、レビューモード 3 集団扱いテスト、版混在検出テスト

### T-008：除外と注意点の報告器（reporting）

- **対応設計節**：design.md §除外と注意点のモデル §1 除外報告、§2 注意点登録
- **対応要件**：Requirement 4 受入 1〜5（除外報告出力、`analysis` と `self-improvement` 向け注意点情報、データ品質と実行時品質の注意点区別、除外件数の手作業非要求報告、無効実行と有効実行の黙示的混合防止）
- **責務**：除外された実行の件数と理由を `classifications/exclusion_report.json` に出力。データ品質の注意点と実行時品質の注意点を区別して `caveats/caveat_register.json` に記録。`analysis` と `self-improvement` が読み取り可能な形式とする
- **前提タスク**：T-004（分類済み実行が前提）、T-005（不十分性診断済み）
- **成果物**：
  - `evaluation/reporting/exclusion_report_writer.py`（`exclusion_report.json` 生成）
  - `evaluation/reporting/caveat_register_writer.py`（`caveat_register.json` 生成）
  - `evaluation/reporting/caveat_classifier.py`（データ品質 ／ 実行時品質の区別）
- **完了条件**：`exclusion_report.json` が件数と理由を含む構造化形式で出力される、`caveat_register.json` がデータ品質と実行時品質を区別して出力される、無効実行と有効実行が黙示的に 1 つの集計に潰されない
- **テスト要件**：`exclusion_report.json` 出力テスト、`caveat_register.json` 出力テスト、注意点区別テスト、無効・有効混合防止テスト

### T-009：レビューモード差分／3 役所見差分の出力（mode_diff／role_diff）

- **対応設計節**：design.md §レビューモード差分報告、§3 役所見差分報告
- **対応要件**：Requirement 9 受入 1〜8（`review_mode` 由来情報の保持、`runtime_mediated` 標準集合からの除外・別スライス、編集活動の有効性非扱い、混在レビューモードの保持、引き継ぎ境界の明示、3 集団規則、3 経路別差分の analysis 向け提供、3 役別差分の analysis 向け提供）
- **責務**：3 経路別（`manual_dogfooding` ／ `subagent_mediated` ／ `runtime_mediated`）の所見差分を `modes/mode_diff_report.json` に出力（最低限 4 要素：`feature` ／ `review_mode` ／ `findings_by_severity`（重大度別件数、design.md §レビューモード差分報告 行 464 のスキーマ命名）／ `target`）。3 役別（main ／ adversarial ／ judgment）の所見差分を `roles/role_diff_report.json` に出力（最低限 4 要素：`feature` ／ `role` ／ `findings_summary`（重大度別・最終判定別・反証状態別の組合せ、役による条件付き必須、design.md §3 役所見差分報告 行 477 のスキーマ命名）／ `target`）。**内部関係**：2 出力器（`mode_diff_writer.py` ／ `role_diff_writer.py`）は共通スキーマ（`diff_report_schema.yaml` の `feature` ／ `target` を共有）を参照し、それぞれ独立の出力責務を持つ。foundation `review_mode` 正本 3 値および 3 役分担（Step A／B／C 由来）を参照のみで使用
- **前提タスク**：T-006（メトリクス抽出済み、識別子連結保持機構を本タスクが利用する前提、二重実装しない、Req 5 受入 2 関連）、T-008（除外と注意点の報告完了済み、`modes/mode_diff_report.json` と `exclusion_report` が並列に下流から読まれる論理順）
- **成果物**：
  - `evaluation/diff_reports/mode_diff_writer.py`（`mode_diff_report.json` 生成、要件 9 受入 7 由来）
  - `evaluation/diff_reports/role_diff_writer.py`（`role_diff_report.json` 生成、要件 9 受入 8 由来、A-011 連動）
  - `evaluation/diff_reports/diff_report_schema.yaml`（両報告の最低限スキーマ、共通フィールド `feature` ／ `target` ＋ 個別フィールド `review_mode` ／ `findings_by_severity`（mode_diff）または `role` ／ `findings_summary`（role_diff）を定義）
- **完了条件**：`mode_diff_report.json` が 4 要素を含む構造化形式で出力される、`role_diff_report.json` が 4 要素を含む構造化形式で出力される（`findings_summary` は役による条件付き必須を実装）、**`analysis` 仕様（起草予定）の下流接合面条件を満たす形式**（具体的な受入条件は §遅延確認事項テーブル DVT-001 で管理、analysis 仕様 tasks 段完了時に解除）
- **テスト要件**：`mode_diff_report.json` 出力テスト、`role_diff_report.json` 出力テスト、4 要素必須テスト、`findings_summary` の役別条件付き必須テスト

### T-010：陳腐化伝播履行器（staleness propagation）

- **対応設計節**：design.md §版管理モデル、§陳腐化伝播の履行、§履行手段の選択ロジック、§判断 6
- **対応要件**：Requirement 5 受入 6（参照実行が無効化された場合の陳腐化マークまたは再導出、本機能が伝播義務の主要履行者）
- **責務**：本機能所有の陳腐化伝播履行手段の選択ロジックを実装。無効化マーカー付与時に派生成果物の陳腐化フラグ付けまたは再導出を選択的に実行。`manifests/staleness_register.json` に陳腐化履歴を記録。foundation Requirement 6 受入 9（無効化マーカー付与時の陳腐化伝播義務）の主要履行者として位置付け。**選択ロジック判定境界の入力源**は T-007 の `treatment_comparisons.json`（標準比較セットでの無効化実行の少数 ／ 多数判定）、T-009 の exploratory 集計（exploratory-only 境界判定）、必要に応じて T-006 の被覆率情報を入力として判定（design.md §履行手段の選択ロジック 行 544-548 の 3 境界に対応）
- **前提タスク**：T-006（被覆率計算完了：選択ロジック閾値判定に使用）、T-007（`treatment_comparisons.json` 生成完了：選択ロジック判定境界の入力源）、T-008（除外と注意点の報告が前提）、T-009（`mode_diff_report.json` ／ `role_diff_report.json` 完了：陳腐化伝播対象の派生成果物として含む、exploratory 集計の入力源）
- **成果物**：
  - `evaluation/staleness/propagation_executor.py`（陳腐化フラグ付け／再導出の選択実行）
  - `evaluation/staleness/handler_selection_logic.py`（履行手段の選択ロジック、本機能所有）
  - `evaluation/staleness/staleness_register_writer.py`（`staleness_register.json` 生成）
- **完了条件**：無効化マーカー付与時に陳腐化フラグ付けまたは再導出が決定的に実行される、選択ロジックが本機能で確定されている、`staleness_register.json` に履歴が記録される
- **テスト要件**：陳腐化伝播の決定的テスト、選択ロジックの境界テスト、`staleness_register.json` 出力テスト

### T-011：テスト戦略整備と統合テスト

- **対応設計節**：design.md §テスト戦略（5 つの検証点）、§完成判定基準
- **対応要件**：Requirement 1〜10 全体の機械判定可能な完了条件の網羅、本機能所有正本（admission 3 値、陳腐化伝播履行手段の選択ロジック）の機械検証
- **責務**：design.md §テスト戦略で定義された 5 つの検証点（分類判定の単体検証点／メトリクス導出の単体検証点／取り込み許容判定の単体検証点／陳腐化伝播の検証点／設計上の段省略と障害欠損の弁別検証点）をすべて Python テストとして整備。pytest で一括実行可能。foundation との接続部（語彙正本 6 件の参照のみで使用、再定義していないこと）と runtime との接続部（語彙正本 3 件の参照のみで使用、再定義していないこと）の機械検証を含める。本機能所有の正本（admission 3 値、陳腐化伝播履行手段の選択ロジック）が確定されていることの機械検証。要件追跡表と各タスク本文の対応要件欄の双方向整合チェック（foundation T-010 ／ runtime T-011 と同様、evaluation 側でも採用）
- **前提タスク**：T-001、T-002、T-003、T-004、T-005、T-006、T-007、T-008、T-009、T-010（全実装タスクが前提）
- **成果物**：`tests/evaluation/` 配下のテストファイル群（`test_layout.py` ／ `test_intake.py` ／ `test_admission.py` ／ `test_classifier.py` ／ `test_readiness.py` ／ `test_metrics.py` ／ `test_comparison.py` ／ `test_reporting.py` ／ `test_diff_reports.py` ／ `test_staleness.py` ／ `test_integration_pipeline.py` ／ `test_downstream_interface.py`（4 下流機能 ＝ self-improvement ／ analysis ／ workflow-management ／ conformance-evaluation との接合面の入力ファイル合致確認、A-003 対処、design.md §下流機能との接合面 行 601-646 の機械検証）の 12 ファイル相当、または機能別に分割）。**経路統合検証（実環境）**：T-003 で単体検証された境界 7 ケース全件を実環境経路でエンドツーエンド検証（T-003 と意図的二層、二重実装ではない）
- **完了条件**：すべての pytest が pass、5 つの検証点のテスト戦略網羅、foundation 6 語彙正本＋runtime 3 語彙正本の参照のみ使用が機械検証される（**語彙正本ハッシュ照合または参照のみ使用の機械検証手順**、runtime F-012 と同一作業）、evaluation 所有正本（admission 3 値、陳腐化伝播履行手段の選択ロジック）が T-003 ／ T-010 の成果物で正本確定されていることが機械検証される、**4 下流接合面の機械検証**（要件追跡表双方向整合 ＋ 語彙正本参照のみ使用 ＋ 成果物配置適合、F-011 ／ A-003 対処）、**Req 5 受入 2 の双方向整合チェック**（T-006 の識別子連結保持機構が T-007 ／ T-009 で正しく利用され、派生出力すべてに識別子が保持されていることの検証）、要件追跡表の双方向整合が機械チェックされる、**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**（A-007 対処、DVT-001 のゲート化）
- **テスト要件**：すべての pytest が pass、回帰なし

---

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1：有効・無効実行の分離 | T-004（4 値分類）、T-008（除外報告） |
| Requirement 2：処理方式の比較契約 | T-007（treatment 比較、受入 1〜6）、T-006（処理方式レベルメトリクス、受入 6 ＝規約版混在検出の機械検証根拠、`analysis_run_manifest.yaml` の版被覆出力） |
| Requirement 3：メトリクス抽出 | T-006（メトリクス抽出器） |
| Requirement 4：除外と注意点の報告 | T-008（reporting） |
| Requirement 5：派生成果物の生成 | T-001（受入 1、3 ＝配置）、**T-006（受入 2 主担当 ＝識別子連結保持機構、受入 4 ＝下流消費、受入 5 ＝版管理可視化）**、T-007（受入 2 利用 ＝ T-006 機構を前提）、T-009（受入 2 利用 ＝ T-006 機構を前提）、T-010（受入 6 ＝陳腐化伝播履行）、T-011（受入 2 検証 ＝双方向整合チェック） |
| Requirement 6：評価準備メタデータの完全性 | T-005（メタデータ検査と不十分性診断） |
| Requirement 7：フェーズ対応の評価 | T-006（phase 重ね合わせ層）、T-007（phase 対応比較） |
| Requirement 8：フェーズ特異な有効性メトリクス | T-006（中核層＋重ね合わせ層） |
| Requirement 9：レビューモードの区別 | T-007（受入 1〜5・6 ＝レビューモード母集団規則、3 集団扱い）、T-009（受入 7 ／ 8 ＝ mode_diff ／ role_diff の analysis 向け出力） |
| Requirement 10：外部証拠束の取り込みと許容判定 | T-002（取り込み）、T-003（許容判定） |

---

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略で定義された 5 つの検証点と各タスクの対応：

- 分類判定の単体検証点 → T-004 ／ T-011
- メトリクス導出の単体検証点 → T-006 ／ T-011
- 取り込み許容判定の単体検証点 → T-003 ／ T-011（design.md §テスト戦略の 7 つの境界入力ケースを網羅）
- 陳腐化伝播の検証点 → T-010 ／ T-011
- 設計上の段省略と障害欠損の弁別検証点 → T-004 ／ T-011

---

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-011 のすべてが起草・実装・テスト・コミット完了
- design.md §完成判定基準の 7 項目すべてが T-011 の統合テストで pass
- foundation の 6 語彙正本（`counter_status`／`validator_status`／`evidence_class`／`review_mode`／`severity`／`final_label`）を evaluation が再定義せず参照のみで使用していることが、機械検証で確認できる（`confidence_label` は推定タスク用であり、evaluation は推定タスクを扱わないため参照範囲外。よって上記 6 件のみを参照する）
- runtime の 3 語彙正本（`phase_profile`／`treatment`／`step_outcome`）を evaluation が再定義せず参照のみで使用していることが、機械検証で確認できる
- evaluation 所有の正本（`admitted_standard`／`admitted_exploratory`／`rejected` の許容判定 3 値、陳腐化伝播履行手段の選択ロジック）が T-003 ／ T-010 の成果物で正本として確定されている
- 各タスクの成果物配置が design.md §分析成果物配置と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）

---

## 変更意図（Change Intent）

本タスク文書は evaluation 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの責務領域。foundation T-001〜T-011 ／ runtime T-001〜T-011 の粒度方針を継承
- **責務領域単位**：設計の節と必ずしも 1 対 1 でなく、関連する節は同じタスクにまとめる
- **要件追跡表**：双方向整合チェックを T-011 に組み込み、要件と各タスク本文の対応要件欄が機械検証される
- **テスト戦略の継承**：design.md §テスト戦略で定義された 5 つの検証点を T-011 で網羅
- **完成判定基準**：design.md §完成判定基準と本タスクの完了条件が一致
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **依存順の明示**：T-001（配置）→ T-002（取り込み）／T-003（許容判定）→ T-004（分類）→ T-005（メタデータ検査）→ T-006（メトリクス）→ T-007（比較）→ T-008（reporting）→ T-009（mode_diff／role_diff）→ T-010（陳腐化伝播）→ T-011（統合テスト）の流れを固定
- **contract consumer 原則の徹底**：foundation 6 語彙正本＋runtime 3 語彙正本を再定義せず参照のみで使用、本機能所有の正本（admission 3 値、陳腐化伝播履行手段の選択ロジック）は本機能で確定
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：foundation T-010 ／ runtime T-011 の方針を踏襲、要件追跡表（Requirement → タスク）と各タスク本文の対応要件欄（タスク → Requirement）の双方向整合を機械検証

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。本セッション 33（2026-05-27）の 7 モデル比較実験 topic-52 A-007 別案 A 採用により新設（利用者明示承認「採用：別案 A」）。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-001 | T-009 | `analysis` 仕様（起草予定）の下流接合面条件（Req 7 受入 3 相当：レビュー収束過程の可視化の入力仕様）。T-009 の `mode_diff_report.json` ／ `role_diff_report.json` が `analysis` 仕様の入力として機能する具体形式は、`analysis` 仕様の tasks 段完了時に再評価して確定 | `analysis` 仕様 tasks 段完了時に T-009 完了条件と整合を再確認 | 未解除 |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-011 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化（A-007 別案 A 対処）
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

**正規化判断（2026-05-27 セッション 34）**：他機能 tasks.md への展開と計画書 ／ 運営ガイドへの正規化は **現時点で不要**。理由：DVT は evaluation 機能で 1 件（DVT-001）発生したのみで、他機能で類似事例が発生していない。汎用パターン化は実施結果を見てから再評価する方が安全。**継続使用範囲**：本機構は evaluation 機能内で T-009 ／ T-011 ／ DVT-001 の関係として継続使用、DVT-001 解除（analysis 仕様 tasks 段完了時）後に効果を確認。**再評価のタイミング**：analysis ／ workflow-management ／ self-improvement ／ conformance-evaluation の tasks 段で類似の遅延確認事項が発生したら、汎用パターン化（templates 整備、計画書 ／ 運営ガイドへの組み込み）の要否を別途判断する。**利用者明示承認の出典**：「ｂ。以降推奨案で自律的に進める」（要確認 4 の処理方針として案 d ＝ 機能内継続使用、汎用パターン化は延期、2026-05-27 セッション 34）。

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、`.reviewcompass/pending-cross-feature-findings.md` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。（A-017 対処 案1、2026-05-29 セッション40：全機能 tasks.md に確認手順を明示）
