# next --json と effective prompt 強制の締め直しメモ

作成日: 2026-06-17

## 背景

`next --json` は、現在状態から唯一の workflow action を返すための正本 selector である。

当初設計では、`next --json` の返値が分かった時点で、その action に必要な短い effective prompt を読み、LLM はその prompt と `next_action` の範囲内で作業する想定だった。

しかし直近の作業では、`next --json` の返値を確認しても、返された `effective_prompt_path` を明示的に読まず、過去文脈や LLM 判断で作業を進める場面があった。これは `next --json` の一意性と同じく、ワークフローの要となる部分が緩んでいる兆候である。

## 中核原則

1. `next --json` は唯一の workflow action selector である。
2. workflow 上の次作業は、`next --json` の返値だけから決める。
3. `next --json` の返値には、その action に対応する `effective_prompt` が必ず付く。
4. LLM は action 実行前に、`effective_prompt_path` の本文を読む。
5. `effective_prompt` がない、読めない、広すぎる、壊れている場合は作業しない。
6. `prompt_source_refs` は根拠参照であり、LLM が毎回広く読む対象ではない。
7. 他サブコマンドの JSON 出力は状態更新結果であり、次作業選択の正本ではない。次に何をするかは、必ず再度 `next --json` で決める。

## 観測されたズレ

1. `next --json` の返値に `effective_prompt_path` が出ていても、LLM がそれを読む運用が徹底されていない。
2. `effective_prompt_loaded=true` は、prompt を生成できたことを示すだけで、LLM が読んだ証跡ではない。
3. `WORKFLOW_DISCIPLINE_MAP.yaml` にない action kind / required_action / stage の組み合わせが存在する可能性がある。
4. `prompt_source_refs` にアンカーが付いていても、現行実装はファイル全体を束ねている可能性があり、「短い prompt」という意図から外れる。
5. `next --json` 以外のサブコマンドが `next_action` 形式を返すため、それを次作業 selector と誤認しやすい。

## 修正候補

1. `next --json` の返値に `effective_prompt` がない場合は fail-closed にする。
2. `effective_prompt_loaded=false` は現行どおり fail-closed とし、対象を全 action に広げる。
3. `WORKFLOW_DISCIPLINE_MAP.yaml` の coverage audit を追加する。
   - `next --json` が返し得る `kind`
   - `reopen_required_action`
   - `workflow_stage`
   - 将来追加される `required_action`
4. `effective_prompt_path` の読了証跡を runtime に記録する。
   - action digest
   - prompt path
   - prompt sha256
   - read_at
   - actor
5. 編集、review 実行、phase 更新、commit の前に、現在 action の effective prompt 読了証跡を guard で確認する。
6. アンカー付き `prompt_source_refs` は、該当節だけを抽出して prompt を短くする。
7. `next --json` 以外のサブコマンド出力には、「これは次作業 selector ではない」ことを明示する。
8. `next --json` の action selection と effective prompt enforcement を SDD に反映する。

## 最初に確認すべき箇所

- `docs/operations/WORKFLOW_NAVIGATION.md`
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`

## 受け入れ条件候補

1. `next --json` が返す全 action に `effective_prompt` が付く。
2. `effective_prompt` の元資料欠落は `DEVIATION` になる。
3. `WORKFLOW_DISCIPLINE_MAP.yaml` に未登録の action kind をテストで検出できる。
4. LLM が effective prompt を読んだ証跡なしに、編集・review 実行・phase 更新・commit へ進めない。
5. prompt source がアンカー付きの場合、effective prompt は該当節に限定される。
6. 他サブコマンドの結果 JSON は、次作業 selector ではないことが明示される。

## 今回は実施しないこと

- SDD 修正
- `next --json` 実装修正
- guard 修正
- effective prompt 読了証跡の実装

このメモは、ワークフロー中核の締め直し候補を記録するための作業中メモである。
