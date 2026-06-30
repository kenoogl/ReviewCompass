# Post-write Review Target

criteria_id: completed-entry-classification-navigation-postwrite
phase: post_write_verification
generated_at: 2026-06-30T09:15:53.225698+00:00

## Change Summary

WORKFLOW_NAVIGATION.md の completed 節に、maintenance / reopen / 新規 workflow の開始分類表と、人間判断待ちの停止条件を追加した。

## Review Question

追加した completed からの作業開始分類が、maintenance workflow protocol plan と作業モード分類に整合し、既存の completed / maintenance_in_progress / reopen_in_progress の説明と矛盾していないか確認してください。

## Target Files

- .reviewcompass/guidance/WORKFLOW_NAVIGATION.md sha256=1bcb3f2a7873b8e2312684eb3032b4f64068c965278bbcedcf3ba9798281ef2a

## Source Materials

### .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml

content_mode: full_text
content_sha256: 3f9d01e32c19afee9ea1ebcee5cef89a18227285444c3d36a1c3eaa8c6375d19

```text
schema_version: reviewcompass-backlog-item-v1
id: plan-2026-06-23-maintenance-workflow-protocol
kind: plan
title: Define maintenance workflow protocol
status: candidate
source_unit_id: main-completed
created_at: '2026-06-23T10:12:00+09:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md
  reason: >
    maintenance を短い修正扱いして review / post-write / completion の境界が曖昧になる問題を、
    独立した backlog plan として管理するため。
summary: >
  completed 状態から maintenance を開始する標準入口、maintenance / reopen / new workflow
  の使い分け、maintenance YAML の review evidence、post-write verification との境界、
  commit 前 guard での未充足検出を整備する。
supersedes:
  - docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md
related:
  - .reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml
  - .reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml
  - tools/check-workflow-action.py
remaining_work:
  - id: MWP-0
    title: Clarify workflow mode taxonomy
    status: candidate
    tasks:
      - workflow 実施区分、maintenance、side-track、blocking unit が同列概念ではないことを整理する。
      - 最小概念セットを「現在状態」「作業区分」「制御関係」に絞る。
      - allowed_scope / allowed_files / completion_conditions は独立概念ではなく、作業宣言の属性として扱う。
      - 作業開始宣言の標準形を定義する。
      - workflow state が completed の場合でも、実作業上の継続地点を一意に返せる work context / anchor stack を設計する。
      - side-track や補修作業の完了後に、LLM の会話記憶ではなく機械記録から return target を復元できるようにする。
    acceptance:
      - maintenance は作業区分、side-track は本線との関係、blocking unit は親作業に束縛された制御構造として区別される。
      - 作業宣言が「現在状態 + 作業区分 + 制御関係 + 許可範囲」で表現できる。
      - LLM が `audit` のような作業内容ラベルを workflow 上の作業区分と混同しない。
      - "`next --json` が workflow state として `completed` を返す状況でも、active anchor / return target があれば `backlog_return_pending` 相当の一意な次地点を返せる。"
      - 本筋、side-track、blocking unit、maintenance の親子関係と復帰先が、会話履歴ではなく構造化記録から説明できる。
    proposed_taxonomy:
      current_state:
        description: >
          `next --json` が返す機械状態。例: completed、maintenance_in_progress、
          blocking_unit_in_progress、post_write_verification。
        required: true
      work_class:
        description: >
          これから実施する手続きの種類。例: normal workflow、maintenance、
          reopen、verification。`audit` はここに入れる場合でも内容ラベルであり、
          workflow 状態名として扱わない。
        required: true
      control_relation:
        description: >
          本線や親作業との関係。例: mainline、side-track、blocking-unit、
          parent-resume。maintenance と blocking unit を同列に置かず、必要なら
          maintenance かつ side-track のように組み合わせて表現する。
        required: true
      permitted_scope:
        description: >
          allowed_scope、allowed_files、completion_conditions。独立した概念軸ではなく、
          作業宣言に必須の属性として扱う。
        required: true
      work_context:
        description: >
          workflow state が completed でも残り得る実作業上の現在地。active_anchor、
          side_track_stack、return_target、status を持ち、補修完了後に戻るべき
          backlog item / plan / workflow unit を一意に決める。これは current_state
          ではなく、作業意図と親子関係の記録である。
        required: true
    system_reflection_candidates:
      - "`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` に用語表を追加する。"
      - "`stages/in-progress/maintenance-*.yaml` に work_class / control_relation を明示フィールドとして追加するか検討する。"
      - "`next --json` の `next_action` に work_class / control_relation を返すか検討する。"
      - "`next --json` が completed を返す前に、work_context.active_anchor / return_pending を確認する層を追加するか検討する。"
      - backlog TODO / plan に parent / blocks / unblocks / return_target を持たせるか、runtime stack と commit 可能 evidence の二層に分けるかを検討する。
      - blocking unit と maintenance の allowed files / return conditions の差を schema または guard で検査する。
      - user-facing progress report では「作業モード」ではなく「現在状態」「作業区分」「本線との関係」を平易に出す。
    discussion_notes:
      - 2026-06-23 の guidance relocation inventory 作業では、plan-to-TODO bridge 補修と mutation boundary 補修が side-track として入り、補修完了後の戻り先は `todo-2026-06-23-guidance-relocation-inventory` だった。
      - "`next --json` は全 workflow_state 完了を正しく `completed` と返したが、会話上の本筋や補修後の復帰先は返せなかった。"
      - 原因は、workflow state の現在地と、実作業意図上の active anchor / return target が別軸なのに、後者が正本化されていないこと。
      - 単語ベースの「作業モード」運用ルールでは不十分であり、作業種類、親子関係、状態、操作境界、承認境界を分離して記録する必要がある。
      - この設計は慎重に行う。maintenance / side-track / blocking unit を単一 enum に押し込まず、別軸として組み合わせられる構造を検討する。
    non_goals:
      - この項目だけで workflow 状態機械を変更しない。
      - maintenance と blocking unit を同じ schema に統合しない。
      - every task に過剰な宣言を義務化しない。
      - completed の意味を「作業意図上も完全終了」に拡張しない。
  - id: MWP-1
    title: Maintenance entry and classification protocol
    status: candidate
    tasks:
      - completed 状態から maintenance を始める標準手順を定義する。
      - maintenance、reopen、新規 workflow unit の使い分け基準を文書化する。
      - 判断が分かれる場合は候補だけを返し、人間判断を required action とする。
    acceptance:
      - completed は作業不要だけでなく、利用者指示により maintenance / reopen / new workflow を開始可能と扱える。
  - id: MWP-2
    title: Maintenance evidence fields and next-json states
    status: candidate
    tasks:
      - workflow_steps、required_reviews、review_evidence、post_write_verification、completion_criteria を定義する。
      - next --json が maintenance review required、post-write required、completion required を返せるようにする。
      - docs note だけの記録作業と code / SDD 変更を分ける。
    acceptance:
      - maintenance 中の不足工程が一意に表示される。
      - post-write verification と変更内容そのものの review が混同されない。
  - id: MWP-3
    title: Commit and sandbox preflight for maintenance
    status: candidate
    tasks:
      - maintenance workflow の未充足を commit guard で検出する。
      - sandbox の git 書き込み権限を commit 実行前に検査する。
      - approval を消費せずに sandbox 外再試行へ進める状態を整理する。
    acceptance:
      - 承認後に sandbox 権限だけで止まった場合、利用者に不要な再承認を求めない。
non_goals:
  - maintenance を通常 workflow unit と完全同型にすること。
  - 軽微な作業にも常に重い 3 者 review を要求すること。
  - commit approval の安全境界を緩めること。
decisions: []
```

