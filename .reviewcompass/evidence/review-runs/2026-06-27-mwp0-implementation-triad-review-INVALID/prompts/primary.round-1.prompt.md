# MWP-0 実装レビュー（主役）

## あなたの役割

あなたは **主役レビュアー（primary reviewer）** です。以下に示す実装成果物を独立して分析してください。

---

## 背景

ReviewCompass というワークフロー管理ツールがある。このツールは `next --json` コマンドで「作業の現在地（kind）」と「次にすべき操作（required_action）」を JSON で返す。

**今回の変更（MWP-0）の動機：**
旧来の `kind` 値は 14 種類あり、「作業の現在地カテゴリ」「手続きの内部サブステップ」「コミット操作の前確認」が同一フィールドに混在していた。`kind` を「作業の現在地カテゴリ」のみを示す **7 種類** に整理し、コミット操作前確認の 3 値（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）を `commit-preflight` という専用サブコマンドへ移動した。

**要件（受入 12）：**
> 本機能は `commit_candidate`、`commit_mixing_risk`、`commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。`next --json` の `kind` は作業の現在地のみを示す7種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。

---

## 実装成果物

### スキーマ 1：next_action_response.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action", "reasons", "current_state"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "type": "object",
      "required": ["kind", "required_action", "active_gate", "feature", "phase", "stage",
                   "required_feature_scope", "blocked_by", "future_gates", "state_refs"],
      "properties": {
        "verdict": false,
        "kind": {
          "type": "string",
          "enum": ["in_progress", "blocking_in_progress", "verification_pending",
                   "reopen_in_progress", "feature_definition_required", "completed", "unknown"]
        },
        "required_action": { "$ref": "urn:reviewcompass:schema:required_action" },
        "active_gate": { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "feature":    { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "phase":      { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "stage":      { "oneOf": [{ "type": "string" }, { "type": "null" }] },
        "required_feature_scope": { "type": "array", "items": { "type": "string" } },
        "blocked_by": { "oneOf": [{ "type": "object" }, { "type": "null" }] },
        "future_gates": { "type": "array" },
        "state_refs": { "type": "object" }
      },
      "allOf": [
        {
          "if": { "properties": { "required_action": { "const": "repair_workflow_state" } }, "required": ["required_action"] },
          "then": { "required": ["repair_reasons"], "properties": { "repair_reasons": { "type": "array", "minItems": 1 } } }
        },
        {
          "if": { "properties": { "required_action": { "const": "run_maintenance" } }, "required": ["required_action"] },
          "then": { "required": ["action_parameters"], "properties": { "action_parameters": {
            "type": "object",
            "required": ["maintenance_action", "allowed_scope", "allowed_files",
                         "completion_conditions", "active_stack_frame_id", "parent_frame_id"]
          }}}
        },
        {
          "$comment": "① commit_stop_point: active_gate/phase/stage はすべて null",
          "if": { "properties": { "required_action": { "const": "commit_stop_point" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "null" }, "phase": { "type": "null" }, "stage": { "type": "null" } } }
        },
        {
          "$comment": "② run_reopen_pending_gate: active_gate 非 null、blocked_by=null",
          "if": { "properties": { "required_action": { "const": "run_reopen_pending_gate" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "string" }, "blocked_by": { "type": "null" } } }
        },
        {
          "$comment": "③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式",
          "if": { "properties": { "required_action": { "const": "run_reopen_drafting" } }, "required": ["required_action"] },
          "then": { "properties": { "active_gate": { "type": "string", "pattern": "^stages/.+\\.yaml#drafting$" } } }
        },
        {
          "$comment": "⑤ wait_for_human_decision: blocked_by 非 null かつ type フィールド必須",
          "if": { "properties": { "required_action": { "const": "wait_for_human_decision" } }, "required": ["required_action"] },
          "then": { "properties": { "blocked_by": { "type": "object", "required": ["type"], "properties": { "type": { "type": "string" } } } } }
        }
      ]
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```

