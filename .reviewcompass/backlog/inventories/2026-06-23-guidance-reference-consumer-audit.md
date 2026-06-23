# Guidance Reference and Consumer Audit

作成日: 2026-06-23

対象計画: `.reviewcompass/backlog/plans/plan-2026-06-23-guidance-relocation-and-docs-classification.yaml`

前段成果物: `.reviewcompass/backlog/inventories/2026-06-23-guidance-relocation-docs-classification.md`

## Scope

この表は GRC-2 の成果物であり、`docs/operations` / `docs/disciplines` に残る文書を移動する前に、参照元と consumer を分類する。ファイル移動、旧 path 削除、参照更新、テスト追加、`deploy-manifest.yaml` 変更はこの段階では行わない。

## Search Summary

実施した検索:

- `rg -l "docs/operations|docs/disciplines" .`
- `rg -l "WORKFLOW_NAVIGATION_FOR_CLAUDE|WORKFLOW_NAVIGATION_FOR_CODEX|INITIAL_DEPLOYMENT_USER_GUIDE|DEPLOYMENT\\.md|SELF_IMPROVEMENT_MACHINE_VERIFICATION" .`
- `rg -l "discipline_(...)" .`
- `rg -n "docs/operations|docs/disciplines|WORKFLOW_NAVIGATION_FOR_|discipline_" AGENTS.md CLAUDE.md TODO_NEXT_SESSION.md templates deploy-manifest.yaml .claude .codex`
- `rg -n "docs/operations|docs/disciplines|WORKFLOW_NAVIGATION_FOR_|discipline_" tests runtime tools learning/workflow`
- `rg -n "docs/operations|docs/disciplines|WORKFLOW_NAVIGATION_FOR_|discipline_" .reviewcompass/guidance .reviewcompass/runtime/effective-prompts .reviewcompass/backlog`

検索結果は大量の履歴、review-run、実験ログ、過去 session 記録を含む。GRC-2 では、移動時に更新が必要になり得る consumer を次の 4 区分で扱う。

| Consumer class | Meaning | Update priority |
|---|---|---|
| `deploy_consumer` | `deploy-manifest.yaml`、配布物、対象アプリ側 LLM が読む入口 | Must update before move |
| `runtime_consumer` | hook、tool、effective prompt、runtime README、実行時判定に影響する参照 | Must update or explicitly retire |
| `test_contract` | tests、schema、lint fixture など旧 path を契約として持つ参照 | Must update with tests |
| `historical_reference` | docs/notes、docs/sessions、review-run、stages/completed、実験ログ | Usually keep; do not rewrite unless policy requires |

## Active Consumer Table

