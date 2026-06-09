---
run_id: 2026-06-09-existing-system-sdd-tasks-all-features-review-run
phase: tasks.triad-review
status: approved_for_fix
created_at: 2026-06-09
review_run_dir: .reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-all-features-review-run
---

# Tasks triad-review トリアージ要約

## 実行結果

3 役レビューは完了した。

| 役割 | モデル | 件数 | 主な結果 |
|---|---|---:|---|
| primary | claude-sonnet-4-6 | 10 | ERROR 1、WARN 4、INFO 5 |
| adversarial | gpt-5.4 | 1 | ERROR 1 |
| judgment | gemini-3.1-pro-preview | 2 | WARN 2 |

## 同根クラスタ

### C1：間接 feature の tasks 段確認証跡が不足

- 対応所見：
  - claude-sonnet-4-6 primary 005
  - claude-sonnet-4-6 primary 006
  - claude-sonnet-4-6 primary 010
- 推奨判断：must-fix
- 平易な説明：今回の review は全 7 feature が対象だが、tasks 段で foundation、runtime、evaluation、analysis、self-improvement を実際に確認したという記録が薄い。直接変更が不要でも、「確認した結果、変更不要」と明示しないと gate を閉じにくい。
- 推奨対応：tasks review-wave へ進む前に、5 つの間接 feature について tasks.md 本体変更が必要かを feature ごとに記録する。必要なら該当 feature の tasks.md を reopen する。

### C2：foundation が共有 schema/state contract を持つかの確認

- 対応所見：
  - claude-sonnet-4-6 primary 004
  - claude-sonnet-4-6 primary 005
  - gemini-3.1-pro-preview judgment 001
- 推奨判断：should-fix
- 平易な説明：workflow-management T-008 は `drafting_completed_gates` や `downstream_impact_decisions` を扱う。これが workflow-management 内だけの状態スキーマなら WM tasks で足りるが、foundation が共有 schema/state contract を所有するなら foundation tasks.md にも作業が必要になる。
- 推奨対応：foundation tasks.md を確認し、共有 schema/state contract の所有が foundation にあるかを判定する。foundation 所有なら foundation tasks.md を reopen して追記する。WM 内部所有なら「foundation 変更不要」の根拠を記録する。

### C3：analysis が T-016 出力を読む必要があるかの確認

- 対応所見：
  - gemini-3.1-pro-preview judgment 002
- 推奨判断：should-fix
- 平易な説明：conformance-evaluation T-016 は新しい候補出力を作る。analysis が conformance output consumption を所有しているなら、その新出力を読む task が analysis に必要かもしれない。
- 推奨対応：analysis tasks.md を確認し、T-016 の出力を analysis が正式に消費するかを判定する。消費するなら analysis tasks.md を reopen して追記する。今回は CE→WM の手続き引き渡しだけで analysis 消費がないなら「analysis 変更不要」の根拠を記録する。

### C4：CE T-016 から WM T-007 への handoff 明示

- 対応所見：
  - claude-sonnet-4-6 primary 007
- 推奨判断：should-fix
- 平易な説明：CE T-016 は tasks.md を直接書き換えず、候補を WM に渡す。tasks-phase conflict の候補が出たとき、WM T-007 の受け皿判定へ渡る道筋が tasks.md 上でも明確だと安全。
- 推奨対応：CE T-016 または WM T-007/T-011 に、`downstream_impact_candidate` が WM reopen へ渡ることを明記する。

### C5：review-target 出力形式の指摘

- 対応所見：
  - gpt-5.4 adversarial 001
- 推奨判断：leave-as-is
- 平易な説明：review-target 末尾は「少なくとも severity、target_location、description、rationale、verifying_commands を含める」と書いており、実際の要求は矛盾していない。所見はレビュー実行側プロンプトとの読み違いの可能性が高い。
- 推奨対応：今回の tasks 正本修正の blocker にはしない。ただし後続で review-target テンプレートを整理する余地はある。

### C6：そのままでよい確認事項

- 対応所見：
  - claude-sonnet-4-6 primary 001
  - claude-sonnet-4-6 primary 002
  - claude-sonnet-4-6 primary 003
  - claude-sonnet-4-6 primary 008
  - claude-sonnet-4-6 primary 009
- 推奨判断：leave-as-is
- 平易な説明：CE Requirement 10 / XDI-CE-002、WM Requirement 9 / XDI-WM-002、CE/WM の責務境界、drafting-before-review の構造はおおむね妥当と見られている。

## 承認判断の選択肢

推奨は、C1 を must-fix、C2〜C4 を should-fix、C5〜C6 を leave-as-is とする判断である。

承認された場合の次作業は、C1〜C4 の反映である。特に C1 は、tasks triad-review を閉じる前に、間接 feature 5 件の tasks 段影響判断を記録する必要がある。

## 利用者承認後の反映

2026-06-09 の利用者発言「承認」により、次の判断で反映した。

- C1：must-fix。全 7 feature の tasks 段影響判断を `tasks-impact-decisions.md` に記録した。
- C2：should-fix。foundation の共有 schema には昇格せず、`stages/in-progress.schema.json` を workflow-management T-008 所有の正本とする旨を workflow-management tasks.md に追記した。
- C3：should-fix。analysis は今回の T-016 出力を正式な reporting input としては消費しないため tasks.md 本体変更不要と判断し、その根拠を `tasks-impact-decisions.md` に記録した。
- C4：should-fix。CE T-016 から WM T-007 への handoff と、tasks phase 候補の reopen pending gate 変換を CE/WM tasks.md に追記した。
- C5/C6：leave-as-is。

反映後は r2 review-run で must-fix/should-fix 解消を確認する。
