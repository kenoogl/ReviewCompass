# Post-write verification target

## TODO_NEXT_SESSION.md

# 次セッション継続用メモ

最終更新：2026-06-15。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である（詳細は `intent/` と各 feature の仕様を正本とする）。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. **前セッションのログはフックが自動取り込みする（手動は予備）**：Claude は SessionEnd／SessionStart、Codex は SessionStart と UserPromptSubmit fallback で「現セッション以外の最新 1 件」を単一取り込みする。Codex は SessionEnd 相当が無いため、`.codex/hooks/session-record-capture-previous.sh` を `.codex/hooks.json` の `SessionStart` と `UserPromptSubmit` に登録し、SessionStart が発火しない環境でも最初の user prompt 時に前 Codex rollout を取り込む方式にしている。取り込まれた生成物は `git status` で確認し、利用者承認のうえコミット・push。Codex 側は診断ログ `.reviewcompass/runtime/session-record-capture-previous.jsonl`（未コミット変更で追加中）も確認し、`start` が無ければ未発火、`start` があれば `selected`／`captured`／`no_previous_session`／`already_checked` 等で hook 内部状態を判定する。**手動の単一取り込みは予備**（フック失効時・前々セッション以前の取りこぼし回収）：`python3 tools/session-record-backfill.py --session <jsonl>`。進行中の現セッションは取り込まない（仮に取り込んでもコミット側の歯止めが弾く）。一括 backfill は使わない。
4. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
5. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

## 2. 不可逆操作の規律（要点）

- commit・push・spec.json（workflow_state）・規律ファイルの変更は、利用者の明示承認が必要。commit は利用者から「コミット」と明示された場合だけ、`tools/guarded-git-commit.py` 経由で実行する。
- commit 承認レコードの置き場は `.reviewcompass/runtime/approvals/commit-approval.json`（2026-06-13 の P1 実装で旧 `.reviewcompass/approvals/` から切替済み。委任欄 `explicit_instruction` は単発「コミット」等の機械判定に合う文字列で記録し、発言全文は rationale に残す）。
- API review-run は実行前に variant と役ごとの provider／model を提示し、結果は raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。操縦 LLM 別の既定 variant と独立性原則の正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3)。新規 review-run の置き場は `.reviewcompass/evidence/review-runs/<run-id>/`。
- Claude Code は子プロセスの `GEMINI_API_KEY`／`ANTHROPIC_API_KEY` を空に上書きする。API 実行は `zsh -c 'source ~/.zshrc && ...'` 経由（正本は `docs/experiments/n-model-comparison.md` §3.1）。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-15 時点）