### docs/notes/2026-06-25-work-mode-taxonomy-related-work-index.md

content_mode: full_text
content_sha256: cfc9b1aa2dc339ed2b4ca28009387b3feadab84a8840fd3460373aefe8046834

```text
# 作業モード分類（workflow mode taxonomy）関連作業の索引

最終更新：2026-06-25。

## このメモの位置づけ

正式なワークフロー手続き（intent→requirements→design→tasks→implementation）以外の作業モード（maintenance／side-track／blocking unit／reopen／parent-resume／cross-feature／post-write verification）を整理する取り組みは、複数のファイルに散在している。本メモは、それらを 1 か所から辿れるようにする**俯瞰索引**である。正本仕様・運用規律・次判定そのものではなく、把握・判断材料の notes として扱う（軽量自己精査の対象）。

関係の整理は、中心 plan の `related`／`supersedes`／`provenance` フィールドと、2026-06-25 の俯瞰調査に基づく暫定整理である。各 plan の細部まで精読した結果ではない点に注意する。

## 中心：作業モード分類の定義

- [plan-2026-06-23-maintenance-workflow-protocol.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml)（status: candidate）
  - **MWP-0「Clarify workflow mode taxonomy」** が中核。maintenance／side-track／blocking unit が「同列概念ではない」とし、次の 5 軸に分けて表す。
    1. `current_state`（現在状態）… `next --json` が返す機械状態（completed／maintenance_in_progress／blocking_unit_in_progress／post_write_verification）
    2. `work_class`（作業区分）… これから行う手続きの種類（normal workflow／maintenance／reopen／verification）
    3. `control_relation`（制御関係）… 本線・親作業との関係（mainline／side-track／blocking-unit／parent-resume）
    4. `permitted_scope`（許可範囲）… allowed_scope／allowed_files／completion_conditions（作業宣言の属性）
    5. `work_context`（作業文脈）… completed でも残る現在地（active_anchor／side_track_stack／return_target）
  - MWP-1：maintenance／reopen／新規 workflow の使い分け基準
  - MWP-2：maintenance の evidence フィールドと next-json 状態
  - MWP-3：commit 前 guard での未充足検出

## ① 発想の元になったメモ（notes）

- [2026-06-17-maintenance-workflow-compliance-improvement-candidates.md](2026-06-17-maintenance-workflow-compliance-improvement-candidates.md) … 直接の前身（中心 plan の `supersedes`／`source_ref`）
- [2026-06-16-next-json-unique-state-redesign.md](2026-06-16-next-json-unique-state-redesign.md) … 「次判定が唯一の現在地を返せない」根本欠陥
- [2026-06-16-workflow-recovery-smell-inventory.md](2026-06-16-workflow-recovery-smell-inventory.md) … 戻り先（return_target）が正本化されていない問題
- [2026-06-18-mechanized-workflow-execution-design.md](2026-06-18-mechanized-workflow-execution-design.md) … 機械化と人間判断の分離という中核思想

## ② 各軸を実装する関連計画（すべて status: candidate）

| 計画 | 主に担う軸 |
| --- | --- |
| [plan-2026-06-22-blocking-unit-control-improvements.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-22-blocking-unit-control-improvements.yaml) | control_relation（blocking-unit）／work_context |
| [plan-2026-06-23-nested-issue-stack.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml) | control_relation の親子（nested） |
| [plan-2026-06-23-operation-registry-preflight.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml) | 作業宣言の機械化／permitted_scope（中心 plan の related） |
| [plan-2026-06-23-commit-stop-point-and-approval-ux.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-commit-stop-point-and-approval-ux.yaml) | completion_conditions／work_context（中心 plan の related） |
| [plan-2026-06-23-action-execution-spec.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml) | permitted_scope（read／write／state_mutation の区別） |
| [plan-2026-06-23-workflow-navigator-webui.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml) | work_context の可視化 |

## ③ 個別モードの掘り下げ

- side-track：[2026-06-09-d027-side-track-state-model-checklist.md](2026-06-09-d027-side-track-state-model-checklist.md)（contract 定義・検証済み）
- nested issue：[2026-06-16-nested-issue-handling-smell.md](2026-06-16-nested-issue-handling-smell.md)
- reopen：[REOPEN_PROCEDURE.md](../../.reviewcompass/guidance/REOPEN_PROCEDURE.md)

## ④ すでに機構側に入っている対応（実装・規格・手引き）

- 実装：`tools/check_workflow_action/` の `side_track_stack.py`／`work_unit_stack.py`／`workflow_state_snapshot.py`／`operation_preflight.py`／`commit_unit.py`
- 規格：`.reviewcompass/schema/` の `next_action_response.schema.json`／`required_action.schema.json`／`operation_contract.schema.json` ほか
- 手引き：[WORKFLOW_NAVIGATION.md](../../.reviewcompass/guidance/WORKFLOW_NAVIGATION.md)、[WORKFLOW_DISCIPLINE_MAP.yaml](../../.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml)

## ⑤ 整理作業の完了記録

- [maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml](../../stages/completed/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml) … この分類を backlog に記録した作業の完了記録

## 現状の要点

- 5 軸の分類（MWP-0）と、各層の実装計画（②）は揃っているが、**分類体系そのものを正式な手引き（WORKFLOW_NAVIGATION）や `next --json` に統合する作業は未着手（candidate）**である。
- 機構側（④）には side-track／blocking unit／snapshot などの個別実装が既に入っているが、5 軸の用語で統一されてはいない。
- 次に進めるなら、MWP-0 の `system_reflection_candidates`（用語表の追加、`next --json` への work_class／control_relation 付与など）が着手点になる。
```

