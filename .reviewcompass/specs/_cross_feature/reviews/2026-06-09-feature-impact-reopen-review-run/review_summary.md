# Feature Impact Reopen Review Summary

## 実行概要

- review-run: `2026-06-09-feature-impact-reopen-review-run`
- phase: `feature_partitioning_reopen_review`
- criteria: `feature_impact_reopen_decision_scope`
- target: `target.md`
- primary: `claude-sonnet-4-6`
- adversarial: `gpt-5.4`
- judgment: `gemini-3.1-pro-preview`

## 3役の一致点

3役とも、現在の「既存 7 feature すべてを reopen 対象にする」仮判断は、そのまま確定するには粒度が粗いと判定した。

共通所見は次の 4 点。

1. 全 7 feature を一律 reopen とする前に、直接影響・間接影響・影響なしを feature ごとに分ける必要がある。
2. 直接影響が強い候補は `foundation`、`runtime`、`evaluation`。
3. `analysis`、`workflow-management`、`self-improvement`、`conformance-evaluation` は間接確認または波及確認で足りる可能性がある。
4. `reopen_trigger: N-0` はツール出力としては確認できるが、定義・選定根拠・参照先が target に不足している。

## 判定

現在の仮判断は、そのまま `reopen-start` に進めない。

`must-fix` 相当:

- feature ごとの impact 区分を明示する。
- `N-0` の定義または選定根拠を記録する。

`should-fix` 相当:

- `new_feature_decision: no_new_feature` は概ね妥当だが、runtime / foundation の変更規模が feature 分割基準を超える場合は再検討する、という留保を記録する。
- 「既存 feature に受け皿がある場合、該当 feature を reopen 候補にする」という workflow 共通規則の参照を記録する。

## 次処理

feature impact 判定を次の形に修正してから、人間承認を受ける。

| Feature | 暫定区分 | 次に必要な処理 |
| --- | --- | --- |
| foundation | direct impact | reopen 対象候補として requirements 以降を確認 |
| runtime | direct impact | reopen 対象候補として requirements 以降を確認 |
| evaluation | direct impact | reopen 対象候補として requirements 以降を確認 |
| analysis | indirect check | direct 3 feature の判断結果に応じて波及確認 |
| workflow-management | indirect check | workflow 手続き側の整合確認 |
| self-improvement | indirect check | 改善入力・履歴モデルへの波及確認 |
| conformance-evaluation | indirect check | 仕様・実装乖離検査への波及確認 |

新 feature は現時点では不要。ただし direct impact feature の再確認で既存責務を超えると判明した場合は、feature-partitioning に戻して再判定する。
