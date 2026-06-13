# proxy_model 裁定依頼：workflow-management tasks（T-012）triad-review 所見（ERROR なし）
あなたは proxy_model（操縦 Claude と別系統）。tasks フェーズ（TDD タスク化）。ラベル：must-fix/should-fix/leave-as-is。
所見と提案：
1. gpt WARN-001：T-012 テストに carry-forward/in-progress の欠落・解析不能の扱いが未明示。提案=should-fix
2. gpt WARN-002：JSON 安定スキーマの固定検証がテスト要件として弱い。提案=should-fix
3. gpt INFO-003：要件追跡の双方向が target 単体で確認不可（tasks.md には記載済み）。提案=leave-as-is
4. gemini WARN-001：テスト(4) に解析不能→exit2 が未含。提案=should-fix
5. gemini INFO-002：--out/--save 保存正常系テスト未明記。提案=should-fix
6. claude INFO-001：前提に既存関数依存の言及なし。提案=leave-as-is（設計で再利用明記済み）
7. claude INFO-002：テスト(6) と design §2 の対応が tasks 上で省略。提案=leave-as-is（design 参照で足る）
8. claude INFO-003：要件追跡が target に引用されず単体検証不可。提案=leave-as-is（target の体裁、tasks 欠陥でない）
出力は YAML のみ：
```yaml
decisions:
  - n: 1
    final_label: <...>
    reason: <一言>
```（8 件）
