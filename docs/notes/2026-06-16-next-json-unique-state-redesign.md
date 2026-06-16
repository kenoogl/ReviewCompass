---
date: 2026-06-16
record_type: design-note
status: draft
topic: next-json-unique-state-redesign
priority: highest
related:
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/REOPEN_PROCEDURE.md
  - docs/operations/WORKFLOW_PRECHECK_DETAILS.md
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - tools/check-workflow-action.py
---

# next --json 唯一状態応答の再設計メモ

## 1. 目的

`tools/check-workflow-action.py next --json` は、現在の repository / workflow state から
「今実行してよい唯一の action」を返す正本でなければならない。

本メモは、現状コードを精査したうえで、`next --json` が停止点、承認待ち、修復要求、
reopen gate、通常 workflow gate を同時に実行可能な action として混ぜないための
根本設計を定める。

本件は D-003 作業中に、`next_step: 第2過程：停止点コミット` と
`required_action: run_reopen_pending_gate` が同一応答に混在したことで顕在化した。
これは個別の pending gate 修正ではなく、`next --json` の action selection 契約の欠陥である。

## 2. 現状コードの調査結果

### 2.1 通常 workflow は先頭未完了段を一意に選んでいる

`tools/check-workflow-action.py` の `resolve_next_action(specs)` は、
`PHASE_ORDER` と `PHASE_STAGES` を順に走査し、最初の未完了 phase / stage を返す。
通常 workflow では「次に実行する段」はおおむね一意に選ばれている。

ただし通常 workflow の出力にも `active_gate` のような明示フィールドはなく、
`kind` / `phase` / `stage` の組み合わせを利用者や LLM が解釈している。

### 2.2 reopen は状態投影と action selection が混ざっている

`build_in_progress_next_action()` は reopen in-progress YAML から次の値を同時に返す。

- `next_step`
- `step_number`
- `pending_gates`
- `next_pending_gate`
- `next_drafting_gate`
- `current_blocker`
- `required_action`
- `phase`
- `stage`

しかし `required_action` の決定は 2 系統に分かれている。

1. `resolve_reopen_required_action(next_step, current_blocker, step_number)` が
   step_number / next_step から過程レベルの action を返す。
2. `_resolve_reopen_next_gate(data, pending_gates, current_blocker)` が
   pending gate から gate レベルの action を返す。

現行コードでは gate 側の `required_action` が存在すると、過程レベルの
`required_action` を上書きする。

このため、`commit_stop_point: true` で第2過程のコミット停止点にいる状態でも、
`pending_gates` が残っていれば `run_reopen_pending_gate` が返り得る。
停止点と gate 実行が同時に表示され、唯一 action 原則が破れる。

### 2.3 commit_stop_point は commit gate では扱われるが next selector では扱われない

commit 前検査には `_is_structured_reopen_commit_stop_point()` があり、
`commit_stop_point: true`、`commit_stop_point_step`、`commit_stop_point_kind` を見て
in-progress reopen の commit を許可する経路がある。

一方で `next --json` は `commit_stop_point` を action selection の最優先条件として扱わない。
そのため commit gate と next selector の間で状態解釈がずれる。

### 2.4 正本変更済み phase の full gate 検査が第2過程停止点に届いていない

`validate_reopen_completion_impact_decisions()` は、完了済み reopen YAML について、
staged canonical spec phase の変更がある場合に
`triad-review` / `review-wave` / `alignment` / `approval` を要求する。

しかしこれは `stages/completed/reopen-procedure-*.yaml` の検査であり、
第2過程の `stages/in-progress/reopen-procedure-*.yaml` commit_stop_point では
同じ不変条件を十分に検査していない。

今回のように requirements 本文を変更したにもかかわらず、in-progress の
`pending_gates` が `alignment` / `approval` だけでも、第2過程コミットを通過し得る。

### 2.5 reopen-start は trigger_map の静的 gate をそのまま使う

`cmd_reopen_start()` は `REOPEN_TRIGGER_MAP[classification]` を読み、
その結果を `pending_gates` として in-progress YAML に保存する。

この入力には「正本本文を修正する phase」と「正本本文を修正しない再確認 phase」の区別がない。
したがって、分類時点で requirements 本文修正が予見されていても、
R-0 の基線である `alignment` / `approval` だけが pending gate になり得る。

### 2.6 テストが混在応答を許容している

`tests/tools/test_check_workflow_action.py` には、reopen の `pending_gates` 先頭を
`next_pending_gate` / `phase` / `stage` として返すテストがある。
この方向自体は第3過程では正しい。

しかし現行テストは「第2過程の commit_stop_point が存在する場合は gate を返してはならない」
という相互排他を固定していない。
その結果、停止点より pending gate を優先する現行挙動をテストが止められない。

## 3. 守るべき原則

### 原則 1：next --json は action selector である

`next --json` は状態要約ではなく、今実行してよい唯一の action を選ぶ。
参考情報として future gates や workflow state を返してもよいが、
`required_action` は常に 1 つだけでなければならない。

### 原則 2：停止点は gate 実行より優先する

`commit_stop_point` または approval blocker が存在する場合、
`next --json` は pending gate 実行を案内してはならない。

停止点では次の形にする。

```json
{
  "kind": "reopen_in_progress",
  "required_action": "commit_stop_point",
  "phase": null,
  "stage": null,
  "active_gate": null,
  "blocked_by": {
    "type": "commit_stop_point"
  }
}
```

### 原則 3：phase / stage は active workflow unit がある時だけ非 null にする

`phase` / `stage` は「今実行してよい workflow unit」の座標である。
ここでいう workflow unit は、通常 workflow の drafting / triad-review / review-wave /
alignment / approval と、reopen 第3過程で active になった drafting または review gate を含む。
停止点、修復要求、承認待ち、分類待ちでは null にする。
maintenance / side track 実行中も通常 workflow の 3 軸上の active unit ではないため、
`feature`、`phase`、`stage`、`active_gate` は null にする。maintenance 側の具体作業名は
`maintenance_action` に分離して保持する。
通常 workflow または reopen 第3過程で active workflow unit がある場合、`feature` は
単一 feature 名または `all_features` のどちらかでなければならず、実行対象を複数 feature list
として曖昧に返してはならない。複数 feature の scope は `required_feature_scope` や
`future_gates` 側の補助情報に置く。

