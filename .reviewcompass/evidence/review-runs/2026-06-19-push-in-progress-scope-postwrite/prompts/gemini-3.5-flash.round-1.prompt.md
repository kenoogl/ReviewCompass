prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: push_in_progress_scope_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T02:45:09.153646+00:00

## Change Summary

push guard から stages/in-progress の存在単体による遮断を外し、dirty tree、commit precheck record 欠落、deployable artifact lint 失敗など push で本当に危険な条件だけを遮断するようにした。

## Review Question

push 操作の運用文書が、in-progress の存在だけでは push を止めず、実害のある dirty tree / commit precheck 欠落 / deployable artifact lint 失敗だけを止める contract と矛盾していないか。

## Target Files

- docs/operations/WORKFLOW_PRECHECK.md sha256=d9c446b65a3d27ab42e608caa3252d225e74b716e8a0d558f4ae600c54091b36
- docs/operations/WORKFLOW_PRECHECK_DETAILS.md sha256=33a6167a08a245cfa62a4aff045277fb2c03c0d0c5c610d824c37e744a38771b

## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
docs/operations/WORKFLOW_PRECHECK.md
docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# Target document
## docs/operations/WORKFLOW_PRECHECK.md

# WORKFLOW_PRECHECK：ワークフロー事前検査の運用契約

本文書は `tools/check-workflow-action.py` と関連ラッパーの運用契約を定める。詳細な引数、判定条件、出力構造、テスト観点は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md) を参照する。仕様の変更には人の明示承認が必要である。

## 1. 目的

ワークフロー事前検査は、不可逆操作の直前に現在のワークフロー状態との整合を機械判定するための仕組みである。

対象となる不可逆操作：

1. spec.json の `workflow_state` 変更
2. git commit
3. git push

## 2. 役割分担

ワークフロー事前検査は、次の 3 段階で扱う。

- **段階 1**：LLM または作業者が、不可逆操作の直前に本スクリプトを呼び出し、結果を解釈する
- **段階 2**：本スクリプトが、状態を読み取り、判定結果を返す
- **段階 3**：実行環境の hook 連携が、呼び忘れを機械的に遮断する

段階 2 は判定だけを行う。承認取得、状態変更、人への問い合わせ、強制遮断は行わない。

## 3. 適用範囲

本スクリプトは次を対象とする。

- `spec-set`：spec.json の workflow_state 変更前検査
- `commit-preflight`：commit 指示直後、stage / approval 作成前の read-only 入口検査
- `commit-approval`：staged 内容に束縛した commit approval challenge、内容承認、実行代行承認、無効化の記録
- `commit`：commit 前検査
- `push`：push 前検査
- `audit-commit`：commit 済み変更に対する post-write-verification 監査
- `reopen-advance-step`：reopen 第1・第2過程の完了更新
- `reopen-advance-gate`：reopen 中の pending gate 完了更新
- `reopen-set-blocker`：reopen 中の approval 承認待ち blocker 設定
- `reopen-finalize`：reopen 第4過程の完了 YAML 生成と completed 移動
- `autonomous-plan`：自律・並列実行計画の開始前検査
- `autonomous-plan-template`：自律・並列実行計画テンプレート生成
- `autonomous-plan-record-integration`：自律・並列実行の統合結果記録
- `commit-from-current-staged.py`：現在の staged index に束縛した approval 作成と guarded commit を 1 コマンドで連続実行するラッパー
- `guarded-git-commit.py`：commit 前検査つき git commit ラッパー

対象外：

- 仕様文書ファイルの編集前検査
- 計画文書の編集前検査
- 応答テキストだけの妥当性判定

適用範囲を拡張する場合は、本文書を改訂して人の明示承認を受ける。

## 4. 呼び出し契約

