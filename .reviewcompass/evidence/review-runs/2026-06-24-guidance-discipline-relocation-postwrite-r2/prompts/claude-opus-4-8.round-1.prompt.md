prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-opus-4-8

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: post_write_verification__discipline_avoid_compound_bash__discipline_concise_complete_report__discipline_facts_vs_interpretation__and_13_more
phase: post_write_verification
generated_at: 2026-06-23T15:12:27.291972+00:00

## Change Summary

post-write verification target files changed: .reviewcompass/guidance/discipline_avoid_compound_bash.md, .reviewcompass/guidance/discipline_concise_complete_report.md, .reviewcompass/guidance/discipline_facts_vs_interpretation.md, .reviewcompass/guidance/discipline_implementation_autonomy.md, .reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md, .reviewcompass/guidance/discipline_must_fix_discussion_obligation.md, .reviewcompass/guidance/discipline_no_redundant_workflow_questions.md, .reviewcompass/guidance/discipline_normal_output_minimization.md, .reviewcompass/guidance/discipline_options_presentation.md, .reviewcompass/guidance/discipline_plain_explanation_each_step.md, .reviewcompass/guidance/discipline_plain_japanese.md, .reviewcompass/guidance/discipline_pre_action_precheck.md, .reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md, .reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md, .reviewcompass/guidance/discipline_workflow_precheck_invocation.md, docs/disciplines/README.md

## Review Question

Verify that the listed post-write target files are consistent with the source materials, keep target/source/out-of-scope separation clear, and do not weaken prompt-manifest preflight, finding policy, or post-write verification stop conditions.

## Target Files

- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_avoid_compound_bash.md sha256=bfb51bebf6877b22c6acc8dd05378b29274961b7bde407fb71c8c4c42869cfc7
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_concise_complete_report.md sha256=715e67d83d5c3d9badc85c8d487498e69d5cf2fa2406ca822e886a34a69e4052
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_facts_vs_interpretation.md sha256=6662bb52b63c0bf7ca2ef743760c34e7554eee85bee5530415073f2750b46449
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_implementation_autonomy.md sha256=47bea56df8fafae0a392d5ada4e2f6b45e8e9239fda64a72d8c6ef915051c0d3
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md sha256=971e44a1f5c5026a98865ffdbfd116fcd80ee86b96f7ebee9b2a34cecf8be968
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md sha256=12c05dede38e024466377cdd8272e90bb84ab73f67b438ec11984935769bac75
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md sha256=db7bdfbc8a2b4b2fcb33c869420c52ac58f06ad7fe4a79f0eab967597201f928
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_normal_output_minimization.md sha256=e74d3098d84c52e50f0e6602a426754b52ecdbe16ffa1f6a3fcdaf6a6d71e8a6
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_options_presentation.md sha256=bd60db3932c2261b6588b9916720cf50222c18b42996952f996fc306a284757c
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_plain_explanation_each_step.md sha256=b7c02e94078eaa2aa519e1fc5b71d2ed9d81e351a55fb4bd2a96056e450a2603
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_plain_japanese.md sha256=21e60fb53585e525fc4220bb738c5ad84f0bc363c0e401ebd878868422d0bd34
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_pre_action_precheck.md sha256=9f14916c6df802c00bd389368ac55161c2e28fa0eec1283116de9df37f3a097f
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md sha256=ab5766d61be4559b38bbd584c3c5bf66b9dd2746fa2eb8792f43c9990208deeb
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md sha256=3b03b245a529af50dfbb5674ee045397572947031b6b8caa564dcc9f552d9e35
- /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_workflow_precheck_invocation.md sha256=f623dc363ec9b49e7b902b0fc9a99213e0d80e60cda06c94bbd1c9adb16d39a7
- /Users/Daily/Development/ReviewCompass/docs/disciplines/README.md sha256=fdb37def67da7d744846c216c0d5884f11c088152c6fa27216889df9227de801

## Source Materials

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/WORKFLOW_NAVIGATION.md

content_mode: full_text
content_sha256: 268076aee0ddbde231009d48d8840773ff87433cd4e8653492f0004c106f76be

```text
# ReviewCompass ワークフローナビゲータ共通手引き

この文書は、`tools/check-workflow-action.py next --json` の読み方を定める共通手引きである。

## 1. 最初に実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

出力 JSON の `next_action.kind` を、現在の作業順序・優先順位の正本として扱う。記憶、要約、TODO の候補欄だけを段取りの根拠にしない。

`next_action.required_disciplines` がある場合は、作業直前にそのファイルだけを読む。セッション開始時に長い規律群を一括で読んで記憶に頼るのではなく、機械判定された場面ごとの短い規律セットで挙動を調整する。対応表は `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` を正本とし、`next --json` はその内容を機械可読に展開する。

`next_action.required_inputs` がある場合は、規律ではなく作業対象ごとの状態入力として扱う。`id`、`source_type`、`read_policy` を確認し、`path` がある場合でもファイル名そのものを一般規律に昇格しない。たとえば持ち越し台帳は、配布先プロジェクトごとに別ファイル、外部台帳、または未配置になり得るため、`unresolved_cross_scope_items` のような抽象入力として扱う。

機械可読な判定点では、判定点ごとに 1 本の effective prompt を読む。複数の元資料を直接ばらばらに読ませるのではなく、判定点に必要な規律・入力・次タスク方針を 1 本へ束ねた effective prompt を作り、その本文を LLM に読ませる。元資料は `prompt_source_refs` として保持し、実際に読ませた統合プロンプトは `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` で記録する。全判定点で同じ巨大な共通プロンプトを使わず、各判定点に必要な短い effective prompt を使う。

## 2. 判定結果の共通分岐

<a id="resume_in_progress"></a>

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。新しい作業を始めず、`next_action.file` に示された進行中ファイルを読む。

<a id="parent_resume_pending"></a>

### `parent_resume_pending`

blocking unit が完了し、戻り先の parent unit へ復帰する必要が残っている。新しい作業を始めず、`next_action.parent_unit_id` と `next_action.completed_unit_id` を確認し、まず parent unit の作業文脈へ戻る。

`parent_resume_pending` が出ている状態で、利用者から別作業への明示的な割り込み指示があった場合は、開始前に次を実行して、active unit と resume pending の有無を機械的に確認する。

```bash
python3 tools/check-workflow-action.py work-unit preflight-start \
  --proposed-unit-id <開始候補 unit ID> \
  --title "<開始候補の題名>" \
  --reason "<開始候補の理由>" \
  --json
```

`start_allowed: false` の場合は、`blocking_reasons` を利用者へ示して停止する。理由を見ずに通常 workflow、maintenance、新しい blocking unit へ進まない。

<a id="blocking_unit_required"></a>

### `blocking_unit_required`

別作業として切り出すべき作業が検出されている。通常 workflow や親作業を続けず、`next_action.proposed_unit` の `unit_id`、`title`、`reason`、`parent_unit_id`、`return_conditions` を確認してから、利用者の明示的な開始指示を待つ。

機械化が完全に揃うまでは、blocking unit の開始を暗黙に扱わない。開始前に、少なくとも次を会話上で明示する。

- blocking unit に入ること。
- 親作業の識別子。
- blocking unit の目的。
- blocking unit で変更してよい allowed files。
- 親作業へ戻るための完了条件。

宣言形式は次の形にそろえる。項目名を変えたり、本文中に散らして書いたりしない。

```text
blocking unit に入ります
- unit_id: <blocking unit ID>
- parent_unit_id: <親作業 ID>
- title: <短い題名>
- reason: <なぜ別作業として切り出すか>
- allowed_files: <変更してよいファイルまたはディレクトリ>
- return_conditions: <親作業へ戻るための完了条件>
```

`allowed_files` は必須であり、空欄や「必要な範囲」「関連ファイル」などの曖昧な指定では開始しない。開始時点で想定できるファイルまたはディレクトリを列挙し、途中で範囲を広げる必要が出た場合は、変更前に allowed files の追加を利用者へ明示する。親作業全体やリポジトリ全体を覆う指定は、混線防止の目的に反するため使わない。

`return_conditions` も必須であり、空欄や「完了したら」「必要なところまで」などの主観的な指定では開始しない。親作業へ戻ってよいかを確認できる条件を列挙し、少なくとも成果物、検証、commit または evidence の扱いを含める。blocking unit を出るときは、各条件を満たしたか、未達なら何を残件として親作業へ戻すかを明示する。

<a id="blocking_unit_in_progress"></a>

### `blocking_unit_in_progress`

blocking unit が active である。`next_action.unit_id` の作業だけを扱い、親作業の commit、push、post-write verification、TODO 整理へ横滑りしない。

機械化が完全に揃うまでは、作業者は次を手動で守る。

- 作業開始時と再開時に、現在の active blocking unit を確認する。
- commit 前に、commit unit が active blocking unit の `unit_id` と一致することを確認する。
- blocking unit 完了前に親作業の成果物を同じ commit に混ぜない。
- 親作業の commit は、blocking unit の完了条件を満たし、必要な commit または evidence を残し、親作業へ戻る宣言を終えるまで実行しない。
- blocking unit を出るときは、完了条件を満たしたこと、残件、親作業への戻り先を明示する。

<a id="reopen_in_progress"></a>

### `reopen_in_progress`

reopen 手続きが進行中である。通常ワークフローや post-write-verification より優先する。`next_action.file`、`next_step`、`completed_steps`、`pending_gates`、`current_blocker`、`required_action` を確認し、`required_action` に従う。

代表的な `required_action`：

- `draft_reopen_classification`：第1過程。種別判定・根拠記録。進行中ファイル発行と spec.json フラグ差し戻しは後続操作（`run_reopen_start`・`apply_approved_reopen_plan`）が担う。
- `repair_canonical_documents`：第2過程。上流フェーズの正本文書修正。
- `run_reopen_drafting`：第3過程。`next_pending_gate` が triad-review でも、同じ phase の drafting 完了が `drafting_completed_gates` または `completed_gates` に記録されていないため、先に正本文書を更新する。`next_drafting_gate`、`phase`、`stage: drafting`、`required_feature_scope` を確認し、レビューを開始しない。
- `run_reopen_pending_gate`：第3過程。drafting 完了記録がある、または次 gate が triad-review 以外であるため、`next_pending_gate` の gate を実行する。alignment / approval 連鎖の再実施を含む。
- `wait_for_human_decision`：人間の判断待ち。判断なしに進めない。
- `finalize_reopen`：第4過程。最終確認、recheck クリア、in-progress の完了処理。
- `repair_workflow_state`：判定不能または状態破損。推測で進めず利用者へ報告する。

<a id="maintenance_in_progress"></a>

### `maintenance_in_progress`

通常ワークフローではなく、ワークフロー制御・運用規律・検査器などの保守作業が進行中である。`next_action.file` を読み、`required_action`、`allowed_scope`、`completion_conditions` に従う。通常の `stage` や `upstream_recheck` へ戻るのは、maintenance の完了条件を満たし、進行中ファイルを `stages/completed/` へ移してからである。

`next_action` と異なる作業へ入る場合、または `next` 判定自体の欠陥を直す場合は、ファイル編集前に `stages/in-progress/maintenance-<日付>-<短い名前>.yaml` を作成する。少なくとも `trigger`、`mainline_blocked_by`、`allowed_scope`、`allowed_files`、`completion_conditions` を記録し、side track であることを明示する。これを省略すると、本筋の作業順序を守るための修復作業自体が、記録されない手順逸脱になる。

本線 reopen 中の maintenance 完了 commit は、`stages/completed/maintenance-*.yaml` の `mainline_blocked_by` が現在の reopen in-progress ファイルを覆うことで許可される。本線 `stages/in-progress/reopen-*.yaml` は、maintenance のためだけに同伴 stage しない。

**maintenance を始める前の事前調査（in-progress YAML を作成する前に実施する）**

1. 変更対象ファイルと依存関係を確認し、影響範囲を特定する。
2. フィーチャー横断の影響がないことを確認する。
3. 先に解決すべきブロッカー（別の問題）が潜んでいないことを確認する。

事前調査の結果として次の開始条件をすべて満たした場合のみ maintenance を始める。

- 変更が局所的である（既存仕様境界を変えず、workflow 機構・承認・状態機械・`next --json` の意味を変えない）。
- 影響範囲が対象フィーチャーに閉じている。

いずれかを満たさない場合：

- 中核変更（仕様境界・workflow 機構を変える）の場合は reopen または新規 workflow として扱う。
- フィーチャー横断の影響がある場合は利用者にエスカレーションする。

開始条件を満たした場合、in-progress YAML を作成した後に最初に次の 3 行を宣言する。

```
変更分類: 局所
理由: <影響範囲と既存仕様境界への影響の説明>
手順: TDD 主導 / 文書のみ（lightweight self-check）
```

コード変更を伴う局所変更は TDD 主導（テスト先行）で進める。文書のみの変更は lightweight self-check で確認する。

### `reopen_classification_required`

完了済み workflow で、`intent`、feature-partitioning、`requirements`、`design`、`tasks` などの上流正本が後続成果物より新しい。単なる再確認として下流へ進めず、意味変更の有無と reopen 種別を分類する。`next_action.reopen_trigger` が候補を示す場合も、分類根拠を保存して `reopen-start` へ進む。

<a id="post_write_verification"></a>

### `post_write_verification`

書き込み後検証の対象となる未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` 全体を対象として検証する。

検証 manifest は `.reviewcompass/post-write-verification/*.yaml` に置く。`target_files`、`target_sha256`、`required_verifiers`、`completed_verifiers`、`unresolved_substantive_findings` を記録する。`verifications[]` がある場合、各 verifier は `target_files` 全体と対応する `target_sha256` を単一エントリで覆る必要がある。ファイルごとの分業は独立多重チェックではない。

API 経由の複数モデル検証を行う場合の標準手順：

```bash
.venv/bin/python3 tools/api_providers/prepare_post_write_review.py \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --source-material .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md \
  [--source-material <additional-source-material> ...] \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --criteria-id <criteria-id> \
  --change-summary "<change-summary>" \
  --review-question "<review-question>"

.venv/bin/python3 tools/api_providers/run_review.py \
  --variant post_write_verification_google \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --phase post_write_verification \
  --criteria-file .reviewcompass/evidence/review-runs/<run-id>/review-target.md \
  --prompt-manifest-path .reviewcompass/evidence/review-runs/<run-id>/prompt-manifest.yaml \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py list-pending \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py decide \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --finding-id <finding-id> \
  --final-label must-fix \
  --decision-reason "<reason>" \
  --decision-actor human \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/api_providers/review_triage.py write-manifest \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --out auto \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/check-workflow-action.py next --json
```

API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target と prompt manifest を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md> --prompt-manifest-path <prompt-manifest.yaml>` を実行することである。外側から `zsh -c` で包まない。API key は配布物や設定ファイルへ書かず、利用者の shell 初期化で読み込まれる環境変数から渡す。Claude Code などの操縦実行面では、子プロセスの `ANTHROPIC_API_KEY` と `GEMINI_API_KEY` が空文字列へ上書きされることが確認済みである。一方、`OPENAI_API_KEY` は同じ確認では上書きされていない。このため `run_review.py` / `run_role.py` entrypoint 内で、環境変数が未設定の場合に `~/.zshrc` を読み直して API key を補完する。補完後も key が得られない場合は API key 未設定として fail-closed する。

`prepare_post_write_review.py` は `review-target.md`、`review-target.yaml`、`prompt-manifest.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、source materials、target file contents、scope / out-of-scope、finding policy、機微情報チェック結果を含める。`prompt-manifest.yaml` には `review_prompt_materials.target_files` と `review_prompt_materials.source_materials` を `content_mode: full_text` と `content_sha256` 付きで記録する。機微情報らしい文字列を検出した場合、または prompt manifest audit が DEVIATION の場合は fail-closed し、外部 API review へ進まない。

`next_action.target_files` が複数ある場合は、`prepare_post_write_review.py` と `run_review.py` の両方で `--target` を複数回指定して同じ review-run に束ねる。API review-run の成否確認は、`review-target.md`、`review-target.yaml`、`prompt-manifest.yaml`、`review_summary.md`、`rounds.yaml`、`model-result-summary.yaml`、`raw/`、`parsed/`、`prompts/`、`target-manifest.yaml` が同じ `--review-run-dir` に生成され、`rounds.yaml` の `target_files`、`criteria_source_path`、`prompt_manifest_path`、provider、model、prompt/raw/parsed path が今回の対象と一致することで行う。

API 呼び出しが失敗した場合は、まず上の正本手順を再確認する。`import` エラー、`argparse` エラー、引数不一致は起動手順または実装の問題であり、外部送信ポリシーや provider 側障害と混同しない。`ConnectError`、名前解決失敗、接続不能が出た場合は sandbox network 制限の可能性を先に疑い、同じ正本コマンドをネットワーク実行が許可された実行面で再実行する。API key 未設定のエラーは `~/.zshrc` から対象 provider の環境変数が読み込まれているかを確認する。

`post_write_verification` では API 経路の variant を明示する。小規模既定は `--variant post_write_verification_google`、大規模または 3 系統検証が必要な場合は `--variant <post-write-api-variant>` として、`config/api-settings.yaml` の `context: post_write_verification` かつ API provider だけで構成された variant を選ぶ。CLI 経路を含む default variant に暗黙フォールバックしてはいけない。

API レビュー結果を得た場合は、raw 参照、モデル別要約、三段階トリアージ（`must-fix`／`should-fix`／`leave-as-is`）を利用者へまとめて提示する。`ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を `decide` する場合、または重要件を含む run から manifest を生成する場合は、承認を記録した `--approval-record` が必須である。承認レコードには `approved_by: user` または `approved_by: proxy_model`、`review_run_id`、`summary_presented_to_user: true`、`triage_presented_to_user: true`、`approved_finding_ids`、必要に応じて `approved_final_labels` を含める。`approved_by: proxy_model` の場合は、`proxy_model_id` と finding ごとの `proxy_decisions` を含め、各 decision file が raw response、候補案、採用案、判断理由、最終ラベルを保持する。

`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。manifest は post-write validation の途中記録ではなく、commit 直前の最終封印である。`triage.yaml` に `decision_status: human_required` が残る場合、重要件の利用者承認が確認できない場合、または review-run の target set に含まれない未コミット post-write target が残る場合は manifest を生成しない。manifest 作成後は対象ファイルを編集せず、stage / approval / commit へ直行する。

この生成停止条件は、現在の review-run から新しい最終 manifest を作る場合の規則である。既存の post-write manifest が現在の対象ファイルと一致し、かつ未解決の本質的指摘を含む場合は、`next --json` が `post_write_human_decision_required` と `next_action.manifest` を返す。

