# tasks triad-review triage summary：operation registry / preflight

date: 2026-06-16
review_run: 2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run
variant: implementation_review_independent_3way_codex_operator
phase: tasks

## Role assignments

| role | provider | model |
| --- | --- | --- |
| primary | openai-api | gpt-5.4 |
| adversarial | anthropic-api | claude-opus-4-8 |
| judgment | gemini-api | gemini-3.1-pro-preview |

## Raw result summary

| model | findings | severity |
| --- | ---: | --- |
| gpt-5.4 | 4 | WARN 3 / INFO 1 |
| claude-opus-4-8 | 6 | ERROR 2 / WARN 2 / INFO 2 |
| gemini-3.1-pro-preview | 1 | INFO 1 |

Total: ERROR 2 / WARN 5 / INFO 4

## 推奨 triage

### must-fix

| finding id | 理由 |
| --- | --- |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-001` | Requirement 12 受入 13（`next --json` 状態一意性）が完了条件・テスト要件・Req2/Req12 所有境界に十分落ちていない。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-002` | 完了条件 13 項目とテスト要件 12 項目が対応しておらず、`state_refs.next_action` の必須 dimensions 固定検証が不足している。 |

### should-fix

| finding id | 理由 |
| --- | --- |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-gpt-5.4-primary-001` | テスト成果物が粗く、review artifact / approval chain / current-session / nested issue / deployment export の失敗条件を分離しにくい。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-gpt-5.4-primary-002` | operation_family ごとの必須検査割当が弱く、review artifact 系の適用範囲が曖昧。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-gpt-5.4-primary-003` | deployment / export preflight の外部観測境界と verdict 基準が未定義。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-003` | T-011 を前提に含めるか、統合テスト側として前提外にするかの責務境界が曖昧。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-004` | criteria / document-type 一致と staged / unstaged 対象選択がテスト要件から落ちている。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-gemini-3.1-pro-preview-judgment-001` | `vocabulary_refs` が完了条件・テスト要件で明示されておらず、schema 検査対象から漏れる可能性がある。 |

### leave-as-is

| finding id | 理由 |
| --- | --- |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-gpt-5.4-primary-004` | Requirement 12 の追跡と Phase 1 read-only 境界を肯定する INFO。追加修正不要。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-005` | Phase 1 / Phase 2 分離と read-only 不変性を肯定する INFO。追加修正不要。 |
| `2026-06-16-workflow-management-tasks-operation-registry-preflight-review-run-claude-opus-4-8-adversarial-006` | LLM / provider / model 非依存の追跡を肯定する INFO。追加修正不要。 |

## Same-root clusters

- `next --json` 状態一意性と追跡不足：adversarial-001、adversarial-002。
- review artifact / operation_family / テスト粒度：primary-001、primary-002、adversarial-004、judgment-001。
- deployment / export 外部境界：primary-003。
- 既存タスクとの責務境界：adversarial-003。

## 推奨判断

推奨は、must-fix 2 件と should-fix 6 件を tasks.md に反映し、leave-as-is 3 件は肯定的所見として記録する案。

反映方針：

- T-014 完了条件とテスト要件を 1:1 に近づけ、特に `next --json` active state dimensions の必須キー固定検証を独立項目にする。
- `operation_family` ごとの必須検査割当と、review artifact 系の criteria / document-type / staged / unstaged 対象検査を明示する。
- deployment / export の外部観測境界を「明示入力で与えられた planned output / root の存在確認に限定」とする。
- T-011 は T-014 の前提ではなく、T-014 の個別テストを後段で統合検証するタスクとして扱うことを明示する。
- `vocabulary_refs` を schema / 完了条件 / テスト要件に明示する。
