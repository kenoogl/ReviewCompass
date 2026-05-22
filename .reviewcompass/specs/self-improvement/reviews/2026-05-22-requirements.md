---
type: requirements_local_review
target: .reviewcompass/specs/self-improvement/requirements.md
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
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 2 }
    count: 3
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 1, INFO: 1 }
    count: 2
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 1 }
    count: 3
    judgment_distribution: { must-fix: 2, should-fix: 1, leave-as-is: 2 }
---

# レビュー記録：self-improvement requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

5 観点：要件の網羅性／機能名置換／自己適用前提除去／§5.16 系継承方針の反映／検証可能性。

### 観点 1：要件の網羅性

§5.16.1〜§5.16.8 の 8 構成（役割と性格／入力／提案単位／提案構造／検証／承認／履歴ロールバック／効果測定）を Requirement 1〜8 に対応。§5.16.9 スコープ外、§5.16.10 命名と配置、§5.16.11 旧モジュール関係は Change Intent に統合。所見なし。

### 観点 2：機能名置換の正確性

機能名 `self-improvement` 変更なし（§5.16.10）。本文に `dual-reviewer-*` 残存なし。所見なし。

### 観点 3：自己適用前提の除去完全性

素材の自己適用前提（先行プロジェクト固有の運用文脈）を除去済み。ReviewCompass の workflow 改善として再構成。所見なし。

### 観点 4：計画書 §5.16 系の継承方針の反映

- §5.16.1 役割と性格：Requirement 1 で反映 ✓
- §5.16.2 入力：Requirement 2 で反映 ✓
- §5.16.3 提案単位（5 種類）：Requirement 3 で反映 ✓
- §5.16.4 提案構造：Requirement 4 で反映 ✓
- §5.16.5 検証（3 方法）：Requirement 5 で反映 ✓
- §5.16.6 承認：Requirement 6 で反映 ✓
- §5.16.7 履歴とロールバック：Requirement 7 で反映 ✓
- §5.16.8 効果測定 7 指標：Requirement 8 で反映 ✓
- §5.16.9 スコープ外：Boundary Context Out of scope と Change Intent で反映 ✓
- §5.16.11 旧モジュール関係：Change Intent で反映 ✓
- §5.16.12 段階的導入：Boundary Context Out of scope（フェーズ 4 完了後）と Change Intent で反映 ✓

所見なし。

### 観点 5：要件の検証可能性

- **finding_id**：F-001
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 1
- **description**：Requirement 4 受入 1 で `proposal_id` フィールドを必須化するが、命名規約（例：`WP-001` の `WP` プレフィックス）が未指定
- **rationale**：計画書 §5.16.4 の YAML 例で `proposal_id: WP-001` と書かれているが、`WP` プレフィックス（おそらく workflow proposal の略）の意味と命名規約は本仕様内で未定義。検証可能性のため、最低限の命名規約（例：`WP-` プレフィックス、連番）を明示するか、命名規約は design 段で確定する旨を記述
- **evidence_type**：inference

