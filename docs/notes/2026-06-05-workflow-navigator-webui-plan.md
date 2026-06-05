# ReviewCompass Navigator WebUI 構想メモ

作成日：2026-06-05

## 0. 位置づけ

本メモは、ReviewCompass の workflow navigation を WebUI で可視化する構想を整理する。対象は、静的ビューアから始め、将来は LLM 対話ペイン、ログ保持、実行補助を持つ独立アプリへ拡張できる Navigator である。

ここでいう Navigator は、単なる進捗表示ではない。ReviewCompass 本体が機械判定した現在位置、標準ルート、例外的な side track、復帰先を、人間が一目で把握できるようにする UI である。

## 1. 基本方針

Navigator は ReviewCompass 本体の内部ファイルを場当たり的に解釈しない。ReviewCompass Core が出力する機械可読な状態スナップショットを読み、その内容をグラフィックに描画する。

接続モデル：

```text
ReviewCompass Core
  - 状態判定
  - workflow 定義
  - current position 判定
  - side track / recovery 判定
  - evidence refs 収集
  - workflow-state snapshot export

Navigator WebUI
  - snapshot 読み込み
  - グラフ描画
  - 詳細ペイン
  - 根拠・ログ表示
  - side track / return point 表示
```

この分離により、UI は状態正本にならない。状態の真実源は引き続き ReviewCompass Core と `workflow_state` / `next --json` の判定であり、UI はその可視化レイヤーとして動く。

## 2. 任意アプリ構造への対応

開発対象アプリによって、機能軸と工程軸は異なる。したがって Navigator は ReviewCompass 固定の `requirements -> design -> tasks -> implementation` だけを前提にしない。

必要なのは、任意のノード、エッジ、レーン、状態、根拠、次アクションを描ける汎用ビューアである。

例：

```text
ReviewCompass:
Intent -> Requirements -> Design -> Tasks -> Implementation -> Review -> Triage

Web app:
Spec -> UI Design -> API -> Implementation -> Browser QA -> Release

Data analysis:
Question -> Dataset -> Cleaning -> Analysis -> Validation -> Report

LLM evaluation:
Prompt -> Model Runs -> Parsing -> Metrics -> Judgment -> Archive
```

このため snapshot schema は、段階名を固定せず、`nodes`、`edges`、`lanes`、`current`、`evidence_refs`、`return_to` を中心に設計する。

## 3. 外側・内側の二層構造

ReviewCompass の workflow は、外側の大工程と、内側の細かい判定・作業ステップの二層で見る必要がある。

例：

```text
Outer:
Intent -> Requirements -> Design -> Tasks -> Implementation -> Review -> Commit

Inner for Review:
Target -> Prompt -> Model Runs -> Raw Capture -> Parse -> Summary -> Triage
```

UI では、外側 workflow を常に表示し、選択中または現在位置の外側ノードについて内側 workflow を展開する。

```text
Outer Navigator:
Intent -> Requirements -> Design -> Review -> Commit

Inner Navigator:
Target -> Prompt -> Runs -> Parse -> Summary -> Triage
```

状態スナップショットでは、現在位置を二層で持つ。

```yaml
current:
  outer_node: review
  inner_node: summary
```

これにより、「全体のどこにいるか」と「今の工程の中でどこにいるか」を同時に表示できる。

## 4. 状態からの復帰可能性

ReviewCompass の重要な性質は、履歴の順番ではなく、機械判定できる状態から現在位置を復元できることである。

標準ルートを進めることが既定だが、ユーザが LLM に例外的な処理を指示しても、状態を最初から辿れば、次に何をすべきかは一意に決まる。

Navigator は次を同時に表示する。

- 標準ルート
- 機械判定された現在位置
- 例外的に触られた領域
- 標準ルートへの復帰点
- 次に必要な action

例：

```yaml
nodes:
  - id: tasks
    normative_status: current
    machine_verdict: incomplete
    observed_activity: present
    recovery_action: complete_tasks_acceptance
  - id: implementation
    normative_status: waiting
    observed_activity: present
    exception_flag: out_of_order_activity
```

UI は例外操作を失敗として叱るのではなく、現在の復帰点と必要な処理を静かに示す。

## 5. Side Track / BTW Track

正規 workflow の途中で、対象外の正本文書修正や補助的な処理が発生する場合がある。このとき Navigator は、その処理を side track として表示する。

