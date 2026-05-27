---
type: tasks_triad_review
target: .reviewcompass/specs/evaluation/tasks.md
target_commit: <未確定、本セッション 33 で起草された tasks.md コミット予定版>
target_content_hash: <未計測>
date: 2026-05-27
mode: subagent_mediated
session: session-33
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: <約 3.9>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <約 2.7>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <約 2.2>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 9, INFO: 3 }
    count: 16
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 3, INFO: 1 }
    count: 7
    counter_distribution: { counter_evidence_raised: 3, no_counter_evidence_after_challenge: 13, not_assessed: 0 }
  judgment:
    by_judgment: { must-fix: 8, should-fix: 11, leave-as-is: 4 }
    by_waterfall: { 機能内対処: 23, 波及: 0, 遡及: 0, 延期: 0 }
    count: 23
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation tasks 2026-05-26 ／ runtime tasks 2026-05-27 と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で「タスク 7」と言及のみで本体未整備、本セッション限りの仮設定（foundation／runtime tasks の 2026-05-26〜27 レビューで採用された 7 観点を踏襲）
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：evaluation tasks triad-review

本記録は evaluation 機能の tasks.md（11 タスク T-001〜T-011、本セッション 33 で起草、約 230 行）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation tasks 2026-05-26 ／ runtime tasks 2026-05-27 と同配置）。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は本セッション仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。16 件の所見（CRITICAL 0／ERROR 4／WARN 9／INFO 3）を提示した。

### 主役所見一覧（16 件、F-001〜F-016）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | ERROR | tasks.md 行 52（T-002 責務、ingestion_register 記録項目） | T-002 の `ingestion_register.json` 記録項目が 4 項目のみで、design.md §取り込み登録 行 489-498 の必須 8 項目（`bundle_id`／`run_id`／`source_repository_id`／`source_revision`／`review_mode`／`ingested_at`／`ingestion_status`／`missing_fields`）と 4 項目差、さらに `source_runtime_version` は design.md に存在しない不明フィールド | fact |
| F-002 | 1：上流仕様の網羅 | ERROR | tasks.md 行 190（要件追跡表、Req 5） | Req 5 受入 4（self-improvement と analysis 両者による下流消費）と受入 5（評価ロジック変更時の成果物版管理可視化）の対応タスク不在、`analysis_run_manifest.yaml` 生成タスクも不在 | fact |
| F-003 | 1：上流仕様の網羅 | ERROR | tasks.md 行 36、行 190 | T-001 が Req 5 受入 2（識別子連結保持）を担う粒度ではなく、要件追跡表でも対応タスク不在 | fact |
| F-004 | 1：上流仕様の網羅 | WARN | tasks.md 行 147（T-009 対応設計節） | T-009 の対応設計節に §比較モデル §4 レビューモード母集団規則が欠落 | fact |
| F-005 | 2：タスク粒度の妥当性 | WARN | tasks.md 行 52、65 | T-002 と T-003 のチェックサム照合責務が文面で重複 | fact |
| F-006 | 3：タスク依存順の整合性 | ERROR | tasks.md 行 162（T-010 前提） | T-010 前提が T-008 のみで、陳腐化対象を生成する T-006／T-007／T-009 が直接依存から欠落 | fact |
| F-007 | 3：タスク依存順の整合性 | WARN | tasks.md 行 149（T-009 前提） | T-009 前提が T-006 のみで、T-008 が欠落（mode_diff／role_diff は exclusion_report ／ caveat_register と並列に self-improvement／analysis から読まれる） | inference |
| F-008 | 4：完了条件の機械判定可能性 | WARN | tasks.md 行 45（T-001 完了条件 2） | 「人間レビューで承認」が機械判定不可、参照形式不明 | fact |
| F-009 | 4：完了条件の機械判定可能性 | WARN | tasks.md 行 128（T-007 完了条件） | 「黙示的に混入しない」の機械判定の具体的方法が記述なし | fact |
| F-010 | 4：完了条件の機械判定可能性 | INFO | tasks.md 行 167（T-010 完了条件） | 「選択ロジックが本機能で確定」の機械検証方法が不明 | mixed |
| F-011 | 5：テスト要件の妥当性 | WARN | tasks.md 行 177（T-011 完了条件） | 4 下流機能（self-improvement／analysis／workflow-management／conformance-evaluation）接合面の機械検証が完了条件から欠落 | fact |
| F-012 | 5：テスト要件の妥当性 | INFO | tasks.md 行 73（T-003 テスト要件） | T-003 単独テストと T-011 統合テストの境界 7 ケース重複担当が不明確 | mixed |
| F-013 | 6：機能横断波及の早期検出 | WARN | tasks.md 行 40-42（T-001 成果物） | `evaluation/analysis_layout/README.md` ／ `layout_spec.yaml` のソースコードパスは design.md に根拠なし、`experiments/analysis/` 配下のみ定義 | fact |
| F-014 | 6：機能横断波及の早期検出 | WARN | tasks.md 行 27（contract consumer 原則） | 再定義禁止の機械検証基準がタスク間で表現揺れ（T-004 行 86／T-006 行 113／T-009 行 148） | mixed |
| F-015 | 7：成果物配置と命名の整合 | WARN | tasks.md 行 148（T-009 責務、findings_summary） | mode_diff_report で `findings_summary` 命名だが design.md §レビューモード差分報告 行 464 では `findings_by_severity` と命名、揺れあり | fact |
| F-016 | 7：成果物配置と命名の整合 | INFO | tasks.md 行 176（T-011 成果物リスト） | T-009 が 2 つの出力器を持つのに `test_diff_reports.py` 1 ファイルにまとめる理由が不明 | inference |

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論または同意（16 件）

