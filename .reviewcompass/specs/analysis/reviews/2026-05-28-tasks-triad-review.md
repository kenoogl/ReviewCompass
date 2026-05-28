---
type: tasks_triad_review
target: .reviewcompass/specs/analysis/tasks.md
target_commit: c742eac
target_content_hash: <未計測、本セッション 35 起草分（257 行、T-001〜T-011）>
date: 2026-05-28
mode: subagent_mediated
session: session-35-36
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: 約 2.5
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
    by_severity: { CRITICAL: 0, ERROR: 6, WARN: 10, INFO: 0 }
    count: 16
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 5, WARN: 7, INFO: 0 }
    count: 12
  judgment:
    by_judgment: { must-fix: 13, should-fix: 12, leave-as-is: 3 }
    by_waterfall: { 機能内対処: 26, 波及: 2, 遡及: 0, 延期: 0 }
    count: 28
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation／runtime／evaluation tasks-triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で「タスク 7」と言及のみで本体未整備、foundation tasks-triad-review（セッション 30）の仮設定を継承
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
  - 本記録は前セッション 35 で実施した 3 役レビューの結果をセッション 36 で起草。3 役の生出力はサブエージェントログ（~/.claude/projects/.../6f3aaa4a-.../subagents/）から復元
---

# レビュー記録：analysis tasks triad-review

本記録は analysis 機能の tasks.md（257 行、11 タスク T-001〜T-011、コミット `c742eac`）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。16 件の所見（CRITICAL 0／ERROR 6／WARN 10／INFO 0）を提示した。

### 主役所見一覧（16 件、F-001〜F-016）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | WARN | 行 185-196（要件追跡表） | Req 1 受入 2／3 が要件追跡表に個別エントリで現れない、受入基準粒度のトレーサビリティ欠落 | fact |
| F-002 | 1：上流仕様の網羅 | ERROR | 行 189、行 106-117（T-006） | Req 2 受入 2／3／4／5 が追跡表に個別示されない、T-006 の対応要件欄「Req 2 受入 1〜5」と一括記載 | fact |
| F-003 | 1：上流仕様の網羅 | WARN | 行 190、行 90-101（T-005） | Req 3 受入 1／3／4 が T-005 追跡表行で個別現れない | inference |
| F-004 | 2：タスク粒度の妥当性 | WARN | 行 147-161（T-009） | T-005 と T-009 の `mixed_review_mode` 検知責務境界が曖昧、design.md §証拠台帳モデル §3 では検知主体は派生段だが T-005 に `mixed_review_mode_detector.py` が含まれる | mixed |
| F-005 | 2：タスク粒度の妥当性 | WARN | 行 33-50（T-001） | T-001 成果物に `shared/conformance/`／`shared/convergence/`/`shared/manifests/` のサブディレクトリ列挙が欠落 | fact |
| F-006 | 3：依存順の整合性 | WARN | 行 106-108（T-006 前提） | T-006 前提に T-002（取り込み）が欠落、`source_artifact_refs` 解決テストが不成立になりうる | mixed |
| F-007 | 3：依存順の整合性 | ERROR | 行 124（T-007 前提）、行 136（T-008 前提） | T-008 前提に T-004（証拠台帳）が含まれない、T-007 前提に T-005 を入れない根拠不明 | mixed |
| F-008 | 4：完了条件の機械判定可能性 | ERROR | 行 47-48（T-001 完了条件 2） | T-001 の「人間レビューで承認されている」が機械判定不可、foundation T-001 の経緯注記が省略 | fact |
| F-009 | 4：完了条件の機械判定可能性 | WARN | 行 61（T-002 完了条件） | T-002 の「`runtime` 生証拠の一次参照経路が存在しないことが機械検証される」の機械的判定手段が曖昧 | fact |
| F-010 | 4：完了条件の機械判定可能性 | WARN | 行 160（T-009 完了条件） | T-009 の「`derivation_contract_version` の更新が `superseded` 履歴と整合」の機械判定方法不明 | mixed |
| F-011 | 5：テスト要件の妥当性 | ERROR | 行 175-183（T-011）、行 200-206 | T-011 のテストファイル 10 件のうち、無声昇格検出統合版を担うファイルが特定されていない | mixed |
| F-012 | 5：テスト要件の妥当性 | WARN | 行 181（T-011 成果物） | 混在レビューモード検知の統合テスト集約先（`test_destinations.py` か `test_caveat_register.py` か）が不明確 | inference |
| F-013 | 6：機能横断波及の早期検出 | ERROR | 行 26-27、行 213-215 | foundation 語彙正本件数が analysis tasks（7 件）と evaluation tasks（6 件）で食い違い、所有者 foundation 側で「7 件」の確定有無が未検証 | fact |
| F-014 | 6：機能横断波及の早期検出 | WARN | 行 59-61（T-002）、design.md 行 612-620 | T-002 完了条件に `evaluation` の 8 成果物の被覆確認が含まれない | mixed |
| F-015 | 7：成果物配置と命名の整合 | ERROR | 行 59-60（T-002）、design.md 行 98-141 | `intake_failure_report.json` の書き出し先（`analysis/shared/manifests/`）が T-002 本文に明示なし、実装者が誤認するリスク | fact |
| F-016 | 7：成果物配置と命名の整合 | WARN | 行 109-115（T-006） | `analysis/fragments/` ディレクトリが design.md の配置ツリーに存在しない | fact |

