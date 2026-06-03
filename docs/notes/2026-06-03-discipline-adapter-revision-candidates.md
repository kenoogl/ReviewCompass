# 規律本体の adapter 化改訂候補

作成日：2026-06-03

位置付け：Codex adapter migration の maintenance 作業メモ。`docs/disciplines/` 配下の規律本体を直接改訂せず、workflow-management 機能の所定手続きに送るための候補一覧である。

## 1. 手続き上の扱い

`docs/disciplines/` は workflow-management 機能の所有物であり、改廃は `docs/disciplines/README.md` §配置と所有に従い、drafting → review → approval の所定手続きで実施する。

現時点の `.reviewcompass/specs/workflow-management/spec.json` では、workflow-management の implementation は全段未着手である。したがって本メモは、通常ワークフロー再開後の workflow-management implementation drafting で参照する改訂入力として扱う。

## 2. 改訂候補の分類

| 規律 | 現在の残存前提 | 改訂方向 | 優先度 |
|---|---|---|---|
| `discipline_workflow_precheck_invocation.md` | 段階 3 hook を `.claude/hooks/pre-bash-precheck.sh` 固定で説明 | Claude / Codex の hook adapter を並列表現にし、段階 1 と段階 3 の責務分担を環境非依存にする | 高 |
| `discipline_avoid_compound_bash.md` | Why が Claude Code permission 機構に依存 | Claude Code の permission に加え、Codex の sandbox / approval と許可粒度にも当てはまる理由へ一般化する | 中 |
| `discipline_workflow_state_truth_source.md` | 読む側の規律が `workflow_state` の直接 Read 中心 | 読む側は `tools/check-workflow-action.py next --json` を入口にし、書く側の要約値禁止・根拠併記は残す | 高 |
| `discipline_pre_action_precheck.md` | `workflow_state` 直接照合と応答内宣言が中心 | 横断操作前の確認に `next` / `maintenance_in_progress` / `post_write_verification` の状態確認を組み込む。網羅 grep と scope 独立検証は残す | 中 |

## 3. 各候補の具体案

### 3.1 `discipline_workflow_precheck_invocation.md`

事実：

- 現本文は段階 3 フックとして `.claude/hooks/pre-bash-precheck.sh` を名指ししている。
- Codex adapter migration では `.codex/hooks.json` と `.codex/hooks/pre-bash-precheck.sh` を repo 管理対象にし、テスト対象も Codex hook に移した。
- `docs/operations/WORKFLOW_PRECHECK.md` は 2026-06-03 時点で「実行環境別 hook adapter」表現へ更新済み。

改訂案：

- 「段階 3 フック（`.claude/hooks/...`）」を「実行環境別 hook adapter」に置き換える。
- Claude Code の例として `.claude/hooks/pre-bash-precheck.sh`、Codex の例として `.codex/hooks/pre-bash-precheck.sh` を併記する。
- 段階 1 は引き続き不可逆操作直前の意図的 precheck を担う、と明記する。
- `next --json` は作業提案前、`spec-set` / `commit` / `push` は不可逆操作直前、という使い分けを補足する。

### 3.2 `discipline_avoid_compound_bash.md`

事実：

- 現本文の Why は Claude Code の permission 機構を主根拠にしている。
- Codex でも shell command は sandbox / approval / prefix rule の単位で扱われ、複合コマンドは確認・承認・ログ解釈を難しくする。
- AGENTS.md では、検索や読み取りにおいて `rg` と並列 tool call を優先する運用が既にある。

改訂案：

- Why を「Claude Code の permission」単独から「各 agent runtime の権限判定・sandbox・承認粒度」に一般化する。
- Claude Code は過去の制定出典として残す。
- Codex では `multi_tool_use.parallel` による独立コマンド並列を推奨する、という adapter 依存の補足を入れるか、Codex adapter 文書への参照に留める。

### 3.3 `discipline_workflow_state_truth_source.md`

事実：

- 現本文は「状態判定時は必ず workflow_state を実際に Read で読む」としている。
- 現在は `tools/check-workflow-action.py next --json` が `spec.json`、`stages/in-progress/`、post-write-verification manifest、reopen / maintenance 状態をまとめて判定する。
- `workflow_state` だけでは、post-write-verification pending や maintenance_in_progress は判定できない。

改訂案：

- 読む側の規律は「まず `next --json` を実行し、`next_action.kind` を正本として扱う」に置換する。
- `workflow_state` は `next` が参照する主要な真実源の一つとして位置付ける。
- 書く側の規律（要約値を spec.json に書かない、状態表現に根拠を併記する）は維持する。
- `next` が `unknown`、または判定不能を返す場合は、直接 Read と利用者確認に戻す。

### 3.4 `discipline_pre_action_precheck.md`

事実：

- 現本文は集約・横断操作前に 5 項目チェックリスト、grep、3 分類、scope 独立検証を求めている。
- 5 項目のうち「workflow_state と整合しているか」は、現在のナビゲータでは `next` の状態確認でより広く扱える。
- 波及調査の網羅 grep は、ナビゲータでは代替できない。

改訂案：

- 事前検査の冒頭に `next --json` を追加し、`post_write_verification`、`post_write_policy_violation`、`maintenance_in_progress`、`reopen_in_progress` の場合は通常の集約作業に進まないと明記する。
- `workflow_state` 直接照合の項目は「`next_action` と整合しているか」に置換する。
- 承認出典、確定／未確定の区別、過去確定との矛盾、最新発言との整合、網羅 grep、3 分類、scope 独立検証は残す。

## 4. 正式手続きに送るときの注意

- 本メモは改訂候補であり、規律本文の変更ではない。
- `docs/disciplines/` を編集する段階では、workflow-management の所定手続き、利用者明示承認、post-write-verification が必要である。
- 規律本文の改訂時は、Claude adapter と Codex adapter の両方を残す。Claude 固有記述を履歴・adapter 資産として残すべき箇所と、現在の作業者を Claude Code に固定してしまう箇所を分ける。
- `next` に畳み込む手続き部分と、LLM / 利用者の判断として残す部分を分ける。

## 5. 推奨順序

1. `discipline_workflow_state_truth_source.md`：`next` 導入効果が最も大きく、現在地誤認を直接防ぐ。
2. `discipline_workflow_precheck_invocation.md`：Codex hook adapter が repo 管理対象になったため、段階 3 の表現更新が必要。
3. `discipline_pre_action_precheck.md`：横断作業の入口に `next` を組み込み、post-write / maintenance / reopen を見落とさないようにする。
4. `discipline_avoid_compound_bash.md`：理由付けの一般化。運用上は重要だが、他 3 件より緊急度は低い。
