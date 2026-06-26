prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
triad-review

# Criteria
mwp0_tasks_triad_review

# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/evidence/review-runs/2026-06-27-mwp0-tasks-triad-review/target.md

# Target document
# レビュー対象：MWP-0（next-json-kind-redesign）workflow-management tasks 追記

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の既定（SESSION_WORKFLOW_GUIDE.md §3.3 a-3 正本。adversarial・judgment は操縦 LLM と別系列）

## 1. レビューの位置付け

reopen R-0（MWP-0 / next-json-kind-redesign）の tasks フェーズ triad-review。

MWP-0 は `next --json` の kind 値域を旧14値から7値へ整理し、コミット操作前確認の3値を `commit-preflight` サブコマンドへ移動した設計変更である。requirements と design は完了済み。本レビューでは MWP-0 が tasks.md に与えた**変更箇所のみ**を審査する。

- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`
- tasks 変更コミット：`d26deab5`（2026-06-27）

## 2. 上流材料（比較基準）

### 2.1 Requirement 2 受入 11（抜粋・関連部分のみ）

`next_action_response.schema.json` の `kind` は「`required_action` の分類子」であり、**値域は受入 12 で確定**する。

`next_action` の最低限の必須フィールドとして `kind`（文字列）が必須。`kind` の値域は受入 12 で別途確定する。

受入 11(6) — `required_action` 値ごとのフィールド制約：
- ①  `commit_stop_point` 時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`
- ②  `run_reopen_pending_gate` 時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`
- ③  `run_reopen_drafting` 時：`active_gate` は `stages/<phase>.yaml#drafting` 形式
- ④  `repair_workflow_state` 時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` 非空
- ⑤  `wait_for_human_decision` 時：`blocked_by.type` で停止理由を区別
- ⑥  `run_maintenance` 時：`action_parameters` に6サブフィールドを含める

**スキーマ上の表現方法は design で確定する（受入 11 はこれを machine-checkable な構造で表現することを要求する）。**

### 2.2 Requirement 2 受入 12（MWP-0 で新設・全文）

`commit_candidate`・`commit_mixing_risk`・`commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。

これらは「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であるため。

`next --json` の `kind` は作業の現在地を示す7種類に限定する：`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`

### 2.3 design.md §5.2〜§5.4（MWP-0 追記部分の抜粋）

**§5.2 `kind` フィールドの値域**

`kind` は `next_action_response.schema.json` 内にインライン `enum` として定義する。

MWP-0 反映：旧14値を7値へ整理した。

| 優先順位 | 値 | 意味 |
|---:|---|---|
| 1 | `reopen_in_progress` | 再開手続き中 |
| 2 | `blocking_in_progress` | 本線とは別の作業中 |
| 3 | `verification_pending` | 書き込み後の検証待ち |
| 4 | `in_progress` | 通常の作業中 |
| 5 | `feature_definition_required` | 初期設定未完了 |
| 6 | `completed` | 全作業完了 |
| 7 | `unknown` | 想定外のエラー状態 |

値の追加・変更はこの表と `next_action_response.schema.json` の `enum` 修正で完結する。**ただし kind の値種を増減する場合は受入 12 の改訂を要する。表と enum の修正は実装作業の手順であり、要件変更を免除しない。**

この正本の範囲は `kind` 値域の新旧対照にのみ適用され、`stage` 等の詳細フィールド制約の正本は本設計書（§5.3）と受入 11(6) である。

**§5.3 `kind` 詳細フィールド設計（MWP-0 反映・抜粋）**

廃止フィールド一覧：`resuming`・`completion_conditions`（→`return_conditions`に統一）・`action_parameters`（`blocking_in_progress` 詳細フィールドとしてのもの、`next_action` 直下の条件付き必須フィールドとしての `action_parameters` とは別物・存続）・その他。

**ただし廃止するのは `blocking_in_progress` 詳細フィールドの `completion_conditions` に限る。`next_action.action_parameters.completion_conditions`（受入 11(2) の `run_maintenance` 時必須サブフィールド）は別物であり廃止しない。**

**§5.4 `commit-preflight` サブコマンドの kind 設計（MWP-0 反映）**

受入 12 により、`commit_candidate`・`commit_mixing_risk`・`commit_unit_stale` の3値を `next --json` から除外し `commit-preflight` サブコマンドの出力にのみ含める。`commit-preflight` が返す `kind` の値域はこの3値とし、`next --json` はこれらを返さない。

## 3. 審査対象（tasks.md MWP-0 変更箇所）

### 3.1 T-015 完了条件の修正（MWP-0 対応）

**変更前**（reopen 前）：
> `kind` が **14値** インライン enum であること（手動確認）

**変更後**（本コミット後）：
> `kind` が **7値** インライン enum であること（手動確認、MWP-0 受入 12 反映：旧14値から整理済み）

さらに、完了条件3の手動確認リストも更新：
> kind **7値** の具体値（`completed`・`in_progress`・`blocking_in_progress`・`verification_pending`・`reopen_in_progress`・`feature_definition_required`・`unknown`）

### 3.2 T-020 新タスク（全文）

