---
type: requirements_local_review
target: .reviewcompass/specs/runtime/requirements.md
target_commit: <未コミット、本セッション内作業>
target_content_hash: <本セッション内、コミット時に確定>
date: 2026-05-22
mode: subagent_mediated         # 正式値（計画書 §5.23.12）
session: session-19
author:
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
  caveat: 主役レビュー（primary）も同一エンティティが担当しているため、§5.4 規律の「起草者と判定者の分離」は最終判定（judgment 役、別エンティティ）の段で担保
reviewer:
  identity: claude_code_subagent
  model: claude-haiku-4-5-20251001
  role: final_judgment
  separation_from_author: true
primary:
  provider: claude_code_main_session
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  prompt_artifact_path: <未整備>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  prompt_artifact_path: <未整備>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-haiku-4-5-20251001
  model_full_id: claude-haiku-4-5-20251001
  prompt_artifact_path: <未整備>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 2 }
    count: 4
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 1 }
    count: 2
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 3, INFO: 1 }
    count: 4  # 6 件中、leave-as-is 2 件（F-003、A-002）を除外、採用所見 4 件
    judgment_distribution: { must-fix: 2, should-fix: 2, leave-as-is: 2 }
subagent_mediated_caveats:
  - メインセッション（主役）と判定役・敵対役は別セッションで、Claude Code 内部のサブエージェント機構を使う正式経路（計画書 §5.23.12）
  - プロンプト雛形（templates/prompts/）が未整備のため、各役のプロンプトは Agent 呼び出し時のメッセージで暫定指示する
  - メインセッションが主役を担っており、§5.9.1 の「メイン LLM は 3 役のいずれにもならない」規律から逸脱（§5.23.12.7 で許容明示）
---

# レビュー記録：runtime requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

レビュー観点（セッション 19 で確立済み、5 観点）：

- 観点 1：要件の網羅性
- 観点 2：機能名置換の正確性（特に §5.15.6 命名変更）
- 観点 3：自己適用前提の除去完全性
- 観点 4：計画書 §5.18／§5.15 系の継承方針の反映
- 観点 5：要件の検証可能性

### 観点 1：要件の網羅性

抽出元 10 要件（Req 10 は「削除済み」表記）と抽出後の対応関係を確認。Req 1〜10 のすべてが抽出後にも存在し、Req 10 は能動的書き換え（パターン定義依存の除外、3 受入基準を新設）。

受入基準件数：
- 抽出元：Req 1 = 6、Req 2 = 5、Req 3 = 5、Req 4 = 7、Req 5 = 5、Req 6 = 9、Req 7 = 5、Req 8 = 6、Req 9 = 5、Req 10 = 0、計 53 件
- 抽出後：上記 ＋ Req 10 = 3、計 56 件（Req 10 の能動的書き換えで増加）

Boundary Context 隣接期待は、抽出元 4 項目 → 抽出後 6 項目（workflow-management と conformance-evaluation 追加、計画書 §3.1 由来）。

該当なし。所見なし。

### 観点 2：機能名置換の正確性

機能名置換 grep（dual-reviewer-*、paper-interface、implementation-governance）：0 件 ✓
処理方式名 grep（旧 single／dual／dual+judgment）：Change Intent の歴史的記録としてのみ言及（旧命名の参照、§5.15.6 命名変更の根拠）✓

所見なし。

### 観点 3：自己適用前提の除去完全性

grep 結果 0 件（Change Intent の説明文を除く）。foundation の F-001／A-002 で得た教訓「削除済み」表記の取り扱いを反映済み（Req 10 を能動的要件に書き換え）。

所見なし。

### 観点 4：計画書 §5.18／§5.15 系の継承方針の反映

- §5.15.6 命名変更：処理方式 single/dual/dual+judgment → primary/adversarial/judgment、Req 2 受入 2 に反映済み ✓
- §5.18.13 レビューモード 3 値体制：Req 4 受入 6 で `manual_dogfooding`／`runtime_mediated`／`subagent_mediated` の foundation 参照を明示 ✓
- §5.18.14 来歴項目：Req 9 受入 2 で `source_repository_id`／`source_revision` を明示 ✓
- §5.18.2 行 2189「現行のみを記述」：Req 10 を能動的要件に書き換え ✓
- foundation Req 1 受入 4 由来の counter_status：Req 4 受入 3 に反映済み ✓
- foundation Req 6 受入 10 由来の検証器状態語彙参照：Req 6 受入 2 に反映済み ✓
- §5.15.4 4 状態軸の独立性：requirements レベルでは明示なし（design.md で扱う想定）

