# C9 post-fix recheck: record_human_decision decision_scope traceability

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-009`
- 指摘: `record_human_decision` の非承認性と、Requirement 14 §1 の `decision_scope` による承認可否判定の接続は設計内に存在するが、Req13 §4 と traceability 表から明示的にたどりにくかった。

## 修正内容

- `.reviewcompass/specs/workflow-management/design.md` の Requirement 13 §4 に、対象 operation を進められるかどうかは Requirement 14 §1 の `decision_scope`、`binding_kind`、digest 束縛、および対象 operation contract から導出した human-only / proxy-allowed 判定で決まることを追記した。
- Requirements Traceability 表で、Requirement 13 受入 6 を `decision_scope` / `binding_kind` による承認対象束縛へ明示的に接続した。
- Requirements Traceability 表で、Requirement 14 受入 3 を Requirement 13 §4 にも接続し、判断記録 operation と承認対象 operation の分離を相互参照できるようにした。

## 再点検結果

- 指摘は INFO の traceability 改善であり、設計ルール自体は既存の Requirement 14 §1 に存在していた。
- 今回の追記により、Req13 側から読んでも `record_human_decision` が承認完了を意味しない理由と、その判定を担う `decision_scope` へ到達できる。
- 新しい正本や追加挙動は導入していないため、既存の human-only / proxy-allowed 境界とは矛盾しない。

## 残リスク

- 実装段階では、`record_human_decision` のテストが `decision_scope` derivation、`binding_kind` derivation、digest mismatch、proxy_model + human_only の拒否を同時に覆う必要がある。
