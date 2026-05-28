---
type: tasks_triad_review
target: .reviewcompass/specs/workflow-management/tasks.md
target_commit: 626c4e2
target_content_hash: <未計測、セッション 37 起草分（T-001〜T-011）>
date: 2026-05-28
mode: subagent_mediated
session: session-37-38
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: 約 3
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 4
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 3
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 1, ERROR: 6, WARN: 13, INFO: 0 }
    count: 20
  adversarial:
    by_severity: { CRITICAL: 1, ERROR: 3, WARN: 4, INFO: 2 }
    count: 10
  judgment:
    by_judgment: { must-fix: 9, should-fix: 17, leave-as-is: 4 }
    by_waterfall: { 機能内対処: 23, 波及: 1, 遡及: 2, 延期: 0 }
    count: 30
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation／runtime／evaluation／analysis tasks-triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で言及のみで本体未整備、foundation tasks-triad-review（セッション 30）の仮設定を継承
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
  - 本記録はセッション 37 で実施した 3 役レビューの結果をセッション 38 で起草。3 役の生出力はサブエージェントログ（~/.claude/projects/.../3e297d96-.../subagents/）から復元
---

# レビュー記録：workflow-management tasks triad-review

本記録は workflow-management 機能の tasks.md（11 タスク T-001〜T-011、コミット `626c4e2`）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。20 件の所見（CRITICAL 1／ERROR 6／WARN 13／INFO 0）を提示した。

### 主役所見一覧（20 件、F-001〜F-020）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | ERROR | tasks.md L235、requirements.md Req 1 受入 6 | 要件追跡表 Req 1 受入 6（review-wave の 7 モデル 2 回方式）の符号化先が DVT-W004 待ちで追跡切れ | mixed |
| F-002 | 1：上流仕様の網羅 | WARN | L246、Req 4 受入 1 | Req 4 受入 1「規律変更は不可逆操作」の追跡が T-010 でなく T-006 のみ参照 | fact |
| F-003 | 1：上流仕様の網羅 | WARN | L266、Req 8 受入 4 | Req 8 受入 4「1 箇所修正で完結」の追跡先に T-009 が含まれる根拠不明 | mixed |
| F-004 | 2：タスク粒度の妥当性 | ERROR | T-009（L183〜）、T-010（L198〜） | T-009 と T-010 の運用文書更新先が重複、規律変更ゲート説明の追記責務が曖昧 | inference |
| F-005 | 2：タスク粒度の妥当性 | WARN | T-004、T-005（L118〜） | T-005 前提が T-004 のみで T-001 が抜け、配置先依存の記述一貫性欠如 | fact |
| F-006 | 3：依存順の整合性 | CRITICAL | T-007 前提 L154 | T-007 前提に T-005（front_matter_checker）欠落、reopen 解決器が分離述語を呼べない | mixed |
| F-007 | 3：依存順の整合性 | ERROR | T-008 前提 L171 | T-008 前提に T-007 欠落、reopen 待機ファイルとの連動が未解決 | fact |
| F-008 | 3：依存順の整合性 | WARN | T-010 前提 L203 | T-010 前提が「T-003 または別途…」の曖昧表記で着手可能性が機械確定不能 | inference |
| F-009 | 4：完了条件の機械判定可能性 | ERROR | T-005 完了条件 3 L131 | 「DVT に登録する」が人手判断で機械判定不可、tasks ポリシー（L26）と不整合 | fact |
| F-010 | 4：完了条件の機械判定可能性 | WARN | T-003 完了条件 5 L95 | テンプレート変数展開規則の明示検証が grep キーワード未定義で機械判定困難 | mixed |
| F-011 | 4：完了条件の機械判定可能性 | WARN | T-009 完了条件・テスト要件 L192-196 | T-009 のテスト要件「grep 検査」のキーワード未明示、解釈余地 | inference |
| F-012 | 5：テスト要件の妥当性 | ERROR | T-011、T-010 完了条件 2 | T-010 の git mv 外部依存のモック／スタブ化がテスト要件・成果物に未記述 | inference |
| F-013 | 5：テスト要件の妥当性 | WARN | T-004 テスト要件 L116 | spec-set の `--rationale`（任意）省略時のログ記録動作テストが欠落 | mixed |
| F-014 | 5：テスト要件の妥当性 | WARN | T-006 テスト要件 L147、完了条件 1 L144 | フェーズ移行ゲートの異常系テスト数（8 ケース）が完了条件に比べ過小 | fact |
| F-015 | 6：機能横断波及の早期検出 | ERROR | T-003、design §3 | stage_schema.json の completion_predicate 値域 7 値検証が T-003 完了条件に未明示 | mixed |
| F-016 | 6：機能横断波及の早期検出 | WARN | T-010、判断 7 L726 | T-010 完了条件 4 が self-improvement §13.5 に依存、上流変更時の追従手段未規定 | mixed |
| F-017 | 7：成果物配置と命名の整合 | ERROR | T-001 成果物 L41-50 | T-001 成果物に tools/.gitkeep がなく、tests/.gitkeep と非対称 | fact |
| F-018 | 7：成果物配置と命名の整合 | ERROR | T-008 成果物 L174 | in_progress.schema.json（アンダースコア）が in-progress/（ハイフン）と不一致、design 未記載 | fact |
| F-019 | 7：成果物配置と命名の整合 | WARN | T-001 成果物 L49 | WORKFLOW_MANAGEMENT.md が design 配置ツリーに存在しない | mixed |
| F-020 | 7：成果物配置と命名の整合 | WARN | T-010 成果物 L204-208 | learning/workflow/approved-updates/ が design 配置ツリーに存在せず接合面記述のみ | mixed |

