# Claude 前提記述の棚卸し

作成日：2026-06-03

位置付け：Codex adapter migration の maintenance 作業メモ。`stages/in-progress/maintenance-2026-06-03-codex-adapter-migration.yaml` の `required_action: inspect_remaining_claude_assumptions` に対応する。

## 1. 目的

ReviewCompass は当初 Claude Code を主な作業環境として開発されたため、repo 内には Claude Code、Claude memory、Agent ツール、`.claude/` hook、`CLAUDE.md` 前提の記述が残っている。

Codex で安全に稼働させるため、これらを一律に削除せず、次の 3 分類に分ける。

1. 即時修正対象：Codex 起動・作業に直接影響する運用導線。
2. 正式手続き送り：`docs/disciplines/` など、workflow-management 所有で改廃手続きが必要なもの。
3. 残すもの：Claude adapter、履歴、モデル識別子、Anthropic API 設定など。

## 2. 既に処理済みの入口導線

処理済み：

- `AGENTS.md` を追加し、Codex の入口規律を repo 内に置いた。
- `docs/operations/WORKFLOW_NAVIGATION.md` を追加し、`next_action` の共通読み方を Claude / Codex から分離した。
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` を追加し、Codex 固有の sandbox、approval、memory 非前提、commit 方針を記述した。
- `TODO_NEXT_SESSION.md` と `templates/todo/TODO_NEXT_SESSION.template.md` を、共通手引き + Codex / Claude adapter 参照へ変更した。
- `next` に `maintenance_in_progress` を追加し、通常ワークフロー外の保守作業が通常 stage に吸い寄せられないようにした。
- `docs/operations/SESSION_WORKFLOW_GUIDE.md` の作業環境説明を adapter 方針へ寄せた。
- `docs/operations/WORKFLOW_PRECHECK.md` の段階 3 hook 説明を Claude Code 固定から実行環境別 hook adapter へ汎用化した。
- `.codex/hooks.json`、`.codex/hooks/README.md`、`.codex/hooks/pre-bash-precheck.sh` を repo 管理対象にし、Codex hook のテストを追加した。
- `tests/hooks/test_pre_bash_precheck.py` は Codex hook 実体を対象に移行済み。

## 3. 即時修正候補

### 3.1 `docs/operations/SESSION_WORKFLOW_GUIDE.md`（処理済み）

残存箇所：

- `Agent ツール` の `model` パラメータで `"sonnet"` / `"haiku"` を指定する記述。
- レビュー記録 front-matter 例の `claude_code_main_session` / `claude_code_subagent`。
- commit message の `Co-Authored-By: Claude Opus ...`。
- 用語ガイドの「メインセッション = Claude Code の主 session」「サブエージェント = Agent ツール経由」。

判定：処理済み。ただし、実験・履歴としての Claude モデル名は残す。

### 3.2 `docs/operations/WORKFLOW_PRECHECK.md`（処理済み）

残存箇所：

- 段階 3 を `Claude Code フック機構` として説明。
- `.claude/hooks/pre-tool-use.sh` などのパス例。
- `CLAUDE.md または規律ファイル` への段階 1 規律化記述。

判定：処理済み。段階 3 は特定環境の hook adapter として説明し直した。

`CLAUDE.md` が存在する場合、それ自体は Codex 入口ではないが、Claude Code adapter の入口規律として扱う。Codex 向け入口は `AGENTS.md` であり、運用文書では `CLAUDE.md` 固定ではなく「各 adapter の入口規律ファイル」として説明する。

### 3.3 tests の説明コメント（処理済み）

残存箇所：

- `tests/tools/test_check_workflow_action.py` の `CLAUDE.md 全体規律`。
- `tests/hooks/test_pre_bash_precheck.py` の `.claude/hooks/pre-bash-precheck.sh` と `CLAUDE.md 全体規律`。

判定：処理済み。コメントだけを Codex 向けに先行修正せず、Codex hook の実体を repo 管理対象にしたうえで、テスト対象を `.codex/hooks/pre-bash-precheck.sh` へ移した。

Claude hook の互換テストが必要になった場合は、Codex hook テストとは別テストとして追加する。

## 4. 正式手続き送り

`docs/disciplines/` 配下は workflow-management 機能の所有物であり、改廃は所定手続きで扱う。

候補：

- `discipline_workflow_precheck_invocation.md`
  - `.claude/hooks/pre-bash-precheck.sh` を段階 3 hook として記述している。
  - Codex hook と Claude hook を adapter として扱う記述へ更新候補。
- `discipline_avoid_compound_bash.md`
  - Why が Claude Code permission 機構に依存している。
  - Codex でも sandbox / approval 負担の観点で趣旨は有効だが、理由付けは汎用化候補。
- `discipline_workflow_state_truth_source.md`
  - 読む側の規律が `workflow_state` の直接 Read 中心。
  - すでに `next` が状態判定の入口になっているため、読む側は navigator-first へ畳み込み候補。
- `discipline_pre_action_precheck.md`
  - workflow_state 直接照合の前提が残る。
  - 横断操作前チェックの一部を `next` / maintenance / post-write 状態へ寄せる候補。

判定：今すぐ編集しない。maintenance 中は候補一覧として保持し、workflow-management 正式手続きで扱う。

## 5. 残すもの

次は削除・置換しない。

- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
  - Claude Code adapter として残す。
- `CLAUDE.md`（存在する場合）
  - Claude Code adapter の入口規律として扱う。Codex 用の入口規律は `AGENTS.md` で分離済み。現時点の git 追跡対象には `CLAUDE.md` は存在しない。
- `.claude/hooks/` と `.claude/settings.json`
  - Claude Code adapter 資産として残す。Codex hook は `.codex/` 側で分離済み。
- `config/api-settings.yaml` の `claude-code-cli`、`claude-opus-*`、`claude-sonnet-*`
  - Claude CLI / Anthropic API の review model 設定であり、Codex 作業者前提ではない。
- `tools/api_providers/tests/` の `claude-*` モデル名
  - Anthropic provider のテスト値として残す。
- `docs/operations/FOUNDATION.md` / `RUNTIME.md` の `subagent_mediated` 説明
  - foundation 正本語彙や過去採用経緯として残す。ただし将来、adapter 表現へ補足する余地はある。
- `tools/session-log-converter.py`
  - Claude Code jsonl 専用 converter として残す。Codex 用 converter が必要なら別ツールを追加する。
- `tools/experiments/`、`docs/sessions/`、`docs/reviews/` 内の Claude 記述
  - 実験記録・過去ログ・モデル識別子として残す。

## 6. repo 外 memory

Claude memory は repo 外のため、Codex では自動ロード前提にしない。

既知の問題：

- Claude memory 側の `MEMORY.md` には「シンボリックリンクをたどって規律本体が auto load される」とする古い記述があり、repo 側 `docs/disciplines/README.md` の「本体は load されないことが判明」と矛盾する。

判定：repo 外なので、この maintenance 作業では勝手に変更しない。修正する場合は、記録内容と場所を提示し、利用者の明示承認を得てから実行する。

## 7. 次の推奨作業

1. 規律本体の改訂候補を workflow-management の正式手続きへ送る。
2. repo 外 Claude memory の修正要否を利用者判断に上げる。
3. 必要なら Claude hook 互換テストを Codex hook テストとは別に追加する。

## 8. maintenance 完了条件との対応

- Codex 新規セッションで TODO から共通手引きと Codex adapter を読んで開始できる：入口文書と TODO / template は整備済み。
- Claude 固有記述が adapter 内または履歴として分類済み：本メモで分類済み。
- 通常ワークフロー外の保守作業が `next` で `maintenance_in_progress` として見える：実装済み。
- 保守作業中でも post-write-verification が隠れない：テスト済み。
- Codex 稼働対応の未解決項目が一覧化されている：本メモ §7 に一覧化。
