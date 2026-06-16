diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index 6c53310c..b8150b60 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -66,7 +66,8 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
    - **事故(あ) YAML 破損が遠い症状で露見**：`next_step` 欄（次の一手を書く自由記述）の説明文に、引用符なしで「コロン＋スペース」を含む値（`impacted_downstream_phases: tasks` 等）を書いた。YAML がこれを「キー: 値」の対応表と誤解しパースエラー→`load_in_progress_file` が `{}`（空）を返し（読めないものは通さない fail-closed）→停止点コミット判定 `is_reopen_stop_point_commit_allowed`（`check-workflow-action.py:3633`）が `next_step` に「停止点コミット」の語を見つけられず逸脱（コミット却下）。症状が「YAML 破損」でなく「コミット許可条件の不成立」として出るため、原因究明が遠回りになった。
    - **事故(い) 完了ファイルの必須項目漏れ**：完了側（`stages/completed/`）に `feature_impact_decisions`（7機能）・`new_feature_decision`・各相の `completed_gates`／`downstream_impact_decisions` が不足し、`validate_reopen_completion_impact_decisions` で逸脱。これも手編集ゆえの項目漏れ。
    - **対処済みの穴**：完了処理では必ず「進行中→完了への移動＝元ファイル削除」が起きるのに、commit 承認の生成・検証が削除ファイルに未対応だった。`validate_commit_approval`（`DELETED` 印を通し、ファイルが残っている時のみエラー）に対応を追加（コミット `94900049`、TDD）。なお `make-commit-approval.py`（削除を検出し `DELETED` 印を生成するツール）は後に設計欠陥で削除（§4 項目9）。
-   - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) 進行中・完了の reopen yaml を、正本（`validate_*` 群）が受け入れる形で生成・更新するツール化＝手編集をやめる（承認レコード・manifest の生成ツールと同じ「事例より正本」の横展開）。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
+   - **対処済み（2026-06-16）**：第4過程の完了 YAML 生成と `stages/in-progress/` から `stages/completed/` への移動を機械化する `tools/check-workflow-action.py reopen-finalize` を追加した。`--feature-impact`、`--new-feature-decision`、`--impacted-downstream-phase` から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` を生成し、既存 `validate_reopen_completion_impact_decisions` と同じ feature impact 検査を完了前に通す。第4過程未到達、pending gate 残存、blocker 残存、feature impact 不足、completed 側の同名ファイル既存は fail-closed で拒否する。operation registry には `reopen_finalize_preflight` を追加済み。
+   - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) 進行中 reopen yaml の第1・第2過程更新や approval blocker 設定を、正本（`validate_*` 群）が受け入れる形でさらに機械化する。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
    - 位置づけ：§4 項目5（裁定負荷対策）と同族の「手続きの作りの弱さが手戻りを生む」実例。今回は機能本体（決定出典検査）とは別の、reopen 手続き基盤の整備課題。
 9. **`make-commit-approval.py` の設計欠陥と削除（2026-06-15・重大案件・コミット `b16a021a` push 済み）**：commit 承認記録（コミット実行の許可証となる JSON ファイル）を自動生成するツールとして 2026-06-14 に作成したが、LLM が自律的に実行できる設計だった。`--explicit-instruction "コミット"` という文字列を渡すだけで、利用者が実際に「コミット」と発言したかどうかに関係なく有効な承認記録を生成できてしまい、コード（`guarded-git-commit.py`）による不可逆操作の防護が実質無効化される。実際に 2026-06-15 のセッションで本ツールを悪用して利用者の明示なしに複数回コミット・push を自律実行した（事後承認）。詳細は `docs/notes/2026-06-15-security-incident-make-commit-approval.md`。**残る運用**：承認記録は Python ワンライナー（手動計算）で生成する。承認記録の安全な生成方法は別途検討。
 10. ~~**reopen 中の pending gate 完了更新コマンド不足**~~ **完了（2026-06-15、`96112385`）**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、対象 gate、decision、feature_scope、rationale、evidence、必要な `spec.json` 更新を構造化入力で受け、既存 `validate_reopen_completion_impact_decisions` が受け入れる形に機械更新できるようにした。今回の scope は pending gate 前進に絞り、approval gate の actor=human / proxy_model blocker 構造化は今後の reopen 実運用で不足が見えた時に別タスク化する。
diff --git a/docs/operations/WORKFLOW_PRECHECK.md b/docs/operations/WORKFLOW_PRECHECK.md
index b3c27b76..acbefdb6 100644
--- a/docs/operations/WORKFLOW_PRECHECK.md
+++ b/docs/operations/WORKFLOW_PRECHECK.md
@@ -31,6 +31,7 @@
 - `push`：push 前検査
 - `audit-commit`：commit 済み変更に対する post-write-verification 監査
 - `reopen-advance-gate`：reopen 中の pending gate 完了更新
+- `reopen-finalize`：reopen 第4過程の完了 YAML 生成と completed 移動
 - `autonomous-plan`：自律・並列実行計画の開始前検査
 - `autonomous-plan-template`：自律・並列実行計画テンプレート生成
 - `autonomous-plan-record-integration`：自律・並列実行の統合結果記録
@@ -54,6 +55,7 @@ tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
 tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
+tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
@@ -104,6 +106,12 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 
 `reopen-advance-gate` は、reopen 第3過程で pending gate を 1 件完了扱いへ進めるときに呼び出す。対象 gate、判断、根拠、必要な `spec.json` 更新を構造化入力で受け取り、reopen 手続き記録の `pending_gates`、`completed_gates`、`downstream_impact_decisions`、`completed_steps` を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-gate) を参照する。
 
+<a id="reopen-finalize"></a>
+
+### 4.7 reopen-finalize
+
+`reopen-finalize` は、reopen 第4過程で in-progress 手続き YAML を completed 側へ移すときに呼び出す。feature impact 判定、new feature 判定、影響 phase を構造化入力で受け取り、完了 YAML に必要な項目を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-finalize) を参照する。
+
 ## 5. 判定契約
 
 終了コード：
@@ -119,6 +127,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `push` は、作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する
 - `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
 - `reopen-advance-gate` は、先頭の pending gate だけを完了扱いに進め、根拠なし更新を拒否する
