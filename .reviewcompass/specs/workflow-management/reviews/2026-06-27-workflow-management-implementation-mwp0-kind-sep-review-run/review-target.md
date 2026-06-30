# workflow-management implementation review — MWP-0: kind value separation

run_id: 2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run
criteria_id: wm-implementation-mwp0-kind-sep-2026-06-27
phase: implementation
stage: triad-review
variant: implementation_review_independent_3way

## Change Summary

MWP-0（next-json-kind-redesign）として、`next --json` の `kind` 値域を旧14値から7値へ整理し、コミット操作前確認用の3値（`commit_candidate`・`commit_mixing_risk`・`commit_unit_stale`）を `commit-preflight` サブコマンドへ移動した。

## Review Question

`next --json` サブコマンドが kind を7値のみに限定しているか、また `commit-preflight` サブコマンドが適切な kind 値を返しているかを、実装・スキーマ・テストを通じて独立して分析してほしい。あなたが気づいた問題・疑問を率直に示してほしい。

分析は上記1点に限定せず、kind 値分離に関して問題と判断したことは自由に指摘してよい。

## Scope / Out of Scope

**対象**：
- `_commit_preflight_next_action` 関数の実装（commit-preflight サブコマンドの kind 解決ロジック）
- `commit_preflight_response.schema.json`（3値 enum の定義）
- `next_action_response.schema.json` の kind enum（7値制限）
- `tests/tools/test_t020_kind_redesign.py` の `NextActionSchemaKindValueTests`・`CommitPreflightSchemaTests`・`NextActionKindBehaviorTests`・`CommitPreflightKindBehaviorTests` の各クラス
- 受入 12 との整合（T-020 完了条件1・2）

**対象外**：
- if/then 制約の完全性（別プロンプトで審査）
- reason vs reasons 責務分離（別プロンプトで審査）
- commit / push / spec.json 更新 / phase 完了 / 人間承認代行

---

## SOURCE MATERIAL: 要件（受入 12）

```text
【Requirement 2 受入 12（MWP-0 で新設）】
本機能は commit_candidate、commit_mixing_risk、commit_unit_stale の3種類の判定を next --json の
kind から除外し、commit-preflight サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」
ではなく「コミット操作の前確認」であり、next --json の kind は作業の現在地のみを示す7種類
（completed / in_progress / blocking_in_progress / verification_pending /
  reopen_in_progress / feature_definition_required / unknown）に限定する。
```

## SOURCE MATERIAL: タスク定義（T-020 完了条件1・2）

```text
【T-020 完了条件】
1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
```

---

## FILE: .reviewcompass/schema/next_action_response.schema.json（kind enum 部分）

```json
{
  "properties": {
    "next_action": {
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "in_progress",
            "blocking_in_progress",
            "verification_pending",
            "reopen_in_progress",
            "feature_definition_required",
            "completed",
            "unknown"
          ]
        }
      }
    }
  }
}
```

## FILE: .reviewcompass/schema/commit_preflight_response.schema.json（全文）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:commit_preflight_response",
  "$comment": "commit-preflight サブコマンドの応答スキーマ（MWP-0 T-020）",
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
          "enum": [
            "commit_candidate",
            "commit_mixing_risk",
            "commit_unit_stale"
          ]
        }
      }
    },
    "reasons": { "type": "array" },
    "current_state": { "type": "object" }
  }
}
```

## FILE: tools/check-workflow-action.py（`_commit_preflight_next_action` 関数の全コードパス）

```python
def _commit_preflight_next_action(cwd, in_progress_files):
    """commit 指示入口で見る現在の workflow action を副作用なしに組み立てる。"""
    if in_progress_files:
        return build_in_progress_next_action(cwd, in_progress_files[0])
        # 注：build_in_progress_next_action が返す kind の値域は別関数の実装に依存する

    verification_targets = list_post_write_verification_targets(cwd)
    if verification_targets:
        manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
        if manifest_state != "completed":
            return {
                "kind": "verification_pending",
                "verification_type": "post_write_verification",
                "required_action": "run_post_write_verification",
                "target_files": verification_targets,
                "reason": "post-write-verification 対象の未完了変更があります",
                "active_gate": None,
                "feature": None,
                "phase": None,
                "stage": None,
                "required_feature_scope": [],
                "blocked_by": None,
                "future_gates": [],
                "state_refs": {},
            }

    commit_unit_state, _ = validate_commit_unit_record(cwd)
    commit_unit_codes = commit_unit_state.get("codes") or []
    if commit_unit_state.get("exists") and "COMMIT_MIXING_RISK" in commit_unit_codes:
        return {
            "kind": "commit_mixing_risk",
            "required_action": "split_or_refresh_commit_unit",
            "active_gate": None,
            "feature": None,
            "phase": None,
            "stage": None,
            "required_feature_scope": [],
            "blocked_by": None,
            "future_gates": [],
            "state_refs": {},
        }
    if commit_unit_state.get("exists") and "STALE_COMMIT_UNIT" in commit_unit_codes:
        return {
            "kind": "commit_unit_stale",
            "required_action": "refresh_commit_unit",
            "active_gate": None,
            "feature": None,
            "phase": None,
            "stage": None,
            "required_feature_scope": [],
            "blocked_by": None,
            "future_gates": [],
            "state_refs": {},
        }

    specs, missing = load_all_feature_specs(cwd)
    if missing:
        return {
            "kind": "unknown",
            "required_action": "repair_workflow_state",
            "reason": "必要な spec.json が不足しています",
            "active_gate": None,
            "feature": None,
            "phase": None,
            "stage": None,
            "required_feature_scope": [],
            "blocked_by": None,
            "future_gates": [],
            "state_refs": {},
        }

    commit_stop_point = resolve_normal_workflow_commit_stop_point_action(cwd, specs)
    if commit_stop_point:
        return commit_stop_point

    return {
        "kind": "commit_candidate",
        "required_action": "prepare_commit",
        "reason": "commit 指示入口で遮断すべき active workflow unit はありません",
        "active_gate": None,
        "feature": None,
        "phase": None,
        "stage": None,
        "required_feature_scope": [],
        "blocked_by": None,
        "future_gates": [],
        "state_refs": {},
    }
