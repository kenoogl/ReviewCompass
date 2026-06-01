---
spec: analysis
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-28
language: ja
---

# Tasks Document：analysis

## 概要（Overview）

本文書は `analysis`（分析機能）の実装タスクを列挙する。`analysis` は `evaluation` の成果物と `conformance-evaluation` の検査結果を入力に、4 出力先（運用ダッシュボード ／ 週次レポート ／ 監査用報告 ／ 報告書向け原データ）に向けた構造化成果物を組み立てる機能であり、読み物の本文執筆は範囲外で「構造化された入力」を整える層である。タスクは設計文書（design.md）の責務領域単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。

タスクの依存順は design.md §全体構造の 5 段（取り込み → 共通台帳生成 → 収束可視化生成 → 派生 → 陳腐化検査）と §分析向け成果物配置（`shared/` ＋ `destinations/` ＋ `figures_tables/` の 3 層構造）に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの責務領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：成果物は静的検証（スキーマ整合、構造化参照の解決可能性、束縛規則整合、語彙整合）で機械的に判定可能とする
- **contract consumer 原則**：foundation の語彙正本 7 件（`counter_status` ／ `validator_status` ／ `evidence_class` ／ `review_mode` ／ `severity` ／ `final_label` ／ `confidence_label`）および evaluation 由来の成果物配置を再定義せず参照のみで使用、本機能所有の正本（`maturity_label` 3 値 ／ `limitation_type` 4 値 ／ `fragment_type` 5 値 ／ `regeneration_status` 4 値）は本機能で確定

`analysis` 全体で 11 タスク。

## タスク一覧（Task List）

### T-001：分析向け成果物配置の準備

- **対応設計節**：design.md §分析向け成果物配置、§配置の根拠
- **対応要件**：Requirement 8 受入 1（4 出力先の最低限必須成果物）、受入 3（追跡可能性を共通保持）
- **責務**：本機能の正本出力先 `analysis/` 配下に 3 層構造（`shared/` ／ `destinations/` ／ `figures_tables/`）を新設し、各ディレクトリに配置目的を記す README を置く。`shared/` の 5 サブディレクトリ（`conformance/` ／ `convergence/` ／ `manifests/`、加えて `claim_map.json` ／ `evidence_register.json` ／ `caveat_register.json` の直下配置）、`destinations/` の 4 サブディレクトリ（`dashboard/` ／ `weekly/` ／ `audit/` ／ `reports/`）、`figures_tables/` の 2 サブディレクトリ（`table_source_bundles/` ／ `figure_source_bundles/`）を配置。テスト関連の初期フォルダ `tests/analysis/` も配置規約に従って作成（`.gitkeep` で追跡可能化、foundation T-001 ／ evaluation T-001 の方針継承）
- **前提タスク**：なし（起点）
- **成果物**：
  - `analysis/README.md`
  - `analysis/shared/README.md`
  - `analysis/shared/conformance/README.md`（F-005 対処 2026-05-28 セッション 36）
  - `analysis/shared/convergence/README.md`（F-005 対処 2026-05-28 セッション 36）
  - `analysis/shared/manifests/README.md`（F-005 対処 2026-05-28 セッション 36）
  - `analysis/shared/manifests/analysis_manifest.yaml`（空の雛形、A-001 対処 2026-05-28 セッション 36：T-002 で `analysis_logic_version` と入力被覆を書き込み）
  - `analysis/shared/manifests/analysis_manifest.schema.json`（スキーマ定義、A-001 対処 2026-05-28 セッション 36：必須項目 `analysis_logic_version` ／ 入力被覆 ／ 生成日時等）
  - `analysis/destinations/README.md`
  - `analysis/figures_tables/README.md`
  - `docs/operations/ANALYSIS.md`（アプリ側規約節を追記、計画書 §5.14.7 由来）
  - `tests/analysis/.gitkeep`
- **完了条件**：
  1. 3 層構造のディレクトリと各 README が存在し、`docs/operations/ANALYSIS.md` に「アプリ側 `.reviewcompass/analysis/`」の規約が記述されている
  2. 配置規約・命名規約の規約文書が記述された上で、README または ANALYSIS.md の人間レビューで承認されている（承認の記録方法は foundation T-001 ／ evaluation T-001 と同じ運用に従う。機械検証は規約の存在と必須節の充足までを対象とし、人間レビューでの最終承認は運用で担保、F-008 対処 2026-05-28 セッション 36）
  3. `tests/analysis/.gitkeep` が Git に追跡可能な状態である
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`tests/analysis/.gitkeep` 存在検査

### T-002：取り込み段（intake reader）

