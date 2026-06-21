# ReviewCompass guidance file move redo plan

Date: 2026-06-21

## Purpose

Redo the guidance file placement change from the pre-move planning state.

The previous attempt moved/copied guidance files into `.reviewcompass/guidance/`
and then deleted the legacy `docs/operations` / `docs/disciplines` copies, but
the verification scope was too narrow. It missed active hook references,
operation tests, deployment smoke behavior, template references, document links,
and deploy-manifest dependency completeness.

This plan is stored outside git before rollback so it can be copied back after
resetting the repository to the pre-move state.

## Rollback Target

Reset target: `ba066a08 Record effective prompt audit plans`

Reason:

- `08c26135 Add deploy guidance layout` already adds `.reviewcompass/guidance/*`.
- `d4517c8c Remove legacy guidance duplicates` deletes the old copies and leaves
  unresolved references.
- Therefore the pre-move planning state is the parent of `08c26135`, namely
  `ba066a08`.

## Failure Lessons From Previous Attempt

The redo must treat this as a repository-wide placement migration, not as a
small file deletion.

Observed failures:

- `.codex/hooks/review-prompt-guide-inject.sh` and
  `.claude/hooks/review-prompt-guide-inject.sh` still read
  `docs/disciplines/discipline_llm_as_judge_prompting.md`, so review prompt
  guide injection silently returns no context.
- `tests/hooks -q` failed with five failures, including the guide injection hook,
  commit / push precheck hook expectations, and previous session capture.
- `tests/operations -q` failed because tests still read deleted
  `docs/operations/*` files directly.
- `tests/deployment -q` failed because the deployment package smoke test missed
  `tools.normal_output`, required by deployed API provider tools.
- Deploy-facing templates still contained old paths:
  - `templates/entry/AGENT_ENTRY.template.md`
  - `templates/todo/TODO_NEXT_SESSION.template.md`
  - `templates/hooks/pre-bash-precheck.sh.template`
  - `templates/review/api_review_criteria_template.md`
- `AGENTS.md` still referenced `docs/operations/SESSION_WORKFLOW_GUIDE.md`.
- `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` and
  `docs/disciplines/README.md` contained links to moved files.
- Existing link and deployment independence linters exposed additional misses.
- The previous post-write review focused on a narrow target set and did not
  force hooks, tests, templates, deploy package, and active docs through one
  integrated migration gate.
- Literal path grep is not sufficient. The deployment smoke failure also showed
  a missing Python import (`tools.normal_output`) that was not a moved-path
  string reference. The redo must inspect deploy-time transitive imports, not
  only old guidance paths.
- "Historical" and "experiment-only" are not safe labels unless they are
  defined mechanically. The redo must record why each remaining old reference is
  non-blocking.

## Plan Review Record

This plan was reviewed by API before rollback.

Review run:

- `/private/tmp/reviewcompass-guidance-move-redo-plan-api-review-run`

Variant:

- `api_review_prompt_quality_2way`

Roles:

- adversarial: `claude-sonnet-4-6`
- judgment: `gemini-3.1-pro-preview`

Result summary:

- `gemini-3.1-pro-preview`: no findings
- `claude-sonnet-4-6`: 9 findings (`ERROR` 3, `WARN` 5, `INFO` 1)

Applied changes from the review:

- Add transitive import / runtime dependency closure checks for deploy package
  tools.
- Define concrete active-reference inclusion and historical exclusion rules.
- Require post-reset baseline assertions before starting edits.
- Require recorded classification before editing current specs or contracts.
- Add explicit resolution paths for unclear spec classifications.
- Split the expected commit structure more finely.

## Canonical Move Map

Move these files to `.reviewcompass/guidance/` and remove the old copies only
after all active references and tests are updated.

From `docs/operations/`:

- `WORKFLOW_DISCIPLINE_MAP.yaml`
- `WORKFLOW_NAVIGATION.md`
- `WORKFLOW_PRECHECK.md`
- `WORKFLOW_PRECHECK_DETAILS.md`
- `REOPEN_PROCEDURE.md`
- `SESSION_WORKFLOW_GUIDE.md`
- `API_REVIEW_PROMPT_QUALITY.md`
- `COMMIT_OPERATION_CARD.md`
- `INITIAL_SETUP_LLM_GUIDE.md`

From `docs/disciplines/`:

- `discipline_approval_operation.md`
- `discipline_llm_as_judge_prompting.md`
- `discipline_post_write_verification.md`
- `discipline_workflow_state_truth_source.md`
- `discipline_yaml_audit.md`

Do not move unrelated remaining files under `docs/operations/` or
`docs/disciplines/`.

## Pre-Move Inventory Gate

