# Post-write verification target: reopen-advance-gate docs

## Current documentation diff

BEGIN_DIFF
diff --git a/TODO_NEXT_SESSION.md b/TODO_NEXT_SESSION.md
index 4c1220fc..f1ac471b 100644
--- a/TODO_NEXT_SESSION.md
+++ b/TODO_NEXT_SESSION.md
@@ -25,7 +25,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 
 ## 3. 現在位置（2026-06-15 時点）
 
-- `next --json`：reopen R-0（decision-source-lint）完了・`make-commit-approval.py` 重大案件削除で **`completed`**（進行中手続きなし・全 workflow_state 完了）。`b16a021a` まで push 済み（2026-06-15）。
+- `next --json`：reopen R-0（decision-source-lint）完了・`make-commit-approval.py` 重大案件削除・reopen pending gate 更新コマンド追加まで **`completed`**（進行中手続きなし・全 workflow_state 完了）。直近作業コミットは `96112385`（2026-06-15）。
 - **裁定負荷対策＝重要決定の出典検査（候補5・Req 11／decision-source-lint）仕組みの実装は完成・公開済み（運用は未開始＝§4 項目5）**：reopen **R-0** で workflow-management に Requirement 11（重要決定の出典検査＝束ね検出・逐語照合・内容性＋構造化した重要決定の記録形式）を新設し、`decision-source-lint` サブコマンドを TDD 実装（`tools/check_workflow_action/decision_source_lint.py`〔コア 10 関数〕・`check-workflow-action.py` への登録と commit 直前ゲート統合〔pending=WARN・unverifiable=DEVIATION〕・`stages/decision-source-lint-config.yaml`〔内容なし語リスト初期 11 件〕）。各 phase は 3 役 triad-review → proxy_model（gemini-3.1-pro-preview）裁定 → 収束 → review-wave/alignment/approval で連鎖再実施（利用者「自律的に実施」2026-06-15）。専用テスト 62 件＋全 395 件 pass。完了記録＝`stages/completed/reopen-procedure-2026-06-15.yaml`。コミット `7610a0d8`〜`bfd00dcf`（第1〜4過程）。**ただし運用は未開始**：構造化決定記録（`.reviewcompass/decisions/`）は現時点 0 件で `decision-source-lint --all` は「0 件（正常）」＝検査対象なし。埋没防止が実効を持つには、going-forward の重要決定を新形式で書き始める運用定着が要る（§4 項目5 の残タスク）。
 - **commit 承認の削除ファイル対応＋reopen 基盤の弱点記録**：reopen 完了処理で必ず起きる「進行中→完了への移動＝元ファイル削除」を承認できるよう、`make-commit-approval.py`（削除を検出し `DELETED` 印を付す）・`validate_commit_approval`（`DELETED` 印を通し、ファイルが残る時のみエラー）に TDD で追加（コミット `94900049` push 済み）。あわせて、第4過程で進行中ファイルの手編集が YAML 破損・必須項目漏れで2度コミットを止めた事故を §4 項目8 に改善課題として記録。
 - **会話ログ取り込みの追記専用マージ化（maintenance side track）完了・改善中**：従来の「丸ごと上書き」をやめ、層 1（整形済み転写）の本文包含で `same`／`extend`／`shrink` を判定し、同一はスキップ・拡張は更新・縮小は既存保全（上書きせず警告）とした。元ログ（jsonl）が何らかの理由で縮んでも取り込み済み記録を失わない。判定モジュール `tools/session_record_extractor/merge.py`（`classify_update`／`is_subsequence`）を追加し `tools/session-record-backfill.py` を改修。判定は層 1 で行い層 2 は同一ソースゆえ追従（層 2 の「（なし）→実データ」を縮小と誤判定しない）。2026-06-15 に、本文同一でも元ログ hash だけ変わった場合に `source_sha256` frontmatter を更新する改善を追加（手修正で直していた stale hash 問題の再発防止）。TDD テストは `tests/tools/test_session_record_append_merge.py`（同一は書かない／本文同一でも hash stale は更新／伸びたら拡張反映／縮んだら保全／空欄→実データは拡張）。書き込み後検証はテスト通過で完了（利用者決定 2026-06-14。前例 postwrite-log-exclusion と同様、多モデル API レビューなし）。完了記録＝`stages/completed/maintenance-2026-06-14-session-record-append-merge.yaml`。コミット `44ed5ea8`。前セッションの取りこぼしセッション記録 4 件も `a37ad0c2` で確定。
