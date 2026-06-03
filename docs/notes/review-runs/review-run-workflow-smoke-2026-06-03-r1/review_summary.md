# Review run summary: review-run-workflow-smoke-2026-06-03-r1

| model_id | parse_status | triage_status | findings | severity | raw |
| --- | --- | --- | ---: | --- | --- |
| claude-sonnet-4-6 | parse_failed | triage_pending | 0 | - | raw/claude-sonnet-4-6.round-1.txt |
| gpt-5.4 | parsed | triage_pending | 4 | low:2, medium:2 | raw/gpt-5.4.round-1.txt |
| gemini-3.1-pro-preview | parsed | triage_pending | 4 | minor:2, moderate:2 | raw/gemini-3.1-pro-preview.round-1.txt |

## Next steps

1. Read raw responses for any parse_failed or triage_pending model.
2. Move finding-level judgments into triage.yaml.
3. Resolve human_required items before treating the run as complete.
