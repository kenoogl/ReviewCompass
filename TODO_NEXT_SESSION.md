# 次セッション継続用メモ

最終更新：2026-06-14。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

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

## 3. 現在位置（2026-06-14 時点）

- `next --json`：**`completed`**（進行中手続きなし・全 workflow_state 完了）。未コミット 0・未公開 0（`a37ad0c2` まで push 済み、2026-06-14）。
- **会話ログ取り込みの追記専用マージ化（maintenance side track）完了・公開済み**：従来の「丸ごと上書き」をやめ、層 1（整形済み転写）の本文包含で `same`／`extend`／`shrink` を判定し、同一はスキップ・拡張は更新・縮小は既存保全（上書きせず警告）とした。元ログ（jsonl）が何らかの理由で縮んでも取り込み済み記録を失わない。判定モジュール `tools/session_record_extractor/merge.py`（`classify_update`／`is_subsequence`）を追加し `tools/session-record-backfill.py` を改修。判定は層 1 で行い層 2 は同一ソースゆえ追従（層 2 の「（なし）→実データ」を縮小と誤判定しない）。TDD テスト 4 件（同一は書かない／伸びたら拡張反映／縮んだら保全／空欄→実データは拡張）＝`tests/tools/test_session_record_append_merge.py`。書き込み後検証はテスト通過で完了（利用者決定 2026-06-14。前例 postwrite-log-exclusion と同様、多モデル API レビューなし）。完了記録＝`stages/completed/maintenance-2026-06-14-session-record-append-merge.yaml`。コミット `44ed5ea8`。前セッションの取りこぼしセッション記録 4 件も `a37ad0c2` で確定。tests/tools 316 件・tests/hooks 21 件 pass。
- **review-wave 要約コマンド（候補2・Req 10／T-012）完成・公開済み**：reopen **R-0** で workflow-management に Requirement 10 を新設し、`review-wave-summary` サブコマンドを TDD 実装（`tools/check-workflow-action.py`。`build_review_wave_summary`／`aggregate_triage_for_summary`／Markdown・JSON 安定スキーマ／fail-closed〔必須記録欠落で exit 2・任意記録の非在は ok〕／読み取り専用／`--out`・`--save`）。出力＝feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 未消化。実行＝`python3 tools/check-workflow-action.py review-wave-summary [--json] [--out PATH|--save]`。各 phase は 3 役 triad-review → proxy_model（gemini-3.1-pro-preview）裁定 → 収束確認 → review-wave/alignment/approval で連鎖再実施（design は反証役の指摘で round-4 まで回し収束）。完了記録＝`stages/completed/reopen-procedure-2026-06-14.yaml`。コミット `451fd3da`（第1・2過程）・`bf3769a0`（第3・4過程）。専用テスト 14 件＋tests/tools 301 件 pass。
- **セッション記録 機械抽出ツール（PLC-DEC-007 候補 5）完成・84 件バックフィル公開済み**：ツールは `tools/session-record-extractor.py`（単体）・`tools/session-record-backfill.py`（一括）・`tools/session_record_extractor/`（ライブラリ）。層 1（整形済み発言全文転写）＝`.reviewcompass/evidence/sessions/`、層 2（人が読む記録）＝`docs/sessions/auto-*.md`。来歴刻印＋再現性チェック（168/168 一致）＋機微除去 3 段（漏えい 0）。Codex は cwd 前方一致で絞り込み、内部思考は除外、ツール結果は先頭＋末尾に縮約。
- **会話ログ自動保持（going-forward 取り込み）実装・公開済み**：Claude のセッション終了時に当該会話ログを2層記録へ自動取り込みする SessionEnd フック（`.claude/hooks/session-record-capture.sh`、`.claude/settings.json` に matcher なしで登録）と、`tools/session-record-backfill.py` の単一セッション取り込み（`--session`／`--source`／`--evidence-dir`／`--docs-dir`）を TDD で追加。`transcript_path` 欠落時は `session_id`＋`cwd` から復元、ログ無し・失敗でも exit 0（終了を妨げない）。Claude 専用（利用する LLM が自分のログを残す方針）で `.codex/` 複製はしない。取りこぼしの回収は**終了済みセッションへの単一取り込み（`--session`）が安全網**（2026-06-14 是正。当初は「オフライン一括バックフィルが安全網」と PLC-DEC-007 追補で定めたが、一括は実行中セッションを掴み churn を生むため既定無効化＝§4 の churn 対応を参照）。フックは**設定読込の都合で次セッションから有効**。コミット `a287684a`（push 済み）。専用テスト＝`tests/tools/test_session_record_single_capture.py`・`tests/hooks/test_session_record_capture.py` 各 4 件、tools 202 件・hooks 21 件 pass。
- **正本優先（事例より正本）の生成ツール（案2）追加・公開済み**：「過去の事例を手で写す」のをやめ、正本（強制コードの検証関数）が受け入れる形を生成し、正本へ通して fail-closed する2ツールを TDD で追加。`tools/make-commit-approval.py`（commit 承認レコード生成。正本＝`validate_commit_approval`／`validate_commit_execution_delegation`）と `tools/make-post-write-manifest.py`（書き込み後検証 manifest 生成。正本＝`evaluate_post_write_manifest_state`／`review_run_traceability_satisfied`）。専用テスト各 4／3 件、いずれも生成物を正本の判定関数へ通して確認。tools 全テスト pass（unittest discover で 209 件）。コミット `83abd1e6`（push 済み）。本 TODO 更新の承認レコード・manifest も両ツールで生成（dogfooding）。動機・経緯と残検討は §4 の項 7。
- **書き込み後検証ポリシー改訂済み**：独立検証が有効でないものを性質ベースで対象外化。(あ) 機械生成・出所明記の派生記録（来歴マーカー判定）、(い) 機械が吐く捕捉物（review-run・自律並列台帳・検証結果ログ＝ディレクトリ判定）。いずれも独立検証でなく再現性／走行・再実行で担保。正本＝`docs/disciplines/discipline_post_write_verification.md`、ガード＝`tools/check-workflow-action.py` の `is_post_write_verification_target`。監査・計測記録（`docs/discipline-compliance-reports/`）は主張を含むため対象に残す。
- **文書配置規約は段階 5 まで完了**（計画 `docs/notes/2026-06-12-document-placement-plan.md` の状態欄が正。P1 完了判定は `docs/notes/2026-06-12-document-placement-stage4-migration.md`）。
  - 配置規約 P1 の reopen 2 本（ce＝R-0・wm＝D-0）は第 4 過程まで完了し `stages/completed/` にある。
  - 新配置の運用が開始済み：証跡は `.reviewcompass/evidence/`（review-runs・features/<feature>/conformance・estimation）、実行時生成物は `.reviewcompass/runtime/`（検査ログ・effective prompt・commit 承認レコード、gitignore 1 行）。旧置き場 6 箇所は凍結（各所の README が案内、読み取り互換は P3 まで）。
  - 凍結違反の機械検出：ce＝`tools/conformance_evaluation/machine_verification.py`（check_record_freeze 等）、wm＝`tools/check_workflow_action/placement_freeze.py`（手動実行手順は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` §8.1）。
- 全テスト：ディレクトリ単位で pass（`tests/tools` は 2026-06-14 の review-wave-summary 追加で 301 件。同名テストファイルの衝突があるため `tests/` 一括ではなくディレクトリごとに pytest を実行する）。

## 4. 次作業（候補。正本は next --json と利用者指示）

`next` が `completed` のため、次は保留事項からの利用者選択になる：

- **会話ログの取り込みは原則フック任せ（手動 backfill は予備）**：会話ログの2層記録は、SessionEnd フック（`a287684a`）がセッション終了時に自動で取り込む。2026-06-14 に、漏れていた `b5bd051e` を対象にフックを一時出力先で実走させ、両層が正しく生成されることを確認済み（フックは動く）。したがって**進行中の本セッションも、終了時にフックが自動記録する**ので「次セッション冒頭で手動取り込み」を常時行う必要はない。取りこぼしの回収が要るときは、**終了済みセッション 1 件だけを `python3 tools/session-record-backfill.py --session <jsonl>` で取り込む**（フックと同じ単一取り込み。安全）。**一括スキャン（`--session` なし）は使わない**：実行中のセッション（自分自身を含む）を掴んで後で取り込み直し＝差分のたまり（churn）を生むため、2026-06-14 にコードで既定無効化した（`--historical-import` フラグ無しでは exit 2 で止まる。過去ログの一括取り込みは完了済み。歯止めテスト＝`tests/tools/test_session_record_bulk_guard.py`）。churn の発端は前セッション `a57d7790` が一括 backfill で自分自身を取り込んだこと。**作る側（一括無効化）だけでは塞ぎ切れない**——フックも継続・再開の区切りで進行中の本セッションを途中記録しうる（`ee627069` で実例）。そこで**コミット側にも歯止め**を追加：コミット前検査（`check-workflow-action.py commit`）が、staged のセッション記録について frontmatter の `source_sha256`（生成時の元ログのハッシュ）と現在の元ログのハッシュを突き合わせ、不一致（＝元ログが生成後に変化＝まだ進行中）なら exit 2 で弾く（手作業の除外に頼らない。判定不能は過剰遮断しない。歯止めテスト＝`tests/tools/test_commit_in_progress_session_guard.py`）。これで「進行中セッションの記録はコミットしない」が機械的に保証される。追記専用マージ化（`44ed5ea8`）により単一取り込みの再実行は安全（同一はスキップ・縮小は保全・増えた分だけ反映）。フック導入前の取りこぼしは `b5bd051e`（フック導入 25 分前に終了）1 件のみで 2026-06-14 に記録済み（`b5951612`）。生成物は `git status` で確認し、コミット・push は利用者承認のうえで行う。

1. **実アプリ pilot**：前提だった P1 完了（PLC-DEC-010）を充足。配布前 smoke も合格済み（`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <root>`）。
2. ~~review-wave 要約コマンドの実装~~ **完了（2026-06-14、R-0、`bf3769a0` push 済み）**：詳細は §3 を参照。2026-06-13 記録の分類ラベル R-1 と併記説明文（種別定義上は R-0 の範囲）の食い違いを 2026-06-14 に利用者と確認し、意図文書を改めず既存「静的検査」（Requirement 1）に含める **R-0** を採用（利用者決定「R-0でよい」。分類記録＝`docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。本件は候補5（裁定負荷対策）の動機事例の一つ＝ラベルと文言の食い違いを利用者確認で是正した実例。
3. **レビュー証跡の機能側ポインタ要件の一般化**：配置規約の実装完了により再開可能（置き場の前提が確定済み）。
4. **P3（最終形）の専用 reopen 計画**：pilot 後に別途起こす（PLC-DEC-008・011）。主な項目＝disciplines／operations の `.reviewcompass/` 同型化（PLC-DEC-008 最終形）、旧パス読み取り互換の明示終了（PLC-DEC-011）、配置規約の「1 本の正本文書化」（段階 5 の未実施分）の再評価。
5. **裁定負荷対策（利用者決定の埋没防止）の規律改訂の検討**（利用者決定 2026-06-13「(b) で対応」）。動機事例＝PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は同決定の 2026-06-13 訂正欄）。検討候補：(1) 決定台帳の各項目に利用者発言の引用（出典）を必須化し、包括承認のみの項目は確定として扱わない、(2) LLM が利用者発言を決定文言へ再構成した場合は原文との差分を並べて個別確認（a-1 の同型を利用者決定へ拡張）、(3) 台帳の決定 ID ごとの出典欄を lint で機械検査、(4) **完成済みのセッション抽出ツール**（候補 5・上記）による台帳 ↔ 転写の突き合わせ検証。
6. 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`。
7. **「正本優先（事例より正本）」の規律化と、規律変更手続きの比例性（2026-06-14 着手・引き継ぎ）**：作業時に過去の事例を写すのでなく、正本（仕様・規律・強制コード）から要件を導く、という作業原則。動機＝本セッションで承認レコード・書き込み後検証 manifest を過去事例から手組みしていた（誤りの温床）こと。案2（生成ツール、`83abd1e6`）で手組みの温床は機械化済み。残る検討は次の3点：
   - (C) **「正本優先」を正式な規律にする**：正本確認の結果、新規規律は `self-improvement` 由来の `new_discipline` 提案を `workflow-management` が drafting→review→approval で実体化する手続きであり（`requirements.md:34`）、かつ「新規規律を1つ足すなら既存規律を1つ以上統廃合する」運用ルール（`requirements.md:124`）に従う＝重い手続き。
   - (D) **規律変更手続きに規模比例の軽い道が無い**：書き込み後検証は小規模1体／大規模3体と規模で軽重を変えるのに、規律変更手続きには小変更用の速路が無い。D を先に整えると C を軽く・正しく足せる（候補5 と同じ「手続きの作り」改善の族）。
   - (拡大) **生成ツールの横展開**：手組みしている他の成果物（例：reopen-classification 記録、in-progress／completed の reopen yaml 等）も、正本から生成するツール化を順次検討（まず承認レコードと manifest の2つは案2 で実装済み）。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。
