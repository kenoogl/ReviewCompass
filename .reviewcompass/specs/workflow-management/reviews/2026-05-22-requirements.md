---
type: requirements_local_review
target: .reviewcompass/specs/workflow-management/requirements.md
date: 2026-05-22
mode: subagent_mediated
session: session-19
author:
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
reviewer:
  identity: claude_code_subagent
  model: claude-haiku-4-5-20251001
  role: final_judgment
  separation_from_author: true
primary:
  provider: claude_code_main_session
  model: claude-opus-4-7
adversarial:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
judgment:
  provider: claude_code_subagent
  model: claude-haiku-4-5-20251001
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 1 }
    count: 2
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 3, INFO: 0 }
    count: 3
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 4, INFO: 0 }
    count: 4
    judgment_distribution: { must-fix: 2, should-fix: 2, leave-as-is: 1 }
---

# レビュー記録：workflow-management requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

5 観点（要件の網羅性／機能名置換／自己適用前提除去／§5.4〜§5.8 系継承方針の反映／検証可能性）。

### 観点 1：要件の網羅性

本仕様は **大規模な再設計**で、素材の 156 行・9 要件を ReviewCompass 用の 8 要件に統合・縮減した。「思想は継承、実装は 1／10」の方針（計画書 §5.4）に従い、削除した部分（旧 Req 9 の大規模機構など）と統合先（Req 1〜4 の軽量版）は Change Intent に明示。網羅性は計画書 §5.4〜§5.8 の確定事項を網羅的に要件化。所見なし。

### 観点 2：機能名置換の正確性

`implementation-governance` → `workflow-management` の改称が反映済み。本文に旧名残存なし（Change Intent と Introduction の歴史的記述のみ）。所見なし。

### 観点 3：自己適用前提の除去完全性

素材の自己適用前提（「実装が spec を守っているか」「fixture / heuristic 依存」など）は除去済み。ReviewCompass の所定手続き管理として再構築。所見なし。

### 観点 4：計画書 §5.4〜§5.8 系の継承方針の反映

- §5.4 軽量化方針：Requirement 1-2 で反映 ✓
- §5.5 階層構造（9 ファイル体制）：Requirement 1 受入 2 で明示 ✓
- §5.6 reopen 機械強制：Requirement 5 で反映 ✓
- §5.7 session 跨ぎ状態管理：Requirement 6 で反映 ✓
- §5.8 多層防御：Requirement 7 で反映 ✓
- §5.4 起草者と判定者の分離：Requirement 3 で反映 ✓
- §5.23.12 サブエージェント方式対応：Requirement 3 受入 3 で反映 ✓
- §5.5 機能依存マップ（feature-dependency.yaml）：Requirement 8 で反映 ✓

所見なし。

### 観点 5：要件の検証可能性