| ID | counter_status | counter_rationale 要約 |
|---|---|---|
| F-001 | no_counter_evidence_after_challenge | 同意。design.md §取り込み登録 行 489-498 で 8 項目確定、tasks.md 行 52 は 4 項目のみ、`source_runtime_version` は design.md にも要件 10 受入 1〜5 にも §必須メタデータ検査の 16 項目にも存在しない不明フィールド、Req 10 受入 1 の中央側取り込み契約担保不成立 |
| F-002 | no_counter_evidence_after_challenge | 同意。Req 5 受入 4／5 は requirements.md 行 95-96 に存在するが、要件追跡表（行 190）は受入 4／5 対応タスク不在、`analysis_run_manifest.yaml` も tasks.md 全文に「生成器」「writer」「extractor」のいずれの形でも登場しない |
| F-003 | no_counter_evidence_after_challenge | 同意。T-001 責務（行 37）は配置仕様文書の新設のみ、Req 5 受入 2 はメトリクスや派生出力生成の機械検証を要求するため配置仕様タスクと適合せず、本来 T-006／T-007／T-009 の責務 |
| F-004 | counter_evidence_raised | 反証。T-009 はレビューモード差分／3 役所見差分の出力（Req 9 受入 7／8）で、§比較モデル §4 レビューモード母集団規則は T-007 責務範囲（tasks.md 行 118 で対応設計節として明示）。責務分離として整合、INFO 相当に過大評価 |
| F-005 | counter_evidence_raised | 反証。T-002 のチェックサム照合は物理コピー前の整合性検証、T-003 の許容判定は来歴情報検証＋チェックサム結果を含む 3 値判定で責務階層分離。T-002 責務文末尾「T-003 の許容判定と連携」が委譲を明示しており重複ではなく協調関係 |
| F-006 | no_counter_evidence_after_challenge | 同意。T-010 陳腐化伝播の対象は派生成果物全般（メトリクス／比較／差分報告）を含み、T-006／T-007／T-009 が直接依存対象。design.md §陳腐化伝播の履行 行 533 で「派生成果物は陳腐化フラグ付け、または再導出」と明示 |
| F-007 | no_counter_evidence_after_challenge | 同意。design.md §self-improvement への接合面 行 612-625 で mode_diff_report と exclusion_report が並列に列挙、T-008 完了後に T-009 を出す論理順を前提タスクに反映すべき |
| F-008 | no_counter_evidence_after_challenge | 同意。「人間レビューで承認」「foundation／runtime tasks T-001 と同じ運用に従う」とあるが foundation／runtime の T-001 運用が機械検証可能か参照可能な形で明示されていない（runtime F-008 と同型問題、should-fix 確定の前例あり） |
| F-009 | no_counter_evidence_after_challenge | 同意。「黙示的に混入しない」の操作的定義（例：treatment_comparisons.json の included_runs から evidence_class != valid の実行を全件除外することの YAML 検査）を欠く（runtime F-009 と同型問題、should-fix 確定済の前例あり） |
| F-010 | no_counter_evidence_after_challenge | 同意。文書レベルの正本確定を要求するが機械検証手順（handler_selection_logic.py に 3 つの選択基準が境界判定として宣言され、selection_logic_definition.yaml が解析可能で 3 値以上の判定状態を返す）が未明示 |
| F-011 | no_counter_evidence_after_challenge | 同意。T-011 完了条件には foundation 6 ／ runtime 3 語彙正本の参照検証は含まれるが、§下流機能との接合面 行 601-646 の 4 下流機能の入力ファイル合致確認が未収録、§完成判定基準 行 741 を担保する手段不在 |
| F-012 | no_counter_evidence_after_challenge | 同意。design.md §テスト戦略 行 710-717 の 7 ケースが T-003 単独（行 73）と T-011 統合（行 178）の双方で「網羅」と書かれているが境界が未定義、二重実装または完全不実装のリスク |
| F-013 | no_counter_evidence_after_challenge | 同意。design.md §分析成果物配置 §配置の根拠（行 138-148）は `experiments/analysis/` 配下のみ定義、`evaluation/analysis_layout/` パスは design.md に直接の根拠なし |
| F-014 | no_counter_evidence_after_challenge | 同意。T-004 行 86 ／ T-006 行 113 ／ T-009 行 148 で表現揺れ（runtime A-007 と同型問題、should-fix 確定済の前例あり） |
| F-015 | no_counter_evidence_after_challenge | 同意。design.md §レビューモード差分報告 行 464 は `findings_by_severity`、§3 役所見差分報告 行 477 は `findings_summary`、tasks.md は両方を `findings_summary` に統一しているため mode_diff 側に齟齬発生 |
| F-016 | counter_evidence_raised | 反証。T-011 行 176 末尾「または機能別に分割」で柔軟性明示済、INFO 相当としても過大評価 |