- **対応設計節**：design.md §全体構造 段 1（取り込み段）、§取り込み失敗のモデル
- **対応要件**：Requirement 1 受入 4（生ログ非利用、`evaluation` 経由）、Requirement 4 受入 1〜3（逆流禁止）
- **責務**：`evaluation` の成果物（`experiments/analysis/` 配下）と `conformance-evaluation` の成果物（`experiments/conformance/` 配下）を読み込み、欠落・読み込み失敗・陳腐化を検知して `shared/manifests/intake_failure_report.json`（実体ファイルの書き出し先は `analysis/shared/manifests/` 配下、スキーマファイルは `analysis/intake/` 配下に置く責務分離、F-015 対処 2026-05-28 セッション 36）に構造化記録する。失敗理由は 4 値（`upstream_evaluation_missing` ／ `upstream_evaluation_unreadable` ／ `upstream_evaluation_stale` ／ `conformance_evaluation_missing`）。`runtime` の生証拠を一次入力にしない方針を符号化
- **前提タスク**：T-001
- **成果物**：
  - `analysis/intake/intake_reader.py`（取り込み実装）
  - `analysis/intake/intake_failure_report.schema.json`（スキーマ定義）
  - `analysis/shared/manifests/intake_failure_report.json`（実体ファイル、F-015 対処 2026-05-28 セッション 36）
- **完了条件**：`evaluation` ／ `conformance-evaluation` の正常系成果物を読み込み正常完了、欠落 ／ 読み込み失敗 ／ 陳腐化を検知して `intake_failure_report.json` に 4 値の `intake_failure_reason` で記録、`runtime` 生証拠の一次参照経路が存在しないことが機械検証される（`grep` で `experiments/runtime/` のパス文字列が成果物コードに登場しないことを検査、F-009 対処 2026-05-28 セッション 36）、`analysis_manifest.yaml` に `analysis_logic_version` と入力被覆を書き込み（A-001 対処 2026-05-28 セッション 36：T-001 で空雛形を準備、本タスクで内容確定）
- **テスト要件**：正常系の読み込みテスト、4 値の失敗理由ごとの検知テスト、`runtime` 生証拠への一次参照がないことの構造検査（具体的に `grep -r 'experiments/runtime/' analysis/` の検出結果がゼロであることを CI で検査、F-009 対処 2026-05-28 セッション 36）、`analysis_manifest.yaml` スキーマ検証テスト（A-001 対処 2026-05-28 セッション 36）

### T-003：主張対応図と参照書式

- **対応設計節**：design.md §主張対応モデル §1〜§3（主張単位、根拠成果物の入力源、参照書式）
- **対応要件**：Requirement 1 受入 5（版付き証拠まで追跡）、受入 6（主張単位の定義）
- **責務**：`shared/claim_map.json` のスキーマと書き出し機構を実装。各エントリの必須 5 項目（`claim_id` ／ `claim_text` ／ `supporting_artifact_refs` ／ `maturity_label` ／ `stale`）と任意 4 項目（`provenance_refs` ／ `caveat_refs` ／ `stale_reason` ／ `stale_source_ref`）、条件付き必須（`stale=true` のとき `stale_reason` ／ `stale_source_ref` 必須）を符号化。参照書式（`ref_type` ／ `target_path` ／ `target_id` の構造化参照）を共通モジュールとして提供
- **前提タスク**：T-002（取り込みされた成果物を参照する必要）
- **成果物**：
  - `analysis/claim_mapping/claim_map_builder.py`
  - `analysis/claim_mapping/claim_map.schema.json`（必須 ／ 任意 ／ 条件付き必須を符号化）
  - `analysis/common/reference_format.py`（`ref_type` ／ `target_path` ／ `target_id` の構造化参照の共通モジュール）
- **完了条件**：`claim_map.schema.json` が JSON Schema として meta-schema 検証を通る、`supporting_artifact_refs` の構造化参照が `evaluation` の成果物配置に対して機械的に解決できる、`stale=true` のとき条件付き必須が機械検証される
- **テスト要件**：スキーマ検証テスト、構造化参照の解決可能性テスト（`evaluation` 成果物への `target_path` 解決）、条件付き必須テスト

### T-004：証拠台帳とレビューモード保持

