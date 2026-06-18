# Raw Review Triage Summary

## Run

- run_id: `2026-06-19-workflow-management-requirements-integrated-design-review-run`
- variant: `implementation_review_independent_3way_codex_operator`
- phase: `requirements`
- criteria: `workflow_management_integrated_design_requirements_triad_review`

## Role Assignments

| role | path | provider | model | raw |
| --- | --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` |
| adversarial | api | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Summary

| model | parse_status | findings | severity |
| --- | --- | ---: | --- |
| gpt-5.4 | parsed | 6 | ERROR 2, WARN 3, INFO 1 |
| claude-opus-4-8 | parsed | 7 | WARN 4, INFO 3 |
| gemini-3.1-pro-preview | parsed | 1 | ERROR 1 |

## Same-root Clusters and Triage Proposal

### C1: 19 `required_action` と複合 operation の要件粒度

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-001`
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-002`
- summary: Requirement 13 は 19 語彙すべてを機械可読に対応付けると要求している一方、複合 operation の表現戦略を未確定候補として残している。残る語彙の `effect_kind` / `approval_required` 対応も requirements 本文だけでは検証しにくい。
- triage_proposal: must-fix
- rationale: operation contract の中核であり、design/tasks へ進む前に要求レベルで少なくとも「曖昧化しないための最小規則」または「全19語彙対応表」を置く必要がある。

### C2: side-track stack と commit mixing 防止の不変条件不足

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-002`
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-006`
- summary: Requirement 14 は frame 属性を列挙しているが、`staged_file_set` / `staged_file_digest` の採取時点、push 後の index 変化、pop 時の一致条件、親子 frame の重なり、digest/set 不一致時の扱いが不足している。
- triage_proposal: must-fix
- rationale: workflow drift と commit mixing の防止は今回の統合設計の重要目的であり、要件段で最低限の不変条件を示す必要がある。

### C3: 承認ゲートと `record_human_decision` の遷移・効果種別

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-003`
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-001`
- summary: `record_human_decision` は承認対象操作ではない点は示されているが、`effect_kind` が固定か条件付きか、拒否・保留・修正要求時に対象操作を許可しない最小遷移条件が requirements 上で弱い。
- triage_proposal: should-fix
- rationale: irreversible operation authorization に関わるため重要度は高い。ただし基本方針は既に書かれており、補強で足りる可能性が高い。

### C4: structured effective prompt の第1層機械検査不足

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-004`
- summary: Requirement 15 の機械検査が参照先・アンカー・長さ・manifest 一致に寄っており、`language_task.output_format` と `postconditions` の対応、`preconditions_checked` の実検査性、`on_completion` と operation contract の整合が弱い。
- triage_proposal: should-fix
- rationale: Phase 6 の LLM judge audit は後回し可能なので、第1層の機械検査で最低限の構造妥当性を持たせるのが自然。

### C5: cross-feature impact と review-wave への持ち上げ

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-005`
- summary: operation contract、effective prompt、snapshot は他 feature が consumer として参照し得るため、reopen 不要判断と impact review 不要判断を混同しないよう review-wave で確認する要求が必要。
- triage_proposal: should-fix
- rationale: 他 feature の正本 reopen は不要でも、review-wave で consumer 契約への影響確認を記録する必要がある。

### C6: D-003 / Phase 0 の canonical anchor

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-003`
- summary: Requirement 16 は D-003 全体を Phase 0 仕様とするが、参照先の所在が退避資料・working note・正本昇格予定の間で揺れて見える。
- triage_proposal: should-fix
- rationale: Phase 0 の失敗テストや repair 条件が D-003 節番号へ依存するため、stable canonical anchor の現在値を明示すると downstream risk が下がる。

### C7: `spec.json.reopened` と今回 R-0 scope の見え方

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-005`
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-gemini-3.1-pro-preview-judgment-001`
  - counterpoint: `2026-06-19-workflow-management-requirements-integrated-design-review-run-gpt-5.4-primary-006`
- summary: Claude と Gemini は `spec.json.reopened.intent=true` / `feature-partitioning=true` が R-0 scope と矛盾すると指摘した。一方、既存手順では `reopened` は履歴フラグとして残す運用であり、GPT は rollback 位置自体は整合していると見ている。
- triage_proposal: should-fix
- rationale: 既存 `REOPEN_PROCEDURE.md` では `reopened.<上流>` は履歴として true のまま残すため、単純に false へ戻すのは危険。今回の対応は `reopened` を変更するより、in-progress / classification / downstream impact 記録で「現在の reopen scope」と「履歴フラグ」を区別する補強が妥当。

### C8: Phase 番号順と実依存順の読み違い

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-004`
- summary: Phase 1 の一部が Phase 0 をブロックし、それ以外の Phase 1 schema は Phase 0 と並行可能という構造は正しいが、番号順が時系列順と誤読される余地がある。
- triage_proposal: leave-as-is
- rationale: 現時点では INFO。C6 や C1 の修正時に表現補強できるなら吸収する。

### C9: source note の draft / superseded 予定

- sources:
  - `2026-06-19-workflow-management-requirements-integrated-design-review-run-claude-opus-4-8-adversarial-007`
- summary: Requirement 13-16 の由来欄が draft / superseded 予定の source notes を参照している。
- triage_proposal: leave-as-is
- rationale: 今回の目的は source note を requirements に織り込むことなので、由来として残すのは妥当。design 段以降で正本 anchor を増やす際に自然に改善される。

## User-visible Gate

This is the user-visible triage gate. Do not ask proxy_model, edit requirements/design/tasks/implementation, update `spec.json`, move the phase, or commit this review response until the triage decisions are approved by the user or proxy_model under an approved proxy-mode request.