### 2.2 独立発見（7 件、A-001〜A-007、ERROR 3／WARN 3／INFO 1）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| A-001 | 1：上流仕様の網羅 | ERROR | tasks.md 行 175-178（T-011）／design.md 行 117 | design.md §分析成果物配置 行 117 で必須成果物として宣言されている `manifests/analysis_run_manifest.yaml`（`analysis_logic_version` ／ `protocol_version_coverage` ／ `runtime_version_coverage` ／ `prompt_set_version_coverage` 等を含む、design.md 行 519-527）の生成タスクが tasks.md に一切登場しない。Req 5 受入 5（評価ロジック変更時の成果物版管理可視化）と Req 2 受入 6（規約版混在検出の機械検証根拠）の両方を担保する中核成果物 | fact |
| A-002 | 1：上流仕様の網羅 | ERROR | tasks.md 行 119-129（T-007） | T-007 対応要件は Req 2 受入 1〜6 と Req 7 受入 1〜5 のみで、Req 9 受入 6（標準比較集団規則、3 集団扱い）が欠落。T-007 責務文（行 120）には「レビューモード母集団規則」が明示されており、design.md §比較モデル §4 もこの責務として位置付けるため、T-007 対応要件に Req 9 受入 6 を明示すべき。要件追跡表（行 194）の Req 9 → T-007 マッピング自体は存在するが、T-007 対応要件欄での受入細目欠落で双方向整合テスト（T-011 行 174）が失敗するリスク | fact |
| A-003 | 6：機能横断波及の早期検出 | ERROR | tasks.md 行 176（T-011 成果物） | design.md §下流機能との接合面 行 601-646 で 4 下流機能が読む各成果物が明示されているが、T-011 テストファイル群に「下流接合面突合テスト」が含まれず、4 下流機能との接合面の機械検証手段が不在。F-011 同根、§完成判定基準 行 741 を担保するテストが構造的に欠落 | fact |
| A-004 | 4：完了条件の機械判定可能性 | WARN | tasks.md 行 58（T-002 完了条件） | T-002 完了条件「runtime 輸出構造との対称性が保たれる」の機械判定方法（例：runtime exports ／ central imports 両側で `bundle_id/run/run_id/...` パス比較関数が一致を返す、または ls 結果の差分が空であることを検査する関数）が未明示（runtime A-005 同型） | fact |
| A-005 | 2：タスク粒度の妥当性 | WARN | tasks.md 行 144-155（T-009） | T-009 は「レビューモード差分」と「3 役所見差分」の 2 出力器を 1 タスクに統合しているが、design.md §レビューモード差分報告 行 456-467 ／ §3 役所見差分報告 行 469-483 が独立節、Req 9 受入 7 と受入 8 も別受入として分離。`findings_summary` の構造が役別条件付き必須で複雑化（runtime A-003 同型） | mixed |
| A-006 | 3：タスク依存順の整合性 | WARN | tasks.md 行 162（T-010 前提）／行 163-166（T-010 成果物） | T-010 選択ロジック判定境界の入力源（T-007 の treatment_comparisons.json／T-006 のメトリクス被覆率）が前提に未明示（F-006 と連動だが境界判定基準の入力源は別観点） | inference |
| A-007 | 7：成果物配置と命名の整合 | INFO | tasks.md 行 154、156、169／design.md 行 460 | T-009 完了条件で「analysis 仕様 Requirement 7 受入 3 の入力として機能する形式」とあるが、analysis 仕様は本セッション時点で未起草（依存マップ順 4 番目以降）であり、検証可能な参照先が現時点で不在 | fact |

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 判定結果一覧（23 件）

