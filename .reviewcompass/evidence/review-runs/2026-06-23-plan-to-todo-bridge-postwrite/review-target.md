# Post-write Review Target

criteria_id: plan_to_todo_bridge_postwrite
phase: post_write_verification
generated_at: 2026-06-23T08:44:14.783483+00:00

## Change Summary

plan から TODO/checklist へ進む operation prompt を登録し、WARN または高リスク時に review materials を作る導線を effective prompt に固定する。

## Review Question

Verify that the workflow discipline map registration and canonical effective prompt correctly prevent direct plan-to-work execution, require TODO/checklist evidence, and route WARN or high-risk conversions to review materials without making triad review always mandatory.

## Target Files

- .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml sha256=c1ab2976322c0b74d8a5d3446e61e7ac28713252f0d5ad355d344b0aec8da65a
- .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md sha256=44b9a73f067a9c71eb786657bdb6311f60514c01c25c8ac394fdebdbef435cb8

## Source Materials

### .reviewcompass/guidance/WORKFLOW_NAVIGATION.md

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

### .reviewcompass/backlog/todos/todo-2026-06-23-plan-to-todo-checklist-evidence.yaml

content_mode: full_text
content_sha256: 6ef2ea4e573b022ec62287178c096aaca3171e4e628ef35199a9a2c3b34346ad

```text
schema_version: reviewcompass-backlog-item-v1
id: todo-2026-06-23-plan-to-todo-checklist-evidence
kind: todo
title: Preserve plan to TODO checklist execution evidence
status: candidate
source_unit_id: main-completed
created_at: '2026-06-23T08:25:46.734782+00:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: conversation:user:証跡としては、todoリストやチェックリストがあった方がよいと思う
  reason: plan から直接作業を進めると、実行単位化した TODO と checklist の証跡が残らず、後から進め方と完了根拠を追跡しにくくなるため
decisions: []
summary: >
  plan の implementation_plan を読んで直接作業へ入る運用を避け、
  実行前に backlog TODO と runtime checklist へ落としてから進める。
  作業完了後は completed checklist / evidence と TODO の execution_history に
  実行証跡を残し、plan、TODO、checklist、完了証跡のつながりを追跡可能にする。
problem_statement:
- plan は方針、分解案、受け入れ条件を持つが、実行単位そのものではない。
- plan から直接作業すると、どの部分を TODO として実行対象化したかが残りにくい。
- checklist なしで進めると、作業中の進捗と完了根拠が会話履歴に寄り、後続セッションから追跡しにくい。
- 完了後に checklist を後付けすると、実行中証跡ではなく回顧メモになり、証跡の意味が曖昧になる。
required_flow:
- plan の implementation_plan / acceptance_criteria / remaining work を読む。
- 実行対象にする範囲を backlog TODO として切り出す。
- "`work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。"
- "`work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` で coverage を確認する。"
- checklist item を進めながら作業し、完了時に checklist を close して evidence へ移す。
- TODO 側の execution_history に checklist_id、evidence_path、completion_summary を残す。
todos:
  design_contract:
  - id: PTC-1
    title: plan、TODO、runtime checklist、evidence の責務境界を明文化する
    status: pending
    detail: plan は方針、TODO は実行単位、runtime checklist は実行中進捗、evidence は完了証跡として扱う。
  - id: PTC-2
    title: plan から作業開始する前の TODO 化ルールを定義する
    status: pending
    detail: implementation_plan の phase/task、acceptance_criteria、残作業をどの単位で TODO に切るかを定義する。
  cli:
  - id: PTC-3
    title: plan 由来 TODO の作成または確認を促す導線を追加する
    status: pending
    detail: plan から次作業を開始する場面で、既存 TODO の有無を確認し、なければ TODO 作成へ進ませる。
  - id: PTC-4
    title: TODO から checklist 生成と coverage audit までを標準手順に組み込む
    status: pending
    detail: start-checklist と audit-checklist-coverage を実行前証跡として残す。
  audit:
  - id: PTC-5
    title: plan 直接実行の逸脱を検出または記録する
    status: pending
    detail: plan 由来の作業完了に対応する TODO/checklist/evidence がない場合、follow-up または deviation として残す。
red_tests:
- id: PTC-RT-1
  title: plan 由来作業に TODO がない場合に検出する
  expected: plan の作業が完了扱いになる前に、対応 TODO がない状態を DEVIATION または follow-up として検出できる
- id: PTC-RT-2
  title: TODO から checklist coverage を確認できる
  expected: plan 由来 TODO に対して runtime checklist が生成され、coverage audit が OK/DEVIATION を返す
- id: PTC-RT-3
  title: 完了後に TODO execution_history へ証跡が戻る
  expected: checklist close 後、TODO に evidence_path と completion_summary が記録される
