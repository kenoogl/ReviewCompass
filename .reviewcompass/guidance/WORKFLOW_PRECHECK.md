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
- `work-backlog start-checklist`：backlog TODO から runtime checklist を作成する状態変更

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
tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
tools/check-workflow-action.py work-backlog start-checklist --id <todo-id> --mutation-boundary-confirmed
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

commit は人の職掌範囲である。利用者が commit を指示した直後は、Git index への追加（`git add`）、commit approval challenge、approval record、execution delegation record、guarded commit のいずれを作る前にも、まず `commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、commit できない理由、何も作らず止めたこと、次に許可されている workflow action だけを短く報告する。利用者の単発 commit 指示は staged 内容承認と LLM commit 実行代行承認として扱える。`--execution-actor llm` の場合も、この直近の利用者発話を実行代行の明示承認の出典にできるが、LLM が利用者発話なしに承認文を生成してはならない。実行時は直接 `git commit` ではなく、原則として `tools/commit-from-current-staged.py` を使う。

`tools/commit-from-current-staged.py` は approval 作成前に `commit-preflight --json` を実行し、`DEVIATION` の場合は承認入力や challenge 作成に進まず停止する。preflight 通過後は TTY からの対話的な承認 1 行を必須とし、pipe / heredoc / redirect など非 TTY 入力、空入力、許可文言外の入力なら challenge 作成前に停止する。承認 1 行は直近の利用者発話または利用者による対話入力に限る。利用者の単発 commit 指示を転送する場合、その 1 行を staged 内容承認と LLM commit 実行代行承認の source として記録する。LLM が `printf` 等で生成して渡してはならず、LLM が利用者発話なしに承認文を生成してはならない。承認文を確認した後、古い runtime approval/delegation を無効化し、現在の staged exact index の digest で challenge を作り、同一プロセス内で approval / execution delegation を記録してから `tools/guarded-git-commit.py` を呼び出す。これにより、古い approval の残存、nonce の手写し、challenge 作成後の別操作、空 stdin 実行、LLM 生成承認文の混入を標準導線から外す。会話出力を最小化する場合は `--progress-format json` を使い、`preflight_ok`、`guarded_commit_running`、`commit_completed` などの状態語だけを利用者へ伝える。

nonce 方式の commit approval を低レベル手順として使う場合、commit 準備は逐次手順として扱う。stage 後に `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を実行し、返された nonce で `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を起動する。`commit-approval prepare` と `commit --json` precheck を並列に実行しない。challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まず、guarded commit に直近の利用者発話で明示された commit 指示を 1 行として渡す。`--approval-source-text-line-stdin` は TTY からの対話入力だけを受け付け、空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行してはいけない。

Codex の `workspace-write` sandbox では、`commit-from-current-staged.py` または `guarded-git-commit.py` が最終的に `.git/index.lock` へ書き込む段階で sandbox に拒否され得る。このため Codex から commit を実行する場合は、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

commit 実行時のユーザー向け報告は、guard や precheck の詳細出力をそのまま貼らず、結論だけを短く伝える。成功時は commit hash と commit message、必要なら検証コマンドだけを報告する。失敗時は停止理由を 1〜3 点に要約し、承認再作成、staged 対象の見直し、post-write 未完了など、次に必要な操作だけを示す。詳細ログは必要時に参照できる状態に留め、通常の進行報告には含めない。

mutation boundary は、利用者指示の語義ではなく、次に実行する操作が状態変更かどうかで判定する。runtime checklist 作成のような小さな状態変更でも、確認済みであることを示す機械入力なしに実行してはならない。`work-backlog start-checklist` は `--mutation-boundary-confirmed` がない場合に `DEVIATION` で停止し、runtime checklist を作成しない。

### 4.0.1 work-backlog plan materialization

backlog plan の `implementation_plan` は、実行可能な slice の候補一覧であり、plan 全体がそのまま TODO / checklist 化済みであることを意味しない。plan の一部だけを TODO 化した場合は、plan item に `execution_slices` を置き、各 slice の materialization 状態を明示する。

`execution_slices` の各 entry は、少なくとも次を持つ。

- `phase_id`：`implementation_plan[].id` と一致する slice ID
- `title`：対象 slice の題名
- `status`：materialization 状態
- `todo_id`：対応する backlog TODO ID。未展開なら `null`
- `checklist_id`：対応する runtime / evidence checklist ID。未生成なら `null`

必要に応じて次を持つ。

- `todo_path`：対応 TODO の path
- `checklist_evidence_path`：完了済み checklist evidence の path
- `note`：後追い接続、defer、not required などの判断理由

`status` は次の意味で使う。

- `not_materialized`：slice はまだ TODO 化されていない。`todo_id` と `checklist_id` は `null`
- `todo_created`：slice に対応する TODO はあるが、checklist は未生成
- `checklist_started`：runtime checklist が生成され、作業中または未完了
- `evidence_recorded`：checklist evidence があり、完了判定前の証跡が残っている
- `completed`：slice の TODO / checklist / evidence が完了している
- `deferred`：明示判断により後回し。`note` に理由を残す
- `not_required`：明示判断により TODO 化不要。`note` に理由を残す

`source_plan_id`、`source_plan_path`、`source_plan_slice.phase_id` を持つ TODO は、該当 plan slice の materialization record と対応しなければならない。runtime / evidence checklist は `source_backlog_item_id` で TODO に接続する。監査では、plan の `implementation_plan[].id`、`execution_slices[].phase_id`、TODO の `source_plan_slice.phase_id`、checklist の `source_backlog_item_id` を突き合わせる。

runtime checklist は作業中の live state であり、`status: active` / `pending` / `blocked` を含む進捗は `.reviewcompass/runtime/work-units/checklists/` に置く。evidence checklist は完了後の固定証跡であり、`.reviewcompass/evidence/work-units/checklists/` 配下に置ける checklist は `status: completed`、`completed_at`、`completion_summary` を持つものだけである。

plan の `checklist_evidence_path` と TODO の `execution_history[].evidence_path` は、完了済み evidence checklist だけを指す。未完了 checklist を evidence path として参照してはならない。active checklist が evidence 配下に紛れた場合は逸脱であり、`work-checklist audit-evidence` と `work-backlog audit-plan-todo-bridge` / `audit-checklist-bridge` で検出し、必要に応じて `work-backlog repair-active-checklist-evidence` で runtime へ戻す。

一部 slice の `completed` は plan 全体の完了を意味しない。全体完了は、全 slice が `completed`、`deferred`、`not_required` のいずれかであり、`deferred` / `not_required` に理由がある場合だけ扱える。未登録の `implementation_plan` slice は `not_materialized` 相当として扱う。

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

`audit-commit` が逸脱を返した場合、呼び出し側は push へ進まない。commit 済み変更に未解決の post-write-verification 不整合が残っているものとして扱い、補正 commit または必要な post-write-verification の再実施に戻る。未解決の本質的指摘が 0 件であることを示す completed manifest が、対象 commit の post-write-verification 対象全体を覆うまで、audit 済みとして扱わない。

<a id="reopen-start"></a>

### 4.5 reopen-start

reopen 開始時は、上流正本変更の影響範囲を分類し、必要な reopen 手続き記録を作成してから通常ワークフローへ戻す。正本本文を実質編集する phase が分かっている場合は `--edited-phase` を指定し、`edited_phases` と下流確認対象を in-progress 記録に初期化する。commit 時には、reopen 手続き記録と spec.json の recheck 状態の整合を検査する。詳細は [REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) と [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-start) を参照する。

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

`reopen-finalize` は、reopen 第4過程で in-progress 手続き YAML を completed 側へ移すときに呼び出す。feature impact 判定、new feature 判定、影響 phase を構造化入力で受け取り、完了 YAML に必要な項目を機械更新する。対象 feature の `spec.json` が存在する場合は recheck クリアと第4過程完了履歴の追加も同じ操作で行う。詳細は [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#reopen-finalize) を参照する。

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
- `reopen-finalize` は、第4過程到達、pending gate 空、blocker なし、全 feature の impact 判定を検査し、対象 feature の recheck クリアと第4過程完了履歴追加を一括で行う
- `autonomous-plan` は、承認、作業境界、停止条件、統合ゲート、履歴台帳方針を検査する
- `autonomous-plan-template` は、既存 review-run から自律・並列実行計画テンプレートを生成する
- `autonomous-plan-record-integration` は、統合結果の状態、検証、判断を履歴台帳へ記録する
- `commit-from-current-staged.py` は、現在の staged index に束縛した approval 作成と guarded commit を同一導線で連続実行する
- `guarded-git-commit.py` は、commit 前検査と approval 照合を通した場合だけ git commit を実行する
- `work-backlog start-checklist` は、mutation boundary 確認済みの場合だけ backlog TODO から runtime checklist を作成する

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
- `.reviewcompass/guidance/WORKFLOW_PRECHECK.md`

補助モジュールを分割する場合は `tools/workflow_precheck/` 配下に置く。

## 9. 段階 1・段階 3 との接続

段階 1 は、不可逆操作の直前に本スクリプトを呼び出す。

- spec.json の `workflow_state` 変更直前：`spec-set`
- git commit 直前：`commit` または `guarded-git-commit.py`
- git push 直前：`push`

段階 3 の hook 連携は、同じ判定を実行環境側で自動発動する。導入時は人の明示承認を必須とする。