Before editing, produce and inspect an active-reference inventory.

After rollback and before any migration edit, assert the baseline:

- `git rev-parse --short HEAD` returns `ba066a08`.
- The 14 source files listed in the move map exist at their legacy paths.
- `.reviewcompass/guidance/` either does not exist or contains no moved guidance
  files from the previous attempt.
- `git status --short` is clean, except for the copied-back plan memo if it has
  already been intentionally restored.

Required grep set:

- Exact old paths for every moved file.
- Directory-level references to `docs/operations/` and `docs/disciplines/`.
- Markdown relative links from `docs/operations` and `docs/disciplines`.
- Hook and template references under `.codex`, `.claude`, and `templates`.
- Test references under `tests` and tool tests.
- Deploy manifest includes and deploy-facing templates.
- Current feature specs under `.reviewcompass/specs/*/{requirements,design,tasks}.md`
  and active YAML contracts.
- Python imports and programmatic path construction in deploy-included runtime
  tools, including:
  - `from tools...` / `import tools...`
  - `Path(...) / "docs" / "operations"` style construction
  - `"docs/operations"` / `"docs/disciplines"` fragments assembled across
    variables
  - modules imported by `tools/api_providers/*.py`, `tools/check-workflow-action.py`,
    and deploy-included helper modules.

Classify each hit:

- `active_runtime`: scripts, hooks, tools, deploy package behavior.
- `active_template`: files copied into external apps.
- `active_test`: tests that assert current source paths or behavior.
- `active_doc`: current documentation used by operators or setup.
- `active_spec`: current spec / contract source that should remain true.
- `historical_evidence`: review evidence, archived prompts, session records.
- `experiment_only`: experiments or scratch prompts not used in runtime.

Only `historical_evidence` and clearly `experiment_only` references may remain
unchanged. Everything else must be updated or explicitly documented as a
follow-up with rationale.

Concrete classification rules:

- `historical_evidence` may include only review-run evidence, raw model
  responses, session transcripts, archived reviews, and post-write records whose
  purpose is to preserve past state. Examples include `.reviewcompass/evidence/**`,
  `.reviewcompass/specs/*/reviews/**`, `docs/reviews/**`, `docs/sessions/**`,
  and `docs/archive/**`.
- `experiment_only` may include only files that are not referenced from hooks,
  templates, deploy manifest, tests, active docs, current specs, or runtime code.
  The inventory must record the command or reasoning used to establish that it is
  not reachable from those active surfaces.
- `active_spec` must be used for current requirements, design, tasks, behavior
  contracts, YAML contracts, and deploy contracts unless the specific section is
  explicitly marked as historical evidence.
- Mixed files that contain both historical notes and active contract text must be
  classified per hit, not only per file.

Pre-deletion active-reference grep must run over these included active surfaces:

- `AGENTS.md`
- `TODO_NEXT_SESSION.md`
- `.codex/**`
- `.claude/**`
- `templates/**`
- `docs/operations/**`
- `docs/disciplines/**`
- `.reviewcompass/guidance/**`
- `.reviewcompass/specs/*/requirements.md`
- `.reviewcompass/specs/*/design.md`
- `.reviewcompass/specs/*/tasks.md`
- `.reviewcompass/specs/**/*.yaml` except review-run evidence paths
- `tools/**` except `tools/experiments/**`
- `tests/**`
- `deploy-manifest.yaml`
- runtime deploy assets under `runtime/**`, `analysis/**`, and `evaluation/**`

Allowed exclusions for old moved-path grep:

- `.reviewcompass/evidence/**`
- `.reviewcompass/specs/*/reviews/**`
- `.reviewcompass/specs/*/conformance/**` only when the file is a dated
  conformance evidence record rather than a current contract
- `.reviewcompass/post-write-verification/**`
- `docs/reviews/**`
- `docs/sessions/**`
- `docs/archive/**`
- `docs/notes/**`
- `tools/experiments/**`

Any old moved-path hit outside the allowed exclusions blocks deletion unless the
inventory records an explicit user-approved reason.

## Deploy Dependency Closure Gate

Before deleting legacy files, verify that deploy-included Python entry points can
import their transitive dependencies from the built package alone.

Minimum entry points:

- `tools/api_providers/run_role.py`
- `tools/api_providers/run_review.py`
- `tools/api_providers/prepare_post_write_review.py`
- `tools/check-workflow-action.py`
- `tools/guarded-git-commit.py`
- `tools/document_link_lint.py`
- `tools/deployment_independence_lint.py`
- any other Python file explicitly included by `deploy-manifest.yaml`

The test must not only check `tools.normal_output`; it must fail for any missing
transitive import in the deploy package.