- **対応設計節**：design.md §証拠台帳モデル §1〜§3（成熟度ラベル、来歴情報、レビューモードの保持）
- **対応要件**：Requirement 5（予備証拠と成熟証拠の区別、受入 6 ＝ foundation 束縛）、Requirement 6（レビューモード由来情報、受入 1〜5）
- **責務**：`shared/evidence_register.json` のスキーマと書き出し機構を実装。`maturity_label` 3 値（`mature` ／ `preliminary` ／ `exploratory`）を本機能所有の正本として確定、foundation の `evidence_class` 4 値を再定義せず参照、束縛規則（`invalid` → 報告対象外 ／ `exploratory` → `exploratory` ／ `analysis_blocked` → 報告対象外 ／ `valid` かつ安定比較集合 → `mature` ／ `valid` かつ非安定 → `preliminary`）を符号化。`evidence_class=exploratory` の証拠に `caveat_refs` を自動付与する規律（A-007 対処由来）を実装。`review_mode` を foundation 正本値として保持（値は foundation 正本を参照、再定義しない）、`supersedes` ／ `superseded_by` で置換系譜を保持
- **前提タスク**：T-002（取り込み）、T-003（参照書式の共通モジュール）
- **成果物**：
  - `analysis/evidence_register/evidence_register_builder.py`
  - `analysis/evidence_register/evidence_register.schema.json`（必須 9 項目 ＋ 任意 5 項目 ＋ 条件付き必須）
  - `analysis/evidence_register/binding_rules.py`（束縛規則の符号化、自動付与規律）
- **完了条件**：`evidence_register.schema.json` が meta-schema 検証を通る、`maturity_label` 3 値の enum が確定、束縛規則表に従って `evidence_class` → `maturity_label` の自動付与が機械検証される、`evidence_class=exploratory` の `caveat_refs` 自動付与が機械検証される、foundation 3 語彙（`evidence_class` ／ `review_mode` ／ `counter_status`）を再定義せず参照のみで使用していることが機械検証される（`final_label` は本タスクのスキーマに登場しないため参照対象から除外、A-006 対処 2026-05-28 セッション 36）
- **テスト要件**：束縛規則の網羅テスト（5 ケース）、自動付与規律テスト、foundation 語彙正本の参照のみ使用検証、置換系譜（`supersedes` ／ `superseded_by`）テスト

### T-005：注意点と限界の台帳

- **対応設計節**：design.md §注意点と限界のモデル
- **対応要件**：Requirement 3（注意点と限界の追跡、受入 1〜5）、Requirement 6 受入 4（混在レビューモードの自動検知）
- **責務**：`shared/caveat_register.json` のスキーマと書き出し機構を実装。`limitation_type` 4 値（`invalid_data_exclusion` ／ `partial_evidence` ／ `methodological_limitation` ／ `mixed_review_mode`）を本機能所有の正本として確定。`mixed_review_mode_detector.py` を T-005 が提供（detector ロジックの所有、書き戻し責任は T-009 の派生段が持つ、A-003 対処 2026-05-28 セッション 36、design.md §証拠台帳モデル §3「派生段が検知主体」と整合）。`mixed_review_mode` 自動検知（報告集合の `review_mode` が 2 値以上のとき自動付与）を派生段（destination deriver）に組み込み。必須 3 項目（`caveat_id` ／ `limitation_type` ／ `narrative_note`）と任意項目、条件付き必須（`applies_to_claim_refs` と `applies_to_artifact_refs` の少なくとも一方は非空）を符号化
- **前提タスク**：T-002、T-004
- **成果物**：
  - `analysis/caveat_register/caveat_register_builder.py`
  - `analysis/caveat_register/caveat_register.schema.json`
  - `analysis/caveat_register/mixed_review_mode_detector.py`（混在検知ロジック）
- **完了条件**：`caveat_register.schema.json` が meta-schema 検証を通る、`limitation_type` 4 値の enum が確定、`mixed_review_mode` 自動検知が報告集合内の `review_mode` 2 値以上のときに発火、条件付き必須が機械検証される
- **テスト要件**：スキーマ検証、4 値 `limitation_type` の enum テスト、混在検知の発火テスト（単一モード ／ 2 値混在 ／ 3 値混在の 3 ケース）、条件付き必須テスト

### T-006：図表束と報告断片

