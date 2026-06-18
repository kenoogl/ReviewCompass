---
date: 2026-06-19
classifier: codex_main_session
classification: R-0（workflow-management）
trigger_source: 統合設計メモの intent / requirements 反映後に、workflow-management の spec.json が実体と合わないことを確認したため。
feature: workflow-management
finding: integrated-design-requirements
---

# Reopen Classification: integrated-design-requirements

## 分類根拠

`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` と `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` は、選択層と実行層を分離し、`required_action` と operation contract、承認ゲート、side-track stack、workflow-state snapshot、structured effective prompt、LLM judge audit を workflow-management の正本へ反映する設計判断を含んでいる。

2026-06-19 の補完作業で、これらは `intent/INTENT.md` と `.reviewcompass/specs/workflow-management/requirements.md` に反映済みである。しかし、`spec.json` は workflow-management の requirements / design / tasks / implementation を全完了扱いのまま保持しており、追加された Requirement 13〜16 に対する正式な requirements triad-review / review-wave / alignment / approval、および下流 design / tasks / implementation への展開は未完了である。

手戻り種別：**R-0（workflow-management requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent：`intent/INTENT.md` には、既存の workflow-management の責務を明確化する意図を追記した。新しい feature 境界や機能分割を導入したものではなく、workflow-management が持つ「状態判定、手続き強制、承認ゲート、LLM judge 運用」の責務を補強する。
- feature-partitioning：追加内容は workflow-management の契約・実行手続き・状態機械に属する。既存 feature の分割変更や新 feature 追加は不要である。
- requirements：Requirement 13〜16 と Change Intent / XDI-WM-005 を追加済みであり、この requirements 正本変更について正式な requirements 段の再実施が必要である。

## 事実

- 反映済み commit：`50c6cbda Recover integrated design requirements`
- 進捗整理 commit：`1763fac4 Record integrated design manual workflow progress`
- 手動進捗表：`docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md`
- 追加要件：
  - Requirement 13：operation contract 語彙と `required_action` 対応
  - Requirement 14：承認ゲート、側道スタック、状態スナップショット
  - Requirement 15：構造化有効プロンプトと監査
  - Requirement 16：段階的実装計画 Phase 0〜6
- 既存 3者 traceability review：`.reviewcompass/evidence/review-runs/2026-06-19-integrated-design-requirements-traceability-3way-rerun`
- post-write verification：`.reviewcompass/post-write-verification/post-write-2026-06-19-251.yaml`

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | Requirement 13〜16 は workflow-management の operation contract、状態管理、承認ゲート、prompt 生成、LLM judge audit を定める契約であり、同 feature が所有する。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通レビュー所見・評価基盤の契約変更ではなく、workflow-management 内部の手続き契約で受けられる。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | レビュー実行パイプラインの runtime 契約変更ではない。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価基準や評価記録契約の変更ではない。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 横断分析の入力・出力契約変更ではない。 |
| self-improvement | no_reopen_existing_feature | consumer_or_derivative_only | LLM judge prompting 規律の参照はあり得るが、今回の契約所有は workflow-management に閉じる。 |
| conformance-evaluation | no_reopen_existing_feature | consumer_or_derivative_only | workflow 状態や operation contract を参照し得るが、正本変更は workflow-management 側で受ける。 |

新 feature 判定：no_new_feature（workflow-management の責務境界で受けられるため）。

## 再実施対象

- workflow-management requirements：triad-review / review-wave / alignment / approval
- workflow-management design：drafting から再実施
- workflow-management tasks：drafting から再実施
- workflow-management implementation：drafting から再実施

`impacted_downstream_phases` は `design`、`tasks`、`implementation` とする。

## 停止点

利用者は 2026-06-19 Codex セッションで、`spec.json` と手動進捗表の照合結果に基づく workflow state 差し戻しを「承認」と明示した。これにより、第1過程（判定とフラグ差し戻し）は承認済みとして記録する。

第2過程の正本修正は、commit `50c6cbda` で `intent/INTENT.md` と `.reviewcompass/specs/workflow-management/requirements.md` に反映済みである。次の実作業は、第3過程として requirements triad-review から開始する。