### 主役の注目発見

- **F-013**：本セッション 35 の縦整合チェックで「重大な不整合なし」と判定した evaluation について、主役が新規不整合を検出。foundation 語彙正本件数が文書間で食い違う事実は §5.23.13.3 残り 27 件の枠を超える新規事象。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への counter_status 付与（16 件）

| 主役 ID | counter_status | counter_rationale 要約 |
|---|---|---|
| F-001 | no_counter_evidence_after_challenge | 追跡表行 189 で Req 1 は「T-003／T-004／T-002」のみ表記、受入 2／3 の個別対応が確認不能、所見妥当 |
| F-002 | no_counter_evidence_after_challenge | T-006 責務文行 107 は「受入 1〜5」と一括、追跡表行 190 も Req 2 を T-006／T-010 でまとめて表記、受入個別性が消失 |
| F-003 | no_counter_evidence_after_challenge | 追跡表行 191 で Req 3 が T-005 単独表記、受入 1〜5 のうちどれが対応するか個別表示なし、妥当 |
| F-004 | counter_evidence_raised | design.md §証拠台帳モデル §3 行 275 で検知主体は派生段（destination deriver）と明記、T-005 の `mixed_review_mode_detector.py` は検知ロジック所有でなく書き出し責務として配置可能 |
| F-005 | no_counter_evidence_after_challenge | T-001 責務文（行 37）は「5 サブディレクトリ」と列挙、`shared/conformance/`／`shared/convergence/`／`shared/manifests/` は責務文に含まれるが成果物欄に README 未列挙 |
| F-006 | counter_evidence_raised | T-006 前提行 108 は「T-003（参照書式）、T-004（`maturity_label`）」、T-003 の前提が T-002 を含むため間接的に T-002 完了は保証される、依存ツリー上は欠落でない |
| F-007 | no_counter_evidence_after_challenge | T-008 前提（行 138）は T-002／T-003 のみ、`source_artifact_refs` で証拠台帳エントリを参照するなら T-004 完了が必要、T-007 前提（行 124）の T-005 不要根拠は不在 |
| F-008 | no_counter_evidence_after_challenge | T-001 完了条件 2「人間レビューで承認」は機械判定不可、foundation T-001 の同等条文と同様だが本 tasks の経緯注記が完了条件欄に省略、所見妥当 |
| F-009 | no_counter_evidence_after_challenge | T-002 完了条件「`runtime` 生証拠の一次参照経路が存在しないことが機械検証される」の手段（imports グラフ静的検査／パス検索）未定義、所見妥当 |
| F-010 | no_counter_evidence_after_challenge | T-009 完了条件「`derivation_contract_version` の更新が `superseded` 履歴と整合」の検証手段（diff 演算／version chain 検査）未定義、所見妥当 |
| F-011 | no_counter_evidence_after_challenge | T-011 のテストファイル群行 181 で `test_traceability.py` のみ列挙、無声昇格専用ファイルなし、所見妥当 |
| F-012 | no_counter_evidence_after_challenge | T-005／T-009／T-011 の 3 連携で集約先テストファイルが行 181 で明示されない、`test_caveat_register.py`／`test_destinations.py` に分散の可能性、所見妥当 |
| F-013 | counter_evidence_raised | foundation 側の語彙正本数も不確定（foundation/design.md 行 644 で 4 件、行 736 で 6 件、判断 7 では §3／§4 委譲で曖昧）、analysis ／ evaluation の食い違いは下流側のみの問題でなく上流の不確定性に起因、所見の severity は ERROR より WARN が妥当との反論成立 |
| F-014 | counter_evidence_raised | T-002 は取り込み段の責務で「`evaluation` の成果物と `conformance-evaluation` の成果物」を読むと明記（行 56）、被覆確認の責務は T-011 の機能横断検証に委ねる設計、T-002 完了条件に含めるべき強い根拠なし |
| F-015 | no_counter_evidence_after_challenge | T-002 成果物行 60 は `intake_failure_report.schema.json` のみ列挙、`intake_failure_report.json` 自体の書き出し先パスが本文に明示なし、所見妥当 |
| F-016 | no_counter_evidence_after_challenge | T-006 成果物行 114 で `analysis/fragments/fragment_builder.py`／`fragment.schema.json` が指定されるが、design.md §分析向け成果物配置ツリー（行 102-141）に `fragments/` 配下は存在しない、所見妥当 |