### 原則 4：pending_gates は予定であり、active_gate ではない

`pending_gates` は計画上残っている review gate の一覧である。
実行してよい workflow unit は `active_gate` 1 件だけで表す。
`active_gate` は通常 workflow や reopen drafting のような drafting unit も
`stages/<phase>.yaml#drafting` として表してよい。`pending_gates` には drafting を入れず、
drafting が必要な場合だけ selector が `active_gate` として派生する。

`active_gate` が null の時、LLM は gate を実行してはならない。

### 原則 5：next は action を返す前に invariants を検査する

`next --json` は in-progress YAML をそのまま投影してはならない。
まず状態不変条件を検査し、不整合があれば通常 action ではなく
`repair_workflow_state` を返す。

### 原則 6：reopen plan の派生値を手入力させない

`pending_gates`、rollback 対象、recheck 対象、stop points は、
構造化された reopen plan から派生する値でなければならない。
LLM が散文分類を読んで直接 `pending_gates` を決める運用は廃止する。

## 4. 目標 JSON 契約

### 4.1 共通フィールド

`next --json` の top-level は `verdict`、`exit_code`、`next_action`、`reasons`、
`current_state` を持つ。`verdict` は top-level にだけ置き、`next_action` 内へ混ぜない。

`next_action` は最低限、次を持つ。

```yaml
kind: string
required_action: string
active_gate: string | null
feature: string | null
phase: string | null
stage: string | null
required_feature_scope: list
blocked_by: object | null
future_gates: list
state_refs: object
```

`feature` は active workflow unit の単一座標であるため、list を許容しない。
複数 feature が影響範囲に入る場合は `required_feature_scope` や `future_gates` に置く。
真に横断 unit として実行する場合だけ `feature=all_features` を使う。

互換のため当面 `pending_gates`、`next_pending_gate` は残してよいが、
新契約では `future_gates`、`active_gate` を正とする。

### 4.2 required_action の相互排他

`required_action` は次のいずれか 1 つに限定する。

- `repair_workflow_state`
- `run_post_write_verification`
- `wait_for_human_decision`
- `record_human_decision`
- `run_maintenance`
- `draft_reopen_plan_candidates`
- `apply_approved_reopen_plan`
- `advance_reopen_after_approval_stop_point`
- `repair_canonical_documents`
- `commit_stop_point`
- `advance_reopen_after_commit_stop_point`
- `run_reopen_drafting`
- `run_reopen_pending_gate`
- `finalize_reopen`
- `collect_required_decisions`
- `draft_reopen_classification`
- `run_reopen_start`
- `run_workflow_stage`
- `completed`

`required_action=commit_stop_point` の時は、
`active_gate=null`、`phase=null`、`stage=null`、`blocked_by.type=commit_stop_point`
でなければならない。

`required_action=run_reopen_pending_gate` の時は、
`active_gate` が非 null で、`phase` / `stage` は `active_gate` と一致し、
`blocked_by=null` でなければならない。

`required_action=run_reopen_drafting` の時も、`active_gate` は
`stages/<phase>.yaml#drafting` とし、`phase` / `stage` はその drafting unit と一致する。

`required_action=repair_workflow_state` の時は、
`active_gate=null`、`phase=null`、`stage=null` とし、
`repair_reasons` を返す。

`required_action=wait_for_human_decision` は、post-write の human_required、
reopen approval blocker、その他の人間判断待ちを共通に表す。
詳細な停止理由は `blocked_by.type` で区別する。

`required_action=record_human_decision` は、人間判断の内容が構造化入力として存在し、
その decision record の作成と blocker 解除だけが未実施の場合に返す。
LLM は判断内容を作らず、構造化コマンドへ既存入力を渡して記録するだけである。

`required_action=collect_required_decisions` は、reopen 第4過程などで必要判断が
まだ存在しない未完了状態を表す。これは状態破損ではないため
`repair_workflow_state` と区別する。

`required_action=run_maintenance` は maintenance / side track の唯一 action を表す。
maintenance YAML 側の個別 action 名は `maintenance_action` に保持し、
`required_action` の語彙には直接混ぜない。
ただし通常 workflow / reopen と同じく、LLM が解釈で対象を探さなくてよいように、
`next_action.action_parameters` には `maintenance_action`、`allowed_scope`、
`allowed_files`、`completion_conditions`、`active_stack_frame_id`、
`parent_frame_id` への state ref を必ず含める。

## 5. reopen plan compiler 方針

### 5.1 structured classification を入力にする

reopen-start は散文分類だけでなく、構造化された分類情報を必須入力にする。

最低限の入力：

```yaml
classification: R-0
reopen_scope:
  - workflow-management
impact_review_scope:
  - foundation
  - runtime
  - evaluation
  - analysis
  - self-improvement
  - conformance-evaluation
canonical_update_phases:
  - requirements
impacted_downstream_phases:
  - design
  - tasks
  - implementation
flag_policy:
  workflow-management:
    requirements:
      alignment: false
      approval: false
```

### 5.2 pending gates は compiler が導出する

`canonical_update_phases` に含まれる phase は full gate を要求する。

```yaml
- stages/<phase>.yaml#triad-review
- stages/<phase>.yaml#review-wave
- stages/<phase>.yaml#alignment
- stages/<phase>.yaml#approval
```

正本本文を修正しない再確認 phase は `alignment` / `approval` のみでよい。
ただし後続の drafting で正本修正が発生した場合は、plan を再コンパイルして
full gate に昇格する。

### 5.3 plan と projection を同じ不変条件で検査する

reopen-start、next、commit gate、operation preflight は同じ invariant 関数を使う。
同じ状態を別々に解釈しない。

