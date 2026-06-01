# run_layout：実行ディレクトリ構造の解説

本ディレクトリは `runtime` 機能が 1 回のレビュー実行（review session）ごとに生成する成果物配置の仕様を持つ。機械可読の正本は [layout_spec.yaml](layout_spec.yaml)、人間向けの解説は本 README である。配置運用ルールの正本は [docs/operations/RUNTIME.md](../../../docs/operations/RUNTIME.md) §実行ディレクトリ配置と運用ルール に置く。

対応タスク：runtime tasks.md T-001。対応設計節：design.md §実行成果物配置、§配置の根拠、§配置の運用ルール。

## 1. 実行ディレクトリの構造

1 実行は 1 ディレクトリ（`experiments/runs/<run_id>/`）に対応する。`<run_id>` は実行ごとに session controller（T-002）が固定する安定識別子である。

```text
experiments/runs/<run_id>/
├── run_manifest.yaml                  # 実行メタデータの運用者可読な正本
├── review_case.json                   # foundation スキーマに従う機械可読な正本（唯一の横断正本）
├── steps/                             # 段単位再演の最小単位（生段証拠、実行終了後は不変）
│   ├── step_a_primary_detection.json
│   ├── step_b_adversarial_review.json
│   ├── step_c_judgment.json
│   └── step_d_integration.json
├── decisions/                         # 人間決定連携を生証拠から切り離して保存
│   ├── decision_units.json
│   └── human_signoff.json
├── failures/
│   └── failure_observations/          # 失敗観察を独立成果物として保管
│       └── <observation_id>.json
├── validation/                        # 検証器結果と無効化標識を別配置
│   ├── validator_result.json
│   └── invalidation_markers.json
└── derived/                           # runtime 便宜成果物（evaluation の正本ではない）
    ├── runtime_summary.json
    ├── comparison_eligibility_note.json
    └── invalid_run_triage_note.json
```

## 2. 必須ディレクトリ 6 件

`layout_spec.yaml` の `required_directories` は次の 6 件を宣言する（5 サブディレクトリ ＋ ルート）。

| パス | 配置目的 |
|---|---|
| `.`（ルート） | `run_manifest.yaml` と `review_case.json` を直下に置く |
| `steps` | 段単位再演の最小単位。生段証拠を保持し実行終了後は不変 |
| `decisions` | 人間決定連携を生証拠から切り離して保存 |
| `failures/failure_observations` | 失敗観察を独立成果物として保管 |
| `validation` | 検証器結果と無効化標識を別配置 |
| `derived` | runtime 便宜成果物（evaluation の正本ではない） |

## 3. 配置運用ルールの所在

生証拠不変・派生分離・`review_case.json` 唯一の横断正本という 3 つの運用ルールは [docs/operations/RUNTIME.md](../../../docs/operations/RUNTIME.md) §実行ディレクトリ配置と運用ルール に記述する。本 README はディレクトリ構造の解説、`layout_spec.yaml` は機械可読の宣言、RUNTIME.md は運用ルールの解説という役割分担である。

## 4. 物理ディレクトリ作成の責務

本ディレクトリ（`run_layout/`）は配置の仕様のみを定義する。物理ディレクトリの実体作成は実行時に session controller（T-002）が `run_id` ごとに行う。
