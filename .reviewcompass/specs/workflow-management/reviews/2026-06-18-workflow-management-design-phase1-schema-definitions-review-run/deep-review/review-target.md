# 設計深掘りレビュー：next_action_response スキーマの3論点

phase: design
criteria: workflow_management_phase1_schema_definitions_deep_review
round_id: round-1

## 背景

ReviewCompass は `next --json` コマンドの出力を JSON Schema Draft 2020-12 で定義する。
対象ファイルは `.reviewcompass/schema/next_action_response.schema.json`。
以下に確定済みの設計を示す。

### 確定済みの構造

```
最上位 (required: verdict, exit_code, next_action, reasons, current_state)
  │
  └── next_action (object)
        required: kind, required_action, active_gate, feature, phase, stage,
                  required_feature_scope, blocked_by, future_gates, state_refs
        条件付き必須:
          repair_reasons（type: array, minItems: 1）← required_action="repair_workflow_state" のとき
          action_parameters（object）← required_action="run_maintenance" のとき
        additionalProperties: 指定しない（後方互換フィールド pending_gates 等を許容するため）
```

最上位の `additionalProperties` も指定しない（実装の段階的拡張を妨げないため）。

`required_action` フィールドには `$ref: "urn:reviewcompass:schema:required_action"` を用いており、
19語彙（`repair_workflow_state` ～ `completed`）の列挙（`enum`）が適用される。

---

## 論点 1：`verdict` フィールドの配置制約

### 現状の設計

要件（受入11）では「`verdict` は最上位にのみあり、`next_action` 内には含めない」と定められている。
しかし現在の設計では `next_action` の `additionalProperties` を指定していないため、
スキーマのレベルでは `next_action.verdict` を含む応答も合格してしまう。

### 問い

`verdict` フィールドが `next_action` 内に現れることをスキーマで禁止すべきか。
どのような方法が有効か。また、スキーマで禁止しない場合に生じる実質的なリスクはどの程度か。
設計方針として採るべき方向を、その根拠とともに分析してほしい。

---

## 論点 2：`additionalProperties` 未指定の理由の区別

### 現状の設計

スキーマは最上位と `next_action` の両方で `additionalProperties` を指定していないが、
その理由は異なる。

- **最上位**：将来の実装で新しいフィールドが追加されたときにスキーマ改訂なしに対応できるよう、
  段階的拡張を妨げないため。
- **`next_action`**：古いバージョンのツールが出力する `pending_gates`・`next_pending_gate`
  （旧来のフィールド名）を許容するため。後方互換を保ちながら将来は `future_gates`・`active_gate`
  を正本とする設計。

### 問い

この 2 つの理由の違いを設計文書に明記することは、どの程度の実用的価値があるか。
明記しない場合に生じる実際の問題（実装者の誤解・将来の誤改訂・他ツールとの連携上のリスクなど）
と、明記する場合のコストを比較して分析してほしい。

---

## 論点 3：`kind` フィールドの値域制約

### 現状の設計

`next_action.kind` は `type: string` のみで、値域は「実装定義」とされている。

一方、同じ `next_action` オブジェクト内の `required_action` は URN 参照で 19 語彙に制限されている。

### 参考情報：`kind` の取り得る値

`kind` は `WORKFLOW_NAVIGATION.md §2` の判定結果種別に対応し、現時点では以下の 14 値のみである。

```
resume_in_progress, reopen_in_progress, maintenance_in_progress,
reopen_classification_required, post_write_verification,
lightweight_self_check, post_write_policy_violation,
post_write_human_decision_required, stage, cross_feature_stage,
upstream_recheck, feature_definition_required, completed, unknown
```

`required_action`（19語彙）はスキーマ別ファイルで列挙しているが、
`kind`（14値）はスキーマで列挙していない。

### 問い

`kind` を現状のオープンな文字列のまま残すべきか、それとも 14 値の `enum` として定義すべきか。
定義するとすれば `required_action.schema.json` と同様にスキーマ別ファイルにすべきか、
`next_action_response.schema.json` 内にインラインで書くべきか。
また `kind` と `required_action` を異なる方法で扱う場合の設計上の整合性についても分析してほしい。

---

## 共通の前提

- スキーマは Python の `jsonschema` ライブラリ（Draft 2020-12 対応）で使用する。
- スキーマは ReviewCompass の `next --json` コマンドが正しい出力を生成しているかを確認するために使う。
- ReviewCompass 自体がまだ開発中のツールであり、`kind` の値が将来追加される可能性がある。
- テストファイル `tests/tools/test_phase1_schema_definitions.py` に 17 個の自動テストがあり、
  スキーマファイルの内容を検証する。

選択肢の枠を超えた分析を歓迎する。
