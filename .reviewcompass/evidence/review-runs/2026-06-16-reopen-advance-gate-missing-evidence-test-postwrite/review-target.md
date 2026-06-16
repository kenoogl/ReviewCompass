diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index e2f9bcf6..e40f7e14 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -76,7 +76,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 12. ~~**旧方式で生成された Codex セッション記録 2 件の後始末（派生課題）**~~ **完了（2026-06-16）**：旧生成物は、TODO hook が正式 2 層へ直接書いていた時期に、最終パス `.reviewcompass/evidence/sessions/2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` と `docs/sessions/auto-2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` へ作ったものだった。guarded commit 時に元 rollout `/Users/keno/.codex/sessions/2026/06/15/rollout-2026-06-15T15-51-42-019eca0c-e1c6-78f2-9060-0e546196fc12.jsonl` が生成時から変化していると判定され、対象がまだ進行中セッションだと確認できたため、旧生成物を正式 2 層記録としてコミットせず削除した。最終状態は、上記 2 ファイルは存在しない状態である。必要なら、このセッション終了後に同 rollout を `tools/session-record-backfill.py --session <jsonl> --source codex` で明示回収する。
 13. ~~**Codex TODO hook の実環境発火確認（派生課題）**~~ **完了（2026-06-16）**：GUI 設定で当時のプロジェクト hook（ツール実行前／ツール実行後）を信頼した後、`TODO_NEXT_SESSION.md` の更新により `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`、`selected`、`drafted` が出ることを確認した。下書きは `.reviewcompass/runtime/session-record-drafts/codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` に生成された。2026-06-16 に Codex 公式 manual で `SessionStart` が利用可能と確認し、`.codex/hooks/session-record-promote-previous-draft.sh` を追加したため、現構成では PreToolUse／PostToolUse／SessionStart の各 hook を GUI 設定または `/hooks` で確認・信頼する必要がある。SessionStart 昇格 hook 自体は、次の Codex `SessionStart` で前セッション下書きを正式 2 層へ自動昇格する。未発火の主因は repo hook 未読込ではなく、非 managed hook の未 trust だった。`UserPromptSubmit` は引き続き使用禁止。
 14. **reopen approval gate の blocker 構造化（派生課題）**：`reopen-advance-gate` は pending gate 前進を機械化したが、approval gate で actor=human / proxy_model の承認待ちを `current_blocker` として構造的に設定する専用操作は未実装。次に reopen 実運用で承認待ち gate を扱う時に、手編集が再発するなら別タスクとして実装する。
-15. **reopen-advance-gate の追加テスト（派生課題）**：実装は `--evidence` なし更新を拒否するが、`96112385` 時点の専用テストは正常更新と非先頭 gate 拒否に限られる。次に同コマンドを触る時は、根拠なし更新の exit 2 を追加テストする。
+15. ~~**reopen-advance-gate の追加テスト（派生課題）**~~ **完了（2026-06-16）**：`ReopenAdvanceGateTests` に `--evidence` なし更新が exit 2 で拒否される回帰テストを追加した。実装側の拒否ロジックは既存どおり。
 16. **reopen-advance-gate の gate 正規化検査（派生課題）**：現状は `--gate` と `pending_gates[0]` の文字列一致で前進を判定し、既存 YAML 内の gate 文字列が標準形式かは追加検証しない。次に同コマンドを強化する時は、`pending_gates` の全要素が `stages/<phase>.yaml#<stage>` 形式として解釈できることを検査する。
 
 ## 5. 参照
