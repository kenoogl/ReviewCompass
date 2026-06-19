# workflow-management implementation drafting 棚卸し

## 目的

workflow-management implementation.drafting の現時点の実装状況を、後続の triad-review と利用者判断で追えるようにする。

今回のターゲットは、自律・並列実行をできるだけ人の承認なしで進め、事後に履歴を確認できるようにすることである。不可逆操作である commit、push、spec.json 更新、フェーズ移行は引き続き人間の明示承認を要求する。

## 実装済み

### 自律・並列実行計画ガード

`tools/check-workflow-action.py autonomous-plan <plan.yaml>` を実装済み。

検査内容：

- `mode: autonomous_parallel` と `run_id`
- 人間または `proxy_model` の承認記録
- レビュー結果サマリと三段階トリアージの提示済みフラグ
- task ごとの `source_finding_ids`、担当、許可パス、期待テスト、停止条件
- 別スレッドまたはサブ担当の `separate_worktree`
- 依存関係のない並列 task の `allowed_paths` 衝突
- 統合ゲート
- 生成物分類
- 履歴台帳設定

### 自律・並列実行計画テンプレート

`tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>` を実装済み。

生成される YAML は `autonomous-plan` の必須フィールドを満たし、そのまま検査可能である。実作業では、生成後に `tasks[]` の `source_finding_ids`、`allowed_paths`、`expected_tests` を実対象へ差し替える。

### 自律・並列実行履歴台帳

`autonomous-plan` 実行時に `docs/logs/autonomous-parallel/<run-id>.yaml` へ履歴台帳を書き出す。

台帳には、`run_id`、verdict、reasons、task IDs、承認根拠、統合ゲート、出力分類、current_state を記録する。

デプロイ後監査では plan ファイルが残らない可能性があるため、ledger を事後監査の正本とする。`autonomous-plan` は `execution_evidence_snapshot` を ledger に保存し、`completed_tasks`、`parallelized_operations`、`human_required_count` を plan なしで確認できるようにする。既存 ledger に snapshot がある場合、古い plan の再実行では snapshot を巻き戻さない。

`tools/check-workflow-action.py autonomous-ledger-audit <ledger.yaml>` を実装済み。これは plan ファイルなしで、ledger の `mode`、verdict、`execution_evidence_snapshot`、`integration_result` を検査する。

### 統合結果追記

`tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"` を実装済み。

統合後に既存台帳へ `integration_result` を追記し、次を後から確認できる。

- 統合状態：`completed`、`blocked`、`rejected`
- 実行したテストまたは未実行理由
- メインセッション LLM の統合判断

`tools/api_providers/review_triage.py assert-review-report-ready` は、`integration_result` だけでなく `execution_evidence_snapshot` も要求する。これにより、自動実行報告の ready 判定は plan に依存せず、ledger 単独で監査可能な状態を前提にする。

### 正本仕様

`docs/operations/WORKFLOW_PRECHECK.md` に、次のサブコマンド仕様を追記済み。

- `autonomous-plan`
- `autonomous-plan-template`
- `autonomous-plan-record-integration`

## 未充足

workflow-management 全体の T-001〜T-011 は、まだ一括完了ではない。

現時点で特に残る事項：

- T-001〜T-003：`stages/` 配下の 9 ファイル体制と stage schema の実装は未完了部分がある。
- T-005：front-matter checker の独立モジュール化は未完了。
- T-006：不可逆操作ゲートは commit/push/spec-set を中心に実装済みだが、設計上の 4 種類すべてを専用モジュールへ分離する作業は未完了。
- T-007：reopen resolver の専用モジュール化は未完了。ただし `reopen-start` と `next` による進行中ファイル処理は部分実装済み。
- T-008：in-progress manager の専用モジュール化は未完了。ただし `next` は in-progress を優先して読める。
- T-009〜T-011：運用文書、規律変更接合面、統合テスト全体は未完了事項が残る。

今回の実装は、T-004 の検査スクリプト本体と、自律・並列実行を安全に始めて履歴を残すための追加ガードに集中している。

## 2026-06-08 tasks 再確認への対応

intent の「レビュー収集処理を事前設定の写像にしない」意図に伴い、workflow-management tasks.md の変更を implementation 観点で再確認した。

