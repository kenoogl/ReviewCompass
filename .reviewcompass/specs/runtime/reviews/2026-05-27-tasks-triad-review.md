---
type: tasks_triad_review
target: .reviewcompass/specs/runtime/tasks.md
target_commit: <未確定、本セッション 32 で起草された tasks.md コミット予定版>
target_content_hash: <未計測>
date: 2026-05-27
mode: subagent_mediated
session: session-32
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: <約 3.4>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <約 2.3>
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
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 10, INFO: 1 }
    count: 14
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 4, INFO: 1 }
    count: 8
    counter_distribution: { counter_evidence_raised: 5, no_counter_evidence_after_challenge: 9, not_assessed: 0 }
  judgment:
    by_judgment: { must-fix: 6, should-fix: 10, leave-as-is: 6 }
    by_waterfall: { 機能内対処: 22, 波及: 0, 遡及: 0, 延期: 0 }
    count: 22
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation tasks の 2026-05-26 三役レビューと同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で「タスク 7」と言及のみで本体未整備、本セッション限りの仮設定（foundation tasks の 2026-05-26 レビューで採用された 7 観点を踏襲）
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：runtime tasks triad-review

本記録は runtime 機能の tasks.md（11 タスク T-001〜T-011、本セッション 32 で起草、約 230 行）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation tasks 2026-05-26 レビューと同配置）。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は本セッション仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。14 件の所見（CRITICAL 0／ERROR 3／WARN 10／INFO 1）を提示した。

### 主役所見一覧（14 件、F-001〜F-014）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | ERROR | T-002 完了条件 行 58 | run_manifest 必須項目「16 件」が design.md §3 の「開始時固定 16 件＋実行中変化 5 件＝計 21 件」と不整合（限定の明示なし） | fact |
| F-002 | 1：上流仕様の網羅 | ERROR | T-004 完了条件 行 87 | final_label foundation 3 値正本テストの参照節未明示（foundation T-004 topic-05 採用と同水準でない） | fact |
| F-003 | 1：上流仕様の網羅 | ERROR | T-008 対応要件 行 128 | Requirement 4 受入 7（failure_observation スキーマ準拠記録の出力）が対応要件欄・要件追跡表で欠落 | fact |
| F-004 | 1：上流仕様の網羅 | WARN | T-009 完了条件 行 149 | 「9 行マッピング全件」が階層構造（探索宣言優先 → 無効化標識 → 7 行）を反映していない、誤解リスク | mixed |
| F-005 | 2：タスク粒度の妥当性 | WARN | T-005 完了条件 行 98、T-007 成果物 行 119 | T-005 と T-007 で `decision_units.json` の責務境界が重複 | mixed |
| F-006 | 3：タスク依存順の整合性 | ERROR | T-006 前提タスク 行 107 | T-006 前提タスクが T-001 のみ、T-003（phase_profile 語彙確定）への依存が欠落 | mixed |
| F-007 | 3：タスク依存順の整合性 | WARN | T-008 前提タスク 行 130 | T-008 前提タスクに T-006（プロンプト解決）が欠落 | inference |
| F-008 | 4：完了条件の機械判定可能性 | WARN | T-001 完了条件 行 45 | 「人間レビューで承認」が機械判定不可、承認の記録方法が不明 | fact |
| F-009 | 4：完了条件の機械判定可能性 | WARN | T-003 完了条件 行 73 | 「相互依存しない」の機械判定基準が不明確 | fact |
| F-010 | 5：テスト要件の妥当性 | WARN | T-011 完了条件 行 171 | runtime 所有語彙（phase_profile／treatment／step_outcome）の正本確定確認が T-011 完了条件に欠落（完成判定基準と不整合） | fact |
| F-011 | 5：テスト要件の妥当性 | WARN | T-009 テスト要件 行 150、T-011 成果物 行 170 | T-009 単体テストと T-011 統合テストの責務分担が不明、順序検証が重複の可能性 | mixed |
| F-012 | 6：機能横断波及の早期検出 | WARN | T-011、全体 | 機能横断波及の確認手順が未明示（A-017 と同型の問題）、5 下流機能との接合面の確認タスクが未定義 | fact |
| F-013 | 7：成果物配置と命名の整合 | WARN | T-001 成果物 行 40-42、責務 行 37 | 「新設」が仕様文書作成か実体作成か曖昧、foundation T-001 の topic-15 対応との対比不明 | fact |
| F-014 | 7：成果物配置と命名の整合 | INFO | T-011 成果物 行 170 | T-011 成果物 8 ファイルに T-001 に対応する test_run_layout.py 相当が欠落 | fact |

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論または同意（14 件）