基本形：

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit-preflight
tools/check-workflow-action.py commit-approval prepare --json
tools/check-workflow-action.py commit-approval record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]
tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin [--json]
tools/check-workflow-action.py commit-approval invalidate [--json]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
tools/check-workflow-action.py reopen-set-blocker --file <path> --gate stages/<phase>.yaml#approval --actor human|proxy_model --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
printf 'コミット\n' | tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

commit は人の職掌範囲である。利用者が commit を指示した直後は、Git index への追加（`git add`）、commit approval challenge、approval record、execution delegation record、guarded commit のいずれを作る前にも、まず `commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、commit できない理由、何も作らず止めたこと、次に許可されている workflow action だけを短く報告する。`--execution-actor llm` の場合、通常の commit 内容承認とは別に、LLM による実行代行の明示承認を必要とする。実行時は直接 `git commit` ではなく、原則として `tools/commit-from-current-staged.py` を使う。

`tools/commit-from-current-staged.py` は stdin の承認 1 行を必須とし、空入力または許可文言外の入力なら challenge 作成前に停止する。承認文を確認した後、古い runtime approval/delegation を無効化し、現在の staged exact index の digest で challenge を作り、その nonce を即 `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` へ渡す。これにより、古い approval の残存、nonce の手写し、challenge 作成後の別操作、空 stdin 実行を標準導線から外す。

nonce 方式の commit approval を低レベル手順として使う場合、commit 準備は逐次手順として扱う。stage 後に `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を実行し、返された nonce で `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を起動する。`commit-approval prepare` と `commit --json` precheck を並列に実行しない。challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まず、guarded commit に承認 1 行を渡す。`--approval-source-text-line-stdin` を空 stdin で実行してはいけない。

Codex の `workspace-write` sandbox では、`commit-from-current-staged.py` または `guarded-git-commit.py` が最終的に `.git/index.lock` へ書き込む段階で sandbox に拒否され得る。このため Codex から commit を実行する場合は、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

commit 実行時のユーザー向け報告は、guard や precheck の詳細出力をそのまま貼らず、結論だけを短く伝える。成功時は commit hash と commit message、必要なら検証コマンドだけを報告する。失敗時は停止理由を 1〜3 点に要約し、承認再作成、staged 対象の見直し、post-write 未完了など、次に必要な操作だけを示す。詳細ログは必要時に参照できる状態に留め、通常の進行報告には含めない。

<a id="spec-set"></a>

### 4.1 spec-set

`spec-set` は、spec.json の `workflow_state` を変更する直前に呼び出す。段順序、上流フェーズ完了、reopen pending、機能横断段の整合を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#spec-set) を参照する。

<a id="commit"></a>

### 4.2 commit

`commit` は、git commit の直前に呼び出す。承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。

`commit-preflight` は `commit` より前、利用者の commit 指示直後に呼び出す。現在の workflow action が commit operation に入ってよい状態かを read-only で判定し、stage や approval 作成に進んでよいかを返す。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit-preflight) を参照する。

<a id="push"></a>

### 4.3 push

`push` は、git push の直前に呼び出す。作業ツリーの clean 性、ローカル先行コミット数、push 先を検査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#push) を参照する。

<a id="audit-commit"></a>

### 4.4 audit-commit

`audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を監査する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#audit-commit) を参照する。

<a id="reopen-start"></a>

### 4.5 reopen-start

reopen 開始時は、上流正本変更の影響範囲を分類し、必要な reopen 手続き記録を作成してから通常ワークフローへ戻す。commit 時には、reopen 手続き記録と spec.json の recheck 状態の整合を検査する。詳細は [REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) と [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) を参照する。

<a id="reopen-advance-step"></a>

### 4.6 reopen-advance-step

`reopen-advance-step` は、reopen 第1過程または第2過程の完了を記録し、次の state へ進めるときに呼び出す。`--from-step` は現在の `step_number` と一致していなければならず、判断理由と証跡なしの更新は拒否する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-step) を参照する。

<a id="reopen-advance-gate"></a>

