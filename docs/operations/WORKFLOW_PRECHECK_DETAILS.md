# WORKFLOW_PRECHECK 詳細仕様

本文書は `tools/check-workflow-action.py` と `tools/guarded-git-commit.py` の詳細仕様を定める。運用時に読む短い契約は [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md) を正とし、本書は実装・保守・テストで必要な詳細を補う。

## 1. サブコマンド

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

<a id="spec-set"></a>

## 2. spec-set

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `<feature>` | 必須 | 対象機能名。`stages/feature-dependency.yaml` の `features` キーと一致する |
| `<phase>` | 必須 | 対象フェーズ |
| `<stage>` | 必須 | 対象段。フェーズにより有効値が異なる |
| `<new-value>` | 必須 | `true` または `false` |
| `--rationale` | 任意 | 変更理由。ログ記録用であり判定値には影響しない |

`<new-value>` が `true` の場合、次を検査する。

- 同フェーズ内で当該段より前の段が完了していること
- 上流フェーズの最終段が完了していること
- `recheck.upstream_change_pending=true` の影響対象 phase を完了扱いに戻していないこと
- `intent` と `feature-partitioning` のような機能横断段で、単一 feature だけを不整合に変えていないこと

`<new-value>` が `false` の場合、reopen 手続きの一部として原則許容する。ただし、完了済み段を戻す場合は警告を返す。

<a id="commit"></a>

## 3. commit

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | commit 理由。人による承認の出典を含めることを推奨する |
| `--execution-actor` | 任意 | commit 実行主体。`llm` または `human`。既定は `llm` |

`--execution-actor llm` の場合、通常の commit 内容承認とは別に、LLM による実行代行承認を必要とする。

承認レコードの最小形：

```json
{
  "approved_action": "commit",
  "approved_by": "user",
  "approved_at": "2026-06-03T00:00:00+09:00",
  "rationale": "人がコミットを明示承認",
  "target_files": ["path/to/file.md"],
  "execution_delegation": {
    "delegated_to": "llm",
    "approved_by": "user",
    "approved_at": "2026-06-03T00:00:00+09:00",
    "explicit_instruction": "コミット",
    "rationale": "人が単発 commit 実行を明示指示"
  },
  "expires_after_commit": true,
  "consumed": false
}
```

判定対象：

- `.reviewcompass/approvals/commit-approval.json` が存在し、形式が正しく、未消費であること
- staged ファイルが `target_files` の範囲内であること
- LLM 実行時は `execution_delegation` があること
- staged ファイルに post-write-verification 対象がある場合、現在 sha256 を覆う completed manifest があること
- staged された `spec.json` に reopen 印がある場合、同じ commit に reopen 手続き記録が含まれること
- reopen 完了記録が含まれる場合、feature impact 判定、下流影響判定、影響フェーズ網羅が記録されていること
- 持ち越し所見の件数を確認し、未消化所見があれば警告すること
- staged ファイルを通常変更、要注意変更、危険変更に分類すること
- staged 文書の Markdown リンク、アンカー、既知の意味的組み合わせを `tools/document_link_lint.py` で検査すること

危険変更がある場合は逸脱とする。要注意変更は警告とする。

`tools/guarded-git-commit.py` は `commit --execution-actor llm` を先に実行し、exit 2 なら commit しない。exit 1 は既定では停止し、人の判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、期限付き承認レコードは消費済みにする。

<a id="push"></a>

## 4. push

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | push 理由。人による承認の出典を含めることを推奨する |

判定対象：

- 作業ツリーが clean であること
- `origin/main` からのローカル先行コミット数を出力すること
- 直近コミットの題名要約を出力すること
- `origin/main` 以外への push が要求されていれば警告すること

作業ツリーが dirty の場合は逸脱とする。

<a id="audit-commit"></a>

## 5. audit-commit

`audit-commit <commit-ish>` は、指定 commit の変更ファイルを読み、post-write-verification 対象だけを抽出する。

判定：

