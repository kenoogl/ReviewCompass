---
type: requirements_local_review
target: .reviewcompass/specs/analysis/requirements.md
target_commit: <未コミット、本セッション内作業>
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
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 2, INFO: 1 }
    count: 3
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 4, INFO: 0 }
    count: 4
    judgment_distribution: { must-fix: 2, should-fix: 2, leave-as-is: 2 }
---

# レビュー記録：analysis requirements.md

## 1. 主役レビュー（primary、Opus 4.7、メインセッション）

5 観点：要件の網羅性／機能名置換／自己適用前提除去／§5.14 系継承方針の反映／検証可能性。

### 観点 1：要件の網羅性

抽出元 Req 1-6（6 件）すべて存在、加えて **Requirement 7（レビュー収束過程の可視化、§5.14.5 由来、新規）と Requirement 8（4 種の出力先への変換、§5.14.4 由来、新規）を追加**。Boundary Context 隣接期待は 3 → 4（`workflow-management` 追加）、Out of scope に `conformance-evaluation` を追加。所見なし。

### 観点 2：機能名置換の正確性

`paper-interface` → `analysis` 改称が反映済み。本文に `paper-interface` 残存なし（Change Intent と運用文書の歴史的記述のみ）。所見なし。

### 観点 3：自己適用前提の除去完全性

grep 結果ほぼ 0 件（運用文書の改称説明は許容）。所見なし。

### 観点 4：計画書 §5.14 系の継承方針の反映

- §5.14.4 4 出力先：Requirement 8 で新設 ✓
- §5.14.5 レビュー収束過程の可視化：Requirement 7 で新設 ✓
- §5.14.6 主要な発見：design.md 抽出時の課題として持ち越し
- §5.18.13 レビューモード 3 値体制：Requirement 6 で反映 ✓
- A-001／A-003 との連動：Requirement 2 受入 6 で陳腐化伝播、Requirement 5 受入 6 で `evidence_class` 語彙参照 ✓

所見なし。

### 観点 5：要件の検証可能性

- **finding_id**：F-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Requirement 7 受入 2／受入 3
- **description**：Requirement 7（レビュー収束過程の可視化）の受入 2／受入 3 が「`findings_by_method` の差分を保持し可視化に渡す」と規定するが、具体的な構造（差分の表現形式、可視化に渡す入力スキーマ）が未定義
- **rationale**：本機能は新規追加要件で、`evaluation` から受け取った 3 役・3 経路の所見差分をどのように可視化用に整理するかの構造が決まらないと、`evaluation` 側との契約が成立しない。requirements レベルで「最低限の構造体（例：機能名 + 役名 + 経路名 + 所見集計）を持つ」程度の表現が必要
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "findings_by_method|レビュー収束" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/analysis/requirements.md`

- **finding_id**：F-002
- **severity**：WARN
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Requirement 8 受入 1
- **description**：Requirement 8 受入 1 が「最低限、運用ダッシュボード、週次レポート、監査用報告、論文向け原データの 4 種」と列挙するが、各出力先の最低限の必須内容（例：監査用報告は無効化マーカー一覧を含む等）が未指定
- **rationale**：「支える」だけでは検証可能性が薄い。各出力先で何が「最低限含まれるべきか」を一文ずつ明示することで、design 段階の責務範囲が明確になる
- **evidence_type**：inference

- **finding_id**：F-003
- **severity**：INFO
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Boundary Context 隣接仕様の期待
- **description**：「`runtime` には原則として `evaluation` を経由してアクセスし、直接アクセスしない」が Requirement 4 受入 1 で機能内に反映されているが、Boundary Context の隣接期待では `runtime` が記述されていない
- **rationale**：他機能（foundation／evaluation／self-improvement／workflow-management）は隣接期待に明示されているのに、`runtime` だけが Requirement 4 受入 1 の表現にとどまる。読み手の構造把握のため、隣接期待にも一行追加が望ましい
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "runtime|隣接仕様" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/analysis/requirements.md`

### 該当なし観点

なし。

### 主役所見集計

