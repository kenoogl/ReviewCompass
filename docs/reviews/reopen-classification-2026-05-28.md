---
date: 2026-05-28
classifier: claude_code_main_session
classification: A-2
trigger_source: workflow-management tasks/triad-review で発見した上流（requirements／design）との不整合
feature: workflow-management
findings: [A-001, A-003]
---

## 分類根拠

本再オープンは workflow-management の tasks 段 triad-review で発見された 2 件の遡及所見（A-001／A-003）を統合して処理する。両所見とも発見フェーズは tasks（起点記号 A）。戻る先が異なるため、より上流まで戻る種別に統合する。

### A-001（再オープン手続きの記述が古い、深さ 1：design まで）

- **発見段**：tasks.triad-review
- **内容**：design.md §reopen 機械強制モデル §5 で「4 過程構成を正とする」と宣言済みだが、同じ design.md の行 57（構成図のコメント）と行 129（モデル表「第 1〜10 ステップ」）に旧記述「10 ステップ」が残存。tasks.md T-003（行 87・93）・T-007（行 153）にも「10 ステップ静的列挙」が残存
- **上流戻り**：design 段（行 57・129）の修正が必須。tasks 段（T-003／T-007）も同時修正
- **単独なら**：A-1（tasks → design）

### A-003（foundation 語彙の不整合、深さ 2：requirements まで、A-018 同根）

- **発見段**：tasks.triad-review
- **内容**：requirements.md 行 32 が旧 foundation 語彙 4 件（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）。一方 tasks.md 行 27 は現行 7 件（`counter_status`／`validator_status`／`evidence_class`／`review_mode`／`severity`／`final_label`／`confidence_label`）。requirements（上流）の記述が現行 foundation 正本と不整合
- **上流戻り**：requirements 段（行 32）の修正が必須
- **単独なら**：A-2（tasks → requirements）

### 統合判定

- A-2（requirements まで戻る）の連鎖再実施範囲が A-1（design まで戻る）を包含するため、別々に処理すると design／tasks の再実施が二重になる。よって **A-2 に統合**して 1 つの再オープンとする
- 利用者明示承認：「承認」（2026-05-28、種別 A-2 統合・フラグ差し戻し）

### trigger_map A-2 による連鎖再実施対象（計画書 §5.6）

- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval

drafting／triad-review／review-wave は再実施対象外（正本修正は手で行い、整合確認と承認のみ再実施。計画書 §5.6 行 3645）。

### 正本修正の対象（第2過程で実施）

- requirements.md 行 32（A-003）：旧 4 件 → 現行 7 件
- design.md 行 57・129（A-001）：「10 ステップ」→「4 過程構成」
- tasks.md T-003 行 87・93、T-007 行 153（A-001）：「10 ステップ静的列挙」→「4 過程構成の段集合」

### 初運用メモ（暫定版手続きの不具合候補）

本再オープンは 4 過程構成（計画書 §5.6.1、design.md §reopen 機械強制モデル §5）の初運用。進行中状態ファイルの `completed_steps`／`next_step` は素材由来の 10 ステップ前提の語彙だが、現行は 4 過程構成のため、過程番号で記録する。手続きの再定義要否は運用後に §5.6.1 で見直す。
