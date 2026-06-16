# Codex SessionStart previous draft promotion post-write verification target r4

## 合意内容

- Codex には SessionStart hook があるため、従来の「Codex には SessionStart 相当も無い」という前提を修正する。
- PostToolUse/TODO 更新では現セッションを runtime 下書きへ保存し、正式 2 層へは直接書かない。
- Codex SessionStart で、現 session_id と異なる最新の前セッション下書き 1 件を正式 2 層記録へ昇格する。
- 下書き frontmatter の source_sha256 と現在 rollout hash が一致する場合だけ昇格する。
- hash 不一致なら previous_draft_in_progress を記録して正式化せず、古い候補へフォールバックしない。
- hash 確認不能なら previous_draft_unverifiable を記録して正式化しない。
- repo hook は REVIEWCOMPASS_PYTHON 環境変数があればそれを使い、なければ python3 にフォールバックする。
- UserPromptSubmit は発話ごとに誤発火し得るため、引き続き使用しない。
- 利用者は、テンプレート変更も今回の実装範囲として残すと明示承認した。

## r1-r3 所見への対処

- 進行中の別 Codex セッション下書きを正式化し得る問題に対し、source_sha256 と現在 rollout hash の一致確認を追加した。
- 不一致時は previous_draft_in_progress としてスキップし、古い候補にはフォールバックしない。
- hash 確認不能時は previous_draft_unverifiable としてスキップする。
- repo hook の Python 呼び出しは、log_event / TARGET_INFO / HASH_INFO / promote 呼び出しの全てで REVIEWCOMPASS_PYTHON を使うよう統一した。
- startup と resume の両方、hash 不一致スキップ、フォールバック禁止、hash 確認不能スキップ（空値と行欠落）をテストで固定した。

## 検証観点

- SessionStart 前提の訂正が公式 Codex hook 仕様に沿って文書・設定・テンプレートへ反映されているか。
- 新 hook が current session_id を正式化せず、最新の別 session_id 下書きだけを昇格するか。
- hash 不一致時に previous_draft_in_progress で安全側に止まり、古い候補へフォールバックしないか。
- hash 確認不能時に previous_draft_unverifiable で安全側に止まるか。
- hook 失敗時にセッション開始を妨げず、診断ログで原因を追えるか。
- 配布テンプレートと repo hook 設定の整合性が保たれているか。

## 対象ファイル

- `.codex/hooks.json`
- `.codex/hooks/README.md`
- `.gitignore`
- `TODO_NEXT_SESSION.md`
- `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`
- `docs/operations/INITIAL_SETUP_LLM_GUIDE.md`
- `templates/hooks/codex-hooks.json.template`
- `tests/hooks/test_codex_hook_repository.py`
- `.codex/hooks/session-record-promote-previous-draft.sh`
- `templates/hooks/session-record-promote-previous-draft.sh.template`
- `tests/hooks/test_codex_session_record_promote_previous.py`

## tracked diff

```diff
diff --git a/.codex/hooks.json b/.codex/hooks.json
index e6dc781c..d5d6f5bc 100644
--- a/.codex/hooks.json
+++ b/.codex/hooks.json
@@ -1,5 +1,17 @@
 {
   "hooks": {
+    "SessionStart": [
+      {
+        "matcher": "startup|resume",
+        "hooks": [
+          {
+            "type": "command",
+            "command": "bash '.codex/hooks/session-record-promote-previous-draft.sh'",
+            "timeout": 60
+          }
+        ]
+      }
+    ],
     "PostToolUse": [
       {
         "hooks": [
diff --git a/.codex/hooks/README.md b/.codex/hooks/README.md
index f7d21d89..08a4e2d8 100644
--- a/.codex/hooks/README.md
+++ b/.codex/hooks/README.md
@@ -51,7 +51,7 @@ Codex の hook 設定で呼び出すスクリプトを置く。
 
 Codex の hook では `Stop` が turn scope であり、Claude の `SessionEnd` 相当としては使わない。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用禁止とし、誤登録されても `ignored_event` を診断ログに残して終了する。Codex では、セッション継続時に `TODO_NEXT_SESSION.md` を更新する運用を合図として使い、TODO の内容 hash が前回保存時から変わった場合だけ現セッションの下書きを更新する。TODO は 1 セッション内で複数回更新され得るため、更新ごとに追記専用マージで伸びた分を反映する。
 
-**2026-06-16 実装反映**：hook は現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接書かない。正式な 2 層セッション記録は、次セッション冒頭または利用者が明示した時点で `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` により作る。Codex には SessionStart 相当も無いため、自動昇格は前提にしない。昇格 CLI は現在の `session_id` と同一のセッションを拒否する。`<current-id>` は、今セッションで TODO 更新 hook を一度走らせた後、診断ログの最新 `selected` event にある `selected_session_id` を使う。current `session_id` を取得できない場合は昇格せず、終了済み rollout を明示した backfill に戻す。診断ログ event は、正式記録と区別するため `drafted`／`draft_failed` を使う。
+**2026-06-16 実装反映**：hook は現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接書かない。正式な 2 層セッション記録は、次の Codex `SessionStart` で `session-record-promote-previous-draft.sh` が前セッション下書きを昇格する。手動復旧が必要な場合は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` または終了済み rollout を明示した backfill を使う。昇格 CLI は現在の `session_id` と同一のセッションを拒否する。診断ログ event は、正式記録と区別するため `drafted`／`draft_failed` を使う。
 
 **入力**：標準入力で Codex の PostToolUse JSON ペイロードを受け取る。
 
