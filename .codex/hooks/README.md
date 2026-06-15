# .codex/hooks/

Codex の hook 設定で呼び出すスクリプトを置く。

仕様：`docs/operations/WORKFLOW_PRECHECK.md` §12 段階 3 フック導入時の拡張余地

## ファイル一覧

### `pre-bash-precheck.sh`（補助層 C 段階 3、PreToolUse hook for Bash）

**役割**：Bash ツール呼び出しの直前に発動し、`git commit`／`git push` を検出したら段階 2 スクリプト（`tools/check-workflow-action.py`）を自動発動して事前検査する。`git commit` は `.reviewcompass/approvals/commit-approval.json` のユーザ承認レコードがない場合、通常変更だけでも deny される。

**入力**：標準入力で Codex の hook から PreToolUse JSON ペイロードを受け取る。

```json
{"tool_name": "Bash", "tool_input": {"command": "git commit -m ..."}}
```

**動作**：

1. JSON ペイロードから `tool_input.command` を取得
2. `git commit`／`git push` を正規表現で検出（パイプ／&&／;／| 経由も対応）
3. 該当しなければ何もせず exit 0（フック対象外として通過）
4. 該当した場合は `python3 tools/check-workflow-action.py <subcommand> --rationale "[stage-3 hook auto-invocation] <command>" --json` を呼び出し
5. 段階 2 スクリプトの終了コードを判定：
   - exit 0（OK）：何も出力せず exit 0 で通過
   - exit 1（WARN）：何も出力せず exit 0 で通過（警告だが通過、stage 1 規律が判断を担う）
   - exit 2（DEVIATION）：`hookSpecificOutput.permissionDecision = "deny"` の JSON を出力して exit 0

**出力（deny 時）**：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "段階 3 フック：DEVIATION 検出（理由文）"
  }
}
```

**通過時**：何も出力せず exit 0。

**依存**：bash、jq、python3、tools/check-workflow-action.py

**登録**：`.codex/hooks.json` の `hooks.PreToolUse` セクションに matcher = `"Bash"` で登録済み。

### `session-record-capture-previous.sh`（SessionStart hook）

**役割**：Codex の新セッション開始時に、現セッション以外で最新の同一 repo Codex rollout を 1 件だけ、2 層セッション記録へ単一取り込みする。

Codex の hook では `Stop` が turn scope であり、Claude の `SessionEnd` 相当としては使わない。進行中ログの毎ターン取り込みを避けるため、`SessionStart` で前回分だけを回収する。

**入力**：標準入力で Codex の SessionStart JSON ペイロードを受け取る。

```json
{"hook_event_name":"SessionStart","session_id":"<id>","cwd":"/path/to/repo","source":"startup"}
```

**動作**：

1. `cwd` が無ければ何もせず exit 0
2. `$HOME/.codex/sessions` 配下の `rollout-*.jsonl` を探索
3. 先頭 `session_meta.payload.cwd` が `cwd` と一致または配下のものだけを対象化
4. `session_meta.payload.id` が `session_id` と一致する現セッションを除外
5. mtime 最新の 1 件を `python3 tools/session-record-backfill.py --session <jsonl> --source codex` で取り込む
6. 取り込めない場合も含め常に exit 0

**出力先**：既定は `.reviewcompass/evidence/sessions/` と `docs/sessions/`。テスト用に `RC_SESSION_EVIDENCE_DIR`／`RC_SESSION_DOCS_DIR` で差し替え可能。

**登録**：`.codex/hooks.json` の `hooks.SessionStart` セクションに登録済み。

## テスト

ユニットテスト：`tests/hooks/test_pre_bash_precheck.py`（7 件）

実行：

```
cd /Users/Daily/Development/ReviewCompass
python3 -m unittest tests.hooks.test_pre_bash_precheck -v
```

テスト構成：

- `HookPassThroughTests`（3 件）：非 git／git status／git log の通過確認
- `HookCommitTests`（3 件）：承認済み通常 commit／承認なし commit／credentials 含む commit
- `HookPushTests`（2 件）：clean push／dirty push

## 設計の要点

### 段階 1 規律との関係

LLM（段階 1）が `tools/check-workflow-action.py` を意図して呼ぶ運用に加え、フックが自動発動することで「LLM が呼び忘れた」ケースを構造的に補う。詳細：`docs/operations/WORKFLOW_PRECHECK.md` §11 段階 1 規律との接続、`docs/operations/WORKFLOW_PRECHECK.md` §12 段階 3 フック導入時の拡張余地。

### fail-closed の度合い

仕様 §12.3 に従い：

- exit 0（OK）：通過
- exit 1（WARN）：警告だが通過（段階 1 が判断を担う）
- exit 2（DEVIATION）：遮断（フックが `deny` を返す）

commit については、段階 2 の `commit` サブコマンドが承認レコードを必須検査するため、LLM が直接 `git commit` を呼んだ場合でも承認レコードなしなら exit 2 になり、hook が deny する。

### rationale の取得方法

仕様 §12.2 で示された通り、フックは自動補完案を採用。`[stage-3 hook auto-invocation] <command>` というプレースホルダで段階 2 スクリプトを呼ぶ。stage 1（LLM）が独立して呼ぶ場合の rationale（利用者承認発言の引用等）とは別の経路。段階 2 のログ（JSON Lines）には両方が時系列で記録される。

## 関連参照

- 仕様：`docs/operations/WORKFLOW_PRECHECK.md` §12
- 共存モデル議論：`docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md`
- 段階 2 スクリプト：`tools/check-workflow-action.py`
- 段階 1 規律：`docs/disciplines/discipline_workflow_precheck_invocation.md`
- 計画書 §5.8 補助層 C：`docs/plan/reconstruction-plan-2026-05-21.md`
