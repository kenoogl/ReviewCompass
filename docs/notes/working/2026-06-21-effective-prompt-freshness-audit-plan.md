---
date: 2026-06-21
record_type: working-note
status: draft
topic: effective-prompt-freshness-audit
related:
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
  - tools/check_workflow_action/effective_prompt_builder.py
  - tools/check_workflow_action/prompt_audit.py
  - docs/notes/working/2026-06-21-workflow-operation-mechanization-improvement-plan.md
---

# Effective Prompt 監査開発計画

## 1. 背景

現在の workflow は、`next --json` で現在地点を一意に得て、その地点で読むべき effective prompt を返す形に近づいている。effective prompt は複数の元文書から生成される派生物であり、今後は各地点で読むべき固定入力として扱われる。

この構造では、元文書が変わったときに対応する effective prompt も更新されなければならない。更新されていない effective prompt を読ませると、LLM は古い規律や古い操作方針に従って処理してしまう。

そのため、後続の機械化を進める前に、まず effective prompt と生成元文書の同期状態を検査する監査の仕組みを整備する。

## 2. 現状評価

既存の `prompt_audit.py` は、主に次を確認している。

- manifest の必須構造があること
- `decision_point` や `postconditions` の語彙が許容範囲にあること
- `source_artifacts` に path と `sha256:<hex>` があること
- source path が存在すること
- language task に machine/state mutation instruction が混入していないこと
- completion 時の follow-up が直接操作指示になっていないこと

一方で、今回重視する監査としては不足がある。

- `source_artifacts[].sha256` が現在の元文書内容と一致するかを検査していない
- `WORKFLOW_DISCIPLINE_MAP.yaml` から現在期待される source refs と、保存済み effective prompt / manifest の source refs が一致するかを検査していない
- Markdown effective prompt 本文が、現在の元文書から再生成した期待本文と一致するかを検査していない
- stale effective prompt を `next --json` の安全性判定へ接続していない
- stale を検出したときの再生成導線が明確でない

## 3. 目的

effective prompt を固定入力として扱えるようにするため、次を機械的に保証する。

1. effective prompt が現在の元文書から生成されたものか分かる。
2. 元文書変更後に effective prompt が古いままなら検出できる。
3. stale な effective prompt が返された状態で通常作業へ進まない。
4. stale 検出後に、どの prompt を再生成すべきか分かる。
5. 元文書変更と effective prompt 更新漏れを commit / CI / precheck のどこかで止められる。

## 4. 監査対象

初期対象は次に絞る。

- `.reviewcompass/runtime/effective-prompts/*.prompt.md`
- structured effective prompt manifest が存在する場合の manifest
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- `next --json` が返す `next_action.effective_prompt`
- `prompt_source_refs`
- `required_disciplines`
- source file の現在 SHA

レビュー用 prompt や proxy 判断 prompt の監査は、後続計画へ回す。まずは workflow 地点用 effective prompt の鮮度監査に集中する。

## 5. 監査仕様

### 5.1 Source Freshness

保存済み source artifact の SHA と、現在のファイル内容の SHA を比較する。

判定:

- 一致: `fresh`
- 不一致: `stale_source`
- 参照先なし: `missing_source`
- SHA 記録なし: `missing_source_sha`

### 5.2 Source Set Consistency

現在の `WORKFLOW_DISCIPLINE_MAP.yaml` と `next_action` から期待される `prompt_source_refs` を算出し、保存済み effective prompt / manifest の source refs と比較する。

判定:

- 一致: `source_set_ok`
- 余分な source: `unexpected_source`
- 不足 source: `missing_expected_source`
- 順序が意味を持つ場合の順序違い: `source_order_mismatch`

### 5.3 Rendered Prompt Consistency

現在の元文書から effective prompt を再レンダリングし、保存済み prompt 本文の SHA と比較する。

判定:

- 一致: `rendered_prompt_ok`
- 不一致: `rendered_prompt_stale`
- 再生成不可: `render_failed`

この判定では、生成時刻や非決定的なメタデータを本文に含めないことが前提になる。含める場合は比較対象から除外する canonicalization が必要。