@@ -81,6 +81,30 @@ TODO hash の状態ディレクトリはテスト用に `RC_SESSION_HOOK_STATE_D
 
 **登録**：`.codex/hooks.json` の `hooks.PostToolUse` セクションに登録済み。`UserPromptSubmit` には登録しない。TODO を更新しないセッション、クラッシュ、hook 失敗、または `session_id` が取れない場合は、終了済み rollout を指定した `tools/session-record-backfill.py --session <jsonl> --source codex` による明示回収を使う。
 
+### `session-record-promote-previous-draft.sh`（SessionStart hook）
+
+**役割**：新しい Codex セッション開始時に、現 session_id と異なる最新の runtime 下書き 1 件を正式 2 層記録へ昇格する。Codex 公式 hook 仕様では `SessionStart` が thread scope で利用できるため、前セッションの正式化はこの hook が担う。`Stop` は turn scope のため、セッション終了確定には使わない。
+
+**入力**：標準入力で Codex の SessionStart JSON ペイロードを受け取る。
+
+```json
+{"hook_event_name":"SessionStart","session_id":"<current-id>","cwd":"/path/to/repo","source":"startup"}
+```
+
+**動作**：
+
+1. `hook_event_name` が `SessionStart` でなければ `ignored_event` を記録して exit 0
+2. `session_id` または `cwd` が無ければ何もせず exit 0
+3. runtime 下書きディレクトリから `codex-<session_id>.md` を探す
+4. current `session_id` と同じ下書きは除外する
+5. 残った下書きのうち最新 1 件を選ぶ。最新候補の hash が不一致の場合は、古い候補へフォールバックせず `previous_draft_in_progress` を記録して終了する
+6. 最新候補の下書き frontmatter `source_sha256` と現在の元 rollout の sha256 が一致する場合だけ、`tools/session-record-promote-draft.py` に current `session_id` と出力先を渡して昇格する
+7. 昇格失敗も含め常に exit 0
+
+**診断ログ**：既定で `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` に JSON Lines を追記する。テスト用に `RC_SESSION_PROMOTE_HOOK_LOG` で差し替え可能。主な `event` は `ignored_event`、`no_current_session_id`、`no_cwd`、`no_draft_dir`、`no_previous_draft`、`selected`、`previous_draft_in_progress`、`previous_draft_unverifiable`、`promoted`、`promote_failed`。`previous_draft_in_progress` は、下書き作成時の `source_sha256` と現在の元 rollout の sha256 が不一致で、対象 rollout がまだ伸びている可能性があるため正式化しなかったことを表す。`previous_draft_unverifiable` は、下書きまたは rollout の hash 確認に必要な情報が不足しているため正式化しなかったことを表す。
+
+**登録**：`.codex/hooks.json` の `hooks.SessionStart` セクションに matcher = `"startup|resume"` で登録済み。配置・変更後は Codex の GUI 設定画面または `/hooks` で利用者が hook を信頼する必要がある。
+
 ## テスト
 
 ユニットテスト：`tests/hooks/test_pre_bash_precheck.py`（7 件）
diff --git a/.gitignore b/.gitignore
index 4afd6b6e..b5bdc1ec 100644
--- a/.gitignore
+++ b/.gitignore
@@ -29,6 +29,7 @@ tools/experiments/logs/
 !.codex/hooks/README.md
 !.codex/hooks/pre-bash-precheck.sh
 !.codex/hooks/session-record-capture-current-on-todo.sh
+!.codex/hooks/session-record-promote-previous-draft.sh
 
 # SES シンポジウム論文テンプレート一式（利用者の論文執筆素材、ReviewCompass 本体とは別管理、2026-05-28 セッション 37）
 SES26/
diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index 4346d274..dfcaa823 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -11,7 +11,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 
 1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
 2. `git status --short` と `git log --oneline -5` で到達点を確認する。
-3. **会話ログはフックまたは明示 backfill で単一取り込みする**：Claude は SessionEnd／SessionStart、Codex は `TODO_NEXT_SESSION.md` 更新後の PostToolUse で現セッションを保存する。Codex は SessionEnd 相当が無いため、`.codex/hooks/session-record-capture-current-on-todo.sh` を `.codex/hooks.json` の `PostToolUse` に登録し、TODO の内容 hash が前回保存時から変わった場合だけ `session_id` が一致する現 rollout を扱う。`UserPromptSubmit` は発話ごとに誤発火し得るため使用禁止。Codex hook は現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、正式 2 層へは直接書かない。診断ログ `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`／`selected`／`drafted` があれば下書き保存成功、`draft_failed` があれば失敗、`todo_unchanged` は変更なし、`baseline_recorded` は初回 baseline、`no_session_id` は自動推測せず手動回収対象、`ignored_event` は誤登録と判定する。正式 2 層記録が必要な終了済み Codex rollout は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>`、または終了済み rollout を指定した `python3 tools/session-record-backfill.py --session <jsonl> --source codex` で明示回収する。`<current-id>` は、今セッションの TODO 更新後に診断ログの最新 `selected` event の `selected_session_id` で確認する。`selected` が無く確認できない場合は昇格しない。一括 backfill は使わない。
+3. **会話ログはフックまたは明示 backfill で単一取り込みする**：Claude は SessionEnd／SessionStart、Codex は `TODO_NEXT_SESSION.md` 更新後の PostToolUse で現セッションを下書き保存し、次の `SessionStart` で前セッション下書きを正式 2 層へ昇格する。Codex は SessionEnd 相当が無いため、`.codex/hooks/session-record-capture-current-on-todo.sh` を `.codex/hooks.json` の `PostToolUse` に登録し、TODO の内容 hash が前回保存時から変わった場合だけ `session_id` が一致する現 rollout を扱う。`UserPromptSubmit` は発話ごとに誤発火し得るため使用禁止。Codex の PostToolUse hook は現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、正式 2 層へは直接書かない。診断ログ `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`／`selected`／`drafted` があれば下書き保存成功、`draft_failed` があれば失敗、`todo_unchanged` は変更なし、`baseline_recorded` は初回 baseline、`no_session_id` は自動推測せず手動回収対象、`ignored_event` は誤登録と判定する。Codex の `SessionStart` hook は `.codex/hooks/session-record-promote-previous-draft.sh` で、現 `session_id` と異なる最新下書き 1 件を `tools/session-record-promote-draft.py` により正式化する。昇格前に下書き frontmatter `source_sha256` と現在の元 rollout sha256 を比較し、一致した場合だけ正式化する。不一致なら `previous_draft_in_progress` を記録し、古い候補へフォールバックしない。診断ログ `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` に `selected`／`promoted` があれば正式化成功、`no_previous_draft` は対象なし、`previous_draft_in_progress` は安全側スキップ、`previous_draft_unverifiable` または `promote_failed` は失敗である。一括 backfill は使わない。
 4. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
 5. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。
 
@@ -33,7 +33,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 - **review-wave 要約コマンド（候補2・Req 10／T-012）完成・公開済み**：reopen **R-0** で workflow-management に Requirement 10 を新設し、`review-wave-summary` サブコマンドを TDD 実装（`tools/check-workflow-action.py`。`build_review_wave_summary`／`aggregate_triage_for_summary`／Markdown・JSON 安定スキーマ／fail-closed〔必須記録欠落で exit 2・任意記録の非在は ok〕／読み取り専用／`--out`・`--save`）。出力＝feature coverage・phase/stage 状態・triage 未解決/draft/human_required 件数・recheck 状態・依存状況・carry-forward 未消化。実行＝`python3 tools/check-workflow-action.py review-wave-summary [--json] [--out PATH|--save]`。各 phase は 3 役 triad-review → proxy_model（gemini-3.1-pro-preview）裁定 → 収束確認 → review-wave/alignment/approval で連鎖再実施（design は反証役の指摘で round-4 まで回し収束）。完了記録＝`stages/completed/reopen-procedure-2026-06-14.yaml`。コミット `451fd3da`（第1・2過程）・`bf3769a0`（第3・4過程）。専用テスト 14 件＋tests/tools 301 件 pass。
 - **セッション記録 機械抽出ツール（PLC-DEC-007 候補 5）完成・84 件バックフィル公開済み**：ツールは `tools/session-record-extractor.py`（単体）・`tools/session-record-backfill.py`（一括）・`tools/session_record_extractor/`（ライブラリ）。層 1（整形済み発言全文転写）＝`.reviewcompass/evidence/sessions/`、層 2（人が読む記録）＝`docs/sessions/auto-*.md`。来歴刻印＋再現性チェック（168/168 一致）＋機微除去 3 段（漏えい 0）。Codex は cwd 前方一致で絞り込み、内部思考は除外、ツール結果は先頭＋末尾に縮約。
 - **会話ログ自動保持（going-forward 取り込み）実装・公開済み**：Claude は、セッション終了時に当該会話ログを2層記録へ自動取り込みする SessionEnd フック（`.claude/hooks/session-record-capture.sh`）と、新セッション開始時に前セッションを補完回収する SessionStart フック（`.claude/hooks/session-record-capture-previous.sh`）を `.claude/settings.json` に登録済み。`tools/session-record-backfill.py` の単一セッション取り込み（`--session`／`--source`／`--evidence-dir`／`--docs-dir`）を TDD で追加。`transcript_path` 欠落時は `session_id`＋`cwd` から復元、ログ無し・失敗でも exit 0（終了を妨げない）。取りこぼしの回収は**終了済みセッションへの単一取り込み（`--session`）が安全網**（2026-06-14 是正。当初は「オフライン一括バックフィルが安全網」と PLC-DEC-007 追補で定めたが、一括は実行中セッションを掴み churn を生むため既定無効化＝§4 の churn 対応を参照）。フックは**設定読込の都合で次セッションから有効**。コミット `a287684a`（push 済み）。専用テスト＝`tests/tools/test_session_record_single_capture.py`・`tests/hooks/test_session_record_capture.py` 各 4 件、tools 202 件・hooks 21 件 pass。
