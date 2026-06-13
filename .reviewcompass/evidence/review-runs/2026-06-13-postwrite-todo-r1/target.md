# 書き込み後検証対象：TODO に候補 2（review-wave 要約コマンド）の reopen 分類 R-1 確定を追記

検証者へ渡すのは合意内容（決定）と書き込み結果のみ。

## 合意内容（決定）

- 候補 2（review-wave 要約コマンドの実装）の reopen 分類を **R-1**（新要件として workflow-management の requirements に追加し、design → tasks → implementation へ連鎖）と確定した（2026-06-13、利用者承認）。
- 実行は新セッションに送る。
- 要件正本は D-001（`docs/notes/2026-06-04-implementation-review-wave-improvements.md`・`docs/notes/2026-06-05-future-development-candidates.md`）。
- 出力項目は feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 件数（Markdown＋JSON、`.reviewcompass/specs/_cross_feature/reviews/` 保存可）。

## 書き込み結果（TODO §4 候補 2）

2. review-wave 要約コマンドの実装：reopen で対応（利用者決定 2026-06-12）。reopen 分類 R-1 確定（2026-06-13、利用者承認）＝新要件として workflow-management の requirements に追加し design → tasks → implementation へ連鎖。要件正本＝D-001。出力＝feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 件数（Markdown＋JSON、`_cross_feature/reviews/` 保存可）。開始＝`reopen-start --classification R-1 --feature workflow-management ...` → 第1過程（分類記録・進行中ファイル発行・spec.json 差し戻し）→ 承認停止点。