- T-004 の `next` による上流更新再展開は、`tools/check-workflow-action.py next --json` と `tests/tools/test_check_workflow_action.py` の upstream recheck 系テストで受けられている
- 2026-06-08 の reopen 判定修正により、完了済み workflow の上流正本更新は `upstream_recheck` ではなく `reopen_classification_required` として返す。`tools/check-workflow-action.py` と `tests/tools/test_check_workflow_action.py` は intent → feature-partitioning、requirements → design、tasks → implementation の代表経路を検証する
- T-006 の不可逆操作直前ゲートは、`tools/check-workflow-action.py` の commit／push／spec-set／phase-transition 系検査と `tests/tools/test_check_workflow_action.py` で受けられている
- T-008 の session 跨ぎ状態管理は、`stages/in-progress/` 優先判定、maintenance side track 判定、post-write pending 判定として `tools/check-workflow-action.py` と `tests/tools/test_check_workflow_action.py` で受けられている
- T-002 の機能依存マップ一元化は、`stages/feature-dependency.yaml` の `feature_order`／`depends_on` 参照と `tests/tools/test_check_workflow_action.py` で受けられている

確認結果として、実装済み workflow-management は次作業を事前設定の写像として固定せず、現在の成果物・進行中状態・post-write manifest・機能依存マップを読み直して `next_action` を機械判定している。完了済み workflow の上流正本更新は reopen 分類へ送るよう修正済みである。

## 2026-06-09 後追い intent 下流再展開への対応

追加 intent を既存システムに適用する今回の reopen では、workflow-management は CE の差分候補を実行命令として直接適用せず、reopen 手続きの候補として受け取る。

実装確認結果：

- `tools/check-workflow-action.py` は、`pending_gates` が triad-review を指していても `drafting_completed_gates` または `completed_gates` に該当 phase の drafting がなければ `run_reopen_drafting` を返す
- `tests/tools/test_check_workflow_action.py` の `test_next_reopen_requires_drafting_before_triad_review` がこの逸脱防止を検査する
- reopen 完了時の `downstream_impact_decisions` coverage 検査は、完了 gate の判断記録欠落を遮断する
- CE T-016 の出力は `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-post-hoc-intent-diff.md` に記録され、workflow-management はそのうち `downstream_impact_candidate` を reopen 判断として扱う

今回、workflow-management の追加コード変更は不要と判断した。理由は、tasks 段までで追加した Requirement 9 / XDI-WM-002 の実装上の受け皿が既に `next`、reopen in-progress state、完了時 coverage 検査に存在するためである。

### Requirement 9 / XDI-WM-002 実装対応表

| 要素 | 実装 | テスト |
| --- | --- | --- |
| 後追い intent の reopen 進行中状態を優先する | `tools/check-workflow-action.py:build_in_progress_next_action` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reads_reopen_in_progress_next_step` |
| triad-review の前に drafting を要求する | `tools/check-workflow-action.py:_resolve_reopen_next_gate` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reopen_requires_drafting_before_triad_review` |
| 全 feature scope を feature impact decisions から返す | `tools/check-workflow-action.py:reopen_feature_scope_from_data` | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_reopen_uses_feature_impact_decisions_as_review_scope` |
| 完了済み gate も downstream decision で覆う | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_blocks_completed_reopen_missing_completed_gate_decision` |
| downstream decision があれば reopen 完了 commit を許可する | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_allows_completed_reopen_with_completed_gate_decisions` |
| 影響 phase を gate 判断で覆る | `tools/check-workflow-action.py:validate_reopen_completion_impact_decisions` | `tests/tools/test_check_workflow_action.py::CommitExitCodeTests::test_commit_blocks_completed_reopen_when_impacted_phase_is_uncovered` |

CE T-016 の試行結果は、WM が直接ファイルへ自動反映する入力ではない。WM は CE 候補を受け、reopen の各 gate で `downstream_impact_decisions` に人間または承認済み判断を記録する。これにより、候補抽出と正式な workflow 遷移を分離する。

追加で、drafting-before-review の中核回帰テストを単独実行した。

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests.test_next_reopen_requires_drafting_before_triad_review -v`：pass

## 2026-06-15 commit 承認 nonce reopen への対応

Requirement 4 受入 6〜7 と tasks T-004／T-006／T-011 の追記に従い、commit 承認を staged 内容に束縛する nonce challenge 経路を実装した。

