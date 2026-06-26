# 次セッション継続用メモ

最終更新：2026-06-26 セッション3（Mac ローカル）。最新状態は必ず `git log --oneline -4`、`git status`、`.venv/bin/python3 tools/check-workflow-action.py next --json` で確認する。

## 1. 今回（2026-06-26 セッション3）の完了作業

- **PPWM-2〜7 すべて実装完了**（計12コミット）
  - PPWM-2: `post_write_policy_violation` に `file_classification` / `allowed_operations` / `forbidden_operations` を追加
  - PPWM-3: `tools/api_providers/source_bundle.py` 新設（ファイル本文込みのソース束、SHA検証）
  - PPWM-4: `tools/api_providers/post_write_prompt_builder.py` 新設（必須10セクション固定順序生成）
  - PPWM-5: `tools/api_providers/post_write_prompt_audit.py` 新設（プロンプト監査・機微情報検出）
  - PPWM-6: `tools/api_providers/runner_gate.py` 新設（API実行前の関門）
  - PPWM-7: 統合テスト追加 + `_extract_section` のコードブロック内見出し誤判定バグ修正
  - backlog の plan と index を `completed` に更新
- **残存4件の失敗テスト原因を特定**（修正は次セッション以降）

現時点のテスト状況：723件通過、4件が既存の失敗として残留（原因特定済み）。

## 2. 最優先：残存4件のテスト失敗を直す

### グループA：`CommitExitCodeTests` の3件（テストコードのバグ）

**テスト名：**
- `test_repair_workflow_state_prepare_allows_post_write_exception_preflight`
- `test_repair_workflow_state_record_allows_matching_commit`
- `test_repair_workflow_state_record_rejects_changed_scope`

**原因：** テストがファイルを作成した後、`git add` でステージングせずに `repair-workflow-state prepare` を呼んでいる。`repair-workflow-state prepare` はステージング済みファイルを必要とするため、"repair 対象の staged 変更がありません" で失敗する。

**修正箇所：** `tests/tools/test_check_workflow_action.py` の各テストで、ファイル作成後・`repair-workflow-state prepare` 呼び出し前に `git add` を追加する。

例（`test_repair_workflow_state_prepare_allows_post_write_exception_preflight` の場合）：
```python
target.write_text("運用正本\n", encoding="utf-8")
tool.write_text("print('repair')\n", encoding="utf-8")
# ↓ この行を追加する
subprocess.run(["git", "add", str(target.relative_to(self.tmpdir)), str(tool.relative_to(self.tmpdir))],
               cwd=str(self.tmpdir), check=True, capture_output=True)
prepare = run_script(["repair-workflow-state", "prepare", ...], cwd=self.tmpdir)
```

`test_repair_workflow_state_record_allows_matching_commit` はすでに中間に `git add` があるが、順序が `prepare` の後になっているため、`prepare` の前に移動する必要がある。

**実装側は正しい**。テストコードだけ直す。

### グループB：`PostWriteReviewRunEndToEndTests` の1件（実装の非対称）

**テスト名：** `test_next_accepts_manifest_generated_from_review_triage_helper`

**原因：** `_write_review_run` ヘルパーがレビュー実行結果を `docs/notes/review-runs/` 以下に作る。このパスは `is_post_write_verification_target` では除外されるが、`is_lightweight_self_check_target` では `docs/notes/` プレフィックスにより軽量自己精査の対象として浮上してしまう。マニフェストが完了状態でも、`next` が `stage` ではなく `lightweight_self_check` を返す。

**修正方針：** `is_lightweight_self_check_target` に `/review-runs/` を含むパスを除外する条件を追加する。または、レビュー実行成果物は完了済み証跡として `next` の変更ファイル対象から外す。

詳細は `issue-2026-06-26-post-write-tests-need-mechanization-not-fixture-rename.yaml` に記録済み。

## 3. セッション記録（untracked のまま・次セッション以降に取り込む）

以下は進行中のため今セッションではコミット不可：

- `.reviewcompass/evidence/sessions/2026-06-24-claude-*.md`（2件）
- `.reviewcompass/evidence/sessions/2026-06-25-claude-*.md`（1件）
- `docs/sessions/auto-2026-06-24-claude-*.md`（2件）
- `docs/sessions/auto-2026-06-25-claude-*.md`（1件）

## 4. 横展開の課題（issue 記録済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは guarded commit が全方法で拒否される。

## 5. MWP-0：next --json kind 再設計（検討完了・実装未着手）

kind を41種類から7種類に整理する設計が確定済み。詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md`。実装の優先順位は未決定。

## 6. 参照

- post-write 機械化計画（完了済み）：`.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`
- 残存テスト issue：`.reviewcompass/backlog/issues/issue-2026-06-26-post-write-tests-need-mechanization-not-fixture-rename.yaml`
- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- backlog 操作カード：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
