---
feature: workflow-management
phase: implementation
stage: triad-review
date: 2026-06-16
reopen: R-0
reopen_topic: commit-execution-delegation-formal-cli
rerun_reason: previous implementation review target lacked inspectable code evidence
target_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
target_implementation_files:
  - tools/check_workflow_action/commit_approval.py
  - tools/check-workflow-action.py
  - tools/guarded-git-commit.py
target_tests:
  - tests/tools/test_check_workflow_action.py
  - tests/tools/test_guarded_git_commit.py
---

# Review Target：workflow-management implementation commit execution delegation formal CLI R2

## Scope

This R2 implementation triad-review covers the implementation drafting update for reopen R-0
`commit-execution-delegation-formal-cli`.

R1 finding C1 said the target was not reviewable because it only summarized the implementation.
This R2 target embeds focused implementation and test evidence so reviewers can inspect the
actual behavior.

Review whether the implementation and tests correctly satisfy:

- Requirement 4 acceptance criterion 8
- design.md §不可逆操作の直前ゲートモデル §2.2
- tasks.md T-004, T-006, T-011 for commit execution delegation
- tasks triad-review C1-C7 resolution

Do not re-review unrelated historic workflow-management behavior except where the new
implementation conflicts with it.

## Implementation Evidence

### Runtime path and schema constants

```python
DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH = (
  ".reviewcompass/runtime/approvals/commit-execution-delegation.json"
)
EXECUTION_DELEGATION_ATTESTATION_TYPE = "commit_execution_delegation_nonce_binding"
EXECUTION_DELEGATION_GUARANTEE_SCOPE = (
  "stdin_text_instruction_bound_to_commit_approval_not_ui_utterance_proof"
)
ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS = {
  "コミット",
  "コミットして",
  "コミットを実行",
  "commit",
  "commitして",
}
```

### Delegation record path and staged file set digest

```python
def delegation_path(cwd):
  return Path(cwd) / DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH


def staged_file_set_digest_from_canonical(canonical):
  file_set = {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "entries": [
      {
        "path": entry["path"],
        "status": entry["status"],
        "mode": entry["mode"],
      }
      for entry in canonical["target"]["entries"]
    ],
  }
  return {
    "algorithm": CANONICAL_DIGEST_ALGORITHM,
    "digest": _json_digest(file_set),
  }
```

### Stdin normalization

```python
def normalize_execution_delegation_instruction(source_text):
  if isinstance(source_text, bytes):
    source_bytes = source_text
    try:
      text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
      raise ValueError(f"source text は UTF-8 である必要があります: {e}") from e
  elif isinstance(source_text, str):
    text = source_text
    source_bytes = text.encode("utf-8")
  else:
    raise ValueError("source text は bytes または str である必要があります")

  if len(source_bytes) > 256:
    raise ValueError("source text は 256 bytes 以下である必要があります")
  if "\x00" in text:
    raise ValueError("source text に NUL は使えません")
  if "\r" in text:
    raise ValueError("source text に CR/CRLF は使えません")
  if text.endswith("\n\n"):
    raise ValueError("source text の末尾 LF は 1 個までです")
  if text.endswith("\n"):
    text = text[:-1]
  if "\n" in text:
    raise ValueError("source text に内部改行は使えません")

  normalized = _lower_ascii(text.strip(" \t\f\v\u3000"))
  if normalized.endswith("。"):
    normalized = normalized[:-1]
  normalized = normalized.strip(" \t\f\v\u3000")
  if not normalized:
    raise ValueError("source text が空です")
  if normalized not in ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS:
    raise ValueError("source text が commit 実行代行承認の許可文言ではありません")
  return normalized
```

### Delegation write path

