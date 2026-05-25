---
type: design_triad_review
target: .reviewcompass/specs/runtime/design.md
target_commit: <未コミット、本セッションで起草された design.md＋must-fix 反映版>
target_baseline_commit: 7ee63e0
target_content_hash: sha256:84b1c897814cf912a32d1b2d7eea4b254371c1bcf6a3160491b5ccc3178a5fc5
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
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 17, INFO: 5 }
    count: 26
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 2, WARN: 8, INFO: 3 }
    count: 13
    counter_distribution: { counter_evidence_raised: 6, no_counter_evidence_after_challenge: 20, not_assessed: 0 }
  judgment:
    by_judgment: { must-fix: 3, should-fix: 17, leave-as-is: 19 }
    by_waterfall: { 機能内対処: 31, 波及: 0, 遡及: 0, 延期: 8 }
    count: 39
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）を採用。改訂された計画書 §5.9.1（2026-05-25 改訂）「主役と敵対役は必ず異なるモデル、判定役は同モデル許容、能力配分優先」に整合
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
---

# レビュー記録：runtime 設計 triad-review

本記録は ReviewCompass の runtime 機能の設計文書（design.md、起草時 704 行→must-fix 反映後 725 行）に対する 3 役レビューの結果である。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）を採用。本セッションで実施した計画書 §5.9.1 包括改訂（旧規律「同モデル使用は禁止」を撤回、「主役と敵対役は必ず異なる、判定役は同モデル許容、能力配分優先」に改訂）に基づく初の triad-review。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点を網羅実施。26 件の所見（CRITICAL 0／ERROR 4／WARN 17／INFO 5）を提示。

### 主役所見一覧（26 件、F-001〜F-026）

| ID | 観点 | severity | target_location | description |
|---|---|---|---|---|
| F-001 | 1：要件全件の網羅 | ERROR | §セッションモデル §3 行 222 | `evidence_class` 4 値目を `analysis_modified` と誤記（正本は `analysis_blocked`） |
| F-002 | 1：要件全件の網羅 | ERROR | §下流接合面 行 603-605 | workflow-management 接合面の成果物リストが他機能と不統一 |
| F-003 | 1：要件全件の網羅 | WARN | §Step A 行 246-260 | Step A 出力に foundation §5 段別再演識別子（step_status 等）が明示なし |
| F-004 | 1：要件全件の網羅 | WARN | §要件追跡表 | 要件 6 受入 4・5 への個別対応が追跡表に記載なし |
| F-005 | 2：アーキテクチャ整合性 | WARN | §全体構造 Mermaid | アーキテクチャ図に workflow-management 接続なし |
| F-006 | 2：アーキテクチャ整合性 | WARN | §配置の運用ルール | `review_case.json` の不変性と二段階更新の境界曖昧 |
| F-007 | 3：データモデル・スキーマ詳細 | ERROR | §証拠出力モデル 行 431-433 | `review_case.json` の必須フィールド投影規約が義務宣言のみで具体的対応表が欠落 |
| F-008 | 3：データモデル・スキーマ詳細 | WARN | §決定単位モデル | `decision_units.json` の `human_decision` フィールド許容値語彙が未定義 |
| F-009 | 3：データモデル・スキーマ詳細 | WARN | §実行成果物配置 | `comparison_eligibility_note.json` の最小フィールド仕様が欠落 |
| F-010 | 3：データモデル・スキーマ詳細 | WARN | §実行成果物配置・不変性担保 | 凍結マーカーが `closed_at` のみ、独立 freeze marker artifact／observable が未定義 |
| F-011 | 4：API 接合面の具体化 | ERROR | §プロンプト解決モデル | プロンプト上書きパスの具体形式が未定義 |
| F-012 | 4：API 接合面の具体化 | WARN | §下流接合面 evaluation | `review_case.json` の何を読むかフィールド粒度未定義 |
| F-013 | 4：API 接合面の具体化 | INFO | §下流接合面 self-improvement | `failure_observation` 発見方式未定義 |
| F-014 | 5：アルゴリズム＋性能達成手段 | WARN | §Step D 統合手順 ステップ 4 | 「規定の既定規則」が未定義 |
| F-015 | 5：アルゴリズム＋性能達成手段 | WARN | §セッションモデル | 「運用者が明示的に探索実行と宣言」の宣言手段未定義 |
| F-016 | 6：失敗モード処理＋観測性 | ERROR | §セッションモデル §3 行 222 | F-001 と同根（blocked → analysis_modified 伝播誤り） |
| F-017 | 6：失敗モード処理＋観測性 | WARN | §実行終了境界 | 「前提条件違反や多重起動の検知」の手段未定義 |
| F-018 | 6：失敗モード処理＋観測性 | INFO | §無効化処理 | `review_case.json` への参照更新タイミング未定義 |
| F-019 | 7：セキュリティ・プライバシー | WARN | §可搬証拠束輸出 | 機密／サニタイズ／プライバシー方針なし |
| F-020 | 7：セキュリティ・プライバシー | INFO | §可搬証拠束輸出 | 輸出実行者の認可制御未定義 |
| F-021 | 8：依存選定 | WARN | §実行成果物配置・セッションモデル | YAML／JSON 混在の選定理由未記述 |
| F-022 | 8：依存選定 | INFO | §セッションモデル | `subagent_mediated` 経路での runtime 挙動が未定義 |
| F-023 | 9：テスト戦略 | WARN | §テスト戦略 | observable 形式・保管先が未定義 |
| F-024 | 9：テスト戦略 | INFO | §テスト戦略 | `evidence_class` 確定遷移ロジックのテスト方針なし |
| F-025 | 10：移行戦略 | WARN | §変更意図 | `failure_observation` 単一→複数ファイル化の理由未記述 |
| F-026 | 10：移行戦略 | INFO | §変更意図 | 素材の `v2/` 採用見送りの明示説明なし |

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（26 件）

