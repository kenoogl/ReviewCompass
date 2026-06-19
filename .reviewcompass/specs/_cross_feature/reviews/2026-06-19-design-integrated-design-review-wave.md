---
date: 2026-06-19
gate: stages/design.yaml#review-wave
feature: all_features
phase: design
stage: review-wave
reopen: R-0（integrated-design-design）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave-summary.md
---

# design review-wave：統合設計メモ反映

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management design フェーズの review-wave（機能横断レビュー段）。

今回の design 変更は、requirements Requirement 13〜16 を workflow-management の設計正本へ展開し、design triad-review の C2/C3 should-fix を反映したものである。主な対象は次の通り。

- operation contract 語彙、registry、19 `required_action` との対応
- 複合 operation の表現方針
- 承認ゲート、side-track stack、commit mixing 防止、状態スナップショット
- structured effective prompt と prompt audit
- proxy_model triage decision の機械処理化
- Phase 0〜6 の段階的実装順序
- Completion Criteria の workflow/reopen 操作面への拡張

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: recheck pending（design, tasks, implementation）
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、現在の workflow-management reopen が完了していないために発生している一時状態である。本 review-wave では、他 feature の design 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 機能横断の影響判定

今回の design 変更の直接所有者は workflow-management である。他 feature は operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision を consumer / derivative として影響確認対象に含める。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。design 正本を実質変更したため、同 feature の design 後段と tasks / implementation の対象 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については design 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave と downstream impact decision に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | foundation は全体共有契約・配置規約を所有するが、ワークフロー段管理機構の具体実装は workflow-management 責務として既に切り分けられている。今回追加した operation contract / approval / prompt audit / snapshot の設計は workflow-management 内の操作契約であり、foundation の共有語彙正本を変更しない。 |
| runtime | existing_sufficient | runtime は状態信号と証拠生成側として workflow-management に `run_manifest.yaml` 等を提供する。今回の変更は workflow-management がそれらをどう選択・事前検査・記録するかの設計であり、runtime の run status、実行終了境界、evidence writer の設計変更を要求しない。 |
| evaluation | existing_sufficient | evaluation は review-run や post-write verification 証跡の評価・派生成果物供給側であり、workflow-management はその成果物を読む。structured effective prompt の監査対象化は workflow-management 側の操作契約であり、evaluation の分類・メトリクス・モデル比較契約は現行設計で足りる。 |
| analysis | existing_sufficient | analysis は workflow-management の所定手続き実行履歴を運用ダッシュボードへ取り込む読み手であり、具体の公開先パスと項目は workflow-management 設計で確定する前提を既に持つ。workflow-state snapshot の追加はこの前提内で扱えるため、analysis design の正本変更は不要。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の design 展開、triad-review 反映、review-wave / alignment / approval、および tasks / implementation の再実施対象である。 |
| self-improvement | existing_sufficient | self-improvement は規律変更の提案権を持ち、実体変更は workflow-management の所定手続きへ委ねる設計である。承認ゲート、side-track、operation contract はその実体変更手続き側の設計であり、self-improvement の提案・承認・履歴モデルの正本変更を要求しない。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は正本更新が必要な gap を workflow-management の reopen 手続きへ引き渡す設計を既に持つ。今回の operation contract / snapshot / structured effective prompt は、引き渡し後に workflow-management がどう処理するかの内側設計であり、reopen handoff package や依存種別の設計変更は不要。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、design 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- reopen scope と impact review scope は区別する。他 feature の workflow flag を false に戻さない理由は、他 feature が正本変更不要であり、consumer / derivative としての確認で足りるためである。
- 下流（tasks / implementation）への縦方向の再展開は、reopen の `impacted_downstream_phases`（design / tasks / implementation）で扱う。

## 証跡

- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/raw-review-triage-summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md`
- `.reviewcompass/post-write-verification/post-write-2026-06-19-277.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-review-wave-summary.md`
