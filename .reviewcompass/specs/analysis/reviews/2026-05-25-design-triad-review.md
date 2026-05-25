---
type: design_triad_review
target: .reviewcompass/specs/analysis/design.md
target_commit: <未コミット、本セッションで起草された design.md＋must-fix 反映版>
target_baseline_commit: 49aa7d8
target_content_hash: sha256:bbccea96e2c1d1453a529810277c81d35e5dad973d54f5a3cf63b71168ac60dd
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
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 8, INFO: 3 }
    count: 14
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 5, WARN: 6, INFO: 2 }
    count: 13
    counter_distribution: { counter_evidence_raised: 4, no_counter_evidence_after_challenge: 10, not_assessed: 0 }
  judgment:
    by_judgment: { must-fix: 14, should-fix: 9, leave-as-is: 4 }
    by_waterfall: { 機能内対処: 21, 波及: 2, 遡及: 1, 延期: 3 }
    count: 27
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）、利用者明示承認「ア」2026-05-25 セッション 25 末。改訂された §5.9.1（コミット 0e85087）「主役と敵対役は必ず異なる、判定役は同モデル許容、能力配分優先」に整合
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：analysis 設計 triad-review

本記録は ReviewCompass の analysis 機能の設計文書（design.md、起草時 659 行→must-fix 反映後 776 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。foundation／runtime／evaluation の同セッション内 triad-review と同じ流れで実施。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点（要件全件の網羅／アーキテクチャ整合性／データモデル・スキーマ詳細／API 接合面の具体化／アルゴリズム＋性能達成手段／失敗モード処理＋観測性／セキュリティ・プライバシーの具体化／依存選定／テスト戦略／移行戦略）を網羅実施。14 件の所見（ERROR 3／WARN 8／INFO 3）を提示。

主役所見の主要発見：

- F-006（ERROR）：`conformance-evaluation` 取り込み元パスが「暫定」扱いで 4 フィールドの取得元未確定
- F-009（ERROR）：取り込み段の失敗時報告先成果物が未定義
- F-003（ERROR）：`role_diff.json` の必須／任意属性が未定義
- F-001／F-002／F-004／F-005／F-007／F-010／F-011／F-012（WARN）：各観点の精緻化対象
- F-008／F-013／F-014（INFO）：軽微な改善余地

主役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（14 件）

- 反証提示（counter_evidence_raised）：4 件（F-003／F-005／F-007／F-011）
- 同意（no_counter_evidence_after_challenge）：10 件（F-001／F-002／F-004／F-006／F-008／F-009／F-010／F-012／F-013／F-014）
- 未評価（not_assessed）：0 件

主要な反論：

- F-003：`by_final_label` の「judgment 役のみ」は任意フィールドとして読める、ERROR 評定は過大
- F-005：`eligible_for_standard_comparison` は evaluation 設計に明示済み、「参照不在」ではなく「明示クロスリンク不足」
- F-007：`analysis_run_manifest.yaml.generated_at` で判定可能、WARN 過大で INFO 相当
- F-011：先送り論点に `conformance-evaluation` は登録済み、`workflow-management` も登録すべき

### 2.2 独立発見（13 件、A-001〜A-013）

- ERROR 5 件：
  - **A-001（ERROR）**：`role_diff.json` の出典「`findings_by_method` 由来」が evaluation 設計の接合面に該当ファイル無し、判断 7 と分離規則 1 と矛盾
  - **A-002（ERROR）**：`workflow-management` 設計未確定で `operations_summary.json` が宙吊り、先送り論点に未登録
  - **A-003（ERROR）**：3 役差分の `findings_summary` に `counter_status` 集計が欠落、ReviewCompass の中核価値命題への寄与不足
  - **A-005（ERROR）**：上流機能 5 つの設計確定状態と本機能の最低限必須成果物の関係が分類・見える化されていない
  - **A-009（ERROR）**：混在レビューモード検知の caveat 自動付与ロジック詳細（誰がいつ付与するか）が未定義
