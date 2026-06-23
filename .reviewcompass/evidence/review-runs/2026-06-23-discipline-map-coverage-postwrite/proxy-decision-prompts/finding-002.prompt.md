# Proxy Decision Prompt: Post-write Finding 002

## User Review Requirements

The user requested proxy-mode inspection of the post-write API review findings before accepting or rejecting them.

Judge this single finding independently. Do not combine it with other findings. Decide whether the finding is a real contradiction that must be fixed now, a wording/legacy-state clarification, a separate backlog item, or invalid.

## Current Change Scope

The current work is narrowly scoped to discipline-map coverage for `next --json` locations.

Changed targets under post-write review:

- `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`

The implementation/test diff adds effective-prompt map coverage for next-action kinds that `next --json` can already return:

- `parent_resume_pending`
- `blocking_unit_required`
- `blocking_unit_in_progress`
- `commit_mixing_risk`
- `commit_unit_stale`

It also adds navigation text for `commit_mixing_risk` and `commit_unit_stale`, plus a regression test asserting each expected `next_action.kind` has an effective prompt.

## Finding Under Review

```yaml
finding_id: 2026-06-23-discipline-map-coverage-postwrite-gemini-3.1-pro-preview-primary-002
severity: ERROR
target_location: ".reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification and #post_write_human_decision_required"
description: Contradiction regarding manifest generation and human decision escalation states.
rationale: The `post_write_verification` section strictly prohibits generating a manifest if `triage.yaml` contains `human_required`. However, the `post_write_human_decision_required` section instructs checking `next_action.manifest` for unresolved substantive findings. If the manifest is completely blocked from being generated in an unresolved state, the workflow engine cannot provide `next_action.manifest`, making the intended human escalation state logically unreachable.
```

## Source Excerpts

### Current workflow navigation text under review

From `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification`:

```markdown
`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。manifest は post-write validation の途中記録ではなく、commit 直前の最終封印である。`triage.yaml` に `decision_status: human_required` が残る場合、重要件の利用者承認が確認できない場合、または review-run の target set に含まれない未コミット post-write target が残る場合は manifest を生成しない。manifest 作成後は対象ファイルを編集せず、stage / approval / commit へ直行する。
```

From `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required`:

```markdown
manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。
```

### Current workflow engine behavior

From `tools/check-workflow-action.py`:

```python
def evaluate_post_write_manifest_state_for_hashes(cwd, target_files, actual_hashes):
  target_set = set(target_files)
  for manifest in load_post_write_manifests(cwd):
    manifest_targets = set(manifest.get("target_files") or [])
    if not target_set.issubset(manifest_targets):
      continue
    if not manifest_hashes_match_values(manifest, target_files, actual_hashes):
      continue
    if unresolved_substantive_count(manifest) > 0:
      return "human_required", manifest
```

And in `next --json`:

```python
elif manifest_state == "human_required":
  next_action = {
    "kind": "post_write_human_decision_required",
    "target_files": verification_targets,
    "manifest": manifest.get("_path"),
    "reason": "post-write-verification に未解決の本質的指摘があります",
  }
```

### Existing tests indicating current behavior

From `tools/api_providers/tests/test_review_triage.py`:

```python
def test_manifest_template_fails_when_human_required_remains(tmp_path, capsys):
  """未判断 finding が残る場合は manifest 雛形を出力しない。"""

def test_write_manifest_creates_file_after_all_decisions(tmp_path):
  """write-manifest は解決済み review-run から manifest ファイルを書く。"""

def test_write_manifest_blocks_important_decisions_without_approval(tmp_path, capsys):
  """重要件を含む review-run は manifest 生成時にも承認レコードを要求する。"""
```

## Main Preanalysis

The finding identifies a real ambiguity in the wording, but it may overstate the implementation contradiction.

`post_write_human_decision_required` is reachable in the engine if an existing post-write manifest file matches the current targets and contains unresolved substantive findings. That can happen for legacy/manual/older manifests or if a manifest exists outside the current review-run write-manifest path. The engine has code to return that state with `next_action.manifest`.

At the same time, current `write-manifest --out auto` is documented as the final seal and is blocked when the current review-run `triage.yaml` still has `human_required`. That means a normal new review-run should not generate a final manifest with unresolved review-run triage.

Therefore the likely problem is not that `post_write_human_decision_required` is impossible in all cases. The likely problem is that the navigation text does not distinguish:

- current review-run triage `human_required`, where manifest generation is blocked before final seal; and
- existing manifest unresolved substantive findings, where `next --json` can return `post_write_human_decision_required` with `next_action.manifest`.

This may be fixable with a small clarification to `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`.

## Required Output

Return valid YAML only.

```yaml
proxy_model_id: "<provider/model or proxy identifier>"
decisions:
  - finding_id: "2026-06-23-discipline-map-coverage-postwrite-gemini-3.1-pro-preview-primary-002"
    final_label: "must-fix|should-fix|leave-as-is|split-out"
    blocks_current_map_coverage_commit: true|false
    should_fix_now: true|false
    rationale: "<concise decision rationale>"
    required_changes:
      - "<specific change, or [] if none>"
    backlog_recommendation: "<none, or a concrete backlog item>"
    confidence: "high|medium|low"
```