検査対象：

- classification と reopen scope の整合
- canonical_update_phases と pending / future gates の整合
- spec.json rollback と flag_policy の整合
- recheck.impacted_downstream_phases と impacted_downstream_phases の整合
- commit_stop_point と required_action の整合
- blocker と active_gate の相互排他
- direct / indirect feature scope の整合

## 6. action selection 優先順位

`next --json` は次の順序で 1 つの action を選ぶ。

1. workflow state / reopen plan が壊れている
   - `required_action=repair_workflow_state`
2. post-write verification が未完了
   - `required_action=run_post_write_verification`
3. post-write / reopen / side track の人間判断待ちがあり、記録可能な構造化入力がまだない
   - `required_action=wait_for_human_decision`
4. 人間判断の構造化入力が存在し、decision record 作成と blocker 解除だけが未実施
   - `required_action=record_human_decision`
5. maintenance / side track が進行中で、より高優先の pending がない
   - `required_action=run_maintenance`
6. reopen の commit stop point が HEAD に取り込まれ、post-commit 遷移だけが未実施
   - `required_action=advance_reopen_after_commit_stop_point`
7. reopen の commit stop point があり、対応する protected operation ledger がまだない
   - `required_action=commit_stop_point`
8. reopen 第1過程で、分類・影響範囲・rollback / recheck の候補作成が必要
   - `required_action=draft_reopen_plan_candidates`
9. 承認済み reopen plan の rollback / recheck 適用が未実施
   - `required_action=apply_approved_reopen_plan`
10. reopen 第1過程の承認停止点が承認済みで、step advance だけが未実施
   - `required_action=advance_reopen_after_approval_stop_point`
11. reopen 第2過程
   - `required_action=repair_canonical_documents`
12. reopen 第3過程で triad-review 前の drafting が必要
   - `required_action=run_reopen_drafting`
13. reopen 第3過程の active gate がある
   - `required_action=run_reopen_pending_gate`
14. reopen 第4過程で必要判断が不足している
   - `required_action=collect_required_decisions`
15. reopen 第4過程で必要判断が揃っている
   - `required_action=finalize_reopen`
16. 完了済み workflow の上流更新により reopen classification draft が必要で、
    進行中 reopen / maintenance が存在しない
   - `required_action=draft_reopen_classification`
17. 承認済み reopen classification があり、reopen-start だけが未実施で、
    進行中 reopen / maintenance が存在しない
   - `required_action=run_reopen_start`
18. 通常 workflow の active gate
   - `required_action=run_workflow_stage`
19. 完了
   - `required_action=completed`

この優先順位をコード、テスト、運用文書で 1 箇所の契約として固定する。

## 7. 実装方針

### 7.1 TDD の最初の失敗テスト

最初に次の失敗テストを追加する。

1. `commit_stop_point=true` の reopen state では pending_gates が残っていても
   `required_action=commit_stop_point`、`active_gate=null`、`phase=null`、`stage=null` を返す。
2. `current_blocker` がある reopen state では pending_gates が残っていても
   `required_action=wait_for_human_decision`、`active_gate=null` を返す。
3. 正本変更済み phase が `canonical_update_phases` にあるのに
   future_gates / pending_gates が full gate を含まない場合、
   `verdict=DEVIATION`、`required_action=repair_workflow_state` を返す。
4. 第3過程で active gate がある場合だけ `phase` / `stage` が非 null になる。
5. commit stop point commit 後、worktree clean で HEAD が当該 stop point を含む場合、
   `required_action=advance_reopen_after_commit_stop_point` を返し、同じ commit stop point を再提示しない。
6. `required_action` ごとの JSON 相互排他 schema を fixture で検証する。

commit stop point が HEAD に取り込まれたかは、コミット後に作る protected operation ledger で判定する。
commit 前の approval challenge は `stop_point_id`、`reopen_yaml_path`、`commit_stop_point_kind`、
`staged_files`、`staged_diff_digest`、`nonce` を持つ。guarded commit 成功後、
commit guard は `head_commit`、`tree_digest`、`committed_files`、
`consumed_approval_id`、`stop_point_id` を ledger に追記する。
`next --json` は reopen YAML の未消費 `commit_stop_point` と ledger の
`stop_point_id` / `staged_diff_digest` / `head_commit` を照合し、HEAD がその
`head_commit` と一致または descendant で、worktree が当該 stop point に対して clean の時だけ
`advance_reopen_after_commit_stop_point` を返す。

### 7.2 コード変更の方向

1. `build_in_progress_next_action()` を直接投影関数から selector 関数へ変える。
2. reopen state を読み、まず `validate_reopen_state_for_next(data, specs)` で不変条件を検査する。
3. `select_reopen_required_action(data)` を作り、停止点・blocker・step・active gate の優先順位を一元化する。
4. `active_gate` / `future_gates` / `blocked_by` を追加する。
5. 既存の `next_pending_gate` は互換フィールドとして残すが、停止点では null にする。
6. `resolve_reopen_required_action()` と `_resolve_reopen_next_gate()` の結果を単純上書きしない。
7. commit gate にも同じ invariant 検査を組み込み、第2過程停止点 commit で full gate 欠落を遮断する。
8. commit stop point commit 後の遷移コマンドとして
   `reopen-advance-after-commit-stop-point` を追加する。このコマンドは対象 reopen YAML、
   HEAD commit、commit_stop_point_kind、evidence を必須引数として受け取り、
   commit_stop_point を消費済みにして第3過程へ進める。
9. workflow state repair 用の `reopen-recompile` または同等の plan repair command を追加する。
   このコマンドは structured classification / canonical_update_phases / flag_policy から
   reopen plan、future_gates、pending_gates、spec rollback plan、recheck plan を再導出する。
   LLM が in-progress YAML の派生値を直接手編集して repair する経路は正規経路にしない。

### 7.3 文書・仕様の反映

更新対象：