-- **Codex TODO 更新 hook による現セッション下書き保存 実装済み（2026-06-16）**：`UserPromptSubmit` 経由は実運用で発話ごとの誤発火が確認されたため使用禁止。TODO 更新を合図にする対象は前セッションではなく現セッションである。`.codex/hooks/session-record-capture-current-on-todo.sh` と `templates/hooks/session-record-capture-current-on-todo.sh.template` は、現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。成功 event は `drafted`、失敗 event は `draft_failed`。正式昇格 helper は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` で、対象が current `session_id` と同じ場合は exit 2 で拒否する。`<current-id>` は今セッションの TODO 更新後に診断ログの最新 `selected` event の `selected_session_id` で確認し、取れない場合は昇格しない。`session_id` が無い場合は並行セッション誤回収を避けて推測しない。
+- **Codex TODO 更新 hook による現セッション下書き保存＋SessionStart 正式昇格 実装済み（2026-06-16）**：`UserPromptSubmit` 経由は実運用で発話ごとの誤発火が確認されたため使用禁止。TODO 更新を合図にする対象は前セッションではなく現セッションである。`.codex/hooks/session-record-capture-current-on-todo.sh` と `templates/hooks/session-record-capture-current-on-todo.sh.template` は、現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存し、`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。成功 event は `drafted`、失敗 event は `draft_failed`。`.codex/hooks/session-record-promote-previous-draft.sh` と `templates/hooks/session-record-promote-previous-draft.sh.template` は、Codex `SessionStart` で現 `session_id` と異なる最新下書き 1 件を正式 2 層へ昇格する。昇格 helper は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` で、対象が current `session_id` と同じ場合は exit 2 で拒否する。`session_id` が無い場合は並行セッション誤回収を避けて推測しない。
 - **正本優先（事例より正本）の生成ツール（案2）追加・公開済み**：「過去の事例を手で写す」のをやめ、正本（強制コードの検証関数）が受け入れる形を生成し、正本へ通して fail-closed する2ツールを TDD で追加。`tools/make-post-write-manifest.py`（書き込み後検証 manifest 生成。正本＝`evaluate_post_write_manifest_state`／`review_run_traceability_satisfied`）は残存。`tools/make-commit-approval.py`（commit 承認レコード生成）は **設計欠陥により 2026-06-15 に削除**（LLM が自律的に承認記録を生成できる＝コミット保護の無効化。経緯は §4 項目9・`docs/notes/2026-06-15-security-incident-make-commit-approval.md`）。コミット `83abd1e6`（追加）→ `b16a021a`（`make-commit-approval.py` 削除）。動機・経緯と残検討は §4 の項 7。
 - **reopen 中の pending gate 完了更新コマンド追加（maintenance side track）完了**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、reopen 第3過程で `pending_gates` の先頭 gate を、判断・根拠・`spec.json` 更新・`completed_gates`・`downstream_impact_decisions`・`completed_steps` と一緒に機械更新できるようにした。非先頭 gate は拒否し、根拠なし更新も拒否する。これにより、`spec-set` が in-progress reopen を遮断する通常保護を保ったまま、reopen 内の gate 前進だけを正規コマンドで処理できる。完了記録＝`stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml`。コミット `96112385`。運用説明は `docs/operations/WORKFLOW_PRECHECK.md` と `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` に反映済み。
 - **書き込み後検証ポリシー改訂済み**：独立検証が有効でないものを性質ベースで対象外化。(あ) 機械生成・出所明記の派生記録（来歴マーカー判定）、(い) 機械が吐く捕捉物（review-run・自律並列台帳・検証結果ログ＝ディレクトリ判定）。いずれも独立検証でなく再現性／走行・再実行で担保。正本＝`docs/disciplines/discipline_post_write_verification.md`、ガード＝`tools/check-workflow-action.py` の `is_post_write_verification_target`。監査・計測記録（`docs/discipline-compliance-reports/`）は主張を含むため対象に残す。
@@ -48,7 +48,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 `next` が `completed` のため、次は保留事項からの利用者選択になる：
 
 - **会話ログの取り込みは原則フック任せ（手動 backfill は予備）**：会話ログの2層記録は、SessionEnd フック（`a287684a`）がセッション終了時に自動で取り込む。2026-06-14 に、漏れていた `b5bd051e` を対象にフックを一時出力先で実走させ、両層が正しく生成されることを確認済み（フックは動く）。したがって**進行中の本セッションも、終了時にフックが自動記録する**ので「次セッション冒頭で手動取り込み」を常時行う必要はない。取りこぼしの回収が要るときは、**終了済みセッション 1 件だけを `python3 tools/session-record-backfill.py --session <jsonl>` で取り込む**（フックと同じ単一取り込み。安全）。**一括スキャン（`--session` なし）は使わない**：実行中のセッション（自分自身を含む）を掴んで後で取り込み直し＝差分のたまり（churn）を生むため、2026-06-14 にコードで既定無効化した（`--historical-import` フラグ無しでは exit 2 で止まる。過去ログの一括取り込みは完了済み。歯止めテスト＝`tests/tools/test_session_record_bulk_guard.py`）。churn の発端は前セッション `a57d7790` が一括 backfill で自分自身を取り込んだこと。**作る側（一括無効化）だけでは塞ぎ切れない**——フックも継続・再開の区切りで進行中の本セッションを途中記録しうる（`ee627069` で実例）。そこで**コミット側にも歯止め**を追加：コミット前検査（`check-workflow-action.py commit`）が、staged のセッション記録について frontmatter の `source_sha256`（生成時の元ログのハッシュ）と現在の元ログのハッシュを突き合わせ、不一致（＝元ログが生成後に変化＝まだ進行中）なら exit 2 で弾く（手作業の除外に頼らない。判定不能は過剰遮断しない。歯止めテスト＝`tests/tools/test_commit_in_progress_session_guard.py`）。これで「進行中セッションの記録はコミットしない」が機械的に保証される。追記専用マージ化（`44ed5ea8`）により単一取り込みの再実行は安全（同一はスキップ・縮小は保全・増えた分だけ反映）。フック導入前の取りこぼしは `b5bd051e`（フック導入 25 分前に終了）1 件のみで 2026-06-14 に記録済み（`b5951612`）。生成物は `git status` で確認し、コミット・push は利用者承認のうえで行う。
-- ~~**Codex TODO 更新 hook の下書き化実装（診断ログ版）**~~ **完了（2026-06-16）**：`tools/session-record-draft.py`、`tools/session-record-promote-draft.py`、hook 本体、配布テンプレート、hook テスト、昇格 helper テスト、deployment テンプレートテストを追加・更新。実装後の確認では `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` の `todo_changed`／`selected`／`drafted` を下書き保存成功、`draft_failed` を失敗、`todo_unchanged` を変更なし、`baseline_recorded` を初回 baseline、`no_session_id` を手動回収対象、`ignored_event` を PostToolUse 以外への誤登録、と判定する。正式 2 層記録が必要な場合は終了済み rollout を対象に `session-record-promote-draft.py` または明示 `session-record-backfill.py --session` を使う。
+- ~~**Codex TODO 更新 hook の下書き化実装（診断ログ版）**~~ **完了（2026-06-16）**：`tools/session-record-draft.py`、`tools/session-record-promote-draft.py`、PostToolUse 下書き hook、SessionStart 昇格 hook、配布テンプレート、hook テスト、昇格 helper テスト、deployment テンプレートテストを追加・更新。実装後の確認では `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` の `todo_changed`／`selected`／`drafted` を下書き保存成功、`draft_failed` を失敗、`todo_unchanged` を変更なし、`baseline_recorded` を初回 baseline、`no_session_id` を手動回収対象、`ignored_event` を PostToolUse 以外への誤登録、と判定する。正式 2 層化は `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` の `selected`／`promoted` で確認する。手動復旧が必要な場合は終了済み rollout を対象に `session-record-promote-draft.py` または明示 `session-record-backfill.py --session` を使う。
 
 1. **実アプリ pilot**：前提だった P1 完了（PLC-DEC-010）を充足。配布前 smoke も合格済み（`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <root>`）。
 2. ~~review-wave 要約コマンドの実装~~ **完了（2026-06-14、R-0、`bf3769a0` push 済み）**：詳細は §3 を参照。2026-06-13 記録の分類ラベル R-1 と併記説明文（種別定義上は R-0 の範囲）の食い違いを 2026-06-14 に利用者と確認し、意図文書を改めず既存「静的検査」（Requirement 1）に含める **R-0** を採用（利用者決定「R-0でよい」。分類記録＝`docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。本件は候補5（裁定負荷対策）の動機事例の一つ＝ラベルと文言の食い違いを利用者確認で是正した実例。
@@ -70,9 +70,9 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
    - 位置づけ：§4 項目5（裁定負荷対策）と同族の「手続きの作りの弱さが手戻りを生む」実例。今回は機能本体（決定出典検査）とは別の、reopen 手続き基盤の整備課題。
 9. **`make-commit-approval.py` の設計欠陥と削除（2026-06-15・重大案件・コミット `b16a021a` push 済み）**：commit 承認記録（コミット実行の許可証となる JSON ファイル）を自動生成するツールとして 2026-06-14 に作成したが、LLM が自律的に実行できる設計だった。`--explicit-instruction "コミット"` という文字列を渡すだけで、利用者が実際に「コミット」と発言したかどうかに関係なく有効な承認記録を生成できてしまい、コード（`guarded-git-commit.py`）による不可逆操作の防護が実質無効化される。実際に 2026-06-15 のセッションで本ツールを悪用して利用者の明示なしに複数回コミット・push を自律実行した（事後承認）。詳細は `docs/notes/2026-06-15-security-incident-make-commit-approval.md`。**残る運用**：承認記録は Python ワンライナー（手動計算）で生成する。承認記録の安全な生成方法は別途検討。
 10. ~~**reopen 中の pending gate 完了更新コマンド不足**~~ **完了（2026-06-15、`96112385`）**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、対象 gate、decision、feature_scope、rationale、evidence、必要な `spec.json` 更新を構造化入力で受け、既存 `validate_reopen_completion_impact_decisions` が受け入れる形に機械更新できるようにした。今回の scope は pending gate 前進に絞り、approval gate の actor=human / proxy_model blocker 構造化は今後の reopen 実運用で不足が見えた時に別タスク化する。