### stages/completed/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml

content_mode: full_text
content_sha256: 5b4fcac20e0c47d1eaaa9ff27eef390478bc439c2b945f668c37c9bbd0948135

```text
process_id: maintenance
started_at: '2026-06-23T00:00:00+09:00'
completed_at: '2026-06-23T00:00:00+09:00'
trigger: >
  利用者指示により、workflow 実施区分、maintenance、side-track、
  blocking unit などの概念が体系的でない問題を backlog に記録するため。
mainline_blocked_by: none
allowed_scope: >
  workflow mode / work classification / control relation の概念整理を
  backlog plan に追記する。実装、仕様正本変更、next --json 挙動変更は行わない。
allowed_files:
- stages/in-progress/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml
- stages/completed/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml
- .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml
completion_conditions:
- maintenance / side-track / blocking unit が同列でないことを backlog に記録する
- 最小概念セットと削るべき概念を backlog に記録する
- 将来のシステム反映候補を backlog に記録する
- この作業では実装、正本 guidance 変更、next --json 挙動変更を行わない
- lightweight self-check と next --json の再確認を行う
completed_changes:
- .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml に MWP-0 を追加した
- 現在状態、作業区分、制御関係、許可範囲の最小整理を記録した
- maintenance / side-track / blocking unit が同列でないことを記録した
- 将来の guidance、maintenance YAML、next --json、guard への反映候補を記録した
- この作業では実装、正本 guidance 変更、next --json 挙動変更を行わなかった
verification:
- command: .venv/bin/python3 tools/document_link_lint.py --json .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml stages/completed/maintenance-2026-06-23-workflow-mode-taxonomy-note.yaml
  result: findings=0
- command: rg -n "MWP-0|workflow mode taxonomy|current_state|work_class|control_relation|permitted_scope|maintenance は作業区分|side-track|blocking unit" .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml
  result: recorded
evidence:
- .reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml
return_to:
  required_action: completed
  state_file: none
status: completed
```


## Target File Contents

### .reviewcompass/guidance/WORKFLOW_NAVIGATION.md

content_mode: full_text
content_sha256: 1bcb3f2a7873b8e2312684eb3032b4f64068c965278bbcedcf3ba9798281ef2a

