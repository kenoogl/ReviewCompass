# 作業中メモの検証トリガー対応メモ

作成日: 2026-06-17

## 背景

作業中に生じた修正候補メモに対して API による post-write verification を反復した結果、メモの目的を超えて内容が肥大化し、作業体験が悪化した。

作業中メモは、仕様正本・設計正本・タスク正本・実装証跡ではなく、後続判断のための一時的な記録である。そのため、通常の post-write verification と同じ扱いにすると、INFO / WARN を逐次反映する流れが生じ、記録の軽さが失われる。

## 問題

現状の `next --json` は、未コミットの `docs/notes` を post-write verification 対象として検出し、メモの配置場所を区別しない。

その結果、次のような問題が起きる。

1. 作業中メモにも API review が走る。
2. INFO / WARN が「修正すべき指摘」として扱われやすい。
3. メモの目的が、候補記録から仕様文書化へずれる。
4. 利用者が求めた作業範囲を超えて検証ループが始まる。

## 方針

検証の重さは、まず配置場所で決める。

正本となるものは厳しく検証する。メモ程度のものは軽く検証する。この分類を中身の marker ではなく、置き場所の規約として表す。

初期方針:

- `docs/notes/working/` 配下は作業中メモ置き場とし、API post-write verification ではなく `lightweight_self_check` に回す。
- 既存の `docs/notes/*.md` は正本寄りメモと作業中メモが混在しているため、従来どおり post-write verification 対象のままとする。
- `docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`TODO_NEXT_SESSION.md`、`stages/completed/` は正本または完了記録として厳格に扱う。
- front matter や本文 marker による中身判定は、初期実装では採用しない。
- 判断に迷う配置は厳格側に倒す。

想定 action:

```json
{
  "kind": "lightweight_self_check",
  "required_action": "review_working_note_without_api",
  "target_files": [
    "docs/notes/working/2026-06-17-working-note-verification-trigger-policy.md"
  ],
  "reason": "作業中メモ置き場の変更であり、API post-write verification ではなく軽量自己精査を行う"
}
```

## 軽量自己精査の観点

作業中メモに対しては、API review ではなく LLM 自身が次の観点だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

## 実装候補

恒久化する場合の変更先候補:

- `docs/operations/WORKFLOW_NAVIGATION.md`
  - `lightweight_self_check` action の意味と扱いを書く。
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
  - `next_action_kind: lightweight_self_check` の effective prompt を追加する。
- `tools/check-workflow-action.py`
  - `docs/notes/working/` を軽量自己精査対象として action selection で分岐する。
- `tests/tools/test_check_workflow_action.py`
  - `docs/notes/working/*.md` が `post_write_verification` ではなく `lightweight_self_check` になることをテストする。
  - `docs/notes/*.md` が従来どおり `post_write_verification` になることをテストする。
  - `docs/notes/working/*.md` と strict 対象が混在する場合、strict 側を優先することをテストする。

## 未決事項

1. 軽量自己精査を完了済みとして記録する manifest を作るか、記録しない運用にするか。
2. `next --json` が既存の post-write manifest と軽量自己精査済みメモをどう区別するか。
3. 正本へ昇格する時点で、通常の API post-write verification を必須にするか。

## 今回の扱い

この文書自体は作業中の対応メモであり、仕様正本ではない。

したがって、API による post-write verification は行わず、軽量自己精査に留める。