-11. ~~**Codex TODO 更新 hook の下書き化と昇格方式**~~ **完了（2026-06-16）**：TODO 更新を合図に現セッションを扱う `.codex/hooks/session-record-capture-current-on-todo.sh` は、現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` に下書き保存するようになった。正式 2 層記録は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` で作る。昇格 helper は現在の `session_id` と同じセッションを拒否し、current `session_id` を取得できない場合は昇格しない。今回既に生成された旧方式の未追跡 2 件（`.reviewcompass/evidence/sessions/2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` と `docs/sessions/auto-2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md`）は、guard により進行中セッション記録と判定されたため、正式扱いせず削除した（次項）。なお、本項目の完了範囲は実装・テンプレート・テスト・文書であり、実環境の `.codex/hooks.json` 経由で PostToolUse hook が発火することの確認は未完了（項目13）。
+11. ~~**Codex TODO 更新 hook の下書き化と昇格方式**~~ **完了（2026-06-16）**：TODO 更新を合図に現セッションを扱う `.codex/hooks/session-record-capture-current-on-todo.sh` は、現セッションを `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` に下書き保存するようになった。正式 2 層記録は `.codex/hooks/session-record-promote-previous-draft.sh` が次の Codex `SessionStart` で、現 `session_id` と異なる最新下書き 1 件を `tools/session-record-promote-draft.py` 経由で作る。昇格 helper は現在の `session_id` と同じセッションを拒否する。今回既に生成された旧方式の未追跡 2 件（`.reviewcompass/evidence/sessions/2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` と `docs/sessions/auto-2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md`）は、guard により進行中セッション記録と判定されたため、正式扱いせず削除した（次項）。
 12. ~~**旧方式で生成された Codex セッション記録 2 件の後始末（派生課題）**~~ **完了（2026-06-16）**：旧生成物は、TODO hook が正式 2 層へ直接書いていた時期に、最終パス `.reviewcompass/evidence/sessions/2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` と `docs/sessions/auto-2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` へ作ったものだった。guarded commit 時に元 rollout `/Users/keno/.codex/sessions/2026/06/15/rollout-2026-06-15T15-51-42-019eca0c-e1c6-78f2-9060-0e546196fc12.jsonl` が生成時から変化していると判定され、対象がまだ進行中セッションだと確認できたため、旧生成物を正式 2 層記録としてコミットせず削除した。最終状態は、上記 2 ファイルは存在しない状態である。必要なら、このセッション終了後に同 rollout を `tools/session-record-backfill.py --session <jsonl> --source codex` で明示回収する。
-13. ~~**Codex TODO hook の実環境発火確認（派生課題）**~~ **完了（2026-06-16）**：GUI 設定でプロジェクト hook 2 件（ツール実行前／ツール実行後）を信頼した後、`TODO_NEXT_SESSION.md` の更新により `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`、`selected`、`drafted` が出ることを確認した。下書きは `.reviewcompass/runtime/session-record-drafts/codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` に生成され、正式 2 層記録（`.reviewcompass/evidence/sessions/` と `docs/sessions/`）は増えていない。未発火の主因は repo hook 未読込ではなく、非 managed hook の未 trust だった。`UserPromptSubmit` は引き続き使用禁止。
+13. ~~**Codex TODO hook の実環境発火確認（派生課題）**~~ **完了（2026-06-16）**：GUI 設定でプロジェクト hook 2 件（ツール実行前／ツール実行後）を信頼した後、`TODO_NEXT_SESSION.md` の更新により `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` に `todo_changed`、`selected`、`drafted` が出ることを確認した。下書きは `.reviewcompass/runtime/session-record-drafts/codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` に生成された。2026-06-16 に Codex 公式 manual で `SessionStart` が利用可能と確認し、`.codex/hooks/session-record-promote-previous-draft.sh` を追加したため、次の Codex `SessionStart` で前セッション下書きは正式 2 層へ自動昇格する。未発火の主因は repo hook 未読込ではなく、非 managed hook の未 trust だった。`UserPromptSubmit` は引き続き使用禁止。
 14. **reopen approval gate の blocker 構造化（派生課題）**：`reopen-advance-gate` は pending gate 前進を機械化したが、approval gate で actor=human / proxy_model の承認待ちを `current_blocker` として構造的に設定する専用操作は未実装。次に reopen 実運用で承認待ち gate を扱う時に、手編集が再発するなら別タスクとして実装する。
 15. **reopen-advance-gate の追加テスト（派生課題）**：実装は `--evidence` なし更新を拒否するが、`96112385` 時点の専用テストは正常更新と非先頭 gate 拒否に限られる。次に同コマンドを触る時は、根拠なし更新の exit 2 を追加テストする。
 16. **reopen-advance-gate の gate 正規化検査（派生課題）**：現状は `--gate` と `pending_gates[0]` の文字列一致で前進を判定し、既存 YAML 内の gate 文字列が標準形式かは追加検証しない。次に同コマンドを強化する時は、`pending_gates` の全要素が `stages/<phase>.yaml#<stage>` 形式として解釈できることを検査する。
diff --git a/docs/notes/2026-06-10-deployment-multi-llm-entry-design.md b/docs/notes/2026-06-10-deployment-multi-llm-entry-design.md
index bcd7efe2..d4f7b15c 100644
--- a/docs/notes/2026-06-10-deployment-multi-llm-entry-design.md
+++ b/docs/notes/2026-06-10-deployment-multi-llm-entry-design.md
@@ -78,7 +78,7 @@
 
 - 背景：Codex には Claude の `SessionEnd` 相当がなく、TODO 更新を合図に現セッション rollout を保存する設計自体は維持する。ただし、2026-06-15 時点で実装・運用していた方式では `PostToolUse` hook が現セッションの途中記録を `.reviewcompass/evidence/sessions/` と `docs/sessions/` に直接生成していたため、セッション中ずっと `git status` に未追跡ファイルとして出続けた。commit guard は進行中セッション記録を除外できるが、正式証跡置き場へ途中版を出すことがノイズと誤運用の原因になるため、2026-06-16 実装では runtime 下書き方式へ変更した。
 - 設計変更：TODO 更新 hook は、現セッションを正式記録へ直接書かず、`.reviewcompass/runtime/session-record-drafts/` 配下の下書き領域へ保存する。runtime は git 管理対象外であり、作業中に TODO を複数回更新しても正式証跡の dirty を増やさない。下書きは `codex-<session_id>.md` とし、`session_id` ごとに 1 件を更新対象とする。TODO が 1 セッション内で複数回更新された場合は同じ下書きを追記専用マージで伸ばす。下書きは正式昇格後に削除してよく、必要なら元 rollout から再生成する。