集計：counter_evidence_raised 4 件（F-004／F-006／F-013／F-014）／ no_counter_evidence_after_challenge 12 件 ／ not_assessed 0 件。

### 2.2 独立発見（12 件、A-001〜A-012、ERROR 5／WARN 7／INFO 0）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| A-001 | 7：成果物配置と命名の整合 | ERROR | 行 33-50（T-001）、行 163-173（T-010）、design.md 行 114 | `analysis/shared/manifests/analysis_manifest.yaml`（本機能の論理版と入力被覆を記録）が design.md で正本宣言されているが、tasks.md 全 11 タスクの成果物欄に出現しない（grep ヒットゼロ）。`analysis_logic_version` の確定先不明 | fact |
| A-002 | 4：完了条件の機械判定可能性 | ERROR | 行 130（T-007 完了条件） | T-007 完了条件「本機能の可視化結果が `evaluation` のメトリクス契約を上書きしないことが構造的に保証される」が機械検証手順として未定義 | fact |
| A-003 | 3：依存順の整合性 | ERROR | 行 152（T-009 前提）、行 168（T-010 前提） | T-009 の「`mixed_review_mode` 検知時は `caveat_register` に自動付与」は T-005 → T-009 → T-005 の循環参照になりうる、書き戻し方向（追加のみ／上書き不可）が責務として未分離 | mixed |
| A-004 | 5：テスト要件の妥当性 | ERROR | 行 175-183（T-011） | テスト戦略「証拠追跡性の機械検証」が T-003 と T-011 連携だが、T-003 単体テストと T-011 統合テストの責務分担（境界／重複／包含）が未定義 | mixed |
| A-005 | 6：機能横断波及の早期検出 | ERROR | 行 26-27、行 214 | foundation 語彙正本「7 件」のうち `confidence_label` を含めているが、foundation/design.md §判断 7 の語彙正本所有列挙では `confidence_label` は §3.5 で独立節として扱われ「正本所有」とは明示されない。「7 件」の確定根拠が analysis 側の独自カウントで越権参照 | fact |
| A-006 | 4：完了条件の機械判定可能性 | WARN | 行 87（T-004 完了条件） | T-004 完了条件「foundation 4 語彙（`evidence_class`／`review_mode`／`counter_status`／`final_label`）を再定義せず参照のみで使用」と書かれるが、`final_label` が T-004 スキーマに登場しない | fact |
| A-007 | 2：タスク粒度の妥当性 | WARN | 行 103-117（T-006） | T-006 は「図表束」と「報告断片」の 2 責務領域を 1 タスクに統合、報告断片の `text_stub` ／ `applicable_destinations` の符号化が責務文に欠落 | fact |
| A-008 | 5：テスト要件の妥当性 | WARN | 行 145（T-008 テスト要件）、design.md 行 626-633 | T-008 完了条件「必須 6 項目」と design.md 行 630「必須 9 件」（conformance-evaluation §14.5 由来）の数の食い違いの説明欠落 | mixed |
| A-009 | 7：成果物配置と命名の整合 | WARN | 行 154-158（T-009 audit_writer） | T-009 の `audit_writer.py` 出力に `conformance_violations_detail.json` が含まれるが、T-008 の `derived_audit_writer.py` と同一の `destinations/audit/` 配下成果物。書き手の重複あり | fact |
| A-010 | 6：機能横断波及の早期検出 | WARN | 行 27（contract consumer 原則）、design.md 行 595-597 | analysis 所有 4 正本（`maturity_label`／`limitation_type`／`fragment_type`／`regeneration_status`）の下流参照禁止宣言が tasks.md にも design.md にも不在 | inference |
| A-011 | 1：上流仕様の網羅 | WARN | 行 192（追跡表 Req 4 行） | Req 4 受入 5（「下流の叙述変換を明示的かつ版管理可能とする」）が追跡表で個別エントリとして欠落、T-009 の `derivation_contract_version` 実装と結びつかない | fact |
| A-012 | 4：完了条件の機械判定可能性 | WARN | 行 172（T-010 完了条件） | T-010 完了条件「再生成対象の登録条件 3 件が機械検証される」の検出機構（poll／hook／timestamp 比較）が未定義 | inference |

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 判定結果一覧（28 件）

