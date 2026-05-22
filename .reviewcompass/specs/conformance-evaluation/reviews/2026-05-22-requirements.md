---
type: requirements_local_review
target: .reviewcompass/specs/conformance-evaluation/requirements.md
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
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 1 }
    count: 3
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 3, INFO: 0 }
    count: 3
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 4, INFO: 0 }
    count: 4
    judgment_distribution: { must-fix: 4, should-fix: 1, leave-as-is: 1 }
---

# レビュー記録：conformance-evaluation requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

5 観点：要件の網羅性／機能名置換（新規機能、N/A）／自己適用前提除去／§5.10 系継承方針の反映／検証可能性。

### 観点 1：要件の網羅性

§5.10.1〜§5.10.7 の確定事項を Requirement 1〜8 に対応：
- §5.10.1 機能の性格 → Req 1 ＋ Req 8（実装適合レビューとの分離）
- §5.10.2 評価軸と criteria 構造 → Req 4
- §5.10.3 3 役レビュー機構の流用 → Req 5
- §5.10.4 評価記録の type 値と配置 → Req 6
- §5.10.5 依存関係（連想配列構造） → Req 7
- §5.10.6 v3-plan §3.3 の扱い → Change Intent
- §5.10.7 段階的導入 → Change Intent

2 モード（文書生成／照合チェック）は §5.10.1 の主要用途を Req 2／3 として分離記述。所見なし。

### 観点 2：機能名置換

新規 7 番目機能のため機能名置換なし（`conformance-evaluation` のまま）。所見なし。

### 観点 3：自己適用前提の除去

新規仕様のため、書き起こし段階で自己適用前提は含まれていない。所見なし。

### 観点 4：§5.10 系継承方針の反映

- §5.10.1 性格と方向：Req 1 で反映 ✓
- §5.10.2 12 criteria：Req 4 で反映 ✓
- §5.10.3 3 役レビュー流用：Req 5 で反映 ✓
- §5.10.4 type 値と配置：Req 6 で反映 ✓
- §5.10.5 連想配列依存：Req 7 で反映、A-005 と整合 ✓
- §5.10.6 v3-plan §3.3 の責務分担：Change Intent で反映 ✓
- §5.10.7 段階的導入：Change Intent で反映 ✓
- §5.18.13 レビューモード 3 値体制：Req 5 受入 6 で反映 ✓

所見なし。

### 観点 5：検証可能性

- **finding_id**：F-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Requirement 2 受入 1
- **description**：Req 2 受入 1「実装コードを入力として上流文書を推定生成する」の最低限充足条件（推定文書のサイズ・節構成等）が未指定
- **rationale**：「推定生成する」のみでは検証時に「何を満たせば生成が完了したか」が判定できない。例：「最低限 Introduction／Boundary Context／Requirements の 3 節を含む」「実装コードへの参照が最低 1 件含まれる」等の具体的な機械判定可能な条件が必要。design 段に委ねるならその旨を明示
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "推定生成|最低限|必須節" .reviewcompass/specs/conformance-evaluation/requirements.md`

- **finding_id**：F-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Requirement 3 受入 1
- **description**：Req 3 受入 1「既存上流文書と推定上流文書を比較し、食い違いを列挙する」の「食い違い」の機械判定基準が未指定
- **rationale**：「比較」と「食い違い」の定義が requirements レベルで欠落していると、design 段以降の判定実装に解釈差異が生じる。例：「節の有無」「節内の主張・受入基準の対応関係」「実装コードと文書の言及齟齬」のどれを「食い違い」とするか
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "食い違い|比較|不整合" .reviewcompass/specs/conformance-evaluation/requirements.md`

- **finding_id**：F-003
- **severity**：INFO
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Boundary Context 隣接仕様の期待
- **description**：Out of scope に「5 評価軸のうち実装適合」が記載されているが、隣接期待では `runtime` が実装適合の責務を持つ点が明示されていない
- **rationale**：Req 8 受入 2 で「実装適合レビューは §5.9 と `runtime` の連携に残る」と明示されているが、Boundary Context の隣接期待リストにこの責務分担を 1 行加えると、読み手の責務把握が早まる
- **evidence_type**：inference

### 該当なし観点

なし。

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 2（F-001、F-002）、INFO 1（F-003）、計 3 件
- evidence_type 別：fact 2、inference 1

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

### 2.1 主役所見への反論検討

#### F-001 への反論検討