所見なし。

### 観点 5：要件の検証可能性

- **finding_id**：F-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Requirement 1 受入 4
- **description**：Req 1 AC 4 で「省略された段と失敗した段を実行記録上で区別する」とあるが、区別方法（フィールド名・語彙）が未指定
- **rationale**：Req 2 AC 4 では処理方式選択による省略マーカーが明示されているが、Req 1 AC 4 の「失敗した段」の表現方法は本仕様内で未定義。検証時に「区別がついているか」を機械判定するためには、`step_outcome` などの語彙フィールドが必要。フィールド名と最低限の語彙（例：`executed`／`skipped_by_treatment`／`failed`）を本仕様内で明示する余地あり
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "step_outcome|失敗した段|skipped|failed" .reviewcompass/specs/runtime/requirements.md`

- **finding_id**：F-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Requirement 6 受入 7
- **description**：Req 6 AC 7 で「機械可読な無効実行トリアージ成果物を出力する」とあるが、成果物の具体形式（ファイル名、配置先、必須節）が未指定
- **rationale**：「機械可読」を満たすにはスキーマ準拠が必要。foundation のどのスキーマに準拠するか、または新規スキーマか、本仕様内で参照が必要。少なくとも `validator_result.schema.json`（foundation 由来、計画書 §5.18.9 で言及）との関係を明示すべき
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "validator_result|無効実行トリアージ|triage" .reviewcompass/specs/runtime/requirements.md`

- **finding_id**：F-003
- **severity**：INFO
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Requirement 5 受入 5
- **description**：Req 5 AC 5 で「大規模言語モデルの所見を確認済みレビュー出力に黙示的に自動採用しない」とあるが、「黙示的」の判定基準が曖昧
- **rationale**：「黙示」を機械判定するのは困難。「人間署名なしに採用扱いにならない」のような具体的な機械可読条件が望ましい。Req 6 AC 9 の「人間署名 → 検証器 → 実行終了」順序の強制と組み合わせて読めば実質的に担保されるが、Req 5 AC 5 単独では検証困難
- **evidence_type**：inference

- **finding_id**：F-004
- **severity**：INFO
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Requirement 8 受入 6
- **description**：Req 8 AC 6「リポジトリ内に複数のプロンプト候補がある場合、プロンプト上書きの解決方針を所有する」が、Req 3（プロンプト解決と版追跡）の責務と重複している可能性
- **rationale**：Req 3 はプロンプト解決の一般規則、Req 8 AC 6 はフェーズプロファイル別の上書き解決。前者が単一プロンプトの版解決、後者が複数候補時の選択方針、と読めば棲み分けは成立する。ただし両者の境界が本仕様内で明示されていないため、実装時に責務の重なりが生じる可能性
- **evidence_type**：inference

### 該当なし観点

なし（5 観点すべてに所見または確認結果あり）

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 2（F-001、F-002）、INFO 2（F-003、F-004）、計 4 件
- evidence_type 別：fact 2、inference 2、mixed 0

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

### 主役所見への反論検討

- **対象 finding_id**：F-001
- **counter_status**：`no_counter_evidence_after_challenge`
- **counter_rationale**：Req 1 AC 4 は「実行記録上で区別する」とするが、区別を実現する具体フィールドも語彙も本仕様内に存在しない。Req 2 AC 4 で「省略マーカーを出力する」とあるが、これは処理方式起因の省略に限定された記述であり、「実行失敗した段の状態表現」は別物。抽出元（英語仕様）にも `step_outcome` や語彙リストは存在せず、foundation 仕様にも当該語彙定義は見当たらない。フィールド名・語彙未定義の状態で検証可能性を満たさないという主役の指摘は反証できない。

- **対象 finding_id**：F-002
- **counter_status**：`counter_evidence_raised`
- **counter_rationale**：主役は「foundation のどのスキーマに準拠するかが未参照」と指摘。しかし Req 6 AC 3 が「無効化マーカーを生の証拠を改変せずに付与できる構造を支える」と述べており、foundation の `invalidation_marker.schema.json`（計画書 §5.18.9 で定義、要検証）との連動を想定可能。さらに Req 4 AC 1「`foundation` のスキーマに準拠した実行レベル証拠を出力する」が requirements レベルの包括的参照として機能し、個別スキーマ名の列挙は design フェーズの責務と解釈する余地がある。WARN ではなく INFO 相当と評価する余地。