| ID | judgment | 波及種別 | 判定理由（対処方針案を含む） |
|---|---|---|---|
| F-001 | must-fix | 機能内対処 | 対処方針：T-002 ingestion_register 記録項目を design.md 8 項目に揃え、`source_runtime_version` を削除（design.md に根拠なし） |
| F-002 | must-fix | 機能内対処 | 対処方針：T-006 または T-001 に `analysis_run_manifest.yaml` 生成責務を明記し、要件追跡表 Req 5 受入 4／5 を当該タスクに連結（A-001 と同根、§4 統合議論論点 2） |
| F-003 | must-fix | 機能内対処 | 対処方針：要件追跡表 Req 5 ／ T-001 の対応欄から受入 2 を T-006／T-007 に振り替える、または T-006／T-007 の対応要件欄に Req 5 受入 2 を明示追加 |
| F-004 | leave-as-is | 機能内対処 | 敵対役反証成立：§4 は T-007 責務（tasks.md 行 118 で §1〜§4 を網羅）、T-009 は §レビューモード差分報告・§3 役所見差分報告に対応、責務分離として整合 |
| F-005 | leave-as-is | 機能内対処 | 敵対役反証成立：T-002 は整合性検証、T-003 は 3 値判定の階層関係で責務重複ではない、tasks.md 行 52／65 で責務分離は読解可能 |
| F-006 | must-fix | 機能内対処 | 対処方針：T-010 前提に T-006／T-007／T-009 を追加（runtime A-004 と同型処理） |
| F-007 | should-fix | 機能内対処 | 対処方針：T-009 前提に T-008 を追記（明示性向上）。間接依存で工程上は破綻しないため must-fix まで上げない |
| F-008 | should-fix | 機能内対処 | 対処方針：runtime topic-26 別案＝案 2 ＋ 注記と同じ判断適用可能、完了条件 2 を「runtime tasks T-001 ／ foundation tasks T-001 と同じ運用に従う」注記に書き換え |
| F-009 | should-fix | 機能内対処 | 対処方針：完了条件に「有効母集団規則適用後の比較集計に invalid／analysis_blocked が 0 件であること」の機械判定基準を補記 |
| F-010 | leave-as-is | 機能内対処 | 選択ロジック確定の機械検証は T-011 で `staleness/handler_selection_logic.py` のスキーマ・分岐網羅テストとして十分実現可能、INFO 相当の指摘で修正不要 |
| F-011 | must-fix | 機能内対処 | A-003 と連動。対処方針：T-011 完了条件に「4 下流接合面の機械検証（要件追跡表双方向整合＋語彙正本参照のみ使用＋成果物配置適合）」を追加 |
| F-012 | should-fix | 機能内対処 | 対処方針：T-003 テスト要件に「単体検証」、T-011 に「経路統合検証」と粒度の役割分担を 1 行ずつ明記 |
| F-013 | should-fix | 機能内対処 | 対処方針：T-001 責務欄に「仕様文書の配置先＝ `evaluation/analysis_layout/`、実体生成物の配置先＝ `experiments/analysis/`」の境界を明示（runtime F-013 と同型処理） |
| F-014 | should-fix | 機能内対処 | 対処方針：T-011 完了条件に語彙正本ハッシュ照合または参照のみ使用の機械検証を明記（runtime F-012 と同一作業） |
| F-015 | should-fix | 機能内対処 | 対処方針：T-009 責務欄を `findings_summary`（重大度別件数）に統一し、design.md 側スキーマと一致させる |
| F-016 | leave-as-is | 機能内対処 | 敵対役反証成立：「または機能別に分割」で柔軟性明示済、INFO 相当の指摘で修正不要 |
| A-001 | must-fix | 機能内対処 | F-002 と連動。対処方針：T-006 に `manifests/analysis_run_manifest.yaml` 生成責務を明示追記、9 項目（design.md 行 517-527）の機械的出力を完了条件に追加 |
| A-002 | must-fix | 機能内対処 | 対処方針：T-007 対応要件欄に Req 9 受入 6 を追加、要件追跡表で Req 9 受入 1〜5・6 → T-007、受入 7・8 → T-009 の分担を明記（runtime A-002 と同型処理） |
| A-003 | must-fix | 機能内対処 | F-011 と連動、最重要の must-fix。対処方針：T-011 完了条件に 4 下流接合面の機械検証手順を追加（F-011 と同一作業で対処） |
| A-004 | should-fix | 機能内対処 | 対処方針：T-002 完了条件に対称性検証の操作的判定方法（パス構造ハッシュ照合等）を補記 |
| A-005 | should-fix | 機能内対処 | 対処方針：T-009 責務記述で 2 出力器の内部関係（共通スキーマ＋出力器分離）を補記、粒度は維持 |
| A-006 | should-fix | 機能内対処 | F-006 の対処（T-010 前提に T-006／T-007／T-009 追加）で同時解消、追加作業なし |
| A-007 | should-fix | 機能内対処 | 対処方針：T-009 完了条件に「analysis 仕様起草後に下流接合面検証を再評価」の注記、または T-011 完了条件に当該検証の遅延扱いを明記 |

### 3.2 集計

- **判定別**：must-fix 8 件／should-fix 11 件／leave-as-is 4 件（合計 23 件）
- **波及種別別**：機能内対処 23 件／波及 0 件／遡及 0 件／延期 0 件

### 3.3 判定役の総評

evaluation tasks.md（11 タスク T-001〜T-011）は foundation tasks／runtime tasks の責務領域単位粒度方針を継承した健全な構成だが、上流仕様の網羅（観点 1）と完了条件の機械判定可能性（観点 4）に集中した欠落が顕在化した。must-fix 8 件はすべて機能内対処で完結し、上流文書（design.md／requirements.md）への遡及や他機能への波及はない。

最優先で議論すべき所見は次の 4 系列：(1) F-001（T-002 ingestion_register 8 項目欠落＋ design 不在フィールド混入）、(2) F-002／A-001 連動（`analysis_run_manifest.yaml` 生成タスクの完全不在、要件 5 受入 4／5 と要件 2 受入 6 の機械検証根拠欠落）、(3) F-011／A-003 連動（T-011 完了条件と §完成判定基準の不整合）、(4) A-002（T-007 対応要件欄から Req 9 受入 6 欠落、要件追跡双方向整合テスト不合格リスク）。これら 4 系列は runtime tasks レビュー §4.1 議論論点 1〜5 の構造を踏襲する形で利用者議論を整理可能で、特に F-002／A-001 連動は runtime tasks レビューにはない evaluation 固有の重大欠落であり、最優先で対処方針を確定すべき。

foundation tasks レビュー（must-fix 6 件、機能内対処 22 件）／runtime tasks レビュー（must-fix 6 件、機能内対処 22 件）との比較では、evaluation の must-fix 8 件はやや多めだが、いずれも機能内対処で完結する点は前 2 機能と同水準。修正規模も中程度で、再レビュー（または差分レビュー）を経て承認可能な水準にある。

自律進行可否：must-fix 8 件の利用者議論（規律 [[must-fix-discussion-obligation]]）を経て対処方針を確定した後、実装フェーズへの移行は規律 [[implementation-autonomy]] に従い自律進行可能。should-fix 11 件は機能内対処で一括処理可能であり、leave-as-is 4 件（F-004／F-005／F-010／F-016）は反証成立または既存記述で十分カバー済みのため修正不要。利用者と must-fix 8 件を 6 議論論点（連動を考慮：F-001 ／ F-002 ＋ A-001 連動 ／ F-003 ／ F-006 ／ F-011 ＋ A-003 連動 ／ A-002）に集約して議論することを推奨する（判定役提示の「5 議論論点」は連動関係の集計誤り、6 論点が正、本レビュー記録 §4.1 で訂正）。

---

## 4. 統合節（integration、対処方針と利用者議論履歴）

本節は規律 [[must-fix-discussion-obligation]] に従い、must-fix 所見ごとの対処方針案を提示し、利用者議論を経て確定方針と反映箇所を記録する。