- `next --json`：reopen R-0（decision-source-lint）完了・`make-commit-approval.py` 重大案件削除で **`completed`**（進行中手続きなし・全 workflow_state 完了）。`b16a021a` まで push 済み（2026-06-15）。
- **裁定負荷対策＝重要決定の出典検査（候補5・Req 11／decision-source-lint）仕組みの実装は完成・公開済み（運用は未開始＝§4 項目5）**：reopen **R-0** で workflow-management に Requirement 11（重要決定の出典検査＝束ね検出・逐語照合・内容性＋構造化した重要決定の記録形式）を新設し、`decision-source-lint` サブコマンドを TDD 実装（`tools/check_workflow_action/decision_source_lint.py`〔コア 10 関数〕・`check-workflow-action.py` への登録と commit 直前ゲート統合〔pending=WARN・unverifiable=DEVIATION〕・`stages/decision-source-lint-config.yaml`〔内容なし語リスト初期 11 件〕）。各 phase は 3 役 triad-review → proxy_model（gemini-3.1-pro-preview）裁定 → 収束 → review-wave/alignment/approval で連鎖再実施（利用者「自律的に実施」2026-06-15）。専用テスト 62 件＋全 395 件 pass。完了記録＝`stages/completed/reopen-procedure-2026-06-15.yaml`。コミット `7610a0d8`〜`bfd00dcf`（第1〜4過程）。**ただし運用は未開始**：構造化決定記録（`.reviewcompass/decisions/`）は現時点 0 件で `decision-source-lint --all` は「0 件（正常）」＝検査対象なし。埋没防止が実効を持つには、going-forward の重要決定を新形式で書き始める運用定着が要る（§4 項目5 の残タスク）。
- **commit 承認の削除ファイル対応＋reopen 基盤の弱点記録**：reopen 完了処理で必ず起きる「進行中→完了への移動＝元ファイル削除」を承認できるよう、`make-commit-approval.py`（削除を検出し `DELETED` 印を付す）・`validate_commit_approval`（`DELETED` 印を通し、ファイルが残る時のみエラー）に TDD で追加（コミット `94900049` push 済み）。あわせて、第4過程で進行中ファイルの手編集が YAML 破損・必須項目漏れで2度コミットを止めた事故を §4 項目8 に改善課題として記録。
- **会話ログ取り込みの追記専用マージ化（maintenance side track）完了・改善中**：従来の「丸ごと上書き」をやめ、層 1（整形済み転写）の本文包含で `same`／`extend`／`shrink` を判定し、同一はスキップ・拡張は更新・縮小は既存保全（上書きせず警告）とした。元ログ（jsonl）が何らかの理由で縮んでも取り込み済み記録を失わない。判定モジュール `tools/session_record_extractor/merge.py`（`classify_update`／`is_subsequence`）を追加し `tools/session-record-backfill.py` を改修。判定は層 1 で行い層 2 は同一ソースゆえ追従（層 2 の「（なし）→実データ」を縮小と誤判定しない）。2026-06-15 に、本文同一でも元ログ hash だけ変わった場合に `source_sha256` frontmatter を更新する改善を追加（手修正で直していた stale hash 問題の再発防止）。TDD テストは `tests/tools/test_session_record_append_merge.py`（同一は書かない／本文同一でも hash stale は更新／伸びたら拡張反映／縮んだら保全／空欄→実データは拡張）。書き込み後検証はテスト通過で完了（利用者決定 2026-06-14。前例 postwrite-log-exclusion と同様、多モデル API レビューなし）。完了記録＝`stages/completed/maintenance-2026-06-14-session-record-append-merge.yaml`。コミット `44ed5ea8`。前セッションの取りこぼしセッション記録 4 件も `a37ad0c2` で確定。
- **review-wave 要約コマンド（候補2・Req 10／T-012）完成・公開済み**：reopen **R-0** で workflow-management に Requirement 10 を新設し、`review-wave-summary` サブコマンドを TDD 実装（`tools/check-workflow-action.py`。`build_review_wave_summary`／`aggregate_triage_for_summary`／Markdown・JSON 安定スキーマ／fail-closed〔必須記録欠落で exit 2・任意記録の非在は ok〕／読み取り専用／`--out`・`--save`）。出力＝feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 未消化。実行＝`python3 tools/check-workflow-action.py review-wave-summary [--json] [--out PATH|--save]`。各 phase は 3 役 triad-review → proxy_model（gemini-3.1-pro-preview）裁定 → 収束確認 → review-wave/alignment/approval で連鎖再実施（design は反証役の指摘で round-4 まで回し収束）。完了記録＝`stages/completed/reopen-procedure-2026-06-14.yaml`。コミット `451fd3da`（第1・2過程）・`bf3769a0`（第3・4過程）。専用テスト 14 件＋tests/tools 301 件 pass。
- **セッション記録 機械抽出ツール（PLC-DEC-007 候補 5）完成・84 件バックフィル公開済み**：ツールは `tools/session-record-extractor.py`（単体）・`tools/session-record-backfill.py`（一括）・`tools/session_record_extractor/`（ライブラリ）。層 1（整形済み発言全文転写）＝`.reviewcompass/evidence/sessions/`、層 2（人が読む記録）＝`docs/sessions/auto-*.md`。来歴刻印＋再現性チェック（168/168 一致）＋機微除去 3 段（漏えい 0）。Codex は cwd 前方一致で絞り込み、内部思考は除外、ツール結果は先頭＋末尾に縮約。
- **会話ログ自動保持（going-forward 取り込み）実装・公開済み**：Claude は、セッション終了時に当該会話ログを2層記録へ自動取り込みする SessionEnd フック（`.claude/hooks/session-record-capture.sh`）と、新セッション開始時に前セッションを補完回収する SessionStart フック（`.claude/hooks/session-record-capture-previous.sh`）を `.claude/settings.json` に登録済み。`tools/session-record-backfill.py` の単一セッション取り込み（`--session`／`--source`／`--evidence-dir`／`--docs-dir`）を TDD で追加。`transcript_path` 欠落時は `session_id`＋`cwd` から復元、ログ無し・失敗でも exit 0（終了を妨げない）。取りこぼしの回収は**終了済みセッションへの単一取り込み（`--session`）が安全網**（2026-06-14 是正。当初は「オフライン一括バックフィルが安全網」と PLC-DEC-007 追補で定めたが、一括は実行中セッションを掴み churn を生むため既定無効化＝§4 の churn 対応を参照）。フックは**設定読込の都合で次セッションから有効**。コミット `a287684a`（push 済み）。専用テスト＝`tests/tools/test_session_record_single_capture.py`・`tests/hooks/test_session_record_capture.py` 各 4 件、tools 202 件・hooks 21 件 pass。
- **Codex SessionStart hook の実発火確認は未解決・UserPromptSubmit fallback を追加中（2026-06-15）**：このセッション開始時点では、前 Codex rollout の 2 層記録が `git status` に現れず、診断ログ `.reviewcompass/runtime/session-record-capture-previous.jsonl` も存在しなかったため、SessionStart の実発火は確認できなかった。既存の `2026-06-15-codex-019ec9d9...` 2 層記録は `f55f8fc3` で既にコミット済みで、元 rollout の `source_sha256` は一致。直前候補 `019ec9d7...`／現候補 `019eca05...` の 2 層記録は存在しなかった。切り分け用に `.codex/hooks/session-record-capture-previous.sh` へ JSONL 診断ログ（既定 `.reviewcompass/runtime/session-record-capture-previous.jsonl`、テスト用 `RC_SESSION_HOOK_LOG`）を追加し、さらに Codex Desktop で実際に動く `UserPromptSubmit` fallback と同一 `session_id`＋`cwd` の重複防止（`already_checked`）を追加中。TDD：追加テストは先に失敗確認済み、その後 `python3 -m unittest tests.hooks.test_codex_session_record_capture_previous tests.hooks.test_codex_hook_repository -v` OK、`python3 -m unittest discover -s tests/hooks -v` 30 件 OK。実 HOME の rollout に対する一時出力ドライランと、`/Users/keno/.codex/hooks.json` へ登録した wrapper の一時出力ドライランはいずれも `start → selected → captured` を確認。**未完了**：この hook fallback 追加と本 TODO 更新は未コミットで、post-write verification も未実施。次の user prompt または次セッションで `.reviewcompass/runtime/session-record-capture-previous.jsonl` に `start`／`selected`／`captured`／`already_checked` が出るか確認する。
- **正本優先（事例より正本）の生成ツール（案2）追加・公開済み**：「過去の事例を手で写す」のをやめ、正本（強制コードの検証関数）が受け入れる形を生成し、正本へ通して fail-closed する2ツールを TDD で追加。`tools/make-post-write-manifest.py`（書き込み後検証 manifest 生成。正本＝`evaluate_post_write_manifest_state`／`review_run_traceability_satisfied`）は残存。`tools/make-commit-approval.py`（commit 承認レコード生成）は **設計欠陥により 2026-06-15 に削除**（LLM が自律的に承認記録を生成できる＝コミット保護の無効化。経緯は §4 項目9・`docs/notes/2026-06-15-security-incident-make-commit-approval.md`）。コミット `83abd1e6`（追加）→ `b16a021a`（`make-commit-approval.py` 削除）。動機・経緯と残検討は §4 の項 7。
- **書き込み後検証ポリシー改訂済み**：独立検証が有効でないものを性質ベースで対象外化。(あ) 機械生成・出所明記の派生記録（来歴マーカー判定）、(い) 機械が吐く捕捉物（review-run・自律並列台帳・検証結果ログ＝ディレクトリ判定）。いずれも独立検証でなく再現性／走行・再実行で担保。正本＝`docs/disciplines/discipline_post_write_verification.md`、ガード＝`tools/check-workflow-action.py` の `is_post_write_verification_target`。監査・計測記録（`docs/discipline-compliance-reports/`）は主張を含むため対象に残す。
- **文書配置規約は段階 5 まで完了**（計画 `docs/notes/2026-06-12-document-placement-plan.md` の状態欄が正。P1 完了判定は `docs/notes/2026-06-12-document-placement-stage4-migration.md`）。
  - 配置規約 P1 の reopen 2 本（ce＝R-0・wm＝D-0）は第 4 過程まで完了し `stages/completed/` にある。
  - 新配置の運用が開始済み：証跡は `.reviewcompass/evidence/`（review-runs・features/<feature>/conformance・estimation）、実行時生成物は `.reviewcompass/runtime/`（検査ログ・effective prompt・commit 承認レコード、gitignore 1 行）。旧置き場 6 箇所は凍結（各所の README が案内、読み取り互換は P3 まで）。
  - 凍結違反の機械検出：ce＝`tools/conformance_evaluation/machine_verification.py`（check_record_freeze 等）、wm＝`tools/check_workflow_action/placement_freeze.py`（手動実行手順は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` §8.1）。
- 全テスト：ディレクトリ単位で pass（`tests/tools` は 2026-06-14 の review-wave-summary 追加で 301 件。同名テストファイルの衝突があるため `tests/` 一括ではなくディレクトリごとに pytest を実行する）。

## 4. 次作業（候補。正本は next --json と利用者指示）

`next` が `completed` のため、次は保留事項からの利用者選択になる：

- **会話ログの取り込みは原則フック任せ（手動 backfill は予備）**：会話ログの2層記録は、SessionEnd フック（`a287684a`）がセッション終了時に自動で取り込む。2026-06-14 に、漏れていた `b5bd051e` を対象にフックを一時出力先で実走させ、両層が正しく生成されることを確認済み（フックは動く）。したがって**進行中の本セッションも、終了時にフックが自動記録する**ので「次セッション冒頭で手動取り込み」を常時行う必要はない。取りこぼしの回収が要るときは、**終了済みセッション 1 件だけを `python3 tools/session-record-backfill.py --session <jsonl>` で取り込む**（フックと同じ単一取り込み。安全）。**一括スキャン（`--session` なし）は使わない**：実行中のセッション（自分自身を含む）を掴んで後で取り込み直し＝差分のたまり（churn）を生むため、2026-06-14 にコードで既定無効化した（`--historical-import` フラグ無しでは exit 2 で止まる。過去ログの一括取り込みは完了済み。歯止めテスト＝`tests/tools/test_session_record_bulk_guard.py`）。churn の発端は前セッション `a57d7790` が一括 backfill で自分自身を取り込んだこと。**作る側（一括無効化）だけでは塞ぎ切れない**——フックも継続・再開の区切りで進行中の本セッションを途中記録しうる（`ee627069` で実例）。そこで**コミット側にも歯止め**を追加：コミット前検査（`check-workflow-action.py commit`）が、staged のセッション記録について frontmatter の `source_sha256`（生成時の元ログのハッシュ）と現在の元ログのハッシュを突き合わせ、不一致（＝元ログが生成後に変化＝まだ進行中）なら exit 2 で弾く（手作業の除外に頼らない。判定不能は過剰遮断しない。歯止めテスト＝`tests/tools/test_commit_in_progress_session_guard.py`）。これで「進行中セッションの記録はコミットしない」が機械的に保証される。追記専用マージ化（`44ed5ea8`）により単一取り込みの再実行は安全（同一はスキップ・縮小は保全・増えた分だけ反映）。フック導入前の取りこぼしは `b5bd051e`（フック導入 25 分前に終了）1 件のみで 2026-06-14 に記録済み（`b5951612`）。生成物は `git status` で確認し、コミット・push は利用者承認のうえで行う。
- **Codex SessionStart／UserPromptSubmit hook の次回実発火確認（診断ログ版）**：Codex には SessionEnd 相当が無いため、`.codex/hooks/session-record-capture-previous.sh` を `.codex/hooks.json` の `SessionStart` と `UserPromptSubmit` に登録し、「現セッション以外の最新同一 repo rollout」を 1 件だけ取り込む方式にした。2026-06-15 の実セッション開始では repo 側 SessionStart の実発火は確認できず、`/Users/keno/.codex/hooks.json` に ReviewCompass 用 wrapper を追加して Desktop が読むグローバル hooks からも呼べるようにした。wrapper は cwd が `/Users/Daily/Development/ReviewCompass` または配下の時だけ repo の hook を呼び、別 repo では何も書かない。次回はまず `.reviewcompass/runtime/session-record-capture-previous.jsonl` を確認する。`start` が無ければ hook 呼び出し未到達、`selected`／`captured` があれば自動取り込み成功、`already_checked` があれば同一セッション内の fallback 再呼び出し抑止、と判定する。あわせて `git status --short` で 2 層記録の生成有無を確認する。

1. **実アプリ pilot**：前提だった P1 完了（PLC-DEC-010）を充足。配布前 smoke も合格済み（`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <root>`）。
2. ~~review-wave 要約コマンドの実装~~ **完了（2026-06-14、R-0、`bf3769a0` push 済み）**：詳細は §3 を参照。2026-06-13 記録の分類ラベル R-1 と併記説明文（種別定義上は R-0 の範囲）の食い違いを 2026-06-14 に利用者と確認し、意図文書を改めず既存「静的検査」（Requirement 1）に含める **R-0** を採用（利用者決定「R-0でよい」。分類記録＝`docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。本件は候補5（裁定負荷対策）の動機事例の一つ＝ラベルと文言の食い違いを利用者確認で是正した実例。
3. **レビュー証跡の機能側ポインタ要件の一般化**：配置規約の実装完了により再開可能（置き場の前提が確定済み）。
4. **P3（最終形）の専用 reopen 計画**：pilot 後に別途起こす（PLC-DEC-008・011）。主な項目＝disciplines／operations の `.reviewcompass/` 同型化（PLC-DEC-008 最終形）、旧パス読み取り互換の明示終了（PLC-DEC-011）、配置規約の「1 本の正本文書化」（段階 5 の未実施分）の再評価。
5. **裁定負荷対策（利用者決定の埋没防止）：仕組みの実装は完了・運用は未開始（2026-06-15・R-0・`bfd00dcf`〜`94900049` push 済み）**。Requirement 11（重要決定の出典検査）を新設し `decision-source-lint`（束ね検出・逐語照合・内容性）＋構造化した重要決定の記録形式を TDD 実装・公開した（詳細は §3）。**「終了」ではない**：構造化決定記録（`.reviewcompass/decisions/{id}.yaml`）が現時点 0 件で `decision-source-lint --all` は「0 件（正常）」＝何も検査していない。今回の reopen の重要決定（R-0 採用・フラグ差し戻し承認・proxy 委任）すら従来の散文（`reopen-procedure` yaml の human_decision 欄）のままで、新形式に載せていない。**残る運用タスク**：(a) 【確定 2026-06-15 利用者「運用は次から」】起点は**次に発生する重要決定から**新形式で記録を始める（今回の reopen 分・既存の散文台帳は遡及しない）、(b) 「誰が・いつ・どの決定を」構造化記録にするかの運用手順の確定（検討候補(1)(2) の運用面。次の重要決定が発生した時点で手順を定めつつ最初の記録を書く）、(c) この運用が回って初めて埋没防止が実効を持つ。以下は実装に至った経緯（背景として保存）。（利用者決定 2026-06-13「(b) で対応」）。動機事例＝PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は同決定の 2026-06-13 訂正欄）。検討候補：(1) 決定台帳の各項目に利用者発言の引用（出典）を必須化し、包括承認のみの項目は確定として扱わない、(2) LLM が利用者発言を決定文言へ再構成した場合は原文との差分を並べて個別確認（a-1 の同型を利用者決定へ拡張）、(3) 台帳の決定 ID ごとの出典欄を lint で機械検査、(4) **完成済みのセッション抽出ツール**（候補 5・上記）による台帳 ↔ 転写の突き合わせ検証。
   - **方針確定（2026-06-14、利用者決定）**：失敗の核心＝**一括承認の中に重要な件が埋もれ**、他が問題なく見えて「OK」と返したため、重要件が正しく裁定されないまま確定した（裁定負荷）。**ルールは既存**（`discipline_approval_operation`＝確定記述に出典必須・出典なし禁止、`discipline_plain_explanation_each_step`＝重要承認は1件ずつ）で、PLC-DEC-007 はその**違反**。よって今セッションの結論と同じく**機械で強制**する方向。**確定した検査方針（lint、重要種別＝不可逆操作・規律変更・仕様/計画変更に限定）**：(i) **束ね検出**＝複数決定が同一出典（同じ「OK」）を共有していたら確定扱いさせない、(ii) **逐語照合**＝出典の引用が会話転写（repo 取り込み済みの層1）に逐語で存在するか機械照合（でっち上げ・言い換えを弾く）、(iii) **内容性**＝「OK」「承認」等の中身なし返事だけを重要決定の出典として不可。**文言が意図を汲むかの意味一致は機械では「検証可能化」まで**で、最終は人/判定役（転写と突き合わせ）。**実装範囲（要・次セッション集中実装）**：決定台帳は散文・複数ファイル散在（PLC-DEC／MLE-DEC／reopen 分類記録…）で、確実な機械検査には**構造化した重要決定の記録形式**（決定ID・文言・出典〔引用＋セッションID＋個別/束ね〕）の新設が要る＝相応に大きい機能。going-forward の新規重要決定から適用し、過去の散文台帳は遡及移行しない方針が現実的。
