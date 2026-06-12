# レビュー対象：reopen R-0（placement-p1-path-contracts）conformance-evaluation tasks 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本 reopen の requirements・design triad-review と同一構成（利用者承認 2026-06-12「開始」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の
第3過程、conformance-evaluation tasks フェーズの triad-review。上流の requirements・design は各 gate を
完了し利用者承認済み。確定した上流契約の要点：

- 配置ルート契約＝ `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`（評価記録・草案・handoff）
- 既存記録は旧配置 `specs/<feature>/conformance/` で凍結。凍結の効力発生は P1 実装反映コミット（書き込み先切替）と同時
- 読み取りは新→旧フォールバック（P3 まで）、書き込みは常に新配置、互換終了は P3 の専用 reopen
- 機械検査 MV-1〜MV-3 は新配置を正とし旧凍結分も対象、新規の旧配置出現は違反検出（git 履歴で判定）
- 所見 ID 採番は凍結期に新旧合算スコープで統合算出
- 推定独立性ログは `evidence/estimation/<run_id>/prompt.log`（旧ルート `logs/estimation/` から変更）

実装より先に仕様を確定する正順であり、**現時点で実装は旧パスへ書く挙動のまま**（意図的）。
implementation 段で TDD（失敗テスト→実装→全テスト通過）により書き込み先変更と読み取り互換を実装する。

## 2. 変更内容（conformance-evaluation tasks.md、6 箇所）

### 2.1 T-001 物理配置の責務（由来注記付き）

> 評価記録の配置先 `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`（`reviews/` とは別ディレクトリ、Req 8 受入 4。旧配置 `specs/<feature>/conformance/` からの変更は 2026-06-12 配置規約 PLC-DEC-003〜005・009〜011 反映、既存記録は旧置き場で凍結・旧パス読み取り互換は P3 まで維持）

### 2.2 成果物パスの追従（4 箇所、一括置換）

`.reviewcompass/specs/<feature>/conformance/` → `.reviewcompass/evidence/features/<feature>/conformance/`

- `<日付>-spec-update-drafts/*.md`（draft-only 草案）
- `<日付>-post-hoc-intent-diff.md`（後追い intent 差分の評価記録）
- `<日付>-reopen-handoff.prompt.md`（次タスクプロンプト）
- `<日付>-reopen-handoff.yaml`（引き渡し package）

### 2.3 MV-6 の推定ログ命名規則（T-014 の機械検査仕様）

> 格納先ディレクトリ命名規則（例 `.reviewcompass/evidence/estimation/<run_id>/prompt.log`。旧 `logs/estimation/` からの変更は 2026-06-12 配置規約 PLC-DEC-005・009 反映、既存ログは旧置き場で凍結）

## 2.4 round-2 注記：round-1 所見の適用（利用者承認 2026-06-12「承認」）

round-1 の同根クラスタ C7（design 新機構のタスク翻訳欠落、must-fix 3）ほかを適用し、tasks.md へ次の 4 箇所を追記した。
round-2 は適用後本文の収束確認である。

> **T-009（評価記録の type 値と配置）責務へ**：書き込みは常に新配置（`evidence/features/<feature>/conformance/`）とし、
> 旧配置への新規書き込みを行わない（凍結契約、design §12.2）。読み取りは新配置優先・旧配置フォールバック
> （P3 まで。両方に同名記録がある場合は新配置を正とし警告を報告）。
> **テスト要件へ**：凍結期挙動テスト 4 件（新配置書き込み／旧配置フォールバック読み取り／新旧同名時の
> 新配置優先と警告／旧配置への新規書き込みが発生しないこと。TDD 先行）

> **T-007（比較モデル）完了条件 4 へ**：凍結期（P3 まで）は新旧両配置を合算した走査範囲で最大番号を統合算出し、
> 旧凍結記録との ID 重複・リセットを防ぐ。**テスト要件へ**：凍結期の新旧合算採番テスト
> （旧凍結記録に CF-007 がある状態で新規が CF-008 になること）

> **T-012（機械検査の具体手段）責務へ**：MV-1〜MV-3 の検査ルートは新配置を正とし、旧配置の凍結済み既存記録も
> 検査対象に含める。新規記録が旧配置に現れた場合は違反として検出する（凍結集合の判定は git 追跡履歴が正本：
> P1 実装反映コミット時点で旧配置に存在したファイルが凍結集合、以降の追加・変更は違反。効力発生は実装切替と同時）。
> 凍結済み旧推定ログ（`logs/estimation/`）も MV-6 の読み取り対象に含める。
> **テスト要件へ**：凍結違反検出テスト（正常系＝凍結集合内は違反としない／異常系＝実装反映後の旧配置追加を検出）

> **T-001 へ**：書き込み・読み取りの挙動は T-009 を正本とする（1 句追加）

## 2.5 round-3 注記：round-2 所見の適用（利用者承認 2026-06-12「shouninn（承認）」）

round-2 の同根クラスタ C8（推定ログの凍結期契約の欠落、must-fix 1・should-fix 2）とトレース不一致
（should-fix 1）を適用した。round-3 は適用後本文の収束確認である。

> **T-012 へ追記**：推定ログの書き込みは常に新配置 `evidence/estimation/<run_id>/` とし、旧 `logs/estimation/`
> への新規書き込みを行わない。旧ルートへの新規追加は凍結違反として検出する（判定規則は評価記録と同一＝
> P1 実装反映コミット以降の git 追跡履歴を正本とする）。
> **テスト要件へ**：推定ログの凍結期テスト 2 件（新配置への書き込み／旧ルートへの新規追加を違反として検出）

> **T-001 の要求トレース補正**：「配置ルート契約は Req 6 受入 2、`reviews/` とは別ディレクトリの分離契約は
> Req 8 受入 4」と両契約を併記（§2.1 と §3 の参照不一致を解消）

## 3. レビュー観点（criteria: tasks_placement_p1_evidence_path_change）

1. **上流追従の完全性**：6 箇所の変更が、承認済み requirements（受入 2 のルート契約）・design（凍結期検査・互換挙動・採番）と矛盾なく追従しているか
2. **取りこぼし**：tasks 内に旧パスを前提とするタスク記述・成果物定義・テスト要件が残っていないか
3. **実装タスクへの翻訳可能性**：implementation 段の TDD（書き込み先変更・新→旧フォールバック・凍結違反検出・採番統合算出）に必要なタスクレベルの情報が揃っているか
4. **テスト要件の整合**：MV-6 ほか機械検査のテスト記述が新配置と凍結期の挙動に追従しているか