| ID | counter_status | counter_rationale 要約 |
|---|---|---|
| F-001 | counter_evidence_raised | 反証。design.md §3 は 2 群分け（開始時固定 16 件＋実行中変化 5 件）、T-002 session controller 責務は前者のみで責務分離として整合。INFO 相当に過大評価 |
| F-002 | no_counter_evidence_after_challenge | 同意。ただし重大度は WARN 相当 |
| F-003 | no_counter_evidence_after_challenge | 同意。さらに T-008 成果物にも failure_observation_writer.py が欠落（A-001 で独立発見） |
| F-004 | counter_evidence_raised | 反証。表は 9 行で読めば階層構造は自明、誤解リスクは推測。INFO 相当 |
| F-005 | no_counter_evidence_after_challenge | 同意。Step D 初期生成と T-007 人間決定後追書き込みの責務分離が文面で明示されていない |
| F-006 | no_counter_evidence_after_challenge | 同意。T-004 経由の間接依存はあるが明示欠落は事実 |
| F-007 | counter_evidence_raised | 反証。投影規約 7 項目にプロンプト識別子フィールドは含まれない、T-008→T-006 依存の根拠は薄い |
| F-008 | no_counter_evidence_after_challenge | 同意。「踏襲」の具体内容が不明 |
| F-009 | no_counter_evidence_after_challenge | 同意 |
| F-010 | no_counter_evidence_after_challenge | 同意。foundation tasks T-009 topic-04 系と同水準でない |
| F-011 | counter_evidence_raised | 反証。階層的補完と読める、INFO 相当 |
| F-012 | no_counter_evidence_after_challenge | 同意。foundation の機能内対処方針踏襲なら T-011 に明記すべき |
| F-013 | no_counter_evidence_after_challenge | 同意 |
| F-014 | counter_evidence_raised | 反証。T-001 にテスト要件あり、T-011 成果物末尾「または機能別に分割」で例示扱い |

### 2.2 独立発見（8 件、A-001〜A-008、ERROR 3／WARN 4／INFO 1）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| A-001 | 1：上流仕様の網羅 | ERROR | T-008 成果物 行 131-134 | T-008 成果物に failure_observation_writer.py 相当が欠落（writer.py 統合か別ファイルかも未決、F-003 連動） | fact |
| A-002 | 1：上流仕様の網羅 | ERROR | T-009 対応要件 行 142、要件追跡表 行 183 | Req 6 受入 6（review_mode=runtime_mediated 付与）は T-002／T-004 責務、T-009 帰属は誤導 | fact |
| A-003 | 2：タスク粒度の妥当性 | WARN | T-009 成果物 行 144-148 | T-009 成果物 4 件は他タスク（多くは 1〜3 件）と比べ多く、一気通貫粒度として肥大化 | mixed |
| A-004 | 3：タスク依存順の整合性 | ERROR | T-010 前提タスク 行 157 | T-010 前提に T-002（session controller）への直接依存が欠落（間接依存のみ） | fact |
| A-005 | 4：完了条件の機械判定可能性 | WARN | T-010 完了条件 行 161 | 「生実行ディレクトリが輸出後も不変」「来歴情報が同一性を保つ」の操作的定義欠落 | fact |
| A-006 | 5：テスト要件の妥当性 | WARN | T-007 テスト要件 行 123 | T-007「決定単位生成テスト」が T-005 と内容重複の可能性（F-005 関連） | fact |
| A-007 | 6：機能横断波及の早期検出 | WARN | tasks.md 全体、変更意図 行 217 | foundation 語彙正本改訂時の runtime tasks への波及プロトコル未定義 | inference |
| A-008 | 7：成果物配置と命名の整合 | INFO | tasks.md 全体 | 成果物配置は runtime/runtime_core/ 配下のみ、experiments/runs/ の実行時配置検証タスクが独立タスク化されていない | fact |

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 判定結果一覧（22 件）

