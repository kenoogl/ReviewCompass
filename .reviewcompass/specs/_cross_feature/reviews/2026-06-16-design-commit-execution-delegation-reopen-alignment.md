---
date: 2026-06-16
gate: stages/design.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-execution-delegation-formal-cli
decision: existing_sufficient
---

# design alignment（整合確認）：commit execution delegation formal CLI

reopen R-0 の第3過程、workflow-management design フェーズの alignment 段。Requirement 4 受入 8、design.md §不可逆操作の直前ゲートモデル §2.2、triad-review C1〜C6 の裁定、review-wave 判定、下流 recheck 状態の整合を確認する。

## Requirement 4 受入 8 との整合

| 要件観点 | 設計での受け方 | 整合判定 |
| --- | --- | --- |
| 正式 CLI | design.md §2.2 で `tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin --json` を正式 CLI とした。 | 整合。argv に承認文を載せない要件と合う。 |
| staged 内容承認との順序制約 | challenge と staged 内容承認 record が存在し、未期限切れ・未消費・未 invalidated で、現在 index と一致する場合だけ delegation を作る。 | 整合。staged content approval より前の実行を fail-closed にしている。 |
| 実行代行承認の分離 | `commit-approval.json` へ追記せず、`.reviewcompass/runtime/approvals/commit-execution-delegation.json` に独立保存する。 | 整合。内容承認と実行代行承認を混同しない。 |
| staged 内容への束縛 | delegation record に nonce、target digest、staged file set digest、staged content approval digest を持たせる。 | 整合。別ファイル化しても別対象へ流用できない。 |
| fail-closed | 形式不正、unknown field、重複 delegation、期限切れ、差し替え、保存直前 race、secret 残留を拒否する。 | 整合。Req 2 / Req 4 の fail-closed 方針と一致。 |
| 許可文言 | stdin の UTF-8 text を正規化し、限定 phrase への完全一致だけを許可する。 | 整合。曖昧な作業継続文言を commit 実行代行承認へ誤用しない。 |
| LLM 非依存 | `llm` / `provider` / `model` 系 field を schema で拒否し、判定を nonce / digest / expiry / consumed / invalidated / instruction に限定する。 | 整合。利用する LLM に依存しない。 |

## triad-review 裁定との整合

| cluster | 裁定 | design 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1 | must-fix、利用者選択は案A | delegation record を別ファイル化し、staged 内容 binding を明示した。 | 整合。 |
| C2 | must-fix | invalidate 範囲、malformed record、duplicate record、atomic write、保存直前再検証を明記した。 | 整合。 |
| C3 | must-fix | delegation 作成直前と commit gate 直前の再検証、expiry race の fail-closed を明記した。 | 整合。 |
| C4 | should-fix | 末尾 POSIX LF 1 個だけ許容、CR / CRLF / 内部改行拒否、全角 Latin 拒否、句点処理を明記した。 | 整合。 |
| C5 | should-fix | strict schema、unknown field 拒否、`attestation_type` / `guarantee_scope` の controlled vocabulary を明記した。 | 整合。 |
| C6 | leave-as-is | source-document cross-reference は sign-off checklist 項目として扱い、設計本文の欠陥とはしなかった。 | 整合。 |

## 既存設計節との整合

| 既存設計節 | 関係 | 整合判定 |
| --- | --- | --- |
| §軽量版検査スクリプトモデル（Req 2） | `commit-approval delegate-execution` は既存検査スクリプトの commit approval 系入口に接続する。 | 整合。fail-closed 方針を強化する。 |
| §不可逆操作の直前ゲートモデル §2.1 | §2.1 は staged 内容承認、§2.2 は LLM 実行代行承認を扱う。commit gate で両者を照合する。 | 整合。責務分離されている。 |
| §session 跨ぎ状態管理モデル（Req 6） | delegation record は `.reviewcompass/runtime/approvals/` 配下の runtime 承認状態であり、`stages/in-progress/` の workflow 進行状態とは責務が別。 | 整合。 |
| §多層防御の位置付けモデル（Req 7） | 曖昧承認や古い承認の再利用を第1層 gate で遮断する。 | 整合。 |
| §Req 11 重要決定の出典検査モデル | Req 11 は重要決定の出典検査、Req 4 受入 8 は commit 実行代行承認の記録・検証で責務が別。 | 整合。 |

## review-wave 判定との整合

- `2026-06-16-design-commit-execution-delegation-review-wave.md` は no_impact と判定し、他 6 機能への design 正本修正不要とした。
- 今回の design 変更は workflow-management の不可逆操作直前 gate と runtime approval record に閉じている。
- self-improvement と conformance-evaluation は workflow-management に依存するが、今回の変更で両機能の design 正本を変更する必要はない。

## 下流 recheck 状態との整合

- `.reviewcompass/specs/workflow-management/spec.json` は design alignment 時点で、design review-wave まで完了、design approval / tasks / implementation を未完了としている。
- tasks では、TDD 対象の完了条件・テストケースへ delegation CLI、record schema、stdin normalization、strict schema、commit gate 再検証を展開する必要がある。
- implementation では、正式 CLI と guarded commit validation を TDD で実装する必要がある。

## 判定

- **decision：existing_sufficient**。
- design.md の §2.2 は Requirement 4 受入 8、triad-review 裁定、review-wave no-impact 判定、既存設計節と整合している。
- 追加の design 改訂は不要。
- tasks / implementation の recheck は維持する。