### 4.7 reopen-advance-gate

`reopen-advance-gate` は、reopen 第3過程で pending gate を 1 件完了扱いへ進めるときに呼び出す。対象 gate、判断、根拠、必要な `spec.json` 更新を構造化入力で受け取り、reopen 手続き記録の `pending_gates`、`completed_gates`、`downstream_impact_decisions`、`completed_steps` を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-advance-gate) を参照する。

<a id="reopen-set-blocker"></a>

### 4.8 reopen-set-blocker

`reopen-set-blocker` は、reopen 第3過程で pending gate の先頭が approval gate に到達し、human または proxy_model の承認待ちで停止するときに呼び出す。対象 gate、承認主体、理由、根拠を構造化入力で受け取り、`current_blocker` を構造化 object として設定する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-set-blocker) を参照する。

<a id="reopen-finalize"></a>

### 4.9 reopen-finalize

`reopen-finalize` は、reopen 第4過程で in-progress 手続き YAML を completed 側へ移すときに呼び出す。feature impact 判定、new feature 判定、影響 phase を構造化入力で受け取り、完了 YAML に必要な項目を機械更新する。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-finalize) を参照する。

## 5. 判定契約

終了コード：

- `0`：問題なし。処理続行可
- `1`：警告あり。呼び出し側の判断で続行可
- `2`：逸脱検出。呼び出し側は停止する

主要な判定対象：

- `spec-set` は、段順序、上流フェーズ完了、reopen pending、機能横断段の整合を検査する
- `commit-preflight` は、commit operation 入口で stage / approval 作成へ進んでよい workflow 状態かを検査する
- `commit-approval` は、staged exact index に束縛した nonce challenge、内容承認、実行代行承認、無効化を記録する
- `commit` は、承認レコード、post-write-verification 完了、reopen 手続き記録、持ち越し所見、staged ファイル分類、staged 文書のリンク整合を検査する
- `push` は、作業ツリーの clean 性、ローカル先行コミット数、commit 事前検査記録、push 先を検査する。`stages/in-progress/` が存在するだけでは遮断しない
- `audit-commit` は、指定 commit に含まれる post-write-verification 対象と completed manifest の対応を検査する
- `reopen-advance-step` は、現在 step と `--from-step` の一致、完了説明、判断理由、証跡を検査する
- `reopen-advance-gate` は、pending gate 文字列が review 系 gate の正規形であること、先頭の pending gate だけを完了扱いに進めること、根拠なし更新を検査する
- `reopen-set-blocker` は、pending gate 先頭の approval gate だけに、根拠つきの構造化 blocker を設定できることを検査する
- `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査する
- `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する

## 6. 出力とログ

既定出力は人間可読形式とし、少なくとも次を含める。

- 判定結果
- 対象サブコマンド
- 判定理由
- 必要な現在状態の要約

`--json` 指定時は、機械処理向けに同等の情報を構造化して出力する。

判定ログは JSON Lines 形式で記録する。既定パスは `.reviewcompass/runtime/logs/workflow-precheck.log` とし、`--log-path` で上書きできる。旧 `docs/logs/workflow-precheck.log` は legacy path として扱う。

## 7. テスト契約

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。

最低限、次の系統を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更の検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `reopen-advance-step`、`reopen-advance-gate`、`reopen-set-blocker`、`reopen-finalize` の構造更新と fail-closed 検査
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

## 8. 配置

主要ファイル：

- `tools/check-workflow-action.py`
- `tools/guarded-git-commit.py`
- `tests/tools/test_check_workflow_action.py`
- `docs/operations/WORKFLOW_PRECHECK.md`

補助モジュールを分割する場合は `tools/workflow_precheck/` 配下に置く。

## 9. 段階 1・段階 3 との接続

段階 1 は、不可逆操作の直前に本スクリプトを呼び出す。

