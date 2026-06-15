# commit 承認 nonce 化 SDD 実装計画メモ

## 位置づけ

本メモは、commit 承認レコードを staged 内容に束縛した nonce 承認方式へ強化するための SDD 着手前メモである。正本仕様ではない。正本化は `workflow-management` の requirements / design / tasks / implementation を正規手順で更新して行う。

## 背景

現状の commit 直前ゲートは `.reviewcompass/runtime/approvals/commit-approval.json` を検査し、`approved_action=commit`、`approved_by=user`、未消費、staged ファイル被覆、staged 内容と一致する `target_sha256` を要求する。

ただし、承認レコード自体を LLM が生成できる構造では、利用者の「コミット」発言と承認レコードの対応が弱い。2026-06-15 の試行では、staged 状態から nonce を作り、利用者が `コミット承認 <nonce>` と返した後に承認レコードを作成する運用で commit を実施した。この方式をプロジェクト全体の LLM 介在 commit に適用するかを検討する。

## SDD 分類案

- 対象 feature: `workflow-management`
- 対象要件: Requirement 4「不可逆操作の直前ゲート」
- 対象タスク: T-006「不可逆操作の直前ゲート機構」
- 分類案: R-0 相当
- 理由: intent や feature 分割の変更は不要。既存の「commit 直前ゲート」の目的に含まれる承認強化であり、Requirement 4 受入基準 5 の拡張として扱える。
- 下流影響: requirements を更新した後、design / tasks / implementation を順に再展開する。

`spec.json` の reopen / recheck フラグ差し戻し、`stages/in-progress/` の発行、仕様本文の変更は、利用者承認後に REOPEN_PROCEDURE に沿って実施する。本メモ作成時点では行わない。

## 目的

LLM 介在の commit に対し、承認を「現在 staged されているファイル集合と内容」に結びつけ、古い承認・別対象の承認・LLM による承認レコード自作を検出しやすくする。

## LLM 非依存方針

本機能は、操縦する LLM、provider、model に依存しない CLI / file contract として設計する。nonce 生成、challenge 保存、approval record 作成、commit gate 判定、consume は staged ファイル集合・staged blob hash・target digest・nonce・expiry・consumed 状態だけを入力にし、Claude / Codex / Gemini / OpenAI などの model 名や provider 名を判定条件に含めない。

LLM ごとの差異は、利用者への説明文やプロンプトの表現に限定する。gate 判定は機械状態のみを見る。これにより、デプロイ時に特定 LLM の runtime や応答形式へ依存しない。

ただし、本方式は「利用者が本当に UI 上で nonce を発話したこと」を暗号的に証明するものではない。今回の保証範囲は、承認を staged 内容に束縛し、古い承認・別対象の承認・対象差し替え後の commit を fail-closed で防ぐことである。より強い人間発話保証は、将来課題として UI 署名や agent runtime 由来の承認イベントを検討する。

## 非目的

- git commit 以外の不可逆操作へただちに拡張しない。
- push 承認方式は今回の実装範囲に含めない。
- UI や外部署名による人間発話の暗号的証明は今回の実装範囲に含めない。
- 既存の post-write verification や decision-source-lint の責務を置き換えない。

## 方式案

1. `prepare` で staged ファイル一覧と staged blob sha を読み、短い nonce と target digest を生成する。
2. `prepare` は `.reviewcompass/runtime/approvals/commit-approval-challenge.json` に challenge を保存する。
3. LLM は利用者へ nonce を提示し、利用者から `コミット承認 <nonce>` のような明示返答を得る。
4. `record` は challenge と現在 staged 状態を再検査し、nonce が一致し、target digest が変わっていない場合だけ `.reviewcompass/runtime/approvals/commit-approval.json` を作る。
5. commit 直前ゲートは approval record だけでなく challenge 由来の nonce / target digest / expiry / consumed 状態も検査する。
6. commit 成功後、approval record と challenge を消費済みにする。

## 検討する CLI 形

- `tools/check-workflow-action.py commit-approval prepare --json`
- `tools/check-workflow-action.py commit-approval record --nonce <nonce> --source-text <利用者発言> --json`
- `tools/check-workflow-action.py commit --rationale "..."`
- `tools/guarded-git-commit.py -m "..." --rationale "..."`

`record` は利用者発言全文を保存する場合でも、secret redaction 方針に従う。API key や token らしき値は approval record / log に残さない。

## 受入基準案

- `prepare` は staged ファイルがない場合に失敗する。
- `prepare` は staged ファイル一覧、ファイル別 `target_sha256`、全体 target digest、nonce、有効期限を challenge に保存する。
- `record` は nonce 不一致、challenge 不在、期限切れ、staged 内容変更、staged ファイル増減で fail-closed する。
- `record` は成功時のみ approval record を作る。
- commit 直前ゲートは nonce なし approval record を fail-closed する。
- commit 直前ゲートは approval record と challenge の target digest 不一致を fail-closed する。
- commit 成功後、approval record と challenge が消費済みになる。
- secret redaction テストで API key 風文字列が runtime approval / precheck log に残らないことを確認する。

## テスト方針

TDD で進める。まず `tools/check-workflow-action.py` と `tools/guarded-git-commit.py` の失敗テストを追加し、失敗を確認してから実装する。

最低限のテストケース：

- prepare 正常系
- prepare staged なし
- record 正常系
- record nonce 不一致
- record staged 変更
- record challenge 期限切れ
- commit gate nonce 欠落
- commit gate challenge / approval 不一致
- commit 成功後 consume
- secret redaction

## 限界

nonce 方式は、LLM が古い承認や別対象の承認を流用する失敗を防ぎやすくする。一方で、利用者発言が本当に外部 UI から来たことを暗号的に証明するものではない。より強い保証が必要な場合は、将来課題として UI 署名、agent runtime 由来の承認イベント、または外部 trust boundary を導入する。

## 正規手順

1. reopen 第1過程として分類記録を作成し、`workflow-management` の requirements 起点 R-0 として利用者承認を得る。
2. 承認後、`spec.json` と `stages/in-progress/` を REOPEN_PROCEDURE に沿って更新する。
3. requirements に Requirement 4 受入基準を追記する。
4. requirements の triad-review / review-wave / alignment / approval を実施する。
5. design に challenge / approval record / consume / redaction の詳細を追記する。
6. design の正規 gate を実施する。
7. tasks の T-006 にテスト要件と成果物を追記する。
8. tasks の正規 gate を実施する。
9. implementation は TDD で進める。テストのみ作成、失敗確認、テストコミット、実装、全テスト通過、post-write verification、commit の順に行う。

## 次の停止点

次は reopen 第1過程に進むかを利用者に確認する。承認があるまで、仕様本文・`spec.json`・`stages/in-progress/` は変更しない。