- **対象 finding_id**：F-003
- **counter_status**：`no_counter_evidence_after_challenge`
- **counter_rationale**：主役は「『黙示』の機械判定が困難」と指摘。Req 5 AC 4「明示的な署名を実行終了の前提」および Req 6 AC 9「人間署名 → 検証器呼び出し → 実行終了の順序強制」を組み合わせれば、署名なしに終了できない仕組みが成立する論理的補完を試みたが、Req 5 AC 5 の文言「黙示的に自動採用しない」は禁止の主体（実装）に対する要件であり、順序強制（process constraint）とは別次元の記述。両者は相互補完だが読者が自力で演繹しなければ機械判定基準が得られない点は改善余地あり。

- **対象 finding_id**：F-004
- **counter_status**：`counter_evidence_raised`
- **counter_rationale**：Req 3 は「版追跡の目的でプロンプトを一意に解決する規則（単一候補解決）」、Req 8 AC 6 は「フェーズプロファイルの文脈で複数候補が存在する際の選択方針（上書き優先順位）」を扱う。前者は一意解決の前提条件違反を失敗扱いにするルール（AC 4）、後者は複数候補時の優先選択ロジックの所有権宣言。両者は対象シナリオが異なり重複とは言えない。ただし Req 8 AC 6 の末尾「`foundation` の配置と同一性規則は維持する」が Req 3 との連動を暗示しており、本仕様内で両者の関係を一文で明示すれば誤解を防げる。重複より「連関の未明示」が本質。

### 独立発見

- **finding_id**：A-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Requirement 6 受入 2
- **description**：`validator_status` の語彙として「最低限 `passed`／`failed`／`blocked`」の 3 値のみを明示しており、計画書 §5.18.7（行 2239）が定義する正本 4 値（`not_run`／`passed`／`failed`／`blocked`）から `not_run` が欠落
- **rationale**：計画書 §5.18.7 は「`validator_status`（検証状態）の値リスト：`not_run`／`passed`／`failed`／`blocked`、所有者：foundation」と明記している。`not_run` は「検証がまだ実行されていない初期状態」を表し、実行ライフサイクル管理において実行前の段階を表現するために必要な値である。runtime 仕様 Req 6 AC 2 は「最低限 `passed`／`failed`／`blocked`」とのみ記述しており、`not_run` への言及が皆無。foundation 仕様 Req 6 AC 10 も同様に 3 値のみ。計画書から foundation 仕様への転記時に `not_run` が脱落した可能性が高く、runtime 仕様はその状態を踏襲。本所見は **foundation 仕様にも遡及波及する重要な発見**
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "not_run" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/runtime/requirements.md`
  - `grep -n "not_run" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/foundation/requirements.md`
  - `grep -n "not_run" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：A-002
