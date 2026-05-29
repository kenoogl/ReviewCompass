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

本機能の triad-review 段で発見された機能横断波及所見は、`.reviewcompass/pending-cross-feature-findings.md` に追記し、tasks の機能横断段（review-wave）で消化する。既登録の接合面所見 A-019（workflow-management T-010 の `approved_update` スキーマと本機能 §8.4 正本の不一致）は本機能の tasks 段では機能内対処せず、機能横断段で workflow-management 側を §8.4 正本に整合させる方向で消化する（DVT-S001 と連動）。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。
