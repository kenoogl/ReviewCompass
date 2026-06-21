# Guidance File Move Active Reference Inventory

Date: 2026-06-21

Baseline:

- HEAD after rollback: `ba066a08`
- Migration plan: `docs/notes/working/2026-06-21-guidance-file-move-redo-plan.md`
- Previous failed attempt preserved at branch:
  `codex/failed-guidance-move-d4517c8c`

## Baseline Assertions

Checked before inventory:

- `git rev-parse --short HEAD` returned `ba066a08`.
- `git status --short` was clean before copying back the plan memo.
- The 14 legacy source files existed under `docs/operations/` and
  `docs/disciplines/`.
- `.reviewcompass/guidance/` did not exist.

## Move Map

Move these files to `.reviewcompass/guidance/`:

`docs/operations/`:

- `WORKFLOW_DISCIPLINE_MAP.yaml`
- `WORKFLOW_NAVIGATION.md`
- `WORKFLOW_PRECHECK.md`
- `WORKFLOW_PRECHECK_DETAILS.md`
- `REOPEN_PROCEDURE.md`
- `SESSION_WORKFLOW_GUIDE.md`
- `API_REVIEW_PROMPT_QUALITY.md`
- `COMMIT_OPERATION_CARD.md`
- `INITIAL_SETUP_LLM_GUIDE.md`

`docs/disciplines/`:

- `discipline_approval_operation.md`
- `discipline_llm_as_judge_prompting.md`
- `discipline_post_write_verification.md`
- `discipline_workflow_state_truth_source.md`
- `discipline_yaml_audit.md`

## Inventory Commands

Primary exact-path search:

```bash
rg -l "docs/operations/(WORKFLOW_DISCIPLINE_MAP.yaml|WORKFLOW_NAVIGATION.md|WORKFLOW_PRECHECK.md|WORKFLOW_PRECHECK_DETAILS.md|REOPEN_PROCEDURE.md|SESSION_WORKFLOW_GUIDE.md|API_REVIEW_PROMPT_QUALITY.md|COMMIT_OPERATION_CARD.md|INITIAL_SETUP_LLM_GUIDE.md)|docs/disciplines/(discipline_approval_operation.md|discipline_llm_as_judge_prompting.md|discipline_post_write_verification.md|discipline_workflow_state_truth_source.md|discipline_yaml_audit.md)" AGENTS.md TODO_NEXT_SESSION.md .codex .claude templates docs/operations docs/disciplines .reviewcompass/specs tools tests deploy-manifest.yaml runtime analysis evaluation --glob '!tools/experiments/**' --glob '!.reviewcompass/specs/*/reviews/**' --glob '!.reviewcompass/specs/*/conformance/**'
```

Filename and relative-link search:

```bash
rg -l "WORKFLOW_DISCIPLINE_MAP.yaml|WORKFLOW_NAVIGATION.md|WORKFLOW_PRECHECK.md|WORKFLOW_PRECHECK_DETAILS.md|REOPEN_PROCEDURE.md|SESSION_WORKFLOW_GUIDE.md|API_REVIEW_PROMPT_QUALITY.md|COMMIT_OPERATION_CARD.md|INITIAL_SETUP_LLM_GUIDE.md|discipline_approval_operation.md|discipline_llm_as_judge_prompting.md|discipline_post_write_verification.md|discipline_workflow_state_truth_source.md|discipline_yaml_audit.md" AGENTS.md TODO_NEXT_SESSION.md .codex .claude templates docs/operations docs/disciplines .reviewcompass/specs tools tests deploy-manifest.yaml runtime analysis evaluation --glob '!tools/experiments/**' --glob '!.reviewcompass/specs/*/reviews/**' --glob '!.reviewcompass/specs/*/conformance/**'
```

Runtime import and programmatic path search:

```bash
rg -n "from tools\\.|import tools\\.|docs/operations|docs/disciplines|Path\\([^\\n]*docs|/ \\\"docs\\\"|/ 'docs'" tools/api_providers tools/check-workflow-action.py tools/guarded-git-commit.py tools/document_link_lint.py tools/deployment_independence_lint.py deploy-manifest.yaml
```

