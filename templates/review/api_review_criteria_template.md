---
criteria_id: <feature>-<phase>-<topic>-review-criteria
phase: <requirements|design|tasks|implementation|post-write|other>
gate: <stages/...#... or operation>
intended_review_target:
  - <path-to-actual-target-document>
source_materials:
  note: "Front matter records provenance only. Model-readable source material must be embedded in the body."
  embedded:
    - <source-material-key-1>
    - <source-material-key-2>
user_review_requirements:
  note: "Model-readable user review requirements must be preserved in the body and mapped to the review task, checks, scope, and finding policy."
  provided_by: <user|workflow|operator>
status: draft_for_prompt_quality_review
---

# <Feature / Phase / Topic> Review Criteria

## Review Task

Review `<path-to-actual-target-document>` for `<phase / gate>`.

The review question is:

<Ask the non-leading review question. For vertical intent transfer, ask whether upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer are carried into the target without omission, weakening, contradiction, unsupported addition, or drift.>

This prompt should contain one primary judgment question. If the review requires multiple independent cluster, finding, acceptance, or design-policy judgments, create one prompt per judgment item and review each prompt separately.

Return findings only when the review target itself is deficient for this review question.

## Why This Review Exists

<Explain why this review-run is needed. Include reopen / post-write / approval context when relevant. State whether older runs are stale or invalid, and why.>

<If there was a prior prompt or target-selection failure, explicitly state how this prompt prevents repeating it.>

## User Review Requirements

Preserve the review requirements that triggered this prompt.

Review purpose:

- <Defect detection / acceptance judgment / upstream transfer check / regression check / comparison / other>

Review object:

- <Artifact, prompt, design proposal, repair proposal, implementation diff, or other object under review>

Review focus:

- <Focus 1>
- <Focus 2>

Scope boundaries:

- In scope: <What must be reviewed>
- Out of scope: <What must not be reviewed yet>

Judgment item granularity:

- <Single cluster / finding / artifact / decision item this prompt judges>
- <If there are multiple items, split them into separate prompt files instead of combining them here>

Source materials required by the user or workflow:

- <Material 1>
- <Material 2>

Output requirements:

- <findings / severity / acceptance judgment / concerns / repair recommendations / comparison axes / other>

Prohibited actions and authority limits:

- <Do not authorize commit, push, phase completion, human approval delegation, or unapproved specification changes unless explicitly in scope and allowed by the governing workflow.>

External API material policy:

- <State whether the user approved API review / proxy_model execution.>
- <Confirm that the prompt includes only review-relevant repository materials and excludes API keys, tokens, passwords, personal identifiers, third-party non-sendable confidential material, and unnecessary full logs.>
- <If any required material is sensitive, describe the redaction or abstraction used.>

Requirement-to-prompt mapping:

- <User requirement 1> -> <Review task / Required check / Out of scope / Finding policy item>
- <User requirement 2> -> <Review task / Required check / Out of scope / Finding policy item>

If any user requirement is ambiguous, state the assumption explicitly and keep it reviewable.

## Required Disciplines

Apply these prompt and review disciplines:

- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`: include appropriate information, a non-leading question, appropriate scope, fixed output contract, and sensitive-information checks.
- `<phase-specific discipline refs>`: <summarize the phase/gate-specific requirements the model needs to apply.>

## Review Target

The review target is only:

- `<path-to-actual-target-document>`

Do not treat this criteria file, a review wrapper, or an author-written summary as a substitute for the target document.

## Source Materials

Use the following source materials only for background and intent-transfer checking. Do not judge these source materials as targets unless the review task explicitly says so.

### <Source Material 1>

Purpose:

<Model-readable purpose.>

Responsibility boundaries:

- <Boundary 1>
- <Boundary 2>

Acceptance criteria / required transfer:

- <Criterion 1>
- <Criterion 2>

Forbidden or high-risk drift:

- <Forbidden item 1>
- <Forbidden item 2>

Unresolved or deferred items:

- <Item, or "None known">

Intended target-phase transfer:

- <What the target document must carry forward.>

### <Source Material 2>

<Repeat the same structure or remove this section.>

## Required Checks

1. <Check 1>
2. <Check 2>
3. <Check 3>
4. Check that the target satisfies the preserved user review requirements without narrowing, broadening, or replacing the requested review question.
5. Check that this prompt does not combine multiple independent judgments in a way that diffuses attention or weakens item-specific evidence.

## Out Of Scope

- Do not judge downstream phase correctness unless a target omission would force downstream invention.
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- Do not treat source-material defects as target findings unless they cause a target transfer defect.
- Do not infer additional review objectives beyond the preserved user review requirements unless the criteria explicitly marks them as workflow-required checks.

## Finding Policy

- Report `CRITICAL` if the prompt or target would bypass a user-stated prohibited action or authority limit.
- Report `CRITICAL` for defects that would allow bypassing human-only approval, irreversible-operation boundaries, or active-scope evidence.
- Report `ERROR` when the criteria omits, weakens, broadens, or replaces a user-stated review requirement in a way that changes the review outcome.
- Report `ERROR` when required upstream purpose, responsibility boundary, acceptance criterion, forbidden action, or target-phase transfer is missing, weakened, contradicted, or replaced by unsupported target behavior.
- Report `ERROR` when the target leaves an authority boundary ambiguous enough that downstream phases must invent policy.
- Report `WARN` for ambiguity likely to force repeated manual judgment, weak traceability, unclear schema/state boundaries, or overclaiming completion.
- Report `INFO` only for non-blocking traceability improvements.
- Return `findings: []` only when the target is traceable, internally consistent, correctly scoped, and sufficiently grounded for the downstream phase.
