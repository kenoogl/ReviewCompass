---
type: tasks_triad_review
target: .reviewcompass/specs/foundation/tasks.md
target_commit: 9f1f472
target_content_hash: <未計測、本セッションで起草された tasks.md コミット版>
date: 2026-05-26
mode: subagent_mediated
session: session-30
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: <約 8>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <約 3>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <約 1>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 6, INFO: 3 }
    count: 12
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 1, WARN: 5, INFO: 3 }
    count: 9
  judgment:
    by_judgment: { must-fix: 10, should-fix: 7, leave-as-is: 4 }
    by_waterfall: { 機能内対処: 20, 波及: 1, 遡及: 0, 延期: 0 }
    count: 21
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（実験(エ)継続、design.triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で「タスク 7」と言及のみで本体未整備、本セッション限りの仮設定（利用者承認「はい」2026-05-26 セッション 30）
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：foundation tasks triad-review

本記録は foundation 機能の tasks.md（193 行、10 タスク T-001〜T-010）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（実験(エ)継続、design.triad-review と同配置）。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は本セッション仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。12 件の所見（CRITICAL 0／ERROR 3／WARN 6／INFO 3）を提示した。

### 主役所見一覧（12 件、F-001〜F-012）

| ID | 観点 | severity | target_location | description | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | ERROR | T-004 行 75 | review_case.schema.json 必須項目が tasks.md「9 項目」、design.md §4「8 項目」で食い違い、design-triad-review.md 行 235 で 9 → 8 修正済みだが tasks.md に未反映 | fact |
| F-002 | 1：上流仕様の網羅 | ERROR | T-003 行 62・65 | 責務欄「4 種の状態語彙」と完了条件欄「5 種の語彙（実際は 6 語彙を列挙）」の数値不整合 | fact |
| F-003 | 1：上流仕様の網羅 | ERROR | T-003 行 62 | 「必須項目 22 件」が design.md §3 のテーブル 20 項目と乖離（2 項目過多） | fact |
| F-004 | 5：テスト要件の妥当性 | WARN | T-009 行 135 | テスト戦略「語彙正本整合」で severity（4 値）／final_label（3 値）／confidence_label（3 値）の 3 語彙がカバーされない | fact |
| F-005 | 4：完了条件の機械判定可能性 | WARN | T-001 行 45 | 完了条件「規約が記述されている」に充足性の機械判定基準なし | fact |
| F-006 | 4：完了条件の機械判定可能性 | WARN | T-004 行 80 | enum 値の参照先「§判断 7」は所有関係宣言節、実際の enum 値は §4 finding 節と §4 necessity_judgment 節 | fact |
| F-007 | 1：上流仕様の網羅 | WARN | T-004 行 70 | 対応設計節に design.md §5 段別再演モデル（review_case の step_records 由来）が欠落 | fact |
| F-008 | 3：タスク依存順の整合性 | WARN | T-002 行 51 | Requirement 2 受入 2（ベンダー名非埋め込み）の対応タスクが要件追跡表に不明示 | fact |
| F-009 | 5：テスト要件の妥当性 | WARN | T-009 行 139 | 累積テスト件数「60 件＋」の積算基点が未定義 | fact |
| F-010 | 7：成果物配置と命名の整合 | WARN | T-008 行 127 | 成果物欄「書き込み権限なし」が意味不明 | fact |
| F-011 | 6：機能横断波及の早期検出 | INFO | 全体 | 機能横断波及への明示的言及がない（pending-cross-feature-findings.md は対処済み 0 件のため致命でない） | fact |
| F-012 | 2：タスク粒度の妥当性 | INFO | T-008 ／ T-009 | 符号化規約整合の検証で T-008（Python スクリプト）と T-009（pytest）の重複可能性 | mixed |

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論または同意（12 件）