<a id="lightweight_self_check"></a>

### `lightweight_self_check`

notes / 履歴 / 判断材料の未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` を API post-write verification ではなく軽量自己精査で確認する。

軽量自己精査の対象は `docs/notes/` 配下と、単独変更の `TODO_NEXT_SESSION.md` とする。`docs/notes/` は議論記録、判断経緯、過去メモ、参考情報を置く場所として扱い、正本仕様・運用規律・レビュー判定そのものではないため、API review ではなく自己検査で確認する。`docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`stages/completed/` は正本または完了記録として厳格に扱う。notes から正本へ昇格する内容は、該当する正本ファイルへ移した時点で strict な `post_write_verification` 対象とする。

`TODO_NEXT_SESSION.md` は更新頻度が高い次セッション導線であり、進捗整理・次タスク・現在状態の更新だけなら API review ではなく軽量自己精査で扱う。ただし、同じ未コミット差分に strict な `post_write_verification` 対象が含まれる場合は、TODO も同じ strict 検証の `target_files` に同梱する。

軽量自己精査では、API review を呼ばず、次だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

完了記録は `.reviewcompass/post-write-verification/*.yaml` に置き、`required_verifiers` と `completed_verifiers` は `lightweight_self_check` とする。`target_files` と `target_sha256` は通常の post-write manifest と同じく対象全体を覆う。

`post_write_verification` 対象と `lightweight_self_check` 対象が混在する場合は、`post_write_verification` を優先する。strict 側が完了した後、軽量対象が残っていれば `lightweight_self_check` を返す。

<a id="post_write_policy_violation"></a>

### `post_write_policy_violation`

post-write-verification pending 中に禁止変更がある。通常ワークフローへ進まず、`next_action.forbidden_files` を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。

現行実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py`、`templates/`、または他の post-write 対象と混ざった `docs/disciplines/` 配下の変更があると逸脱になる。

<a id="post_write_human_decision_required"></a>

### `post_write_human_decision_required`

既存の post-write manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。

これは、現在の review-run で `triage.yaml` に `decision_status: human_required` が残ったまま新しい最終 manifest を生成する状態ではない。その場合は manifest 生成前に停止し、triage の判断または承認を先に解決する。

### `stage`

通常ワークフロー上の次タスクが決まっている。`feature`、`phase`、`stage` の示す作業だけを扱う。

`stage` が `triad-review` の場合、review-run の開始前に使用 variant と role ごとの path／provider／model を確定し、曖昧なまま開始しない。review-run に使うプロンプトは [[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）で設計する。API review-run 完了後は、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、raw 参照、モデル別要約、同根所見クラスタ、`must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案、重要件の平易な説明を利用者へ提示して停止する。詳細手順は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2` を正本とする。

### `cross_feature_stage`

機能横断段に進む。`feature` は `all_features` になる。`recheck_items` がある場合は上流変更の織り込みを含める。`required_inputs` に `unresolved_cross_scope_items` があり、`unresolved_count` が 0 より大きい場合は、`read_policy` に従って未消化の持ち越し所見だけを確認する。ReviewCompass では互換情報として `pending_cross_feature_findings` も返るが、一般化された判断根拠は `required_inputs` とする。

自律・並列で機能横断段を試行する場合は、通常の review-wave 完了判定に入る前に `autonomous-plan` を作成し、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で検査する。計画には `recheck_items` と `stages/feature-dependency.yaml` から分かる依存を明示し、上流 recheck 対象を下流判断より先に置く。同じ worktree で並列化してよいのは読取調査または差分を残さない確認に限る。新しい依存、暗黙依存、未記録依存、または上流 recheck の下流反映が必要だと分かった場合、その作業単位は停止し、機能横断段の実施記録に blocked として記録してから統合判断へ戻す。

機能横断段の実施記録は、単一 feature 配下に置かず `.reviewcompass/specs/_cross_feature/reviews/` に置く。標準ファイル名は `.reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md` とし、`feature: all_features`、対象 phase/stage、確認した feature 範囲、持ち越し件数、recheck 結果、実行した検証コマンド、判断結果を記録する。`_cross_feature` は実 feature ではなく、横断段成果物だけの名前空間である。

<a id="commit_stop_point"></a>

### `commit_stop_point`

通常 workflow の phase 終端または reopen 手続き上の停止点に到達している。`required_action: commit_stop_point` の場合、次 phase / 次 gate へ進まず、利用者の明示的な commit 指示を待つ。

利用者が commit を指示した直後は、Git index への追加（`git add`）や approval record を作る前に `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、理由と次に許可されている action だけを報告する。

通常 workflow では、`intent.approval` または `feature-partitioning.approval` が全 feature で完了し、該当 phase の workflow_state または成果物に未コミット変更がある場合に返る。`blocked_by.phase`、`blocked_by.stage`、`blocked_by.dirty_paths` を確認する。`commit-preflight` が `OK` を返した後に対象差分を `git add` し、guarded commit の通常手順へ進む。commit 後に作業ツリーが clean であれば、同じ停止点を返し続けず次 phase の action へ進む。

reopen 手続きでは、`reopen_in_progress` の `required_action: commit_stop_point` として返る。`blocked_by.kind` と `blocked_by.gate` を確認し、reopen 手続きファイルを含む停止点 commit を行う。

<a id="commit_mixing_risk"></a>

### `commit_mixing_risk`

commit unit が固定した対象外の staged file が混入している。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files`、`extra_staged_files`、`path` を確認する。

利用者に、対象外ファイルを別 commit unit / blocking unit へ分けるか、現在の commit unit を再作成してよいかを確認する。対象外ファイルを理由なしに同じ commit へ混ぜない。

<a id="commit_unit_stale"></a>

### `commit_unit_stale`

commit unit が現在の staged 内容と一致していない。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files` と `path` を確認する。

staged 内容を commit unit に合わせて戻すか、現在の staged 内容に合わせて commit unit を再作成する。古い commit unit のまま承認 record や commit execution delegation を作らない。

### `upstream_recheck`

完了済み workflow であっても、上流成果物が下流成果物より新しいため、下流へ進む前に再確認が必要である。`upstream_phase`、`phase`、`stage` を確認し、`phase.stage` に示された作業を次作業として扱う。たとえば intent 更新後は feature-partitioning の確認、requirements 更新後は design の再確認、tasks 更新後は implementation の再確認を先に行う。

この kind が返った場合、記憶や直前の会話から requirements、design、tasks、implementation へ飛ばない。必ず `next_action.phase` と `next_action.stage` に従い、上流から下流へ順に反映する。

<a id="feature_definition_required"></a>

### `feature_definition_required`

feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない（verdict OK）。

`next_action.reason`（立ち上げ案内の本文）と `current_state.feature_dependency_source`（解決元）を確認する。`feature_dependency_source` が null ならファイル自体が探索順（`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml`）のどこにも存在せず、ファイルパスが入っていればそのファイルはあるが `feature_order` キーが未定義または不正である。前者は分割結果の記録から、後者は既存ファイルへの `feature_order` キーの追記から始める。

新しい作業を始めず、intent と feature-partitioning を実施し、承認された分割結果（機能ごとの依存の主張と理由、順序の導出を含む）を `.reviewcompass/feature-dependency.yaml` の `feature_order` キーに記録する。記録後に `next` を再実行する。feature 立ち上げの手順は `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。

なお、`feature_order` と `depends_on` の整合違反（依存される機能が先に並んでいない、循環依存がある）は本 kind ではなく `unknown`／DEVIATION（fail-closed）になる。理由に従って `feature-dependency.yaml` を修正する。

### `completed`

全 workflow_state が完了している。通常の次タスクはない。

利用者指示により maintenance、reopen、または新規 workflow を開始できる。別作業を開始する前には、原則として `work-unit preflight-start` を実行し、`start_allowed` と `blocking_reasons` を確認する。maintenance を始める場合は、その後に `maintenance_in_progress` の事前調査と開始条件を確認する。

### `unknown`

状態判定できない。推測で進めず、`reasons` と `current_state` を利用者へ報告する。

## 3. 共通禁止事項

- `next` を実行せずに次作業を提案しない。
- `resume_in_progress`、`parent_resume_pending`、`reopen_in_progress`、`post_write_verification`、`post_write_policy_violation`、`post_write_human_decision_required` を通常ワークフローより後回しにしない。
- `lightweight_self_check` を通常ワークフローより後回しにしない。
- `reopen_classification_required` を「再確認で足りる」と独断して下流成果物を更新しない。
- `next_action` と異なる side track に入る場合、または `next` 判定自体を修復する場合は、maintenance in-progress を作らずに編集を始めない。
- 事前調査を省略して maintenance を始めない。影響範囲・依存関係・ブロッカーの確認が済んでいない状態で in-progress YAML を作成しない。
- spec.json の workflow_state 変更、commit、push は不可逆操作として扱い、対応する precheck サブコマンドを実行する。
- 検証者は `target_files` 全体を見る。ファイルごとの分業を独立多重チェックとして扱わない。
- 本質的指摘を独断で逐語的指摘に落とさない。迷う場合は利用者へ上げる。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md

content_mode: full_text
content_sha256: 7a4698ec32170ced27d6f7dad1910a4e5a9b64d4639c74892c37cf60cee999a8

```text
# API Review Prompt Quality

最終更新：2026-06-23

本文書は、API 経由の review-run を開始する前に、レビュー用プロンプト自体を品質確認するための運用手順である。

この手順は、特定 feature や特定 phase に閉じない。各 review-run は、この共通手順に phase / gate / feature 固有の上流接続要件を差し込んで使う。

利用者が任意の場面で API review を依頼する場合は、利用者が伝えたレビュー要件を `User Review Requirements` として保持し、criteria 作成・prompt quality review・実 review-run の全段で照合する。

## 1. 目的

API review-run の品質は、モデルや provider だけでなく、プロンプトの作り方に強く依存する。

レビュー用プロンプトの監査は、高リスク時だけの追加確認ではなく、API review-run の標準ゲートである。プロンプトが target / source / scope / output contract を誤ると、その後の raw response、parsed YAML、triage、proxy decision、実装修正がすべて誤った入力に基づく。したがって、prompt audit にかかるコストはレビュー外の余分なコストではなく、レビュー品質を成立させるための本体コストとして扱う。

特に、次の失敗を防ぐ。

- `--target` が実際の審査対象本文ではなく、作成者の要約になっている
- `--criteria-file` と `--target` が同一の author-written summary になっている
- source materials が path-only で、モデルが本文を読めない
- review target / source materials / out of scope が分離されていない
- 上流意図伝達レビューで、上流の目的・責務境界・受入条件・禁止事項が prompt に含まれていない
- 利用者が指定したレビュー目的、重視点、範囲、禁止事項が main によって狭められる、広げられる、または別の問いに置き換えられる
- output contract が曖昧で parser / triage に載らない
- プロンプトが結論を誘導している

## 2. 役割

APIレビュー用プロンプト品質確認は、次の 2 者レビュー体制で行う。

| 役割 | 担当 | 目的 |
|---|---|---|
| main | 操縦中の LLM | API review criteria 素案を作る |
| adversarial | 別モデル | 素案の欠落、誘導、対象違い、材料不足、範囲ミスを探す |
| judgment | 別モデル | adversarial 所見の反映後、その prompt を実 review-run に使ってよいか判定する |

ここでいう 2 者レビュー体制は、作成者である main を除き、adversarial と judgment の 2 者で品質確認する運用を指す。

## 3. 入力分離

API review-run では、criteria と target を分離する。

- `User Review Requirements`: 利用者が指定したレビュー目的、判断対象、重視点、範囲、禁止事項、必要出力
- `--criteria-file`: レビュー目的、背景、上流材料、必須チェック、範囲外、finding policy を含む
- `--target`: 実際に審査する本文

`User Review Requirements` は criteria の上位入力であり、criteria 作成時に失われてはならない。main は、利用者要件を criteria に構造化して写し、どの要件がどの review task / required check / out of scope / finding policy に対応するかを確認できる形にする。

禁止:

- criteria と target に同じ review wrapper / author-written summary を渡す
- target manifest が実審査対象を含まない状態で gate 完了根拠にする
- target 本文を入れず、target の要約だけで review-run を実行する
- 利用者が求めたレビュー範囲を、合意なく狭める、広げる、または別目的の review に置き換える

## 4. User Review Requirements

利用者が任意の場面で review を依頼する場合、main は prompt 作成前に次を整理する。

1. review purpose: 欠陥検出、採否判断、上流接続確認、回帰確認、比較評価など
2. review object: artifact、prompt、設計案、修正案、実装差分など
3. review focus: API設計、互換性、セキュリティ、運用境界、上流要件、実装可能性など
4. scope boundaries: 含める範囲、含めない範囲、まだ判断しない下流工程
5. source materials: 根拠にする要件、設計、過去判断、制約、禁止事項
6. output requirements: findings、severity、採否、懸念点、修正案、比較軸など
7. prohibited actions: commit、push、phase 完了、人間承認代行、未合意の仕様変更など

利用者要件が曖昧な場合でも、main が勝手に確定しない。作業可能な仮定として扱う場合は、criteria に仮定を明記し、prompt quality review で妥当性を確認させる。

## 5. API 送信可能材料の基準

API review-run / proxy_model 判断では、判断に必要な ReviewCompass リポジトリ内の仕様、設計、タスク、レビュー所見、構造化要約、証跡パスを prompt に含めてよい。

これは、次の条件を満たす場合に限る。

1. 利用者が当該 API review-run / proxy_model 判断の実行を明示承認している。
2. API key、token、password、nonce などの秘密値を含めない。
3. メールアドレス、電話番号など個人識別情報を含めない。
4. 第三者との契約上、外部送信できない非公開情報を含めない。
5. 判断に不要な全文ログや周辺ファイルを含めず、判断項目に必要な抜粋または構造化要約に絞る。

単にリポジトリ内の未公開仕様・設計・レビュー要約であることだけを理由に、API 送信を禁止しない。ReviewCompass の API review / proxy_model 運用では、それらは通常のレビュー材料である。

ただし、利用者が外部送信を避ける方針を示した場合、または上記 2〜4 に該当する情報が含まれる場合は、伏字化、抽象化、または外部 API を使わない判断へ切り替える。

## 6. Main が作る criteria の必須要素

criteria file は、少なくとも次を持つ。

1. review task
2. why this review exists
3. user review requirements
4. required disciplines
5. review target
6. source materials
7. required checks
8. out of scope
9. finding policy

source materials は path-only にしない。必要な本文抜粋または構造化要約を、モデルが読める形で criteria に含める。

front matter に path を置く場合は、provenance なのか model-readable material なのかを明示する。

criteria は、利用者要件を単に引用するだけでなく、review task / required checks / out of scope / finding policy へ反映する。

## 6.1 Main Preanalysis

main は criteria 素案を書く前に、対象 review requirement と source materials を直接検討し、判断に必要な材料、判断項目、分割要否、未読資料、機微情報リスクを整理する。

main preanalysis は、prompt 作成のための材料揃えと判断点発見であり、reviewer に対する正解ではない。preanalysis を後続の監査や prompt に含める場合は、仮説・source discovery aid として明示し、reviewer に source materials から独立再構成させる。

main preanalysis には少なくとも次を含める。

- 読んだ source materials と使用目的
- 判断項目と、それぞれの target / source / out of scope
- 複数 prompt に分割すべき独立判断の有無
- prompt に含めるべき model-readable source material
- 送信してはいけない、または最小化すべき機微情報
- 未解決・未読・推測に留まる事項

preanalysis 内の所見は、`open`、`resolved`、`superseded`、`used_for_context` など現在性を区別できる形で扱う。解決済み所見を open な欠陥として prompt bundle に残すと、reviewer を誤誘導するためである。

### 6.2 Behavior-Path Claim の材料選定

review requirement が「あるトリガーから、意図した機械手順へ進むか」「短い利用者指示が gate を bypass しないか」「特定の guard が必ず作動するか」のような behavior-path claim / 実行経路 claim を含む場合、main preanalysis は変更文書だけを target/source にしてはならない。

この場合、source materials には少なくとも次を含める。

- trigger resolver または利用者発話を operation に写像する map
- operation preflight、guard、gate、runner など実行経路上の制御実装
- その経路を固定するテスト、または存在しない場合は「未固定」と分かる証跡
- 変更対象文書、effective prompt、plan / TODO / checklist など経路上の入力成果物
- 期待される停止点、禁止 bypass、許可される次操作

対象が「文書の整合性」ではなく「動作上の強制」なら、変更された guidance / prompt だけを target にした review-run は不足である。文書に要件が書かれていても、trigger resolver、operation preflight、runner、test がその要件を読んでいなければ behavior-path claim は成立しない。

### 6.3 Review Question Decomposition

main は criteria 作成前に review question decomposition を行う。整合性確認だけの一括質問にしない。

分解では、利用者要件または workflow 要件を要求 claim ごとの required check に写す。各 required check は、次を明示する。

1. 何を成立させる claim か
2. どの target / source material で判定するか
3. finding にすべき失敗条件は何か
4. out of scope は何か

例: 「ショートリクエストが bridge を bypass しない」を検証するなら、単に「prompt と map が整合しているか」と聞かない。`次へ`、`進める`、`継続` などの短い発話がどの trigger resolver / operation preflight / effective prompt に到達し、どこで plan materialization status、TODO/checklist coverage、quality audit を確認するかを required check に分解する。

review question が複数 claim を含む場合は、claim ごとに prompt を分けるか、少なくとも required checks を分離して reviewer が各 claim を個別に pass/fail できる形にする。