- **対応設計節**：design.md §図表束モデル、§報告断片モデル
- **対応要件**：Requirement 2（分析向けデータ契約、受入 1〜5）
- **責務**：`figures_tables/table_source_bundles/<table_id>.json` ／ `figures_tables/figure_source_bundles/<figure_id>.json` のスキーマと書き出し機構を実装。表は必須 5 項目（`table_id` ／ `source_artifact_refs` ／ `field_projection` ／ `maturity_label` ／ `applicable_destinations`）、図は必須 5 項目（`figure_id` ／ `source_artifact_refs` ／ `plot_contract` ／ `maturity_label` ／ `applicable_destinations`）。報告断片は `fragment_type` 5 値（`claim_summary` ／ `method_note` ／ `limitation_note` ／ `comparison_summary` ／ `trend_summary`）を本機能所有の正本として確定、複数出典の成熟度集約規則（保守的な値を採る、出典別保持）を符号化。**報告断片の必須 6 項目すべて**（`fragment_id` ／ `fragment_type` ／ `source_artifact_refs` ／ `maturity_label` ／ `text_stub` ／ `applicable_destinations`）を符号化（A-007 対処 2026-05-28 セッション 36）
- **前提タスク**：T-003（参照書式）、T-004（`maturity_label`）
- **成果物**：
  - `analysis/figures_tables/table_bundle_builder.py`
  - `analysis/figures_tables/figure_bundle_builder.py`
  - `analysis/figures_tables/table_bundle.schema.json`
  - `analysis/figures_tables/figure_bundle.schema.json`
  - `analysis/fragments/fragment_builder.py`
  - `analysis/fragments/fragment.schema.json`（`fragment_type` 5 値 enum を含む）
- **完了条件**：3 スキーマすべて meta-schema 検証を通る、`fragment_type` 5 値の enum が確定、成熟度集約規則（保守的な値、出典別保持）が機械検証される
- **テスト要件**：3 スキーマ検証、`fragment_type` enum テスト、成熟度集約規則テスト（出典の成熟度が異なるときに保守的な値を採る、出典別が保持されている）

### T-007：レビュー収束過程の可視化

- **対応設計節**：design.md §レビュー収束過程の可視化モデル §1〜§3
- **対応要件**：Requirement 7（レビュー収束過程の可視化、受入 1〜4）
- **責務**：`shared/convergence/role_diff.json` と `shared/convergence/mode_diff.json` のスキーマと書き出し機構を実装。`role_diff` は出典 `evaluation` の `experiments/analysis/roles/role_diff_report.json`（evaluation Req 9 受入 8、A-011 対処）を読み込んで内部表現に変換、最低限 4 要素（`feature` ／ `role` ／ `findings_summary` ／ `target`）、`findings_summary` は条件付き必須（`by_final_label` は `role=judgment` のとき必須、`by_counter_status` は `role=adversarial` のとき必須）。`mode_diff` は出典 `evaluation` の `modes/mode_diff_report.json`、最低限 4 要素。本機能のレビュー収束可視化は `evaluation` の標準集計と区別、`evaluation` 派生として位置付け。**前提タスクに T-005 を含めない根拠**：`role_diff.json` の `evidence_refs` は T-004 の証拠台帳または入力成果物参照に解決されるもので、`caveat_register`（T-005）の生成結果には依存しないため（F-007 対処 2026-05-28 セッション 36、外部 6 モデル多数派融合判断）
- **前提タスク**：T-002、T-003、T-004
- **成果物**：
  - `analysis/convergence/role_diff_builder.py`
  - `analysis/convergence/mode_diff_builder.py`
  - `analysis/convergence/role_diff.schema.json`
  - `analysis/convergence/mode_diff.schema.json`
- **完了条件**：2 スキーマとも meta-schema 検証を通る、`role_diff` の条件付き必須が機械検証される、`mode_diff` の `review_mode` が foundation 正本を参照のみで使用していることが機械検証される、本機能の可視化結果が `evaluation` のメトリクス契約を上書きしないことが次の 3 点で構造的に保証される（A-002 対処 2026-05-28 セッション 36）：(1) **書き込み先パス制約**：本タスクが出力するすべてのファイルが `analysis/destinations/` 配下のみであることを CI で `grep` または静的解析で機械検証、`evaluation/` 配下への書き込みがゼロであることも同検査で確認。(2) **スキーマ非重複制約**：`role_diff.json` ／ `mode_diff.json` のトップレベルフィールド名・型定義が `evaluation` のメトリクス契約と重複しないことをスキーマ差分スクリプトで機械検証（`evaluation` 側スキーマが実体化次第追加）。(3) **T-011 との責務境界明記**：(1)(2) は静的・単体レベルの構造保証であり、実行時の入出力整合（`evaluation` 結果が `analysis` を経由した後も値が変化しないこと）は T-011 双方向整合テストの責務とする
- **テスト要件**：2 スキーマ検証、`role_diff` 条件付き必須テスト（3 役それぞれのケース）、`mode_diff` foundation 語彙参照テスト、出典との対応テスト（`evaluation` の `role_diff_report.json` ／ `mode_diff_report.json` を入力にしたときの正常変換）

### T-008：conformance-evaluation 取り込み