主要なポイント：

- **反証提示（counter_evidence_raised）**：6 件（F-002／F-004／F-006／F-016／F-021／F-025）
- **同意（no_counter_evidence_after_challenge）**：20 件
- **未評価（not_assessed）**：0 件

特に F-016 は F-001 と同根の問題として「別 ID として独立判定する意義が薄い、F-001 修正で同時解消」と反証。F-021（YAML／JSON 選定理由）は「foundation 慣習の踏襲、説明不要」と反証。

### 2.2 独立発見（13 件、A-001〜A-013）

| ID | severity | target_location | description |
|---|---|---|---|
| A-001 | ERROR | §証拠出力モデル／foundation §5／§段実行マトリクス | foundation `step_status` と runtime `step_outcome` の関係未統合、`review_case.step_records[]` のスキーマが機械決定不能 |
| A-002 | ERROR | §セッションモデル 行 220-223 | `evidence_class` 確定遷移が `rejected`／`deferred` 終了をカバーせず、機械判定で網羅性ギャップ |
| A-003 | WARN | §セッションモデル／§検証器結果 | foundation 由来語彙の重複列挙、契約 consumer 原則の精神に反する |
| A-004 | WARN | §セッションモデル | `schema_set_version`／`prompt_set_version` の決定方法が両設計書から読み取れない |
| A-005 | WARN | §決定単位モデル／foundation §4 finding | finding 必須項目 `decision_unit_id` と Step D 後付け生成の時系列矛盾 |
| A-006 | WARN | §セッションモデル | `run_status=closed` 直後の極短時間で `evidence_class` がどの値を取るか未定義 |
| A-007 | WARN | §責務境界 | foundation との責務境界記述で重複・冗長 |
| A-008 | INFO | §テスト戦略 | 実装言語未確定段階で pytest／rspec 等を例示するのは早すぎる |
| A-009 | INFO | §配置の運用ルール／§可搬証拠束輸出 | 「別機能」が evaluation か workflow-management か analysis か明示なし |
| A-010 | WARN | §フェーズ対応レビュープロファイル | `phase_profile` 強調点の物理配置が未定義 |
| A-011 | WARN | §セッションモデル／§人間署名記録 | operator identity の形式・型が未定義 |
| A-012 | INFO | §プロンプト解決モデル／§Step D | Step D 機械的決定論性の形式仕様レベルの保証なし |
| A-013 | WARN | §下流接合面 conformance-evaluation | conformance-evaluation 接合面が薄く、責務分離曖昧 |

**Opus 敵対役の重要な独自発見**：

- A-001（foundation `step_status` と runtime `step_outcome` の関係未統合）は両設計書を跨ぐ構造的論点
- A-002（`evidence_class` 確定遷移の網羅性ギャップ）は machine 判定で重大ギャップ
- A-005（finding 必須項目と Step D 後付け生成の時系列矛盾）は foundation との連携が必要な可能性のある構造的論点

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（39 件）