## 7. Phase 別の上流接続

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` が適用される review では、phase ごとに次を確認する。

| phase | target | source materials |
|---|---|---|
| requirements | `requirements.md` | upstream decision materials, reopen classification, planning notes, user decisions |
| design | `design.md` | `requirements.md` |
| tasks | `tasks.md` | `requirements.md`, `design.md` |
| implementation | implementation artifacts | `requirements.md`, `design.md`, `tasks.md` |

source materials は背景・意図伝達確認のために使う。現在 phase の correctness だけを target として判定し、下流 phase の correctness を同時に判定しない。

利用者が指定した review focus が phase 標準の観点と異なる場合は、両者の関係を criteria に明記する。phase 標準の必須検査を外す必要がある場合は、利用者合意なしに外してはならない。

## 8. Prompt Quality Review

main が criteria 素案を作ったら、実 review-run の前に preanalysis sufficiency audit と prompt quality review を行う。

標準手順は次の順序とする。

1. main preanalysis
2. preanalysis sufficiency audit
3. API review criteria draft
4. prompt quality review
5. 実 review-run
6. raw / parsed / model summary / triage
7. 必要に応じて proxy_model decision

通常の prompt quality review の前に、`templates/review/main_preanalysis_sufficiency_audit_criteria_template.md` を使って preanalysis sufficiency audit を行う。この監査では、reviewer に source materials から judgment item を独立再構成させたうえで、main preanalysis を仮説として比較させる。main preanalysis を正解として渡してはならない。

preanalysis sufficiency audit では、target bundle に次を含める。

- 利用者または workflow の review requirement
- 判断に必要な source materials の本文または構造化抜粋
- main session LLM の preanalysis
- proposed API review criteria または prompt

監査結果の `required_prompt_changes` を反映してから、通常の `templates/review/api_review_prompt_quality_criteria_template.md` による prompt quality review へ進む。

preanalysis sufficiency audit は、次の欠陥を検出するための標準ゲートである。

- source selection の漏れ
- source summary と原文対応の不足
- main preanalysis の stale / resolved 所見による anchoring
- 複数の独立判断を 1 prompt に押し込む粒度誤り
- 誤検出防止文言が、重要な欠陥検出まで抑制する framing bias
- output contract と runner / parser の不一致
- behavior-path claim に必要な trigger resolver / operation preflight / runner / test の欠落
- review question decomposition の不足による、整合性確認だけの一括質問化

review question は 1 prompt につき原則 1 つにする。複数の独立した採否判断、クラスタ判断、設計論点判断を 1 つの prompt に押し込まない。

複数判断がある場合は、判断項目ごとに prompt を分ける。各 prompt は、その判断に必要な source findings、上流材料、対象本文要約、out of scope、output contract だけを持つ。共通背景を入れる場合も、個別判断の焦点を曖昧にしない量に抑える。

adversarial には、`templates/review/api_review_prompt_quality_criteria_template.md` を criteria として渡し、criteria 素案を target としてレビューさせる。

利用者要件がある場合、prompt quality review では次も確認する。

- 利用者要件が criteria に保持されている
- 利用者要件が review task / required checks / out of scope / finding policy に反映されている
- main が利用者要件を合意なく狭めたり広げたりしていない
- 利用者が禁止した操作や判断代行が prompt に混入していない
- 複数の独立判断を 1 prompt に押し込んでおらず、判断項目ごとに注意が分散しない粒度になっている

adversarial の所見を main が反映した後、judgment に同じ quality criteria と adversarial 所見を渡し、使用可否を判定させる。

judgment が `findings: []` を返した場合だけ、実 review-run へ進める。

judgment が finding を返した場合は、prompt を再修正し、必要に応じて再度 judgment へ回す。

高リスクまたは実行経路 claim を含む review では、single-model findings: [] を単独の完了根拠にしない。根拠説明なしの 0 件、特に raw response が `findings: []` のみの場合は、対象材料と問いが狭すぎる可能性を疑い、次のいずれかを行う。

- 3-way の独立 review に切り替える
- reviewer に claim ごとの pass/fail rationale と参照 material を出力させる
- main preanalysis sufficiency audit へ戻り、source selection と review question decomposition をやり直す

## 9. 実 Review-Run

prompt quality review を通過した後、実 review-run を実行する。

複数 prompt に分けた場合は、各 prompt の prompt quality review 通過証跡と実 review-run / proxy decision 結果を判断項目ごとに保存する。一括 summary は後段で作ってよいが、個別判断の raw / parsed / decision 証跡を上書きしない。

実行時には次を確認する。

- `target-manifest.yaml` に実審査対象が入っている
- `rounds.yaml` の criteria は使用可判定済み criteria である
- raw / parsed / model-result-summary / triage が生成されている
- 利用者提示ゲート前に、raw 結果概要、モデル別 summary、同根クラスタ、三段階トリアージ案をまとめる
- 実 review-run の結果を、利用者要件に含まれていない操作承認や phase 完了根拠へ拡張しない

## 10. 成果物配置

推奨配置:

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-prompt-quality-run/
  api-review-criteria.md
  prompt-quality-review-criteria.md
  variant-role-assignment.yaml
  raw/
  parsed/
  prompts/
  rounds.yaml
  model-result-summary.yaml
  prompt-quality-summary.md
```

実 review-run は別ディレクトリに分ける。

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-review-run/
```

prompt-quality-run は、実 review-run の gate 完了根拠ではない。実 review-run の criteria を使ってよいことを示す補助証跡である。

## 11. 今回の事例から得た規則

2026-06-20 の `workflow-management` design triad-review では、旧 run が `review-target.md` を criteria と target の両方に使い、`findings: []` になった。

その後、prompt quality review を挟み、`design.md` を実 target として再実行した v2 run では 15 件の所見が出た。

同日の `workflow-management` implementation Req14 approval gate prompt audit では、preanalysis sufficiency audit により、source summary の原文対応不足と、誤検出防止文言が approval gate bypass 検出を鈍らせる framing bias が検出された。これは、prompt audit が形式確認ではなく、実 review-run の欠陥検出力そのものを左右することを示す。

2026-06-23 の plan-todo-checklist materialization PTC-4 post-write review では、prompt が「updated effective prompts and discipline map の整合性確認」に寄りすぎ、短い `次へ` / `進める` から plan-to-TODO bridge へ到達する実行経路を検証できなかった。target は guidance / effective prompt に寄り、trigger resolver、operation preflight、runner、経路テストを含めなかったため、single-model findings: [] が返っても behavior-path claim の完了根拠としては弱かった。

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む
- behavior-path claim では、変更文書だけでなく trigger resolver / operation preflight / runner / test を source materials に含める
- review question は要求 claim ごとの required check に分解し、整合性確認だけの一括質問にしない
- 高リスクまたは実行経路 claim では、根拠説明なしの single-model findings: [] を完了根拠にしない

## 12. 停止点

prompt quality review は、実 review-run の開始許可であり、次の操作を自動許可しない。

- `spec.json` 更新
- phase / gate 完了
- proxy_model 判断
- design / requirements / tasks / implementation 本文修正
- commit
- push

これらはそれぞれの workflow gate と利用者承認に従う。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_post_write_verification.md

content_mode: full_text
content_sha256: b5db5b8a11c57304976fd13a03e15fd39cbc44cb7b6f206b579065b0f62a10e2

```text
---
name: post-write-verification
description: ワークフロー段の外側にある正本文書への書き込み後、起草者と異なる検証者による独立検証を必須化する。検出は逐語的指摘と本質的指摘に分類して処理する
metadata:
  type: feedback
---

ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書への書き込み後、書いた本人とは別の検証者による独立検証を必ず実施する。検出が出たときの処理は動作仕様ファイル `.reviewcompass/specs/workflow-management/post-write-verification-spec.yaml` の収束基準に従う（逐語的指摘は弾き、本質的指摘は人へ上げる）。

**適用範囲：**

- 対象：運用文書、規律文書、作業メモ、監査記録、再オープン記録など、通常ワークフロー段の成果物ではない正本文書
- 対象外：`.reviewcompass/specs/`（ワークフロー段で検証）、spec.json 状態変更（workflow precheck で検証）、`docs/archive/`、テスト用一時ファイル
- 対象外（性質ベース）：**機械生成され引用元を明記した派生記録**（front-matter に `generated_by: session-record-extractor` 等の来歴を持つもの）。独自の主張を持たず引用元からの決定論的な派生であり、独立検証が想定する「合意の取り違え・参照誤り・既存記述との矛盾」を持たないため対象外とする。これらは独立検証ではなく「**来歴の刻印＋引用元からの再生成突き合わせ（再現性）**」で担保する（取り込み時に引用元から再生成して 1 バイト一致を確認し、来歴〔引用元のハッシュ・ツール版・機微除去ルール版〕を刻む）。判定はディレクトリでなく来歴マーカーで行う
- 対象外（性質ベース）：**機械が吐く捕捉物**（API 生出力・parsed・triage の review-run 一式、自律並列の走行台帳、書き込み後検証の API 結果ログ）。これらも独自の主張ではなく走行・実行の忠実な捕捉であり、独立検証ではなく**走行・再実行・再生成**で担保する。台帳の `authorization` 等の埋め込み値は、承認レコードや autonomous-plan 検査など別の層で守られる。新規分は `.reviewcompass/evidence/` 配下へ置かれ docs 配下に出ない。docs 配下の凍結旧配置はディレクトリ単位で対象外とする（`**/review-runs/**`、`docs/logs/autonomous-parallel/`、`docs/notes/post-write-verification-review/`）。なお**監査・計測記録**（例：`docs/discipline-compliance-reports/`）は主張を含むため対象に残す
- 新規ディレクトリ：判定に迷えば対象側に倒す

**検証者の要件：**

- 独立性：起草者と異なる検証者
- 複数体並列：大規模時は複数の独立系統で検証する
- small 時は 1 体検証を許容するが、起草者と異なる独立系統を使う
- 情報最小化：合意内容（決定事項の箇条書きのみ、判断理由文を含まない）と書き込み結果のみ渡す。起草者の解釈・判断理由・議論ログは渡さない
- フォールバック：独立系統が利用できない環境では書き込みを fail-closed で阻止し、人へエスカレーションする。同一系統内代替は既定では認めない。人が個別事案ごとに明示承認した場合に限り例外的に代替可（記録に残す）

**発火規模制御：**

- 小規模（既存節への 1〜2 行追記・字句修正・既存リスト項目追加）：1 体検証
- 大規模（新節起草・構造変更・複数節改訂）：3 体検証
- 判定に迷えば大規模側に倒す

**検査観点 4 項目（yaml の `inspection_criteria` と対応）：**

1. `agreement_reflection`：合意内容が書き込みに反映されているか
2. `reference_accuracy`：数値・出典・固有名詞が正本と一致するか
3. `existing_record_consistency`：既存記述との齟齬がないか
4. `internal_logic`：内部の論理矛盾がないか

**失敗時の挙動：**

- 検出の処理は動作仕様ファイル `post-write-verification-spec.yaml` の収束基準に従う。**逐語的指摘**（合意の意味に影響しない字句・表現レベル）は収束を妨げず、機械的に直せるものは直し、直せないものは記録に留める（再検証ループは回さず、修正時は起草者が機械的反映を 1 回確認）。**本質的指摘**（合意の解釈・設計判断に触れうるもの）は起草者が独断で修正せず人へ上げる。逐語か本質か迷えば本質側に倒す。
- 収束＝未解決の本質的指摘がゼロ。逐語的指摘だけが残る状況は実質収束。
- 深刻度（高／中／低）は検証者の**報告フォーマット用途**。

**実装段階：**

- **段階 1**：起草者が書き込み完了を認識し、独立検証者を呼び出して検証する。阻止は起草者の判断
- **段階 2**：書き込み後フックスクリプトによる機械的な検証起動と阻止
- **段階 3（スコープ外、将来）**：Git/IDE フックによる機械的な検証起動と阻止（commit／push 時のフックで未検証の書き込みを検出して差し戻す）

**本規律の改訂：**

- 本規律の改訂時は本規律を適用する。ただし改訂前の設定に従って検証者を起動する
- 改訂時は**変更の影響評価を実施**する（既存設定の意味変化、新規必須項目の追加、依存関係の変化、過去成果物への波及等を点検し、影響評価結果を改訂記録に残す）
- 改訂内容に破壊的変更（既存設定の意味変化、新しい必須項目の追加等）がある場合は人の明示承認必須

**過去成果物：**

- 遡及適用しない
- 過去分の誤りは再オープン手続きで発見の都度修正

**Why:** 起草者の自己検証だけでは、合意内容の取り違え、参照誤り、既存記述との矛盾を見落とす可能性がある。書き込みを「合意内容の機械的清書」ではなく「書き込み＋独立検証」の不可分な単位として扱う。費用対効果と体験への配慮から、ワークフロー段で検証される文書は対象外（多層防御の役割分担）。

**How to apply:**

- 対象文書の書き込み完了を起点に `reviewcompass.yaml#review.post_write_verification` 設定で検証者を起動（段階別に手段が異なる、上記実装段階節）
- 書き込み規模を判定（`scale_classification`、判定不能なら large）
- 検証者には合意内容（決定箇条書きのみ）と書き込み結果のみ渡す（`information_policy`）
- 検査観点 4 項目で評価、深刻度を報告フォーマットとして使用
- 検出は動作仕様ファイルの収束基準で分類処理（逐語は弾く、本質は人へ）
- 再検証ループは上限まで、超過は人間エスカレーション

**関連規律：**

- [[facts-vs-interpretation]]（書き込み前の機械的照合と相補的）
- [[workflow-precheck-invocation]]（spec.json 状態変更の事前検査と相補的）
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/specs/workflow-management/post-write-verification-spec.yaml

content_mode: full_text
content_sha256: 3e72e7431ccef008e0f87ac841053aed11b88f4350a027979661ffe1c6291d81

```text
# post-write-verification 動作仕様（収束基準）
# 書き込み後の独立検証で、検出時の処理を定義する正本。デプロイ対象。
# 規律 docs/disciplines/discipline_post_write_verification.md が本ファイルを参照する。

meta:
  name: post-write-verification-spec
  scope: 書き込み後検証の検出時の収束基準
  owner: workflow-management
  related:
    discipline: docs/disciplines/discipline_post_write_verification.md  # 行動規範
    config: "reviewcompass.yaml#review.post_write_verification"          # 設定値（モデル・逐語リスト）

convergence_criterion:
  classify:
    - type: literal                    # 逐語的指摘
      action: skip                     # 収束を妨げない
      fix_if_mechanical: true          # 機械的に直せるものは直す
      record_if_not_fixable: true      # 直せないものは記録に留める
      rerun_loop: false                # 再検証ループは回さない
      post_fix_recheck:                # 逐語修正後の確認
        enabled: true
        actor: drafter                 # 起草者
        method: grep_or_read           # 機械的反映を 1 回だけ確認
        scope: mechanical_reflection_only  # 新たな実質的食い違いの捕捉は求めない
    - type: substantive                # 本質的指摘
      action: escalate_to_human        # 起草者が独断で修正せず人へ上げる
  tie_break: substantive               # 逐語か本質か迷えば本質側に倒す
  convergence_definition: 未解決の本質的指摘がゼロになれば収束。逐語的指摘だけが残る状況は実質収束。
  no_autonomous_loop: true             # 人なしの自律ループは設けない
  description: |
    検証者が出した指摘を逐語的指摘と本質的指摘の 2 種類に分類して処理する。
    逐語的指摘は合意の意味に影響しない字句・表現レベル（文体・言い回しの好み、
    具体例の有無、付帯情報の省略、合意の意味を変えない用語の言い換え・付加）。
    本質的指摘は合意の解釈・設計判断に触れうるもの。
    判定に迷えば本質側（人へ）に倒す（安全側原則。本物の見落としのコストは
    収束遅延より高い。少数の系統だけが本質を突く場合があるため、系統数の多寡で
    切り捨てない）。本質的指摘は独自判断での仕様修正禁止と同原則で人へ上げる。

literal_patterns:
  values_in: "reviewcompass.yaml#review.post_write_verification.literal_patterns"  # 初期リストの値は設定側
  management: |
    逐語的指摘とみなすパターンは拡張可能なリストで管理する。初期値は description の類型。
    新たなパターンの追加は規律変更扱いとし、人の明示承認を要する（恣意的な拡大の防止）。
    起草者が「逐語」と分類した指摘は記録に残し、人が事後に検証できるようにする
    （本質を逐語と誤分類して握りつぶすことの防止）。

verifier_availability:                  # 検証者の応答可用性（必要な独立系統が揃わない場合）
  on_incomplete_responses: escalate_to_human
  same_family_substitute: requires_explicit_approval  # 同一系統内代替は既定で不可、明示承認時のみ
  description: |
    api_mediated（独立 API 経由）の検証で、必要な独立系統のうち一部が応答を返さない
    （API エラー・クォータ超過・タイムアウト等で揃わない）場合、起草者は揃った少数の
    系統だけで収束・確定させない。人にエスカレートし、(a) 原因確認のうえ再試行、
    (b) 揃った範囲で収束とみなす、(c) 別の独立系統で代替、のいずれかの判断を仰ぐ。
    規律 discipline_post_write_verification.md のフォールバック節を実行時ルールに反映する。
  rationale: |
    必要な独立系統が揃わないまま収束扱いにすると、検証者の独立性が崩れるため。

scope_of_application: |
  本収束基準は書き込み後検証（docs 配下の正本文書）にのみ適用する。
  ワークフロー段（.reviewcompass/specs/ 配下、5 段で検証）には適用しない（多層防御の役割分担）。
  設定・動作仕様 yaml（config/**/*.yaml、runtime/config/**/*.yaml、stages/*.yaml、
  .reviewcompass/specs/**/*.yaml）は本補助層 D ではなく補助層 E（yaml 監査）が担当する。
  詳細は docs/disciplines/discipline_yaml_audit.md および
  .reviewcompass/specs/workflow-management/yaml-audit-spec.yaml を参照。
```


## Target File Contents

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_avoid_compound_bash.md

content_mode: full_text
content_sha256: bfb51bebf6877b22c6acc8dd05378b29274961b7bde407fb71c8c4c42869cfc7

