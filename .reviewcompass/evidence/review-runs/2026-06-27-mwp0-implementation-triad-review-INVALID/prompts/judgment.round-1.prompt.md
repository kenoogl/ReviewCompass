# MWP-0 実装レビュー（判定役）

## あなたの役割

あなたは **判定役レビュアー（judgment reviewer）** です。主役と敵対役の2つのレビュー結果を参照し、各 claim について **最終的な判定** を下してください。

---

## 背景（概要）

ReviewCompass の `next --json` の `kind` 値を 14 値から 7 値に整理した実装（MWP-0 T-020）をレビューしている。要件は「`next --json` の `kind` は 7 種類に限定し、コミット前確認の3値は `commit-preflight` サブコマンドへ移動する」。

---

## 主役レビューの結果（要約）

| claim | 判定 | 重大度 |
|-------|------|--------|
| A：commit-preflight スキーマ違反 | 問題あり | should-fix |
| B：blocking_phase 値の不一致 | 問題あり | should-fix |
| C：verification_type の pending vs post_write_verification | 問題あり（設計書更新） | should-fix（設計書側） |
| D：if/then ①省略・②③省略 | ①should-fix、②③leave-as-is | 混在 |
| 追加）blocked_by.type の不統一 | should-fix | should-fix |

---

## 敵対役レビューの結果（要約）

| claim | 判定 | 重大度 |
|-------|------|--------|
| A：commit-preflight スキーマ違反 | 問題として成立しない | leave-as-is |
| B：blocking_phase 値の不一致 | 部分的に成立する | should-fix（低優先度） |
| C：verification_type | 問題として成立しない | 設計書更新のみ |
| D：①について新問題を発見・②③leave-as-is | ①should-fix | 混在 |

---

## 判定に必要な追加事実（両役レビュー後に判明した事項）

### 事実1：`build_commit_stop_point_next_action` の実装

```python
def build_commit_stop_point_next_action(phase, dirty_paths):
    """通常 workflow の phase 終端 commit 停止点を返す"""
    return {
        "kind": "in_progress",
        "required_action": "commit_stop_point",
        "feature": None,
        "phase": phase,           # 例："requirements"（非 null！）
        "stage": "approval",      # 非 null！
        ...
    }
```

### 事実2：スキーマの①制約

```json
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
```

### 事実3：設計書 §5.3 の規定

> ただし `commit_stop_point` を統合する場合、受入 11(6) の制約（`required_action = "commit_stop_point"` 時は `phase=null`・`stage=null`・`active_gate=null`・`blocked_by.type="commit_stop_point"`）に従い、`stage` フィールドの値は null になる（`stage: "commit_stop_point"` という文字列値は取らない）。

### 事実4：テストの内容

- `test_commit_stop_point_valid_when_all_null`：phase=null, stage=null のとき valid ✓
- `test_commit_stop_point_invalid_when_phase_nonnull`：phase が非 null のとき invalid ✓

テストはスキーマの制約を正しく検証しているが、`build_commit_stop_point_next_action` の **実際の出力**（非 null の phase）はこのテストで検証されていない。つまりスキーマと実装が互いを検証し合っておらず、矛盾が見逃されている。

### 事実5：WORKFLOW_DISCIPLINE_MAP.yaml でのスキーマ検証状況

実行時スキーマ検証は実施されていない（テストのみ）。したがって今のところランタイムエラーは発生しない。

---

## 判定してほしい最終クレームセット

### claim-A：commit-preflight の `verification_pending` 返却

主役：should-fix（スキーマ違反）
敵対役：leave-as-is（ランタイム検証なし・合理的な動作）

**判定のポイント：**
- スキーマ検証がランタイムで行われないなら、スキーマと実装の不整合は実害があるか
- 設計書 §5.4 が「commit-preflight が返す kind の値域はこの3値とし」と明記している点

### claim-B：blocking_phase の値の不一致

主役：should-fix
敵対役：should-fix（低優先度）・実害なし

**判定のポイント：**
- `blocking_phase` 値が機械処理されていないなら、実害はどの程度か
- 設計書が宣言した3値への統合は T-020 の実施義務だったか、別タスクへの先送り事項だったか

### claim-D'（新）：スキーマ①制約と `build_commit_stop_point_next_action` の実装矛盾

**これは敵対役レビューで発見された重大な新所見。**

`required_action = "commit_stop_point"` のとき：
- スキーマ（および設計書）は `phase=null, stage=null` を要求する
- 実装 `build_commit_stop_point_next_action` は `phase=<フェーズ名>, stage="approval"` を返す

設計書は明確に `phase=null` を要求しており、スキーマもそれに従っている。しかし実装は逆（`phase` に値を入れて文脈情報を伝える）。

**判定のポイント：**
- この矛盾は「実装が設計を誤った」か「設計が実装の実態を考慮していなかった」か
- `phase` に値を入れることでユーザーへの説明が改善されるのであれば、どちらを修正すべきか
- ランタイム検証がないため今すぐ問題は起きないが、将来スキーマ検証を導入したときの影響は

### claim-C：verification_type の `pending` vs `post_write_verification`（設計書更新）

主役：設計書更新
敵対役：設計書更新のみ・実装変更不要

主役・敵対役の方向が一致しているが、判定役として最終確認してほしい：
- 設計書 §5.3 の `"pending"` は誤記として確定してよいか
- `lightweight_self_check` の設計書への追記は必要か

---

## 期待する回答形式

各 claim について：
- **最終判定**：問題あり / 問題なし
- **重大度**：must-fix / should-fix / leave-as-is / 設計書更新のみ
- **修正の方向**（問題ありの場合）

最後に：
- **全体評価**：PASS（対処不要で次段に進める） / CONDITIONAL（指摘項目の対処後に進める）
- **優先順位付き対処リスト**（CONDITIONAL の場合）
