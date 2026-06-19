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
5. commit と push は利用者の運用方針に従う。「次のコミットまで自律実行」は commit 停止点まで進めて止まる指示であり、commit 実行代行は含まない。停止点到達後、利用者の単発 commit 指示（例：`コミット`）は、提示済みまたは直後に stage する対象への staged 内容承認と LLM commit 実行代行承認として扱う。最初から commit も含めて自律実行する場合は、「コミット代行も含めて自律実行」のように commit 実行代行を含むことを明示する。commit 直前は `docs/operations/COMMIT_OPERATION_CARD.md` を読み、共通手順は同カードに従う。Codex では `commit-preflight`、stage、nonce prepare、guarded commit を同一ターンで逐次実行し、`tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を PTY で起動する。承認入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。利用者発話なしに Codex が承認文を生成してはならない。sandbox escalation が必要な場合は、guarded commit の preflight 結果に従って利用者へ確認する。コミットメッセージは利用者指定があればそれを使い、指定がなければ staged 差分の主目的を 1 行の命令形または名詞句で要約する。
6. 通常の `next_action` と異なる side track に入るときは、作業前に `SIDE TRACK 開始: <名前>`、`本線停止理由`、`復帰条件` を利用者へ明示する。side track から抜けるときは、`SIDE TRACK 終了: <名前>`、`復帰先`、`next` の判定結果を明示する。
7. docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は、`next` を再実行して結果を報告する。`post_write_verification` が返った場合は通常ワークフローへ戻らない。
8. post-write-verification pending 中に、再発防止や反省を目的として規律、TODO、テンプレート、hook、スクリプトを勝手に変更しない。必要なら提案して利用者の承認を待つ。
9. `.codex/hooks.json` と `.codex/hooks/` は Codex 側の hook 設定である。Claude Code の `.claude/` 設定とは分けて扱う。
10. `triad-review` の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示する。variant や role 割当が曖昧な場合は開始しない。
11. API review-run 完了後は、`SESSION_WORKFLOW_GUIDE.md#3.3-a-2` の利用者提示ゲートを完了するまで、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行へ進まない。

<a id="3-commit"></a>

## 3. commit

commit 直前は `docs/operations/COMMIT_OPERATION_CARD.md` を読む。Codex では利用者の単発 commit 指示を staged 内容承認と LLM commit 実行代行承認として扱い、`tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を PTY で起動する。承認入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。利用者発話なしに Codex が承認文を生成してはならない。sandbox escalation が必要な場合は、guarded commit の preflight 結果に従って利用者へ確認する。

## 4. post-write-verification の扱い

Codex は `next_action.target_files` 全体を確認する。複数ファイルがある場合でも、ファイルごとの分業を独立多重チェックとして扱わない。

外部 API を使う検証は、利用者の明示承認または既に許可された既存コマンドがある場合だけ実行する。実行できない場合は、検証対象、必要な検証者数、実行しようとした手段、実行できない理由を報告して停止する。

## 5. Claude 固有資産の扱い

Claude 用の手引き、memory、`.claude/` hook、Claude Code session log converter は削除しない。Claude Code で再検証・比較実行するための adapter 資産として残す。

Codex 作業時に修正すべきなのは、「現在の作業者が必ず Claude Code である」と読める入口記述である。triad-review のモデル名としての `claude-*` や、過去セッション記録内の Claude 記述は履歴・モデル識別子として扱う。
