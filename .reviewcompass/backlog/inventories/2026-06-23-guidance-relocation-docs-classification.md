# Guidance Relocation Inventory and Classification

作成日: 2026-06-23

対象計画: `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml`

## Scope

この表は GRC-1 の成果物であり、`docs/operations` と `docs/disciplines` に残る文書の棚卸しと一次分類だけを行う。ファイル移動、旧 path 削除、参照更新、`deploy-manifest.yaml` 変更はこの段階では行わない。

分類は後続の GRC-2 参照監査と GRC-3 検査追加で更新され得る。ここでの `proposed destination` は移動実施の承認ではなく、次段階で検証する候補である。

## Classification Legend

| Classification | Meaning |
|---|---|
| `deploy_facing` | 配布先に持ち込み、対象アプリ内の LLM / hooks / tools が読む必要がある |
| `runtime_facing` | workflow navigation、commit / push / review-run / proxy 操作へ影響する |
| `effective_prompt_source` | effective prompt の source ref として使われる、または使うべき規律 |
| `spec_or_contract_source` | 機能仕様・受入条件・機械検査の正本または準正本として扱われている |
| `human_reference` | 人間向けの背景説明、機能解説、履歴整理であり実行時必読ではない |
| `historical` | 過去の判断経緯・古い規律・退役済み文書 |
| `requires_decision` | 移動・残置・分割の判断に追加監査が必要 |

## Inventory Table

