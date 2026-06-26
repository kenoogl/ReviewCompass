# Codex セッション採取：全件取り込みへの対応メモ

作成：2026-06-26

## 背景

Claude 側では以下2点を修正した（コミット `bae0e71f`・`e3a1b829`）。

1. セッション記録をスナップショットとしてコミット可能にした（進行中セッションのブロックを廃止）
2. SessionStart フックを「最新1件のみ」から「未記録の全件」に変更した

Codex 側は `active-sessions.json` ゲートを元から使っていないため 1 の影響はない。
しかし 2 に対応する変更がまだ行われていない。

## 対応が必要な箇所

- `.codex/hooks/session-record-capture-previous-codex.sh`
  - `--max-count 1` を外し、未記録セッションを全件取り込むよう変更する
- `tools/session-record-capture-previous-codex.py`
  - `--max-count` の既定値が 5 になっているが、上限なし（全件）に変更するか、
    フック側で大きな値を渡すかを検討する

## 参照

- Claude 側の実装：`.claude/hooks/session-record-capture-previous.sh`（全件ループの参考）
- テスト：`tests/hooks/test_session_record_capture_previous.py`（全件取り込みのテスト例）
