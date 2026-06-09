---
run_id: 2026-06-09-existing-system-sdd-requirements-review-run
phase: requirements.triad-review
features:
  - conformance-evaluation
  - workflow-management
reopen_procedure: stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml
---

# Requirements triad-review target: existing-system SDD code drift

## Review Purpose

Review the requirements updates added for the 2026-06-09 reopen procedure.

The user clarified that the added intent is not merely to confirm whether existing specifications are sufficient. The purpose is to support applying specification-driven development to an existing system where intent is added after requirements, design, tasks, and implementation already exist. The workflow must notice possible conflicts with existing design and implementation while deriving new requirements/design/tasks/implementation updates.

This review should decide whether the new requirements are clear enough to proceed to requirements review-wave, or whether they need must-fix correction before downstream design/tasks/implementation work.

## Scope

Primary target requirements:

- `.reviewcompass/specs/conformance-evaluation/requirements.md` Requirement 10
- `.reviewcompass/specs/workflow-management/requirements.md` Requirement 9

Related reopen state:

- `stages/in-progress/reopen-procedure-2026-06-09-existing-system-sdd-code-drift.yaml`

Related implementation and operation evidence:

- `tools/check-workflow-action.py`
- `docs/operations/REOPEN_PROCEDURE.md`
- `docs/operations/WORKFLOW_NAVIGATION.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`

## Added Requirement: conformance-evaluation Requirement 10

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

Trace addition:

- `XDI-CE-002`：既存システムに後追いで intent を追加した場合のコード由来仕様差分抽出、既存設計との衝突確認、仕様更新草案と実装変更候補の分離は Requirement 10 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。

## Added Requirement: workflow-management Requirement 9

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

Trace addition:

- `XDI-WM-002`：既存システムへの後追い intent 追加時に、受け皿 feature の reopen、下流工程の修正要否判定、既存設計との衝突確認、conformance-evaluation 出力の正式手続きへの取り込みを行う契約は Requirement 9 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。

## Reopen State

The current reopen procedure has:

- `classification: N-0`
- impacted features: `conformance-evaluation`, `workflow-management`
- `impacted_downstream_phases`: requirements, design, tasks, implementation
- next gate: `stages/requirements.yaml#triad-review`
- pending gates include requirements/design/tasks/implementation triad-review, review-wave, alignment, approval.

The reopen record states:

> requirements 正本を実質修正したため、alignment へ直行せず、requirements triad-review と review-wave を再実施してから alignment / approval に進む。

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use the following labels in the finding rationale when applicable:

- `must-fix`: blocks requirements triad-review completion and must be fixed before review-wave.
- `should-fix`: should be fixed in this reopen chain, but may be discussed before deciding whether it blocks this gate.
- `leave-as-is`: record only.

Check especially:

1. Whether CE Requirement 10 captures the user's clarified intent: existing-system SDD from a newly added intent, with code-derived evidence extraction and conflict detection.
2. Whether WM Requirement 9 captures the workflow side: reopen existing features, do not stop because similar requirements already exist, and propagate through requirements/design/tasks/implementation.
3. Whether the two requirements have a clear boundary: conformance-evaluation extracts and classifies code/spec difference candidates; workflow-management consumes those outputs through the formal reopen workflow.
4. Whether either requirement contradicts existing CE requirements that previously limited conformance-evaluation to requirements/design and treated tasks as out of scope.
5. Whether either requirement is too vague to design or test later, especially around outputs, classification labels, evidence, and human decision points.
6. Whether the current reopen pending gates are appropriate for a material requirements change.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