#### must-fix（3 件、すべて機能内対処）

| ID | judgment | waterfall_class | 判定根拠 |
|---|---|---|---|
| F-001 | must-fix | 機能内対処 | `analysis_blocked` 正本との明白な誤記、foundation 語彙正本参照禁止違反 |
| A-001 | must-fix | 機能内対処 | foundation `step_status` と runtime `step_outcome` の関係未統合、`review_case.step_records[]` のスキーマが機械決定不能 |
| A-002 | must-fix | 機能内対処 | `evidence_class` 確定遷移が `rejected`／`deferred` 終了をカバーせず、機械判定で網羅性ギャップ |

注：F-016 は F-001 と同根のため、判定本文で leave-as-is（F-001 修正で同時解消）と判定された。集計では must-fix 4 件と記録されているが、本文判定を優先する。

#### should-fix（17 件）

F-003／F-005／F-007／F-008／F-009／F-010／F-011／F-012／F-014／F-015／F-017／F-019／F-023／A-004／A-005／A-009／A-010／A-011／A-013（19 件、判定本文）。集計の 17 件と差異あり、本文を優先。

#### leave-as-is（19 件）

F-002／F-004／F-006／F-013／F-016／F-018／F-020／F-021／F-022／F-024／F-025／F-026／A-003／A-006／A-007／A-008／A-012

### 3.2 判定方針

判定役の方針（300 字程度の要約）：

> must-fix は「foundation 契約に直接違反する誤記」「機械判定で網羅性が破綻する欠落」のみに限定。F-001／A-001／A-002 がこれに該当する。機能内対処と波及／遡及／延期の振り分けは、foundation 既定済の語彙正本に対する違反は本機能修正で済むため機能内対処、foundation の必須項目宣言と runtime の時系列が矛盾する論点（A-005）は本機能で時系列補強を試み、解決不能なら波及／遡及を検討する。過剰修正偏りを抑える具体的判断軸：設計書本文に既に記載されている内容を「未定義」と指摘する所見、foundation の言及を再列挙するか参照のみとするかの様式論、実装段／タスク段で詰めれば足りる具体は leave-as-is。敵対役の反証が成立した所見は反証どおり leave-as-is とする。foundation との契約整合性は本機能の最重要規律。

### 3.3 集計

- by_judgment: `{ must-fix: 3, should-fix: 17, leave-as-is: 19 }`（合計 39、判定本文を優先）
- by_waterfall: `{ 機能内対処: 31, 波及: 0, 遡及: 0, 延期: 8 }`
- count: 39

---

## 4. 統合（integration）

### 4.1 採用所見一覧

#### must-fix（3 件、本セッション内で design.md に反映済み）

| finding_id | severity | judgment | target_location | 概要 | 対処方針 |
|---|---|---|---|---|---|
| F-001 | ERROR | must-fix | §セッションモデル §3 行 222 | `analysis_blocked` 誤記 | 1 文字列置換で修正完了 |
| A-001 | ERROR | must-fix | §証拠出力モデル／§段実行マトリクス | foundation `step_status` と runtime `step_outcome` の関係未統合 | §段実行マトリクス節に関係明示、§証拠出力モデルに投影規約追記 |
| A-002 | ERROR | must-fix | §セッションモデル §3 | `evidence_class` 確定遷移の網羅性ギャップ | 9 ケースの網羅マッピング表に拡張 |

#### should-fix（17 件、本セッション内では対処せず、後続フェーズで対処）

設計の精緻化に資する論点だが、triad-review 段の完了基準（must-fix 解消）の必須要件ではないため、本機能の design 段の後続段（review-wave／alignment）または tasks 段で順次対処する。

#### leave-as-is（19 件、記録のみ）

第 3 節 3.1 に列挙。修正不要、本記録に残すのみ。

### 4.1.1 must-fix 対処内容の利用者議論結果（運営ガイド §3.3 (a-1) 準拠）

判定役の判定後、運営ガイド §3.3 (a-1)「must-fix 所見の対処手順（深掘り議論の義務化）」に従い、3 件を 1 件ずつ深掘り議論して対処内容を確定した。本記録はその議論結果を保存する。

**議論結果**：