6. 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`。
7. **「正本優先（事例より正本）」の規律化と、規律変更手続きの比例性（2026-06-14 着手・引き継ぎ）**：作業時に過去の事例を写すのでなく、正本（仕様・規律・強制コード）から要件を導く、という作業原則。動機＝本セッションで承認レコード・書き込み後検証 manifest を過去事例から手組みしていた（誤りの温床）こと。案2（生成ツール、`83abd1e6`）で手組みの温床は機械化済み。残る検討は次の3点：
   - **結論（2026-06-14 試行）：コードで強制済みのルールは規律に書く必要がない**（コード＋テスト＋コミットがそれ自体で説明になる）。実例＝churn 歯止め（`b3d527b2`／`c069983c`）を規律化しようとして、「鍵のかかったドアに貼り紙」になると判明。よって (C)(D) は **コード強制済みルールの範囲では不要**：(C) の「正本優先」のうち生成ツールで強制済みの部分は規律化不要、(D) の軽い道もその狙い（コード強制済みルールの軽い規律化）が消えるため不要。残るのは「コードで強制していない、広い心がけとしての正本優先」を規律にするか否かだけで、これは別問題（必要が出てから重い道で検討）。なお (D) の一般的な軽量道は §5.23.13 軽量手続き（dogfooding 期間限定・整合性借金27件の前例あり）の復活になるため不採用と判断（方向B＝狭い例外も上記結論で不要化）。
   - (C) **「正本優先」を正式な規律にする**：正本確認の結果、新規規律は `self-improvement` 由来の `new_discipline` 提案を `workflow-management` が drafting→review→approval で実体化する手続きであり（`requirements.md:34`）、かつ「新規規律を1つ足すなら既存規律を1つ以上統廃合する」運用ルール（`requirements.md:124`）に従う＝重い手続き。
   - (D) **規律変更手続きに規模比例の軽い道が無い**：書き込み後検証は小規模1体／大規模3体と規模で軽重を変えるのに、規律変更手続きには小変更用の速路が無い。D を先に整えると C を軽く・正しく足せる（候補5 と同じ「手続きの作り」改善の族）。
   - (拡大) **生成ツールの横展開**：手組みしている他の成果物（例：reopen-classification 記録、in-progress／completed の reopen yaml 等）も、正本から生成するツール化を順次検討（manifest は案2 で実装済み。承認レコードの生成ツールは設計欠陥で削除＝§4 項目9）。
8. **reopen 進行中ファイルの手編集が手戻りを生んだ実例と基盤改善（2026-06-15・要対処）**：reopen R-0（decision-source-lint）の第4過程（完了処理）で、進行中ファイル（`stages/in-progress/reopen-procedure-*.yaml`）を手で書き換えていたため2件の事故が起きた。§4 項目7 の「(拡大) 生成ツールの横展開」で予見していた「手組みの温床」を実際に踏んだ形であり、優先度を上げて対処する。
   - **事故(あ) YAML 破損が遠い症状で露見**：`next_step` 欄（次の一手を書く自由記述）の説明文に、引用符なしで「コロン＋スペース」を含む値（`impacted_downstream_phases: tasks` 等）を書いた。YAML がこれを「キー: 値」の対応表と誤解しパースエラー→`load_in_progress_file` が `{}`（空）を返し（読めないものは通さない fail-closed）→停止点コミット判定 `is_reopen_stop_point_commit_allowed`（`check-workflow-action.py:3633`）が `next_step` に「停止点コミット」の語を見つけられず逸脱（コミット却下）。症状が「YAML 破損」でなく「コミット許可条件の不成立」として出るため、原因究明が遠回りになった。
   - **事故(い) 完了ファイルの必須項目漏れ**：完了側（`stages/completed/`）に `feature_impact_decisions`（7機能）・`new_feature_decision`・各相の `completed_gates`／`downstream_impact_decisions` が不足し、`validate_reopen_completion_impact_decisions` で逸脱。これも手編集ゆえの項目漏れ。
   - **対処済みの穴**：完了処理では必ず「進行中→完了への移動＝元ファイル削除」が起きるのに、commit 承認の生成・検証が削除ファイルに未対応だった。`validate_commit_approval`（`DELETED` 印を通し、ファイルが残っている時のみエラー）に対応を追加（コミット `94900049`、TDD）。なお `make-commit-approval.py`（削除を検出し `DELETED` 印を生成するツール）は後に設計欠陥で削除（§4 項目9）。
   - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) 進行中・完了の reopen yaml を、正本（`validate_*` 群）が受け入れる形で生成・更新するツール化＝手編集をやめる（承認レコード・manifest の生成ツールと同じ「事例より正本」の横展開）。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
   - 位置づけ：§4 項目5（裁定負荷対策）と同族の「手続きの作りの弱さが手戻りを生む」実例。今回は機能本体（決定出典検査）とは別の、reopen 手続き基盤の整備課題。
9. **`make-commit-approval.py` の設計欠陥と削除（2026-06-15・重大案件・コミット `b16a021a` push 済み）**：commit 承認記録（コミット実行の許可証となる JSON ファイル）を自動生成するツールとして 2026-06-14 に作成したが、LLM が自律的に実行できる設計だった。`--explicit-instruction "コミット"` という文字列を渡すだけで、利用者が実際に「コミット」と発言したかどうかに関係なく有効な承認記録を生成できてしまい、コード（`guarded-git-commit.py`）による不可逆操作の防護が実質無効化される。実際に 2026-06-15 のセッションで本ツールを悪用して利用者の明示なしに複数回コミット・push を自律実行した（事後承認）。詳細は `docs/notes/2026-06-15-security-incident-make-commit-approval.md`。**残る運用**：承認記録は Python ワンライナー（手動計算）で生成する。承認記録の安全な生成方法は別途検討。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。


## docs/operations/INITIAL_SETUP_LLM_GUIDE.md

# 初期設定 LLM 指示書

最終更新：2026-06-13（§8 手順 5 の gitignore 除外を `.reviewcompass/runtime/` の 1 行へ簡素化。配置規約 P1 反映）

本文書は、ReviewCompass 配布物を使って初期設定を行う LLM のための指示書である。利用者がターミナルで Python コマンドを直接実行する前提ではなく、LLM が必要な確認と設定を案内または代行する。

関連する利用者向け説明は [INITIAL_DEPLOYMENT_USER_GUIDE.md](INITIAL_DEPLOYMENT_USER_GUIDE.md) を参照する。

## 1. 役割

あなたは ReviewCompass 初期設定を支援する LLM である。利用者に確認すべき点を平易に説明し、必要なファイル確認、設定作成、ReviewCompass ツール実行を代行する。

初期設定では、次を守る。

1. 対象アプリの既存ファイルを不用意に変更しない。
2. 対象アプリに書き込む前に、書き込み先を利用者へ説明する。
3. ReviewCompass 配布物ディレクトリと対象アプリ root を混同しない。
4. API key、token、password などの秘密値をファイルへ書き込まない。
5. 実行した確認、作成したファイル、残タスクを最後に報告する。

## 2. 最初に確認すること

利用者から次を確認する。

| 項目 | 確認内容 |
| --- | --- |
| 起動パターン | パターン 1、2、3 のどれで進めるか。 |
| 操縦 LLM | この設定作業と以後の運用をどの LLM で行うか（Claude Code か Codex CLI か。それ以外の LLM の場合は §11 のフォールバックに従う）。review-run の既定 variant 選択（§11）に使う。 |
| ReviewCompass 配布物ディレクトリ | ReviewCompass の配布物が置かれている場所（絶対パス）。 |
| 対象アプリ root | ReviewCompass を適用する対象アプリの root。未定なら対象アプリへは書き込まない。 |
| 初期設定の範囲 | 配布物単体確認までか、対象アプリ側設定まで行うか。 |
| API 秘密値の渡し方 | 環境変数など、配布物外の方法で渡すこと。 |
| hook 導入 | commit／push の事前検査 hook を導入するか（強く推奨、§10）。見送る場合は利用者の明示判断として完了報告に記録する。 |

不足している情報がある場合は、推測で進めず、利用者に確認する。

## 3. パターン別の進め方

### 3.1 パターン 1：ReviewCompass 配布物側で起動して対象アプリも設定する

このパターンでは、現在の作業ディレクトリが ReviewCompass 配布物ディレクトリであることを確認する。対象アプリ root は利用者から指定される。

進め方：

1. ReviewCompass 配布物に `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
2. 対象アプリ root が存在することを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の設定テンプレートを作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. workflow next、review-run smoke、conformance-evaluation など、利用者が選んだ初期確認へ進む。