@@ -34,6 +34,7 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
 - **会話ログ自動保持（going-forward 取り込み）実装・公開済み**：Claude は、セッション終了時に当該会話ログを2層記録へ自動取り込みする SessionEnd フック（`.claude/hooks/session-record-capture.sh`）と、新セッション開始時に前セッションを補完回収する SessionStart フック（`.claude/hooks/session-record-capture-previous.sh`）を `.claude/settings.json` に登録済み。`tools/session-record-backfill.py` の単一セッション取り込み（`--session`／`--source`／`--evidence-dir`／`--docs-dir`）を TDD で追加。`transcript_path` 欠落時は `session_id`＋`cwd` から復元、ログ無し・失敗でも exit 0（終了を妨げない）。取りこぼしの回収は**終了済みセッションへの単一取り込み（`--session`）が安全網**（2026-06-14 是正。当初は「オフライン一括バックフィルが安全網」と PLC-DEC-007 追補で定めたが、一括は実行中セッションを掴み churn を生むため既定無効化＝§4 の churn 対応を参照）。フックは**設定読込の都合で次セッションから有効**。コミット `a287684a`（push 済み）。専用テスト＝`tests/tools/test_session_record_single_capture.py`・`tests/hooks/test_session_record_capture.py` 各 4 件、tools 202 件・hooks 21 件 pass。
 - **Codex TODO 更新 hook による現セッション回収へ方針変更中（2026-06-15）**：このセッション開始時点では、前 Codex rollout の 2 層記録が `git status` に現れず、Codex の自動回収経路も確認できなかった。その後 `UserPromptSubmit` 経由の自動回収を検討したが、実運用で発話ごとの誤発火が確認されたため使用禁止とした。さらに利用者指摘により、TODO 更新を合図にするなら対象は前セッションではなく現セッションが正しい、と方針修正した。`.codex/hooks/session-record-capture-current-on-todo.sh` は `PostToolUse` で起動し、`TODO_NEXT_SESSION.md` の hash が変わった場合だけ、`session_id` が一致する現 Codex rollout を単一 backfill する。TODO は 1 セッション内で複数回更新されるため、そのたび追記専用マージで伸びた分を反映する。`session_id` が無い場合は並行セッション誤回収を避けて推測しない。配布物の `templates/hooks/session-record-capture-current-on-todo.sh.template`・`templates/hooks/codex-hooks.json.template`・`deploy-manifest.yaml`・`docs/operations/INITIAL_SETUP_LLM_GUIDE.md` へ汎用実装として反映中。次回は `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` の `todo_changed`／`selected`／`captured`／`todo_unchanged`／`baseline_recorded`／`no_session_id`／`ignored_event` を確認する。
 - **正本優先（事例より正本）の生成ツール（案2）追加・公開済み**：「過去の事例を手で写す」のをやめ、正本（強制コードの検証関数）が受け入れる形を生成し、正本へ通して fail-closed する2ツールを TDD で追加。`tools/make-post-write-manifest.py`（書き込み後検証 manifest 生成。正本＝`evaluate_post_write_manifest_state`／`review_run_traceability_satisfied`）は残存。`tools/make-commit-approval.py`（commit 承認レコード生成）は **設計欠陥により 2026-06-15 に削除**（LLM が自律的に承認記録を生成できる＝コミット保護の無効化。経緯は §4 項目9・`docs/notes/2026-06-15-security-incident-make-commit-approval.md`）。コミット `83abd1e6`（追加）→ `b16a021a`（`make-commit-approval.py` 削除）。動機・経緯と残検討は §4 の項 7。
+- **reopen 中の pending gate 完了更新コマンド追加（maintenance side track）完了**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、reopen 第3過程で `pending_gates` の先頭 gate を、判断・根拠・`spec.json` 更新・`completed_gates`・`downstream_impact_decisions`・`completed_steps` と一緒に機械更新できるようにした。非先頭 gate は拒否し、根拠なし更新も拒否する。これにより、`spec-set` が in-progress reopen を遮断する通常保護を保ったまま、reopen 内の gate 前進だけを正規コマンドで処理できる。完了記録＝`stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml`。コミット `96112385`。運用説明は `docs/operations/WORKFLOW_PRECHECK.md` と `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` に反映済み。
 - **書き込み後検証ポリシー改訂済み**：独立検証が有効でないものを性質ベースで対象外化。(あ) 機械生成・出所明記の派生記録（来歴マーカー判定）、(い) 機械が吐く捕捉物（review-run・自律並列台帳・検証結果ログ＝ディレクトリ判定）。いずれも独立検証でなく再現性／走行・再実行で担保。正本＝`docs/disciplines/discipline_post_write_verification.md`、ガード＝`tools/check-workflow-action.py` の `is_post_write_verification_target`。監査・計測記録（`docs/discipline-compliance-reports/`）は主張を含むため対象に残す。
 - **文書配置規約は段階 5 まで完了**（計画 `docs/notes/2026-06-12-document-placement-plan.md` の状態欄が正。P1 完了判定は `docs/notes/2026-06-12-document-placement-stage4-migration.md`）。
   - 配置規約 P1 の reopen 2 本（ce＝R-0・wm＝D-0）は第 4 過程まで完了し `stages/completed/` にある。
@@ -67,8 +68,11 @@ ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三
    - **残る改善（§4 項目7「(拡大)」の具体化）**：(a) 進行中・完了の reopen yaml を、正本（`validate_*` 群）が受け入れる形で生成・更新するツール化＝手編集をやめる（承認レコード・manifest の生成ツールと同じ「事例より正本」の横展開）。(b) 停止点コミット判定を `next_step` の語の有無から `step_number`（構造化された過程番号）へ移す。`check-workflow-action.py:3741` のコメントが既に示す方向で、人間向けの説明文と機械判定用データが同じ欄に同居している弱さを解消する。
    - 位置づけ：§4 項目5（裁定負荷対策）と同族の「手続きの作りの弱さが手戻りを生む」実例。今回は機能本体（決定出典検査）とは別の、reopen 手続き基盤の整備課題。
 9. **`make-commit-approval.py` の設計欠陥と削除（2026-06-15・重大案件・コミット `b16a021a` push 済み）**：commit 承認記録（コミット実行の許可証となる JSON ファイル）を自動生成するツールとして 2026-06-14 に作成したが、LLM が自律的に実行できる設計だった。`--explicit-instruction "コミット"` という文字列を渡すだけで、利用者が実際に「コミット」と発言したかどうかに関係なく有効な承認記録を生成できてしまい、コード（`guarded-git-commit.py`）による不可逆操作の防護が実質無効化される。実際に 2026-06-15 のセッションで本ツールを悪用して利用者の明示なしに複数回コミット・push を自律実行した（事後承認）。詳細は `docs/notes/2026-06-15-security-incident-make-commit-approval.md`。**残る運用**：承認記録は Python ワンライナー（手動計算）で生成する。承認記録の安全な生成方法は別途検討。