| ID | counter_status | counter_rationale 要約 |
|---|---|---|
| F-001 | no_counter_evidence_after_challenge | 同意。design.md §4 review_case で必須 8 項目を機械的に確認 |
| F-002 | counter_evidence_raised | 反証。「4 種」は責務分離 4 種で正しい、「5 種」が誤記（実際の列挙は 6 種）。ERROR ではなく WARN レベル |
| F-003 | no_counter_evidence_after_challenge | 同意。design.md §3 テーブル 20 項目を機械的に確認 |
| F-004 | no_counter_evidence_after_challenge | 同意。語彙正本整合のカバレッジが 3 語彙で漏れる |
| F-005 | no_counter_evidence_after_challenge | 同意。完了条件の充足基準が文字列有無のみで不十分 |
| F-006 | no_counter_evidence_after_challenge | 同意。§判断 7 は所有関係宣言、enum 値は §3 と §4 が正本 |
| F-007 | no_counter_evidence_after_challenge | 同意。step_records 参照には §5 の明示が必要 |
| F-008 | counter_evidence_raised | 反証。要件追跡表で T-002 が Requirement 2 担当として明示済み、INFO 相当に下げるべき |
| F-009 | no_counter_evidence_after_challenge | 同意。基点未定義で充足判断不可 |
| F-010 | no_counter_evidence_after_challenge | 同意。「書き込み権限なし」は属性指定として意味不明 |
| F-011 | no_counter_evidence_after_challenge | 同意。読者が参照経路を持たない |
| F-012 | counter_evidence_raised | 反証。T-008 と T-009 は責務分離が明示済み（テスト戦略継承表 行 168）、leave-as-is 相当 |

### 2.2 独立発見（9 件、A-001〜A-009、ERROR 1／WARN 5／INFO 3）

| ID | 観点 | severity | target_location | description | evidence_type |
|---|---|---|---|---|---|
| A-001 | 1：上流仕様の網羅 | ERROR | T-003 行 65-66 | run_status（4 値：created／in_progress／closed／orchestration_failed）と human_signoff_status（4 値：pending／approved／rejected／deferred）の値テストが完了条件・テスト要件から欠落 | fact |
| A-002 | 7：成果物配置と命名の整合 | WARN | 要件追跡表 行 159 | Requirement 5 の対応タスクが要件追跡表で T-001 担当だが、T-001 本文の対応要件欄に Requirement 7 のみ列挙、双方向不整合 | fact |
| A-003 | 4：完了条件の機械判定可能性 | WARN | T-007 行 116 | 「役ごとのモデル識別子 ／ 対象アプリの言語 ／ 規約版 ／ 証拠出力先 ／ 既定の phase ／ profile」表記が「／」を項目区切りと連用、「既定の phase」と「profile」を別項目と誤読する余地（design.md §10 では 1 項目） | fact |
| A-004 | 3：タスク依存順の整合性 | WARN | T-009 行 136 | 前提タスクに T-001 が含まれず、tests/foundation/ ディレクトリ準備責任の所在が不明 | fact |
| A-005 | 4：完了条件の機械判定可能性 | WARN | T-010 行 148 | 完了条件「レポート出力が design.md §完成判定基準と一致」のレポート（YAML）構造が未定義 | fact |
| A-006 | 5：テスト要件の妥当性 | WARN | T-006 行 106 | frontmatter の step 値の 3 値整合（primary_detection／adversarial_review／judgment）が明示されない | fact |
| A-007 | 1：上流仕様の網羅 | INFO | 要件追跡表 行 154-161 | 要件追跡表が片方向のみで、双方向整合の機械検証手順なし | fact |
| A-008 | 2：タスク粒度の妥当性 | INFO | T-004 行 68-81 | 5 スキーマを 1 タスクとした粒度判断の根拠が個別明示されていない | inference |
| A-009 | 6：機能横断波及の早期検出 | INFO | 全体 | 各タスクの完了条件に下流仕様（6 機能）の参照禁止対象の機械整合チェックが含まれない | fact |

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 判定結果一覧（21 件）