### 主役の注目発見

最も危険な依存欠落は **F-006（CRITICAL）と F-007（ERROR）の組み合わせ**。T-005 → T-007 → T-008 の依存チェーンが前提タスク表で切断されており、実装序列を正しい順に保証できていない。F-018（in_progress.schema.json 命名）は design 配置ツリーに存在しないパスの新規導入で、実装者が正しいパスを推定できない。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への counter_status 付与（20 件、判定役が集約）

counter_evidence_raised（反証あり）は 5 件（F-002／F-003／F-005／F-007／F-014）、残り 15 件は no_counter_evidence_after_challenge（同意）。

| 主役 ID | counter_status | 要旨 |
|---|---|---|
| F-001 | no_counter_evidence_after_challenge | 段集合・完了述語の符号化先が DVT-W004 待ちで不明、所見妥当 |
| F-002 | counter_evidence_raised | 追跡欄は受入 1 主旨に正しく対応、T-010 は別行で追跡済み、severity 引き下げ可 |
| F-003 | counter_evidence_raised | T-009 が運用文書全般を担うため誤追跡とは断定できないが問題意識は妥当 |
| F-004 | no_counter_evidence_after_challenge | 規律変更ゲート追記責務が両タスクのどちらにも明記なし、事実 |
| F-005 | counter_evidence_raised | T-004 経由で間接的に T-001 に依存、直接欠落ではない、severity 引き下げ可 |
| F-006 | no_counter_evidence_after_challenge | T-007 前提に T-005 欠落、依存順の実在する穴、所見妥当 |
| F-007 | counter_evidence_raised | T-008 の責務は一般管理で reopen 固有でない、必須化の根拠は弱い、severity 引き下げ可 |
| F-008 | no_counter_evidence_after_challenge | 「T-003 または別途」曖昧表記で着手可能性が機械確定不能、所見妥当 |
| F-009 | no_counter_evidence_after_challenge | 「DVT に登録」は人手判断で機械判定不可、所見妥当 |
| F-010 | no_counter_evidence_after_challenge | grep キーワード未定義で機械判定困難、所見妥当 |
| F-011 | no_counter_evidence_after_challenge | grep キーワード具体語が未定義、所見妥当 |
| F-012 | no_counter_evidence_after_challenge | git mv 外部依存のモック化が未記述、統合テスト実行可能性に穴、所見妥当 |
| F-013 | no_counter_evidence_after_challenge | spec-set の --rationale 省略時ログ記録テスト欠落、所見妥当 |
| F-014 | counter_evidence_raised | 異常系 4 パターンは 4 ゲート横断で 1 つずつ対応する設計、16 ケース必須は過大主張 |
| F-015 | no_counter_evidence_after_challenge | completion_predicate 値域 7 値のバリデーション明示なし、実装漏れリスク、所見妥当 |
| F-016 | no_counter_evidence_after_challenge | §13.5 内容変更時の追従手段が未規定、所見妥当 |
| F-017 | no_counter_evidence_after_challenge | tools/.gitkeep／README が成果物に皆無、tests/ との非対称は事実 |
| F-018 | no_counter_evidence_after_challenge | 命名混在＋schema が design 配置ツリー未記載、所見妥当（軽微） |
| F-019 | no_counter_evidence_after_challenge | WORKFLOW_MANAGEMENT.md が設計配置ツリー外、所見妥当（軽微） |
| F-020 | no_counter_evidence_after_challenge | learning/ が配置ツリー外、ただし self-improvement §13.5 に記述あり機能横断では整合 |

