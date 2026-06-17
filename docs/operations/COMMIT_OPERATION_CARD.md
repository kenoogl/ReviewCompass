<a id="commit-operation-card"></a>

# COMMIT_OPERATION_CARD

commit 操作カード

最終更新: 2026-06-17

このカードは commit 直前に読む短い実行手順である。仕様説明ではなく、操作事故を防ぐための実行カードとして扱う。詳細契約は `WORKFLOW_PRECHECK.md` と `WORKFLOW_PRECHECK_DETAILS.md` を参照する。

## 手順

1. `git add` 後、staged 対象を確認する。
2. `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を単独で実行する。
3. `commit-approval prepare` と `commit --json` precheck を並列実行しない。
4. 返された nonce を使い、すぐに `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を起動する。
5. challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まない。
6. `--approval-source-text-line-stdin` は stdin を渡せる実行形でだけ使う。
7. 空 stdin は challenge invalidation を起こし得るため、非対話・空入力で実行しない。
8. guarded commit が承認入力待ちになってから、利用者承認の 1 行を渡す。
9. 失敗時は、まず承認入力経路、challenge 状態、staged digest の一致を確認する。

## Codex

Codex で `--approval-source-text-line-stdin` を使う場合は、PTY で guarded commit を起動し、入力待ちになってから `write_stdin` で承認 1 行を渡す。sandbox により git 書き込みが拒否された場合は、guarded commit の preflight 結果に従い、必要な escalation を利用者へ確認する。

## Claude Code

Claude Code で `--approval-source-text-line-stdin` を使う場合は、stdin を渡せる実行形でのみ使う。空 stdin での実行は challenge invalidation（承認無効化）を起こすため、非対話・空入力で実行しない。

## 禁止

- challenge 作成後に、承認 record や staged index を変える別コマンドを挟む。
- `--approval-source-text-line-stdin` を stdin なしで実行する。
- commit 実行後に結果確認なしで完了扱いにする。