- **finding_id**：F-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/workflow-management/requirements.md §Requirement 3 受入 3
- **description**：Requirement 3 受入 3「サブエージェント方式でメインセッションが主役を担う場合、判定役を必ず別エンティティ（別モデル、別 session）で実施することを要求する」が、機械的にどう検知するかの判定条件を持たない
- **rationale**：本機能の検査スクリプト（Requirement 2）は front-matter の必須フィールド存在と異名条件を判定する（Requirement 3 受入 4）。しかし「別モデル」「別 session」の機械判定条件は未指定。例えば「`reviewer.model_full_id != author.model_full_id`」「`reviewer.identity` が `claude_code_subagent` を含むこと」のような具体的な機械条件を示さないと、検査スクリプトの実装で曖昧さが残る
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "subagent_mediated|別エンティティ|別モデル|別 session" .reviewcompass/specs/workflow-management/requirements.md`

- **finding_id**：F-002
- **severity**：INFO
- **target_location**：.reviewcompass/specs/workflow-management/requirements.md §Requirement 7 受入 4
- **description**：Requirement 7 受入 4「第 1 層の限界を運用文書に明示し、利用者の期待値を整える」は機械判定不能で、本機能の検査スクリプト責務外
- **rationale**：「運用文書に明示し」は文書整備の指示で、機械検査の対象にならない。Requirement 7 全体が「位置付け」を扱うため、機械判定不能な受入が混じるのは自然だが、本機能の検査スクリプト責務外であることを Boundary Context Out of scope に明示すると整合性が増す
- **evidence_type**：inference

### 該当なし観点

なし。

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 1（F-001）、INFO 1（F-002）、計 2 件
- evidence_type 別：fact 1、inference 1

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

### 主役所見への反論検討

- **対象 finding_id**：F-001
- **counter_status**：`counter_evidence_raised`（部分的反証）
- **counter_rationale**：「機械的にどう検知するかの判定条件が未指定」という指摘は仕様の設計意図を踏まえると評価が一部過剰。Requirement 3 受入 4 が「front-matter の必須フィールド存在と異名条件を判定する」と明示しており、受入 3 の「別エンティティ」要求を機械判定に引き込む設計か否かは仕様上意図的に区別されている可能性がある。「思想は継承、実装は 1／10」方針と組み合わせると、「別モデル・別 session の機械判定」は第 1 層から外すことが合理的判断。ただし受入 3 と受入 4 の検査対象の対応が曖昧である点は妥当。

- **対象 finding_id**：F-002
- **counter_status**：`counter_evidence_raised`（完全反証）
- **counter_rationale**：「機械判定不能な受入が混じる」点は仕様の書き方に対する improvement 提案で、欠落や矛盾の指摘ではない。Requirement 7 は多層防御の「位置付け」を扱う要件であり、受入 4 が文書整備の義務を規定することは要件の性質上当然。検査スクリプト責務外である事実は Req 2 受入 3 と Req 7 受入 1 の組み合わせから自明に導出可能で、Boundary Context への重複明示は冗長。

### 独立発見

#### 機能内所見

- **finding_id**：F-003
- **severity**：WARN
- **target_location**：.reviewcompass/specs/workflow-management/requirements.md §Requirement 5 受入 1
- **description**：手戻り種別表記「N／R／D／A／I ＋ 深さ 0〜4」が均一表記だが、計画書 §5.6 の trigger_map では N 起点は N-0 のみで、N-1 以上は原理上発生しない（intent より上流のフェーズがない）
- **rationale**：起点フェーズより上流の存在しないものについて深さ上限が異なる非対称性を均一表記すると、実装者が N-1 等の種別文字列を誤入力したときの扱いが未定義。**メインセッション事前検証で計画書 §5.6 行 516〜522 が N-0 のみを定義することを確認**
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nA 5 "N 起点\|N-0" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：F-004
- **severity**：WARN
- **target_location**：.reviewcompass/specs/workflow-management/requirements.md §Requirement 4 受入 1／受入 2 と §Requirement 6 受入 3
- **description**：session 開始時の事前検査（Req 6 受入 3）と不可逆操作直前ゲート（Req 4）の関係が未定義
- **rationale**：session 開始時のスクリプト走行結果を直前ゲートが参照するのか、直前に独立して再走行するのかで挙動が変わる。前者なら session 開始後の中間操作で状態変化を検知できず、後者なら二重実行。本仕様はどちらかを規定していない
- **evidence_type**：inference

#### 機能横断所見

- **finding_id**：A-005
- **severity**：WARN
- **target_location**：.reviewcompass/specs/workflow-management/requirements.md §Requirement 8 受入 2／受入 3
- **description**：計画書 §5.5 の feature-dependency.yaml 構造例で `conformance-evaluation` の `depends_on` は `hard`／`review` の依存種別を持つ特殊構造になっているが、Req 8 受入 2 のスキーマ定義は依存種別の多様性を明示していない
- **rationale**：計画書 §5.5 行 368〜373 で `conformance-evaluation.depends_on` は `foundation: hard`／`runtime: review`／`evaluation: review`／`workflow-management: review` の連想配列構造。他機能は `depends_on: [list]` の単純構造。Req 8 受入 2「`features`（機能ごとの `depends_on` 列挙）」では両者の差を扱えない。**メインセッション事前検証で確認**
- **波及範囲**：
  - **workflow-management**：Req 8 受入 2／3 のスキーマ定義に依存種別（`hard`／`review`）を明示
  - **conformance-evaluation**：将来の conformance-evaluation requirements.md における feature-dependency.yaml への依存記述
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nA 25 "feature-dependency.yaml の構造例" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

### 敵対役所見集計

- 主役所見への反論：counter_evidence_raised 2 件（F-001 部分／F-002 完全）／not_assessed 0 件
- 独立発見の重大度別：機能内 WARN 2（F-003、F-004）、機能横断 WARN 1（A-005）、計 3 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：should-fix
- **rationale**：「機械判定条件が未指定」という指摘は部分的に妥当。敵対役の反証「思想は継承、実装は 1／10 方針下で別モデル・別 session の機械判定を第 1 層から外すのは合理的」も支持される。ただし受入 3 と受入 4 の検査対象範囲の対応が曖昧である点は改善必要。受入 4 に「（別モデル・別 session の機械判定は第 1 層検査対象外）」の括弧書きを追加、または受入 3 をより具体的に機械条件化。

- **finding_id**：F-002
- **judgment**：leave-as-is
- **rationale**：敵対役の反証が妥当。Req 7 全体が「位置付け」を扱う要件で、受入 4「運用文書に明示」は文書整備の義務。要件の性質上の自然な結果。Boundary Context への冗長な明示は不要。

- **finding_id**：F-003
- **judgment**：must-fix
- **rationale**：計画書 §5.6 行 516〜522 で N 起点が N-0 のみ（intent より上流が存在しない）と確認済み。Req 5 受入 1 の「0〜4 均一表記」は不正確。N 起点は深さ 0 のみ、R 起点は 0〜1、D 起点は 0〜2、A 起点は 0〜3、I 起点は 0〜4 と非対称（計画書 §5.6 の trigger_map から導出）。受入 1 に非対称性を明示する必要。

- **finding_id**：F-004
- **judgment**：should-fix
- **rationale**：Req 6 受入 3「session 開始時の検査」と Req 4 受入 2「不可逆操作直前のゲート」の関係が未定義。二重実行か、session 開始時の結果を直前ゲートが参照するか、その間の変化検知方針かが不透明。Req 4 受入 2 に「直前ゲートは毎回独立して走行する（session 開始後の状態変化の可能性）」を明示するか、Req 6 受入 3 に「session 開始時の検査は進行中手続きの優先判定用、不可逆操作時は Req 4 が独立実行」を明示。

- **finding_id**：A-005
- **judgment**：must-fix（機能内スキーマ拡張 ＋ 機能横断記録の二重対応）
- **rationale**：計画書 §5.5 行 368〜373 で `conformance-evaluation.depends_on` が連想配列構造（`hard`／`review`）であることを確認。Req 8 受入 2 のスキーマ定義は他機能の単純配列と conformance-evaluation の連想配列の両方を扱えない。**本セッションで Req 8 受入 2 のスキーマ拡張は機能内対処として可能**。**conformance-evaluation requirements.md 作成時の反映は機能横断要素として pending-cross-feature-findings.md に記録**。

### 判定役所見集計

- judgment_distribution：must-fix 2 件（F-003 機能内、A-005 機能内 ＋ 機能横断記録）／should-fix 2 件（F-001、F-004）／leave-as-is 1 件（F-002）
- 採用所見の重大度別（must-fix ＋ should-fix）：CRITICAL 0、ERROR 0、WARN 4、INFO 0、計 4 件
- 機能内対処（本セッション可能）：4 件（F-001、F-003、F-004、A-005 の workflow 側）
- 機能横断記録（pending-cross-feature-findings.md）：1 件（A-005 の conformance-evaluation 側反映予定）
- 不採用：1 件（F-002）

### 判定の総合所見

本機能は計画書 §5.4〜§5.8 の確定方針に基づく大規模再設計であるが、計画書の具体例（§5.6 trigger_map の N-0 のみ、§5.5 feature-dependency.yaml の連想配列構造）を仕様明文化時に十分参照しきれていない点で F-003 と A-005 の must-fix が発生。これらは事前検証済みの計画書ズレで、明示修正が必要。

F-001 と F-004 は「思想は継承、実装は 1／10」方針下での機械検査の責務範囲の定義不足。第 1 層と利用者監査の境界、検査実行タイミングの連携を仕様で明示することで、フェーズ 2 設計段階の混乱を防げる。

A-005 は workflow-management 側のスキーマ拡張（機能内）と conformance-evaluation 側の反映（機能横断記録）の二重対応。本セッションで workflow 側を直し、conformance-evaluation 抽出時に同様の対応を反映する位置付け。サブエージェント方式は計画書との照合で 5 機能目も有効に機能。

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 対処範囲 |
|---|---|---|---|---|
| F-001 | WARN | should-fix | requirements.md §Req 3 受入 4 | 機能内 |
| F-003 | WARN | must-fix | requirements.md §Req 5 受入 1 | 機能内 |
| F-004 | WARN | should-fix | requirements.md §Req 4 受入 2 または §Req 6 受入 3 | 機能内 |
| A-005 | WARN | must-fix | requirements.md §Req 8 受入 2 ＋ 将来 conformance-evaluation | **機能内 ＋ 機能横断記録** |

### 残課題と対処方針

**本セッション内で対処（機能内、4 件）**：

- F-001：Req 3 受入 4 に「別モデル・別 session の機械判定は第 1 層検査対象外、利用者監査の第 3 層に委ねる」の括弧書きを追加
- F-003：Req 5 受入 1 を起点別の深さ範囲（N=0、R=0〜1、D=0〜2、A=0〜3、I=0〜4）に修正
- F-004：Req 4 受入 2 に「直前ゲートは毎回独立して走行する」の明示を追加
- A-005（workflow 側）：Req 8 受入 2 のスキーマ定義を依存種別（`hard`／`review`）対応に拡張

**機能横断記録（A-005 の conformance-evaluation 側、1 件）**：

- conformance-evaluation requirements 作成時に「feature-dependency.yaml の依存記述」を反映する旨を pending-cross-feature-findings.md に記録

**leave-as-is（1 件）**：

- F-002（INFO）：Req 7 の性質上の自然な結果、不要

### サブエージェント方式の効果評価（workflow-management、5 機能目）

- **計画書との照合**：敵対役（Sonnet 4.6）が計画書 §5.6 と §5.5 の具体例から仕様の不整合（F-003、A-005）を独立に発見。サブエージェント方式の独立視点の効果が継続的に確認
- **大規模再設計の検証**：素材から ReviewCompass 用への大規模再設計（156 行 9 要件 → 8 要件）で漏れた具体例（N-0 のみ、連想配列構造）を露出
- **機能横断累積**：A-005 が pending-cross-feature-findings.md の 4 件目（A-001／A-003／A-004／A-005）。conformance-evaluation 抽出時に集中消化対象

---