```python
def _validate_ready_for_delegation(cwd, nonce):
  challenge = _load_json_object(challenge_path(cwd), "commit approval challenge")
  approval = _load_json_object(approval_path(cwd), "commit approval record")
  if challenge.get("nonce") != nonce:
    raise ValueError("nonce が challenge と一致しません")
  if approval.get("nonce") != nonce:
    raise ValueError("nonce が commit approval record と一致しません")
  errors = validate(cwd, approval)
  if errors:
    raise ValueError("; ".join(errors))
  return challenge, approval


def delegate_execution(cwd, nonce, source_text):
  normalized_instruction = normalize_execution_delegation_instruction(source_text)
  redacted, source_omission_reason, findings = _redact_source(normalized_instruction)
  if source_omission_reason is not None or findings:
    raise ValueError("source text の redaction に失敗したため実行代行承認を保存しません")

  existing_path = delegation_path(cwd)
  if existing_path.exists():
    existing = _load_json_object(existing_path, "commit execution delegation")
    expires_at = _parse_datetime(existing.get("expires_at"))
    if (
      existing.get("consumed") is not True
      and existing.get("invalidated") is not True
      and (expires_at is None or expires_at > utc_now())
    ):
      raise ValueError("未消費の commit-execution-delegation record が既にあります")

  _, approval = _validate_ready_for_delegation(cwd, nonce)
  current = canonical_target(cwd)
  now = utc_now()
  record_data = {
    "schema_version": 1,
    "approved_action": "commit_execution_delegation",
    "delegated_action": "commit",
    "delegated_to": "llm",
    "approved_by": "user",
    "nonce": nonce,
    "target_digest": {
      "algorithm": CANONICAL_DIGEST_ALGORITHM,
      "digest": current["digest"],
    },
    "staged_file_set_digest": staged_file_set_digest_from_canonical(current),
    "staged_content_approval_digest": approval_record_digest(approval),
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "approval_record_path": DEFAULT_COMMIT_APPROVAL_PATH,
    "created_at": _isoformat(now),
    "expires_at": approval["expires_at"],
    "explicit_instruction": redacted,
    "instruction_sha256": hashlib.sha256(redacted.encode("utf-8")).hexdigest(),
    "attestation_type": EXECUTION_DELEGATION_ATTESTATION_TYPE,
    "guarantee_scope": EXECUTION_DELEGATION_GUARANTEE_SCOPE,
    "consumed": False,
    "invalidated": False,
  }

  _, approval_before_write = _validate_ready_for_delegation(cwd, nonce)
  if approval_record_digest(approval_before_write) != record_data["staged_content_approval_digest"]:
    raise ValueError("commit approval record が実行代行承認の保存直前に変化しました")
  if canonical_target(cwd)["digest"] != current["digest"]:
    raise ValueError("staged 内容が実行代行承認の保存直前に変化しました")

  _atomic_write_json(existing_path, record_data)
```

### Delegation validation

```python
def validate_execution_delegation(cwd, approval):
  path = delegation_path(cwd)
  if not path.exists():
    return [
      "LLM によるコミット実行代行の明示承認がありません"
      f"（{DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH} が必要）"
    ]

  delegation = _load_json_object(path, "commit execution delegation")
  errors = []
  allowed_fields = {
    "schema_version",
    "approved_action",
    "delegated_action",
    "delegated_to",
    "approved_by",
    "nonce",
    "target_digest",
    "staged_file_set_digest",
    "staged_content_approval_digest",
    "challenge_path",
    "approval_record_path",
    "created_at",
    "expires_at",
    "explicit_instruction",
    "instruction_sha256",
    "attestation_type",
    "guarantee_scope",
    "consumed",
    "invalidated",
  }
  missing = sorted(allowed_fields - set(delegation))
  extra = sorted(set(delegation) - allowed_fields)
  if missing:
    errors.append("commit-execution-delegation 必須フィールド不足: " + ", ".join(missing))
  if extra:
    errors.append("commit-execution-delegation 不明フィールド: " + ", ".join(extra))
  for field in sorted(FORBIDDEN_APPROVAL_FIELDS):
    if field in delegation:
      errors.append(f"commit-execution-delegation record に禁止フィールド {field} があります")

  expected_values = {
    "approved_action": "commit_execution_delegation",
    "delegated_action": "commit",
    "delegated_to": "llm",
    "approved_by": "user",
    "challenge_path": DEFAULT_COMMIT_APPROVAL_CHALLENGE_PATH,
    "approval_record_path": DEFAULT_COMMIT_APPROVAL_PATH,
    "attestation_type": EXECUTION_DELEGATION_ATTESTATION_TYPE,
    "guarantee_scope": EXECUTION_DELEGATION_GUARANTEE_SCOPE,
    "consumed": False,
    "invalidated": False,
  }
  for field, expected in expected_values.items():
    if delegation.get(field) != expected:
      errors.append(f"commit-execution-delegation {field} が不正です")

  if delegation.get("nonce") != approval.get("nonce"):
    errors.append("commit-execution-delegation nonce が commit-approval と一致しません")

  current = canonical_target(cwd)
  if delegation.get("staged_file_set_digest") != staged_file_set_digest_from_canonical(current):
    errors.append("commit-execution-delegation staged_file_set_digest が一致しません")
  if delegation.get("staged_content_approval_digest") != approval_record_digest(approval):
    errors.append("commit-execution-delegation staged_content_approval_digest が一致しません")

  if errors:
    _invalidate_runtime_records(cwd, approval)
  return errors
```