### 2.2 独立発見（10 件、A-001〜A-010、CRITICAL 1／ERROR 3／WARN 4／INFO 2）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| A-001 | reopen 静的列挙の前提破綻 | CRITICAL | tasks.md L87・L93・L153／design.md L57・L129・L486 | reopen-procedure.yaml「10 ステップ静的列挙」が完了条件だが design はステップ 6・第 7 段の 2 つしか定義せず、残 8 ステップが起草不能 | mixed |
| A-002 | self-improvement との双方向整合 | ERROR | tasks.md L207／self-improvement §8.4 | T-010 の approved_update schema（approved_at／target_discipline）が正本（target_discipline_path／status、approved_at なし）と食い違う | fact |
| A-003 | foundation 語彙正本の参照（A-018 同型） | ERROR | requirements.md L32／tasks.md L27・L285 | tasks は foundation 語彙 7 件参照だが上流 requirements は旧 4 件（run_status 等）で機能内不整合 | fact |
| A-004 | actor 値域の機械検査漏れ | ERROR | tasks.md L81・L93・L132／design L125・L359・L455 | design は actor 3 値（human/llm/proxy_model）だが tasks は 2 値、proxy_model がスキーマ・テストに不在 | fact |
| A-005 | DVT 登録漏れ（先送り論点 8／9） | WARN | tasks.md L313-318／design L807-808 | design 先送り論点 9 件のうち DVT 登録は 4 件、論点 8（参照層 memory→repo 移管）・9（運営ガイド改廃手続き）が未登録 | fact |
| A-006 | completion_predicate の検査範囲不整合 | WARN | tasks.md L106・L116／design L694 | depends_on_resolves_correctly 述語の「値域チェックのみ、変更検知は別機構（フェーズ 2 宿題）」の二重性が tasks に未反映 | fact |
| A-007 | grandfathering 判断の責務帰属の曖昧 | WARN | tasks.md L131／design L792 | T-005 完了条件 3 が「検査実行」と「grandfathering 判断」を混在、未確定走行で自己ロック risk | inference |
| A-008 | 複数 in-progress 並存の取りこぼし | WARN | tasks.md L181・L277／design L840 | design 境界条件「複数 reopen-procedure-*.yaml 並存」を継承表は T-008 に割当てるが T-008 テスト要件は単数前提、自己矛盾 | fact |
| A-009 | フェーズ移行ゲートの全機能同期 risk | INFO | tasks.md L138／design L378 | 「全機能 approval=true」要求が機能ごと非同期進行と整合しない可能性を T-006 が検証範囲に含めていない | inference |
| A-010 | reopen_classification_template.md の二重所有 | INFO | tasks.md L48・L158 | 同一パスが T-001（雛形配置）と T-007（内容確定）の両成果物に列挙、完了主体の一意性が機械判定不能 | fact |

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 判定結果一覧（30 件）