```text
---
name: avoid-compound-bash
description: 読み取り目的の複合 Bash コマンドを避ける。Read／Glob／Grep ツールで代替するか、Bash は単一コマンド 1 つに留める
metadata:
  type: feedback
---

読み取り目的（ファイル列挙、行数集計、文字列検索、ログ末尾確認など）で Bash を呼ぶときは、次の優先順位で対応する：

1. **Read ／ Glob ／ Grep ツールを使う**（Bash を呼ばない、許可プロンプト発生せず）
   - ファイル内容を見る → Read
   - パス・ファイル列挙 → Glob
   - 文字列検索 → Grep
2. Bash が必要な場合は **単一コマンド 1 つ** に留める
3. 複数情報が必要なら **複数の独立した Bash 呼び出しに分ける**（並列実行可、許可リストが効く）

**避けるべきパターン**：`;`／`&&`／`|` で複数コマンドを繋ぐ複合 Bash。例：`tail file.log; ls dir/ | grep pattern | wc -l`

**Why**：

Claude Code の permission 機構（許可リスト）は **単一コマンドのシグネチャ単位** で効く。複合コマンドは組み合わせごとに別シグネチャ扱いとなり、毎回新規承認プロンプトが発生する。利用者は毎セッション「許可をとるのが多すぎる」「同じ議論を何度もしている」と指摘してきたが、私の習慣として複合 Bash を多用し改善されていなかった。2026-05-28 セッション 36 で再指摘を受けて確立。利用者明示承認の出典：「案 イを処理」（規律本体を repo `docs/disciplines/` に新設、memory はシンボリックリンクで参照、2026-05-28 セッション 36）。

**How to apply**：

- Bash 呼び出しを書く前に自問：「Read／Glob／Grep ツールで代替できないか？」
- 代替できない場合：複合せず単一コマンドにする。`;`／`&&`／`|` の使用を最小化
- 複数情報を取りたい場合：複数の独立した Bash 呼び出しを並列発行（同じ応答内に複数 Bash ブロック）
- 例外：パイプが本質的に必要な場合（`grep | wc` の集計など）のみ複合を許容、ただし利用者承認の負担を意識
- 削除・書き込み・移動などの不可逆操作は規律 [[approval-operation]] に従い別途明示承認

**典型例**：

- × `cat file.log | tail -20`
- ○ Read file.log offset=… で末尾を読む
- × `ls dir/ | grep pattern | wc -l`
- ○ Glob で列挙、結果を Bash 不要でカウント
- × `git log --oneline; git status; git diff`
- ○ 3 つの独立した Bash 呼び出しを並列発行

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）、[[approval-operation]]（不可逆操作の明示承認）
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_concise_complete_report.md

content_mode: full_text
content_sha256: 715e67d83d5c3d9badc85c8d487498e69d5cf2fa2406ca822e886a34a69e4052

```text
---
name: concise-complete-report
description: 利用者からプロンプトを受けて作業を行ったら、実施内容を簡潔にもれなく報告する。報告には何をどのファイルに対してどう変更したかを必ず含め、抜けや概数で済まさない
metadata: 
  type: feedback
---

利用者からプロンプトを受けて作業（編集・新規作成・削除・コミット等）を行ったら、応答の最後に **実施内容を簡潔にもれなく報告する**。報告には次を含める。

- どのファイルに対して
- どの箇所を
- どう変更したか（追加／削除／書き換え／移動）

抜け・概数・「主な変更」のような曖昧表現で済ませず、全件を列挙する。同種の変更が多い場合は件数を明示し、対象一覧（ファイル名・行範囲・キーワード）を簡潔に並べる。

**Why:**

セッション 14（2026-05-21）で、利用者から「指示して終了したと思っていたものをやっていない、それが取りこぼしになってバグになっている」と指摘された。私の状況報告は「やったことの行動ログ」を述べているだけで、利用者の指示に対して「全件完了したか」「抜けがないか」を機械的に照合していなかった。結果、利用者が「完了したと思って次に進む → 実は未完だった」という品質欠陥を繰り返した。

本規律は事後の透明性を保つ最終関門として機能する。事前の達成基準宣言（[[facts-vs-interpretation]]）と組み合わせると、「事前に何を達成すべきか宣言 → 事後に達成基準と照合して全件報告」という二段の品質保証になる。

本規律は、過去に PreToolUse フック `pre-write-self-check.sh`（agreement-quote と scope check の 2 行を毎編集ごとに強制）が担っていた「合意範囲の逸脱検出」機能を、より柔軟かつ低ノイズな形で置き換えるもの。フックは編集ごとに発火する重い検査だったが、本規律は応答末尾の報告に集約することで会話の流れを保つ。

**How to apply:**

## 報告の構造

- 応答の末尾（または明示的な「報告」見出し）で、当該プロンプトに対して実施した変更を **箇条書きで全件列挙** する
- 各項目に「ファイルパス」「変更内容（追加／削除／書き換え／移動）」「対象範囲（行番号・節番号・キーワード）」を含める
- 同種の変更（例：13 か所の用語置換）はまとめてよいが、件数と対象は明示する
- ファイル作成・削除・コミット・push は別項目として明示
- 「主な変更は」「いくつか修正」のような曖昧表現は使わない

## 報告の確認

- 報告した内容と利用者の指示を自分で読み返し、抜けがないか確認する
- 抜けがあった場合は報告に「（追加で確認したところ X も対象でしたが対応漏れ。次の応答で対応します）」を明示する
- 利用者が「他にもあるはず」と気づける材料を提供する

## 取りこぼし防止のため避けるべき行動

- 報告を省いて次の指示を待つ（「ご指示をお待ちします」だけで終わる）
- 報告内容を「やったこと」（行動ログ）に限定し、「達成基準を満たしたか」の照合結果を出さない
- 「○○件完了、残り△件」のような曖昧な進捗報告で、具体的な未完項目を出さない
- 利用者が指示した範囲を分割実行する際、最後に総括せず途中で打ち切る

## 既存規律との関係

- [[facts-vs-interpretation]] と相互補完：事前に達成基準を宣言し、編集後に grep／Read で照合し、その結果を本規律に従って報告する（事実と解釈を分けて報告）

関連：[[facts-vs-interpretation]]（達成基準の事前宣言と機械的照合 ＋ 事実と解釈の分離）
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_facts_vs_interpretation.md

content_mode: full_text
content_sha256: 6662bb52b63c0bf7ca2ef743760c34e7554eee85bee5530415073f2750b46449

```text
---
name: facts-vs-interpretation
description: 達成基準を事前宣言、編集後は機械的（grep／Read）照合、事実と解釈を別個に示し出典に辿れる形に（旧 3 規律統合：check-logs-and-git／separate-facts-from-interpretation／completion-verification-protocol、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

事実は記憶でなく出典（ファイル行・コミット・ログ）で確認し、解釈と明示的に分けて示す。

**達成基準と検証のプロトコル：**

- 指示を受けたら冒頭で達成基準を箇条書きで宣言
- 編集後は grep／Read で機械的に照合し、出典を残す
- 報告の中心は「やったこと」でなく「達成基準と現状の照合結果」
- 完了承認後は基準を満たすまで作業継続

**事実と解釈の区別：**

- 完了・適合・GO を断定せず、検証可能な証拠と「満たした／満たさない」で示す
- 主張・報告は必ず出典（ファイル行・コミット）に辿れる形にする

**Why:** 旧 3 規律（check-logs-and-git／completion-verification-protocol／separate-facts-from-interpretation）を統合（2026-05-25 セッション 24）。事実根拠と機械的確認と解釈の分離は密接に関連する一連の規律で、一体運用が自然。過去の失態：記憶に頼って事実と異なる断定をした、達成基準を宣言せず「やったこと」を報告して齟齬が露見、解釈と事実を混在させて利用者に誤伝した。

**How to apply:**

- 指示を受けたら冒頭で「達成基準の宣言」節を出力
- 編集後に grep／Read の出力を引用して「達成基準 N が満たされている」を機械的に証明
- 報告は「やったこと」ではなく「達成基準 N → 検証結果」の形式
- 機械化の一部は段階 2 スクリプト（[[workflow-precheck-invocation]]）が代行するが、宣言と報告の構造は LLM の責務
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 3 ファイルを参照
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_implementation_autonomy.md

content_mode: full_text
content_sha256: 47bea56df8fafae0a392d5ada4e2f6b45e8e9239fda64a72d8c6ef915051c0d3

```text
---
name: implementation-autonomy
description: 実装（コード編集・TDD・テスト実行）は per-task 承認で止めず自律的に進める。コミット／プッシュ／spec.json 承認／フェーズ移行のみ明示承認を維持
metadata: 
  type: feedback
---
実装フェーズでは、タスク（例：統治 Task 14→15→16→18）ごとに「説明→承認待ち」で止めない。テスト駆動で実装し、テストは許可リストに一致する単一コマンドで実行し、連続して次タスクへ進む。

**Why:** 利用者の明示指示「実装はできるだけ許可不要で進める」（2026-05-18 セッション9、強制関数実装中）。per-task の平易説明＋承認ゲートは丁寧すぎて進行が遅い、と判断された。

**How to apply:**
- 適用対象＝ローカルで可逆な作業（コード編集、TDD のテスト作成・実行、設計正本に基づく実装）。各タスク完了時は簡潔な進捗のみ報告し、承認を待たずに次タスクへ。
- 適用外（従来どおり明示承認が必須）＝コミット、プッシュ、spec.json の approve、フェーズ移行（feedback_approval_required は不変）。
- 平易な日本語・ジャーゴン抑制の応答品質規律は維持。止めないだけで説明を省くわけではない。
- スコープ外の改変はしない（合意範囲を超える追加・リファクタは引き続き禁止）。判断が要る分岐や正本不在の曖昧点のみ質問する。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md

content_mode: full_text
content_sha256: 971e44a1f5c5026a98865ffdbfd116fcd80ee86b96f7ebee9b2a34cecf8be968

```text
---
name: intent-conformance-is-the-acceptance-gate
description: 実装の受け入れ基準は「フルスクラッチで作ったか」でなく「実装されたコード・システムが意図どおりに機能するか（承認仕様＝意図に適合するか）」。フルスクラッチは手法でありゲートではない
metadata: 
  type: feedback
---

実装成果を受け入れてよいかの判定基準（acceptance gate）は、「フルスクラッチ開発だったか否か」ではなく、「実装されたコード・システムが意図どおりに機能するか＝承認済み仕様（要件・設計・タスク＝意図）に適合するか」である。

**Why:** 利用者決定 2026-05-19（統治フィーチャーの扱いを巡る議論の中で確定）。理由＝「フルスクラッチか」はワークフローのゲートで検証できず（成果物-対-仕様しか検査しない）、自信をもった誤った「完了」宣言を生んだ（統治を部分修正で済ませ独断確定→偶然発覚）。本質的に重要なのは作り方でなく、できたものが意図どおり機能するか。それは承認仕様＋再実行可能な証拠で実体的に確認できる。フルスクラッチは依然として推奨されうる手法だが、それ自体は受け入れゲートではない。

**How to apply:**
- 実装が受け入れ可能かを判断するときは、手法（スクラッチか部分修正か）でなく「承認仕様＝意図への適合」を基準にする
- 適合確認は信頼できる証拠で行う：機械化できる部分は再実行可能な決定的検査（テスト・不変条件・差分再導出）の生出力、機械化できない意図部分（プロセス契約など）は人間または別系統モデルの判断。単一LLMレビューの要約を適合の根拠として断定しない（[[standing-directives-are-hard-constraints]] と一体）
- 「フルスクラッチ要件」は本基準へ改定済み。ただし利用者が個別に手法を指示した場合はその指示が優先（指示は硬い制約＝[[standing-directives-are-hard-constraints]]）
- 「テスト緑＝意図適合」と短絡しない。回帰テスト緑は「符号化済み期待が壊れていない」を測るのみ。意図適合の証拠としての強さはテストの仕様忠実度に依存（[[implementation-autonomy]] の自律進行も本基準下で運用）

**重要：[[standing-directives-are-hard-constraints]] との衝突解決（セッション 12 利用者裁定 2026-05-19）**

本基準（意図適合）と恒常指示（[[standing-directives-are-hard-constraints]]、例：全機能フルスクラッチ）が衝突する場合は **恒常指示が優先する**。本基準だけを根拠に「意図適合すれば手法は問わない」と独断で部分修正を確定してはならない。衝突が認められたら、自律確定せず利用者に明示してエスカレーションし、利用者の裁定を仰ぐ。セッション 12 で本基準のみを根拠に統治を部分修正で確定した結果、恒常指示「全機能フルスクラッチ」に違反した重大な過失が発覚した経緯による。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md

content_mode: full_text
content_sha256: 12c05dede38e024466377cdd8272e90bb84ab73f67b438ec11984935769bac75

```text
---
name: must-fix-discussion-obligation
description: triad-review 段で must-fix と判定された所見の対処は利用者と必ず議論する。独自判断で仕様文書を修正することを禁ずる。各推奨案には後段影響の深掘りを義務付ける。
metadata: 
  type: feedback
---

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM）が独自判断で仕様文書（design.md／requirements.md／tasks.md／implementation.md）を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**Why**：2026-05-25 セッション 25 で、foundation／design の must-fix 7 件の対処内容を私が独自判断で起草し design.md に反映、コミット・push まで進めた事案が発生。利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」で気づき進行を中断。その後の議論で「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」と指摘を受け、本規律として確立した。

**How to apply**：

- 正本手順：運営ガイド `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-1) must-fix 所見の対処手順 を参照する。本 memory は参照リンクのみで、規律本体は運営ガイドが正本
- triad-review 完了後、must-fix 所見を 1 件ずつ取り上げ、利用者と議論しながら平易な日本語で対処方針を提案する
- 各推奨案には必ず後段影響の深掘り（下流仕様・対象アプリ配置・機械検証・実装運用・将来拡張）を含める
- 「現状維持を推奨」する場合も、現状維持の弱点を検証してから示す
- 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
- 候補案は必ず複数提示、代替案との比較を欠かない
- API 経由の review-run で `ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を扱う場合、この規律は「利用者に提示して承認を得る」という会話上の義務だけを定める。`review_triage.py decide`、manifest 生成、承認レコード要件などの機械ゲートは `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` の `post_write_verification` 分岐を正本とする

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md

content_mode: full_text
content_sha256: db7bdfbc8a2b4b2fcb33c869420c52ac58f06ad7fe4a79f0eab967597201f928

```text
---
name: no-redundant-workflow-questions
description: 波進行など正本ワークフローが順序・方式を既定する局面で、機能ごとに止めて利用者へ進め方を尋ねない
metadata: 
  type: feedback
---
正本ワークフローが進行順序・単位を既に規定している局面では、機能ごとに止めて「ここで確認するか／まとめて進めるか」を利用者に尋ねない。手順どおり手を止めず進める。

**Why:** タスクフェーズ着手時、方式（全面再導出）も波順（基盤→実行側→評価→自己改善→論文→横断整合ゲート→統治）も正本（WORKFLOW_OVERVIEW 節 2、phase-and-feature-dependency-map §5.1「1 つ書き切って終わりではなく wave として横に広げてから alignment する」）で確定済みなのに、基盤タスク再生成後に進行単位を尋ね「愚問」と指摘された。正本が答えを持つ質問は利用者の時間を奪うだけ。

**How to apply:** 質問の前に自問する——「この答えは正本文書（WORKFLOW_OVERVIEW / 依存マップ / HUMAN_WORKFLOW / spec.json）に既に書かれているか？」。書かれていれば質問せず正本どおり進める。質問してよいのは、正本が沈黙している分岐（例：差分追従型 vs 全面再導出型のような方式選択で前例も指示もない場合）と、spec.json approve / commit / push / phase 移行の明示承認のみ。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_normal_output_minimization.md

content_mode: full_text
content_sha256: e74d3098d84c52e50f0e6602a426754b52ecdbe16ffa1f6a3fcdaf6a6d71e8a6

```text
---
name: normal-output-minimization
description: CLI / tool の正常系出力を最小化し、異常系と機械可読出力には必要情報を残す
metadata:
  type: feedback
---

# 正常系出力最小化

CLI / tool の人間可読出力は、正常系では利用者が次に進むために必要な最小情報だけを出す。異常系では原因、現在状態、次に取れる行動を省略しない。機械可読出力は `--json` などの明示オプションに集約し、詳細情報を保持する。

## 原則

- 正常系の人間可読出力は 1 行から数行に抑える。
- 正常系では内部判定、全入力、詳細な current state、長い候補一覧を既定出力に出さない。
- 異常系では、判定結果、原因、対象ファイル、現在状態、次の許可 action を出す。
- `--json` は詳細を落とさない。自動処理、監査、デバッグ、ログ連携は `--json` を使う。
- `--verbose` がある場合だけ、正常系でも詳細ログを出してよい。
- 非定型処理は、利用者が状況を理解するために必要な短い説明を許容する。ただし定型化できる処理は CLI 側へ寄せる。

## CLI 実装契約

新規または改修する CLI / tool は、次の出力面を分ける。

| 出力面 | 契約 |
|---|---|
| 正常系 human output | 成功事実と対象 action だけを短く出す |
| 警告系 human output | 警告理由、続行可否、必要な人間判断を出す |
| 異常系 human output | 停止理由、壊さないために行わなかった処理、次 action を出す |
| `--json` output | 判定、理由、対象、状態、証跡パスを完全に出す |
| `--verbose` output | 調査・保守に必要な詳細を出す |

## 適用手順

1. 既存 CLI / tool を棚卸しし、正常系出力が多いもの、対話で頻出するもの、不可逆操作に近いものを優先する。
2. 正常系 human output の期待をテストに固定する。
3. 異常系 human output と `--json` の情報量が落ちていないことをテストする。
4. 実装では、判定データの生成と human formatter を分ける。
5. 正常系の詳細を削る場合も、JSON / log / manifest のどこかに監査可能な詳細を残す。

## 棚卸し

共通棚卸しの正本は `docs/notes/working/2026-06-19-normal-output-minimization-tool-inventory.yaml` とする。各 tool の対応状態、優先度、次 action はこの YAML を更新する。

## 既存規律との関係

- [[concise-complete-report]]: 最終報告は簡潔かつ漏れなく行う。本規律は CLI / tool の通常出力を対象にし、LLM の最終報告そのものを省略しない。
- [[facts-vs-interpretation]]: 正常系で省略した詳細も、必要なら JSON / log / manifest から事実確認できるようにする。
- [[workflow-precheck-invocation]]: 不可逆操作直前の検査は維持する。ただし OK の既定 human output は最小にする。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_options_presentation.md

content_mode: full_text
content_sha256: bd60db3932c2261b6588b9916720cf50222c18b42996952f996fc306a284757c

