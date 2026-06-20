### Requirement 13：operation contract 語彙と required_action 対応

**目的（Objective）**：保守担当者が、`next --json` が選んだ唯一 action を、記憶や前例ではなく operation contract に基づいて実行できるようにする。選択層は「何をすべきか」を一意に返し、実行層は「どう実行するか」を副作用・承認・前提条件・事後条件として定義する。

#### 受入基準（Acceptance Criteria）

1. 本機能は operation contract の共通語彙として、最低限 `effect_kind`、`approval_required`、`phase_boundary`、`sequence`、`preconditions`、`postconditions` を定義する。`effect_kind` は `read`、`write`、`state_mutation`、`external_call` の4値を基線とし、`approval_required` は `effect_kind` とは独立した真偽値として扱う。
2. 本機能は Phase 1 のスキーマ定義として、operation contract schema、`effect_kind` schema、`phase_boundary` schema、状態スナップショット schema、言語タスク共通入出力 schema を `.reviewcompass/schema/` 配下に定義する。既存実行挙動はこの段階では変更しない。
3. 本機能は D-003 §6 の19段階優先順位に対応する `required_action` それぞれについて、operation contract 上の `effect_kind`、実行主体、`approval_required` の対応を registry または同等の機械可読定義で表す。対応表は19語彙すべてを対象とし、`run_maintenance`、`run_reopen_pending_gate`、`run_workflow_stage` のような条件分岐を持つ action を代表値だけで曖昧化しない。`required_action` 語彙そのものの正本は Requirement 2 受入 10 の JSON Schema とする。
4. 19語彙対応表は各 `required_action` について、最低限 `required_action`、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、実行主体、分岐条件の有無、参照する preconditions / postconditions を機械可読に持つ。複合操作または条件分岐を持つ語彙は、対応表上で「未確定」や代表値だけにせず、分岐ごとの条件と最大副作用を明示する。
5. 承認ゲートを必須とする単純操作は、最低限 `commit_stop_point`、`apply_approved_reopen_plan`、`run_reopen_start`、`advance_reopen_after_commit_stop_point`、`advance_reopen_after_approval_stop_point`、`finalize_reopen`、`repair_workflow_state` を含む。これらは `approval_required: true` として扱い、実行前に明示的な人間判断記録を必要とする。ただし、この人間判断記録は受入 6 および Requirement 14 受入 1〜3 の承認ゲート全体の一部であり、`record_human_decision` の完了だけを対象 operation の承認成立として扱ってはならない。この列挙は複合操作の分岐条件を否定しない。`run_maintenance` は maintenance YAML または内部操作の承認要求に従い、`run_workflow_stage` は stage 種別に従う。
6. `record_human_decision` は承認対象操作ではなく、承認ゲートを構成する判断記録操作として扱う。`effect_kind` は判断記録を書き込む場合は `state_mutation` とし、`approval_required` は常に `false` とする。`record_human_decision` の完了だけでは、対象 operation の `approval_required: true` を満たしたことにしてはならない。
7. `run_reopen_pending_gate` は active gate 種別に応じて operation contract を分岐する。`triad-review` と `review-wave` は外部レビュー実行を伴う `external_call`、`alignment` は LLM が整合確認材料を生成する `write`、`approval` は承認要求を構造化する `state_mutation` として扱う。drafting は `run_reopen_drafting` として分離する。
8. `run_maintenance` と `run_workflow_stage` は、内部で実行する操作または stage 種別によって `effect_kind` と `approval_required` が変わる複合操作として扱う。複合操作を単一代表値、list 型、内部ステップ分解のいずれで表すかは design で確定するが、LLM が都度推測する形にはしない。design で確定するまでの最小規則として、複合操作は分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則を持つものとして扱う。
9. 複合操作の schema 表現は Phase 1 の未確定事項として扱う。候補は、最大副作用の `effect_kind` を代表値として注記する、`effect_kind` を list 型にする、複合操作を単一 enum の内部ステップへ分解する、の3案を最低限保持する。どの案を design で採用する場合でも、受入 8 の分岐条件、内部 step、各 step の `effect_kind`、最大副作用、承認要否の集約規則という最小制約を失わせてはならない。また、`record_human_decision` が記録する判断と承認対象の `required_action` を、セッション識別子、タイムスタンプ、操作 ID、または同等の識別子で結びつける方法を design で確定する。
10. 本機能は operation contract の実行前に preconditions を、実行後に postconditions を機械確認できるようにする。確認不能な条件を `OK` として扱わず、read-only advisory 段階では `WARN` 以上、runner-enabled operation では `DEVIATION` として fail-closed にする。
11. operation contract と operation registry / preflight の間には、単一の機械可読正本境界を置く。物理表現は design で確定するが、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、preconditions、postconditions、side effects、承認要否の集約規則を、registry と contract の複数箇所で別々に再定義してはならない。registry / preflight は正本 contract を参照または同一正本内で読み取り、実行・更新・承認消費を行わない read-only confirmation として扱う。
12. operation contract 正本と registry / preflight の参照関係は、欠落、stale、digest / version drift、または正本 field の重複を機械検出できなければならない。検出時は read-only advisory 段階では `WARN` 以上、runner-enabled operation では `DEVIATION` として fail-closed にする。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §3、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §3・§10 Phase 1。2026-06-18 セッション 77e272a2 の統合設計メモ要件追記未完了分を、AC10・AC11 だけでなく operation contract 全体へ戻す。