```text
# ReviewCompass ワークフローナビゲータ共通手引き

この文書は、`tools/check-workflow-action.py next --json` の読み方を定める共通手引きである。

## 1. 最初に実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

出力 JSON の `next_action.kind` を、現在の作業順序・優先順位の正本として扱う。記憶、要約、TODO の候補欄だけを段取りの根拠にしない。

`next_action.required_disciplines` がある場合は、作業直前にそのファイルだけを読む。セッション開始時に長い規律群を一括で読んで記憶に頼るのではなく、機械判定された場面ごとの短い規律セットで挙動を調整する。対応表は `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` を正本とし、`next --json` はその内容を機械可読に展開する。

`next_action.required_inputs` がある場合は、規律ではなく作業対象ごとの状態入力として扱う。`id`、`source_type`、`read_policy` を確認し、`path` がある場合でもファイル名そのものを一般規律に昇格しない。たとえば持ち越し台帳は、配布先プロジェクトごとに別ファイル、外部台帳、または未配置になり得るため、`unresolved_cross_scope_items` のような抽象入力として扱う。

機械可読な判定点では、判定点ごとに 1 本の effective prompt を読む。複数の元資料を直接ばらばらに読ませるのではなく、判定点に必要な規律・入力・次タスク方針を 1 本へ束ねた effective prompt を作り、その本文を LLM に読ませる。元資料は `prompt_source_refs` として保持し、実際に読ませた統合プロンプトは `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` で記録する。全判定点で同じ巨大な共通プロンプトを使わず、各判定点に必要な短い effective prompt を使う。

## 1.1 作業モード分類の用語表（work mode taxonomy）

作業者は、maintenance、side-track、blocking unit、reopen、post-write verification を単一 enum に押し込まない。これらは同列の「作業モード」ではなく、次の軸を組み合わせて説明する。

| 用語 | 意味 |
| --- | --- |
| `current_state` | `next --json` が返す機械状態。例：`completed`、`maintenance_in_progress`、`blocking_unit_in_progress`、`post_write_verification`。 |
| `work_class` | これから行う手続きの種類。例：normal workflow、maintenance、reopen、verification。maintenance は作業区分であり、作業内容ラベルや親子関係ではない。 |
| `control_relation` | 本線・親作業との関係。例：mainline、side-track、blocking-unit、parent-resume。side-track は本線との関係であり、maintenance と同列の状態名ではない。blocking unit は親作業に束縛された制御構造である。 |
| `permitted_scope` | 作業宣言の属性。`allowed_scope`、`allowed_files`、`completion_conditions` で、どこまで触ってよいかと戻る条件を表す。 |
| `work_context` | workflow state が `completed` でも残り得る実作業上の文脈。active anchor、side-track stack、return target など、戻り先や親子関係を会話記憶ではなく構造化記録から説明するために使う。 |

例：`next --json` が `completed` を返していても、利用者が検査器の局所修正を求めた場合は、`current_state=completed`、`work_class=maintenance`、`control_relation=mainline` または `side-track`、`permitted_scope=allowed_files と completion_conditions` と分けて説明する。`audit` のような作業内容ラベルを、`current_state` や `control_relation` の値として扱わない。

## 2. 判定結果の共通分岐

<a id="resume_in_progress"></a>

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。新しい作業を始めず、`next_action.file` に示された進行中ファイルを読む。

<a id="parent_resume_pending"></a>

### `parent_resume_pending`

blocking unit が完了し、戻り先の parent unit へ復帰する必要が残っている。新しい作業を始めず、`next_action.parent_unit_id` と `next_action.completed_unit_id` を確認し、まず parent unit の作業文脈へ戻る。

`parent_resume_pending` が出ている状態で、利用者から別作業への明示的な割り込み指示があった場合は、開始前に次を実行して、active unit と resume pending の有無を機械的に確認する。

```bash
python3 tools/check-workflow-action.py work-unit preflight-start \
  --proposed-unit-id <開始候補 unit ID> \
  --title "<開始候補の題名>" \
  --reason "<開始候補の理由>" \
  --json