| ID | 観点 | severity | judgment | 波及種別 | 根拠（要約） |
|---|---|---|---|---|---|
| F-001 | 1 | WARN | should-fix | 機能内対処 | 追跡表に行追加で完結、T-011 双方向整合チェックで機械検出される可能性 |
| F-002 | 1 | ERROR | must-fix | 機能内対処 | Req 2 受入 4 件分が T-006 一括で個別化されておらず、追跡可能性が機械検証不能 |
| F-003 | 1 | WARN | should-fix | 機能内対処 | Req 3 受入を T-005 行で個別化、追跡表の受入粒度を揃える小修正 |
| F-004 | 2 | WARN | leave-as-is | 機能内対処 | 敵対役反証成立、T-005 に detector を置き T-009 派生段で発火という責務分担は design.md §305 と整合 |
| F-005 | 2 | WARN | should-fix | 機能内対処 | T-001 成果物欄に `shared/` 配下 3 サブディレクトリ README が未列挙、配置宣言の明示性向上に必要 |
| F-006 | 3 | WARN | leave-as-is | 機能内対処 | 敵対役反証成立、T-006 は T-003 経由で T-002 を間接前提に持ち依存閉包は成立 |
| F-007 | 3 | ERROR | must-fix | 機能内対処 | T-008 は `caveat_register` の無効化標識を集約するため T-004 完了が前提、前提行修正必須 |
| F-008 | 4 | ERROR | must-fix | 機能内対処 | T-001 完了条件 2「人間レビューで承認」は機械判定不可で本文書冒頭の規律と矛盾、具体検証式に置換必須 |
| F-009 | 4 | WARN | should-fix | 機能内対処 | 「`runtime` 生証拠の一次参照経路が存在しない機械検証」の具体（import 検査、grep 等）を T-002 テスト要件に明記すべき |
| F-010 | 4 | WARN | should-fix | 機能内対処 | T-009 「`derivation_contract_version` 更新が `superseded` 履歴と整合」の機械判定式（前版 ref 存在、単調増加等）を完了条件に明記すべき |
| F-011 | 5 | ERROR | must-fix | 機能内対処 | T-011 のテストファイル 10 件に「無声昇格検出」担当を割当不在、`test_evidence_register.py` に担務として明記必須 |
| F-012 | 5 | WARN | should-fix | 機能内対処 | 混在レビューモード検知統合テストを `test_caveat_register.py` または `test_destinations.py` に担務明記すべき |
| F-013 | 6 | ERROR | must-fix | 波及 | 敵対役反証は severity 見直しに留まり件数食い違い自体は実在、機能横断段で foundation／evaluation の整合是正が必要 |
| F-014 | 6 | WARN | leave-as-is | 機能内対処 | 敵対役反証成立、被覆確認は T-011 統合段で実施する設計が妥当 |
| F-015 | 7 | ERROR | must-fix | 機能内対処 | T-002 本文の成果物欄に `analysis/shared/manifests/intake_failure_report.json` 自体が成果物として明記されていない、明示追加必須 |
| F-016 | 7 | WARN | should-fix | 機能内対処 | T-006 成果物の `fragments/` が design.md §配置ツリーに不在、ツリーへの追記または T-001 成果物に組み込みが必要 |
| A-001 | 7 | ERROR | must-fix | 機能内対処 | `analysis_manifest.yaml` の作成・配置タスクが 11 タスクのどこにも明記されていない、T-002 または T-009 に組み込み必須 |
| A-002 | 4 | ERROR | must-fix | 機能内対処 | T-007 完了条件「メトリクス契約を上書きしない」の機械検証手順（書き込み先除外検査、参照のみ検査等）未定義、具体化必須 |
| A-003 | 3 | ERROR | must-fix | 機能内対処 | T-005／T-009 の `caveat_register` 書き戻し方向に明示分離なく循環参照可能性あり、T-005 が detector 提供／T-009 が呼び出して追加のみ（上書き禁止）と明確化必須 |
| A-004 | 5 | ERROR | must-fix | 機能内対処 | T-003 単体テストと T-011 統合テストの「証拠追跡性」責務分担（境界／重複／包含）未定義、T-011 責務文に明示必須 |
| A-005 | 6 | ERROR | must-fix | 波及 | F-013 と同根、foundation 正本「7 件」の正式確定が foundation 側 design.md にないまま analysis が 7 件と数えるのは越権、機能横断段で双方向整合是正 |
| A-006 | 4 | WARN | must-fix | 機能内対処 | T-004 完了条件と T-004 スキーマ範囲の内部矛盾、放置すると T-011 双方向整合チェック失敗（severity は WARN だが must-fix 格上げ） |
| A-007 | 2 | WARN | should-fix | 機能内対処 | T-006 で図表束と報告断片の 2 責務統合は許容だが、報告断片の `text_stub`／`applicable_destinations` 符号化が責務文に欠落、責務文補強推奨 |
| A-008 | 5 | WARN | must-fix | 機能内対処 | T-008 完了条件「必須 6 項目」と design.md 行 630「必須 9 件」の関係を明示必須（6 項目は本機能の取り込み成果物スキーマ、9 件は元データのスキーマ） |
| A-009 | 7 | WARN | should-fix | 機能内対処 | T-009 `audit_writer.py` と T-008 `derived_audit_writer.py` の `conformance_violations_detail.json` 書き手重複、単一化または責務分離の明示が必要 |
| A-010 | 6 | WARN | should-fix | 機能内対処 | analysis 所有 4 正本の下流参照禁止／許容宣言が不在、`self-improvement` 等への明示宣言追加が望ましい |
| A-011 | 1 | WARN | should-fix | 機能内対処 | Req 4 受入 5（下流叙述変換の明示・版管理）が追跡表で個別行不在、T-009（`derivation_contract_version`／`manifest.yaml`）に明示割当 |
| A-012 | 4 | WARN | should-fix | 機能内対処 | T-010「再生成対象の登録条件 3 件が機械検証される」の検出機構（差分検出方式）未定義、timestamp 比較／hash 比較等の具体化が望ましい |

