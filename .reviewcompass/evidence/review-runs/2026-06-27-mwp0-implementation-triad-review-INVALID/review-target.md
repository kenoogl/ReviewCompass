# Implementation Triad-Review: MWP-0（next --json kind 再設計）

## 背景

ReviewCompass は `next --json` コマンドで「作業の現在地（kind）」と「次にすべき操作（required_action）」を JSON で返す。

MWP-0（next-json-kind-redesign）は次の問題を解決した：
- 旧来の `kind` 値は 14 種類あり、「作業の現在地カテゴリ」「手続きサブステップ」「コミット前確認」が同一フィールドに混在していた
- `kind` を「作業の現在地カテゴリ」だけを示す **7 種類** に整理した
- コミット操作前確認の 3 値（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）は `commit-preflight` という専用サブコマンドへ移動した

今回の reopen 手続き第3過程として、**実装フェーズの成果物**を審査する。

## 実装の変更内容（T-020 の成果物）

### 変更対象ファイル

| ファイル | 変更内容 |
|--------|---------|
| `.reviewcompass/schema/next_action_response.schema.json` | `kind` の `enum` を 14 値から 7 値へ更新、if/then 制約 4 件追加 |
| `.reviewcompass/schema/commit_preflight_response.schema.json` | 新規作成（`kind` 3 値：commit_candidate / commit_mixing_risk / commit_unit_stale） |
| `tools/check-workflow-action.py` | 全 `build_*_next_action()` を新 7 値体系に統一、commit-preflight サブコマンド追加 |
| `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` | `next_action_kind`（9 値）と `next_action_verification_type`（4 値）を新体系に更新 |
| `tests/tools/test_t020_kind_redesign.py` | T-020 専用テスト（TDD 実装）。13 件のスキーマ if/then 制約テスト含む |
| `tests/tools/test_check_workflow_action.py` | 旧 kind 値テストを新 7 値体系に合わせて更新 |
| `tests/tools/test_effective_prompt_contract.py` | `next_action_kind`（9 値）+ `next_action_verification_type`（4 値）に更新 |
| `tests/tools/test_work_unit_cli.py` | `kind` 期待値を新体系に更新 |

### kind 値の新旧対照

| 旧 kind 値 | 新 kind 値 | 備考 |
|-----------|----------|------|
| `stage` / `cross_feature_stage` / `upstream_recheck` / `commit_stop_point` | `in_progress` | 統合 |
| `blocking_unit_required` / `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` / `parent_resume_pending` | `blocking_in_progress` | 統合。`blocking_phase` サブフィールドで区別 |
| `post_write_verification` / `post_write_policy_violation` / `post_write_human_decision_required` / `lightweight_self_check` | `verification_pending` | 統合。`verification_type` サブフィールドで区別 |
| `reopen_in_progress` / `reopen_classification_required` | `reopen_in_progress` | 保持 |
| `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` | — | **commit-preflight へ移動** |
| `feature_definition_required` | `feature_definition_required` | 保持 |
| `completed` | `completed` | 保持 |
| `unknown` | `unknown` | 保持 |
| `reopen_started` / `reopen_start_failed` | — | reopen-start コマンド固有のため catalog のみ維持 |

### スキーマ if/then 制約（受入 11(6)①②③⑤）

設計書が確定した 4 件の制約を `next_action_response.schema.json` に追加した：

1. **①** `required_action = "commit_stop_point"` のとき：`active_gate=null`, `phase=null`, `stage=null`
2. **②** `required_action = "run_reopen_pending_gate"` のとき：`active_gate` は非 null な文字列、`blocked_by=null`
3. **③** `required_action = "run_reopen_drafting"` のとき：`active_gate` は `stages/<phase>.yaml#drafting` 形式
4. **⑤** `required_action = "wait_for_human_decision"` のとき：`blocked_by` は非 null なオブジェクトかつ `type` フィールド必須

## 審査してほしい判断ポイント

以下の claim（判断対象）を独立して分析してほしい。

### claim-A：kind 7 値化の実装完全性（Requirement 2 受入 12 の充足）

`next --json` の `kind` が正確に 7 種類に限定されており、旧 3 値（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）が返されないことを確認する。

**実装の証拠：**
- `next_action_response.schema.json` の `kind` enum が 7 値であること
- `commit_preflight_response.schema.json` が 3 値を持つこと
- `tests/tools/test_t020_kind_redesign.py` の `KindEnumSchemaTests` クラスが種別を正確に検証していること

**審査ポイント：**
1. スキーマ `enum` の 7 値が設計書 §5.2 の値域表と完全に一致するか
2. `next --json` の実装コードに旧 3 値（commit_candidate / commit_mixing_risk / commit_unit_stale）の出力パスが残っていないか
3. `commit-preflight` サブコマンドのテストカバレッジは十分か

### claim-B：blocking_phase サブフィールドの値が設計と一致するか

設計書 §5.3「`blocking_in_progress` の追加フィールド」は `blocking_phase` の値を 3 種類と定義している。

