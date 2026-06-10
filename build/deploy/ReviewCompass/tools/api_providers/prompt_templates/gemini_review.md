prompt_id: {{ prompt_id }}
provider: {{ provider_name }}
model_id: {{ model }}

# Task
Review the target document for the requested phase and criteria.

# Phase
{{ phase }}

# Criteria
{{ criteria }}

# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
{{ prior_findings }}

# Target path
{{ target_path }}

# Target document
{{ target_content }}