| ID | judgment | waterfall | judgment_rationale 要約 |
|---|---|---|---|
| F-001 | leave-as-is | 機能内対処 | 敵対役反証成立、session controller 責務範囲として整合、修正不要 |
| F-002 | should-fix | 機能内対処 | 参照節明示で機械判定可能性が向上、機能内対処 |
| F-003 | must-fix | 機能内対処 | A-001 と連動、対応要件欄に Req 4 受入 7 を追加＋成果物に failure_observation_writer.py 追記 |
| F-004 | leave-as-is | 機能内対処 | 敵対役反証成立、表参照で階層は自明 |
| F-005 | must-fix | 機能内対処 | T-005 と T-007 の責務分離を明示（T-005 が生成、T-007 は人間署名・決定付加） |
| F-006 | should-fix | 機能内対処 | T-006 前提タスクに T-003 を追加 |
| F-007 | leave-as-is | 機能内対処 | 敵対役反証成立、T-008 が T-006 に直接依存する根拠は薄い |
| F-008 | should-fix | 機能内対処 | 完了条件を機械判定可能な客観基準に書き直す |
| F-009 | should-fix | 機能内対処 | 完了条件に操作的定義（軸独立性の判定基準）を補記 |
| F-010 | must-fix | 機能内対処 | T-011 完了条件に runtime 所有 3 語彙の正本確定確認を追加 |
| F-011 | leave-as-is | 機能内対処 | 敵対役反証成立、階層的補完関係 |
| F-012 | should-fix | 機能内対処 | T-011 完了条件に foundation 語彙正本との整合確認手順を補記 |
| F-013 | should-fix | 機能内対処 | T-001 責務欄にディレクトリ構造仕様の境界明示を補記 |
| F-014 | leave-as-is | 機能内対処 | 敵対役反証成立、テスト要件は既存記述で十分 |
| A-001 | must-fix | 機能内対処 | F-003 連動、T-008 成果物に failure_observation_writer.py 追記、または T-004／T-009 帰属を明示 |
| A-002 | must-fix | 機能内対処 | 要件追跡表で Req 6 受入 6 を T-004 にも明示、T-009 対応要件欄から受入 6 を除外 |
| A-003 | should-fix | 機能内対処 | T-009 責務記述で 4 ファイルの内部関係を補記、粒度自体は維持 |
| A-004 | must-fix | 機能内対処 | T-010 前提タスクに T-002 を追加（直接依存明示） |
| A-005 | should-fix | 機能内対処 | 完了条件にハッシュ照合・フィールド一致等の判定方法を補記 |
| A-006 | should-fix | 機能内対処 | F-005 解消と同一作業で対処（T-007 テスト要件を人間署名関連に書き換え） |
| A-007 | should-fix | 機能内対処 | T-011 完了条件に語彙正本ハッシュ照合または参照のみ使用の機械検証手順を明示、F-012 と同一作業で対処 |
| A-008 | leave-as-is | 機能内対処 | 独立タスク化は粒度方針に反する、配置仕様検証は T-001／T-011 で担保済み |

### 3.2 集計

- **判定別**：must-fix 6 件／should-fix 10 件／leave-as-is 6 件
- **波及別**：機能内対処 22 件／波及 0 件／遡及 0 件／延期 0 件

### 3.3 判定役の総評

runtime tasks.md は foundation tasks の 11 タスク構成と整合する責務領域分割で、design.md §全体構造 4 役を主軸とした粒度設計は健全。must-fix 6 件はすべて機能内対処で完結し、上流文書（design.md／requirements.md）への遡及や他機能への波及はない。

深刻度の高い欠陥は次の 5 点：

1. T-008 における failure_observation_writer の欠落と Req 4 受入 7 の対応要件欠落（F-003 ／ A-001 連動）
2. T-005 ／ T-007 の `decision_units.json` 責務重複（F-005 ／ A-006 連動）
3. T-004 ／ T-009 の Req 6 受入 6 担当責務の二重記載（A-002）
4. T-010 の T-002 前提欠落（A-004）
5. T-011 完了条件と完成判定基準の語彙正本確認の不整合（F-010）