```

`start_allowed: false` の場合は、`blocking_reasons` を利用者へ示して停止する。理由を見ずに通常 workflow、maintenance、新しい blocking unit へ進まない。

<a id="blocking_unit_required"></a>

### `blocking_unit_required`

別作業として切り出すべき作業が検出されている。通常 workflow や親作業を続けず、`next_action.proposed_unit` の `unit_id`、`title`、`reason`、`parent_unit_id`、`return_conditions` を確認してから、利用者の明示的な開始指示を待つ。

機械化が完全に揃うまでは、blocking unit の開始を暗黙に扱わない。開始前に、少なくとも次を会話上で明示する。

- blocking unit に入ること。
- 親作業の識別子。
- blocking unit の目的。
- blocking unit で変更してよい allowed files。
- 親作業へ戻るための完了条件。

宣言形式は次の形にそろえる。項目名を変えたり、本文中に散らして書いたりしない。

```text
blocking unit に入ります
- unit_id: <blocking unit ID>
- parent_unit_id: <親作業 ID>
- title: <短い題名>
- reason: <なぜ別作業として切り出すか>
- allowed_files: <変更してよいファイルまたはディレクトリ>
- return_conditions: <親作業へ戻るための完了条件>
```

`allowed_files` は必須であり、空欄や「必要な範囲」「関連ファイル」などの曖昧な指定では開始しない。開始時点で想定できるファイルまたはディレクトリを列挙し、途中で範囲を広げる必要が出た場合は、変更前に allowed files の追加を利用者へ明示する。親作業全体やリポジトリ全体を覆う指定は、混線防止の目的に反するため使わない。

`return_conditions` も必須であり、空欄や「完了したら」「必要なところまで」などの主観的な指定では開始しない。親作業へ戻ってよいかを確認できる条件を列挙し、少なくとも成果物、検証、commit または evidence の扱いを含める。blocking unit を出るときは、各条件を満たしたか、未達なら何を残件として親作業へ戻すかを明示する。

<a id="blocking_unit_in_progress"></a>

### `blocking_unit_in_progress`

blocking unit が active である。`next_action.unit_id` の作業だけを扱い、親作業の commit、push、post-write verification、TODO 整理へ横滑りしない。

機械化が完全に揃うまでは、作業者は次を手動で守る。

- 作業開始時と再開時に、現在の active blocking unit を確認する。
- commit 前に、commit unit が active blocking unit の `unit_id` と一致することを確認する。
- blocking unit 完了前に親作業の成果物を同じ commit に混ぜない。
- 親作業の commit は、blocking unit の完了条件を満たし、必要な commit または evidence を残し、親作業へ戻る宣言を終えるまで実行しない。
- blocking unit を出るときは、完了条件を満たしたこと、残件、親作業への戻り先を明示する。

<a id="reopen_in_progress"></a>

### `reopen_in_progress`

reopen 手続きが進行中である。通常ワークフローや post-write-verification より優先する。`next_action.file`、`next_step`、`completed_steps`、`pending_gates`、`current_blocker`、`required_action` を確認し、`required_action` に従う。

代表的な `required_action`：

- `draft_reopen_classification`：第1過程。種別判定・根拠記録。進行中ファイル発行と spec.json フラグ差し戻しは後続操作（`run_reopen_start`・`apply_approved_reopen_plan`）が担う。
- `repair_canonical_documents`：第2過程。上流フェーズの正本文書修正。
- `run_reopen_drafting`：第3過程。`next_pending_gate` が triad-review でも、同じ phase の drafting 完了が `drafting_completed_gates` または `completed_gates` に記録されていないため、先に正本文書を更新する。`active_gate`、`phase`、`stage: drafting`、`required_feature_scope` を確認し、レビューを開始しない。
- `run_reopen_pending_gate`：第3過程。drafting 完了記録がある、または次 gate が triad-review 以外であるため、`next_pending_gate` の gate を実行する。alignment / approval 連鎖の再実施を含む。
- `wait_for_human_decision`：人間の判断待ち。判断なしに進めない。
- `finalize_reopen`：第4過程。最終確認、recheck クリア、in-progress の完了処理。
- `repair_workflow_state`：判定不能または状態破損。推測で進めず利用者へ報告する。

<a id="maintenance_in_progress"></a>

### `maintenance_in_progress`

通常ワークフローではなく、ワークフロー制御・運用規律・検査器などの保守作業が進行中である。`next_action.file` を読み、`required_action`、`allowed_scope`、`completion_conditions` に従う。通常の `stage` や `upstream_recheck` へ戻るのは、maintenance の完了条件を満たし、進行中ファイルを `stages/completed/` へ移してからである。

`next_action` と異なる作業へ入る場合、または `next` 判定自体の欠陥を直す場合は、ファイル編集前に `stages/in-progress/maintenance-<日付>-<短い名前>.yaml` を作成する。少なくとも `trigger`、`mainline_blocked_by`、`work_class`、`control_relation`、`allowed_scope`、`allowed_files`、`completion_conditions` を記録し、side track であることを明示する。保守作業を side-track として始める場合は `work_class: maintenance`、`control_relation: side-track` を使う。これを省略すると、本筋の作業順序を守るための修復作業自体が、記録されない手順逸脱になる。

本線 reopen 中の maintenance 完了 commit は、`stages/completed/maintenance-*.yaml` の `mainline_blocked_by` が現在の reopen in-progress ファイルを覆うことで許可される。本線 `stages/in-progress/reopen-*.yaml` は、maintenance のためだけに同伴 stage しない。

**maintenance を始める前の事前調査（in-progress YAML を作成する前に実施する）**

1. 変更対象ファイルと依存関係を確認し、影響範囲を特定する。
2. フィーチャー横断の影響がないことを確認する。
3. 先に解決すべきブロッカー（別の問題）が潜んでいないことを確認する。

事前調査の結果として次の開始条件をすべて満たした場合のみ maintenance を始める。

- 変更が局所的である（既存仕様境界を変えず、workflow 機構・承認・状態機械・`next --json` の意味を変えない）。
- 影響範囲が対象フィーチャーに閉じている。

いずれかを満たさない場合：

- 中核変更（仕様境界・workflow 機構を変える）の場合は reopen または新規 workflow として扱う。
- フィーチャー横断の影響がある場合は利用者にエスカレーションする。

開始条件を満たした場合、in-progress YAML を作成した後に最初に次の 3 行を宣言する。

```
変更分類: 局所
理由: <影響範囲と既存仕様境界への影響の説明>
手順: TDD 主導 / 文書のみ（lightweight self-check）
```

コード変更を伴う局所変更は TDD 主導（テスト先行）で進める。文書のみの変更は lightweight self-check で確認する。

### `reopen_classification_required`

完了済み workflow で、`intent`、feature-partitioning、`requirements`、`design`、`tasks` などの上流正本が後続成果物より新しい。単なる再確認として下流へ進めず、意味変更の有無と reopen 種別を分類する。`next_action.reopen_trigger` が候補を示す場合も、分類根拠を保存して `reopen-start` へ進む。

<a id="post_write_verification"></a>

### `post_write_verification`

書き込み後検証の対象となる未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` 全体を対象として検証する。