- 重大度別：CRITICAL 0、ERROR 0、WARN 2（F-001、F-002）、INFO 1（F-003）、計 3 件
- evidence_type 別：fact 2、inference 1

---

## 2. 敵対役レビュー（adversarial、Sonnet 4.6、サブエージェント）

注：敵対役が "partial_agreement" 等の標準語彙外の counter_status を使用したため、メインセッションが §5.4 標準 3 値（`counter_evidence_raised`／`no_counter_evidence_after_challenge`／`not_assessed`）に整理して記録する。

### 主役所見への反論検討

- **対象 finding_id**：F-001
- **counter_status**：`counter_evidence_raised`（部分的反証：重大度の議論）
- **counter_rationale**：「構造体の最低限定義が requirements レベルで必要」という主張は、requirements と design の責務境界を混同している可能性。計画書 §5.14.5 は可視化対象（所見の減少カーブ・Sankey 図等）と可視化形式を detail レベルで記述しており、その詳細設計は design.md で扱うべき事項。一方、Requirement 7 受入 1 に「構造化入力を定義する」と明記されており、最低限の検証可能性は担保されている。WARN を INFO に格下げする論拠あり。

- **対象 finding_id**：F-002
- **counter_status**：`no_counter_evidence_after_challenge`（部分的同意：主役指摘は残る価値あり）
- **counter_rationale**：計画書 §5.14.4 は 4 出力先ごとに具体的な成果物名や情報種別を明示しているが、仕様文書単体での自己完結性という観点では、出力先ごとに最低限の必須成果物が 1 行でも列挙されていると検証可能性が増すという主役の指摘は否定できない。運用文書 ANALYSIS.md §4 には 4 出力先の概要が記載されているが、形式仕様 requirements.md 内には存在しないというギャップは事実。WARN として残す価値はある。

- **対象 finding_id**：F-003
- **counter_status**：`counter_evidence_raised`（完全反証）
- **counter_rationale**：requirements.md 行 32 の隣接仕様の期待には「`runtime` には原則として `evaluation` を経由してアクセスし、直接アクセスしない（Requirement 4 受入 1 と整合）」と明示されている。**メインセッションの事前検証で確認済み**。F-003 は事実誤認に近い。INFO ではなく leave-as-is が適切。

### 独立発見

#### 機能内所見