### スキーマ 2：commit_preflight_response.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:commit_preflight_response",
  "$comment": "commit-preflight サブコマンドの応答スキーマ",
  "type": "object",
  "required": ["verdict", "exit_code", "next_action"],
  "properties": {
    "verdict": { "type": "string" },
    "exit_code": { "type": "integer" },
    "next_action": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": ["commit_candidate", "commit_mixing_risk", "commit_unit_stale"]
        }
      }
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```

### 実装コード抜粋（check-workflow-action.py）

**commit-preflight の next_action 組み立て関数：**

```python
def _commit_preflight_next_action(cwd, in_progress_files):
    """commit 指示入口で見る現在の workflow action を副作用なしに組み立てる。"""
    if in_progress_files:
        return build_in_progress_next_action(cwd, in_progress_files[0])

    verification_targets = list_post_write_verification_targets(cwd)
    if verification_targets:
        manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
        if manifest_state != "completed":
            action = {
                "kind": "verification_pending",           # ← 7値の新 kind を使用
                "verification_type": "post_write_verification",
                "required_action": "run_post_write_verification",
                ...
            }
            return action

    commit_unit_state, _ = validate_commit_unit_record(cwd)
    commit_unit_codes = commit_unit_state.get("codes") or []
    if commit_unit_state.get("exists") and "COMMIT_MIXING_RISK" in commit_unit_codes:
        return {
            "kind": "commit_mixing_risk",               # ← commit-preflight 専用 kind
            ...
        }
    if commit_unit_state.get("exists") and "STALE_COMMIT_UNIT" in commit_unit_codes:
        return {
            "kind": "commit_unit_stale",                # ← commit-preflight 専用 kind
            ...
        }

    return {
        "kind": "commit_candidate",                     # ← commit-preflight 専用 kind
        ...
    }
```

**blocking_in_progress の blocking_phase 値（3か所）：**

```python
# 作業中の blocking unit がある場合
next_action = {
    "kind": "blocking_in_progress",
    "blocking_phase": "blocking_unit_in_progress",  # ← 旧値（設計では "in_progress"）
    ...
}

# 親への復帰待ちの場合
next_action = {
    "kind": "blocking_in_progress",
    "blocking_phase": "parent_resume_pending",      # ← 旧値（設計では "return_pending"）
    ...
}

# 新しい blocking unit の開始が必要な場合
next_action = {
    "kind": "blocking_in_progress",
    "blocking_phase": "blocking_unit_required",     # ← 旧値（設計では "required"）
    ...
}

# maintenance 中の場合
next_action = {
    "kind": "blocking_in_progress",
    "blocking_phase": "maintenance_in_progress",    # ← 旧値（設計では "in_progress"）
    ...
}
```

### 設計書の定義（design.md §5.3 から）

**blocking_phase の設計意図：**

| 設計書の値 | 意味 | 統合された旧 kind |
|-----------|------|----------------|
| `required` | blocking 作業の開始が必要 | `blocking_unit_required` |
| `in_progress` | blocking 作業中 | `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` |
| `return_pending` | blocking 完了・親への復帰待ち | `parent_resume_pending` |

**verification_type の設計意図（§5.3）：**

| 設計書の値 | 意味 | 旧 kind |
|-----------|------|--------|
| `pending` | 検証待ち・未着手 | `post_write_verification` |
| `policy_violation` | 禁止変更が混入 | `post_write_policy_violation` |
| `human_decision_required` | 未解決の重大所見あり | `post_write_human_decision_required` |

**if/then 制約の設計仕様（受入 11(6)）：**

① `commit_stop_point` のとき：`active_gate=null`, `phase=null`, `stage=null`, **`blocked_by.type="commit_stop_point"`**
② `run_reopen_pending_gate` のとき：`active_gate` 非 null、**`phase`/`stage` は `active_gate` と一致**、`blocked_by=null`
③ `run_reopen_drafting` のとき：`active_gate` は `stages/<phase>.yaml#drafting` 形式、**`phase`/`stage` はその drafting 単位と一致**
⑤ `wait_for_human_decision` のとき：`blocked_by.type` で停止理由を区別