- WARN 6 件：A-004（figures_tables/ の第 3 層配置）／A-006（必須／任意属性の体系的不備）／A-007（exploratory／analysis_blocked の caveat_refs 自動付与未定義）／A-008（成熟度集約規則の保守的過剰）／A-010（conformance_intake.json の 2 か所同名配置）／A-011（§下流仕様への影響の節構造不整合）
- INFO 2 件：A-012（先送り論点の確定タイミング整理不足）／A-013（§概要と §変更意図の重複）

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（27 件）

#### must-fix（14 件）

| ID | severity | waterfall_class | 判定根拠 |
|---|---|---|---|
| F-001 | WARN | **波及** | 3 役差分集約の出典が evaluation 接合面 5 ファイルに該当物無し、機械追跡が破綻 |
| F-003 | ERROR | 機能内対処 | 必須／任意属性の未定義は機械検証の前提を欠く |
| F-004 | WARN | 機能内対処 | `fragment_type` の正本値宣言不在で機械検証契約が成立しない |
| F-009 | ERROR | 機能内対処 | 取り込み失敗時の報告先未定義、要件 1 受入 4 の機械的実装根拠不在 |
| F-010 | WARN | 機能内対処 | `regeneration_status` 3 値では永遠の `in_progress` 滞留シナリオ未解消 |
| F-012 | WARN | 機能内対処 | テスト戦略 §3 の `mixed_review_mode` と `limitation_type` 3 値の不整合 |
| A-001 | ERROR | **波及** | F-001 の根本原因、evaluation 設計に 3 役差分集約成果物の新設が必要 |
| A-002 | ERROR | 機能内対処 | `workflow-management` 先送り論点未登録の非対称解消 |
| A-003 | ERROR | 機能内対処 | `counter_status` 集計欠落、中核価値命題の可視化不能 |
| A-006 | WARN | 機能内対処 | 必須／任意属性の体系的明示は JSON 機械検証の前提 |
| A-007 | WARN | 機能内対処 | exploratory／analysis_blocked の caveat_refs 自動付与未定義、要件 3 受入 5 機械検証不能 |
| A-009 | ERROR | 機能内対処 | 混在検知の caveat 自動付与ロジック詳細不在、F-012 と統合 |
| A-010 | WARN | 機能内対処 | conformance_intake.json の 2 か所同名配置は判断 5 と矛盾 |
| A-011 | WARN | 機能内対処 | §下流仕様への影響の節構造矛盾、記述位置の移動で完結 |

#### should-fix（9 件）

| ID | severity | waterfall_class | 判定根拠 |
|---|---|---|---|
| F-002 | WARN | 延期 | `workflow-management` 設計確定後に確定 |
| F-005 | WARN | 機能内対処 | 「明示クロスリンク不足」への絞り込み（敵対役反論採用） |
| F-006 | ERROR | 延期 | `conformance-evaluation` 設計確定後に確定 |
| F-007 | WARN→INFO | 機能内対処 | 敵対役の代替判定方法提示を受け INFO に降格 |
| F-011 | WARN | 機能内対処 | 先送り論点の追記に限定 |
| A-004 | WARN | 機能内対処 | `figures_tables/` の独立配置の根拠を明記 |
| A-005 | WARN | 機能内対処 | ブロッカー対応表として整理 |
| A-008 | WARN | 機能内対処 | 「集約値は保守表示、出典別保持を代替しない」を明示 |
| A-012 | INFO | 機能内対処 | 先送り論点の確定タイミングを表形式に整理 |

#### leave-as-is（4 件）

| ID | severity | waterfall_class | 判定根拠 |
|---|---|---|---|
| F-008 | INFO | 機能内対処 | 設計段は what を固定、how は実装段委ねが運営ガイド §2.1 と整合 |
| F-013 | INFO | 延期 | テストの単体／結合区別はタスク段の責務 |
| F-014 | INFO | 遡及 | 物理移行手順は計画書側の話題、本機能設計の責務外 |
| A-013 | INFO | 機能内対処 | §概要と §変更意図の重複は別目的（読者向け要約と差分明示）として許容 |

### 3.2 severity 再評定（敵対役の反証を踏まえた判定）

- F-003：ERROR 維持（曖昧さを残す解釈は受け入れず）
- F-005：WARN 維持、対処は「クロスリンク追記」に絞る
- **F-007：WARN → INFO 降格**（敵対役の代替判定方法提示を採用）
- F-011：WARN 維持、対処は先送り論点の追記に限定