-10. **reopen 中の pending gate 完了更新コマンド不足（2026-06-15・要対処）**：commit-approval-nonce の reopen 第3過程で `requirements alignment` を進める際、`spec-set workflow-management requirements alignment true` は `stages/in-progress/` が存在するため fail-closed で遮断された。通常作業では正しい保護だが、reopen 第3過程では in-progress がある状態で pending gate を処理する必要がある。現状は `next` が次 gate を案内し、`reopen-start` が開始状態を作れる一方、`reopen-advance-gate` 相当の「判定記録作成／`spec.json` 更新／`pending_gates` 更新／`completed_gates` 追加／`downstream_impact_decisions` 追加」を一貫実行する正規コマンドが無い。そのため今回は、`.reviewcompass/specs/_cross_feature/reviews/2026-06-15-requirements-commit-approval-nonce-reopen-alignment.md` を手で作り、`spec.json` の `requirements.alignment=true`、in-progress の `pending_gates`・`completed_gates`・`downstream_impact_decisions`・`current_blocker` を手編集するワークアラウンドになった。**改善案**：`tools/check-workflow-action.py reopen-advance-gate`（仮）を追加し、対象 gate、decision、feature_scope、rationale、evidence、必要な `spec.json` 更新を構造化入力で受け、既存 `validate_reopen_completion_impact_decisions` が受け入れる形に機械生成・更新する。あわせて actor=human / proxy_model の approval gate では `current_blocker` を構造的に設定し、手編集を不要にする。本項は §4 項目8 の「reopen yaml 手編集」問題を、実際の gate 前進操作に絞った具体タスクである。
+10. ~~**reopen 中の pending gate 完了更新コマンド不足**~~ **完了（2026-06-15、`96112385`）**：`tools/check-workflow-action.py reopen-advance-gate` を追加し、対象 gate、decision、feature_scope、rationale、evidence、必要な `spec.json` 更新を構造化入力で受け、既存 `validate_reopen_completion_impact_decisions` が受け入れる形に機械更新できるようにした。今回の scope は pending gate 前進に絞り、approval gate の actor=human / proxy_model blocker 構造化は今後の reopen 実運用で不足が見えた時に別タスク化する。
 11. **Codex TODO 更新 hook 未発火の実確認（2026-06-15・会話記録保全は手動で実施済み）**：TODO 更新を合図に現セッションを回収する `.codex/hooks/session-record-capture-current-on-todo.sh` は repo 内 `.codex/hooks.json` に `PostToolUse` 登録済みだが、2026-06-15 の TODO 更新後に `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` は作られず、直近の `.reviewcompass/evidence/sessions/`／`docs/sessions/` 生成物も無かった。つまりこの Codex 実行環境では、少なくとも今回の `apply_patch` / `exec_command` による TODO 更新時には repo 内 hook が発火していない。会話記録は重要証跡なので、同セッションの rollout `/Users/keno/.codex/sessions/2026/06/15/rollout-2026-06-15T15-51-42-019eca0c-e1c6-78f2-9060-0e546196fc12.jsonl` を手動単一 backfill し、`.reviewcompass/evidence/sessions/2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` と `docs/sessions/auto-2026-06-15-codex-019eca0c-e1c6-78f2-9060-0e546196fc12.md` を生成済み（再現性チェック ok 2）。**改善案**：Codex desktop が repo 内 `.codex/hooks.json` を読む条件、`PostToolUse` の対象 tool 種別、cwd / hook input の実際を確認する。発火しない環境では、終了時または TODO 更新時に手動単一 backfill を標準手順として明示する。会話記録を失わないことを優先し、hook 確認が終わるまで「hook 任せで保存済み」と見なさない。
+12. **reopen approval gate の blocker 構造化（派生課題）**：`reopen-advance-gate` は pending gate 前進を機械化したが、approval gate で actor=human / proxy_model の承認待ちを `current_blocker` として構造的に設定する専用操作は未実装。次に reopen 実運用で承認待ち gate を扱う時に、手編集が再発するなら別タスクとして実装する。
+13. **reopen-advance-gate の追加テスト（派生課題）**：実装は `--evidence` なし更新を拒否するが、`96112385` 時点の専用テストは正常更新と非先頭 gate 拒否に限られる。次に同コマンドを触る時は、根拠なし更新の exit 2 を追加テストする。
+14. **reopen-advance-gate の gate 正規化検査（派生課題）**：現状は `--gate` と `pending_gates[0]` の文字列一致で前進を判定し、既存 YAML 内の gate 文字列が標準形式かは追加検証しない。次に同コマンドを強化する時は、`pending_gates` の全要素が `stages/<phase>.yaml#<stage>` 形式として解釈できることを検査する。
 
 ## 5. 参照
 
