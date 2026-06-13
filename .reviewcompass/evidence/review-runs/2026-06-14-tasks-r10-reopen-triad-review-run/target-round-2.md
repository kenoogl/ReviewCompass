# レビュー対象（round-2 収束確認）：tasks T-012（更新後全文）
## 0. 経緯
round-1 で should-fix 4・leave-as-is 4（ERROR・must-fix なし、proxy 裁定）。should-fix（スキーマ固定検証・必須/任意記録の欠落と解析不能・--out/--save 保存正常系）を T-012 テスト要件へ反映。本 round-2 は収束確認。variant=implementation_review_independent_3way。
## 1. 更新後 T-012（tasks.md より）

### T-012：review-wave 横断確認の要約コマンド（Req 10、reopen R-0 2026-06-14）

- **対応設計節**：design.md §review-wave 要約コマンドモデル §1〜§6
- **対応要件**：Requirement 10 受入 1〜5
- **責務**：`tools/check-workflow-action.py` に `review-wave-summary` サブコマンドを追加（`next`／`spec-set`／`commit` と同じ CLI 体系）。design §2 の読み取り元（各 feature の spec.json の `workflow_state`・`recheck`、`stages/in-progress/`、feature-dependency.yaml の `feature_order`、review-run の `triage.yaml` 群〔`evidence/review-runs/` 優先・旧 `_cross_feature/reviews/` 互換、`run_id` 単位で重複排除〕、carry-forward register）から design §2 の算出定義で指標を集計する。出力は Markdown（既定）と JSON（`--json`、design §3 の安定スキーマ）で情報同等。fail-closed（design §4：必須記録〔spec.json・feature-dependency.yaml〕の欠落・解析不能、および任意記録の解析不能で `status: insufficient`＋非ゼロ終了コード 2。任意記録〔triage.yaml 群・carry-forward register〕の非在は 0 件として `ok`）。読み取りに徹し spec.json・triage・phase を書き換えない。保存は `--out`／`--save` で自身の要約出力のみ（design §5）。既存関数（`load_all_feature_specs`・`feature_order` 解決・`collect_recheck_items`・`review_triage` 集計）を再利用し二重定義を避ける。
- **前提タスク**：T-002（feature-dependency）、T-003（段集合 YAML）、T-004（検査スクリプト本体）
- **成果物**：`tools/check-workflow-action.py` の `review-wave-summary` サブコマンド（必要に応じ `tools/check_workflow_action/` 配下の helper モジュール）、`tests/tools/`（または `tests/workflow-management/`）のテストファイル
- **完了条件**：design §1〜§6 を満たす。Markdown と JSON が情報同等で JSON が安定スキーマ（キー名・型固定）。必須記録の欠落・解析不能で `status: insufficient`＋終了コード 2、任意記録の非在は `ok`（0 件）。spec.json・triage・phase を書き換えない。TDD（赤→緑→全テスト通過、回帰なし）。
- **テスト要件（TDD：先に失敗テストを書く）**：(1) 各指標の集計（feature coverage・phase/stage 状態・triage の unresolved/draft/human_required・recheck・依存状況・carry-forward 未消化）、(2) JSON 安定スキーマの**キー名・型を固定値として表明検証**（design §3 のトップレベル・ネスト構造と一致）と `status` 判定基準、(3) Markdown と JSON の情報同等、(4) fail-closed：必須記録（spec.json・feature-dependency.yaml）の**欠落**と**解析不能（パースエラー・非連想配列）**で `status: insufficient`＋**exit 2**、任意記録（triage.yaml 群・carry-forward register・stages/in-progress/）の**非在は `ok`・0 件**だが**存在して解析不能なら `status: insufficient`＋exit 2**、(5) 読み取り専用（実行後に spec.json・triage が不変）、(6) draft は run 単位・unresolved/human_required は item 単位の集計軸の区別、(7) **`--out`／`--save` の保存正常系**（指定パス／既定保存先 `_cross_feature/reviews/` へ自身の要約出力が書かれ、spec.json・triage・phase は不変）。全 pytest が pass、回帰なし。

## 2. レビュー観点（criteria: tasks_r10_round2_convergence）
1. round-1 should-fix（スキーマ固定検証・必須/任意記録の欠落と解析不能・保存正常系）が T-012 テスト要件に反映され、design の各契約を検証可能か。
2. 残存する must-fix 級の欠陥がないか（収束したか）。
