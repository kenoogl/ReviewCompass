prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt-quality

# Criteria
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


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-preanalysis-audit-run/preanalysis-audit-bundle.md

# Target document
---
bundle_id: workflow-management-implementation-mwp0-preanalysis-audit
phase: prompt-quality
target_proposed_review_criteria: .reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-review-run/review-target.md
status: draft_for_preanalysis_sufficiency_audit
---

# Preanalysis Audit Bundle: MWP-0 (kind 7-value redesign)

This bundle is the target for `main-preanalysis-sufficiency-audit`.

The reviewer must not judge the implementation artifacts themselves. The reviewer must judge whether the proposed API review criteria can support a later implementation review.

## User And Workflow Review Requirement

- Review purpose: workflow-management implementation triad-review — MWP-0 (next-json-kind-redesign).
- Review object: proposed API review criteria for MWP-0 implementation upstream transfer.
- Review focus:
  - if/then constraint completeness in the JSON Schema
  - kind value separation between `next --json` and `commit-preflight` subcommand
  - reason vs reasons field responsibility separation
  - upstream intent transfer (requirements → design → tasks → implementation)
- Scope boundary:
  - In scope: `.reviewcompass/schema/next_action_response.schema.json`, `.reviewcompass/schema/commit_preflight_response.schema.json`, relevant implementation in `tools/check-workflow-action.py`, if/then constraint test coverage, upstream alignment with requirements 受入11(6) and 受入12.
  - Out of scope: unrelated subcommands or tools outside MWP-0, commit/push/spec.json update/phase completion, triage decisions on findings, implementation fixes.
- Required method:
  - Use source materials as upstream intent.
  - Use main preanalysis as a hypothesis and source-discovery aid, not as an answer key.
  - Check whether the proposed criteria gives a later API reviewer enough information to independently judge the implementation target.

## Source Materials

The following source material is model-readable upstream intent for MWP-0.

### 要件（受入 11(6)）— if/then 制約の仕様

```text
【Requirement 2 受入 11(6)】
required_action の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、
スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。

① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時：active_gate=null・phase=null・stage=null・repair_reasons に修復理由を含める
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時：action_parameters に maintenance_action・allowed_scope・allowed_files・
   completion_conditions・active_stack_frame_id・parent_frame_id を含める

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

### 要件（受入 12）— kind 値分離の仕様

```text
【Requirement 2 受入 12（MWP-0 で新設）】
本機能は commit_candidate、commit_mixing_risk、commit_unit_stale の3種類の判定を next --json の
kind から除外し、commit-preflight サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」
ではなく「コミット操作の前確認」であり、next --json の kind は作業の現在地のみを示す7種類
（completed / in_progress / blocking_in_progress / verification_pending /
  reopen_in_progress / feature_definition_required / unknown）に限定する。
```

### 設計（§5.2 スキーマ設計）

```text
【design §5.2 next_action_response.schema.json】
- 必須フィールド（5つ）：verdict・exit_code・next_action・reasons・current_state
- next_action 必須フィールド（10つ）：kind・required_action・active_gate・feature・phase・stage・
  required_feature_scope・blocked_by・future_gates・state_refs
- properties: { "verdict": false }：verdict を next_action 内で明示禁止
- kind：7値インライン enum（スキーマ内で定義、別ファイル化しない）

条件付き必須フィールド（if/then 構文で next_action 内に定義）:
- repair_reasons（非空配列）：required_action = "repair_workflow_state" のとき必須
- action_parameters（オブジェクト、サブフィールド 6 つ必須）：required_action = "run_maintenance" のとき必須

受入 11(6) の制約①②③⑤も同じ if/then 構文でスキーマに定義する（MWP-0 T-020 の責務）。
```

### 設計（§5.3 kind 詳細フィールド）

```text
【design §5.3 next_action フィールドの意味】
| フィールド      | 役割                      |
|----------------|---------------------------|
| kind           | 現在地のカテゴリ（7値）     |
| required_action| 次にすべき操作の名前（機械が読む）|
| reason         | 状態の説明（人間が読む）    |
```

### タスク定義（T-020 先送り事項・完了条件）

```text
【T-020 先送り事項】
(a) 受入 11(6)①②③⑤の required_action 値ごとのフィールド制約を next_action_response.schema.json の
    if/then 構文で定義する（④の repair_reasons と⑥の action_parameters は T-015 完了条件2で対処済みのため除外）。
(b) next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
(c) design §5.3 の「廃止」と Req 2 受入 12 の「廃止予定」の表現を統一する。

