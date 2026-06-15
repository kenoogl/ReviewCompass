# workflow-management implementation triad-review recheck target: commit approval nonce fixes

## Scope

This recheck covers the implementation changes made after the prior implementation triad-review for:

- C1 challenge consumption is incomplete
- C2 `execution_delegation` is embedded by default in nonce approval records
- C3 exact-index digest edge cases are under-tested and may be incomplete
- C4 malformed/no-partial-inference coverage is insufficient
- C5 `source_omission_reason: null` is ambiguous
- C6 legacy fallback invalidation interaction is unclear
- C7 `commit_stop_point` is under-constrained

C8 normal git execution failure conditional retry was decided by proxy_model as follow-up / leave-as-is for this gate.

The review should verify whether C1-C7 are now sufficiently addressed and whether the changes introduce regressions. Do not treat C8 as blocking unless the new changes make it worse.

## Changed Files

- `tools/check_workflow_action/commit_approval.py`
- `tools/guarded-git-commit.py`
- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_guarded_git_commit.py`
- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `stages/in-progress/reopen-procedure-2026-06-15-commit-approval-nonce.yaml`

## C1: Challenge Consumption

`tools/guarded-git-commit.py` now consumes both the approval record and nonce challenge after a successful guarded commit. Consumption failures return non-zero after the git commit instead of silently succeeding.

Key implementation:

```python
def _mark_consumed(path, consumed_at):
  try:
    record = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return False, f"{path}: {e}"

  if not isinstance(record, dict):
    return False, f"{path}: record is not an object"

  record["consumed"] = True
  record["consumed_at"] = consumed_at
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
      json.dumps(record, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    return False, f"{path}: {e}"
  return True, record
```

```python
def consume_commit_approval(cwd):
  read_path = Path(cwd) / resolve_commit_approval_path(cwd)
  try:
    approval = json.loads(read_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    print(f"error: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
    return False
  if not isinstance(approval, dict):
    print("error: 承認レコードが object ではないため消費済みにできません", file=sys.stderr)
    return False

  if approval.get("expires_after_commit") is False:
    return True

  consumed_at = datetime.now(timezone.utc).isoformat()
  write_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
  approval["consumed"] = True
  approval["consumed_at"] = consumed_at
  try:
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text(
      json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
      encoding="utf-8",
    )
  except OSError as e:
    print(f"error: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
    return False

  if approval.get("nonce"):
    challenge_ref = approval.get("challenge_path")
    if not isinstance(challenge_ref, str) or not challenge_ref:
      print("error: nonce 承認の challenge_path がありません", file=sys.stderr)
      return False
    challenge_path = Path(cwd) / challenge_ref
    ok, result = _mark_consumed(challenge_path, consumed_at)
    if not ok:
      print(f"error: challenge の消費済み記録に失敗しました: {result}", file=sys.stderr)
      return False

  return True
```

```python
record_last_commit_precheck(cwd, precheck)
if not consume_commit_approval(cwd):
  return 2
return 0
```

Regression test:

- `test_guarded_commit_consumes_nonce_challenge_after_success`

## C2: Execution Delegation Separation

`commit-approval record` no longer embeds `execution_delegation` by default. The existing commit precheck still requires explicit `execution_delegation` for `--execution-actor llm`, so content approval and execution delegation are separate records/concerns.

Removed default block from `commit_approval.record`:

```python
"execution_delegation": {
  "delegated_to": "llm",
  "approved_by": "user",
  "approved_at": _isoformat(now),
  "explicit_instruction": "コミット代行も含めて自律実行",
  "rationale": "利用者が LLM によるコミット実行代行を明示承認",
},
```

Regression tests:

- `test_commit_approval_record_does_not_embed_execution_delegation_by_default`
- existing `test_llm_commit_without_execution_delegation_returns_two`
- existing `test_human_commit_precheck_allows_content_approval_without_delegation`

## C3: Exact-Index Edge Cases

The staged file collection for nonce canonical target now uses the parsed staged status map instead of `git diff --cached --name-only -z`. Rename source deletion is included in the target entries.

Key implementation:

```python
def staged_files(cwd):
  return sorted(_staged_status_map(cwd))
```

```python
if code.startswith("R") and i + 2 < len(parts):
  old_path = parts[i + 1]
  new_path = parts[i + 2]
  status[old_path] = "D"
  status[new_path] = "R"
  i += 3
elif code.startswith("C") and i + 2 < len(parts):
  new_path = parts[i + 2]
  status[new_path] = "C"
  i += 3
```

Regression tests:

- `test_commit_approval_prepare_includes_rename_source_deletion`
- `test_commit_approval_prepare_preserves_staged_gitlink_entry`

## C4: Malformed / No Partial Inference

Challenge fields are now validated before record creation.

Key implementation:

```python
def _require_string_list(value, label):
  if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
    raise ValueError(f"{label} は文字列配列である必要があります")
  if len(value) != len(set(value)):
    raise ValueError(f"{label} に重複があります")
  return value
```

```python
def _require_target_digest(value, label):
  if not isinstance(value, dict):
    raise ValueError(f"{label} target_digest が不正です")
  if value.get("algorithm") != CANONICAL_DIGEST_ALGORITHM:
    raise ValueError(f"{label} target_digest algorithm が不正です")
  digest = value.get("digest")
  if not isinstance(digest, str) or len(digest) != 64:
    raise ValueError(f"{label} target_digest digest が不正です")
  try:
    int(digest, 16)
  except ValueError as e:
    raise ValueError(f"{label} target_digest digest が不正です") from e
  return value
```

```python
challenge_target_files = _require_string_list(
  challenge.get("target_files"),
  "challenge target_files",
)
challenge_digest = _require_target_digest(
  challenge.get("target_digest"),
  "challenge",
)
if challenge_digest.get("digest") != current["digest"]:
  raise ValueError("staged 内容が challenge と一致しません")
if challenge_target_files != [
  entry["path"]
  for entry in current["target"]["entries"]
]:
  raise ValueError("challenge target_files が staged exact index と一致しません")
```

Regression test:

- `test_commit_approval_record_rejects_malformed_challenge_target_files`

## C5: Source Omission Schema

When source text is stored after redaction, `source_omission_reason` is omitted instead of emitted as `null`.

Key implementation:

```python
if source_omission_reason is not None:
  approval["source_omission_reason"] = source_omission_reason
if redacted_source is not None:
  approval["source_text_redacted"] = redacted_source
```

Regression test:

- `test_commit_approval_record_source_text_is_redacted` now asserts `source_omission_reason` is absent when `source_text_redacted` is present.

## C6: Legacy Fallback Invalidation

When nonce approval is loaded from the legacy fallback path and validation fails, the frozen legacy record is left unchanged and an invalidated runtime copy is written. The runtime challenge is invalidated as well.

Key implementation:

```python
def _write_runtime_invalidated_approval(cwd, approval, invalidated_at):
  if not isinstance(approval, dict) or not approval.get("nonce"):
    return
  path = approval_path(cwd)
  if path.exists():
    return
  data = dict(approval)
  data["invalidated"] = True
  data["invalidated_at"] = invalidated_at
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def _invalidate_runtime_records(cwd, approval=None):
  try:
    invalidated_at = _isoformat(utc_now())
    invalidate(cwd)
    _write_runtime_invalidated_approval(cwd, approval, invalidated_at)
  except OSError:
    pass
```

Regression test:

- `test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails`

## C7: `commit_stop_point` Constraints

`commit_stop_point: true` is no longer a broad bypass. It is accepted only for the implementation drafting completion stop point shape.

Key implementation:

```python
if "停止点コミット" in next_step:
  continue
if data.get("commit_stop_point") is not True:
  return False
reason = data.get("commit_stop_point_reason") or ""
if data.get("step_number") != 3:
  return False
if next_step != "第3過程：implementation triad-review":
  return False
if "implementation drafting 完了" not in reason:
  return False
```

Regression tests:

- existing `test_commit_allows_reopen_explicit_commit_stop_point_field`
- new `test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason`

## Verification Already Run

```bash
.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_source_text_is_redacted tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason -v
```

Result: pass after implementation.

```bash
.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v
```

Result: 184 tests passed.

```bash
git diff --check
```

Result: pass.

## Review Questions

1. Are C1-C7 adequately addressed?
2. Are there any remaining blockers for implementation triad-review completion?
3. Did the fixes introduce regressions in commit approval, guarded commit, runtime placement freeze, or reopen stop-point behavior?
4. Is C8 still acceptable as follow-up / leave-as-is for this gate?

Return findings in the standard ReviewCompass YAML format.
