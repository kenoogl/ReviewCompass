---
date: 2026-06-19
gate: stages/implementation.yaml#review-wave
feature: all_features
phase: implementation
stage: review-wave
reopen: R-0（integrated-design-implementation）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md
---

# implementation review-wave：統合設計メモ反映

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management implementation フェーズの review-wave（機能横断レビュー段）。

今回の implementation 変更は、Requirement 13〜16 / T-016〜T-019 を implementation drafting へ展開し、implementation triad-review の proxy_model 判断 C1〜C6 を反映したものである。主な対象は次の通り。

- T-016: operation contract、`required_action` 対応、preconditions / postconditions / side_effects / workflow_state_effect、commit boundary
- T-017: 承認ゲート、side track stack、workflow-state snapshot、staged file set digest、human-only decision / proxy_model decision 境界
- T-018: 構造化 effective prompt、prompt audit、review-run recording、text-only 互換 WARN、manifest 不一致 DEVIATION
- T-019: Phase 0〜6、proxy_model triage decision 機械処理化、review-wave consumer impact blocking

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態である。本 review-wave では、workflow-management 以外の feature の implementation 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

今回の implementation drafting / triad-review 対応の直接所有者は workflow-management である。他 feature は operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision を consumer / derivative として影響確認対象に含める。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。implementation 正本を実質変更したため、同 feature の implementation 後段 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については implementation 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | foundation は共有語彙・配置規約を所有するが、今回の implementation drafting は workflow-management 内の操作契約、承認ゲート、prompt audit、triage decision 処理の実装準備である。foundation implementation 正本変更は不要である。 |
| runtime | existing_sufficient | runtime は実行状態や証跡生成側の provider であり、workflow-management はそれらを snapshot / precondition / postcondition の入力として扱う。runtime implementation の run status や evidence writer 実装変更を要求しない。 |
| evaluation | existing_sufficient | evaluation は review-run と post-write verification の成果物を供給する側である。T-018 / T-019 は workflow-management が成果物を structured prompt manifest や proxy_model decision としてどう束ねるかの準備であり、evaluation implementation の分類・比較・出力契約を変更しない。 |
| analysis | existing_sufficient | analysis は workflow-management の手続き履歴・状態を読み取る consumer である。workflow-state snapshot の payload と drift 検査は workflow-management 側で確定・出力される前提で扱えるため、analysis implementation 変更は不要である。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の implementation drafting、triad-review 反映、review-wave / alignment / approval、および後続の実装対象である。 |
| self-improvement | existing_sufficient | self-improvement は改善提案や規律変更の提案側であり、実体の workflow 操作は workflow-management 手続きへ委ねる。proxy_model / human decision 境界や approval gate の実装準備は workflow-management 側で足りるため、self-improvement implementation 変更は不要である。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は gap を workflow-management の reopen 手続きへ引き渡す consumer / upstream source である。active reopen scope と impact review scope の分離、consumer impact blocking は引き渡し後の workflow-management 側で扱うため、conformance-evaluation implementation 変更は不要である。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、implementation 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。

## 証跡

- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/raw-review-triage-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-approval.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-decision-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-response.md`
- `.reviewcompass/post-write-verification/post-write-2026-06-19-286.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md`