【T-020 完了条件】
1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
3. スキーマの if/then 制約（先送り事項(a)）の失敗テストが作成され、実装で通過する。
4. WORKFLOW_NAVIGATION.md の next_drafting_gate 廃止に伴う記述を更新する。
5. design §5.3 と Req 2 受入 12 の「廃止」「廃止予定」の表現が統一されていること（手動確認）。
```

## Main Preanalysis

The main session LLM produced this preanalysis before writing the proposed criteria. Treat it as a hypothesis, not as ground truth.

```yaml
candidate_judgment_items:

  - item_id: mwp0-if-then-completeness
    status: open
    judgment_question: >
      受入 11(6)①②③⑤ が定める条件付きフィールド制約が、next_action_response.schema.json の
      if/then 構文と実装テストに漏れなく・正確に反映されているか。
    target_files:
      - .reviewcompass/schema/next_action_response.schema.json
      - tests/tools/test_t020_kind_redesign.py (SchemaIfThenConstraintTests クラス)
    source_materials:
      - 受入 11(6)① の原文（active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"）
      - 受入 11(6)②③⑤ の原文
      - design §5.2（if/then 構文で定義する旨の確定）
    preanalysis_finding: >
      ①の if/then 定義は active_gate/phase/stage=null のみを強制しているが、
      受入 11(6)① が明示する blocked_by.type="commit_stop_point" 制約はスキーマに含まれていない。
      テストにも blocked_by の型を検証するケースが存在しない。
      ただし、これは material を独立に読んだモデルが確認すべき事項であり、
      確定所見ではなく仮説として扱う。
    sensitivity: low

  - item_id: mwp0-kind-separation
    status: open
    judgment_question: >
      next --json の kind 出力が7値に限定され、commit-preflight が3値のみを返すことが
      実装とテストで保証されているか。
    target_files:
      - tools/check-workflow-action.py (next --json の kind 出力パス、_commit_preflight_next_action)
      - tests/tools/test_t020_kind_redesign.py (KindValueSeparationTests クラス)
    source_materials:
      - 受入 12（kind 値分離の仕様）
    preanalysis_finding: >
      next --json の出力は 7 値の enum を返すコードパスを持ち、
      _commit_preflight_next_action は commit_candidate/commit_mixing_risk/commit_unit_stale の
      3値のみを kind として返す。テストが両方向を覆っているかは独立確認が必要。
    sensitivity: low

  - item_id: mwp0-reason-reasons-separation
    status: open
    judgment_question: >
      next_action.reason（next_action 内の内側フィールド）と最上位の reasons 配列の意味的区別が
      スキーマ・設計・実装において十分に明確化されているか。
    target_files:
      - .reviewcompass/schema/next_action_response.schema.json
      - .reviewcompass/specs/workflow-management/design.md §5.3
    source_materials:
      - design §5.3（reason フィールドの説明：「状態の説明（人間が読む）」）
      - T-020 先送り事項(b)
    preanalysis_finding: >
      設計書 §5.3 は reason を「状態の説明（人間が読む）」と説明しているが、
      最上位の reasons 配列との意味的な対比が明示されていない。
      T-020(b) がこれを先送り事項として挙げているが、完了条件に明示的な検証方法がない。
    sensitivity: low

  - item_id: mwp0-upstream-intent-transfer
    status: open
    judgment_question: >
      要件→設計→タスク→実装の連鎖で、受入条件・責務境界・禁止事項が漏れ・弱体化・
      未根拠追加なく引き継がれているか。
    target_files:
      - .reviewcompass/schema/next_action_response.schema.json
      - .reviewcompass/schema/commit_preflight_response.schema.json
    source_materials:
      - 受入 11(6)①②③⑤（条件付きフィールド制約の原文）
      - 受入 12（kind 値分離の原文）
      - design §5.2（スキーマ設計の確定内容）
    preanalysis_finding: >
      受入 11(6)① の blocked_by.type 制約が上流（要件）に存在しながら、
      下流（スキーマ・テスト）で欠落している可能性がある。
      受入 E(設計書 §5.3 廃止表現の統一) と F(WORKFLOW_NAVIGATION.md 更新) は
      コミット履歴の確認で解決済みと判断したが、独立確認が必要。
    sensitivity: low

resolved_claims:
  - claim_id: mwp0-claim-e-deprecation-wording
    resolution: design.md の「廃止予定」が「廃止」に更新されていることをコミット履歴で確認
  - claim_id: mwp0-claim-f-navigation-update
    resolution: WORKFLOW_NAVIGATION.md に next_drafting_gate が残存しないことを確認