```
T-020：kind 7値スキーマ更新と commit-preflight サブコマンド（Req 2 受入 12、MWP-0 2026-06-27）

- 対応設計節：design.md §5.2 kind フィールドの値域・§5.4 commit-preflight サブコマンドの kind 設計
- 対応要件：Requirement 2 受入 12（MWP-0 で新設）
- 背景：MWP-0（next-json-kind-redesign）により next --json の kind 値域を旧14値から7値へ整理し、
  コミット操作前確認用の3値（commit_candidate・commit_mixing_risk・commit_unit_stale）を
  commit-preflight サブコマンドへ移動した。本タスクは MWP-0 の設計変更をスキーマ・実装・テストに反映する。
- 責務：
  1. next_action_response.schema.json の kind インライン enum を旧14値から7値へ更新する。
  2. commit-preflight サブコマンドの出力スキーマを定義する。返す kind は3値に限定する。
  3. tools/check-workflow-action.py の next --json 実装から旧3値の出力を除去し commit-preflight に集約する。
  4. design.alignment の先送り事項3件を tasks として記録し、実装時に対処する：
     (a) 受入 11(6)②〜⑥の required_action 値ごとのフィールド制約を if/then 構文で定義する
     (b) next_action 内の reason と最上位 reasons 配列の責務差を明確化する
     (c) design §5.3の「廃止」と Req 2 受入 12 の「廃止予定」の表現を統一する
- 前提タスク：T-015（next_action_response.schema.json の基盤）、T-004（check-workflow-action.py 本体）
- 成果物：
  - .reviewcompass/schema/next_action_response.schema.json（kind 7値更新版）
  - .reviewcompass/schema/commit_preflight_response.schema.json（新規）
  - tools/check-workflow-action.py（commit-preflight サブコマンド追加・next --json から3値除去）
- テスト要件（TDD）：
  - next --json が kind=commit_candidate・commit_mixing_risk・commit_unit_stale を返さないこと
  - commit-preflight が上記3値のみを返すこと
  - next_action_response.schema.json の kind enum が7値に限定されていること（既存テストの更新）
  - 受入 11(6)②〜⑥の if/then 制約の正常系・異常系テスト（先送り事項 (a)）
  - next_action.reason と最上位 reasons の責務分離が実装に反映されていること（先送り事項 (b)）
- 完了条件：
  1. next --json の kind 値域が7値に限定され、旧3値が出力されないことを pytest で確認できる。
  2. commit-preflight サブコマンドが3値の kind を返し、他の kind を返さないことを pytest で確認できる。
  3. スキーマの if/then 制約（先送り事項 (a)）の失敗テストが作成され、実装で通過する。
  4. WORKFLOW_NAVIGATION.md の next_drafting_gate 廃止に伴う記述を更新する（design §5.4 反映）。
```

### 3.3 要件追跡への追加（MWP-0 対応）

```
| Requirement 2 受入 11：next_action_response 応答スキーマ定義 | T-015（kind 7値は T-020 で更新） |
| Requirement 2 受入 12：kind 値域を7値に限定・commit-preflight 集約（MWP-0） | T-020 |
```

## 4. レビューの問い

上記の上流材料（Req 2 受入 11・受入 12、design §5.2〜§5.4）と、審査対象（T-015 修正・T-020・要件追跡）を独立して比較し、以下を分析してください。

**主問**：MWP-0 の上流意図（Req 2 受入 12 の kind 値域限定・commit-preflight 集約、design §5.2〜§5.4 の詳細設計）が、tasks.md の変更箇所へ**欠落・弱体化・逸脱・未根拠追加なく**引き継がれているか。

**具体的な確認観点**（ただしこれ以外の問題を発見した場合も報告してください）：

1. **T-020 の責務4（先送り事項）の扱いは適切か**：design.alignment で「tasks フェーズで対処」と明示された3件（受入 11(6)②〜⑥のスキーマ表現・reason vs reasons の責務差・廃止表現統一）が T-020 の責務として記録されているが、これらが「実装時に対処する」という扱いで tasks.md に収まっているか。先送り事項が「完了条件」や「テスト要件」に分散して記載されているが、整合しているか。

2. **`commit_preflight_response.schema.json` の追加は上流で根拠があるか**：T-020 は `.reviewcompass/schema/commit_preflight_response.schema.json` の新規作成を成果物として掲げている。Req 2 受入 12 や design §5.4 にこのスキーマファイル作成の明示的な指示はない。この成果物は上流の意図から導出できるか、それとも未根拠追加か。

3. **完了条件4（WORKFLOW_NAVIGATION.md 更新）の根拠**：T-020 の完了条件4に「WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述を更新する」とある。この更新は reopen 分類文書（`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）の「手引き改修：WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述改修が必要」に根拠があるが、その根拠が T-020 内に明記されていない。このトレーサビリティの欠落は問題か。

4. **T-015 の既存テスト変更禁止との矛盾**：T-015 の「テスト要件」節には「テストの変更は禁止」とある。一方 T-020 のテスト要件には「`next_action_response.schema.json` の `kind` enum が7値に限定されていること（**既存テストの更新**）」とある。T-020 の要求は T-015 の「テスト変更禁止」制約と矛盾しないか。

5. **先送り事項 (a)（受入 11(6)②〜⑥ の if/then）は T-015 と T-020 のどちらの責務か**：T-015 の完了条件2には「条件付き必須フィールドが `if/then` 構文で定義されていること：`repair_reasons`・`action_parameters`」と記載されている（受入 11(6)①⑥相当）。T-020 の先送り事項 (a) は「受入 11(6)②〜⑥」を扱う。しかし T-015 と T-020 の責務分担が文書上明確でなく、重複・漏れが生じていないか。

所見は重大度（`must-fix` / `should-fix` / `leave-as-is`）と対象箇所（T-015修正 / T-020責務 / T-020テスト要件 / T-020完了条件 / 要件追跡）を明示してください。

