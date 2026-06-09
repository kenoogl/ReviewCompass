---
run_id: 2026-06-09-existing-system-sdd-requirements-all-features-review-run
phase: requirements.triad-review
features:
  - foundation
  - runtime
  - evaluation
  - analysis
  - workflow-management
  - self-improvement
  - conformance-evaluation
reopen_procedure: stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml
supersedes_partial_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-run
---

# Requirements triad-review target: existing-system SDD code drift, all features

## Review Purpose

Review the requirements-stage impact of the 2026-06-09 reopen procedure across all ReviewCompass features.

The previous review-run covered only `conformance-evaluation` and `workflow-management`. That was insufficient because the reopen decision includes direct and indirect feature impact for all seven features. This run treats all features as in scope. It should decide whether the requirements-stage handling is complete enough to proceed to requirements review-wave, or whether the requirements text / impact decisions need must-fix correction first.

## User Clarification

The user clarified:

- The added intent is to support specification-driven development for an existing system after intent is added post hoc.
- When existing requirements, design, tasks, and implementation already exist, downstream work must still be reopened and checked.
- If direct and indirect impact are both included, all features are target features.
- On the safe side, requirements triad-review should be run across all features.

## Feature Impact Decisions From Reopen Record

| feature | decision | impact_basis | short rationale |
| --- | --- | --- | --- |
| conformance-evaluation | reopen_existing_feature | implementation_ownership | Owns code-derived requirements/design/task/implementation difference candidate extraction and comparison. |
| workflow-management | reopen_existing_feature | contract_ownership | Owns the formal reopen workflow and downstream propagation procedure. |
| foundation | indirect_check_only | consumer_or_derivative_only | Shared evidence, metadata, and vocabulary contracts may be referenced. |
| runtime | indirect_check_only | consumer_or_derivative_only | LLM execution and review evidence may be used, but core change is not runtime behavior. |
| evaluation | indirect_check_only | consumer_or_derivative_only | Evaluation outputs may be read, but core change is not metrics definition. |
| analysis | indirect_check_only | consumer_or_derivative_only | Reads or summarizes conformance outputs but does not own the extraction/decision process. |
| self-improvement | indirect_check_only | consumer_or_derivative_only | May consume workflow improvement signals but does not directly mutate the formal workflow. |

## Current Reopen State

The reopen procedure has:

- `classification: N-0`
- impacted features: all seven features by direct or indirect decision
- direct reopen features: `conformance-evaluation`, `workflow-management`
- indirect check features: `foundation`, `runtime`, `evaluation`, `analysis`, `self-improvement`
- `impacted_downstream_phases`: requirements, design, tasks, implementation
- next gate: `stages/requirements.yaml#triad-review`
- pending gates include requirements/design/tasks/implementation triad-review, review-wave, alignment, approval.

The current reopen record also says:

> requirements 正本を実質修正したため、alignment へ直行せず、requirements triad-review と review-wave を再実施してから alignment / approval に進む。

## Direct Requirements Changes

### conformance-evaluation Requirement 10

Title: 既存システムへの後追い intent 追加時のコード由来差分抽出

Purpose:

保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加したとき、既存設計との衝突を確認しながら、実装コードから仕様追記候補と実装変更候補を証拠付きで取り出せるようにする。

Acceptance criteria:

1. 本機能は既存システムを対象に、追加 intent、既存 feature-partitioning、既存 requirements／design／tasks、実装コードを入力として扱う実行モードを持つ。
2. 本機能は実装コードから、現在の実装が前提にしている requirements 候補、design 候補、tasks または実装上の作業契約候補を抽出し、それぞれにコード参照を付ける。
3. 本機能は抽出した候補を既存 requirements／design／tasks と比較し、次のいずれに当たるかを分類する：既存仕様で説明済み、仕様追記候補、既存設計との衝突候補、実装変更候補、人間判断が必要。
4. 本機能は追加 intent と抽出候補の関係を記録する。追加 intent を満たすために、既存仕様追記で足りるのか、既存設計と衝突するのか、実装変更が必要なのかを区別する。
5. 本機能は固定チェックリストだけで候補を生成しない。コード参照、既存仕様の該当箇所、LLM による推定理由を合わせて記録し、根拠が不足する候補は `needs_human_decision: true` とする。
6. 本機能は出力として、feature ごとの差分候補一覧、仕様更新草案、実装変更候補、既存設計との衝突候補を含む評価記録を生成する。
7. 本機能は仕様本文を直接更新しない。仕様更新草案と実装変更候補を提示し、正式な requirements／design／tasks／implementation の更新は `workflow-management` の所定手続きで進める。
8. 本機能は ReviewCompass 自身を対象にした試行実行を許容し、その結果を workflow 手続き改善の入力として保存できる。

Trace:

- `XDI-CE-002`：既存システムに後追いで intent を追加した場合のコード由来仕様差分抽出、既存設計との衝突確認、仕様更新草案と実装変更候補の分離は Requirement 10 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。

### workflow-management Requirement 9

Title: 既存システムへの後追い intent 追加時の下流再展開

Purpose:

保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加した場合でも、仕様駆動開発の順序を崩さず、既存設計との衝突確認を含めて下流工程へ進められるようにする。

Acceptance criteria:

1. 本機能は、既存システムで intent が追加または修正された場合、機能分割で受け皿 feature を判定し、受け皿がある feature は reopen 対象、受け皿がない場合は新 feature 候補として扱う。
2. 本機能は、既存 requirements に似た記述があることだけを理由に処理を終了しない。該当 feature を reopen し、requirements／design／tasks／implementation の各段で、修正不要か修正必要かを判定して記録する。
3. 本機能は、下流工程の各段で既存仕様との衝突確認を要求する。新しい要件や設計が既存設計、既存タスク、既存実装と矛盾する可能性がある場合は、衝突候補として記録し、人間承認または所定のレビューを停止点にする。
4. 本機能は、コード由来の仕様差分抽出を `conformance-evaluation` の出力として受け取り、正式な requirements／design／tasks／implementation 更新は本機能の reopen 手続きで進める。
5. 本機能は、後追い intent 追加が既存 implementation まで影響する可能性を持つ場合、`impacted_downstream_phases` に requirements、design、tasks、implementation を含める。各段で `existing_sufficient` と判定する場合も、その判定対象、理由、証跡を `downstream_impact_decisions` に残す。
6. 本機能は、ReviewCompass 自身を試行対象にした場合も、通常の所定手続きとして扱う。試行中にワークフロー手続きの不足が見つかった場合は、本線作業と side track を区別し、必要なら maintenance 進行中ファイルを作成する。

Trace:

- `XDI-WM-002`：既存システムへの後追い intent 追加時に、受け皿 feature の reopen、下流工程の修正要否判定、既存設計との衝突確認、conformance-evaluation 出力の正式手続きへの取り込みを行う契約は Requirement 9 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。

## Existing Requirements Context For Indirect Features

### foundation

Foundation owns shared review state, role abstractions, schemas, metadata, evidence vocabularies, and repository asset rules. Existing requirements say downstream features, including workflow-management and conformance-evaluation, must reference foundation vocabularies and not redefine them. The 2026-06-08 note says the added intent is received by fixed-pattern exclusion and evidence/metadata contracts.

### runtime

Runtime owns review execution control, treatment handling, prompt resolution, structured evidence output, human decision integration, verifier linkage, replay, phase review profiles, portable evidence bundles, and fixed-pattern exclusion. The 2026-06-08 note says the added intent is received by review execution control, prompt versioning, structured evidence output, and fixed-pattern exclusion.

### evaluation

Evaluation owns valid/invalid run separation, treatment comparison, metrics extraction, exclusions, derivative artifacts, metadata completeness, phase-aware evaluation, phase-specific metrics, review mode distinction, and external evidence bundle ingestion. It explicitly treats upstream document conformance as conformance-evaluation's responsibility. The 2026-06-08 note says the added intent is received by validity separation, metrics extraction from structured evidence, metadata checks, and review mode distinction.

### analysis

Analysis owns claim-to-evidence mapping, analysis data contracts, caveat tracking, separation from runtime/evaluation logic, preliminary/mature evidence distinction, review-mode report information, convergence visualization, and four output transforms. It explicitly does not perform conformance-evaluation's judgment work. The 2026-06-08 note says the added intent is received by claim-to-evidence mapping, evaluation-output provenance, separation from runtime/evaluation logic, and evidence classification.

### self-improvement

Self-improvement owns workflow-layer improvement only: observing drift between rules and practice, proposing discipline updates, validation, approval, history, and rollback. It can use conformance-evaluation results as input but does not directly mutate workflow files. Its requirements say workflow-management executes approved discipline changes through the formal procedure.

## Prior Partial Review Findings

The partial CE/WM review-run found these candidate clusters. Reassess them in all-feature scope:

1. CE Requirement 10 includes tasks and implementation task contracts, but existing CE scope says tasks are out of scope.
2. CE classification and output structure are under-specified for later design/tests.
3. WM conflict stop condition is under-specified.
4. The reopen gate sequence itself appears appropriate.

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use the following proposed labels in rationale when applicable:

- `must-fix`: blocks requirements triad-review completion and must be fixed before review-wave.
- `should-fix`: should be fixed in this reopen chain, but may be discussed before deciding whether it blocks this gate.
- `leave-as-is`: record only.

Check especially:

1. Whether all seven features are properly included in requirements-stage impact review.
2. Whether direct/indirect feature impact decisions are plausible and sufficiently evidenced.
3. Whether indirect features need requirements text changes, or whether `indirect_check_only` is sufficient.
4. Whether CE Requirement 10 conflicts with existing CE scope, especially tasks being out of scope.
5. Whether CE and WM boundaries are clear: CE extracts/classifies evidence-backed candidates; WM consumes them through the formal reopen workflow.
6. Whether foundation/runtime/evaluation/analysis/self-improvement contracts are affected by the added requirements.
7. Whether requirements triad-review can complete after fixes, or whether feature-partitioning must be reopened again.
8. Whether the current pending gates are appropriate for material requirements changes across all impacted features.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