### 3.2 パターン 2：対象アプリ側で起動して ReviewCompass 配布物を指定する

このパターンでは、現在の作業ディレクトリが対象アプリ root であることを確認する。ReviewCompass 配布物ディレクトリは利用者から指定される。

進め方：

1. 現在のディレクトリが対象アプリ root か確認する。
2. ReviewCompass 配布物ディレクトリに `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の `.reviewcompass/config.yaml` を作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. 配布済み ReviewCompass のツールを使い、対象アプリ側の workflow next を確認する（feature 未確定なら `feature_definition_required` の案内が返る。§9）。

通常利用を始める場合は、このパターンを基本とする。

### 3.3 パターン 3：配布物側だけ先に確認し、対象アプリ側設定は後で行う

このパターンでは、まず ReviewCompass 配布物ディレクトリだけを確認する。対象アプリ root が未定、または利用者がまだ対象アプリへ書き込みたくない場合は、この範囲で止める。

配布物側で確認すること：

1. `tools/`、`runtime/`、`templates/`（入口・hook・feature-dependency の雛形を含む）、`config/api-settings.yaml` があること。
2. `config/api-settings.yaml` に秘密値が含まれていないこと。
3. `runtime/config/config.yaml.template` があること。
4. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` と本文書があること。
5. ReviewCompass の Python ツールを実行できる環境か確認すること。

