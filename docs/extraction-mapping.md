# 抽出対応表（フェーズ 1 進行記録）

最終更新：2026-05-23（セッション 19 で全 7 機能の requirements.md 抽出完了 ＋ 要件 review-wave／alignment-gate を実施、機能横断波及所見 6 件すべて消化）

本文書は計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.20 を出発点として、フェーズ 1 抽出作業の進行記録を残すための作業文書である。計画書 §5.20 は正本、本文書は進行中の作業記録（§5.20.5）。

抽出元リポジトリ：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/`（読み取り専用扱い）
抽出先：本リポジトリ `/Users/Daily/Development/ReviewCompass/`

抽出物の配置方針：解釈 う（2026-05-22 確定、§5.19.2 第 5 項目）。requirements.md／design.md は運用文書（`docs/operations/<機能>.md`）と仕様文書（`.reviewcompass/specs/<機能>/requirements.md`・`design.md`）の両方に出力する。schema／prompt／config 等の実成果物は仕様文書側には複製せず、`schemas/`／`templates/` 配下にのみ配置する。

dogfeeding（自己適用）方針：計画書 §5.23.10 に基づき、各機能の requirements.md／design.md 抽出時に手動 3 役レビュー（§5.23.4）を実施する。レビュー記録は `templates/review/manual_dogfooding_review_template.md` を雛形として `.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md` に保存する。schema／prompt／config 等の機械的なファイルコピーは dogfeeding 対象外（実施履歴欄は「—」）。

状態欄の値：

- 未着手：抽出作業に取り掛かっていない
- 抽出中：作業中、未完了
- 抽出済：抽出完了、確認待ち
- 確認済：利用者確認を経た状態

実施履歴欄の記法：

- dogfeeding 対象（requirements.md／design.md）：実施日 ＋ 記録ファイル相対リンク（例：`2026-06-01 → .reviewcompass/specs/foundation/reviews/2026-06-01-requirements.md`）
- dogfeeding 対象外（schema／prompt／config／script 等）：「—」

---

## 1. 機能別対応表

### foundation（基盤機能）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-foundation/requirements.md` | `docs/operations/FOUNDATION.md`（§5.18.16）＋ `.reviewcompass/specs/foundation/requirements.md`（解釈 う） | 機能名 dual-reviewer-* → ReviewCompass の機能名、自己適用表現の除去 | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/foundation/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/foundation/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、must-fix 4 件処理済） | サブエージェント方式で 3 役レビュー実施、must-fix 4 件を反映、F-004 は次セッション持ち越し |
| `.kiro/specs/dual-reviewer-foundation/design.md` | `docs/operations/FOUNDATION.md`（§5.18 の継承方針に従い再編）＋ `.reviewcompass/specs/foundation/design.md`（解釈 う） | 同上 | 未着手 | — | — | — |
| `runtime/foundation/layer1_framework.yaml` | `schemas/foundation/layer1_framework.yaml` | パス相対化 | 未着手 | — | — | — |
| `runtime/foundation/metadata_contract.yaml` | `schemas/foundation/metadata_contract.yaml` | パス相対化 | 未着手 | — | — | — |
| `runtime/schemas/review_case.schema.json` | `schemas/domain/review_case.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/schemas/finding.schema.json` | `schemas/domain/finding.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/schemas/impact_score.schema.json` | `schemas/domain/impact_score.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/schemas/failure_observation.schema.json` | `schemas/domain/failure_observation.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/schemas/necessity_judgment.schema.json` | `schemas/domain/necessity_judgment.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/validators/contracts/validator_result.schema.json` | `schemas/validators/validator_result.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/validators/contracts/invalidation_marker.schema.json` | `schemas/validators/invalidation_marker.schema.json` | パス相対化 | 未着手 | — | — | — |
| `runtime/prompts/primary_detection/primary_reviewer.prompt.md` | `templates/prompts/primary_detection/primary_reviewer.prompt.md` | パス相対化、prompt 内容のレビューと一般化 | 未着手 | — | — | — |
| `runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md` | `templates/prompts/adversarial_review/adversarial_reviewer.prompt.md` | 同上 | 未着手 | — | — | — |
| `runtime/prompts/judgment/judgment_reviewer.prompt.md` | `templates/prompts/judgment/judgment_reviewer.prompt.md` | 同上 | 未着手 | — | — | — |
| `runtime/config/config.yaml.template` | `templates/config/config.yaml.template` | §5.18.15 残課題（reviewcompass.yaml との境界）の確定後に整備 | 未着手 | — | — | — |
| `runtime/config/terminology.yaml.template` | `templates/config/terminology.yaml.template` | パス相対化 | 未着手 | — | — | — |

