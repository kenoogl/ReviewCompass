# 次セッション継続用メモ

最終更新：2026-06-27 セッション8（Mac ローカル）。最新状態は必ず `git log --oneline -5`、`git status`、spec.json を直接確認する。

**重要：`next --json` コマンドは MWP-0 の実装対象そのものであるため、ワークフロー進行の判断に使えない。spec.json の値を直接読んで現在のフェーズを把握すること。**

## 1. 今回（2026-06-27 セッション8）の完了作業

- **MWP-0 tasks.drafting 完了**（コミット git:d26deab5）
  - tasks.md に T-015（kind 14値→7値）・T-020（新タスク）・要件追跡2行を追記
  - spec.json の tasks.drafting = true に更新
- **MWP-0 tasks.triad-review 完了**（コミット git:82baec61）
  - 3モデル外部 API 審査（claude-sonnet-4-6・gpt-5.5・gemini-3.1-pro-preview）
  - 5クラスタを proxy_model（gpt-5.5）で判断、tasks.md に5件修正を適用
    - α：T-015「テスト変更禁止」に kind 更新分の例外追記
    - β：完了条件4の根拠参照を reopen 分類文書に差し替え
    - γ：T-020 先送り事項(a)の担当範囲を ①②③⑤ に整理（④⑥は T-015 対処済み）
    - δ：T-020 完了条件5（廃止表現統一・手動確認）を追加
    - ε：要件追跡の受入11行に T-020 担当分を追記

## 2. 次セッションの最初にやること

### セッション記録のコミット

現セッション（`76b4149b`）の記録が untracked のまま。次セッションの SessionStart フックが自動取り込み・コミット可能になる。

### MWP-0 tasks.review-wave へ進む

spec.json の現在値（2026-06-27 時点）：
```
tasks:          drafting=true  triad-review=true  review-wave=false  alignment=false  approval=false
implementation: drafting=true  triad-review=true  review-wave=true   alignment=false  approval=false
```

tasks.review-wave（全機能横断のまとめレビュー）の手順：

1. review-wave の前提「全機能の drafting＋triad-review 完了」を spec.json で確認する
2. cross-feature レビューを実施する
3. 完了後 `tasks.alignment` → `tasks.approval` へ進む

tasks.approval 通過後は implementation フェーズへ。implementation.alignment・implementation.approval が false なので、MWP-0 反映内容を確認してから実装に入ること。

## 3. 横展開の課題（issue 記録済み・未着手）

- `issue-2026-06-24-approval-stage-proxy-actor-boundary-mismatch`：guide の approval 段の承認主体記述が human-only 境界と矛盾の疑い。
- `issue-2026-06-24-sandbox-guarded-commit-blocked`：WEB サンドボックスでは guarded commit が全方法で拒否される。

## 4. 参照

- commit 手順：`.reviewcompass/guidance/COMMIT_OPERATION_CARD.md`
- ワークフロー操作ガイド：`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`
- kind 再設計メモ：`docs/notes/2026-06-26-next-json-kind-redesign.md`
- reopen 分類根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`
- tasks triad-review 記録：`.reviewcompass/evidence/review-runs/2026-06-27-mwp0-tasks-triad-review/`

過去の詳細は git log、`docs/notes/`、`docs/sessions/` を正本とする。
