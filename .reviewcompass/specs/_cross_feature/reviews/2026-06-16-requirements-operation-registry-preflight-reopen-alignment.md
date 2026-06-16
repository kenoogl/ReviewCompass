---
date: 2026-06-16
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: operation-registry-preflight-unified-design
decision: existing_sufficient
---

# requirements alignment（整合確認）：operation registry / preflight

reopen R-0 の第3過程、workflow-management requirements フェーズの alignment 段。Requirement 12 と既存 Requirement 1〜11、分類記録、triad-review 対処、review-wave 判定、下流 recheck 状態の整合を確認する。

## Requirement 12 と既存要件の整合

| 既存要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Req 1（段集合の静的列挙） | operation registry / preflight は既存段集合を直接増やさず、操作開始前の契約・検査として扱う。 | 整合。改訂不要。 |
| Req 2（検査スクリプト・next・post-write・effective prompt） | Requirement 12 は Req 2 の検査スクリプトを operation 単位へ拡張する。`next`、post-write target detection、effective prompt の既存契約を置き換えず、preflight の入力として参照する。 | 整合。Req 2 の詳細変更は design で接続点を確定する。 |
| Req 3（起草者と判定者の分離） | operation preflight は proxy_model や human approval の代替ではない。レビュー判断や不可逆操作の承認権限を移さない。 | 整合。改訂不要。 |
| Req 4（不可逆操作の直前ゲート） | commit approval chain、LLM 実行代行承認、commit gate は Requirement 12 の `irreversible` operation 対象に含まれる。Req 4 の安全契約を操作開始前へ補助的に広げる。 | 整合。既存目的内の拡張。 |
| Req 5（reopen 手続きの機械強制） | reopen-start / reopen-advance-gate / reopen finalize は `workflow_state` operation として registry 対象になる。trigger_map 自体は変更しない。 | 整合。改訂不要。 |
| Req 6（session 跨ぎ状態管理） | session-record formal output、maintenance side track、nested issue handling は session 跨ぎ状態管理と接続する。Requirement 12 は current-session formal output の作成前防止と nested scope drift 検査を要求する。 | 整合。既存責務を補強。 |
| Req 7（多層防御の第1層） | preflight は第一層の機械ガードであり、意味判断を完全自動化しない。`WARN` / `DEVIATION` の fail-closed 方針も Req 7 と整合する。 | 整合。改訂不要。 |
| Req 8（機能依存マップ） | 全 feature impact review scope は `feature_order` を参照して展開する。依存マップの構造変更は不要。 | 整合。改訂不要。 |
| Req 9（後追い intent 追加時の下流再展開） | downstream re-expansion / conformance handoff は operation preflight の consumer になり得るが、Req 9 の候補取り込み契約を変更しない。 | 整合。改訂不要。 |
| Req 10（review-wave 要約コマンド） | review-wave summary は今回の横断確認証跡として使用した。Requirement 12 は review-wave summary を置き換えない。 | 整合。改訂不要。 |
| Req 11（重要決定の出典検査） | decision-source-lint は operation registry の対象 operation になり得るが、Requirement 11 の出典検査契約を変更しない。 | 整合。改訂不要。 |

## 分類記録との整合

- `docs/reviews/reopen-classification-2026-06-16-wm-operation-registry-preflight.md` は R-0、feature は workflow-management、下流影響は design／tasks／implementation と判定している。
- 全 feature は impact review scope に開くが、正本変更の直接所有者は workflow-management であるという分類と、Requirement 12 受入 11 は整合する。
- Requirement 12 は workflow-management の既存意図である「作業順序、承認、不可逆操作、post-write verification、reopen などの workflow gate を機械強制する」責務の範囲内にある。

## triad-review 対処との整合

- deployment / export 漏れ：Requirement 12 受入 1 の `kind` と受入 10 に `deployment_export` と deployment / export 系 operation を追加した。
- fail-closed 漏れ：受入 3 に `DEVIATION` の停止、未確認を `OK` にしないこと、runner-enabled operation の fail-closed を明示した。
- 正本 command / entrypoint：受入 1 と 4 に正本 invocation identity、parser / parser adapter 照合、短縮名・未登録 alias 拒否を追記した。
- approval / bundle coverage：受入 6 に `approval_record_preflight`、approval record の finding id / final label、bundle / export artifact coverage を追記した。
- read-only 明確化：受入 2 に review-run directory、manifest、approval record、session record、commit、deployment / export output を作らないことを明示した。
- serial-only：受入 7 に並列または順序外実行の試みを拒否することを明示した。
- nested issue / scope：受入 9 に元作業の対象、検証範囲、allowed files、review target、manifest target、return condition が広がる条件を明示した。
- 全 feature impact scope：受入 11 に consumer / derivative feature を review scope に含めることを明示した。

## review-wave 判定との整合

- `2026-06-16-requirements-operation-registry-preflight-review-wave.md` は no_impact と判定し、他 6 機能への requirements 正本修正不要とした。
- Requirement 12 は workflow-management の operation contract であり、他 feature の所有契約を移さないため、review-wave 判定と整合する。

## 下流 recheck 状態との整合

- `.reviewcompass/specs/workflow-management/spec.json` は requirements review-wave / alignment / approval を未完了に戻し、design／tasks／implementation を未完了、`recheck.impacted_downstream_phases` を design／tasks／implementation として保持している。
- design では operation contract、preflight response、command validation、worktree / pending policy、artifact policy、Phase 1 / Phase 2 境界を確定する必要がある。
- tasks では TDD 対象の初期 operation 群、parser adapter、fixture、read-only preflight、runner を分けてタスク化する必要がある。
- implementation では TDD でまず read-only registry / preflight を実装する必要がある。

## 判定

- **decision：existing_sufficient**。
- Requirement 12 は既存要件、分類、triad-review 対処、review-wave 判定と整合し、requirements 内の追加改訂を要しない。
- design／tasks／implementation で operation registry / preflight を再展開する必要があるため、recheck は維持する。