- spec.json の `workflow_state` 変更直前：`spec-set`
- git commit 直前：`commit` または `guarded-git-commit.py`
- git push 直前：`push`

段階 3 の hook 連携は、同じ判定を実行環境側で自動発動する。導入時は人の明示承認を必須とする。


## docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# WORKFLOW_PRECHECK 詳細仕様

本文書は `tools/check-workflow-action.py`、`tools/commit-from-current-staged.py`、`tools/guarded-git-commit.py` の詳細仕様を定める。運用時に読む短い契約は [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md) を正とし、本書は実装・保守・テストで必要な詳細を補う。

## 1. サブコマンド

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit-preflight
tools/check-workflow-action.py commit-approval prepare --json
tools/check-workflow-action.py commit-approval record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]
tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin [--json]
tools/check-workflow-action.py commit-approval invalidate [--json]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
tools/check-workflow-action.py reopen-set-blocker --file <path> --gate stages/<phase>.yaml#approval --actor human|proxy_model --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
printf 'コミット\n' | tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
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

<a id="commit-preflight"></a>

### 3.0 commit-preflight

`commit-preflight` は、利用者が commit を指示した直後、stage / approval challenge / approval record / execution delegation record / guarded commit のいずれかを作る前に実行する read-only 入口検査である。

出力は少なくとも次を持つ。

- `verdict`: `OK` または `DEVIATION`
- `allowed_to_stage`
- `allowed_to_prepare_approval`
- `allowed_to_delegate_execution`
- `allowed_to_run_guarded_commit`
- `next_required_action`
- `reasons`
- `current_state.next_action`

判定順序：

1. `stages/in-progress/` がある場合、現在位置が構造化された reopen `commit_stop_point` かを確認する。
2. `commit_stop_point` でない reopen / maintenance / resume 途中状態なら `DEVIATION` とし、stage / approval 作成へ進まない。
3. ただし、本線 reopen 中に対応する `stages/completed/maintenance-*.yaml` が未コミット差分にあり、その `mainline_blocked_by` が全 in-progress reopen を覆う場合は、maintenance 完了 commit 候補として stage / approval 作成を許可する。この場合、本線 `stages/in-progress/reopen-*.yaml` は commit 対象に含めない。side-track 完了 commit のために本線 state を人工的に変更しない。
4. post-write-verification 対象の未完了変更がある場合は `DEVIATION` とし、stage / approval 作成へ進まない。
5. 通常 workflow の phase 終端停止点、reopen の構造化停止点、maintenance 完了 commit 候補では stage / approval 作成を許可する。
6. `allowed_to_run_guarded_commit` は、staged ファイルがあり、commit approval と execution delegation が現在の staged 内容に対して有効な場合だけ `true` にする。

`DEVIATION` の場合、LLM は stage、approval challenge、approval record、execution delegation record、guarded commit のいずれにも進まない。

### 3.1 commit-approval

`commit-approval` は、`commit-preflight` が commit 準備を許可した後、Git index への追加（`git add`）済みの staged exact index に束縛して approval 系 record を作る。

サブコマンド：

| サブコマンド | 役割 |
|---|---|
| `prepare --json` | staged exact index から nonce challenge を作る |
| `record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]` | nonce に対応する commit 内容承認を保存する |
| `delegate-execution --nonce <nonce> --source-text-stdin [--json]` | LLM による commit 実行代行承認を保存する |
| `invalidate [--json]` | challenge と承認レコードを無効化する |

`prepare` 後は staged index を変更しない。内容承認と実行代行承認は同じ nonce / target digest に束縛され、guarded commit で照合される。

### 3.2 commit

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