| ID | judgment | waterfall | judgment_rationale 要約 |
|---|---|---|---|
| F-001 | must-fix | 機能内対処 | design.md §4 確定 8 項目と tasks.md「9 項目」の不整合、機械検証で確実に検出される項目数差異 |
| F-002 | must-fix | 機能内対処 | WARN 相当だが完了条件の機械判定可能性に直結するため must-fix に格上げ。「5 種」を「6 種」に訂正、または列挙語彙数の整理 |
| F-003 | must-fix | 機能内対処 | テスト要件「必須項目数テスト」が直接参照する数字のため修正必須 |
| F-004 | must-fix | 機能内対処 | 語彙正本整合の網羅性に直結 |
| F-005 | should-fix | 機能内対処 | T-001 は README 群と FOUNDATION.md でレビュー判定が自然、完了条件強化は望ましいが必須でない |
| F-006 | must-fix | 機能内対処 | 参照先の不正確はテスト要件で参照する正本箇所のため修正必須 |
| F-007 | should-fix | 機能内対処 | 対応設計節欠落、完了条件への影響なし |
| F-008 | leave-as-is | 機能内対処 | 敵対役反証どおり T-002 で自然に担保、INFO 相当 |
| F-009 | must-fix | 機能内対処 | 累積件数の基点未定義は機械判定不能 |
| F-010 | must-fix | 機能内対処 | 「書き込み権限なし」は誤記または不要記述、削除必須 |
| F-011 | should-fix | 波及 | pending-cross-feature-findings.md に追加すべき波及項目 |
| F-012 | leave-as-is | 機能内対処 | 責務分離は明示済み、敵対役反証どおり |
| A-001 | must-fix | 機能内対処 | run_status／human_signoff_status の値テスト欠落は語彙正本整合の網羅性に直結 |
| A-002 | must-fix | 機能内対処 | 要件追跡表と本文の双方向不整合は機械検査で必ず引っかかる |
| A-003 | should-fix | 機能内対処 | 表記の誤読防止は望ましいが機械判定への直接影響は小さい |
| A-004 | should-fix | 機能内対処 | T-001 は暗黙の前提とも解釈可能、明示すべきだが完了条件は機械判定可能 |
| A-005 | must-fix | 機能内対処 | レポート形状の最低限の明示が必須 |
| A-006 | should-fix | 機能内対処 | step 値の整合は完了条件に含まれると解釈可能、明示が望ましい |
| A-007 | should-fix | 機能内対処 | 双方向整合の機械検証手順を T-009／T-010 に追加すべきだが INFO 相当 |
| A-008 | leave-as-is | 機能内対処 | 概要・変更意図節で総論的に説明済み |
| A-009 | leave-as-is | 機能内対処 | foundation 段階では下流仕様未確定、conformance-evaluation の責務 |

### 3.2 集計

- **判定別**：must-fix 10 件／should-fix 7 件／leave-as-is 4 件
- **波及別**：機能内対処 20 件／波及 1 件（F-011）／遡及 0 件／延期 0 件

### 3.3 判定役の総評

must-fix 10 件のうち 8 件は数値・参照先・テスト網羅性に関する具体的記述ミスで、機械判定可能性に直結する（F-001／F-002／F-003／F-006／F-009／F-010／A-001／A-005）。F-002 は敵対役反証を受けて「完了条件の数字記述自体が誤記」という核心は維持しつつ WARN → must-fix へ格上げ。F-004／A-002 は要件追跡・語彙網羅性に関わるため must-fix。F-011 のみ機能横断波及のため pending-cross-feature-findings.md への追加を要する。遡及（上流修正）と延期はなし。F-008／F-012／A-008／A-009 は反証または責務範囲外として leave-as-is。

利用者と must-fix 10 件を議論する際、特に F-001（review_case 必須項目数 8 か 9 か）と F-003（メタデータ必須項目数 20 か 22 か）は design.md 側の数え方確認が前提のため、まず数字確定の協議を勧める（規律 [[must-fix-discussion-obligation]]）。

---

## 4. 統合節（integration、対処方針と利用者議論履歴）

本節は規律 [[must-fix-discussion-obligation]] に従い、must-fix 所見ごとの対処方針案を提示し、利用者議論を経て確定方針と反映箇所を記録する。

### 4.1 must-fix 10 件の対処方針案（利用者議論前）

#### 議論論点 1：F-001 review_case 必須項目数 9 → 8

