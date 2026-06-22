# Effective Prompt: User-Initiated Task Quality Review Materials

## Decision Point
- group: operation_prompt
- id: user_initiated_task_quality_review_materials

## Purpose
task/checklist 品質を API review または proxy_model へ渡す前に、材料と問いを固定する。レビュー品質を守るため、main preanalysis、材料本文、分割された問い、機微情報確認を必須にする。

## Required Inputs
- 対象 backlog TODO 本文。
- 対象 runtime checklist 本文。
- `task-quality-check audit` 結果。
- main preanalysis。
- review result contract。
- decision boundary。

## Mechanical Steps
1. `task-quality-check audit` が OK または WARN であることを確認する。
2. `task-quality-check prepare-review-materials --todo-id <todo-id> --checklist-id <checklist-id>` を実行する。
3. review materials に TODO 本文、checklist 本文、audit 結果、main preanalysis が含まれることを確認する。
4. review questions が粒度、重複、対応、red_tests、順序などに分割されていることを確認する。
5. API に送る前に機微情報を確認する。
6. adversarial / judgment の variant は登録済み variant から選ぶ。

## LLM Scope
- main preanalysis を仮説として作る。
- 足りない観点を明示する。
- API review に進めるべきかを説明する。

## Prohibitions
- main preanalysis を正解としてレビュー側に押し付けない。
- path-only materials にしない。
- 複数の独立判断を 1 prompt に詰め込まない。
- レビュー対象外の repo 情報を広く含めない。

## Stop Conditions
- `task-quality-check audit` が DEVIATION。
- materials に source 本文が含まれない。
- main preanalysis が欠落している。
- review questions が分割されていない。
- API 送信範囲の承認または前提が不明。
