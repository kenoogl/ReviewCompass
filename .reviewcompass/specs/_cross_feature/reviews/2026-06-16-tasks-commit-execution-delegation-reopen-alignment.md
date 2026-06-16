---
date: 2026-06-16
gate: stages/tasks.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-execution-delegation-formal-cli
decision: existing_sufficient
---

# tasks alignment（整合確認）：commit execution delegation formal CLI

reopen R-0 の第3過程、workflow-management tasks フェーズの alignment 段。Requirement 4 受入 8、design.md §不可逆操作の直前ゲートモデル §2.2、tasks.md の T-004／T-006／T-011、triad-review C1〜C7 の裁定、review-wave 判定、下流 implementation recheck 状態の整合を確認する。

## Requirement 4 受入 8 との整合

| 要件観点 | tasks での受け方 | 整合判定 |
| --- | --- | --- |
| 正式 CLI | T-004 に `commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json` を追加した。 | 整合。 |
| staged 内容承認との順序制約 | T-004 / T-006 に、同じ nonce の challenge と staged 内容承認 record が有効で現在 index と一致する場合だけ delegation record を作る責務を置いた。 | 整合。 |
| 別ファイル化 | T-006 に `.reviewcompass/runtime/approvals/commit-execution-delegation.json` 保存と `commit-approval.json` の staged 内容承認専用性を明記した。 | 整合。 |
| staged 内容への束縛 | T-006 完了条件に nonce、target digest、staged file set digest、staged content approval digest 等の全必須 field 生成・検証を明記した。 | 整合。 |
| stdin 正規化と許可文言 | T-004 / T-006 に UTF-8 stdin、末尾 LF、CR/CRLF/内部改行/NUL/空/空白/byte 上限/全角 Latin 拒否、許可文言完全一致を展開した。 | 整合。 |
| LLM 非依存 | T-006 / T-011 に禁止 LLM/provider/model 系 field、判定非依存、統合・回帰テストを明記した。 | 整合。 |
| gate 再検証 | T-006 に `--execution-actor llm` で challenge／staged 内容承認 record／delegation record／現在 index を commit gate 直前に再検証する責務を置いた。 | 整合。 |

## triad-review 裁定との整合

| cluster | 裁定 | tasks 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1 | must-fix | delegation record の全必須 field、別ファイル保存、`commit-approval.json` の staged 内容承認専用性を T-006 に明示した。 | 整合。 |
| C2 | must-fix | stdin 正規化・許可文言完全一致・拒否条件を T-004 / T-006 の責務とテスト要件へ明示した。 | 整合。 |
| C3 | must-fix | LLM/provider/model 系 field 拒否と非依存回帰テストを T-006 / T-011 に明示した。 | 整合。 |
| C4 | must-fix | 保存直前再検証、current index 再検証、actor 別 gate 挙動を T-006 に明示した。 | 整合。 |
| C5 | should-fix | T-011 が Req 4 受入 8 の一気通貫統合・回帰テストを担うことを明示した。 | 整合。 |
| C6 | should-fix | 案Aを新タスク化せず T-004/T-006/T-011 に展開する理由を tasks.md に追記した。 | 整合。 |
| C7 | should-fix | T-013 decision-source-lint と Req 4 受入 8 の責務分離を明記した。 | 整合。 |

## review-wave 判定との整合

- `2026-06-16-tasks-commit-execution-delegation-review-wave.md` は no_impact と判定し、他 6 機能への tasks 正本修正不要とした。
- tasks.md の変更は workflow-management の T-004／T-006／T-011 に閉じている。
- self-improvement と conformance-evaluation は workflow-management に依存するが、今回の tasks 更新で両機能の tasks 正本を変更する必要はない。

## 下流 recheck 状態との整合

- `.reviewcompass/specs/workflow-management/spec.json` は tasks alignment 時点で、tasks triad-review / review-wave まで完了、tasks approval / implementation を未完了としている。
- implementation では、TDD により `commit-approval delegate-execution`、delegation record schema、stdin 正規化、strict schema、atomic write、invalidate / consume、`--execution-actor llm` gate を具体実装へ展開する必要がある。

## 判定

- **decision：existing_sufficient**。
- tasks.md の更新は Requirement 4 受入 8、design.md §2.2、triad-review 裁定、review-wave no-impact 判定と整合している。
- 追加の tasks 改訂は不要。
- implementation の recheck は維持する。
