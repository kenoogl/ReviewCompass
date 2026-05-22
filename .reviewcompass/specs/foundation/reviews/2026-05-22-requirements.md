---
type: requirements_local_review
target: .reviewcompass/specs/foundation/requirements.md
target_commit: <未コミット、本セッション内作業>
target_content_hash: <本セッション内、コミット時に確定>
date: 2026-05-22
mode: subagent_mediated         # 正式値（計画書 §5.23.12、2026-05-22 確定）
session: session-19
author:                          # 起草者（§5.4 起草者と判定者の分離を担保するための明示）
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
  caveat: 主役レビュー（primary）も同一エンティティが担当しているため、§5.4 規律の「起草者と判定者の分離」は最終判定（judgment 役、別エンティティ）の段で担保されている
reviewer:                        # 判定者（§5.4 規律で起草者と異名必須）
  identity: claude_code_subagent
  model: claude-haiku-4-5-20251001
  role: final_judgment            # 主役・敵対役・判定役 3 役のうち、最終判定を担う役
  separation_from_author: true    # author と reviewer は別エンティティ（別モデル、別 session）
primary:
  provider: claude_code_main_session
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <記入時に書く>
  prompt_artifact_path: <未整備>  # フェーズ 4 で templates/prompts/primary_detection/primary_reviewer.prompt.md を整備予定
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
    by_severity: { CRITICAL: 0, ERROR: 1, WARN: 3, INFO: 1 }
    count: 5
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 0 }
    count: 2
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 1, WARN: 5, INFO: 0 }
    count: 6  # 主役 5 件 ＋ 敵対役独立発見 2 件 ＝ 7 件中、F-002 は leave-as-is で除外、残 6 件を判定対象とした
    judgment_distribution: { must-fix: 5, should-fix: 1, leave-as-is: 1 }
subagent_mediated_caveats:
  - メインセッション（主役）と判定役・敵対役は別セッションで、Claude Code 内部のサブエージェント機構（Agent ツール）を使う正式経路（計画書 §5.23.12）
  - プロンプト雛形（templates/prompts/）が未整備のため、各役のプロンプトは Agent 呼び出し時のメッセージで暫定指示する（フェーズ 4 で正式整備予定）
  - ファイル遮断規律（§5.9.1）はサブエージェントのツール権限制限で部分的に達成（読み取りのみ許可、書き込み禁止）
  - 主役（Opus 4.7）と判定役（Haiku 4.5）はモデルファミリーが異なるが、§5.9.1 推奨既定（主役 Opus／判定役 Opus）からは外れる
  - メインセッションが主役を担っており、§5.9.1 の「メイン LLM は 3 役のいずれにもならない」規律から逸脱（§5.23.12.7 で許容を明示）
---

# レビュー記録：foundation requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

レビュー観点（仮設定、利用者承認 2026-05-22）：

- 観点 1：要件の網羅性（抽出元 7 要件のうち必要な内容が抜け落ちていないか）
- 観点 2：機能名置換の正確性（隣接仕様参照を含む）
- 観点 3：自己適用前提の除去完全性
- 観点 4：計画書 §5.18 系の継承方針の反映
- 観点 5：要件の検証可能性

### 観点 1：要件の網羅性

抽出元 7 要件（Req 5 削除済み）と抽出後の対応関係を確認した。Req 1〜7 のすべてが抽出後にも存在する。

受入基準（Acceptance Criteria）の件数：

- 抽出元：Req 1 = 9、Req 2 = 5、Req 3 = 10、Req 4 = 5、Req 6 = 10、Req 7 = 4、計 43 件
- 抽出後：Req 1 = 9、Req 2 = 6、Req 3 = 10、Req 4 = 5、Req 6 = 10、Req 7 = 4、計 44 件（Req 2 AC 6 を §5.18.15 由来で追加）

該当なし。所見：なし。

### 観点 2：機能名置換の正確性

