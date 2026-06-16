---
date: 2026-06-16
gate: stages/implementation.yaml#alignment
feature: workflow-management
reopen: R-0（commit-execution-delegation-formal-cli）
decision: existing_sufficient
---

# implementation alignment：commit execution delegation formal CLI

## 対象

workflow-management reopen R-0 `commit-execution-delegation-formal-cli` の implementation alignment。

照合対象：

- Requirement 4 受入 8（LLM commit 実行代行承認の正式 CLI）
- design.md §2.2 commit 実行代行承認
- tasks.md T-004／T-006／T-011
- implementation triad-review R2 裁定と対処
- implementation review-wave no-impact 判定
- 実装差分とテスト結果

## 整合確認

| 観点 | 判定 | 根拠 |
| --- | --- | --- |
| staged 内容承認と実行代行承認の分離 | 整合 | `commit-approval.json` は staged 内容承認のみ保持し、delegation は `.reviewcompass/runtime/approvals/commit-execution-delegation.json` に保存する実装とテストを追加した。 |
| formal CLI | 整合 | `tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json` を追加し、argv に承認文を載せない。 |
| nonce / staged binding | 整合 | delegation record は nonce、target digest、staged file set digest、staged 内容承認 digest、challenge path、approval record path、expiry、instruction hash へ束縛される。 |
| fail-closed | 整合 | malformed stdin、CR/CRLF、target digest 改ざん、unknown field、identity field、redaction failure、embedded delegation bypass、malformed existing delegation を遮断するテストを追加した。 |
| LLM / provider / model 非依存 | 整合 | delegation validation は actor と record 内容で判定し、LLM/provider/model 系 field を禁止する。 |
| `--execution-actor human` exemption | 整合 | 人間実行では execution delegation 不要、LLM 実行では nonce-based separate delegation 必須。 |
| invalidate / consume | 整合 | invalidate は challenge / staged approval / delegation を一括 invalidated にし、guarded commit 成功後は approval / challenge / delegation を consumed にする。 |
| review-wave | 整合 | implementation review-wave は他機能 implementation への波及なしと判定した。 |

## triad-review R2 対処との整合

- C1：malformed existing delegation は既存実装で既に fail-closed。回帰テストを追加して固定した。
- C2：unknown field / identity field の negative tests を追加した。
- C3：redaction failure の negative test を追加した。
- C4：保存直前の fresh canonical target から `target_digest` と `staged_file_set_digest` を再設定するよう修正した。
- C5：nonce 承認では embedded `execution_delegation` があっても別 record なしなら遮断するテストを追加した。
- C6〜C8：argparse required flag、LF/byte limit、runtime ignore は現状維持で整合している。

## 検証

通過済み：

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests -v`
- `.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit -v`
- `PYTHONPYCACHEPREFIX=/tmp/reviewcompass-pycache python3 -m py_compile tools/check-workflow-action.py tools/check_workflow_action/commit_approval.py tools/guarded-git-commit.py`
- `git diff --check`

## 判定

**decision：existing_sufficient**。

実装は Requirement 4 受入 8、design.md §2.2、tasks.md T-004／T-006／T-011、implementation triad-review R2 の対処結果、implementation review-wave no-impact 判定と整合している。次段の implementation approval へ進める。