既存の post-write-verification は、この原型である。正規 workflow 外の文書書き込みを検出し、post-write-verification を通常 workflow より優先し、manifest 完了後に通常 workflow へ戻る。

概念モデル：

```text
Main Track:
A -> B -> C -> D

Side Track:
B
  -> BTW: post-write verification
  -> return to C
```

side track は単なる会話上の脱線ではなく、次を持つ機械判定可能な状態である。

- `track_kind`
- `reason`
- `target_files`
- `manifest_status`
- `policy_violations`
- `return_to`
- `required_action`

例：

```yaml
active_track:
  kind: side_track
  id: post_write_verification
  label: Post-write Verification
  reason: post_write_target_dirty
  target_files:
    - docs/notes/example.md
  manifest_status: pending
  return_to:
    outer_node: implementation
    inner_node: review_wave
```

## 6. Git Tree の扱い

side track 中は git tree も状態入力にする。dirty tree を混乱として扱うのではなく、変更理由、検証対象、禁止変更、復帰先が機械的に説明できる状態として扱う。

小さい side track は同一 worktree のまま扱う。

```text
Git Tree: dirty
Active Track: Post-write Verification
Target Changes:
- docs/notes/example.md

Blocked Changes:
- tools/example.py

Return To:
implementation / review-wave
```

大きい side track、実装変更を含む side track、正規 workflow と並行したい side track は、将来的に別 branch または別 worktree へ分離する余地がある。ただし初期 Navigator は、同一 worktree 上で `git diff`、post-write 対象、manifest coverage、非対象変更を表示するところから始める。

## 7. SDD と TDD / Sandbox 探索

Navigator は SDD 一辺倒ではなく、TDD を仕様探索の手段として扱える必要がある。

仕様案を実行可能なテストに落とし、sandbox で試し、その結果を仕様へ反映する流れを、内側 workflow として表示できるようにする。

```text
Spec Draft
  -> Test Hypothesis
  -> Sandbox Trial
  -> Result Capture
  -> Spec Revision
  -> Acceptance Lock
```

このループにより、仕様は単なる静的文書ではなく、実験結果で鍛えられる仮説として扱える。Navigator は「テスト結果は存在するが仕様反映が未完了」のような状態も、現在位置として表示できる。

## 8. グラフィック方針

名称は Atlas ではなく Navigator とする。目的は地図帳のような静的俯瞰ではなく、現在位置、進路、復帰点を示すことだからである。

グラフィックは美しく、しかし装飾過多にしない。方向性は、Subway Map と System Monitor の混合である。

- 外側 workflow は大きな幹線として表示する。
- 内側 workflow は選択中ノードの拡大図として表示する。
- lane は機能軸やアプリ固有軸を表す。
- current node は輪郭、光量、サイズで強調する。
- completed / current / waiting / blocked / failed / side_track を色と形の両方で区別する。
- 再オープンや side track は戻り線や分岐線で表す。
- 詳細説明は右ペインへ逃がし、グラフ上のラベルは短く保つ。

初期実装では React + SVG が扱いやすい。SVG は線、ノード、ラベル、矢印、フォーカスリングを綺麗に制御でき、後からズーム、パン、アニメーションを追加しやすい。

## 9. 静的 Navigator MVP

最初の MVP は、操作 UI ではなく、状態スナップショットを読む静的 Navigator とする。

MVP の構成：

- 上段：外側 workflow
- 中央：現在または選択中の内側 workflow
- 右ペイン：選択ノードの状態、根拠、次 action、ログ
- 下部または側面：active side track / git tree status

MVP で扱う状態：

- `completed`
- `current`
- `waiting`
- `blocked`
- `failed`
- `side_track`
- `deviation`
- `unknown`

MVP の入力：

- ReviewCompass Core が出力する `workflow-state` snapshot
- evidence refs
- git tree summary
- post-write manifest summary

MVP の非目標：

- UI が状態を直接変更すること
- LLM 対話を実行すること
- 任意 workflow engine を作ること
- branch / worktree 自動分離を行うこと

## 10. 将来拡張

将来は次を検討する。

- LLM 対話ペイン
- 会話ログ保持
- review-run raw / parsed / triage の閲覧
- side track の開始・終了操作
- post-write manifest 生成補助
- workflow-state snapshot の live reload
- branch / worktree 分離の補助
- 複数アプリ横断の workflow comparison

ただし、最初の価値は「状態から現在位置と復帰点が一目で分かること」に置く。