should-fix 10 件は機械判定基準の明確化（F-008 ／ F-009 ／ A-005）、依存順明示（F-006）、責務境界明示（F-013 ／ A-003）、参照節明示（F-002）、foundation 語彙正本改訂時の波及確認手順（F-012 ／ A-007）、人間署名関連テスト（A-006）に集中しており、foundation tasks レビューで採用された機能内対処方針を踏襲することで一括対処可能。

leave-as-is 6 件は敵対役反証または既存記述で十分カバーされている事項。全体として、修正コストは中程度で foundation tasks 修正規模と同水準、runtime 機能の起草段階完了に向けて修正後に再レビュー（または差分レビュー）を経て承認可能な水準にある。

利用者と must-fix 6 件を議論する際、特に F-003 ／ A-001 の連動所見（failure_observation_writer の欠落）と F-005 ／ A-006 の連動所見（decision_units.json 責務重複）は実装段で必ず問題化するため、優先的な議論を勧める（規律 [[must-fix-discussion-obligation]]）。

---

## 4. 統合節（integration、対処方針と利用者議論履歴）

本節は規律 [[must-fix-discussion-obligation]] に従い、must-fix 所見ごとの対処方針案を提示し、利用者議論を経て確定方針と反映箇所を記録する。

### 4.1 must-fix 6 件の対処方針案（5 議論論点、F-003 と A-001 を連動として 1 論点に集約。利用者判定は §4.2 参照、反映箇所は §4.3 参照）

#### 議論論点 1：F-003 ／ A-001 連動 — T-008 の failure_observation 関連の欠落

**事実**：tasks.md T-008（evidence writer）の対応要件欄（行 128）が「Requirement 4 受入 4、Requirement 6 受入 3、Requirement 7 受入 5」のみで Req 4 受入 7（failure_observation スキーマ準拠記録の出力）が欠落。さらに成果物（行 131-134）にも failure_observation_writer.py 相当が欠落。design.md §証拠出力モデル 行 454 で「runtime は foundation の failure_observation スキーマに準拠した記録を failures/failure_observations/<observation_id>.json に書き出す」が evidence writer の責務として明示。

**候補案**：

- (案 1) T-008 対応要件欄に Req 4 受入 7 を追加、成果物に `runtime/runtime_core/evidence_writer/failure_observation_writer.py` を追記（writer.py から独立ファイルとして分離）
- (案 2) T-008 対応要件欄に Req 4 受入 7 を追加、`writer.py` の責務に failure_observation 書き出しを統合（独立ファイル化せず writer.py 内のメソッドとして実装）

**深掘り**：

- 案 1 利点：責務分離が明示、テスト・保守が容易
- 案 2 利点：ファイル数を抑制、関連責務を 1 ファイルに集約
- 後段影響：T-008 のテスト件数（独立 writer のテスト追加）、failure_observation の発生頻度（実装段で見えてくる）

**推奨**：案 1（独立ファイル分離、責務明示）

---

#### 議論論点 2：F-005 ／ A-006 連動 — T-005 と T-007 の `decision_units.json` 責務重複

**事実**：T-005（Step D 実行器）責務欄（行 94）に「`decisions/decision_units.json` を出力」、T-007（決定単位と人間署名記録）成果物（行 120）に `decision_unit_writer.py`。design.md §Step D 行 332-334 では Step D が `decision_units.json` を初期生成（人間決定未確定）し、後段の人間署名で `human_signoff.json` が記録される構造。tasks.md の文面では責務分離が不明示。

**候補案**：

- (案 1) T-005 が `decision_units.json` を生成（機械統合の初期版、人間決定未確定）、T-007 は `human_signoff.json` の生成と `decision_units.json` への人間決定付加のみを担う。T-007 成果物から `decision_unit_writer.py` を削除し、`human_signoff_writer.py` と `decision_unit_updater.py`（人間決定付加用）に整理
- (案 2) T-007 を「人間署名記録のみ」に縮約、T-005 が `decision_units.json` の生成と更新を一括で担う

**深掘り**：