- **finding_id**：F-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 5
- **description**：Requirement 5（削除済み）節で「旧 v1 の取得処理」「v2 では実 LLM 呼び出しに置き換える方針」という記述が抽出元のまま残っている
- **rationale**：抽出元では「v1／v2」は dual-reviewer-rebuild プロジェクト固有の版命名だが、ReviewCompass の文脈ではこの版命名が未定義。読者は「ReviewCompass のどの版か」と混乱する可能性がある。計画書 §5.18.11 の自己適用前提除去の観点では「dual-reviewer-rebuild の歴史的経緯」を一般化すべき
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "v1\|v2" .reviewcompass/specs/foundation/requirements.md`

### 観点 3：自己適用前提の除去完全性

- **finding_id**：F-002
- **severity**：INFO
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Change Intent
- **description**：Change Intent 節で「先行プロジェクトの土台仕様」という記述があり、先行プロジェクトへの言及が残る
- **rationale**：これは継承元の歴史的記録として正当な言及である一方、Change Intent の趣旨は「再構築の初期段階で必要な契約に絞り込む」ことを述べる節であり、先行プロジェクトへの言及がなくても成立する。読み手対象（個人利用者）にとっては不要情報の可能性
- **evidence_type**：inference
- **verifying_commands**：（推論ベースのため不要）

### 観点 4：計画書 §5.18 系の継承方針の反映

§5.18.11〜§5.18.15 の確定方針の反映状況：

- §5.18.11（自己適用前提除去）：dual-reviewer-*／paper-interface／implementation-governance の grep 結果 0 件、達成済み
- §5.18.12（ディレクトリ構造）：FOUNDATION.md §7 で配置先を明記、達成済み
- §5.18.13（レビューモード語彙）：Req 6 AC 6 で `manual_dogfooding` 継承、達成済み
- §5.18.14（来歴項目）：Req 6 AC 7 で `source_repository_id`／`source_revision` 継承、達成済み
- §5.18.15（設定二層モデル）：Req 2 AC 6 で明記、達成済み

加えて、本セッションで採用したサブエージェント方式のため、Req 6 AC 6 に「将来サブエージェント経由など他の経路を区別する追加値の余地を残す」を追記している。

- **finding_id**：F-003
- **severity**：WARN
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 6 受入 6
- **description**：「将来サブエージェント経由など他の経路を区別する追加値の余地を残す」という記述が、計画書 §5.23 に未反映の暫定方針に基づいている
- **rationale**：本セッション 19 でサブエージェント方式を「(b) 限定採用」として実験的に採用したが、計画書 §5.23 には未反映。仕様文書側でだけ先行記述があると、計画書と仕様文書の整合性が一時的に崩れる。事後評価で正式採用するなら §5.23 への反映が必要、見送るなら本記述の削除が必要
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "subagent\|サブエージェント" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`
  - `grep -n "サブエージェント" .reviewcompass/specs/foundation/requirements.md`

### 観点 5：要件の検証可能性

- **finding_id**：F-004
- **severity**：WARN
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 3 受入 9
- **description**：Req 3 AC 9 で「基本動作（B-1.0 相当）に必須のフィールドと、意図的に先送りされる将来拡張点を明示する」とあるが、「B-1.0」は先行プロジェクト固有の版命名で、ReviewCompass 内では定義されていない
- **rationale**：版命名「B-1.0」は抽出元の dual-reviewer-rebuild プロジェクトの段階表記。ReviewCompass では §7 で「フェーズ 1／2／3／4」と命名されており、対応する基準点が「フェーズ 2 完了時」「フェーズ 3 スタブ完成時」のどれかは未指定。検証時に「何をもって基本動作と判定するか」が定まらず、検証可能性が損なわれる
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "B-1.0" .reviewcompass/specs/foundation/requirements.md`
  - `grep -n "B-1" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：F-005