### 4.1 must-fix 8 件の対処方針案（6 議論論点、F-002 と A-001、F-011 と A-003 を連動として集約。利用者判定は §4.2 参照（議論論点 1 ＝ F-001：案 1、議論論点 2 ＝ F-002 ／ A-001：案 1、議論論点 3 ＝ F-003：別案、議論論点 4 ＝ F-006：案 1、議論論点 5 ＝ F-011 ／ A-003：案 1、議論論点 6 ＝ A-002：案 1）、反映箇所は §4.3 参照）

判定役 §3.3 総評の「5 議論論点」は連動関係の集計誤り、本レビュー記録では 6 議論論点として整理する。

#### 議論論点 1：F-001 — T-002 ingestion_register の必須項目欠落と不明フィールド混入

**事実**：tasks.md T-002 責務（行 52）の `ingestion_register.json` 記録項目が「`bundle_id` ／ `ingested_at` ／ `ingestion_status` ／ `source_runtime_version`」の 4 項目のみ。design.md §取り込み登録 行 489-498 が定める必須 8 項目（`bundle_id` ／ `run_id` ／ `source_repository_id` ／ `source_revision` ／ `review_mode` ／ `ingested_at` ／ `ingestion_status` ／ `missing_fields`）と 4 項目差。さらに `source_runtime_version` は design.md にも要件 10 受入 1〜5 にも §必須メタデータ検査 16 項目にも存在しない不明フィールド。

**候補案**：

- (案 1) T-002 責務欄を design.md 8 項目に揃え、`source_runtime_version` を削除（design.md に根拠なし）。要件追跡表 Req 10 → T-002 マッピングは維持
- (案 2) `source_runtime_version` を design.md §取り込み登録に追加する遡及対処（design 段の再オープン必要）

**深掘り**：

- 案 1 利点：機能内対処で完結、design.md を正本として整合化、Req 10 受入 1 の中央側取り込み契約担保
- 案 2 利点：将来 runtime バージョン管理の取り込み履歴を残したい場合の拡張余地
- 後段影響：T-002 の実装テスト範囲、`bundle_intake.py` の出力スキーマ
- design.md は既に approval 完了（spec.json `design.approval=true`）のため、案 2 は軽量再オープン手続きが必要

**推奨**：案 1（機能内対処、design.md を正本として整合化）

---

#### 議論論点 2：F-002 ／ A-001 連動 — `analysis_run_manifest.yaml` 生成タスクの完全不在

**事実**：design.md §分析成果物配置 行 117 で必須成果物として宣言されている `manifests/analysis_run_manifest.yaml`（9 項目：`analysis_logic_version` ／ `protocol_version_coverage` ／ `runtime_version_coverage` ／ `prompt_set_version_coverage` 等を含む、design.md 行 517-527）の生成タスクが tasks.md に完全に不在。Req 5 受入 4（self-improvement と analysis 両者による下流消費）／受入 5（評価ロジック変更時の成果物版管理可視化）／Req 2 受入 6（規約版混在検出の機械検証根拠）の対応タスクも要件追跡表（行 190）に存在しない。

**候補案**：

- (案 1) T-006（メトリクス抽出器）に `manifests/analysis_run_manifest.yaml` 生成責務を追加し、9 項目の機械的出力を完了条件に明記。要件追跡表 Req 5 受入 4／5 と Req 2 受入 6 を T-006 にも連結
- (案 2) 独立タスク T-012（評価実行マニフェスト生成器）を新設、11 タスク → 12 タスクに拡張
- (案 3) T-001（分析成果物配置）に `analysis_run_manifest.yaml` の生成と版被覆記録を追加

**深掘り**：

- 案 1 利点：T-006 が既に派生成果物のメトリクス生成を担うため、版被覆記録の追加が自然。タスク数を維持
- 案 2 利点：マニフェスト生成という独立責務を明示、責務境界が明確
- 案 3 利点：T-001 が配置仕様タスクなので、マニフェスト構造定義として配置と一体化
- 後段影響：要件追跡表の構造変化、T-011 統合テストの双方向整合チェック対象
- 案 1 推奨：T-006 のメトリクス抽出器が `analysis_run_manifest.yaml` の `protocol_version_coverage` 等を生成する責務として自然、規約版混在検出（Req 2 受入 6）と密接に連動

**推奨**：案 1（T-006 に責務追加、要件追跡表で連結）

---

#### 議論論点 3：F-003 — Req 5 受入 2（識別子連結保持）の対応タスク不在

**事実**：tasks.md T-001 対応要件（行 36）は「Req 5 受入 1〜3」と限定。Req 5 受入 2（派生出力から実行識別子と対象識別子への連結保持）はメトリクスや派生出力生成の機械検証を要求するため、T-001（配置仕様タスク）の責務範囲を超える。要件追跡表（行 190）でも Req 5 受入 2 を明示的に担うタスクが存在しない。

**候補案**：

- (案 1) T-006（メトリクス）／T-007（比較）／T-009（差分報告）の対応要件欄に Req 5 受入 2 を追加（多重対応）、要件追跡表で受入 2 → T-006／T-007／T-009 を明示
- (案 2) T-001 対応要件を「Req 5 受入 1、受入 3」に縮約し、受入 2 を T-006 のみに集約

**深掘り**：

- 案 1 利点：派生出力すべてで識別子連結が担保される（網羅性）
- 案 2 利点：責務単一性、T-001 の役割が明確
- 後段影響：T-011 双方向整合チェック、各派生出力テストの追加項目