### runtime（実行時機能）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-runtime/requirements.md` | `docs/operations/RUNTIME.md`（§5.15.8）＋ `.reviewcompass/specs/runtime/requirements.md`（解釈 う） | 自己適用表現の除去、実行方式名の置換（§5.15.6） | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/runtime/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/runtime/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、must-fix 1／should-fix 2 処理済、A-001 は機能横断波及所見として [pending-cross-feature-findings.md](../.reviewcompass/pending-cross-feature-findings.md) §A-001 に持ち越し） | サブエージェント方式で 3 役レビュー実施、F-001／F-002／F-004 処理済、A-001（not_run 欠落、foundation にも波及）は要件 review-wave／alignment-gate へ持ち越し |
| `.kiro/specs/dual-reviewer-runtime/design.md` | `docs/operations/RUNTIME.md` ＋ `.reviewcompass/specs/runtime/design.md`（解釈 う） | 同上、ファイル名置換（v2/ → internal/、review_artifact.json → review_taxonomy.json 等） | 未着手 | — | — | — |
| `scripts/run_review_session.rb` 等の実行スクリプト | （実装は移植しない、§2.2 クリーンスレート） | 思想のみ継承 | 未着手 | — | — | — |

### evaluation（評価機能）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-evaluation/requirements.md` | `docs/operations/EVALUATION.md`（§5.17.14）＋ `.reviewcompass/specs/evaluation/requirements.md`（解釈 う） | 機能名置換、実行方式名置換（single/dual/dual+judgment → primary/adversarial/judgment、§5.17.8）、自己適用表現の除去 | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/evaluation/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/evaluation/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、機能内 must-fix 2／should-fix 1 処理済、A-003 は機能横断波及所見として [pending-cross-feature-findings.md](../.reviewcompass/pending-cross-feature-findings.md) §A-003 に持ち越し） | サブエージェント方式で 3 役レビュー実施、F-001／F-003／A-002 処理済、A-003（analysis_blocked 欠落、foundation にも波及）は要件 review-wave／alignment-gate へ持ち越し |
| `.kiro/specs/dual-reviewer-evaluation/design.md` | `docs/operations/EVALUATION.md` ＋ `.reviewcompass/specs/evaluation/design.md`（解釈 う） | 同上、固定パス（experiments/analysis/／experiments/runs/）の抽象化 | 未着手 | — | — | — |
| `scripts/evaluation/*.rb`（実装 18 ファイル） | （実装は移植しない、§2.2 クリーンスレート） | 思想・構造のみ継承（5 段パイプライン、4 状態区分、3 階層 2 層指標等） | 未着手 | — | — | — |

