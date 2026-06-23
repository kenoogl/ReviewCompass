# Proxy Decision Prompt: Post-write Finding 001

## User Review Requirements

The user requested proxy-mode inspection of the post-write API review findings before accepting or rejecting them.

Judge this single finding independently. Do not combine it with other findings. Decide whether it blocks the current discipline-map coverage change, should be fixed immediately, should be split into a separate backlog/maintenance item, or should be left as-is.

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

Out of current change scope unless the finding truly blocks this patch:

- redesigning the whole post-write review runner
- changing API provider variants
- replacing the review-run artifact format

## Finding Under Review

```yaml
finding_id: 2026-06-23-discipline-map-coverage-postwrite-gemini-3.1-pro-preview-primary-001
severity: ERROR
target_location: .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
description: Specifying that `review-target.md` should contain `target file contents` violates the strict separation of criteria and target.
rationale: According to `API_REVIEW_PROMPT_QUALITY.md`, the review criteria and target MUST be separated. Including the full target contents directly inside the criteria file (`review-target.md`) undermines prompt isolation, risks framing bias within the criteria wrapper, and contradicts the established rule that target contents should be handled independently via `--target`.
```

## Source Excerpts

### API review prompt quality discipline

From `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`:

```markdown
API review-run では、criteria と target を分離する。

- `User Review Requirements`: 利用者が指定したレビュー目的、判断対象、重視点、範囲、禁止事項、必要出力
- `--criteria-file`: レビュー目的、背景、上流材料、必須チェック、範囲外、finding policy を含む
- `--target`: 実際に審査する本文

禁止:

- criteria と target に同じ review wrapper / author-written summary を渡す
- target manifest が実審査対象を含まない状態で gate 完了根拠にする
- target 本文を入れず、target の要約だけで review-run を実行する
```

The same file says API review prompt failures to prevent include:

```markdown
- `--target` が実際の審査対象本文ではなく、作成者の要約になっている
- `--criteria-file` と `--target` が同一の author-written summary になっている
- source materials が path-only で、モデルが本文を読めない
- review target / source materials / out of scope が分離されていない
```

### Current workflow navigation text under review

From `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification`:

```markdown
API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target と prompt manifest を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md> --prompt-manifest-path <prompt-manifest.yaml>` を実行することである。

`prepare_post_write_review.py` は `review-target.md`、`review-target.yaml`、`prompt-manifest.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、source materials、target file contents、scope / out-of-scope、finding policy、機微情報チェック結果を含める。
```

The documented command also passes the underlying target files as `--target`, and passes `review-target.md` as `--criteria-file`:

```bash
.venv/bin/python3 tools/api_providers/run_review.py \
  --variant post_write_verification_google \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --phase post_write_verification \
  --criteria-file .reviewcompass/evidence/review-runs/<run-id>/review-target.md \
  --prompt-manifest-path .reviewcompass/evidence/review-runs/<run-id>/prompt-manifest.yaml \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>
```

### Existing tests indicating current behavior

The test suite intentionally checks that post-write review preparation embeds target bodies and source bodies, and that `run_review.py` accepts the generated prompt manifest. However, the same discipline says criteria and target must remain separated.

Relevant behavior:

- `test_prepare_post_write_review_embeds_target_body_not_only_path_and_sha`
- `test_prepare_post_write_review_embeds_source_material_body_separate_from_target`
- `test_prepare_post_write_review_writes_auditable_prompt_manifest`
- `test_run_review_accepts_prepare_post_write_prompt_manifest`

## Main Preanalysis

The finding appears substantively valid as a broader post-write review prompt architecture issue: `review-target.md` is serving as a criteria wrapper while also containing the full target contents, and the earlier failed-review history explicitly warns against criteria/target collapse.

However, the current patch did not introduce this post-write review architecture. The current patch only adds discipline-map coverage for next-action kinds and adds two navigation sections for commit-unit anomalies. Fixing finding 001 properly likely requires a separate source-bundle/criteria/target restructuring of post-write review preparation and runner behavior, which is larger than this map coverage patch.

The key decision is therefore not simply whether the finding is true. Decide whether it should block the current map coverage commit, or be recorded as a separate must-fix/should-fix backlog item for the post-write prompt mechanization line.

## Required Output

Return valid YAML only.

```yaml
proxy_model_id: "<provider/model or proxy identifier>"
decisions:
  - finding_id: "2026-06-23-discipline-map-coverage-postwrite-gemini-3.1-pro-preview-primary-001"
    final_label: "must-fix|should-fix|leave-as-is|split-out"
    blocks_current_map_coverage_commit: true|false
    should_fix_now: true|false
    rationale: "<concise decision rationale>"
    required_changes:
      - "<specific change, or [] if none>"
    backlog_recommendation: "<none, or a concrete backlog item>"
    confidence: "high|medium|low"
```
