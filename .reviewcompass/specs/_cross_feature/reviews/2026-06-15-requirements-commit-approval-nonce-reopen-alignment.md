---
date: 2026-06-15
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-approval-nonce
decision: existing_sufficient
---

# requirements alignment（整合確認）：Requirement 4 commit 承認 nonce 化

reopen R-0 の第3過程、workflow-management requirements フェーズの alignment 段。Requirement 4 受入 6〜7 と既存 Requirement 1〜11、および分類記録・下流 recheck 状態の整合を確認する。

## Requirement 4 受入 6〜7 と既存要件の整合

| 既存要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Req 1（段集合の静的列挙） | 段集合の変更なし。commit 承認 nonce は既存の不可逆操作直前ゲートの中身であり、段定義を増やさない。 | 整合。改訂不要。 |
| Req 2（検査スクリプト・next・fail-closed） | nonce challenge / approval record / commit gate 判定は既存検査スクリプトの commit 経路に接続する。欠落・期限切れ・不一致・消費済みを fail-closed とするため Req 2 の fail-closed 方針と整合。 | 整合。Req 2 改訂不要。 |
| Req 3（起草者と判定者の分離） | 本件は commit 実行前の承認対象束縛であり、review の起草者・判定者分離を変えない。LLM 非依存方針により操縦モデル名を承認条件にしない。 | 整合。改訂不要。 |
| Req 4（不可逆操作の直前ゲート） | 受入 6〜7 は既存受入 5（commit 承認レコード + staged `target_sha256`）を強化し、nonce challenge と target digest の一致検査を追加する。目的「所定手続きの空洞化を防ぐ」と一致。 | 整合。既存目的内の拡張。 |
| Req 5（reopen 手続きの機械強制） | 本 reopen 自体は R-0 として記録済み。nonce 機能は reopen 機構の変更ではない。 | 整合。改訂不要。 |
| Req 6（session 跨ぎ状態管理） | commit 承認 challenge / approval は runtime 承認状態であり、session 跨ぎ状態管理の進行中ファイルとは責務が別。 | 整合。改訂不要。 |
| Req 7（多層防御の第1層） | nonce は第1層の機械ゲート強化であり、LLM 自己申告の限界を staged 内容束縛で補う。暗号的な人間発話証明ではない限界も受入 7 に明記済み。 | 整合。改訂不要。 |
| Req 8（機能依存マップ） | 機能順・依存解決に変更なし。 | 整合。改訂不要。 |
| Req 9（後追い intent 追加時の下流再展開） | 本件は intent 追加ではなく Requirement 4 の拡張。 | 整合。改訂不要。 |
| Req 10（review-wave 要約コマンド） | 対象・責務が異なる。 | 整合。改訂不要。 |
| Req 11（重要決定の出典検査） | どちらも不可逆操作や重要決定の保護に関係するが、Req 11 は出典検査、Req 4 受入 6〜7 は commit 承認対象の staged 内容束縛で責務が別。 | 整合。改訂不要。 |

## 分類記録との整合

- `docs/reviews/reopen-classification-2026-06-15-wm-commit-approval-nonce.md` は R-0、feature は workflow-management、下流影響は design／tasks／implementation と判定している。
- Requirement 4 受入 6〜7 は、既存の不可逆操作直前ゲート内の commit 承認強化であり、intent・feature-partitioning へ遡らないという分類と整合する。
- `.reviewcompass/specs/workflow-management/spec.json` は requirements alignment / approval を差し戻し、`recheck.impacted_downstream_phases` に design／tasks／implementation を保持しているため、要件変更の下流再展開が残っている。

## 判定

- **decision：existing_sufficient**。
- Requirement 4 受入 6〜7 は既存要件と整合し、他 Requirement の改訂を要しない。
- design／tasks／implementation で challenge / approval record / consume / redaction / TDD 実装の詳細を再展開する必要があるため、recheck は維持する。
