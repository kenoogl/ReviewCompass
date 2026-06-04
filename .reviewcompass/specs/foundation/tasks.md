---
spec: foundation
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-26
language: ja
---

# Tasks Document：foundation

## 概要（Overview）

本文書は `foundation` 機能の実装タスクを列挙する。`foundation` は ReviewCompass 全体で共有される最下層の契約（contract、約束事の集合）を成果物として固定する機能であり、実行コードは持たない。タスクは設計文書（design.md）の責務領域単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。

タスクの依存順は design.md の §共有資産配置で固定された配置規約と、§領域モデルの責務分離に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの責務領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：成果物は静的検証（スキーマ整合、語彙整合、配置整合）で機械的に判定可能とする

`foundation` 全体で 10 タスク。

## タスク一覧（Task List）

### T-001：共有資産ディレクトリ構造とアプリ側規約の準備

- **対応設計節**：design.md §共有資産配置、§配置決定
- **対応要件**：Requirement 5（パターン定義依存の除外、topic-09 A-002 案 1 採用で T-001 本文に追加）、Requirement 7（リポジトリ内資産の規則）
- **責務**：`runtime/foundation/` ／ `runtime/schemas/` ／ `runtime/prompts/` ／ `runtime/config/` ／ `runtime/validators/contracts/` の 5 ディレクトリを新設し、各ディレクトリに配置目的を記す README を置く。アプリ側 `<対象アプリ>/.reviewcompass/` 規約を `docs/operations/FOUNDATION.md` に記述。テスト関連の初期フォルダ `tests/foundation/` も配置規約に従って作成（`.gitkeep` で追跡可能化、topic-15 A-004 案 1 ＋ 方向 X 採用）
- **前提タスク**：なし（起点）
- **成果物**：
  - `runtime/foundation/README.md`
  - `runtime/schemas/README.md`
  - `runtime/prompts/README.md`
  - `runtime/config/README.md`
  - `runtime/validators/contracts/README.md`
  - `docs/operations/FOUNDATION.md`（アプリ側規約節を追記）
  - `tests/foundation/.gitkeep`（テスト用初期フォルダ、topic-15 採用による追加）
- **完了条件**：
  1. 5 ディレクトリと 5 README が存在し、`docs/operations/FOUNDATION.md` に「アプリ側 `.reviewcompass/config.yaml`」の規約が記述されている
  2. 配置規約・命名規約等の規約文書が記述された上で、README または FOUNDATION.md の人間レビューで承認されていること（topic-11 F-005 別案・最小タイプ採用：「規約が記述された＋人間レビュー承認」）
  3. 配置規約に従った初期フォルダ `tests/foundation/` が作成され、`.gitkeep` で Git に追跡可能な状態である（topic-15 採用）
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`tests/foundation/.gitkeep` 存在検査

### T-002：レイヤ 1 フレームワーク（layer1_framework.yaml）

- **対応設計節**：design.md §1 レビュー段の論理契約、§2 役の抽象化
- **対応要件**：Requirement 1（レビュー状態機械の契約、受入 1〜9）、Requirement 2 受入 1（役の抽象名）
- **責務**：レビューパイプライン Step A／B／C／D の論理契約と役抽象名を YAML 成果物として固定。最上位区画 7 つ（`version` ／ `roles` ／ `step_pipeline` ／ `step_intents` ／ `required_metadata_refs` ／ `asset_locations` ／ `override_extension_point`）を持つ
- **前提タスク**：T-001
- **成果物**：`runtime/foundation/layer1_framework.yaml`
- **完了条件**：YAML として解析可能、必須最上位区画 7 件が存在、Step A／B／C／D の正本名称（`primary_detection` ／ `adversarial_review` ／ `judgment` ／ `integration`）と役抽象名（`primary_reviewer` ／ `adversarial_reviewer` ／ `judgment_reviewer`）が宣言されている
- **テスト要件**：YAML 解析テスト、必須区画存在テスト、Step 名・役名の固定値テスト

### T-003：実行メタデータ契約（metadata_contract.yaml）

