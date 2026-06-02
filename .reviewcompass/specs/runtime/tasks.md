---
spec: runtime
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-27
language: ja
---

# Tasks Document：runtime

## 概要（Overview）

本文書は `runtime` 機能の実装タスクを列挙する。`runtime` は `foundation` が定義する共有資産層（shared asset layer）の上で、レビュー実行（review session）を駆動するオーケストレーション層であり、実装コードを持つ。タスクは設計文書（design.md）の責務領域単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。

タスクの依存順は design.md の §全体構造で固定された 4 役（session controller／step executors／evidence writer／validation bridge）の責務分離と、§実行成果物配置の生成順序に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの責務領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：実装機能は単体テスト（pytest）で検証可能とする。言語モデル呼び出しは差し替え点を設け、固定応答で決定的に検証する
- **foundation contract consumer 原則**：runtime は foundation の語彙正本（foundation 所有は foundation/design.md §判断 7 の全 7 件。うち runtime が参照するのは 6 件で、`confidence_label` は推定タスク用のため対象外）を再定義・縮約せず、参照のみで使用する（runtime/design.md §判断 6 準拠）

`runtime` 全体で 11 タスク。

## タスク一覧（Task List）

### T-001：実行ディレクトリ構造と命名規約

- **対応設計節**：design.md §実行成果物配置、§配置の根拠、§配置の運用ルール
- **対応要件**：Requirement 1 受入 6（実行ディレクトリ配置と段ファイル命名の所有）、Requirement 4 受入 1（foundation スキーマ準拠の実行レベル証拠出力）
- **責務**：`experiments/runs/<run_id>/` 配下のディレクトリ構造（`run_manifest.yaml` ／ `review_case.json` ／ `steps/` ／ `decisions/` ／ `failures/failure_observations/` ／ `validation/` ／ `derived/`）を仕様文書として新設し（実体の物理ディレクトリ作成は実行時に T-002 session controller が `run_id` ごとに行う、本タスクは仕様文書と配置運用ルールの定義のみ）、各サブディレクトリに配置目的を記す README を置く。生証拠不変・派生分離の配置ルールを `docs/operations/RUNTIME.md` に記述
- **前提タスク**：なし（起点、foundation T-001 完了を前提とする外部依存あり）
- **成果物**：
  - `runtime/runtime_core/run_layout/README.md`（実行ディレクトリ構造の解説）
  - `runtime/runtime_core/run_layout/layout_spec.yaml`（配置仕様の機械可読版）
  - `docs/operations/RUNTIME.md`（配置運用ルールを記述、または該当節を追記）
- **完了条件**：
  1. 配置仕様 YAML が解析可能で、必須サブディレクトリ 6 件（`steps`／`decisions`／`failures/failure_observations`／`validation`／`derived` ＋ ルート）が宣言されている
  2. 配置の運用ルール（生証拠不変、派生分離、`review_case.json` 唯一の横断正本）が `docs/operations/RUNTIME.md` に記述された上で、README または RUNTIME.md の人間レビューで承認されていること（承認の記録方法は foundation tasks T-001 と同じ運用に従う）
- **テスト要件**：配置仕様 YAML の解析テスト、必須サブディレクトリ宣言の存在検査

### T-002：session controller（セッション制御器）

- **対応設計節**：design.md §全体構造（session controller 役）、§セッションモデル §1〜§3、§Reference-Free Runtime Entry Principle
- **対応要件**：Requirement 1 受入 1〜3（4 段パイプライン制御）、Requirement 1 受入 5（実行終了境界の露出）、Requirement 5（人間決定の組み込みのうち決定単位提示の起点）、Requirement 6 受入 6（`review_mode=runtime_mediated` 付与の起点）、Requirement 7（再生対応の実行時記録）
- **責務**：実行開始時のセッション入力固定、`run_manifest.yaml` 生成、`run_status` 4 値（`created`／`in_progress`／`closed`／`orchestration_failed`）の遷移制御。実行入口を事例マニフェストまたは明示入力群に限定し、特定事例の暗黙既定値を排除（Reference-Free Runtime Entry Principle）
- **前提タスク**：T-001
- **成果物**：
  - `runtime/runtime_core/session_controller.py`（セッション制御器の本体）
  - `runtime/runtime_core/session_inputs_schema.yaml`（セッション入力の必須項目集合）
