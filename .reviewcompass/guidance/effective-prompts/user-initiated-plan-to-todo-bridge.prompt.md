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
- `operation-prompt --trigger-text <text> --json` から入った場合は `trigger_resolution`。
- `work-backlog plan-todo-bridge --plan-id <plan-id> --json` の出力。
- 現在の work unit stack。

## Trigger Resolution Evidence
- `trigger_resolution.trigger_kind` が `short_continuation` の場合、短い「次へ」「進める」「継続」から bridge に入ったことを示す。
- `trigger_resolution.reason` が `unmaterialized_plan_slice` の場合、未展開 plan slice が bridge 選択理由である。
- `trigger_resolution.reason` が `multiple_unmaterialized_plan_candidates` の場合、複数 plan 候補があるため、`candidate_plan_ids` を利用者に示し、対象 plan を明示してから進む。
- `trigger_resolution.candidate_plan_ids` は候補 plan の一覧であり、TODO 化する plan を一意に決めるための証跡である。
- `trigger_resolution.requested_plan_id` がある場合は、その plan に絞って解決されたことを確認する。

## Artifact Boundaries
- plan は方針、分解案、受け入れ条件、残作業を保持する。実行対象そのものではなく、どこを TODO 化するかを判断する上流材料である。
- TODO は実行対象化した最小の追跡単位である。1 つの TODO は、同じ目的、同じ完了条件、同じ検証単位で閉じる範囲だけを扱う。
- runtime checklist は実行中の進捗証跡である。TODO の task / implementation_plan / todos / red_tests から生成し、作業中の active / pending / done を保持する。
- evidence checklist は完了後の固定証跡である。runtime checklist を後から作業中だったかのように補う場所ではなく、完了時点の checklist と検証結果を残す。
- TODO の execution_history は、完了した checklist_id、evidence_path、completion_summary を TODO 正本へ戻す索引である。

## TODO Conversion Rules
- 同時に完了判定できる範囲だけを 1 TODO にする。複数の独立した成果物、検証、判断待ちを含む場合は TODO を分ける。
- plan の一部だけを実行する場合、TODO には source_plan_id または source_plan_path と、対象 phase / task / acceptance_criteria / red_tests の対応を記録する。
- acceptance_criteria は TODO の完了条件へ落とす。受け入れ条件に対応しない checklist item だけで実作業へ進まない。
- red_tests は実装前の確認項目として TODO または checklist に残す。赤テストが不要な文書作業では lightweight self-check の理由を明示する。
- 既存 TODO がある場合は、対象範囲、完了条件、検証単位が plan の実行範囲を覆るかを確認してから再利用する。
- 対応が曖昧な場合は TODO を新規作成または分割し、曖昧なまま既存 TODO に押し込まない。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `work-backlog plan-todo-bridge --plan-id <plan-id> --json` を実行し、`materialization.summary`、`materialization.slices`、`materialization.next_candidates` を確認する。
3. 未展開 slice がある場合、`materialization.next_candidates` から今回扱う phase を選び、plan 全体完了と一部完了を区別して利用者に示す。
4. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
5. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
6. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
7. 状態変更の直前確認を済ませた場合だけ、`work-backlog start-checklist --id <todo-id> --mutation-boundary-confirmed` で runtime checklist を生成する。
8. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
9. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
10. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
11. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
12. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
13. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

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
- `work-backlog plan-todo-bridge` の materialization status を確認せずに、短い「次へ」「進める」から実装へ進まない。
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