**事実**：tasks.md T-004 行 75「review_case.schema.json（必須 9 項目）」。design.md §4 review_case 節を機械的にカウントすると 8 項目（run_id／target_id／run_metadata_ref／step_records／findings／validator_result_refs／invalidation_marker_refs／integration_summary）。design.triad-review.md 行 235 に「9 → 8 項目（failure_observations を削除）」と確定経緯あり。

**候補案**：

- (案 1) tasks.md T-004 の「必須 9 項目」を「必須 8 項目」に訂正、テスト要件の「必須項目数テスト」も 8 で記述
- (案 2) design.md を再確認し、もし 9 項目が正しいなら design.md 側を修正（遡及）

**深掘り**：

- 後段影響：T-004 実装時のテスト件数（必須項目数テスト）が 1 件減る、回帰検出力に影響なし
- design.md 確認結果：機械的カウントで 8 項目を確認、design.triad-review.md にも 9 → 8 経緯あり
- 案 2 の遡及は不要（design.md は確定済み、tasks.md の誤りが正しい認識）

**推奨**：案 1（tasks.md を 8 項目に訂正、遡及不要）

---

#### 議論論点 2：F-002 T-003 の語彙数記述（5 種 → 6 種）

**事実**：tasks.md T-003 行 62「4 種の状態語彙」（責務分離 4 種：run_status／validator_status／human_signoff_status／evidence_class、design.md §3 と整合）。行 65 完了条件「5 種の語彙（実際は 6 語彙を列挙）」。敵対役反証どおり「5 種」が誤記、実際の列挙語彙数は 6（validator_status／evidence_class／review_mode／confidence_label に加え暗黙の責務分離 2 つ）。

**候補案**：

- (案 1) 完了条件の「5 種の語彙」を「6 種の語彙」に訂正、列挙数と一致させる
- (案 2) 列挙を 5 語彙に絞る（confidence_label を別行として整理）

**深掘り**：

- design.md §3 と §3.5 では合計 6 語彙が foundation 所有正本として定義（run_status／validator_status／human_signoff_status／evidence_class／review_mode／confidence_label）
- 案 1 は責務分離 4 種と語彙正本 6 種の両方を tasks.md で扱える
- 案 2 は confidence_label を別タスクに分離する案だが、tasks.md は既に T-003 にまとめており、再分割は粒度悪化
- 後段影響：T-003 のテスト要件（語彙正本値テスト）の網羅性、設計の責務分離との整合

**推奨**：案 1（「6 種の語彙」に訂正、列挙語彙数と整合）

---

#### 議論論点 3：F-003 T-003 の必須項目数 22 → 20

**事実**：tasks.md T-003 行 62「必須項目 22 件」。design.md §3 のテーブルを機械的にカウントすると 20 項目（run_id／target_id／target_artifact_hash／source_repository_id／source_revision／phase_profile／treatment／review_mode／protocol_version／runtime_version／schema_set_version／prompt_set_version／config_version／config_hash／run_status／validator_status／human_signoff_status／evidence_class／started_at／closed_at）。

**候補案**：

- (案 1) tasks.md T-003 の「必須項目 22 件」を「必須項目 20 件」に訂正
- (案 2) design.md を再確認し、22 項目が正しいなら design.md 側を修正（遡及）

**深掘り**：

- 後段影響：T-003 実装時のテスト件数（必須項目数テスト）が 2 件減る、回帰検出力に影響なし
- design.md 確認結果：20 項目（テーブル行を直接カウント）
- 案 2 の遡及は不要（design.md は確定済み）

**推奨**：案 1（tasks.md を 20 項目に訂正、遡及不要）

---

#### 議論論点 4：F-004 テスト戦略の語彙正本整合カバレッジ

**事実**：tasks.md T-009 行 135 のテスト戦略継承で「語彙正本整合」項目に counter_status／validator_status／evidence_class／review_mode の 4 語彙のみ列挙（design.md §テスト戦略の記述に従う）。一方、design.md §判断 7 では 7 語彙（上記 4＋severity／final_label／confidence_label）が foundation 所有正本。3 語彙（severity／final_label／confidence_label）の語彙正本整合テストが T-009 でカバーされない。

**候補案**：