- **counter_status**：partial_accept
- **counter_rationale**：
  「推定生成する」の最低限充足条件が requirements レベルで未指定である点は事実だが、主役の「記述が完全にない」という評価は過剰。Req 2 受入 3（「推定の根拠を実行記録に保持する」）と受入 4（「人間判断の必要性を明示する」）は、出力物の最低限の属性として「推定根拠の可追跡性」と「人間チェックを前提とした未完性」を間接的に規定している。したがって「出力物の定義が一切ない」とは言えない。ただし、「最低限の節構成」「参照カウント」などの機械判定可能な完了基準は requirements レベルで確かに欠落しており、設計段での明示が不可欠。所見の方向性は正当だが、重大度 WARN の根拠となる「設計段への委任が明示されていない」点の補足があれば説得力が増す。F-001 は部分的に支持し、design.md 作成時の明示要求として残すことを推奨する。

#### F-002 への反論検討

- **counter_status**：accept
- **counter_rationale**：
  「食い違い」の機械判定基準が requirements レベルで欠落している点は純粋な事実。Req 3 受入 1 の「比較し、食い違いを列挙する」には「何をもって食い違いとするか」の定義が一切ない。§5.10 の計画書本文（行 1012〜1033）も 12 criteria の内容を列挙するにとどまり、比較対象の粒度（節の有無・主張の一致・AC との対応など）を規定していない。反論材料なし。主役の指摘は妥当であり、F-002 は全面的に支持する。重大度 WARN 相当が適切。

#### F-003 への反論検討

- **counter_status**：reject
- **counter_rationale**：
  F-003 は「Boundary Context の隣接期待に runtime の責務分担を 1 行加えると読み手の理解が早まる」という利便性提案。しかし Req 8 受入 2（「実装適合レビューは §5.9 と runtime の連携に残る」）が Requirements セクション内で明示済みであり、Boundary Context 内での重複記載は情報冗長を招く。仕様文書の読み方として Boundary Context は「隣接機能が何を期待するか」を記載する場所であり、本機能の責務分担の詳細説明は Requirement 8 の担当範囲。主役の所見は「あったほうが便利」レベルの改善提案であり、要件上の欠落ではない。重大度 INFO の評価と合わせても、leave-as-is が妥当。

### 2.2 独立発見（機能内）

#### A-CONF-I-001

- **finding_id**：A-CONF-I-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Requirement 2 受入 2
- **description**：既存上流文書がある場合の出力先「別名または別ディレクトリ」の具体的パス規則が未定義
- **rationale**：受入 2 は「既存上流文書がある場合は上書きせず別名または別ディレクトリで出力」と規定するが、「別名」と「別ディレクトリ」の両方が許容されており、どちらを選ぶかの判断基準・実際のパス規則が requirements レベルで未指定。§5.10 計画書本文にも具体的なパス規則の記述がない（計画書 §5.10 行 1102〜1106 を精査したが「推定版」の出力先に言及なし）。実装者が `intent_inferred.md`（別名案）と `conformance/inferred/intent.md`（別ディレクトリ案）のどちらを選ぶかが設計段まで持ち越される。受入 5（生成記録の配置先は `conformance/<日付>-generation.md`）と対で、推定文書本体の配置先も同等の具体性で指定されるべき。
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "別名|別ディレクトリ|inferred|generated" .reviewcompass/specs/conformance-evaluation/requirements.md`
  - `grep -nE "推定版.*出力|inferred_spec" docs/plan/reconstruction-plan-2026-05-21.md`

#### A-CONF-I-002

- **finding_id**：A-CONF-I-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Requirement 5 受入 1〜5
- **description**：§5.9 の規律を流用する旨の記載は Req 5 受入 1〜5 にあるが、API 経路と障害対応（§5.9.7）が Requirement 5 の流用対象から漏れている
- **rationale**：Req 5 受入 1（3 役機構）、受入 2（§5.9.1 の規律）、受入 3（重大度語彙）、受入 4（所見メタデータ）、受入 5（§5.9.6 の 3 方式比較）は明示されているが、§5.10.3 で計画書が明示している「API 経路と障害対応（§5.9.7）」が Requirement 5 の受入基準に含まれていない。計画書 §5.10.3 行 1051 に「API 経路と障害対応（§5.9.7）」が §5.9 規律の適用項目として明記されているにもかかわらず、仕様 Req 5 には受入 6 として追加されていない。conformance-evaluation は LLM API 呼び出しを伴う機能のため、障害対応の不在は実装段で影響が出うる。
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "§5\.9\.7|API 経路|障害対応|タイムアウト|リトライ" .reviewcompass/specs/conformance-evaluation/requirements.md`
  - `grep -nE "§5\.9\.7|API 経路" docs/plan/reconstruction-plan-2026-05-21.md | grep -i "5\.10"`

