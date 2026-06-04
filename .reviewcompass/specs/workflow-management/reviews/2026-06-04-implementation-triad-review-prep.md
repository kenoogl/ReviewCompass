---
spec: workflow-management
phase: implementation
stage: triad-review-prep
date: 2026-06-04
author:
  identity: main session LLM
  role: preparer
review_mode: api_mediated_independent_3way
---

# workflow-management implementation triad-review 準備

## 目的

workflow-management implementation.drafting の完了を受け、次段の triad-review で
レビュー対象の取りこぼしを防ぎ、各モデルの raw response から main session LLM が
三段階トリアージを行えるようにする。

## レビュー対象

- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_workflow_management_implementation_drafting.py`
- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md`

## 必須規律

- 各モデルの返答は structured YAML だけに依存せず、raw response として保存する。
- main session LLM は raw response を読み、三段階トリアージを作成する。
- 重要所見は、修正案・判断理由・採用案を示し、承認または proxy decision の記録後に実装へ進む。
- proxy decision を使う場合も、人間の代行判断として扱い、判断理由と候補案を後から追える形で残す。
- レビュー結果の要約は、モデル別所見、三段階トリアージ、重要所見の扱いをまとめて提示する。

## レビュー観点

- フェーズ内ワークフロー手順が正本と一致しているか。
- 自律・並列実行で、人間ゲート、proxy decision、コミット承認の境界が曖昧になっていないか。
- サブ担当 LLM の成果物、ログ、統合記録を後から追えるか。
- 機械判定で取りこぼしや順序違反を検出できるか。
- テストが規律違反を実装前に検出できるか。

## 推薦手順

1. 上記レビュー対象をプロンプトに含め、独立3モデルへ API 経由で投げる。
2. 各モデルの raw response を保存する。
3. main session LLM が raw response を読み、重要・推奨・保留の三段階トリアージにまとめる。
4. 重要所見について、平易な説明、候補案、推薦案を提示する。
5. 承認または proxy decision の記録後に、必要な実装作業を切り出す。
6. 並列化できる実装作業は、統合者を main session LLM として分担可能性を判定する。

## 次アクション

`workflow-management / implementation / triad-review` を実行する。実行後はこの準備メモを
照合表として使い、レビュー対象の欠落、raw response の欠落、三段階トリアージの欠落、
重要所見ゲートの欠落がないか確認する。
