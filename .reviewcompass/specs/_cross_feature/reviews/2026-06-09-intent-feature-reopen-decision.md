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

新 feature は作成しない。既存 7 feature すべてを reopen 対象とする。

| Feature | Reopen 判断 | 理由 | 主な証跡 |
| --- | --- | --- | --- |
| foundation | reopen 対象 | 固定パターン依存の除外、実行メタデータ、証拠スキーマ、検証成果物分離の共有契約で受ける | `.reviewcompass/specs/foundation/requirements.md`, `.reviewcompass/specs/foundation/design.md`, `.reviewcompass/specs/foundation/tasks.md`, `.reviewcompass/specs/foundation/implementation-drafting.md` |
| runtime | reopen 対象 | 実 LLM 呼び出し、プロンプト版追跡、構造化証拠、パターン定義非依存の実行境界で受ける | `.reviewcompass/specs/runtime/requirements.md`, `.reviewcompass/specs/runtime/design.md`, `.reviewcompass/specs/runtime/tasks.md`, `.reviewcompass/specs/runtime/implementation-drafting.md` |
| evaluation | reopen 対象 | 収集結果の有効・無効分類、構造化証拠からのメトリクス導出、レビューモード母集団分離で受ける | `.reviewcompass/specs/evaluation/requirements.md`, `.reviewcompass/specs/evaluation/design.md`, `.reviewcompass/specs/evaluation/tasks.md`, `.reviewcompass/specs/evaluation/implementation-drafting.md` |
| analysis | reopen 対象 | 評価・適合性確認の出力を証拠台帳と主張対応図へ構造化し、実行判断を上書きしない派生層として受ける | `.reviewcompass/specs/analysis/requirements.md`, `.reviewcompass/specs/analysis/design.md`, `.reviewcompass/specs/analysis/tasks.md`, `.reviewcompass/specs/analysis/implementation-drafting.md` |
| workflow-management | reopen 対象 | intent 変更を下流工程へ再展開し、不可逆操作前に機械判定する workflow として受ける | `.reviewcompass/specs/workflow-management/requirements.md`, `.reviewcompass/specs/workflow-management/design.md`, `.reviewcompass/specs/workflow-management/tasks.md`, `.reviewcompass/specs/workflow-management/implementation-drafting.md` |
| self-improvement | reopen 対象 | 観測事実と証跡を入力モデルとして保持し、改善提案・履歴・ロールバックへ接続する責務で受ける | `.reviewcompass/specs/self-improvement/requirements.md`, `.reviewcompass/specs/self-improvement/design.md`, `.reviewcompass/specs/self-improvement/tasks.md`, `.reviewcompass/specs/self-improvement/implementation-drafting.md` |
| conformance-evaluation | reopen 対象 | 実装コードからの推定、既存上流文書との比較、契約所有候補と仕様更新草案で受ける | `.reviewcompass/specs/conformance-evaluation/requirements.md`, `.reviewcompass/specs/conformance-evaluation/design.md`, `.reviewcompass/specs/conformance-evaluation/tasks.md`, `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md` |

## 補正理由

先行記録は「既存 feature で受けられるため新 feature 不要」という判断までは行っていたが、そこから導かれる「該当 feature を reopen 対象にする」という判断を明示していなかった。

今回の補正では、新 feature 作成不要の判断と、既存 7 feature の reopen 対象化を分離して記録する。
