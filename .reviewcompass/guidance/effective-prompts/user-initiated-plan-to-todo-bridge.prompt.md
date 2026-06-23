# Effective Prompt: User-Initiated Plan To TODO Bridge

## Decision Point
- group: operation_prompt
- id: user_initiated_plan_to_todo_bridge

## Purpose
ユーザが backlog plan または plan 内の一部作業を実行しようとしたときに読む。plan を実行単位へ変換する直前で、plan から直接実作業に入らず、backlog TODO、runtime checklist、coverage / quality audit、必要時の review materials へ接続する。

## Trigger Boundary
- ユーザが「次へ」「進める」「この plan を進める」など、plan 由来の実作業開始を指示した。
- `next --json` が completed で、次作業を backlog plan から選ぶ状態になった。
- plan の `implementation_plan`、`acceptance_criteria`、remaining work を読んで実装、整理、移行、監査へ入ろうとしている。
- plan の一部 phase / task だけを実行しようとしている。

plan を読むだけ、説明するだけ、優先順位を相談するだけの場合は、この bridge を開始しない。

## Required Inputs
- 対象 plan id または plan path。
- `.reviewcompass/backlog/index.yaml`
- 対象 plan 本文。
- 対応する既存 backlog TODO の有無。
- 現在の work unit stack。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
3. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
4. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
5. `work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。
6. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
7. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
8. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
9. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
10. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
11. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

## High-Risk Signals
- plan から複数の独立作業を切り出す必要がある。
- TODO の粒度や順序に迷いがある。
- `task-quality-check audit` が WARN を返した。
- red test の位置づけ、レビュー要否、または実行順序に判断が必要である。
- plan と既存 TODO/checklist の対応が曖昧である。

## LLM Scope
- ユーザの自然言語指示がどの plan 範囲に対応するかを読む。
- 既存 TODO が plan の対象範囲を十分に覆うかを説明する。
- WARN または高リスクの理由を利用者に平易に説明する。
- review materials を作る場合、送信前に認証情報、個人情報、不要な全文ログ、外部送信不可情報が含まれないか確認する。

## Prohibitions
- TODO/checklist がないまま plan から実作業へ進まない。
- plan 本文を読まずに path-only で TODO 化しない。
- plan の広い範囲を 1 つの曖昧な TODO に押し込まない。
- 3者レビューを常に必須化しない。
- WARN または高リスクを無視して実作業へ進まない。

## Stop Conditions
- 対象 plan または実行範囲が一意に定まらない。
- 対応 TODO が複数あり、どれを使うべきか判断できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
- WARN または高リスクについて、review materials 作成または明示判断が未了。