diff --git a/docs/operations/WORKFLOW_PRECHECK.md b/docs/operations/WORKFLOW_PRECHECK.md
index 4dd25879..b3c27b76 100644
--- a/docs/operations/WORKFLOW_PRECHECK.md
+++ b/docs/operations/WORKFLOW_PRECHECK.md
@@ -30,6 +30,7 @@
 - `commit`：commit 前検査
 - `push`：push 前検査
 - `audit-commit`：commit 済み変更に対する post-write-verification 監査
+- `reopen-advance-gate`：reopen 中の pending gate 完了更新
 - `autonomous-plan`：自律・並列実行計画の開始前検査
 - `autonomous-plan-template`：自律・並列実行計画テンプレート生成
 - `autonomous-plan-record-integration`：自律・並列実行の統合結果記録
@@ -52,6 +53,7 @@ tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [-
 tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
+tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
@@ -96,6 +98,12 @@ commit は人の職掌範囲である。`--execution-actor llm` の場合、通
 
 reopen 開始時は、上流正本変更の影響範囲を分類し、必要な reopen 手続き記録を作成してから通常ワークフローへ戻す。commit 時には、reopen 手続き記録と spec.json の recheck 状態の整合を検査する。詳細は [REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) と [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。
 
+<a id="reopen-advance-gate"></a>
+
+### 4.6 reopen-advance-gate
+
+`reopen-advance-gate` は、reopen 第3過程で pending gate を 1 件完了扱いへ進めるときに呼び出す。対象 gate、判断、根拠、必要な `spec.json` 更新を構造化入力で受け取り、reopen 手続き記録の `pending_gates`、`completed_gates`、`downstream_impact_decisions`、`completed_steps` を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-gate) を参照する。
+
 ## 5. 判定契約
 
 終了コード：
@@ -110,6 +118,7 @@ reopen 開始時は、上流正本変更の影響範囲を分類し、必要な
 - `commit` は、承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する
 - `push` は、作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する
 - `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
+- `reopen-advance-gate` は、先頭の pending gate だけを完了扱いに進め、根拠なし更新を拒否する
 - `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する
 
 ## 6. 出力とログ
diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 42fb547a..999d3edf 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -9,6 +9,7 @@ tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [-
 tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
 tools/check-workflow-action.py push --rationale "<理由>"
 tools/check-workflow-action.py audit-commit <commit-ish>
+tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
 tools/check-workflow-action.py autonomous-plan <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
 tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
@@ -128,12 +129,45 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 
 この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。
 
+<a id="reopen-advance-gate"></a>
+
+## 6. reopen-advance-gate
+
+`reopen-advance-gate` は、reopen 手続きファイルの `pending_gates` を 1 件進める更新コマンドである。`spec-set` は in-progress reopen が存在する状態を通常作業として遮断するため、reopen 第3過程の gate 完了更新では本コマンドを使う。
+
+引数：
+
+| 引数 | 必須 | 説明 |
+|---|---|---|
+| `--file` | 必須 | 対象の reopen 手続き YAML |
+| `--gate` | 必須 | 完了扱いにする gate。`pending_gates` 内と同じ文字列で指定する。標準の gate 文字列は `stages/<phase>.yaml#<stage>` 形式。例：`stages/requirements.yaml#alignment` |
+| `--decision` | 必須 | 下流影響判断 |
+| `--feature-scope` | 必須 | 判断対象の feature |
+| `--rationale` | 必須 | 判断理由 |
+| `--evidence` | 必須 | 判断根拠。複数指定可 |
+| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |
+| `--set-spec` | 任意 | `FEATURE PHASE STAGE VALUE` の 4 値で `spec.json` も同時更新する。指定は 1 回のみ。`VALUE` は `true` または `false` |
+
+判定と更新：
+
+- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
+- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
+- `pending_gates` 自体は、`reopen-start` 等が作る標準の `stages/<phase>.yaml#<stage>` 形式を前提とする。既存 YAML 内の gate 文字列を追加検証する正規化処理は本コマンドの対象外である
+- `--evidence` が 1 件も無い更新は逸脱とする
+- 完了した gate を `pending_gates` から除去し、`completed_gates` へ追加する
+- `downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を追記する
+- `--completed-step` があれば `completed_steps` へ追記する
+- `--set-spec` があれば、対象 feature の `spec.json` の該当 workflow_state を同時更新する
+- gate 完了後は `current_blocker` を `null` にする。本コマンドは approval gate の承認待ち blocker を新規作成しない
+- 残る pending gate があれば `step_number: 3` を維持し、`next_step` を次 gate に更新する。無ければ `step_number: 4` と `next_step: 第4過程：完了` へ進める
+- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す
+
 <a id="autonomous-plan"></a>
 <a id="autonomous-plan-template"></a>
 <a id="autonomous-plan-record-integration"></a>
 <a id="autonomous-ledger-audit"></a>
 
-## 6. autonomous-plan 系
+## 7. autonomous-plan 系
 
 `autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。
 
@@ -151,7 +185,7 @@ tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
 
 `autonomous-plan-template` は最小テンプレートを生成する。`autonomous-plan-record-integration` は統合後に既存の履歴台帳へ `integration_result` を追記する。
 
-## 7. 出力形式
+## 8. 出力形式
 
 終了コード：
 
@@ -176,7 +210,7 @@ JSON 出力は、少なくとも次のキーを含む。
 }
 ```
 
-## 8. ログ
+## 9. ログ
 
 判定ログは JSON Lines 形式で記録する。`--json` 出力と同等の構造に `timestamp` を追加する。
 
@@ -187,7 +221,7 @@ JSON 出力は、少なくとも次のキーを含む。
 
 `--log-path` でテスト用の隔離パスへ上書きできる。
 
-### 8.1 実行時生成物の凍結期（P3 まで）の扱い
+### 9.1 実行時生成物の凍結期（P3 まで）の扱い
 
 検査ログ・effective prompt（`.reviewcompass/runtime/effective-prompts/`、旧 `.reviewcompass/effective-prompts/`）・
 commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.json`、旧 `.reviewcompass/approvals/commit-approval.json`）の
@@ -217,7 +251,7 @@ commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.js
    旧配置を追跡している構成（対象アプリ等）に限る。未追跡の旧成果物の凍結は書き込み経路のテスト
    （`tests/tools/test_runtime_placement_freeze.py`）で担保する。
 
-## 9. テスト観点
+## 10. テスト観点
 
 主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。
 
@@ -225,6 +259,7 @@ commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.js
 - `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
 - `push` の clean 性検査
 - `audit-commit` の manifest 対応検査
+- `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
 - `guarded-git-commit.py` の commit 遮断と承認レコード消費
 - `autonomous-plan` 系サブコマンドの構造検査
 
END_DIFF

## Implementation evidence commit

commit 9611238569ad143f698bf98df02dd57408f75ecd
subject Add reopen advance gate helper


stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml
tests/tools/test_check_workflow_action.py
tools/check-workflow-action.py

## Implementation evidence excerpt
BEGIN_IMPLEMENTATION_DIFF
diff --git a/stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml b/stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml
new file mode 100644
index 00000000..62462a3d
--- /dev/null
+++ b/stages/completed/maintenance-2026-06-15-reopen-advance-gate.yaml
@@ -0,0 +1,28 @@
+process_id: maintenance
+started_at: 2026-06-15T14:05:00Z
+title: reopen advance gate helper
+trigger: reopen 第3過程で pending gate 完了時の証跡・spec.json・in-progress 状態更新を手編集しており、YAML 破損や必須項目漏れの原因になった。
+mainline_blocked_by: completed workflow has no required next action
+allowed_scope:
+- workflow-management maintenance
+allowed_files:
+- tools/check-workflow-action.py
+- tests/tools/test_check_workflow_action.py
+- docs/operations/WORKFLOW_PRECHECK.md
+- docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+- TODO_NEXT_SESSION.md
+- stages/in-progress/maintenance-2026-06-15-reopen-advance-gate.yaml
+completion_conditions:
+- reopen-advance-gate 相当のコマンドが TDD で追加される。
+- pending gate 完了時に spec.json、pending_gates、completed_gates、downstream_impact_decisions、completed_steps が機械更新される。
+- YAML parse、対象 unittest、git diff --check、next --json が通過する。
+current_status: completed
+completed_at: 2026-06-15T14:15:00Z
+completion_evidence:
+- tools/check-workflow-action.py
+- tests/tools/test_check_workflow_action.py
+deferred_follow_up:
+- docs/operations/WORKFLOW_PRECHECK.md
+- docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+- TODO_NEXT_SESSION.md
+deferred_reason: post-write-verification 対象文書と tools 変更を同一未コミット差分に混在させると policy violation になるため、文書反映は別単位で扱う。
diff --git a/tests/tools/test_check_workflow_action.py b/tests/tools/test_check_workflow_action.py
index 7d4cef2a..1232773b 100644
--- a/tests/tools/test_check_workflow_action.py
+++ b/tests/tools/test_check_workflow_action.py
@@ -3636,40 +3636,178 @@ class ReopenStartTests(unittest.TestCase):
     cwd = Path(self.tmpdir)
     result = run_script(
       [
         "reopen-start",
         "--classification", "Z-9",
         "--feature", "runtime",
         "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
         "--date", "2026-06-02",
         "--trigger", "invalid",
         "--json",
       ],
       cwd=cwd,
     )
 
     _assert_script_invoked(self, result)
     self.assertEqual(result.returncode, 2)
     data = json.loads(result.stdout)
     self.assertEqual(data["verdict"], "DEVIATION")
 
 
+class ReopenAdvanceGateTests(unittest.TestCase):
+  """reopen-advance-gate サブコマンドの進行中 gate 更新"""
+
+  def setUp(self):
+    self.tmpdir = tempfile.mkdtemp()
+    self.addCleanup(shutil.rmtree, self.tmpdir)
+
+  def _write_spec(self):
+    spec_path = (
+      Path(self.tmpdir)
+      / ".reviewcompass"
+      / "specs"
+      / "workflow-management"
+      / "spec.json"
+    )
+    spec_path.parent.mkdir(parents=True)
+    spec_path.write_text(
+      json.dumps(
+        {
+          "feature_name": "workflow-management",
+          "workflow_state": {
+            "requirements": {
+              "drafting": True,
+              "triad-review": True,
+              "review-wave": True,
+              "alignment": False,
+              "approval": False,
+            }
+          },
+        },
+        ensure_ascii=False,
+        indent=2,
+      )
+      + "\n",
+      encoding="utf-8",
+    )
+    return spec_path
+
+  def test_reopen_advance_gate_updates_spec_and_in_progress_state(self):
+    """pending gate 完了時の spec.json と reopen YAML 更新を機械処理する"""
+    spec_path = self._write_spec()
+    in_progress = (
+      Path(self.tmpdir)
+      / "stages"
+      / "in-progress"
+      / "reopen-procedure-2026-06-15.yaml"
+    )
+    in_progress.parent.mkdir(parents=True)
+    in_progress.write_text(
+      "process_id: reopen-procedure\n"
+      "feature: workflow-management\n"
+      "step_number: 3\n"
+      "next_step: 第3過程：requirements alignment\n"
+      "completed_steps: []\n"
+      "pending_gates:\n"
+      "  - stages/requirements.yaml#alignment\n"
+      "  - stages/requirements.yaml#approval\n"
+      "completed_gates: []\n"
+      "downstream_impact_decisions: []\n"
+      "current_blocker: null\n",
+      encoding="utf-8",
+    )
+
+    result = run_script(
+      [
+        "reopen-advance-gate",
+        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
+        "--gate", "stages/requirements.yaml#alignment",
+        "--decision", "existing_sufficient",
+        "--feature-scope", "workflow-management",
+        "--rationale", "requirements alignment は既存で受けられる。",
+        "--evidence", ".reviewcompass/specs/_cross_feature/reviews/alignment.md",
+        "--completed-step", "第3過程：requirements alignment 実施",
+        "--set-spec", "workflow-management", "requirements", "alignment", "true",
+        "--json",
+      ],
+      cwd=self.tmpdir,
+    )
+
+    _assert_script_invoked(self, result)
+    self.assertEqual(result.returncode, 0, result.stdout)
+    data = json.loads(result.stdout)
+    self.assertEqual(data["verdict"], "OK")
+    spec = json.loads(spec_path.read_text(encoding="utf-8"))
+    self.assertTrue(spec["workflow_state"]["requirements"]["alignment"])
+    state = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
+    self.assertEqual(state["pending_gates"], ["stages/requirements.yaml#approval"])
+    self.assertEqual(state["completed_gates"], ["stages/requirements.yaml#alignment"])
+    self.assertEqual(
+      state["downstream_impact_decisions"][0]["gate"],
+      "stages/requirements.yaml#alignment",
+    )
+    self.assertEqual(state["next_step"], "第3過程：requirements approval")
+
+  def test_reopen_advance_gate_blocks_nonleading_pending_gate(self):
+    """pending_gates の先頭以外を飛ばして完了できない"""
+    self._write_spec()
+    in_progress = (
+      Path(self.tmpdir)
+      / "stages"
+      / "in-progress"
+      / "reopen-procedure-2026-06-15.yaml"
+    )
+    in_progress.parent.mkdir(parents=True)
+    in_progress.write_text(
+      "process_id: reopen-procedure\n"
+      "feature: workflow-management\n"
+      "step_number: 3\n"
+      "next_step: 第3過程：requirements alignment\n"
+      "completed_steps: []\n"
+      "pending_gates:\n"
+      "  - stages/requirements.yaml#alignment\n"
+      "  - stages/requirements.yaml#approval\n"
+      "completed_gates: []\n"
+      "downstream_impact_decisions: []\n"
+      "current_blocker: null\n",
+      encoding="utf-8",
+    )
+
+    result = run_script(
+      [
+        "reopen-advance-gate",
+        "--file", "stages/in-progress/reopen-procedure-2026-06-15.yaml",
+        "--gate", "stages/requirements.yaml#approval",
+        "--decision", "approved",
+        "--feature-scope", "workflow-management",
+        "--rationale", "approval を先に進める。",
+        "--evidence", "approval.md",
+        "--json",
+      ],
+      cwd=self.tmpdir,
+    )
+
+    _assert_script_invoked(self, result)
+    self.assertEqual(result.returncode, 2, result.stdout)
+    self.assertIn("先頭", result.stdout)
+
+
 def _init_git_repo(tmpdir):
   """temp dir に git リポジトリを初期化し、初回コミットと .reviewcompass 構造を準備する
 
   commit／push サブコマンドのテスト用ヘルパー。
   """
   for cmd in [
     ["git", "init", "-q", "-b", "main"],
     ["git", "config", "user.email", "test@example.com"],
     ["git", "config", "user.name", "Test User"],
     ["git", "config", "commit.gpgsign", "false"],
   ]:
     subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
   # 初回コミット（空でないリポジトリにする）
   (Path(tmpdir) / ".gitignore").write_text("")
   subprocess.run(
     ["git", "add", ".gitignore"], cwd=str(tmpdir), check=True, capture_output=True
   )
   subprocess.run(
     ["git", "commit", "-qm", "initial"],
     cwd=str(tmpdir), check=True, capture_output=True,
diff --git a/tools/check-workflow-action.py b/tools/check-workflow-action.py
index 5b34f4d9..ee62efa1 100644
--- a/tools/check-workflow-action.py
+++ b/tools/check-workflow-action.py
@@ -5205,40 +5205,190 @@ def cmd_reopen_start(args):
 
   action_dict = {
     "subcommand": "reopen-start",
     "args": {
       "classification": args.classification,
       "feature": args.feature,
       "basis": args.basis,
       "date": args.date,
       "trigger": args.trigger,
     },
   }
   log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
   try:
     append_log(log_path, action_dict, verdict, exit_code, reasons, current_state)
   except OSError as e:
     print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)
 
   return exit_code
 
 
+def _write_json_file(path, data):
+  """JSON ファイルを安定した形式で書き戻す"""
+  path.write_text(
+    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
+    encoding="utf-8",
+  )
+
+
+def _load_reopen_advance_state(cwd, relpath):
+  """reopen-advance-gate の対象 YAML を読む"""
+  path = Path(cwd) / relpath
+  if not path.exists():
+    raise ValueError(f"{relpath} が見つかりません")
+  try:
+    data = yaml.safe_load(path.read_text(encoding="utf-8"))
+  except yaml.YAMLError as e:
+    raise ValueError(f"{relpath} を YAML として読めません: {e}") from e
+  if not isinstance(data, dict):
+    raise ValueError(f"{relpath} は YAML object が必要です")
+  if data.get("process_id") != "reopen-procedure":
+    raise ValueError("process_id が reopen-procedure ではありません")
+  return path, data
+
+
+def _update_reopen_advance_spec(cwd, set_spec):
+  """--set-spec 指定があれば spec.json の workflow_state を更新する"""
+  if not set_spec:
+    return None
+  feature, phase, stage, value_text = set_spec
+  if value_text not in ("true", "false"):
+    raise ValueError("--set-spec の値は true または false が必要です")
+  if phase not in PHASE_STAGES or stage not in PHASE_STAGES[phase]:
+    raise ValueError("--set-spec の phase/stage が不正です")
+  spec_path = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
+  if not spec_path.exists():
+    raise ValueError(f"{spec_path.relative_to(cwd)} が見つかりません")
+  data = json.loads(spec_path.read_text(encoding="utf-8"))
+  workflow_state = data.setdefault("workflow_state", {})
+  phase_state = workflow_state.setdefault(phase, {})
+  phase_state[stage] = (value_text == "true")
+  _write_json_file(spec_path, data)
+  return str(spec_path.relative_to(cwd))
+
+
+def _next_step_for_pending_gate(gate):
+  """pending gate から人間向け next_step を作る"""
+  phase, stage = _parse_stage_gate(gate)
+  return f"第3過程：{phase} {stage}"
+
+
+def cmd_reopen_advance_gate(args):
+  """reopen 第3過程の pending gate 完了更新を機械処理する"""
+  cwd = Path.cwd()
+  reasons = []
+  try:
+    path, data = _load_reopen_advance_state(cwd, args.file)
+    pending_gates = data.get("pending_gates")
+    if not isinstance(pending_gates, list) or not all(isinstance(v, str) for v in pending_gates):
+      raise ValueError("pending_gates は文字列 list が必要です")
+    if not pending_gates or pending_gates[0] != args.gate:
+      raise ValueError("指定 gate は pending_gates の先頭である必要があります")
+    evidence = args.evidence or []
+    if not evidence:
+      raise ValueError("--evidence は 1 件以上必要です")
+
+    spec_path = _update_reopen_advance_spec(cwd, args.set_spec)
+
+    remaining_gates = pending_gates[1:]
+    data["pending_gates"] = remaining_gates
+    completed_gates = data.get("completed_gates")
+    if completed_gates is None:
+      completed_gates = []
+    if not isinstance(completed_gates, list):
+      raise ValueError("completed_gates は list が必要です")
+    if args.gate not in completed_gates:
+      completed_gates.append(args.gate)
+    data["completed_gates"] = completed_gates
+
+    completed_steps = data.get("completed_steps")
+    if completed_steps is None:
+      completed_steps = []
+    if not isinstance(completed_steps, list):
+      raise ValueError("completed_steps は list が必要です")
+    if args.completed_step and args.completed_step not in completed_steps:
+      completed_steps.append(args.completed_step)
+    data["completed_steps"] = completed_steps
+
+    decisions = data.get("downstream_impact_decisions")
+    if decisions is None:
+      decisions = []
+    if not isinstance(decisions, list):
+      raise ValueError("downstream_impact_decisions は list が必要です")
+    decisions.append(
+      {
+        "gate": args.gate,
+        "feature_scope": args.feature_scope,
+        "decision": args.decision,
+        "rationale": args.rationale,
+        "evidence": evidence,
+      }
+    )
+    data["downstream_impact_decisions"] = decisions
+    data["current_blocker"] = None
+    if remaining_gates:
+      data["next_step"] = _next_step_for_pending_gate(remaining_gates[0])
+      data["step_number"] = 3
+    else:
+      data["next_step"] = "第4過程：完了"
+      data["step_number"] = 4
+
+    path.write_text(
+      yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
+      encoding="utf-8",
+    )
+    verdict, exit_code = "OK", 0
+    next_action = {
+      "kind": "reopen_gate_advanced",
+      "file": args.file,
+      "gate": args.gate,
+      "remaining_gates": remaining_gates,
+      "phase": None,
+      "stage": None,
+      "reason": "reopen pending gate を更新しました",
+    }
+    current_state = {
+      "file": args.file,
+      "updated_spec": spec_path,
+      "pending_gates": remaining_gates,
+      "completed_gates": completed_gates,
+    }
+  except (OSError, ValueError, json.JSONDecodeError) as e:
+    verdict, exit_code = "DEVIATION", 2
+    reasons = [str(e)]
+    next_action = {
+      "kind": "reopen_advance_gate_failed",
+      "file": args.file,
+      "gate": args.gate,
+      "phase": None,
+      "stage": None,
+      "reason": "reopen pending gate を更新できません",
+    }
+    current_state = {}
+
+  if args.json:
+    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
+  else:
+    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))
+  return exit_code
+
+
 def _feature_all_approved(specs, feature):
   """feature の全 phase で approval=true かを返す（review-wave-summary 用、Req 10）"""
   ws = specs.get(feature, {}).get("workflow_state", {})
   approvals = [
     v.get("approval")
     for v in ws.values()
     if isinstance(v, dict) and "approval" in v
   ]
   return bool(approvals) and all(bool(a) for a in approvals)
 
 
 def aggregate_triage_for_summary(cwd):
   """triage.yaml 群を走査し件数を集計する（Req 10、design §2 集計規則）
 
   戻り値：(unresolved, draft, human_required, errors)
   - unresolved／human_required は item 単位、draft は run 単位。
   - 重複排除は run_id（＝ディレクトリ名）単位で、新パス（evidence）を優先。
   - 任意記録の非在（glob ゼロ件）は 0 件として正常。存在して解析不能なら errors に積む。
   """
   cwd = Path(cwd)