```

## Proposed API Review Criteria

The following is the complete proposed review criteria that will be used as the `--criteria-file` in the actual review-run. The reviewer must judge whether this criteria is sufficient to support an independent implementation review.

Source path: `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-review-run/review-target.md`

```markdown
# workflow-management implementation triad-review — MWP-0 (kind 7-value redesign)

run_id: 2026-06-27-workflow-management-implementation-mwp0-review-run
criteria_id: wm-implementation-mwp0-triad-review-2026-06-27
phase: implementation
stage: triad-review
variant: implementation_review_independent_3way

## Change Summary

MWP-0（next-json-kind-redesign）として、`next --json` の `kind` 値域を旧14値から7値へ整理し、コミット操作前確認用の3値（`commit_candidate`・`commit_mixing_risk`・`commit_unit_stale`）を `commit-preflight` サブコマンドへ移動した。
あわせて、スキーマに `required_action` 値ごとの条件付きフィールド制約（if/then 構文）を追加した。

主な成果物：
- `.reviewcompass/schema/next_action_response.schema.json`（kind 7値更新・if/then 制約④⑥はT-015で実装済み、①②③⑤をT-020で追加）
- `.reviewcompass/schema/commit_preflight_response.schema.json`（新規）
- `tools/check-workflow-action.py`（commit-preflight サブコマンド追加・next --json から3値除去）
- テスト群（1,496件通過）

## Review Question

このレビューでは、下記の範囲を独立して分析してほしい。選択肢を選ばせるのではなく、あなたが気づいた問題・疑問・改善案を率直に示してほしい。

1. **if/then 制約の完全性**：要件（受入 11(6)①②③⑤）が定める条件付きフィールド制約が、スキーマと実装に漏れなく、かつ正確に反映されているか。
2. **kind 値分離の正確性**：`next --json` の kind 出力が7値に限定され、`commit-preflight` サブコマンドへの3値の移動が設計通りに機能しているか。テストが両方向を十分に覆っているか。
3. **reason と reasons の責務分離**：`next_action.reason`（内側フィールド）と最上位の `reasons` 配列の意味的な区別が、設計書と実装において十分に明確化されているか。
4. **上流意図の継承**：要件→設計→タスク→実装の連鎖の中で、受入条件・責務境界・禁止事項が漏れ・弱体化・未根拠追加なく引き継がれているか。

分析は上記4点に限定せず、問題と判断したことは自由に指摘してよい。

## Scope / Out of Scope

**対象**：
- `next_action_response.schema.json` のスキーマ正確性（if/then 制約を中心に）
- `commit_preflight_response.schema.json` のスキーマ定義
- `check-workflow-action.py` の commit-preflight サブコマンドと kind 出力実装（関連箇所のみ）
- if/then 制約テスト群（`test_t020_kind_redesign.py` の SchemaIfThenConstraintTests クラス）
- 要件・設計・タスクとの整合

**対象外**：
- MWP-0 以外のタスク（T-001〜T-019 の実装詳細）
- `check-workflow-action.py` の他サブコマンドや他機能の実装
- テストカバレッジの網羅的な評価
- CI/CD パイプラインや運用手順

---

## SOURCE MATERIAL 1: 要件（受入 11(6) と受入 12）

```text
【Requirement 2 受入 11(6)】
required_action の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2 で確定している制約であり、
スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の表現方法は design で確定）。

① commit_stop_point の時：active_gate=null・phase=null・stage=null・blocked_by.type="commit_stop_point"
② run_reopen_pending_gate の時：active_gate 非 null・phase/stage は active_gate と一致・blocked_by=null
③ run_reopen_drafting の時：active_gate は stages/<phase>.yaml#drafting 形式・phase/stage はその drafting 単位と一致
④ repair_workflow_state の時：active_gate=null・phase=null・stage=null・repair_reasons に修復理由を含める
⑤ wait_for_human_decision の時：blocked_by.type で停止理由を区別
⑥ run_maintenance の時：action_parameters に maintenance_action・allowed_scope・allowed_files・
   completion_conditions・active_stack_frame_id・parent_frame_id を含める

上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の required_action 種別には
確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```text

```text
【Requirement 2 受入 12（MWP-0 で新設）】
本機能は commit_candidate、commit_mixing_risk、commit_unit_stale の3種類の判定を next --json の
kind から除外し、commit-preflight サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」
ではなく「コミット操作の前確認」であり、next --json の kind は作業の現在地のみを示す7種類
（completed / in_progress / blocking_in_progress / verification_pending /
  reopen_in_progress / feature_definition_required / unknown）に限定する。
```text

