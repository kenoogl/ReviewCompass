---
feature: all_features
phase: feature-partitioning
stage: candidate-proposal
date: 2026-06-09
status: correction
source_intent: intent/INTENT.md
---

# Intent Feature Reopen Decision

## 判定対象

2026-06-08 に `intent/INTENT.md` へ追加された「レビュー収集処理を事前設定の写像にしない」意図について、feature-partitioning 段階で次を判定する。

1. 既存 feature に受け皿があるか
2. 受け皿がある場合、どの既存 feature を reopen 対象にするか
3. 受け皿がない場合、新 feature を作成するか

## 判定

新 feature は作成しない。既存 feature への影響は、実装上の所有を軸に、直接影響と間接確認に分ける。intent 文書内の挿入箇所は、intent の性質上、feature 所属判定の主根拠にしない。

| Feature | Impact 区分 | Reopen 判断 | 理由 | 主な証跡 |
| --- | --- | --- | --- | --- |
| foundation | direct impact | reopen 対象 | 固定パターン依存の除外、実行メタデータ、証拠スキーマ、検証成果物分離の共有契約で直接受ける | `.reviewcompass/specs/foundation/requirements.md`, `.reviewcompass/specs/foundation/design.md`, `.reviewcompass/specs/foundation/tasks.md`, `.reviewcompass/specs/foundation/implementation-drafting.md` |
| runtime | direct impact | reopen 対象 | 実 LLM 呼び出し、プロンプト版追跡、構造化証拠、パターン定義非依存の実行境界で直接受ける | `.reviewcompass/specs/runtime/requirements.md`, `.reviewcompass/specs/runtime/design.md`, `.reviewcompass/specs/runtime/tasks.md`, `.reviewcompass/specs/runtime/implementation-drafting.md` |
| evaluation | direct impact | reopen 対象 | 収集結果の有効・無効分類、構造化証拠からのメトリクス導出、レビューモード母集団分離で直接受ける | `.reviewcompass/specs/evaluation/requirements.md`, `.reviewcompass/specs/evaluation/design.md`, `.reviewcompass/specs/evaluation/tasks.md`, `.reviewcompass/specs/evaluation/implementation-drafting.md` |
| conformance-evaluation | direct impact | reopen 対象 | 実装コードからの推定、既存上流文書との比較、契約所有候補、仕様更新草案を実装上の所有責務として持つため直接受ける | `.reviewcompass/specs/conformance-evaluation/requirements.md`, `.reviewcompass/specs/conformance-evaluation/design.md`, `.reviewcompass/specs/conformance-evaluation/tasks.md`, `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md` |
| analysis | indirect check | 間接確認のみ | evaluation / conformance-evaluation の出力を証拠台帳と主張対応図へ構造化する派生層であり、収集判断自体は上書きしない | `.reviewcompass/specs/analysis/requirements.md`, `.reviewcompass/specs/analysis/design.md`, `.reviewcompass/specs/analysis/tasks.md`, `.reviewcompass/specs/analysis/implementation-drafting.md` |
| workflow-management | indirect check | 間接確認のみ | intent 変更を下流工程へ再展開する手続き側の整合確認として扱い、レビュー収集仕様の直接受け皿ではない | `.reviewcompass/specs/workflow-management/requirements.md`, `.reviewcompass/specs/workflow-management/design.md`, `.reviewcompass/specs/workflow-management/tasks.md`, `.reviewcompass/specs/workflow-management/implementation-drafting.md` |
| self-improvement | indirect check | 間接確認のみ | 観測事実と証跡を改善提案・履歴・ロールバックへ接続する後段であり、収集処理の判断主体ではない | `.reviewcompass/specs/self-improvement/requirements.md`, `.reviewcompass/specs/self-improvement/design.md`, `.reviewcompass/specs/self-improvement/tasks.md`, `.reviewcompass/specs/self-improvement/implementation-drafting.md` |

`N-0` は、計画書 §5.6 の trigger map と `tools/check-workflow-action.py` の `REOPEN_TRIGGER_MAP` に定義された、intent 起点の再確認分類である。今回の `intent/INTENT.md` 追記は feature-partitioning の再確認を必要とするため、`N-0` として扱う。

この判定は、`.reviewcompass/specs/_cross_feature/reviews/2026-06-09-feature-impact-reopen-review-run/review_summary.md` の3役レビュー結果を踏まえつつ、実装上の所有を主軸に再検討したもの。direct impact feature の再確認で既存責務を超えると判明した場合は、feature-partitioning に戻して新 feature 要否を再判定する。

## 補正理由

先行記録は「既存 feature で受けられるため新 feature 不要」という判断までは行っていたが、そこから導かれる「該当 feature を reopen 対象にする」という判断を明示していなかった。

今回の補正では、新 feature 作成不要の判断、実装上の所有を持つ direct impact feature の reopen 対象化、indirect check feature の波及確認を分離して記録する。
