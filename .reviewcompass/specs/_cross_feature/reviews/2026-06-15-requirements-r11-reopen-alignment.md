---
date: 2026-06-15
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: existing_sufficient
---

# requirements alignment（整合確認）：Requirement 11（重要決定の出典検査）

reopen R-0 の第3過程、workflow-management requirements フェーズの alignment 段。新設 Requirement 11 と既存 Requirement 1〜10、および受入基準間の整合・矛盾を確認する。

## Requirement 11 と既存要件の整合

| 既存要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Req 1（段集合の静的列挙） | Req 11 は静的検査の一種。意図（静的検査・機械強制）の範囲に収まる。 | 整合。Req 1 改訂不要。 |
| Req 2（検査スクリプト・next・fail-closed） | Req 11 受入7 が「Req 2 の検査スクリプトのサブコマンドとして提供（必須）」。受入5 の fail-closed（非ゼロ終了・機械可読 status）は Req 2 受入4 と同型。Req 10 も同様に Req 2 のサブコマンドを追加しており前例と整合。 | 整合。Req 2 の責務内でサブコマンドを足す形で Req 2 改訂不要。 |
| Req 3（起草者と判定者の分離） | Req 11 受入5 が Req 3 受入5（proxy_model 非代行範囲）を参照。受入6（意味一致の最終判断は人・判定役、機械は検証可能化まで）は Req 3 の分離原則と整合。 | 整合。Req 3 改訂不要。 |
| Req 4（不可逆操作の直前ゲート） | Req 11 受入1 が重要種別の境界を Req 4 を基準に判定。受入7 が Req 4 の commit 直前ゲートへの組み込みを設計拡張として言及。受入3 の「未取り込み出典は確定保留・直前ゲートを通過させて確定済みと見なさない」は Req 4 の不可逆操作直前ゲートと整合。 | 整合。Req 4 の対象に「重要決定の出典検査」を将来 design で接続しうるが、要件層では Req 4 改訂不要。 |
| Req 5（reopen 手続きの機械強制） | 直接の関係なし。 | 整合。改訂不要。 |
| Req 6（session 跨ぎ状態管理） | Req 11 受入3 の「現セッション（未取り込み）出典の保留→取り込み後に確定」は session を跨ぐ状態であり、Req 6 の stages/in-progress による session 跨ぎ状態管理と補完的。矛盾しない。 | 整合。保留状態の具体的な管理手段は design で確定（Req 6 の枠組みを利用しうる）。Req 6 改訂不要。 |
| Req 7（多層防御の第1層） | Req 11 受入5 が Req 7 を参照。fail-closed の第1層位置づけと整合。 | 整合。改訂不要。 |
| Req 8（機能依存マップ） | 直接の関係なし。 | 整合。改訂不要。 |
| Req 9（後追い intent 追加時の下流再展開） | 直接の関係なし。 | 整合。改訂不要。 |
| Req 10（review-wave 横断確認の要約コマンド） | ともに Req 2 のサブコマンド／静的検査だが、Req 10 は review-wave 指標の集計、Req 11 は重要決定の出典検査で対象・目的が別。重複・矛盾なし。 | 整合。改訂不要。 |

## 受入基準間の整合（Requirement 11 内部）

- 受入2（束ね検出 fail-closed）・受入3（逐語照合 fail-closed・未取り込みは確定保留）・受入5（読み取り専用・結論不能で fail-closed）は、いずれも「未検証の決定を確定済みとして扱わない」という一貫した原則で結ばれ、相互に矛盾しない。受入3 の保留経路は受入5 の fail-closed と整合する（保留＝確定済みと見なさない）。
- 受入6（機械は検証可能化まで・意味一致は人/判定役）は受入1〜4 の機械検査範囲と役割分担で整合。

## 判定

- **decision：existing_sufficient**（Requirement 11 は既存要件と整合し、既存 Requirement 1〜10 の改訂を要さない。未処理の整合所見なし）。
- 下流（design／tasks／implementation）で確定する事項は Requirement 11 内に「design で確定」と明記済みで、要件層の整合に未解決はない。