- **severity**：ERROR
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 1 受入 4
- **description**：Req 1 AC 4 の「敵対役が主役結果に対し独立した異論を提示することを最低限要求する」という記述で、「独立した異論」が具体的に何を含むかが未定義
- **rationale**：仕様検査時に「異論が出されたか」「異論の独立性が確保されたか」を機械判定する必要があるが、本 AC は判定基準を持たない。例えば「主役所見と異なる finding_id を 1 件以上含む」「主役所見への counter_status フィールドが最低 1 件 `counter_evidence_raised` または `no_counter_evidence_after_challenge`」など、具体的な機械判定可能な条件が必要。検証可能性が損なわれている
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "独立した異論\|forced.*divergence\|counter_status" .reviewcompass/specs/foundation/requirements.md`

### 該当なし観点

なし（5 観点すべてに所見または確認結果あり）

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 1、WARN 3、INFO 1、計 5 件
- evidence_type 別：fact 4、inference 1、mixed 0

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

### 主役所見への反論検討

- **対象 finding_id**：F-001
- **counter_status**：`no_counter_evidence_after_challenge`
- **counter_rationale**：計画書 §5.18.11 が「v1 撤廃の経緯（Requirement 5 削除）：抽出時に『削除済み』表記は持ち込まず、現行のみを記述」を明示している（敵対役の主張、判定役で要検証）。実際に抽出後仕様 Req 5 には「旧 v1 の取得処理」「v2 では実 LLM 呼び出しに置き換える方針」が残存し、計画書の指示に違反している。この指示は抽出元（英語版 Req 5）にも和訳相当テキストがそのまま存在しており、抽出元からの直接転写が原因と特定できる。主役指摘は正当で反証なし。ただし「v1／v2」表記の問題は機能名置換（観点 2）よりも §5.18.11 の自己適用前提除去（観点 3）にも分類できる点で観点の帰属に若干の揺れがある。

- **対象 finding_id**：F-002
- **counter_status**：`counter_evidence_raised`
- **counter_rationale**：主役は「Change Intent 節の『先行プロジェクトの土台仕様』という記述が自己適用前提として問題になり得る」と INFO として指摘している。しかし計画書 §5.18.11 が除去対象として列挙するのは「機能名参照（dual-reviewer-*）」「配置先（runtime/ 配下集約）」「リポジトリ前提（dual-reviewer-rebuild 内の固定パス）」の 3 種類であり、「先行プロジェクト」という一般的な参照は明示的な除去対象に含まれない。Change Intent の目的は「なぜ先行プロジェクト仕様をそのまま継承せず再構築したか」を説明することであり、先行プロジェクトへの一般的言及はその文脈説明として機能している。読者にとって不要情報という主役の推論は成立するが、それは設計上の判断であり仕様として誤りではない。severity INFO は妥当だが、「除去が望ましい」という示唆には反証がある。

- **対象 finding_id**：F-003
- **counter_status**：`no_counter_evidence_after_challenge`
- **counter_rationale**：「将来サブエージェント経由など他の経路を区別する追加値の余地を残す」という記述が計画書に由来するか調査したところ、計画書 §5.18.13（レビューモード語彙の節）の本文には当該フレーズが存在しない（grep で不一致確認）。計画書が定義する語彙は `manual_dogfooding` と `runtime_mediated` の 2 値のみで、サブエージェント経由への言及は計画書には皆無。仕様文書側が本セッションの暫定実験に基づき計画書未反映の記述を先行追加した状態は、主役指摘のとおり計画書との整合性が崩れている事実証拠がある。反証なし。

- **対象 finding_id**：F-004
- **counter_status**：`counter_evidence_raised`
- **counter_rationale**：主役は「B-1.0 は抽出元プロジェクト固有の版命名で ReviewCompass 内未定義」と WARN で指摘している。これは事実だが、計画書 §5.18.9 近傍に「JSON Schema 上で『B-1.0 運用で必須』と『意図的先送り』を区別する符号化規約を継承する」という記述が確認された（敵対役の主張、判定役で要検証）。計画書自体が「B-1.0 相当」という表現を継承した概念として使用しており、この表記は抽出元の直接転写でなく継承された計画書用語である可能性がある。したがって ReviewCompass 文脈での「B-1.0」は計画書に一定の根拠を持ち、undefined とは言い切れない。ただし「フェーズ何に相当するか」の対応が仕様書内で未注記である点は改善余地があり、WARN は維持が妥当。

- **対象 finding_id**：F-005
- **counter_status**：`no_counter_evidence_after_challenge`
- **counter_rationale**：主役は「独立した異論」の機械判定可能な条件が未定義であると ERROR で指摘している。`counter_status` や `adversarial_outcome` などの具体的なフィールド語彙が Req 3（スキーマ集合）の `finding` 契約または `review_case` 契約で補完されるかを検討したが、Req 3 AC 5 が「由来表示、重大度、反証連結、判定連結、人間決定の連結を支える」と記述するのみで、`adversarial_outcome` フィールドの語彙や `counter_status` の具体条件は本仕様文書内のいかなる箇所にも記述されていない。「異論を出さなかったこと自体を意図的な結果として記録する」という要求に対応するフィールドと語彙が Req 1 AC 4 と Req 3 のいずれにも不在であり、反証なし。計画書 §5.18.5 に `adversarial_outcome` の語彙（反証提示／反証なし／未評価）が言及されているが（敵対役の主張、判定役で要検証）、この語彙が仕様書 Req 1 AC 4 の判定基準として明示されておらず隔離したままとなっている点で主役指摘を支持する。

### 独立発見

- **finding_id**：A-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 6 受入 10
- **description**：Req 6 AC 10 の検証器状態語彙の参照禁止対象から `conformance-evaluation` 仕様が欠落している
- **rationale**：Req 6 AC 10 は「下流の `runtime` と `evaluation` 仕様は本語彙を参照し、再定義してはならない」と規定する。しかし Boundary Context「隣接仕様の期待」では `conformance-evaluation` が「本仕様の検証器用メタデータ契約に依存する」と明記されており、`conformance-evaluation` は検証器状態語彙の主要消費者のひとつである。計画書 §5.10 では `conformance-evaluation` が検証器機能を独立して持つ（passed／failed／blocked を参照して実行結果を判定する）ことが示されている。参照禁止リストに `conformance-evaluation` が含まれないと、将来の `conformance-evaluation` 実装者が誤って独自の語彙を定義するリスクがある。抽出元（英語原文 AC 10）も「downstream runtime and evaluation specs」とのみ記しており、`conformance-evaluation` は ReviewCompass 新規追加機能であるため抽出元に根拠がないことは正当だが、追加時の整合調整として補完が必要。
- **evidence_type**：mixed
- **verifying_commands**：
  - `grep -n "conformance-evaluation\|runtime.*再定義\|再定義.*runtime" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/foundation/requirements.md`

- **finding_id**：A-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/foundation/requirements.md §Requirement 5
- **description**：計画書 §5.18.11 が明示的に禁じた「削除済み」表記と v1／v2 経緯文が抽出後に残存し、自己適用前提除去の要件が達成されていない可能性
- **rationale**：計画書 §5.18.11 は「v1 撤廃の経緯（Requirement 5 削除）：抽出時に『削除済み』表記は持ち込まず、現行のみを記述」と明示的に指示している（敵対役の主張、判定役で要検証）。抽出後仕様 Req 5 節の節タイトルが「Requirement 5：削除済み」であり、本文に「旧 v1 の取得処理」「v2 では実 LLM 呼び出しに置き換える方針」が残存している。計画書の指示は「現行のみを記述」すなわちこの節を空記述または除去することを求めていると解釈できる。主役 F-001 が「機能名置換」観点で指摘した内容と重複するが、敵対役として独立の観点を追記する：「削除済み」という状態の記述自体が先行プロジェクトの開発経緯に依存しており、ReviewCompass で初めて本仕様を読む保守担当者にとって Req 5 の現行適用範囲が「ない」なのか「将来追加予定」なのかが不明確になる。
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "削除済み\|v1\|v2" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/foundation/requirements.md`