| ID | judgment | 波及種別 | 判定理由（簡潔） |
|---|---|---|---|
| F-001 | should-fix | 機能内対処 | 段集合本体は DVT-W004 で延期、tasks.md に延期明示で足りる |
| F-002 | leave-as-is | — | 追跡欄は受入 1 主旨に正しく対応、T-010 は別行で追跡済み |
| F-003 | should-fix | 機能内対処 | 追跡欄から T-009 を外すか寄与根拠を明記 |
| F-004 | should-fix | 機能内対処 | 規律変更ゲート説明の追記責務を T-009 か T-010 に明記 |
| F-005 | leave-as-is | — | T-004 経由で間接的に T-001 に依存、直接欠落でない |
| F-006 | must-fix | 機能内対処 | T-007 前提に T-005 を追加（依存順の実在する穴） |
| F-007 | should-fix | 機能内対処 | reopen 連動を明記するなら T-008 前提に T-007 追記が望ましいが必須性は中 |
| F-008 | must-fix | 機能内対処 | T-010 前提の「または」曖昧表記を一意化（DVT-W003 と整合） |
| F-009 | must-fix | 機能内対処 | T-005 完了条件 3 を機械判定可能に書き換え（tasks ポリシー違反の解消） |
| F-010 | should-fix | 機能内対処 | T-003 完了条件 5 に grep キーワードを明示 |
| F-011 | should-fix | 機能内対処 | T-009 完了条件・テスト要件に grep キーワードを明示 |
| F-012 | must-fix | 機能内対処 | T-010 テスト要件に git mv 外部依存のモック／スタブ化を追加 |
| F-013 | should-fix | 機能内対処 | T-004 テスト要件に spec-set --rationale 省略時ログ記録テストを追加 |
| F-014 | leave-as-is | — | 異常系 4 パターンは 4 ゲート横断で 1 つずつ対応、16 ケース必須は過大 |
| F-015 | must-fix | 機能内対処 | T-003 完了条件に completion_predicate 値域 7 値バリデーションを明示 |
| F-016 | should-fix | 機能内対処 | T-010 完了条件 4 に §13.5 変更時の追従手段を追記 |
| F-017 | should-fix | 機能内対処 | T-001 成果物に tools/.gitkeep または README を追加、tests/ と対称化 |
| F-018 | should-fix | 機能内対処 | in_progress.schema.json の命名統一＋design 配置ツリー追記 |
| F-019 | should-fix | 機能内対処 | design 配置ツリー追記は遡及だが軽微、tasks 内で吸収可 |
| F-020 | should-fix | 機能内対処 | self-improvement §13.5 で配置記述があるため tasks.md に出典注記で足りる |
| A-001 | must-fix | 遡及 | reopen 残 8 ステップが design に存在せず T-003 着手時に起草不能、design 加筆が必要 |
| A-002 | must-fix | 波及 | T-010 schema の field 名を self-improvement §8.4 正本に整合（両機能の接合面修正） |
| A-003 | must-fix | 遡及 | requirements.md L32 の旧語彙 4 件を現行 foundation 正本に訂正（上流訂正） |
| A-004 | must-fix | 機能内対処 | tasks.md に proxy_model を追加（design が正本なので機能内で吸収可） |
| A-005 | should-fix | 機能内対処 | tasks.md DVT に先送り論点 8・9 を 2 件追加 |
| A-006 | should-fix | 機能内対処 | depends_on_resolves_correctly の境界テスト・DVT 登録を追加 |
| A-007 | should-fix | 機能内対処 | T-005 完了条件 3 から判断部分を分離（F-009 と同根） |
| A-008 | should-fix | 機能内対処 | T-008 テスト要件に複数並存ケースを追記 |
| A-009 | leave-as-is | — | フェーズ移行の全機能同期は design §不可逆操作 §1 の確定仕様、意図通り |
| A-010 | should-fix | 機能内対処 | reopen_classification_template.md の重複列挙を注記で明確化（軽微） |