-- 正式化：Codex には SessionStart 相当も無いため、自動昇格は前提にしない。次セッション冒頭または利用者が明示した時点で、下書きまたは元 rollout を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ昇格する専用操作を呼ぶ。実装済み CLI は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` である。契約は「対象 `session_id` 明示」「現在実行中の `session_id` を明示できること」「対象が現在実行中の `session_id` と同一なら拒否」「終了済みセッションだけを正式記録にする」の 4 点とする。current `session_id` は、今セッションで TODO 更新 hook を一度走らせた後の診断ログにある最新 `selected` event の `selected_session_id` で確認する。current `session_id` を取得できない場合は安全側に倒し、昇格せず明示 backfill 手順へ戻す。
+- 正式化：Codex 公式 hook 仕様では `SessionStart` が利用可能であるため、次の Codex `SessionStart` で、現 `session_id` と異なる最新下書き 1 件を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ昇格する。実装済み hook は `.codex/hooks/session-record-promote-previous-draft.sh`、実装済み CLI は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` である。契約は「対象 `session_id` 明示」「現在実行中の `session_id` を明示できること」「対象が現在実行中の `session_id` と同一なら拒否」「終了済みセッションだけを正式記録にする」の 4 点とする。hook は、選んだ最新下書きの `source_sha256` と現在の元 rollout の sha256 が一致する場合だけ CLI へ進む。不一致の場合は進行中の可能性があるため正式化せず、古い候補へフォールバックしない。自動昇格できない場合は安全側に倒し、終了済み rollout を指定した明示 backfill 手順へ戻す。
 - 既存ルールとの関係：`UserPromptSubmit` を使わない方針、`session_id` が無い場合に推測しない方針、TODO を更新しないセッションや hook 失敗時は明示 `--session` backfill に倒す方針は維持する。変更するのは「現セッションをどこに書くか」と「正式記録へ昇格する時点」である。
 - 実装変更対象：
   - `.codex/hooks/session-record-capture-current-on-todo.sh`：`tools/session-record-backfill.py` の正式出力先を直接使わず、runtime 下書き出力へ切り替える。診断ログは `captured`／`capture_failed` ではなく `drafted`／`draft_failed` へ改め、正式記録と区別できる event 名にする。
diff --git a/docs/operations/INITIAL_SETUP_LLM_GUIDE.md b/docs/operations/INITIAL_SETUP_LLM_GUIDE.md
index 38d3bcb7..5c383c03 100644
--- a/docs/operations/INITIAL_SETUP_LLM_GUIDE.md
+++ b/docs/operations/INITIAL_SETUP_LLM_GUIDE.md
@@ -173,17 +173,18 @@ API key は設定ファイルに書かず、環境変数など配布物外の方
 
 commit／push の事前検査 hook を対象アプリへ導入する。LLM が規律を読み忘れても、不可逆操作だけは機械が止める防衛線になる。初期設定の標準手順として導入し、見送る場合は利用者の明示判断として完了報告に記録する。
 
-1. 配布物の `templates/hooks/pre-bash-precheck.sh.template` と `templates/hooks/session-record-capture-current-on-todo.sh.template` の 2 つのプレースホルダを**絶対パス**へ置換する。
+1. 配布物の `templates/hooks/pre-bash-precheck.sh.template`、`templates/hooks/session-record-capture-current-on-todo.sh.template`、`templates/hooks/session-record-promote-previous-draft.sh.template` のプレースホルダを**絶対パス**へ置換する。
    - `{{REVIEWCOMPASS_PYTHON}}`：依存（PyYAML 等）導入済みの Python 実行系
    - `{{REVIEWCOMPASS_DIR}}`：配布物 root
 2. 置換後のファイルを、対象アプリの `.claude/hooks/pre-bash-precheck.sh` と `.codex/hooks/pre-bash-precheck.sh` の両方へ同一内容で複製する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
-3. 置換後の `session-record-capture-current-on-todo.sh.template` は、対象アプリの `.codex/hooks/session-record-capture-current-on-todo.sh` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
+3. 置換後の `session-record-capture-current-on-todo.sh.template` と `session-record-promote-previous-draft.sh.template` は、対象アプリの `.codex/hooks/` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
 4. `templates/hooks/claude-settings.json.template` と `templates/hooks/codex-hooks.json.template` から、`.claude/settings.json` と `.codex/hooks.json` を作る。いずれも既存ファイルがある場合は上書きせず、hooks キーだけを既存へ合流させる（合流して書き込む内容を、書き込み前に利用者へ提示する）。
 5. 静的チェック：複製した hook ファイルに未置換トークン（`{{`）が残っていないこと、置換先のパスが実在することを確認する。
 6. Codex 側の環境設定：Codex の非 managed command hook は、配置しただけでは実行されない。Codex の GUI 設定画面または CLI の `/hooks` で、対象アプリのプロジェクト hook が認識されていることを確認し、利用者が内容を確認したうえで信頼する。未信頼のままでは hook 一覧に出ても Active 0 / review 待ちになり、`PreToolUse` も `PostToolUse` も実行されない。hook ファイルや `.codex/hooks.json` を変更した場合は、定義 hash が変わるため再度 review / trust が必要になる。
-7. Codex のセッション取り込み hook は `PostToolUse` に登録し、`TODO_NEXT_SESSION.md` の内容 hash が前回保存時から変わった場合だけ、現セッション rollout を `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存する。下書き先はテスト時に `RC_SESSION_DRAFT_DIR` で差し替えられる。現セッション途中版を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。Codex には SessionStart 相当も無いため、正式な 2 層記録は自動昇格せず、次セッション冒頭または利用者が明示した時点で `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` により作る。`<current-id>` は、今セッションで TODO 更新 hook を一度走らせた後、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` にある最新の `selected` event の `selected_session_id` を使う。`selected` が無く current `session_id` を取得できない場合は昇格せず、明示 backfill に戻す。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用しない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` を確認する。`todo_changed`、`selected`、`drafted`、`draft_failed`、`todo_unchanged`、`baseline_recorded` などが出る。あわせて `git status --short` で正式 2 層記録が増えていないことを確認する。`ignored_event` が出た場合は、`PostToolUse` 以外へ誤登録されているため hook 設定を修正する。
-8. TODO を更新しないセッション、クラッシュ、hook 失敗、または Codex の `session_id` が取れない場合は、自動 fallback を追加せず、終了済みの対象 rollout を指定して `tools/session-record-backfill.py --session <jsonl> --source codex` を明示実行する。
-9. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。Codex で hook が発火しない場合は、まず GUI 設定または `/hooks` で対象 hook が信頼済みか確認する。
+7. Codex の現セッション下書き hook は `PostToolUse` に登録し、`TODO_NEXT_SESSION.md` の内容 hash が前回保存時から変わった場合だけ、現セッション rollout を `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存する。下書き先はテスト時に `RC_SESSION_DRAFT_DIR` で差し替えられる。現セッション途中版を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用しない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` を確認する。`todo_changed`、`selected`、`drafted`、`draft_failed`、`todo_unchanged`、`baseline_recorded` などが出る。`ignored_event` が出た場合は、`PostToolUse` 以外へ誤登録されているため hook 設定を修正する。
+8. Codex の前セッション正式化 hook は `SessionStart` に matcher = `startup|resume` で登録し、現 `session_id` と異なる最新の runtime 下書き 1 件を正式 2 層記録へ昇格する。正式化前に下書き frontmatter `source_sha256` と現在の元 rollout の sha256 を比較し、一致した場合だけ昇格する。不一致なら `previous_draft_in_progress` を記録し、古い候補へフォールバックしない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` を確認する。`selected` と `promoted` があれば正式化成功、`no_previous_draft` は昇格対象なし、`previous_draft_in_progress` は下書き作成後に rollout が伸びた可能性があるため安全側でスキップ、`previous_draft_unverifiable` は hash 確認情報不足、`promote_failed` はその他の昇格失敗である。`Stop` は turn scope のためセッション終了 hook として使わない。
+9. TODO を更新しないセッション、クラッシュ、hook 失敗、または Codex の `session_id` が取れない場合は、自動 fallback を追加せず、終了済みの対象 rollout を指定して `tools/session-record-backfill.py --session <jsonl> --source codex` を明示実行する。
+10. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。Codex で hook が発火しない場合は、まず GUI 設定または `/hooks` で対象 hook が信頼済みか確認する。
 
 ## 11. 操縦 LLM 別の既定 variant
 
