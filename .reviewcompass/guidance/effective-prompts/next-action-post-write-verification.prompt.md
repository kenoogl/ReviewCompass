# Effective Prompt: post_write_verification

## Decision Point

- group: next_action_kind
- id: post_write_verification

## Meaning

`post_write_verification` is the API review execution point. The current worktree
contains post-write verification targets and no policy violations are blocking
the flow.

This is the point at which an API review-run may be prepared and executed.

## Allowed Operation

Prepare and execute a post-write API review-run.

Steps:
1. Build a source bundle containing the full text of the target file(s) and
   any referenced source materials.
2. Generate a structured review prompt from the source bundle.
3. Run the prompt audit to confirm the prompt meets quality requirements.
4. Execute the API review-run against the audited prompt.
5. Record the result as a post-write manifest.

## Forbidden Operations

- Summarize the target file body instead of using full text.
- Use path-only references as a substitute for source material content.
- Skip the prompt audit and proceed directly to the API runner.
- Treat an audit-rejected prompt as a valid review basis.
- Commit before the manifest is completed and accepted.

## Required Boundary

Do not start an API review-run when `next_action.kind` is anything other than
`post_write_verification`. In particular, `post_write_policy_violation` is a
blocking state that must be resolved first.

## Output Contract

The review-run must produce a manifest that records:

- target files and their SHA-256 digests
- source materials and their SHA-256 digests
- verifier model and run identifier
- per-entry review result (verdict, findings)
- manifest SHA-256 for later audit