### Requirement 14：承認ゲート、側道スタック、状態スナップショット

**目的（Objective）**：保守担当者が、不可逆操作の承認、予期しない側道作業、現在状態の可視化を、LLM の暗黙解釈ではなく機械可読な状態として扱えるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は承認ゲートを、`wait_for_human_decision` と `record_human_decision` のペア、およびその後の `next --json` による分岐として扱う。`record_human_decision` が完了した事実は、対象操作が承認された事実と同一視しない。
2. 承認ゲートは、承認、拒否、保留、修正要求を区別して記録できなければならない。記録された判断の内容を読み、対象の不可逆操作へ進むか、停止を維持するか、再起草へ戻すかを決めるのは `next --json` の責務とする。
3. 承認、拒否、保留、修正要求の各判断は、対象 operation ID、対象 `required_action`、対象 artifact または staged file set digest、判断者、判断時刻、出典を持つ。`next --json` は、承認以外の判断が記録されている場合に対象の不可逆操作を許可してはならず、拒否は停止、保留は待機、修正要求は再起草または repair に分岐させる。
4. 本機能は side track をスタックとして扱う。各 frame は最低限、`frame_id`、`kind`、`parent_frame_id`、`pushed_by`、`allowed_scope`、`allowed_files`、`completion_conditions`、`return_to`、`title`、`spawned_from`、`staged_file_digest`、`staged_file_set` を持つ。
5. `staged_file_set` と `staged_file_digest` は side track push 時点、pop 直前、commit / push 直前に採取・照合できなければならない。frame の `allowed_files` 外の staged 変更、push 時点からの予期しない digest 変化、親子 frame 間で明示許可されていない staged file set の重なり、pop 時の digest / set 不一致は、Phase 3 では WARN 以上、Phase 5 では `DEVIATION` または `repair_workflow_state` として扱う。
6. side track は top frame だけを閉じられる。`side-track-pop` 後は `next --json` が直下の frame または本線作業を自動的に再開する。LLM が復帰先を会話文脈から選ばない。pop 後に git index が side track 開始前の本線状態へ戻っていない場合、または side track 内の commit / push 後に index の変化を説明する記録がない場合、通常作業へ戻してはならない。
7. side track の `max_depth` は既定 2 とし、Phase 3 では超過を警告、Phase 5 ではブロック対象とする。深度超過または scope drift は `repair_workflow_state` または同等の停止状態として扱う。
8. 本機能は `.reviewcompass/runtime/workflow-state-snapshot.yaml` を現在状態のスナップショットとして出力できるようにする。スナップショットは `next --json` の副産物であり、`next --json` 自体の出力契約を置き換えない。
9. 状態スナップショットは最低限、`schema_version`、`generated_by`、`generated_at`、`current_work`、`active_side_tracks`、`git_tree_summary`、`post_write_manifest_summary`、`workflow_state_summary` を持つ。`current_work` は `required_action`、人間可読 `title`、`outer_node`、`inner_node`、`active_gate` を含む。
10. スナップショットが古い、手動更新された、または `next --json` の実行結果と照合できない場合は信頼しない。正本は常に `next --json` と state refs であり、スナップショットは可視化・監査補助である。
11. 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。proxy_model の適用可否と human-required predicate の優先順位は Requirement 16 受入 13〜14 と整合させる。
12. side track stack、approval gate record、workflow-state snapshot は保存先、read-only 操作、mutating 操作を区別できなければならない。状態を書き換える push / pop / consume / invalidate / save 系操作と、状態を読む current / snapshot / inspect 系操作を同一 operation として曖昧化してはならない。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §5.1〜§5.3、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §3.3・§8・§10 Phase 1。