| 設計書の値 | 意味 | 統合された旧 kind |
|-----------|------|----------------|
| `required` | blocking 作業の開始が必要 | `blocking_unit_required` |
| `in_progress` | blocking 作業中 | `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` |
| `return_pending` | blocking 完了・親への復帰待ち | `parent_resume_pending` |

**実装の実際の値（`check-workflow-action.py` から）：**
- `"blocking_phase": "blocking_unit_in_progress"` （設計では `in_progress` のはず）
- `"blocking_phase": "parent_resume_pending"` （設計では `return_pending` のはず）
- `"blocking_phase": "blocking_unit_required"` （設計では `required` のはず）
- `"blocking_phase": "maintenance_in_progress"` （設計では `in_progress` のはず）
- `"blocking_phase": "resume_in_progress"` （設計では `in_progress` のはず）

**審査ポイント：**
1. この不一致は「設計書の意図を実装が誤った」のか、「設計書が変更されたが実装が古いまま残った」のか、「意図的に旧値を維持した」のかを判断してほしい
2. この不一致が実際の動作やテストに影響しているか（テストで `blocking_phase` 値を検証しているか確認）
3. must-fix / should-fix / leave-as-is のどれに該当するか

### claim-C：verification_type サブフィールドの値が設計と一致するか

設計書 §5.3「`verification_pending` の追加フィールド」は `verification_type` を 3 種類と定義している。

| 設計書の値 | 意味 |
|-----------|------|
| `pending` | 検証待ち・未着手 |
| `policy_violation` | 禁止変更が混入 |
| `human_decision_required` | 未解決の重大所見あり |

**実装の実際の値（`check-workflow-action.py` から）：**
- `"verification_type": "post_write_verification"` （設計では `pending` のはず）
- `"verification_type": "policy_violation"` ✓
- `"verification_type": "human_decision_required"` ✓
- `"verification_type": "lightweight_self_check"` （設計の表に記載なし）

**さらに `WORKFLOW_DISCIPLINE_MAP.yaml` の `next_action_verification_type` グループは：**
- `post_write_verification`（設計では `pending`）
- `policy_violation` ✓
- `human_decision_required` ✓
- `lightweight_self_check`（設計の表に記載なし）

**審査ポイント：**
1. `post_write_verification` vs `pending` の不一致：設計書の値 `pending` を使うべきか、実装の値 `post_write_verification` が実質的に等価で問題ないか
2. `lightweight_self_check` は設計書に記載がないが、実装とカタログに存在する。これはT-020のスコープ外で意図的に残したものか、設計の漏れか
3. `test_effective_prompt_contract.py` では `next_action_verification_type` の期待値として `"post_write_verification"` を使っているが、これは設計書の `pending` と一致しない。これは問題か

### claim-D：if/then 制約の実装精度（受入 11(6)①②③⑤）

4 件の if/then 制約が設計書 §5.2 の仕様と正確に一致しているかを確認する。

**実装の if/then 制約（schema.json から）：**

```
① commit_stop_point: active_gate=null, phase=null, stage=null
② run_reopen_pending_gate: active_gate=string（非null）, blocked_by=null
③ run_reopen_drafting: active_gate は "stages/...yaml#drafting" パターン
⑤ wait_for_human_decision: blocked_by=object かつ type フィールド必須
```

**設計書 §5.2 (受入 11(6)) の仕様：**
```
① commit_stop_point: active_gate=null, phase=null, stage=null, blocked_by.type="commit_stop_point"
② run_reopen_pending_gate: active_gate 非null, phase/stage は active_gate と一致, blocked_by=null
③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式, phase/stage はその drafting 単位と一致
⑤ wait_for_human_decision: blocked_by.type で停止理由を区別
```

**審査ポイント：**
1. ①の制約：設計書は `blocked_by.type="commit_stop_point"` も要求しているが、スキーマに含まれていない。これは欠落か省略か
2. ②の制約：設計書は `phase/stage は active_gate と一致` を要求しているが、スキーマに含まれていない。省略は適切か
3. ③の制約：`phase/stage はその drafting 単位と一致` がスキーマに含まれていない。省略は適切か
4. これらの省略が `acceptance_criteria` の受入条件を満たしているか

## 上流目的の確認項目

上流の要件（受入 12）が「作業の現在地を示す 7 種類に限定」と明確に述べており、この目的を実装が達成しているかを縦方向監査の視点で確認してほしい。

- kind の 7 値化は `next --json` の出力契約を変えたため、このコマンドを利用しているコンシューマ（WORKFLOW_NAVIGATION.md、手引き文書、テスト）が正しく更新されているか
- 旧 kind 値を参照する箇所が設計書・テスト・手引きのどこかに残っていないか

## 参考：テスト実行結果

実装後のテスト結果：`python3 -m pytest tests/tools/ -q` → **715 件全通過**

専用テストクラス `test_t020_kind_redesign.py` の内訳：
- `KindEnumSchemaTests`（6 件）：kind enum の値域・旧値排除
- `CommitPreflightSchemaTests`（7 件）：commit-preflight の kind 3 値
- `SchemaIfThenConstraintTests`（13 件）：if/then 制約①②③⑤
