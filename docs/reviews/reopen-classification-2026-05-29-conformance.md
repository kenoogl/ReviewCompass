---
date: 2026-05-29
classifier: claude_code_main_session
classification: A-1
trigger_source: conformance-evaluation tasks/triad-review で確定した design への遡及修正
feature: conformance-evaluation
findings: [topic-111(G-003), topic-112(F-015), topic-119(F-017)]
---

## 分類根拠

本再オープンは conformance-evaluation の tasks 段 triad-review＋7 モデル比較実験で確定した遡及所見（上流の design への修正を要するもの）を統合して処理する。全所見の発見フェーズは tasks（起点記号 A）。戻る先は design のみで requirements には及ばないため、**種別 A-1（tasks → design、深さ 1）**。self-improvement（セッション 39 の A-2、要件＋設計）より範囲が狭い。

### design まで戻る所見（深さ 1：A-1）

- **topic-111（G-003、axis 値域矛盾）**：axis を照合対象の 2 値（requirements/design）に固定し intent は別フィールドに分離。design §10.5（intent 差異記録の axis: intent）／§14.5（analysis 出力の必須フィールド axis 3 値）を「intent は axis でなく参考情報専用フィールド」に修正。§8.1／§9.4／§10.4／§20.3 の 2 値記述は維持
- **topic-112（F-015、陳腐化）**：design §20.1（行 1005-1006）の A-011／A-012 を「✅ 対処済み（セッション 28、出典 pending 166/190 行）」に更新。§14.3／§14.5 の A-011 参照も対処済み前提に整える。§20.1 以外の同種陳腐化の全体点検
- **topic-119（F-017、schemas/ 配置）**：design §12.2 または §18.2 に tools/conformance_evaluation/schemas/ の配置を 1 行追記

### tasks 側の反映（機能内、第2過程で同時実施）

- topic-111：T-005 完了条件1 を「axis 2 値固定、intent は別フィールド」に整合
- topic-113：T-008 前提は維持＋責務明記、変更意図フロー図を T-001→T-005／T-001→T-008 並列に修正（別案）
- topic-114：T-009/T-012 前提に緩い依存 T-006/T-007 を明記
- topic-115：要件追跡表に T-005/T-007 追記、曖昧記述具体化
- topic-116：T-012/T-004 に MV-6 最小仕様（ログ必須フィールド・命名規則・grep 雛形）を記述＋DVT-C004 連動（別案）
- topic-117：T-003/T-004 にテスト追加（候補提示形式／feature-partitioning 肯定確認）
- topic-118：T-007 発番境界テスト／T-004 --check-partitioning／T-005 完了条件4／DVT-C002 括弧書き／CONFORMANCE_EVALUATION.md 既存明記
- topic-119：T-001/T-009 のスキーマ配置は schemas/ サブフォルダ（既記）
- topic-120：T-002 完了条件を「ディスパッチ機構の確立」に言い換え

### trigger_map A-1 による連鎖再実施対象（計画書 §5.6）

- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval

drafting／triad-review／review-wave は再実施対象外。tasks は triad-review 継続中（alignment/approval はまだ false）のため通常フローで段通過。requirements は触れないため再実施対象外。

### 全体点検（topic-112 の利用者条件）

design 全体を点検し、§20.1／§14.3／§14.5 以外に同種の陳腐化記述（横断所見の古い状態への言及）がないか確認し、発見すれば一括修正する。