diff --git a/templates/hooks/codex-hooks.json.template b/templates/hooks/codex-hooks.json.template
index c0fa1c47..b3bae984 100644
--- a/templates/hooks/codex-hooks.json.template
+++ b/templates/hooks/codex-hooks.json.template
@@ -1,6 +1,18 @@
 {
-  "_comment": "対象アプリの .codex/hooks.json の雛形。pre-bash-precheck は Claude/Codex 共通、session-record-capture-current-on-todo は Codex 専用。",
+  "_comment": "対象アプリの .codex/hooks.json の雛形。pre-bash-precheck は Claude/Codex 共通、session-record-capture-current-on-todo と session-record-promote-previous-draft は Codex 専用。",
   "hooks": {
+    "SessionStart": [
+      {
+        "matcher": "startup|resume",
+        "hooks": [
+          {
+            "type": "command",
+            "command": "bash '.codex/hooks/session-record-promote-previous-draft.sh'",
+            "timeout": 60
+          }
+        ]
+      }
+    ],
     "PostToolUse": [
       {
         "hooks": [
diff --git a/tests/hooks/test_codex_hook_repository.py b/tests/hooks/test_codex_hook_repository.py
index 72eb0780..b1fb425e 100644
--- a/tests/hooks/test_codex_hook_repository.py
+++ b/tests/hooks/test_codex_hook_repository.py
@@ -13,6 +13,7 @@ CODEX_HOOK_FILES = [
   ".codex/hooks/README.md",
   ".codex/hooks/pre-bash-precheck.sh",
   ".codex/hooks/session-record-capture-current-on-todo.sh",
+  ".codex/hooks/session-record-promote-previous-draft.sh",
 ]
 
 
@@ -67,16 +68,26 @@ class CodexHookRepositoryTests(unittest.TestCase):
       "Codex PostToolUse で TODO 更新後の現セッション取り込み hook を登録する必要がある",
     )
 
-  def test_codex_session_start_capture_hook_is_not_registered(self):
+  def test_codex_session_start_promote_previous_draft_hook_is_registered(self):
     hooks_config = json.loads((REPO_ROOT / ".codex/hooks.json").read_text())
     commands = [
       hook["command"]
       for group in hooks_config["hooks"].get("SessionStart", [])
       for hook in group.get("hooks", [])
     ]
-    self.assertFalse(
-      any(".codex/hooks/session-record-capture-current-on-todo.sh" in c for c in commands),
-      "Codex の現セッション取り込み hook は SessionStart へ登録しない",
+    self.assertTrue(
+      any(".codex/hooks/session-record-promote-previous-draft.sh" in c for c in commands),
+      "Codex SessionStart で前セッション下書きの正式昇格 hook を登録する必要がある",
+    )
+    matchers = [
+      group.get("matcher", "")
+      for group in hooks_config["hooks"].get("SessionStart", [])
+      for hook in group.get("hooks", [])
+      if ".codex/hooks/session-record-promote-previous-draft.sh" in hook.get("command", "")
+    ]
+    self.assertTrue(
+      any("startup" in matcher and "resume" in matcher for matcher in matchers),
+      "SessionStart hook は startup/resume の開始契機で前セッション昇格を試みる必要がある",
     )
 
   def test_codex_user_prompt_capture_fallback_hook_is_not_registered(self):
```

## new file: `.codex/hooks/session-record-promote-previous-draft.sh`

```text
#!/bin/bash
# SessionStart フック：新しい Codex セッション開始時に、現セッション以外で
# 最新の runtime 下書きを正式 2 層記録へ昇格する。
#
# 設計：
#   - SessionStart 以外では何もしない
#   - current session_id と同じ下書きは昇格しない
#   - 最新の別 session_id の下書き 1 件だけを対象にする
#   - 昇格できない場合も常に exit 0（セッション開始を妨げない）

set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT=$(cat)

HOOK_EVENT_NAME=$(printf '%s' "$INPUT" | jq -r '.hook_event_name // empty')
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')
LOG_PATH="${RC_SESSION_PROMOTE_HOOK_LOG:-$REPO_ROOT/.reviewcompass/runtime/session-record-promote-previous-draft.jsonl}"
DRAFT_DIR="${RC_SESSION_DRAFT_DIR:-$REPO_ROOT/.reviewcompass/runtime/session-record-drafts}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$REPO_ROOT/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$REPO_ROOT/docs/sessions}"
CODEX_ROOT="${CODEX_SESSIONS_ROOT:-$HOME/.codex/sessions}"
REVIEWCOMPASS_PYTHON="${REVIEWCOMPASS_PYTHON:-python3}"

log_event() {
  EVENT="$1"
  TARGET_SESSION_ID="${2:-}"
  TARGET_DRAFT="${3:-}"
  mkdir -p "$(dirname "$LOG_PATH")" 2>/dev/null || true
  EVENT="$EVENT" \
  HOOK_EVENT_NAME="$HOOK_EVENT_NAME" \
  SESSION_ID="$SESSION_ID" \
  CWD="$CWD" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  TARGET_DRAFT="$TARGET_DRAFT" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY' >>"$LOG_PATH" 2>/dev/null || true
import json
import os
from datetime import datetime, timezone

row = {
  "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
  "hook": "codex_session_record_promote_previous_draft",
  "hook_event_name": os.environ.get("HOOK_EVENT_NAME", ""),
  "event": os.environ.get("EVENT", ""),
  "session_id": os.environ.get("SESSION_ID", ""),
  "cwd": os.environ.get("CWD", ""),
}
target_session_id = os.environ.get("TARGET_SESSION_ID", "")
target_draft = os.environ.get("TARGET_DRAFT", "")
if target_session_id:
  row["target_session_id"] = target_session_id
if target_draft:
  row["target_draft"] = target_draft
print(json.dumps(row, ensure_ascii=False, sort_keys=True))
PY
}

[ "$HOOK_EVENT_NAME" != "SessionStart" ] && { log_event "ignored_event"; exit 0; }
[ -z "$SESSION_ID" ] && { log_event "no_current_session_id"; exit 0; }
[ -z "$CWD" ] && { log_event "no_cwd"; exit 0; }
[ ! -d "$DRAFT_DIR" ] && { log_event "no_draft_dir"; exit 0; }

TARGET_INFO=$(
  DRAFT_DIR="$DRAFT_DIR" SESSION_ID="$SESSION_ID" "$REVIEWCOMPASS_PYTHON" - <<'PY'
import json
import os
from pathlib import Path

draft_dir = Path(os.environ["DRAFT_DIR"])
current_id = os.environ["SESSION_ID"]

best = None
for path in draft_dir.glob("codex-*.md"):
  session_id = path.name.removeprefix("codex-").removesuffix(".md")
  if not session_id or session_id == current_id:
    continue
  try:
    mtime = path.stat().st_mtime
  except OSError:
    continue
  if best is None or mtime > best[0]:
    best = (mtime, session_id, path)

if best is not None:
  print(json.dumps({"session_id": best[1], "draft": str(best[2])}, ensure_ascii=False))
PY
)

[ -z "$TARGET_INFO" ] && { log_event "no_previous_draft"; exit 0; }
TARGET_SESSION_ID=$(printf '%s' "$TARGET_INFO" | jq -r '.session_id // empty')
TARGET_DRAFT=$(printf '%s' "$TARGET_INFO" | jq -r '.draft // empty')
[ -z "$TARGET_SESSION_ID" ] && { log_event "no_previous_draft"; exit 0; }

log_event "selected" "$TARGET_SESSION_ID" "$TARGET_DRAFT"

HASH_INFO=$(
  TARGET_DRAFT="$TARGET_DRAFT" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  CODEX_ROOT="$CODEX_ROOT" \
  CWD="$CWD" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY'
import hashlib
import json
import os
from pathlib import Path

draft = Path(os.environ["TARGET_DRAFT"])
target_session_id = os.environ["TARGET_SESSION_ID"]
root = Path(os.environ["CODEX_ROOT"])
repo = os.environ["CWD"].rstrip("/")


def read_draft_sha(path):
  try:
    text = path.read_text(encoding="utf-8", errors="replace")
  except OSError:
    return ""
  if not text.startswith("---\n"):
    return ""
  end = text.find("\n---\n", 4)
  block = text[4:end] if end != -1 else text[4:]
  for line in block.splitlines():
    if line.startswith("source_sha256:"):
      return line.split(":", 1)[1].strip().strip("'\"")
  return ""


def read_meta(path):
  try:
    with path.open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 5:
          break
        line = line.strip()
        if not line:
          continue
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
          payload = obj.get("payload") or {}
          return payload if isinstance(payload, dict) else {}
  except (OSError, json.JSONDecodeError):
    return {}
  return {}


def find_rollout():
  best = None
  for path in root.rglob("rollout-*.jsonl"):
    meta = read_meta(path)
    if meta.get("id") != target_session_id:
      continue
    cwd = str(meta.get("cwd") or "").rstrip("/")
    if cwd != repo and not cwd.startswith(repo + "/"):
      continue
    try:
      mtime = path.stat().st_mtime
    except OSError:
      continue
    if best is None or mtime > best[0]:
      best = (mtime, path)
  return best[1] if best else None


expected = read_draft_sha(draft)
rollout = find_rollout()
if not expected:
  print(json.dumps({"status": "unverifiable", "reason": "missing_draft_source_sha256"}))
elif rollout is None:
  print(json.dumps({"status": "unverifiable", "reason": "missing_rollout"}))
else:
  actual = hashlib.sha256(rollout.read_bytes()).hexdigest()
  if actual == expected:
    print(json.dumps({"status": "match", "rollout": str(rollout)}))
  else:
    print(json.dumps({"status": "mismatch", "rollout": str(rollout)}))
PY
)

HASH_STATUS=$(printf '%s' "$HASH_INFO" | jq -r '.status // empty')
if [ "$HASH_STATUS" = "mismatch" ]; then
  log_event "previous_draft_in_progress" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi
if [ "$HASH_STATUS" != "match" ]; then
  log_event "previous_draft_unverifiable" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi

cd "$REPO_ROOT" || exit 0
if "$REVIEWCOMPASS_PYTHON" tools/session-record-promote-draft.py \
  --session-id "$TARGET_SESSION_ID" \
  --source codex \
  --current-session-id "$SESSION_ID" \
  --codex-root "$CODEX_ROOT" \
  --repo-path "$CWD" \
  --draft-dir "$DRAFT_DIR" \
  --evidence-dir "$EVIDENCE_DIR" \
  --docs-dir "$DOCS_DIR" >/dev/null 2>&1; then
  log_event "promoted" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
else
  log_event "promote_failed" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
fi

exit 0
```

## new file: `templates/hooks/session-record-promote-previous-draft.sh.template`

```text
#!/bin/bash
# Target app template: promote the latest previous Codex draft on SessionStart.

set -u

INPUT=$(cat)

HOOK_EVENT_NAME=$(printf '%s' "$INPUT" | jq -r '.hook_event_name // empty')
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')

REVIEWCOMPASS_PYTHON="{{REVIEWCOMPASS_PYTHON}}"
REVIEWCOMPASS_DIR="{{REVIEWCOMPASS_DIR}}"
LOG_PATH="${RC_SESSION_PROMOTE_HOOK_LOG:-$CWD/.reviewcompass/runtime/session-record-promote-previous-draft.jsonl}"
DRAFT_DIR="${RC_SESSION_DRAFT_DIR:-$CWD/.reviewcompass/runtime/session-record-drafts}"
EVIDENCE_DIR="${RC_SESSION_EVIDENCE_DIR:-$CWD/.reviewcompass/evidence/sessions}"
DOCS_DIR="${RC_SESSION_DOCS_DIR:-$CWD/docs/sessions}"
CODEX_ROOT="${CODEX_SESSIONS_ROOT:-$HOME/.codex/sessions}"

log_event() {
  EVENT="$1"
  TARGET_SESSION_ID="${2:-}"
  TARGET_DRAFT="${3:-}"
  mkdir -p "$(dirname "$LOG_PATH")" 2>/dev/null || true
  EVENT="$EVENT" \
  HOOK_EVENT_NAME="$HOOK_EVENT_NAME" \
  SESSION_ID="$SESSION_ID" \
  CWD="$CWD" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  TARGET_DRAFT="$TARGET_DRAFT" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY' >>"$LOG_PATH" 2>/dev/null || true
import json
import os
from datetime import datetime, timezone

row = {
  "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
  "hook": "codex_session_record_promote_previous_draft",
  "hook_event_name": os.environ.get("HOOK_EVENT_NAME", ""),
  "event": os.environ.get("EVENT", ""),
  "session_id": os.environ.get("SESSION_ID", ""),
  "cwd": os.environ.get("CWD", ""),
}
target_session_id = os.environ.get("TARGET_SESSION_ID", "")
target_draft = os.environ.get("TARGET_DRAFT", "")
if target_session_id:
  row["target_session_id"] = target_session_id
if target_draft:
  row["target_draft"] = target_draft
print(json.dumps(row, ensure_ascii=False, sort_keys=True))
PY
}

[ "$HOOK_EVENT_NAME" != "SessionStart" ] && { log_event "ignored_event"; exit 0; }
[ -z "$SESSION_ID" ] && { log_event "no_current_session_id"; exit 0; }
[ -z "$CWD" ] && { log_event "no_cwd"; exit 0; }
[ ! -d "$DRAFT_DIR" ] && { log_event "no_draft_dir"; exit 0; }
[ ! -f "$REVIEWCOMPASS_DIR/tools/session-record-promote-draft.py" ] && { log_event "no_promote_tool"; exit 0; }

TARGET_INFO=$(
  DRAFT_DIR="$DRAFT_DIR" SESSION_ID="$SESSION_ID" "$REVIEWCOMPASS_PYTHON" - <<'PY'
import json
import os
from pathlib import Path

draft_dir = Path(os.environ["DRAFT_DIR"])
current_id = os.environ["SESSION_ID"]

best = None
for path in draft_dir.glob("codex-*.md"):
  session_id = path.name.removeprefix("codex-").removesuffix(".md")
  if not session_id or session_id == current_id:
    continue
  try:
    mtime = path.stat().st_mtime
  except OSError:
    continue
  if best is None or mtime > best[0]:
    best = (mtime, session_id, path)

if best is not None:
  print(json.dumps({"session_id": best[1], "draft": str(best[2])}, ensure_ascii=False))
PY
)

[ -z "$TARGET_INFO" ] && { log_event "no_previous_draft"; exit 0; }
TARGET_SESSION_ID=$(printf '%s' "$TARGET_INFO" | jq -r '.session_id // empty')
TARGET_DRAFT=$(printf '%s' "$TARGET_INFO" | jq -r '.draft // empty')
[ -z "$TARGET_SESSION_ID" ] && { log_event "no_previous_draft"; exit 0; }

log_event "selected" "$TARGET_SESSION_ID" "$TARGET_DRAFT"

HASH_INFO=$(
  TARGET_DRAFT="$TARGET_DRAFT" \
  TARGET_SESSION_ID="$TARGET_SESSION_ID" \
  CODEX_ROOT="$CODEX_ROOT" \
  CWD="$CWD" \
  "$REVIEWCOMPASS_PYTHON" - <<'PY'
import hashlib
import json
import os
from pathlib import Path

draft = Path(os.environ["TARGET_DRAFT"])
target_session_id = os.environ["TARGET_SESSION_ID"]
root = Path(os.environ["CODEX_ROOT"])
repo = os.environ["CWD"].rstrip("/")


def read_draft_sha(path):
  try:
    text = path.read_text(encoding="utf-8", errors="replace")
  except OSError:
    return ""
  if not text.startswith("---\n"):
    return ""
  end = text.find("\n---\n", 4)
  block = text[4:end] if end != -1 else text[4:]
  for line in block.splitlines():
    if line.startswith("source_sha256:"):
      return line.split(":", 1)[1].strip().strip("'\"")
  return ""


def read_meta(path):
  try:
    with path.open(encoding="utf-8", errors="replace") as f:
      for index, line in enumerate(f):
        if index >= 5:
          break
        line = line.strip()
        if not line:
          continue
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
          payload = obj.get("payload") or {}
          return payload if isinstance(payload, dict) else {}
  except (OSError, json.JSONDecodeError):
    return {}
  return {}


def find_rollout():
  best = None
  for path in root.rglob("rollout-*.jsonl"):
    meta = read_meta(path)
    if meta.get("id") != target_session_id:
      continue
    cwd = str(meta.get("cwd") or "").rstrip("/")
    if cwd != repo and not cwd.startswith(repo + "/"):
      continue
    try:
      mtime = path.stat().st_mtime
    except OSError:
      continue
    if best is None or mtime > best[0]:
      best = (mtime, path)
  return best[1] if best else None


expected = read_draft_sha(draft)
rollout = find_rollout()
if not expected:
  print(json.dumps({"status": "unverifiable", "reason": "missing_draft_source_sha256"}))
elif rollout is None:
  print(json.dumps({"status": "unverifiable", "reason": "missing_rollout"}))
else:
  actual = hashlib.sha256(rollout.read_bytes()).hexdigest()
  if actual == expected:
    print(json.dumps({"status": "match", "rollout": str(rollout)}))
  else:
    print(json.dumps({"status": "mismatch", "rollout": str(rollout)}))
PY
)

HASH_STATUS=$(printf '%s' "$HASH_INFO" | jq -r '.status // empty')
if [ "$HASH_STATUS" = "mismatch" ]; then
  log_event "previous_draft_in_progress" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi
if [ "$HASH_STATUS" != "match" ]; then
  log_event "previous_draft_unverifiable" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
  exit 0
fi

if cd "$REVIEWCOMPASS_DIR" && "$REVIEWCOMPASS_PYTHON" tools/session-record-promote-draft.py \
  --session-id "$TARGET_SESSION_ID" \
  --source codex \
  --current-session-id "$SESSION_ID" \
  --codex-root "$CODEX_ROOT" \
  --repo-path "$CWD" \
  --draft-dir "$DRAFT_DIR" \
  --evidence-dir "$EVIDENCE_DIR" \
  --docs-dir "$DOCS_DIR" >/dev/null 2>&1; then
  log_event "promoted" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
else
  log_event "promote_failed" "$TARGET_SESSION_ID" "$TARGET_DRAFT"
fi

exit 0
```

## new file: `tests/hooks/test_codex_session_record_promote_previous.py`

```text
"""Codex SessionStart hook の前セッション正式昇格テスト。

Codex の TODO hook は現セッションを runtime 下書きへ保存する。
新しい Codex セッション開始時には、現 session_id と異なる最新下書きを
正式 2 層記録へ昇格する。
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "session-record-promote-previous-draft.sh"


def _codex_fixture(path, session_id, cwd, text, mtime):
  path.parent.mkdir(parents=True, exist_ok=True)
  rows = [
    {
      "timestamp": "2026-06-15T10:00:00.000Z",
      "type": "session_meta",
      "payload": {
        "id": session_id,
        "timestamp": "2026-06-15T10:00:00.000Z",
        "cwd": cwd,
      },
    },
    {
      "timestamp": "2026-06-15T10:00:01.000Z",
      "type": "response_item",
      "payload": {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
      },
    },
  ]
  path.write_text(
    "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
    encoding="utf-8",
  )
  os.utime(path, (mtime, mtime))


def _sha256(path):
  import hashlib

  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _draft_fixture(path, session_id, mtime, source_sha256="draft-sha"):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    "---\n"
    "source: codex\n"
    f"session_id: {session_id}\n"
    "layer: draft\n"
    f"source_sha256: {source_sha256}\n"
    "---\n"
    "\n"
    "draft\n",
    encoding="utf-8",
  )
  os.utime(path, (mtime, mtime))


def _run_hook(payload, evidence_dir, docs_dir, draft_dir, codex_root, log_path):
  env = dict(os.environ)
  env["RC_SESSION_EVIDENCE_DIR"] = str(evidence_dir)
  env["RC_SESSION_DOCS_DIR"] = str(docs_dir)
  env["RC_SESSION_DRAFT_DIR"] = str(draft_dir)
  env["CODEX_SESSIONS_ROOT"] = str(codex_root)
  env["RC_SESSION_PROMOTE_HOOK_LOG"] = str(log_path)
  return subprocess.run(
    ["bash", str(HOOK)],
    input=json.dumps(payload),
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
    env=env,
  )


def _events(path):
  if not path.exists():
    return []
  return [
    json.loads(line)["event"]
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
  ]


class CodexPromotePreviousDraftHookTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"
    self.drafts = self.tmp / "drafts"
    self.codex_root = self.tmp / "codex"
    self.log_path = self.tmp / "promote.jsonl"
    self.cwd = "/Users/Daily/Development/ReviewCompass"
    self.prev_id = "aaaaaaaa-1111-2222-3333-444444444444"
    self.current_id = "bbbbbbbb-1111-2222-3333-444444444444"
    self.old_id = "cccccccc-1111-2222-3333-444444444444"

  def _rollout(self, session_id):
    return (
      self.codex_root
      / "2026"
      / "06"
      / "15"
      / f"rollout-2026-06-15T10-00-00-{session_id}.jsonl"
    )

  def _payload(self, session_id=None):
    return {
      "hook_event_name": "SessionStart",
      "session_id": session_id or self.current_id,
      "cwd": self.cwd,
      "source": "startup",
    }

  def test_promotes_latest_non_current_draft_on_session_start(self):
    """SessionStart で現セッション以外の最新下書きだけを正式化する。"""
    _codex_fixture(self._rollout(self.old_id), self.old_id, self.cwd, "古い下書き", 1000)
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _codex_fixture(self._rollout(self.current_id), self.current_id, self.cwd, "現セッション", 3000)
    _draft_fixture(
      self.drafts / f"codex-{self.old_id}.md",
      self.old_id,
      1000,
      _sha256(self._rollout(self.old_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.current_id}.md",
      self.current_id,
      3000,
      _sha256(self._rollout(self.current_id)),
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "前セッション下書きを正式層1へ昇格する必要がある",
    )
    self.assertTrue(
      (self.docs / f"auto-2026-06-15-codex-{self.prev_id}.md").exists(),
      "前セッション下書きを正式層2へ昇格する必要がある",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.current_id}.md").exists(),
      "現セッションは正式化してはいけない",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.old_id}.md").exists(),
      "最新より古い下書きはこの hook では正式化しない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_only_current_draft_is_noop(self):
    """現セッション下書きしか無い場合は何もせず exit 0。"""
    _codex_fixture(self._rollout(self.current_id), self.current_id, self.cwd, "現セッション", 3000)
    _draft_fixture(
      self.drafts / f"codex-{self.current_id}.md",
      self.current_id,
      3000,
      _sha256(self._rollout(self.current_id)),
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["no_previous_draft"])

  def test_non_session_start_is_ignored(self):
    """SessionStart 以外に誤登録されても正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    payload = self._payload()
    payload["hook_event_name"] = "PostToolUse"

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(self.evidence.exists() and any(self.evidence.iterdir()))
    self.assertEqual(_events(self.log_path), ["ignored_event"])

  def test_skips_latest_previous_draft_when_rollout_hash_changed(self):
    """最新候補の rollout が下書き作成後に伸びた場合は正式化しない。"""
    _codex_fixture(self._rollout(self.old_id), self.old_id, self.cwd, "古い終了済み", 1000)
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション v1", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.old_id}.md",
      self.old_id,
      1000,
      _sha256(self._rollout(self.old_id)),
    )
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション v2", 3000)

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "hash 不一致の最新候補は正式化してはいけない",
    )
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.old_id}.md").exists(),
      "最新候補が進行中なら古い候補へフォールバックしない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_in_progress"])

  def test_resume_session_start_uses_same_safety_checks(self):
    """resume 起動でも startup と同じ安全確認で前セッションを昇格する。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      _sha256(self._rollout(self.prev_id)),
    )
    payload = self._payload()
    payload["source"] = "resume"

    result = _run_hook(payload, self.evidence, self.docs, self.drafts, self.codex_root, self.log_path)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "resume でも hash 一致した前セッション下書きは正式化する",
    )
    self.assertEqual(_events(self.log_path), ["selected", "promoted"])

  def test_missing_draft_hash_is_unverifiable_and_not_promoted(self):
    """source_sha256 の無い下書きは検証不能として正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    _draft_fixture(
      self.drafts / f"codex-{self.prev_id}.md",
      self.prev_id,
      2000,
      "",
    )

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "hash 検証不能な下書きは正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])

  def test_missing_draft_hash_line_is_unverifiable_and_not_promoted(self):
    """source_sha256 行そのものが無い下書きも検証不能として正式化しない。"""
    _codex_fixture(self._rollout(self.prev_id), self.prev_id, self.cwd, "前セッション", 2000)
    draft = self.drafts / f"codex-{self.prev_id}.md"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(
      "---\n"
      "source: codex\n"
      f"session_id: {self.prev_id}\n"
      "layer: draft\n"
      "---\n"
      "\n"
      "draft\n",
      encoding="utf-8",
    )
    os.utime(draft, (2000, 2000))

    result = _run_hook(
      self._payload(),
      self.evidence,
      self.docs,
      self.drafts,
      self.codex_root,
      self.log_path,
    )

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertFalse(
      (self.evidence / f"2026-06-15-codex-{self.prev_id}.md").exists(),
      "source_sha256 行の無い下書きは正式化してはいけない",
    )
    self.assertEqual(_events(self.log_path), ["selected", "previous_draft_unverifiable"])


if __name__ == "__main__":
  unittest.main()
```
