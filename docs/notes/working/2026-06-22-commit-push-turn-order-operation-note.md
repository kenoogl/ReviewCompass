---
date: 2026-06-22
record_type: working-note
status: draft
topic: commit-push-turn-order-operation
related:
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
  - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
  - .reviewcompass/guidance/COMMIT_OPERATION_CARD.md
  - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md
  - docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md
  - docs/notes/working/2026-06-20-commit-operation-failure-cases.md
---

# Commit / Push Turn Order Operation Note

## 1. 背景

これまでの作業で、commit、push、side-track 記録、計画メモ更新、本線実装が会話上で混線し、その修復に多くの時間を使った。

直近の失敗では、未 push commit がある状態で、利用者が本線の post-write prompt 機械化へ進む意図を示していたにもかかわらず、先に push すべき停止点を保持できず、実装調査へ進みかけた。

この問題は、git 状態や `next --json` を確認していなかったことだけが原因ではない。確認結果を、次の利用者操作に対応する停止点として扱い切れなかったことが原因である。

## 2. 失敗原因

主な原因は次の通り。

- 直前の完了報告に書いた `次に必要な操作` を、次ターンの最優先入力として扱わなかった。
- `main ahead 1` という状態を見ても、それを「push 承認待ち」として固定できなかった。
- side-track / 本線の境界が曖昧なまま作業が続き、何が完了し何が未完かの説明が揺れた。
- commit guard の nonce / approval record 手順を一度取り違え、古い consumed approval に引っかかった。
- 「計画メモへ反映する作業」と「実装を開始する作業」を同じ流れで扱いかけた。
- コンテキスト圧縮後、機械状態の再確認はしても、直前の停止点を会話上で復元する手順が弱かった。

## 3. ポリシーとの衝突を避けるための整理

単純に「`ahead` があれば push を最優先する」というルールにはしない。

理由:

- push は不可逆操作であり、利用者の明示承認が必須である。
- `git status` は補助状態であり、作業順序の正本は `next --json` である。
- `next_action` と異なる作業へ進む場合は、maintenance / side-track の手続きが必要になる。
- commit 後に push するかどうかは利用者の運用判断であり、自動次段として扱わない。

したがって、対策は「push を自動優先する」ことではない。不可逆操作の承認待ちを、会話上の明示的な停止点として扱うことである。

## 4. 運用ルール

### 4.1 ターン冒頭の復元

各ターンの冒頭では、必要に応じて次を確認する。

- `git status --short --branch`
- `tools/check-workflow-action.py next --json`
- 直前の完了報告に書いた `次に必要な操作`

ただし、これらの関係は次のように読む。

- `next --json` は workflow 上の作業順序の正本である。
- `git status` は clean / dirty / ahead を確認する補助状態である。
- 直前の `次に必要な操作` は、利用者が短く返信した場合にどの不可逆操作または判断を実行するかの会話上の停止点である。

### 4.2 不可逆操作語が来たターン

利用者が `コミット`、`プッシュ`、`承認`、`判断` など、直前の停止点に対応する操作語を返した場合、そのターンでは原則としてその操作だけを実行する。

例:

- `次に必要な操作: プッシュ` の後に `プッシュ` が来た場合、push precheck と push だけを行う。
- push 完了後、状態確認と次の停止点報告を行う。
- push と同じターンで本線実装へ進まない。
- `次に必要な操作: コミット` の後に `コミット` が来た場合、commit 操作だけを正規手順で行う。
- commit 完了後に `ahead 1` なら、push 待ちとして報告する。自律的に push しない。

### 4.3 本線作業へ戻る条件

本線作業へ戻るのは、次を満たした後に限る。

- 作業ツリーが clean である。
- 必要な commit / push が利用者承認に基づいて完了している。
- `next --json` が `completed` または利用者が始めようとしている作業に対応する状態を返している。
- side-track / maintenance に入る場合は、開始理由、復帰条件、復帰先を明示している。

### 4.4 メモ更新と実装開始の分離

利用者が「メモに残す」「計画を反映する」と指示した場合、そのターンの対象は文書更新である。

文書更新後は、必要な軽量自己精査または post-write verification、commit、push までを閉じる。実装作業は、その後に利用者が `次へ` や `承認` で進行を示したときに開始する。

## 5. うまくいかない場合の機械処理化候補

この運用メモだけで混線が再発する場合、次の機械処理を検討する。

- 直前の完了報告の `次に必要な操作` を runtime state に保存する。
- 次ターン開始時に、利用者発話と保存された操作語の一致を検査する。
- 操作語が一致した場合、その操作以外の tool 実行やファイル編集を遮断する preflight を追加する。
- commit 成功後に `ahead > 0` なら、`next --json` とは別に `pending_user_operation: push` を返す補助状態を追加する。ただし push 自体は利用者明示承認がある場合だけ許可する。
- side-track 開始 / 終了を working note ではなく構造化 CLI で push / pop できるようにする。

機械処理化する場合も、push / commit / spec.json 更新などの不可逆操作を自動実行する方向にはしない。目的は、自動化ではなく、停止点の取り違えを防ぐことである。

## 6. 現時点の判断

まずは運用メモとして扱う。

同じ種類の混線が再発した場合に、機械処理化へ進む。その場合も、現行ワークフローの正本である `next --json`、不可逆操作の利用者明示承認、maintenance / side-track 手続きと衝突しない形で設計する。
