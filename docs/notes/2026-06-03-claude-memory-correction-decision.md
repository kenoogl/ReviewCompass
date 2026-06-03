# repo 外 Claude memory 修正判断メモ

作成日：2026-06-03

位置付け：Codex adapter migration の maintenance 作業メモ。repo 外 Claude memory を勝手に編集せず、修正要否を利用者判断に上げるための材料である。

## 1. 確認した事実

repo 外 memory：

- `/Users/keno/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/MEMORY.md`

確認した記述：

- `MEMORY.md` 10 行目付近に「セッション起動時の auto memory 機構がシンボリックリンクをたどり、規律本体の完全な内容を auto load する」とある。
- 同じ `MEMORY.md` は、memory 配下の `feedback_*.md` が repo 側 `docs/disciplines/discipline_*.md` を指すシンボリックリンクである、と説明している。

repo 側の正本：

- `docs/disciplines/README.md` 過去履歴には、2026-05-26 セッション 27 前半に「auto memory 機構の起動時 load 対象は MEMORY.md の索引までで、シンボリックリンク経由でも規律本体は load されないことが判明」とある。
- `TODO_NEXT_SESSION.md` も、Codex では Claude memory の自動ロードを前提にせず、規律本文は repo 内 `docs/disciplines/` を正本として必要時に Read する方針に更新済みである。

## 2. 問題

repo 外 `MEMORY.md` は、規律本体が auto load されると読める古い前提を残している。

このままだと、Claude Code で作業を再開したときに、Claude が「規律本文は起動時に読めている」と誤認する可能性がある。これは Codex で解消してきた「LLM の記憶・規律依存を機械判定へ寄せる」方針とずれる。

## 3. 修正方針案

repo 外 memory は ReviewCompass repo の通常 post-write-verification 対象ではない。したがって、修正する場合は利用者の明示承認を得てから実行する。

推奨は、`MEMORY.md` 冒頭の説明を次の方針へ差し替えること：

1. memory 側 `MEMORY.md` は索引である。
2. `feedback_*.md` は repo 側規律への参照であり、起動時に規律本文が完全 auto load されるとは扱わない。
3. 規律本文の正本は repo 内 `docs/disciplines/` である。
4. 作業時は `TODO_NEXT_SESSION.md`、`docs/operations/WORKFLOW_NAVIGATION.md`、各 adapter 文書、必要な規律本文を Read する。
5. Codex では Claude memory を自動ロード前提にしない。

## 4. 具体的な修正文案

利用者が承認する場合、repo 外 `MEMORY.md` の冒頭説明を次の趣旨へ更新する。

```markdown
## 重要：memory は規律索引であり、規律本文の自動ロードを前提にしない

規律ファイルの正本は ReviewCompass リポジトリ内の
`docs/disciplines/discipline_*.md` に置かれている。

memory 配下の `feedback_*.md` は repo 側規律への参照索引である。
セッション起動時の auto memory 機構がシンボリックリンク先の規律本文を
完全に auto load するとは扱わない。

作業開始時は `TODO_NEXT_SESSION.md`、`docs/operations/WORKFLOW_NAVIGATION.md`、
実行環境別 adapter 文書を読み、必要な規律本文は repo 内
`docs/disciplines/` から明示的に Read する。

Codex では Claude memory の自動ロードを前提にしない。
```

## 5. 判断

この maintenance 作業では repo 外 memory を編集しない。

次に必要な利用者判断：

- repo 外 `/Users/keno/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/MEMORY.md` を、上記方針で修正してよいか。

承認された場合のみ、memory への書き込み操作として別途実行する。