## SOURCE MATERIAL 2: 設計（design §5.2 スキーマ設計・§5.3 kind 詳細フィールド）

```text
【design §5.2 next_action_response.schema.json】
- 必須フィールド（5つ）：verdict・exit_code・next_action・reasons・current_state
- next_action 必須フィールド（10つ）：kind・required_action・active_gate・feature・phase・stage・
  required_feature_scope・blocked_by・future_gates・state_refs
- properties: { "verdict": false }：verdict を next_action 内で明示禁止
- kind：7値インライン enum（スキーマ内で定義、別ファイル化しない）

条件付き必須フィールド（if/then 構文で next_action 内に定義）:
- repair_reasons（非空配列）：required_action = "repair_workflow_state" のとき必須
- action_parameters（オブジェクト、サブフィールド 6 つ必須）：required_action = "run_maintenance" のとき必須

受入 11(6) の制約①②③⑤も同じ if/then 構文でスキーマに定義する（MWP-0 T-020 の責務）。
```text

```text
【design §5.3 kind 詳細フィールド（全 kind 共通フィールド）】
| フィールド      | 役割                      |
|----------------|---------------------------|
| kind           | 現在地のカテゴリ（7値）     |
| required_action| 次にすべき操作の名前（機械が読む）|
| reason         | 状態の説明（人間が読む）    |
```text

## SOURCE MATERIAL 3: タスク定義（T-020 の先送り事項(a)(b)）

```text
【T-020 先送り事項】
(a) 受入 11(6)①②③⑤の required_action 値ごとのフィールド制約を next_action_response.schema.json の
    if/then 構文で定義する（④の repair_reasons と⑥の action_parameters は T-015 完了条件2で対処済みのため除外）。
(b) next_action 内の reason フィールドと最上位の reasons 配列の責務差を設計書と実装で明確化する。
(c) design §5.3 の「廃止」と Req 2 受入 12 の「廃止予定」の表現を統一する。

【T-020 完了条件】
1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
3. スキーマの if/then 制約（先送り事項(a)）の失敗テストが作成され、実装で通過する。
4. WORKFLOW_NAVIGATION.md の next_drafting_gate 廃止に伴う記述を更新する。
5. design §5.3 と Req 2 受入 12 の「廃止」「廃止予定」の表現が統一されていること（手動確認）。
```text

---

## FILE: .reviewcompass/schema/next_action_response.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "$comment": "additionalProperties は指定しない（前向き拡張用）",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "$comment": "additionalProperties は指定しない（後ろ向き互換用）",
      "type": "object",
      "required": ["kind","required_action","active_gate","feature","phase","stage","required_feature_scope","blocked_by","future_gates","state_refs"],
      "properties": {
        "verdict": false,
        "kind": {
          "type": "string",
          "enum": ["in_progress","blocking_in_progress","verification_pending","reopen_in_progress","feature_definition_required","completed","unknown"]
        },
        "required_action": { "$ref": "urn:reviewcompass:schema:required_action" },
        "active_gate": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "feature": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "phase": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "stage": { "oneOf": [{ "type": "null" }, { "type": "string" }] },
        "required_feature_scope": { "type": "array", "items": { "type": "string" } },
        "blocked_by": { "oneOf": [{ "type": "object" }, { "type": "null" }] },
        "future_gates": { "type": "array" },
        "state_refs": { "type": "object" },
        "pending_gates": { "type": "array" }
      },
      "allOf": [
        {
          "if": { "properties": { "required_action": { "const": "repair_workflow_state" } }, "required": ["required_action"] },
          "then": { "required": ["repair_reasons"], "properties": { "repair_reasons": { "type": "array", "minItems": 1 } } }
        },
        {
          "if": { "properties": { "required_action": { "const": "run_maintenance" } }, "required": ["required_action"] },
          "then": { "required": ["action_parameters"], "properties": { "action_parameters": { "type": "object", "required": ["maintenance_action","allowed_scope","allowed_files","completion_conditions","active_stack_frame_id","parent_frame_id"] } } }
        },
        {
          "$comment": "① commit_stop_point: active_gate/phase/stage はすべて null（受入 11(6)①）",
          "if": { "properties": { "required_action": { "const": "commit_stop_point" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "null" }, "phase": { "type": "null" }, "stage": { "type": "null" } } }
        },
        {
          "$comment": "② run_reopen_pending_gate: active_gate 非 null、blocked_by=null（受入 11(6)②）",
          "if": { "properties": { "required_action": { "const": "run_reopen_pending_gate" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "string" }, "blocked_by": { "type": "null" } } }
        },
        {
          "$comment": "③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式（受入 11(6)③）",
          "if": { "properties": { "required_action": { "const": "run_reopen_drafting" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "string", "pattern": "^stages/.+\\.yaml#drafting$" } } }
        },
        {
          "$comment": "⑤ wait_for_human_decision: blocked_by 非 null かつ type フィールド必須（受入 11(6)⑤）",
          "if": { "properties": { "required_action": { "const": "wait_for_human_decision" } }, "required": ["required_action"] },
          "then": { "properties": { "blocked_by": { "type": "object", "required": ["type"], "properties": { "type": { "type": "string" } } } } }
        }
      ]
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```json

## FILE: .reviewcompass/schema/commit_preflight_response.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:commit_preflight_response",
  "$comment": "commit-preflight サブコマンドの応答スキーマ（MWP-0 T-020）",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": ["commit_candidate","commit_mixing_risk","commit_unit_stale"]
        }
      }
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```json

