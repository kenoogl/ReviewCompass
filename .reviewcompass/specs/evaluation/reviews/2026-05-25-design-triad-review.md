---
type: design_triad_review
target: .reviewcompass/specs/evaluation/design.md
target_commit: <未コミット、本セッションで起草された design.md＋must-fix 反映版>
target_baseline_commit: 6ebf9e8
target_content_hash: sha256:2693982fbe0935cc3cd8577e74eb280935e89a5a745fe7b59e99077b67b767fc
date: 2026-05-25
mode: subagent_mediated
session: session-25
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 2, ERROR: 12, WARN: 20, INFO: 4 }
    count: 38
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 5, INFO: 2 }
    count: 10
    counter_distribution: { counter_evidence_raised: 18, no_counter_evidence_after_challenge: 18, not_assessed: 2 }
  judgment:
    by_judgment: { must-fix: 9, should-fix: 20, leave-as-is: 19 }
    by_waterfall: { 機能内対処: 43, 波及: 2, 遡及: 0, 延期: 3 }
    count: 48
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。改訂された §5.9.1（2026-05-25 改訂版、コミット 0e85087）「主役と敵対役は必ず異なる、判定役は同モデル許容、能力配分優先」に整合
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：evaluation 設計 triad-review

本記録は ReviewCompass の evaluation 機能の設計文書（design.md、起草時 686 行→must-fix 9 件反映後 749 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。foundation／runtime の同セッション内 triad-review と同じ流れで実施。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点を網羅実施。38 件の所見（CRITICAL 2／ERROR 12／WARN 20／INFO 4）を提示。

主役所見の主要発見：

- F-008（CRITICAL）：`caveat_register.json` のフィールド定義が存在せず機械実装不可
- F-009（CRITICAL）：`treatment_comparisons.json` と `phase_comparisons.json` のフィールド定義なし
- F-005（ERROR）：`exports/<bundle_id>/run/<run_id>/` サブディレクトリ解決手順未記述
- F-010／F-011／F-014／F-015／F-018／F-019／F-022／F-025／F-028／F-031／F-035（ERROR）：設計の機械実装可能性に関わる欠落多数
- WARN 20 件／INFO 4 件は各観点の精緻化対象

詳細所見は本セッション内のサブエージェント出力を参照。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（38 件）

- 反証提示（counter_evidence_raised）：18 件
- 同意（no_counter_evidence_after_challenge）：18 件
- 未評価（not_assessed）：2 件

主要な反論：

- F-008／F-009（CRITICAL）：両方とも反論成立。foundation／runtime も同じスタイル（design 段で骨格、tasks 段でスキーマ詳細化）。CRITICAL は過剰指摘、先送り論点に明記済み
- F-010／F-014／F-015／F-019／F-028 等：過剰指摘または既出箇所の見落とし

主要な同意：

- F-005／F-011／F-018／F-022／F-025／F-031 など：機械実装可能性に直結する欠落

### 2.2 独立発見（10 件、A-001〜A-010）

- ERROR 4 件：
  - **A-001（ERROR）**：`imports/` 配下に raw bundle 保管先がなく、中央側取り込み後の参照解決手順未定義
  - **A-002（ERROR）**：foundation `counter_status`（3 値正本）がメトリクス対象として未活用、ReviewCompass の中核価値命題（敵対役の有効性測定）に直結する重要欠落
  - **A-003（ERROR）**：`analysis_run_manifest.yaml` に `protocol_version` 入力被覆記録なし、規約版混在検出責務と論理矛盾
  - （4 件目は WARN）
- WARN 5 件：A-004〜A-008 など、入力源曖昧／接合面欠落／非対称構造など
- INFO 2 件：A-009（必須項目集合の根拠未明示）／A-010（先送り論点に各成果物項目最終確定が明示なし）

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（48 件）

#### must-fix（9 件、すべて機能内対処）

| ID | judgment | waterfall_class | 判定根拠 |
|---|---|---|---|
| F-005 | must-fix | 機能内対処 | Mermaid 図と取り込みパス解決手順の不整合 |
| F-011 | must-fix | 機能内対処 | `staleness_register.json` の配置先が成果物配置に未記載 |
| F-018 | must-fix | 機能内対処 | treatment × 段実行マトリクス整合チェック手順未定義 |
| F-022 | must-fix | 機能内対処 | 必須メタデータ欠落時の診断情報出力先未定義 |
| F-025 | must-fix | 機能内対処 | 束のチェックサム整合性検証未記述、外部改ざんリスク |
| F-031 | must-fix | 機能内対処 | 許容判定 3 値の境界入力ケース未定義 |
| A-001 | must-fix | 機能内対処 | 取り込み後の raw bundle 保管先未定義 |
| A-002 | must-fix | 機能内対処 | `counter_status` メトリクス未活用、中核価値命題の測定不能 |
| A-003 | must-fix | 機能内対処 | `protocol_version` 入力被覆記録なし |