### 3.2 集計

- **判定別**：must-fix 13 件／should-fix 12 件／leave-as-is 3 件
- **波及別**：機能内対処 26 件／波及 2 件（F-013／A-005、foundation 語彙正本件数の同根問題）／遡及 0 件／延期 0 件
- **観点別**：観点 1（要件追跡）4 件／観点 2（タスク責務境界）3 件／観点 3（依存順）3 件／観点 4（完了条件の機械判定可能性）6 件／観点 5（テスト戦略）4 件／観点 6（語彙正本・整合）4 件／観点 7（配置・成果物）4 件

### 3.3 判定役の総評

28 件中 leave-as-is は 3 件のみ（F-004／F-006／F-014、いずれも敵対役の counter_evidence_raised が成立）。残り 25 件は何らかの修正を要する。

機能内対処の must-fix 11 件は次の構造的問題を含む：

- **配置宣言の欠落**：A-001（`analysis_manifest.yaml` 欠落）、F-015（`intake_failure_report.json` 書き出し先未明示）
- **完了条件の機械判定可能性違反**：F-008（人間レビュー承認）、A-002（構造的保証の手順未定義）
- **依存順の欠落**：F-007（T-008 前提 T-004 欠落）、A-003（書き戻し方向未分離による循環参照）
- **テスト責務分担の欠落**：F-011（無声昇格統合担当）、A-004（T-003／T-011 責務分担）
- **追跡表粒度欠落**：F-002（Req 2 受入 4 件分の追跡）
- **接合面整合**：A-006（T-004 完了条件と T-004 スキーマの内部矛盾）、A-008（取り込み元 9 件と取り込み先 6 件の対応未明示）