### analysis（分析機能、旧 paper-interface）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-paper-interface/requirements.md` | `docs/operations/ANALYSIS.md`（§5.14.7）＋ `.reviewcompass/specs/analysis/requirements.md`（解釈 う） | 機能名 paper-interface → analysis（§5.15.6）、自己適用表現の除去、§5.14 拡張（4 出力先 ＋ レビュー収束過程の可視化を Req 7／8 として新設） | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/analysis/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/analysis/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、機能内 must-fix 1／should-fix 2 処理済、A-004 持ち越し） | サブエージェント方式 4 機能目、Req 7／8 新設、F-001／F-002／B-001 処理済、A-004（evaluation の経路別差分出力欠落）は持ち越し |
| `.kiro/specs/dual-reviewer-paper-interface/design.md` | `docs/operations/ANALYSIS.md` ＋ `.reviewcompass/specs/analysis/design.md`（解釈 う） | 同上、§5.14 の役割拡張（論文用以外に運用ダッシュボード・週次・監査）を反映 | 未着手 | — | — | — |
| `scripts/paper_interface/*.rb` | （実装は移植しない） | 思想のみ継承 | 未着手 | — | — | — |

### workflow-management（旧 implementation-governance）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-implementation-governance/requirements.md` | `docs/operations/WORKFLOW_MANAGEMENT.md` ＋ `.reviewcompass/specs/workflow-management/requirements.md`（解釈 う） | 機能名 implementation-governance → workflow-management（§5.15.6）、§5.4 軽量化方針に従い大部分を削減 | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/workflow-management/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/workflow-management/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、機能内 must-fix 2／should-fix 2 処理済、A-005 の conformance-evaluation 側反映予定を持ち越し） | 大規模再設計（156 行 9 要件 → 8 要件）、§5.4〜§5.8 統合、F-001／F-003／F-004／A-005 workflow 側処理済 |
| `.kiro/specs/dual-reviewer-implementation-governance/design.md` | `docs/operations/WORKFLOW_MANAGEMENT.md` ＋ `.reviewcompass/specs/workflow-management/design.md`（解釈 う） | 同上 | 未着手 | — | — | — |
| `scripts/governance/*.rb` | （実装は移植しない、軽量版を新規実装） | §5.4 の軽量化方針に従い静的 YAML 検査に置換 | 未着手 | — | — | — |

### self-improvement（改善機能、workflow 層のみ）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/specs/dual-reviewer-self-improvement/requirements.md` | `docs/operations/SELF_IMPROVEMENT.md`（§5.16.12）＋ `.reviewcompass/specs/self-improvement/requirements.md`（解釈 う） | 旧 8 要件のうち workflow 層改善向け部分のみ継承、§5.16 の 8 構成で再設計 | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/self-improvement/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/self-improvement/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、機能内 must-fix 1／should-fix 1 処理済、A-007 機能横断持ち越し） | §5.16 全面書き直し方針、F-002／F-003 処理済、A-007（self-improvement と workflow-management の権限分散調停）は要件 review-wave へ持ち越し |
| `.kiro/specs/dual-reviewer-self-improvement/design.md` | `docs/operations/SELF_IMPROVEMENT.md` ＋ `.reviewcompass/specs/self-improvement/design.md`（解釈 う） | 同上 | 未着手 | — | — | — |
| `scripts/self_improvement/*.rb`（旧 8 モジュール） | （継承 4 モジュール、新規実装 4 モジュール、§5.16.11） | 継承可能：decision_adoption_model／rollback_model／pipeline_driver／learning_layout。新規：input_model／proposal_model／replay_backtest_model 相当／signal_extraction | 未着手 | — | — | — |

### conformance-evaluation（新規 7 番目機能）

| 抽出元 | 抽出先 | クリーニング | 状態 | 完了日 | 実施履歴 | 備考 |
|---|---|---|---|---|---|---|
| `.kiro/methodology/dual-reviewer-spec-driven-paper/v3-plan.md` | `docs/operations/CONFORMANCE_EVALUATION.md`（§5.10.7）＋ `.reviewcompass/specs/conformance-evaluation/requirements.md`（解釈 う、design.md は v3-plan に明示なきため後続セッションで起こす） | future feature 記述を実機能仕様として書き起こし、12 criteria 構造（§5.10.2）を明示 | 抽出済 | 2026-05-22 | 2026-05-22 → [.reviewcompass/specs/conformance-evaluation/reviews/2026-05-22-requirements.md](../.reviewcompass/specs/conformance-evaluation/reviews/2026-05-22-requirements.md)（subagent_mediated、3 役完了、機能内 must-fix 4／should-fix 1 処理済、A-008 既記録済み） | 新規 7 番目機能、§5.10 ＋ v3-plan.md から書き起こし、F-001／F-002／A-CONF-I-001／A-CONF-I-002／A-008 すべて処理済 |

