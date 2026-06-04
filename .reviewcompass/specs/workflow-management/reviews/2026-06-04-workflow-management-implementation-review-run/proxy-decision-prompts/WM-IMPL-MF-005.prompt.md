# Proxy decision request: WM-IMPL-MF-005

あなたは ReviewCompass の triad-review 後の proxy_model 判断担当です。
実装はせず、下記の重要所見クラスタについて採用案、棄却案理由、最終ラベルを決めてください。

## 対象クラスタ

- cluster_id: WM-IMPL-MF-005
- title: 自律並列計画で main_session/same_worktree のAPI並列をどう扱うかが曖昧
- source_models: gpt-5.4
- source_raw_paths: raw/gpt-5.4.round-1.txt
- finding_ids: 2026-06-04-workflow-management-implementation-review-run-gpt-5.4-adversarial-001

## 平易な説明

サブ担当による実装並列は別 worktree が原則ですが、今回の3モデルAPI呼び出しは実装差分を作らない読み取り・生成処理です。この例外を計画ガード上で明示できていない、という問題です。

## 候補案

- A: task に writes_repo_diff=false / output_only=true のような区分を追加し、同一 worktree API並列を証跡生成に限定して許可する / tradeoff: 今回の実態に合い、実装並列との混同を防げる
- B: API呼び出しもすべて subthread/separate_worktree 扱いにする / tradeoff: 規律は単純だが、raw取得だけでも過剰に重くなる
- C: この指摘を leave-as-is にする / tradeoff: 今後も同じ混乱が起きる

## メインセッション推薦案

- recommended_option: A
- recommended_reason: 実装差分を作る並列と、raw取得だけの並列を分けて機械判定できるため。

## 出力形式

YAMLのみを返してください。

```yaml
cluster_id: WM-IMPL-MF-005
approved_by: proxy_model
proxy_model_id: <model-id>
selected_option: <A|B|C>
final_label: <must-fix|should-fix|leave-as-is>
rationale: <判断理由>
rejected_options:
  - option_id: <id>
    reason: <棄却理由>
```