注：F-008／F-009（主役 CRITICAL）は判定役が should-fix（延期）に格下げ。理由：敵対役の反論成立、foundation／runtime も design 段で骨格・tasks 段でスキーマ詳細化の方針と整合、先送り論点に明記済み。

#### should-fix（20 件、うち延期 3）

延期：F-008／F-009／F-015（フィールド定義は tasks 段で詰める）
機能内対処（後段で対処）：F-002／F-003／F-010／F-012／F-013／F-017／F-019／F-020／F-023／F-024／F-026／F-032／F-033／F-034／F-037／F-038／A-004／A-005／A-006／A-007／A-010

#### leave-as-is（19 件、修正不要・記録のみ）

F-001／F-004／F-006／F-007／F-014／F-016／F-021／F-027（波及）／F-028／F-029／F-030／F-035／F-036／A-008／A-009 など

### 3.2 判定方針

判定役の方針要約：

> 本機能は design drafting 段であり、骨格（語彙正本所有・成果物配置・分類規則・比較規則・接合面・履行ロジック）の確定が責務。フィールド詳細スキーマや具体閾値は tasks 段で詰める設計フェーズ分担を前提に判定。must-fix の選定軸：(a) 骨格の論理整合崩れ、(b) 要件直接対応の必須手順欠落、(c) 評価ロジック判定可能性崩れ、(d) 中核価値命題に直結する欠落（A-002）、(e) 上流契約との論理矛盾（A-003）に限定。A-002 はフィールド詳細欠如とは別格の must-fix として扱う。

### 3.3 集計

- by_judgment: `{ must-fix: 9, should-fix: 20, leave-as-is: 19 }`（合計 48）
- by_waterfall: `{ 機能内対処: 43, 波及: 2, 遡及: 0, 延期: 3 }`
- count: 48

---

## 4. 統合（integration）

### 4.1 採用所見一覧

#### must-fix（9 件、本セッション内で design.md に反映済み）

| finding_id | severity | judgment | 対処方針 |
|---|---|---|---|
| A-002 | ERROR | must-fix | 所見レベル中核メトリクスに `counter_status` 分布、処理方式レベルに反証発生率指標を追加 |
| A-001／F-005 | ERROR | must-fix | 取り込み束を `imports/bundles/<bundle_id>/run/<run_id>/...` に物理コピー保管、runtime 輸出構造を継承 |
| A-003 | ERROR | must-fix | `analysis_run_manifest.yaml` に `protocol_version_coverage`／`runtime_version_coverage`／`prompt_set_version_coverage` を追加 |
| F-011 | ERROR | must-fix | `manifests/staleness_register.json` を §分析成果物配置に追加 |
| F-018 | ERROR | must-fix | §分類モデル §4 に整合チェック 5 ステップ手順を追記 |
| F-022 | ERROR | must-fix | `classifications/insufficient_metadata_report.json` を新設、5 項目を持つ |
| F-025 | ERROR | must-fix | `checksums/bundle_checksums.json` を取り込み入力に追加、物理コピー前のチェックサム照合手順 |
| F-031 | ERROR | must-fix | §テスト戦略に 7 つの境界入力ケースを列挙 |

実質的な修正対象は次の 4 種類への追記：

1. §メトリクスモデル §3 中核メトリクス層（counter_status 関連）
2. §分析成果物配置 構造図と §配置の根拠（bundles／staleness_register／insufficient_metadata_report 等の追加）
3. §分類モデル §4／§取り込みモデル／§評価準備メタデータ検査（具体手順の追記）
4. §版管理モデル／§テスト戦略（被覆記録・境界ケースの追記）

### 4.1.1 must-fix 対処内容の利用者議論結果（運営ガイド §3.3 (a-1) 準拠）

判定役の判定後、運営ガイド §3.3 (a-1)「must-fix 所見の対処手順（深掘り議論の義務化）」に従い、9 件を 2 議論にまとめて深掘り議論し対処内容を確定。

- **議論 1（A-002）**：1 件単独で深掘り、(ア) 所見レベル counter_status 分布＋処理方式レベル反証発生率指標追加で決着
- **議論 2（A-001／F-005）**：関連 2 件として深掘り、(ア) `imports/bundles/<bundle_id>/run/<run_id>/...` への物理コピー保管で決着
- **議論 3〜8（A-003／F-011／F-018／F-022／F-025／F-031）**：(ウ) 残り 6 件は推奨案でまとめて即時採用（利用者承認「ア」2026-05-25 セッション 25）

