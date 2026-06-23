# Effective Prompt: User-Initiated Backlog TODO Execution

## Decision Point
- group: operation_prompt
- id: user_initiated_backlog_todo_execution

## Purpose
ユーザが backlog TODO の実行を指示したときに読む。主 workflow の `next --json` から直接開始されない補助処理でも、対象 TODO、runtime checklist、blocking unit、quality gate の接続を固定する。

## Required Inputs
- ユーザが明示した backlog TODO id、または status: promoted の単一 TODO。
- `.reviewcompass/backlog/index.yaml`
- 対象 backlog TODO 本文。
- 対象 TODO から生成または選択した runtime checklist。
- 現在の work unit stack。

## Mechanical Steps
1. `work-unit preflight-start` で active unit と resume pending を確認する。
2. 対象 TODO が未指定の場合、status: promoted の TODO が単一かを確認する。
3. 複数 promoted TODO がある場合は停止し、ユーザに対象 TODO id を確認する。
4. `work-backlog show --id <todo-id> --json` で対象 TODO 本文を読む。
5. 必要なら `work-unit enter-blocking` で blocking unit を開始する。
6. 状態変更の直前確認を済ませた場合だけ、`work-backlog start-checklist --id <todo-id> --mutation-boundary-confirmed` で runtime checklist を作成する。
7. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
8. coverage が DEVIATION の場合は実装へ進まず、TODO/checklist の修正に戻る。
9. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
10. quality が DEVIATION の場合は実装へ進まず、TODO/checklist の修正に戻る。
11. coverage / quality が OK の場合だけ checklist item を active にして作業を進める。

## LLM Scope
- ユーザの自然言語指示がどの TODO に対応するかを読む。
- 複数候補がある場合、勝手に選ばず停止する。
- warning の意味を説明する。

## Prohibitions
- TODO 本文を読まずに path-only で進めない。
- checklist item を LLM 要約だけで作らない。
- `work-backlog audit-checklist-coverage` と `task-quality-check audit` の前に checklist item を active にしない。
- 複数判断を 1 回の API review prompt に詰め込まない。
- blocking unit の出入りを暗黙にしない。

## Stop Conditions
- 対象 TODO が一意に定まらない。
- active unit と新規作業の関係が説明できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