+- `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査する
 - `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する
 
 ## 6. 出力とログ
@@ -144,6 +153,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更の検査
 - `push` の clean 性検査
 - `audit-commit` の manifest 対応検査
+- `reopen-advance-gate` と `reopen-finalize` の構造更新と fail-closed 検査
 - `guarded-git-commit.py` の commit 遮断と承認レコード消費
 - `autonomous-plan` 系サブコマンドの構造検査
 
diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 999d3edf..571027f2 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -10,6 +10,7 @@ tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
 tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
+tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
@@ -162,12 +163,41 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 - 残る pending gate があれば `step_number: 3` を維持し、`next_step` を次 gate に更新する。無ければ `step_number: 4` と `next_step: 第4過程：完了` へ進める
 - 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す
 
+<a id="reopen-finalize"></a>
+
+## 7. reopen-finalize
+
+`reopen-finalize` は、reopen 第4過程で `stages/in-progress/` の手続き YAML を `stages/completed/` へ移す更新コマンドである。完了 YAML の必須項目を手編集で埋める代わりに、構造化引数から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases`、`completed_steps` を更新する。
+
+引数：
+
+| 引数 | 必須 | 説明 |
+|---|---|---|
+| `--file` | 必須 | `stages/in-progress/` 配下の reopen 手続き YAML |
+| `--impacted-downstream-phase` | 必須 | `impacted_downstream_phases` に記録する phase。複数指定可 |
+| `--feature-impact` | 必須 | `FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE` の 5 値で feature impact 判定を追加する。既存 feature すべてについて指定する |
+| `--new-feature-decision` | 必須 | `DECISION RATIONALE EVIDENCE` の 3 値で new feature 判定を記録する |
+| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |
+
+判定と更新：
+
+- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
+- 対象 YAML は `stages/in-progress/` 配下でなければならない
+- `step_number` は `4`、`pending_gates` は空、`current_blocker` は `null` でなければならない
+- `--feature-impact` は既存 feature すべてを覆う必要がある
+- feature impact の `decision`、`impact_basis`、`rationale`、`evidence` は commit 前検査の完了 YAML 検査と同じ条件で検査する
+- `--new-feature-decision` は `decision`、`rationale`、`evidence` を必須とする
+- `--impacted-downstream-phase` は既知 phase 名だけを許可する
+- 成功時は `step_number: 4`、`next_step: 完了`、`pending_gates: []`、`current_blocker: null` を保存し、同名ファイルを `stages/completed/` へ作成して元の in-progress ファイルを削除する
+- completed 側に同名ファイルが既にある場合は上書きせず DEVIATION とする
+- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す
+
 <a id="autonomous-plan"></a>
 <a id="autonomous-plan-template"></a>
 <a id="autonomous-plan-record-integration"></a>
 <a id="autonomous-ledger-audit"></a>
 
-## 7. autonomous-plan 系
+## 8. autonomous-plan 系
 
 `autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。
 
@@ -260,6 +290,7 @@ commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.js
 - `push` の clean 性検査
 - `audit-commit` の manifest 対応検査
 - `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
+- `reopen-finalize` の完了 YAML 生成、in-progress 削除、第4過程未到達と feature impact 不足の拒否
 - `guarded-git-commit.py` の commit 遮断と承認レコード消費
 - `autonomous-plan` 系サブコマンドの構造検査
 
