# commit approval stdin 入力事故メモ

作成日: 2026-06-17

artifact_class: working_note
verification_policy: self_check

## 背景

guarded commit の実行時に、commit 対象や post-write verification ではなく、承認入力の渡し方を誤ったために `commit-approval` challenge を潰す問題が多発した。

今回の具体例では、`commit-approval prepare` により staged exact index に対応する challenge は作成できていた。しかし、その後 `tools/guarded-git-commit.py --approval-source-text-line-stdin` を非対話で実行し、stdin に承認文を渡さなかったため、`承認文が入力されていません` で失敗した。この失敗により challenge が invalidated になり、再度 `commit-approval prepare` からやり直す必要が生じた。

## 問題の切り分け

これは次の問題ではない。

- commit 対象ファイルの不一致
- post-write verification の不足
- staged exact index の digest 不一致
- API review や外部送信承認の問題
- git sandbox preflight の問題

本質は、LLM 操縦面で `--approval-source-text-line-stdin` を使うときの stdin 入力手順が明文化されておらず、空 stdin 実行が challenge invalidation という破壊的な結果を生む点である。

## 現在の正本の不足

`docs/operations/WORKFLOW_PRECHECK.md` と `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` には、commit では `guarded-git-commit.py` を使うこと、LLM 実行時に execution delegation が必要なこと、承認文を stdin で扱うことは書かれている。

しかし、コミット直前に LLM が実際に読む運用規律としては、次が不足している。

1. `--approval-source-text-line-stdin` を非対話・空 stdin で実行してはいけないこと。
2. Codex の tool 実行では、stdin を渡せる実行形にしてから承認文 `コミット\n` を渡すこと。
3. 空 stdin は単なる入力ミスではなく、challenge を invalidated にし得ること。
4. challenge 作成後の guarded commit は、承認文入力までを 1 つの不可分な手順として扱うこと。
5. 失敗時に commit 対象や post-write verification を疑う前に、まず承認入力経路を確認すること。

## 修正候補

短期の運用対策:

1. `--approval-source-text-line-stdin` を使う場合は、必ず stdin 入力を渡せる実行形にする。
2. 非対話で stdin を渡せない実行面では、同オプションを使わない。
3. `承認文が入力されていません` が出た場合は、commit 対象や post-write verification を疑う前に、challenge invalidation と stdin 手順を確認する。
4. コミット直前規律に、承認入力を空 stdin で実行しない手順を追記する。

実装候補:

1. `guarded-git-commit.py` が stdin 入力なしを検出した場合、challenge を invalidated にする前に fail-fast できるか検討する。
2. `--approval-source-text-line-stdin` 指定時の利用例を `WORKFLOW_PRECHECK.md` に短く追加する。
3. commit 直前の effective prompt に、承認入力手順の注意を含める。
4. 空 stdin 事故を再現するテストを追加し、期待挙動を固定する。

## 今回は実施しないこと

- `guarded-git-commit.py` の実装修正
- `WORKFLOW_PRECHECK.md` / `WORKFLOW_PRECHECK_DETAILS.md` の正本改訂
- commit approval schema の変更
- API post-write verification

このメモは、再発防止候補を残すための作業中メモである。利用者指示により、API 検証は行わず、自前の軽量自己精査に留める。
