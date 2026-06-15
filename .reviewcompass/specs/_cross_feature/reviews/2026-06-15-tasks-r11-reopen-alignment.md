---
date: 2026-06-15
gate: stages/tasks.yaml#alignment
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: existing_sufficient
---

# tasks alignment（整合確認）：Req 11 タスク追記（reopen R-0 2026-06-15）

reopen R-0 の第3過程、tasks フェーズの alignment 段。T-013 タスク定義と既存の T-001〜T-012 タスク、および requirements/design との整合・矛盾を確認する。

## T-013 と既存タスクの整合

| 既存タスク | 関係 | 整合判定 |
| --- | --- | --- |
| T-001（成果物配置の準備） | T-013 の前提タスクに含まれる。`decisions/` ディレクトリ・`bundle-exceptions/` サブディレクトリの配置準備は T-001 の責務範囲か implementation で作成するかの判断は T-013 成果物の実装段で行う。タスク間の境界は明確。 | 整合。改訂不要。 |
| T-004（軽量版検査スクリプト本体） | T-013 の前提タスク。T-013 は `cmd_commit` への統合を行うが、T-004 が `cmd_commit` の基本構造を提供する。責務分離は明確（T-004 = commit ゲート基盤、T-013 = decision-source-lint サブコマンドの追加と統合）。 | 整合。T-004 の改訂不要。 |
| T-005（起草者と判定者の分離 機械検査） | 直接の関係なし。T-013 の `--verify-pending` は決定記録の更新であり、著者・レビュアー同一チェックとは別の責務。 | 整合。改訂不要。 |
| T-006（不可逆操作の直前ゲート機構） | T-013 は T-006 の commit ゲート体系に decision-source-lint チェックを追加する。T-006 が commit ゲートの基盤を提供し、T-013 がそこに追加するという依存関係は T-013 の「前提タスク：T-004」で（T-004 が T-006 を前提とする形で）間接的にカバーされる。 | 整合。T-006 の改訂不要。 |
| T-007（reopen 機械強制） | 直接の関係なし。 | 整合。改訂不要。 |
| T-008（session 跨ぎ状態管理） | T-013 の `verification_status: pending` 管理は session を跨ぐ状態であり、T-008 の session 跨ぎ管理と補完的。ただし `decisions/` ディレクトリは `stages/in-progress/` とは別の管理域であり、責務重複なし。 | 整合。改訂不要。 |
| T-012（review-wave 横断確認の要約コマンド） | 直接の関係なし。T-012 は review-wave 指標の集計、T-013 は重要決定の出典検査で対象・目的が別。 | 整合。改訂不要。 |

## 要件追跡の双方向整合

- T-013 は Req 11 受入 1〜7 を網羅することを要件追跡表で確認済み。
- Req 11 のすべての受入基準（7 条件）が T-013 の責務・テスト要件・完了条件のいずれかに対応している。
- T-001〜T-012 が担う受入基準との重複・漏れなし。

## T-013 内部の整合

- T-013 完了条件の「design §6 の実装委譲 4 事項が implementation で確定」は、tasks が implementation の成果要件を宣言する正当な役割であり、tasks のスコープ超過ではない。
- テスト要件(2)の部分満足 fail-closed は design §2「3 条件をすべて満たす場合のみ通過」の正確な反転であり、整合している。
- テスト要件(10)の end-to-end テストは T-004 の commit ゲート基盤と一致する検証粒度である。

## 判定

- **decision：existing_sufficient**（T-013 タスク定義は既存タスク T-001〜T-012 と整合し、既存タスクの改訂を要さない。未処理の整合所見なし）。
