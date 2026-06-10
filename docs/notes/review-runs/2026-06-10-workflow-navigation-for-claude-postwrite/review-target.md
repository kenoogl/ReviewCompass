# Post-write verification target: WORKFLOW_NAVIGATION_FOR_CLAUDE.md rewrite

## Target files

- docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md

## Agreed decisions（合意内容、決定事項のみ）

- LLM 固有機能への依存を最小化し、規律・手順の正本はプロジェクト内ファイル（`docs/disciplines/`、`docs/operations/WORKFLOW_NAVIGATION.md`）に置く。
- Claude 対応は、現行の Codex 作業版に合わせて更新する。
- `WORKFLOW_NAVIGATION_FOR_CLAUDE.md` は、共通正本 `docs/operations/WORKFLOW_NAVIGATION.md` に委ね、Claude 固有の差分だけを書く薄い adapter 形式（`WORKFLOW_NAVIGATION_FOR_CODEX.md` と同形式）に書き直す。
- リポジトリ直下に `CLAUDE.md` を新設し、`AGENTS.md` を取り込むだけの入口とする。`CLAUDE.md` に固有の指示を書き足さない。
- ユーザディレクトリ配下の Claude project memory は規律の正本として扱わず、原則書き込まない。恒久記録は repo 側ファイルに、利用者の明示承認を得て書く。
- フック本体 `pre-bash-precheck.sh` は `.claude/hooks/` と `.codex/hooks/` の両複製を同一内容に保ち、同一性を `tests/hooks/test_claude_hook_repository.py` で機械検査する。
- `.claude/settings.json` に環境固有の絶対パスを書かない。環境固有の許可は git 非追跡の `.claude/settings.local.json` に置く。
- commit 代行、side track 宣言、review-run 提示ゲートの運用規則は Codex 版（`WORKFLOW_NAVIGATION_FOR_CODEX.md` 規則 5・6・10・11）と同一とする。

## Review instruction

検証対象は `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` の全面書き直し結果である。次の 4 観点で検査する。

1. agreement_reflection：上記の合意内容が書き込みに反映されているか
2. reference_accuracy：参照ファイル名・ツール名・節番号などの固有名詞が正しいか
3. existing_record_consistency：参照用に添付した `WORKFLOW_NAVIGATION_FOR_CODEX.md`（既存記述）と齟齬がないか（意図的な Claude／Codex の読み替えを除く）
4. internal_logic：内部に論理矛盾がないか

所見は、逐語的指摘（字句・表現レベル）と本質的指摘（合意の解釈・設計判断に触れるもの）を区別して報告する。

## Target file contents

### docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md（検証対象）

````markdown
# Claude 作業用：ReviewCompass ワークフローナビゲータの使い方

この文書は、Claude が ReviewCompass の開発作業を始める前に読むための adapter 手引きである。

共通の `next_action` の読み方は `docs/operations/WORKFLOW_NAVIGATION.md` を正本とする。本書は Claude 環境に固有の制約だけを補う。

## 1. 起点

作業開始前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

その後、`next_action.kind` は `docs/operations/WORKFLOW_NAVIGATION.md` に従って読む。

## 2. Claude 固有の作業規則

1. リポジトリ直下の `CLAUDE.md` は、`AGENTS.md` を取り込むだけの入口として扱う。入口規律の正本は `AGENTS.md` であり、`CLAUDE.md` に固有の指示を書き足さない。
2. ユーザディレクトリ配下の Claude project memory（セッション開始時に自動ロードされる記憶領域）が読み込まれても、その内容を規律の正本として扱わない。必要な規律本文は repo 内 `docs/disciplines/` を読む。
3. Claude project memory への追加・変更・削除は原則行わない。「忘れないため」「再発防止のため」「規律違反を直すため」であっても例外ではない。恒久記録が必要な場合は、repo 内の記録先と内容を利用者へ提示し、明示承認を得てから repo 側ファイルに書く。
4. permission（許可・遮断リスト）と承認モードの制約を守る。外部 API、ネットワーク通信、repo 外書き込み、破壊的操作は、許可が必要な場合に承認を得てから実行する。共有する設定は `.claude/settings.json` に置き、環境固有の許可は git 非追跡の `.claude/settings.local.json` に置く。`settings.json` に環境固有の絶対パスを書かない。
5. commit と push は利用者の運用方針に従う。「次のコミットまで自律実行」は commit 停止点まで進めて止まる指示であり、commit 実行代行は含まない。停止点到達後に利用者が「コミット」と指示した場合は、その 1 回の commit 実行を代行してよい。最初から commit も含めて自律実行する場合は、「コミット代行も含めて自律実行」のように commit 実行代行を含むことを明示する。代行時は `tools/guarded-git-commit.py` を使い、同ラッパーが `tools/check-workflow-action.py commit --execution-actor llm` を直前 precheck として実行する。コミットメッセージは利用者指定があればそれを使い、指定がなければ staged 差分の主目的を 1 行の命令形または名詞句で要約する。
6. 通常の `next_action` と異なる side track に入るときは、作業前に `SIDE TRACK 開始: <名前>`、`本線停止理由`、`復帰条件` を利用者へ明示する。side track から抜けるときは、`SIDE TRACK 終了: <名前>`、`復帰先`、`next` の判定結果を明示する。
7. docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は、`next` を再実行して結果を報告する。`post_write_verification` が返った場合は通常ワークフローへ戻らない。
8. post-write-verification pending 中に、再発防止や反省を目的として規律、TODO、テンプレート、hook、スクリプトを勝手に変更しない。必要なら提案して利用者の承認を待つ。
9. `.claude/settings.json` と `.claude/hooks/` は Claude Code 側の hook 設定である。Codex の `.codex/` 設定とは分けて扱う。フック本体 `pre-bash-precheck.sh` は `.codex/hooks/` の複製と同一内容を保ち、同一性は `tests/hooks/test_claude_hook_repository.py` で機械検査する。
10. `triad-review` の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示する。variant や role 割当が曖昧な場合は開始しない。
11. API review-run 完了後は、`SESSION_WORKFLOW_GUIDE.md#3.3-a-2` の利用者提示ゲートを完了するまで、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行へ進まない。