```

## FILE: tests/tools/test_t020_kind_redesign.py（kind 値分離関連テストクラス）

```python
EXPECTED_NEXT_KIND_VALUES = frozenset({
    "in_progress", "blocking_in_progress", "verification_pending",
    "reopen_in_progress", "feature_definition_required", "completed", "unknown",
})
EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES = frozenset({
    "commit_candidate", "commit_mixing_risk", "commit_unit_stale",
})

class NextActionSchemaKindValueTests(unittest.TestCase):
    """next_action_response.schema.json の kind enum が7値に限定されていることを確認"""

    def test_schema_kind_enum_has_exactly_seven_values(self):
        """next_action_response.schema.json の kind enum は7値のみ"""
        # スキーマを読み込み、kind enum が EXPECTED_NEXT_KIND_VALUES と一致することを確認
        ...

    def test_schema_kind_enum_excludes_commit_related_values(self):
        """next_action_response.schema.json の kind enum にコミット関連値が含まれないこと"""
        # EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES のいずれも含まれないことを確認
        ...

    def test_schema_kind_enum_excludes_old_14_values(self):
        """旧 14 値の詳細 kind が next_action_response.schema.json に残っていないこと"""
        # old_values_to_remove リストの値が含まれないことを確認
        ...


class CommitPreflightSchemaTests(unittest.TestCase):
    """commit_preflight_response.schema.json の存在と kind 値域を確認"""

    def test_commit_preflight_schema_file_exists(self):
        """commit_preflight_response.schema.json が存在すること"""
        ...

    def test_commit_preflight_schema_kind_enum_has_exactly_three_values(self):
        """commit_preflight_response.schema.json の kind enum は3値のみ"""
        # kind enum が EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES と一致することを確認
        ...


class NextActionKindBehaviorTests(unittest.TestCase):
    """next --json が旧 commit 関連 kind を返さないことを確認"""

    def test_next_does_not_return_commit_unit_stale(self):
        """stale commit unit 状態で next --json が commit_unit_stale を返さないこと"""
        # commit unit を stale 状態にして next --json を実行し、kind != "commit_unit_stale" を確認
        ...

    def test_next_does_not_return_commit_mixing_risk(self):
        """commit unit 混入状態で next --json が commit_mixing_risk を返さないこと"""
        ...

    def test_next_returns_only_seven_kind_values(self):
        """next --json が返す kind は7値のいずれかであること"""
        # 空リポジトリで next --json を実行し、kind が EXPECTED_NEXT_KIND_VALUES に含まれることを確認
        ...


class CommitPreflightKindBehaviorTests(unittest.TestCase):
    """commit-preflight --json がコミット関連 kind を返すことを確認"""

    def test_commit_preflight_returns_commit_unit_stale_when_stale(self):
        """stale commit unit 状態で commit-preflight --json が commit_unit_stale を返すこと"""
        ...

    def test_commit_preflight_returns_commit_mixing_risk_when_mixing(self):
        """commit unit 混入状態で commit-preflight --json が commit_mixing_risk を返すこと"""
        ...

    def test_commit_preflight_kind_is_always_commit_related(self):
        """commit-preflight --json が返す kind は常にコミット関連3値のいずれかであること"""
        # 空リポジトリで commit-preflight --json を実行
        # 実装上の注意：テストは kind が None の場合はチェックをスキップしている
        # assertIn で許可している値：
        #   EXPECTED_COMMIT_PREFLIGHT_KIND_VALUES | {"post_write_verification", "unknown"}
        ...
```

## Output Contract

所見は次の形式で出力してほしい。

```yaml
findings:
  - id: <連番（F-001 など）>
    severity: must-fix | should-fix | leave-as-is
    target: <対象ファイル名または箇所>
    summary: <1行の説明（日本語）>
    detail: <具体的な問題の説明。要件・設計の原文を引用して根拠を示す>
    suggestion: <修正の方向性（あれば）>
```

所見がない場合は `findings: []` を返してほしい。
