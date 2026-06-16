diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index e40f7e14..fe66bc82 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -77,7 +77,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 13. ~~**Codex TODO hook の実環境発火確認（派生課題）**~~ **完了（2026-06-16）**：GUI 設定で当時のプロジェクト hook（ツール実行前／ツール実行後）を信頼した後、`TODO_NEXT_SESSION.md` の更新により `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`、`selected`、`drafted` が出ることを確認した。下書きは `.reviewcompass/runtime/session-record-drafts/codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` に生成された。2026-06-16 に Codex 公式 manual で `SessionStart` が利用可能と確認し、`.codex/hooks/session-record-promote-previous-draft.sh` を追加したため、現構成では PreToolUse／PostToolUse／SessionStart の各 hook を GUI 設定または `/hooks` で確認・信頼する必要がある。SessionStart 昇格 hook 自体は、次の Codex `SessionStart` で前セッション下書きを正式 2 層へ自動昇格する。未発火の主因は repo hook 未読込ではなく、非 managed hook の未 trust だった。`UserPromptSubmit` は引き続き使用禁止。
 14. **reopen approval gate の blocker 構造化（派生課題）**：`reopen-advance-gate` は pending gate 前進を機械化したが、approval gate で actor=human / proxy_model の承認待ちを `current_blocker` として構造的に設定する専用操作は未実装。次に reopen 実運用で承認待ち gate を扱う時に、手編集が再発するなら別タスクとして実装する。
 15. ~~**reopen-advance-gate の追加テスト（派生課題）**~~ **完了（2026-06-16）**：`ReopenAdvanceGateTests` に `--evidence` なし更新が exit 2 で拒否される回帰テストを追加した。実装側の拒否ロジックは既存どおり。
-16. **reopen-advance-gate の gate 正規化検査（派生課題）**：現状は `--gate` と `pending_gates[0]` の文字列一致で前進を判定し、既存 YAML 内の gate 文字列が標準形式かは追加検証しない。次に同コマンドを強化する時は、`pending_gates` の全要素が `stages/<phase>.yaml#<stage>` 形式として解釈できることを検査する。
+16. ~~**reopen-advance-gate の gate 正規化検査（派生課題）**~~ **完了（2026-06-16）**：`reopen-advance-gate` が `pending_gates` の全要素を `stages/<phase>.yaml#<stage>` 形式かつ既知 phase の review 系 gate（`triad-review`／`review-wave`／`alignment`／`approval`）として解釈できることを検査するようにした。壊れた gate 文字列や `drafting` gate が 1 件でもあれば更新前に exit 2 で拒否する。
 
 ## 5. 参照
 
diff --git a/docs/operations/WORKFLOW_PRECHECK.md b/docs/operations/WORKFLOW_PRECHECK.md
index 67adb178..00f7d547 100644
--- a/docs/operations/WORKFLOW_PRECHECK.md
+++ b/docs/operations/WORKFLOW_PRECHECK.md
@@ -135,7 +135,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `push` は、作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する
 - `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
 - `reopen-advance-step` は、現在 step と `--from-step` の一致、完了説明、判断理由、証跡を検査する
-- `reopen-advance-gate` は、先頭の pending gate だけを完了扱いに進め、根拠なし更新を拒否する
+- `reopen-advance-gate` は、pending gate 文字列が review 系 gate の正規形であること、先頭の pending gate だけを完了扱いに進めること、根拠なし更新を検査する
 - `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査する
 - `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する
 
diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 8612950f..3b58df72 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -182,7 +182,7 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 
 - 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
 - `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
-- `pending_gates` 自体は、`reopen-start` 等が作る標準の `stages/<phase>.yaml#<stage>` 形式を前提とする。既存 YAML 内の gate 文字列を追加検証する正規化処理は本コマンドの対象外である
+- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate（`triad-review`／`review-wave`／`alignment`／`approval`）として解釈できる必要がある。壊れた gate 文字列や `drafting` gate が 1 件でもあれば逸脱とする
 - `--evidence` が 1 件も無い更新は逸脱とする
 - 完了した gate を `pending_gates` から除去し、`completed_gates` へ追加する
 - `downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を追記する