### 3.3 judgment の分布

- **must-fix：14 件**
- **should-fix：9 件**
- **leave-as-is：4 件**
- 合計：27 件

### 3.4 waterfall_class の分布

- **機能内対処：21 件**
- **波及（evaluation 設計改訂が必要）：2 件**（F-001／A-001、A-011 として `pending-cross-feature-findings.md` に記録）
- **遡及：1 件**（F-014、leave-as-is）
- **延期：3 件**（F-002／F-006／F-013）

---

## 4. 統合（integration）

### 4.1 must-fix 14 件の対処方針と利用者承認の出典

運営ガイド §3.3 (a-1)「must-fix 対処は利用者と議論、深掘り義務」に従い、14 件の must-fix 所見を 3 セット（中核・構造／観測性・整合／細部・整理）11 グループに分けて利用者と深掘り議論を実施。各グループで候補案を列挙、利点・弱点・後段影響を分析し、利用者の明示承認を得てから対処方針を確定。

#### セット 1（中核・構造、3 グループ）

| グループ | 所見 | 採用案 | 利用者承認の出典 |
|---|---|---|---|
| 1 | A-001＋F-001 | 候補案 A（evaluation 設計に 3 役差分集約成果物 `roles/role_diff_report.json` を新設、波及対処） | 「(ア)」（候補案 A 採用）2026-05-25 |
| 2 | A-003 | 候補案 A（`role_diff.json` の `findings_summary` に `by_counter_status` を追加、グループ 1 と統合対処） | 「(ア)」2026-05-25 |
| 3 | F-003＋A-006 | 候補案 B（脚注形式で必須／任意属性を明示、軽量化案） | 「(イ)」2026-05-25 |

#### セット 2（観測性・整合、3 グループ）

| グループ | 所見 | 採用案 | 利用者承認の出典 |
|---|---|---|---|
| 4 | F-009 | 候補案 A（`shared/manifests/intake_failure_report.json` を新設） | 「(ア)」2026-05-25 |
| 5 | F-010 | 候補案 A（`regeneration_status` を 4 値拡張、`failed` 追加）＋補助論点 (a)（`regeneration_failure_reason` を任意フィールド追加） | 「(ア)」2026-05-25 |
| 6 | F-012＋A-009 | 候補案 A'（`limitation_type` を 4 値拡張、`mixed_review_mode` 追加、検知主体は派生段、過渡的対処の位置付け明記、先送り論点に再評価条項追加） | 「(ア')」2026-05-25（利用者の深掘り質問「混在レビューモードは現時点・システム稼働前のみの事象では？」を経て過渡的対処の位置付けを明示） |

#### セット 3（細部・整理、5 グループ）

| グループ | 所見 | 採用案 | 利用者承認の出典 |
|---|---|---|---|
| 7 | F-004 | 候補案 A（`fragment_type` 5 値正本宣言） | 「(ア)」2026-05-25（一括承認） |
| 8 | A-002 | 候補案 A（先送り論点に `workflow-management` を追記） | 「(ア)」2026-05-25 |
| 9 | A-007 | 候補案 A（束縛規則表の脚注に `caveat_refs` 自動付与規律を追記） | 「(ア)」2026-05-25 |
| 10 | A-010 | 候補案 A（`shared/conformance/conformance_intake.json` を正本化、`destinations/<出力先>/` を別名加工版 `conformance_violations_detail.json` と `conformance_compliance_trend.json` に） | 「(ア)」2026-05-25 |
| 11 | A-011 | 候補案 A（`workflow-management` 記述を §上流機能との接合面に移動） | 「(ア)」2026-05-25 |

### 4.2 反映箇所一覧（design.md、9 件の機能内対処）