- 案 1 利点：責務分離が明示、Step D 機械統合と人間決定の責務境界が明確
- 案 2 利点：成果物がシンプル、決定単位管理が 1 タスクに集中
- 後段影響：T-007 のテスト範囲、責務領域単位の粒度方針との整合

**推奨**：案 1（責務分離の明示）

---

#### 議論論点 3：A-002 — Req 6 受入 6 の責務帰属の二重記載

**事実**：design.md §セッションモデル §2 行 187「review_mode：foundation 正本語彙から選択。runtime 自身が実行する場合は `runtime_mediated`」が session controller 責務。T-004 完了条件 3（行 87）が既に「`review_mode=runtime_mediated` が各段の出力に付与される」と明記。一方、T-009 対応要件欄（行 142）の「Requirement 6（受入 1〜9）」と要件追跡表（行 183）の「Requirement 6 → T-009」が Req 6 受入 6 を T-009 帰属と誤導。

**候補案**：

- (案 1) T-009 対応要件欄を「Requirement 6（受入 1〜5、7〜9）」に修正（受入 6 を除外）、要件追跡表で Req 6 受入 6 を T-002 ／ T-004 にも明示
- (案 2) T-002 と T-004 の対応要件欄に Req 6 受入 6 を明示、T-009 は現状維持（責務重複として実装段で運用）

**深掘り**：

- 案 1 利点：責務の二重記載を解消、要件追跡表の双方向整合が成立
- 案 2 利点：tasks.md 修正範囲が小さい
- 後段影響：T-011 統合テストの実装範囲、双方向整合チェック（T-011 に組み込み済み）の合格条件

**推奨**：案 1（責務の二重記載解消）

---

#### 議論論点 4：A-004 — T-010 前提タスクへの T-002 直接依存追加

**事実**：T-010（可搬証拠束輸出）の前提タスク（行 157）が「T-008（実行終了後の正本成果物が前提）、T-009（検証完了が前提）」のみで T-002（session controller）への直接依存が欠落。`bundle_manifest.yaml` の必須項目（行 156）に `source_repository_id` ／ `source_revision` ／ `review_mode` を含み、これらは session controller が `run_manifest.yaml` に書き込む項目。T-002 への間接依存（T-008 経由）はあるが、Requirement 9 受入 2／3 の来歴情報保持要件と直接対応するため明示が必要。

**候補案**：

- (案 1) T-010 前提タスクに T-002 を追加（T-002／T-008／T-009 の 3 前提）
- (案 2) 現状維持（間接依存で十分とみなす）

**深掘り**：

- 案 1 利点：依存順の明示性、実装着手時の前提確認の確実性
- 案 2 利点：前提リストを最小限に保つ
- 後段影響：T-010 着手時のチェック手順

**推奨**：案 1（直接依存明示）

---

#### 議論論点 5：F-010 — T-011 完了条件と完成判定基準の語彙正本確認の不整合

**事実**：tasks.md 完成判定基準節（行 205）に「runtime 所有の語彙（`phase_profile` 4 値、`treatment` 3 値、`step_outcome` 3 値）が T-003 ／ T-004 ／ T-006 の成果物で正本として確定されている」とあるが、T-011 完了条件（行 171）には「foundation 6 語彙正本の参照のみ使用が機械検証される」のみで runtime 所有語彙の正本確定確認が欠落。完成判定基準と T-011 の整合が崩れている。

**候補案**：

- (案 1) T-011 完了条件に「runtime 所有 3 語彙（`phase_profile` 4 値 ／ `treatment` 3 値 ／ `step_outcome` 3 値）が T-003 ／ T-004 ／ T-006 の成果物で正本確定されている機械検証」を追加
- (案 2) 完成判定基準節の該当行を削除（T-011 で機械検証しない方針に変更）

**深掘り**：

- 案 1 利点：完成判定基準と T-011 が整合、機械検証で語彙正本確定を担保
- 案 2 利点：T-011 テスト範囲を抑制
- 後段影響：T-011 のテスト件数、runtime 所有語彙の改訂時の波及

**推奨**：案 1（完成判定基準との整合）

---

### 4.2 利用者判定履歴

