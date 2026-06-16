diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index b8150b60..e2f9bcf6 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -67,7 +67,8 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
    - **事故(い) 完了ファイルの必須項目漏れ**：完了側（`stages/completed/`）に `feature_impact_decisions`（7機能）・`new_feature_decision`・各相の `completed_gates`／`downstream_impact_decisions` が不足し、`validate_reopen_completion_impact_decisions` で逸脱。これも手編集ゆえの項目漏れ。
    - **対処済みの穴**：完了処理では必ず「進行中→完了への移動＝元ファイル削除」が起きるのに、commit 承認の生成・検証が削除ファイルに未対応だった。`validate_commit_approval`（`DELETED` 印を通し、ファイルが残っている時のみエラー）に対応を追加（コミット `94900049`、TDD）。なお `make-commit-approval.py`（削除を検出し `DELETED` 印を生成するツール）は後に設計欠陥で削除（§4 項目9）。
    - **対処済み（2026-06-16）**：第4過程の完了 YAML 生成と `stages/in-progress/` から `stages/completed/` への移動を機械化する `tools/check-workflow-action.py reopen-finalize` を追加した。`--feature-impact`、`--new-feature-decision`、`--impacted-downstream-phase` から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` を生成し、既存 `validate_reopen_completion_impact_decisions` と同じ feature impact 検査を完了前に通す。第4過程未到達、pending gate 残存、blocker 残存、feature impact 不足、completed 側の同名ファイル既存は fail-closed で拒否する。operation registry には `reopen_finalize_preflight` を追加済み。
-   - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) 進行中 reopen yaml の第1・第2過程更新や approval blocker 設定を、正本（`validate_*` 群）が受け入れる形でさらに機械化する。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
+   - **対処済み（2026-06-16）**：進行中 reopen yaml の第1・第2過程更新を機械化する `tools/check-workflow-action.py reopen-advance-step` を追加した。`--from-step` と現在 `step_number` の一致、完了説明、判断理由、証跡を必須にし、第1過程完了時は `第2過程：正本修正`、第2過程完了時は `第2過程：停止点コミット` へ進める。更新証跡は `reopen_step_records` に残す。operation registry には `reopen_advance_step_preflight` を追加済み。
+   - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) approval blocker 設定を、正本（`validate_*` 群）が受け入れる形でさらに機械化する。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
    - 位置づけ：§4 項目5（裁定負荷対策）と同族の「手続きの作りの弱さが手戻りを生む」実例。今回は機能本体（決定出典検査）とは別の、reopen 手続き基盤の整備課題。
 9. **`make-commit-approval.py` の設計欠陥と削除（2026-06-15・重大案件・コミット `b16a021a` push 済み）**：commit 承認記録（コミット実行の許可証となる JSON ファイル）を自動生成するツールとして 2026-06-14 に作成したが、LLM が自律的に実行できる設計だった。`--explicit-instruction "コミット"` という文字列を渡すだけで、利用者が実際に「コミット」と発言したかどうかに関係なく有効な承認記録を生成できてしまい、コード（`guarded-git-commit.py`）による不可逆操作の防護が実質無効化される。実際に 2026-06-15 のセッションで本ツールを悪用して利用者の明示なしに複数回コミット・push を自律実行した（事後承認）。詳細は `docs/notes/2026-06-15-security-incident-make-commit-approval.md`。**残る運用**：承認記録は Python ワンライナー（手動計算）で生成する。承認記録の安全な生成方法は別途検討。
 10. ~~**reopen 中の pending gate 完了更新コマンド不足**~~ **完了（2026-06-15、`96112385`）**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、対象 gate、decision、feature_scope、rationale、evidence、必要な `spec.json` 更新を構造化入力で受け、既存 `validate_reopen_completion_impact_decisions` が受け入れる形に機械更新できるようにした。今回の scope は pending gate 前進に絞り、approval gate の actor=human / proxy_model blocker 構造化は今後の reopen 実運用で不足が見えた時に別タスク化する。
diff --git a/docs/operations/WORKFLOW_PRECHECK.md b/docs/operations/WORKFLOW_PRECHECK.md
index acbefdb6..67adb178 100644
--- a/docs/operations/WORKFLOW_PRECHECK.md
+++ b/docs/operations/WORKFLOW_PRECHECK.md
@@ -30,6 +30,7 @@
 - `commit`：commit 前検査
 - `push`：push 前検査
 - `audit-commit`：commit 済み変更に対する post-write-verification 監査
+- `reopen-advance-step`：reopen 第1・第2過程の完了更新
 - `reopen-advance-gate`：reopen 中の pending gate 完了更新
 - `reopen-finalize`：reopen 第4過程の完了 YAML 生成と completed 移動
 - `autonomous-plan`：自律・並列実行計画の開始前検査
@@ -54,6 +55,7 @@ tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [-
 tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
+tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
 tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
 tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
@@ -100,15 +102,21 @@ commit は人の職掌範囲である。`--execution-actor llm` の場合、通
 
 reopen 開始時は、上流正本変更の影響範囲を分類し、必要な reopen 手続き記録を作成してから通常ワークフローへ戻す。commit 時には、reopen 手続き記録と spec.json の recheck 状態の整合を検査する。詳細は [REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) と [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。
 
+<a id="reopen-advance-step"></a>
+
+### 4.6 reopen-advance-step
+
+`reopen-advance-step` は、reopen 第1過程または第2過程の完了を記録し、次の state へ進めるときに呼び出す。`--from-step` は現在の `step_number` と一致していなければならず、判断理由と証跡なしの更新は拒否する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-step) を参照する。
+
 <a id="reopen-advance-gate"></a>
 
-### 4.6 reopen-advance-gate
+### 4.7 reopen-advance-gate
 
 `reopen-advance-gate` は、reopen 第3過程で pending gate を 1 件完了扱いへ進めるときに呼び出す。対象 gate、判断、根拠、必要な `spec.json` 更新を構造化入力で受け取り、reopen 手続き記録の `pending_gates`、`completed_gates`、`downstream_impact_decisions`、`completed_steps` を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-gate) を参照する。
 
 <a id="reopen-finalize"></a>
 
-### 4.7 reopen-finalize
+### 4.8 reopen-finalize
 
 `reopen-finalize` は、reopen 第4過程で in-progress 手続き YAML を completed 側へ移すときに呼び出す。feature impact 判定、new feature 判定、影響 phase を構造化入力で受け取り、完了 YAML に必要な項目を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-finalize) を参照する。
 
@@ -126,6 +134,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `commit` は、承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する
 - `push` は、作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する
 - `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