| グループ | 反映先 | 修正規模 |
|---|---|---|
| 3 | 9 モデル節の末尾に「必須／任意の区分」脚注追加（主張対応図／証拠台帳／注意点台帳／図表束（表・図）／報告断片／3 役差分／3 経路差分／派生 manifest／conformance_intake／陳腐化登録／取り込み失敗報告） | 12 箇所、約 30 行追加 |
| 4 | §取り込み失敗のモデル新節、§分析向け成果物配置の図に `intake_failure_report.json` 追加 | 約 25 行追加 |
| 5 | §陳腐化伝播の継承 §3 の `regeneration_status` 4 値拡張、`regeneration_failure_reason` 追加 | 約 5 行追加 |
| 6 | §注意点と限界のモデル（`limitation_type` 4 値拡張、過渡的対処の位置付け明記）、§証拠台帳モデル §3（検知主体・evaluation 側との粒度分担・過渡的対処の明示）、§先送り論点（再評価条項） | 約 25 行追加 |
| 7 | §報告断片モデルの `fragment_type` を正本値として確定 | 1 行修正 |
| 8 | §先送り論点に `workflow-management` 関連 1 行追記 | 1 行追加 |
| 9 | §証拠台帳モデル §1 束縛規則表の脚注（「安定比較集合」のクロスリンク・自動付与規律） | 約 8 行追加 |
| 10 | §分析向け成果物配置（ディレクトリ図）、§出力先別の派生モデル §4・§5、§conformance-evaluation メトリクス取り込みモデル §2・§3、§テスト戦略 §5 | 約 15 行修正 |
| 11 | §下流仕様への影響から `workflow-management` 削除、§上流機能との接合面の `workflow-management` と `conformance-evaluation` に上流側設計への期待を統合 | 約 7 行修正 |

合計：design.md 約 117 行の追加・修正（659 行 → 776 行）

### 4.3 波及所見の処理（A-011 として記録）

A-001 と F-001 は判定役が **波及** と判定したため、運営ガイド §3.2 (b) に従い `pending-cross-feature-findings.md` に **A-011** として追記済み。design レビュー波段（残り 3 機能（workflow-management／self-improvement／conformance-evaluation）の drafting＋triad-review 完了後）で `evaluation` 設計と analysis 設計を同時に修正する予定。

- evaluation 設計改訂：§分析成果物配置に `roles/role_diff_report.json` を追加、§下流接合面に `roles/role_diff_report.json` を追加、3 役所見差分報告の最低限の構造化形式項目を定義
- analysis 設計改訂：§レビュー収束過程の可視化モデル §1 の出典記述を `experiments/analysis/roles/role_diff_report.json` 由来に書き換え、§上流機能との接合面（`evaluation` との接合面）の読み取りファイル一覧に追加

連動所見：A-003（`counter_status` 集計）は A-011 の対処時に `role_diff_report.json` の構造に `by_counter_status` を含める形で同時反映する旨を pending エントリに記録。

### 4.4 過渡的対処として位置付けた事項（A-009／F-012 関連）

`limitation_type=mixed_review_mode` は要件 6 受入 4 由来の自動検知種別として 4 値正本に追加したが、本値は過渡期・移行時・配置先テストケースで発生する混在状態への対処であり、恒久運用の中核仕様ではない。フェーズ 4 完了後の運用次第で再評価する条項を §先送り論点に登録（利用者の深掘り指摘「混在レビューモードは現時点・システム稼働前のみの事象では？」を反映、過渡的対処の位置付けを設計内に明記）。

### 4.5 関連参照

- 運営ガイド §3.3 (a-1) must-fix 所見の対処手順（深掘り議論の義務化）
- pending-cross-feature-findings.md §A-011（本セッションで追記、design レビュー波段で消化予定）
- 計画書 §5.9.1（モデル能力配分規律、改訂後既定との整合）
- 計画書 §5.9.2（観点 ＋ 重大度の統一）
- 計画書 §5.9.3（所見メタデータの必須化と機械検査）
- 計画書 §5.23.12（サブエージェント方式）
- analysis 要件文書（Req 1〜8 の充足対応は design.md §要件と設計の対応参照）

### 4.6 主役の集計不整合の事後検証

主役（Sonnet 4.6）が自己申告した WARN「7 件」と所見列挙の WARN「8 件」に不整合があった（列挙：F-001／F-002／F-004／F-005／F-007／F-010／F-011／F-012）。判定役レビューでは列挙の WARN 8 件を採用、F-007 を WARN → INFO に降格した結果、最終的な severity 分布は ERROR 3／WARN 7／INFO 4 となる。本記録の `findings_by_method.primary.by_severity` には主役所見の集計を主役発表時のスナップショット（WARN 8）として記載し、判定役による再評定後の値とは区別する。