## 3. post-write-verification の扱い

Claude は `next_action.target_files` 全体を確認する。複数ファイルがある場合でも、ファイルごとの分業を独立多重チェックとして扱わない。

外部 API を使う検証は、利用者の明示承認または既に許可された既存コマンドがある場合だけ実行する。実行できない場合は、検証対象、必要な検証者数、実行しようとした手段、実行できない理由を報告して停止する。

## 4. Codex 固有資産の扱い

Codex 用の手引き（`WORKFLOW_NAVIGATION_FOR_CODEX.md`）と `.codex/` hook は削除しない。Codex で再検証・比較実行するための adapter 資産として残す。`AGENTS.md` は Codex 専用ではなく、`CLAUDE.md` から取り込まれる共通入口の正本である。

Claude 作業時も、triad-review のモデル名としての `gpt-*`／`gemini-*` や、過去セッション記録内の Codex 記述は履歴・モデル識別子として扱う。
````

## Reference contents（検証対象外、整合確認用）

### docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md（参照、既存記述）

````markdown
# Codex 作業用：ReviewCompass ワークフローナビゲータの使い方

この文書は、Codex が ReviewCompass の開発作業を始める前に読むための adapter 手引きである。

共通の `next_action` の読み方は `docs/operations/WORKFLOW_NAVIGATION.md` を正本とする。本書は Codex 環境に固有の制約だけを補う。

## 1. 起点

作業開始前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

その後、`next_action.kind` は `docs/operations/WORKFLOW_NAVIGATION.md` に従って読む。

## 2. Codex 固有の作業規則

1. `AGENTS.md` をプロジェクト内の Codex 向け入口規律として扱う。
2. Claude memory が自動ロードされる前提を置かない。必要な規律本文は repo 内 `docs/disciplines/` を読む。
3. repo 外 memory への書き込みを前提にしない。memory 相当の永続記録が必要な場合は、まず記録先と内容を利用者へ提示し、明示承認を得る。
4. filesystem sandbox と approval の制約を守る。外部 API、ネットワーク通信、repo 外書き込み、破壊的操作は、許可が必要な場合に承認を得てから実行する。
5. commit と push は利用者の運用方針に従う。「次のコミットまで自律実行」は commit 停止点まで進めて止まる指示であり、commit 実行代行は含まない。停止点到達後に利用者が「コミット」と指示した場合は、その 1 回の commit 実行を代行してよい。最初から commit も含めて自律実行する場合は、「コミット代行も含めて自律実行」のように commit 実行代行を含むことを明示する。代行時は `tools/guarded-git-commit.py` を使い、同ラッパーが `tools/check-workflow-action.py commit --execution-actor llm` を直前 precheck として実行する。コミットメッセージは利用者指定があればそれを使い、指定がなければ staged 差分の主目的を 1 行の命令形または名詞句で要約する。
6. 通常の `next_action` と異なる side track に入るときは、作業前に `SIDE TRACK 開始: <名前>`、`本線停止理由`、`復帰条件` を利用者へ明示する。side track から抜けるときは、`SIDE TRACK 終了: <名前>`、`復帰先`、`next` の判定結果を明示する。
7. docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は、`next` を再実行して結果を報告する。`post_write_verification` が返った場合は通常ワークフローへ戻らない。
8. post-write-verification pending 中に、再発防止や反省を目的として規律、TODO、テンプレート、hook、スクリプトを勝手に変更しない。必要なら提案して利用者の承認を待つ。
9. `.codex/hooks.json` と `.codex/hooks/` は Codex 側の hook 設定である。Claude Code の `.claude/` 設定とは分けて扱う。
10. `triad-review` の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示する。variant や role 割当が曖昧な場合は開始しない。
11. API review-run 完了後は、`SESSION_WORKFLOW_GUIDE.md#3.3-a-2` の利用者提示ゲートを完了するまで、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行へ進まない。

## 3. post-write-verification の扱い

Codex は `next_action.target_files` 全体を確認する。複数ファイルがある場合でも、ファイルごとの分業を独立多重チェックとして扱わない。

外部 API を使う検証は、利用者の明示承認または既に許可された既存コマンドがある場合だけ実行する。実行できない場合は、検証対象、必要な検証者数、実行しようとした手段、実行できない理由を報告して停止する。

## 4. Claude 固有資産の扱い

Claude 用の手引き、memory、`.claude/` hook、Claude Code session log converter は削除しない。Claude Code で再検証・比較実行するための adapter 資産として残す。

Codex 作業時に修正すべきなのは、「現在の作業者が必ず Claude Code である」と読める入口記述である。triad-review のモデル名としての `claude-*` や、過去セッション記録内の Claude 記述は履歴・モデル識別子として扱う。
````