- workflow-management requirements
  - Requirement 2 に `next --json` 一意 action selector 契約を追加
  - Requirement 5 に reopen plan compiler 契約を追加
  - Requirement 12 は Requirement 2 の出力を参照するだけに整理
- workflow-management design
  - reopen plan schema
  - action selection 優先順位
  - invariant 関数
- workflow-management tasks
  - テスト項目と実装タスク
- WORKFLOW_NAVIGATION.md
  - `required_action` の相互排他と `active_gate` 契約
- WORKFLOW_PRECHECK_DETAILS.md
  - reopen-start / reopen-advance-step / commit gate の invariant 検査

## 8. 想定シナリオ

以下は、利用者・LLM・機械コマンドが実際にどう動くべきかを記述する。
各シナリオでは、最初に必ず `next --json` を呼び、返された唯一の
`required_action` だけを実行する。補助情報として future gates や state refs を
表示してよいが、それらは実行指示ではない。

8 章の全シナリオは、LLM の状況判断で分岐してはならない。
次の feature、phase、stage、gate、reopen step、side track frame、復帰先、
承認待ち、修復要求、post-write 優先は、すべて selector と構造化コマンドの
アルゴリズムで決定する。LLM の役割は、返された `required_action` と
`action_parameters` を読み、許可された 1 action を実行することに限定する。
候補が複数ある場合、LLM は選ばず、`next --json` が一意に選べない状態として
`required_action=repair_workflow_state` を返す。

selector と構造化コマンドがアルゴリズムで参照してよい情報源は次に限定する。

- repository state
  - `git status`、staged files、HEAD、merge/rebase 状態、branch と upstream の差分
  - tracked / untracked file inventory
  - file content hash、mtime、diff against HEAD、staged diff
  - path existence、rename / delete detection
- workflow specs
  - 各 feature の `spec.json`
  - `feature_order`
  - phase order と stage order
  - phase / stage 定義、gate ordering、stage flag schema
  - `requirements.md`、`design.md`、`tasks.md` などの canonical documents
  - intent / feature-partitioning 正本
  - feature ownership / document ownership mapping
  - upstream / downstream dependency mapping
  - completion flag semantics、recheck semantics
- workflow evidence
  - drafting 証跡
  - triad-review / review-wave / alignment / approval の review-run
  - gate completion record
  - human approval / decision record
  - review target、criteria、variant、role assignment、provider / model assignment
  - raw / parsed / triage / proxy decision / final decision の対応関係
  - evidence が覆う target hash / commit / file set
- reopen state
  - `stages/in-progress/reopen-procedure-*.yaml`
  - `stages/completed/reopen-procedure-*.yaml`
  - structured reopen classification
  - structured reopen candidate record
  - approved reopen plan
  - reopen plan、`canonical_update_phases`、`impacted_downstream_phases`
  - rollback / recheck / flag_policy
  - `pending_gates`、`future_gates`、completed gates
  - `commit_stop_point`、`current_blocker`
  - reopen coverage record
  - reopen が覆う upstream diff / canonical document hash / commit range
  - reopen step transition record
  - reopen command evidence
- side track / maintenance state
  - side track stack frames
  - active top frame
  - `parent_frame_id`、`return_to`
  - `allowed_scope`、`allowed_files`、`completion_conditions`
  - `maintenance_action`
  - push / pop operation record
  - superseded / blocked / expanded frame record
- post-write verification state
  - post-write manifest
  - review-run raw / parsed / triage
  - unresolved findings、human_required、completed status
  - manifest coverage target set
  - target file hash / commit / diff basis
  - document type / artifact type classification
  - post-write requirement policy
- operation guard state
  - commit approval challenge / approval record
  - approval nonce、digest、staged file list、consumed status、expiry
  - commit precheck result
  - push precheck result
  - protected operation ledger
  - last successful guarded operation record
- command registry / operation schema
  - 実行可能な構造化コマンド名
  - 各 command の required / optional arguments
  - command が読み書きしてよい state
  - command precondition / postcondition
  - operation alias と deprecated command mapping
- workflow policy / document policy
  - post-write 対象判定規則
  - 正本文書と補助文書の配置規約
  - artifact coverage policy
  - review-run 保存先規約
  - commit / push / approval の運用規約
- explicit user input recorded by a structured command
  - feature selection
  - human approval / rejection
  - side track push request
  - ambiguous repair choice
  - requested action scope
  - selected candidate ID
  - user decision provenance

LLM の会話記憶、推測、未記録の利用者意図、ファイル名順の偶然、未構造化メモの散文解釈は、
selector の情報源にしてはならない。必要な情報が上記の正本 state に存在しない場合は、
`required_action=repair_workflow_state` または `required_action=wait_for_human_decision`
として、構造化記録を作ってから再度 `next --json` を実行する。

### 8.0 軸と単位の前提

`next --json` は、少なくとも次の 3 軸を区別して扱う。

- **フィーチャー軸（feature axis）**：仕様を所有する機能単位。例は
  `foundation`、`runtime`、`workflow-management` などだが、対象アプリでは
  feature-partitioning の結果として任意の feature 名になり得る。利用者指定や
  進行中 feature がない場合の既定順は `feature_order` が正本である。
- **フェーズ軸（phase axis）**：仕様駆動開発の縦方向の工程。代表値は
  `intent`、`feature-partitioning`、`requirements`、`design`、`tasks`、
  `implementation` である。上流 phase の変更は下流 phase の再確認や reopen を要求し得る。
- **ステージ軸（stage axis）**：各 phase 内の段階的な進行段。
  通常の feature phase では `drafting`、`triad-review`、`review-wave`、
  `alignment`、`approval` を扱う。`intent` や `feature-partitioning` は専用 stage を持つ。

この 3 軸の 1 点、つまり `<feature, phase, stage>` が通常 workflow の
候補 unit である。`next --json` は候補 unit の中から、現在実行してよい 1 件だけを
**active workflow unit** として選ぶ。active workflow unit がある場合だけ、
`feature`、`phase`、`stage`、`active_gate` は具体値を持つ。
active workflow unit がない場合、`feature`、`phase`、`stage`、`active_gate` は null である。