実装内容：

- `tools/check_workflow_action/commit_approval.py` を追加し、`commit-approval-v1` canonical digest、nonce challenge、承認 record、invalidate、commit validation を分離した
- `tools/check-workflow-action.py commit-approval prepare --json`、`record --nonce <nonce> --source-text-stdin --json`、`record --nonce <nonce> --no-source-text --json`、`invalidate --json` を追加した
- `commit` 直前検査は、承認 record に `nonce` がある場合、challenge と approval の `target_digest`、現在の staged exact index、UTC ISO timestamp、TTL 10 分、期限切れ、clock rollback、`attestation_type`、`guarantee_scope`、禁止 LLM/provider/model 系 field を検査する
- 承認本文は argv で受け取らず、stdin または no-store mode に限定した。stdin 保存時は `tools.session_record_extractor.redact.redact_text` と `find_residual_secrets` を通し、秘密候補が残る場合は本文を保存せず `source_omission_reason=residual_secret_detected` として記録する
- 旧 `target_sha256` 型の commit 承認 record は互換入力として維持し、nonce がある record だけ新しい厳格検査を追加する

TDD 実施結果：

- 赤フェーズ：`commit-approval` サブコマンド未実装により、nonce prepare／record／commit validation 系 5 テストが失敗することを確認した
- 緑フェーズ：nonce challenge と validation 実装後、追加テスト 7 件と既存 commit/guarded/runtime 配置回帰 51 件が通過した

実行済み：

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_outputs_nonce_challenge_json tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_no_source_json_validates_for_commit tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_rejects_staged_change_after_record tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_rejects_expired_record tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_rejects_llm_metadata_fields -v`：red から green
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_source_text_is_redacted tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_residual_secret_omits_source -v`：pass
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v`：pass

未充足・triad-review 確認対象：

- consume 永続化失敗後の再利用拒否、通常 git execution failure 後の条件付き retry、malformed record の網羅、削除 staged／path 順非依存の nonce 専用回帰は追加確認が必要である
- 実装は LLM/provider/model に依存しない record schema と機械検査で構成される。proxy_model や利用 LLM は承認判断の運用主体であり、nonce validation の入力 field ではない

## 2026-06-15 implementation triad-review must-fix 対応

proxy_model 裁定後、implementation triad-review の C1〜C4 must-fix に TDD で対応した。

対応内容：

- C1：guarded commit 成功後に approval record と nonce challenge の両方を `consumed=true` として永続化する。消費永続化に失敗した場合、guarded commit wrapper は成功扱いにしない。
- C2：`commit-approval record` は `execution_delegation` を既定で保存しない。staged content approval と LLM commit 実行代行承認を分離した。
- C3：rename の source deletion を canonical target に含めるよう、staged file collection を status map 基準へ変更した。gitlink の mode/object_id 保存も回帰テストで確認した。
- C4：challenge の `target_files` は文字列配列かつ重複なしであること、`target_digest` は algorithm と 64 桁 hex digest を満たすこと、`target_files` が現在の canonical staged entries と一致することを record 作成前に検査する。

追加・更新テスト：

- `tests.tools.test_guarded_git_commit.GuardedGitCommitTests.test_guarded_commit_consumes_nonce_challenge_after_success`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_does_not_embed_execution_delegation_by_default`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_rejects_malformed_challenge_target_files`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_includes_rename_source_deletion`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_preserves_staged_gitlink_entry`

実行済み：

- `.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit.GuardedGitCommitTests.test_guarded_commit_consumes_nonce_challenge_after_success tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_does_not_embed_execution_delegation_by_default tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_rejects_malformed_challenge_target_files tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_preserves_staged_gitlink_entry tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_prepare_includes_rename_source_deletion -v`：red から green
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit -v`：pass

## 2026-06-15 implementation triad-review should-fix 対応

must-fix 対応に続き、C5〜C7 should-fix に TDD で対応した。

対応内容：