機能横断波及 2 件（F-013／A-005）は同根（foundation 語彙正本件数の食い違い）であり、`.reviewcompass/pending-cross-feature-findings.md` に 1 件として集約する。

利用者と must-fix 13 件を議論する際、特に優先 1（A-001／F-015／F-008）は完成判定基準に直結する基盤的欠落のため最優先（規律 [[must-fix-discussion-obligation]]）。

---

## 4. 統合節（integration、対処方針と利用者議論履歴）

本節は規律 [[must-fix-discussion-obligation]] に従い、must-fix 13 件の対処方針案を提示し、利用者議論を経て確定方針と反映箇所を記録する。

### 4.1 must-fix 13 件の対処方針案（利用者議論前）

機能内対処 11 件と波及 2 件に分けて整理する。

#### 4.1.1 機能内対処 11 件（優先順位順）

| 優先 | ID | 対処方針案（議論前） |
|---|---|---|
| 1 | A-001 | T-002 の成果物に `analysis/shared/manifests/analysis_manifest.yaml` と `analysis_manifest.schema.json` を追加、責務に「`analysis_logic_version`／入力被覆／生成日時の記録」を明記。あるいは T-001 で manifests ディレクトリ準備時に空 manifest を生成、T-002 で内容書き込み |
| 1 | F-015 | T-002 成果物に `analysis/shared/manifests/intake_failure_report.json` を実体ファイルとして追加、責務文で書き出し先を明示 |
| 1 | F-008 | T-001 完了条件 2 を機械判定可能な式に置換：「README または ANALYSIS.md が存在し、必須 N 節（規約／配置／インデックス）を含む」を grep で検証 |
| 2 | A-006 | 2 案：(a) T-004 完了条件から `final_label` を削除（実装と整合）、(b) T-004 スキーマに `final_label` を追加して整合させる。要件側に判断を仰ぐ |
| 2 | F-007 | T-008 の前提タスクに T-004 を追加。T-007 の前提タスクに T-005 を追加または「T-005 不要根拠」を本文に明示 |
| 2 | F-002 | 要件追跡表の T-006 行を Req 2 受入別に 4 行に分解、または T-006 責務文で受入別の担当成果物を明示 |
| 3 | A-002 | T-007 完了条件に「書き込み先パスが `analysis/destinations/` 配下に限定されること」と「`evaluation` 配下への書き込みがないこと」を grep または AST 検査で機械検証 |
| 3 | A-003 | T-005 責務に「`mixed_review_mode_detector` を提供（書き戻し責任は T-009 が持つ）」と明記、T-009 完了条件に「`caveat_register` への書き込みは追加のみで上書き禁止」を機械検証として追加 |
| 3 | A-008 | T-008 完了条件に「`conformance_intake.json` の必須 6 項目と上流 `conformance-evaluation §14.5` の必須 9 件の対応マッピング」を明記、または design.md 行 626-633 の §14.5 参照節に対応表を追加 |
| 4 | F-011 | T-011 テストファイル一覧の `test_evidence_register.py` 担務に「無声昇格検出統合版（design.md §テスト戦略 §2 由来）」を明記 |
| 4 | A-004 | T-011 責務文に「T-003 単体テストは個別 finding の参照解決可能性、T-011 統合テストは全証拠の追跡経路を通すスモーク」と責務境界明示 |

