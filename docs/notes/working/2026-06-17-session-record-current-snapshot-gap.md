# session record current snapshot gap

作成日: 2026-06-17

## 背景

利用者が「このセッションの会話ログを今すぐ記録したい」と指示した際、Codex は
`.reviewcompass/runtime/session-record-drafts/` に現セッション下書きを保存した。

しかし利用者が期待していた過去例は、次の 2 層の正式記録だった。

- `.reviewcompass/evidence/sessions/<date>-codex-<session-id>.md`
- `docs/sessions/auto-<date>-codex-<session-id>.md`

このため、「記録した」という応答が、下書き保存なのか正式な 2 層記録なのかを曖昧にした。

## 現状の整理

現在の Codex セッション記録運用は、次の使い分けになっている。

- 進行中セッション: `.reviewcompass/runtime/session-record-drafts/codex-<session-id>.md`
- 終了済みセッションの正式記録:
  - `.reviewcompass/evidence/sessions/<date>-codex-<session-id>.md`
  - `docs/sessions/auto-<date>-codex-<session-id>.md`
- 正式化: 次の `SessionStart` で前セッション下書きを昇格、または終了済み rollout を明示して backfill

この設計は、進行中 rollout が伸び続けて `source_sha256` が変わることを避けるため、現セッションを
正式 2 層記録へ直接昇格しない。

## 問題

利用者の「今すぐ記録」は、少なくとも次の 2 通りに読める。

- 安全な下書き保存
- `docs/sessions/auto-...` を含む正式記録の即時作成

現行手順では、この区別を利用者に明示する標準文言や command がない。

## 改善候補

1. 「現セッション下書き保存」と「終了済みセッション正式記録」を明示的に別コマンドまたは別手順として案内する。
2. 進行中セッションのスナップショットを正式に扱うなら、`status: in_progress_snapshot` などの来歴を front matter に持たせる。
3. スナップショットを許す場合は、同じ session id の後続更新時に追記更新できる merge / provenance ルールを定義する。
4. `TODO_NEXT_SESSION.md` や `SESSION_WORKFLOW_GUIDE.md` の会話ログ取り込み節で、下書きと正式記録の違いを短く固定する。

## 未実装

このメモは問題整理であり、手順・CLI・hook・仕様の変更はまだ行っていない。