| File | Classification | Current readers | Expected readers | Deploy inclusion | Effective prompt source status | Proposed destination | Delete-old-path condition |
|---|---|---|---|---|---|---|---|
| `docs/operations/ANALYSIS.md` | `human_reference`, `spec_or_contract_source` | 計画書、notes、analysis 関連の人間向け参照 | analysis の運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `.reviewcompass/specs/analysis` などへ正本を寄せ、参照更新と link lint が完了した場合 |
| `docs/operations/CONFORMANCE_EVALUATION.md` | `human_reference`, `spec_or_contract_source` | 計画書、conformance-evaluation 関連 notes / review-run 記録 | conformance-evaluation の運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `.reviewcompass/specs/conformance-evaluation` 側へ正本性を整理し、参照更新が完了した場合 |
| `docs/operations/DEPLOYMENT.md` | `human_reference`, `deploy_facing`, `requires_decision` | deployment 方針、post-write 記録、legacy path audit | ReviewCompass 開発側で配布方針を確認する作業者 | Decision | None | Decision required: keep as owner-facing docs or split deploy-facing rules into `.reviewcompass/guidance` | 配布物生成・manifest・外部アプリ手順の正本先を分割し、旧 path 参照がなくなった場合 |
| `docs/operations/EVALUATION.md` | `human_reference`, `spec_or_contract_source` | tests、review-run 記録、計画書、evaluation 関連 notes | evaluation の運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `.reviewcompass/specs/evaluation` と layout specs へ正本を寄せ、参照更新が完了した場合 |
| `docs/operations/FOUNDATION.md` | `human_reference`, `spec_or_contract_source` | runtime/config README、runtime/foundation README、tests、計画書 | foundation 契約の背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | runtime README / tests / notes の参照更新と仕様正本分離が完了した場合 |
| `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` | `deploy_facing`, `human_reference`, `requires_decision` | `deploy-manifest.yaml` が配布対象として明示、post-write 記録 | 初期 pilot を行う利用者または操縦 LLM | Yes | None | Keep until deploy guide ownership is decided; possible split to `.reviewcompass/guidance` for LLM-facing parts | 配布 manifest の扱いを決め、利用者向け文書と LLM-facing 手順を分離した場合 |
| `docs/operations/RUNTIME.md` | `human_reference`, `spec_or_contract_source` | runtime run layout README、sessions、計画書、runtime 関連 notes | runtime 運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `runtime/runtime_core/run_layout` 参照と仕様正本先の整理が完了した場合 |
| `docs/operations/SELF_IMPROVEMENT.md` | `human_reference`, `spec_or_contract_source` | 計画書、self-improvement 関連 logs / notes | self-improvement の運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `.reviewcompass/specs/self-improvement` と learning workflow docs へ責務を整理した場合 |
| `docs/operations/SELF_IMPROVEMENT_MACHINE_VERIFICATION.md` | `runtime_facing`, `spec_or_contract_source`, `requires_decision` | self-improvement check の手引きとして人間参照 | self-improvement 検査器を保守する作業者 | Decision | None | Decision required: `.reviewcompass/guidance` if operator-facing, otherwise `docs/operations` | `tools/self-improvement-check.py` の正本契約先を決め、参照監査が完了した場合 |
| `docs/operations/WORKFLOW_MANAGEMENT.md` | `human_reference`, `spec_or_contract_source` | 計画書、experiments、workflow-management 関連 notes | workflow-management の運用背景を読む開発者 | No | None | Keep in `docs/operations` or move later to feature-local operations note | `.reviewcompass/specs/workflow-management` へ正本性を寄せ、旧参照がなくなった場合 |
| `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` | `runtime_facing`, `deploy_facing`, `effective_prompt_source`, `requires_decision` | `CLAUDE.md`、notes、post-write 記録 | Claude Code で作業する LLM | Decision | Not currently mapped as canonical effective prompt; content points to `.reviewcompass/guidance` | Likely move to `.reviewcompass/guidance` or absorb into entry templates | `CLAUDE.md` / templates / deployment consumers が新正本を読み、旧 path 参照がなくなった場合 |
| `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` | `runtime_facing`, `deploy_facing`, `effective_prompt_source`, `requires_decision` | `templates/todo/TODO_NEXT_SESSION.template.md`、notes、post-write 記録 | Codex で作業する LLM | Decision | Not currently mapped as canonical effective prompt; content points to `.reviewcompass/guidance` | Likely move to `.reviewcompass/guidance` or absorb into entry templates | TODO template / adapter consumers が新正本を読み、旧 path 参照がなくなった場合 |
| `docs/disciplines/README.md` | `runtime_facing`, `human_reference`, `requires_decision` | docs notes、計画書、experiments、discipline ownership references | 規律一覧と所有境界を確認する作業者 | Decision | None | Decision required: active discipline index may move to `.reviewcompass/guidance` while history remains in docs | active 必読一覧の正本先を決め、archive / history の残置方針が決まった場合 |
| `docs/disciplines/discipline_avoid_compound_bash.md` | `runtime_facing`, `effective_prompt_source`, `human_reference` | TODO snapshots、discipline README | LLM 作業者、将来の effective prompt | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active; otherwise demote to notes | active / reference / retired status を README と discipline map で確定した場合 |
| `docs/disciplines/discipline_concise_complete_report.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、experiments、discipline README | LLM 作業者、作業完了報告 prompt | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` or fold into `SESSION_WORKFLOW_GUIDE.md` | 完了報告契約との重複を解消し、新正本へ参照更新した場合 |
| `docs/disciplines/discipline_facts_vs_interpretation.md` | `runtime_facing`, `effective_prompt_source` | learning proposal、TODO snapshots、draft references | LLM 作業者、監査・報告 prompt | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | active status と effective prompt 接続を確定し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_implementation_autonomy.md` | `runtime_facing`, `effective_prompt_source`, `requires_decision` | discipline README、関連規律 | LLM 作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Decision required: keep, merge, or demote depending on overlap with current workflow guidance | 自律進行の現行正本との重複を整理し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_intent_conformance_is_the_acceptance_gate.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、discipline README、関連規律 | LLM 作業者、implementation acceptance 判断 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | acceptance gate の正本先を確定し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_must_fix_discussion_obligation.md` | `runtime_facing`, `effective_prompt_source`, `requires_decision` | legacy path audit、experiments、discipline README | triad-review 後の LLM 作業者 | Decision | Content says `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md` is canonical for body | Likely demote to pointer or delete after guidance coverage confirmed | `SESSION_WORKFLOW_GUIDE.md` への統合が十分で、旧 path 参照が更新された場合 |
| `docs/disciplines/discipline_no_redundant_workflow_questions.md` | `runtime_facing`, `effective_prompt_source` | discipline README | LLM 作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | active status と source map の扱いを確定した場合 |
| `docs/disciplines/discipline_normal_output_minimization.md` | `runtime_facing`, `effective_prompt_source`, `deploy_facing` | discipline README、normal-output rollout plan | CLI / tool 実装者、LLM 作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` or tool contract docs | normal output 契約の deploy-facing 正本先を決め、tools/tests の参照を更新した場合 |
| `docs/disciplines/discipline_options_presentation.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、discipline README | LLM 作業者、利用者判断提示場面 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | active status と effective prompt 接続を確定した場合 |
| `docs/disciplines/discipline_plain_explanation_each_step.md` | `runtime_facing`, `effective_prompt_source` | decision-source lint notes、TODO snapshots、discipline README | LLM 作業者、承認前説明場面 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` or fold into session guide | 承認前説明契約との重複を整理し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_plain_japanese.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、discipline README | LLM 作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | active status と source map の扱いを確定した場合 |
| `docs/disciplines/discipline_pre_action_precheck.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、discipline README | LLM 作業者、横断操作前の作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | 現行 workflow precheck との重複を整理し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_reopen_procedure_for_settled_topics.md` | `runtime_facing`, `effective_prompt_source`, `requires_decision` | TODO snapshots、discipline README | reopen 判断を行う LLM 作業者 | Decision | Not currently in `.reviewcompass/guidance` map | Decision required: move to guidance or fold into `REOPEN_PROCEDURE.md` | reopen 手続き正本との重複を整理し、旧 path 参照がなくなった場合 |
| `docs/disciplines/discipline_standing_directives_are_hard_constraints.md` | `runtime_facing`, `effective_prompt_source` | TODO snapshots、discipline README、関連規律 | LLM 作業者、approach 変更判断 | Decision | Not currently in `.reviewcompass/guidance` map | Likely move to `.reviewcompass/guidance` if still active | active status と source map の扱いを確定した場合 |
| `docs/disciplines/discipline_workflow_precheck_invocation.md` | `runtime_facing`, `effective_prompt_source`, `requires_decision` | legacy path audit、TODO snapshots、discipline README | LLM 作業者、不可逆操作前 | Decision | Overlaps with `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` and precheck tooling | Likely fold into `.reviewcompass/guidance` or delete after guidance coverage confirmed | precheck invocation の現行正本が guidance 側で十分と確認し、旧 path 参照がなくなった場合 |

## Archive Observations

次のファイルは `docs/disciplines/archive` 配下で、初期計画の main target には含まれていない。ただし `find docs/disciplines -type f` では残存文書として観測されるため、GRC-2 では historical として参照監査対象に含める。

| File | Classification | Current readers | Proposed handling |
|---|---|---|---|
| `docs/disciplines/archive/README.md` | `historical` | archive 配下の説明 | Keep in archive unless docs archive policy changes |
| `docs/disciplines/archive/2026-05-26-consolidation/README.md` | `historical` | options presentation 統廃合履歴 | Keep in archive |
| `docs/disciplines/archive/2026-05-26-consolidation/discipline_choice_presentation.md` | `historical` | 統廃合履歴、旧規律参照 | Keep in archive |
| `docs/disciplines/archive/2026-05-26-consolidation/discipline_dominant_dominated_options.md` | `historical` | 統廃合履歴、旧規律参照 | Keep in archive |

## Summary by Proposed Action

| Proposed action | Files |
|---|---|
| Keep as human-reference operations docs for now | `ANALYSIS.md`, `CONFORMANCE_EVALUATION.md`, `EVALUATION.md`, `FOUNDATION.md`, `RUNTIME.md`, `SELF_IMPROVEMENT.md`, `WORKFLOW_MANAGEMENT.md` |
| Requires deploy / owner-facing split decision | `DEPLOYMENT.md`, `INITIAL_DEPLOYMENT_USER_GUIDE.md` |
| Requires operator / tool-contract decision | `SELF_IMPROVEMENT_MACHINE_VERIFICATION.md` |
| Likely adapter guidance relocation or template absorption | `WORKFLOW_NAVIGATION_FOR_CLAUDE.md`, `WORKFLOW_NAVIGATION_FOR_CODEX.md` |
| Requires active discipline consolidation decision | `docs/disciplines/README.md` and active `discipline_*.md` files |
| Historical, keep archived | `docs/disciplines/archive/**` |

## Next Audit Questions for GRC-2

1. `docs/disciplines/README.md` の active 必読一覧と `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` の対応は一致しているか。
2. adapter guidance は `.reviewcompass/guidance` に移すべきか、`AGENTS.md` / `CLAUDE.md` / templates の入口生成へ吸収すべきか。
3. `INITIAL_DEPLOYMENT_USER_GUIDE.md` は配布物に含め続けるべきか、利用者向け文書と LLM-facing 手順に分割すべきか。
4. feature operation docs は `docs/operations` に残すべきか、`.reviewcompass/specs/<feature>/operations.md` へ寄せるべきか。
5. active discipline のうち、すでに `.reviewcompass/guidance` の session guide / workflow navigation に実質統合済みのものはどれか。