Note: the full function also validates UTC timestamps, expiry, target digest algorithm/digest,
target digest equality with current exact index, allowed instruction, and instruction hash.

### CLI integration

```python
elif args.commit_approval_command == "delegate-execution":
  source_text = sys.stdin.buffer.read()
  payload = commit_approval.delegate_execution(
    cwd,
    args.nonce,
    source_text,
  )
```

```python
cap_delegate = cap_sub.add_parser(
  "delegate-execution",
  help="nonce に対応する commit 実行代行承認を別レコードに保存する",
)
cap_delegate.add_argument("--nonce", required=True, help="prepare が出力した nonce")
cap_delegate.add_argument(
  "--source-text-stdin",
  action="store_true",
  required=True,
  help="実行代行承認の明示文言を stdin から読む",
)
cap_delegate.add_argument("--json", action="store_true", help="JSON のみを出力する")
```

### Commit gate actor separation

```python
def validate_commit_execution_delegation(cwd, approval_state, execution_actor):
  if execution_actor == "human":
    return []

  approval_path = Path(cwd) / approval_state.get("path", DEFAULT_COMMIT_APPROVAL_PATH)
  approval = json.loads(approval_path.read_text(encoding="utf-8"))
  if approval.get("nonce"):
    return commit_approval.validate_execution_delegation(cwd, approval)

  delegation = approval_state.get("execution_delegation")
  if not isinstance(delegation, dict):
    return [
      "LLM によるコミット実行代行の明示承認がありません"
      f"（{commit_approval.DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH} が必要）"
    ]
```

The non-nonce embedded `execution_delegation` branch remains only for legacy simple approval
records used by existing tests. Formal nonce-based approval uses the separate file.

### Invalidate and guarded commit consumption

```python
def invalidate(cwd):
  changed = []
  for path in (challenge_path(cwd), approval_path(cwd), delegation_path(cwd)):
    ...
    data["invalidated"] = True
```

```python
if approval.get("nonce"):
  challenge_ref = approval.get("challenge_path")
  challenge_path = Path(cwd) / challenge_ref
  ok, result = _mark_consumed(challenge_path, consumed_at)
  if not ok:
    return False
  delegation_path = Path(cwd) / DEFAULT_COMMIT_EXECUTION_DELEGATION_PATH
  ok, result = _mark_consumed(delegation_path, consumed_at)
  if not ok:
    return False
```

## Test Evidence

### Separate record and no embedded delegation

```python
def test_commit_approval_delegate_execution_writes_separate_record(self):
  _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
  challenge = _prepare_commit_approval(self.tmpdir)
  record_result = _record_commit_approval(self.tmpdir, challenge["nonce"])
  self.assertEqual(record_result.returncode, 0, record_result.stderr)

  delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])

  self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)
  approval = _read_commit_approval(self.tmpdir)
  self.assertNotIn("execution_delegation", approval)
  delegation = _read_commit_execution_delegation(self.tmpdir)
  self.assertEqual(delegation["approved_action"], "commit_execution_delegation")
  self.assertEqual(delegation["delegated_to"], "llm")
  self.assertEqual(delegation["nonce"], challenge["nonce"])
  self.assertNotIn("llm", delegation)
  self.assertNotIn("provider", delegation)
  self.assertNotIn("model", delegation)
```

### LLM commit requires separate delegation