- **対応設計節**：design.md §conformance-evaluation メトリクス取り込みモデル §1〜§3
- **対応要件**：Requirement 8 受入 5（`conformance-evaluation` 取り込み）、Requirement 4 受入 4（`conformance-evaluation` 判定の不干渉）
- **責務**：`shared/conformance/conformance_intake.json`（正本）のスキーマと書き出し機構を実装。一方向取り込み（`analysis ← conformance-evaluation` の read）の境界を符号化、判定基準の変更や判定結果の上書きを構造的に禁止。`conformance-evaluation` 設計 §14.5（A-015 対処）のスキーマ（必須 9 件 ＋ 任意 2 件）に従って取り込み。出力先別の加工版（`destinations/audit/conformance_violations_detail.json` ／ `destinations/reports/conformance_compliance_trend.json`）は正本の `conformance_run_ref` を参照することで派生関係を機械的に確認できる。**前提タスクに T-004 を含めない根拠**：`conformance_intake.json` は `conformance-evaluation` の検査結果を判定せずに取り込むのみで、`maturity_label` や証拠台帳由来の解釈情報を参照しないため（F-007 対処 2026-05-28 セッション 36、外部 6 モデル多数派融合判断）
- **前提タスク**：T-002（取り込み）、T-003（参照書式）
- **成果物**：
  - `analysis/conformance_intake/conformance_intake_builder.py`
  - `analysis/conformance_intake/conformance_intake.schema.json`（必須 6 項目）
  - `analysis/conformance_intake/derived_audit_writer.py`（監査用加工版）
  - `analysis/conformance_intake/derived_reports_writer.py`（報告書向け加工版）
- **完了条件**：`conformance_intake.schema.json` が meta-schema 検証を通る、必須 6 項目（`conformance_run_ref` ／ `assessment_summary` ／ `violation_findings` ／ `compliance_rate` ／ `included_disciplines` ／ `intake_at`）が確定（**注**：必須 6 項目は上流 `conformance-evaluation` §14.5 の必須 9 件を本機能の取り込みスキーマに再編成したもの。9 件から 6 項目への対応マッピングは `design.md` §`conformance-evaluation` メトリクス取り込みモデル §2 を参照のこと（詳細は別途確定、DVT-A003 として登録、A-008 対処 2026-05-28 セッション 36））、両加工版が正本の `conformance_run_ref` を参照していることが機械検証される、判定基準の変更経路 ／ 判定結果の上書き経路が存在しないことが構造検査される
- **テスト要件**：スキーマ検証、必須 6 項目存在テスト、両加工版の派生関係テスト、判定不干渉の構造検査

### T-009：出力先別の派生

- **対応設計節**：design.md §出力先別の派生モデル §1〜§5
- **対応要件**：Requirement 8 受入 1〜4（4 出力先の最低限必須成果物、共通／派生の分離、加工方針の版管理）
- **責務**：4 出力先（`dashboard` ／ `weekly` ／ `audit` ／ `reports`）ごとの派生機構（`destination deriver`）を実装。各出力先の `manifest.yaml` に必須 8 項目（`destination` ／ `analysis_logic_version` ／ `derivation_contract_version` ／ `included_evidence_refs` ／ `included_caveat_refs` ／ `granularity_profile` ／ `summary_level` ／ `review_mode_mixed`）を記録、`mixed_review_mode` 検知時は `caveat_register` に自動付与（T-005 と連動）。4 出力先それぞれの最低限必須成果物（運用ダッシュボード ／ 週次レポート ／ 監査用報告 ／ 報告書向け原データ）を生成
- **前提タスク**：T-003〜T-008（共通台帳群と取り込み）
- **成果物**：
  - `analysis/destinations/destination_deriver.py`
  - `analysis/destinations/manifest.schema.json`（必須 8 項目）
  - `analysis/destinations/dashboard_writer.py`（`operations_summary.json`）
  - `analysis/destinations/weekly_writer.py`（`trend_summary.json`）
  - `analysis/destinations/audit_writer.py`（`invalidation_index.json` ／ `validator_failure_trace.json` ／ `discipline_violation_index.json`、`conformance_violations_detail.json` は T-008 `derived_audit_writer.py` の単独所有として削除、A-009 対処 2026-05-28 セッション 36）
  - `analysis/destinations/reports_writer.py`（`claim_evidence_trace.json` ／ `treatment_comparison_report.json` ／ `mode_comparison_report.json` ／ `conformance_compliance_trend.json`）
