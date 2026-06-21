# Claude 作業用：ReviewCompass ワークフローナビゲータの使い方

この文書は、Claude が ReviewCompass の開発作業を始める前に読むための adapter 手引きである。

共通の `next_action` の読み方は `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` を正本とする。本書は Claude 環境に固有の制約だけを補う。

## 1. 起点

作業開始前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

その後、`next_action.kind` は `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` に従って読む。

## 2. Claude 固有の作業規則

1. リポジトリ直下の `CLAUDE.md` は、`AGENTS.md` を取り込むだけの入口として扱う。入口規律の正本は `AGENTS.md` であり、`CLAUDE.md` に固有の指示を書き足さない。
2. ユーザディレクトリ配下の Claude project memory（セッション開始時に自動ロードされる記憶領域）が読み込まれても、その内容を規律の正本として扱わない。必要な規律本文は repo 内 `.reviewcompass/guidance/` を読む。
3. Claude project memory への追加・変更・削除は原則行わない。「忘れないため」「再発防止のため」「規律違反を直すため」であっても例外ではない。恒久記録が必要な場合は、repo 内の記録先と内容を利用者へ提示し、明示承認を得てから repo 側ファイルに書く。
4. permission 設定（`.claude/settings.json`・`.claude/settings.local.json` の allow／deny）と Claude Code の承認モードの制約を守る。外部 API、ネットワーク通信、repo 外書き込み、破壊的操作は、許可が必要な場合に承認を得てから実行する。共有する設定は `.claude/settings.json` に置き、環境固有の許可は git 非追跡の `.claude/settings.local.json` に置く。`settings.json` に環境固有の絶対パスを書かない。
5. commit と push は利用者の運用方針に従う。「次のコミットまで自律実行」は commit 停止点まで進めて止まる指示であり、commit 実行代行は含まない。停止点到達後に利用者が「コミット」と指示した場合は、その利用者の単発 commit 指示を staged 内容承認と LLM commit 実行代行承認として扱い、同一ターンで commit 実行を代行してよい。最初から commit も含めて自律実行する場合は、「コミット代行も含めて自律実行」のように commit 実行代行を含むことを明示する。commit 直前は `.reviewcompass/guidance/COMMIT_OPERATION_CARD.md` を読み、共通手順は同カードに従う。Claude Code 側で `--approval-source-text-line-stdin` を使う場合も、TTY からの対話入力だけを渡し、利用者発話なしに LLM が承認文を生成してはならない。コミットメッセージは利用者指定があればそれを使い、指定がなければ staged 差分の主目的を 1 行の命令形または名詞句で要約する。
6. 通常の `next_action` と異なる side track に入るときは、作業前に `SIDE TRACK 開始: <名前>`、`本線停止理由`、`復帰条件` を利用者へ明示する。side track から抜けるときは、`SIDE TRACK 終了: <名前>`、`復帰先`、`next` の判定結果を明示する。
7. docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は、`next` を再実行して結果を報告する。`post_write_verification` が返った場合は通常ワークフローへ戻らない。
8. post-write-verification pending 中に、再発防止や反省を目的として規律、TODO、テンプレート、hook、スクリプトを勝手に変更しない。必要なら提案して利用者の承認を待つ。
9. `.claude/settings.json` と `.claude/hooks/` は Claude Code 側の hook 設定である。Codex の `.codex/` 設定とは分けて扱う。フック本体 `pre-bash-precheck.sh` は `.claude/hooks/` と `.codex/hooks/` の両複製を同一内容に保ち、同一性は `tests/hooks/test_claude_hook_repository.py` で機械検査する。
10. `triad-review` の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示する。variant や role 割当が曖昧な場合は開始しない。
11. API review-run 完了後は、`SESSION_WORKFLOW_GUIDE.md#3.3-a-2` の利用者提示ゲートを完了するまで、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行へ進まない。

<a id="3-commit"></a>

## 3. commit

commit 直前は `.reviewcompass/guidance/COMMIT_OPERATION_CARD.md` を読む。Claude Code 側で `--approval-source-text-line-stdin` を使う場合も、TTY からの対話入力だけを渡し、利用者発話なしに LLM が承認文を生成してはならない。共通手順は操作カードに寄せ、Claude 固有の実行面だけを本節で扱う。

利用者の指示テキストが許可文言（`コミット`・`承認` など）の場合、直近の利用者発話で明示された commit 指示を承認語として使い、nonce 取得から guarded commit 実行まで同一ターンで完結させる。別途承認語の再入力を求めない。

コミット操作中のテキスト出力は最小化する。ツール実行前後の説明文（「ステージします」「nonce を取得します」等）は省き、完了後に `<コミット番号> コミット完了。` の1行だけを出す。詳細はツール出力に委ねる。

## 4. post-write-verification の扱い

Claude は `next_action.target_files` 全体を確認する。複数ファイルがある場合でも、ファイルごとの分業を独立多重チェックとして扱わない。

外部 API を使う検証は、利用者の明示承認または既に許可された既存コマンドがある場合だけ実行する。実行できない場合は、検証対象、必要な検証者数、実行しようとした手段、実行できない理由を報告して停止する。

## 5. Codex 固有資産の扱い

Codex 用の手引き（`WORKFLOW_NAVIGATION_FOR_CODEX.md`）と `.codex/` hook は削除しない。Codex で再検証・比較実行するための adapter 資産として残す。`AGENTS.md` は Codex 専用ではなく、`CLAUDE.md` から取り込まれる共通入口の正本である。

Claude 作業時も、triad-review のモデル名としての `gpt-*`／`gemini-*` や、過去セッション記録内の Codex 記述は履歴・モデル識別子として扱う。