### 3.2 集計

| 区分 | 件数 | 内訳 |
|---|---|---|
| by_judgment | must-fix 9／should-fix 17／leave-as-is 4 | 計 30 |
| by_waterfall（must-fix＋should-fix 26 件） | 機能内対処 23／波及 1／遡及 2／延期 0 | leave-as-is 4 件は波及種別なし |

- **must-fix 9 件**：F-006／F-008／F-009／F-012／F-015／A-001／A-002／A-003／A-004
- **should-fix 17 件**：F-001／F-003／F-004／F-007／F-010／F-011／F-013／F-016／F-017／F-018／F-019／F-020／A-005／A-006／A-007／A-008／A-010
- **leave-as-is 4 件**：F-002／F-005／F-014／A-009
- **波及 1 件**：A-002　**遡及 2 件**：A-001／A-003

### 3.3 判定役の総評

最重要 3 件は構造的問題：A-001（reopen 上流設計の穴がタスクに伝播）、A-002（consumer 側が producer 正本と違う field 名を機械必須化）、A-003（既知 A-018 が機能内 requirements↔tasks で未消化）。いずれも文書の具体行を根拠とする fact／mixed 中心。

---

## 4. 統合節（integration、対処方針と利用者議論履歴）

本節は規律 [[must-fix-discussion-obligation]] に従い、must-fix 9 件の対処方針を提示し、7 モデル比較実験と利用者議論を経た確定方針を記録する。

### 4.1 must-fix 9 件の対処方針

遡及 2 件（A-001／A-003）と波及 1 件（A-002）は実験対象外として別経路で処理済み。機能内 6 件は 7 モデル実験＋利用者議論で確定。

#### 4.1.1 遡及・波及 3 件（実験対象外、別経路で処理済み）

| ID | 種別 | 処理 |
|---|---|---|
| A-001 | 遡及（design） | 確定済み再オープン手続き（種別 A-2）の初運用で処理。tasks.md／design.md の「10 ステップ」記述を「4 過程構成」に統一、design §reopen 機械強制モデル §5 で段集合を定義（コミット `2f5ee06`、`da1c95a`） |
| A-003 | 遡及（requirements） | 同じ A-2 再オープンで処理。requirements.md 行 32 の旧 foundation 語彙 4 件を現行正本（review_mode のみ参照、所見系・状態軸系は不参照）に訂正（コミット `2f5ee06`） |
| A-002 | 波及（self-improvement） | `pending-cross-feature-findings.md` に **A-019** として登録、機能横断段（tasks review-wave）で消化予定（コミット `a7e0496`） |

#### 4.1.2 機能内 must-fix 6 件（7 モデル実験＋利用者議論で確定）

§4.2 の議論結果を参照。F-006／F-008／F-009／F-012／F-015／A-004。

### 4.2 利用者議論履歴（7 モデル比較実験、2026-05-28 セッション 38）

機能内 must-fix 6 件＋should-fix 17 件＝23 topic（topic-76〜98）を 7 モデル（Opus 4.7／Sonnet 4.6 CLI／Sonnet 4.6 API／GPT-5.5／GPT-5.4／Gemini-3.5-flash／Gemini-3.1-pro）で評価。質問返し 13 件はマルチターン続行（代理回答は事実情報のみ、実験ノート §3.4 準拠）。人本人判定は `tools/experiments/results/topic-NN-human.yaml` に 23 件保存（実験データ）。

#### 完全一致 6 件（一括承認、最終判定で全 7 モデル案 1）

