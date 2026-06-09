---
review_target: requirements-reopen-no-change-decision
date: 2026-06-09
phase: requirements_reopen_triad_review
status: draft_for_triad_review
---

# Requirements Reopen Triad Review Target

## 背景

`intent/INTENT.md` に「レビュー収集処理が事前設定の写像にならない」という意図が追加された。

この意図は、レビューの収集処理を、規則ファイル照合や固定プロンプトの単純写像ではなく、実際の大規模言語モデルの判断に基づく発見と判断として扱う、というもの。

feature-partitioning 再確認では、新 feature は作成せず、既存 7 feature の責務境界で受けると判断した。

## 現在の requirements 判定

requirements 再確認では、次のように判定した。

- 7 feature の requirements.md は、2026-06-08 intent 追加を既存 Requirement で受ける記録を既に持つ。
- そのため、requirements.md 本体への追加修正は不要。
- ただし、この「追加修正不要」判断を triad-review で検証する。

## Feature impact 区分

| Feature | 区分 | requirements 上の受け皿 |
| --- | --- | --- |
| foundation | direct impact | Requirement 5 の固定パターン依存除外、Requirement 1／3／6 の証拠・メタデータ契約 |
| runtime | direct impact | Requirement 1 のレビュー実行制御、Requirement 3 のプロンプト解決と版追跡、Requirement 4 の構造化証拠出力、Requirement 10 のパターン定義依存除外 |
| evaluation | direct impact | Requirement 1 の有効・無効実行の分離、Requirement 3 の構造化証拠からのメトリクス抽出、Requirement 6 のメタデータ完全性検査、Requirement 9 のレビューモード区別 |
| conformance-evaluation | direct impact | Requirement 1 の逆方向推定、Requirement 3 の二段階照合、Requirement 5 の推定・照合両段階への 3 役レビュー適用、Requirement 9 の実装由来契約の仕様更新草案 |
| analysis | indirect check | Requirement 1 の主張から証拠への写像、Requirement 2 の evaluation 出力への来歴連結、Requirement 4 の runtime／evaluation ロジックからの分離、Requirement 5 の証拠分類 |
| workflow-management | indirect check | Requirement 2 の next による上流から下流への再展開、Requirement 4 の不可逆操作直前ゲート、Requirement 6 の session 跨ぎ状態管理、Requirement 8 の機能依存マップ一元化 |
| self-improvement | indirect check | Requirement 1 の workflow 層改善限定、Requirement 2 の規律と実体の乖離入力、Requirement 3 の規律提案単位、Requirement 7 の改善履歴 |

## レビュー対象ファイル

- `intent/INTENT.md`
- `stages/feature-partitioning/2026-05-24-proposal.md`
- `.reviewcompass/specs/foundation/requirements.md`
- `.reviewcompass/specs/runtime/requirements.md`
- `.reviewcompass/specs/evaluation/requirements.md`
- `.reviewcompass/specs/conformance-evaluation/requirements.md`
- `.reviewcompass/specs/analysis/requirements.md`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/self-improvement/requirements.md`
- `stages/in-progress/reopen-procedure-2026-06-09.yaml`

## レビューで判定してほしいこと

次の観点で、現在の requirements 判定が妥当かをレビューする。

1. direct impact の 4 feature について、既存 requirements の受け皿だけで足りるか。
2. indirect check の 3 feature について、requirements 追加修正なしでよいか。
3. intent の追加内容に対して、requirements.md に新しい Requirement または受入基準を追加すべき feature があるか。
4. 「既に requirements に 2026-06-08 の受け皿確認が書かれている」ことをもって、drafting 再実施完了とみなしてよいか。
5. 次段へ進む場合、requirements triad-review の結論として人間承認待ちにすべき未確定点はあるか。

## 出力期待

所見がある場合は、feature ごと、または判断ルールごとに、次のどれかを指摘する。

- `must_fix`: requirements triad-review 完了前に修正が必要。
- `should_fix`: 記録や根拠を補強した方がよい。
- `leave_as_is`: 現在の requirements 判定でよい。

特に重要なのは、direct impact feature である `foundation`、`runtime`、`evaluation`、`conformance-evaluation` に、requirements 本文の不足が残っていないかである。