- **完了条件**：`manifest.schema.json` が meta-schema 検証を通る、必須 8 項目が確定、4 出力先それぞれの最低限必須成果物が design.md §出力先ごとの最低限必須成果物の表と一致、`derivation_contract_version` の更新が `manifest.yaml` の `superseded_versions` フィールドに前版 ref として記録され、版番号が単調増加することが機械検証される（F-010 対処 2026-05-28 セッション 36）、`mixed_review_mode` 検知時の `caveat_register` への書き込みは追加のみで上書き禁止（append-only モード）であることが機械検証される（A-003 対処 2026-05-28 セッション 36）
- **テスト要件**：`manifest.schema.json` 検証、4 出力先の必須成果物存在テスト、`review_mode_mixed` 検知時の `caveat_register` 自動付与テスト（T-005 連動）、版管理（`superseded` 履歴）テスト

### T-010：陳腐化伝播と再生成登録

- **対応設計節**：design.md §陳腐化伝播の継承 §1〜§3
- **対応要件**：Requirement 2 受入 6（陳腐化時の再生成要求）
- **責務**：`shared/manifests/staleness_register.json` のスキーマと書き出し機構を実装。`stale` ／ `stale_reason` ／ `stale_source_ref` の陳腐化標識を本機能の派生成果物（証拠台帳エントリ ／ 主張対応図エントリ ／ 報告断片 ／ 図表束）に伝播。再生成対象の登録条件 3 件（`evaluation` の `staleness_register.json` 新規エントリ ／ 依存成果物の `stale` が真に変わる ／ `conformance-evaluation` 検査結果の更新）を符号化。`regeneration_status` 4 値（`pending` ／ `in_progress` ／ `completed` ／ `failed`）を本機能所有の正本として確定
- **前提タスク**：T-003〜T-009（陳腐化伝播対象の派生成果物すべて）
- **成果物**：
  - `analysis/staleness/staleness_checker.py`
  - `analysis/staleness/staleness_register.schema.json`（必須 4 項目 ＋ 任意 1 項目）
- **完了条件**：`staleness_register.schema.json` が meta-schema 検証を通る、`regeneration_status` 4 値の enum が確定、再生成対象の登録条件 3 件が **timestamp 比較ベース** で機械検証される（A-012 対処 2026-05-28 セッション 36：再生成側成果物の生成時刻が入力側成果物の最終更新時刻より古い場合に登録、誤検出方向は安全側＝過剰生成で見逃しでない、単一マシンまたは同期 CI 環境を前提）、陳腐化標識の派生成果物への伝播が機械検証される
- **テスト要件**：スキーマ検証、4 値 enum テスト、3 件の登録条件発火テスト、`failed` からの遷移（任意）テスト

### T-011：テスト戦略全体の整備