- (案 1) T-009 のテスト要件に severity／final_label／confidence_label の値テストを追加（T-009 で 7 語彙すべての整合確認）
- (案 2) severity／final_label は T-004 の enum 値テストでカバー、confidence_label は T-003 でカバーする旨を T-009 に明記（責務分散明示）

**深掘り**：

- 案 1：T-009 で 7 語彙すべての整合確認、責務集中型
- 案 2：各タスクで自然な責務分散、tasks.md の構造に沿う
- 後段影響：T-009 の累積テスト件数（既に 60 件＋ foundation テスト 40〜60 件想定）、案 1 では追加 3 件、案 2 では既存 T-003／T-004 に内包される
- 設計文書（design.md §テスト戦略）の意図：「語彙正本整合」を 1 つの検査項目として束ねる

**推奨**：案 1（T-009 で 7 語彙すべての整合確認、設計の意図に整合）

---

#### 議論論点 5：F-006 T-004 完了条件の参照先訂正

**事実**：tasks.md T-004 行 80 完了条件「`severity` ／ `counter_status` ／ `final_label` の enum 値が design.md §判断 7 と一致」。design.md §判断 7 は語彙正本の所有関係宣言節、enum 値の確定列挙は §3（validator_status／evidence_class／review_mode）、§4 finding 節（severity／counter_status）、§4 necessity_judgment 節（final_label）。

**候補案**：

- (案 1) 参照先を「design.md §4 finding 節（severity／counter_status）と §4 necessity_judgment 節（final_label）」に訂正
- (案 2) 参照先を「design.md §判断 7（所有関係）＋ §4 finding 節（severity／counter_status）＋ §4 necessity_judgment 節（final_label、enum 値）」と両参照に明示

**深掘り**：

- 案 1 は enum 値だけを参照、簡潔
- 案 2 は所有関係と enum 値の両方を参照、設計の意図を反映
- 後段影響：実装者の参照経路、テスト記述の精度
- 設計の意図：所有関係は §判断 7、enum 値は各節という分散

**推奨**：案 2（両参照に明示、所有関係と enum 値の両方を確認）

---

#### 議論論点 6：F-009 T-009 の累積件数記述

**事実**：tasks.md T-009 行 139「累積テスト件数が 60 件＋ foundation テスト件数（見込み 40〜60 件、合計 100〜120 件想定）」。60 件の積算基点（既存 API 経路先取り実装のテスト件数想定）が tasks.md 単体では特定不能。

**候補案**：

- (案 1) 累積件数の記述を削除し、「すべてのテストが pytest で pass」のみ完了条件とする
- (案 2) 積算基点を明示（「サイクル 4 完了時点で累積 60 件、foundation 完成時に 100〜120 件想定」）

**深掘り**：

- 案 1：完了条件は「すべて pass」で機械判定可能、累積件数は情報的記述として不要
- 案 2：将来の見通しを残すが、tasks.md 単体での参照経路が必要
- 後段影響：実装者の達成基準理解
- 計画書 §5.9 のテスト件数管理方針は特になし

**推奨**：案 1（累積件数の記述を削除し、「すべて pass」を完了条件とする）

---

#### 議論論点 7：F-010 T-008 の「書き込み権限なし」削除

**事実**：tasks.md T-008 行 127「`tools/foundation_validators/check_encoding_convention.py`（Python スクリプト、書き込み権限なし）」。「書き込み権限なし」は属性指定として意味不明（ファイル権限か、スクリプトの副作用なしか不明）。

**候補案**：

- (案 1) 「（書き込み権限なし）」を削除
- (案 2) 「（読み取り専用検証器、ファイル書き込みの副作用なし）」と明示

**深掘り**：

- 案 1：簡潔、誤解の余地なし
- 案 2：副作用なしという意図を明示、読者の理解を補助
- 後段影響：実装者のスクリプト設計

**推奨**：案 2（読み取り専用検証器、ファイル書き込みの副作用なし）と明示

---

#### 議論論点 8：A-001 T-003 に run_status／human_signoff_status の値テスト追加

**事実**：T-003 の語彙正本値テスト記述では validator_status／evidence_class／review_mode／confidence_label の 4 語彙のみで、run_status（4 値：created／in_progress／closed／orchestration_failed）と human_signoff_status（4 値：pending／approved／rejected／deferred）の値テストが欠落。design.md §3 行 258-272 で両語彙とも 4 値の正本として宣言。