- 対象なし：OK
- 対象あり、commit 内ファイル内容 sha256 を覆う completed manifest がある：OK
- 対象あり、manifest がない、sha256 不一致、coverage matrix 不足、または未解決本質的指摘がある：逸脱
- `<commit-ish>` が解決できない：逸脱

この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。

<a id="autonomous-plan"></a>
<a id="autonomous-plan-template"></a>
<a id="autonomous-plan-record-integration"></a>
<a id="autonomous-ledger-audit"></a>

## 6. autonomous-plan 系

`autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。

- `mode: autonomous_parallel`
- `run_id`
- `authorization.approved_by`
- レビュー結果サマリと三段階トリアージの提示済み記録
- 各 task の `source_finding_ids`、`allowed_paths`、`expected_tests`、停止条件
- 並列 task 間の `allowed_paths` 衝突がないこと
- `integration_gate` の確認項目
- 作業ノイズを本線 repo に取り込まない出力方針
- 履歴台帳パス、タスク割当記録、判断根拠記録、統合結果記録、保存方針

検査に通った場合も、通らなかった場合も、台帳パスが妥当なら判定履歴を記録する。

`autonomous-plan-template` は最小テンプレートを生成する。`autonomous-plan-record-integration` は統合後に既存の履歴台帳へ `integration_result` を追記する。

## 7. 出力形式

終了コード：

- `0`：問題なし
- `1`：警告あり
- `2`：逸脱検出

人間可読出力は、少なくとも判定結果、対象サブコマンド、判定理由、現在状態の要約を含む。

JSON 出力は、少なくとも次のキーを含む。

```json
{
  "verdict": "OK | WARN | DEVIATION",
  "exit_code": 0,
  "action": {
    "subcommand": "commit",
    "args": {}
  },
  "reasons": [],
  "current_state": {}
}
```

## 8. ログ

判定ログは JSON Lines 形式で記録する。`--json` 出力と同等の構造に `timestamp` を追加する。

既定パス：

- `.reviewcompass/runtime/logs/workflow-precheck.log`（旧 `docs/logs/workflow-precheck.log` からの変更は
  2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。旧ログは凍結、読み取り互換は P3 まで）

`--log-path` でテスト用の隔離パスへ上書きできる。

### 8.1 実行時生成物の凍結期（P3 まで）の扱い

検査ログ・effective prompt（`.reviewcompass/runtime/effective-prompts/`、旧 `.reviewcompass/effective-prompts/`）・
commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.json`、旧 `.reviewcompass/approvals/commit-approval.json`）の
3 パスは、書き込みを常に新配置（runtime 区画、原則 git 無視）へ行い、読み取りは新→旧の順でフォールバックする
（新旧競合時は新配置を正とする）。契約の正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
定数と読み取り解決の実装正本は `tools/check_workflow_action/runtime_paths.py`。

凍結検査の手動実行手順（ゲートへの自動統合は行わず、手動運用とする）：

1. 凍結境界（P1 実装反映コミット＝書き込み先切替のコミット）を特定する。例：

   ```bash
   git log --reverse --format=%H -S "runtime/logs/workflow-precheck" -- tools/check_workflow_action/runtime_paths.py | head -1
   ```

2. 旧 3 パスへの凍結違反（追加・変更・削除）を検出する。例：

   ```bash
   PYTHONPATH=. .venv/bin/python3 -c "
   from tools.check_workflow_action.placement_freeze import check_runtime_placement_freeze
   for v in check_runtime_placement_freeze('.', '<freeze-commit>'):
     print(v)
   "
   ```

   注記：ReviewCompass 自身では旧 3 パスは gitignore 対象（未追跡）のため、git 履歴で不変性を立証できるのは
   旧配置を追跡している構成（対象アプリ等）に限る。未追跡の旧成果物の凍結は書き込み経路のテスト
   （`tests/tools/test_runtime_placement_freeze.py`）で担保する。

## 9. テスト観点

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。