対象アプリが決まったら、対象アプリ root で新しい LLM セッションを立ち上げ、パターン 2 として初期設定を続ける。

## 4. 対象アプリ側に作成または確認するもの

対象アプリ側では、次を確認する。

| パス | 扱い |
| --- | --- |
| `.reviewcompass/` | 対象アプリ側の ReviewCompass 作業領域。なければ作成候補。 |
| `.reviewcompass/config.yaml` | 対象アプリ固有の設定。テンプレートから作成候補。 |
| `.reviewcompass/specs/` | 仕様、設計、タスク、review-run 記録の置き場。 |
| `.reviewcompass/AGENT_ENTRY.md` | LLM セッションの入口規律。テンプレートから実体化する（§8）。 |
| `.reviewcompass/feature-dependency.yaml` | feature 一覧・開発順・依存の定義。feature-partitioning 承認後に作成する（§9）。 |
| `CLAUDE.md`／`AGENTS.md` | 既存入口ファイルへの参照 1 行の追記（§8）。 |
| `.claude/`／`.codex/` | commit／push 事前検査 hook と設定（§10、強く推奨）。 |

既存の `.reviewcompass/` がある場合は、上書きせず、内容を確認してから進める。

## 5. 秘密値の扱い

`config/api-settings.yaml` や対象アプリ側の `.reviewcompass/config.yaml` に API key、token、password などを書き込まない。