**推奨**：案 1（多重対応、派生出力すべてで網羅）

---

#### 議論論点 4：F-006 — T-010 前提タスクへの T-006 ／ T-007 ／ T-009 直接依存追加

**事実**：tasks.md T-010 前提タスク（行 162）が「T-008（除外と注意点の報告が前提）」のみ。T-010（陳腐化伝播履行）は派生成果物（メトリクス／比較／差分報告）を陳腐化フラグ付けまたは再導出する責務で、T-006（`metrics/`）／T-007（`comparisons/`）／T-009（`modes/` ／ `roles/`）が直接依存対象。design.md §陳腐化伝播の履行 行 533 で「派生成果物は陳腐化フラグ付け、または再導出」と明示。

**候補案**：

- (案 1) T-010 前提タスクに T-006 ／ T-007 ／ T-009 を追加（T-006／T-007／T-008／T-009 の 4 前提）
- (案 2) 現状維持（間接依存で十分とみなす）

**深掘り**：

- 案 1 利点：依存順の明示性、A-006（選択ロジック判定境界の入力源）も同時解消
- 案 2 利点：前提リストを最小限に保つ
- 後段影響：T-010 着手時のチェック手順、実装段の前提確認

**推奨**：案 1（直接依存明示、runtime A-004 と同型処理）

---

#### 議論論点 5：F-011 ／ A-003 連動 — T-011 完了条件と §完成判定基準の不整合

**事実**：tasks.md T-011 完了条件（行 177）に foundation 6 ／ runtime 3 語彙正本の参照検証は含まれるが、design.md §下流機能との接合面 行 601-646 で明示された 4 下流機能（`self-improvement` ／ `analysis` ／ `workflow-management` ／ `conformance-evaluation`）の入力ファイル合致確認が未収録。§完成判定基準 行 741「下流 4 機能がどの分析成果物を読むか §下流機能との接合面 で追跡できる」を担保する機械検証手段が不在。

**候補案**：

- (案 1) T-011 完了条件に「4 下流接合面の機械検証（要件追跡表双方向整合 ＋ 語彙正本参照のみ使用 ＋ 成果物配置適合）」を追加、テストファイル `test_downstream_interface.py` 相当を成果物リストに追記
- (案 2) 機能横断段（review-wave）で対処、本機能の T-011 では本機能内検証に限定

**深掘り**：

- 案 1 利点：本機能内で機械検証が完結、§完成判定基準と T-011 完了条件が整合
- 案 2 利点：機能横断段で全機能の接合面を一括検証、本機能の修正範囲を抑制
- 後段影響：T-011 のテスト件数増、機能横断段との責務分担
- 案 1 推奨：foundation／runtime tasks の T-011 ／ T-010 でも各機能内で機械検証を行う方針、整合性のため

**推奨**：案 1（本機能内で機械検証完結）

---

#### 議論論点 6：A-002 — T-007 対応要件欄から Req 9 受入 6 欠落

**事実**：tasks.md T-007 対応要件（行 119）は「Req 2 受入 1〜6」と「Req 7 受入 1〜5」のみで、Req 9 受入 6（標準比較集団規則、3 集団扱い）が欠落。T-007 責務文（行 120）には「レビューモード母集団規則」が明示されており、design.md §比較モデル §4 もこの責務として位置付ける。要件追跡表（行 194）の Req 9 → T-007（レビューモード母集団規則）と T-009 のみで受入分担が不明示、双方向整合テスト（T-011 行 174）が失敗するリスク。

**候補案**：

- (案 1) T-007 対応要件欄に Req 9 受入 6 を追加、要件追跡表で Req 9 受入 1〜5・6 → T-007、受入 7・8 → T-009 の分担を明記
- (案 2) 要件追跡表のみ修正、T-007 対応要件欄は現状維持

**深掘り**：

- 案 1 利点：双方向整合テスト合格、責務分担が両方向で明示
- 案 2 利点：tasks.md 修正範囲が小さい
- 後段影響：T-011 双方向整合チェックの合格条件、実装段の運用

**推奨**：案 1（責務の二重記載解消、runtime A-002 と同型処理）

---

### 4.2 利用者判定履歴

利用者判定は 7 モデル比較実験（2026-05-27 セッション 33、実験ノート [docs/experiments/n-model-comparison.md](../../../../docs/experiments/n-model-comparison.md)）に基づき、本セッションで対話形式により確定。各 topic-NN-human.yaml を出典として記録。