#### 4.1.2 機能横断波及 2 件（pending 追記）

| ID | 観点 | 対処方針案 |
|---|---|---|
| F-013／A-005 | 6 | 同根問題として `.reviewcompass/pending-cross-feature-findings.md` に **A-018** として 1 件で追記、機能横断段（tasks review-wave）で foundation／evaluation／analysis の整合是正。foundation 側で語彙正本の所有件数を確定（4 件か 6 件か 7 件か）し、analysis／evaluation tasks の完成判定基準を整合させる |

### 4.2 利用者議論履歴

（must-fix 13 件の議論はセッション 36 以降で実施。1 件ずつ平易な日本語で対処方針を提案し、後段影響の深掘りを示してから合意。本節は議論進行に応じて追記。）

### 4.3 反映箇所

（利用者議論を経て確定した対処を tasks.md に反映後、grep／Read で機械的に照合した結果を本節に記録。）

### 4.4 should-fix 12 件と leave-as-is 3 件の扱い

- **should-fix 12 件**（F-001／F-003／F-005／F-009／F-010／F-012／F-016／A-007／A-009／A-010／A-011／A-012）：機能内対処の優先順位は must-fix の次。本セッションの議論範囲に含める想定だが、利用者判断で「must-fix 完了後に一括対処」「pending に持ち越し」も可
- **leave-as-is 3 件**（F-004／F-006／F-014）：いずれも敵対役の counter_evidence_raised が成立。修正不要、本記録の §3 で判定根拠を残すのみ

### 4.5 機能横断波及 2 件（F-013／A-005）の扱い

- 同根問題のため `.reviewcompass/pending-cross-feature-findings.md` に **A-018** として 1 件で追記
- 機能横断段（tasks review-wave）で foundation 側を含めた整合是正
- 7 モデル比較実験の **2 回目**（機能横断段の 7 モデル評価、2026-05-28 セッション 35 で確定した 2 回方式）で同根問題として評価対象とする

---

## 5. 関連参照

- 規律：[discipline_must_fix_discussion_obligation.md](../../../../docs/disciplines/discipline_must_fix_discussion_obligation.md)
- 過去の同型レビュー記録：
  - [foundation/reviews/2026-05-26-tasks-triad-review.md](../../foundation/reviews/2026-05-26-tasks-triad-review.md)
  - [runtime/reviews/2026-05-27-tasks-triad-review.md](../../runtime/reviews/2026-05-27-tasks-triad-review.md)
  - [evaluation/reviews/2026-05-27-tasks-triad-review.md](../../evaluation/reviews/2026-05-27-tasks-triad-review.md)
- 計画書：§5.5（5 段構造）／ §5.9.1〜§5.9.3（3 役レビュー）／ §5.23.12（サブエージェント方式）
- 運営ガイド：§3.3 (a-1) must-fix 所見の対処手順
- 持ち越し所見ファイル：[pending-cross-feature-findings.md](../../../pending-cross-feature-findings.md)
- レビュー記録雛形：[manual_dogfooding_review_template.md](../../../../templates/review/manual_dogfooding_review_template.md)
- サブエージェント生ログ復元元：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/6f3aaa4a-9d94-4ae1-b834-d793e6a1a491/subagents/`（主役 ／ 敵対役 ／ 判定役の 3 jsonl）