### 敵対役所見集計

- 主役所見への反論：counter_evidence_raised 2 件（F-002、F-004）／no_counter_evidence_after_challenge 3 件（F-001、F-003、F-005）／not_assessed 0 件
- 独立発見の重大度別：CRITICAL 0、ERROR 0、WARN 2（A-001、A-002）、INFO 0、計 2 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：must-fix
- **rationale**：抽出元の「v1／v2」版命名は dual-reviewer-rebuild プロジェクト固有であり、ReviewCompass の自己適用前提除去対象（計画書 §5.18.11 および §5.18.2 周辺の行 2189）。主役指摘は正当。敵対役による反証挑戦後も「no_counter_evidence_after_challenge」で反証なしが確認された。版命名を「先行プロジェクトの歴史的背景」として一般化するか、または Requirement 5 の節そのものを現行仕様のみの簡潔な記述に改める必要がある。

- **finding_id**：F-002
- **judgment**：leave-as-is
- **rationale**：敵対役が反証「Change Intent の先行プロジェクト言及は計画書 §5.18.11 の除去対象（機能名参照／配置先／リポジトリ前提）3 種に含まれず、文脈説明として機能している」を提示し、反証は根拠あり。主役は INFO として「除去が望ましい」と示唆したが、設計判断レベルの改善提案であり、形式要件違反ではない。現仕様のままで問題なし。