```text
---
name: options-presentation
description: 複数案提示時の規律 — dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設、2026-05-26 セッション 27）
metadata:
  type: feedback
---

利用者に複数の選択肢を提示する際、dominated 案（明らかに他案に劣る案）は提示しない。提示前に内部検査結果を応答内で明示宣言し、合理案のみを階層性を守って並べる。

**Why:** 旧 2 規律（dominant-dominated-options ／ choice-presentation）を統合し事前検査宣言義務を新設（2026-05-26 セッション 27）。旧 dominant-dominated-options（参照層）は決定の瞬間に発火しない構造的欠陥が露見（利用者発言「規律が効いていない」）、active 必読昇格と事前宣言義務の併設で対処。

## 対象範囲（2026-05-26 セッション 27 で明確化）

本規律の対象は **利用者に判断を仰ぐ複数案提示の応答**（レビュー／設計議論／実装議論の中で利用者の選択を仰ぐ場面）に限定する。

**対象外**：

- **設計文書内の比較記述**：design.md ／ requirements.md ／ tasks.md 等の仕様文書内で複数の選択肢を列挙し、採用案を確定する記述（経緯記録の性格を持ち、利用者の判断を仰ぐ場面ではない）
- **過去の議論経緯の引用**：archive 配下の旧文書や履歴記述中の複数案列挙
- **規律本体の説明**：規律ファイル内の例示

**対象範囲明確化の理由**：本規律の本来目的は「利用者の判断負荷を減らす」「dominated 案を提示しない」こと。設計文書内の経緯記録に同様の事前検査宣言を要求すると、設計文書が宣言だらけになり可読性が落ちる。経緯記録の自由度を保つため、規律の射程を「利用者判断を仰ぐ場面」に限定する。

**利用者明示承認の出典**：「候補 3」（規律の対象範囲を明確化する小改訂、2026-05-26 セッション 27 の conformance-evaluation／design.triad-review／G8 議論）。

## How to apply

### 1. dominated 判定の厳密化 3 規律（必須適用）

dominated と判定する案ごとに：

- **合理的成立条件 1 文以上**：その案が合理になる前提（規模・利用頻度・UX 重視等）を記述
- **量的主張には numerical 規模感**：性能 = ms/s ／ コスト = LOC など、抽象論禁止
- **暗黙前提**：前提が変わると判定が反転する場合は依存性を明記

3 規律のいずれも満たさず合理的成立条件が思い浮かばない案のみ「真の dominated」と判定可。

### 2. 事前検査宣言義務

複数案を提示する応答を作る前に、応答内で次を明示宣言する（[[facts-vs-interpretation]] の事前宣言と同型）：

- **(a)** 内部検討した候補の総数
- **(b)** 各案に上記 3 規律を適用した結果
- **(c)** dominated と判定して除外した案（除外理由つき）
- **(d)** 残った合理案だけを提示

宣言は応答に埋め込み、grep で事後集計可能な形を保つ。効果は `docs/discipline-compliance-reports/options-precheck-log.md` で計測。

### 3. 残った合理案の提示

- **ラベル必須**：【文言確定済】【選択肢あり】【SSoT 判定要】【範囲拡張】のいずれかを明示
- **階層性**：大局（方針）→ 細部（具体案）の順。同一ターンで並列禁止
- **3 選択肢以内**：4 個以上並ぶなら大局判断を分離する設計が間違っている疑い
- **メリデメは 2〜3 点**：長文比較表は判断負荷を上げる
- **推奨を明示**：「推奨で進める」と一言で答えられる形に
- **物理レイアウト例外**：ファイル配置・パス命名等は ASCII ツリー＋比較表＋判断軸要約の 3 点組み

## 関連規律

- [[approval-operation]]：選択肢提示後の承認は別工程、明示承認必須
- [[facts-vs-interpretation]]：事前宣言の同型構造
- [[pre-action-precheck]]：別の事前検査チェックリスト（集約・横断操作向け）

## 統廃合元

`docs/disciplines/archive/2026-05-26-consolidation/` の旧 2 件（discipline_dominant_dominated_options.md ／ discipline_choice_presentation.md）に詳細例と経緯あり。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_plain_explanation_each_step.md

content_mode: full_text
content_sha256: b7c02e94078eaa2aa519e1fc5b71d2ed9d81e351a55fb4bd2a96056e450a2603

```text
---
name: plain-explanation-each-step
description: must-fix 適用など 1 件ずつ承認の各ステップで、利用者が都度求めなくても承認前に平易な日本語説明を先に添える
metadata: 
  type: feedback
---
1 件ずつ承認で進める各ステップ（must-fix 適用、spec.json 変更、文書修正など）で、利用者が「平易に説明」と都度指示しなくても、承認を求める前に必ず平易な日本語の説明（何が問題か・どう直すか・意図は変わらないか）を先に添える。

**Why:** 統治要件 9 の must-fix を 1 件ずつ適用中、利用者が #1・#2 と続けて「平易に説明」を要求し、最後に「以降も同様」と明示した。毎回求めさせるのは手間で、説明は既定動作にすべきという指示。

**How to apply:** 1 件ずつ承認のシーケンス（レビュー must-fix、spec.json 反映、横断整合の C 群対応など）では、英語技術用語の羅列を避けた完全な日本語の文で「問題／修正内容／意図不変か」を述べてから承認を求める。技術用語は初出時に意味併記。feedback_plain_japanese の一般規律を、承認ステップで先出し必須として具体化したもの。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_plain_japanese.md

content_mode: full_text
content_sha256: 21e60fb53585e525fc4220bb738c5ad84f0bc363c0e401ebd878868422d0bd34

```text
---
name: plain-japanese
description: 英語技術用語を多用しない。完全な日本語の文で書く。応答送信前に自己検査する。
metadata: 
  type: feedback
---
## 問題点

英語技術用語の混入と「(= ...)」の連発で意図が伝わらない。

## 特に気をつけること

完全な日本語の文で書く。英語の技術用語を使うときは、初出時に意味を併記する。

## 応答送信前の自己検査 (59 回目セッション追加)

応答を生成し終わったら、送信ボタンを押す前に自分で次の検査を実施する。フックの事後検出に頼らない。

**Why:** ジャーゴン検査フックが事後検出して書き直しを要求する運用が繰り返されると、user 側の体験を著しく損なう (= 1 つの応答に対して 2 〜 3 回書き直しが発生する)。59 回目セッションで「ジャーゴンを検知して、書き直し、またジャーゴンを検知して書き直す。ここも体験が損なわれる。1 回で済むようにする」と user から明示の指摘を受けた。

**How to apply:**

- **検査対象の典型ジャーゴン**: dev_log / rework_log / treatment / treatment-dual / treatment-single / Adjacent Sync / pristine state / escalate / forced_divergence / metapattern など (= dual-reviewer 方法論内部用語)
- **置き換え方針**: 修正履歴の記録 / 1 人レビュー実験用ブランチ / 2 人レビュー実験用ブランチ / 他仕様書への波及通知 / 修正前の元状態 / 単独判断せず user 判断を仰ぐ / 暗黙前提を別前提に置き換える検証 / パターン分類
- **検査の閾値**: 同じジャーゴンが 3 回以上出現する場合、確実にフック検出されるので必ず書き直す
- **不可避な場合**: ファイル名や schema 名で固有名詞として登場する場合は初出時に意味を併記する。固有名詞の使用は最小限に留める。
- **送信前最終チェック**: 応答全体を見渡し、ジャーゴン濫用がないか目視確認する
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_pre_action_precheck.md

content_mode: full_text
content_sha256: 9f14916c6df802c00bd389368ac55161c2e28fa0eec1283116de9df37f3a097f

```text
---
name: pre-action-precheck
description: 集約・横断操作（≥3 file 操作、確定事項表作成等）の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示（旧 2 規律統合：aggregation-self-check／multi-file-dependency-precheck、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

集約・横断操作の前に、応答内で事前検査チェックリストを明示し、grep で対象を全件列挙する。

**集約局面（確定事項表・採用方針一覧等）の事前検査 5 項目：**

1. 各項目に承認発言の出典は併記されているか（[[approval-operation]] 連動）
2. 確定済み論点と未確定論点が区別されているか
3. workflow_state（spec.json）の状態と整合しているか（[[workflow-state-truth-source]] 連動）
4. 過去確定との矛盾はないか
5. 利用者の最新発言と整合しているか

**多 file 操作（≥3 file）の事前検査：**

- grep 実行で対象を行番号付き全件提示
- 3 分類で categorize（編集／追記／削除、または機能内対処／波及／遡及）
- scope 独立検証（提案範囲が利用者意図と一致するか）

**波及調査の網羅性（2026-06-02 セッション 47 追加）：**

ある変更が他機能・他文書に波及するかを調べるときは、影響を受けうる **全対象**（全機能・全文書）を **全表記**（機械可読の識別子と人間可読の和訳の両方、例：`review_mode` と「レビューモード」）で網羅 grep し、波及の全範囲を確定してから対処に着手する。部分的な対象・単一表記での調査で着手すると、調査漏れにより同じ再オープン手続きを繰り返すことになる。

**Why:** 旧 2 規律（aggregation-self-check／multi-file-dependency-precheck v2.1）を統合（2026-05-25 セッション 24）。事前検査は集約局面と多 file 操作の両方で必要、規律として一体で扱う方が自然。過去の経緯：aggregation-self-check はセッション 21 の表作成前自己検査として制定、multi-file-dependency-precheck v2.1 はセッション 22 で旧 pre-action-checklist を統合した経緯がある。波及調査の網羅性は 2026-06-02 セッション 47 で追加：foundation の `review_mode` 正本への `api_mediated` 追加の波及対処で、英語表記「review_mode」のみ・部分機能のみの調査で着手したため、日本語表記「レビューモード」の箇所や残りの機能を取りこぼし、再オープン手続きを 3 回繰り返した失敗が出典。

**How to apply:**

- 確定事項表・採用方針一覧を書く前：5 項目チェックリストを応答内で明示宣言、書く前の事前検査として実行
- 3 file 以上の操作前：grep ＋ 全件提示 ＋ 3 分類 ＋ scope 独立検証を実施
- 段階 2 スクリプトの機械検査では捕捉できない（応答内の宣言で守る）
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 2 ファイルを参照
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md

content_mode: full_text
content_sha256: ab5766d61be4559b38bbd584c3c5bf66b9dd2746fa2eb8792f43c9990208deeb

```text
---
name: reopen-procedure-for-settled-topics
description: 一度確定した論点を再考する場合の手順、明示承認なしでの再確定を禁止
metadata: 
  type: feedback
---

一度利用者の明示承認で確定した論点を再考する場合は、次の手順を踏む：

1. **再オープンの宣言**：「論点 N を再オープンしたい」と明示する
2. **再考の理由を述べる**：他論点との整合崩れ、新情報の発見、矛盾の発覚など、再考が必要になった理由を具体的に説明
3. **新しい結論案の提示**：AskUserQuestion で選択を仰ぐか、明示的な質問形式で利用者の判断を求める
4. **明示承認の取得**：「論点 N を ○○ に再確定します」という利用者の明示承認発言を必ず取る（[[approval-operation]] に従う）
5. **再オープン履歴の記録**：設計メモ・TODO 等に「再確定：YYYY-MM-DD、旧確定 ○○ → 新確定 ××、根拠 line NN」と履歴を残す

**Why:** セッション 20 で論点 1（spec.json の階層範囲）の再オープン提案後、私が利用者の「議論継続指示」「計画書再読指示」を黙示の同意と誤解し、「6 階層 → 4 階層」と確定を書き換えた。この一連の流れには「再オープン提案」「議論継続」「計画書再読」「私の整理」「命名指摘」「私の確定書き込み」と多くのステップがあったが、どこにも利用者の「論点 1 を 4 階層に再確定する」という明示承認発言が存在しなかった。一度確定したものを変更する重大さに対し、手順が明文化されていなかった。

**How to apply:** 確定済み論点に変更を提案する前に本手順を意識する。特に「整合性の取り直し」「他論点との連動」を理由に既存確定を変えるとき、論理的に導けても利用者の明示承認なしでは「確定」と書いてはならない。再オープン履歴は読者が「なぜ変わったか」を追跡できるよう、旧確定・新確定・根拠ログ行を併記する（[[approval-operation]] と一体）。
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md

content_mode: full_text
content_sha256: 3b03b245a529af50dfbb5674ee045397572947031b6b8caa564dcc9f552d9e35

```text
---
name: standing-directives-are-hard-constraints
description: 恒常的な利用者指示（フルスクラッチ等）は既定でなく硬い制約。approach を変える決定はレビュアー/自分の技術判断で自律確定せず、恒常指示と突き合わせ衝突あれば必ずエスカレーション
metadata: 
  type: feedback
---

恒常的な利用者指示（例：6機能すべてフルスクラッチ再構築、旧コードを中途半端に流用しない＝[[implementation-autonomy]] と一体の利用者方針）は、「技術的に妥当なら外してよい既定」ではなく「approach を縛る硬い制約」として扱う。

**Why:** セッション12で統治中核を、独立適合レビューの「部分修正で技術的に足りる」推奨を採用して部分修正で確定させた。だが利用者の恒常指示は「全機能フルスクラッチ」。記憶にその指示はあったのに、approach 変更決定を縛る硬い制約として扱わず、「技術的に十分」を「やってよい」と取り違えた。ワークフローのゲート（仕様適合・回帰テスト）は「作り方の制約」を検証しないため全ゲート通過し、利用者の偶然の問い（「全てフルスクラッチの筈」）でしか露見しなかった。重大な見逃し。

**How to apply:**
- approach を変える決定（スクラッチ↔部分修正、再実装↔既存流用、reopen↔task内吸収など「やり方そのもの」を選ぶ判断）に直面したら、着手前に恒常指示・記憶された利用者方針と必ず突き合わせる
- レビュアー（サブエージェント）や自分が技術的に「部分で足りる／不要」と判断しても、それは恒常指示を上書きしない。技術的十分性 ≠ 許可。恒常指示に触れる approach 変更は利用者の判断事項
- 衝突または衝突の疑いがあれば自律確定せず、「レビュアーは X を技術的に推奨。ただし恒常指示は Y。どちらが支配するか」と明示してエスカレーション。「止めず合理的判断で進める」指示があっても、恒常指示との衝突点はその例外（commit/push/spec.json/phase/設計差し戻し判断と同格の承認点）
- 言われた指示は必ず明示的な不変条件として記憶化し、決定点で参照する。これでも未言明の指示は防げない＝人手判断はゼロにできない、と認識する

**重要：[[intent-conformance-is-the-acceptance-gate]] との衝突解決（セッション 12 利用者裁定 2026-05-19）**

[[intent-conformance-is-the-acceptance-gate]]（意図適合が受け入れ基準）と本規律が衝突する場合は **本規律（恒常指示）が優先する**。意図適合のみを根拠に手法（スクラッチ↔部分修正）を自律変更してはならない。意図適合は「できあがったものを受け入れるかの基準」を扱い、本規律は「作り方の選択に対する制約」を扱う。両者は機能が異なり、作り方が恒常指示の制約に違反していれば、意図適合していても受け入れない（あるいは利用者裁定を仰ぐ）のが本規律の趣旨である。

関連：[[approval-operation]]（承認点）、[[implementation-autonomy]]（自律進行の範囲。本規律はその境界＝approach 変更は自律の外）、[[intent-conformance-is-the-acceptance-gate]]（意図適合の受け入れ基準、衝突時は本規律が優先）
```

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/discipline_workflow_precheck_invocation.md

content_mode: full_text
content_sha256: f623dc363ec9b49e7b902b0fc9a99213e0d80e60cda06c94bbd1c9adb16d39a7

```text
---
name: workflow-precheck-invocation
description: 不可逆操作（spec.json 変更／git commit／git push）の直前に現行の precheck 入口を呼び、判定結果を応答内で明示する
metadata: 
  type: feedback
---

ReviewCompass の不可逆操作の直前に、必ず現行の precheck 入口を呼び、
出力の verdict と reasons を応答に書く。通常の作業開始時は先に
`.venv/bin/python3 tools/check-workflow-action.py next --json` を確認し、
`next_action.required_disciplines` に示された規律だけを作業直前に読む。

**対象操作と呼び出し：**

- spec.json の workflow_state を変更する直前：
  `.venv/bin/python3 tools/check-workflow-action.py spec-set <feature> <phase> <stage> <true/false> [--rationale "..."]`
- 利用者が commit を指示した直後、git add や approval record 作成の前：
  `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json`
- git push の直前：
  `.venv/bin/python3 tools/check-workflow-action.py push --rationale "<理由>"`
- 別作業を開始する直前：
  `.venv/bin/python3 tools/check-workflow-action.py work-unit preflight-start --proposed-unit-file <path> --json`

**判定結果の扱い：**

- exit 0（OK）：続行
- exit 1（WARN）：警告を応答に明示し、人の判断を仰ぐ（自律続行しない）
- exit 2（DEVIATION）：処理を止めて人に報告、原因を是正してから再試行

**段階 1 と段階 3 の責務分担：**

段階 3 フック（`.claude/hooks/pre-bash-precheck.sh`）が Bash の git commit／push を
PreToolUse で自動検査するようになったが、段階 1（LLM 自身の意図呼び出し）は依然
として必要：

- **依然として LLM が必ず呼ぶ**：spec.json 修正（Edit／Write）の直前。段階 3 は
  Bash 系のみ実装済みであり、Edit／Write の spec.json 検知は未対応
- **LLM が呼ぶことが望ましい**：git commit／git push の直前。段階 3 が自動発動する
  が、LLM が事前に呼べば応答内で verdict／reasons を共有でき、人間判断との連携
  が滑らか
- **「呼び忘れ」の救済**：段階 3 フックが exit 2 で遮断するため、LLM の見落とし時も
  Bash 系はブロックが効く。ただし応答テキストのみの判断（フックが効かない領域）
  は段階 1 規律が恒久的に担う

**Why:** LLM が段階 2 のスクリプトを呼ばないと機械検査の効果が消える。
仕様 `.reviewcompass/guidance/WORKFLOW_PRECHECK.md`「段階 1・段階 3 との接続」で
規定された段階 1 規律の文書化。

**How to apply:**

- 「直前」とは、対応する Edit／Write／Bash 呼び出しの直前
- `--rationale` には人の承認発言や操作理由を渡し、ログ `.reviewcompass/runtime/logs/workflow-precheck.log` に残す
- [[approval-operation]] の機械検査による補強。
  当該規律が言う「承認なしで進めない」を構造的に強化する
- 不可逆操作で恒常的に運用する
```

### /Users/Daily/Development/ReviewCompass/docs/disciplines/README.md

content_mode: full_text
content_sha256: fdb37def67da7d744846c216c0d5884f11c088152c6fa27216889df9227de801

```text
# 規律ファイルの旧配置（disciplines）

最終更新：2026-06-19（`discipline_normal_output_minimization.md` を新設、active 必読昇格。CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する共通規律。利用者指示「全 CLI / 全ツールへ広げるなら、別途『正常系出力最小化』の共通規律と各ツールの棚卸し。これを対応」に基づく）／2026-06-18（イレギュラー組み込み：`discipline_llm_as_judge_prompting.md` を新設、active 必読昇格。3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。通常の drafting→review→approval 手続きを省略し利用者明示承認「強制的に組み込みたい」「はい」で即時発効）／2026-06-02（セッション 50：`discipline_yaml_audit.md` を新設、active 必読昇格。設定・動作仕様 yaml 専用の監査規律（補助層 E）。独立 3 系統で 2 回の検証ループを経て発効、利用者明示承認「承認」）／2026-05-31（セッション 41：`discipline_post_write_verification.md` を新設、active 必読昇格。本規律自身の起草に対し独立 3 系統で 5 回の検証ループを経て発効、OpenAI／Google で ALL_CLEAR 達成）／2026-05-26（セッション 27：旧 dominant-dominated-options ／ choice-presentation を統合し `discipline_options_presentation.md` を新設、active 必読昇格＋事前検査宣言義務を新設、旧 2 件は `archive/2026-05-26-consolidation/` へ退避。利用者明示承認「OK」「承認」）