- C5：redaction 後の source text を保存する場合、`source_omission_reason` key を出さないようにした。source を保存しない場合だけ omission reason enum を使う。
- C6：legacy fallback で読まれた nonce approval が security validation failure になった場合、凍結済み legacy record は変更せず、runtime 側に invalidated copy を作る。runtime challenge も invalidated にする。
- C7：`commit_stop_point=true` は broad bypass にしない。現在は構造化された停止点だけを許可する。第2過程は `step_number=2`、`commit_stop_point_step=2`、`commit_stop_point_kind=canonical_update_complete` の形だけを許可し、第3過程は `step_number=3`、`commit_stop_point_step=3`、`commit_stop_point_kind=drafting_complete`、`commit_stop_point_gate=stages/<phase>.yaml#drafting` の形だけを許可する。`next_step` の「停止点コミット」文字列だけでは許可しない。

追加・更新テスト：

- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_source_text_is_redacted`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason`

実行済み：

- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_source_text_is_redacted tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_invalidates_runtime_copy_when_legacy_nonce_fails tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_blocks_reopen_commit_stop_point_with_unscoped_reason -v`：red から green
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests tests.tools.test_guarded_git_commit tests.tools.test_runtime_placement_freeze.CommitApprovalPlacementTests -v`：pass

残タスク：

- C8：normal git execution failure conditional retry は proxy_model 判断どおり this gate では leave-as-is / follow-up とする。
- implementation triad-review gate 完了前に、C1〜C7 対応後の recheck が必要である。

## 2026-06-15 implementation triad-review recheck 対応

recheck review-run の R1〜R5 について、人間判断で R1 は must-fix、R3 は should-fix、R2/R4/R5 は leave-as-is とした。

対応内容：

- R1：nonce approval の消費順序を challenge → approval に変更した。approval consumed 書き込みに失敗しても、先に challenge が consumed になっているため nonce challenge の再利用を拒否できる。
- R3：`target_digest.digest` は小文字 `0-9a-f` の 64 桁だけを正規形として受け付ける。大文字 hex は内容不一致ではなく malformed digest として拒否する。

追加・更新テスト：

- `tests.tools.test_guarded_git_commit.GuardedGitCommitTests.test_guarded_commit_consumes_nonce_challenge_before_approval`
- `tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_rejects_uppercase_challenge_target_digest`

実行済み：

- `.venv/bin/python3 -m unittest tests.tools.test_guarded_git_commit.GuardedGitCommitTests.test_guarded_commit_consumes_nonce_challenge_before_approval tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_approval_record_rejects_uppercase_challenge_target_digest -v`：red から green

## 2026-06-19 integrated design Requirement 13〜16 implementation drafting

2026-06-19 の reopen R-0 では、requirements / design / tasks に Requirement 13〜16 と T-016〜T-019 が追加された。implementation drafting では、既存実装に混ぜて完了主張せず、実装対象を次の 4 領域へ分離する。

### T-016：operation contract 語彙と required_action 対応

T-016 は、`next --json` の `required_action` と実行前検査を operation contract に接続する作業である。既存の `stages/operation-registry.yaml` と read-only preflight は参照側として残し、次を新規または拡張対象とする。

- `.reviewcompass/schema/effect_kind.schema.json`
- `.reviewcompass/schema/phase_boundary.schema.json`
- `.reviewcompass/schema/operation_contract.schema.json`
- `stages/operation-contracts.yaml` または `stages/operation-registry.yaml` 内の contract 正本節
- `tools/check_workflow_action/operation_contracts.py`
- `tests/workflow-management/test_operation_contract_schema.py`
- `tests/workflow-management/test_required_action_contract_mapping.py`

implementation では、commit boundary を `commit_boundary` として明示し、強制 commit 点と bookkeeping 更新を区別する。停止点消費、approval consumption、phase boundary の扱いは TDD で検査し、既存の `commit_stop_point` ガードを広い bypass に戻さない。

実装時に追加する予定の検証：

- `preconditions` 欠落、`postconditions` 欠落、`side_effects` 欠落、`workflow_state_effect` 欠落を operation contract schema で拒否する
- `required_action` と operation contract の対応が未登録の場合、`next --json` の実行前検査を DEVIATION にする
- `commit_boundary=true` の強制点は commit なしで先へ進めない
- bookkeeping 更新のみの操作は、強制 commit 点として扱わない
- `record_human_decision` は記録操作であり、commit / push / spec.json 更新 / フェーズ移行の実行権限を与えない

### T-017：承認ゲート・side track stack・workflow-state snapshot

T-017 は、承認判断、side track、workflow-state snapshot を会話文脈ではなく機械可読状態として扱う作業である。

