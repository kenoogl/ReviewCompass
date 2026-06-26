# 次セッション継続用メモ

最終更新：2026-06-26 セッション2（Mac ローカル）。最新状態は必ず `git log --oneline -4`、`git status`、`.venv/bin/python3 tools/check-workflow-action.py next --json` で確認する。

## 1. 今回（2026-06-26 セッション2）の完了作業

- **テスト付け替え（commit `799dbe5f`）**：`tests/tools/test_check_workflow_action.py` の post-write 関連テスト20件のうち18件を緑化。`docs/notes/` の見本パスを `docs/disciplines/` へ付け替え。backlog todo `todo-2026-06-26-post-write-test-fixture-strict-path-realignment` 完了。
- **PPWM-1 実装（commit `81db6ff7`）**：`next` コマンドが `post_write_verification` 地点で `runtime` 生成パスではなく `guidance` 正本パス（`.reviewcompass/guidance/effective-prompts/next-action-post-write-verification.prompt.md`）を返すよう修正。`WORKFLOW_DISCIPLINE_MAP.yaml` と `check-workflow-action.py` の `DEFAULT_DISCIPLINE_MAP` 両方に `canonical_effective_prompt_path` を追加。repair record の照合ロジックを staged_files ベースに統一（バグ修正）。backlog todo `todo-2026-06-26-ppwm1-canonical-effective-prompt-fixation` 完了。

## 2. 最優先：PPWM-2 以降の実装

**`plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`** の残作業。

- **PPWM-1**：完了（canonical effective prompt 正本固定）
- **PPWM-2**：`post_write_policy_violation inspect` 操作の実装（未着手）
- **PPWM-3**：Source bundle builder（未着手）
- **PPWM-4**：Prompt builder（未着手）
- **PPWM-5**：Prompt audit（未着手）
- **PPWM-6**：Runner gate（未着手）
- **PPWM-7**：実運用確認（未着手）

次セッションは PPWM-2 から着手する。

## 3. テスト残件（issue 分離済み・実装待ち）

`issue-2026-06-26-post-write-tests-need-mechanization-not-fixture-rename` に記録済み。

- `test_next_post_write_verification_returns_canonical_effective_prompt`：PPWM-1 で解消済み（緑）
- `test_next_accepts_manifest_generated_from_review_triage_helper`：`docs/notes/review-runs/` 配下が `lightweight_self_check` の対象として浮上する問題。実装方針は issue に記録。

現時点のテスト状況：276件通過、1件が上記 issue として残留。

## 4. セッション記録（untracked のまま・次セッション以降に取り込む）

以下は進行中のため今セッションではコミット不可。セッション終了後に別コミットで取り込む：

- `.reviewcompass/evidence/sessions/2026-06-24-claude-*.md`（3件）
- `docs/sessions/auto-2026-06-24-claude-*.md`（2件）
- `docs/sessions/auto-2026-06-25-claude-*.md`（1件）

## 5. 横展開の課題（issue 記録済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは guarded commit が全方法で拒否される。

## 6. MWP-0：next --json kind 再設計（検討完了・実装未着手）

kind を41種類から7種類に整理する設計が確定済み。詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md`。実装の優先順位は未決定。

## 7. 参照

- 機械化計画：`.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`
- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- backlog 操作カード：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
