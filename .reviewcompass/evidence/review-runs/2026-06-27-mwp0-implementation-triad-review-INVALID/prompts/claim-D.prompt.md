# レビュー：Claim D（スキーマの if/then 制約と実装の整合性）

## 背景

MWP-0 の実装で `next_action_response.schema.json` に4件の if/then 制約を追加した。設計書（受入 11(6)）が要求する内容の一部は省略されている。また、そのうちの①制約は実装コードと矛盾している疑いがある。

---

## 設計書の要求（受入 11(6)）

```
① required_action = "commit_stop_point" のとき:
   active_gate=null, phase=null, stage=null, blocked_by.type="commit_stop_point"

② required_action = "run_reopen_pending_gate" のとき:
   active_gate 非null, phase/stage は active_gate と一致, blocked_by=null

③ required_action = "run_reopen_drafting" のとき:
   active_gate は stages/<phase>.yaml#drafting 形式,
   phase/stage はその drafting 単位と一致

⑤ required_action = "wait_for_human_decision" のとき:
   blocked_by.type で停止理由を区別
```

設計書 §5.3 の詳細フィールド表（line 511-512）：

> | `phase` | 現在のフェーズ（commit_stop_point 時は null） |
> | `stage` | 現在のステージ（commit_stop_point 時は null・受入 11(6) 参照） |

---

## 実装されたスキーマの if/then 制約（next_action_response.schema.json）

```json
// ①（抜粋）
{
  "$comment": "① commit_stop_point: active_gate/phase/stage はすべて null",
  "if": { "properties": { "required_action": { "const": "commit_stop_point" } }, "required": ["required_action"] },
  "then": {
    "properties": {
      "active_gate": { "type": "null" },
      "phase": { "type": "null" },
      "stage": { "type": "null" }
    }
  }
}

// ②（抜粋）
{
  "$comment": "② run_reopen_pending_gate: active_gate 非 null、blocked_by=null",
  "if": { "properties": { "required_action": { "const": "run_reopen_pending_gate" } }, "required": ["required_action"] },
  "then": {
    "properties": {
      "active_gate": { "type": "string" },
      "blocked_by": { "type": "null" }
    }
  }
}

// ③（抜粋）
{
  "$comment": "③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式",
  "if": { "properties": { "required_action": { "const": "run_reopen_drafting" } }, "required": ["required_action"] },
  "then": {
    "properties": {
      "active_gate": { "type": "string", "pattern": "^stages/.+\\.yaml#drafting$" }
    }
  }
}

// ⑤（抜粋）
{
  "$comment": "⑤ wait_for_human_decision: blocked_by 非 null かつ type フィールド必須",
  "if": { "properties": { "required_action": { "const": "wait_for_human_decision" } }, "required": ["required_action"] },
  "then": {
    "properties": {
      "blocked_by": { "type": "object", "required": ["type"], "properties": { "type": { "type": "string" } } }
    }
  }
}
```

---

## 省略されている制約

- **①**：`blocked_by.type = "commit_stop_point"` の検証がスキーマにない
- **②**：`phase`/`stage` が `active_gate` と一致するという制約がスキーマにない
- **③**：`phase`/`stage` が `active_gate` の drafting 単位と一致するという制約がスキーマにない

---

## スキーマ①制約と実装の矛盾（重要な事実）

スキーマ①は `required_action = "commit_stop_point"` のとき `phase=null, stage=null` を要求する。テストもこの制約を確認している：

```python
# tests/tools/test_t020_kind_redesign.py

def test_commit_stop_point_invalid_when_phase_nonnull(self):
    """① commit_stop_point: phase が非 null なら無効"""
    # phase="requirements"（非null）のデータがスキーマに対してinvalidになることを確認
    ...

def test_commit_stop_point_valid_when_all_null(self):
    """① commit_stop_point: active_gate/phase/stage がすべて null なら有効"""
    # blocked_by={"type": "commit_stop_point"} と phase=null でvalidになることを確認
    ...
```

しかし、通常ワークフローの commit_stop_point を処理する実装関数：

```python
def build_commit_stop_point_next_action(phase, dirty_paths):
    """通常 workflow の phase 終端 commit 停止点を返す"""
    return {
        "kind": "in_progress",
        "required_action": "commit_stop_point",
        "feature": None,
        "phase": phase,           # 例："requirements"（非null！設計では null）
        "stage": "approval",      # 非null！（設計では null）
        "reason": f"{phase}.approval 完了後の未コミット変更があるため、次 phase へ進む前に commit が必要です",
        "blocked_by": {
            "type": "workflow_phase_end",  # 設計では "commit_stop_point"
            "phase": phase,
            "stage": "approval",
            "kind": "phase_approval_complete",
            "dirty_paths": dirty_paths,
        },
    }
```

設計書・スキーマ・テストが示す期待値と、この実装が返す実際の値が3箇所（`phase`, `stage`, `blocked_by.type`）で一致しない。

一方、reopen 経由の commit_stop_point を処理する別の関数（`_reopen_commit_stop_point_blocked_by`）は `blocked_by.type="commit_stop_point"` を返す。つまり同じ `required_action=commit_stop_point` でも、通常ワークフロー経由とreopen経由で `blocked_by.type` が異なる。

ランタイムでスキーマ検証は実施されていないため、現状はエラーにならない。

---

## 審査してほしいこと

**D-1（省略①：blocked_by.type の制約）**

実装では `blocked_by.type` が通常ワークフロー経由で `"workflow_phase_end"`、reopen 経由で `"commit_stop_point"` の2種類になる。この状況でスキーマに `blocked_by.type="commit_stop_point"` を固定する制約を追加することは適切か。また、この不統一自体は問題か。

**D-2（省略②③：phase/stage と active_gate の一致）**

`phase`/`stage` が `active_gate` の内容と一致することを JSON Schema（JSON Schema Draft 2020-12）の標準機能で表現できるか。技術的な観点から判断してほしい。

**D-3（スキーマ①と `build_commit_stop_point_next_action` の矛盾）**

スキーマ①と設計書は `phase=null` を要求しているが、実装は `phase=<フェーズ名>` を返す。この矛盾をどう評価するか。「実装が設計書を誤った」「設計書が通常ワークフローの実態を考慮していなかった」「両者の前提が食い違っている」のどれに近いか。問題だとすれば何を修正すべきか。

自由に分析してよい。選択肢の枠を超えた指摘も歓迎する。

---

## 回答形式

D-1 / D-2 / D-3 それぞれについて：
- **所見**：問題あり / 問題なし / その他
- **根拠**
- **重大度**：must-fix / should-fix / leave-as-is
- **提案**（must-fix / should-fix の場合）
