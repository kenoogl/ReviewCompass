# Carry-forward Register

This directory stores the project-independent carry-forward register used by self-improvement.

The register is the canonical structured form for unresolved cross-scope items that must be considered before a review-wave or equivalent cross-feature stage. Project-local ledgers, such as `sources/reviewcompass-pending-cross-feature-findings.md`, are treated as import sources or historical evidence, not as general workflow discipline.

## Files

- `reviewcompass-import.yaml`: initial import generated from the ReviewCompass Markdown ledger.
- `sources/reviewcompass-pending-cross-feature-findings.md`: historical Markdown import source. This is not the canonical register.
- `../schemas/carry-forward-register.schema.json`: canonical schema for register entries.

## Field Policy

- General decision fields must use project-independent concepts: `item_id`, `scope`, `source_feature`, `target_feature_or_phase`, `finding_summary`, `status`, `decision_needed`, `carry_forward_reason`, `resolution`, and `evidence_refs`.
- Project-local identifiers, session labels, legacy A-xxx IDs, and original file names belong in `project_local_context` or `evidence_refs`.
- Items that cannot be converted without human judgment must remain in the register with `decision_needed: true` and explicit `decision_reasons`.