- **finding_id**：F-003
- **judgment**：must-fix
- **rationale**：敵対役が計画書 §5.18.13 に「サブエージェント経由への言及」が実際に存在しないことを grep で確認し「反証なし」と判定。仕様文書が計画書未反映の暫定実験（§5.23 本格採用未決定）に基づき記述されており、計画書との整合性が崩れている事実は確認された。フェーズ 1 完了前に計画書 §5.23 への反映または記述の取り下げが必須。

- **finding_id**：F-004
- **judgment**：should-fix
- **rationale**：敵対役が反証「計画書 §5.18.9 近傍（行 2247）で『B-1.0 運用で必須』という語彙が継承された概念として使用されており、undefined ではない」を提示。反証は根拠あり。ただし「フェーズ何に相当するか」の対応が仕様書内で未注記である点は重要。§5.18.8 の符号化規約（mandatory／deferred）との連動や、フェーズ 2 配置時点での対応明記が改善を推す。WARN 維持は妥当。

- **finding_id**：F-005
- **judgment**：must-fix
- **rationale**：敵対役が反証を検討したが「独立した異論」の機械判定可能な条件は仕様書内に記述なし。敵対役が計画書 §5.18.5 の `adversarial_outcome` 語彙（行 2221）を引用したが、この語彙が Req 1 AC 4 の検証基準として明示されていない。Req 1 AC 4 に「counter_status：反証提示／反証なし／未評価のいずれかを記録する」「必須：counter_status フィールドを finding に含める」など、機械判定可能な条件を追記が必須。

- **finding_id**：A-001
- **judgment**：must-fix
- **rationale**：敵対役の独立発見「conformance-evaluation 仕様が検証器状態語彙の参照禁止リストに欠落」は正当。Boundary Context 隣接期待で conformance-evaluation が「検証器用メタデータ契約に依存する」と明記され、計画書 §5.10 で conformance-evaluation の検査仕様が確認された。Req 6 AC 10 に「conformance-evaluation を参照禁止対象に追加」が必須。

- **finding_id**：A-002
- **judgment**：must-fix
- **rationale**：敵対役が主役 F-001 と関連した観点で「Requirement 5 の『削除済み』表記と v1／v2 経緯文が計画書指示に違反」と指摘。敵対役は独立に「削除済み状態の記述が読者に現行適用範囲を不明確にする」設計観点も追加提示。計画書指示「現行のみを記述」（§5.18.2 行 2189）から Req 5 の記述方法改善は要件達成必須。F-001 と統合した修正計画で対応する。

### 判定役所見集計

- judgment_distribution：must-fix 5 件（F-001、F-003、F-005、A-001、A-002）／should-fix 1 件（F-004）／leave-as-is 1 件（F-002）
- 採用所見の重大度別（must-fix ＋ should-fix）：CRITICAL 0、ERROR 1（F-005）、WARN 5（F-001、F-003、F-004、A-001、A-002）、INFO 0、計 6 件
- 不採用所見数（leave-as-is）：1 件（F-002、INFO）

