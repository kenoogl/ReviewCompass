---
date: 2026-06-19
classifier: codex_main_session
classification: A-0
trigger_source: 利用者指示「次の作業は、タスク段からのreopenで、新しい規律に従ってタスクを再生成、実装を行う。」
feature: workflow-management
finding: task-granularity-regeneration
---

# Reopen Classification: task-granularity-regeneration

## 分類根拠

直前の完了状態では、`implementation-drafting.md` を正式成果物として採用しない方針に変更済みである。implementation drafting は別文書の作成ではなく、`tasks.md` に従って実際のテストと実装コードを生成する段として扱う。

一方、既存の `.reviewcompass/specs/workflow-management/tasks.md` は、T-016〜T-019 の実装対象を大きく束ねており、implementation drafting に直接入るには粒度が不足している。新しい tasks 粒度規律では、各タスクに実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を含める必要がある。

このため、本件は tasks 段で確定したタスク正本の粒度不足を起点とする手戻りである。requirements と design の意味変更は行わず、tasks 正本を再生成し、その tasks に従って implementation 段でテストと実装コードを作成する。

手戻り種別：**A-0（tasks 起点。design / requirements / intent / feature-partitioning へは遡らない）**。

## 事実

- 直近 commit：`b06e3e2a Remove implementation drafting artifacts`
- `implementation-drafting.md` は正式成果物として採用しない方針へ変更済み。
- `implementation-drafting.md` の削除と、旧 implementation drafting テストの削除は完了済み。
- `test_workflow_management_task_granularity.py` により、tasks.md の粒度規律は検査対象になっている。
- 利用者は、次作業として「タスク段からの reopen」「新しい規律に従ってタスクを再生成」「実装」を指示している。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | tasks.md の粒度規律と、それに従う workflow-management 実装作業を同 feature が所有する。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | tasks 粒度規律の適用対象は workflow-management の tasks 正本と実装であり、foundation 正本の変更は不要である。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | runtime の実行パイプライン契約変更ではない。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価基準・評価記録契約の変更ではない。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析成果物や横断分析契約の変更ではない。 |
| self-improvement | no_reopen_existing_feature | consumer_or_derivative_only | タスク粒度規律を参照し得るが、今回の正本修正は workflow-management に閉じる。 |
| conformance-evaluation | no_reopen_existing_feature | consumer_or_derivative_only | workflow 規律を参照し得るが、今回の正本修正は workflow-management に閉じる。 |

新 feature 判定：no_new_feature（workflow-management の既存責務境界で受けられるため）。

## 再実施対象

- workflow-management tasks：drafting から再実施
- workflow-management implementation：drafting から再実施

`impacted_downstream_phases` は `implementation` とする。

## 停止点

`reopen-start` により in-progress ファイルを発行し、`workflow-management/spec.json` の tasks / implementation を差し戻す。第1過程の停止点として、利用者が手戻り種別・再実施範囲・差し戻し内容を承認するまで、tasks 再生成、テスト、実装コード作成には進まない。