- **対応設計節**：design.md §テスト戦略 §1〜§5
- **対応要件**：本機能全要件の機械的合否判定、foundation／evaluation 語彙正本の参照のみ使用の機械検証、要件追跡表の双方向整合、DVT 解除確認
- **責務**：design.md §テスト戦略で定義された 5 検証点（証拠追跡性 ／ 無声昇格の検出 ／ 混在レビューモードの注意点検証 ／ 陳腐化再生成の確認 ／ `conformance-evaluation` 取り込みの整合）をすべて Python テストとして整備。pytest で一括実行可能。foundation との接続部（語彙正本 7 件の参照のみで使用、再定義していないこと）と evaluation との接続部（成果物配置の参照のみで使用）の機械検証を含める。本機能所有の正本（`maturity_label` 3 値 ／ `limitation_type` 4 値 ／ `fragment_type` 5 値 ／ `regeneration_status` 4 値）が T-004 ／ T-005 ／ T-006 ／ T-010 の成果物で正本確定されていることの機械検証。要件追跡表と各タスク本文の対応要件欄の双方向整合チェック（foundation T-010 ／ runtime T-011 ／ evaluation T-011 の方針継承）。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化（evaluation T-011 の方針継承）。**テスト責務分担の明示**（A-004 対処 2026-05-28 セッション 36）：T-003 単体テスト＝個別 finding の参照解決可能性検証、T-011 統合テスト（`test_traceability.py`）＝全証拠の追跡経路を通すスモークテスト、両者は二層検証で重複ではなく補完関係。**テストファイルごとの担務明示**（F-011 ／ F-012 対処 2026-05-28 セッション 36）：`test_evidence_register.py` が「無声昇格検出統合版」（design.md §テスト戦略 §2 由来）を担う（T-004 単体・T-011 統合の二層意図）、`test_destinations.py` が「混在レビューモード検知の統合テスト」（T-005 detector 提供 ／ T-009 単体「付与ロジック」／ T-011 統合「出力先全体の一貫性」の責務分担）を担う
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010
- **成果物**：`tests/analysis/` 配下のテストファイル群（`test_intake.py` ／ `test_claim_map.py` ／ `test_evidence_register.py` ／ `test_caveat_register.py` ／ `test_figures_fragments.py` ／ `test_convergence.py` ／ `test_conformance_intake.py` ／ `test_destinations.py` ／ `test_staleness.py` ／ `test_traceability.py` の 10 ファイル相当）
- **完了条件**：すべての pytest が pass、5 検証点を網羅、foundation 7 語彙正本＋evaluation 成果物配置の参照のみ使用が機械検証される、analysis 所有正本（`maturity_label` ／ `limitation_type` ／ `fragment_type` ／ `regeneration_status`）が正本確定されている、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：主張単位の定義 | T-003（claim_id 構造、主張単位） |
| Requirement 1 受入 2：実行と分析の来歴を保持 | T-004（来歴情報、F-001 対処 2026-05-28 セッション 36 で個別行分解） |
| Requirement 1 受入 3：直接証拠と注意点付き証拠を区別 | T-004（証拠区別、F-001 対処 2026-05-28 セッション 36 で個別行分解） |
| Requirement 1 受入 4：生ログ非利用、`evaluation` 経由 | T-002（受入 4） |
| Requirement 1 受入 5：版付き証拠まで追跡 | T-003（supporting_artifact_refs の構造化参照） |
| Requirement 1 受入 6：主張単位の定義 | T-003（claim_id） |
| Requirement 2 受入 1：図表束・出力構成 | T-006（図表束、F-002 対処 2026-05-28 セッション 36 で受入別 × 担当タスク単位に展開） |
| Requirement 2 受入 2：evaluation 出力への来歴連結 | T-006（source_artifact_refs、F-002 対処 2026-05-28 セッション 36） |
| Requirement 2 受入 3：生証拠と分析向け成果物の分離保持 | T-001（配置）＋ T-006（F-002 対処 2026-05-28 セッション 36） |
| Requirement 2 受入 4：再生成支援 | T-006（fragment_builder.py、F-002 対処 2026-05-28 セッション 36） |
| Requirement 2 受入 5：書式都合によるスキーマ変更強制禁止 | T-009（derivation_contract_version 版管理、F-002 対処 2026-05-28 セッション 36 で T-006 から T-009 に正しく紐付け） |
| Requirement 2 受入 6：陳腐化再生成 | T-010 |
| Requirement 3 受入 1：証拠源に関連する注意点メタデータの保持 | T-005（caveat メタデータ、F-003 対処 2026-05-28 セッション 36 で個別行分解） |
| Requirement 3 受入 2：限界の追跡 | T-005（caveat_register、4 値 limitation_type） |
| Requirement 3 受入 3：手作業で読み直さずに注意点を参照 | T-005（参照機構、F-003 対処 2026-05-28 セッション 36 で個別行分解） |
| Requirement 3 受入 4：予備ラベル付与の支援 | T-005（予備ラベル支援、F-003 対処 2026-05-28 セッション 36 で個別行分解） |
| Requirement 3 受入 5：注意点台帳の正本管理 | T-005（正本管理） |
| Requirement 4 受入 1〜3：`runtime` ／ `evaluation` ロジックからの分離（逆流禁止） | T-002（受入 1〜3 ＝逆流禁止、`runtime` 非結合） |
| Requirement 4 受入 4：`conformance-evaluation` 判定の不干渉 | T-008（受入 4 ＝判定不干渉） |
| Requirement 4 受入 5：下流の叙述変換を明示的かつ版管理可能 | T-009（`derivation_contract_version` ／ `manifest.yaml` 版管理、A-011 対処 2026-05-28 セッション 36 で個別行追加） |
| Requirement 5：予備証拠と成熟証拠の区別 | T-004（`maturity_label` 3 値、束縛規則、自動付与） |
| Requirement 6：報告におけるレビューモード由来情報 | T-004（受入 1〜3 ／ 5 ＝ `review_mode` 保持、置換系譜）、T-005（受入 4 ＝混在検知）、T-009（受入 4 連動 ＝派生段の `review_mode_mixed` フィールド） |
| Requirement 7：レビュー収束過程の可視化 | T-007（role_diff、mode_diff） |
| Requirement 8：4 種の出力先への変換 | T-001（受入 1 ＝配置）、T-008（受入 5 ＝ `conformance-evaluation` 取り込み）、T-009（受入 1〜4 ＝派生、4 出力先成果物、共通／派生分離、版管理） |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略の 5 検証点を T-011 にまとめて継承する。各検証点の対応タスクは次のとおり：

