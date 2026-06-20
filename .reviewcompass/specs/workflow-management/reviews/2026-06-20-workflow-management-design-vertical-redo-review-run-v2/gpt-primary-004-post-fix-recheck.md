# GPT primary 004 post-fix recheck: proxy / human approval boundary

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-004`
- 指摘: 段集合の approval stage example が `proxy_model` を許すように読める一方、Requirement 14 では phase approval が human-only とされ、proxy / human 境界が矛盾していた。

## 修正内容

- 段集合の approval stage example は `actor: human`、`actor_allowed: [human]`、`completion_predicate: explicit_human_approval_recorded` に整理済みであることを再確認した。
- review-run 後の proxy_model 判断代行モデルは、approval 段ではなく triad-review 段内の修正方針判断に限ると再確認した。
- proxy decision bundle が承認 record ではなく、human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize を許可しないことを再確認した。
- Requirement 14 §1 で、`decided_by=proxy_model` かつ `decision_scope=human_only` の record は承認として扱わず、`next --json` が不可逆操作へ進めないことを再確認した。
- 変更意図の履歴に残っていた「proxy_model による approval 段の代行条件」という旧表現を、triad-review 内の修正方針判断だけを代行できる、という表現へ修正した。

## 再点検結果

- approval 段の代行を proxy_model に許す直接記述は除去されている。
- `explicit_human_approval_recorded` は利用者の human-only approval record だけで満たされ、proxy_model decision は満たさない。
- human-only override set は operation contract より強く、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize、approval-required irreversible operation execution を proxy decision で進められない。
- 指摘された直接矛盾は解消済みと判断する。

## 残リスク

- 実装段階では、phase approval branch に `proxy_model` actor や `decided_by=proxy_model` が混入した場合に schema / preflight で fail-closed する fixture が必要である。
