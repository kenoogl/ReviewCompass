---
date: 2026-06-16
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-execution-delegation-formal-cli
decision: existing_sufficient
---

# requirements alignment（整合確認）：commit execution delegation formal CLI

reopen R-0 の第3過程、workflow-management requirements フェーズの alignment 段。Requirement 4 受入 8 と既存 Requirement 1〜11、分類記録、triad-review 対処、review-wave 判定、下流 recheck 状態の整合を確認する。

## Requirement 4 受入 8 と既存要件の整合

| 既存要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Req 1（段集合の静的列挙） | 段集合の変更なし。commit 実行代行承認は既存の不可逆操作直前ゲートの中身であり、段定義を増やさない。 | 整合。改訂不要。 |
| Req 2（検査スクリプト・next・fail-closed） | 正式 CLI、機械可読 delegation record、stdin 入力、fail-closed は既存検査スクリプトのサブコマンド／commit gate 経路に接続する。結論不能・不正入力を通さないため Req 2 の fail-closed 方針と整合。 | 整合。Req 2 改訂不要。 |
| Req 3（起草者と判定者の分離） | 本件は commit 実行代行の明示承認であり、review の起草者・判定者分離を変えない。proxy_model が不可逆操作を代行しない境界とも矛盾しない。 | 整合。改訂不要。 |
| Req 4（不可逆操作の直前ゲート） | 受入 8 は既存受入 5（commit 承認レコード）と受入 6〜7（nonce challenge／LLM 非依存）を補完し、staged content approval と execution delegation を分離したまま同じ nonce context に束縛する。目的「所定手続きの空洞化を防ぐ」と一致。 | 整合。既存目的内の拡張。 |
| Req 5（reopen 手続きの機械強制） | 本 reopen 自体は R-0 として記録済み。delegation CLI は reopen 機構そのものを変更しない。 | 整合。改訂不要。 |
| Req 6（session 跨ぎ状態管理） | delegation record は runtime approval 状態であり、`stages/in-progress/` の進行中状態とは責務が別。commit 直前 gate が `stages/in-progress/` を見る既存規律を変えない。 | 整合。改訂不要。 |
| Req 7（多層防御の第1層） | runtime JSON 手編集を正規経路にしないこと、曖昧文言・不正入力・secret 残留を fail-closed にすることは、第1層の機械ガード強化として整合。 | 整合。改訂不要。 |
| Req 8（機能依存マップ） | 機能順・依存解決に変更なし。 | 整合。改訂不要。 |
| Req 9（後追い intent 追加時の下流再展開） | 本件は intent 追加ではなく Requirement 4 の拡張。 | 整合。改訂不要。 |
| Req 10（review-wave 要約コマンド） | 対象・責務が異なる。Req 10 の機械サマリを本 review-wave 証跡として使ったが、Req 10 の契約変更は不要。 | 整合。改訂不要。 |
| Req 11（重要決定の出典検査） | どちらも不可逆操作や重要決定の保護に関係するが、Req 11 は出典検査、Req 4 受入 8 は commit execution delegation の記録・検証で責務が別。 | 整合。改訂不要。 |

## 分類記録との整合

- `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md` は R-0、feature は workflow-management、下流影響は design／tasks／implementation と判定している。
- Requirement 4 受入 8 は、既存の不可逆操作直前ゲート内の commit 承認強化であり、intent・feature-partitioning へ遡らないという分類と整合する。
- `docs/reviews/reopen-classification-2026-06-16-wm-commit-execution-delegation.md` の design 引き継ぎ（delegate-execution 相当の別サブコマンド、record shape、正規化、許可文言、禁止文言、redaction、validation）は、Requirement 4 受入 8 の後段確定事項として残っている。

## triad-review 対処との整合

- C1（formal CLI path and approval ordering）：Requirement 4 受入 8 に、stdin 入力、機械可読 delegation record、有効な staged content challenge／approval record の前提、staged content approval より前の fail-closed を追記済み。
- C2（stdin payload and replay fail-closed）：Requirement 4 受入 8 に、UTF-8 解析不能、空、空白のみ、byte 上限超過、non-text/binary input、既存未期限切れ delegation record の fail-closed を追記済み。
- C3（residual secret detection outcome）：Requirement 4 受入 8 に、redaction 失敗または残留 secret 検出時は delegation record を作成せず fail-closed とすることを追記済み。
- C4（phrase examples）：要件意図の例示として残し、exact match、Unicode 正規化、case folding、空白処理、phrase-list maintenance は design で確定する方針とした。

## review-wave 判定との整合

- `2026-06-16-requirements-commit-execution-delegation-review-wave.md` は no_impact と判定し、他 6 機能への正本修正不要とした。
- Requirement 4 受入 8 は workflow-management の gate 契約であり、他機能の共有語彙・実行契約・評価契約・分析契約・改善提案契約・conformance 評価契約を変えないため、review-wave 判定と整合する。

## 下流 recheck 状態との整合

- `.reviewcompass/specs/workflow-management/spec.json` は requirements alignment / approval を未完了に戻し、`recheck.impacted_downstream_phases` に design／tasks／implementation を保持している。
- design では delegation CLI の具体サブコマンド、record schema、validation、secret handling、matching / normalization を確定する必要がある。
- tasks では TDD 対象の完了条件・テスト要件へ展開する必要がある。
- implementation では正式 CLI と guard validation を TDD で実装する必要がある。

## 判定

- **decision：existing_sufficient**。
- Requirement 4 受入 8 は既存要件、分類、triad-review 対処、review-wave 判定と整合し、requirements 内の追加改訂を要しない。
- design／tasks／implementation で正式 CLI、delegation record、validation、matching、redaction を再展開する必要があるため、recheck は維持する。
