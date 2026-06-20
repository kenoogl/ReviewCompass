---
criteria_id: main-preanalysis-sufficiency-audit
phase: prompt-quality
review_target: <preanalysis-audit-bundle.md>
status: template
---

# Main Preanalysis Sufficiency Audit Criteria

Review the target bundle before the actual API review-run.

The target bundle must contain:

- the user or workflow review requirement
- the source materials needed for the judgment item
- the main session LLM preanalysis
- the proposed API review criteria or prompt

The review question is:

Can the proposed API review prompt derive the needed review judgment from the provided source materials, without relying on the main preanalysis as an answer key, and does the main preanalysis reveal any missing viewpoints, unsupported claims, or framing bias that must be corrected before the real review-run?

## Required Method

Perform the audit in this order:

1. Independently reconstruct the judgment item from the source materials and user or workflow requirement.
2. Compare that reconstruction with the main preanalysis.
3. Judge whether the proposed API review prompt gives enough source material, scope, question, and output instructions for the actual reviewer.
4. Identify required prompt changes before any real review-run.

Treat the main preanalysis as a hypothesis and source-discovery aid. Do not treat it as ground truth.

## Required Checks

### Independent Reconstruction

From the source materials alone, identify:

- the judgment item ID
- the exact review question
- the target artifact or section
- the source materials that are necessary
- the material that is out of scope
- the rationale connecting the source materials to the review question

If multiple independent judgment items are present, report that the proposed review prompt must be split.

### Main Preanalysis Assessment

Compare the main preanalysis against the independent reconstruction.

Check for:

- supported parts that are well grounded in the sources
- missing perspectives or missing source materials
- unsupported, overconfident, or overstated parts
- framing bias, including treating a draft answer as established fact
- source coverage gaps caused by path-only references, summaries without source basis, or omitted upstream context

### Prompt Sufficiency

Judge whether the proposed API review prompt:

- includes enough model-readable source material
- asks one non-leading primary question
- keeps target, source materials, and out-of-scope material distinct
- preserves user or workflow requirements without narrowing, broadening, or replacing them
- defines the expected output clearly enough for the runner
- prevents the reviewer from authorizing commit, push, phase completion, human approval delegation, or unapproved specification changes

## Finding Policy

- Report `CRITICAL` if the prompt would authorize or imply authorization of irreversible operations, human-only approval, phase completion, or unapproved repository changes.
- Report `ERROR` if the prompt cannot support the requested review because source materials are missing, path-only, wrong, or treated as target material.
- Report `ERROR` if multiple independent judgments are bundled into one prompt.
- Report `ERROR` if the prompt depends on the main preanalysis as the answer instead of requiring source-based independent judgment.
- Report `ERROR` if user or workflow review requirements are omitted, narrowed, broadened, or replaced.
- Report `WARN` for usable prompts with avoidable ambiguity, incomplete source mapping, weak target/source separation, or bias risk.
- Report `INFO` for minor clarity or ergonomics improvements.

## Output Contract

Return YAML only. Do not wrap it in Markdown fences.

The response must include these top-level keys:

- `verdict`
- `independent_reconstruction`
- `preanalysis_assessment`
- `prompt_sufficiency`
- `required_prompt_changes`
- `findings`

Use one of these `verdict` values:

- `sufficient`
- `sufficient_with_revisions`
- `insufficient`

Use this shape:

verdict: sufficient_with_revisions
independent_reconstruction:
  judgment_items:
    - item_id: "<stable-id>"
      question: "<source-derived review question>"
      target_files:
        - "<path or section>"
      source_materials:
        - "<path, section, or embedded source label>"
      out_of_scope:
        - "<material or action not judged>"
      rationale: "<why this is the right judgment item>"
preanalysis_assessment:
  supported_parts:
    - "<grounded part>"
  missing_perspectives:
    - "<missing viewpoint or source>"
  unsupported_or_overconfident_parts:
    - "<claim that needs source support or softening>"
  bias_risks:
    - "<framing or anchoring risk>"
prompt_sufficiency:
  information: "sufficient | revisions_needed | insufficient"
  question: "sufficient | revisions_needed | insufficient"
  scope: "sufficient | revisions_needed | insufficient"
  sensitivity_check: "sufficient | revisions_needed | insufficient"
  notes:
    - "<short note>"
required_prompt_changes:
  - "<required change before actual review-run>"
findings:
  - severity: WARN
    target_location: "<section in proposed prompt or bundle>"
    description: "<concise finding>"
    rationale: "<why this matters>"

If there are no defects, return `verdict: sufficient`, complete the assessment keys with empty lists where appropriate, and return:

findings: []