## FILE: tests/tools/test_t020_kind_redesign.py (SchemaIfThenConstraintTests クラスのみ — 抜粋)

```python
# ① commit_stop_point の制約（active_gate/phase/stage の null 強制のみ）
def test_commit_stop_point_valid_when_all_null(self): ...
def test_commit_stop_point_invalid_when_active_gate_nonnull(self): ...
def test_commit_stop_point_invalid_when_phase_nonnull(self): ...
def test_commit_stop_point_invalid_when_stage_nonnull(self): ...

# ② run_reopen_pending_gate の制約
def test_run_reopen_pending_gate_valid_with_nonnull_active_gate(self): ...
def test_run_reopen_pending_gate_invalid_when_active_gate_null(self): ...
def test_run_reopen_pending_gate_invalid_when_blocked_by_nonnull(self): ...

# ③ run_reopen_drafting の制約
def test_run_reopen_drafting_valid_with_drafting_active_gate(self): ...
def test_run_reopen_drafting_invalid_when_active_gate_not_drafting(self): ...
def test_run_reopen_drafting_invalid_when_active_gate_null(self): ...

# ⑤ wait_for_human_decision の制約
def test_wait_for_human_decision_valid_with_blocked_by_type(self): ...
def test_wait_for_human_decision_invalid_when_blocked_by_null(self): ...
def test_wait_for_human_decision_invalid_when_blocked_by_lacks_type(self): ...
```python

## FILE: tools/check-workflow-action.py（commit-preflight の kind 分岐実装 — 抜粋）

```python
def _commit_preflight_next_action(cwd, in_progress_files):
    if in_progress_files:
        return build_in_progress_next_action(cwd, in_progress_files[0])
    verification_targets = list_post_write_verification_targets(cwd)
    if verification_targets:
        manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
        if manifest_state != "completed":
            return {"kind": "verification_pending", "required_action": "run_post_write_verification", ...}
    commit_unit_state, _ = validate_commit_unit_record(cwd)
    commit_unit_codes = commit_unit_state.get("codes") or []
    if commit_unit_state.get("exists") and "COMMIT_MIXING_RISK" in commit_unit_codes:
        return {"kind": "commit_mixing_risk", "required_action": "split_or_refresh_commit_unit", ...}
    if commit_unit_state.get("exists") and "STALE_COMMIT_UNIT" in commit_unit_codes:
        return {"kind": "commit_unit_stale", "required_action": "refresh_commit_unit", ...}
    specs, missing = load_all_feature_specs(cwd)
    if missing:
        return {"kind": "unknown", "required_action": "repair_workflow_state", ...}
    commit_stop_point = resolve_normal_workflow_commit_stop_point_action(cwd, specs)
    if commit_stop_point:
        return commit_stop_point
    return {"kind": "commit_candidate", "required_action": "prepare_commit", ...}
```python

## Output Contract

所見は次の形式で出力してほしい。

```yaml
findings:
  - id: <連番（F-001 など）>
    severity: must-fix | should-fix | leave-as-is
    target: <対象ファイル名または関数名>
    summary: <1行の説明（日本語）>
    detail: <具体的な問題の説明。要件・設計の原文を引用して根拠を示す>
    suggestion: <修正の方向性（あれば）>
```yaml

所見がない場合は `findings: []` を返してほしい。
```

