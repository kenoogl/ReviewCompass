# proxy_model 裁定依頼：workflow-management design（Req 10 要約コマンド）triad-review 所見

あなたは人の判断を代行する proxy_model（操縦 Claude と別系統）。各所見の最終ラベルを決める。
文脈：design フェーズ（「どう実現するか」を確定。スキーマ・判定基準は design で確定すべき。実装コードの細部は implementation で可）。
ラベル：must-fix=設計に欠陥・不足で修正必須／should-fix=改善が望ましい／leave-as-is=対処不要。

所見（finding 番号と提案ラベル）：
1. claude-001 WARN：終了コード「既定 2」が next/spec-set/commit 規約と整合か未確認。提案=should-fix
2. claude-002 WARN：triage 新旧パスの重複排除ロジック未記載。提案=should-fix
3. claude-003 WARN：features[].phases の型・構造未定義。提案=should-fix（D1 スキーマの一部）
4. claude-004 WARN：status(ok/insufficient) 判定基準未記載。提案=should-fix
5. claude-005 INFO：--save/--out の出力先命名規則未記載。提案=should-fix
6. claude-006 INFO：carry-forward status≠resolved を全て未消化とする解釈の確認。提案=should-fix
7. gpt-001 ERROR：JSON 安定スキーマのネスト要素のキー・型が未定義。提案=must-fix（要件が design へ委譲したスキーマの確定）
8. gpt-002 ERROR：fail-closed 対象の欠落・解析不能入力の範囲が design 内で一意でない。提案=should-fix（範囲を列挙すれば足りる）
9. gpt-003 WARN：triage 集計の重複排除と draft/human_required 判定規則が曖昧。提案=should-fix
10. gpt-004 WARN：--save と --out の意味・出力先制約が未定義。提案=should-fix
11. gemini-001 WARN：保存先 _cross_feature/reviews/ が旧構造との指摘（承認済み要件受入5で決めた現行置き場）。提案=should-fix（要件どおりと明記）
12. gemini-002 INFO：tasks/implementation へ委譲する未確定事項の明示不足。提案=should-fix

出力は次の YAML のみ：
```yaml
decisions:
  - n: 1
    final_label: <must-fix|should-fix|leave-as-is>
    reason: <一言>
  ...（12 件）
```
