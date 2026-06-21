# Effective Prompt: post_write_policy_violation

## Decision Point

- group: next_action_kind
- id: post_write_policy_violation

## Meaning

`post_write_policy_violation` is a safety stop. The current worktree contains
post-write verification targets together with files that are not allowed to be
changed during that verification flow.

This point is not a review execution point. Do not start an API review-run from
this state.

## Allowed Operation

Run or report the equivalent of `post_write_policy_violation.inspect`.

The inspection may classify the current dirty files and explain which files are
post-write targets, which files are forbidden for the current post-write flow,
and what must be resolved before normal post-write verification can continue.

## Forbidden Operations

- `run_post_write_review`
- `create_post_write_manifest`
- treat an invalid review-run as post-write verification evidence
- commit
- push

## Required Boundary

API prompt generation and API review-run execution are allowed only after the
workflow state has changed so that `next_action.kind == post_write_verification`.

While the current kind is `post_write_policy_violation`, the next step is to
resolve the policy violation or record a valid side-track/repair plan. Do not
compose a review prompt from source refs at this point.

## Output Contract

Report:

- current state: `post_write_policy_violation`
- forbidden files
- target files, if any
- allowed next operation
- forbidden next operations
- stop condition before returning to post-write verification
