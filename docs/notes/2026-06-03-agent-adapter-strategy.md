# 各社モデル向け作業入口 adapter 方針メモ

作成日：2026-06-03

位置付け：正式な計画書改訂ではなく、Codex 移行時に見つかった Claude 前提記述をどう扱うかの方針メモ。将来、正式方針へ昇格する場合は `workflow-management` 機能の所定手続きで計画書・規律へ反映する。

## 1. 背景

ReviewCompass の開発は当初 Claude Code を主な作業環境として進められた。そのため、手引き、TODO、規律、hook、memory 参照の一部に Claude Code 前提の記述が残っている。

一方、現在は Codex でも作業を進める段階に入っている。将来は Claude、Codex、Gemini など複数社・複数環境のモデルで ReviewCompass を運用できるようにしたい。

そのため、Claude 前提を単純に Codex 前提へ置換するのではなく、共通ロジックと各社向け入口を分離する。

## 2. 基本方針

ReviewCompass のワークフロー正本は共通化する。各社モデル・実行環境ごとの差は adapter として分ける。

共通化するもの：

- `tools/check-workflow-action.py next --json` による現在位置と次作業の判定
- `.reviewcompass/specs/*/spec.json` の `workflow_state`
- `stages/in-progress/` の進行中手続き
- post-write-verification manifest による完了認定
- reopen 手続きと trigger_map
- 規律ファイルの正本本文

adapter として分けるもの：

- 作業開始時に読む手引き
- hook の登録方法と発火条件
- memory の有無、場所、扱い
- permission / sandbox / approval の癖
- 外部 API やネットワーク実行の承認方法
- 自動検出できる逸脱と、行動規律に残る禁止事項

## 3. 文書構造案

既存の `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` を無理に Codex 用へ上書きしない。

将来の構造案：

```text
docs/operations/
  WORKFLOW_NAVIGATION.md
  WORKFLOW_NAVIGATION_FOR_CLAUDE.md
  WORKFLOW_NAVIGATION_FOR_CODEX.md
```

または：

```text
docs/operations/agents/
  common.md
  claude-code.md
  codex.md
```

共通文書には `next_action.kind` の意味、通常ワークフロー、reopen、post-write-verification、manifest、policy violation など、実行環境に依存しない読み方を置く。

各社向け文書には、その環境で実際に守るべき入口手順と制約を書く。

## 4. Claude adapter に閉じ込めるもの

Claude Code 固有の次の内容は、Claude 用 adapter に閉じ込める。

- `/Users/keno/.claude/.../memory/` 配下の memory 操作
- Claude Code の PreToolUse hook
- Claude Code の Agent / Task ツール
- Claude Code の permission allow / deny 設定
- Claude Code セッション jsonl 変換
- `claude-code-cli` を CLI 経路として扱う説明

これらは Claude で再実行・検証する場合には有用なので、履歴や実装を削除するのではなく、Claude 固有の入口として整理する。

## 5. Codex adapter に書くもの

Codex 用 adapter には、Codex 環境で実際に効く制約を書く。

- `AGENTS.md` を起点にする
- `.codex/hooks.json` と `.codex/hooks/` を参照する
- filesystem sandbox と approval の扱い
- network 制限と外部 API 実行時の承認
- git 操作時の Codex 側 directive と利用者承認
- repo 外 memory を前提にしないこと

Codex では Claude memory が自動ロードされる前提を置かない。規律本文は repo 内 `docs/disciplines/` を正本とし、必要な規律を読む。

## 6. 当面の修正対象

優先度が高い移行対象：

1. `TODO_NEXT_SESSION.md` の Claude 手引き参照と MEMORY.md 前提
2. `templates/todo/TODO_NEXT_SESSION.template.md` の同種記述
3. `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` の共通部分と Claude 固有部分の分離
4. `.codex/hooks/README.md` の `.claude/hooks/` 説明の移植漏れ

規律本体の修正候補：

- `discipline_workflow_precheck_invocation.md`
- `discipline_avoid_compound_bash.md`
- `discipline_workflow_state_truth_source.md`
- `discipline_pre_action_precheck.md`
- 必要に応じて `discipline_post_write_verification.md`

規律本体は `docs/disciplines/` 配下であり、改廃は `workflow-management` 機能の所定手続きで扱う。

## 7. 残すべき Claude 記述

すべての Claude 記述を削除しない。

残すべきもの：

- 過去セッション・レビュー・実験記録に含まれる Claude 記述
- triad-review のモデル名としての `claude-*`
- Anthropic API のモデル識別子
- Claude で動かす adapter や検証経路

削除・置換すべきなのは、「現在の作業者が必ず Claude Code である」という運用前提の記述である。

## 8. 正式化の順序

1. 本メモで方針を仮合意する。
2. 共通文書と Codex adapter の最小案を作る。
3. TODO とテンプレートの参照先を、共通文書または現在の adapter 選択へ更新する。
4. Codex 環境で小さく運用し、`next` / post-write-verification / hook の挙動を確認する。
5. 問題がなければ `workflow-management` の正式手続きで、規律本体と計画書への反映を検討する。

## 9. 未決事項

- 共通文書を `docs/operations/WORKFLOW_NAVIGATION.md` とするか、`docs/operations/agents/common.md` とするか。
- Codex adapter をどこまで詳細化するか。
- Claude memory 側の古い索引を更新するか、repo 正本への参照だけに縮退させるか。
- `tools/session-log-converter.py` を Claude 専用のまま残すか、Codex 用 converter を別途用意するか。
- `claude-code-cli` の扱いを将来の汎用 CLI provider 設計へ拡張するか。