途中、利用者から「平易に説明することになっているはず」とのご指摘を受け、技術用語多用を是正して書き直した（議論 2 から）。

**採用された設計原則**（foundation／runtime との連動）：

- 原則 1（contract consumer 徹底）：foundation 6 語彙正本のうち中核価値命題に直結する `counter_status` は中核メトリクスとして活用必須（A-002 の反映）
- 原則 2（構造対称性）：runtime 輸出構造を中央側で同じ階層で受け取る（A-001／F-005 の反映）
- 原則 3（被覆記録）：分析の版管理ファイルは含まれる実行の規約版集合を記録（A-003 の反映）

design.md 行数の変化：起草 686 行 → must-fix 反映 749 行（+63 行）。

**利用者明示承認の出典**：「ア」（議論 1 A-002）「ア」（議論 2 A-001／F-005）「平易に説明することになっているはず」（指摘）「ア」（議論 2 書き直し後）「ウ」（議論進め方）「ア」（残り 6 件即時採用）2026-05-25 セッション 25。本 triad-review に先立ち、運営ガイド §3.3 (a-1) と memory 規律「must-fix 対処の議論義務化」をコミット bdca440 で新設済み。

### 4.2 抽出元との対応

- 抽出元 finding：素材文書 `dual-reviewer-rebuild/.kiro/specs/dual-reviewer-evaluation/design.md`（496 行）と本設計書（749 行）の差分は §変更意図に集約済み
- 新規発見（本 triad-review による）：A-002（counter_status メトリクス未活用）は素材段階から潜在的に存在した欠落だが、本 triad-review で Opus 敵対役が初検出した中核的論点。foundation／runtime で counter_status 正本が確定したことで、評価側で活用すべき必須メトリクスとして浮上

### 4.3 残課題

- must-fix 9 件は本セッション内で design.md に反映済み
- should-fix 20 件（うち延期 3：F-008／F-009／F-015）は本機能の後続段または tasks 段で順次対処
- 波及 2 件（F-014：workflow-management 側の責務／F-027：横断機密方針）は別機能設計時に扱う
- 遡及は発生せず、`.reviewcompass/pending-cross-feature-findings.md` への追記は不要

### 4.4 triad-review 段の完了判定

判定役（Opus 4.7）の総合所見：

> must-fix 9 件はすべて機能内対処（波及・遡及・延期なし）で解消可能。delegated 関係文書の変更を要しないため、本機能の design 段内で再 drafting → 再レビューにより triad-review 段の収束は達成できる。中核価値命題（counter_status メトリクス）の追加は drafting 段で必ず取り込むべきであり、これを欠いたまま tasks 段に進めばスキーマ詳細化が空回りする。総じて、設計骨格は堅実だが中核価値の測定軸 1 点と取り込み配置数点の補強が必要な段階。

本記録に基づき、must-fix 9 件を design.md に反映完了したため、本機能の design.triad-review 段は完了基準を満たすと判定する。

---

## 5. 関連参照

- 設計文書：[.reviewcompass/specs/evaluation/design.md](../design.md)
- 要件文書：[.reviewcompass/specs/evaluation/requirements.md](../requirements.md)
- 素材文書：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/dual-reviewer-evaluation/design.md`（読み取り専用）
- foundation 設計書：[.reviewcompass/specs/foundation/design.md](../../foundation/design.md)
- runtime 設計書：[.reviewcompass/specs/runtime/design.md](../../runtime/design.md)
- foundation／runtime のレビュー記録（セッション 25 同日実施）：
  - [foundation reviews/](../../foundation/reviews/2026-05-25-design-triad-review.md)
  - [runtime reviews/](../../runtime/reviews/2026-05-25-design-triad-review.md)
- モデル配分実験記録：[docs/notes/2026-05-25-triad-review-model-allocation-experiment.md](../../../../docs/notes/2026-05-25-triad-review-model-allocation-experiment.md)
- 計画書 §5.9.1（2026-05-25 改訂版、コミット 0e85087）／§5.17（evaluation 関連）／§5.23.12（サブエージェント方式）
- 運営ガイド §3.3 (a)（機能内対処）／§3.3 (a-1)（must-fix 対処の議論義務化、コミット bdca440 新設）
- レビュー記録雛形：[templates/review/manual_dogfooding_review_template.md](../../../../templates/review/manual_dogfooding_review_template.md)