@@ -5605,40 +5755,59 @@ def main():
   )
   ac.add_argument("commitish", help="監査対象 commit（例：HEAD）")
 
   sub.add_parser(
     "next",
     help="現在の workflow_state から次に許可される作業を返す",
     parents=[common_parser],
   )
 
   rs = sub.add_parser(
     "reopen-start",
     help="reopen classification から in-progress ファイルを生成する",
     parents=[common_parser],
   )
   rs.add_argument("--classification", required=True, help="手戻り種別（例：D-1）")
   rs.add_argument("--feature", required=True, help="対象 feature 名")
   rs.add_argument("--basis", required=True, help="種別判定根拠ファイル")
   rs.add_argument("--date", required=True, help="in-progress ファイル名に使う日付（YYYY-MM-DD）")
   rs.add_argument("--trigger", required=True, help="reopen 起動理由")
 
+  rag = sub.add_parser(
+    "reopen-advance-gate",
+    help="reopen 第3過程の pending gate 完了更新を機械処理する",
+    parents=[common_parser],
+  )
+  rag.add_argument("--file", required=True, help="更新対象の reopen in-progress YAML")
+  rag.add_argument("--gate", required=True, help="完了する gate（例: stages/design.yaml#alignment）")
+  rag.add_argument("--decision", required=True, help="downstream_impact_decisions に記録する decision")
+  rag.add_argument("--feature-scope", required=True, help="downstream_impact_decisions に記録する feature_scope")
+  rag.add_argument("--rationale", required=True, help="判断理由")
+  rag.add_argument("--evidence", action="append", default=[], help="判断証跡。複数指定可")
+  rag.add_argument("--completed-step", default=None, help="completed_steps に追加する説明")
+  rag.add_argument(
+    "--set-spec",
+    nargs=4,
+    metavar=("FEATURE", "PHASE", "STAGE", "VALUE"),
+    help="spec.json の workflow_state を同時更新する",
+  )
+
   rws = sub.add_parser(
     "review-wave-summary",
     help="review-wave 横断確認の指標を集計して出力する（Req 10）",
     parents=[common_parser],
   )
   rws.add_argument("--out", default=None, help="要約出力の書き出し先パス（自身の出力のみ。状態は書き換えない）")
   rws.add_argument(
     "--save",
     action="store_true",
     help="既定保存先 .reviewcompass/specs/_cross_feature/reviews/ へ書き出す",
   )
 
   cap = sub.add_parser(
     "commit-approval",
     help="commit 承認 nonce challenge を作成・記録・無効化する",
   )
   cap_sub = cap.add_subparsers(
     dest="commit_approval_command",
     required=True,
   )
