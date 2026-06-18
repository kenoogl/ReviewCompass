# commit 指示時 preflight 不足の改善メモ

作成日: 2026-06-19

## 対象

利用者が「コミット」と指示した後、stage、commit approval、commit execution delegation、guarded commit まで進んだが、最終的に `stages/in-progress/` の存在により commit guard が `DEVIATION` で停止した件を記録する。

このメモは後日の改善検討用である。workflow state や commit 対象の staged 内容は変更しない。

## 起きたこと

利用者の「コミット」指示後、以下の処理を進めた。

1. staged 対象を作成した。
2. staged diff check を確認した。
3. guarded commit を実行した。
4. 古い commit approval record により一度停止した。
5. 現在の staged 内容に対する commit approval challenge を作成した。
6. commit approval と commit execution delegation を記録した。
7. guarded commit を再実行した。
8. `stages/in-progress/reopen-procedure-2026-06-19.yaml` が残っているため `DEVIATION` で停止した。

最終的に commit は作成されなかった。

## 問題点

### 1. commit 可否を最初に判定していない

`stages/in-progress/` が存在する場合、guarded commit が通るかどうかは stage や approval 作成より前に判定できる。

今回の状態では、`next --json` は `reopen_in_progress` を返しており、active gate は `stages/requirements.yaml#review-wave` だった。これは通常の commit stop point ではなく、reopen 第3過程の途中である。

この状態で commit operation に入るべきではなかった。

### 2. 不可と分かる前に副次的な状態を作った

commit が通らない可能性を先に判定せず、以下を作成した。

- staged index
- commit approval challenge
- commit approval record
- commit execution delegation record

これにより、利用者から見ると「多くの処理を行った後で、結局できない」という悪い体験になった。

### 3. guard が最後の防壁に寄りすぎている

guarded commit は最終防壁として正しく停止した。一方で、利用者指示を受けた直後の operation 開始可否判定が不足していた。

本来は、最終 guard まで行かずに、commit operation の入口で停止すべきだった。

## 改善方針

### A. commit instruction preflight を追加する

利用者が「コミット」と指示した直後、stage や approval nonce 作成より前に read-only preflight を実行する。

最低限の判定:

- `next --json` が commit 可能な状態か。
- `stages/in-progress/` がある場合、それが構造化された commit stop point か。
- `reopen_in_progress` / `maintenance_in_progress` / `post_write_verification` など、commit より優先すべき active unit が残っていないか。
- staged / unstaged の状態に入る前に commit operation を開始してよいか。

判定結果が `DEVIATION` の場合は、stage、approval challenge、approval record、delegation record を作らず停止する。

### B. commit 指示時の標準分岐を機械化する

理想の分岐:

```text
利用者: コミット
  -> commit instruction preflight
    -> OK: stage / approval / guarded commit へ進む
    -> WARN: 利用者に短く理由を提示し、必要なら承認を得て進む
    -> DEVIATION: 何も作らず停止し、理由と次 action だけ返す
```

今回であれば、次のように停止すべきだった。

```text
今は reopen in-progress が残っており、commit stop point ではありません。
guarded commit は通らないため、stage / approval 作成には進みません。
次の許可 action は requirements review-wave です。
```

### C. operation-preflight へ接続する

この処理は、既存の統合設計が目指している operation contract / operation preflight の対象に入れる。

`commit` operation の preflight は、以下を入力にする。

- `next --json`
- `stages/in-progress/`
- `spec.json`
- staged / unstaged 状態
- 既存 commit approval challenge / approval / delegation record

出力は、少なくとも以下を持つ。

- `verdict`: `OK` / `WARN` / `DEVIATION`
- `reason`
- `allowed_to_stage`
- `allowed_to_prepare_approval`
- `allowed_to_delegate_execution`
- `allowed_to_run_guarded_commit`
- `next_required_action`

### D. 古い approval record の扱いを入口で検出する

今回、古い consumed / expired approval record も guard で検出された。

これも commit instruction preflight で先に表示する。

ただし、古い approval record があること自体は、新しい staged 内容に対する approval を作り直せば解消できる。一方、`stages/in-progress/` が commit stop point でないことは、approval を作り直しても解消しない。

そのため、preflight の優先順位は次のようにする。

1. active workflow unit が commit を許すか。
2. commit stop point か。
3. post-write verification pending がないか。
4. staged 対象の作成可否。
5. approval record の fresh / stale / consumed / expired 状態。

## 未決事項

- `tools/check-workflow-action.py commit` を read-only preflight として先に使えるようにするか。
- 新しい `operation-preflight commit --json` を正規入口にするか。
- `guarded-git-commit.py` 側に、stage / approval 前の quick preflight mode を追加するか。
- Codex / Claude の「コミット」発話フックで、この preflight を必須化するか。
- reopen 第3過程の途中 commit を許す例外が必要か。必要な場合は、`commit_stop_point` として明示的に記録するべきであり、単なる `stages/in-progress` 同居を許すべきではない。

## 現時点の推奨

次に commit 周りを改善するときは、まず「commit 指示直後の read-only preflight」を実装する。

この preflight が `DEVIATION` を返した場合、LLM は stage、approval challenge、approval record、delegation record、guarded commit のいずれにも進まない。

利用者へは、詳細な guard ログではなく、次の3点だけを返す。

- commit できない理由
- 何も作らず止めたこと
- 次に許可されている workflow action
