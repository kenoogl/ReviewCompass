# レビュー対象：reopen R-0（review-wave-summary-command）workflow-management requirements 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の API 既定（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。利用者承認 2026-06-14「許可。自律的に進める」。
- 本 run の置き場は `.reviewcompass/evidence/review-runs/`（配置規約 PLC-DEC-004・009）。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）の第3過程、workflow-management requirements フェーズの triad-review。

背景：D-001（review-wave summary command）を新要件として追加する。review-wave（機能横断段）の横断確認で用いた指標（feature coverage・段状態・triage 件数・recheck 状態・依存状況・carry-forward 件数）を手動集計から機械生成へ移す。分類は R-0（intent・feature-partitioning は不変、既存「静的検査」の範囲に含む）。**実装より先に仕様を確定する正順**であり、コマンドの実装は design・tasks 確定後に implementation 段で TDD により行う。**現時点で実装は未着手**である（意図的）。

## 2. 変更内容（workflow-management requirements.md）

### 2.1 Requirement 10 新設

> ### Requirement 10：review-wave 横断確認の要約コマンド
>
> **目的（Objective）**：保守担当者が、review-wave（機能横断段）の横断確認で用いる指標を、手動集計ではなく機械的に生成・再現できるようにする。集計漏れや報告の揺れを防ぐ。本要件は Requirement 1 が定める「段集合 YAML による静的列挙」と Requirement 2 の検査スクリプトを土台に、横断確認の指標化を機能内の静的検査として位置づける（新しい意図を要さない。2026-06-14 reopen R-0、利用者決定）。
>
> #### 受入基準（Acceptance Criteria）
>
> 1. 本機能は、review-wave の横断確認指標を機械生成する要約コマンド（Requirement 2 の検査スクリプトのサブコマンド、または同等の helper）を提供する。指標は `workflow_state`・`stages/in-progress/`・recheck・機能依存マップ（Requirement 8 の `feature_order`）・機能横断持ち越し所見記録から読み取り、手動集計に依存しない。
> 2. 本コマンドの出力項目は最低限、次を含む：feature coverage（機能ごとの段到達状況）、各機能の phase／stage 状態、triage の未解決（unresolved）件数・draft 件数・human_required 件数、recheck 状態（`upstream_change_pending` と `impacted_downstream_phases`）、依存状況（`feature_order` と未充足依存）、carry-forward（機能横断持ち越し所見）の未消化件数。
> 3. 本コマンドは出力形式として Markdown と JSON の両方を提供する。JSON は機械処理用、Markdown は人が読む横断確認用とする。
> 4. 本コマンドは結論不能（必要な記録が解析不能・欠落）の場合、合格や完了を主張せず、不能であることを出力に明示する（第 1 層の限界・fail-closed と整合、Requirement 2 受入 4・Requirement 7）。
> 5. 本コマンドは集計（読み取り）に徹し、`spec.json`・フェーズ状態・トリアージ判断を書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。出力は `.reviewcompass/specs/_cross_feature/reviews/` に保存できる形式とする。
>
> 由来：D-001（review-wave summary command）。要件正本は `docs/notes/2026-06-04-implementation-review-wave-improvements.md` と `docs/notes/2026-06-05-future-development-candidates.md`。分類は 2026-06-14 reopen R-0。実装は仕様確定後に TDD で行う正順の手続きとする。

### 2.2 Change Intent への追記

> - 2026-06-14 の reopen R-0（review-wave-summary-command、D-001）により、Requirement 10 を新設し、review-wave 横断確認指標の機械生成（要約コマンド）を機能内の静的検査として要件化した。分類は意図文書を改めず既存「静的検査」（Requirement 1）の範囲に含める R-0 とした（2026-06-13 記録の R-1 ラベルと併記説明文の食い違いを 2026-06-14 に利用者と確認のうえ R-0 を採用）。本改訂は仕様確定後に TDD で実装する正順の手続きである。

## 3. レビュー観点（criteria: requirements_r10_review_wave_summary_command）

1. **要件の妥当性・明確さ**：受入 1〜5 が、実装者が検証可能な形で書かれているか。曖昧・多義な語がないか。
2. **既存要件との整合**：Requirement 1（静的列挙）・Requirement 2（検査スクリプト・next・fail-closed）・Requirement 8（feature_order）との重複・矛盾がないか。「Requirement 2 のサブコマンドまたは同等 helper」という書き方は責務境界として適切か。
3. **責務の越境がないか**：受入 5 の「集計に徹し spec.json・フェーズ状態・トリアージを書き換えない」が、Requirement 3 受入 5・Requirement 4 受入 1（不可逆操作）と整合し、要約コマンドが書き込み権を持たないことを担保できているか。
4. **出力項目の網羅性**：受入 2 の出力項目が D-001（要件正本）の指標（feature coverage・triage completeness・recheck state・dependency status・carry-forward count）を漏れなく反映しているか。
5. **fail-closed の整合**：受入 4 の結論不能時の挙動が、Requirement 2 受入 4・Requirement 7（多層防御の第 1 層）と矛盾しないか。
6. **下流への波及**：design・tasks・implementation で追従すべき事項の漏れが requirements 側の文言から生じないか（例：出力スキーマ・保存形式・JSON/Markdown の双方提供）。