**候補案**：

- (案 1) T-003 のテスト要件に run_status と human_signoff_status の値テストを追加（合計 6 語彙の値テスト）
- (案 2) 現状維持（責務分離 4 種は記述のみで、値テストは validator_status／evidence_class／review_mode／confidence_label のみ）

**深掘り**：

- 案 1：foundation が所有する 4 語彙の状態語彙すべての整合確認、責務分離の完全カバー
- 案 2：run_status は runtime ライフサイクル、human_signoff_status は承認状態で、両者とも foundation の責務だが、フェーズ 3 必須項目で初版語彙固定として扱う
- 後段影響：T-003 のテスト件数増加（+2 語彙）、回帰検出力向上
- 設計の意図：design.md §3 では両語彙とも正本として宣言、テスト網羅性を高めるべき

**推奨**：案 1（T-003 のテスト要件に run_status と human_signoff_status の値テストを追加）

---

#### 議論論点 9：A-002 要件追跡表と T-001 本文の整合

**事実**：要件追跡表 行 159「Requirement 5：パターン定義依存の除外 | T-001（配置規約に含めない方針の明示）」。T-001 本文 行 35「対応要件：Requirement 7（リポジトリ内資産の規則）」のみ。Requirement 5 の追跡が双方向で整合しない。

**候補案**：

- (案 1) T-001 本文の対応要件欄に「Requirement 5（パターン定義依存の除外）」を追加
- (案 2) 要件追跡表から Requirement 5 行を削除し、Requirement 5 は T-001 ではなく別の処置とする

**深掘り**：

- 案 1：T-001 で「パターン定義配置規約を含めない」を明示することで双方向整合
- 案 2：Requirement 5 は「配置規約を定義しない」という消極的契約で、特定のタスクに紐付かないとも解釈可能
- 後段影響：要件追跡の機械検査（双方向整合）

**推奨**：案 1（T-001 本文に Requirement 5 を追加、双方向整合）

---

#### 議論論点 10：A-005 T-010 完了条件のレポート構造明示

**事実**：tasks.md T-010 行 148 完了条件「レポート出力（標準出力に整形済み YAML）が design.md §完成判定基準と一致」。design.md §完成判定基準は 6 項目の自然言語宣言、YAML レポートの構造（必須キー、値域）が未定義。

**候補案**：

- (案 1) T-010 の完了条件に YAML レポートの最低限の構造（例：`checks: { all_pass: true, items: [{ name, status, details }] }`）を明示
- (案 2) 完了条件を「6 判定項目すべてが pass」と表現し、出力形式は実装段で確定する旨を明示

**深掘り**：

- 案 1：レポート構造を明示、機械判定可能
- 案 2：完了条件は判定 pass で機械判定可能、出力形式は実装段で柔軟
- 後段影響：T-010 実装の自由度、テストの記述精度

**推奨**：案 2（6 判定項目すべてが pass を完了条件とし、出力形式は実装段で確定）

---

### 4.2 利用者議論履歴

本対処は 7 モデル比較実験（人間代役機構 §5.12 検証、`docs/experiments/n-model-comparison.md`）と統合して実施。must-fix 10 件は第 1 段階（2026-05-27 セッション 31）、should-fix 7 件は第 2 段階（2026-05-27 セッション 32）で議論・確定。

**第 1 段階：must-fix 10 件（2026-05-27 セッション 31）**