| topic | 所見 | 種別 | 判定 | 対処の要旨 |
|---|---|---|---|---|
| 76 | F-006 | must | 案 1 | T-007 前提に T-005 を追加 |
| 77 | F-008 | must | 案 1 | T-010 前提を discipline-update.yaml 新設に一意化 |
| 88 | F-013 | should | 案 1 | T-004 に spec-set --rationale 省略時ログ記録テスト追加 |
| 93 | F-020 | should | 案 1 | learning/ は self-improvement §13.5 正本を出典注記で吸収 |
| 95 | A-006 | should | 案 1 | depends_on_resolves_correctly 境界テスト追加＋変更検知先送りを DVT 登録 |
| 97 | A-008 | should | 案 1 | 複数 in-progress 並存を正常系として T-008 テスト要件に追記 |

#### 多数派採用 8 件（明確多数決に沿って記録）

| topic | 所見 | 種別 | 判定 | 7 モデル投票（最終） |
|---|---|---|---|---|
| 78 | F-009 | must | 案 1 | 案 1: 5 ／ 別案: 2 |
| 80 | F-015 | must | 案 1 | 案 1: 5 ／ 別案: 2 |
| 82 | F-001 | should | 案 1 | 案 1: 5 ／ 別案: 2 |
| 83 | F-003 | should | 案 1 | 案 1: 6 ／ 別案: 1 |
| 90 | F-017 | should | 案 1 | 案 1: 6 ／ 別案: 1 |
| 91 | F-018 | should | 案 1 | 案 1: 4 ／ 別案: 3 |
| 94 | A-005 | should | 案 1 | 案 1: 5 ／ 別案: 2 |
| 96 | A-007 | should | 案 1 | 案 1: 6 ／ 別案: 1 |

#### 起草者孤立 6 件（1 件ずつ平易説明、利用者は全件多数派を採用）

私（Opus、起草者）のみが案 1 を出し、他 6 モデルが別の答えに収束した 6 件。利用者は 6 件すべて多数派（他のモデルの案）を採用。利用者発言は各件「ア」（多数派採用、2026-05-28 セッション 38）。

| # | topic | 所見 | 種別 | 確定判定 | 7 モデル投票（最終） |
|---|---|---|---|---|---|
| 1 | 81 | A-004 | must | **別案を提示** | 案 1: 1（**Opus 起草者バイアス**）／ 別案: 6 |
| 2 | 79 | F-012 | must | **別案を提示** | 案 1: 1（**Opus**）／ 案 2: 2 ／ 別案: 4 |
| 3 | 85 | F-007 | should | **採用：案 2** | 案 1: 1（**Opus**）／ 案 2: 6 |
| 4 | 87 | F-011 | should | **採用：案 2** | 案 1: 1（**Opus**）／ 案 2: 6 |
| 5 | 92 | F-019 | should | **採用：案 2** | 案 1: 1（**Opus**）／ 案 2: 6 |
| 6 | 98 | A-010 | should | **採用：案 2** | 案 1: 1（**Opus**）／ 案 2: 6 |

確定した対処の要旨：
- **81 A-004（別案）**：actor 値域に proxy_model 追加＋proxy_allowed 解決ロジック＋approval 段の proxy_model 承認判定仕様を tasks に明示（proxy 機構の実装範囲は要確定）
- **79 F-012（別案）**：consumer 統合テストは T-010、producer/consumer 境界の契約確認は T-011 に集約、共有フィクスチャは A-019 解消後に確定
- **85 F-007（案 2）**：T-008 は一般管理に独立、reopen 固有解釈は T-007 の責務と本文明記
- **87 F-011（案 2）**：T-009 の grep テスト要件を削除し必須節存在確認に絞る（自己矛盾解消）
- **92 F-019（案 2）**：design 配置ツリーに WORKFLOW_MANAGEMENT.md／WORKFLOW_PRECHECK.md を追記（design 軽量再オープン）
- **98 A-010（案 2）**：reopen_classification_template.md の二重列挙を解消、T-001＝雛形配置／T-007＝内容確定を別表現に整理