- **対応設計節**：design.md §3 実行メタデータ契約、§3.5 推定タスク用語彙
- **対応要件**：Requirement 1 受入 5、Requirement 6 受入 1〜11（検証器向けメタデータ）
- **責務**：実行メタデータの必須項目一覧（20 項目、topic-03 F-003 案 1 採用で「22 → 20」訂正）、4 種の状態語彙、来歴項目、推定タスク用語彙を YAML 成果物として固定。`run_status` ／ `validator_status` ／ `human_signoff_status` ／ `evidence_class` の責務分離を明示。語彙正本の所有関係も明示
- **前提タスク**：T-002
- **成果物**：`runtime/foundation/metadata_contract.yaml`
- **完了条件**：必須項目 20 件が列挙され、6 種の語彙（`run_status` 4 値 ／ `validator_status` 4 値 ／ `human_signoff_status` 4 値 ／ `evidence_class` 4 値 ／ `review_mode` 4 値 ／ `confidence_label` 3 値）が宣言されている（topic-02 F-002 案 1 採用で「5 種 → 6 種」訂正、`review_mode` は api_mediated 追加で 3 値 → 4 値、2026-06-01 セッション 46）
- **テスト要件**：YAML 解析テスト、必須項目数テスト、語彙正本値テスト（`run_status`＝`created`／`in_progress`／`closed`／`orchestration_failed`、`validator_status`＝`not_run`／`passed`／`failed`／`blocked`、`human_signoff_status`＝`pending`／`approved`／`rejected`／`deferred`、`evidence_class`＝`valid`／`invalid`／`exploratory`／`analysis_blocked`、`review_mode`＝`manual_dogfooding`／`runtime_mediated`／`subagent_mediated`／`api_mediated`、`confidence_label`＝`high`／`medium`／`low`）（topic-08 A-001 案 1 採用で `run_status` ／ `human_signoff_status` の値テストを追加）

### T-004：共有スキーマ群（5 ファイル）

- **対応設計節**：design.md §4 共有スキーマの関係（review_case／finding／impact_score／failure_observation／necessity_judgment の 5 スキーマ）、design.md §5 段別再演モデル（review_case の step_records の再演意図、topic-12 F-007 案 1 採用で追加）
- **対応要件**：Requirement 3（共通スキーマ集合、受入 1〜10）、Requirement 1 受入 4（finding の counter_status 必須化）
- **責務**：5 つの共有スキーマを JSON Schema として作成。mandatory／deferred の符号化規約（`required` 配列と `x-deferred` 注記）に準拠。`finding.severity` 4 値と `necessity_judgment.final_label` 3 値の enum を明示
- **前提タスク**：T-003（語彙正本の参照のため）
- **成果物**：
  - `runtime/schemas/review_case.schema.json`（必須 8 項目、Step D 統合レビュー記録の正本兼用、topic-01 F-001 案 1 採用で「9 → 8」訂正：failure_observations 削除を反映）
  - `runtime/schemas/finding.schema.json`（必須 11 項目、`severity` 4 値 enum、`counter_status` 3 値 enum）
  - `runtime/schemas/impact_score.schema.json`（必須 4 項目）
  - `runtime/schemas/failure_observation.schema.json`（必須 6 項目、独立成果物として配置）
  - `runtime/schemas/necessity_judgment.schema.json`（必須 5 項目構造＋ `final_label` 3 値 enum＋ `recommended_action` ／ `override_reason`）
- **完了条件**：5 ファイルすべて JSON Schema meta-schema 検証を通る、符号化規約（mandatory→ `required` 列挙、deferred→ `x-deferred` ＋ `description`）に準拠、`severity` ／ `counter_status` ／ `final_label` の enum 値が design.md §判断 7（所有関係宣言）＋ §4 finding 節（`severity` ／ `counter_status` の enum 値正本）＋ §4 necessity_judgment 節（`final_label` の enum 値正本）と一致（topic-05 F-006 案 2 採用で両参照を明示）
- **テスト要件**：5 スキーマの meta-schema 検証、必須項目数テスト（必須 8 項目）、enum 値テスト

### T-005：検証器側契約スキーマ（2 ファイル）

- **対応設計節**：design.md §8 検証と無効化のモデル
- **対応要件**：Requirement 6 受入 3（無効化マーカー）、受入 4（必須メタデータ欠落 → 検証不合格）、受入 9（陳腐化伝播義務）
- **責務**：検証器結果と無効化標識の形状を JSON Schema として固定。生証拠は不変、検証結果と無効化標識は別成果物の方針を符号化
- **前提タスク**：T-003（`validator_status` 4 値の参照のため）
- **成果物**：
  - `runtime/validators/contracts/validator_result.schema.json`（必須 6 項目：`run_id` ／ `validator_status` ／ `checked_contract` ／ `error_list` ／ `validated_by` ／ `validated_at`）
  - `runtime/validators/contracts/invalidation_marker.schema.json`（必須 6 項目：`run_id` ／ `reason_code` ／ `reason_detail` ／ `scope` ／ `issued_by` ／ `issued_at`、`scope` enum＝`run` ／ `step` ／ `finding`）
- **完了条件**：2 ファイルとも meta-schema 検証を通る、必須項目数と enum 値が design.md §8 と一致、deferred 表現に `x-staleness-propagation` 注記を使う場合は委譲先を明示
- **テスト要件**：2 スキーマの meta-schema 検証、必須項目数テスト、`scope` enum テスト