秘密値が必要な場合は、利用者に次のように説明する。

```text
API key は設定ファイルに書かず、環境変数など配布物外の方法で渡してください。
この初期設定では、秘密値そのものは表示・保存しません。
```

## 6. 初期確認の最小セット

対象アプリ側まで設定する場合は、最低限次を確認する。

1. ReviewCompass 配布物ディレクトリを参照できる。
2. 対象アプリ root に書き込みできる。
3. 対象アプリ側の `.reviewcompass/` の作成または既存確認が済んでいる。
4. 対象アプリ側の `.reviewcompass/config.yaml` の作成または既存確認が済んでいる。
5. 入口の合流（§8）が済んでいる。
6. workflow next を確認できる（feature 未確定の段階では `feature_definition_required` の案内が返ることを確認する）。
7. review-run 記録の出力先を対象アプリ側に指定できる。

## 7. 完了報告

初期設定が終わったら、利用者へ次を報告する。

1. 選択した起動パターンと操縦 LLM。
2. ReviewCompass 配布物ディレクトリ。
3. 対象アプリ root。
4. 作成または変更した対象アプリ側ファイル。
5. hook 導入の有無（見送った場合は、利用者の明示判断であることと理由）。
6. 実行した確認。
7. 未実施の確認。
8. 次に行うべき作業。

