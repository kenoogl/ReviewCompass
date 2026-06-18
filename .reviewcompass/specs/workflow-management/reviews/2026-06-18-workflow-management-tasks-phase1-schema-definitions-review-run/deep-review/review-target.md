# deep-review：クラスタ A・C の深掘り

run_id: 2026-06-18-workflow-management-tasks-phase1-schema-definitions-review-run/deep-review
phase: tasks
gate: stages/tasks.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_tasks_triad_review_deep

## 1. 深掘りの目的

第1ラウンドで2つの問題クラスタが指摘された。

- **クラスタ C**：T-015 完了条件1に「D-003 §6 の優先順位順」が明記されていない
- **クラスタ A**：T-015 完了条件2の一部（verdict禁止・kind 14値enum・条件付き必須フィールド・$ref具体値）を確認するテストが存在しない

両クラスタの本質は「**テストの17件全通過が、要件（AC10・AC11）と設計（§5.1・§5.2）の充足を保証しない**」という点で共通している。

本 deep-review の目的は、この問題に対して **tasks.md の完了条件としてどのような記述が適切か** を独立して判断することである。

---

## 2. 制約

以下の制約は変更できない。

- **テスト17件は変更禁止**（TDD規律：テストは commit 済み、実装でテストを通過させる）
- T-015 の成果物（2つのスキーマファイル）は変更・追加できる
- tasks.md の完了条件の記述は修正可能

---

## 3. 問題の詳細

### 3.1 クラスタ C：順序要件の明記漏れ

**要件（AC10）**：
「`required_action.schema.json` の `enum` フィールドは D-003 §6 の優先順位順に 19 語彙を列挙する。この順が正本。」

**設計（design §5.1）**：
「`enum`：D-003 §6 の優先順位順に 19 値を列挙する（この順が正本）」

**現状の完了条件1**：
「`required_action.schema.json` が design §5.1 の設計（`$schema: https://json-schema.org/draft/2020-12/schema`・`$id: urn:reviewcompass:schema:required_action`・`type: string`・`enum` 19語彙）を満たす」

**現状のテストの挙動**：
- `test_all_expected_values_present`：EXPECTED_REQUIRED_ACTIONS（優先順位順の定数）の各語彙が enum に含まれることを確認する。ただし `assertIn` による存在確認のみで、配列の順序は確認しない
- 順序を確認するテストは存在しない
- → enum が `["completed", "run_workflow_stage", ...]`（逆順）でも17テストは全通過する

**問い**：
完了条件1の記述を修正するとしたら、どのような記述が AC10 の要件を漏れなく反映するか？テストで保証できない順序要件を完了条件にどう組み込むべきか？

---

### 3.2 クラスタ A：テストが未検証の完了条件2の項目

**要件（AC11）**：
「`next_action_response.schema.json` は：最上位に `verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の5フィールドを必須とし、`next_action` に `kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs` の10フィールドを必須とし、`verdict` フィールドを `next_action` 内で禁止し（`properties: { "verdict": false }`）、`next_action.required_action` が required_action スキーマの語彙に限定され（`$ref: "urn:reviewcompass:schema:required_action"`）、`kind` が14値のインライン `enum` で定義されている。」

**設計（design §5.2）**：
- 最上位5フィールド必須：`verdict`・`exit_code`・`next_action`・`reasons`・`current_state`
- `next_action` 10フィールド必須：`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`
- `properties: { "verdict": false }`：`next_action` 内での `verdict` 禁止
- `next_action.required_action`：`$ref: "urn:reviewcompass:schema:required_action"`（具体値）
- `kind`：14値インライン enum

**現状の完了条件2**：
「`next_action_response.schema.json` が design §5.2 の設計（最上位5フィールド必須・`next_action` 10フィールド必須・条件付き必須フィールド・`properties: { "verdict": false }`・`kind` 14値インライン enum・`$ref: "urn:reviewcompass:schema:required_action"`）を満たす」

**現状のテストの挙動**（テストが検証する項目と未検証の項目）：

| 完了条件2の要件 | テストによる保証 |
|---|---|
| 最上位5フィールド必須 | `test_required_top_level_fields` でカバー ✓ |
| `next_action` 10フィールド必須 | `test_next_action_required_fields` でカバー ✓ |
| `properties: { "verdict": false }`（verdict 禁止） | **テスト未検証** ✗ |
| `kind` 14値インライン enum | **テスト未検証** ✗ |
| 条件付き必須フィールド | **テスト未検証** ✗ |
| `$ref: "urn:reviewcompass:schema:required_action"`（具体値） | `test_required_action_ref_or_enum` は `$ref` の存在のみ確認（値は不問）→ **不完全** △ |

つまり、17テスト全通過のとき、`verdict` が `next_action` 内で禁止されていなくても、`kind` の値が `["foo", "bar", ...]` という14個の架空の値であっても、`$ref` が `"urn:something-else"` を指していても、完了条件3はクリアされる。

**現状の完了条件3**：
「`python3 -m pytest tests/tools/test_phase1_schema_definitions.py -v` の 17 テストが全て pass する（exit 0）」

**問い**：
テスト17件が完了条件2の全項目を保証しないという状況で、tasks.md の完了条件としてどのような記述が適切か？具体的には：

1. 完了条件3の表現を「17テスト全passは必要条件の確認に使うが、以下の項目は実装後に手動確認する」という形に弱めるべきか
2. 完了条件2の各項目に「テストで確認」か「手動確認」かを明示するべきか
3. または現在の書き方で問題なく、「テストで担保」という表現を設計意図（design §5 への参照）で読み替えられるか

---

## 4. 判断に必要な関連事項

- テスト17件の作成は commit 済み。テストを通過させることが T-015 の実装上の目標
- T-015 の「テスト要件」節に「テストの変更は禁止」と明記されている
- T-015 完了後、T-011（統合テスト）で回帰テストが実施される予定。T-011 で不足分のテストカバレッジを補う設計上の余地はある
- design §5.1・§5.2 への参照（「design §5.1 の設計を満たす」）が完了条件に含まれているため、要件全体は design 参照から間接的に読み取れる