## Active Runtime

These are blocking active runtime references. They must be updated before legacy
file deletion:

- `.codex/hooks/review-prompt-guide-inject.sh`
  - Reads `docs/disciplines/discipline_llm_as_judge_prompting.md`.
  - Previous failure: hook returned empty output after deletion.
- `.claude/hooks/review-prompt-guide-inject.sh`
  - Same issue as Codex hook.
- `.codex/hooks/pre-bash-precheck.sh`
  - Comment references `docs/operations/WORKFLOW_PRECHECK.md`; not runtime path
    logic, but active shipped hook documentation.
- `.claude/hooks/pre-bash-precheck.sh`
  - Same comment reference.
- `tools/check-workflow-action.py`
  - `DEFAULT_DISCIPLINE_MAP_PATH = "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"`.
  - Built-in required discipline paths include moved `docs/operations/*` and
    `docs/disciplines/*`.
  - Post-move behavior must use `.reviewcompass/guidance/*`.
- `tools/document_link_lint.py`
  - Built-in contract references currently point to
    `docs/operations/WORKFLOW_PRECHECK*.md`.
  - Must be updated if canonical location changes.
- `tools/api_providers/*.py`
  - Import closure must be checked in deploy package.
  - Previous failed attempt missed `tools.normal_output`.

## Active Deploy Manifest And Deploy Docs

Blocking active deploy references:

- `deploy-manifest.yaml`
  - Includes moved `docs/operations/*` files and `docs/disciplines/discipline_*.md`.
  - Must include `.reviewcompass/guidance/*` instead.
  - Must include transitive runtime imports needed by deployed entry points,
    including but not limited to `tools.normal_output`.
- `docs/operations/DEPLOYMENT.md`
  - Lists moved guidance files under legacy `docs/operations` /
    `docs/disciplines`.
  - Must document `.reviewcompass/guidance/*` as the deploy guidance location.
- `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md`
  - Relative link to `INITIAL_SETUP_LLM_GUIDE.md` must be rechecked after move.

## Active Templates

Blocking active template references:

- `templates/entry/AGENT_ENTRY.template.md`
  - Points users to `docs/operations/WORKFLOW_NAVIGATION.md`.
- `templates/todo/TODO_NEXT_SESSION.template.md`
  - Points to `docs/operations/WORKFLOW_NAVIGATION.md` and
    `docs/operations/SESSION_WORKFLOW_GUIDE.md`.
- `templates/hooks/pre-bash-precheck.sh.template`
  - Recovery comment points to `docs/operations/INITIAL_SETUP_LLM_GUIDE.md`.
- `templates/review/api_review_criteria_template.md`
  - Points to `docs/disciplines/discipline_llm_as_judge_prompting.md`.
- `templates/review/api_review_prompt_quality_criteria_template.md`
  - Contains filename-only references to `SESSION_WORKFLOW_GUIDE.md`; must be
    verified after move.

## Active Docs / Entry Points

Blocking active documentation references:

- `AGENTS.md`
  - Current work-completion contract points to
    `docs/operations/SESSION_WORKFLOW_GUIDE.md`.
- `TODO_NEXT_SESSION.md`
  - Points to workflow navigation, session guide, and discipline map under
    `docs/operations`.
- `docs/disciplines/README.md`
  - Relative links to moved discipline files.