#### 引き分け 2 件（3 対 3 のタイブレーク、利用者判断）

| # | topic | 所見 | 種別 | 確定判定 | 7 モデル投票（最終） |
|---|---|---|---|---|---|
| 7 | 84 | F-004 | should | **採用：案 2** | 案 1: 3 ／ 案 2: 1 ／ 別案: 3（タイ） |
| 8 | 86 | F-010 | should | **採用：案 2** | 案 1: 2（Opus 含む）／ 案 2: 4 ／ 別案: 1（多数派案 2） |
| 9 | 89 | F-016 | should | **別案を提示（案 3）** | 案 1: 3 ／ 別案: 3（タイ）／ 案 2: 1 |

- **84 F-004（案 2）**：運用文書を T-009 に一本化、T-010 完成後に追記する分担を明記
- **86 F-010（案 2）**：多数派が案 2（私 Opus は少数派案 1、実質的に起草者孤立の 7 件目）。展開規則を stage_schema.json 構造化フィールドに格納し存在検証
- **89 F-016（案 3）**：依存マップ駆動の自動 reopen。§13.5 変更が機能依存マップに記録されたら DVT-W003 を自動的に open に差し戻し、再評価完了まで T-010 を完了扱いにしない（この仕組み自身の機能を自己適用）

#### 起草者バイアス検出の重要な観察（2026-05-28 セッション 38）

私（Opus 4.7、起草者）は **23 件すべてで案 1（最小修正）** を出したが、最終判定で **7 件（81／79／85／87／92／98／86）で他モデルが「より徹底した修正（案 2／別案）」に収束し、利用者も多数派を採用**して私の案 1 が覆った。

これは analysis tasks（F-007／F-002）に続く 2 例目の構造的検出で、私のバイアスは「**軽量に倒す傾向**（最小修正で足ると考え、徹底修正の必要性を過小評価する）」と明確に特徴づけられた。**外部視点の 7 モデル評価は起草者バイアスの構造的検出に有用**という観察を再確認。実験ノート §6 観点別考察への重要な知見。

#### 人本人判定の実験データ採取

各 topic の人本人判定を `tools/experiments/results/topic-NN-human.yaml` に 23 件保存（実験データ、コミット `baf2c66`）。7 モデル比較表の人本人基準点。

### 4.3 反映箇所（2026-05-28 セッション 38 実施、grep 機械照合済み）

確定 23 件を tasks.md／design.md に反映。各反映に「<所見 ID> 対処 2026-05-28」マーカーを付与し grep で照合した。