| topic | 所見 | 判定 | 採用方式 | 出典 yaml |
|---|---|---|---|---|
| topic-34 | F-001 | 案 1 | 完全一致 13 件の一括採用 | [topic-34-human.yaml](../../../../tools/experiments/results/topic-34-human.yaml) |
| topic-35 | F-002 | 案 1 | 分岐 6 件のうち 1 件目、3 対 3 から案 1 採用 | [topic-35-human.yaml](../../../../tools/experiments/results/topic-35-human.yaml) |
| topic-36 | A-001 | 案 1 | 完全一致 13 件の一括採用、F-002 と一体作業 | [topic-36-human.yaml](../../../../tools/experiments/results/topic-36-human.yaml) |
| topic-37 | F-003 | **別案** | 分岐 6 件のうち 2 件目、別案（責務主担当制 ＋ 3 列構造）採用 | [topic-37-human.yaml](../../../../tools/experiments/results/topic-37-human.yaml) |
| topic-38 | F-006 | 案 1 | 完全一致 13 件の一括採用、runtime A-004 同型 | [topic-38-human.yaml](../../../../tools/experiments/results/topic-38-human.yaml) |
| topic-39 | F-011 | 案 1 | 完全一致 13 件の一括採用、A-003 と一体作業 | [topic-39-human.yaml](../../../../tools/experiments/results/topic-39-human.yaml) |
| topic-40 | A-003 | 案 1 | 完全一致 13 件の一括採用、F-011 と一体作業 | [topic-40-human.yaml](../../../../tools/experiments/results/topic-40-human.yaml) |
| topic-41 | A-002 | 案 1 | 完全一致 13 件の一括採用、runtime A-002 同型 | [topic-41-human.yaml](../../../../tools/experiments/results/topic-41-human.yaml) |
| topic-42 | F-007 | 案 1 | 完全一致 13 件の一括採用 | [topic-42-human.yaml](../../../../tools/experiments/results/topic-42-human.yaml) |
| topic-43 | F-008 | 案 1 | 分岐 6 件のうち 3 件目、案 1（runtime topic-26 同一枠組み、一貫性重視） | [topic-43-human.yaml](../../../../tools/experiments/results/topic-43-human.yaml) |
| topic-44 | F-009 | 案 1 | 完全一致 13 件の一括採用 | [topic-44-human.yaml](../../../../tools/experiments/results/topic-44-human.yaml) |
| topic-45 | F-012 | **改良版 A** | 分岐 6 件のうち 4 件目、案 1 の改良版 A（環境差で 7 ケース全件分担、二層検証）採用 | [topic-45-human.yaml](../../../../tools/experiments/results/topic-45-human.yaml) |
| topic-46 | F-013 | 案 1 | 完全一致 13 件の一括採用、runtime F-013 同型 | [topic-46-human.yaml](../../../../tools/experiments/results/topic-46-human.yaml) |
| topic-47 | F-014 | 案 1 | 完全一致 13 件の一括採用、runtime F-012 同一作業 | [topic-47-human.yaml](../../../../tools/experiments/results/topic-47-human.yaml) |
| topic-48 | F-015 | 案 1 | 完全一致 13 件の一括採用、tasks.md 側で mode_diff／role_diff の命名差を design.md 既存スキーマと整合 | [topic-48-human.yaml](../../../../tools/experiments/results/topic-48-human.yaml) |
| topic-49 | A-004 | 案 1 | 完全一致 13 件の一括採用、runtime A-005 同型 | [topic-49-human.yaml](../../../../tools/experiments/results/topic-49-human.yaml) |
| topic-50 | A-005 | 案 1 | 完全一致 13 件の一括採用、runtime A-003 同型（粒度維持） | [topic-50-human.yaml](../../../../tools/experiments/results/topic-50-human.yaml) |
| topic-51 | A-006 | **別案** | 分岐 6 件のうち 5 件目、別案（前提追加 ＋ 責務欄／注釈で入力源と判定境界の対応関係を明示）採用 | [topic-51-human.yaml](../../../../tools/experiments/results/topic-51-human.yaml) |
| topic-52 | A-007 | **別案 A** | 分岐 6 件のうち 6 件目、別案 A（遅延管理テーブル DVT 新設 ＋ 参照仮称化）採用、将来拡張性重視 | [topic-52-human.yaml](../../../../tools/experiments/results/topic-52-human.yaml) |

集計：案 1 採用 14 件／別案採用 4 件（F-003 ／ F-012 改良版 A ／ A-006 ／ A-007 別案 A）／案 2 採用 0 件／合計 19 件（leave-as-is 4 件は除外）。

### 4.3 反映箇所

evaluation/tasks.md の修正箇所を行番号で記録。本セッション 33（2026-05-27）末時点で grep ／ Read による機械的照合済み。