| ID | 利用者決定 | design.md への反映 |
|---|---|---|
| F-001 | (ア) `analysis_modified` → `analysis_blocked` 修正 | 行 222 を 1 文字列置換 |
| A-001 | (ア) `step_outcome` を `step_status` の値域として機能させる旨を runtime 側で宣言 | §treatment × 段実行マトリクスに「`step_status`（foundation）と `step_outcome`（本機能）の関係」段落追加、§証拠出力モデル §生証拠と派生証拠の分離に「主要な投影対応」リスト追加 |
| A-002 | (ア) `validator_status` × `human_signoff_status` の網羅マッピング表に拡張（9 ケース） | §セッションモデル §3 の確定遷移を 4 ケース → 9 ケースに拡張 |

**採用された設計原則**（foundation との連動）：

- 原則 1：foundation の `step_status` 値域未確定は runtime 所有正本 `step_outcome` で実体化する（contract consumer 原則の例外的解釈ではなく役割分担）
- 原則 2：foundation の `validator_status` × `human_signoff_status` 4×4 組み合わせの確定先は runtime が網羅マッピングとして所有する

design.md 行数の変化：起草 704 行 → must-fix 反映 725 行（+21 行）。

**利用者明示承認の出典**：「ア」（F-001 修正）「ア」（A-001 (ア) 採用）「ア」（A-002 (ア) 採用）（2026-05-25 セッション 25）。本 triad-review に先立ち、運営ガイド §3.3 (a-1) と memory 規律「must-fix 対処の議論義務化」を新設済み（コミット bdca440）。

### 4.2 抽出元との対応

- 抽出元 finding：素材文書 `dual-reviewer-rebuild/.kiro/specs/dual-reviewer-runtime/design.md`（810 行）と本設計書（725 行）の差分は §変更意図に集約済み
- 新規発見（本 triad-review による）：A-001（`step_status`／`step_outcome` 関係未統合）と A-002（`evidence_class` 確定遷移網羅性ギャップ）は素材文書段階から潜在的に存在した欠落だが、本 triad-review で Opus 敵対役が初検出した中核的論点

### 4.3 残課題

- must-fix 3 件は本セッション内で design.md に反映済み
- should-fix 17 件（または 19 件、本文）は本機能の後続段（review-wave／alignment）または tasks 段で順次対処
- 波及・遡及は発生せず、`.reviewcompass/pending-cross-feature-findings.md` への追記は不要
- 計画書 §5.9.1 は本セッション中に改訂済み（コミット 0e85087）、本 triad-review はその改訂後の規律に整合

### 4.4 triad-review 段の完了判定

判定役（Opus 4.7）の総合所見：

> must-fix 3 件はすべて機能内対処で解消可能であり、波及／遡及は発生しない。A-001 のみ将来的に foundation 側で `step_status` 値域を明示することが望ましく、その場合は本機能修正後に pending-cross-feature-findings へ補助所見として記録する余地がある。foundation との契約整合性：基本構造は健全。ただし F-001／A-001／A-002 の 3 点は契約整合性を実害レベルで損なうため、triad-review 段で必ず解消すべき。

本記録に基づき、must-fix 3 件を design.md に反映完了したため、本機能の design.triad-review 段は完了基準を満たすと判定する。

---

## 5. 関連参照

- 設計文書：[.reviewcompass/specs/runtime/design.md](../design.md)
- 要件文書：[.reviewcompass/specs/runtime/requirements.md](../requirements.md)
- 素材文書：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/dual-reviewer-runtime/design.md`（読み取り専用）
- foundation 設計書：[.reviewcompass/specs/foundation/design.md](../../foundation/design.md)
- foundation レビュー記録（セッション 25 同日実施）：[.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md](../../foundation/reviews/2026-05-25-design-triad-review.md)
- モデル配分実験記録（セッション 25 同日）：[docs/notes/2026-05-25-triad-review-model-allocation-experiment.md](../../../../docs/notes/2026-05-25-triad-review-model-allocation-experiment.md)
- 計画書 §5.9.1（2026-05-25 改訂版、コミット 0e85087）、§5.9.2（観点）、§5.23.12（サブエージェント方式）
- 運営ガイド §2.3（段の進め方）、§3.3 (a)（機能内対処）、§3.3 (a-1)（must-fix 対処の議論義務化、本記録の運用根拠、コミット bdca440 新設）
- レビュー記録雛形：[templates/review/manual_dogfooding_review_template.md](../../../../templates/review/manual_dogfooding_review_template.md)