- commit 承認レコード（新配置 `.reviewcompass/runtime/approvals/commit-approval.json`、旧配置 `.reviewcompass/approvals/commit-approval.json`）が存在し、形式が正しく、未消費であること。読み取りは新→旧の順で解決する
- staged ファイルが `target_files` の範囲内であること
- LLM 実行時は `execution_delegation` があること
- staged ファイルに post-write-verification 対象がある場合、現在 sha256 を覆う completed manifest があること
- staged された `spec.json` に reopen 印がある場合、同じ commit に reopen 手続き記録が含まれること
- reopen 完了記録が含まれる場合、feature impact 判定、下流影響判定、影響フェーズ網羅が記録されていること
- 持ち越し所見の件数を確認し、未消化所見があれば警告すること
- staged ファイルを通常変更、要注意変更、危険変更に分類すること
- staged 文書の Markdown リンク、アンカー、既知の意味的組み合わせを `tools/document_link_lint.py` で検査すること

危険変更がある場合は逸脱とする。要注意変更は警告とする。

`tools/commit-from-current-staged.py` は、stdin 承認 1 行を検査してから `commit_approval.prepare()` を呼び、現在の staged exact index に束縛した challenge を作る。古い runtime approval/delegation は `prepare()` により invalidated になり、返された nonce は同じ process 内で `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` に渡す。stdin 承認文が空、UTF-8 でない、複数行、または許可文言外の場合は challenge 作成前に停止する。

`tools/guarded-git-commit.py` は `commit --execution-actor llm` を先に実行し、exit 2 なら commit しない。exit 1 は既定では停止し、人の判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、期限付き承認レコードは消費済みにする。

通常 workflow の `intent.approval` / `feature-partitioning.approval` 完了後の停止点は、`next --json` が `kind: commit_stop_point` として検出する。これらは `stages/in-progress/` を使わない通常 commit であるため、commit guard 側では特別な in-progress 例外を要求せず、通常どおり承認レコード、staged 範囲、post-write-verification、文書 lint を検査する。

通常の nonce challenge 付き commit 手順は、次の順序で逐次実行する。

1. `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行し、`OK` を確認する。
2. `git add ...` で対象を stage する。
3. `printf 'コミット\n' | .venv/bin/python3 tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"` を実行する。

低レベル手順として `commit-approval prepare` と `guarded-git-commit.py --approval-nonce` を直接使う場合も、`commit-approval prepare` と `commit --json` precheck を並列化しない。`prepare` 後の challenge は staged exact index と承認状態に束縛されるため、guarded commit 以外の承認系コマンドを挟まない。`--approval-source-text-line-stdin` を指定して空 stdin で実行すると challenge が invalidated になり得るため、非対話・空入力の実行形では使わない。

<a id="next"></a>

## 3-a. next

`next --json` は通常 workflow の次 action を返す前に、cross-feature phase 終端の未コミット変更を確認する。

判定：

- `intent.approval` が全 feature で `true` であり、`intent` phase の workflow_state または intent 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: intent` を返す
- `feature-partitioning.approval` が全 feature で `true` であり、`feature-partitioning` phase の workflow_state または feature-partitioning 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: feature-partitioning` を返す
- 対象 phase の終端変更が commit 済みで作業ツリーが clean な場合、停止点を返し続けず、次 phase の通常 action へ進む
- post-write-verification、lightweight self-check、reopen/maintenance/resume の in-progress は従来どおり通常 workflow の停止点判定より優先する

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
- ローカル先行 commit がある場合、HEAD に対応する commit 事前検査記録があること
- `origin/main` 以外への push が要求されていれば警告すること

作業ツリーが dirty の場合、HEAD の commit 事前検査記録がない場合、または deployable artifact の配置非依存 lint が失敗する場合は逸脱とする。`stages/in-progress/` が存在するだけでは push を遮断しない。in-progress は次 action 判定の状態であり、clean な作業ツリー上の push 済み候補 commit を危険にする直接条件ではない。

<a id="audit-commit"></a>

## 5. audit-commit

`audit-commit <commit-ish>` は、指定 commit の変更ファイルを読み、post-write-verification 対象だけを抽出する。

判定：