@@ -5696,33 +5865,35 @@ def main():
   elif args.subcommand == "stage":
     sys.exit(cmd_stage(args))
   elif args.subcommand == "commit":
     sys.exit(cmd_commit(args))
   elif args.subcommand == "push":
     sys.exit(cmd_push(args))
   elif args.subcommand == "autonomous-plan":
     sys.exit(cmd_autonomous_plan(args))
   elif args.subcommand == "autonomous-plan-template":
     sys.exit(cmd_autonomous_plan_template(args))
   elif args.subcommand == "autonomous-plan-record-integration":
     sys.exit(cmd_autonomous_plan_record_integration(args))
   elif args.subcommand == "autonomous-ledger-audit":
     sys.exit(cmd_autonomous_ledger_audit(args))
   elif args.subcommand == "audit-commit":
     sys.exit(cmd_audit_commit(args))
   elif args.subcommand == "next":
     sys.exit(cmd_next(args))
   elif args.subcommand == "reopen-start":
     sys.exit(cmd_reopen_start(args))
+  elif args.subcommand == "reopen-advance-gate":
+    sys.exit(cmd_reopen_advance_gate(args))
   elif args.subcommand == "review-wave-summary":
     sys.exit(cmd_review_wave_summary(args))
   elif args.subcommand == "commit-approval":
     sys.exit(cmd_commit_approval(args))
   elif args.subcommand == "decision-source-lint":
     sys.exit(cmd_decision_source_lint(args))
   else:
     parser.print_help(sys.stderr)
     sys.exit(2)
 
 
 if __name__ == "__main__":
   main()
END_IMPLEMENTATION_DIFF