non_goals:
- 完了済み作業に対して、実行時から存在したかのような checklist を後付けすること
- すべての plan を即時に TODO 化すること
- plan の内容を LLM 要約だけで実行 checklist に変換すること
notes:
- 既存の `work-backlog start-checklist` は TODO から checklist への導線であり、plan から TODO への導線は別課題として扱う。
- 既に plan から直接進めた作業は、必要に応じて retrospective execution trace または deviation/follow-up note として記録する。
```


## Target File Contents

### .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml

content_mode: full_text
content_sha256: c1ab2976322c0b74d8a5d3446e61e7ac28713252f0d5ad355d344b0aec8da65a

```text
# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
default_prompt_length_bounds:
  min_chars: 400
  max_chars: 20000
  failure_verdict: WARN
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_stop_point
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#feature_definition_required
        - .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: parent_resume_pending
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: blocking_unit_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_required
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: blocking_unit_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_mixing_risk
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_mixing_risk
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_unit_stale
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_unit_stale
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
    - id: post_write_human_decision_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - .reviewcompass/guidance/discipline_post_write_verification.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 1200
        max_chars: 60000
        failure_verdict: DEVIATION
    - id: review-wave
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 400
        max_chars: 12000
        failure_verdict: DEVIATION
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#commit
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#push
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#audit-commit
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#reopen-start
        - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#commit
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - .reviewcompass/guidance/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: user_initiated_plan_to_todo_bridge
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/todos/todo-2026-06-23-plan-to-todo-checklist-evidence.yaml
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md
    - id: user_initiated_backlog_todo_execution
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-backlog-todo-execution.prompt.md
    - id: user_initiated_task_quality_gate
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-task-quality-gate.prompt.md
    - id: user_initiated_task_quality_review_materials
      prompt_source_refs:
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/backlog/plans/plan-2026-06-22-user-initiated-backlog-checklist-effective-prompt.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/user-initiated-task-quality-review-materials.prompt.md
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - .reviewcompass/guidance/discipline_post_write_verification.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      canonical_effective_prompt_path: .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
        - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - .reviewcompass/guidance/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - .reviewcompass/guidance/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - .reviewcompass/guidance/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - .reviewcompass/guidance/discipline_yaml_audit.md
        - .reviewcompass/guidance/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  post_write_verification:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_verification
    - .reviewcompass/guidance/discipline_post_write_verification.md
  lightweight_self_check:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#lightweight_self_check
  parent_resume_pending:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#parent_resume_pending
  blocking_unit_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_required
  blocking_unit_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#blocking_unit_in_progress
  commit_mixing_risk:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_mixing_risk
  commit_unit_stale:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#commit_unit_stale
  post_write_policy_violation:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - .reviewcompass/guidance/discipline_post_write_verification.md
  post_write_human_decision_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - .reviewcompass/guidance/discipline_post_write_verification.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  reopen_in_progress:
    - .reviewcompass/guidance/REOPEN_PROCEDURE.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  maintenance_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md#feature_definition_required
    - .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - .reviewcompass/guidance/REOPEN_PROCEDURE.md
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  triad-review:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
    - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
    - .reviewcompass/guidance/discipline_approval_operation.md
  review-wave:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - .reviewcompass/guidance/discipline_workflow_state_truth_source.md
  approval:
    - .reviewcompass/guidance/discipline_approval_operation.md
    - .reviewcompass/guidance/WORKFLOW_PRECHECK.md#spec-set
    - .reviewcompass/guidance/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
```

### .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md

content_mode: full_text
content_sha256: 44b9a73f067a9c71eb786657bdb6311f60514c01c25c8ac394fdebdbef435cb8

```text
# Effective Prompt: User-Initiated Plan To TODO Bridge

## Decision Point
- group: operation_prompt
- id: user_initiated_plan_to_todo_bridge

## Purpose
ユーザが backlog plan または plan 内の一部作業を実行しようとしたときに読む。plan を実行単位へ変換する直前で、plan から直接実作業に入らず、backlog TODO、runtime checklist、coverage / quality audit、必要時の review materials へ接続する。

## Trigger Boundary
- ユーザが「次へ」「進める」「この plan を進める」など、plan 由来の実作業開始を指示した。
- `next --json` が completed で、次作業を backlog plan から選ぶ状態になった。
- plan の `implementation_plan`、`acceptance_criteria`、remaining work を読んで実装、整理、移行、監査へ入ろうとしている。
- plan の一部 phase / task だけを実行しようとしている。

plan を読むだけ、説明するだけ、優先順位を相談するだけの場合は、この bridge を開始しない。

## Required Inputs
- 対象 plan id または plan path。
- `.reviewcompass/backlog/index.yaml`
- 対象 plan 本文。
- 対応する既存 backlog TODO の有無。
- 現在の work unit stack。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
3. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
4. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
5. `work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。
6. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
7. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
8. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
9. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
10. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
11. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

## High-Risk Signals
- plan から複数の独立作業を切り出す必要がある。
- TODO の粒度や順序に迷いがある。
- `task-quality-check audit` が WARN を返した。
- red test の位置づけ、レビュー要否、または実行順序に判断が必要である。
- plan と既存 TODO/checklist の対応が曖昧である。

## LLM Scope
- ユーザの自然言語指示がどの plan 範囲に対応するかを読む。
- 既存 TODO が plan の対象範囲を十分に覆うかを説明する。
- WARN または高リスクの理由を利用者に平易に説明する。
- review materials を作る場合、送信前に認証情報、個人情報、不要な全文ログ、外部送信不可情報が含まれないか確認する。

## Prohibitions
- TODO/checklist がないまま plan から実作業へ進まない。
- plan 本文を読まずに path-only で TODO 化しない。
- plan の広い範囲を 1 つの曖昧な TODO に押し込まない。
- 3者レビューを常に必須化しない。
- WARN または高リスクを無視して実作業へ進まない。

## Stop Conditions
- 対象 plan または実行範囲が一意に定まらない。
- 対応 TODO が複数あり、どれを使うべきか判断できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
- WARN または高リスクについて、review materials 作成または明示判断が未了。
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
