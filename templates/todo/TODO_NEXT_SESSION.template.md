# ReviewCompass - Codex 次セッション継続用メモ

最終更新：<YYYY-MM-DD>。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 0. 全体像

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である。

開発は feature ごとの `workflow_state` に従い、intent → feature-partitioning → requirements → design → tasks → implementation の各 phase を、drafting／triad-review／review-wave／alignment／approval の段で進める。

LLM の記憶に頼らず、`tools/check-workflow-action.py next --json`、spec.json、post-write manifest、commit guard、carry-forward register などの機械判定を、作業順序と規律遵守の正本にする。

重要件は、raw・要約・三段階トリアージ・判断理由を残し、通常モードでは修正前に利用者承認を得る。自律／proxy_model モードでは、判断代行の raw・候補案・採用案・理由を記録する。

旧 ReviewCompass 固有の状態台帳は carry-forward register に抽象化し、配布先プロジェクトでは別の状態入力に差し替えられるようにする。

## 1. 起動時に必ず行うこと

1. `tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

Python 実行は、必要に応じて venv を使う：

```bash
.venv/bin/python3 tools/check-workflow-action.py next --json
```

## 2. 不可逆操作の規律

- spec.json の workflow_state 変更、commit、push、規律ファイル変更、大方針転換は利用者の明示承認が必要。
- commit は利用者から「コミット」と明示された場合だけ実行する。
- commit は原則 `tools/guarded-git-commit.py -m "<message>" --rationale "<理由>"` 経由。
- commit 前に `.reviewcompass/approvals/commit-approval.json` を staged 内容と SHA に合わせる。
- post-write-verification 対象文書を staged する場合、completed manifest と SHA 一致が必要。
- API review-run の結果を使う場合は、raw、モデル別要約、三段階トリアージをまとめて提示する。重要件は通常モードでは修正前に案を示して承認を得る。

## 3. 現在位置

`next --json` の直近確認結果をここに記録する：

- feature: `<feature>`
- phase: `<phase>`
- stage: `<stage>`
- reason: `<reason>`

implementation など、次作業に必要な最小限の進捗だけを箇条書きで残す。長いセッション履歴は `docs/sessions/` や `docs/archive/todo/` に送る。

## 4. 次作業

`next_action.kind == "stage"` の場合のみ、`feature`、`phase`、`stage` が本節の条件と一致することを確認して進む。

`post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、この節の作業へ進まない。

進め方：

1. `next_action.required_disciplines` に出た規律を読む。
2. 対象 feature の `spec.json` と、対象 phase の requirements/design/tasks を必要範囲だけ読む。
3. API 経由で review-run を実施する場合は raw を必ず保存し、モデル別要約と三段階トリアージを残す。
4. 重要件を通常モードで修正する場合は、修正前に案を示して承認を得る。

## 5. 直近の完了事項

直近の到達点だけを短く残す。古いセッション履歴、長い検証経緯、コミット列挙はここへ溜め込まず、該当する `docs/sessions/`、`docs/notes/`、`docs/archive/todo/` を参照する。

## 6. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- Codex adapter guidance: `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`
- disciplines: `docs/disciplines/`
- spec.json: `.reviewcompass/specs/<feature>/spec.json`
- carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