| 所見 | 確定 | 反映箇所 |
|---|---|---|
| F-001 | 案 1 | tasks.md 要件追跡表 Req 1 受入 6 に DVT-W004 延期注記 |
| F-003 | 案 1 | tasks.md 要件追跡表 Req 8 受入 4 から T-009 を除外 |
| F-004 | 案 2 | tasks.md T-009 責務に規律変更ゲート説明追記責務を一本化 |
| F-006 | 案 1 | tasks.md T-007 前提に T-005 追加 |
| F-007 | 案 2 | tasks.md T-008 責務に「reopen 固有解釈は T-007」明記（前提は不変） |
| F-008 | 案 1 | tasks.md T-010 前提を discipline-update.yaml 新設に一意化 |
| F-009／A-007 | 案 1 | tasks.md T-005 完了条件 3 を機械検証＋判断分離（自己ロック回避） |
| F-010 | 案 2 | tasks.md T-003 完了条件 5 を構造化フィールド化 |
| F-011 | 案 2 | tasks.md T-009 テスト要件から grep 検査を削除 |
| F-012 | 別案 | tasks.md T-010 テスト要件に consumer 統合テスト、T-011 に境界契約集約 |
| F-013 | 案 1 | tasks.md T-004 完了条件 4／テスト要件に spec-set 省略時ログ記録テスト |
| F-015／A-004 | 案 1／別案 | tasks.md T-003 完了条件 1 に値域 7 値＋actor 3 値、T-004 完了条件 6 に proxy_allowed／approval 述語、design 配置ツリー |
| F-016 | 案 3 | tasks.md T-010 完了条件 4 を依存マップ駆動の自動 reopen に改訂、DVT-W007（A-006 調停）|
| F-017 | 案 1 | tasks.md T-001 成果物に tools/README.md、完了条件 1 に確認 |
| F-018 | 案 1 | tasks.md T-008 成果物・完了条件で in-progress.schema.json にハイフン統一、design 配置ツリーに追記 |
| F-019 | 案 2 | design 配置ツリーに WORKFLOW_MANAGEMENT.md／WORKFLOW_PRECHECK.md 追記 |
| F-020 | 案 1 | tasks.md T-010 成果物に learning/ の出典注記（self-improvement §13.5 正本） |
| A-005 | 案 1 | tasks.md DVT に DVT-W005（論点 8）／DVT-W006（論点 9）追加 |
| A-006 | 案 1 | tasks.md T-004 完了条件 6・テスト要件に depends 述語の境界、DVT-W007 登録 |
| A-008 | 案 1 | tasks.md T-008 テスト要件に複数 in-progress 並存テスト |
| A-010 | 案 2 | tasks.md T-001 成果物所有を単独化、T-007 完了条件 5 に内容確定を分離 |

遡及 2 件（A-001／A-003）・波及 1 件（A-002）は §4.1.1 の通り別経路で処理済み。

### 4.4 should-fix 17 件と leave-as-is 4 件の扱い

- **should-fix 17 件**：本実験で全件 topic 化し、利用者判断で確定済み（§4.2）。tasks.md／design.md 反映は §4.3 で実施
- **leave-as-is 4 件**（F-002／F-005／F-014／A-009）：F-002／F-005／F-014 は敵対役の counter_evidence_raised が成立、A-009 は design 確定仕様と整合。いずれも修正不要、本記録 §3 で判定根拠を残すのみ

### 4.5 遡及 2 件・波及 1 件の扱い

§4.1.1 に記載。A-001／A-003 は A-2 再オープンで処理済み、A-002 は A-019 として pending 登録済み。

### 4.6 実装時の調停事項（F-016 案 3 × A-006 案 1）

topic-89（F-016）で採用した案 3（依存マップ駆動の自動 reopen で §13.5 変更を検知）は、変更検知の仕組みを必要とする。一方 topic-95（A-006）は全員一致の案 1 で「depends_on_resolves_correctly の変更検知はフェーズ 2 の宿題（先送りを DVT 登録）」を確定した。両者は緊張する。

**調停方針**：§13.5（self-improvement との接合面）の変更検知だけを先行実装し、機能依存マップ全般の汎用的な変更検知はフェーズ 2 の宿題のまま据え置く、という線引きで実装する。tasks.md 反映時（§4.3）に T-010 完了条件 4 と A-006 関連の DVT 記述の双方にこの線引きを明記する。

---

## 5. 関連参照

- 規律：[discipline_must_fix_discussion_obligation.md](../../../../docs/disciplines/discipline_must_fix_discussion_obligation.md)
- 7 モデル比較実験ノート：[docs/experiments/n-model-comparison.md](../../../../docs/experiments/n-model-comparison.md)
- 実験結果：`tools/experiments/results/topic-76〜98-*.yaml`（コミット `baf2c66`）
- 持ち越し所見：[.reviewcompass/pending-cross-feature-findings.md](../../../pending-cross-feature-findings.md) A-019
- 再オープン手続き：計画書 §5.6.1（4 過程構成）、[docs/operations/REOPEN_PROCEDURE.md](../../../../docs/operations/REOPEN_PROCEDURE.md)
- 過去の同型レビュー記録：[analysis tasks triad-review](../../analysis/reviews/2026-05-28-tasks-triad-review.md)