| 論点 | 所見 ID | 利用者判定 | 議論経緯 |
|---|---|---|---|
| topic-01 | F-001 | 採用：案 1 | 予備実験で議論、design.md §4 確定の必須 8 項目への訂正 |
| topic-02 | F-002 | 採用：案 1 | T-003 完了条件「5 種 → 6 種」訂正、列挙数と一致 |
| topic-03 | F-003 | 採用：案 1 | T-003「必須項目 22 → 20」訂正 |
| topic-04 | F-004 | 採用：案 1 | T-009 のテスト要件に severity ／ final_label ／ confidence_label の 3 語彙追加、責務集中型 |
| topic-05 | F-006 | 採用：案 2 | T-004 完了条件の参照先を両参照（§判断 7 ＋ §4 finding ＋ §4 necessity_judgment）に明示 |
| topic-06 | F-009 | 採用：案 1 | T-009 累積件数記述を削除、「すべて pass」のみ |
| topic-07 | F-010 | 採用：案 2 | T-008「（読み取り専用検証器、ファイル書き込みの副作用なし）」と意味明示 |
| topic-08 | A-001 | 採用：案 1 | T-003 のテスト要件に run_status ／ human_signoff_status の値テスト追加 |
| topic-09 | A-002 | 採用：案 1 | T-001 本文の対応要件欄に Requirement 5 を追加、双方向整合 |
| topic-10 | A-005 | 別案 | design.md §完成判定基準にスキーマ定義を遡及追加、軽量再オープン手続き |

**第 2 段階：should-fix 7 件（2026-05-27 セッション 32）**

判定支援資料の表現が分かりにくいとの利用者指摘（「判定 7 件に必要な判定支援資料を読んだが、理解できる言葉で書かれていない。一つづつ平易に説明してもらう必要がある」）を受け、メインセッションが 1 件ずつ平易な日本語で説明し直す対話形式で進行。

| 論点 | 所見 ID | 利用者判定 | 議論経緯 |
|---|---|---|---|
| topic-11 | F-005 | 別案（最小タイプ） | 5 経路の別案中身を一覧で開示、3 タイプに整理。完了条件を「規約が記述された ＋ 人間レビュー承認」に変更 |
| topic-12 | F-007 | 採用：案 1 | T-004 の対応設計節リストに design.md §5 を追加 |
| topic-13 | F-011 | 採用：案 1 | 全 6 経路完全一致、pending-cross-feature-findings.md に A-017 として登録 |
| topic-14 | A-003 | 別案（A+D 併用） | 4 経路の別案中身を開示、5 種類の手段に整理。件数明示 ＋ 自然言語接続詞の組合せを採用。利用者発言「今回は別案を参考に更に議論して決定」 |
| topic-15 | A-004 | 案 1 ＋ 方向 X | 4 経路の別案中身を開示、2 方向（X／Y）に整理。T-009 前提タスクに T-001 追加 ＋ T-001 にディレクトリ作成責任を含める |
| topic-16 | A-006 | 別案 | 3 経路の別案がすべて同方向、既存テスト要件への注記追加を採用。利用者発言「先の問題もそうだったが、別案が提出された場合には、検討する価値があることが多い」 |
| topic-17 | A-007 | 採用：案 1 | T-010 が CI ／メタタスク的性格のため T-010 への組み込みを採用。Gemini-pro の別案（Linter ／共通検証基盤への切り出し）は将来検討として保留。利用者発言「現状では案 1 を指示、Linter 機能は後ほどの議論としてメモ。今回は、システムの改善案のヒントが得られた」 |

**重要な観察（実験ノート §6.9.7 に詳細記録）**：

- 別案集約・再議論パターンの実例化（topic-14）
- 別案の検討価値の一般化（topic-16 利用者発言）
- 実験を通じたシステム改善案のヒント（topic-17 利用者発言：Linter ／共通検証基盤の構想を将来検討事項として保留）
- should-fix での一致率パターン（別案を提案する力が利用者との一致率に直結）

これらは計画書 §5.12 改訂時の追加根拠として実験ノート §6.9.7 に集約。

### 4.3 反映箇所

**tasks.md の修正（must-fix 10 件＋ should-fix 6 件、topic-13 F-011 は機能横断のため tasks.md 修正なし）**：

