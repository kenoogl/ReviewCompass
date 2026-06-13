# レビュー対象（round-2 収束確認）：workflow-management implementation T-012

## 0. 経緯
round-1 で should-fix 2・leave-as-is 5（ERROR・must-fix なし、proxy 裁定）。should-fix（--save 挙動テスト、dependencies/carry_forward/recheck 算出テスト）をテストに追加。実装コード自体は round-1 から不変。本 round-2 は収束確認。variant=implementation_review_independent_3way。

## 1. 追加したテスト（tests/tools/test_review_wave_summary.py、計 14 件）
- test_save_default_location：--save で既定保存先 _cross_feature/reviews/review-wave-summary.{md,json} に書き出し、--json --save は .json。
- test_dependencies_unmet：foundation 未承認＋runtime/evaluation が foundation 依存 → unmet に (runtime,foundation)・(evaluation,foundation)。
- test_carry_forward_count：register の status≠resolved（in_progress・未設定）を 2 件として集計。
- test_recheck_reflected：workflow-management の recheck pending(implementation) が features[].recheck に反映。
- 既存 10 件（JSON スキーマ・status ok、必須欠落で insufficient+exit2、任意非在は ok・0 件、存在解析不能で insufficient、triage 集計軸、run_id 重複排除、読み取り専用、Markdown 既定、--out 保存+読み取り専用）。

## 2. 検証結果
- 14/14 pass。tests/tools/ 全体 297→301 件 pass（回帰なし）。実リポジトリ dogfooding：workflow-management が pending(implementation)、status ok、exit 0。

## 3. レビュー観点（criteria: implementation_r10_round2_convergence）
1. round-1 should-fix（--save・dependencies・carry_forward・recheck のテスト）が網羅され、design 契約を検証可能か。
2. 残存する must-fix 級の欠陥がないか（収束したか）。