**active workflow unit** とは、`next --json` が現在状態から選択し、
LLM が今すぐ実行してよいと許可した単一の workflow 実行単位である。
通常 workflow では `<feature, phase, stage>` の 1 点であり、reopen 第3過程では
drafting または review gate の 1 件である。未完了 unit、future gates、pending gates、
reopen scope に含まれる feature 群は、それだけでは active workflow unit ではない。

**active workflow unit を持たない action** とは、`next --json` が返す唯一 action ではあるが、
通常 workflow の `<feature, phase, stage>` 座標として実行されるものではない action である。
該当例は post-write verification、human decision、maintenance、reopen 第1過程、
reopen 第2過程、commit stop point、workflow state repair である。
これらでは `feature`、`phase`、`stage`、`active_gate` は null にし、
対象 feature、対象 phase、対象ファイル、実行コマンドは `state_refs` や
`action_parameters` などの補助フィールドから読む。

このメモでは「非 active workflow unit」という用語は使わない。
未選択の `<feature, phase, stage>` は **candidate workflow unit**、
3 軸外の唯一 action は **active workflow unit を持たない action** と呼び分ける。

reopen や maintenance では、通常 workflow の 3 軸に加えて手続き軸が入る。
この場合も `next --json` は「手続き上いま実行できる 1 unit」だけを active にする。
停止点、承認待ち、修復要求では active workflow unit は存在しないため、
`feature`、`active_gate`、`phase`、`stage` は null になる。
複数 feature を reopen scope に含む場合でも、active workflow unit は 1 feature ずつ選ぶ。
ただし選択順は常に `feature_order` 固定ではない。利用者が特定 feature の作業を指示した、
または in-progress state が現在作業中の feature を保持している場合、`next --json` は
その feature の次の unit を返す。利用者指定も進行中 feature もない場合だけ、
`feature_order` を tie-breaker として使う。review-wave のように本当に横断 gate として
扱う unit だけは `feature=all_features` を返す。

active workflow unit を持たない action では、修正対象や検証対象を `feature` / `phase` /
`stage` に入れない。たとえば post-write verification の対象は `state_refs` と
post-write manifest 候補から読み、reopen 第1・第2過程の対象は reopen plan の
`reopen_scope`、`canonical_update_phases`、`impacted_downstream_phases` から読む。
maintenance の対象は maintenance YAML の `allowed_scope` / `allowed_files` /
`maintenance_action` から読む。この区別により、`phase` や `feature` が null でも
LLM は補助情報から対象を特定できるが、それを active gate と誤認しない。

### 8.1 通常 workflow

#### S-001 clean かつ feature 指定なしの通常進行

起点：作業ツリーに進行中手続きがなく、post-write pending もない。全 feature の
`spec.json` を読むと、未完了の `<feature, phase, stage>` は複数存在し得る。
利用者から特定 feature の作業指示はなく、in-progress state に作業中 feature もない。
そのため selector は `feature_order`、phase order、stage order の順序に従って、
1 件だけを active workflow unit として選ぶ。
例として、選ばれた active workflow unit が
`<feature>.requirements.drafting` である。

動作：LLM は `next --json` を実行する。`next` は既定順と workflow_state から
唯一の active workflow unit を選び、feature、phase、stage を機械可読に返す。
LLM は返された feature / phase / stage だけを扱い、同じ phase の他 feature、
後続 stage、reopen 分類、side track へは進まない。

完了後：drafting 証跡を作り、必要な検査を通してから `spec.json` の該当 flag を進める。
その後に再度 `next --json` を呼び、次の唯一 action を取得する。

禁止動作：`next` が future gates を返しても、それを先取りして実行しない。
通常 workflow 中に未登録の side track を始めない。

#### S-001b feature 指定または作業中 feature がある通常進行

起点：作業ツリーに進行中手続きがなく、post-write pending もない。
利用者が特定 feature の作業を指示している、または workflow state が作業中 feature を
保持している。

動作：LLM は `next --json` を実行する。`next` は `feature_order` の先頭 feature ではなく、
指定または作業中 feature の未完了 unit から 1 件だけを active workflow unit として返す。
その feature 内での phase / stage 選択は phase order、stage order に従う。

完了後：該当 feature の unit を完了記録し、再度 `next --json` を呼ぶ。
同じ feature に未完了 unit が残っている場合は、その feature の次 unit を返す。
利用者指定または作業中 feature が解消された場合だけ、既定順の選択に戻る。

禁止動作：利用者が指定した feature を無視して `feature_order` 先頭 feature に戻らない。

#### S-002 通常 workflow 完了

起点：全 feature の workflow state が完了し、上流成果物の更新も post-write pending もない。

動作：`next --json` は `required_action=completed` を返す。LLM は任意の改善候補を提示してよいが、
それを workflow 上の次 action と混同しない。

完了後：利用者が改善候補を選んだ場合、その作業が通常 workflow か maintenance か
reopen かを判定し、必要なら進行中ファイルを作ってから着手する。

#### S-003 完了済み workflow で上流成果物が新しい

起点：通常 workflow は完了しているが、`requirements.md` が `design.md` より新しく、
その差分を覆う completed reopen がない。

動作：`next --json` は `required_action=draft_reopen_classification` を返す。
LLM は design の再確認へ直接進まず、
まず上流変更の意味を調査し、reopen classification 候補を構造化して記録する。
分類候補を記録したら、ただちに `next --json` を再実行する。
分類に利用者承認が必要な場合、次の応答は `wait_for_human_decision` になる。
承認済み分類が揃っている場合だけ、次の応答は
`required_action=run_reopen_start` を返す。
LLM はその action に従い、`reopen-start` で reopen plan を生成する。

完了後：`reopen-start` 成功後に `next --json` を再実行し、reopen 第1過程の唯一 action に従う。

禁止動作：`requirements` が新しいことを「軽い alignment でよい」と LLM が判断して
直接 downstream gate に進めない。