- **完了条件**：
  1. セッション制御器が `run_id`／`target_id`／`target_artifact_hash`／`source_repository_id`／`source_revision`／`phase_profile`／`treatment`／`review_mode`／`protocol_version`／`runtime_version`／`prompt_set_version`／`schema_set_version`／`config_version`／`config_hash`／運用者識別子／`started_at` の 16 項目を `run_manifest.yaml` に書き込む
  2. `run_status` の状態遷移が `created` → `in_progress` → `closed`（または `orchestration_failed`）の 1 方向に制限される
  3. 特定事例の暗黙既定値（事例名・識別子等）を入口で受けない
- **テスト要件**：セッション開始時の `run_manifest.yaml` 生成テスト、`run_status` 不正遷移の拒否テスト（例：`created` → `closed` 直接遷移を拒否）、Reference-Free 入口の境界テスト

### T-003：treatment × phase/profile 選択軸

- **対応設計節**：design.md §セッションモデル §4 phase／profile と treatment の軸
- **対応要件**：Requirement 2（処理方式対応の実行、受入 1〜5）、Requirement 8（フェーズ対応のレビュープロファイル、受入 1〜5）
- **責務**：処理方式（`treatment`、3 値正本：`primary`／`adversarial`／`judgment`）とフェーズプロファイル（`phase_profile`、4 値正本：`intent`／`requirements`／`design`／`tasks`）を独立軸として実装。両者を実行メタデータに第一級属性として記録し、選択軸の混同を構造的に防ぐ
- **前提タスク**：T-002
- **成果物**：
  - `runtime/runtime_core/treatment_vocab.yaml`（`treatment` 3 値正本）
  - `runtime/runtime_core/phase_profile_vocab.yaml`（`phase_profile` 4 値正本）
  - `runtime/runtime_core/axis_selector.py`（軸選択ロジック）
- **完了条件**：両軸の語彙 YAML が解析可能で、`treatment` 3 値と `phase_profile` 4 値が宣言されている。軸選択ロジックが両軸を独立に扱い、相互依存しない（操作的定義：一方の軸の値を変更しても他方の軸選択ロジック出力が変化しないことを機械検証で確認）
- **テスト要件**：語彙 YAML の値テスト、軸選択の独立性テスト（一方の変更が他方に影響しないこと）、無効値の拒否テスト

### T-004：Step A／B／C 実行器（言語モデル呼び出しを含む 3 段）

- **対応設計節**：design.md §ステップ実行モデル Step A／Step B／Step C、§プロンプト解決モデル（役と段の対応）
- **対応要件**：Requirement 1 受入 1〜3（4 段パイプライン）、Requirement 2 受入 3〜5（treatment 別の段実行・省略）、Requirement 4 受入 1〜6（構造化された証拠の出力）、Requirement 6 受入 6（`runtime_mediated` レビューモード付与）、Requirement 10 受入 2（固定パターン非依存の動的判定）
- **責務**：Step A（primary detection、主役検出）／Step B（adversarial review、敵対レビュー）／Step C（judgment、判定）の 3 段実行器を実装。各段の入出力、言語モデル呼び出し境界、所見記録（`counter_status` 3 値正本の参照を含む）、段別メタデータ出力（`steps/step_a_primary_detection.json` ／ `step_b_adversarial_review.json` ／ `step_c_judgment.json`）を担う。`counter_status` の 3 値（`counter_evidence_raised`／`no_counter_evidence_after_challenge`／`not_assessed`）を Step B で必ず設定し、「反証なし」と「反証を試みていない」を曖昧にしない
- **前提タスク**：T-002、T-003、T-006（プロンプト解決機構）
- **成果物**：
  - `runtime/runtime_core/step_executors/step_a_primary_detection.py`
  - `runtime/runtime_core/step_executors/step_b_adversarial_review.py`
  - `runtime/runtime_core/step_executors/step_c_judgment.py`
  - `runtime/runtime_core/step_executors/llm_invocation_boundary.py`（言語モデル呼び出しの差し替え点）
