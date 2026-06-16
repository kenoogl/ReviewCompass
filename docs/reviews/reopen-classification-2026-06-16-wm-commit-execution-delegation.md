---
date: 2026-06-16
classifier: codex_main_session
classification: R-0（workflow-management）
trigger_source: guarded commit 実行時に、commit 承認 record は staged content approval を保存する一方、guard が要求する execution_delegation を正式 CLI で保存する経路がないことを確認した。利用者は runtime JSON 手編集の workaround を禁止し、workflow の SDD 流儀に従って扱うよう指示した。
feature: workflow-management
finding: commit-execution-delegation-formal-cli
---

## 分類根拠

本件は、`git commit` という不可逆操作に対して、利用者の「内容承認」と、LLM が commit 実行を代行してよいという「実行代行承認」を分離した設計を維持しつつ、後者を正式に記録する経路が不足している問題である。

2026-06-15 の commit 承認 nonce reopen では、Requirement 4 受入 6〜7 と design §不可逆操作の直前ゲートモデル §2.1 により、staged 内容に束縛された nonce challenge、承認 record、LLM/provider/model 非依存判定、秘匿情報 redaction が定義された。同時に implementation-drafting.md では、`commit-approval record` が `execution_delegation` を既定で保存しないことを明示し、staged content approval と LLM commit 実行代行承認を分離した。

しかし、分離後の「実行代行承認」を正式に保存する CLI と受入条件が requirements／design／tasks に未定義だった。そのため、guarded commit は `execution_delegation` 欠落で正しく遮断したが、通すための正規手段がなく、runtime 承認 JSON を手作業で追記する workaround が生じた。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は、所定手続きと不可逆操作ゲートの機械強制を担うことである。本件は既存意図の範囲内であり、意図文書の改訂は不要。
- feature-partitioning（機能分割）：commit 承認、不可逆操作ゲート、承認 runtime record は workflow-management の既存責務で受けられる。新 feature 境界は不要。
- requirements：Requirement 4 の commit 承認契約に、「LLM が commit 実行を代行する場合の execution delegation を正式 CLI で記録し、同じ nonce/challenge/target digest/TTL に束縛し、曖昧な文言では fail-closed にする」受入条件を追加する必要がある。
- design：`commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json` 相当の別サブコマンド、record shape、正規化、許可文言、禁止文言、redaction、validation を定義する必要がある。
- tasks／implementation：正式 CLI と guard validation を TDD で実装し、runtime JSON 手編集なしに commit できることを検証する必要がある。

## 事実

- `commit-approval record` は staged content approval を作るが、`execution_delegation` を既定保存しない。
- `guarded-git-commit.py` は LLM による commit 実行代行を行う場合、承認 record に `execution_delegation` があることを要求する。
- 現状では、利用者が明示的に「コミット」と指示しても、その文言を execution delegation として正式に保存する CLI がない。
- runtime JSON の手編集は監査性が低く、利用者により workaround として禁止された。
- UserPromptSubmit hook は誤発火が確認されており、本件の承認経路には使わない。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | 不可逆操作直前ゲート、commit approval runtime record、承認 CLI、guard validation を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通レビュー語彙や評価スキーマを変更しない。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | アプリ実行時の tracing／artifact 契約ではなく、workflow gate の承認記録で完結する。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | review/evaluation 判定契約を変更しない。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析入力・レポート契約を変更しない。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 改善提案の所有範囲ではなく、workflow-management の既存 gate 強化で受ける。 |
| conformance-evaluation | indirect_check_only | consumer_or_derivative_only | workflow-management の承認契約を確認対象として参照し得るが、実装所有責務は変わらない。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements の Requirement 4 へ受入条件を追加し、design／tasks／implementation へ連鎖する。
- impacted_downstream_phases：design／tasks／implementation。

## 停止点

`reopen-start` により in-progress ファイルを発行し、`workflow-management/spec.json` の requirements 後段と recheck を差し戻す。第1過程の停止点として、利用者が手戻り種別・再実施範囲・差し戻し内容を承認するまで、要件本文・設計本文・タスク本文・テスト・実装には進まない。