---

## 審査してほしい判断ポイント

以下の claim（判断対象）を **独立して** 分析してください。特定の結論に誘導しているわけではありません。

### claim-A：commit-preflight スキーマと実装の整合性

`_commit_preflight_next_action()` 関数は post-write 検証待ちのとき `kind: "verification_pending"` を返す。しかし `commit_preflight_response.schema.json` の `kind` enum には `"verification_pending"` が含まれておらず、3値（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）のみである。

また `next --json` の `next_action_response.schema.json` には `"verification_pending"` が含まれている。

**分析してほしいこと：**
1. この不整合は実際に問題を引き起こすか（スキーマ検証が行われているか、テストがこのケースを確認しているか）
2. `commit-preflight` が `verification_pending` を返すことは設計の意図どおりか、それとも3値の外に出た逸脱か
3. 修正が必要な場合、どちらを修正すべきか：スキーマに `verification_pending` を追加するか、実装で `commit-preflight` から `verification_pending` を排除するか

### claim-B：blocking_phase サブフィールドの値の不一致

設計書は `blocking_phase` を3値（`required` / `in_progress` / `return_pending`）と定義しているが、実装は旧値（`blocking_unit_required` / `blocking_unit_in_progress` / `parent_resume_pending` / `maintenance_in_progress` / `resume_in_progress`）を使っている。テストはこの値を検証していない。

**分析してほしいこと：**
1. この不一致は機能的な問題（ランタイムエラー・テスト失敗・ドキュメントの誤案内）を引き起こすか
2. 設計書の3値を使うよう実装を変更すべきか、それとも設計書を修正すべきか、またはそのままでよいか
3. `blocking_phase` 値が公開インターフェイスに含まれる場合（例：WORKFLOW_NAVIGATION.md が参照している場合）、どの程度の影響があるか

### claim-C：verification_type の `pending` vs `post_write_verification`

設計書は `verification_type: "pending"` と定義しているが、実装は `verification_type: "post_write_verification"` を使っている。さらに `lightweight_self_check` という値が実装とカタログ（WORKFLOW_DISCIPLINE_MAP.yaml）に存在するが、設計書の表には記載がない。

**分析してほしいこと：**
1. `"pending"` と `"post_write_verification"` の不一致は、設計書の意図に対する実装の誤りか、意図的な判断か
2. `lightweight_self_check` が設計書の表に記載されていないのは、設計の漏れか、意図的な省略か
3. これらの不一致が実際の動作（tests / WORKFLOW_NAVIGATION.md での参照 / effective prompt の解決）に影響するか

### claim-D：if/then 制約の不完全実装

スキーマに追加された if/then 制約は、設計書が要求する内容の一部を省略している：

- **① の省略**：設計は `blocked_by.type = "commit_stop_point"` を要求しているが、実装にない
- **②③ の省略**：設計は `phase`/`stage` が `active_gate` と一致することを要求しているが、実装にない

**分析してほしいこと：**
1. これらの省略は意図的（JSON Schema では表現できない制約を省いた）か、見落としか
2. `blocked_by.type = "commit_stop_point"` は JSON Schema の `if/then` で表現可能か
3. `phase`/`stage` と `active_gate` の一致制約は JSON Schema で表現可能か、不可能ならどのような代替手段があるか
4. これらの省略が実際の安全性（誤った JSON を通過させるリスク）に与える影響はどの程度か

---

## 期待する回答形式

各 claim について：
- **所見の有無**：問題あり / 問題なし / 情報不足で判断できない
- **根拠**：判断の根拠を具体的に示す（コードの行・スキーマの制約・設計書との対照）
- **重大度**：must-fix / should-fix / leave-as-is / 情報不足で判断できない
- **提案**（must-fix / should-fix の場合）：具体的な修正案

また、上記 claim 以外に気づいた問題があれば、別途記載してください。