利用者判定は 7 モデル比較実験（2026-05-27 セッション 32、実験ノート [docs/experiments/n-model-comparison.md](../../../../docs/experiments/n-model-comparison.md) §5.3.3 ／ §5.3.4）の中で 1 件ずつ平易な日本語の説明＋利用者判定の対話形式で確定。本セッション 33（2026-05-27）の利用者明示承認「(イ) 実験段階の判定を合意済みとみなし tasks.md 反映へ進む」により、各 topic-NN-human.yaml を出典として tasks.md へ反映した。

| topic | 所見 | 利用者判定 | 出典 yaml | 議論経緯（要約） |
|---|---|---|---|---|
| topic-18 | F-003 | 採用：案 1 | [topic-18-human.yaml](../../../../tools/experiments/results/topic-18-human.yaml) | 5 経路案 1、Gemini-pro 別案は方法論違いで結果同じ（A-001 既採用により実質達成） |
| topic-19 | F-005 | 採用：案 1 | [topic-19-human.yaml](../../../../tools/experiments/results/topic-19-human.yaml) | 完全一致 6 経路、一括判定方針 (B) |
| topic-20 | F-010 | 採用：案 1 | [topic-20-human.yaml](../../../../tools/experiments/results/topic-20-human.yaml) | 完全一致 6 経路 |
| topic-21 | A-001 | 採用：案 1 | [topic-21-human.yaml](../../../../tools/experiments/results/topic-21-human.yaml) | 完全一致 6 経路、F-003 連動 |
| topic-22 | A-002 | 採用：案 1 | [topic-22-human.yaml](../../../../tools/experiments/results/topic-22-human.yaml) | 完全一致 6 経路 |
| topic-23 | A-004 | 採用：案 1 | [topic-23-human.yaml](../../../../tools/experiments/results/topic-23-human.yaml) | 完全一致 6 経路 |
| topic-24 | F-002 | 採用：案 1 | [topic-24-human.yaml](../../../../tools/experiments/results/topic-24-human.yaml) | 完全一致 6 経路 |
| topic-25 | F-006 | 採用：案 1 | [topic-25-human.yaml](../../../../tools/experiments/results/topic-25-human.yaml) | 完全一致 6 経路 |
| topic-26 | F-008 | 別案＝案 2 ＋ 注記 | [topic-26-human.yaml](../../../../tools/experiments/results/topic-26-human.yaml) | 利用者問い「完了条件は機械が判断するものか？」が転換点、foundation T-001 と同じ運用に従う注記を採用 |
| topic-27 | F-009 | 採用：案 1 | [topic-27-human.yaml](../../../../tools/experiments/results/topic-27-human.yaml) | 完全一致 6 経路 |
| topic-28 | F-012 | 採用：案 2 | [topic-28-human.yaml](../../../../tools/experiments/results/topic-28-human.yaml) | 統一性重視、機能横断段（A-017 と同型）に委ねる、tasks.md 変更なし |
| topic-29 | F-013 | 採用：案 1 | [topic-29-human.yaml](../../../../tools/experiments/results/topic-29-human.yaml) | 完全一致 6 経路 |
| topic-30 | A-003 | 採用：案 1 | [topic-30-human.yaml](../../../../tools/experiments/results/topic-30-human.yaml) | 完全一致 6 経路 |
| topic-31 | A-005 | 採用：案 1 | [topic-31-human.yaml](../../../../tools/experiments/results/topic-31-human.yaml) | 完全一致 6 経路 |
| topic-32 | A-006 | 採用：案 1 | [topic-32-human.yaml](../../../../tools/experiments/results/topic-32-human.yaml) | F-005 連動、本記録 §4.1 議論論点 2 の一体作業で対処 |
| topic-33 | A-007 | 採用：案 2 | [topic-33-human.yaml](../../../../tools/experiments/results/topic-33-human.yaml) | 統一性重視、tasks.md 変更なし、機能横断段で扱う |

集計：案 1 採用 13 件／別案 1 件（topic-26）／案 2 採用 2 件（topic-28／topic-33）。案 2 採用 2 件は tasks.md 変更なし、機能横断段に委ねる方針。

### 4.3 反映箇所

tasks.md（runtime）の編集箇所を行番号で記録。本セッション 33（2026-05-27）末時点で grep による機械的照合済み（訂正前文字列の残存ゼロ）。

