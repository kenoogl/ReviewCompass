---
date: 2026-06-02
classifier: claude_code_main_session
classification: 波及（同フェーズ横方向）。foundation requirements の review_mode 語彙拡張に伴う runtime／workflow-management への波及。両機能の固定列挙を参照方式へ修正
trigger_source: reopen-classification-2026-06-02-analysis-evaluation-review-mode.md と同一の波及イベント（foundation review_mode への api_mediated 追加）。analysis／evaluation 対処後の alignment（整合確認）で runtime／workflow-management にも同型の固定列挙が残存していることを発見、案 A（全機能で直す）で対象拡大
feature: [runtime, workflow-management]
findings: [review-mode-propagation-runtime-wm]
---

## 分類根拠

本再オープンは、[reopen-classification-2026-06-02-analysis-evaluation-review-mode.md](reopen-classification-2026-06-02-analysis-evaluation-review-mode.md) と同一の波及イベント（foundation の review_mode 正本への `api_mediated` 追加）の対象拡大である。analysis／evaluation の波及対処後、第3過程 alignment（整合確認）で runtime と workflow-management にも同型の「全レビューモードを指す固定列挙」が残存していることを発見した。

利用者は当初 analysis／evaluation のみ（案ア）を承認したが、alignment で追加波及が判明したため、案 A（同型の波及を全機能で直す）を選択した（利用者明示承認「案 A」2026-06-02）。

## 問題の事実

foundation の review_mode 正本は 4 値（`manual_dogfooding`／`runtime_mediated`／`subagent_mediated`／`api_mediated`）。runtime／workflow-management の本体文書に旧 3 値前提の固定列挙が残る。

- **runtime**（全レビューモードを指す固定列挙）：
  - requirements.md 86（Req 4 受入 6）：「foundation の語彙正本（3 値列挙）を再定義せず参照する」
  - design.md 187（run_manifest フィールド）：「review_mode：foundation 正本語彙（3 値列挙）から選択」
- **workflow-management**（全レビューモードを指す固定列挙）：
  - design.md 314（レビュー記録 front-matter 例のコメント）：3 値列挙
  - tasks.md 134（T-005 テスト要件）：「mode 3 値（3 値列挙）の複合役許容テスト」

**対象外**：workflow-management の `subagent_mediated` 方式（複合役 `drafter_and_primary_reviewer` 許容、Req 3 受入 3）は特定の方式に固有の機能であり、api_mediated とは無関係。複合役の許容は `subagent_mediated` 特例のみで、`api_mediated`（独立 3 社で完全分離）は複合役不許容（本対処で tasks.md 134 に明示）。

## 連鎖再実施対象（REOPEN_PROCEDURE §4、計画書 §5.6）

- runtime：起点 requirements。requirements／design／tasks の alignment／approval を再実施（drafting／triad-review／review-wave は据え置き、正本を手修正のうえ整合確認・承認のみ再実施）
- workflow-management：起点 design。design／tasks の alignment／approval を再実施（requirements は全値列挙の波及がなく修正対象外のため再実施せず、据え置き）

implementation は両機能とも未着手（全 false）のため対象外。

## spec.json フラグ差し戻し（第1過程ステップ 6、承認済み・案 A 2026-06-02）

**runtime/spec.json**：

- `reopened.requirements`／`reopened.design`／`reopened.tasks`：false → **true**
- `workflow_state.requirements.alignment`／`approval`：true → **false**
- `workflow_state.design.alignment`／`approval`：true → **false**
- `workflow_state.tasks.alignment`／`approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["requirements","design","tasks"]**（再実施対象フェーズの列挙）

**workflow-management/spec.json**（`reopened.requirements`／`reopened.design` は §5.12 改訂で既に true、維持。`reopened` は §5.24.8.1 の履歴フラグ＝過去に再オープンされた履歴を示すもので、現在 alignment／approval が true で再承認済みであることと矛盾しない。requirements は本対処の修正対象外で alignment／approval は true 維持）：

- `reopened.tasks`：false → **true**
- `workflow_state.design.alignment`／`approval`：true → **false**
- `workflow_state.tasks.alignment`／`approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["design","tasks"]**

## 正本修正の対象（第2過程、実施済み）

- runtime/requirements.md 86：3 値列挙を削除し「foundation の語彙正本を再定義せず参照する（値は foundation 正本が定める）」
- runtime/requirements.md 172（Change Intent）：経緯を残し「2026-06-02 に api_mediated を追加し 4 値体制へ拡張」を追記
- runtime/design.md 187：3 値列挙を削除し「foundation 正本語彙から選択（値は foundation 正本が定め、再定義しない）。runtime 自身が実行する場合は runtime_mediated」
- workflow-management/design.md 314：コメントの 3 値列挙を「レビューモード。値は foundation 正本を参照（再定義しない）」へ
- workflow-management/tasks.md 134：「mode の各値（foundation 正本が定める）の複合役許容テスト（複合役の許容は subagent_mediated 特例のみ、他の値は不許容）」へ

## 補助層 D（書き込み後の独立検証）の扱い

本記録は analysis／evaluation 記録（3 系統検証で本質的指摘ゼロを確認済み）と同型構造（機能名・対象箇所のみ相違）のため、小規模扱いとし独立系統 1 体（Google `gemini-3.5-flash`）で検証する。仕様文書（`.reviewcompass/specs/`）はワークフロー段で検証されるため補助層 D 対象外。
