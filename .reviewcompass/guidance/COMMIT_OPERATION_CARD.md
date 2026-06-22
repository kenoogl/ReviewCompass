<a id="commit-operation-card"></a>

# COMMIT_OPERATION_CARD

commit 操作カード

最終更新: 2026-06-20

このカードは commit 直前に読む短い実行手順である。仕様説明ではなく、操作事故を防ぐための実行カードとして扱う。詳細契約は `WORKFLOW_PRECHECK.md` と `WORKFLOW_PRECHECK_DETAILS.md` を参照する。

## 手順

1. 利用者の単発 commit 指示を commit 操作の開始条件として扱う。
2. `git add` 前に `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行する。
3. `DEVIATION` の場合は stage / approval / guarded commit に進まず、停止理由と次に必要な操作だけを報告する。
4. `git add` 後、staged 対象を確認する。
5. `.venv/bin/python3 tools/commit-from-current-staged.py -m "<message>" --rationale "<理由>"` を TTY で起動する。
6. wrapper が承認入力待ちになってから、直近の利用者発話で明示された commit 指示を 1 行として渡す。
7. wrapper は approval 作成前に再度 `commit-preflight` を実行し、現在の staged 内容に束縛した approval / execution delegation を作って guarded commit する。
8. 空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行しない。
9. 失敗時は、承認入力経路、staged 内容、post-write / workflow 停止理由のいずれかを短く確認する。

低レベル nonce 手順は、標準 wrapper が使えない場合の補助手順としてだけ使う。

## Codex

Codex で `--approval-source-text-line-stdin` を使う場合は、PTY で guarded commit を起動し、入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。この 1 行を staged 内容承認と LLM commit 実行代行承認として扱う。利用者発話なしに Codex / Claude / LLM が承認文を生成してはならない。Codex の `workspace-write` sandbox では、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

commit 中に承認内容を作り直す、既存 delegation を使い直す、nonce を更新する、といった内部再準備が必要になっても、それ自体を利用者に報告しない。これは承認済みの対象範囲内で、利用者判断を要しない場合に限る。コミット対象が増えた、staged 内容が変わった、または再承認が必要になった場合は内部再準備として隠さず、追加判断が必要な停止理由だけを短く報告する。利用者へ報告するのは、作業を続けられない異常、追加判断が必要な WARN / DEVIATION、または成功結果だけとする。

## Claude Code

Claude Code で `--approval-source-text-line-stdin` を使う場合は、TTY からの対話入力でのみ使う。直近の利用者発話で明示された commit 指示は staged 内容承認と LLM commit 実行代行承認として扱い、別の承認語の再入力を求めない。空 stdin での実行は challenge invalidation（承認無効化）を起こすため、非対話・空入力で実行しない。

## 禁止

- challenge 作成後に、承認 record や staged index を変える別コマンドを挟む。
- `--approval-source-text-line-stdin` を stdin なし、pipe、heredoc、redirect で実行する。
- LLM が `printf` 等で承認文を生成して commit approval / execution delegation を作る。
- commit 実行後に結果確認なしで完了扱いにする。
