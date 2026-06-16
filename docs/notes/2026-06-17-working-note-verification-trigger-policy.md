# 作業中メモの検証トリガー対応メモ

作成日: 2026-06-17

## 背景

作業中に生じた修正候補メモに対して API による post-write verification を反復した結果、メモの目的を超えて内容が肥大化し、作業体験が悪化した。

作業中メモは、仕様正本・設計正本・タスク正本・実装証跡ではなく、後続判断のための一時的な記録である。そのため、通常の post-write verification と同じ扱いにすると、INFO / WARN を逐次反映する流れが生じ、記録の軽さが失われる。

## 問題

現状の `next --json` は、未コミットの `docs/notes` を post-write verification 対象として検出し、メモの性格を区別しない。

その結果、次のような問題が起きる。

1. 作業中メモにも API review が走る。
2. INFO / WARN が「修正すべき指摘」として扱われやすい。
3. メモの目的が、候補記録から仕様文書化へずれる。
4. 利用者が求めた作業範囲を超えて検証ループが始まる。

## 方針

検証対象の分類は、post-write verification の中ではなく、その手前の action selection で行う。

`next --json` は、書き込み後の未検証ファイルを見つけた時点で artifact class を判定し、作業中メモであれば通常の `post_write_verification` ではなく、軽量自己精査 action を返す。

想定 action:

```json
{
  "kind": "lightweight_self_check",
  "required_action": "review_working_note_without_api",
  "target_files": [
    "docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md"
  ],
  "reason": "作業中の修正候補メモであり、仕様正本ではないため API post-write verification ではなく軽量自己精査を行う"
}
```

## 軽量自己精査の観点

作業中メモに対しては、API review ではなく LLM 自身が次の観点だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

## artifact class の初期判定候補

軽量自己精査に回す候補:

- `docs/notes/*-improvement-candidates.md`
- `docs/notes/*-smell-inventory.md`
- `docs/notes/*-rollback*.md`
- front matter または見出しに `artifact_class: working_note` 相当の明示がある文書
- front matter または見出しに `verification_policy: self_check` 相当の明示がある文書

通常の post-write verification に回す候補:

- SDD の requirements / design / tasks / implementation 文書
- `docs/operations` の運用規約正本
- `stages/completed` の completed maintenance / reopen 記録
- review-run / post-write manifest
- commit guard や workflow guard の仕様・実装に直接関係する正本

## 仕様化候補

恒久化する場合の変更先候補:

- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
  - 作業中メモは原則 API post-write 対象にしないという運用規約を書く。
- `docs/operations/WORKFLOW_NAVIGATION.md`
  - `lightweight_self_check` action の意味と扱いを書く。
- `tools/check-workflow-action.py`
  - `next --json` の action selection で artifact class を判定する。
- `tests/tools/test_check_workflow_action.py`
  - 作業中メモが `post_write_verification` ではなく `lightweight_self_check` になることをテストする。

## 未決事項

1. artifact class をファイル名規則だけで判定するか、front matter を必須にするか。
2. 軽量自己精査を完了済みとして記録する manifest を作るか、記録しない運用にするか。
3. `next --json` が既存の post-write manifest と軽量自己精査済みメモをどう区別するか。
4. 正本へ昇格する時点で、通常の API post-write verification を必須にするか。

## 今回の扱い

この文書自体は作業中の対応メモであり、仕様正本ではない。

したがって、API による post-write verification は行わず、軽量自己精査に留める。