| Source / candidate | Active consumers found | Consumer class | Update needed before move | Notes |
|---|---|---|---|---|
| `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` | `CLAUDE.md:7` | `deploy_consumer`, `runtime_consumer` | Yes | Claude entrypoint still points to old docs path. If adapter guidance moves to `.reviewcompass/guidance` or templates, `CLAUDE.md` must be updated in same migration. |
| `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` | `templates/todo/TODO_NEXT_SESSION.template.md:74` | `deploy_consumer` | Yes | TODO handoff template still mentions Codex adapter guidance at old path. If moved, template must change. |
| `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` | `deploy-manifest.yaml:129`; `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md:78` | `deploy_consumer` | Yes | This is currently the only remaining `docs/operations` file explicitly included in deploy manifest. Split decision is required before moving. |
| `docs/operations/DEPLOYMENT.md` | Human docs and review-run records; no active deploy manifest inclusion found | `historical_reference`, possible `deploy_consumer` | Decision | It governs deployment policy but is not itself in manifest. If split into guidance, only policy consumers should update. |
| `docs/operations/RUNTIME.md` | `runtime/runtime_core/run_layout/README.md:3`, `:50` | `runtime_consumer` | Yes if moved | Runtime layout README treats it as placement-rule source. Moving requires README and any tests that assert this relation to change. |
| `docs/operations/FOUNDATION.md` | `runtime/foundation/README.md:13`; `runtime/config/README.md:18`; foundation tests | `runtime_consumer`, `test_contract` | Yes if moved | Runtime/config README uses it as operational explanation. Feature-local relocation needs README/test updates. |
| `docs/operations/EVALUATION.md` | `tests/evaluation/test_t001_layout.py`; review-run records | `test_contract` | Yes if moved | Test asserts existence or behavior tied to old operations path. |
| `docs/operations/ANALYSIS.md` | analysis tests / experiments / plan references | `test_contract`, `historical_reference` | Yes if moved | Treat as feature operation doc until feature-local target is decided. |
| `docs/operations/CONFORMANCE_EVALUATION.md` | `tests/fixtures/conformance-evaluation/cross-feature-contract-ownership.yaml:187`; docs notes | `test_contract`, `historical_reference` | Yes if moved | Contract ownership fixture names this path. |
| `docs/operations/SELF_IMPROVEMENT.md` | self-improvement tests / logs / planning references | `test_contract`, `historical_reference` | Yes if moved | Most active behavior uses specs/tools, but tests and docs still refer to operations path. |
| `docs/operations/SELF_IMPROVEMENT_MACHINE_VERIFICATION.md` | docs sessions, tests, self-improvement check context | `runtime_consumer`, `historical_reference` | Decision | If this becomes operator guidance, move to `.reviewcompass/guidance`; if only human reference, keep in docs. |
| `docs/operations/WORKFLOW_MANAGEMENT.md` | experiments and historical design prompts | `historical_reference`, possible `test_contract` | Decision | Current guidance正本 is already `.reviewcompass/guidance`; old operation doc appears mostly feature explanation. |
| `docs/disciplines/discipline_workflow_precheck_invocation.md` | `.claude/hooks/README.md:124`; `.codex/hooks/README.md:184`; legacy audit notes | `runtime_consumer` | Yes | Hook README still points to old discipline path. Content likely overlaps with `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`. |
| `docs/disciplines/discipline_normal_output_minimization.md` | `tools/README.md:7`; tests/operations normal-output docs | `runtime_consumer`, `test_contract` | Yes | Tool-facing output contract points to old docs path. Migration should either move discipline or change `tools/README.md` target. |
| `docs/disciplines/discipline_facts_vs_interpretation.md` | `learning/workflow/proposals/WP-001-finding-cause-attribution.yaml:41` | `runtime_consumer`, `historical_reference` | Decision | Learning proposal uses it as source discipline. If active source moves, proposal schema/path rules need treatment. |
| `docs/disciplines/README.md` | docs notes, experiments, archive snapshots | `historical_reference`, possible `runtime_consumer` | Decision | It still describes active必読. If active index moves, README may remain as history with explicit non-canonical status. |
| active `docs/disciplines/discipline_*.md` set | `learning/workflow/schemas/proposal.schema.json`; `tools/self_improvement/proposal_model.py`; `tools/self_improvement/impact_analysis.py`; `tools/self_improvement/machine_verification.py` | `runtime_consumer`, `test_contract` | Yes if discipline root moves | Self-improvement currently models discipline proposals around `docs/disciplines/discipline_*.md`. A guidance move needs schema / model / MV-1 policy decision, not just link edits. |
| retired `docs/disciplines/archive/**` | `docs/disciplines/README.md`; archive references | `historical_reference` | Usually no | Keep archive unless docs archive policy changes. |

## Consumer Groups

### Deploy-Facing Consumers

| File | Current reference | Required treatment |
|---|---|---|
| `deploy-manifest.yaml` | Includes `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md`; includes `.reviewcompass/guidance/discipline_*` for migrated core guidance | Decide whether user guide remains deploy-facing docs or is split. Do not move without manifest update. |
| `CLAUDE.md` | Reads `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` | Update when adapter guidance is moved or absorbed into entry templates. |
| `templates/todo/TODO_NEXT_SESSION.template.md` | Mentions `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` and `docs/disciplines/` | Update if adapter guidance / active discipline index moves. |
| `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` | Mentions `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` | Update together with deployment guide split/move. |

### Runtime / Tool Consumers

| File | Current reference | Required treatment |
|---|---|---|
| `.claude/hooks/README.md` | `docs/disciplines/discipline_workflow_precheck_invocation.md` | Update or demote once precheck invocation source is guidance-side. |
| `.codex/hooks/README.md` | `docs/disciplines/discipline_workflow_precheck_invocation.md` | Same as Claude hook README. |
| `tools/README.md` | `docs/disciplines/discipline_normal_output_minimization.md`; commands for `docs/operations` / `docs/disciplines` lint | Update if normal output discipline moves; keep command examples only if docs paths remain lint targets. |
| `tools/check-workflow-action.py` | Treats `docs/operations/` and `docs/disciplines/` as strict post-write / mixing categories | Any relocation must update path classification policy or explicitly keep docs paths strict. |
| `tools/api_providers/review_triage.py` | Sensitive / target handling lists `docs/disciplines/` and `docs/operations/` | Review if guidance move changes what counts as high-sensitivity or canonical target. |
| `runtime/runtime_core/run_layout/README.md` | Points to `docs/operations/RUNTIME.md` | Update if runtime operation docs move. |
| `runtime/foundation/README.md`, `runtime/config/README.md` | Point to `docs/operations/FOUNDATION.md` | Update if foundation operation docs move. |