### 8.2 post-write verification

#### S-010 docs の未検証変更

起点：`docs/notes/*.md` を編集したが、その変更を覆う completed manifest がない。
reopen / maintenance in-progress はない。

動作：`next --json` は `required_action=run_post_write_verification` を唯一 action として返す。
LLM は対象ファイル全体を review target として post-write verification を実行する。
この応答では active workflow unit は存在しないため、`feature=null`、`phase=null`、
`stage=null`、`active_gate=null` である。検証対象は post-write 対象情報から読む。
検証 run と manifest を作るまでは通常 workflow に戻らない。

完了後：manifest が completed になったら `next --json` を再実行する。
そこで初めて通常 workflow、reopen、maintenance の次 action を見る。

禁止動作：検証対象の docs 変更を抱えたまま stage flag 更新や commit に進まない。

#### S-011 post-write に human_required が残る

起点：post-write manifest はあるが、重要件または human_required の所見が残っている。

動作：`next --json` は `required_action=wait_for_human_decision` を返す。LLM は所見の raw、要約、候補案、
推奨案を提示し、利用者判断を待つ。proxy_model に判断させる場合も、利用者提示ゲートを
通してからにする。

完了後：判断を triage / approval record に反映し、manifest を再生成してから
`next --json` を再実行する。

禁止動作：human_required を未解決のまま completed とみなさない。

### 8.3 reopen 第1・第2過程

#### S-020 reopen 第1過程

起点：reopen in-progress が作られ、`step_number: 1` である。

動作：`next --json` は `required_action=draft_reopen_plan_candidates` を唯一 action として返す。
LLM は分類根拠、feature impact、reopen scope、impact review scope、
spec rollback plan、downstream recheck plan の候補を構造化して提示する。
ここで作るのは候補だけであり、分類採否、影響範囲、rollback / recheck の採否は人間判断に任せる。
LLM は候補を確定扱いにせず、flag rollback もまだ実行しない。
この応答では active workflow unit は存在しないため、`feature=null`、`phase=null`、
`stage=null`、`active_gate=null` である。対象 feature / phase は reopen plan から読む。

完了後：候補を structured candidate record として保存したら、ただちに
`next --json` を再実行する。候補の採否が未決なら、次の応答は
`required_action=wait_for_human_decision` になる。利用者が候補を承認または修正承認し、
approved reopen plan が構造化記録された後に再度 `next --json` を実行する。
次の応答が `required_action=apply_approved_reopen_plan` を返した場合だけ、
承認済み plan に従って flag rollback / recheck plan の適用を行う。
適用後に再度 `next --json` を実行し、
`required_action=advance_reopen_after_approval_stop_point` が返った場合だけ、
`reopen-advance-step --from-step 1` を実行して第2過程へ進める。

禁止動作：第1過程の途中で requirements 本文、design 本文、テスト、実装を編集しない。

#### S-021 reopen 第1過程の承認待ち

起点：第1過程の分類、再実施範囲、rollback / recheck plan の候補が揃い、
人間承認待ちになっている。

動作：`next --json` は `required_action=wait_for_human_decision` を返す。
LLM は候補、根拠、差し戻し案、再実施範囲案を提示し、承認または修正指示を待つ。

完了後：利用者承認を記録したら `next --json` を再実行する。
次の応答が `apply_approved_reopen_plan` を返した場合だけ、
承認済み plan を機械適用する。適用後に `next --json` を再実行し、
`advance_reopen_after_approval_stop_point` が返った場合だけ、
`reopen-advance-step --from-step 1` を実行して第2過程へ進む。

禁止動作：承認前に正本修正や commit をしない。

#### S-022 reopen 第2過程の正本修正

起点：第1過程が承認され、`step_number: 2` になっている。commit stop point はまだない。

動作：`next --json` は `required_action=repair_canonical_documents` を唯一 action として返す。
LLM は reopen plan が指定する
canonical update phase だけを編集する。本文修正が発生した phase は full gate
（triad-review、review-wave、alignment、approval）を plan に持つ必要がある。
この応答でも active workflow unit は存在しないため、`feature=null`、`phase=null`、
`stage=null`、`active_gate=null` である。修正対象 phase は `phase` ではなく
reopen plan の `canonical_update_phases` から読む。

完了後：正本修正が終わったら `reopen-advance-step --from-step 2` を実行し、
commit stop point を作る。次に `next --json` を再実行する。

禁止動作：`pending_gates` が残っていても、第2過程中に gate 実行へ進まない。

#### S-023 reopen 第2過程の停止点コミット

起点：第2過程の正本修正が終わり、`commit_stop_point: true` が立っている。
pending gates は今後の予定として残っている。

動作：`next --json` は `required_action=commit_stop_point` を唯一 action として返す。
LLM は staged 対象、digest、nonce を提示し、利用者承認後に guarded commit を実行する。

完了後：commit 成功後に `next --json` を再実行する。`next` は同じ commit stop point を
再提示せず、`advance_reopen_after_commit_stop_point` を唯一 action として返す。
LLM は `reopen-advance-after-commit-stop-point --file <reopen-yaml> --head <commit> --kind <commit_stop_point_kind> --evidence <path>`
を実行して `commit_stop_point` を消費済みにし、`step_number: 3`、
`next_step: 第3過程：<先頭 gate>` へ進める。その後に再度 `next --json` を呼び、
第3過程の drafting / gate 実行へ進む。

禁止動作：commit stop point 中に `pending_gates[0]` を実行しない。
`phase` / `stage` を gate 実行可能な値として返さない。

### 8.4 reopen 第3過程

#### S-030 triad-review 前に drafting が必要

起点：第3過程に入り、次の planned gate は `design triad-review` だが、
design drafting 完了記録がまだない。