- Remaining active docs under `docs/operations/` that refer to moved files:
  - `WORKFLOW_DISCIPLINE_MAP.yaml`
  - `WORKFLOW_NAVIGATION.md`
  - `WORKFLOW_PRECHECK.md`
  - `WORKFLOW_PRECHECK_DETAILS.md`
  - `SESSION_WORKFLOW_GUIDE.md`
  - `API_REVIEW_PROMPT_QUALITY.md`
  - `WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
  - `WORKFLOW_NAVIGATION_FOR_CODEX.md`

These internal references should be updated when the canonical source becomes
`.reviewcompass/guidance/*`.

## Active Tests

Tests that currently assert legacy guidance paths and must be updated or
expanded before deletion:

- `tests/operations/test_session_workflow_guide.py`
- `tests/tools/test_effective_prompt_contract.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_commit_single_turn_policy_docs.py`
- `tests/tools/test_document_link_lint.py`
- `tests/tools/test_workflow_management_implementation_triad_prep.py`
- `tests/tools/test_workflow_management_task_granularity.py`
- `tests/tools/test_session_record_contract.py`
- `tests/hooks/test_pre_bash_precheck.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/deployment/test_deploy_manifest.py`
- `tests/deployment/test_build_deploy_package.py`
- `tests/deployment/test_deploy_package_external_app_smoke.py`
- `tests/conformance-evaluation/test_contract_ownership.py`
- `tests/fixtures/conformance-evaluation/*.yaml`

Required new/updated coverage:

- Hook guide injection must read
  `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`.
- Operation docs tests must read `.reviewcompass/guidance/*`.
- Deployment tests must reject moved legacy source includes.
- Deployment smoke must catch any missing transitive import from deploy-included
  entry points.

## Active Specs / Contracts

These old-path hits are active contract candidates and should not be treated as
historical without review:

- `.reviewcompass/specs/workflow-management/requirements.md`
  - Requirement 2 still names
    `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`.
- `.reviewcompass/specs/workflow-management/design.md`
  - Multiple active design sections name moved `docs/operations/*` paths.
  - This includes layout tree, precheck contracts, discipline map contract,
    deployment guidance, and prompt length source references.
- `.reviewcompass/specs/workflow-management/tasks.md`
  - T-004 and related task outputs name moved `docs/operations/*` paths.
- `.reviewcompass/specs/workflow-management/post-write-verification-spec.yaml`
  - Names `docs/disciplines/discipline_post_write_verification.md` and
    `docs/disciplines/discipline_yaml_audit.md`.
- `.reviewcompass/specs/workflow-management/yaml-audit-spec.yaml`
  - Names `docs/disciplines/discipline_yaml_audit.md`.
- `.reviewcompass/specs/self-improvement/design.md`
  - Links to moved `discipline_approval_operation.md`.
- `.reviewcompass/specs/self-improvement/tasks.md`
  - Contains workflow-management resolver update references around
    `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`.

Decision for redo:

- Treat these as active specs/contracts unless a specific hit is explicitly
  classified as historical evidence.
- Update active contract text when the canonical location changes.
- If a section is mixed historical/active, classify per hit.
- If unclear, stop and ask before deleting legacy files.

## Historical / Evidence Candidates

These may remain unchanged only if their role is preserving past state:

- `.reviewcompass/evidence/**`
- `.reviewcompass/specs/*/reviews/**`
- `.reviewcompass/post-write-verification/**`
- `docs/reviews/**`
- `docs/sessions/**`
- `docs/archive/**`
- `docs/notes/**`
- `tools/experiments/**`

Special case:

- `.reviewcompass/specs/*/conformance/**` contains dated conformance evidence
  and handoff packages. Treat dated evidence as historical, but do not globally
  exclude the directory if a file is acting as a current contract.

## Pre-Deletion Blocking Rule

Before deleting the legacy copies, old moved-path references may remain only in
the historical/evidence candidates above, or in entries explicitly approved by
the user.

Any old moved-path hit in these surfaces blocks deletion:

- `AGENTS.md`
- `TODO_NEXT_SESSION.md`
- `.codex/**`
- `.claude/**`
- `templates/**`
- `docs/operations/**`
- `docs/disciplines/**`
- `.reviewcompass/guidance/**`
- `.reviewcompass/specs/*/{requirements,design,tasks}.md`
- current behavior-contract YAML files
- `tools/**` except `tools/experiments/**`
- `tests/**`
- `deploy-manifest.yaml`
- `runtime/**`
- `analysis/**`
- `evaluation/**`

## Next Planned Step

Add or update tests that fail while the legacy active references remain. Do not
copy files into `.reviewcompass/guidance/` and do not delete legacy files until
the active-reference and deploy import-closure tests exist.
