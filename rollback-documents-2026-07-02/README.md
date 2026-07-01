# 中断した reopen 作業から退避した文書

## 経緯

このディレクトリは、`e1c5a4ac` へ戻す前に作成されていた計画・証跡・作業経緯の文書を退避したものです。

中断対象は `workflow-management` の reopen 作業です。design review へ進む過程で、review protocol の機械処理、prompt quality の扱い、review-run の操作選択などが不安定になり、reopen 作業を継続せず戻す判断になりました。

`e1c5a4ac` へ checkout する前の状態は、次のコミットとして保存・push 済みです。

- `6f5b6101c96ae2491f04778f3551c6718af314af`
- `Checkpoint interrupted reopen work`

その後、作業ツリーを次のコミットへ戻しました。

- `e1c5a4ac2e550e6dd148b2cc42f722463c895ba8`
- `Initialize reopen-start edited phase scope`

この地点から、次の作業ブランチを作成しました。

- `codex/e1c5a4ac-recovered-documents`

## 目的

ここに置いた文書は、元の active な場所へ復元したものではありません。壊れた reopen state をそのまま有効な workflow state として持ち越さず、有用な動機・計画・証跡だけを後で参照できるようにするための退避資料です。

重要なのは、この期間に変更されたコードそのものではなく、なぜその作業が必要だと判断されたのかを示す文書・作業記録です。

## 内容

- `.reviewcompass/backlog/index.yaml`
- `.reviewcompass/backlog/plans/plan-2026-07-01-user-facing-output-minimality-policy.yaml`
- `.reviewcompass/evidence/sessions/2026-06-30-codex-019f18da-ed8b-7e93-8660-d9bad4b06d0e.md`
- `.reviewcompass/evidence/sessions/2026-07-01-codex-019f1ccc-c3b9-7e11-b9b5-f04d85278406.md`
- `docs/sessions/auto-2026-06-30-codex-019f18da-ed8b-7e93-8660-d9bad4b06d0e.md`
- `docs/sessions/auto-2026-07-01-codex-019f1ccc-c3b9-7e11-b9b5-f04d85278406.md`
- `stages/completed/maintenance-2026-07-01-required-prompt-changes-criteria-mechanization.yaml`
- `stages/completed/maintenance-2026-07-01-review-execution-spec-role-assignment.yaml`
- `stages/completed/maintenance-2026-07-01-triad-review-default-variant-resolution.yaml`
- `stages/completed/maintenance-2026-07-01-triad-review-protocol-runner.yaml`
- `stages/completed/maintenance-2026-07-01-user-facing-output-minimality-plan.yaml`
- `stages/completed/maintenance-2026-07-02-checkpoint-interrupted-reopen-work.yaml`
- `stages/in-progress/reopen-procedure-2026-07-01.yaml`

## 注意

- 元の起点 plan である `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml` は `e1c5a4ac` 時点ですでに存在していたため、ここには重複して置いていません。
- このディレクトリは rollback 後の参照資料であり、active な workflow state として扱わないでください。