動作：`next --json` は `required_action=run_reopen_drafting` を唯一 action として返し、
対象座標を `phase=design`、`stage=drafting` に入れる。
この応答では active workflow unit が存在するため、`feature` は対象 feature 名、
`active_gate=stages/design.yaml#drafting`、`phase=design`、`stage=drafting` であり、
これらを null にしてはならない。
LLM は review を始めず、まず design 正本本文を更新し、drafting 完了を記録する。

完了後：drafting 完了記録を入れて `next --json` を再実行する。
次に triad-review が active gate になる。

禁止動作：本文更新前に triad-review review-run を開始しない。

#### S-031 triad-review を実行できる

起点：第3過程で `design drafting` は完了済み。次の planned gate は `design triad-review`。

動作：`next --json` は `required_action=run_reopen_pending_gate` として
`design triad-review` を唯一の active gate に返す。
LLM は対象正本、review target、variant、role assignment を確定し、triad-review を実行する。

完了後：review 所見の判断と対処を完了し、`reopen-advance-gate` で triad-review gate を
completed に移す。その後 `next --json` を再実行する。

禁止動作：review-wave や alignment を先に実行しない。

#### S-032 approval gate は承認停止点として扱う

起点：第3過程で次の planned gate は `requirements approval` で、まだ承認待ち blocker はない。

動作：`next --json` は `required_action=run_reopen_pending_gate` として
approval gate を唯一 action に返す。この時点の `active_gate` は
`requirements approval` を指すが、approval gate の実行内容は自動完了可能な
review-run ではなく、承認要求の構造化である。LLM は approval に必要な判断材料をまとめ、
`reopen-set-blocker` で人間承認待ちを構造化する。

完了後：`next --json` を再実行すると S-033 になる。

禁止動作：approval gate を「自動で完了」として進めない。

#### S-033 approval blocker がある

起点：`current_blocker` に approval gate の人間承認待ちが記録されている。

動作：`next --json` は `required_action=wait_for_human_decision` を唯一 action として返す。
LLM は承認対象、理由、証跡を提示し、利用者の承認を待つ。

完了後：利用者の承認または却下は、まず構造化入力として記録する。
次に `next --json` を再実行する。構造化入力が存在し、decision record 作成と
blocker 解除だけが未実施なら、`required_action=record_human_decision` を返す。
LLM は `reopen-record-human-decision` などの構造化コマンドで approval decision record を作成し、
`current_blocker` を消費済みにする。その後に `next --json` を再実行し、
approval gate が承認済みなら `required_action=run_reopen_pending_gate` として
`reopen-advance-gate` の実行対象を返す。却下なら selector は repair または候補再作成など、
構造化された却下理由に対応する唯一 action を返す。

禁止動作：blocker が残っている状態で次の pending gate を実行しない。

### 8.5 reopen 第4過程

#### S-040 finalize 可能

起点：第3過程の gates はすべて完了し、`pending_gates` は空。
feature impact / downstream impact / new feature decision も揃っている。

動作：`next --json` は `required_action=finalize_reopen` を唯一 action として返す。
LLM は final consistency check、recheck clear、completed YAML への移動を
`reopen-finalize` で実行する。

完了後：`reopen-finalize` 成功後に必ず `next --json` を再実行する。
次の応答が `commit_stop_point`、post-write verification、completed のどれになるかは
selector が状態から一意に選ぶ。

#### S-041 第4過程だが required decisions が不足

起点：第4過程に到達しているが、必要な feature impact decision や
downstream impact decision が欠けている。

動作：`next --json` は `required_action=collect_required_decisions` を唯一 action として返す。
これは状態破損ではなく、finalize 前の未完了作業である。
LLM は不足項目を提示し、必要な判断・証跡を構造化候補として作る。
採否が必要な判断は `wait_for_human_decision` / `record_human_decision` を経由して記録する。

完了後：不足項目を構造化して補い、再度 `next --json` を実行する。

### 8.6 side track / maintenance

side track は stack として管理する。mainline は stack の底にある frame であり、
maintenance や一時的な修復作業は `side-track-push` によって上に積まれる。
完了時は `side-track-pop` が top frame だけを閉じ、復帰先は直下の frame に機械的に決まる。
LLM は復帰先を判断しない。

`next --json` は常に stack top の frame だけを実行対象として返す。
stack 全体を `state_refs` に表示してよいが、`required_action` と `action_parameters` は
top frame 由来の 1 件だけでなければならない。top frame より下の mainline / side track は、
top frame が pop されるまで実行してはならない。

stack frame は最低限、`frame_id`、`kind`、`parent_frame_id`、`pushed_by`、
`allowed_scope`、`allowed_files`、`completion_conditions`、`return_to` を持つ。
`return_to` は LLM が解釈する復帰先ではなく、pop 後に selector が直下 frame を再開するための
機械参照である。

#### S-050 maintenance が単独で進行中

起点：workflow 制御や検査器修正のため、maintenance in-progress が作られている。
post-write pending はない。
side track stack の top frame はこの maintenance である。

動作：`next --json` は `required_action=run_maintenance` を唯一 action として返す。
LLM は maintenance YAML の allowed scope / allowed files / completion conditions だけを扱う。
この応答では active workflow unit は存在しないため、`feature=null`、`phase=null`、
`stage=null`、`active_gate=null` である。作業対象は `maintenance_action` と
maintenance YAML の scope 情報から読む。

完了後：completion conditions を満たしたら `side-track-pop` が top frame を閉じる。
その後に `next --json` を再実行すると、selector は直下の frame を機械的に再開する。

禁止動作：maintenance 中に通常 workflow の phase/stage を同時に進めない。

#### S-051 maintenance 中に post-write pending がある

起点：maintenance 作業で docs を編集し、post-write verification が未完了になった。

動作：`next --json` は maintenance ではなく
`required_action=run_post_write_verification` を唯一 action として返す。
LLM は検証を完了させるまで maintenance 本体の追加編集を進めない。

完了後：post-write manifest が completed になったら `next --json` を再実行し、
maintenance action に戻る。

#### S-052 mainline reopen 中の maintenance

