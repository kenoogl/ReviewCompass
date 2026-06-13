# alignment（整合確認）：design / Requirement 10（review-wave 要約コマンド、reopen R-0）

- 日付：2026-06-14／対象：design §review-wave 要約コマンドモデル（round-4 収束後）

## 判定：existing_sufficient

| 観点 | 確認 |
| --- | --- |
| requirements 整合 | Requirement 10 受入 1〜5 を設計が網羅（要件と設計の対応表に 5 行追加）。受入 4 の機械可読 fail-closed（非ゼロ終了コード＋JSON status）を §3・§4 で実現。 |
| 既存設計との整合 | §軽量版検査スクリプトモデル §4（fail-closed・第 1 層の限界）、§機能依存マップモデル（feature_order）、§不可逆操作の直前ゲートモデル（読み取り専用）と整合。終了コード規約（0/2、例外 1）は既存サブコマンドと整合。 |
| 内部整合 | §3 スキーマ（固定契約）と §6 委譲範囲が分離（キー名は固定、細部のみ委譲）。draft は run 単位・unresolved/human_required は item 単位で集計軸を明示。insufficient は必須記録欠落/解析不能＋任意記録の解析不能で、任意記録の非在は 0 件として ok。 |
| 三役レビュー収束 | round-1（must-fix 4・should-fix 7）→ 適用 → round-3（must-fix 3 の規範衝突解消）→ round-4 で gpt-5.5・gemini 0 件、claude INFO 3（leave-as-is）。must-fix 0 で収束。 |

未処理所見なし。追加修正不要。
