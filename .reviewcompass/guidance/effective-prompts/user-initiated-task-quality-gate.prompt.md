# Effective Prompt: User-Initiated Task Quality Gate

## Decision Point
- group: operation_prompt
- id: user_initiated_task_quality_gate

## Purpose
backlog TODO から runtime checklist へ落とした内容が、作業単位として妥当かを検査する。これは仕様駆動開発における要件・設計から task へ落とす処理に相当する。

## Required Inputs
- 対象 backlog TODO 本文。
- 対象 runtime checklist 本文。
- checklist の source_ref と item 一覧。
- red_tests、implementation_plan、acceptance_criteria がある場合はその本文。

## Mechanical Steps
1. 対象 TODO と checklist の対応を確認する。
2. `task-quality-check audit --todo-id <todo-id> --checklist-id <checklist-id>` を実行する。
3. checklist item の粒度、重複、空項目、TODO との対応、red_tests 欠落、作業順序の妥当性を確認する。
4. DEVIATION がある場合は実装へ進まない。
5. WARN がある場合は review materials に引き継ぐ。
6. OK の場合だけ実装または review materials 生成へ進む。

## LLM Scope
- warning が実作業上の問題かを説明する。
- TODO の意図と checklist item の意味的対応を読む。
- 修正案を出す場合は checklist item 単位で示す。

## Prohibitions
- task-quality-check を省略しない。
- warning を黙って捨てない。
- TODO/checklist の path だけを材料にしない。
- red test 欠落を「あとで補う」として通過扱いにしない。

## Stop Conditions
- TODO と checklist の source backlink が確認できない。
- checklist item が空、重複、または TODO と対応しない。
- red_tests が必要なのに欠落している。
- `task-quality-check audit` が DEVIATION。