- **完了条件**：3 段が独立に実行可能、各段が `steps/step_<x>_*.json` を foundation スキーマ準拠で出力。Step B が全所見に `counter_status` を foundation 3 値正本から設定。`review_mode=runtime_mediated` が各段の出力に付与される
- **テスト要件**：3 段の入出力テスト（固定応答による決定的検証）、Step B の `counter_status` 必須テスト、Step C の `final_label` foundation 3 値正本テスト（foundation tasks T-004 topic-05 採用の参照節と同水準で foundation 語彙正本ファイルへの参照を明示）

### T-005：Step D 実行器（機械統合、言語モデル非依存）

- **対応設計節**：design.md §ステップ実行モデル Step D Integration（統合手順 6 ステップ）
- **対応要件**：Requirement 1 受入 1〜3（4 段パイプラインの完結）、Requirement 4 受入 2〜5（由来表示と判定連結、生証拠と派生要約の分離）、Requirement 5 受入 1（決定単位提示）
- **責務**：前段（Step A／B、treatment に応じ Step C）の出力から、追加の言語モデル呼び出しなしで `decision_units`（決定単位）と統合成果物を機械的に生成。統合手順 6 ステップ（所見収集 → 判定紐付け → 決定単位集約 → 推奨措置決定 → 実行終了準備判定 → 出力）を実装。`steps/step_d_integration.json` と `decisions/decision_units.json`（人間決定未確定の初期版）、`review_case.json` の `integration_summary` 項目を出力
- **前提タスク**：T-004（Step A／B／C の出力が前提）
- **成果物**：
  - `runtime/runtime_core/step_executors/step_d_integration.py`（機械統合本体、言語モデル呼び出しを行わない）