- **severity**：INFO
- **target_location**：.reviewcompass/specs/runtime/requirements.md §Change Intent
- **description**：Change Intent 内の引用書式が不統一（§5.23.12 と §5.15.6／§5.18.2 行 2189 の参照粒度が揃っていない）
- **rationale**：他の引用（§5.15.6、§5.18.2 行 2189）が節番号または行番号併記で統一されているのに対し、`subagent_mediated` の参照は「§5.23.12 由来」のみで詳細節（§5.23.12.5 など）の参照がない。foundation セッション 19 の教訓（§番号引用誤り）を踏まえると、参照粒度の統一は今後のレビュー精度に影響
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "§5.23.12\|§5.15.6\|§5.18.2" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/runtime/requirements.md`

### 敵対役所見集計

- 主役所見への反論：counter_evidence_raised 2 件（F-002、F-004）／no_counter_evidence_after_challenge 2 件（F-001、F-003）／not_assessed 0 件
- 独立発見の重大度別：CRITICAL 0、ERROR 0、WARN 1（A-001）、INFO 1（A-002）、計 2 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：must-fix
- **rationale**：Req 1 AC 4 で「省略された段と失敗した段を実行記録上で区別する」と規定しながら、区別を実現する具体的フィールド名・語彙が仕様内で定義されていない。Req 2 AC 4 では処理方式由来の省略に限定された省略マーカーが明示されているが、実行失敗の状態表現メカニズムは空白。検証可能性が満たされず、実装時の解釈差異を招く。`step_outcome` のようなフィールド名と最低限の語彙定義（例：`executed`／`skipped_by_treatment`／`failed`）を本仕様内に明示することが必須。foundation 仕様との整合も必要。

- **finding_id**：F-002
- **judgment**：should-fix
- **rationale**：敵対役の反証で計画書 §5.18.9 における `invalidation_marker.schema.json` の存在が言及され、Req 4 AC 1 の「foundation のスキーマに準拠した実行レベル証拠を出力」が包括的参照として機能する論拠が示された。ただし Req 6 AC 7「機械可読な無効実行トリアージ成果物を出力する」は具体形式について仕様内の直接言及がない。design フェーズで詳細化されるべき項目だが、requirements 段階で最低限「foundation の validator_result.schema.json ／ invalidation_marker.schema.json との関係」を一文で明示することが、読み手の解釈誤差を減らすために有効。

- **finding_id**：F-003
- **judgment**：leave-as-is
- **rationale**：Req 5 AC 5「黙示的に自動採用しない」は禁止の意思表示として requirements に必要。主役が指摘した「黙示」の機械判定困難性は事実だが、敵対役が示したように Req 5 AC 4 と Req 6 AC 9 の組み合わせにより、論理的に署名なしの自動採用は構造上不可能。requirements がプロセス制約を述べ、その効果を design で実装する分離が成立。現状で矛盾はない。

- **finding_id**：F-004
- **judgment**：should-fix
- **rationale**：敵対役の反証が説得力を持つ。Req 3 は「単一候補プロンプトの版解決規則」、Req 8 AC 6 は「複数候補時のフェーズプロファイル別選択方針」で、対象シナリオが異なる。重複ではなく「連関の未明示」が本質。実装時の混乱を防ぐため、Req 8 AC 6 に関係明示の一文追加が should-fix。

- **finding_id**：A-001
- **judgment**：must-fix
- **rationale**：計画書 §5.18.7 行 2239 が `validator_status` の正本値を `not_run`／`passed`／`failed`／`blocked` の 4 値と明記しているのに対し、runtime requirements.md Req 6 AC 2 では 3 値のみ（`not_run` 欠落）。foundation 仕様 Req 6 AC 10 も同様に 3 値のみ。`not_run` は検証ライフサイクルの「未実行初期状態」を表す必須値。**foundation 仕様にも遡及波及する重要な発見**であり、両仕様の正当性に関わる must-fix。

- **finding_id**：A-002
- **judgment**：leave-as-is
- **rationale**：敵対役が指摘した引用粒度の不統一は事実だが、§5.23.12 には計画書内で確認可能な 8 つの小節（5.23.12.1〜5.23.12.8）が存在し、参照元が必要に応じて小節を指定できる構造にある。引用粒度統一は future improvement として有効だが、現在の形式で読み手の解釈を妨げるほどの曖昧さはない。

### 判定役所見集計

- judgment_distribution：must-fix 2 件（F-001、A-001）／should-fix 2 件（F-002、F-004）／leave-as-is 2 件（F-003、A-002）
- 採用所見の重大度別（must-fix ＋ should-fix）：CRITICAL 0、ERROR 0、WARN 3（F-001、F-002、A-001）、INFO 1（F-004）、計 4 件
- 不採用所見数：2 件（F-003、A-002）

### 判定の総合所見

今回のレビューは **foundation 仕様に遡及波及する重要な発見（A-001）を露出した点で高い価値**を持つ。`validator_status` の 4 値体制の欠落は、計画書 §5.18.7 の正本定義と runtime・foundation 仕様の乖離を示しており、両仕様の早期修正が必須。

F-001（`step_outcome` の語彙未定義）も must-fix で、requirements 段階での検証可能性向上に直結する。敵対役が F-001 に「反証できない」と判定した点は、仕様欠陥が客観的に実在することを示す。

F-002 と F-004 は should-fix。敵対役の反証により「重複ではなく連関の未明示」「個別スキーマ参照は design フェーズの責務」という本質が明確化された。design フェーズで詳細化される工程で参照粒度を上げるための形成的フィードバックとして機能。

F-003 と A-002 は leave-as-is。いずれも敵対役の論拠が採用される結果で、3 役レビュー機構の健全性を示唆。

本レビューの結果、runtime 仕様は「foundation 仕様との同期確保」と「requirements 段階での語彙定義補強」という 2 つの改善軸を得た。A-001 の修正は foundation セッションへの跨境フィードバックとして戦略的価値が高い。

---

## 4. 統合（integration）

統合段は §5.15.2 に従い、追加の大規模言語モデル呼び出しを伴わずに 3 役出力を統合する。実施者はメインセッション（Opus 4.7）。

### 採用所見一覧

| finding_id | severity | judgment | target_location | 概要 |
|---|---|---|---|---|
| F-001 | WARN | must-fix | requirements.md §Requirement 1 受入 4 | 段の省略／失敗の区別フィールド・語彙が未定義 |
| F-002 | WARN | should-fix | requirements.md §Requirement 6 受入 7 | 無効実行トリアージ成果物の foundation スキーマ参照が未明示 |
| F-004 | INFO | should-fix | requirements.md §Requirement 8 受入 6 | Req 3 と Req 8 AC 6 の連関明示が必要 |
| A-001 | WARN | must-fix | requirements.md §Requirement 6 受入 2 | `validator_status` 4 値のうち `not_run` が欠落、foundation 仕様にも遡及 |

### 抽出元との対応

- 抽出元由来の論点：
  - F-001：抽出元 Req 1 AC 4 も「omitted from failed」を区別する記述があるが具体フィールドは未指定（抽出元の不備、抽出後も継承）
  - F-002：抽出元 Req 6 AC 7 も「machine-readable invalid-run triage artifact」と記述するのみで具体形式は未指定（同上）
  - A-001：抽出元 Req 6 AC 2 も `pass / fail / blocked` の 3 値のみで `not_run` 欠落（抽出元の不備）。**foundation 仕様も同じ問題**で、計画書 §5.18.7 の正本との不整合
- 新規発見（抽出による）：
  - F-004：Req 3 と Req 8 AC 6 の連関未明示は抽出元にもあるが、本セッションのレビューで明示化が必要と認識された

### 残課題と本セッションでの対処方針

**本セッション内で対処済み（2026-05-22 利用者承認後実施）**：

- **F-001**：Req 1 AC 4 に `step_outcome` フィールドと語彙（`executed`／`skipped_by_treatment`／`failed`）を追記済み
- **F-002**：Req 6 AC 7 に foundation の `validator_result.schema.json`／`invalidation_marker.schema.json` への参照を明示済み
- **F-004**：Req 8 AC 6 に Req 3 との関係明示を一文追記済み

**機能横断レビューに持ち越し（波及所見、要件 review-wave／alignment-gate で対処）**：

- **A-001（波及所見、must-fix）**：runtime Req 6 AC 2 と foundation Req 6 AC 10 の両方で `validator_status` 語彙の `not_run` が欠落（計画書 §5.18.7 行 2239 の正本 4 値からの脱落）。性格上、機能間の正本語彙の不整合であり、§5.5 が定める要件 review-wave（複数機能を横断する複数ラウンドレビュー）または alignment-gate（フェーズ終端の機能横断整合確認）で扱うのが筋。本セッションでは個別機能の drafting 段の範囲を超えるため未対処。[.reviewcompass/pending-cross-feature-findings.md](../../../pending-cross-feature-findings.md) §A-001 に集約し、要件 review-wave 着手時に消化する

**leave-as-is（修正不要）**：

- F-003（INFO）：Req 5 AC 5 の「黙示」記述は Req 5 AC 4／Req 6 AC 9 で実質担保
- A-002（INFO）：引用粒度の不統一は form improvement、現状で曖昧さなし

### 用語訂正（利用者指摘、2026-05-22）

当初本セッションで「A-001 は foundation 仕様への遡及修正」と整理していたが、利用者の指摘により次のとおり訂正：

- **遡及修正ではなく波及**：機能間の不整合は機能を増やすほど明らかになる通常現象。過去の作業の過失ではない
- **段の所属**：個別機能の drafting 段の責務ではなく、review-wave／alignment-gate の責務（§5.5）
- **持ち越し管理**：`.reviewcompass/pending-cross-feature-findings.md` に集約し、要件 review-wave 着手時に消化

### サブエージェント方式の効果評価（runtime レビュー観察）

セッション 19 で正式採用したサブエージェント方式（mode = `subagent_mediated`）を runtime レビューで 2 回目の実証：

- **追加の効果確認**：敵対役（Sonnet 4.6）が **foundation セッション 19 レビューで見逃した正本 4 値の欠落（A-001）を発見**。サブエージェントの独立視点が遡及的な仕様欠陥を露出する効果を実証
- **メインセッションの事実検証の役割**：敵対役の計画書引用について、メインセッションが grep で確認し A-001 の正当性を確認（foundation セッションの教訓を反映）
- **判定役の総合判定**：両者の論を勘案し、F-002／F-004 を should-fix、F-003／A-002 を leave-as-is と適切に振り分け
