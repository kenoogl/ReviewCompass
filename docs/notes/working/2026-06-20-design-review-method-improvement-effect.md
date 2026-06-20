---
date: 2026-06-20
record_type: evaluation-report
topic: design フェーズにおける縦方向意図レビュー方式の改善効果
status: finalized
baseline:
  approval_record: .reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-approval.md
  review_run: .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/
current:
  approval_record: .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-approval.md
  review_run: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/
---

# design レビュー方式改善効果レポート

## 目的

今回の design フェーズでは、通常の設計レビューに加えて「上流フェーズの意図が現フェーズに反映されているか」という観点を明示したレビュー過程を採り入れた。

本レポートは、その結果として `workflow-management/design.md` の品質がどう変わったかを、前回 design approval 済み成果物と比較して評価する。

## ベースライン選定

比較ベースラインは、2026-06-19 の design approval 済み成果物とする。

- Baseline: `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-design-integrated-design-approval.md`
- Baseline review-run: `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/`
- Current: `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-approval.md`
- Current review-run: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/`

このベースラインを選ぶ理由は、単なる修正前 SHA ではなく「一度 design フェーズを完了扱いにした前回の結果」と比較できるためである。今回の問いは、局所 diff の量ではなく、レビュー方式を変えたことで design フェーズの成果物品質がどう変わったかである。

採用しなかった候補:

- `2026-06-20-workflow-management-design-vertical-redo-review-run/`: prompt target が `review-target.md` にずれており、比較対象としては失敗 run そのものに寄りすぎる。
- v2 の original target SHA: post-fix 前後の局所比較には使えるが、「前回 design フェーズ結果」との比較には狭すぎる。
- requirements approval 結果: 上流 phase であり、design 文書品質そのものの比較対象ではない。

## 比較サマリ

| 観点 | 前回 design 結果 | 今回 design 結果 | 評価 |
| --- | --- | --- | --- |
| レビュー観点 | Requirement 13〜16 の design 展開確認が中心 | 上流目的・責務境界・受入条件・禁止事項が design に継承されたかを明示確認 | 改善 |
| triad-review 所見 | 3 件。C1 leave-as-is、C2/C3 should-fix | 15 件。13 件 must-fix、2 件 should-fix | 検出力は大幅改善 |
| adversarial 役 | `claude-opus-4-8` は parse_failed | `claude-sonnet-4-6` が 9 件検出、parse 成功 | 安定性改善 |
| 問題の深さ | completion criteria など表層・整合表現の修正中心 | contract authority、19語彙、proxy/human、active scope、Phase 0 など設計決定の不足を検出 | 設計密度改善 |
| post-fix 検証 | triage 反映後の局所確認中心 | coverage inventory、integrated post-fix review、post-fix manifest、readiness check を追加 | 証跡性改善 |
| 手続きコスト | 比較的軽い | 非常に重い。prompt quality review、proxy 判断、post-fix recheck、manifest、readiness など多数 | 悪化 |

## 品質面の改善

### 1. 「設計で決めるべきこと」が明確になった

前回の design approval では、Requirement 13〜16 は design に展開されたと扱われたが、実際には「requirements のどの意図・責務境界・禁止事項を design が設計決定として受け止めるか」の境界が弱かった。

今回のレビューでは、次が design 欠陥として検出された。

- operation contract と operation registry / preflight の正本境界
- 19 `required_action` の個別 mapping
- `run_maintenance` / `run_workflow_stage` の branch / internal step / approval aggregation
- approval record の binding rule
- proxy_model が代行できる判断と human-only approval の境界
- active reopen scope の保存場所と `next --json` への接続
- Phase 0 completion criteria と D-003 traceability
- prompt length-bound の source of truth

これにより、requirements 由来の判断が design 本文の中で明示され、後続工程が推測で設計決定を補う余地が減った。

### 2. 上流意図の欠落が見えるようになった

前回は「Requirement 13〜16 が design にあるか」を確認する傾向が強かった。今回は「Requirement 13〜16 の目的・責務境界・禁止事項が、design の実際の構造に落ちているか」を確認した。

この違いにより、たとえば「proxy_model は approval を代行しない」という上流意図が、単なる文章ではなく、`decision_scope`、`binding_kind`、human-only override、operation contract からの導出規則として design に必要だと見えるようになった。

### 3. requirements から design への接続が強くなった

今回の design alignment では、Requirement 13〜16 が design の各設計モデルへどう落ちているかを明示した。

- Requirement 13 → design §Requirement 13：operation contract 語彙と `required_action` 対応
- Requirement 14 → design §Requirement 14：承認ゲート、側道スタック、状態スナップショット
- Requirement 15 → design §Requirement 15：構造化有効プロンプトと監査
- Requirement 16 → design §Requirement 16：段階的実装計画 Phase 0〜6

tasks T-016〜T-019 への追跡は補助的に確認しているが、本レポート上の主評価対象は requirements → design の反映品質である。前回も対応節は存在したが、今回の方が「requirements の意図が design のどの設計判断として確定したか」が明確になった。

### 4. 証跡の信頼性が上がった

今回追加した証跡は次である。

- `post-fix-coverage-inventory.md`
- `integrated-post-fix-review.md`
- `integrated-post-fix-recheck.md`
- `post-fix-target-manifest.yaml`
- `post-fix-completion-readiness.md`

これにより、単に「直した」と言うだけでなく、15 件の所見がすべて post-fix recheck に接続され、さらに統合後に発生した新しい不整合も検出・修正されたことを追跡できる。

## 悪化・副作用

### 1. コストが大きい

今回の方式は、品質面では有効だったが、手続き量が非常に大きい。

- prompt quality review
- proxy_model 判断
- finding ごとの post-fix recheck
- integrated post-fix review
- manifest 補正
- triage finalization
- readiness 記録
- review-wave / alignment / approval 記録

この重さは、毎回そのまま使うには過剰である。特に、今回の design review-wave は実質的には「他 feature 変更不要」の軽量確認で足りた。

### 2. 修正中に新しい不整合を作った

C1〜C7 を直す過程で、Req 13 の表に次の新しい不整合が入った。

- `approval_required` は boolean なのに、表では「外部送信承認 contract に従う」という方針文が入った。
- `internal_steps[]` は `source_ref` 必須なのに、branch step table に `source_ref` がなかった。

これは integrated post-fix review で検出して修正できたが、同時に「修正量が増えるほど、post-fix 自体のレビューが必要になる」ことを示している。

### 3. 手作業運用の失敗余地が大きい

今回の途中では、proxy_model 用 runner / prompt quality runner の使い分け、複数判断を 1 prompt に詰める問題、sandbox / approval 経路の混乱が発生した。

これは文書品質そのものとは別だが、レビュー方式としては重要な欠点である。機械化されていない状態では、正しい方法を採っていても運用ミスで時間とコストが増える。

### 4. 所見数の増加を品質低下と誤読しやすい

今回の review-run は 15 件の所見を出した。表面的には「前回より悪くなった」と見えるが、実際には前回見落としていた design authority の不足が露出した面が大きい。

ただし、これは説明を要する。所見数だけで品質を測ると、今回の改善効果を誤解する。

## 総合評価

今回の方式は、設計文書の品質を実質的に改善した。

特に改善したのは、文面の整合性ではなく、requirements の上流意図を design が設計判断として受け止める決定密度である。前回は「Requirement 13〜16 を design に書いた」状態だった。今回は「Requirement 13〜16 を design 内の責務境界・機械可読契約・禁止事項へ落とした」状態に近づいた。

一方で、方式そのものは重い。すべての review-wave や小規模修正に同じ深さで適用すると、費用対効果が悪くなる。

## 今後の運用案

1. 上流意図の反映が問題になる design / tasks / implementation レビューでは、今回の縦方向意図レビューを採用する。
2. review-wave は、他 feature 正本変更の可能性が低い場合、今回のような軽量確認でよい。
3. prompt quality review は、高リスク・上流接続・外部 API review の前に使う。小規模な局所修正では省略可能にする。
4. post-fix 量が多い場合は、integrated post-fix review を必須にする。
5. proxy_model / prompt quality / triad-review の runner 選択と出力契約は機械 preflight 化する。
6. 所見数ではなく、「設計決定が tasks に先送りされていないか」「上流の禁止事項が機械可読境界に落ちているか」を品質指標にする。

## 結論

ベースラインと比べ、今回の設計文書は品質的に改善している。

改善の中核は、上流意図を設計本文へ明示的に接続したことで、operation contract、approval boundary、active scope、Phase 0〜6 のような重要判断が tasks / implementation の推測に残りにくくなった点である。

ただし、今回の方式は重い。今後は、上流接続リスクが高いレビューには今回の方式を使い、横断影響が軽い review-wave は軽量記録に留める、という使い分けが必要である。
