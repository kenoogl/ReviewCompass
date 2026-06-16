# post-write verification target: deployable commit UX

## User decision

- Current commit approval UX is too heavy for third-party deployment.
- The safety model may keep nonce / digest / execution delegation internally, but the visible operation must be deployable:
  - user says `コミット`;
  - agent presents staged target, digest, nonce, and expiry;
  - user says `承認`;
  - agent completes the commit without exposing low-level record / delegation steps.
- Old consumed, expired, or malformed runtime approval records should not repeatedly make the next commit experience bad.
- EOF waiting after `承認\n` is also bad; approval should be consumed as one line.
- Reflect this in the design memo and implement immediately.

## Written changes

### Design and task memo

- `.reviewcompass/specs/workflow-management/requirements.md`
  - Requirement 4 acceptance 8 now accepts `承認` as the second commit approval utterance after a challenge has been presented.
  - It states that `guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` performs record / delegation / precheck / commit as one ordered operation.
- `.reviewcompass/specs/workflow-management/design.md`
  - §2.1 now says `prepare` invalidates old runtime approval / delegation records so stale records do not degrade normal commit UX.
  - §2.2 now defines the deployable two-turn UX and the guarded commit wrapper that reads one approval line without waiting for EOF.
- `.reviewcompass/specs/workflow-management/tasks.md`
  - T-004/T-006/T-011 responsibilities and test requirements include the one-line guarded wrapper and stale delegation cleanup.

### User-facing operation docs/templates

- `TODO_NEXT_SESSION.md`
- `templates/todo/TODO_NEXT_SESSION.template.md`
- `templates/entry/AGENT_ENTRY.template.md`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`

These now describe the visible operation as:

1. `コミット` means prepare and present staged target / digest / nonce / expiry.
2. `承認` means approve the presented content and LLM commit execution delegation.
3. The agent uses `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin`.
4. Low-level record / delegation commands are not exposed to normal third-party users.

### Implementation and tests

- `tools/guarded-git-commit.py`
  - Adds `--approval-nonce`.
  - Adds `--approval-source-text-line-stdin`.
  - Reads only one stdin line, then internally creates staged content approval and execution delegation before running precheck and commit.
- `tools/check_workflow_action/commit_approval.py`
  - `prepare` invalidates old runtime approval / delegation records before writing a new challenge.
- `tests/tools/test_guarded_git_commit.py`
  - Adds a high-level test where `承認\n` commits successfully through the guarded wrapper.
- `tests/tools/test_check_workflow_action.py`
  - Adds a regression test that malformed stale delegation no longer blocks a new prepare / approval flow.

## Verification requested

Check whether the documentation and implementation reflect the user decision without weakening the safety properties:

1. agreement_reflection
2. reference_accuracy
3. existing_record_consistency
4. internal_logic
