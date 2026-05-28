---
date: 2026-05-29
classifier: claude_code_main_session
classification: A-2
trigger_source: self-improvement tasks/triad-review で確定した上流（requirements／design）への遡及修正
feature: self-improvement
findings: [topic-104(F-004), topic-99(G-002), topic-100(G-003), topic-101(F-005), topic-102(F-003), topic-103(G-001), topic-106(F-007), topic-110(G-004)]
---

## 分類根拠

本再オープンは self-improvement の tasks 段 triad-review＋7 モデル比較実験で確定した遡及所見（上流の requirements／design への修正を要するもの）を統合して処理する。全所見の発見フェーズは tasks（起点記号 A）。戻る先が requirements（最上流）と design に分かれるため、より上流まで戻る種別に統合する。利用者は案ア（1 つの再オープンに統合）を選択（2026-05-29 セッション 39）。

### requirements まで戻る所見（深さ 2：A-2）

- **topic-104（F-004、source 値域）**：requirements Req 4 受入 2 が source 値域 3 値（review_record／compliance_report／user_audit）。設計 §6.2 は observation_pattern を加えた 4 値。利用者は案 2（要件を 4 値に更新＝遡及）を採用。requirements（最上流）の修正が必須

### design まで戻る所見（深さ 1：A-1、A-2 に包含）

- **topic-99（G-002、採番衝突）**：design §8.5 採番手順「proposals/ の最大番号＋1」→「全 4 ディレクトリ走査の最大番号＋1」。tasks T-004 完了条件 4 も同時修正
- **topic-100（G-003、依存逆転）**：design §8.9／§9.2 の責務分担を明確化（T-004＝statistical_evidence の存在検証のみ、生成は T-005）。tasks 側に責務境界を一文明記
- **topic-101（F-005、metrics 配置）**：design §11.1 配置図に learning/workflow/metrics/ を追記
- **topic-102（F-003、採用率）**：design §12.1・§12.5 の採用率式を (approved＋superseded)／(approved＋rejected＋superseded) に統一（案 2、superseded を分子分母両方に）
- **topic-103（G-001、陳腐化）**：design §13.3（行611）・§19.3（行923）の A-011／A-016 記述を「対処済み」に更新
- **topic-106（F-007、スキーマ配置）**：design §11.1 にスキーマ配置方針（正本性で分離＋schemas/ 専用サブフォルダ）を追記。tasks 側も明記
- **topic-110（G-004、MV-3 空値）**：design §17.1 の MV-3 に「materialization_commit_hash が空なら正常スキップ」を明記。tasks T-009 も同時修正

### 統合判定

- A-2（requirements まで戻る）の連鎖再実施範囲が A-1（design まで戻る）を包含するため、別々に処理すると design／tasks の再実施が二重になる。よって **A-2 に統合**して 1 つの再オープンとする（利用者案ア）
- requirements と design の両方の正本を修正するため、reopened は requirements／design の双方を true にする
- 利用者明示承認：案ア採用「案ア」（2026-05-29 セッション 39）。フラグ差し戻し内容の承認は第1過程の停止点で別途取得

### trigger_map A-2 による連鎖再実施対象（計画書 §5.6）

- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval

drafting／triad-review／review-wave は再実施対象外（正本修正は手で行い、整合確認と承認のみ再実施。計画書 §5.6）。tasks は現在 triad-review 継続中（alignment／approval はまだ false）のため、通常フローで段通過する。

### 正本修正の対象（第2過程で実施）

- **requirements.md**：Req 4 受入 2（topic-104）：source 3 値 → 4 値
- **design.md**：§8.5（topic-99）／§8.9・§9.2（topic-100）／§11.1（topic-101・topic-106）／§12.1・§12.5（topic-102）／§13.3・§19.3（topic-103）／§17.1（topic-110）
- **tasks.md**：上記の tasks 側反映＋tasks 固有（topic-105 命名／topic-107 hard-soft 依存＋T-002／topic-108 テスト／topic-109 path 検証統合）

### 全体点検（topic-101／103 の利用者条件）

正本修正の際、requirements.md と design.md の全体を点検し、(a) §11.1 以外の配置図・章間の漏れ、(b) §13.3・§19.3 以外の横断所見（A-NNN）の古い状態への言及、がないか確認し、発見すれば一括修正する。
