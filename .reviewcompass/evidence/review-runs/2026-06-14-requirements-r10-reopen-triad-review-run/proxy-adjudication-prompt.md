# proxy_model 裁定依頼：workflow-management requirements（Requirement 10）triad-review 所見

あなたは人の判断を代行する proxy_model である。操縦 LLM（Claude）とは別系統として、各所見の最終ラベルを決める。

## 文脈

- 対象は workflow-management requirements への新要件 Requirement 10（review-wave 横断確認の要約コマンド）の追加。reopen 分類 R-0。
- 現フェーズは requirements。requirements は「何を満たすか（受入基準）」を定め、スキーマ・パス・終了コード等の実装詳細は design 以降で確定してよい。ただし再現性・契約・fail-closed に関わる事項は requirements で担保すべき。
- ラベル定義：must-fix=要件として欠陥・不足があり修正必須／should-fix=改善として反映が望ましい／leave-as-is=対処不要（情報提供・軽微・design 委譲で足りる）。

## 所見一覧と操縦 LLM の提案ラベル

各 finding_id について final_label（must-fix/should-fix/leave-as-is）と一言の reason を返すこと。

1. claude-...-primary-001（WARN, C5）：実装形態「サブコマンドまたは helper」の優先順が無い。提案=leave-as-is（design で決定可）。
2. claude-...-primary-002（WARN, C1）：carry-forward 持ち越し所見の読み取り元（パス・形式）が未明記。提案=should-fix。
3. claude-...-primary-003（WARN, C1）：triage 件数の算出元フィールド・構造が未明記（Requirement 2 への暗黙参照）。提案=should-fix。
4. claude-...-primary-004（WARN, C2）：JSON スキーマ未定義、design 委譲の旨と責任所在が未明記。提案=should-fix。
5. claude-...-primary-005（INFO, C3）：「結論不能」の範囲（パース失敗・欠落等）が未具体化。提案=should-fix（fail-closed 詳細に寄与）。
6. claude-...-primary-006（INFO, C4）：「保存できる形式」が必須か可能かで曖昧。提案=should-fix。
7. claude-...-primary-007（INFO, C6）：Change Intent の R-1→R-0 経緯の根拠ドキュメント参照パス未記載。提案=should-fix。
8. gpt-5.5-...-adversarial-001（ERROR, C1）：集計元・集計定義が一部未規定で再現性に不足。提案=should-fix（要件で読み取り元を参照し、詳細定義は design 委譲を明記すれば足りる）。
9. gpt-5.5-...-adversarial-002（ERROR, C2）：JSON 安定スキーマ・必須フィールドが未要求。提案=should-fix（安定スキーマ要求を要件に入れ、キー詳細は design）。
10. gpt-5.5-...-adversarial-003（ERROR, C3）：不能時の機械可読シグナル（終了コード・JSON status）が未規定。提案=must-fix（fail-closed の契約に関わる）。
11. gpt-5.5-...-adversarial-004（WARN, C4）：読み取り専用責務と出力保存の境界が曖昧。提案=should-fix。

## 出力形式

次の YAML だけを返す（コードブロック可）。各 finding は連番（1〜11）で示してよい。

```yaml
decisions:
  - n: 1
    final_label: <must-fix|should-fix|leave-as-is>
    reason: <一言>
  ...（11 件）
```