### Requirement 15：構造化有効プロンプトと監査

**目的（Objective）**：保守担当者が、有効プロンプトを長い説明文ではなく、LLM が担当する言語タスクの仕様書として扱えるようにする。機械タスクは operation contract とツールが担い、有効プロンプトには言語タスクの入力・出力・制約・事後条件を明示する。

#### 受入基準（Acceptance Criteria）

1. 本機能は有効プロンプトの構造として、最低限 `decision_point`、`preconditions_checked`、`language_task`、`postconditions`、`on_completion` を定義する。
2. `language_task` は最低限、`document_kind`、`input`、`output_format`、`constraints` を持つ。LLM が生成または判断する対象、参照すべき入力、出力形式、禁止事項を判定点ごとに明示する。
3. 機械タスクは有効プロンプトに実行手順として埋め込まず、operation contract、preflight、runner、guard の責務として扱う。有効プロンプトは、機械が実行済みまたは確認済みの preconditions と、LLM が行う言語タスクだけを表す。
4. 本機能は Phase 4 で、`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` または後継 registry から、全判定点について構造化有効プロンプトを生成できるようにする。既存の `next_action.effective_prompt.effective_prompt_path` との互換は維持する。
5. 本機能は有効プロンプトの第1層機械検査を提供する。検査は、参照先ファイルの実在、アンカーの実在、必須構造節の存在、長さの上下限、DISCIPLINE_MAP 未登録 action kind、review target manifest と review-run target の一致を確認する。加えて、`language_task.output_format` と `postconditions` の対応、`preconditions_checked` が機械確認済み条件だけを参照していること、`on_completion` が operation contract の postconditions / 次 action と矛盾しないことを検査する。側道スタックまたは operation preflight が持つ staged file set とのコミット混線検査は Requirement 12・14 の責務として扱い、有効プロンプト監査から参照可能にする。
6. 本機能は Phase 6 で、構造化有効プロンプトと `WORKFLOW_NAVIGATION.md` の該当節を入力に、LLM 裁判官による意味的監査を行えるようにする。監査は不足や gap を構造化出力で返す補助であり、意味的な最終承認を自動化しない。監査観点は、前提条件が機械確認可能な条件を網羅しているか、言語タスクの入出力形式が明確か、事後条件が出力妥当性を確認できるか、機械タスクに移すべき処理が有効プロンプトへ残っていないかを含む。
7. LLM 裁判官の出力は schema に適合する JSON または同等の構造化形式とし、既知の gap を検出できることをテストで確認する。既知の gap には、必須構造節の欠落だけでなく、機械タスクの有効プロンプト内残留、preconditions の網羅不足、postconditions の確認不能性を含める。Phase 6 は Phase 5 までの機械的強制が完了した後の任意・後回し可能な段階とする。

由来：`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §4・§5・§10 Phase 4・Phase 6、`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §4.2。

### Requirement 16：段階的実装計画 Phase 0〜6