検証 manifest は `.reviewcompass/post-write-verification/*.yaml` に置く。`target_files`、`target_sha256`、`required_verifiers`、`completed_verifiers`、`unresolved_substantive_findings` を記録する。`verifications[]` がある場合、各 verifier は `target_files` 全体と対応する `target_sha256` を単一エントリで覆る必要がある。ファイルごとの分業は独立多重チェックではない。

API 経由の複数モデル検証を行う場合の標準手順：

```bash
.venv/bin/python3 tools/api_providers/prepare_post_write_review.py \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --source-material .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md \
  [--source-material <additional-source-material> ...] \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --criteria-id <criteria-id> \
  --change-summary "<change-summary>" \
  --review-question "<review-question>"

.venv/bin/python3 tools/api_providers/run_review.py \
  --variant post_write_verification_google \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --phase post_write_verification \
  --criteria-file .reviewcompass/evidence/review-runs/<run-id>/review-target.md \
  --prompt-manifest-path .reviewcompass/evidence/review-runs/<run-id>/prompt-manifest.yaml \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py list-pending \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py decide \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --finding-id <finding-id> \
  --final-label must-fix \
  --decision-reason "<reason>" \
  --decision-actor human \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/api_providers/review_triage.py write-manifest \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --out auto \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/check-workflow-action.py next --json
```

API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target と prompt manifest を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md> --prompt-manifest-path <prompt-manifest.yaml>` を実行することである。外側から `zsh -c` で包まない。API key は配布物や設定ファイルへ書かず、利用者の shell 初期化で読み込まれる環境変数から渡す。Claude Code などの操縦実行面では、子プロセスの `ANTHROPIC_API_KEY` と `GEMINI_API_KEY` が空文字列へ上書きされることが確認済みである。一方、`OPENAI_API_KEY` は同じ確認では上書きされていない。このため `run_review.py` / `run_role.py` entrypoint 内で、環境変数が未設定の場合に `~/.zshrc` を読み直して API key を補完する。補完後も key が得られない場合は API key 未設定として fail-closed する。

`prepare_post_write_review.py` は `review-target.md`、`review-target.yaml`、`prompt-manifest.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、source materials、target file contents、scope / out-of-scope、finding policy、機微情報チェック結果を含める。`prompt-manifest.yaml` には `review_prompt_materials.target_files` と `review_prompt_materials.source_materials` を `content_mode: full_text` と `content_sha256` 付きで記録する。機微情報らしい文字列を検出した場合、または prompt manifest audit が DEVIATION の場合は fail-closed し、外部 API review へ進まない。

`next_action.target_files` が複数ある場合は、`prepare_post_write_review.py` と `run_review.py` の両方で `--target` を複数回指定して同じ review-run に束ねる。API review-run の成否確認は、`review-target.md`、`review-target.yaml`、`prompt-manifest.yaml`、`review_summary.md`、`rounds.yaml`、`model-result-summary.yaml`、`raw/`、`parsed/`、`prompts/`、`target-manifest.yaml` が同じ `--review-run-dir` に生成され、`rounds.yaml` の `target_files`、`criteria_source_path`、`prompt_manifest_path`、provider、model、prompt/raw/parsed path が今回の対象と一致することで行う。

API 呼び出しが失敗した場合は、まず上の正本手順を再確認する。`import` エラー、`argparse` エラー、引数不一致は起動手順または実装の問題であり、外部送信ポリシーや provider 側障害と混同しない。`ConnectError`、名前解決失敗、接続不能が出た場合は sandbox network 制限の可能性を先に疑い、同じ正本コマンドをネットワーク実行が許可された実行面で再実行する。API key 未設定のエラーは `~/.zshrc` から対象 provider の環境変数が読み込まれているかを確認する。

`post_write_verification` では API 経路の variant を明示する。小規模既定は `--variant post_write_verification_google`、大規模または 3 系統検証が必要な場合は `--variant <post-write-api-variant>` として、`config/api-settings.yaml` の `context: post_write_verification` かつ API provider だけで構成された variant を選ぶ。CLI 経路を含む default variant に暗黙フォールバックしてはいけない。

API レビュー結果を得た場合は、raw 参照、モデル別要約、三段階トリアージ（`must-fix`／`should-fix`／`leave-as-is`）を利用者へまとめて提示する。`ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を `decide` する場合、または重要件を含む run から manifest を生成する場合は、承認を記録した `--approval-record` が必須である。承認レコードには `approved_by: user` または `approved_by: proxy_model`、`review_run_id`、`summary_presented_to_user: true`、`triage_presented_to_user: true`、`approved_finding_ids`、必要に応じて `approved_final_labels` を含める。`approved_by: proxy_model` の場合は、`proxy_model_id` と finding ごとの `proxy_decisions` を含め、各 decision file が raw response、候補案、採用案、判断理由、最終ラベルを保持する。

`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。manifest は post-write validation の途中記録ではなく、commit 直前の最終封印である。`triage.yaml` に `decision_status: human_required` が残る場合、重要件の利用者承認が確認できない場合、または review-run の target set に含まれない未コミット post-write target が残る場合は manifest を生成しない。manifest 作成後は対象ファイルを編集せず、stage / approval / commit へ直行する。