- 証拠追跡性の機械検証 → T-003 ／ T-011
- 無声昇格の検出 → T-004 ／ T-011
- 混在レビューモードの注意点検証 → T-005 ／ T-009 ／ T-011
- 陳腐化再生成の確認 → T-010 ／ T-011
- `conformance-evaluation` 取り込みの整合 → T-008 ／ T-011

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-011 のすべてが起草・実装・テスト・コミット完了
- design.md §完成判定基準の 8 項目すべてが T-011 の統合テストで pass
- foundation の 7 語彙正本（`counter_status` ／ `validator_status` ／ `evidence_class` ／ `review_mode` ／ `severity` ／ `final_label` ／ `confidence_label`）を analysis が再定義せず参照のみで使用していることが、機械検証で確認できる
- evaluation の成果物配置（`experiments/analysis/` 配下、`comparisons/` ／ `classifications/` ／ `caveats/` ／ `modes/` ／ `roles/` ／ `metrics/` ／ `manifests/`）を analysis が一次入力として参照のみで使用していることが、機械検証で確認できる
- analysis 所有の正本（`maturity_label` 3 値 ／ `limitation_type` 4 値 ／ `fragment_type` 5 値 ／ `regeneration_status` 4 値）が T-004 ／ T-005 ／ T-006 ／ T-010 の成果物で正本として確定されている
- 各タスクの成果物配置が design.md §分析向け成果物配置と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は analysis 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの責務領域。foundation T-001〜T-010 ／ runtime T-001〜T-011 ／ evaluation T-001〜T-011 の粒度方針を継承
- **責務領域単位の分離**：design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **依存順の明示**：T-001（配置）→ T-002（取り込み）→ T-003〜T-008（共通台帳群）→ T-009（派生）→ T-010（陳腐化）→ T-011（統合テスト）の流れを固定
- **共通／派生 2 層構造の実装**：design.md 判断 5 を実装側で踏襲、共通台帳（`shared/`）と出力先別派生（`destinations/`）を別タスク（T-003〜T-008 と T-009）に切り分け
- **contract consumer 原則の徹底**：foundation 7 語彙正本＋evaluation 成果物配置を再定義せず参照のみで使用、本機能所有の正本（`maturity_label` ／ `limitation_type` ／ `fragment_type` ／ `regeneration_status`）は本機能で確定
- **テスト戦略の継承**：design.md §テスト戦略の 5 検証点を T-011 で網羅
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：foundation T-010 ／ runtime T-011 ／ evaluation T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定上流仕様（`workflow-management` 設計 ／ 過渡的対処の `mixed_review_mode` 運用必要性）を DVT で集約管理、T-011 完了条件で未解除項目がないことをゲート化（evaluation T-011 の方針継承）
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **計画書 §5.4 軽量化方針との整合**：節ハッシュ・supersedes リンク・通過マーカー後続確認などは導入せず、`required` 配列と `x-deferred` 注記、構造化参照、機械検証可能な束縛規則のみで mandatory ／ deferred を符号化

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。evaluation T-011 の DVT-001 と同型運用（A-007 別案 A 採用、2026-05-27 セッション 33）。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-A001 | T-009 | `workflow-management` の所定手続き実行履歴の取り込み元パスと項目（運用ダッシュボード派生の根拠、design.md §先送り論点 A-002 由来）。`workflow-management` 設計の design alignment 段で確定後に T-009 完了条件と整合を再確認 | `workflow-management` 仕様 tasks 段完了時に T-009 完了条件と整合を再確認 | 未解除 |
| DVT-A002 | T-005 | `limitation_type=mixed_review_mode`（過渡的対処）の運用必要性。フェーズ 4 完了後、各レビューモードの恒久運用が定着した時点で、本値が日常業務で出現しない場合は廃止または条件付き運用への変更を検討（design.md §先送り論点 F-012＋A-009 由来） | フェーズ 4 完了後の混在検知頻度の観測結果による再評価 | 未解除（フェーズ 4 完了まで延期） |
| DVT-A003 | T-008 | `conformance_intake.json` の必須 6 項目と上流 `conformance-evaluation` §14.5 の必須 9 件の対応マッピング（9 件→6 項目の集約・除外・統合の規則）が `design.md` 側でも `tasks.md` 側でも詳細未確定（A-008 対処 2026-05-28 セッション 36 で TBD 付き仮記述を入れたが、具体マッピングは未定）| `conformance-evaluation` の正本（§14.5 のスキーマ）が実体化した時点で、9 件→6 項目の対応表を `design.md` §`conformance-evaluation` メトリクス取り込みモデル §2 と `tasks.md` T-008 完了条件に反映 | 未解除 |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-011 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、`.reviewcompass/pending-cross-feature-findings.md` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価と同根問題集約は本機能では実施せず、機能横断段で一括実施する（(Q2) ／ (ニ) 採用、計画書 §5.5 ／ §5.9.6 反映済み）。
