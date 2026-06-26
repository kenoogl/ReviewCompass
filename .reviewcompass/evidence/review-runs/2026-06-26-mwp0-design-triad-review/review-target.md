# Design Triad-Review: MWP-0（next --json kind 再設計）

## 背景

ReviewCompass は `next --json` コマンドでワークフロー作業の現在地と次の操作を JSON で返すツールである。今回の変更（MWP-0）は `kind` フィールドの値域を整理する。

**変更の動機：**
現状の `kind` 値は 41 種類あり、「作業の現在地カテゴリ」「手続きの内部サブステップ」「コミット操作の前確認」が同一フィールドに混在している。この混在によって機械的な次アクション決定が困難になっている。

**変更の内容：**
1. `next --json` の `kind` 値域を 7 種類に整理する
2. `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の 3 種類を `next --json` から除外し、`commit-preflight` サブコマンドの出力へ移動する

今回の審査は、`design.md` に追記・更新した §5.2〜5.4 の内容が、確定した要件（requirements.md 受入 11・受入 12）および設計メモ（`docs/notes/2026-06-26-next-json-kind-redesign.md`）と整合しているかを確認する。

---

## 確定要件（requirements.md より抜粋）

**受入 11（Requirement 2 の一部）：**
```
11. 本機能は `next --json` の目標応答スキーマを
`.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。

（1）最上位の必須フィールドは `verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の 5 つ。
（2）`next_action` の最低限の必須フィールドは `kind`（文字列・値域は受入 12 で確定）・
`required_action`・`active_gate`・`feature`・`phase`・`stage`・
`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs` の 10 フィールド。
これに加え、
- `repair_reasons`（配列）は `required_action = "repair_workflow_state"` のとき必須（非空配列）
- `action_parameters`（オブジェクト）は `required_action = "run_maintenance"` のとき必須。
  6 フィールド（`maintenance_action`・`allowed_scope`・`allowed_files`・`completion_conditions`・
  `active_stack_frame_id`・`parent_frame_id`）はすべて required とする。
  追加フィールドの許可・禁止は design で確定する。
（3）`feature` は「単一フィーチャー名」・`"all_features"`・null の 3 種類に限る。
（4）進行中の作業単位がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null。
（5）後方互換のため `pending_gates`・`next_pending_gate` をオプションフィールドとして定義。
    正本フィールドは `future_gates`・`active_gate`。
（6）`required_action` 値ごとのフィールド制約（D-003 §4.2 の確定内容）：
    ① commit_stop_point: active_gate=null, phase=null, stage=null, blocked_by.type="commit_stop_point"
    ② run_reopen_pending_gate: active_gate 非 null
    ③ run_reopen_drafting: active_gate は stages/<phase>.yaml#drafting 形式
    ④ repair_workflow_state: active_gate=null, repair_reasons に理由を含める
    ⑤ wait_for_human_decision: blocked_by.type で停止理由を区別
    ⑥ run_maintenance: action_parameters に上記 6 フィールドを含める
```

**受入 12（Requirement 2 に新設）：**
```
12. 本機能は `commit_candidate`、`commit_mixing_risk`、`commit_unit_stale` の 3 種類の判定を
`next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。
これらの判定は「コミット操作の前確認」であり「作業の現在地カテゴリ」ではない。
`next --json` の `kind` は作業の現在地のみを示す 7 種類
（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` /
`reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。
設計の詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする。
```

---

## 確定設計メモ（docs/notes/2026-06-26-next-json-kind-redesign.md より抜粋）

**`blocking_in_progress` の廃止フィールド（設計メモ line 97 の確定内容）：**
```
廃止するフィールド：
resuming（blocking_phase 値）/ completion_conditions（return_conditions に統一）/
process_id（blocking_phase で代替）/ maintenance_action（required_action で代替）/
blocked_normal_workflow（blocking_phase: in_progress で暗示）/
mainline_blocked_by（completed 開始の maintenance に戻り先はなく不要）/
action_parameters（他フィールドの重複コピー）/
active_gate（maintenance では常に null）
```

**`blocking_in_progress` の blocking_phase 値（設計メモ line 83 の確定内容）：**
```
resuming は廃止。in_progress（unit_id / parent_unit_id が null）として吸収。
```

**`reopen_in_progress` の廃止フィールド（設計メモ line 119 の確定内容）：**
```
廃止するフィールド：
next_drafting_gate（active_gate で代替・手引き改修が必要）/
feature（required_feature_scope で代替）/
direct_features / indirect_features / feature_impact_scope_basis（手引きに参照なし）
```

---

## 審査の観点

design.md の §5.2・§5.3・§5.4 を読み、以下の観点で独立して分析してほしい。

**観点 1：受入 11 と §5.3 設計の整合性**

受入 11 は `action_parameters` を `required_action = "run_maintenance"` のときの必須フィールドと定義している。§5.3 の `blocking_in_progress` 節は `action_parameters` を「廃止するフィールド」に列挙している。
この 2 つの記述は矛盾しているか。矛盾している場合、どちらが優先されるべきか、あるいはどのように整合を取るべきか分析してほしい。

**観点 2：受入 12 の 7 値と §5.2 値域表の整合性**

受入 12 が列挙する 7 種類の kind 値と、§5.2 の値域表が定義する 7 種類の kind 値を比較してほしい。値の集合・意味・選択子としての優先順位付けに問題があれば指摘してほしい。

**観点 3：設計メモと §5.3 の整合性**

上記「確定設計メモ」の内容と design.md §5.3 の記述を比較してほしい。フィールドの欠落、余剰、意味の不一致があれば指摘してほしい。

**観点 4：設計の完結性**

§5.2〜5.4 を読んだ実装者が、 実装内容を一意に決定できるか。決定できない事項や曖昧な点があれば指摘してほしい。特に `commit-preflight` サブコマンドの設計（§5.4）が `commit-preflight` の既存実装と矛盾しないか確認してほしい。

**観点 5：design.md 内の内部整合性**

§5.2〜5.4 の間、および §5.2〜5.4 と design.md の他の箇所との間に矛盾や不整合はないか。