### 2.3 独立発見（機能横断）

#### A-008：conformance-evaluation から self-improvement への出力経路が両仕様で非対称

- **finding_id**：A-008
- **severity**：WARN
- **target_location**：.reviewcompass/specs/conformance-evaluation/requirements.md §Boundary Context 隣接仕様の期待 vs .reviewcompass/specs/self-improvement/requirements.md
- **description**：conformance-evaluation は Boundary Context で「self-improvement へ規律レベル戻しを受け取り、規律改善の入力とする」と記載しているが、方向が逆（self-improvement が conformance-evaluation の出力を受け取る側のはずであり、conformance-evaluation の隣接期待に記載すべきは「self-improvement が何を期待するか」ではなく「本機能が self-improvement に何を出力するか」）
- **rationale**：self-improvement の requirements.md（行 33）は「conformance-evaluation から規律遵守検査の適合性評価結果を入力源として活用可能」と記載しており、self-improvement が conformance-evaluation の出力を読む方向。一方 conformance-evaluation の隣接期待（行 33）は「self-improvement：規律レベル戻し（文書とは別経路）を受け取り、規律改善の入力とする」と表現しており、conformance-evaluation が self-improvement を入力源として受け取る（逆方向）かのように読める文言になっている。これは Out of scope の記述（「規律レベルの戻し：self-improvement の workflow 改善（§5.16）が扱う、本機能のスコープ外」）とも方向性が不明確な矛盾を生じさせる。feature-dependency.yaml にも `self-improvement` が conformance-evaluation の depends_on に含まれておらず、依存構造との整合が崩れている。
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "self-improvement" .reviewcompass/specs/conformance-evaluation/requirements.md`
  - `grep -nE "conformance.evaluation" .reviewcompass/specs/self-improvement/requirements.md`
  - `grep -nE "self.improvement" .reviewcompass/specs/conformance-evaluation/requirements.md`

### 2.4 敵対役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 3（A-CONF-I-001、A-CONF-I-002、A-008）、INFO 0、計 3 件
- うち機能内：2 件（A-CONF-I-001、A-CONF-I-002）
- うち機能横断：1 件（A-008、pending-cross-feature-findings.md へ追記）
- F-001 counter_status：partial_accept／F-002 counter_status：accept／F-003 counter_status：reject
- evidence_type 別：fact 3

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：should-fix
- **rationale**：敵対役 partial_accept の通り、受入 3／4 で出力物の属性は部分的に規定されている。ただし「最低限の節構成」など機械判定可能な完了基準を Requirement 2 受入 1 に 1 行追加すれば仕様完成度が上がる。design 段での詳細化余地があるため must-fix ではなく should-fix。

- **finding_id**：F-002
- **judgment**：must-fix
- **rationale**：敵対役 accept、反論なし。Req 3「比較し、食い違いを列挙する」に「何をもって食い違いとするか」の定義がないのは仕様の基礎欠落。requirements 段でも最低限「4 上流フェーズ × 3 criteria に基づく比較対象粒度」を明示すべき。実装者解釈差異リスクが高い。

- **finding_id**：F-003
- **judgment**：leave-as-is
- **rationale**：敵対役 reject が正当。Req 8 受入 2 で既明示。Boundary Context は「隣接機能の期待」の場所で、本機能の責務分担の重複記載は冗長。

- **finding_id**：A-CONF-I-001
- **judgment**：must-fix
- **rationale**：Req 2 受入 5（生成記録の配置先）と対で、推定文書本体の配置先も同等の具体性で規定されるべき。「別名または別ディレクトリ」の両方を許容したまま判断基準を仕様に記さないのは曖昧。Req 6 の評価記録配置の具体性と並ぶ重要要素。

- **finding_id**：A-CONF-I-002
- **judgment**：must-fix
- **rationale**：計画書 §5.10.3 行 1051 で「API 経路と障害対応（§5.9.7）」が §5.9 規律の流用対象として明記されているのに、Requirement 5 に欠落。LLM API を伴う本機能では実装影響大。Req 5 に受入 6 として追加すべき。

- **finding_id**：A-008
- **judgment**：must-fix（機能内修正 ＋ pending-cross-feature-findings.md 既追記）
- **rationale**：両仕様文書で情報流の方向が不一致は読み手を混乱させる事実矛盾。conformance-evaluation 側の Boundary Context 「self-improvement」の記述を「本機能の 12 criteria 検査結果を規律改善の入力として提供する」と方向整理。pending-cross-feature-findings.md には記録済みだが、conformance-evaluation 側の修正は本セッション内で対処可能。

### 判定役所見集計

- judgment_distribution：must-fix 4 件（F-002／A-CONF-I-001／A-CONF-I-002／A-008）／should-fix 1 件（F-001）／leave-as-is 1 件（F-003）
- 採用所見の重大度別：CRITICAL 0、ERROR 0、WARN 5（F-001／F-002／A-CONF-I-001／A-CONF-I-002／A-008）、INFO 0、計 5 件
- 機能内対処（本セッション可能）：5 件（F-001／F-002／A-CONF-I-001／A-CONF-I-002／A-008 conformance 側）
- 機能横断記録（pending-cross-feature-findings.md）：1 件（A-008、既追記済み）
- 不採用：1 件（F-003）

### 判定の総合所見

本仕様は計画書 §5.10 の要件を網羅的に反映した初版として適切な構成を持つが、要件仕様としての検証可能性と具体性で 5 点の修正が必要。F-002（「食い違い」判定基準欠落）と A-CONF-I-001（推定文書出力先パス規則欠落）は実装者解釈差異リスクが高い基礎的欠落。A-CONF-I-002 は計画書 §5.10.3 で明記された §5.9.7 の確認漏れであり、LLM 複数呼び出しに依存する本機能の性格を考えるとリスク評価は高い。A-008 は機能横断矛盾で、self-improvement との仕様整合を優先すべき。F-001 と F-003 は改善余地と冗長性のレベルで棲み分けが明確。

7 機能目の最終レビューとして、サブエージェント方式（mode = `subagent_mediated`）は新規機能の書き起こしに対しても有効に機能した。敵対役（Sonnet 4.6）が機能横断の方向矛盾（A-008）を独立に発見した点は特筆に値する。サブエージェント方式の独立視点が、新規機能を含むすべての機能で機能横断整合を露出させる効果を実証した。

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 対処範囲 |
|---|---|---|---|---|
| F-001 | WARN | should-fix | requirements.md §Req 2 受入 1 | 機能内 |
| F-002 | WARN | must-fix | requirements.md §Req 3 受入 1 | 機能内 |
| A-CONF-I-001 | WARN | must-fix | requirements.md §Req 2 受入 2 | 機能内 |
| A-CONF-I-002 | WARN | must-fix | requirements.md §Req 5 に受入 6 追加 | 機能内 |
| A-008 | WARN | must-fix | requirements.md §Boundary Context self-improvement 記述 | 機能内 ＋ 機能横断既記録 |

### 残課題と本セッションでの対処方針

**本セッション内で対処（機能内 5 件、すべて）**：

- F-001：Req 2 受入 1 に最低限充足条件（節構成・実装コード参照）を追記
- F-002：Req 3 受入 1 に「食い違い」の比較対象粒度を明示
- A-CONF-I-001：Req 2 受入 2 に推定文書の出力先パス規則を明示
- A-CONF-I-002：Req 5 に受入 6 として §5.9.7 API 経路と障害対応を追加
- A-008：Boundary Context の「self-improvement」記述を方向整理（出力先として参照される、依存記述は外部化）

**機能横断記録（既記載済み）**：

- A-008 は pending-cross-feature-findings.md に既追記済み

**leave-as-is**：

- F-003（INFO）：Req 8 で既明示、Boundary Context 重複記載は冗長

### サブエージェント方式の最終評価（conformance-evaluation、7 機能目）

- **新規機能への有効性**：素材なしの新規 7 番目機能でも、敵対役が機能横断視点（A-008）を独立発見。サブエージェント方式の独立視点の効果が新規機能でも実証
- **直接書き込みの効率化**：敵対役が pending-cross-feature-findings.md に A-008 を直接追記。前セッションのパターン（self-improvement A-007）が確立
- **計画書照合の継続効果**：敵対役が計画書 §5.10.3 行 1051 の §5.9.7 流用記述の欠落（A-CONF-I-002）を発見。計画書との整合確認が継続的に機能
- **機能横断累積**：A-001／A-003／A-004／A-005／A-007／A-008 と計 6 件に累積（A-005 は workflow 側対処済み、A-008 は conformance 側で対処予定）。要件 review-wave での消化対象
