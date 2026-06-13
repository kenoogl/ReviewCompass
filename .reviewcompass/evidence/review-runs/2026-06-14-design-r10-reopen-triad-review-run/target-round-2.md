# レビュー対象（round-2 収束確認）：workflow-management design §review-wave 要約コマンドモデル

## 0. variant 選定理由

- variant：`implementation_review_independent_3way`（claude-sonnet-4-6／gpt-5.5／gemini-3.1-pro-preview）。利用者承認 2026-06-14「コミット点まで自律で進める」。

## 1. round-1 からの変更（適用済み・proxy_model 裁定）

round-1 で must-fix 4・should-fix 7・leave-as-is 1 と裁定（proxy=gemini-3.1-pro-preview、ERROR・must-fix は承認レコード付き）。本 round-2 は適用後本文の**収束確認**。

- must-fix（JSON ネストスキーマ／phases 型／status 判定基準／triage 重複排除・判定規則）：§3 に JSON 安定スキーマを構造付きで確定（`features[].phases` は phase 名キーのオブジェクト→`{stage: bool}`、各フィールド型、`status` 判定基準＝必要記録が全て読めれば ok）。§2 に triage の run_id 単位重複排除と unresolved/draft/human_required の判定規則を明記。
- should-fix：§4 に fail-closed の対象範囲（欠落／パース不能／非連想配列、Req8受入9 同型）と終了コード規約（0=ok、2=insufficient、既存サブコマンドと整合）。§2 に carry-forward 未消化＝status≠resolved。§5 に `--out`/`--save` の意味・既定命名・保存先（承認済み要件受入5の現行置き場）。§6 に implementation 委譲事項を新設。
- leave-as-is：保存先 `_cross_feature/reviews/` は承認済み要件への誤検知のため変更なし。

## 2. 適用後の確定設計（要約）

- §1 配置：`review-wave-summary` サブコマンドを check-workflow-action.py に追加、読み取り専用。
- §2 読み取り元と算出定義＋集計規則（triage 重複排除・判定規則、carry-forward 未消化）。
- §3 JSON 安定スキーマ（構造・型・status 判定基準）、Markdown 情報同等。
- §4 fail-closed（対象範囲の一意化、終了コード 0/2）。
- §5 保存（既定 stdout、--out/--save、状態変更でない）。
- §6 implementation 委譲事項。

## 3. レビュー観点（criteria: design_r10_review_wave_summary_command_round2_convergence）

1. round-1 の must-fix 4 件（スキーマ構造・phases 型・status 判定基準・triage 規則）が過不足なく反映され、機械処理契約として一意か。
2. should-fix の反映で新たな矛盾・曖昧さが生じていないか。
3. 残存する must-fix 級の欠陥がないか（収束したか）。
