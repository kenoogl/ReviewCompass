# .codex/hooks/

Codex の hook 設定で呼び出すスクリプトを置く。

仕様：`.reviewcompass/guidance/WORKFLOW_PRECHECK.md` §12 段階 3 フック導入時の拡張余地

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

### `review-prompt-guide-inject.sh`（UserPromptSubmit hook）

**役割**：レビュー、審査、3者レビュー、triad、proxy、プロンプト、判定に関するユーザー発話を検出したとき、`.reviewcompass/guidance/discipline_llm_as_judge_prompting.md` を追加コンテキストとして注入する。3者レビューや proxy_model 判断の前に、材料揃え、問い設計、機微情報チェックを Codex が読み落とさないようにする。

**入力**：標準入力で Codex の UserPromptSubmit JSON ペイロードを受け取る。

```json
{"hook_event_name":"UserPromptSubmit","session_id":"<id>","cwd":"/path/to/repo","prompt":"3者レビューで確認してはどうか"}
```

**動作**：

1. JSON ペイロードから `prompt` と `cwd` を取得
2. `prompt` が `レビュー|審査|3者|triad|proxy|プロンプト|判定` に一致しなければ何もせず exit 0
3. `cwd/.reviewcompass/guidance/discipline_llm_as_judge_prompting.md` が存在しなければ何もせず exit 0
4. 一致した場合だけ、同規律本文を `hookSpecificOutput.additionalContext` として返す

**出力（該当時）**：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "..."
  }
}
```

**通過時**：何も出力せず exit 0。

**登録**：`.codex/hooks.json` の `hooks.UserPromptSubmit` セクションに登録済み。これはレビュー用プロンプト規律の注入専用であり、セッション記録の取り込みには使わない。

### `session-record-capture-previous-codex.sh`（SessionStart hook）

**役割**：新しい Codex セッション開始時に、payload の current `session_id` と `cwd` を使って、現在セッション以外の未記録 Codex rollout を 1 件だけ正式な 2 層セッション記録へ取り込む。手動 CLI は既定で最大 5 件まで連続回収できるが、hook では `--max-count 1` を指定してセッション開始時の副作用を抑える。

記録は生ログの丸写しではない。`$HOME/.codex/sessions/.../rollout-*.jsonl` を一次ソースにし、`tools/session-record-capture-previous-codex.py` から `tools/session-record-backfill.py --session <jsonl> --source codex` を呼び、`.reviewcompass/evidence/sessions/` の整形済み転写と `docs/sessions/` の人間向け記録を生成する。

`TODO_NEXT_SESSION.md` の更新、`PostToolUse`、`UserPromptSubmit`、`SessionEnd` は、Codex セッション会話記録の取り込みトリガーにしない。明示回収が必要な場合は、この hook と同じ CLI を手動実行する。

**入力**：標準入力で Codex の SessionStart JSON ペイロードを受け取る。

```json
{"hook_event_name":"SessionStart","session_id":"<current-id>","cwd":"/path/to/repo","source":"startup"}
```

**動作**：

1. `hook_event_name` が `SessionStart` でなければ `ignored_event` を記録して exit 0
2. `session_id` が無ければ `no_current_session_id` で exit 0
3. `cwd` が無ければ `no_cwd` で exit 0
4. `tools/session-record-capture-previous-codex.py --current-session-id <current> --repo-path <cwd>` を呼ぶ
5. CLI は current `session_id` を除外し、既存記録に `session_id` がある候補を飛ばし、hook では最新の未記録過去 rollout 1 件だけを正式 2 層記録へ取り込む
6. 取り込めない場合も含め常に exit 0

**手動実行**：

```bash
python3 tools/session-record-capture-previous-codex.py \
  --current-session-id <current-session-id> \
  --repo-path /path/to/repo
```

確認だけなら `--list` を付ける。既定では対象 repo の全件を、日時・短縮 ID・状態（現在 / 記録済み / 未記録）の表で表示する。直近 N 件だけ見たい場合は `--recent <件数>` を付ける。機械処理用の JSONL が必要な場合は `--format jsonl` を付ける。

```bash
python3 tools/session-record-capture-previous-codex.py \
  --current-session-id <current-session-id> \
  --repo-path /path/to/repo \
  --list

python3 tools/session-record-capture-previous-codex.py \
  --current-session-id <current-session-id> \
  --repo-path /path/to/repo \
  --list --recent 10

python3 tools/session-record-capture-previous-codex.py \
  --current-session-id <current-session-id> \
  --repo-path /path/to/repo \
  --list --format jsonl
```

手動実行は既定で最大 5 件まで処理する。件数を変える場合は `--max-count <件数>` を付ける。

**診断ログ**：既定で `.reviewcompass/runtime/session-record-capture-previous-codex.jsonl` に JSON Lines を追記する。hook 側の主な `event` は `missing_jq`、`ignored_event`、`no_current_session_id`、`no_cwd`、`no_capture_tool`、`capture_checked`、`capture_failed`。CLI 側は `current_session_skipped`、`already_recorded`、`selected`、`captured`、`capture_failed`、`no_unrecorded_previous_session` を同じログへ追記する。

**登録**：`.codex/hooks.json` の `hooks.SessionStart` セクションに matcher = `"startup|resume"` で登録済み。`.codex/hooks.json` の `hooks.SessionEnd` には Codex セッション記録 hook を登録しない。配置・変更後は Codex の GUI 設定画面または `/hooks` で利用者が hook を信頼する必要がある。

**依存**：bash、jq、Python、`tools/session-record-capture-previous-codex.py`、`tools/session-record-backfill.py`。jq が無い場合は Codex payload を読めないため、`missing_jq` を記録して安全側の no-op にする。

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

LLM（段階 1）が `tools/check-workflow-action.py` を意図して呼ぶ運用に加え、フックが自動発動することで「LLM が呼び忘れた」ケースを構造的に補う。詳細：`.reviewcompass/guidance/WORKFLOW_PRECHECK.md` §11 段階 1 規律との接続、`.reviewcompass/guidance/WORKFLOW_PRECHECK.md` §12 段階 3 フック導入時の拡張余地。

### fail-closed の度合い

仕様 §12.3 に従い：

- exit 0（OK）：通過
- exit 1（WARN）：警告だが通過（段階 1 が判断を担う）
- exit 2（DEVIATION）：遮断（フックが `deny` を返す）

commit については、段階 2 の `commit` サブコマンドが承認レコードを必須検査するため、LLM が直接 `git commit` を呼んだ場合でも承認レコードなしなら exit 2 になり、hook が deny する。

### rationale の取得方法

仕様 §12.2 で示された通り、フックは自動補完案を採用。`[stage-3 hook auto-invocation] <command>` というプレースホルダで段階 2 スクリプトを呼ぶ。stage 1（LLM）が独立して呼ぶ場合の rationale（利用者承認発言の引用等）とは別の経路。段階 2 のログ（JSON Lines）には両方が時系列で記録される。

## 関連参照

- 仕様：`.reviewcompass/guidance/WORKFLOW_PRECHECK.md` §12
- 共存モデル議論：`docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md`
- 段階 2 スクリプト：`tools/check-workflow-action.py`
- 段階 1 規律：`.reviewcompass/guidance/WORKFLOW_PRECHECK.md`
- 計画書 §5.8 補助層 C：`docs/plan/reconstruction-plan-2026-05-21.md`
