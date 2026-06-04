# Proxy decision prompt reference for 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-002

Cluster prompt: ../proxy-decision-prompts/WM-IMPL-MF-002.prompt.md

Cluster: WM-IMPL-MF-002

Finding: 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-002

# Proxy decision request: WM-IMPL-MF-002

あなたは ReviewCompass の triad-review 後の proxy_model 判断担当です。
実装はせず、下記の重要所見クラスタについて採用案、棄却案理由、最終ラベルを決めてください。

## 対象クラスタ

- cluster_id: WM-IMPL-MF-002
- title: commit / push / spec-set が stages/in-progress を見ていない
- source_models: gemini-3.1-pro-preview, gpt-5.4
- source_raw_paths: raw/gemini-3.1-pro-preview.round-1.txt, raw/gpt-5.4.round-1.txt
- finding_ids: 2026-06-04-workflow-management-implementation-review-run-gpt-5.4-adversarial-002, 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-002

## 平易な説明

進行中の手続きが残っているときに commit、push、spec-set を通せてしまう、という指摘です。作業途中のまま不可逆操作をしてしまう危険があります。

## 候補案

- A: stages/in-progress/ の非空検査を共通関数化し、commit / push / spec-set の直前に必ず見る / tradeoff: 実装範囲は明確で、不可逆操作全体に効く
- B: commit / push だけ先に遮断し、spec-set は後続に回す / tradeoff: 小さく始められるが、spec-set の穴が残る
- C: WARN に留める / tradeoff: 自律実行中の事故防止として弱い

## メインセッション推薦案

- recommended_option: A
- recommended_reason: 要件上の不可逆操作ゲートなので、対象を分けず共通で fail-closed にするのが自然。

## 出力形式

YAMLのみを返してください。

```yaml
cluster_id: WM-IMPL-MF-002
approved_by: proxy_model
proxy_model_id: <model-id>
selected_option: <A|B|C>
final_label: <must-fix|should-fix|leave-as-is>
rationale: <判断理由>
rejected_options:
  - option_id: <id>
    reason: <棄却理由>
```