過去履歴：
- セッション 27（2026-05-26）前半：シンボリックリンク検証失敗・fallback 案イ採用により、当時は毎セッション開始時に TODO §1 起動手順で active 必読を Read で読む運用に切り替えた。現在は `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` に従い、`tools/check-workflow-action.py next --json` の `next_action.required_disciplines` が示す場面別の規律だけを作業直前に読む。
- セッション 26（2026-05-25）：active 必読 12 件 ＋ 参照層 5 件＝合計 17 件を memory から軽量移送 → `no-unilateral-action` 撤去で 16 件 → memory 側 `feedback_*.md` をシンボリックリンクに変更

## 配置と所有

active 規律ファイルの正本は `.reviewcompass/guidance/discipline_*.md` へ移動済みである。

本ディレクトリ `docs/disciplines/` は旧配置の説明と archive を保管する。**所有者は `workflow-management` 機能**（A-007 案 2、2026-05-23 利用者承認）で、active 規律の改廃は `.reviewcompass/guidance/discipline_*.md` を対象として本機能の所定手続き（drafting → review → approval）経由で実施する。

active 規律ファイルは `.reviewcompass/guidance/discipline_<name>.md` の命名規約に従う。`<name>` は規律内容を表す英語ハイフン区切り（例：`discipline_must_fix_discussion_obligation.md`）。

## 内部リンク記法

各規律ファイル本文に `[[link-name]]` 形式の内部参照（例：`[[approval-operation]]`、`[[workflow-precheck-invocation]]`）が登場する。これは memory 機構の慣習を引き継いだ記法で、本ディレクトリ内では次の規則で解決する：

- **`[[name]]`** → `.reviewcompass/guidance/discipline_<name>.md`
- 例：`[[approval-operation]]` → `discipline_approval_operation.md`
- 例：`[[workflow-precheck-invocation]]` → `discipline_workflow_precheck_invocation.md`

本記法は Markdown viewer によっては自動でクリック可能リンクとして解決されないが、内部参照の意図を明示する目的で維持する。Markdown リンク形式への一括変換は別途検討（フェーズ 2 以降の宿題）。

## 規律ファイル一覧

最新の件数は本一覧の各表（active 必読／参照層／archive）で確認すること。件数は本見出しには固定しない（増減の都度に編集箇所が分散するのを避けるため）。

### active 規律（`next --json` の required_disciplines に従い作業直前に読む）

| ファイル | 概要 |
|---|---|
| [discipline_must_fix_discussion_obligation.md](../../.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md) | triad-review の must-fix 所見は利用者と必ず議論、独自判断で仕様修正禁止 |
| [discipline_intent_conformance_is_the_acceptance_gate.md](../../.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md) | 受け入れ基準は「実装が意図どおり機能＝承認仕様に適合」か（フルスクラッチは手法でゲートでない） |
| [discipline_standing_directives_are_hard_constraints.md](../../.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md) | フルスクラッチ等の恒常指示は既定でなく硬い制約、approach 変更は自律確定せずエスカレーション |
| [discipline_workflow_precheck_invocation.md](../../.reviewcompass/guidance/discipline_workflow_precheck_invocation.md) | 不可逆操作の直前に tools/check-workflow-action.py を呼び verdict／reasons を応答に明示 |
| [discipline_approval_operation.md](../../.reviewcompass/guidance/discipline_approval_operation.md) | 不可逆操作は利用者明示承認必須、明示的肯定発言のみ承認、確定記述には承認出典を併記 |
| [discipline_facts_vs_interpretation.md](../../.reviewcompass/guidance/discipline_facts_vs_interpretation.md) | 達成基準を事前宣言、編集後は機械的照合、事実と解釈を別個に示し出典に辿れる形に |
| [discipline_pre_action_precheck.md](../../.reviewcompass/guidance/discipline_pre_action_precheck.md) | 集約・横断操作の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示。波及調査は全対象×全表記（機械可読の識別子と人間可読の和訳の両方）で網羅 grep してから着手（2026-06-02 セッション 47 追加） |
| [discipline_workflow_state_truth_source.md](../../.reviewcompass/guidance/discipline_workflow_state_truth_source.md) | 状態判定は workflow_state を読み、過去確定事項は出典付きのみ信頼 |
| [discipline_concise_complete_report.md](../../.reviewcompass/guidance/discipline_concise_complete_report.md) | 作業後は応答末尾で実施内容を箇条書きで全件列挙、ファイルパス・変更内容を必ず含める |
| [discipline_reopen_procedure_for_settled_topics.md](../../.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md) | 確定済み論点を変更する場合は 5 ステップ（宣言・理由・新案・明示承認・履歴記録） |
| [discipline_plain_japanese.md](../../.reviewcompass/guidance/discipline_plain_japanese.md) | 英語技術用語を多用しない、完全な日本語の文で書く、応答送信前に自己検査 |
| [discipline_options_presentation.md](../../.reviewcompass/guidance/discipline_options_presentation.md) | 複数案提示時、dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設） |
| [discipline_avoid_compound_bash.md](../../.reviewcompass/guidance/discipline_avoid_compound_bash.md) | 読み取り目的の複合 Bash コマンド（`;`／`&&`／`|`）を避ける、Read／Glob／Grep ツールで代替するか単一コマンドに留める、許可プロンプト多発の防止（2026-05-28 セッション 36 軽量移送で確立、利用者明示承認「案 イを処理」） |
| [discipline_post_write_verification.md](../../.reviewcompass/guidance/discipline_post_write_verification.md) | ワークフロー段の外側にある正本文書への書き込み後、起草者と異なる検証経路による独立検証を必須化。検出は逐語的指摘（弾く）と本質的指摘（人へ上げる）に分類して処理し、収束基準は動作仕様ファイル post-write-verification-spec.yaml と現行 API variant 設定に従う。2026-05-31 セッション 41 新設・2026-06-01 セッション 43 収束基準改訂 |
| [discipline_yaml_audit.md](../../.reviewcompass/guidance/discipline_yaml_audit.md) | 設定・動作仕様 yaml（config/, runtime/config/, stages/, .reviewcompass/specs/ 配下）への書き込み後に監査を必須化する規律（補助層 E）。md 用書き込み後検証（補助層 D）とは別立て。11 観点（A 系統：機械検査 6 必須＋2 推奨、B 系統：独立検証 3 必須）で点検。新規対象の組み入れ時に全件を初回検証。2026-06-02 セッション 50 新設 |
| [discipline_llm_as_judge_prompting.md](../../.reviewcompass/guidance/discipline_llm_as_judge_prompting.md) | 3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。材料揃え（メインLLMが問題を直接検討）→ 問い設計（情報・問い・範囲の3要素）→ 選択肢なし分析の手順で品質を高める。2026-06-18 セッション 新設 |
| [discipline_normal_output_minimization.md](../../.reviewcompass/guidance/discipline_normal_output_minimization.md) | CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する。共通棚卸し YAML を更新しながら全 tool へ段階適用する。2026-06-19 新設 |

### 参照層（3 件、必要時に grep／Read で参照、起動時 load なし）

| ファイル | 概要 |
|---|---|
| [discipline_no_redundant_workflow_questions.md](../../.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md) | 正本ワークフローが順序・方式を既定する局面で機能ごとに止めて尋ねない |
| [discipline_plain_explanation_each_step.md](../../.reviewcompass/guidance/discipline_plain_explanation_each_step.md) | 1 件ずつ承認の各ステップで承認前に平易な日本語説明を先に添える |
| [discipline_implementation_autonomy.md](../../.reviewcompass/guidance/discipline_implementation_autonomy.md) | 実装フェーズはタスクごとに止めず自律進行、コミット／プッシュ／spec.json／フェーズ移行のみ明示承認 |

### archive（統廃合元・撤廃済みの本体保全、起動時 load なし）

| ディレクトリ | 内容 |
|---|---|
| [archive/2026-05-26-consolidation/](archive/2026-05-26-consolidation/) | セッション 27（2026-05-26）の統廃合元 2 件（旧 dominant-dominated-options ／ choice-presentation）。統合先は active 必読の `discipline_options_presentation.md` |

## 関連参照

