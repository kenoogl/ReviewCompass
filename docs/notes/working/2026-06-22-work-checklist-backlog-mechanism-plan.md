---
date: 2026-06-22
record_type: working-note
status: draft
topic: work-checklist-backlog-mechanism-plan
related:
  - docs/notes/working/2026-06-22-commit-push-turn-order-operation-note.md
  - docs/notes/working/2026-06-22-postwrite-prompt-mechanization-checklist.md
  - tools/check_workflow_action/commit_unit.py
---

# Work Checklist / Backlog 機構の実装計画

## 1. 背景

ReviewCompass の主軸は仕様駆動開発である。一方、実開発では TDD や探索的なアドホック開発も有効であり、これまでの開発でもその有効性が確認されている。

ただし、アドホック開発では次の問題が繰り返し発生した。

- 本線作業中に先行して直すべき別作業が見つかる
- その別作業の途中でさらに別処理が必要になる
- 作業中に発生した TODO、計画候補、不具合報告がメモや文書に散らばる
- 後から全項目を回収し、順序立てて整理することが難しい
- LLM 作業者の記憶や注意に依存し、作業の見通しが悪くなる

この問題への対策として、正式 workflow より小さい単位で、作業チェックリストを機械可読に管理する仕組みを導入する。

## 2. 目的

目的は、大きな workflow を増やすことではない。

目的は、作業単位ごとに次を機械的に見えるようにすることである。

- 今どの作業をしているか
- 何が未完了か
- どの項目が active / done / blocked か
- 途中で発生した追加作業がどこに保存されたか
- 分岐作業から戻る条件は何か
- commit 前に未回収項目が残っていないか

これにより、LLM の注意力に頼らず、利用者も現在状態を確認できるようにする。

## 3. 構成

### 3.1 Work Checklist

Work checklist は、現在進めている work unit 内の実行リストである。

配置:

```text
.reviewcompass/runtime/work-units/checklists/
```

性質:

- mutable な実行状態
- active item / pending item / blocked item を持つ
- child checklist への分岐を記録する
- close 時に未完了 item があれば fail-closed する
- close 成功後は runtime から削除し、進行中リストに残さない

### 3.2 Checklist Evidence

Checklist evidence は、完了した checklist の証跡である。

配置:

```text
.reviewcompass/evidence/work-units/checklists/
```

性質:

- 完了時 snapshot の正本
- provenance の証跡
- 後から作業経路を説明するために保持する
- close 成功後、完了済み checklist は runtime から evidence へ移動したものとして扱う
- 対象アプリへの deploy には含めない

### 3.3 Backlog

Backlog は、正式 workflow に乗せる前の計画候補、TODO 候補、不具合報告を一元管理する場所である。

配置:

```text
.reviewcompass/backlog/index.yaml
.reviewcompass/backlog/plans/
.reviewcompass/backlog/issues/
.reviewcompass/backlog/todos/
```

性質:

- 未採択候補の台帳
- 利用者が後から一元確認できる
- checklist とは分ける
- workflow へ昇格、却下、保留を記録できる

## 4. Deploy Policy

`.reviewcompass` 配下であっても、すべてが deploy 対象ではない。

配布対象:

```text
.reviewcompass/guidance/**
```

配布しない対象:

```text
.reviewcompass/runtime/**
.reviewcompass/evidence/**
.reviewcompass/backlog/**
```

理由:

- runtime は実行状態であり対象アプリへ持ち込むべきではない
- evidence は ReviewCompass 自身または実行時の証跡であり、対象アプリへ持ち込むべきではない
- backlog は開発中の計画候補であり、対象アプリへ持ち込むべきではない

したがって、実装時には deployment scrub / export policy の検査を含める。

## 5. MVP

### 5.1 `work-checklist`

最小 CLI:

- `work-checklist start`
- `work-checklist add-item`
- `work-checklist set-status`
- `work-checklist branch`
- `work-checklist status`
- `work-checklist close`

最小 schema:

```yaml
schema_version: work-checklist-v1
checklist_id: checklist-2026-06-22-001
unit_id: unit-2026-06-22-001
title: 作業チェックリスト機構の実装
status: active
created_at: null
provenance:
  created_by: llm
  source_ref: conversation:user
  reason: 作業見通しと抜け漏れ防止
items:
  - id: C1
    title: red test を作成する
    status: pending
    checked: false
    child_checklist_id: null
progress:
  total: 1
  done: 0
  active: 0
  pending: 1
  blocked: 0
  active_item_ids: []
  blocked_item_ids: []
```

### 5.2 `work-backlog`

最小 CLI:

- `work-backlog add-plan`
- `work-backlog add-issue`
- `work-backlog add-todo`
- `work-backlog list`
- `work-backlog show`
- `work-backlog promote`
- `work-backlog reject`

最小 index schema:

```yaml
schema_version: reviewcompass-backlog-index-v1
items:
  - id: plan-2026-06-22-001
    kind: plan
    title: checklist 機構導入計画
    status: candidate
    path: .reviewcompass/backlog/plans/plan-2026-06-22-001.yaml
    source_unit_id: unit-2026-06-22-001
    created_at: null
```

## 6. TDD 方針

実装は TDD で進める。

Phase 0: deploy policy red test

- `.reviewcompass/guidance/**` は deploy 対象に含める
- `.reviewcompass/runtime/**` は deploy 対象から除外する
- `.reviewcompass/evidence/**` は deploy 対象から除外する
- `.reviewcompass/backlog/**` は deploy 対象から除外する

Phase 1: checklist red test

- checklist YAML が `.reviewcompass/runtime/work-units/checklists/` に作られる
- `schema_version / checklist_id / unit_id / provenance / items` がある
- item を追加できる
- item status を `pending / active / done / blocked` で更新できる
- blocked item から child checklist を作れる
- 未完了 item がある場合 close できない
- checklist YAML 自体に `checked` と `progress` が残り、人が直接読んでも進捗が分かる
- close 成功時に `.reviewcompass/evidence/work-units/checklists/` へ snapshot を移動する
- close 成功後、`.reviewcompass/runtime/work-units/checklists/` に完了済み checklist を残さない

Phase 2: backlog red test

- `.reviewcompass/backlog/index.yaml` が機械生成される
- plan / issue / todo の item YAML が機械生成される
- index と item YAML が相互参照できる
- promote / reject の判断が記録される

Phase 3: workflow visibility

- `workflow-snapshot` に active checklist を出す
- `workflow-snapshot` に backlog 件数を出す
- 必要なら `next --json` の current_state に active checklist summary を出す

## 7. Commit Unit との関係

今回実装済みの commit unit guard は、staged 内容の混線を防ぐ。

Work checklist / backlog は、それより手前で作業者の認知負荷を下げる。

- checklist: 今やる作業項目を見える化する
- backlog: 後で扱う候補を見える化する
- commit unit: commit 候補の混線を機械的に遮断する

この 3 つを組み合わせることで、アドホック開発を禁止せず、混線と抜け漏れを減らす。

## 8. 実装時の注意点

- checklist に将来候補を詰め込まない
- backlog に現在作業の進捗状態を詰め込まない
- `.reviewcompass/backlog/` は deploy 対象にしない
- runtime / evidence / backlog は対象アプリへの deploy 前に scrub する
- YAML は provenance を持つ
- 手書きで増やさず、CLI で生成する
- close / promote / reject は判断履歴を残す

## 9. 次作業

1. この計画を commit する
2. Phase 0 の deploy policy red test を作る
3. 失敗を確認して commit する
4. deploy scrub / export policy を実装する
5. checklist / backlog の red test へ進む
