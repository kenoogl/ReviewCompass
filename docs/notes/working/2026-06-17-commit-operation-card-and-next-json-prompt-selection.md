# commit 操作カードと next prompt selection 改修メモ

作成日: 2026-06-17

## 背景

commit 時の規律が複数箇所に分散している。

- `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`

それぞれ役割はあるが、commit 直前に LLM が読むべき短い操作手順が一意ではない。そのため、`commit-approval prepare` と `commit --json` precheck の並列実行、challenge 作成後の余計な承認系コマンド、`--approval-source-text-line-stdin` の空 stdin 実行といった操作事故が起きやすい。

## 問題

現状の整理では、正本・詳細仕様・実行面 adapter が混ざっている。

- 正本は厳密であるべきだが、commit 直前に読むには長い。
- adapter は Codex / Claude の違いを書く場所だが、commit 手順本体まで重複しやすい。
- `next --json` は通常作業の `effective_prompt` を返すが、commit のような不可逆操作直前の操作 prompt は別系統になっている。

## 方針案

commit 直前に必ず読む短い一枚を作る。

候補:

- `docs/operations/COMMIT_OPERATION_CARD.md`

この文書は commit 操作だけを扱う。仕様説明ではなく、LLM が実行直前に迷わないための操作カードとする。

記載する内容:

1. `git add` 後に staged 状態を確認する。
2. `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を単独で実行する。
3. `prepare` と `commit --json` precheck を並列実行しない。
4. 返された nonce で guarded commit を起動する。
5. challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まない。
6. `--approval-source-text-line-stdin` は stdin を渡せる実行形でだけ使う。
7. 空 stdin は単なる入力ミスではなく challenge invalidation を起こし得る。
8. guarded commit が承認入力待ちになってから承認 1 行を渡す。
9. 失敗時は、まず承認入力経路と challenge 状態を確認する。

## Codex / Claude の分離

commit 手順本体は `COMMIT_OPERATION_CARD.md` に寄せる。

Codex 固有の adapter には、次だけを残す。

- PTY で guarded commit を起動する必要がある場合の注意。
- `write_stdin` で `コミット\n` を渡すこと。
- sandbox escalation が必要な場合の扱い。
- 非対話・空 stdin にしないこと。

Claude 固有の adapter には、Claude Code 側の実行面に合わせた注意だけを残す。

両 adapter は commit 手順本体を重複して書かず、`COMMIT_OPERATION_CARD.md` を参照する。

## next --json 改修との関係

通常の次作業 selection と、不可逆操作直前 selection を分ける。

現状:

- `next --json` は `next_action.kind` に応じた `effective_prompt` を返す。
- commit は利用者発話を契機に実行されるため、通常の `next_action.kind` とは別経路になっている。

改修案:

- `check-workflow-action.py` に不可逆操作用の prompt selection を追加する。
- 例: `commit-operation --json` または `operation-prompt commit --json`
- 出力には、共通操作カードと実行面 adapter を含める。

想定出力:

```json
{
  "operation": "commit",
  "required_operation_card": "docs/operations/COMMIT_OPERATION_CARD.md",
  "adapter_card": "docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md#commit",
  "effective_prompt_path": ".reviewcompass/runtime/effective-prompts/operation-commit.prompt.md"
}
```

## 読み込み規律の最適化

通常作業:

- `next --json` の `effective_prompt_path` だけを読む。

commit 直前:

- `COMMIT_OPERATION_CARD.md` を読む。
- 実行面 adapter の commit 節だけを読む。
- 詳細確認が必要な場合だけ `WORKFLOW_PRECHECK.md` / `WORKFLOW_PRECHECK_DETAILS.md` へ降りる。

これにより、正本の厳密さと、実行直前の短さを両立する。

## 実装候補

1. `docs/operations/COMMIT_OPERATION_CARD.md` を追加する。
2. Codex / Claude adapter の commit 節を、操作カード参照中心に整理する。
3. `WORKFLOW_DISCIPLINE_MAP.yaml` に不可逆操作用 decision point を追加する。
4. `check-workflow-action.py` に operation prompt 出力を追加する。
5. tests で `commit` 操作 prompt が共通カードと adapter を含むことを固定する。

## 今回は実施しないこと

- `COMMIT_OPERATION_CARD.md` の正本追加
- `next --json` / `check-workflow-action.py` の実装修正
- Codex / Claude adapter の整理
- post-write verification

この文書は、次作業候補を整理するための作業中メモであり、仕様正本ではない。
