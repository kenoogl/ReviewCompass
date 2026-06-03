# Final post-write verification target: proxy review and parallel implementation workflow

## Scope

This final check verifies the proxy review / parallel implementation workflow after r1 and r2 fixes.

## r1 fixes now present

- Important-finding threshold is explicit.
- Proxy decision records require `decision_prompt_path`, `source_raw_paths`, `candidate_options`, `selected_option`, `final_label`, `rationale`, `rejected_options`, and `raw_response_path`.
- Machine guard checks prompt/raw references, non-empty proxy raw response, candidate options, label consistency, finding ID consistency, and proxy model ID consistency.
- `work_noise` is promoted to `decision_basis` when it affects judgment.
- Parallelization boundaries include shared files, generated artifacts, shared helpers, transitive contracts, same manifests, and same traceability outputs.
- Same-repo parallel implementation is limited to read-only investigation or checks that leave no diff.
- Unapproved incidental refactors, adjacent behavior changes, and out-of-scope cleanup stop as new judgment questions.
- Deleting canon, removing machine guards, lowering important thresholds, deleting approval evidence, or shrinking verification scope requires explicit human approval.

## r2 fixes now present

- Same-root finding identity is defined as sharing the same target file, output contract, machine guard, evidence, or root cause across model findings.
- Current lightweight proxy consistency checks are explicitly documented: proxy_model_id string match, finding_id match, final_label match, prompt/raw/candidate evidence existence.
- Cryptographic/API-signed provenance is documented as future scope.
- Main session LLM is responsible for summarizing or preserving promoted `decision_basis` evidence from sub-implementation work.

## Verification commands

```text
.venv/bin/python3 -m pytest tests/tools/test_session_record_contract.py -q
8 passed

.venv/bin/python3 -m pytest tools/api_providers/tests -q
113 passed
```

## Review request

Please check whether any substantive issue remains after r1 and r2 fixes.

Classify findings as:

- ERROR or WARN only for issues that should block completion or require another correction.
- INFO for future-scope notes, non-blocking observations, or optional refinements.

Return structured YAML if possible. If strict YAML is difficult, return raw findings with stable IDs, severity, target location, description, rationale, and recommendation.