この生成停止条件は、現在の review-run から新しい最終 manifest を作る場合の規則である。既存の post-write manifest が現在の対象ファイルと一致し、かつ未解決の本質的指摘を含む場合は、`next --json` が `post_write_human_decision_required` と `next_action.manifest` を返す。

<a id="lightweight_self_check"></a>

### `lightweight_self_check`

notes / 履歴 / 判断材料の未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` を API post-write verification ではなく軽量自己精査で確認する。

軽量自己精査の対象は `docs/notes/` 配下と、単独変更の `TODO_NEXT_SESSION.md` とする。`docs/notes/` は議論記録、判断経緯、過去メモ、参考情報を置く場所として扱い、正本仕様・運用規律・レビュー判定そのものではないため、API review ではなく自己検査で確認する。`docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`stages/completed/` は正本または完了記録として厳格に扱う。notes から正本へ昇格する内容は、該当する正本ファイルへ移した時点で strict な `post_write_verification` 対象とする。

`TODO_NEXT_SESSION.md` は更新頻度が高い次セッション導線であり、進捗整理・次タスク・現在状態の更新だけなら API review ではなく軽量自己精査で扱う。ただし、同じ未コミット差分に strict な `post_write_verification` 対象が含まれる場合は、TODO も同じ strict 検証の `target_files` に同梱する。

軽量自己精査では、API review を呼ばず、次だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

完了記録は `.reviewcompass/post-write-verification/*.yaml` に置き、`required_verifiers` と `completed_verifiers` は `lightweight_self_check` とする。`target_files` と `target_sha256` は通常の post-write manifest と同じく対象全体を覆う。

`post_write_verification` 対象と `lightweight_self_check` 対象が混在する場合は、`post_write_verification` を優先する。strict 側が完了した後、軽量対象が残っていれば `lightweight_self_check` を返す。

<a id="post_write_policy_violation"></a>

### `post_write_policy_violation`

post-write-verification pending 中に禁止変更がある。通常ワークフローへ進まず、`next_action.forbidden_files` を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。

現行実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py`、`templates/`、または他の post-write 対象と混ざった `docs/disciplines/` 配下の変更があると逸脱になる。

<a id="post_write_human_decision_required"></a>

### `post_write_human_decision_required`

既存の post-write manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。

これは、現在の review-run で `triage.yaml` に `decision_status: human_required` が残ったまま新しい最終 manifest を生成する状態ではない。その場合は manifest 生成前に停止し、triage の判断または承認を先に解決する。

### `stage`

通常ワークフロー上の次タスクが決まっている。`feature`、`phase`、`stage` の示す作業だけを扱う。

`stage` が `triad-review` の場合、review-run の開始前に使用 variant と role ごとの path／provider／model を確定し、曖昧なまま開始しない。review-run に使うプロンプトは [[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）で設計する。API review-run 完了後は、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、raw 参照、モデル別要約、同根所見クラスタ、`must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案、重要件の平易な説明を利用者へ提示して停止する。詳細手順は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2` を正本とする。

### `cross_feature_stage`

機能横断段に進む。`feature` は `all_features` になる。`recheck_items` がある場合は上流変更の織り込みを含める。`required_inputs` に `unresolved_cross_scope_items` があり、`unresolved_count` が 0 より大きい場合は、`read_policy` に従って未消化の持ち越し所見だけを確認する。ReviewCompass では互換情報として `pending_cross_feature_findings` も返るが、一般化された判断根拠は `required_inputs` とする。

自律・並列で機能横断段を試行する場合は、通常の review-wave 完了判定に入る前に `autonomous-plan` を作成し、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で検査する。計画には `recheck_items` と `stages/feature-dependency.yaml` から分かる依存を明示し、上流 recheck 対象を下流判断より先に置く。同じ worktree で並列化してよいのは読取調査または差分を残さない確認に限る。新しい依存、暗黙依存、未記録依存、または上流 recheck の下流反映が必要だと分かった場合、その作業単位は停止し、機能横断段の実施記録に blocked として記録してから統合判断へ戻す。

機能横断段の実施記録は、単一 feature 配下に置かず `.reviewcompass/specs/_cross_feature/reviews/` に置く。標準ファイル名は `.reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md` とし、`feature: all_features`、対象 phase/stage、確認した feature 範囲、持ち越し件数、recheck 結果、実行した検証コマンド、判断結果を記録する。`_cross_feature` は実 feature ではなく、横断段成果物だけの名前空間である。

<a id="commit_stop_point"></a>

### `commit_stop_point`

通常 workflow の phase 終端または reopen 手続き上の停止点に到達している。`required_action: commit_stop_point` の場合、次 phase / 次 gate へ進まず、利用者の明示的な commit 指示を待つ。

利用者が commit を指示した直後は、Git index への追加（`git add`）や approval record を作る前に `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、理由と次に許可されている action だけを報告する。