- **finding_id**：F-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 4 と §Requirement 6 受入 5
- **description**：Requirement 4 受入 4 の 4 状態（`pending`／`approved`／`rejected`／`superseded`）と、Requirement 6 受入 5 で扱われる「4 状態（pending／approved／rejected／superseded）」が同一語彙だが、計画書 §5.16.6 では「提案レビュー／承認／却下／採用」と 4 語彙で記述されている
- **rationale**：「提案レビュー」と `pending`、「承認」と `approved`、「却下」と `rejected`、「採用」と `superseded` の対応が不明確。「承認」が `approved` で「採用」が別の概念か、両者は同義かが本仕様内で曖昧。実装時の解釈差異を招く
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "pending|approved|rejected|superseded|提案レビュー|承認|却下|採用" .reviewcompass/specs/self-improvement/requirements.md`
  - `grep -nA 5 "5.16.6" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：F-003
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Boundary Context Out of scope
- **description**：計画書 §5.16.10 で「`learning/findings/`、`learning/backtests/`、`learning/templates/` は他層改善で使うため第 1 期は空、フェーズ 4 完了後に活用」と明示されているが、本仕様の Out of scope に明示されていない
- **rationale**：第 1 期の workflow 改善は `learning/workflow/` のみを使うが、他ディレクトリの取り扱い（第 1 期は空のまま）は読み手にとって有益な情報。Out of scope または運用文書での明示が望ましい
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "learning/findings\|learning/backtests\|learning/templates" .reviewcompass/specs/self-improvement/requirements.md`

### 該当なし観点

なし。

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 1（F-002）、INFO 2（F-001、F-003）、計 3 件
- evidence_type 別：fact 2、inference 1

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

5 観点：F-001／F-002／F-003 への反論検討 ／ 機能内独立発見 ／ 機能横断独立発見。

### F-001 への反論検討

**主役の主張**：`proposal_id` の命名規約（`WP-` プレフィックスと連番の意味）が本仕様内で未定義。

**反論検討**：

計画書 §5.16.4 の YAML 例に `proposal_id: WP-001` の記述があるが、要件文書の役割は「何を保証するか」の定義であり、「どのように命名するか」の細則は設計文書の責務という原則がある。Requirement 4 受入 1 が求めるのは「`proposal_id` フィールドが存在すること」であり、命名規約の粒度を設計段階で確定させる判断は合理的。計画書 §5.16.4 はあくまで例示であって規範的定義ではなく、`WP-` の由来を要件段で強制しなくても検証可能性を大きく損なわない。

**counter_status**：counter_evidence_raised

**counter_rationale**：命名規約の確定粒度は要件段 vs 設計段の責務分担の問題であり、`proposal_id` フィールドの存在と一意性を要件段で求め、命名則を設計段に委ねることは正当。ただし「設計段で確定する旨を明記すること」という主役の条件付き提案については、明示がなければ計画書 YAML 例を規範と誤解するリスクが残る。重大度 INFO は妥当な評価であり、完全な退却とはしない。

---

### F-002 への反論検討

**主役の主張**：計画書 §5.16.6 の「提案レビュー／承認／却下／採用」と本仕様の `pending／approved／rejected／superseded` の対応が不明確。とくに「採用」と `superseded` の関係。

**反論検討**：

計画書 §5.16.6（行 1918）を実確認：「提案レビュー／承認／却下／採用の 4 状態を明示」。一方、本仕様 Requirement 4 受入 4 の 4 値は `pending／approved／rejected／superseded`。

反論として、`superseded` は計画書の 4 語彙にない独自追加の第 5 状態（後続提案に置き換えられた特殊状態）であり、計画書の「採用」= `approved` という解釈で全体が整合する可能性を検討した。しかしその解釈は本仕様内で一切説明されておらず、`approved`（承認）と `superseded`（後続置き換え）のどちらが計画書「採用」に対応するかが実装者依存のままとなる。`superseded` の英語語義（置き換え・廃止）が「採用」と結びつかないことも読み手の混乱要因として実在する。

**counter_status**：no_counter_evidence_after_challenge

**counter_rationale**：`superseded` が計画書 4 語彙のどれに対応するかについて反論を試みたが、本仕様内では決着がつかない。`approved`（承認）と `superseded`（後続置き換え）が「採用」という自然言語に対してどちらが対応するかが不明確であり、実装時の解釈差異リスクは実質的。主役の WARN 評価を維持。

---

### F-003 への反論検討

**主役の主張**：計画書 §5.16.10 の「`learning/findings/`、`learning/backtests/`、`learning/templates/` は第 1 期は空」が本仕様の Out of scope に記載されていない。

**反論検討**：

「運用文書 SELF_IMPROVEMENT.md に同内容が記載されていれば仕様への記載は不要」という分担論を反論候補として検討した。しかし運用文書（`docs/operations/SELF_IMPROVEMENT.md`）§10「後続セッションでの追加予定」に当該情報の記述はなく、仕様・運用文書のいずれにも欠落している。

**counter_status**：no_counter_evidence_after_challenge

**counter_rationale**：仕様文書・運用文書のどちらにも §5.16.10 の「他 3 ディレクトリは第 1 期空置き」情報が存在しないことを確認。主役の事実認定を覆す根拠なし。仕様の内部矛盾ではなく欠落であり、INFO 相当の評価は妥当。

---

### 独立発見（機能内）

- **finding_id**：A-006（機能内）
- **severity**：INFO
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md §Requirement 4 受入 5
- **description**：`statistical_evidence` フィールドは「統計的証拠が可能な場合」に追加するとあるが、「可能な場合」の判断基準が未定義
- **rationale**：パイロット運用初期など `observed_runs` が 0〜2 件しかない段階でも `statistical_evidence` フィールドを省略するか記入するかの判断が実装者依存になる。Requirement 5 受入 2 で「対象データ範囲を提案ごとに明示する」と定めており、遡及シミュレーションの件数（例：過去 17 件）は提案に記録されるが、`statistical_evidence` との記録場所の重複整理も未定義。
- **evidence_type**：inference

### 独立発見（機能横断）

- **finding_id**：A-007
- **severity**：WARN
- **target_location**：.reviewcompass/specs/self-improvement/requirements.md Requirement 1 受入 4 と Boundary Context 隣接期待
- **description**：Requirement 1 受入 4 で `self-improvement` は「規律ファイルの作成・更新・退避・統廃合の責務を持つ」と定め、Boundary Context 隣接期待では `workflow-management` が「規律の昇格・退避・統廃合を所定手続き（drafting → review → approval）に従って実行」するとある。規律ファイルの変更権と手続き実行権が二機能に分散しており、その調停ルール（`self-improvement` が変更を作成し `workflow-management` が手続きを踏む、あるいは `self-improvement` が直接変更するのか）が本仕様内で明示されていない。
- **rationale**：`workflow-management` の requirements.md（Requirement 2 受入 3、Requirement 6 等）は「変更の手続き実行」を担うとしているが、`self-improvement` が「正本所有者」として直接変更する場合に `workflow-management` の手続きをバイパスするケースが発生するかが不明確。フェーズ 4 実装時に矛盾が顕在化するリスクあり。
- **evidence_type**：fact
- **波及範囲**：self-improvement Req 1 受入 4、workflow-management Req 2 受入 3 および Req 6

---

### 敵対役所見集計

- counter_evidence_raised：1 件（F-001）
- no_counter_evidence_after_challenge：2 件（F-002、F-003）
- 独立発見：機能内 1 件（A-006）、機能横断 1 件（A-007）
- 重大度別（独立発見のみ）：CRITICAL 0、ERROR 0、WARN 1（A-007）、INFO 1（A-006）、計 2 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：leave-as-is
- **rationale**：敵対役の反論が正当。要件段の責務は「フィールド存在と一意性を保証する」であり、命名規約の粒度（`WP-` プレフィックスの由来・形式）は設計段で確定するのが責務分担として妥当。Requirement 4 受入 1 に小注記「命名規約は design 段で確定」を付記する軽微な補強は推奨だが、必須ではない。

- **finding_id**：F-002
- **judgment**：must-fix
- **rationale**：敵対役の反論「`superseded` が計画書の 4 語彙のどれに対応するか不明確」は支持。計画書 §5.16.6 の「提案レビュー／承認／却下／採用」と本仕様の `pending`／`approved`／`rejected`／`superseded` の対応が実装者依存のままになるのは重大。特に `superseded`（置き換え・廃止）と「採用」の対応は自然言語的に不整合。Requirement 4 受入 4 に 4 状態の定義と計画書語彙との対応を明示。

- **finding_id**：F-003
- **judgment**：should-fix
- **rationale**：敵対役が確認した通り、仕様・運用文書のいずれにも欠落。第 1 期 scope は `learning/workflow/` のみで、他 3 ディレクトリ（`learning/findings/`／`learning/backtests/`／`learning/templates/`）の取扱い（フェーズ 4 以降活用、第 1 期は空）は読み手にとって有益。Boundary Context Out of scope または運用文書に追加。

- **finding_id**：A-006
- **judgment**：leave-as-is
- **rationale**：敵対役の指摘「`observed_runs` 0〜2 件段階での判断基準が実装者依存」は妥当だが、INFO 相当の軽微性と、パイロット運用初期での実装判断の必然的な柔軟性を勘案すると、要件段で固定することは適切でない。Requirement 5 受入 2 の「対象データ範囲を提案ごとに明示」で `observed_runs` 件数が記録されれば、後段検証時に基準を事後設定する柔軟性が確保される。

- **finding_id**：A-007
- **judgment**：must-fix（wave-level、pending-cross-feature-findings.md に持ち越し済み）
- **rationale**：本所見は既に `.reviewcompass/pending-cross-feature-findings.md` に A-007 として記載済み（敵対役が直接追記）。self-improvement Req 1 受入 4（規律ファイル変更権）と workflow-management Req 2 受入 3／Req 6（手続き実行権）の権限分散が不明確で、機能横断の本質的不整合。個別機能の drafting 段では解決不可、要件 review-wave で両仕様を同時参照して整備する所見として正当。本セッション内で機能内修正は不要。

### 判定役所見集計

- judgment_distribution：must-fix 2 件（F-002 機能内、A-007 機能横断）／should-fix 1 件（F-003 機能内）／leave-as-is 2 件（F-001、A-006）
- 採用所見の重大度別：CRITICAL 0、ERROR 0、WARN 2（F-002、A-007）、INFO 1（F-003）、計 3 件
- 機能内対処（本セッション可能）：2 件（F-002、F-003）
- 機能横断持ち越し：1 件（A-007、既記載済み）
- 不採用：2 件（F-001、A-006）

### 判定の総合所見

主役 3 件のうち 2 件が機能内軽微（INFO×2）と要件内語彙対応不明確（WARN×1）、敵対役独立 2 件のうち 1 件が軽微判断基準未定義（INFO、設計段で対応可）、1 件が機能横断の本質的不整合（WARN）。機能内対処として F-002 の `proposal_state` 語彙対応と F-003 の `learning/` ディレクトリ記載が should-fix〜must-fix で、self-improvement 要件の内部曖昧さを解消する必要。A-007 の規律変更権・手続き実行権の調停ルールは複数機能にまたがる権限設計の根本問題で、要件 review-wave で self-improvement と workflow-management の両仕様を同時参照して整備するのが筋。敵対役の機能横断検知は適切で、pending-cross-feature-findings.md への記載は本来的な carry-forward 対象として妥当。

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 対処範囲 |
|---|---|---|---|---|
| F-002 | WARN | must-fix | requirements.md §Req 4 受入 4 | 機能内 |
| F-003 | INFO | should-fix | requirements.md §Boundary Context Out of scope | 機能内 |
| A-007 | WARN | must-fix | self-improvement Req 1 受入 4 ＋ workflow-management Req 2／6 | **機能横断、既持ち越し済み** |

### 残課題と対処方針

**本セッション内で対処（機能内、2 件）**：

- F-002：Requirement 4 受入 4 に 4 状態（`pending`／`approved`／`rejected`／`superseded`）の定義と計画書 §5.16.6 語彙（提案レビュー／承認／却下／採用）との対応を明示
- F-003：Boundary Context Out of scope に「`learning/findings/`／`learning/backtests/`／`learning/templates/` は第 1 期空置き、フェーズ 4 で他層改善時に活用」を追加

**機能横断持ち越し（既記載済み）**：

- A-007：`.reviewcompass/pending-cross-feature-findings.md` に既追記済み。要件 review-wave で対処

**leave-as-is**：

- F-001（INFO）：要件段の責務範囲として正当
- A-006（INFO）：パイロット運用の柔軟性を尊重

### サブエージェント方式の効果評価（self-improvement、6 機能目）

- **新パターン**：敵対役が直接 pending-cross-feature-findings.md に A-007 を追記（メインセッションを介さず）。ファイル書き込み権限を持つサブエージェントの効率化パターンとして実証
- **§5.16 全面書き直しの検証**：先行プロジェクトの 8 要件から workflow 改善向け 8 要件への再設計を敵対役が機能横断視点（A-007）から検証。再設計の漏れを露出
- **機能横断累積**：A-001／A-003／A-004／A-005／A-007 と 5 件に累積。要件 review-wave での消化対象が拡大