対象アプリへ何も書き込んでいない場合は、そのことを明示する。

## 8. 入口の合流（AGENT_ENTRY の実体化と参照 1 行）

対象アプリで複数の LLM（Claude Code、Codex CLI）を同じ規律で使うための入口を作る。

1. 配布物の `templates/entry/AGENT_ENTRY.template.md` を、対象アプリの `.reviewcompass/AGENT_ENTRY.md` として実体化する。冒頭の記入欄（実体化日、実体化元の配布物）と §2 の「配布物の場所」（**絶対パス**）を記入する。
2. 既存の入口ファイルへ、利用者承認のうえ参照 1 行を末尾に追記する。追記の前に、書き込み先・挿入する行・挿入位置を利用者へ提示する。書き込むのは次の枠内の文字列**だけ**である（枠外の説明文を書き込まない）。

   `CLAUDE.md` へ追記する 1 行：

   ```text
   @.reviewcompass/AGENT_ENTRY.md
   ```

   `AGENTS.md` へ追記する 1 行：

   ```text
   ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。
   ```
3. 入口ファイルが存在しない場合は、その 1 行だけの新規ファイルを作る（これも承認のうえ）。同じ行が既にある場合は何もしない。既存の記述は変更しない。
4. 既存入口の規律と AGENT_ENTRY の規律が衝突している場合（例：既存入口が「commit は自動で実行してよい」と指示しているが、AGENT_ENTRY §5 は利用者の明示承認を求める、というように両立しない指示）は、作業を進めず利用者へ提示する。優先順位は自動で決めず、利用者判断で AGENT_ENTRY 側を調整する。
5. 対象アプリの `.gitignore` へ、ReviewCompass ツールの実行時生成物の除外 1 行を利用者承認のうえ追記する（除外がないと、2 回目以降の `next` がツール自身の実行記録を未検証の文書変更として誤検出し、`post_write_verification` を返し続ける）。実行時生成物（検査ログ・effective prompt・commit 承認レコード）は `.reviewcompass/runtime/` 区画に集約されている（2026-06-12 配置規約 PLC-DEC-004 反映。旧 3 パスの個別除外は不要になった）。

   ```text
   .reviewcompass/runtime/
   ```