| 論点 | 修正箇所 |
|---|---|
| topic-01 (F-001) | T-004 成果物 `review_case`「必須 9 項目 → 必須 8 項目」、テスト要件「必須 8 項目」 |
| topic-02 (F-002) | T-003 完了条件「5 種 → 6 種」 |
| topic-03 (F-003) | T-003 責務「22 項目 → 20 項目」、完了条件「22 件 → 20 件」 |
| topic-04 (F-004) | T-009 責務に語彙正本整合 7 語彙の明示 |
| topic-05 (F-006) | T-004 完了条件の参照先を両参照（§判断 7 ＋ §4 finding ＋ §4 necessity_judgment）に明示 |
| topic-06 (F-009) | T-009 テスト要件の累積件数記述を削除 |
| topic-07 (F-010) | T-008 成果物「（読み取り専用検証器、ファイル書き込みの副作用なし）」 |
| topic-08 (A-001) | T-003 テスト要件に run_status と human_signoff_status の値テスト追加 |
| topic-09 (A-002) | T-001 対応要件欄に Requirement 5 を追加 |
| topic-10 (A-005) | T-010 完了条件を design.md スキーマ準拠に変更（+ design.md §完成判定基準にスキーマ定義を追加） |
| topic-11 (F-005) | T-001 完了条件に「規約記述 ＋ 人間レビュー承認」を追加 |
| topic-12 (F-007) | T-004 対応設計節リストに design.md §5 を追加 |
| topic-14 (A-003) | T-007 成果物の表記「既定の phase および profile（以上 5 項目）」に変更 |
| topic-15 (A-004) | T-001 にディレクトリ作成責任を追加（`tests/foundation/`、`.gitkeep`）、T-009 前提タスクに T-001 を追加 |
| topic-16 (A-006) | T-006 テスト要件に step 値 enum 検証の補足注記を追加 |
| topic-17 (A-007) | T-010 テスト要件に双方向整合チェックを追加 |

**design.md の修正（topic-10 A-005 別案による遡及）**：

- §完成判定基準に「完成判定レポートの YAML スキーマ」節を新規追加（軽量再オープン手続きで処理、spec.json は本セッション中の更新対象外）

**pending-cross-feature-findings.md の修正（topic-13 F-011 波及）**：

- A-017「機能横断波及の確認手順が tasks.md に明示されていない」を新規追加

**機械的照合の結果**：

- tasks.md：8 つの Edit がすべて成功（重なる範囲なし、各 Edit の old_string が一意に一致）
- design.md：1 つの Edit が成功（§完成判定基準と §変更意図 の間に新節挿入）
- pending-cross-feature-findings.md：A-017 を §3 に追加

**leave-as-is 4 件（F-008、F-012、A-008、A-009）**：

本記録 §3.1 判定一覧のとおり、判定役判定により tasks.md は修正せず、本記録の §3 にのみ判定結果を残す。

### 4.4 should-fix 7 件と leave-as-is 4 件の扱い

- **should-fix 7 件**（F-005／F-007／F-011／A-003／A-004／A-006／A-007）：tasks.md に必要に応じて反映、ただし must-fix 対処の中で関連項目があれば同時に反映可
- **leave-as-is 4 件**（F-008／F-012／A-008／A-009）：本記録に判定結果を残すのみ、tasks.md は修正しない
- **F-011（波及）**：pending-cross-feature-findings.md に A-017 として追記予定（次節）

### 4.5 機能横断波及（F-011）の扱い

F-011（機能横断波及への明示的言及がない）は波及項目として `.reviewcompass/pending-cross-feature-findings.md` に追加すべき。ただし foundation 自体は波及元ではなく、tasks.md の記述構造の問題のため、他機能の tasks.md にも同様の構造を踏襲する必要があり、機能横断段（tasks 段 review-wave）で全機能の tasks.md に対して一括対処する見込み。

---

## 5. 関連参照

- 計画書 §5.9.1〜§5.9.3（レビュー方法の規律、所見メタデータ）
- 計画書 §5.23.12（サブエージェント方式の運用条件）
- 規律 [[must-fix-discussion-obligation]]（must-fix 対処の議論義務）
- 規律 [[implementation-autonomy]]（実装フェーズの自律進行）
- 過去レビュー記録：[2026-05-25-design-triad-review.md](2026-05-25-design-triad-review.md)
- 起草対象：[../tasks.md](../tasks.md)
- 上流参照：[../requirements.md](../requirements.md)、[../design.md](../design.md)
- 機能横断波及：[../../pending-cross-feature-findings.md](../../pending-cross-feature-findings.md)