- 対象なし：OK
- 対象あり、commit 内ファイル内容 sha256 を覆う completed manifest がある：OK
- 対象あり、manifest がない、sha256 不一致、coverage matrix 不足、または未解決本質的指摘がある：逸脱
- `<commit-ish>` が解決できない：逸脱

この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。

<a id="reopen-advance-step"></a>

## 6. reopen-advance-step

`reopen-advance-step` は、reopen 手続きファイルの第1過程・第2過程を機械的に進める更新コマンドである。第1過程の完了では第2過程の正本修正へ進め、第2過程の完了では停止点コミット状態へ進める。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--from-step` | 必須 | 完了扱いにする過程番号。`1` または `2` |
| `--completed-step` | 必須 | `completed_steps` に追記する完了ステップ |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--from-step` は `1` または `2` のみを許可する
- 対象 YAML の `step_number` は `--from-step` と一致する必要がある。不一致は逸脱とする
- `--completed-step`、`--rationale`、`--evidence` が空の更新は逸脱とする
- `completed_steps` に `--completed-step` を追記する
- `reopen_step_records` に `from_step`、`completed_step`、`rationale`、`evidence` を追記する
- `--from-step 1` の成功時は `step_number: 2`、`next_step: 第2過程：正本修正`、`current_blocker: null` を保存する
- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: null`、`commit_stop_point: true`、`commit_stop_point_step: 2`、`commit_stop_point_kind: canonical_update_complete`、`commit_stop_point_reason: 第2過程の正本修正完了` を保存する
- commit guard は構造化された停止点だけを許可する。第2過程は `canonical_update_complete`、第3過程は `drafting_complete` または review 系 gate 完了（`triad_review_complete` / `review_wave_complete` / `alignment_complete` / `approval_complete`）、第4過程は implementation approval 完了の `approval_complete` を許可する。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-advance-gate"></a>

## 7. reopen-advance-gate

`reopen-advance-gate` は、reopen 手続きファイルの `pending_gates` を 1 件進める更新コマンドである。`spec-set` は in-progress reopen が存在する状態を通常作業として遮断するため、reopen 第3過程の gate 完了更新では本コマンドを使う。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 完了扱いにする gate。`pending_gates` 内と同じ文字列で指定する。標準の gate 文字列は `stages/<phase>.yaml#<stage>` 形式。例：`stages/requirements.yaml#alignment` |
| `--decision` | 必須 | 下流影響判断 |
| `--feature-scope` | 必須 | 判断対象の feature |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |
| `--set-spec` | 任意 | `FEATURE PHASE STAGE VALUE` の 4 値で `spec.json` も同時更新する。指定は 1 回のみ。`VALUE` は `true` または `false` |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate（`triad-review`／`review-wave`／`alignment`／`approval`）として解釈できる必要がある。壊れた gate 文字列や `drafting` gate が 1 件でもあれば逸脱とする
- `--evidence` が 1 件も無い更新は逸脱とする
- 完了した gate を `pending_gates` から除去し、`completed_gates` へ追加する
- `downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を追記する
- `--completed-step` があれば `completed_steps` へ追記する
- `--set-spec` があれば、対象 feature の `spec.json` の該当 workflow_state を同時更新する
- gate 完了後は `current_blocker` を `null` にする。本コマンドは approval gate の承認待ち blocker を新規作成しない
- 残る pending gate があれば `step_number: 3` を維持し、`next_step` を次 gate に更新する。無ければ `step_number: 4` と `next_step: 第4過程：完了` へ進める
- 完了した gate について、`commit_stop_point: true`、`commit_stop_point_step`、`commit_stop_point_kind`、`commit_stop_point_gate`、`commit_stop_point_reason` を保存する。kind は `triad-review` → `triad_review_complete`、`review-wave` → `review_wave_complete`、`alignment` → `alignment_complete`、`approval` → `approval_complete` とする。これにより requirements / design / tasks / implementation の各 review 系 gate 完了後を再開可能な停止点コミットとして扱う。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-set-blocker"></a>

## 8. reopen-set-blocker

`reopen-set-blocker` は、reopen 第3過程で approval gate の承認待ちに到達したとき、`current_blocker` を構造化して設定する更新コマンドである。承認待ちを自由記述で手編集する代わりに、対象 gate、承認主体、理由、根拠を機械可読に保存する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 承認待ちにする gate。`pending_gates` 先頭と同じ `stages/<phase>.yaml#approval` 形式 |
| `--actor` | 必須 | 承認主体。`human` または `proxy_model` |
| `--rationale` | 必須 | 承認待ちにする理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate として解釈できる必要がある
- `--gate` は `approval` gate でなければならない。`alignment` など approval 以外への blocker 設定は逸脱とする
- `--actor` は `human` または `proxy_model` のみを許可する
- `--rationale`、`--evidence` が空の更新は逸脱とする
- 成功時は `current_blocker` に `blocker_type: approval_gate`、`gate`、`actor`、`status: waiting_for_approval`、`rationale`、`evidence` を保存する
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-finalize"></a>

