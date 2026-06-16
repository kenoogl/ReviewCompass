# post-write verification target: commit approval UX alignment

## User decision

- 1 回目の「コミット」は commit 準備として扱う。
- 2 回目は「承認」とし、提示済み staged 対象・digest・nonce・期限への承認、および LLM commit 実行代行承認として扱う。
- 2 回目を「コミット」とは呼ばない。
- テンプレート変更も今回の実装範囲に含める。

## Written changes

### TODO_NEXT_SESSION.md

`TODO_NEXT_SESSION.md` §2 を、commit 不可逆操作の要点として以下の意味に更新した。

- commit/push/spec.json/規律ファイル変更は利用者の明示承認が必要。
- commit は 1 回目の「コミット」を準備、2 回目の「承認」を提示済み内容への承認および LLM commit 実行代行承認として扱う。
- `tools/guarded-git-commit.py` 経由で実行する。
- 2 回目を「コミット」とは呼ばない。

### templates/todo/TODO_NEXT_SESSION.template.md

テンプレートの不可逆操作規律にも、同じ 1 回目「コミット」・2 回目「承認」の運用を反映した。

### docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md

Codex 向け運用ガイドの commit/push 項目にも、停止点到達後の 1 回目「コミット」は準備、2 回目「承認」は LLM commit 実行代行承認であることを反映した。

### tools/check_workflow_action/commit_approval.py

`ALLOWED_EXECUTION_DELEGATION_INSTRUCTIONS` に `"承認"` を追加し、実行代行承認レコードの生成・検証で同じ語彙を受け入れるようにした。

### tests/tools/test_check_workflow_action.py

`CommitExitCodeTests.test_commit_approval_delegate_execution_accepts_approval_instruction` を追加し、`承認\n` を stdin として渡した場合に `commit-execution-delegation.json` の `explicit_instruction` が `"承認"` になることを検証した。

## Verification requested

Check whether the post-write documentation changes accurately reflect the user decision and are consistent with the implementation/test change. Focus on:

1. agreement_reflection
2. reference_accuracy
3. existing_record_consistency
4. internal_logic
