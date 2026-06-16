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

### `session-record-capture-current-on-todo.sh`（PostToolUse hook）

**役割**：`TODO_NEXT_SESSION.md` の更新を合図に、現 Codex セッションの rollout を 1 件だけ、runtime 下書きへ保存する。

Codex の hook では `Stop` が turn scope であり、Claude の `SessionEnd` 相当としては使わない。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用禁止とし、誤登録されても `ignored_event` を診断ログに残して終了する。Codex では、セッション継続時に `TODO_NEXT_SESSION.md` を更新する運用を合図として使い、TODO の内容 hash が前回保存時から変わった場合だけ現セッションの下書きを更新する。TODO は 1 セッション内で複数回更新され得るため、更新ごとに追記専用マージで伸びた分を反映する。

**2026-06-16 実装反映**：hook は現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接書かない。正式な 2 層セッション記録は、次の Codex `SessionStart` で `session-record-promote-previous-draft.sh` が前セッション下書きを昇格する。手動復旧が必要な場合は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` または終了済み rollout を明示した backfill を使う。昇格 CLI は現在の `session_id` と同一のセッションを拒否する。診断ログ event は、正式記録と区別するため `drafted`／`draft_failed` を使う。

**入力**：標準入力で Codex の PostToolUse JSON ペイロードを受け取る。

```json
{"hook_event_name":"PostToolUse","session_id":"<id>","cwd":"/path/to/repo","tool_input":{"file_path":"/path/to/repo/TODO_NEXT_SESSION.md"}}
```

**動作**：

1. `hook_event_name` が `PostToolUse` でなければ `ignored_event` を記録して exit 0
2. `cwd` が無ければ何もせず exit 0
3. `cwd/TODO_NEXT_SESSION.md` が無ければ何もせず exit 0
4. TODO の sha256 を、`session_id + cwd` ごとの状態ファイルに残した前回 hash と比較する
5. 初回かつ hook payload に `TODO_NEXT_SESSION.md` が含まれない場合は baseline だけ記録し、既に dirty な TODO を誤回収しない
6. TODO hash が変わっていなければ何も取り込まない
7. TODO hash が変わっていても `session_id` が無ければ、並行セッション誤回収を避けるため推測せず終了する
8. `$HOME/.codex/sessions` 配下から `session_meta.payload.id == session_id` かつ `cwd` が一致または配下の rollout を選ぶ
9. `RC_SESSION_DRAFT_DIR`（未指定なら既定 runtime 下書き先）を `python3 tools/session-record-draft.py --session <jsonl> --source codex --draft-dir <draft-dir>` へ渡し、runtime 下書きへ保存する
10. 保存できない場合も含め常に exit 0

**出力先**：既定は `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md`。テスト用に `RC_SESSION_DRAFT_DIR` で差し替え可能。正式な 2 層記録は終了済みセッションを対象にした昇格操作または明示 backfill で作る。

**診断ログ**：hook が呼ばれたか、どの理由で通過したかを後から確認できるよう、既定で `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に JSON Lines を追記する。テスト用に `RC_SESSION_HOOK_LOG` で差し替え可能。主な `event` は `ignored_event`、`baseline_recorded`、`todo_unchanged`、`todo_changed`、`no_session_id`、`no_codex_root`、`no_current_session`、`selected`、`drafted`、`draft_failed`。
TODO hash の状態ディレクトリはテスト用に `RC_SESSION_HOOK_STATE_DIR` で差し替え可能。

**昇格時の current 確認**：`--session-id` には正式記録へ昇格したい終了済みセッションの ID を渡す。`--current-session-id` には、昇格対象ではなく今動いている Codex セッションの ID を渡す。通常は TODO 更新後に診断ログを見て、最新の `selected` event の `selected_session_id` を current ID として確認する。`drafted` は下書き保存成功の確認用 event として扱う。`selected` が無く current ID を取得できない場合は推測せず、昇格操作を行わない。

**登録**：`.codex/hooks.json` の `hooks.PostToolUse` セクションに登録済み。`UserPromptSubmit` には登録しない。TODO を更新しないセッション、クラッシュ、hook 失敗、または `session_id` が取れない場合は、終了済み rollout を指定した `tools/session-record-backfill.py --session <jsonl> --source codex` による明示回収を使う。

### `session-record-promote-previous-draft.sh`（SessionStart hook）

**役割**：新しい Codex セッション開始時に、現 session_id と異なる最新の runtime 下書き 1 件を正式 2 層記録へ昇格する。Codex 公式 hook 仕様では `SessionStart` が thread scope で利用できるため、前セッションの正式化はこの hook が担う。`Stop` は turn scope のため、セッション終了確定には使わない。

**入力**：標準入力で Codex の SessionStart JSON ペイロードを受け取る。

```json
{"hook_event_name":"SessionStart","session_id":"<current-id>","cwd":"/path/to/repo","source":"startup"}
```

**動作**：

1. `hook_event_name` が `SessionStart` でなければ `ignored_event` を記録して exit 0
2. `session_id` または `cwd` が無ければ何もせず exit 0
3. runtime 下書きディレクトリから `codex-<session_id>.md` を探す
4. current `session_id` と同じ下書きは除外する
5. 残った下書きのうち最新 1 件を選ぶ。最新候補の hash が不一致の場合は、古い候補へフォールバックせず `previous_draft_in_progress` を記録して終了する
6. 最新候補の下書き frontmatter `source_sha256` と現在の元 rollout の sha256 が一致する場合だけ、`tools/session-record-promote-draft.py` に current `session_id` と出力先を渡して昇格する
7. 昇格失敗も含め常に exit 0

**診断ログ**：既定で `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` に JSON Lines を追記する。テスト用に `RC_SESSION_PROMOTE_HOOK_LOG` で差し替え可能。主な `event` は `missing_jq`、`ignored_event`、`no_current_session_id`、`no_cwd`、`no_draft_dir`、`no_promote_tool`、`no_previous_draft`、`selected`、`previous_draft_in_progress`、`previous_draft_unverifiable`、`promoted`、`promote_failed`。`missing_jq` は Codex payload の解析に必要な jq が見つからないため、安全側の no-op にしたことを表す。`previous_draft_in_progress` は、下書き作成時の `source_sha256` と現在の元 rollout の sha256 が不一致で、対象 rollout がまだ伸びている可能性があるため正式化しなかったことを表す。`previous_draft_unverifiable` は、下書きまたは rollout の hash 確認に必要な情報が不足しているため正式化しなかったことを表す。複数の終了済み下書きが溜まっている場合も、この hook は最新候補 1 件だけを扱う。最新候補が不一致または検証不能なら古い候補へは進まず、残りは次回 `SessionStart` または明示 backfill の対象とする。

**登録**：`.codex/hooks.json` の `hooks.SessionStart` セクションに matcher = `"startup|resume"` で登録済み。配置・変更後は Codex の GUI 設定画面または `/hooks` で利用者が hook を信頼する必要がある。

**依存**：bash、jq、Python、`tools/session-record-promote-draft.py`。jq が無い場合は Codex payload を読めないため、`missing_jq` を記録して安全側の no-op にする。導入時チェックでも jq の存在を確認する。

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