実装対象：

- `.reviewcompass/schema/approval_gate.schema.json`
- `.reviewcompass/schema/side_track_stack.schema.json`
- `.reviewcompass/schema/workflow_state_snapshot.schema.json`
- `tools/check_workflow_action/approval_gate.py`
- `tools/check_workflow_action/side_track_stack.py`
- `tools/check_workflow_action/workflow_state_snapshot.py`
- `tools/check-workflow-action.py workflow-snapshot --json`
- `tests/workflow-management/test_approval_gate.py`
- `tests/workflow-management/test_side_track_stack.py`
- `tests/workflow-management/test_workflow_state_snapshot.py`

今回の side track で修正した bookkeeping commit boundary の緩和は、T-017 の本実装ではなく既存 workflow の操作性回復である。T-017 では、承認 record の target digest、expiry、consume / invalidate 状態、side track stack の LIFO、許可ファイル、nesting depth、snapshot drift を個別に検査する。

実装時に追加する予定の検証：

- `staged file set digest` が承認時と実行時で一致しない場合、承認 record を使えない
- `human-only decision` を `proxy_model decision` で通過させようとした場合、DEVIATION にする
- proxy_model が代行可能な判断は、対象 finding / cluster、判断範囲、不可逆操作を含まないことを schema で検査する
- side track stack は LIFO、`return_to`、許可ファイル、最大 depth、親 state digest を検査する
- workflow-state snapshot は `spec.json`、`pending_gates`、`drafting_completed_gates`、`completed_gates`、operation contract、staged file set digest、worktree digest を含む
- snapshot drift がある場合、phase 移行、approval 完了、commit 境界通過を許可しない

### T-018：構造化有効プロンプトと prompt audit

T-018 は、effective prompt を単なる連結テキストではなく language task I/O、入力 artifact、制約、禁止事項、出力 schema、completion routing、監査 anchor を持つ構造成果物へ拡張する作業である。

実装対象：

- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/check-workflow-action.py prompt-audit --prompt-manifest <path> --json`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`

既存の `.reviewcompass/runtime/effective-prompts/*.prompt.md` と `next_action.effective_prompt.effective_prompt_path` は互換出力として維持する。構造化 manifest がある場合は source digest coverage を正本検査対象にし、text-only のみは移行期 WARN として扱う。

実装時に追加する予定の検証：

- `rounds.yaml` に structured manifest path / sha256 と既存 `effective_prompt_path` / `effective_prompt_sha256` を併存して記録できる
- text-only のみの場合は `text-only 互換 WARN` とし、移行期の互換状態として扱う
- structured manifest と text-only decision point が食い違う場合は `manifest 不一致 DEVIATION` にする
- structured manifest と text-only effective prompt の両方が欠落する場合は DEVIATION にする
- language task と machine task を分離し、`on_completion` が commit / push / spec.json 更新 / フェーズ移行を直接実行しないことを検査する
- review-run recording は `run_role.py` / `run_review.py` の raw、parsed、rounds、model-result summary に structured manifest 参照を残す

### T-019：Phase 0〜6 と proxy_model triage decision 機械処理化

T-019 は、Requirement 13〜15 の実装を Phase 0〜6 に分け、各 phase の entry criteria、exit criteria、allowed operations、forbidden operations、required tests、commit boundary を検査可能にする作業である。あわせて proxy_model triage decision を raw response、candidate、selected decision、reason、target まで構造化し、human-required decision を proxy_model で通過させない。

実装対象：

- `stages/workflow-management-implementation-phases.yaml`
- `.reviewcompass/schema/implementation_phase.schema.json`
- `.reviewcompass/schema/proxy_triage_decision.schema.json`
- `tools/check_workflow_action/implementation_phases.py`
- `tools/check_workflow_action/proxy_triage_decisions.py`
- `tools/check-workflow-action.py implementation-phase-check --feature workflow-management --json`
- `tools/check-workflow-action.py proxy-triage-decision-check --run <path> --json`
- `tests/workflow-management/test_implementation_phase_plan.py`
- `tests/workflow-management/test_proxy_triage_decision_machine.py`
- `tests/workflow-management/test_review_wave_consumer_impact.py`

