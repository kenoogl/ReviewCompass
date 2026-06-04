# 自動実行テスト報告

対象: workflow-management implementation triad-review 後の自律・並列実行検証

## 生じた問題

1. raw response と triage の存在確認が自己申告に近く、全モデル分の raw 保存、三段階トリアージ、human_required 0 件を開始前に機械確認できなかった。
2. proxy decision の根拠 raw はパス確認止まりで、rounds.yaml の raw_sha256 と照合していなかった。
3. 重要所見の実装承認フローは、会話規律だけでは「案提示、承認または proxy decision、実装」の順序を守りきれない可能性があった。
4. same worktree の API 並列と、repo 差分を作る実装並列の区別が曖昧だった。
5. commit、push、spec-set の不可逆操作で、stages/in-progress、commit 承認の鮮度、push 前の commit 検査通過確認が不足していた。
6. stages YAML の completion_predicate が導入された場合に、spec-set が固定辞書だけで進める可能性があった。
7. autonomous-plan の再実行で、台帳の integration_result が上書きされて消える問題が実際に発生した。
8. 自動実行テスト報告そのものが、成果物として揃っているかを機械確認する入口がなかった。

## 対応したこと

1. autonomous-plan に execution_evidence を追加し、review_run_dir、required_raw_paths、triage_path、human_required 0 件を機械確認するようにした。
2. proxy decision の source_raw_paths を rounds.yaml の raw_sha256 と照合するようにした。
3. must-fix 6 件について、平易な説明、候補案、推薦案、proxy decision、実装結果を review-run 配下に保存した。
4. same worktree の main_session 並列は output_only=true / writes_repo_diff=false の場合だけ許可するようにした。
5. spec-set、commit、push で stages/in-progress 非空時の遮断を追加した。
6. commit approval に staged file sha256 を必須化し、古い承認の流用を遮断した。
7. guarded commit 成功後に .git/reviewcompass/last-commit-precheck.json を保存し、push 前に HEAD と照合するようにした。
8. completion_predicate は未評価のまま通さず、正本 7 値（artifact_exists、artifact_exists_and_sections_present、artifact_exists_and_sections_present_and_author_reviewer_distinct、all_features_drafting_and_triad_review_completed、cross_spec_alignment_passed、explicit_human_approval_recorded、depends_on_resolves_correctly）を実際に評価するようにした。既存の file_exists mapping 形式も互換として残した。
9. autonomous-plan 再実行時に既存の integration_result を保全するようにした。
10. assert-review-report-ready を追加し、報告メモ、must-fix clusters、proxy decision summary、triage、summary、台帳 integration_result が揃っているかを機械確認できるようにした。
11. workflow-management implementation.triad-review を完了状態に更新した。

## 残った課題

1. 別 worktree のサブ担当 LLM による実装並列は、まだ本格運用テスト前である。成果物統合、ログ収集、差分レビューの実戦検証が必要。
2. 重要所見を 1 件ずつ丁寧に説明する形式は運用上確認したが、表示テンプレートとしてさらに強制できる余地がある。
3. raw、モデル別所見、三段階トリアージ、重要所見、採用案、実装結果を一枚にまとめる自動レポート生成は、今回の ready 検査に続く後続課題。
4. dogfooding 論文用メトリクスは専用抽出器が未整備。実装手戻り、失敗、上流遡及、承認待ち時間などを集計できる形にする必要がある。

## 今回追加で対応した課題

- 残課題 1 について、completion_predicate 正本 7 値の実評価を追加した。
- 残課題 3 と 4 の入口として、報告成果物の存在と台帳 integration_result を assert-review-report-ready で検査できるようにした。
- 2026-06-04 追加対応として、正本 7 値の正常系／異常系テストを追加し、未対応述語や証跡不足を fail-closed で遮断できるようにした。

## 次に扱う候補

1. assert-review-report-ready を拡張し、重要所見ごとの平易な説明、候補案、採用案が欠ける場合に fail-closed する。
2. raw、モデル別所見、三段階トリアージ、重要所見、採用案、実装結果を一枚にまとめる自動レポート生成を追加する。
3. dogfooding 用メトリクス抽出器の最小スキーマを決め、review-run と workflow-precheck.log から抽出する。