Acceptable implementation options:

- A deployment test that builds the package, sets `PYTHONPATH` to the package
  root, and imports or executes the deploy-included entry points from an external
  app root.
- A static import-closure helper, if it is validated by the external-app smoke.

The external-app smoke remains required even if static import closure passes.

## Redo Execution Plan

1. Add tests first.

   - Add or update tests that fail while old active references remain.
   - Include hook tests for review prompt guide injection using
     `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`.
   - Update operation tests to read `.reviewcompass/guidance/*`.
   - Update deployment manifest tests to require `.reviewcompass/guidance/*`
     and reject moved legacy sources.
   - Add deploy smoke and import-closure coverage for all imported modules
     required by included API provider tools and other deploy entry points.
   - Add or extend template checks so deploy-facing templates do not point to
     deleted docs paths.
   - Add link-lint coverage over `.reviewcompass/guidance`, active docs,
     hooks, templates, and deploy manifest.

2. Confirm tests fail for the right reason.

   - Run the focused tests before moving files.
   - Confirm failures identify old paths, missing deploy dependency, or old
     canonical path assumptions.

3. Copy / move guidance files.

   - Create `.reviewcompass/guidance/`.
   - Copy the 14 mapped files into the new location.
   - Keep old copies temporarily while references are updated.

4. Update active references.

   - Update hooks in `.codex/hooks` and `.claude/hooks`.
   - Update deploy-facing templates under `templates`.
   - Update `AGENTS.md`, active operation docs, and discipline README links.
   - Update tests and helper code to use `.reviewcompass/guidance`.
   - Update `deploy-manifest.yaml` to include `.reviewcompass/guidance/*`
     and all runtime dependencies required by deploy smoke.
   - Update current specs / active contracts only after recording their
     hit-level classification in the inventory. Do not mechanically rewrite
     review evidence.

   For specs and contracts:

   - If a hit is active contract text, update it before deleting the old file.
   - If a hit is historical evidence, leave it unchanged and record why.
   - If a hit is ambiguous, stop and escalate before editing or deleting.

5. Delete old copies only after active references are clean.

   - Run active-reference grep against non-historical locations.
   - Run document link lint.
   - Run deploy package verify and external-app smoke.
   - Run deploy import-closure checks.
   - Only then remove the 14 legacy source files.

6. Run post-delete verification.

   Required commands:

   - `git status --short`
   - `tools/check-workflow-action.py next --json`
   - focused tests for moved paths and hooks
   - `tests/operations -q`
   - `tests/hooks -q`
   - `tests/deployment -q`
   - targeted tool/provider tests touched by deletion handling
   - full `pytest -q` if runtime permits
   - `tools/document_link_lint.py --json` over active docs, hooks, templates,
     `.reviewcompass/guidance`, and deploy manifest
   - `tools/deployment_independence_lint.py --json` over deploy-facing assets
   - deploy package build with `--clean --verify --smoke-external-app-root`
   - deploy package import-closure check over deploy-included Python entry
     points

7. Review and record.

   - Record the active-reference inventory and classification.
   - Record test results.
   - Run post-write review with a target that includes:
     - move map,
     - active-reference inventory,
     - hook behavior,
     - deploy smoke,
     - operation tests,
     - template references,
     - link lint output.
     - deploy import-closure output.

## Stop Conditions

Stop and report before deleting old copies if any of the following remain:

- Active hooks or templates still point to moved legacy paths.
- Active tests still read moved legacy paths.
- Deploy smoke fails.
- Document link lint finds missing moved files in active docs.
- Any runtime import needed by the deployed package is absent from manifest.
- Specs contain old paths whose status is unclear between active contract and
  historical evidence.

Resolution paths:

- For unclear spec / contract status, stop and ask the user to classify the hit
  before editing or deleting.
- For a remaining old-path hit in an active surface, update the reference or add
  a dedicated follow-up only with explicit user approval.
- For a missing deploy import, update `deploy-manifest.yaml` and add/adjust the
  import-closure test before continuing.
- For hook or template failures, stop before deleting old copies.

## Expected Commit Structure

Use small commits:

1. Planning memo and active-reference inventory.
2. Tests for guidance relocation, active-reference gates, hooks, templates, and
   deploy import closure.
3. Add `.reviewcompass/guidance` copies only.
4. Update runtime hooks and deploy-facing templates.
5. Update tests, active docs, AGENTS / TODO, and current contracts classified as
   active.
6. Update deploy manifest and deploy smoke / import-closure support.
7. Delete old source copies after passing active-reference gates.
8. Post-write review evidence and TODO handoff.

Avoid combining copy, reference rewrite, deletion, and evidence into one large
commit.