- **対応する memory 側索引**：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/feedback_*.md`（短い参照索引、本体は本ディレクトリを Read で参照）
- **memory archive**（統廃合元 14 件）：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/archive/2026-05-25-consolidation/`
- **本機能の設計**：`.reviewcompass/specs/workflow-management/design.md` §責務境界の明確化
- **計画書 §5.21**：規律ファイルの ReviewCompass 方針への取り入れ手順
- **移送経緯**：本セッション 26（2026-05-25）の軽量手続きにより、active 必読 12 件＋参照層 5 件を memory から移管。2026-06-23 の guidance relocation により、active 本体は `.reviewcompass/guidance/` へ移動
```


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
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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

If there are no findings and the criteria does not define additional top-level keys, return exactly:

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
.reviewcompass/guidance/discipline_avoid_compound_bash.md
.reviewcompass/guidance/discipline_concise_complete_report.md
.reviewcompass/guidance/discipline_facts_vs_interpretation.md
.reviewcompass/guidance/discipline_implementation_autonomy.md
.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md
.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md
.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md
.reviewcompass/guidance/discipline_normal_output_minimization.md
.reviewcompass/guidance/discipline_options_presentation.md
.reviewcompass/guidance/discipline_plain_explanation_each_step.md
.reviewcompass/guidance/discipline_plain_japanese.md
.reviewcompass/guidance/discipline_pre_action_precheck.md
.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md
.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md
.reviewcompass/guidance/discipline_workflow_precheck_invocation.md
docs/disciplines/README.md

# Target document
## .reviewcompass/guidance/discipline_avoid_compound_bash.md

---
name: avoid-compound-bash
description: 読み取り目的の複合 Bash コマンドを避ける。Read／Glob／Grep ツールで代替するか、Bash は単一コマンド 1 つに留める
metadata:
  type: feedback
---

読み取り目的（ファイル列挙、行数集計、文字列検索、ログ末尾確認など）で Bash を呼ぶときは、次の優先順位で対応する：

1. **Read ／ Glob ／ Grep ツールを使う**（Bash を呼ばない、許可プロンプト発生せず）
   - ファイル内容を見る → Read
   - パス・ファイル列挙 → Glob
   - 文字列検索 → Grep
2. Bash が必要な場合は **単一コマンド 1 つ** に留める
3. 複数情報が必要なら **複数の独立した Bash 呼び出しに分ける**（並列実行可、許可リストが効く）

**避けるべきパターン**：`;`／`&&`／`|` で複数コマンドを繋ぐ複合 Bash。例：`tail file.log; ls dir/ | grep pattern | wc -l`

**Why**：

Claude Code の permission 機構（許可リスト）は **単一コマンドのシグネチャ単位** で効く。複合コマンドは組み合わせごとに別シグネチャ扱いとなり、毎回新規承認プロンプトが発生する。利用者は毎セッション「許可をとるのが多すぎる」「同じ議論を何度もしている」と指摘してきたが、私の習慣として複合 Bash を多用し改善されていなかった。2026-05-28 セッション 36 で再指摘を受けて確立。利用者明示承認の出典：「案 イを処理」（規律本体を repo `docs/disciplines/` に新設、memory はシンボリックリンクで参照、2026-05-28 セッション 36）。

**How to apply**：

- Bash 呼び出しを書く前に自問：「Read／Glob／Grep ツールで代替できないか？」
- 代替できない場合：複合せず単一コマンドにする。`;`／`&&`／`|` の使用を最小化
- 複数情報を取りたい場合：複数の独立した Bash 呼び出しを並列発行（同じ応答内に複数 Bash ブロック）
- 例外：パイプが本質的に必要な場合（`grep | wc` の集計など）のみ複合を許容、ただし利用者承認の負担を意識
- 削除・書き込み・移動などの不可逆操作は規律 [[approval-operation]] に従い別途明示承認

**典型例**：

- × `cat file.log | tail -20`
- ○ Read file.log offset=… で末尾を読む
- × `ls dir/ | grep pattern | wc -l`
- ○ Glob で列挙、結果を Bash 不要でカウント
- × `git log --oneline; git status; git diff`
- ○ 3 つの独立した Bash 呼び出しを並列発行

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）、[[approval-operation]]（不可逆操作の明示承認）


## .reviewcompass/guidance/discipline_concise_complete_report.md

---
name: concise-complete-report
description: 利用者からプロンプトを受けて作業を行ったら、実施内容を簡潔にもれなく報告する。報告には何をどのファイルに対してどう変更したかを必ず含め、抜けや概数で済まさない
metadata: 
  type: feedback
---

利用者からプロンプトを受けて作業（編集・新規作成・削除・コミット等）を行ったら、応答の最後に **実施内容を簡潔にもれなく報告する**。報告には次を含める。

- どのファイルに対して
- どの箇所を
- どう変更したか（追加／削除／書き換え／移動）

抜け・概数・「主な変更」のような曖昧表現で済ませず、全件を列挙する。同種の変更が多い場合は件数を明示し、対象一覧（ファイル名・行範囲・キーワード）を簡潔に並べる。

**Why:**

セッション 14（2026-05-21）で、利用者から「指示して終了したと思っていたものをやっていない、それが取りこぼしになってバグになっている」と指摘された。私の状況報告は「やったことの行動ログ」を述べているだけで、利用者の指示に対して「全件完了したか」「抜けがないか」を機械的に照合していなかった。結果、利用者が「完了したと思って次に進む → 実は未完だった」という品質欠陥を繰り返した。

本規律は事後の透明性を保つ最終関門として機能する。事前の達成基準宣言（[[facts-vs-interpretation]]）と組み合わせると、「事前に何を達成すべきか宣言 → 事後に達成基準と照合して全件報告」という二段の品質保証になる。

本規律は、過去に PreToolUse フック `pre-write-self-check.sh`（agreement-quote と scope check の 2 行を毎編集ごとに強制）が担っていた「合意範囲の逸脱検出」機能を、より柔軟かつ低ノイズな形で置き換えるもの。フックは編集ごとに発火する重い検査だったが、本規律は応答末尾の報告に集約することで会話の流れを保つ。

**How to apply:**

## 報告の構造

- 応答の末尾（または明示的な「報告」見出し）で、当該プロンプトに対して実施した変更を **箇条書きで全件列挙** する
- 各項目に「ファイルパス」「変更内容（追加／削除／書き換え／移動）」「対象範囲（行番号・節番号・キーワード）」を含める
- 同種の変更（例：13 か所の用語置換）はまとめてよいが、件数と対象は明示する
- ファイル作成・削除・コミット・push は別項目として明示
- 「主な変更は」「いくつか修正」のような曖昧表現は使わない

## 報告の確認

- 報告した内容と利用者の指示を自分で読み返し、抜けがないか確認する
- 抜けがあった場合は報告に「（追加で確認したところ X も対象でしたが対応漏れ。次の応答で対応します）」を明示する
- 利用者が「他にもあるはず」と気づける材料を提供する

## 取りこぼし防止のため避けるべき行動

- 報告を省いて次の指示を待つ（「ご指示をお待ちします」だけで終わる）
- 報告内容を「やったこと」（行動ログ）に限定し、「達成基準を満たしたか」の照合結果を出さない
- 「○○件完了、残り△件」のような曖昧な進捗報告で、具体的な未完項目を出さない
- 利用者が指示した範囲を分割実行する際、最後に総括せず途中で打ち切る

## 既存規律との関係

- [[facts-vs-interpretation]] と相互補完：事前に達成基準を宣言し、編集後に grep／Read で照合し、その結果を本規律に従って報告する（事実と解釈を分けて報告）

関連：[[facts-vs-interpretation]]（達成基準の事前宣言と機械的照合 ＋ 事実と解釈の分離）


## .reviewcompass/guidance/discipline_facts_vs_interpretation.md

---
name: facts-vs-interpretation
description: 達成基準を事前宣言、編集後は機械的（grep／Read）照合、事実と解釈を別個に示し出典に辿れる形に（旧 3 規律統合：check-logs-and-git／separate-facts-from-interpretation／completion-verification-protocol、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

事実は記憶でなく出典（ファイル行・コミット・ログ）で確認し、解釈と明示的に分けて示す。

**達成基準と検証のプロトコル：**

- 指示を受けたら冒頭で達成基準を箇条書きで宣言
- 編集後は grep／Read で機械的に照合し、出典を残す
- 報告の中心は「やったこと」でなく「達成基準と現状の照合結果」
- 完了承認後は基準を満たすまで作業継続

**事実と解釈の区別：**

- 完了・適合・GO を断定せず、検証可能な証拠と「満たした／満たさない」で示す
- 主張・報告は必ず出典（ファイル行・コミット）に辿れる形にする

**Why:** 旧 3 規律（check-logs-and-git／completion-verification-protocol／separate-facts-from-interpretation）を統合（2026-05-25 セッション 24）。事実根拠と機械的確認と解釈の分離は密接に関連する一連の規律で、一体運用が自然。過去の失態：記憶に頼って事実と異なる断定をした、達成基準を宣言せず「やったこと」を報告して齟齬が露見、解釈と事実を混在させて利用者に誤伝した。

**How to apply:**

- 指示を受けたら冒頭で「達成基準の宣言」節を出力
- 編集後に grep／Read の出力を引用して「達成基準 N が満たされている」を機械的に証明
- 報告は「やったこと」ではなく「達成基準 N → 検証結果」の形式
- 機械化の一部は段階 2 スクリプト（[[workflow-precheck-invocation]]）が代行するが、宣言と報告の構造は LLM の責務
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 3 ファイルを参照


## .reviewcompass/guidance/discipline_implementation_autonomy.md

---
name: implementation-autonomy
description: 実装（コード編集・TDD・テスト実行）は per-task 承認で止めず自律的に進める。コミット／プッシュ／spec.json 承認／フェーズ移行のみ明示承認を維持
metadata: 
  type: feedback
---
実装フェーズでは、タスク（例：統治 Task 14→15→16→18）ごとに「説明→承認待ち」で止めない。テスト駆動で実装し、テストは許可リストに一致する単一コマンドで実行し、連続して次タスクへ進む。

**Why:** 利用者の明示指示「実装はできるだけ許可不要で進める」（2026-05-18 セッション9、強制関数実装中）。per-task の平易説明＋承認ゲートは丁寧すぎて進行が遅い、と判断された。

**How to apply:**
- 適用対象＝ローカルで可逆な作業（コード編集、TDD のテスト作成・実行、設計正本に基づく実装）。各タスク完了時は簡潔な進捗のみ報告し、承認を待たずに次タスクへ。
- 適用外（従来どおり明示承認が必須）＝コミット、プッシュ、spec.json の approve、フェーズ移行（feedback_approval_required は不変）。
- 平易な日本語・ジャーゴン抑制の応答品質規律は維持。止めないだけで説明を省くわけではない。
- スコープ外の改変はしない（合意範囲を超える追加・リファクタは引き続き禁止）。判断が要る分岐や正本不在の曖昧点のみ質問する。


## .reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md

---
name: intent-conformance-is-the-acceptance-gate
description: 実装の受け入れ基準は「フルスクラッチで作ったか」でなく「実装されたコード・システムが意図どおりに機能するか（承認仕様＝意図に適合するか）」。フルスクラッチは手法でありゲートではない
metadata: 
  type: feedback
---

実装成果を受け入れてよいかの判定基準（acceptance gate）は、「フルスクラッチ開発だったか否か」ではなく、「実装されたコード・システムが意図どおりに機能するか＝承認済み仕様（要件・設計・タスク＝意図）に適合するか」である。

**Why:** 利用者決定 2026-05-19（統治フィーチャーの扱いを巡る議論の中で確定）。理由＝「フルスクラッチか」はワークフローのゲートで検証できず（成果物-対-仕様しか検査しない）、自信をもった誤った「完了」宣言を生んだ（統治を部分修正で済ませ独断確定→偶然発覚）。本質的に重要なのは作り方でなく、できたものが意図どおり機能するか。それは承認仕様＋再実行可能な証拠で実体的に確認できる。フルスクラッチは依然として推奨されうる手法だが、それ自体は受け入れゲートではない。

**How to apply:**
- 実装が受け入れ可能かを判断するときは、手法（スクラッチか部分修正か）でなく「承認仕様＝意図への適合」を基準にする
- 適合確認は信頼できる証拠で行う：機械化できる部分は再実行可能な決定的検査（テスト・不変条件・差分再導出）の生出力、機械化できない意図部分（プロセス契約など）は人間または別系統モデルの判断。単一LLMレビューの要約を適合の根拠として断定しない（[[standing-directives-are-hard-constraints]] と一体）
- 「フルスクラッチ要件」は本基準へ改定済み。ただし利用者が個別に手法を指示した場合はその指示が優先（指示は硬い制約＝[[standing-directives-are-hard-constraints]]）
- 「テスト緑＝意図適合」と短絡しない。回帰テスト緑は「符号化済み期待が壊れていない」を測るのみ。意図適合の証拠としての強さはテストの仕様忠実度に依存（[[implementation-autonomy]] の自律進行も本基準下で運用）

**重要：[[standing-directives-are-hard-constraints]] との衝突解決（セッション 12 利用者裁定 2026-05-19）**

本基準（意図適合）と恒常指示（[[standing-directives-are-hard-constraints]]、例：全機能フルスクラッチ）が衝突する場合は **恒常指示が優先する**。本基準だけを根拠に「意図適合すれば手法は問わない」と独断で部分修正を確定してはならない。衝突が認められたら、自律確定せず利用者に明示してエスカレーションし、利用者の裁定を仰ぐ。セッション 12 で本基準のみを根拠に統治を部分修正で確定した結果、恒常指示「全機能フルスクラッチ」に違反した重大な過失が発覚した経緯による。


## .reviewcompass/guidance/discipline_must_fix_discussion_obligation.md

---
name: must-fix-discussion-obligation
description: triad-review 段で must-fix と判定された所見の対処は利用者と必ず議論する。独自判断で仕様文書を修正することを禁ずる。各推奨案には後段影響の深掘りを義務付ける。
metadata: 
  type: feedback
---

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM）が独自判断で仕様文書（design.md／requirements.md／tasks.md／implementation.md）を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**Why**：2026-05-25 セッション 25 で、foundation／design の must-fix 7 件の対処内容を私が独自判断で起草し design.md に反映、コミット・push まで進めた事案が発生。利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」で気づき進行を中断。その後の議論で「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」と指摘を受け、本規律として確立した。

**How to apply**：

- 正本手順：運営ガイド `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-1) must-fix 所見の対処手順 を参照する。本 memory は参照リンクのみで、規律本体は運営ガイドが正本
- triad-review 完了後、must-fix 所見を 1 件ずつ取り上げ、利用者と議論しながら平易な日本語で対処方針を提案する
- 各推奨案には必ず後段影響の深掘り（下流仕様・対象アプリ配置・機械検証・実装運用・将来拡張）を含める
- 「現状維持を推奨」する場合も、現状維持の弱点を検証してから示す
- 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
- 候補案は必ず複数提示、代替案との比較を欠かない
- API 経由の review-run で `ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を扱う場合、この規律は「利用者に提示して承認を得る」という会話上の義務だけを定める。`review_triage.py decide`、manifest 生成、承認レコード要件などの機械ゲートは `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` の `post_write_verification` 分岐を正本とする

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）


## .reviewcompass/guidance/discipline_no_redundant_workflow_questions.md

---
name: no-redundant-workflow-questions
description: 波進行など正本ワークフローが順序・方式を既定する局面で、機能ごとに止めて利用者へ進め方を尋ねない
metadata: 
  type: feedback
---
正本ワークフローが進行順序・単位を既に規定している局面では、機能ごとに止めて「ここで確認するか／まとめて進めるか」を利用者に尋ねない。手順どおり手を止めず進める。

**Why:** タスクフェーズ着手時、方式（全面再導出）も波順（基盤→実行側→評価→自己改善→論文→横断整合ゲート→統治）も正本（WORKFLOW_OVERVIEW 節 2、phase-and-feature-dependency-map §5.1「1 つ書き切って終わりではなく wave として横に広げてから alignment する」）で確定済みなのに、基盤タスク再生成後に進行単位を尋ね「愚問」と指摘された。正本が答えを持つ質問は利用者の時間を奪うだけ。

**How to apply:** 質問の前に自問する——「この答えは正本文書（WORKFLOW_OVERVIEW / 依存マップ / HUMAN_WORKFLOW / spec.json）に既に書かれているか？」。書かれていれば質問せず正本どおり進める。質問してよいのは、正本が沈黙している分岐（例：差分追従型 vs 全面再導出型のような方式選択で前例も指示もない場合）と、spec.json approve / commit / push / phase 移行の明示承認のみ。


## .reviewcompass/guidance/discipline_normal_output_minimization.md

---
name: normal-output-minimization
description: CLI / tool の正常系出力を最小化し、異常系と機械可読出力には必要情報を残す
metadata:
  type: feedback
---

# 正常系出力最小化

CLI / tool の人間可読出力は、正常系では利用者が次に進むために必要な最小情報だけを出す。異常系では原因、現在状態、次に取れる行動を省略しない。機械可読出力は `--json` などの明示オプションに集約し、詳細情報を保持する。

## 原則

- 正常系の人間可読出力は 1 行から数行に抑える。
- 正常系では内部判定、全入力、詳細な current state、長い候補一覧を既定出力に出さない。
- 異常系では、判定結果、原因、対象ファイル、現在状態、次の許可 action を出す。
- `--json` は詳細を落とさない。自動処理、監査、デバッグ、ログ連携は `--json` を使う。
- `--verbose` がある場合だけ、正常系でも詳細ログを出してよい。
- 非定型処理は、利用者が状況を理解するために必要な短い説明を許容する。ただし定型化できる処理は CLI 側へ寄せる。

## CLI 実装契約

新規または改修する CLI / tool は、次の出力面を分ける。

| 出力面 | 契約 |
|---|---|
| 正常系 human output | 成功事実と対象 action だけを短く出す |
| 警告系 human output | 警告理由、続行可否、必要な人間判断を出す |
| 異常系 human output | 停止理由、壊さないために行わなかった処理、次 action を出す |
| `--json` output | 判定、理由、対象、状態、証跡パスを完全に出す |
| `--verbose` output | 調査・保守に必要な詳細を出す |

## 適用手順

1. 既存 CLI / tool を棚卸しし、正常系出力が多いもの、対話で頻出するもの、不可逆操作に近いものを優先する。
2. 正常系 human output の期待をテストに固定する。
3. 異常系 human output と `--json` の情報量が落ちていないことをテストする。
4. 実装では、判定データの生成と human formatter を分ける。
5. 正常系の詳細を削る場合も、JSON / log / manifest のどこかに監査可能な詳細を残す。

## 棚卸し

共通棚卸しの正本は `docs/notes/working/2026-06-19-normal-output-minimization-tool-inventory.yaml` とする。各 tool の対応状態、優先度、次 action はこの YAML を更新する。

## 既存規律との関係

- [[concise-complete-report]]: 最終報告は簡潔かつ漏れなく行う。本規律は CLI / tool の通常出力を対象にし、LLM の最終報告そのものを省略しない。
- [[facts-vs-interpretation]]: 正常系で省略した詳細も、必要なら JSON / log / manifest から事実確認できるようにする。
- [[workflow-precheck-invocation]]: 不可逆操作直前の検査は維持する。ただし OK の既定 human output は最小にする。


## .reviewcompass/guidance/discipline_options_presentation.md

---
name: options-presentation
description: 複数案提示時の規律 — dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設、2026-05-26 セッション 27）
metadata:
  type: feedback
---

利用者に複数の選択肢を提示する際、dominated 案（明らかに他案に劣る案）は提示しない。提示前に内部検査結果を応答内で明示宣言し、合理案のみを階層性を守って並べる。

**Why:** 旧 2 規律（dominant-dominated-options ／ choice-presentation）を統合し事前検査宣言義務を新設（2026-05-26 セッション 27）。旧 dominant-dominated-options（参照層）は決定の瞬間に発火しない構造的欠陥が露見（利用者発言「規律が効いていない」）、active 必読昇格と事前宣言義務の併設で対処。

## 対象範囲（2026-05-26 セッション 27 で明確化）

本規律の対象は **利用者に判断を仰ぐ複数案提示の応答**（レビュー／設計議論／実装議論の中で利用者の選択を仰ぐ場面）に限定する。

**対象外**：

- **設計文書内の比較記述**：design.md ／ requirements.md ／ tasks.md 等の仕様文書内で複数の選択肢を列挙し、採用案を確定する記述（経緯記録の性格を持ち、利用者の判断を仰ぐ場面ではない）
- **過去の議論経緯の引用**：archive 配下の旧文書や履歴記述中の複数案列挙
- **規律本体の説明**：規律ファイル内の例示

**対象範囲明確化の理由**：本規律の本来目的は「利用者の判断負荷を減らす」「dominated 案を提示しない」こと。設計文書内の経緯記録に同様の事前検査宣言を要求すると、設計文書が宣言だらけになり可読性が落ちる。経緯記録の自由度を保つため、規律の射程を「利用者判断を仰ぐ場面」に限定する。

**利用者明示承認の出典**：「候補 3」（規律の対象範囲を明確化する小改訂、2026-05-26 セッション 27 の conformance-evaluation／design.triad-review／G8 議論）。

## How to apply

### 1. dominated 判定の厳密化 3 規律（必須適用）

dominated と判定する案ごとに：

- **合理的成立条件 1 文以上**：その案が合理になる前提（規模・利用頻度・UX 重視等）を記述
- **量的主張には numerical 規模感**：性能 = ms/s ／ コスト = LOC など、抽象論禁止
- **暗黙前提**：前提が変わると判定が反転する場合は依存性を明記

3 規律のいずれも満たさず合理的成立条件が思い浮かばない案のみ「真の dominated」と判定可。

### 2. 事前検査宣言義務

複数案を提示する応答を作る前に、応答内で次を明示宣言する（[[facts-vs-interpretation]] の事前宣言と同型）：

- **(a)** 内部検討した候補の総数
- **(b)** 各案に上記 3 規律を適用した結果
- **(c)** dominated と判定して除外した案（除外理由つき）
- **(d)** 残った合理案だけを提示

宣言は応答に埋め込み、grep で事後集計可能な形を保つ。効果は `docs/discipline-compliance-reports/options-precheck-log.md` で計測。

### 3. 残った合理案の提示

- **ラベル必須**：【文言確定済】【選択肢あり】【SSoT 判定要】【範囲拡張】のいずれかを明示
- **階層性**：大局（方針）→ 細部（具体案）の順。同一ターンで並列禁止
- **3 選択肢以内**：4 個以上並ぶなら大局判断を分離する設計が間違っている疑い
- **メリデメは 2〜3 点**：長文比較表は判断負荷を上げる
- **推奨を明示**：「推奨で進める」と一言で答えられる形に
- **物理レイアウト例外**：ファイル配置・パス命名等は ASCII ツリー＋比較表＋判断軸要約の 3 点組み

## 関連規律

- [[approval-operation]]：選択肢提示後の承認は別工程、明示承認必須
- [[facts-vs-interpretation]]：事前宣言の同型構造
- [[pre-action-precheck]]：別の事前検査チェックリスト（集約・横断操作向け）

## 統廃合元

`docs/disciplines/archive/2026-05-26-consolidation/` の旧 2 件（discipline_dominant_dominated_options.md ／ discipline_choice_presentation.md）に詳細例と経緯あり。


## .reviewcompass/guidance/discipline_plain_explanation_each_step.md

---
name: plain-explanation-each-step
description: must-fix 適用など 1 件ずつ承認の各ステップで、利用者が都度求めなくても承認前に平易な日本語説明を先に添える
metadata: 
  type: feedback
---
1 件ずつ承認で進める各ステップ（must-fix 適用、spec.json 変更、文書修正など）で、利用者が「平易に説明」と都度指示しなくても、承認を求める前に必ず平易な日本語の説明（何が問題か・どう直すか・意図は変わらないか）を先に添える。

**Why:** 統治要件 9 の must-fix を 1 件ずつ適用中、利用者が #1・#2 と続けて「平易に説明」を要求し、最後に「以降も同様」と明示した。毎回求めさせるのは手間で、説明は既定動作にすべきという指示。

**How to apply:** 1 件ずつ承認のシーケンス（レビュー must-fix、spec.json 反映、横断整合の C 群対応など）では、英語技術用語の羅列を避けた完全な日本語の文で「問題／修正内容／意図不変か」を述べてから承認を求める。技術用語は初出時に意味併記。feedback_plain_japanese の一般規律を、承認ステップで先出し必須として具体化したもの。


## .reviewcompass/guidance/discipline_plain_japanese.md

---
name: plain-japanese
description: 英語技術用語を多用しない。完全な日本語の文で書く。応答送信前に自己検査する。
metadata: 
  type: feedback
---
## 問題点

英語技術用語の混入と「(= ...)」の連発で意図が伝わらない。

## 特に気をつけること

完全な日本語の文で書く。英語の技術用語を使うときは、初出時に意味を併記する。

## 応答送信前の自己検査 (59 回目セッション追加)

応答を生成し終わったら、送信ボタンを押す前に自分で次の検査を実施する。フックの事後検出に頼らない。

**Why:** ジャーゴン検査フックが事後検出して書き直しを要求する運用が繰り返されると、user 側の体験を著しく損なう (= 1 つの応答に対して 2 〜 3 回書き直しが発生する)。59 回目セッションで「ジャーゴンを検知して、書き直し、またジャーゴンを検知して書き直す。ここも体験が損なわれる。1 回で済むようにする」と user から明示の指摘を受けた。

**How to apply:**

- **検査対象の典型ジャーゴン**: dev_log / rework_log / treatment / treatment-dual / treatment-single / Adjacent Sync / pristine state / escalate / forced_divergence / metapattern など (= dual-reviewer 方法論内部用語)
- **置き換え方針**: 修正履歴の記録 / 1 人レビュー実験用ブランチ / 2 人レビュー実験用ブランチ / 他仕様書への波及通知 / 修正前の元状態 / 単独判断せず user 判断を仰ぐ / 暗黙前提を別前提に置き換える検証 / パターン分類
- **検査の閾値**: 同じジャーゴンが 3 回以上出現する場合、確実にフック検出されるので必ず書き直す
- **不可避な場合**: ファイル名や schema 名で固有名詞として登場する場合は初出時に意味を併記する。固有名詞の使用は最小限に留める。
- **送信前最終チェック**: 応答全体を見渡し、ジャーゴン濫用がないか目視確認する


## .reviewcompass/guidance/discipline_pre_action_precheck.md

---
name: pre-action-precheck
description: 集約・横断操作（≥3 file 操作、確定事項表作成等）の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示（旧 2 規律統合：aggregation-self-check／multi-file-dependency-precheck、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

集約・横断操作の前に、応答内で事前検査チェックリストを明示し、grep で対象を全件列挙する。

**集約局面（確定事項表・採用方針一覧等）の事前検査 5 項目：**

1. 各項目に承認発言の出典は併記されているか（[[approval-operation]] 連動）
2. 確定済み論点と未確定論点が区別されているか
3. workflow_state（spec.json）の状態と整合しているか（[[workflow-state-truth-source]] 連動）
4. 過去確定との矛盾はないか
5. 利用者の最新発言と整合しているか

**多 file 操作（≥3 file）の事前検査：**

- grep 実行で対象を行番号付き全件提示
- 3 分類で categorize（編集／追記／削除、または機能内対処／波及／遡及）
- scope 独立検証（提案範囲が利用者意図と一致するか）

**波及調査の網羅性（2026-06-02 セッション 47 追加）：**

ある変更が他機能・他文書に波及するかを調べるときは、影響を受けうる **全対象**（全機能・全文書）を **全表記**（機械可読の識別子と人間可読の和訳の両方、例：`review_mode` と「レビューモード」）で網羅 grep し、波及の全範囲を確定してから対処に着手する。部分的な対象・単一表記での調査で着手すると、調査漏れにより同じ再オープン手続きを繰り返すことになる。

**Why:** 旧 2 規律（aggregation-self-check／multi-file-dependency-precheck v2.1）を統合（2026-05-25 セッション 24）。事前検査は集約局面と多 file 操作の両方で必要、規律として一体で扱う方が自然。過去の経緯：aggregation-self-check はセッション 21 の表作成前自己検査として制定、multi-file-dependency-precheck v2.1 はセッション 22 で旧 pre-action-checklist を統合した経緯がある。波及調査の網羅性は 2026-06-02 セッション 47 で追加：foundation の `review_mode` 正本への `api_mediated` 追加の波及対処で、英語表記「review_mode」のみ・部分機能のみの調査で着手したため、日本語表記「レビューモード」の箇所や残りの機能を取りこぼし、再オープン手続きを 3 回繰り返した失敗が出典。

**How to apply:**

- 確定事項表・採用方針一覧を書く前：5 項目チェックリストを応答内で明示宣言、書く前の事前検査として実行
- 3 file 以上の操作前：grep ＋ 全件提示 ＋ 3 分類 ＋ scope 独立検証を実施
- 段階 2 スクリプトの機械検査では捕捉できない（応答内の宣言で守る）
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 2 ファイルを参照


## .reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md

---
name: reopen-procedure-for-settled-topics
description: 一度確定した論点を再考する場合の手順、明示承認なしでの再確定を禁止
metadata: 
  type: feedback
---

一度利用者の明示承認で確定した論点を再考する場合は、次の手順を踏む：

1. **再オープンの宣言**：「論点 N を再オープンしたい」と明示する
2. **再考の理由を述べる**：他論点との整合崩れ、新情報の発見、矛盾の発覚など、再考が必要になった理由を具体的に説明
3. **新しい結論案の提示**：AskUserQuestion で選択を仰ぐか、明示的な質問形式で利用者の判断を求める
4. **明示承認の取得**：「論点 N を ○○ に再確定します」という利用者の明示承認発言を必ず取る（[[approval-operation]] に従う）
5. **再オープン履歴の記録**：設計メモ・TODO 等に「再確定：YYYY-MM-DD、旧確定 ○○ → 新確定 ××、根拠 line NN」と履歴を残す

**Why:** セッション 20 で論点 1（spec.json の階層範囲）の再オープン提案後、私が利用者の「議論継続指示」「計画書再読指示」を黙示の同意と誤解し、「6 階層 → 4 階層」と確定を書き換えた。この一連の流れには「再オープン提案」「議論継続」「計画書再読」「私の整理」「命名指摘」「私の確定書き込み」と多くのステップがあったが、どこにも利用者の「論点 1 を 4 階層に再確定する」という明示承認発言が存在しなかった。一度確定したものを変更する重大さに対し、手順が明文化されていなかった。

**How to apply:** 確定済み論点に変更を提案する前に本手順を意識する。特に「整合性の取り直し」「他論点との連動」を理由に既存確定を変えるとき、論理的に導けても利用者の明示承認なしでは「確定」と書いてはならない。再オープン履歴は読者が「なぜ変わったか」を追跡できるよう、旧確定・新確定・根拠ログ行を併記する（[[approval-operation]] と一体）。


## .reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md

---
name: standing-directives-are-hard-constraints
description: 恒常的な利用者指示（フルスクラッチ等）は既定でなく硬い制約。approach を変える決定はレビュアー/自分の技術判断で自律確定せず、恒常指示と突き合わせ衝突あれば必ずエスカレーション
metadata: 
  type: feedback
---

恒常的な利用者指示（例：6機能すべてフルスクラッチ再構築、旧コードを中途半端に流用しない＝[[implementation-autonomy]] と一体の利用者方針）は、「技術的に妥当なら外してよい既定」ではなく「approach を縛る硬い制約」として扱う。

**Why:** セッション12で統治中核を、独立適合レビューの「部分修正で技術的に足りる」推奨を採用して部分修正で確定させた。だが利用者の恒常指示は「全機能フルスクラッチ」。記憶にその指示はあったのに、approach 変更決定を縛る硬い制約として扱わず、「技術的に十分」を「やってよい」と取り違えた。ワークフローのゲート（仕様適合・回帰テスト）は「作り方の制約」を検証しないため全ゲート通過し、利用者の偶然の問い（「全てフルスクラッチの筈」）でしか露見しなかった。重大な見逃し。

**How to apply:**
- approach を変える決定（スクラッチ↔部分修正、再実装↔既存流用、reopen↔task内吸収など「やり方そのもの」を選ぶ判断）に直面したら、着手前に恒常指示・記憶された利用者方針と必ず突き合わせる
- レビュアー（サブエージェント）や自分が技術的に「部分で足りる／不要」と判断しても、それは恒常指示を上書きしない。技術的十分性 ≠ 許可。恒常指示に触れる approach 変更は利用者の判断事項
- 衝突または衝突の疑いがあれば自律確定せず、「レビュアーは X を技術的に推奨。ただし恒常指示は Y。どちらが支配するか」と明示してエスカレーション。「止めず合理的判断で進める」指示があっても、恒常指示との衝突点はその例外（commit/push/spec.json/phase/設計差し戻し判断と同格の承認点）
- 言われた指示は必ず明示的な不変条件として記憶化し、決定点で参照する。これでも未言明の指示は防げない＝人手判断はゼロにできない、と認識する

**重要：[[intent-conformance-is-the-acceptance-gate]] との衝突解決（セッション 12 利用者裁定 2026-05-19）**

[[intent-conformance-is-the-acceptance-gate]]（意図適合が受け入れ基準）と本規律が衝突する場合は **本規律（恒常指示）が優先する**。意図適合のみを根拠に手法（スクラッチ↔部分修正）を自律変更してはならない。意図適合は「できあがったものを受け入れるかの基準」を扱い、本規律は「作り方の選択に対する制約」を扱う。両者は機能が異なり、作り方が恒常指示の制約に違反していれば、意図適合していても受け入れない（あるいは利用者裁定を仰ぐ）のが本規律の趣旨である。

関連：[[approval-operation]]（承認点）、[[implementation-autonomy]]（自律進行の範囲。本規律はその境界＝approach 変更は自律の外）、[[intent-conformance-is-the-acceptance-gate]]（意図適合の受け入れ基準、衝突時は本規律が優先）


## .reviewcompass/guidance/discipline_workflow_precheck_invocation.md

---
name: workflow-precheck-invocation
description: 不可逆操作（spec.json 変更／git commit／git push）の直前に現行の precheck 入口を呼び、判定結果を応答内で明示する
metadata: 
  type: feedback
---

ReviewCompass の不可逆操作の直前に、必ず現行の precheck 入口を呼び、
出力の verdict と reasons を応答に書く。通常の作業開始時は先に
`.venv/bin/python3 tools/check-workflow-action.py next --json` を確認し、
`next_action.required_disciplines` に示された規律だけを作業直前に読む。

**対象操作と呼び出し：**

- spec.json の workflow_state を変更する直前：
  `.venv/bin/python3 tools/check-workflow-action.py spec-set <feature> <phase> <stage> <true/false> [--rationale "..."]`
- 利用者が commit を指示した直後、git add や approval record 作成の前：
  `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json`
- git push の直前：
  `.venv/bin/python3 tools/check-workflow-action.py push --rationale "<理由>"`
- 別作業を開始する直前：
  `.venv/bin/python3 tools/check-workflow-action.py work-unit preflight-start --proposed-unit-file <path> --json`

**判定結果の扱い：**

- exit 0（OK）：続行
- exit 1（WARN）：警告を応答に明示し、人の判断を仰ぐ（自律続行しない）
- exit 2（DEVIATION）：処理を止めて人に報告、原因を是正してから再試行

**段階 1 と段階 3 の責務分担：**

段階 3 フック（`.claude/hooks/pre-bash-precheck.sh`）が Bash の git commit／push を
PreToolUse で自動検査するようになったが、段階 1（LLM 自身の意図呼び出し）は依然
として必要：

- **依然として LLM が必ず呼ぶ**：spec.json 修正（Edit／Write）の直前。段階 3 は
  Bash 系のみ実装済みであり、Edit／Write の spec.json 検知は未対応
- **LLM が呼ぶことが望ましい**：git commit／git push の直前。段階 3 が自動発動する
  が、LLM が事前に呼べば応答内で verdict／reasons を共有でき、人間判断との連携
  が滑らか
- **「呼び忘れ」の救済**：段階 3 フックが exit 2 で遮断するため、LLM の見落とし時も
  Bash 系はブロックが効く。ただし応答テキストのみの判断（フックが効かない領域）
  は段階 1 規律が恒久的に担う

**Why:** LLM が段階 2 のスクリプトを呼ばないと機械検査の効果が消える。
仕様 `.reviewcompass/guidance/WORKFLOW_PRECHECK.md`「段階 1・段階 3 との接続」で
規定された段階 1 規律の文書化。

**How to apply:**

- 「直前」とは、対応する Edit／Write／Bash 呼び出しの直前
- `--rationale` には人の承認発言や操作理由を渡し、ログ `.reviewcompass/runtime/logs/workflow-precheck.log` に残す
- [[approval-operation]] の機械検査による補強。
  当該規律が言う「承認なしで進めない」を構造的に強化する
- 不可逆操作で恒常的に運用する


## docs/disciplines/README.md

# 規律ファイルの旧配置（disciplines）

最終更新：2026-06-19（`discipline_normal_output_minimization.md` を新設、active 必読昇格。CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する共通規律。利用者指示「全 CLI / 全ツールへ広げるなら、別途『正常系出力最小化』の共通規律と各ツールの棚卸し。これを対応」に基づく）／2026-06-18（イレギュラー組み込み：`discipline_llm_as_judge_prompting.md` を新設、active 必読昇格。3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。通常の drafting→review→approval 手続きを省略し利用者明示承認「強制的に組み込みたい」「はい」で即時発効）／2026-06-02（セッション 50：`discipline_yaml_audit.md` を新設、active 必読昇格。設定・動作仕様 yaml 専用の監査規律（補助層 E）。独立 3 系統で 2 回の検証ループを経て発効、利用者明示承認「承認」）／2026-05-31（セッション 41：`discipline_post_write_verification.md` を新設、active 必読昇格。本規律自身の起草に対し独立 3 系統で 5 回の検証ループを経て発効、OpenAI／Google で ALL_CLEAR 達成）／2026-05-26（セッション 27：旧 dominant-dominated-options ／ choice-presentation を統合し `discipline_options_presentation.md` を新設、active 必読昇格＋事前検査宣言義務を新設、旧 2 件は `archive/2026-05-26-consolidation/` へ退避。利用者明示承認「OK」「承認」）

過去履歴：
- セッション 27（2026-05-26）前半：シンボリックリンク検証失敗・fallback 案イ採用により、当時は毎セッション開始時に TODO §1 起動手順で active 必読を Read で読む運用に切り替えた。現在は `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` に従い、`tools/check-workflow-action.py next --json` の `next_action.required_disciplines` が示す場面別の規律だけを作業直前に読む。
- セッション 26（2026-05-25）：active 必読 12 件 ＋ 参照層 5 件＝合計 17 件を memory から軽量移送 → `no-unilateral-action` 撤去で 16 件 → memory 側 `feedback_*.md` をシンボリックリンクに変更

## 配置と所有

active 規律ファイルの正本は `.reviewcompass/guidance/discipline_*.md` へ移動済みである。

本ディレクトリ `docs/disciplines/` は旧配置の説明と archive を保管する。**所有者は `workflow-management` 機能**（A-007 案 2、2026-05-23 利用者承認）で、active 規律の改廃は `.reviewcompass/guidance/discipline_*.md` を対象として本機能の所定手続き（drafting → review → approval）経由で実施する。

active 規律ファイルは `.reviewcompass/guidance/discipline_<name>.md` の命名規約に従う。`<name>` は規律内容を表す英語ハイフン区切り（例：`discipline_must_fix_discussion_obligation.md`）。

## 内部リンク記法

各規律ファイル本文に `[[link-name]]` 形式の内部参照（例：`[[approval-operation]]`、`[[workflow-precheck-invocation]]`）が登場する。これは memory 機構の慣習を引き継いだ記法で、本ディレクトリ内では次の規則で解決する：

- **`[[name]]`** → `.reviewcompass/guidance/discipline_<name>.md`
- 例：`[[approval-operation]]` → `discipline_approval_operation.md`
- 例：`[[workflow-precheck-invocation]]` → `discipline_workflow_precheck_invocation.md`

本記法は Markdown viewer によっては自動でクリック可能リンクとして解決されないが、内部参照の意図を明示する目的で維持する。Markdown リンク形式への一括変換は別途検討（フェーズ 2 以降の宿題）。

## 規律ファイル一覧

最新の件数は本一覧の各表（active 必読／参照層／archive）で確認すること。件数は本見出しには固定しない（増減の都度に編集箇所が分散するのを避けるため）。

### active 規律（`next --json` の required_disciplines に従い作業直前に読む）

| ファイル | 概要 |
|---|---|
| [discipline_must_fix_discussion_obligation.md](../../.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md) | triad-review の must-fix 所見は利用者と必ず議論、独自判断で仕様修正禁止 |
| [discipline_intent_conformance_is_the_acceptance_gate.md](../../.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md) | 受け入れ基準は「実装が意図どおり機能＝承認仕様に適合」か（フルスクラッチは手法でゲートでない） |
| [discipline_standing_directives_are_hard_constraints.md](../../.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md) | フルスクラッチ等の恒常指示は既定でなく硬い制約、approach 変更は自律確定せずエスカレーション |
| [discipline_workflow_precheck_invocation.md](../../.reviewcompass/guidance/discipline_workflow_precheck_invocation.md) | 不可逆操作の直前に tools/check-workflow-action.py を呼び verdict／reasons を応答に明示 |
| [discipline_approval_operation.md](../../.reviewcompass/guidance/discipline_approval_operation.md) | 不可逆操作は利用者明示承認必須、明示的肯定発言のみ承認、確定記述には承認出典を併記 |
| [discipline_facts_vs_interpretation.md](../../.reviewcompass/guidance/discipline_facts_vs_interpretation.md) | 達成基準を事前宣言、編集後は機械的照合、事実と解釈を別個に示し出典に辿れる形に |
| [discipline_pre_action_precheck.md](../../.reviewcompass/guidance/discipline_pre_action_precheck.md) | 集約・横断操作の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示。波及調査は全対象×全表記（機械可読の識別子と人間可読の和訳の両方）で網羅 grep してから着手（2026-06-02 セッション 47 追加） |
| [discipline_workflow_state_truth_source.md](../../.reviewcompass/guidance/discipline_workflow_state_truth_source.md) | 状態判定は workflow_state を読み、過去確定事項は出典付きのみ信頼 |
| [discipline_concise_complete_report.md](../../.reviewcompass/guidance/discipline_concise_complete_report.md) | 作業後は応答末尾で実施内容を箇条書きで全件列挙、ファイルパス・変更内容を必ず含める |
| [discipline_reopen_procedure_for_settled_topics.md](../../.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md) | 確定済み論点を変更する場合は 5 ステップ（宣言・理由・新案・明示承認・履歴記録） |
| [discipline_plain_japanese.md](../../.reviewcompass/guidance/discipline_plain_japanese.md) | 英語技術用語を多用しない、完全な日本語の文で書く、応答送信前に自己検査 |
| [discipline_options_presentation.md](../../.reviewcompass/guidance/discipline_options_presentation.md) | 複数案提示時、dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設） |
| [discipline_avoid_compound_bash.md](../../.reviewcompass/guidance/discipline_avoid_compound_bash.md) | 読み取り目的の複合 Bash コマンド（`;`／`&&`／`|`）を避ける、Read／Glob／Grep ツールで代替するか単一コマンドに留める、許可プロンプト多発の防止（2026-05-28 セッション 36 軽量移送で確立、利用者明示承認「案 イを処理」） |
| [discipline_post_write_verification.md](../../.reviewcompass/guidance/discipline_post_write_verification.md) | ワークフロー段の外側にある正本文書への書き込み後、起草者と異なる検証経路による独立検証を必須化。検出は逐語的指摘（弾く）と本質的指摘（人へ上げる）に分類して処理し、収束基準は動作仕様ファイル post-write-verification-spec.yaml と現行 API variant 設定に従う。2026-05-31 セッション 41 新設・2026-06-01 セッション 43 収束基準改訂 |
| [discipline_yaml_audit.md](../../.reviewcompass/guidance/discipline_yaml_audit.md) | 設定・動作仕様 yaml（config/, runtime/config/, stages/, .reviewcompass/specs/ 配下）への書き込み後に監査を必須化する規律（補助層 E）。md 用書き込み後検証（補助層 D）とは別立て。11 観点（A 系統：機械検査 6 必須＋2 推奨、B 系統：独立検証 3 必須）で点検。新規対象の組み入れ時に全件を初回検証。2026-06-02 セッション 50 新設 |
| [discipline_llm_as_judge_prompting.md](../../.reviewcompass/guidance/discipline_llm_as_judge_prompting.md) | 3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。材料揃え（メインLLMが問題を直接検討）→ 問い設計（情報・問い・範囲の3要素）→ 選択肢なし分析の手順で品質を高める。2026-06-18 セッション 新設 |
| [discipline_normal_output_minimization.md](../../.reviewcompass/guidance/discipline_normal_output_minimization.md) | CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する。共通棚卸し YAML を更新しながら全 tool へ段階適用する。2026-06-19 新設 |

### 参照層（3 件、必要時に grep／Read で参照、起動時 load なし）

| ファイル | 概要 |
|---|---|
| [discipline_no_redundant_workflow_questions.md](../../.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md) | 正本ワークフローが順序・方式を既定する局面で機能ごとに止めて尋ねない |
| [discipline_plain_explanation_each_step.md](../../.reviewcompass/guidance/discipline_plain_explanation_each_step.md) | 1 件ずつ承認の各ステップで承認前に平易な日本語説明を先に添える |
| [discipline_implementation_autonomy.md](../../.reviewcompass/guidance/discipline_implementation_autonomy.md) | 実装フェーズはタスクごとに止めず自律進行、コミット／プッシュ／spec.json／フェーズ移行のみ明示承認 |

### archive（統廃合元・撤廃済みの本体保全、起動時 load なし）

| ディレクトリ | 内容 |
|---|---|
| [archive/2026-05-26-consolidation/](archive/2026-05-26-consolidation/) | セッション 27（2026-05-26）の統廃合元 2 件（旧 dominant-dominated-options ／ choice-presentation）。統合先は active 必読の `discipline_options_presentation.md` |

## 関連参照

- **対応する memory 側索引**：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/feedback_*.md`（短い参照索引、本体は本ディレクトリを Read で参照）
- **memory archive**（統廃合元 14 件）：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/archive/2026-05-25-consolidation/`
- **本機能の設計**：`.reviewcompass/specs/workflow-management/design.md` §責務境界の明確化
- **計画書 §5.21**：規律ファイルの ReviewCompass 方針への取り入れ手順
- **移送経緯**：本セッション 26（2026-05-25）の軽量手続きにより、active 必読 12 件＋参照層 5 件を memory から移管。2026-06-23 の guidance relocation により、active 本体は `.reviewcompass/guidance/` へ移動