```python
def test_llm_commit_accepts_separate_execution_delegation_record(self):
  _stage_file(self.tmpdir, "notes.md", "# nonce 対象")
  challenge = _prepare_commit_approval(self.tmpdir)
  _record_commit_approval(self.tmpdir, challenge["nonce"])

  result_without_delegation = run_script(
    ["commit", "--rationale", "内容承認だけで LLM commit しようとするテスト"],
    cwd=self.tmpdir,
  )
  self.assertEqual(result_without_delegation.returncode, 2, result_without_delegation.stdout)
  self.assertIn("commit-execution-delegation", result_without_delegation.stdout)

  delegate_result = _delegate_commit_execution(self.tmpdir, challenge["nonce"])
  self.assertEqual(delegate_result.returncode, 0, delegate_result.stderr)

  result_with_delegation = run_script(
    ["commit", "--rationale", "別ファイル実行代行承認付き commit"],
    cwd=self.tmpdir,
  )
  self.assertEqual(result_with_delegation.returncode, 0, result_with_delegation.stdout)
```

### CRLF rejection and target digest tamper rejection

```python
def test_commit_approval_delegate_execution_rejects_crlf_instruction(self):
  delegate_result = _delegate_commit_execution(
    self.tmpdir,
    challenge["nonce"],
    source_text="コミット\r\n",
  )
  self.assertEqual(delegate_result.returncode, 2, delegate_result.stdout)
  self.assertIn("source text", delegate_result.stdout)
```

```python
def test_commit_rejects_tampered_execution_delegation_record(self):
  delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
  delegation["target_digest"]["digest"] = "0" * 64
  delegation_path.write_text(
    json.dumps(delegation, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )

  result = run_script(
    ["commit", "--rationale", "実行代行承認改ざん遮断"],
    cwd=self.tmpdir,
  )
  self.assertEqual(result.returncode, 2, result.stdout)
  self.assertIn("commit-execution-delegation", result.stdout)
```

### Guarded commit consumption

```python
def test_guarded_commit_consumes_nonce_challenge_after_success(self):
  _stage_file(self.tmpdir, "notes.md", "# nonce commit")
  challenge = _prepare_commit_approval(self.tmpdir)
  _record_commit_approval(self.tmpdir, challenge["nonce"])
  _delegate_commit_execution(self.tmpdir, challenge["nonce"])

  result = run_guarded_commit(
    [
      "-m", "guarded nonce commit",
      "--rationale", "利用者が LLM によるコミット実行代行を明示承認",
    ],
    cwd=self.tmpdir,
  )

  self.assertEqual(result.returncode, 0, result.stderr)
  self.assertTrue(approval["consumed"])
  self.assertTrue(consumed_challenge["consumed"])
  self.assertTrue(delegation["consumed"])
```

## Known Review Gaps From R1

R1 triage identified these review questions:

- C2: should add or explicitly accept a focused test for unknown-field and identity-field rejection
  on `commit-execution-delegation.json`.
- C3: should add or explicitly accept a focused redaction failure / residual-secret test for
  `delegate_execution`.
- C4: `.reviewcompass/runtime/` is already ignored by `.gitignore`, so accidental tracking of
  `commit-execution-delegation.json` is covered.

Reviewers should decide whether C2/C3 are implementation blockers or test-hardening follow-ups.

## Verification Already Run

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests -v`
- `.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit -v`
- `PYTHONPYCACHEPREFIX=/tmp/reviewcompass-pycache python3 -m py_compile tools/check-workflow-action.py tools/check_workflow_action/commit_approval.py tools/guarded-git-commit.py`
- `git diff --check`

## Review Questions

1. Does the implementation preserve separation between staged content approval and commit execution delegation?
2. Does `delegate-execution` fail closed for malformed stdin, missing or mismatched nonce, missing staged content approval, staged content drift, expired/consumed/invalidated records, duplicate unexpired delegation, redaction failure, and residual secrets?
3. Is the delegation record sufficiently bound to the same staged content approval context and current index?
4. Is the strict schema complete and does it reject unknown fields and LLM/provider/model identity fields?
5. Does commit gate validation revalidate challenge, staged content approval, delegation, and current index for `--execution-actor llm`?
6. Does `--execution-actor human` remain exempt from execution delegation without weakening LLM execution checks?
7. Does guarded commit consume approval, challenge, and delegation in a safe order after successful commit?
8. Are tests sufficient for Requirement 4 acceptance 8, design §2.2, and tasks T-004/T-006/T-011?
9. Are there deployment or portability concerns in the implementation, including runtime paths, Python version compatibility, and use outside the ReviewCompass development repository?

## Expected Output

Return findings with severity and evidence. Classify issues as:

- `must-fix`: implementation approval should not proceed before correction.
- `should-fix`: correction is recommended before approval unless explicitly accepted.
- `leave-as-is`: no change needed.