| 議論論点 ／ 所見 | tasks.md の編集箇所 |
|---|---|
| 議論論点 1（F-003 ／ A-001 連動） | 行 128（T-008 対応要件に Req 4 受入 7 追加）、行 135（成果物に `failure_observation_writer.py` 追加）、行 136-137（完了条件・テスト要件に failure_observation 関連追記） |
| 議論論点 2（F-005 ／ A-006 連動） | 行 94（T-005 責務に「人間決定未確定の初期版」明示）、行 117（T-007 責務を「人間決定付加」に書き換え）、行 120（成果物を `decision_unit_updater.py` に整理、`decision_unit_writer.py` 削除）、行 122-123（完了条件・テスト要件更新） |
| 議論論点 3（A-002） | 行 51（T-002 対応要件に Req 6 受入 6 追加）、行 142（T-009 対応要件から受入 6 除外）、行 184（要件追跡表で T-002 ／ T-004 ／ T-009 の役割分担明示） |
| 議論論点 4（A-004） | 行 158（T-010 前提タスクに T-002 追加） |
| 議論論点 5（F-010） | 行 172（T-011 完了条件に runtime 所有 3 語彙の正本確定機械検証追加） |
| should-fix F-002 | 行 88（T-004 テスト要件に foundation 参照節明示） |
| should-fix F-006 | 行 106（T-006 前提タスクに T-003 追加） |
| should-fix F-008（別案＝案 2 ＋ 注記） | 行 45（T-001 完了条件 2 の注記を「foundation tasks T-001 と同じ運用に従う」に更新） |
| should-fix F-009 | 行 73（T-003 完了条件に操作的定義補記） |
| should-fix F-013 | 行 37（T-001 責務に仕様文書／実体作成の境界明示） |
| should-fix A-003 | 行 145-149（T-009 成果物に内部関係補記、bridge.py がオーケストレーション役） |
| should-fix A-005 | 行 162（T-010 完了条件にハッシュ照合・フィールド一致の判定方法補記） |
| should-fix F-012（案 2） | tasks.md 変更なし（機能横断段で扱う） |
| should-fix A-007（案 2） | tasks.md 変更なし（機能横断段で扱う） |

機械的照合：本セッション末で grep により全編集箇所を再確認（議論論点 1〜5 と should-fix 7 件のすべてで訂正前文字列の残存ゼロ）。

### 4.4 should-fix 10 件と leave-as-is 6 件の扱い

- **should-fix 10 件**の処理結果：
  - tasks.md 反映済み 8 件：F-002（行 88）／F-006（行 106）／F-008 別案（行 45）／F-009（行 73）／F-013（行 37）／A-003（行 145-149）／A-005（行 162）／A-006（議論論点 2 で一体対処、行 117-123）
  - tasks.md 変更なし 2 件：F-012（topic-28 案 2、機能横断段に委ねる）／A-007（topic-33 案 2、機能横断段で扱う）
- **leave-as-is 6 件**（F-001／F-004／F-007／F-011／F-014／A-008）：本記録に判定結果を残すのみ、tasks.md は修正しない
- **波及／遡及 0 件**：本セッションでは機能横断波及や上流文書遡及は発生せず、すべて機能内対処で完結

---

## 5. 関連参照

- 計画書 §5.9.1〜§5.9.3（レビュー方法の規律、所見メタデータ）
- 計画書 §5.23.12（サブエージェント方式の運用条件）
- 規律 [[must-fix-discussion-obligation]]（must-fix 対処の議論義務）
- 規律 [[implementation-autonomy]]（実装フェーズの自律進行）
- 過去レビュー記録：[2026-05-22-requirements.md](2026-05-22-requirements.md)、[2026-05-25-design-triad-review.md](2026-05-25-design-triad-review.md)
- foundation 参考：[foundation tasks triad-review 2026-05-26](../../foundation/reviews/2026-05-26-tasks-triad-review.md)
- 起草対象：[../tasks.md](../tasks.md)
- 上流参照：[../requirements.md](../requirements.md)、[../design.md](../design.md)
- 機能横断波及：[../../pending-cross-feature-findings.md](../../pending-cross-feature-findings.md)
