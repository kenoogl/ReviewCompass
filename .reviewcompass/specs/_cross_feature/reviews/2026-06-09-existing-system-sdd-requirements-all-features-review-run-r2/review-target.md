---
run_id: 2026-06-09-existing-system-sdd-requirements-all-features-review-run-r2
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
supersedes_review_run: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run
---

# Requirements triad-review target: existing-system SDD code drift, all features, post-fix

## Review Purpose

Review whether the requirements fixes applied after the all-feature requirements triad-review resolve the approved must-fix / should-fix findings enough to complete `stages/requirements.yaml#triad-review`.

The prior all-feature run found:

1. must-fix: `conformance-evaluation` Requirement 10 made tasks look like a direct CE responsibility, conflicting with existing CE scope.
2. should-fix: CE candidate classification / output fields were too vague.
3. should-fix: `workflow-management` Requirement 9 conflict stop conditions and CE-to-WM handoff were too vague.
4. should-fix: indirect features require recorded checks, but likely do not need requirements body changes.
5. leave-as-is: all-feature scope and the reopen gate sequence were appropriate.

## Current Feature Scope

All seven features are in scope because the reopen record contains direct and indirect impact decisions for all features.

Direct features:

- `conformance-evaluation`
- `workflow-management`

Indirect features:

- `foundation`
- `runtime`
- `evaluation`
- `analysis`
- `self-improvement`

## Updated conformance-evaluation Requirement 10

Title: 既存システムへの後追い intent 追加時のコード由来差分抽出

Purpose:

保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加したとき、既存設計との衝突を確認しながら、実装コードから仕様追記候補と実装変更候補を証拠付きで取り出せるようにする。

Acceptance criteria after fixes:

1. 本機能は既存システムを対象に、追加 intent、既存 feature-partitioning、既存 requirements／design／tasks、実装コードを入力として扱う実行モードを持つ。ただし tasks は正式な推定・再作成対象ではなく、下流影響を確認する参照入力として扱う。
2. 本機能は実装コードから、現在の実装が前提にしている requirements 候補、design 候補、下流影響候補、実装変更候補を抽出し、それぞれにコード参照を付ける。tasks.md 本体の推定やタスク分解の確定は本機能の責務外とし、tasks への正式反映要否は `workflow-management` の reopen 手続きで判断する。
3. 本機能は抽出した候補を既存 requirements／design／tasks と比較し、候補ごとに最低限 `feature`、`phase`、`classification`、`code_refs`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` を記録する。`classification` は `existing_sufficient`、`spec_update_candidate`、`design_conflict_candidate`、`downstream_impact_candidate`、`implementation_change_candidate` のいずれかを基本値とし、人間判断が必要な場合は `needs_human_decision: true` を併記する。
4. 本機能は追加 intent と抽出候補の関係を記録する。追加 intent を満たすために、既存仕様追記で足りるのか、既存設計と衝突するのか、下流工程の確認が必要なのか、実装変更が必要なのかを区別する。
5. 本機能は固定チェックリストだけで候補を生成しない。コード参照、既存仕様の該当箇所、LLM による推定理由の要約を合わせて記録し、根拠が不足する候補は `needs_human_decision: true` とする。証拠・メタデータの語彙は `foundation` の契約を参照し、本機能で再定義しない。
6. 本機能は出力として、feature ごとの差分候補一覧、仕様更新草案、下流影響候補、実装変更候補、既存設計との衝突候補を含む評価記録を生成する。評価記録の詳細 schema は design 段で確定するが、requirements 段では前項の最小フィールドを外部可視契約とする。
7. 本機能は仕様本文を直接更新しない。仕様更新草案と実装変更候補を提示し、正式な requirements／design／tasks／implementation の更新は `workflow-management` の所定手続きで進める。
8. 本機能は ReviewCompass 自身を対象にした試行実行を許容し、その結果を workflow 手続き改善の入力として保存できる。

Updated trace:

- `XDI-CE-002`：既存システムに後追いで intent を追加した場合のコード由来仕様差分抽出、既存設計との衝突確認、仕様更新草案、下流影響候補、実装変更候補の分離は Requirement 10 の外部可視要件に含める。tasks.md 本体の推定は本機能の責務外とし、詳細な設計・タスク化は design／tasks 段で確定する。

## Updated workflow-management Requirement 9

Title: 既存システムへの後追い intent 追加時の下流再展開

Purpose:

保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加した場合でも、仕様駆動開発の順序を崩さず、既存設計との衝突確認を含めて下流工程へ進められるようにする。

Acceptance criteria after fixes:

1. 本機能は、既存システムで intent が追加または修正された場合、機能分割で受け皿 feature を判定し、受け皿がある feature は reopen 対象、受け皿がない場合は新 feature 候補として扱う。
2. 本機能は、既存 requirements に似た記述があることだけを理由に処理を終了しない。該当 feature を reopen し、requirements／design／tasks／implementation の各段で、修正不要か修正必要かを判定して記録する。
3. 本機能は、下流工程の各段で既存仕様との衝突確認を要求する。新しい要件や設計が既存設計、既存タスク、既存実装と矛盾する可能性がある場合は、衝突候補として記録し、reopen record の `current_blocker` に人間承認待ちを設定するか、該当 phase の approval gate で停止する。停止解除には、判定対象 gate、feature scope、判断、理由、証跡、判定者を `downstream_impact_decisions` に記録することを必要とする。
4. 本機能は、コード由来の仕様差分抽出を `conformance-evaluation` の評価記録として受け取り、正式な requirements／design／tasks／implementation 更新は本機能の reopen 手続きで進める。受け取り対象の評価記録は、最低限 `feature`、`phase`、`classification`、`code_refs`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` を持つ候補一覧を含む。
5. 本機能は、後追い intent 追加が既存 implementation まで影響する可能性を持つ場合、`impacted_downstream_phases` に requirements、design、tasks、implementation を含める。各段で `existing_sufficient` と判定する場合も、その判定対象 gate、feature scope、理由、証跡、判定者を `downstream_impact_decisions` に残す。
6. 本機能は、ReviewCompass 自身を試行対象にした場合も、通常の所定手続きとして扱う。試行中にワークフロー手続きの不足が見つかった場合は、本線作業と side track を区別し、必要なら `stages/in-progress/maintenance-*.yaml` を作成する。maintenance 進行中ファイルは、本線の `mainline_blocked_by`、許可範囲、許可ファイル、完了条件を持ち、完了時は `stages/completed/maintenance-*.yaml` に移す。

Updated trace:

- `XDI-WM-002`：既存システムへの後追い intent 追加時に、受け皿 feature の reopen、下流工程の修正要否判定、既存設計との衝突確認、conformance-evaluation 評価記録の正式手続きへの取り込み、衝突候補発見時の停止・承認・記録を行う契約は Requirement 9 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。

## Review Criteria

Classify findings as CRITICAL, ERROR, WARN, or INFO.

Use these labels in rationale when applicable:

- `must-fix`: still blocks requirements triad-review completion.
- `should-fix`: should be considered in this reopen chain but may be handled in review-wave/design/tasks.
- `leave-as-is`: record only.

Check especially:

1. Whether CE Requirement 10 no longer makes tasks.md inference or task decomposition a direct CE responsibility.
2. Whether CE still gives enough output structure for design/tests to proceed.
3. Whether WM Requirement 9 now defines conflict stop conditions and CE-to-WM handoff enough for requirements stage.
4. Whether indirect features still do not need requirements body changes.
5. Whether requirements triad-review can be considered complete after this post-fix check, or whether more requirements edits are needed.

Return YAML-compatible findings with at least:

- severity
- target_location
- description
- rationale
- verifying_commands
