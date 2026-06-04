# Proxy decision request: WM-IMPL-MF-003

あなたは ReviewCompass の triad-review 後の proxy_model 判断担当です。
実装はせず、下記の重要所見クラスタについて採用案、棄却案理由、最終ラベルを決めてください。

## 対象クラスタ

- cluster_id: WM-IMPL-MF-003
- title: proxy decision が元 raw と一致しているか確認できない
- source_models: claude-sonnet-4-6, gemini-3.1-pro-preview
- source_raw_paths: raw/claude-sonnet-4-6.round-1.txt, raw/gemini-3.1-pro-preview.round-1.txt
- finding_ids: 2026-06-04-workflow-management-implementation-review-run-claude-sonnet-4-6-primary-004, 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-003

## 平易な説明

proxy decision は「どのレビュー生データを読んで判断したか」が重要ですが、今は raw ファイルが存在することしか見ていません。別の raw に差し替わっても見抜きにくい、という問題です。

## 候補案

- A: decision の source_raw_paths を triage.yaml と rounds.yaml に照合し、raw_sha256 まで一致確認する / tradeoff: 証跡の真正性を一番強く守れる
- B: source_raw_paths が triage の source_raw_path と一致することだけ確認する / tradeoff: 軽いが、ファイル内容の差し替えは防げない
- C: decision に raw_sha256 を追記するだけにする / tradeoff: 記録は増えるが検査がなければ防止力が弱い

## メインセッション推薦案

- recommended_option: A
- recommended_reason: raw response を根拠にした判断代行という契約を守るには、パスとハッシュの両方を照合する必要がある。

## 出力形式

YAMLのみを返してください。

```yaml
cluster_id: WM-IMPL-MF-003
approved_by: proxy_model
proxy_model_id: <model-id>
selected_option: <A|B|C>
final_label: <must-fix|should-fix|leave-as-is>
rationale: <判断理由>
rejected_options:
  - option_id: <id>
    reason: <棄却理由>
```
