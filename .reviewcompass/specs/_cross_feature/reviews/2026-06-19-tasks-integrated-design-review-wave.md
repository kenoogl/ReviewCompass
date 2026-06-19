---
date: 2026-06-19
gate: stages/tasks.yaml#review-wave
feature: all_features
phase: tasks
stage: review-wave
reopen: R-0（integrated-design-tasks）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md
---

# tasks review-wave：統合設計メモ反映

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management tasks フェーズの review-wave（機能横断レビュー段）。

今回の tasks 変更は、requirements Requirement 13〜16 と design の統合設計内容を workflow-management の実装タスクへ展開し、tasks triad-review の proxy_model 判断 C1〜C4 を反映したものである。主な対象は次の通り。

- T-016: operation contract 語彙、19 `required_action` との対応、commit boundary 強制
- T-017: 承認ゲート、side track stack、workflow-state snapshot、snapshot payload / drift 検査
- T-018: 構造化有効プロンプト、prompt audit、既存 `rounds.yaml` の `effective_prompt_path` / `effective_prompt_sha256` 互換
- T-019: Phase 0〜6 の実装計画、proxy_model triage decision 機械処理化、consumer impact blocking
- Requirement 14〜16 の追跡行における proxy_model / human 境界、staged file set / digest、prompt manifest 互換、active reopen scope / impact review scope 分離

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態である。本 review-wave では、他 feature の tasks 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

今回の tasks 変更の直接所有者は workflow-management である。他 feature は operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision を consumer / derivative として影響確認対象に含める。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。tasks 正本を実質変更したため、同 feature の tasks 後段と implementation の対象 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については tasks 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | foundation は共有語彙・配置規約を所有するが、今回の T-016〜T-019 は workflow-management 内の操作契約、承認ゲート、prompt audit、triage decision 処理の実装単位である。foundation tasks の共有正本タスクを増やす必要はない。 |
| runtime | existing_sufficient | runtime は実行状態や証跡生成側の provider であり、workflow-management はそれらを snapshot / precondition / postcondition の入力として扱う。今回の tasks は workflow-management 側の読み取り・検査・記録方法を定めるため、runtime tasks の run status や evidence writer タスク変更を要求しない。 |
| evaluation | existing_sufficient | evaluation は review-run と post-write verification の成果物を供給する側である。T-018 / T-019 はその成果物を workflow-management が structured prompt manifest や proxy_model decision としてどう束ねるかのタスクであり、evaluation tasks の分類・比較・出力契約を変更しない。 |
| analysis | existing_sufficient | analysis は workflow-management の手続き履歴・状態を読み取る consumer である。workflow-state snapshot の payload と drift 検査は workflow-management 側で確定・出力される前提で扱えるため、analysis tasks のダッシュボード・取り込みタスク変更は不要である。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の T-016〜T-019 展開、triad-review 反映、review-wave / alignment / approval、および implementation の再実施対象である。 |
| self-improvement | existing_sufficient | self-improvement は改善提案や規律変更の提案側であり、実体の workflow 操作は workflow-management 手続きへ委ねる。proxy_model / human decision 境界や approval gate の実装タスクは workflow-management 側で足りるため、self-improvement tasks の変更は不要である。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は gap を workflow-management の reopen 手続きへ引き渡す consumer / upstream source である。active reopen scope と impact review scope の分離、consumer impact blocking は引き渡し後の workflow-management 側タスクであり、conformance-evaluation tasks の handoff package タスク変更を要求しない。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、tasks 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。
- 下流（implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design / tasks / implementation）で扱う。

## 証跡

- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/raw-review-triage-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/proxy-approval.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/proxy-decision-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/review-response.md`
- `.reviewcompass/post-write-verification/post-write-2026-06-19-282.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md`
