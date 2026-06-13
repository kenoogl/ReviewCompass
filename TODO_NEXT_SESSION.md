# 次セッション継続用メモ

最終更新：2026-06-13。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である（詳細は `intent/` と各 feature の仕様を正本とする）。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

## 2. 不可逆操作の規律（要点）

- commit・push・spec.json（workflow_state）・規律ファイルの変更は、利用者の明示承認が必要。commit は利用者から「コミット」と明示された場合だけ、`tools/guarded-git-commit.py` 経由で実行する。
- commit 承認レコードの置き場は `.reviewcompass/runtime/approvals/commit-approval.json`（2026-06-13 の P1 実装で旧 `.reviewcompass/approvals/` から切替済み。委任欄 `explicit_instruction` は単発「コミット」等の機械判定に合う文字列で記録し、発言全文は rationale に残す）。
- API review-run は実行前に variant と役ごとの provider／model を提示し、結果は raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。操縦 LLM 別の既定 variant と独立性原則の正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3)。新規 review-run の置き場は `.reviewcompass/evidence/review-runs/<run-id>/`。
- Claude Code は子プロセスの `GEMINI_API_KEY`／`ANTHROPIC_API_KEY` を空に上書きする。API 実行は `zsh -c 'source ~/.zshrc && ...'` 経由（正本は `docs/experiments/n-model-comparison.md` §3.1）。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-13 時点）

- `next --json`：**`completed`**（進行中手続きなし・全 workflow_state 完了）。未コミット 0・未公開 0（段階 5 完了判定を含む `682935f5` まで push 済み、2026-06-13）。
- **文書配置規約は段階 5 まで完了**（計画 `docs/notes/2026-06-12-document-placement-plan.md` の状態欄が正。P1 完了判定は `docs/notes/2026-06-12-document-placement-stage4-migration.md`）。
  - 配置規約 P1 の reopen 2 本（ce＝R-0・wm＝D-0）は第 4 過程まで完了し `stages/completed/` にある。
  - 新配置の運用が開始済み：証跡は `.reviewcompass/evidence/`（review-runs・features/<feature>/conformance・estimation）、実行時生成物は `.reviewcompass/runtime/`（検査ログ・effective prompt・commit 承認レコード、gitignore 1 行）。旧置き場 6 箇所は凍結（各所の README が案内、読み取り互換は P3 まで）。
  - 凍結違反の機械検出：ce＝`tools/conformance_evaluation/machine_verification.py`（check_record_freeze 等）、wm＝`tools/check_workflow_action/placement_freeze.py`（手動実行手順は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` §8.1）。
- 全テスト：ディレクトリ単位で計 921 件 pass（同名テストファイルの衝突があるため `tests/` 一括ではなくディレクトリごとに pytest を実行する）。

## 4. 次作業（候補。正本は next --json と利用者指示）

`next` が `completed` のため、次は保留事項からの利用者選択になる：

1. **実アプリ pilot**：前提だった P1 完了（PLC-DEC-010）を充足。配布前 smoke も合格済み（`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <root>`）。
2. **review-wave 要約コマンドの実装**：reopen で対応（利用者決定 2026-06-12）。
3. **レビュー証跡の機能側ポインタ要件の一般化**：配置規約の実装完了により再開可能（置き場の前提が確定済み）。
4. **P3（最終形）の専用 reopen 計画**：pilot 後に別途起こす（PLC-DEC-008・011）。主な項目＝disciplines／operations の `.reviewcompass/` 同型化（PLC-DEC-008 最終形）、旧パス読み取り互換の明示終了（PLC-DEC-011）、配置規約の「1 本の正本文書化」（段階 5 の未実施分）の再評価。
5. **セッション記録の機械抽出ツールの実装**：全セッションの会話転写（Claude `~/.claude/projects/<本プロジェクト>/*.jsonl`・Codex `~/.codex/sessions/...`）を一次ソースとして、出力 2 層を生成する（PLC-DEC-007 の 2026-06-13 訂正＋追補が正本）。(1) **整形・機微除去済みの発言全文転写**を evidence 区画へ取り込み（利用者決定「案 A」。裁定の遡及検証用。生 jsonl は無加工取り込みしない）、(2) 人が読むセッション記録（日付・利用者指示と決定・コミット一覧・触れたファイル）。選別規則は不要（全セッションが対象）。過去分のバックフィルは現存転写のみのベストエフォート（実測 2026-06-13：Claude 47 件・Codex 39 件混在。消去済み分は復元不能）。残る設計課題＝機微情報の除去規則・対象アプリ絞り込み（Codex）。
6. **裁定負荷対策（利用者決定の埋没防止）の規律改訂の検討**（利用者決定 2026-06-13「(b) で対応」）。動機事例＝PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は同決定の 2026-06-13 訂正欄）。検討候補：(1) 決定台帳の各項目に利用者発言の引用（出典）を必須化し、包括承認のみの項目は確定として扱わない、(2) LLM が利用者発言を決定文言へ再構成した場合は原文との差分を並べて個別確認（a-1 の同型を利用者決定へ拡張）、(3) 台帳の決定 ID ごとの出典欄を lint で機械検査、(4) 抽出ツール（候補 5）による台帳 ↔ 転写の突き合わせ検証。
7. 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。