- **finding_id**：B-001
- **severity**：WARN
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Boundary Context Out of scope と §Requirement 1〜8
- **description**：仕様文書は `conformance-evaluation` を Out of scope（適合性評価の責務外）と明記するが、計画書 §5.14.3 カテゴリ 5（行 1568）と行 2146 で「analysis → conformance-evaluation を read（メトリクス取り込み）」が確定方向として明示されており、`conformance-evaluation` からの入力契約が Requirement 1〜8 のいずれにも着地していない
- **rationale**：Out of scope の記載は「`analysis` が conformance-evaluation の判定作業を行わない」という責務境界として正当だが、計画書 §5.14.8 の依存記述 `conformance-evaluation: review` と §5.14.3 カテゴリ 5 の「conformance-evaluation メトリクスを取り込む」という入力契約は、Requirement 8 または Requirement 2 に着地すべき。**メインセッションの事前検証で正当性確認済み**
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -n "conformance" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/analysis/requirements.md`
  - `grep -n "カテゴリ 5\|analysis.*conformance" /Users/Daily/Development/ReviewCompass/docs/plan/reconstruction-plan-2026-05-21.md`

- **finding_id**：B-002
- **severity**：INFO
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Requirement 7 受入 2〜3
- **description**：Requirement 7 受入 2 で「3 役（`primary`／`adversarial`／`judgment`）の所見出力の差分（`findings_by_method` 由来）」、受入 3 で「3 経路（`manual_dogfooding`／`subagent_mediated`／`runtime_mediated`）の所見出力の差分」と書いており、役・方式・経路の 3 つの軸が混在して読める懸念
- **rationale**：計画書 §5.9.6 行 857「方式名は役名と一致」と明示。役と方式は同名で同概念として扱われており、Sonnet の前提（独立 3 軸）は誤り。ただし「3 役」と「3 経路（レビューモード）」は確かに別軸で、受入 2 と受入 3 は適切に区別されている。表現の明確化余地はあるが本質的不備ではない。**メインセッションの事前検証で Sonnet の前提が弱いことを確認**
- **evidence_type**：inference

#### 機能横断波及所見（持ち越し対象として記録）

- **finding_id**：A-004
- **severity**：WARN
- **target_location**：.reviewcompass/specs/analysis/requirements.md §Requirement 7 受入 3 ＋ `.reviewcompass/specs/evaluation/requirements.md`
- **description**：Requirement 7 受入 3「3 経路の所見出力の差分を保持し可視化に渡す」が、`evaluation` 側に対応する出力責務（経路別差分の出力）を要求するが、evaluation requirements.md には対応する受入基準が存在しない
- **rationale**：analysis は「消費するが支配しない」原則で、evaluation の出力を消費する。Requirement 7 受入 3 が成立するには、evaluation 側がレビューモード別差分の出力を行う受入基準を持つ必要がある。**メインセッションの事前検証で evaluation requirements.md に該当受入基準がないことを確認**。機能横断の不整合
- **波及範囲**：
  - evaluation：Requirement 4 または Requirement 9 付近に「3 経路（レビューモード）別の所見差分を analysis 向け出力として提供する」受入基準を追加
- **evidence_type**：fact
- **verifying_commands**：
  - `grep -nE "経路.*差分|レビューモード.*差分|by_review_mode" /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/evaluation/requirements.md`

### 敵対役所見集計

- 主役所見への反論：counter_evidence_raised 2 件（F-001 部分／F-003 完全）／no_counter_evidence_after_challenge 1 件（F-002 部分同意）／not_assessed 0 件
- 独立発見の重大度別：機能内 WARN 1（B-001）、機能内 INFO 1（B-002）、機能横断 WARN 1（A-004）、計 3 件

---

## 3. 判定役レビュー（judgment、Haiku 4.5、サブエージェント）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：should-fix
- **rationale**：「最低限の構造化入力定義が requirements レベルで必要」という主役指摘は妥当。Requirement 7 受入 1 で「構造化入力を定義する」と明記されながら、受入 2／3 で最低限のスキーマが不明確なのは検証可能性を損なう。敵対役の「WARN → INFO 格下げ」提案は受け入れず、should-fix。要件側で「機能名・役名・経路・集計値」最低限の構造体記載が有益。

- **finding_id**：F-002
- **judgment**：should-fix
- **rationale**：敵対役が部分同意。運用文書 ANALYSIS.md §4 に 4 出力先の概要はあるが、形式仕様内には具体的な必須成果物が列挙されていない事実は確認。Requirement 8 受入 1 で「監査用報告は無効化マーカー一覧を含む」等の最低限の列挙があれば、design の責務範囲が明確になる。

- **finding_id**：F-003
- **judgment**：leave-as-is
- **rationale**：敵対役の完全反証が正当。requirements.md 行 32 の隣接仕様の期待に runtime の記述が既に明示されている。メインセッション事前検証で正当性確認済み。F-003 は事実誤認に近い主役の観察ミス。

- **finding_id**：B-001
- **judgment**：must-fix
- **rationale**：計画書 §5.14.3（行 1568）と §5.14.8 で「analysis → conformance-evaluation を read（メトリクス取り込み）」が明示されているが、Requirement 1〜8 のいずれにも着地していない。Out of scope 記載は「適合性評価の責務外」という正当な責務境界だが、入力契約（どのメトリクスを、どこから受け取るか）は仕様に明記すべき。Requirement 2 または Requirement 8 に追加。

- **finding_id**：B-002
- **judgment**：leave-as-is
- **rationale**：敵対役は「独立 3 軸」と主張したが、計画書 §5.9.6 行 857「方式名は役名と一致」と明示。役と方式は同名同概念。受入 2（3 役）と受入 3（3 経路）は実際には適切に区別されている。敵対役の前提が誤り。表現の明確化余地はあるが本質的不備でなし。

- **finding_id**：A-004
- **judgment**：must-fix（pending-cross-feature-findings.md に持ち越し）
- **rationale**：Requirement 7 受入 3 が機能内成立には、evaluation 側が「経路別差分出力」を行う受入基準を持つ必要があるが、evaluation requirements.md に該当受入基準がない。機能横断の不整合で本セッション内修正対象ではない。要件 review-wave／alignment-gate で evaluation 側を修正。

### 判定役所見集計

- judgment_distribution：must-fix 2 件（B-001 機能内、A-004 機能横断）／should-fix 2 件（F-001、F-002）／leave-as-is 2 件（F-003、B-002）
- 採用所見の重大度別（must-fix ＋ should-fix）：CRITICAL 0、ERROR 0、WARN 4（F-001、F-002、B-001、A-004）、INFO 0、計 4 件
- 機能内対処（本セッション可能）：3 件（F-001、F-002、B-001）
- 機能横断持ち越し（pending-cross-feature-findings.md）：1 件（A-004）
- 不採用：2 件（F-003、B-002）

### 判定の総合所見

本機能の requirements 仕様の完成度は高く、3 件の主役指摘のうち F-003 は事実誤認で leave-as-is、F-001／F-002 は検証可能性の微調整レベルで should-fix。敵対役の 3 件独立発見も、本質的欠陥というより機能内表現明確化（B-002）または隣接機能との整合不備（B-001、A-004）。

B-001 の `conformance-evaluation` メトリクス取り込み契約は、requirements レベルで着地が必要な重要事項。計画書 §5.14.3 と §5.14.8 に明記された依存関係が仕様に反映されていない。A-004 の evaluation 側受入基準欠落は、機能横断 alignment-gate で evaluation 修正で解決。これら 2 件（B-001 must-fix、A-004 持ち越し）が品質改善の中心。

サブエージェント方式のレビューでは、4 機能目の実証として **A-004（機能横断波及）が新たに発見**された。pending-cross-feature-findings.md には A-001（`not_run`）／A-003（`analysis_blocked`）／A-004（経路別差分出力）の 3 件が集約。要件 review-wave 着手時の消化対象が累積。

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 対処範囲 |
|---|---|---|---|---|
| F-001 | WARN | should-fix | requirements.md §Req 7 受入 2／3 | 機能内 |
| F-002 | WARN | should-fix | requirements.md §Req 8 受入 1 | 機能内 |
| B-001 | WARN | must-fix | requirements.md §Req 2 または §Req 8 | 機能内 |
| A-004 | WARN | must-fix | requirements.md §Req 7 受入 3 ＋ evaluation 仕様 | **機能横断波及、持ち越し** |

### 残課題と本セッションでの対処方針

**本セッション内で対処すべき（機能内、利用者承認後実施）**：

- F-001：Requirement 7 受入 2／3 に最低限の構造化入力スキーマを追記（例：機能名・役名・経路名・集計値）
- F-002：Requirement 8 受入 1 に各出力先の最低限必須成果物を 1 行ずつ列挙
- B-001：Requirement 2 または Requirement 8 に「conformance-evaluation メトリクスの取り込み」受入基準を追加（§5.14.3 カテゴリ 5 由来）

**機能横断レビューに持ち越し**：

- A-004：`.reviewcompass/pending-cross-feature-findings.md` に追記、要件 review-wave／alignment-gate で対処。evaluation 仕様に「3 経路別の所見差分を analysis 向け出力として提供」受入基準を追加

**leave-as-is**：

- F-003（INFO）：実際は隣接期待に runtime 記述あり、事実誤認
- B-002（INFO）：方式と役は同名同概念のため Sonnet の前提が弱い

### サブエージェント方式の効果評価（analysis レビュー観察、4 機能目）

- **計画書との整合確認**：敵対役が計画書 §5.14.3 カテゴリ 5 ／ §5.14.8 ／ §5.9.6 を参照し、仕様文書との乖離を 3 件発見（B-001、B-002 は前提弱、A-004）
- **事実誤認の発見**：F-003 で敵対役が「実は記述あり」を指摘し、主役の観察ミスを是正。サブエージェント方式の独立視点が誤発見も検出
- **機能横断累積**：A-001／A-003／A-004 と 3 件に累積。要件 review-wave での一括消化対象

---