| 議論論点 ／ 所見 | tasks.md の編集箇所 |
|---|---|
| 議論論点 1（F-001、ingestion_register 8 項目） | T-002 責務（行 52）：必須 8 項目（`bundle_id` ／ `run_id` ／ `source_repository_id` ／ `source_revision` ／ `review_mode` ／ `ingested_at` ／ `ingestion_status` ／ `missing_fields`）に揃え、`source_runtime_version` 削除。T-002 完了条件（行 58）：8 必須項目を明記 |
| 議論論点 2（F-002 ／ A-001 連動、analysis_run_manifest.yaml） | T-006 対応要件（行 104）：Req 5 受入 4 ／ 5 ／ Req 2 受入 6 追加。T-006 責務（行 105）：`analysis_run_manifest.yaml` 生成（9 項目）を追加。T-006 成果物（行 107-113）：`analysis_run_manifest_writer.py` 追加。T-006 完了条件（行 113）：9 項目出力の機械検証。T-006 テスト要件（行 114）：`analysis_run_manifest.yaml` 9 項目出力テスト。要件追跡表（行 192）：Req 5 受入分担明記 |
| 議論論点 3（F-003 別案、識別子連結保持） | T-001 対応要件（行 36）：「Req 5 受入 1〜3」 → 「Req 5 受入 1、3」（受入 2 縮約）。T-006 対応要件（行 104）：Req 5 受入 2 主担当として追加。T-006 成果物（行 107-113）：`identifier_link_validator.py` 追加（主担当）。T-007 前提タスク（行 123）：「T-006 機構を前提として利用」明記。T-009 前提タスク（行 151）：「T-006 機構を前提として利用」明記。T-011 完了条件（行 179）：Req 5 受入 2 の双方向整合チェック追加。要件追跡表（行 192）：「主担当（T-006）／利用（T-007 ／ T-009）／検証（T-011）」の 3 列構造で明示 |
| 議論論点 4（F-006、T-010 前提タスク） | T-010 前提タスク（行 164）：T-006 ／ T-007 ／ T-009 追加（T-006 ／ T-007 ／ T-008 ／ T-009 の 4 前提） |
| 議論論点 5（F-011 ／ A-003 連動、4 下流接合面の機械検証） | T-011 成果物（行 178）：`test_downstream_interface.py` 追加。T-011 完了条件（行 179）：4 下流接合面の機械検証手順を追加 |
| 議論論点 6（A-002、Req 9 受入 6） | T-007 対応要件（行 121）：Req 9 受入 6 追加。要件追跡表（行 196）：Req 9 → T-007（受入 1〜5・6）／T-009（受入 7 ／ 8）の分担明記 |
| should-fix F-007（T-009 前提に T-008） | T-009 前提タスク（行 151）：T-008 追加 |
| should-fix F-008（注記そのまま） | tasks.md 変更なし（現状の「foundation tasks T-001 と同じ運用に従う」注記を維持） |
| should-fix F-009（黙示的混入の操作的判定） | T-007 完了条件（行 130）：「有効母集団規則適用後の比較集計に invalid ／ analysis_blocked が 0 件であることを機械検査」補記 |
| should-fix F-012（改良版 A、環境差で二層検証） | T-003 テスト要件（行 73）：「単体検証（モック環境）：境界 7 ケース全件」明示。T-011 成果物（行 178）：「経路統合検証（実環境）：7 ケース全件を実環境経路でエンドツーエンド検証」を追記 |
| should-fix F-013（仕様文書／実体生成物の境界） | T-001 責務（行 37）：「仕様文書の配置先＝ `evaluation/analysis_layout/`、実体生成物の配置先＝ `experiments/analysis/`」を冒頭に明示 |
| should-fix F-014（語彙正本ハッシュ照合） | T-011 完了条件（行 179）：「語彙正本ハッシュ照合または参照のみ使用の機械検証手順」を明記 |
| should-fix F-015（findings_summary／findings_by_severity 区別） | T-009 責務（行 150）：mode_diff の `findings_by_severity`（design.md §レビューモード差分報告 行 464 命名）と role_diff の `findings_summary`（design.md §3 役所見差分報告 行 477 命名）を区別 |
| should-fix A-004（対称性検証の操作的判定） | T-002 完了条件（行 58）：「対称性検証の操作的判定：輸出前後のディレクトリツリーのパス構造ハッシュ照合または ls 結果の差分が空であることを検査」補記 |
| should-fix A-005（2 出力器の内部関係） | T-009 責務（行 150）：「内部関係：2 出力器は共通スキーマ（feature ／ target）を参照し、それぞれ独立の出力責務」明示 |
| should-fix A-006 別案（前提追加 ＋ 注釈／補記） | T-010 責務（行 163）：「選択ロジック判定境界の入力源は T-007 の `treatment_comparisons.json`、T-009 の exploratory 集計、必要に応じて T-006 の被覆率」補記。T-010 前提タスク（行 164）：各前提タスクに注釈付き（「T-006（被覆率計算完了：選択ロジック閾値判定に使用）」等） |
| should-fix A-007 別案 A（DVT 新設） | T-009 完了条件（行 156）：参照文字列を「`analysis` 仕様（起草予定）の下流接合面条件を満たす形式」と仮称化、「DVT-001 で管理」と明記。tasks.md 末尾に §遅延確認事項テーブル（DVT）セクション新設、DVT-001 として T-009 関連を登録。T-011 完了条件（行 179）：「DVT 内の未解除項目がない、または延期理由が明記されている」をゲート化 |

機械的照合：本セッション末に grep で全編集箇所を確認、訂正前文字列の残存ゼロ（後段で再確認予定）。

### 4.4 should-fix 11 件と leave-as-is 4 件の扱い

- **should-fix 11 件**の処理結果：
  - tasks.md 反映済み 10 件：F-007（行 151）／F-009（行 130）／F-012 改良版 A（行 73 ／ 178）／F-013（行 37）／F-014（行 179）／F-015（行 150）／A-004（行 58）／A-005（行 150）／A-006 別案（行 163 ／ 164）／A-007 別案 A（行 156 ／ 179 ／ §DVT）
  - tasks.md 変更なし 1 件：F-008（案 1 採用、現状の「foundation tasks T-001 と同じ運用に従う」注記を維持）
- **leave-as-is 4 件**（F-004 ／ F-005 ／ F-010 ／ F-016）：本記録に判定結果を残すのみ、tasks.md は修正しない
- **波及／遡及 0 件**：本セッションでは機能横断波及や上流文書遡及は発生せず、すべて機能内対処で完結

---

## 5. 関連参照

- 計画書 §5.9.1〜§5.9.3（レビュー方法の規律、所見メタデータ）
- 計画書 §5.23.12（サブエージェント方式の運用条件）
- 規律 [[must-fix-discussion-obligation]]（must-fix 対処の議論義務）
- 規律 [[implementation-autonomy]]（実装フェーズの自律進行）
- 前例レビュー記録：[runtime tasks 2026-05-27](../../runtime/reviews/2026-05-27-tasks-triad-review.md)、[foundation tasks 2026-05-26](../../foundation/reviews/2026-05-26-tasks-triad-review.md)
- 過去レビュー記録：[2026-05-22-requirements.md](2026-05-22-requirements.md)、[2026-05-25-design-triad-review.md](2026-05-25-design-triad-review.md)