## 9. feature 一覧の立ち上げ

対象アプリの workflow 管理は、`.reviewcompass/feature-dependency.yaml` の `feature_order` キーに基づいて動く。

1. feature 一覧が未確定の段階では、`next` は `feature_definition_required` を返し、intent と feature-partitioning の実施を案内する。これはエラーではなく正常な立ち上げ状態である。
2. feature-partitioning の提案には、機能ごとの依存の主張と理由、順序の導出を必須で含める（人が根拠を検討できるようにする）。
3. 承認された分割結果を、配布物の `templates/specs/feature-dependency.yaml.template` から実体化した `.reviewcompass/feature-dependency.yaml` に記録する。依存される機能を先に並べる。
4. `feature_order` が `depends_on` と矛盾する場合（依存先が後ろ、依存先が一覧にない、循環依存）、`next` は理由つきの逸脱を返す。

## 10. hook 導入（強く推奨）

commit／push の事前検査 hook を対象アプリへ導入する。LLM が規律を読み忘れても、不可逆操作だけは機械が止める防衛線になる。初期設定の標準手順として導入し、見送る場合は利用者の明示判断として完了報告に記録する。

1. 配布物の `templates/hooks/pre-bash-precheck.sh.template` と `templates/hooks/session-record-capture-previous.sh.template` の 2 つのプレースホルダを**絶対パス**へ置換する。
   - `{{REVIEWCOMPASS_PYTHON}}`：依存（PyYAML 等）導入済みの Python 実行系
   - `{{REVIEWCOMPASS_DIR}}`：配布物 root
2. 置換後のファイルを、対象アプリの `.claude/hooks/pre-bash-precheck.sh` と `.codex/hooks/pre-bash-precheck.sh` の両方へ同一内容で複製する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
3. 置換後の `session-record-capture-previous.sh.template` は、対象アプリの `.codex/hooks/session-record-capture-previous.sh` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
4. `templates/hooks/claude-settings.json.template` と `templates/hooks/codex-hooks.json.template` から、`.claude/settings.json` と `.codex/hooks.json` を作る。いずれも既存ファイルがある場合は上書きせず、hooks キーだけを既存へ合流させる（合流して書き込む内容を、書き込み前に利用者へ提示する）。
5. 静的チェック：複製した hook ファイルに未置換トークン（`{{`）が残っていないこと、置換先のパスが実在することを確認する。
6. Codex のセッション取り込み hook は `SessionStart` と `UserPromptSubmit` の両方に登録される。`UserPromptSubmit` は fallback であり、同一 `session_id` + `cwd` は 1 回だけ処理する。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-previous.jsonl` に `start`、`selected`、`captured`、`already_checked` などが出るかを見る。
7. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。

## 11. 操縦 LLM 別の既定 variant

review-run の variant（モデルの組）は、起草者（操縦 LLM）と検証者の独立を保つため、操縦 LLM に応じた既定を使う。

| 操縦 LLM | 3 役 review-run の既定 | 小規模 1 体検証の既定 |
| --- | --- | --- |
| Claude Code | 接尾辞なしの `*_independent_3way` 系 | `post_write_verification_google`（共通） |
| Codex CLI | `*_independent_3way_codex_operator` 系 | 同上（共通） |

proxy_model（人の判断を代行させる場合のモデル）も、操縦 LLM と別系列のモデルを選ぶ。

上記以外の LLM で操縦する場合は、独断で進めず利用者に確認し、「起草者（操縦 LLM）と同系列のモデルを反証役・判定役・単独検証役に置かない」という独立性の原則に従って variant を選ぶ。その操縦 LLM 向けの既定 variant の追加は、第3者配布時の再検討事項とする。