---

## 2. 正本文書の対応表

| 抽出元 | 抽出先 | 状態 | 完了日 | 備考 |
|---|---|---|---|---|
| `operations/REVIEW_PROTOCOL.md` | `docs/operations/REVIEW_PROTOCOL.md`（§6 実装適合レビューを統合、§5.9） | 未着手 | — | — |
| `operations/HUMAN_WORKFLOW.md` | `docs/operations/HUMAN_WORKFLOW.md` | 未着手 | — | — |
| `operations/DATA_INVALIDATION_POLICY.md` | `docs/operations/DATA_INVALIDATION_POLICY.md` | 未着手 | — | — |
| `operations/DEPLOYMENT_MODEL.md` | `docs/operations/DEPLOYMENT_MODEL.md` | 未着手 | — | — |
| `operations/TRUST_BOUNDARY.md` | `docs/operations/TRUST_BOUNDARY.md` | 未着手 | — | — |
| `operations/WORKFLOW_OVERVIEW.md` | `docs/operations/WORKFLOW_OVERVIEW.md`（§5.4 軽量化方針を反映） | 未着手 | — | — |
| `docs/coordination/workflow-repair-procedure.md` | `docs/operations/REOPEN_PROCEDURE.md`（§5.6 機械強制を反映） | 抽出済 | 2026-05-28 | 素材 10 ステップを現在の 5 段ワークフローに再構成、§5.6.1 の 4 過程構成として正式記録（セッション 37） |
| リポジトリ直下 CONVENTIONS.md／DOCUMENT_INDEX.md／EVIDENCE_PROTOCOL.md／MIGRATION_MANIFEST.md／SELF_IMPROVEMENT_LOOP.md／SYSTEM_BOUNDARY.md／REPRODUCIBILITY_CONTRACT.md／README.md | `docs/operations/` に集約（§3.2） | 未着手 | — | — |

---

## 3. 規律ファイルの対応表

| 抽出元 | 抽出先 | 状態 | 完了日 | 備考 |
|---|---|---|---|---|
| `.kiro/memory/discipline_*.md`（活用される規律 8 件程度） | `docs/disciplines/discipline_*.md`（status: enforced、§5.9.4） | 未着手 | — | — |
| `.kiro/memory/discipline_review_judgment_patterns.md`（23 パターン） | `docs/archive/disciplines/<日付>/discipline_review_judgment_patterns.md`（§5.9.4） | 未着手 | — | — |
| `.kiro/memory/discipline_review_necessity_judgment.md`（必要性 5 観点、参照ゼロ） | `docs/archive/disciplines/<日付>/`（§5.9.4） | 未着手 | — | — |
| `operations/disciplines/discipline_*.md`（7 件） | `docs/disciplines/discipline_*.md` | 未着手 | — | — |

---

## 4. 運用ルール（計画書 §5.20.5 抜粋）

- 本文書はフェーズ 1 進行中の作業記録。計画書 §5.20 が正本
- 抽出を進めながら、各成果物の状態欄・完了日・実施履歴・備考を更新する
- 雛形は不完全な初版であり、フェーズ 1 進行中に網羅性と粒度を見直す
- 抽出順序は計画書 §3.1 で確定済みの機能依存マップ（foundation → runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation）に従う
- dogfeeding 対象（requirements.md／design.md）の手動 3 役レビューは `templates/review/manual_dogfooding_review_template.md` を雛形として実施する（§5.23.4／§5.23.5）
