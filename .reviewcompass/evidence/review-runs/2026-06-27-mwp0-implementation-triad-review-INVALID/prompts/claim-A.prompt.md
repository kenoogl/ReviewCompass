# レビュー：Claim A（commit-preflight が返す kind 値と設計の不整合）

## 背景

ReviewCompass は `next --json` コマンドで「作業の現在地（kind）」を返す。MWP-0 では kind を 7 種類に整理し、コミット前確認の判定（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）を `commit-preflight` という専用サブコマンドへ移動した。

---

## 設計書の定義（design.md §5.4、MWP-0 反映）

設計書は次のように明示している：

> commit-preflight サブコマンドが返す `kind` の値域はこの 3 値とし、`next --json` は `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` を返さない。

（出典：design.md line 575）

§5.4 に列挙された3値：

| `kind` | 意味 |
|--------|------|
| `commit_candidate` | コミット可能状態 |
| `commit_mixing_risk` | 異なる作業単位が混在したコミット |
| `commit_unit_stale` | コミット単位の情報が古い |

---

## 実装の実態（check-workflow-action.py）

`commit-preflight` サブコマンドの next_action を組み立てる関数：

```python
def _commit_preflight_next_action(cwd, in_progress_files):
    if in_progress_files:
        return build_in_progress_next_action(cwd, in_progress_files[0])

    verification_targets = list_post_write_verification_targets(cwd)
    if verification_targets:
        manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
        if manifest_state != "completed":
            return {
                "kind": "verification_pending",           # ← 設計書の3値に含まれない
                "verification_type": "post_write_verification",
                "required_action": "run_post_write_verification",
                ...
            }

    commit_unit_state, _ = validate_commit_unit_record(cwd)
    commit_unit_codes = commit_unit_state.get("codes") or []
    if commit_unit_state.get("exists") and "COMMIT_MIXING_RISK" in commit_unit_codes:
        return { "kind": "commit_mixing_risk", ... }     # ← 設計書の3値
    if commit_unit_state.get("exists") and "STALE_COMMIT_UNIT" in commit_unit_codes:
        return { "kind": "commit_unit_stale", ... }      # ← 設計書の3値

    return { "kind": "commit_candidate", ... }           # ← 設計書の3値
```

`verification_pending` は `next --json`（`next_action_response.schema.json`）の kind enum には含まれる。しかし `commit_preflight_response.schema.json` の kind enum には含まれていない。

---

## スキーマの定義（commit_preflight_response.schema.json）

```json
{
  "properties": {
    "next_action": {
      "properties": {
        "kind": {
          "type": "string",
          "enum": ["commit_candidate", "commit_mixing_risk", "commit_unit_stale"]
        }
      }
    }
  }
}
```

---

## 実行環境での検証状況

- スキーマ検証はランタイムで実施されていない（`check-workflow-action.py` は jsonschema ライブラリを使用していない）
- スキーマはテストでのみ使用されている
- `test_commit_preflight_kind_is_always_commit_related`（tests/tools/test_t020_kind_redesign.py line 320）は `EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES | {"post_write_verification", "unknown"}` を許容しており、`"verification_pending"` は明示的に除外されている

---

## 審査してほしいこと

設計書は commit-preflight の kind を「この 3 値とし」と明示している。実装は post-write 検証待ちのとき `verification_pending` を返す。

1. この不整合を問題として扱うべきか。その根拠は何か
2. 問題だとすれば、どちらを修正すべきか。なぜか：
   - 実装を修正し、commit-preflight では `verification_pending` を返さないようにする
   - スキーマと設計書を修正し、commit-preflight も `verification_pending` を返せるようにする
   - 別の解決策があるか
3. テストがこのケースを検証していないことは独立した問題か、上記の不整合の結果か

自由に分析してよい。「A か B のどちらかを選べ」という意図はなく、選択肢の枠を超えた指摘も歓迎する。

---

## 回答形式

- **所見**：問題あり / 問題なし / その他
- **根拠**
- **重大度**：must-fix / should-fix / leave-as-is
- **提案**（must-fix / should-fix の場合）