+- `reopen-advance-step` は、現在 step と `--from-step` の一致、完了説明、判断理由、証跡を検査する
 - `reopen-advance-gate` は、先頭の pending gate だけを完了扱いに進め、根拠なし更新を拒否する
 - `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査する
 - `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する
@@ -153,7 +162,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更の検査
 - `push` の clean 性検査
 - `audit-commit` の manifest 対応検査
-- `reopen-advance-gate` と `reopen-finalize` の構造更新と fail-closed 検査
+- `reopen-advance-step`、`reopen-advance-gate`、`reopen-finalize` の構造更新と fail-closed 検査
 - `guarded-git-commit.py` の commit 遮断と承認レコード消費
 - `autonomous-plan` 系サブコマンドの構造検査
 
diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 571027f2..8612950f 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -9,6 +9,7 @@ tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [-
 tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
+tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
 tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
 tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
@@ -130,9 +131,37 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 
 この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。
 
+<a id="reopen-advance-step"></a>
+
+## 6. reopen-advance-step
+
+`reopen-advance-step` は、reopen 手続きファイルの第1過程・第2過程を機械的に進める更新コマンドである。第1過程の完了では第2過程の正本修正へ進め、第2過程の完了では停止点コミット状態へ進める。
+
+引数：
+
+| 引数 | 必須 | 説明 |
+|---|---|---|
+| `--file` | 必須 | 対象の reopen 手続き YAML |
+| `--from-step` | 必須 | 完了扱いにする過程番号。`1` または `2` |
+| `--completed-step` | 必須 | `completed_steps` に追記する完了ステップ |
+| `--rationale` | 必須 | 判断理由 |
+| `--evidence` | 必須 | 判断根拠。複数指定可 |
+
+判定と更新：
+
+- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
+- `--from-step` は `1` または `2` のみを許可する
+- 対象 YAML の `step_number` は `--from-step` と一致する必要がある。不一致は逸脱とする
+- `--completed-step`、`--rationale`、`--evidence` が空の更新は逸脱とする
+- `completed_steps` に `--completed-step` を追記する
+- `reopen_step_records` に `from_step`、`completed_step`、`rationale`、`evidence` を追記する
+- `--from-step 1` の成功時は `step_number: 2`、`next_step: 第2過程：正本修正`、`current_blocker: null` を保存する
+- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: 第2過程の停止点としてコミットが必要` を保存する
+- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す
+
 <a id="reopen-advance-gate"></a>
 
-## 6. reopen-advance-gate
+## 7. reopen-advance-gate
 
 `reopen-advance-gate` は、reopen 手続きファイルの `pending_gates` を 1 件進める更新コマンドである。`spec-set` は in-progress reopen が存在する状態を通常作業として遮断するため、reopen 第3過程の gate 完了更新では本コマンドを使う。
 
@@ -165,7 +194,7 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 
 <a id="reopen-finalize"></a>
 
-## 7. reopen-finalize
+## 8. reopen-finalize
 
 `reopen-finalize` は、reopen 第4過程で `stages/in-progress/` の手続き YAML を `stages/completed/` へ移す更新コマンドである。完了 YAML の必須項目を手編集で埋める代わりに、構造化引数から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases`、`completed_steps` を更新する。
 
@@ -197,7 +226,7 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 <a id="autonomous-plan-record-integration"></a>
 <a id="autonomous-ledger-audit"></a>
 
-## 8. autonomous-plan 系
+## 9. autonomous-plan 系
 
 `autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。
 
@@ -289,6 +318,7 @@ commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.js
 - `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
 - `push` の clean 性検査
 - `audit-commit` の manifest 対応検査
+- `reopen-advance-step` の第1・第2過程更新、根拠なし更新拒否、現在 step 不一致拒否
 - `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
 - `reopen-finalize` の完了 YAML 生成、in-progress 削除、第4過程未到達と feature impact 不足の拒否
 - `guarded-git-commit.py` の commit 遮断と承認レコード消費
diff --git a/stages/operation-registry.yaml b/stages/operation-registry.yaml
index 2aa92d05..2d8397da 100644
--- a/stages/operation-registry.yaml
+++ b/stages/operation-registry.yaml
@@ -172,6 +172,50 @@ operations:
       - verdict
       - workflow_stage
 
+  - operation_id: reopen_advance_step_preflight
+    kind: workflow_state
+    operation_family: workflow_cli
+    canonical_invocation:
+      entrypoint: tools/check-workflow-action.py
+      subcommand: reopen-advance-step
+      options:
+        - --file
+        - --from-step
+        - --completed-step
+        - --rationale
+        - --evidence
+        - --json
+      positional_args: []
+      execution_context: repo_root
+    workflow_binding:
+      phase: null
+      stage: null
+      gate: null
+      next_action_kind: null
+    required_inputs:
+      - stages/in-progress/reopen-procedure-{date}.yaml
+      - from_step
+      - completed_step
+      - rationale
+      - evidence
+    target_identity:
+      - reopen_procedure
+      - step_number
+    planned_outputs:
+      - stages/in-progress/reopen-procedure-{date}.yaml
+    sequence_mode: serial_only
+    worktree_policy: allow_dirty_structured_state_update
+    pending_conflict_policy: require_matching_reopen_step
+    artifact_policy: update_existing_reopen_in_progress_only
+    family_required_checks:
+      - parser_invocation
+      - workflow_binding
+      - next_active_state_dimensions
+      - scope_consistency
+    vocabulary_refs:
+      - verdict
+      - workflow_stage
+
   - operation_id: commit_approval_chain_preflight
     kind: irreversible
     operation_family: commit_approval_chain