### 判定の総合所見

抽出物の品質は全般的に高く、計画書 §5.18 系継承方針をほぼ網羅的に反映している。しかし以下の 3 点で要件達成が不完全である：

1. **自己適用前提除去の完全性（F-001、A-002）**：v1／v2 版命名と「削除済み」状態表記が残存しており、計画書 §5.18.2 行 2189 の「現行のみを記述」指示に違反。特に Requirement 5 では、先行プロジェクトの歴史的背景を記述せず、ReviewCompass 独立利用者が理解可能な一般化表現への改め、または削除が必須。修正難易度は低く、影響は限定的（段落 1〜2 の改訳で解決可）。

2. **機械検証可能性の欠落（F-005、A-001）**：Req 1 AC 4 の「独立した異論」と Req 6 AC 10 の「参照禁止対象」が具体的な判定基準を欠く。特に F-005 は ERROR（最高重大度）であり、検証実装時に「何をもって異論とするか」が定まらないと、判定役の意思を機械化できない。計画書 §5.18.5 行 2221 に存在する `adversarial_outcome` 語彙を Req スキーマに明記し、AC 記述を具体条件に改める必要がある。修正難易度は中程度（AC 追記 2〜3 項）。

3. **計画書との整合性（F-003）**：サブエージェント経由の語彙記述が計画書 §5.23 に未反映。本セッション実験的採用の暫定状態のため、フェーズ 1 完了前に計画書決定の有無を利用者確認し、仕様文書と計画書を同期する必要がある。修正難易度は低く、判断待ち（利用者承認）。

採用所見 6 件のうち must-fix が 5 件で、抽出物がリリース可能な水準には達していない。フェーズ 1 完了条件「自己適用前提の grep 0 件」達成のため、最低限 F-001・A-002 の修正は必須。F-005 の機械判定可能条件追記により、3 役レビュー機構の運用準備も完成する。3 点の改修によって、抽出物は要件達成水準に到達する見通し。修正工数は 2〜4 時間程度と見積もられる。

---

## 4. 統合（integration）

統合段は §5.15.2 に従い、追加の大規模言語モデル呼び出しを伴わずに主役・敵対役・判定役の出力を統合する。実施者はメインセッション（Opus 4.7、本記録のオーケストレーター）。

### 採用所見一覧

| finding_id | severity | judgment | target_location | 概要 |
|---|---|---|---|---|
| F-001 | WARN | must-fix | requirements.md §Requirement 5 | v1／v2 版命名が残存（一般化または削除が必須） |
| F-003 | WARN | must-fix | requirements.md §Requirement 6 受入 6 | サブエージェント語彙が計画書 §5.23 未反映の暫定記述 |
| F-004 | WARN | should-fix | requirements.md §Requirement 3 受入 9 | B-1.0 とフェーズ対応の未注記（フェーズ 2 配置時点で対応） |
| F-005 | ERROR | must-fix | requirements.md §Requirement 1 受入 4 | 「独立した異論」の機械判定条件未定義 |
| A-001 | WARN | must-fix | requirements.md §Requirement 6 受入 10 | 参照禁止対象に `conformance-evaluation` 欠落 |
| A-002 | WARN | must-fix | requirements.md §Requirement 5 | 「削除済み」表記が計画書指示違反（F-001 と統合修正） |

### 抽出元との対応

- 抽出元由来の論点：
  - F-001／A-002：抽出元の Req 5 が「v1／v2」「削除済み」表記を含み、これを直接転写したことに起因
  - F-005：抽出元の Req 1 AC 4 も「独立した異論を最低限要求する」とのみ記述し具体条件を持たない（抽出元由来の不備）
- 新規発見（抽出による）：
  - A-001：`conformance-evaluation` は ReviewCompass 新規追加機能。抽出元の Req 6 AC 10 は `runtime` と `evaluation` のみを参照禁止対象としており、新規機能の追加に伴う整合調整漏れを発見
  - F-003：本セッションで採用したサブエージェント方式に関する記述が、計画書 §5.23 未反映の暫定状態のまま仕様文書に先行記述された問題