## 9. reopen-finalize

`reopen-finalize` は、reopen 第4過程で `stages/in-progress/` の手続き YAML を `stages/completed/` へ移す更新コマンドである。完了 YAML の必須項目を手編集で埋める代わりに、構造化引数から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases`、`completed_steps` を更新する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | `stages/in-progress/` 配下の reopen 手続き YAML |
| `--impacted-downstream-phase` | 必須 | `impacted_downstream_phases` に記録する phase。複数指定可 |
| `--feature-impact` | 必須 | `FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE` の 5 値で feature impact 判定を追加する。既存 feature すべてについて指定する |
| `--new-feature-decision` | 必須 | `DECISION RATIONALE EVIDENCE` の 3 値で new feature 判定を記録する |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- 対象 YAML は `stages/in-progress/` 配下でなければならない
- `step_number` は `4`、`pending_gates` は空、`current_blocker` は `null` でなければならない
- `--feature-impact` は既存 feature すべてを覆う必要がある
- feature impact の `decision`、`impact_basis`、`rationale`、`evidence` は commit 前検査の完了 YAML 検査と同じ条件で検査する
- `--new-feature-decision` は `decision`、`rationale`、`evidence` を必須とする
- `--impacted-downstream-phase` は既知 phase 名だけを許可する
- 成功時は `step_number: 4`、`next_step: 完了`、`pending_gates: []`、`current_blocker: null` を保存し、同名ファイルを `stages/completed/` へ作成して元の in-progress ファイルを削除する
- completed 側に同名ファイルが既にある場合は上書きせず DEVIATION とする
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="autonomous-plan"></a>
<a id="autonomous-plan-template"></a>
<a id="autonomous-plan-record-integration"></a>
<a id="autonomous-ledger-audit"></a>

## 10. autonomous-plan 系

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

## 11. 出力形式

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

## 12. ログ

判定ログは JSON Lines 形式で記録する。`--json` 出力と同等の構造に `timestamp` を追加する。

既定パス：

- `.reviewcompass/runtime/logs/workflow-precheck.log`（旧 `docs/logs/workflow-precheck.log` からの変更は
  2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。旧ログは凍結、読み取り互換は P3 まで）

`--log-path` でテスト用の隔離パスへ上書きできる。

### 12.1 実行時生成物の凍結期（P3 まで）の扱い

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

## 13. テスト観点

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `reopen-advance-step` の第1・第2過程更新、根拠なし更新拒否、現在 step 不一致拒否
- `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
- `reopen-set-blocker` の構造化 blocker 設定、非先頭 gate 拒否、非 approval gate 拒否、根拠なし更新拒否
- `reopen-finalize` の完了 YAML 生成、in-progress 削除、第4過程未到達と feature impact 不足の拒否
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。

