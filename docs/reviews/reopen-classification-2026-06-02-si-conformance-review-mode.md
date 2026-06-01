---
date: 2026-06-02
classifier: claude_code_main_session
classification: 波及（同フェーズ横方向）。foundation requirements の review_mode 語彙拡張に伴う self-improvement／conformance-evaluation への波及。両機能の固定列挙を参照方式へ修正
trigger_source: reopen-classification-2026-06-02-analysis-evaluation-review-mode.md・reopen-classification-2026-06-02-runtime-wm-review-mode.md と同一の波及イベント（foundation review_mode への api_mediated 追加）。日本語表記「レビューモード」も含めて全機能を再調査した結果、self-improvement／conformance-evaluation にも同型の固定列挙が残存していることを発見、案 A（全機能で直す）の範囲に追加
feature: [self-improvement, conformance-evaluation]
findings: [review-mode-propagation-si-conformance]
---

## 分類根拠

本再オープンは、foundation の review_mode 正本への `api_mediated` 追加の波及イベントの最終範囲確定である。analysis／evaluation（第1コミット）・runtime／workflow-management（第2コミット）の対処後、波及調査を **日本語表記「レビューモード」も含めて全機能に再実施**した結果、self-improvement／conformance-evaluation にも同型の「全レビューモードを指す固定列挙」が残存していることを発見した。

当初の波及調査が英語表記「review_mode」のみで行われ、日本語表記「レビューモード語彙」の箇所を取りこぼしていたことが、範囲が段階的に広がった原因（記録として明示）。利用者は案 A（同型の波及を全機能で直す）の範囲に本 2 機能を追加することを承認（利用者明示承認「対応」2026-06-02）。

これにより、波及は foundation の下流 6 機能（analysis／evaluation／runtime／workflow-management／self-improvement／conformance-evaluation）すべてに及んでいたことが確定した。

## 問題の事実

- **self-improvement**：design.md 605（foundation 接合面の入力欄）に review_mode 語彙の 3 値列挙
- **conformance-evaluation**：requirements.md 125（受入 7）・design.md 570（適用語彙表、機械検査 MV-7 で foundation Req 6 受入 6 と照合）に 3 値列挙

いずれも「全レビューモードを指す固定列挙」。参照方式（foundation 正本を参照、値を埋めない）に変更。conformance-evaluation の MV-7 は foundation 正本と照合する機械検査であり、参照方式にすることで foundation の現行値（4 値）と値数非依存で照合できる。

## 連鎖再実施対象（REOPEN_PROCEDURE §4、計画書 §5.6）

- self-improvement：起点 design（design 605 が最上流の修正箇所）。design／tasks の alignment／approval を再実施（requirements は修正対象外で据え置き）
- conformance-evaluation：起点 requirements（requirements 125 が最上流）。requirements／design／tasks の alignment／approval を再実施

implementation は両機能とも未着手のため対象外。

## spec.json フラグ差し戻し（第1過程ステップ 6、承認済み・案 A／対応 2026-06-02）

**self-improvement/spec.json**（`reopened.requirements`／`reopened.design` は §5.12 改訂で既に true、履歴フラグ §5.24.8.1 として維持。requirements は本対処の修正対象外で alignment／approval は true 維持）：

- `reopened.tasks`：false → **true**
- `workflow_state.design.alignment`／`approval`：true → **false**
- `workflow_state.tasks.alignment`／`approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["design","tasks"]**

**conformance-evaluation/spec.json**（`reopened.design` は既に true、履歴フラグとして維持）：

- `reopened.requirements`：false → **true**
- `reopened.tasks`：false → **true**
- `workflow_state.requirements.alignment`／`approval`：true → **false**
- `workflow_state.design.alignment`／`approval`：true → **false**
- `workflow_state.tasks.alignment`／`approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["requirements","design","tasks"]**

## 正本修正の対象（第2過程、実施済み）

- self-improvement/design.md 605：3 値列挙を「レビューモード語彙（値は foundation 正本を参照、再定義しない）」へ
- conformance-evaluation/requirements.md 125：3 値列挙を削除し「レビューモード語彙（foundation Requirement 6 受入 6 由来）を再定義せず参照する（値は foundation 正本が定める）」へ
- conformance-evaluation/design.md 570：3 値列挙を「レビューモード語彙（値は foundation 正本を参照）」へ

## 補助層 D（書き込み後の独立検証）の扱い

本記録は先行 2 記録（analysis-evaluation を 3 系統で検証し本質的指摘ゼロを確認、runtime-wm を 1 系統で検証）と同型構造のため、小規模扱いとし独立系統 1 体（Google `gemini-3.5-flash`）で検証する。