- **完了条件**：固定の Step A／B／C 出力を入力に与えると、決定単位生成と統合成果物が決定的に再現可能。言語モデル呼び出しを一切含まない（design.md §判断 4「decision_unit_id` と人間判定の接続」と整合）
- **テスト要件**：固定入力に対する決定的出力テスト、treatment 別の挙動テスト（Step C 非実行時の判定紐付けスキップ等）、`integration_summary` の foundation スキーマ準拠テスト

### T-006：プロンプト解決機構

- **対応設計節**：design.md §プロンプト解決モデル、§フェーズ対応レビュープロファイル §プロンプト上書きの選択
- **対応要件**：Requirement 3（プロンプト解決と版追跡、受入 1〜5）、Requirement 8 受入 6（複数候補時のプロンプト上書き解決）
- **責務**：foundation 正本プロンプトと runtime 所有のフェーズ／役上書きプロンプトを 2 階層で解決。`prompt_artifact_path` ／ `prompt_id` ／ `prompt_version` ／ `role` を各段の記録に必ず付与。一意解決できない場合は明示的に失敗（Requirement 3 受入 4）、リポジトリ外記憶への依存を禁止（Requirement 3 受入 5）。複数候補時は runtime 所有の選択方針で解決（Requirement 8 受入 6、Requirement 3 との対象シナリオ差を遵守）
- **前提タスク**：T-001（配置先の準備）、T-003（phase_profile 語彙確定。プロンプト上書きパス解決で phase_profile を参照するため）
- **成果物**：
  - `runtime/runtime_core/prompt_resolver/resolver.py`（解決ロジック本体）
  - `runtime/runtime_core/prompt_resolver/override_paths.yaml`（runtime 所有の上書きパス規約）
- **完了条件**：foundation 正本パスと runtime 上書きパスから一意解決可能、複数候補時に選択方針が機械的に適用される、一意解決失敗時に明示的失敗を返す
- **テスト要件**：正常解決テスト、複数候補時の選択テスト、一意解決失敗時の失敗テスト（リポジトリ外パスの拒否を含む）

### T-007：決定単位と人間署名記録

- **対応設計節**：design.md §決定単位モデル、§人間署名記録
- **対応要件**：Requirement 5（人間決定の組み込み、受入 1〜5）、Requirement 6 受入 9（実行終了境界の順序の起点）
- **責務**：T-005 が生成した `decisions/decision_units.json`（初期版）への人間決定（承認・却下・保留）の付加、`decisions/human_signoff.json` の出力。`human_signoff_status` を foundation 4 値正本（`pending`／`approved`／`rejected`／`deferred`）から設定。人間決定の不在と明示的な保留／却下を区別（Requirement 5 受入 3）、大規模言語モデル所見を確認済みレビュー出力に黙示的に自動採用しない（Requirement 5 受入 5）
- **前提タスク**：T-005（決定単位の生成元）
- **成果物**：
  - `runtime/runtime_core/decisions/decision_unit_updater.py`（T-005 が生成した `decision_units.json` への人間決定付加）
  - `runtime/runtime_core/decisions/human_signoff_writer.py`（`human_signoff.json` 生成）
- **完了条件**：T-005 が生成した決定単位への人間決定付加が foundation スキーマ準拠で行われる、人間署名記録が `human_signoff_status` foundation 4 値正本を再定義せず参照する、不在と明示保留／却下が機械区別可能
- **テスト要件**：人間決定付加テスト（決定単位生成は T-005 側に集約）、人間署名 4 値の整合テスト、不在と保留の区別テスト

### T-008：evidence writer（証拠書き出し器と不変性担保）

- **対応設計節**：design.md §全体構造（evidence writer 役）、§証拠出力モデル §生証拠と派生証拠の分離、§不変性の担保
- **対応要件**：Requirement 4 受入 4（生の証拠と派生要約の分離）、Requirement 4 受入 7（failure_observation スキーマ準拠記録の出力）、Requirement 6 受入 3（無効化マーカーが生証拠を改変しない）、Requirement 7 受入 5（再生可能性を失うほど証拠を過度に圧縮しない）
- **責務**：3 層（生段証拠 ／ 人間・決定統合証拠 ／ 便宜要約）の証拠書き出しを実装。`steps/*.json` ／ `decisions/*.json` から `review_case.json` への投影（§証拠出力モデルの「主要な投影対応」7 項目）を実施。凍結マーカー（`closed_at`）以降の生段証拠変更を構造的に禁止
- **前提タスク**：T-004、T-005、T-007（投影元の成果物が前提）
- **成果物**：
  - `runtime/runtime_core/evidence_writer/writer.py`（3 層書き出し本体）
  - `runtime/runtime_core/evidence_writer/projection_rules.yaml`（`steps/*.json` ／ `decisions/*.json` → `review_case.json` の投影規約 7 項目）
  - `runtime/runtime_core/evidence_writer/immutability_guard.py`（凍結後の生段証拠変更を拒否）
  - `runtime/runtime_core/evidence_writer/failure_observation_writer.py`（foundation の failure_observation スキーマに準拠した記録を `failures/failure_observations/<observation_id>.json` に書き出す。design.md §証拠出力モデル 行 454 に対応）
- **完了条件**：投影規約 7 項目（`step_outcome` → `step_status`、段別識別子、所見、決定単位参照、検証器結果参照、無効化標識参照、`integration_summary`）が機械的に適用される、凍結後の生段証拠への書き込みが拒否される、failure_observation スキーマ準拠記録が `failures/failure_observations/<observation_id>.json` に書き出される
- **テスト要件**：投影規約 7 項目のテスト、凍結後書き込み拒否テスト、`review_case.json` の foundation スキーマ準拠テスト、`failure_observation` スキーマ準拠テスト

### T-009：validation bridge（検証器連携と実行終了境界）

- **対応設計節**：design.md §全体構造（validation bridge 役）、§検証器連携 §実行終了境界、§無効化処理
- **対応要件**：Requirement 1 受入 5（実行終了境界の露出）、Requirement 6（検証器連携と実行終了、受入 1〜5、7〜9。受入 6 ＝ `review_mode` 付与は T-002 ／ T-004 が担う）
- **責務**：実行終了境界の順序（Step D 完了 → 人間署名 → 凍結 → 検証器呼び出し → `validator_result.json` 保存）を強制。`validator_status` foundation 4 値正本（`not_run`／`passed`／`failed`／`blocked`）を再定義せず伝播。無効化標識を `validation/invalidation_markers.json` への追加で表現（生証拠を改変しない）。前提条件違反や多重起動を検知した場合、検証器を起動せず `run_status=orchestration_failed` として fail-closed。`derived/invalid_run_triage_note.json` を生成（無効実行時、`primary_failure_code` ／ `failed_validator_check_ids` ／ `invalidation_marker_linkage` ／ `operator_action_hint` を含む）。`evidence_class` foundation 4 値正本の確定遷移を design.md §セッションモデル §3 の 9 行マッピング表に従って実施
- **前提タスク**：T-002（`run_status` 制御）、T-007（人間署名）、T-008（証拠凍結）
- **成果物**（内部関係：`bridge.py` が他 3 ファイルを呼び出すオーケストレーション役、他 3 ファイルは個別責務の補助モジュール）：
  - `runtime/runtime_core/validation_bridge/bridge.py`（順序強制と検証器呼び出し、他 3 補助モジュールを統合）
  - `runtime/runtime_core/validation_bridge/invalidation_marker_writer.py`（補助：無効化標識の追加書き込み）
  - `runtime/runtime_core/validation_bridge/evidence_class_transitioner.py`（補助：design.md §3 の 9 行マッピング表を実装）
  - `runtime/runtime_core/validation_bridge/triage_note_writer.py`（補助：`invalid_run_triage_note.json` 生成）
- **完了条件**：順序違反（人間署名前の検証器呼び出し等）が構造的に拒否される、`validator_status` 4 値が foundation 正本を再定義せず伝播される、`evidence_class` 確定遷移が 9 行マッピング表のすべての組み合わせをカバーする
- **テスト要件**：順序強制テスト（前提違反の拒否）、`validator_status` 4 値の伝播テスト、`evidence_class` 確定遷移の網羅性テスト（9 行マッピング全件）、fail-closed 動作テスト

### T-010：可搬証拠束輸出

- **対応設計節**：design.md §可搬証拠束輸出 §輸出境界 §束形状
- **対応要件**：Requirement 9（可搬な証拠束の輸出、受入 1〜5）
- **責務**：実行終了・検証完了後の別工程として、`exports/<bundle_id>/`（`bundle_manifest.yaml` ／ `run/<run_id>/...` ／ `checksums/bundle_checksums.json`）を生成。`bundle_manifest.yaml` に `bundle_id` ／ `run_id` ／ `source_repository_id` ／ `source_revision` ／ `review_mode` ／ `exported_at` ／ `export_runtime_version` ／ `included_artifact_refs` を必ず含める。生実行ディレクトリを置き換えず、別成果物として扱う（生証拠の意味を書き換えない、欠落した来歴を暗黙補完しない、中央側の取り込み判定を済ませたことにしない）
- **前提タスク**：T-002（`bundle_manifest.yaml` の必須項目 `source_repository_id` ／ `source_revision` ／ `review_mode` は session controller が `run_manifest.yaml` に書き込む値。Requirement 9 受入 2 ／ 3 の来歴情報保持要件と直接対応）、T-008（実行終了後の正本成果物が前提）、T-009（検証完了が前提）
- **成果物**：
  - `runtime/runtime_core/bundle_exporter/exporter.py`
  - `runtime/runtime_core/bundle_exporter/bundle_manifest_schema.yaml`
- **完了条件**：可搬束が生成可能、`bundle_manifest.yaml` の必須 8 項目が出力される、生実行ディレクトリが輸出後も不変（輸出前後のディレクトリツリーのハッシュ照合で確認）、来歴情報（`source_repository_id` ／ `source_revision` ／ `review_mode`）が同一性を保つ（`run_manifest.yaml` と `bundle_manifest.yaml` のフィールド一致で確認）
- **テスト要件**：束生成テスト、必須項目存在テスト、生実行ディレクトリ不変性テスト、来歴同一性テスト

### T-011：テスト戦略整備と統合テスト

- **対応設計節**：design.md §テスト戦略（5 項目の縫い目）
- **対応要件**：Requirement 1 受入 1〜6 の網羅検証、Requirement 10（参照規約なしの機械検証）。なお「各 Requirement の機械判定可能な完了条件の網羅」は T-011 の横断的責務（テスト整備）であり、個別の対応要件としては要件 1・要件 10 を担う（要件追跡表もこの 2 要件に T-011 を載せる）
- **責務**：design.md §テスト戦略で定義された 5 項目（言語モデル差し替え点 ／ 検証ブリッジ起動点 ／ 段入出力分離点 ／ 決定単位生成の検証方針 ／ 実行終了境界の順序検証）をすべて Python テストとして整備。pytest で一括実行可能。foundation との接続部（語彙正本 6 件の参照のみで使用、再定義していないこと）の機械検証も含める。要件追跡表と各タスク本文の対応要件欄の双方向整合チェック（foundation T-010 と同様、runtime 側でも採用）
- **前提タスク**：T-001、T-002、T-003、T-004、T-005、T-006、T-007、T-008、T-009、T-010（全実装タスクが前提）
- **成果物**：`tests/runtime/` 配下のテストファイル群（test_session_controller.py ／ test_step_executors.py ／ test_prompt_resolver.py ／ test_decision_units.py ／ test_evidence_writer.py ／ test_validation_bridge.py ／ test_bundle_exporter.py ／ test_integration_run_close_order.py の 8 ファイル相当、または機能別に分割）
- **完了条件**：すべての pytest が pass、5 項目のテスト戦略網羅、foundation 6 語彙正本の参照のみ使用が機械検証される、runtime 所有 3 語彙（`phase_profile` 4 値 ／ `treatment` 3 値 ／ `step_outcome` 3 値）が T-003 ／ T-004 ／ T-006 の成果物で正本確定されていることが機械検証される、要件追跡表の双方向整合が機械チェックされる
- **テスト要件**：すべての pytest が pass、回帰なし

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1：レビュー実行制御 | T-001（実行配置・命名の所有、受入 6）、T-002（session controller）、T-004（Step A／B／C）、T-005（Step D）、T-009（実行終了境界、受入 5）、T-011（受入 1〜6 網羅検証） |
| Requirement 2：処理方式対応の実行 | T-003（treatment 軸）、T-004（treatment 別実行） |
| Requirement 3：プロンプト解決と版追跡 | T-006（プロンプト解決機構） |
| Requirement 4：構造化された証拠の出力 | T-001（実行レベル証拠出力の配置、受入 1）、T-004（段別証拠）、T-005（統合証拠）、T-008（evidence writer） |
| Requirement 5：人間決定の組み込み | T-002（決定単位提示の起点、受入 1）、T-005（決定単位生成）、T-007（人間署名記録） |
| Requirement 6：検証器連携と実行終了 | T-002（受入 6 ＝ `review_mode` 付与の起点）、T-004（受入 6 ＝ 各段出力への `review_mode` 付与）、T-007（受入 9 ＝ 署名は順序の起点）、T-008（受入 3 ＝ 無効化が生証拠を改変しない）、T-009（受入 1〜5、7〜9 ＝ 検証器連携・実行終了境界） |
| Requirement 7：再生対応の実行時記録 | T-002（マニフェスト）、T-008（生段証拠保持） |
| Requirement 8：フェーズ対応レビュープロファイル | T-003（phase/profile 軸）、T-006（プロンプト上書き選択） |
| Requirement 9：可搬証拠束輸出 | T-010（bundle exporter） |
| Requirement 10：パターン定義依存の除外 | T-004（パターン定義参照なし、動的判定）、T-011（参照規約なしの機械検証） |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略の 5 項目を T-011 にまとめて継承する。各項目の対応タスクは次のとおり：

- 言語モデル差し替え点 → T-004 ／ T-011
- 検証ブリッジ起動点 → T-009 ／ T-011
- 段入出力分離点 → T-004 ／ T-005 ／ T-011
- 決定単位生成の検証方針 → T-005 ／ T-011
- 実行終了境界の順序検証 → T-009 ／ T-011

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-011 のすべてが起草・実装・テスト・コミット完了
- design.md §完成判定基準の 6 項目すべてが T-011 の統合テストで pass
- foundation の 6 語彙正本（`counter_status`／`validator_status`／`evidence_class`／`review_mode`／`severity`／`final_label`）を runtime が再定義せず参照のみで使用していることが、機械検証で確認できる（`confidence_label` は推定タスク用であり、runtime は推定タスクを扱わないため参照範囲外。foundation 所有は foundation/design.md §判断 7 の全 7 件で、runtime はうち 6 件を参照）
- runtime 所有の語彙（`phase_profile` 4 値、`treatment` 3 値、`step_outcome` 3 値）が T-003 ／ T-004 ／ T-006 の成果物で正本として確定されている
- 各タスクの成果物配置が design.md §実行成果物配置と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは design §先送り論点（Open Issues for Design Alignment Gate、design.md 行689-697）を tasks 段に転記し、実装フェーズでの確定を管理する（tasks 段 2 軸整合性監査 T-1 で転記、2026-05-29。evaluation／workflow-management の DVT 運用と同型）。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-R001 | T-006 等 | runtime 所有プロファイル設定の具体配置（design §先送り論点） | 実装フェーズでプロファイル設定の配置を確定 | 未解除（実装フェーズで確定） |
| DVT-R002 | T-008 | `review_case.json` 内での段参照粒度（design §先送り論点） | 実装フェーズで段参照粒度を確定 | 未解除（実装フェーズで確定） |
| DVT-R003 | T-009 | 検証ブリッジの実行入口（design §先送り論点） | 実装フェーズで検証ブリッジ起動入口を確定 | 未解除（実装フェーズで確定） |
| DVT-R004 | T-010 | 確定レビュー出力の最終輸出形（design §先送り論点） | 実装フェーズで最終輸出形を確定 | 未解除（実装フェーズで確定） |
| DVT-R005 | T-006 | プロンプト上書き選択順序の具体実装（design §先送り論点、T-006 の `override_paths.yaml` で部分対応） | 実装フェーズで選択順序の具体を確定 | 未解除（実装フェーズで確定） |

**運用ルール**：未解除項目があっても延期理由が明記されていれば完了判定可能（T-011 完了条件でゲート化、evaluation T-011 の方針継承）。

## 変更意図（Change Intent）

本タスク文書は runtime 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **タスク粒度の中庸化**：design.md の節単位（15 節以上）から、責務領域単位（11 タスク）に再編。タスクが細分化されすぎず、各タスクが一気通貫で完結できる単位を採る
- **責務領域単位の分離**：design.md §全体構造の 4 役（session controller ／ step executors ／ evidence writer ／ validation bridge）を主軸に、補助領域（プロンプト解決／決定単位／可搬証拠束輸出／テスト整備）を独立タスクに切り出す
- **依存順の明示**：T-001（配置）→ T-002／T-003（制御・軸）→ T-006（プロンプト解決）→ T-004（Step A／B／C）→ T-005（Step D）→ T-007（決定単位／署名）→ T-008（証拠書き出し）→ T-009（検証器連携）→ T-010（束輸出）→ T-011（統合テスト）の流れを固定
- **foundation contract consumer 原則**：runtime は foundation の語彙正本 6 件を再定義・縮約せず、参照のみで使用する（design.md §判断 6 準拠）。T-011 で機械検証
- **言語モデル境界の差し替え可能化**：T-004 で言語モデル呼び出しを差し替え点として独立コンポーネント化、固定応答による決定的テストを可能にする
- **Step D の言語モデル非依存**：T-005 を Step A／B／C と分離し、機械統合のみで言語モデル呼び出しを含まないことを構造的に保証
- **計画書 §5.4 軽量化方針との整合**：節ハッシュ・supersedes リンク・通過マーカー後続確認などは導入せず、テスト件数の累積管理は行わず「すべて pass」を完了条件とする（foundation T-009 の topic-06 採用方針を踏襲）
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：foundation T-010 の topic-17 採用方針を踏襲、要件追跡表（Requirement → タスク）と各タスク本文の対応要件欄（タスク → Requirement）の双方向整合を機械検証

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、`.reviewcompass/pending-cross-feature-findings.md` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。（A-017 対処 案1、2026-05-29 セッション40：全機能 tasks.md に確認手順を明示）
