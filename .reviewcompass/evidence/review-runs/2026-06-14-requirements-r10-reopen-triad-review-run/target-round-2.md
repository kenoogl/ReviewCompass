# レビュー対象（round-2 収束確認）：workflow-management requirements Requirement 10

## 0. variant 選定理由

- variant：`implementation_review_independent_3way`（primary=claude-sonnet-4-6、adversarial=gpt-5.5、judgment=gemini-3.1-pro-preview）。Claude Code 操縦時の API 既定。利用者承認 2026-06-14「許可。自律的に進める」「続けて」。

## 1. round-1 からの変更（適用済み）

round-1 の triage（proxy_model=gemini-3.1-pro-preview 裁定）で must-fix 1・should-fix 9・leave-as-is 1 と決め、次を requirements.md へ適用した。本 round-2 は適用後本文の**収束確認**（残 must-fix の有無の確認）であり、新規論点の発掘が目的ではない。

- must-fix（受入 4）：結論不能時に**非ゼロ終了コード**＋JSON の機械可読 `status`＋Markdown での明示を返し、部分集計を完了扱いしない（fail-closed の機械可読シグナル）。
- should-fix（受入 1）：読み取り元（spec.json の workflow_state・recheck、stages/in-progress/、feature_order、各 review-run の triage.yaml、carry-forward register）を明記、厳密な算出定義は design 委譲。
- should-fix（受入 3）：Markdown と JSON は情報同等、JSON は安定スキーマ（詳細は design）。
- should-fix（受入 5）：書き出しは自身の要約出力に限り、既定は標準出力・保存はオプション、状態変更でない旨を明記。
- should-fix（Change Intent）：分類記録のパスを追記。
- leave-as-is（受入 1 の実装形態）：サブコマンド／helper の優先順は design 判断。

## 2. 適用後の Requirement 10（確定本文）

### Requirement 10：review-wave 横断確認の要約コマンド

**目的**：保守担当者が、review-wave の横断確認で用いる指標を手動集計ではなく機械的に生成・再現できるようにする。Requirement 1（静的列挙）と Requirement 2（検査スクリプト）を土台に、横断確認の指標化を機能内の静的検査として位置づける（R-0、新しい意図を要さない）。

受入基準：

1. 要約コマンド（Requirement 2 のサブコマンド、または同等の helper）を提供。読み取り元＝各 feature の spec.json の `workflow_state`・`recheck`、`stages/in-progress/`、`feature_order`（Requirement 8）、各 review-run の `triage.yaml`、carry-forward register（`learning/workflow/carry-forward-register/`）。厳密な算出定義は design で確定。
2. 出力項目＝feature coverage、各機能の phase／stage 状態、triage の未解決・draft・human_required 件数、recheck 状態、依存状況、carry-forward 未消化件数。
3. Markdown と JSON の両方（情報同等）。JSON は安定スキーマ（詳細は design）。
4. 結論不能時は合格・完了を主張せず、非ゼロ終了コード＋JSON の機械可読 `status`＋Markdown 明示を返し、部分集計を完了扱いしない（fail-closed、Requirement 2 受入 4・Requirement 7 と整合）。
5. 集計（読み取り）に徹し spec.json・フェーズ状態・トリアージを書き換えない。書き出しは自身の要約出力に限る（既定は標準出力、保存はオプション、保存先 `_cross_feature/reviews/`、状態変更でない）。

## 3. レビュー観点（criteria: requirements_r10_review_wave_summary_command_round2_convergence）

1. round-1 の must-fix（受入 4 の機械可読 fail-closed シグナル）が過不足なく反映され、Requirement 2 受入 4・Requirement 7 と矛盾しないか。
2. should-fix の反映で新たな矛盾・曖昧さ・受入間の不整合が生じていないか。
3. 残存する must-fix 級の欠陥がないか（収束したか）。
