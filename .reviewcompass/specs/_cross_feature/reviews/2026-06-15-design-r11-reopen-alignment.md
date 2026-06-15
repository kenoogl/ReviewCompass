---
date: 2026-06-15
gate: stages/design.yaml#alignment
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: existing_sufficient
---

# design alignment（整合確認）：Requirement 11 設計（重要決定の出典検査）

reopen R-0 の第3過程、design フェーズの alignment 段。§Req 11 設計モデル（design.md 追加節）と既存の設計節（§1〜§XDI）および他の受入基準との整合・矛盾を確認する。

## §Req 11 設計モデルと既存設計の整合

| 既存設計節 | 関係 | 整合判定 |
| --- | --- | --- |
| §段集合の静的列挙モデル（Req 1） | Req 11 の設計（静的検査・サブコマンド）は Req 1 の静的列挙モデルの上に位置する。 | 整合。改訂不要。 |
| §軽量版検査スクリプトモデル（Req 2） | decision-source-lint サブコマンドは Req 2 の拡張として正確に位置づけられている。§Req 11 §5 の接続点設計（サブコマンド名・引数・commit ゲート）は Req 2 のサブコマンド構成（spec-set・commit・push）と形式が一致。 | 整合。Req 2 の設計節の改訂不要。 |
| §起草者と判定者の分離モデル（Req 3） | §Req 11 §6 実装委譲事項は Req 3 の読み取り専用原則（受入 5）との関係を §5 で明示した。proxy_model 非代行の対象（決定記録の書き換え）の例外として --verify-pending を design で確定。Req 3 の設計と整合。 | 整合。改訂不要。 |
| §不可逆操作の直前ゲートモデル（Req 4） | §Req 11 §5 の commit 直前ゲート組み込みは Req 4 のゲート最小集合方針と整合。commit サブコマンドへの統合方法は Req 4 受入 1〜4 と同型。 | 整合。Req 4 の設計節の改訂不要。 |
| §reopen 機械強制モデル（Req 5） | 直接の関係なし。 | 整合。改訂不要。 |
| §session 跨ぎ状態管理モデル（Req 6） | §Req 11 §3 の保留管理は session を跨ぐ状態遷移（pending→転写取り込み→verified）を定める。stages/in-progress/ の枠組みとは別だが補完的。Req 6 の設計節と矛盾しない。 | 整合。Req 6 の設計節の改訂不要（保留状態の具体的な格納場所は implementation で確定）。 |
| §多層防御の位置付けモデル（Req 7） | §Req 11 §5 の fail-closed（unverifiable=DEVIATION）は Req 7 の第 1 層定義と整合。 | 整合。改訂不要。 |
| §機能依存マップモデル（Req 8） | 直接の関係なし。 | 整合。改訂不要。 |
| §reopen 機械強制モデル §6（Req 9） | 直接の関係なし。 | 整合。改訂不要。 |
| §review-wave 要約コマンドモデル（Req 10） | ともに Req 2 のサブコマンド・静的検査だが、Req 10 は review-wave 指標の集計、Req 11 は重要決定の出典検査で対象・目的が別。重複・矛盾なし。 | 整合。改訂不要。 |
| §XDI-WM-001〜003 | 直接の関係なし。 | 整合。改訂不要。 |

## §Req 11 設計モデル内部の整合（受入基準との対応）

- §1（スキーマ）・§2（束ね例外）・§3（逐語照合・保留管理）は「未検証の決定を確定済みとして扱わない」という一貫した fail-closed 原則で結ばれており相互に矛盾しない。
- §3 の保留管理フロー（ステップ 5b）と §5 の commit ゲート（pending=WARN）は、「作業進行をブロックしない」と「確定は保留のまま」の両立を設計で明確に分離しており、requirements AC3 との一貫性が保たれている。
- `--verify-pending` の読み取り専用例外は requirements 受入 5 と design §5 の両方で明示されており、相互参照が整合している。
- bundle-exceptions 承認レコードのスキーマ（§2）と lint の 3 条件確認（§2）は、requirements AC2「個別出典なしには確定させない」の機械強制を設計で確定している。矛盾なし。

## 判定

- **decision：existing_sufficient**（§Req 11 設計モデルは既存設計節と整合し、既存の設計節の改訂を要さない。未処理の整合所見なし）。
- 下流（tasks／implementation）で確定する事項は §6「implementation へ委譲する未確定事項」として明記済み。要件層・設計層の整合に未解決はない。