### 残課題と本セッションでの対処結果

**本セッション内で対処済み（2026-05-22 利用者承認後実施）**：

- **F-001／A-002 統合**：Requirement 5 の節を「削除済み」表記から「パターン定義依存の除外」の能動的要件に書き換え（3 受入基準を新設）。v1／v2 表記と「削除済み」表記をすべて除去
- **F-005**：Requirement 1 受入 4 に counter_status の機械判定条件を追記（語彙：`counter_evidence_raised`／`no_counter_evidence_after_challenge`／`not_assessed`、本仕様が語彙正本を所有）。Requirement 3 受入 5 にも counter_status フィールドを追加
- **A-001**：Requirement 6 受入 10 の参照禁止対象に `conformance-evaluation` を追加
- **F-003**：利用者承認によりサブエージェント方式を正式採用。計画書に新節 §5.23.12「サブエージェント方式（中間経路、2026-05-22 確定）」を追加し、§5.18.13 にレビューモード語彙の 3 値体制への拡張を明記。仕様文書側 Requirement 6 受入 6 を「正式値として保持」に書き換え

**次セッション以降への持ち越し**：

- **F-004**：Requirement 3 受入 9 の B-1.0 とフェーズ対応の未注記。仕様より配置の話に近く、フェーズ 2 着手時にディレクトリ配置と合わせて検討
- **将来のフェーズ波及**：A-001 の解消に伴う `schemas/foundation/metadata_contract.yaml` の所有者明記（フェーズ 2 配置時）、F-005 の解消に伴う `schemas/domain/finding.schema.json` への `counter_status` フィールド追加（フェーズ 2 配置時）

### 修正後の検証

修正後、再度 grep 検査を実施：

- `dual-reviewer-*` ／ `paper-interface` ／ `implementation-governance` の残存：0 件（変更なし）
- `v1` ／ `v2` ／ `削除済み` の残存：requirements.md 内で 0 件（修正により解消、ただし旧バージョン参照を意図的に残す Change Intent は除外）
- counter_status の追加：Requirement 1 受入 4 と Requirement 3 受入 5 に追加済み
- conformance-evaluation の参照禁止リスト追加：Requirement 6 受入 10 に追加済み

### サブエージェント方式の効果評価（暫定）

本セッションで初めて採用したサブエージェント方式（敵対役 Sonnet 4.6、判定役 Haiku 4.5）の効果と課題を暫定的に記録する。事後評価で計画書 §5.23 への正式採用可否を判断する材料とする。

- **効果**：
  - 異なるモデルファミリーを 3 役に割り当てられた（モデル多様化規律 §5.9.1 を実質達成）
  - 敵対役は計画書を独自に grep して反証根拠を提示（A-002 は主役が見逃した観点を発見、A-001 は完全に独立な発見）
  - 判定役は両者を踏まえた総合判定を実施。重大度の引き上げと修正計画の構築を実施
  - 1 セッション内で 3 役完結。手動 dogfooding で問題となる独立性の確保が技術的に達成された
- **課題**：
  - 敵対役の計画書引用に §番号誤り（§5.18.11 と引用したが実体は §5.18.2 周辺）。事実検証はメインセッションで補完する必要があった
  - プロンプト雛形が未整備のため、各役のプロンプトを Agent 呼び出し時のメッセージで暫定指示した。フェーズ 4 で `templates/prompts/<段の用途>/` の整備が前提となる
  - サブエージェントは独立 session のためメインセッションの作業文脈を直接共有しない。プロンプトに必要情報を網羅的に書き込む必要があり、プロンプト設計が結果品質に強く影響する
- **計画書 §5.23 への提案**：
  - 新節 §5.23.X として「サブエージェント方式の運用条件」を追加する案
  - mode 値として `subagent_mediated` を foundation の metadata_contract.yaml レビューモード語彙に正式追加する案
  - 上記の正式採用可否は利用者判断（本セッション末または次セッション初）

