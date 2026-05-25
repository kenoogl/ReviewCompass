---
name: no-redundant-workflow-questions
description: 波進行など正本ワークフローが順序・方式を既定する局面で、機能ごとに止めて利用者へ進め方を尋ねない
metadata: 
  type: feedback
---
正本ワークフローが進行順序・単位を既に規定している局面では、機能ごとに止めて「ここで確認するか／まとめて進めるか」を利用者に尋ねない。手順どおり手を止めず進める。

**Why:** タスクフェーズ着手時、方式（全面再導出）も波順（基盤→実行側→評価→自己改善→論文→横断整合ゲート→統治）も正本（WORKFLOW_OVERVIEW 節 2、phase-and-feature-dependency-map §5.1「1 つ書き切って終わりではなく wave として横に広げてから alignment する」）で確定済みなのに、基盤タスク再生成後に進行単位を尋ね「愚問」と指摘された。正本が答えを持つ質問は利用者の時間を奪うだけ。

**How to apply:** 質問の前に自問する——「この答えは正本文書（WORKFLOW_OVERVIEW / 依存マップ / HUMAN_WORKFLOW / spec.json）に既に書かれているか？」。書かれていれば質問せず正本どおり進める。質問してよいのは、正本が沈黙している分岐（例：差分追従型 vs 全面再導出型のような方式選択で前例も指示もない場合）と、spec.json approve / commit / push / phase 移行の明示承認のみ。
