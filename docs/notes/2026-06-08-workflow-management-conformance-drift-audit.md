# workflow-management 仕様・実装乖離監査

作成日：2026-06-08

## 0. 位置づけ

本メモは、`docs/notes/2026-06-08-conformance-drift-audit-process.md` で定義した初回テストケースとして、`workflow-management` を対象に実施した read-only の仕様・実装乖離監査である。

この監査は `conformance-evaluation` 本格実装前の手作業テストケースであり、仕様や実装を修正するものではない。差分分類後、どの項目を requirements / design / operations / tests / carry-forward に戻すかは別途判断する。

## 1. 監査範囲

対象仕様：

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`（参考）

対象実装：

- `tools/check-workflow-action.py`
- `tools/guarded-git-commit.py`

対象テスト：

- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_guarded_git_commit.py`
- `tests/tools/test_workflow_management_implementation_drafting.py`
- `tests/tools/test_workflow_management_implementation_triad_prep.py`

関連運用文書：

- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/WORKFLOW_NAVIGATION.md`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
- `docs/disciplines/discipline_post_write_verification.md`

## 2. コード由来設計スケッチ

本節の契約は、主に `tools/check-workflow-action.py` の argparse / helper 群、`tools/guarded-git-commit.py` の wrapper 実装、`tests/tools/test_check_workflow_action.py`、`tests/tools/test_guarded_git_commit.py` から観測した。後続の自動化では、ここで列挙した契約ごとに evidence refs を構造化する必要がある。

### 2.1 公開 subcommand

`tools/check-workflow-action.py` は、少なくとも次の subcommand を実装している。

- `spec-set`
- `commit`
- `push`
- `next`
- `reopen-start`
- `audit-commit`
- `autonomous-plan`
- `autonomous-plan-template`
- `autonomous-plan-record-integration`
- `autonomous-ledger-audit`

`tools/guarded-git-commit.py` は、`tools/check-workflow-action.py commit` を通してから `git commit` を行う薄い wrapper として実装されている。commit 成功後に `.reviewcompass/approvals/commit-approval.json` を消費済みにし、`.git/reviewcompass/last-commit-precheck.json` に push 用の直前 commit 検査記録を残す。

証拠参照：

- `tools/check-workflow-action.py` の argparse 定義
- `tools/guarded-git-commit.py`
- `tests/tools/test_guarded_git_commit.py`

### 2.2 判定出力

`check-workflow-action.py` は主に次の出力契約を持つ。

- `verdict`: `OK` / `WARN` / `DEVIATION`
- `exit_code`: `0` / `1` / `2`
- `reasons`
- `current_state`
- `next_action`（`next` 系）
- `required_disciplines`
- `required_inputs`

`--json` 指定時は JSON を出力する。未指定時は人間可読出力を返す。

### 2.3 spec-set 契約

`spec-set` は、`spec.json` の `workflow_state` 変更前に依存関係と完了述語を検査する。

コードとテストから観測できる完了述語：

- `file_exists`
- `artifact_exists`
- `artifact_exists_and_sections_present`
- `artifact_exists_and_sections_present_and_author_reviewer_distinct`
- `all_features_drafting_and_triad_review_completed`
- `cross_spec_alignment_passed`
- `explicit_human_approval_recorded`
- `depends_on_resolves_correctly`

主な fail-closed 条件：

- `stages/in-progress/` が非空である。
- 上流 phase の `approval` が false のまま下流 phase の `drafting` を true にする。
- 前段 stage が false のまま後段 stage を true にする。
- 必須 artifact が存在しない。
- 必須 section が存在しない。
- author / reviewer が同一 identity である。
- alignment report が pass でない、または unresolved findings が 0 でない。
- approval record が存在しない。
- `depends_on` に `hard` / `review` 以外の依存種別がある。

true から false への変更は reopen 警告として `WARN` を返す。

証拠参照：

- `tests/tools/test_check_workflow_action.py` の `SpecSetExitCodeTests`
- `tests/tools/test_check_workflow_action.py` の `SpecSetOutputTests`
- `tests/tools/test_check_workflow_action.py` の `SpecSetArgumentValidationTests`

### 2.4 next 契約

`next` は通常 workflow の次段だけでなく、通常 workflow より優先すべき状態を返す。

観測できる priority model：

1. post-write-verification 対象の未コミット変更
2. post-write pending 中の policy violation
3. post-write manifest の未解決本質的指摘
4. maintenance / reopen / resume の in-progress
5. 通常 workflow の stage / cross_feature_stage
6. completed

`next_action.kind` として観測できるもの：

- `post_write_verification`
- `post_write_policy_violation`
- `post_write_human_decision_required`
- `maintenance_in_progress`
- `reopen_in_progress`
- `resume_in_progress`
- `stage`
- `cross_feature_stage`
- `completed`

`next` は `required_disciplines` と `required_inputs` を付与し、triad-review 前には対象仕様文書と review-run 成果物、review-wave 前には carry-forward register の未解決件数などを返す。

証拠参照：

- `tools/check-workflow-action.py` の `cmd_next`
- `tests/tools/test_check_workflow_action.py` の `NextNavigationTests`

### 2.5 post-write verification 契約

post-write 対象は、少なくとも次を含む。

- `TODO_NEXT_SESSION.md`
- `docs/experiments/`
- `docs/logs/autonomous-parallel/`
- `docs/notes/`
- `docs/operations/`
- `docs/plan/`
- `docs/reviews/*audit*.md`
- `docs/reviews/reopen-classification-*.md`
- `docs/workflow-evidence/`
- `docs/disciplines/`（単独変更時）

対象外として観測できるもの：

- `.reviewcompass/specs/`
- `docs/archive/`
- 通常 review 記録としての `docs/reviews/*impl-triad-review.md`
- `docs/reviews/audit-summary.md`

完了 manifest の契約：

- `status: completed`
- `target_files` が現在の対象を覆う。
- `target_sha256` が現在の対象ファイル内容と一致する。
- `required_verifiers` が非空である。
- `completed_verifiers` または `verifications[]` が必要な検証者を満たす。
- `unresolved_substantive_findings: 0`
- `review_run` 宣言がある場合は raw / rounds / triage / summary の traceability が揃う。

`verifications[]` がある場合は、各 verifier が全 target files を見ており、かつ per-entry `target_sha256` が manifest 最上位の `target_sha256` と一致する必要がある。検証者ごとの分業は完了扱いされない。

post-write pending 中の禁止混在として、少なくとも次が遮断される。

- 新規検証 runner の作成
- `templates/` 変更
- 他の post-write 対象と混在した `docs/disciplines/` 変更

証拠参照：

- `tools/check-workflow-action.py` の post-write manifest / target 判定 helper 群
- `tests/tools/test_check_workflow_action.py` の `NextNavigationTests`
- `tests/tools/test_check_workflow_action.py` の `PostWriteCoverageMatrixTests`
- `tests/tools/test_check_workflow_action.py` の `PostWriteReviewRunTraceabilityTests`
- `tests/tools/test_check_workflow_action.py` の `PostWriteReviewRunEndToEndTests`

### 2.6 commit / push 契約

`commit` の主な契約：

- `--rationale` 必須。
- `stages/in-progress/` が非空なら `DEVIATION`。
- carry-forward register に未解決所見があれば `WARN`。
- `spec.json` 変更は `WARN`。
- `docs/plan/` 変更は `WARN`。
- credentials など危険ファイル名は `DEVIATION`。
- `.reviewcompass/approvals/commit-approval.json` が必須。
- approval record は未消費である必要がある。
- approval record の `target_files` が staged files を覆う必要がある。
- approval record の `target_sha256` が staged 内容と一致する必要がある。
- staged files に post-write 対象が含まれる場合、現在内容を覆う completed manifest が必須。

`guarded-git-commit.py` は、commit 成功後に approval record を消費済みにし、push 用に `.git/reviewcompass/last-commit-precheck.json` を記録する。

`push` の主な契約：

- `--rationale` 必須。
- `stages/in-progress/` が非空なら `DEVIATION`。
- 作業ツリーが dirty なら `DEVIATION`。
- origin に対する ahead commit がある場合、HEAD と一致する last commit precheck record が必要。

`audit-commit` の主な契約：

- 指定 commit に post-write 対象が含まれ、対応する manifest がなければ `DEVIATION`。
- root commit も監査対象に含める。
- 対応 manifest があれば `OK`。

証拠参照：

- `tools/check-workflow-action.py` の commit / push / audit-commit helper 群
- `tools/guarded-git-commit.py`
- `tests/tools/test_check_workflow_action.py` の `CommitExitCodeTests`
- `tests/tools/test_check_workflow_action.py` の `PushExitCodeTests`
- `tests/tools/test_check_workflow_action.py` の `AuditCommitTests`
- `tests/tools/test_check_workflow_action.py` の `CommitPushOutputTests`
- `tests/tools/test_guarded_git_commit.py`

### 2.7 autonomous / parallel 契約

`autonomous-plan` は自律・並列実行計画を検査し、正常時に `docs/logs/autonomous-parallel/<run_id>.yaml` へ履歴台帳を書き出す。

観測できる必須要素：

- `mode: autonomous_parallel`
- `authorization.approval_record_path`
- `authorization.summary_presented_to_user`
- `authorization.triage_presented_to_user`
- `tasks[].task_id`
- `tasks[].source_finding_ids`
- `tasks[].assignee`
- `tasks[].allowed_paths`
- `tasks[].forbidden_paths`
- `tasks[].expected_tests`
- `tasks[].stop_conditions` に `important_decision_requires_approval`
- `execution_evidence`
- `integration_gate.requires_main_session_review`
- `integration_gate.requires_diff_scope_check`
- `integration_gate.requires_tests`
- `integration_gate.requires_decision_basis_review`
- `history.ledger_path`
- `outputs_policy`

主な遮断条件：

- authorization 欠落
- subthread 実装なのに separate worktree でない
- 依存関係のない並列 task の allowed paths が overlap
- raw / triage 証跡欠落
- triage に `human_required` が残る
- main session / same worktree の並列 write が output-only 境界なし
- integration gate 欠落
- history 欠落

`autonomous-plan-record-integration` は既存 ledger に integration result を追記する。`autonomous-ledger-audit` は plan file なしでも ledger 単独から実行後 snapshot と integration result を検査する。

証拠参照：

- `tools/check-workflow-action.py` の autonomous-plan / ledger helper 群
- `tests/tools/test_check_workflow_action.py` の `AutonomousParallelPlanTests`

## 3. 仕様照合

### 3.1 requirements conformance

| Criterion | 状態 | 所見 |
|---|---|---|
| 受け入れ基準と実装の対応 | 部分一致 | Requirement 1〜8 の中核は実装されている。ただし `next`、post-write manifest、commit approval SHA、audit-commit、autonomous ledger など、後続で追加された受け入れ契約が requirements に十分には出ていない。 |
| API / データ契約と実装の対応 | 部分一致 | `spec-set` / `commit` / `push` は design にあるが、実装上の subcommand は増えている。post-write manifest、commit approval record、last-commit-precheck、autonomous plan / ledger の field 契約は operations / tests にはあるが、requirements の中核契約としては薄い。 |
| 例外系・境界条件と実装の対応 | 部分一致 | fail-closed 方針は requirements にあるが、実装は post-write policy violation、manifest hash mismatch、coverage matrix 欠落、review_run traceability 欠落、root commit audit など具体的な境界条件を追加している。 |

### 3.2 design conformance

| Criterion | 状態 | 所見 |
|---|---|---|
| モジュール構成・データモデルと実装の対応 | 部分一致 | design は `tools/check-workflow-action.py` を中心に据えるが、実装は `guarded-git-commit.py`、post-write manifest、approval record、autonomous ledger、review-run traceability へ広がっている。 |
| 接合面（API シグネチャ・エラーモデル）と実装の対応 | 部分一致 | exit code と `--json` は設計されているが、`next` の `next_action.kind`、`required_disciplines`、`required_inputs`、post-write / maintenance / reopen priority model は実装と運用文書側で具体化されている。 |
| アルゴリズム・性能達成手段と実装の対応 | 部分一致 | 段集合 YAML と spec.json の走査は設計どおり。追加で、git status から post-write 対象を検出し、manifest をファイル名降順で評価し、sha256 と coverage matrix を照合する実装上の判断が入っている。 |

## 4. 差分分類

| ID | 分類 | 対象 | 差分 | 推奨扱い |
|---|---|---|---|---|
| WM-DRIFT-001 | `spec-missing` | requirements / design | `next` subcommand が通常 workflow navigation の正本入口になっているが、requirements の受入基準では明示的な中核契約になっていない。 | requirements に「現在位置判定 / next_action 生成」を追加する候補。 |
| WM-DRIFT-002 | `spec-missing` | requirements / design | post-write verification の対象検出、manifest 完了判定、hash 照合、human decision required、policy violation が実装契約化されている。 | requirements または workflow-management design に post-write side track 契約として戻す候補。D-027 と接続。 |
| WM-DRIFT-003 | `spec-missing` | requirements / design | `verifications[]` coverage matrix により、各 verifier が全 target files と sha256 を覆うことを要求している。 | post-write manifest schema / workflow-management design に戻す候補。 |
| WM-DRIFT-004 | `spec-missing` | requirements / design | `review_run` 宣言付き manifest では raw / rounds / triage / summary の traceability を検査する。 | D-003 / D-006 / D-012 と接続し、review-run evidence pointer 契約として戻す候補。 |
| WM-DRIFT-005 | `spec-missing` | requirements / design | commit approval record が `target_files` だけでなく `target_sha256` を要求し、staged 内容との一致を検査している。 | commit approval contract として requirements / operations の対応を確認し、必要なら requirements へ昇格。 |
| WM-DRIFT-006 | `spec-missing` | requirements / design | `guarded-git-commit.py` が commit 後に approval record を consume し、`.git/reviewcompass/last-commit-precheck.json` を保存する。 | wrapper / push precheck 接続として design に明記する候補。 |
| WM-DRIFT-007 | `spec-missing` | requirements / design | `audit-commit` が commit 済み post-write 対象を遡及監査し、root commit も対象にする。 | operations には詳しいが requirements の中核契約としては薄い。commit/push guard 強化候補 D-014 と接続。 |
| WM-DRIFT-008 | `spec-missing` | requirements / design | `autonomous-plan`、template、record-integration、ledger-audit が実装され、authorization / evidence / integration / history / output policy の schema 的契約を持つ。 | requirements に自律・並列実行 ledger 契約を追加する候補。D-007 と接続。 |
| WM-DRIFT-009 | `mismatch` | requirements / design | Requirement 2 は主に「証跡ファイル存在＋必須節充足」と述べるが、実装は post-write、commit approval、review_run traceability、autonomous ledger など、内容構造と sha256 を深く検査している。 | 「段完了判定は軽量、不可逆操作 / side track guard は構造検査あり」と責務を分けて明文化する候補。 |
| WM-DRIFT-010 | `implementation-detail` | design | manifest ファイル名の辞書順降順で最新を優先する実装詳細。 | operations に留めるか、manifest 選択規則として仕様化するか判断。 |
| WM-DRIFT-011 | `implementation-detail` | design | post-write 対象 path の詳細 matrix。 | path policy は運用文書 / discipline 正本に置き、requirements には「対象範囲は動作仕様に従う」とする案が自然。 |
| WM-DRIFT-012 | `needs-user-decision` | requirements / design | `docs/logs/autonomous-parallel/` が post-write 対象に含まれている一方、autonomous-plan が ledger をそこへ自動生成する。現状はテスト上成立しているが、生成 ledger 自体の post-write 対象性をどう扱うかは整理余地がある。 | D-007 で ledger の監査単位と post-write 対象性を再整理。 |

## 5. 初回監査から見えた conformance-evaluation 本格実装への示唆

### 5.1 コードから抽出すべき contract field

workflow-management では、単なる関数一覧ではなく、次の contract field を抽出できる必要がある。

- subcommand
- required arguments
- optional arguments
- output fields
- exit code
- files read
- files written
- state priority
- fail-closed conditions
- warning conditions
- manifest schema
- approval schema
- ledger schema
- evidence refs
- hash / traceability requirements
- test-backed boundary cases

### 5.2 差分分類として必要な列

今回の手作業では、少なくとも次の列が有効だった。

- finding id
- difference class
- affected spec layer
- implementation evidence
- existing spec evidence
- severity
- recommended disposition
- related future candidate id

### 5.3 自動推定の限界

コードから subcommand や引数、ファイル読み書き、schema field、exit code は抽出しやすい。一方で、次は人間判断が必要である。

- 追加実装を requirements に昇格すべきか、operations に留めるべきか。
- post-write / autonomous / audit-commit を workflow-management の中核要件とするか、D-007 / D-027 などの後続改善候補に寄せるか。
- 「軽量版検査」という設計思想と、実装済みの構造検査強化をどう両立して記述するか。

## 6. 現時点の判断

初回監査では、重大な `code-missing` は確認していない。むしろ、実装が requirements / design より進んでおり、`spec-missing` と `mismatch` が中心である。

特に、post-write verification、commit approval SHA、review-run traceability、autonomous ledger、`next` navigation は、現行コードとテストで強く契約化されている。これらは単なる内部詳細ではなく、ReviewCompass の運用安全性に関わるため、少なくとも requirements / design / operations のどこを正本にするかを決める必要がある。

この監査結果は、全 7 feature 監査へ展開する前に、conformance-evaluation の期待出力例として利用できる。