### T-006：プロンプト雛形 3 件

- **対応設計節**：design.md §6 プロンプト成果物モデル、§配置決定 3
- **対応要件**：Requirement 4（プロンプトの正本配置、受入 1〜5）
- **責務**：Step A／B／C の 3 役プロンプト雛形を frontmatter 付き Markdown として作成。本機能はプロンプトの正本配置と識別規則のみ定義、本文は最小限の雛形（フェーズ 4 で整備対象、計画書 §5.23.12.3）
- **前提タスク**：T-001（配置先ディレクトリの準備）
- **成果物**：
  - `runtime/prompts/primary_detection/primary_reviewer.prompt.md`
  - `runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md`
  - `runtime/prompts/judgment/judgment_reviewer.prompt.md`
- **完了条件**：3 ファイルとも frontmatter が解析可能、必須項目 6 件（`prompt_id` ／ `version` ／ `role` ／ `step` ／ `language` ／ `source_ref`）を持つ
- **テスト要件**：3 ファイルの frontmatter 解析テスト、必須項目存在テスト、`role` ／ `step` 値の整合テスト（※ `step` キーの値が `primary_detection` ／ `adversarial_review` ／ `judgment` の 3 値のいずれかであることの enum 検証を含む、topic-16 A-006 別案採用：独立テスト項目を追加せず既存スキーマ整合テストの記述内に補足注記）

### T-007：設定 2 層モデル雛形

- **対応設計節**：design.md §10 設定と雛形のモデル
- **対応要件**：Requirement 2（役と設定の抽象化、受入 1〜6）、Requirement 7 受入 3（環境設定は実行メタデータに記録される場合のみ許容）
- **責務**：設定成果物の 2 層モデル（ツール本体既定値とアプリ側上書き）を 3 ファイルで実装。`terminology.yaml.template` の最小契約も含む
- **前提タスク**：T-001（配置先ディレクトリの準備）
- **成果物**：
  - `runtime/config/reviewcompass.yaml`（ツール本体既定値、§10 下層）
  - `runtime/config/config.yaml.template`（アプリ側上書き用雛形、§10 上層の素材、必須項目 5 件：役ごとのモデル識別子 ／ 対象アプリの言語 ／ 規約版 ／ 証拠出力先 ／ 既定の phase および profile（以上 5 項目）、topic-14 A-003 別案 A+D 採用：件数明示 ＋ 自然言語接続詞で誤読防止）
  - `runtime/config/terminology.yaml.template`（必須項目 2 件：`version` ／ `entries`、`entries` は空配列でも成立）
- **完了条件**：3 ファイルとも YAML として解析可能、`config.yaml.template` の必須 5 項目と `terminology.yaml.template` の必須 2 項目が存在
- **テスト要件**：3 ファイルの YAML 解析テスト、必須項目存在テスト

### T-008：符号化規約整合検証スクリプト

- **対応設計節**：design.md §4「mandatory／deferred の JSON Schema 符号化規約」
- **対応要件**：Requirement 3 受入 9（mandatory／deferred 明示）
- **責務**：T-004／T-005 で作成した 7 つのスキーマが符号化規約に準拠することを機械的に検証する Python スクリプトを作成。mandatory 項目が `required` 配列に列挙されているか、deferred 項目が `x-deferred` ＋ `description` を持つかを判定
- **前提タスク**：T-004、T-005
- **成果物**：`tools/foundation_validators/check_encoding_convention.py`（Python スクリプト、読み取り専用検証器、ファイル書き込みの副作用なし、topic-07 F-010 案 2 採用で意味明示）と対応するテストファイル
- **完了条件**：スクリプトを 7 スキーマに対して実行して exit 0、違反スキーマには非ゼロ＋ stderr 出力。テストは符号化規約準拠／非準拠の両系統を確認
- **テスト要件**：規約準拠スキーマでの pass テスト、非準拠スキーマでの fail テスト（テスト用 fixture）

### T-009：テスト戦略全体の整備

- **対応設計節**：design.md §テスト戦略（7 項目）
- **対応要件**：Requirement 3 受入 9、Requirement 6 受入 4
- **責務**：design.md §テスト戦略で定義された 7 項目（スキーマ整合 ／ 符号化規約整合 ／ 枠組み整合 ／ メタデータ整合 ／ 語彙正本整合（`counter_status` ／ `validator_status` ／ `evidence_class` ／ `review_mode` ／ `severity` ／ `final_label` ／ `confidence_label` の 7 語彙すべてをカバー、topic-04 F-004 案 1 採用） ／ プロンプト整合 ／ 雛形整合）をすべて Python テストとして整備。pytest で一括実行可能
- **前提タスク**：T-001（`tests/foundation/` ディレクトリの準備、topic-15 A-004 案 1 ＋ 方向 X 採用で明示）、T-002、T-003、T-004、T-005、T-006、T-007、T-008
- **成果物**：`tests/foundation/` 配下のテストファイル群（test_layer1_framework.py ／ test_metadata_contract.py ／ test_schemas.py ／ test_validator_contracts.py ／ test_prompts.py ／ test_config_templates.py の 6 ファイル相当、または機能別に分割）
- **完了条件**：すべてのテストが pytest で pass、7 項目を網羅
- **テスト要件**：すべての pytest が pass、回帰なし（topic-06 F-009 案 1 採用で累積件数記述を削除）

