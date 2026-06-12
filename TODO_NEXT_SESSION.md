# 次セッション継続用メモ

最終更新：2026-06-12（深夜）。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

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
- API review-run は実行前に variant と役ごとの provider／model を提示し、結果は raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。操縦 LLM 別の既定 variant と独立性原則の正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3)。
- Claude Code は子プロセスの `GEMINI_API_KEY`／`ANTHROPIC_API_KEY` を空に上書きする。API 実行は `zsh -c 'source ~/.zshrc && ...'` 経由（正本は `docs/experiments/n-model-comparison.md` §3.1）。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-12 深夜時点）

- `next --json`：**`reopen_in_progress`**（配置規約 P1 のパス契約 reopen、2 件進行中）。
  - `stages/in-progress/reopen-procedure-2026-06-12-placement-p1-ce.yaml`（conformance-evaluation、R-0）：requirements・design・tasks の gate 連鎖**完了**（triad-review 計 8 round、must-fix 8・should-fix 17 適用、各フェーズ利用者承認済み）。**残り＝implementation の gate 連鎖（TDD 実装）**
  - `stages/in-progress/reopen-procedure-2026-06-12-placement-p1-wm.yaml`（workflow-management、D-0）：第 2 過程（正本修正）まで完了。**残り＝design から implementation までの gate 連鎖**
- **未公開コミット 2 件**（`41720094`・`ed829135`）。reopen 進行中は push が機械遮断されるため（仕様どおり）、**手続き完了後に push** する。
- 文書配置規約の策定は**段階 4 まで完了・公開済み**（計画 `docs/notes/2026-06-12-document-placement-plan.md`、決定台帳 PLC-DEC-001〜012）。段階 5（P1 実装）の途中＝上記 reopen。
- 本日（2026-06-12）の完了事項（記録が正本、ここは要約）：旧 TODO 候補 5 件（配布物再生成 smoke・全体サマリ現時点版・post_hoc_intent_diff の fixture 化・棚卸し・スキーマ enum 追従）、配置規約 段階 1〜4、P1 reopen の仕様確定（ce 3 フェーズ）。

## 4. 次作業（再開手順）

`next --json` が reopen を最優先で返すので、それに従う。順序の目安：

1. **ce reopen・implementation 段**：tasks 確定本文（T-009／T-007／T-012）どおり TDD で実装する。
   - 評価記録：書き込み常時新配置（`evidence/features/<feature>/conformance/`）・旧配置への新規書き込み禁止・読み取り新→旧フォールバック・同名は新を正として警告（テスト 4 件）
   - 採番：凍結期は新旧合算スコープで統合算出（境界テスト）
   - 機械検査：MV-1〜3 の凍結違反検出（git 履歴判定）・推定ログの凍結期契約（テスト 3 件）
   - 実装後：implementation の triad-review → review-wave → alignment → approval → 第 4 過程（recheck クリア・completed へ移動）
2. **wm reopen・第 3 過程**：design の triad-review から（effective prompt・approvals・検査ログの runtime 区画移行。variant は ce と同じ `implementation_review_independent_3way`）
3. **P1 残作業**（段階 4 記録の #6〜9）：gitignore 簡素化＋初期設定ガイド §8（判断 2 の解）、運用文書追従（WORKFLOW_NAVIGATION の run 例示等）、旧置き場 6 箇所の凍結 README、配布物再生成＋smoke
4. **完了後**：push（未公開分一括）、配置規約 段階 5 の完了判定

予定済み・保留（忘れないこと）：

- review-wave 要約コマンドの実装：reopen で対応（利用者決定 2026-06-12）
- レビュー証跡の機能側ポインタ要件の一般化：配置規約の実装後に再開（置き場の前提が確定済み）
- 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`
- 実アプリ pilot：P1 完了が前提（PLC-DEC-010）

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。
