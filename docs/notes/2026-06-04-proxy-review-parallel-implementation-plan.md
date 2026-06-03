# proxy review 判断代行と並列実装の正本化計画メモ

作成日：2026-06-04

## 目的

API review-run 後に、メインセッション LLM が raw レビューを集約して三段階トリアージし、重要件の判断を proxy_model が代行し、実装作業を必要に応じて別スレッド・分離 worktree へ切り出せるようにする。

本メモは、会話上の運用案を正本と機械ガードへ落とすための計画メモである。正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様であり、本メモは作業計画と段階導入の記録に限定する。

## 正本化する事項

1. メインセッション LLM は raw review を読み、モデル別要約、同根所見集約、三段階トリアージ下書き、候補案、推薦案を作る。
2. proxy_model は重要件について、採用案、判断理由、棄却案理由、最終ラベルを決める。
3. 機械ガードは proxy decision、raw response、候補案、採用案、判断理由、triage との整合を検査する。
4. 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う。
5. 別スレッド生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する。
6. 作業ノイズは本線 repo に取り込まない。
7. コミット、プッシュ、spec.json 更新、フェーズ移行は人間の明示承認を要求し、proxy_model は代行しない。

## 今回の実装範囲

- `review_triage.py` の approval record 検査で `approved_by: proxy_model` を扱う。
- proxy approval では `proxy_decisions` に finding ごとの decision file を要求する。
- decision file には `approved_by: proxy_model`、`proxy_model_id`、`decision_prompt_path`、`source_raw_paths`、`candidate_options`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を要求する。
- `raw_response_path` の実体が存在しなければ fail-closed にする。
- `decision_prompt_path` と `source_raw_paths` の実体が存在しなければ fail-closed にする。
- `candidate_options` が空または欠落していれば fail-closed にする。
- `approved_final_labels` と decision file の `final_label` が一致しなければ fail-closed にする。

## 今回はまだ実装しない事項

- 別スレッド作成や分離 worktree 作成の自動化。
- サブ担当への依頼テンプレート生成。
- サブ担当差分の許可ファイル外変更検査。
- triage / proxy decision / diff / test result の統合照合コマンド。

これらは、proxy approval gate が安定した後に段階的に追加する。

## 追加対応：自律・並列モード実行前ガード

自律・並列モードは、実装を始める前に実行計画 YAML を作り、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で機械検査する。

このガードは、次の事項を fail-closed で検査する。

1. 実行計画が `mode: autonomous_parallel` と `run_id` を持つ。
2. 人間または `proxy_model` の承認記録があり、レビュー結果サマリと三段階トリアージが利用者へ提示済みである。
3. 各タスクに `source_finding_ids`、担当、許可パス、期待テスト、停止条件がある。
4. 別スレッドまたはサブ担当へ渡すタスクは `separate_worktree` を使う。
5. 依存関係のない並列タスクが同じ `allowed_paths` を更新しない。
6. 統合ゲートとして、メインセッション確認、差分範囲確認、テスト確認、判断根拠確認を要求する。
7. 生成物分類として、実装差分、検証結果、判断根拠、作業ノイズの扱いを明示し、作業ノイズは本線 repo へ取り込まない。

重要件の修正は、レビュー結果の三段階トリアージ後に、候補案、推薦案、判断理由を提示し、承認または proxy decision が記録されるまで実装に進めない。自律実行中でも、`important_decision_requires_approval` が停止条件として各タスクに入っていない計画は逸脱とする。
