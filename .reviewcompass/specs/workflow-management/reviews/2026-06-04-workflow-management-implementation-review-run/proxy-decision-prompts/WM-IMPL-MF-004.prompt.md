# Proxy decision request: WM-IMPL-MF-004

あなたは ReviewCompass の triad-review 後の proxy_model 判断担当です。
実装はせず、下記の重要所見クラスタについて採用案、棄却案理由、最終ラベルを決めてください。

## 対象クラスタ

- cluster_id: WM-IMPL-MF-004
- title: spec-set が stages/*.yaml の completion_predicate を評価していない
- source_models: gemini-3.1-pro-preview
- source_raw_paths: raw/gemini-3.1-pro-preview.round-1.txt
- finding_ids: 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-001

## 平易な説明

spec-set が段階定義 YAML を読まず、コード内の固定順序だけで段の進行可否を見ている、という指摘です。段ごとの「成果物があるか」「author/reviewer が分離しているか」などの述語が効いていない可能性があります。

## 候補案

- A: まず実装済み範囲との差分を確認し、completion_predicate 評価不足をT-004残課題として機械検査に追加する / tradeoff: 大きな改修に入る前に事実確認できる
- B: stages/*.yaml パーサと全 predicate 評価を即実装する / tradeoff: 正攻法だが影響範囲が大きく、この場の自律実装としては危険
- C: 今回は誤検出として保留する / tradeoff: CRITICAL 指摘を十分に扱えない

## メインセッション推薦案

- recommended_option: A
- recommended_reason: CRITICAL だが広範囲。まず現実の実装差分とタスク残を照合し、実装単位を切るのが安全。

## 出力形式

YAMLのみを返してください。

```yaml
cluster_id: WM-IMPL-MF-004
approved_by: proxy_model
proxy_model_id: <model-id>
selected_option: <A|B|C>
final_label: <must-fix|should-fix|leave-as-is>
rationale: <判断理由>
rejected_options:
  - option_id: <id>
    reason: <棄却理由>
```
