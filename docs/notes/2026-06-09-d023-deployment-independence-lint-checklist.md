---
date: 2026-06-09
candidate_id: D-023
title: deployment independence lint checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-023 Deployment Independence Lint Checklist

## 0. 位置づけ

このチェックリストは、D-023 `相対リンク・配置非依存性の機械検査` を進めるための作業台帳である。

D-023 の目的は、ReviewCompass の文書・設定・スキーマが、配置先ディレクトリに依存しない参照だけで構成されているかを機械的に検査することである。

## 1. 作業前確認

- [x] D-023 本文を確認した。
- [x] D-021 / D-020 の安定デプロイ判定で、配置非依存性 lint が残タスクであることを確認した。
- [x] 成果物対象範囲の初期 lint 対象を `docs/operations`、`learning/workflow/schemas`、`config` とした。
- [x] `docs/notes` 全体は作業記録・review-run raw を含むため、初期 blocking lint 対象からは除外した。

## 2. Lint Contract

`tools/deployment_independence_lint.py` は次を検出する。

| Target | Rule |
| --- | --- |
| Unix local absolute path | local user / private temp などの Unix 絶対パスを検出する。 |
| Windows local absolute path | drive-letter 形式の Windows 絶対パスを検出する。 |
| Markdown / YAML / JSON | lint 対象 suffix とする。 |
| External URL | `https://...` / `http://...` は許容する。 |
| Temporary audit path | `/private/tmp/reviewcompass-...` と `/tmp/reviewcompass-...` は許容する。 |

## 3. 実装チェックリスト

- [x] red test を追加し、linter 未実装で失敗することを確認した。
- [x] Unix absolute path 検出テストを追加した。
- [x] Windows absolute path 検出テストを追加した。
- [x] external URL 例外テストを追加した。
- [x] temporary audit path 例外テストを追加した。
- [x] Markdown / YAML / JSON のみ scan するテストを追加した。
- [x] 単一ファイル scan テストを追加した。
- [x] `tools/deployment_independence_lint.py` を追加した。
- [x] `tools/README.md` に実行例を追記した。
- [x] 初期対象範囲 lint を実行した。
- [x] post-write verification を実施する。
- [x] commit precheck guard に deployable artifact の staged 内容 lint を統合した。
- [x] push guard に HEAD commit 内容 lint を直接統合した。

## 4. Initial Lint Result

実行コマンド:

```bash
.venv/bin/python3 tools/deployment_independence_lint.py --json docs/operations learning/workflow/schemas config
```

初回結果:

- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` に Claude project memory storage のローカル絶対パスが 1 件あった。
- 該当箇所を環境非依存の説明へ置き換えた。

修正後結果:

```json
{
  "findings": []
}
```

## 5. Deployment Gate Impact

この対応により、安定デプロイ前の配置非依存性 gate は次の状態になった。

| Gate | State |
| --- | --- |
| D-023 linter implementation | ready |
| docs/operations lint | passed |
| learning/workflow/schemas lint | passed |
| config lint | passed |
| commit guard integration | implemented |
| push guard integration | implemented |

stable deploy candidate までに残る blocking 項目はない。push guard 直接統合も完了したため、D-023 scope の guard hardening は完了として扱える。

## 6. Status Snapshot

- `next --json`: `completed`
- current task: D-023 commit and push guard integration implemented
- next task: commit
- last status refresh: 2026-06-09, after push guard tests