Phase 0〜6 は、選択層、schema、read-only registry、advisory preflight、structured prompt、mechanical blocking、LLM judge audit の順に分ける。implementation では、複数 phase の途中状態を単一 commit に混在させず、各 phase の完了条件を TDD で先に固定する。

実装時に追加する予定の検証：

- Phase 0〜6 の entry criteria、exit criteria、allowed operations、forbidden operations、required tests、commit boundary を phase plan schema で検査する
- phase の依存順を飛ばした場合、implementation-phase-check を DEVIATION にする
- `review-wave consumer impact blocking` は review-wave summary、carry-forward register、downstream_impact_decisions、`spec.json.recheck.impacted_downstream_phases` を入力として未反映を検出する
- `spec.json.reopened` を active reopen scope と誤認した場合、impact review scope の混同として DEVIATION にする
- proxy_model triage decision は raw response、candidate options、selected decision、reason、source raw paths を欠く場合、実装着手の承認証跡として扱わない

### drafting 判断

今回の implementation drafting は、Requirement 13〜16 / T-016〜T-019 を implementation 正本上の実装対象へ展開する作業であり、T-016〜T-019 の実装完了主張ではない。次 gate の implementation triad-review では、上記 4 領域の分離、成果物一覧、TDD 境界、既存実装との接続、commit boundary / approval boundary の扱いが妥当かを確認する。

## proxy_model implementation triad-review C1〜C6 対応

2026-06-19 の implementation triad-review では、proxy_model が C1〜C6 を修正対象、C7 を修正不要と判断した。

- C1: drafting 完了は triad-review 開始準備の記録であり、implementation triad-review 完了ではない。spec.json の drafting flag はこの下書きがレビュー対象として準備済みであることだけを表し、review-wave、alignment、approval、実装完了、commit、push を完了扱いにしない。
- C2: T-017 には `staged file set digest` と `human-only decision` / `proxy_model decision` 境界の赤テストを追加する。
- C3: T-016 には `preconditions`、`postconditions`、`side_effects`、`workflow_state_effect`、commit boundary の赤テストを追加する。
- C4: T-018 には `text-only 互換 WARN`、`manifest 不一致 DEVIATION`、両欠落 DEVIATION、review-run recording の赤テストを追加する。
- C5: T-019 には Phase 0〜6 の entry / exit、forbidden operations、`review-wave consumer impact blocking` の赤テストを追加する。
- C6: 検証欄は実行済み検証と、実装時に追加する予定の検証を分けて記録する。

## 検証

実行済み検証：

- `python3 -m unittest tests.tools.test_check_workflow_action -v`
- `python3 -m pytest tests/tools/test_session_record_contract.py -q`
- `python3 -m pytest tests/tools/test_workflow_management_implementation_drafting.py -q`
- `.venv/bin/python3 -m pytest tests/tools/test_workflow_management_implementation_drafting.py -q`
- `python3 tools/check-workflow-action.py next --json`

実装時に追加する予定の検証：

- `tests/workflow-management/test_operation_contract_schema.py`
- `tests/workflow-management/test_required_action_contract_mapping.py`
- `tests/workflow-management/test_approval_gate.py`
- `tests/workflow-management/test_side_track_stack.py`
- `tests/workflow-management/test_workflow_state_snapshot.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_implementation_phase_plan.py`
- `tests/workflow-management/test_proxy_triage_decision_machine.py`
- `tests/workflow-management/test_review_wave_consumer_impact.py`

結果：

- `tests.tools.test_check_workflow_action` は通過
- `tests/tools/test_session_record_contract.py` は通過
- `tests/tools/test_workflow_management_implementation_drafting.py` は通過済みの棚卸し検査
- `next` は drafting 完了後の次作業として `workflow-management / implementation / triad-review` を返す

## drafting 完了判断

現時点では、workflow-management implementation.drafting の下書き成果物として、本棚卸しを作成した段階である。

推薦判断：

1. 本棚卸しをもとに implementation.drafting の triad-review へ進める。
2. triad-review では、T-004 周辺の実装を重点的に確認し、T-001〜T-011 全体の未充足を drafting 完了の阻害要因とするか、後続 implementation task として扱うかを判定する。
3. 2026-06-19 integrated design reopen では、T-016〜T-019 を implementation 正本上の実装対象へ展開したため、drafting 完了は triad-review 開始準備の記録であり、implementation triad-review 完了ではない。