### Test / Schema Consumers

| File | Current reference | Required treatment |
|---|---|---|
| `tests/workflow-management/test_guidance_file_relocation_contract.py` | Encodes old forbidden docs paths and new `.reviewcompass/guidance` paths | Extend before migration to catch remaining old path uses. |
| `tests/deployment/test_deploy_manifest.py` | Encodes deployed guidance files and forbidden old guidance paths | Update if deployment guide or additional discipline files move into deploy package. |
| `learning/workflow/schemas/proposal.schema.json` | Patterns require `docs/disciplines/discipline_*.md` | Requires design decision before moving active discipline root. |
| `tools/self_improvement/proposal_model.py` | Regex requires `docs/disciplines/discipline_*.md` | Same as schema. |
| `tools/self_improvement/impact_analysis.py` | Scans `docs/disciplines/discipline_*.md` | Same as schema. |
| `tools/self_improvement/machine_verification.py` | MV-1 checks direct writes to `docs/disciplines/discipline_*` | Same as schema. |
| `tests/evaluation/test_t001_layout.py` | Uses `docs/operations/EVALUATION.md` | Update if feature operation doc moves. |
| `tests/foundation/test_t001_layout.py` | Uses `docs/operations/FOUNDATION.md` | Update if feature operation doc moves. |
| `tests/runtime/test_t001_layout.py` | Uses `docs/operations/RUNTIME.md` | Update if feature operation doc moves. |
| `tests/analysis/test_analysis_t001_layout.py` | Uses `docs/operations/ANALYSIS.md` | Update if feature operation doc moves. |

## Move Candidate Update Matrix

| Move candidate group | Must update consumers | Can remain historical |
|---|---|---|
| Adapter guidance (`WORKFLOW_NAVIGATION_FOR_CLAUDE.md`, `WORKFLOW_NAVIGATION_FOR_CODEX.md`) | `CLAUDE.md`; `templates/todo/TODO_NEXT_SESSION.template.md`; deployment / entry templates if they materialize these paths | docs/notes, review-run records, sessions, stages/completed |
| Deployment guide split (`DEPLOYMENT.md`, `INITIAL_DEPLOYMENT_USER_GUIDE.md`) | `deploy-manifest.yaml`; `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md`; deployment tests | historical review-run records and old deployment discussions |
| Feature operation docs (`FOUNDATION.md`, `RUNTIME.md`, `EVALUATION.md`, `ANALYSIS.md`, `SELF_IMPROVEMENT.md`, `CONFORMANCE_EVALUATION.md`, `WORKFLOW_MANAGEMENT.md`) | feature-local README / tests / fixtures that point to docs path | reconstruction plan, old sessions, review-runs |
| Tool-contract doc (`SELF_IMPROVEMENT_MACHINE_VERIFICATION.md`) | self-improvement CLI docs/tests if any explicit active use is confirmed | sessions, notes |
| Active discipline docs | `learning/workflow/schemas/proposal.schema.json`; `tools/self_improvement/*`; hook READMEs; `tools/README.md`; guidance relocation tests | old TODO snapshots, sessions, review-runs, archive |
| Archived disciplines | None unless archive policy changes | archive and old history |

## GRC-3 Test Targets Suggested by Audit

1. Adapter entrypoints must not point to `docs/operations/WORKFLOW_NAVIGATION_FOR_*` after adapter relocation.
2. `deploy-manifest.yaml` must not include old `docs/operations` deploy-facing guidance unless explicitly classified as user-facing docs.
3. Active discipline source paths must have a single canonical root. If `.reviewcompass/guidance` wins, self-improvement schema/model/tests must reject stale `docs/disciplines/discipline_*.md` for active discipline changes or explicitly treat them as historical.
4. Hook READMEs and templates must not point to old discipline paths when guidance-side equivalents exist.
5. Feature operation docs must either remain in `docs/operations` as human reference or move with all README/test references updated; no mixed source-of-truth.

## Open Decisions

1. Should adapter guidance live in `.reviewcompass/guidance`, or be absorbed into entry templates such as `AGENTS.md` / `CLAUDE.md` generation?
2. Should `INITIAL_DEPLOYMENT_USER_GUIDE.md` remain deploy-facing user documentation under `docs/operations`, or split into user docs plus LLM-facing guidance?
3. Should active discipline paths remain `docs/disciplines/discipline_*.md` for self-improvement workflow ownership, while only selected deploy-facing disciplines move to `.reviewcompass/guidance`?
4. Should feature operation docs remain under `docs/operations`, or move to `.reviewcompass/specs/<feature>/operations.md`?
5. Should effective prompt artifacts containing old paths be regenerated as part of freshness audit, rather than edited directly?