**目的（Objective）**：保守担当者が、選択層と実行層の機械化を一度に混ぜず、既存挙動を壊さない順序で TDD 実装できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能は D-003 の19段階優先順位、`required_action` 唯一化、invariant 検査、reopen plan compiler を Phase 0 として扱う。Phase 0 は選択層の実装であり、D-003 全体を仕様とする。D-003 の参照元は `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` とし、正本昇格または移動が起きた場合は stable canonical anchor を requirements または design で明示する。
2. Phase 0 の開始前提として、Phase 1 のうち Requirement 2 受入 10・11 のスキーマ定義を先に満たす。これは Phase 0 TDD 開始を可能にする最小前提であり、統合設計全体を AC10・AC11 に限定するものではない。`effect_kind`、`phase_boundary`、operation contract、状態スナップショット、言語タスク共通入出力 schema は Phase 0 と並行して定義してよい。
3. Phase 0 の完了条件は、D-003 §7.1 の6つの失敗テストが全てパスし、現在の D-003 reopen に必要な workflow state repair を機械的に検出できることである。D-003 の節番号が変わる場合は、6つの失敗テストを requirements、design、または tasks のいずれかで列挙し、節番号だけに依存しない完了条件へ移す。必要に応じて `reopen-recompile` が reopen plan の派生値を再導出し、in-progress YAML の `pending_gates` と `commit_stop_point` の整合を修復できるようにする。
4. Phase 1 は語彙・スキーマ定義を行い、実行挙動を変えない。新規スキーマは `.reviewcompass/schema/` に置き、スキーマ自体の整合性をテストで確認する。Phase 1 のうち Phase 0 開始をブロックする最小スキーマは Requirement 2 受入 10・11 であり、それ以外の operation contract 系 schema は Phase 0 と並行可能な Phase 1 作業として扱う。
5. Phase 2 は読み取り専用 registry を実装する。`check-workflow-action.py operation-list --json` または同等のコマンドが、各 operation の `canonical_commands`、`effect_kind`、`approval_required`、`sequence`、`pending_conflicts` を返せることを完了条件とする。既存の `next --json` の動作は変えない。
6. Phase 3 は `operation-preflight <id> --json` または同等の事前検査を警告のみで導入する。pending conflict、側道 depth、コミット混線、有効プロンプト第1層機械検査を検出するが、この段階では既存フローをブロックしない。
7. Phase 4 は有効プロンプトを構造化し、全判定点で新構造の prompt を生成できるようにする。構造の完全性はテストで確認する。
8. Phase 5 は Phase 3 の警告を機械的ブロックへ昇格する。`sequence: serial_only` の順序違反、コミット混線、side track depth 超過、`approval_required: true` の承認欠落をブロックする。正常パスがブロックされないことをテストで確認する。
9. Phase 6 は LLM 裁判官による意味的監査を実装する。構造化した有効プロンプトと該当運用文書を入力にし、gap を構造化出力として返す。Phase 6 は Phase 5 までの後に着手し、後回し可能とする。
10. 各 Phase の終了時には `next --json` が通常作業に戻れる状態、または明示された停止状態を返すことを確認してからコミット対象にする。Phase をまたいだ途中状態を単一コミットに混在させない。
11. 本改訂の reopen scope は workflow-management の requirements から design / tasks / implementation への連鎖再実施である。`spec.json.reopened` は過去に上流を reopen した履歴フラグとして保持し得るため、現在の active reopen scope と同一視しない。現在の scope、impact review scope、direct / indirect feature、flag policy は in-progress reopen record、classification record、`spec.json.recheck`、および review-wave / alignment の証跡で区別して記録する。
12. operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の機械処理化は、workflow-management 以外の feature が consumer / derivative として参照し得る。正本 reopen の対象を workflow-management に限定する場合でも、review-wave では foundation、runtime、evaluation、analysis、self-improvement、conformance-evaluation などへの正本変更要否と consumer 契約影響を確認し、reopen scope と impact review scope を混同せず記録する。
13. proxy_model triage decision の適用可否は、provider / model 名ではなく、機械可読な evidence completeness、対象 finding / cluster coverage、approval gate record、operation contract の `approval_required`、review-wave impact evidence、human-only decision 境界に基づいて判定する。human-required を示す証跡が 1 つでも存在する場合、または必要な判定元が欠落・競合する場合、proxy_model decision だけで通過させてはならない。
14. human-required predicate の優先順位と競合解決は design で確定する。最低限、human-only decision 境界、未解決 approval gate、`approval_required: true` の対象 operation、未解決 review-wave impact evidence は proxy_model 適用より優先される。triage 上の leave-as-is や proxy approved は、これらの human-required 証跡を打ち消さない。

由来：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §4・§6・§7、`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md` §7・§10。2026-06-18 セッション 77e272a2 の「統合設計メモ全体を requirements に書き込む」未完了作業の中核。