起点：本線 reopen が進行中だが、その `next` 判定自体に欠陥があるため、
`side-track-push` により maintenance frame が本線 reopen frame の上に積まれている。

動作：`next --json` は `required_action=run_maintenance` を唯一 action として返す。
LLM は本線 reopen gate を実行せず、`next` 欠陥修復だけを進める。

完了後：`side-track-pop` が maintenance frame を閉じる。
その後に `next --json` を再実行すると、本線 reopen frame が stack top になり、
その唯一 action が改めて返る。

禁止動作：maintenance が完了する前に本線 reopen の pending gate を進めない。

#### S-053 side track のネスト

起点：本線 reopen の上に maintenance frame が積まれている。
その maintenance の実行中に、post-write 判定器や commit guard など、
maintenance 自体を完了するための別修復が必要になった。

動作：LLM は復帰先を判断しない。`side-track-push` が現在の top frame を parent として、
新しい side track frame を stack top に積む。`next --json` は新しい top frame だけを
`required_action=run_maintenance` として返す。

完了後：新しい side track frame の completion conditions を満たしたら、
`side-track-pop` がその frame だけを閉じる。`next --json` を再実行すると、
直下の maintenance frame が再び top になり、その唯一 action が返る。

禁止動作：LLM が stack を手編集して frame を飛ばさない。
pop 対象は常に top frame だけであり、親 frame や mainline へ直接戻らない。

### 8.7 repair / 異常系

#### S-060 commit_stop_point と active gate の混在

起点：reopen YAML に `commit_stop_point: true` があるにもかかわらず、
selector が pending gate を active gate として materialize しようとしている。
pending gates が将来予定として残っているだけなら正常であり、異常ではない。

動作：`next --json` は `required_action=commit_stop_point` を唯一 action として返し、
active gate は返さない。
もし selector 内部で active gate と stop point が同時に立つなら、それは実装バグまたは
状態投影バグとして repair を返す。

完了後：`required_action=commit_stop_point` なら commit 停止点の処理だけを実行する。
`required_action=repair_workflow_state` なら repair だけを実行する。
どちらの場合も、処理後に `next --json` を再実行して次の唯一 action を取得する。

#### S-061 正本変更済み phase の full gate 欠落

起点：reopen plan は requirements 正本を変更したと記録しているが、
future / pending / completed / required gates のどこにも requirements full gate が揃っていない。

動作：`next --json` は `verdict=DEVIATION` と
`required_action=repair_workflow_state` を返す。
LLM は triad-review でも alignment でもなく、まず `reopen-recompile` などの
plan repair command を実行して reopen plan / in-progress YAML の派生値を再導出する。
手編集で `pending_gates` だけを足して修復した扱いにしない。

完了後：full gate が機械的に導出・記録された状態で `next --json` を再実行する。

#### S-062 spec rollback と flag policy の不一致

起点：reopen plan は `requirements.alignment=false` を要求しているが、
実際の `spec.json` は true のままである。

動作：`next --json` は `required_action=repair_workflow_state` を返す。
LLM は通常 workflow や reopen gate へ進まず、plan repair command または
spec rollback 用の構造化コマンドで flag rollback の不一致を修復する。

完了後：spec rollback と plan が一致したら `next --json` を再実行する。

#### S-063 複数 in-progress の優先順位が不明

起点：複数の in-progress YAML が存在するが、mainline / side track の関係が記録されていない。

動作：`next --json` は `required_action=repair_workflow_state` を返す。
LLM はファイル名順で勝手に 1 件を選ばない。構造化コマンドが既存 state から
mainline / side track stack を一意に再構成できる場合だけ修復する。
一意に再構成できない場合は利用者入力を要求し、その入力を構造化コマンドに渡して
stack frame 関係を記録する。LLM が本線や side track を直接選ばない。

完了後：優先関係が一意になってから `next --json` を再実行する。

### 8.8 commit / push

#### S-070 commit 停止点での commit

起点：`next --json` は commit stop point を返している。

動作：LLM は対象ファイルを stage し、commit approval challenge を作り、
digest / nonce / staged files を利用者へ提示する。利用者が承認したら guarded commit を実行する。

完了後：commit 成功後に `next --json` を再実行し、次の唯一 action を確認する。

#### S-071 commit 停止点でないのに commit

起点：`next --json` は gate 実行、human decision、repair のいずれかを返しており、
commit stop point ではない。

動作：LLM が commit しようとしても、commit gate は遮断する。
LLM は `next --json` の唯一 action に戻る。

#### S-072 push

起点：worktree は clean、HEAD の commit precheck 記録があり、branch は origin より ahead。

動作：LLM は push precheck を通してから push する。

完了後：`next --json` を再実行し、リモート同期後の唯一 action を確認する。

禁止動作：workflow state repair pending のまま push を許可しない。

## 9. 現在の D-003 reopen への扱い

現在の `stages/in-progress/reopen-procedure-2026-06-16.yaml` は、
requirements 正本を変更済みであるにもかかわらず、
`pending_gates` が `alignment` / `approval` のみである。

さらに `commit_stop_point: true` があるにもかかわらず、現行 `next --json` は
`run_reopen_pending_gate` を返す。

したがって現在の D-003 reopen は、次へ進める前に workflow state repair が必要である。
ただしこれは手作業で pending_gates を直すだけでは再発を防げない。
最優先で `next --json` 一意 action selector と reopen invariant 検査を実装し、
その後に現在の in-progress state を機械的に修復する。

## 10. 結論

`next --json` の正本性は、単に「必要なフィールドを増やす」ことでは達成できない。
必要なのは、状態投影ではなく、優先順位付き action selector と invariant 検査である。

今後の実装では、`next --json` が返す `required_action` を常に唯一にし、
`phase` / `stage` / `active_gate` を gate 実行時だけ非 null にする。
不整合状態では通常 action を返さず、必ず `repair_workflow_state` を返す。

この原則を 1 ミリも外さないことを、Requirement 2、Requirement 5、Requirement 12、
運用文書、テスト、commit gate に同時に反映する。