### T-010：完成判定基準の自動実行

- **対応設計節**：design.md §完成判定基準
- **対応要件**：foundation 全要件の機械的合否判定
- **責務**：foundation 機能全体の完成判定基準（6 項目）を自動実行する統合スクリプトを作成。T-009 の全テストと T-008 のスクリプトをまとめて実行し、合否を判定
- **前提タスク**：T-008、T-009
- **成果物**：`tools/foundation_validators/check_completion.py`（統合検証スクリプト）
- **完了条件**：foundation 全要件の自動判定が exit 0 で完結、レポート出力（標準出力に整形済み YAML）が design.md §完成判定基準で定義された YAML スキーマに準拠（topic-10 A-005 別案採用：design.md に遡及してレポートスキーマを定義、軽量再オープン手続きで処理）
- **テスト要件**：統合スクリプトの正常系テスト、不完全状態での fail テスト、**要件追跡表（Requirement → タスク）と各タスク本文の対応要件欄（タスク → Requirement）の双方向整合チェック**（topic-17 A-007 案 1 採用：T-010 が CI ／メタタスク的な性格のため本タスクの責務として組み込み）

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1：レビュー状態機械の契約 | T-002（layer1_framework）、T-004（finding の counter_status） |
| Requirement 2：役と設定の抽象化 | T-002（役抽象名）、T-007（設定 2 層モデル） |
| Requirement 3：共通スキーマ集合 | T-004（5 スキーマ）、T-008（符号化規約検証） |
| Requirement 4：プロンプトの正本配置 | T-006（プロンプト雛形 3 件） |
| Requirement 5：パターン定義依存の除外 | T-001（配置規約に含めない方針の明示） |
| Requirement 6：検証器向けメタデータ契約 | T-003（metadata_contract）、T-005（validator_result／invalidation_marker） |
| Requirement 7：リポジトリ内資産の規則 | T-001（全資産のリポジトリ内配置）、T-007（設定の 2 層モデル） |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略の 7 項目を T-009 にまとめて継承する。各項目の対応タスクは次のとおり：

- スキーマ整合 → T-004／T-005／T-009
- 符号化規約整合 → T-004／T-005／T-008
- 枠組み整合 → T-002／T-009
- メタデータ整合 → T-003／T-009
- 語彙正本整合 → T-003／T-004／T-009
- プロンプト整合 → T-006／T-009
- 雛形整合 → T-007／T-009

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-010 のすべてが起草・実装・テスト・コミット完了
- design.md §完成判定基準の 6 項目すべてが T-010 の統合検証スクリプトで pass
- 累積テスト件数の増分が design.md §テスト戦略の 7 項目を網羅
- 各タスクの成果物配置が design.md §共有資産配置と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）

## 変更意図（Change Intent）

本タスク文書は foundation 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **タスク粒度の中庸化**：design.md の節単位（15 節）から、責務領域単位（10 タスク）に再編。タスクが細分化されすぎず、各タスクが一気通貫で完結できる単位を採る
- **テストの優先**：各タスクの完了条件に「機械的検証」を含める。実行コードを持たない `foundation` の特性に合わせ、静的検証（スキーマ／語彙／配置）で合否判定する
- **依存順の明示**：design.md §共有資産配置の責務分離を踏まえ、T-001（ディレクトリ準備）→ T-002／T-003（フレームワーク／メタデータ）→ T-004／T-005（スキーマ）→ T-006／T-007（プロンプト／設定）→ T-008／T-009／T-010（検証） の流れを固定
- **プロンプト雛形は最小実装**：本文の整備は計画書 §5.23.12.3 のとおりフェーズ 4 対象、本機能では配置・識別規則と frontmatter 形状のみ固定（T-006）
- **計画書 §5.4 軽量化方針との整合**：節ハッシュ・supersedes リンク・通過マーカー後続確認などは導入せず、`required` 配列と `x-deferred` 注記のみで mandatory／deferred を符号化

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、carry-forward register 正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。（A-017 対処 案1、2026-05-29 セッション40：全機能 tasks.md に確認手順を明示）
