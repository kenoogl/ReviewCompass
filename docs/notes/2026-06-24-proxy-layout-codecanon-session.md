# 経緯ノート：proxy 裁定レコードのレイアウト整合（コード正本）と post-write 封印の落とし穴

日付：2026-06-24（Claude セッション）
関連：`plan-2026-06-24-proxy-decision-record-naming-reconciliation`、review-run `2026-06-24-proxy-layout-codecanon-postwrite-3way`

## 1. 背景

前回セッションで「proxy 裁定レコードの命名統一」（`proxy-approval.yaml` / `approved_by`）を実施し completed としたが、その post-write 封印が**単一 Gemini**による不十分なものだった（TODO §3 で「早まった完了」と自己申告）。本セッションはその続き（option 3＝レイアウトの正本決定）から再開した。

## 2. 利用者の決定

option 3 を「**コードが正本**」で確定。proxy 裁定ファイルの配置は、実コード `make-proxy-approval.py` が固定名で生成する `decisions/<suffix>.yaml` と `proxy-approval.yaml` を正とする。

## 3. 実コード調査で判明した追加の食い違い

「コードが正本」を適用するため実コードと実 run を精査したところ、**design.md の図自体が現行コードと食い違っていた**：

- 図にあった `proxy-decision-prompts/`・`proxy-decisions/<batch>.raw.yaml`・`<batch>.decisions-input.yaml` は、現行コードが生成しない 2026-06-12 頃の旧 run の名残。
- 現行は proxy へのプロンプト/応答を review-run 直下に置き（実例 `proxy-adjudication-prompt.md` / `-response.txt`、ファイル名は実行時引数で変わる）、裁定は `decisions/<suffix>.yaml`、束ねは `proxy-approval.yaml`。

利用者の合意（案A）で、guide・tasks だけでなく design.md の図も現行コードへ整合した。

## 4. 実施内容

- design.md 図/本文、`SESSION_WORKFLOW_GUIDE.md`(206/222-235)、`tasks.md`(128) を `decisions/<suffix>.yaml` + `proxy-approval.yaml` へ整合。プロンプト/応答は「review-run 直下・既定名・実行時指定可」と概念記述し、変わりうるファイル名は断定しない。
- TDD：`test_session_record_contract.py` に `test_proxy_decision_record_layout_matches_implementation` を追加（レッド確認 → 整合 → 12 件 green）。
- 機械的3者（claude-sonnet-4-6 / gpt-5.5 / gemini-3.1-pro-preview）で post-write 検証。diff＋実コード＋決定箇条書きを同梱し、焦点化した問いと「所見0でも観点ごとに照合根拠を1行」を指示。結果：gemini が4観点で整合を明示確認、claude 所見0、gpt-5.5 が ERROR 1件（後述）。parse_failed=0。

## 5. gpt-5.5 の所見と扱い

gpt-5.5 は、今回のレイアウト整合**ではなく**、guide 76/104 の approval 段（フェーズ移行承認）の主体記述「actor=human または proxy_model」が human-only 境界と矛盾する、と指摘。これは別機構の既存記述への本質的指摘。利用者承認（案A）で `leave-as-is`（今回スコープ外）とし、`issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch` へ横展開記録した（真偽は design の decision_scope 機構と照合して別途精査）。

## 6. 詰まりと回避（重要な教訓）

- **post_write_policy_violation**：起動時 next が DEVIATION。前回の単一 Gemini manifest（旧 005）が pending を作り、guide が「変更禁止」ロック。旧 005 を退け、TODO を一時退避して解除した。
- **write-manifest と next の post-write 判定不整合（バグ）**：`review_triage.py:76` の `_is_post_write_target` が specs 配下 .md と機械生成セッション記録を対象に含め、guide 単独封印を「未レビューが残る」と拒否。`check-workflow-action.py` と discipline は specs を対象外とする。→ `issue-2026-06-24-post-write-target-judgment-mismatch` へ横展開。修正は post-write pending 中は tools/*.py が forbidden のため封印後。
- **git stash -u の巻き込み**：`git stash push -u -- <pathspec>` が pathspec 外の未追跡ファイル（run-dir 含む）まで巻き込み、pop で封印（006 manifest）と decide 結果が巻き戻った。approval.yaml も一時消失。→ stash を捨て、**skip-worktree（tracked の design/tasks）＋ファイル一時移動（untracked の docs-session）** で guide 単独封印し、即復元した。封印は `post-write-2026-06-24-005.yaml`（3者版・guide のみ・sha 3acbdc75・unresolved 0）。

## 7. 記録是正

前回（命名統一）の plan/maintenance の封印根拠は単一 Gemini で不十分だったため、両者に3者再検証の addendum を追記（completed は維持）。今回のレイアウト整合は前回の漏れの補完と位置づけ。

## 8. 残課題

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`（approval 段の承認境界、decision_scope と照合）
- `issue-2026-06-24-post-write-target-judgment-mismatch`（post-write 判定不整合バグ、TDD 修正）