通常 workflow では、`intent.approval` または `feature-partitioning.approval` が全 feature で完了し、該当 phase の workflow_state または成果物に未コミット変更がある場合に返る。`blocked_by.phase`、`blocked_by.stage`、`blocked_by.dirty_paths` を確認する。`commit-preflight` が `OK` を返した後に対象差分を `git add` し、guarded commit の通常手順へ進む。commit 後に作業ツリーが clean であれば、同じ停止点を返し続けず次 phase の action へ進む。

reopen 手続きでは、`reopen_in_progress` の `required_action: commit_stop_point` として返る。`blocked_by.kind` と `blocked_by.gate` を確認し、reopen 手続きファイルを含む停止点 commit を行う。

<a id="commit_mixing_risk"></a>

### `commit_mixing_risk`

commit unit が固定した対象外の staged file が混入している。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files`、`extra_staged_files`、`path` を確認する。

利用者に、対象外ファイルを別 commit unit / blocking unit へ分けるか、現在の commit unit を再作成してよいかを確認する。対象外ファイルを理由なしに同じ commit へ混ぜない。

<a id="commit_unit_stale"></a>

### `commit_unit_stale`

commit unit が現在の staged 内容と一致していない。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files` と `path` を確認する。

staged 内容を commit unit に合わせて戻すか、現在の staged 内容に合わせて commit unit を再作成する。古い commit unit のまま承認 record や commit execution delegation を作らない。

### `upstream_recheck`

完了済み workflow であっても、上流成果物が下流成果物より新しいため、下流へ進む前に再確認が必要である。`upstream_phase`、`phase`、`stage` を確認し、`phase.stage` に示された作業を次作業として扱う。たとえば intent 更新後は feature-partitioning の確認、requirements 更新後は design の再確認、tasks 更新後は implementation の再確認を先に行う。

この kind が返った場合、記憶や直前の会話から requirements、design、tasks、implementation へ飛ばない。必ず `next_action.phase` と `next_action.stage` に従い、上流から下流へ順に反映する。

<a id="feature_definition_required"></a>

### `feature_definition_required`

feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない（verdict OK）。

`next_action.reason`（立ち上げ案内の本文）と `current_state.feature_dependency_source`（解決元）を確認する。`feature_dependency_source` が null ならファイル自体が探索順（`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml`）のどこにも存在せず、ファイルパスが入っていればそのファイルはあるが `feature_order` キーが未定義または不正である。前者は分割結果の記録から、後者は既存ファイルへの `feature_order` キーの追記から始める。

新しい作業を始めず、intent と feature-partitioning を実施し、承認された分割結果（機能ごとの依存の主張と理由、順序の導出を含む）を `.reviewcompass/feature-dependency.yaml` の `feature_order` キーに記録する。記録後に `next` を再実行する。feature 立ち上げの手順は `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。

なお、`feature_order` と `depends_on` の整合違反（依存される機能が先に並んでいない、循環依存がある）は本 kind ではなく `unknown`／DEVIATION（fail-closed）になる。理由に従って `feature-dependency.yaml` を修正する。

### `completed`

全 workflow_state が完了している。通常の次タスクはない。

利用者指示により maintenance、reopen、または新規 workflow を開始できる。別作業を開始する前には、原則として `work-unit preflight-start` を実行し、`start_allowed` と `blocking_reasons` を確認する。maintenance を始める場合は、その後に `maintenance_in_progress` の事前調査と開始条件を確認する。

**completed からの作業開始分類**

| 分類 | 使う条件 |
| --- | --- |
| maintenance | 局所的な運用・検査器・手引き補修で、既存仕様境界や workflow 機構の意味を変えない。 |
| reopen | 既存正本の意味変更や下流再実施が必要で、既存 feature の責務内に収まる。 |
| 新規 workflow | 既存 feature の責務境界に収まらない新しい責務を導入する。 |

判断が分かれる場合は候補だけを提示し、人間判断を待つ。候補のまま `stages/in-progress/maintenance-*.yaml` を作成したり、reopen-start や新規 workflow の正本作成へ進んだりしない。

### `unknown`

状態判定できない。推測で進めず、`reasons` と `current_state` を利用者へ報告する。

## 3. 共通禁止事項

- `next` を実行せずに次作業を提案しない。
- `resume_in_progress`、`parent_resume_pending`、`reopen_in_progress`、`post_write_verification`、`post_write_policy_violation`、`post_write_human_decision_required` を通常ワークフローより後回しにしない。
- `lightweight_self_check` を通常ワークフローより後回しにしない。
- `reopen_classification_required` を「再確認で足りる」と独断して下流成果物を更新しない。
- `next_action` と異なる side track に入る場合、または `next` 判定自体を修復する場合は、maintenance in-progress を作らずに編集を始めない。
- 事前調査を省略して maintenance を始めない。影響範囲・依存関係・ブロッカーの確認が済んでいない状態で in-progress YAML を作成しない。
- spec.json の workflow_state 変更、commit、push は不可逆操作として扱い、対応する precheck サブコマンドを実行する。
- 検証者は `target_files` 全体を見る。ファイルごとの分業を独立多重チェックとして扱わない。
- 本質的指摘を独断で逐語的指摘に落とさない。迷う場合は利用者へ上げる。
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.