### 5.4 Next Integration

`next --json` が返す effective prompt について、少なくとも次の状態を返せるようにする。

```yaml
effective_prompt:
  effective_prompt_loaded: true
  freshness:
    verdict: OK | WARN | DEVIATION
    status: fresh | stale | missing | render_mismatch
    checked_at: null
    stale_reasons: []
```

初期実装では `next --json` の既存互換を壊さず、`freshness` を追加情報として出す。通常作業を止める条件は段階導入する。

## 6. 実装順序

### Phase 0: 現状固定テスト

現在の `prompt-audit` の動作を壊さないため、既存 manifest 監査の代表ケースをテストで固定する。

### Phase 1: Source SHA 監査

`source_artifacts[].sha256` と現在のファイル SHA を比較する read-only 関数を追加する。

受入条件:

- SHA 一致で OK
- SHA 不一致で DEVIATION
- source file 不在で DEVIATION
- `sha256:` prefix なしは既存どおり DEVIATION

### Phase 2: Source Set 監査

`WORKFLOW_DISCIPLINE_MAP.yaml` と decision point から期待 source refs を算出し、保存済み source set と比較する。

受入条件:

- 期待 source が不足していれば DEVIATION
- 余分な source は初期段階では WARN、固定運用後は DEVIATION
- map にない判定点は DEVIATION

### Phase 3: Rendered Prompt 監査

現在の元文書から prompt を再生成し、保存済み prompt の SHA と比較する。

受入条件:

- 同一入力なら同一 SHA になる
- 元文書を変更すると stale を検出する
- prompt 本文だけ変更しても render mismatch を検出する

### Phase 4: next --json 連携

`next --json` が返す effective prompt に freshness 結果を含める。

受入条件:

- fresh なら従来どおり進める
- stale なら `next_action` に stale reason が出る
- missing source は fail-closed

### Phase 5: 再生成導線

stale な prompt を再生成する専用コマンドを追加する。

候補:

```bash
.venv/bin/python3 tools/check-workflow-action.py prompt-audit --refresh <decision-point>
.venv/bin/python3 tools/check-workflow-action.py operation-prompt regenerate-effective-prompt --decision-point <id>
```

最終名は既存 operation registry との整合を見て決める。

### Phase 6: commit / CI 接続

元文書や discipline map を変更した commit で、対応する effective prompt の更新漏れを止める。

初期は WARN、固定運用後は DEVIATION に上げる。

## 7. テスト方針

TDD で進める。

最初に追加するテスト:

1. manifest の source SHA が現ファイルと一致する正常系
2. source SHA 不一致の stale 検出
3. source file 不在の missing 検出
4. discipline map 上の期待 source 不足検出
5. regenerated prompt と保存済み prompt の SHA 不一致検出
6. `next --json` が stale 情報を返すケース
7. stale 状態で通常作業へ進ませないケース

## 8. 停止条件

この監査開発は、次を満たしたら一区切りとする。

- 現在の effective prompt の fresh / stale を read-only に判定できる
- 元文書変更後の更新漏れを機械的に検出できる
- stale の理由と対象 prompt が利用者に説明できる
- 再生成すべき対象が機械的に特定できる
- 後続の operation 機械化計画が、この監査結果を前提にできる

## 9. 未決事項

- Markdown prompt と structured manifest のどちらを正本にするか
- 生成時刻など非決定的要素を prompt に含めるか
- stale を最初から DEVIATION にするか、段階的に WARN へ置くか
- `next --json` が stale を返した場合、通常作業を完全停止するか、再生成 action を返すか
- 過去 review-run に記録された effective prompt は凍結証跡として扱うため、freshness 監査対象から除外するか

## 10. 結論

effective prompt を各地点で読む固定入力として運用するなら、最初に整備すべきなのは生成や運用の拡張ではなく監査である。監査がないまま operation 機械化を広げると、古い prompt を正しいものとして読ませる危険が増える。

したがって、後続の処理機械化改善は、この freshness audit を先に実装してから進める。
