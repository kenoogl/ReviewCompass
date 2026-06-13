# .claude/hooks/

Claude Code のフック機構（PreToolUse 等）に登録するスクリプトを置く。

仕様：`docs/operations/WORKFLOW_PRECHECK.md` §12 段階 3 フック導入時の拡張余地

## ファイル一覧

### `pre-bash-precheck.sh`（補助層 C 段階 3、PreToolUse hook for Bash）

**役割**：Bash ツール呼び出しの直前に発動し、`git commit`／`git push` を検出したら段階 2 スクリプト（`tools/check-workflow-action.py`）を自動発動して事前検査する。`git commit` は `.reviewcompass/approvals/commit-approval.json` のユーザ承認レコードがない場合、通常変更だけでも deny される。

**入力**：標準入力で Claude Code の hook から PreToolUse JSON ペイロードを受け取る。

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

**登録**：`.claude/settings.json` の `hooks.PreToolUse` セクションに matcher = `"Bash"` で登録済み。

### `session-record-capture.sh`（会話ログ自動保持、SessionEnd hook）

**役割**：Claude のセッション終了時に発火し、当該セッションの会話ログ（jsonl）を 2 層のセッション記録（層1＝整形済み転写 `.reviewcompass/evidence/sessions/`、層2＝人が読む記録 `docs/sessions/auto-*.md`）へ自動取り込みする。PLC-DEC-007 候補5（会話転写を一次ソースとし機械抽出で記録を生成）の going-forward 取り込み。「利用する LLM が、利用時の自分のログを残す」方針に基づく Claude 専用フック。

**入力**：標準入力で SessionEnd の JSON ペイロードを受け取る。

```json
{"hook_event_name":"SessionEnd","session_id":"<id>","transcript_path":"/.../<id>.jsonl","cwd":"/path/to/repo","reason":"clear"}
```

**動作**：

1. `transcript_path` があればそれを使う。無ければ `session_id` と `cwd` から `$HOME/.claude/projects/<cwd の / を - に置換>/<session_id>.jsonl` を復元する
2. 当該 jsonl が存在すれば `python3 tools/session-record-backfill.py --session <path> --source claude` を呼び、1 セッション分だけ取り込む（来歴刻印・再現性チェック・機微の fail-closed はツール側が担保）
3. 取り込めるログが無い場合も含め常に exit 0（セッション終了を妨げない）

**出力先の差し替え**：既定は repo の正規置き場。テスト時は環境変数 `RC_SESSION_EVIDENCE_DIR`（層1）／`RC_SESSION_DOCS_DIR`（層2）で temp に差し替える。

**取りこぼしの安全網**：クラッシュ等で SessionEnd が発火しなかったセッションは、オフラインの一括バックフィル（`python3 tools/session-record-backfill.py`）で後から取り込む（PLC-DEC-007 追補：過去分はベストエフォート）。

**Codex 複製はしない**：本フックは Claude 専用（利用する LLM ごとに自分のログを残す方針）。`pre-bash-precheck.sh` のような `.codex/` との同一性対象には含めない。Codex 側は Codex の機構で別途対応する。

**依存**：bash、jq、python3、tools/session-record-backfill.py

**登録**：`.claude/settings.json` の `hooks.SessionEnd` セクションに matcher なし（全終了理由）で登録済み。

## Codex 複製との同一性

フック本体 `pre-bash-precheck.sh` は `.claude/hooks/` と `.codex/hooks/` の両複製を同一内容に保つ。同一性は `tests/hooks/test_claude_hook_repository.py` の parity テストで機械検査する。本体を変更する場合は両複製へ同時に反映する。

## テスト

ユニットテスト：

- 挙動：`tests/hooks/test_pre_bash_precheck.py`（8 件、同一内容の codex 複製を対象に実行）
- リポジトリ管理状態と複製同一性：`tests/hooks/test_claude_hook_repository.py`

実行：

```
cd /Users/Daily/Development/ReviewCompass
python3 -m unittest discover -s tests/hooks -v
```

挙動テストの構成：

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
- Codex 側の登録：`.codex/hooks.json`、`.codex/hooks/README.md`
- 計画書 §5.8 補助層 C：`docs/plan/reconstruction-plan-2026-05-21.md`
