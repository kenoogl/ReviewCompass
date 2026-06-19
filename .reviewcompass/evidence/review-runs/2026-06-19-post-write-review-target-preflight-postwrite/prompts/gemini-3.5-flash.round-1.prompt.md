prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: post_write_review_target_preflight_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T00:50:08.642667+00:00

## Change Summary

post-write API review 前に review-target を機械生成し、run_review は criteria-file と rendered prompt 証跡を保存するようにした。標準手順と配布 manifest も追従した。

## Review Question

post-write API review の標準手順が、短い criteria ID だけに依存せず、review-target 生成、criteria-file 利用、rendered prompt 保存、機微情報チェックを一貫して要求しているか。

## Target Files

- docs/operations/WORKFLOW_NAVIGATION.md sha256=f467affd2d8d842369a4b9e54fdd5322b1d230b427fca12bfc5c3205916fef73
- docs/operations/DEPLOYMENT.md sha256=4d7230eae5a6bd91ee7b427e99dd786174c6431a1591ed37d9326521f323ac8f
- deploy-manifest.yaml sha256=6500b168b1024b40d8848a1480ea44a9ab6ff8cfc139603a9786d38cf00bfa03
- stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml sha256=f625b5678e2cbe421f7fa7408ab41d5b7b6e1c1091fe88c37a65f38185ad8040

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
docs/operations/WORKFLOW_NAVIGATION.md
docs/operations/DEPLOYMENT.md
deploy-manifest.yaml
stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml

# Target document
## docs/operations/WORKFLOW_NAVIGATION.md

# ReviewCompass ワークフローナビゲータ共通手引き

この文書は、`tools/check-workflow-action.py next --json` の読み方を定める共通手引きである。

## 1. 最初に実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

出力 JSON の `next_action.kind` を、現在の作業順序・優先順位の正本として扱う。記憶、要約、TODO の候補欄だけを段取りの根拠にしない。

`next_action.required_disciplines` がある場合は、作業直前にそのファイルだけを読む。セッション開始時に長い規律群を一括で読んで記憶に頼るのではなく、機械判定された場面ごとの短い規律セットで挙動を調整する。対応表は `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を正本とし、`next --json` はその内容を機械可読に展開する。

`next_action.required_inputs` がある場合は、規律ではなく作業対象ごとの状態入力として扱う。`id`、`source_type`、`read_policy` を確認し、`path` がある場合でもファイル名そのものを一般規律に昇格しない。たとえば持ち越し台帳は、配布先プロジェクトごとに別ファイル、外部台帳、または未配置になり得るため、`unresolved_cross_scope_items` のような抽象入力として扱う。

機械可読な判定点では、判定点ごとに 1 本の effective prompt を読む。複数の元資料を直接ばらばらに読ませるのではなく、判定点に必要な規律・入力・次タスク方針を 1 本へ束ねた effective prompt を作り、その本文を LLM に読ませる。元資料は `prompt_source_refs` として保持し、実際に読ませた統合プロンプトは `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` で記録する。全判定点で同じ巨大な共通プロンプトを使わず、各判定点に必要な短い effective prompt を使う。

## 2. 判定結果の共通分岐

<a id="resume_in_progress"></a>

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。新しい作業を始めず、`next_action.file` に示された進行中ファイルを読む。

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

API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md>` を実行することである。外側から `zsh -c` で包まない。API key は配布物や設定ファイルへ書かず、利用者の shell 初期化で読み込まれる環境変数から渡す。Claude Code などの操縦実行面では、子プロセスの `ANTHROPIC_API_KEY` と `GEMINI_API_KEY` が空文字列へ上書きされることが確認済みである。一方、`OPENAI_API_KEY` は同じ確認では上書きされていない。このため `run_review.py` / `run_role.py` entrypoint 内で、環境変数が未設定の場合に `~/.zshrc` を読み直して API key を補完する。補完後も key が得られない場合は API key 未設定として fail-closed する。

`prepare_post_write_review.py` は `review-target.md` と `review-target.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、scope / out-of-scope、finding policy、機微情報チェック結果を含める。機微情報らしい文字列を検出した場合は fail-closed し、外部 API review へ進まない。

`next_action.target_files` が複数ある場合は、`prepare_post_write_review.py` と `run_review.py` の両方で `--target` を複数回指定して同じ review-run に束ねる。API review-run の成否確認は、`review-target.md`、`review-target.yaml`、`review_summary.md`、`rounds.yaml`、`model-result-summary.yaml`、`raw/`、`parsed/`、`prompts/`、`target-manifest.yaml` が同じ `--review-run-dir` に生成され、`rounds.yaml` の `target_files`、`criteria_source_path`、provider、model、prompt/raw/parsed path が今回の対象と一致することで行う。

API 呼び出しが失敗した場合は、まず上の正本手順を再確認する。`import` エラー、`argparse` エラー、引数不一致は起動手順または実装の問題であり、外部送信ポリシーや provider 側障害と混同しない。`ConnectError`、名前解決失敗、接続不能が出た場合は sandbox network 制限の可能性を先に疑い、同じ正本コマンドをネットワーク実行が許可された実行面で再実行する。API key 未設定のエラーは `~/.zshrc` から対象 provider の環境変数が読み込まれているかを確認する。

`post_write_verification` では API 経路の variant を明示する。小規模既定は `--variant post_write_verification_google`、大規模または 3 系統検証が必要な場合は `--variant <post-write-api-variant>` として、`config/api-settings.yaml` の `context: post_write_verification` かつ API provider だけで構成された variant を選ぶ。CLI 経路を含む default variant に暗黙フォールバックしてはいけない。

API レビュー結果を得た場合は、raw 参照、モデル別要約、三段階トリアージ（`must-fix`／`should-fix`／`leave-as-is`）を利用者へまとめて提示する。`ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を `decide` する場合、または重要件を含む run から manifest を生成する場合は、承認を記録した `--approval-record` が必須である。承認レコードには `approved_by: user` または `approved_by: proxy_model`、`review_run_id`、`summary_presented_to_user: true`、`triage_presented_to_user: true`、`approved_finding_ids`、必要に応じて `approved_final_labels` を含める。`approved_by: proxy_model` の場合は、`proxy_model_id` と finding ごとの `proxy_decisions` を含め、各 decision file が raw response、候補案、採用案、判断理由、最終ラベルを保持する。

`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。`triage.yaml` に `decision_status: human_required` が残る場合、または重要件の利用者承認が確認できない場合は manifest を生成しない。

<a id="lightweight_self_check"></a>

### `lightweight_self_check`

作業中メモ置き場の未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` を API post-write verification ではなく軽量自己精査で確認する。

軽量自己精査の対象は `docs/notes/working/` 配下と、単独変更の `TODO_NEXT_SESSION.md` とする。既存の `docs/notes/*.md` は正本寄りメモと作業中メモが混在しているため、従来どおり `post_write_verification` 対象とする。`docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`stages/completed/` は正本または完了記録として厳格に扱う。front matter や本文 marker による中身判定は初期実装では採用しない。判断に迷う配置は厳格側に倒す。

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

manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。

### `stage`

通常ワークフロー上の次タスクが決まっている。`feature`、`phase`、`stage` の示す作業だけを扱う。

`stage` が `triad-review` の場合、review-run の開始前に使用 variant と role ごとの path／provider／model を確定し、曖昧なまま開始しない。review-run に使うプロンプトは [[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）で設計する。API review-run 完了後は、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、raw 参照、モデル別要約、同根所見クラスタ、`must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案、重要件の平易な説明を利用者へ提示して停止する。詳細手順は `docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2` を正本とする。

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

### `upstream_recheck`

完了済み workflow であっても、上流成果物が下流成果物より新しいため、下流へ進む前に再確認が必要である。`upstream_phase`、`phase`、`stage` を確認し、`phase.stage` に示された作業を次作業として扱う。たとえば intent 更新後は feature-partitioning の確認、requirements 更新後は design の再確認、tasks 更新後は implementation の再確認を先に行う。

この kind が返った場合、記憶や直前の会話から requirements、design、tasks、implementation へ飛ばない。必ず `next_action.phase` と `next_action.stage` に従い、上流から下流へ順に反映する。

<a id="feature_definition_required"></a>

### `feature_definition_required`

feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない（verdict OK）。

`next_action.reason`（立ち上げ案内の本文）と `current_state.feature_dependency_source`（解決元）を確認する。`feature_dependency_source` が null ならファイル自体が探索順（`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml`）のどこにも存在せず、ファイルパスが入っていればそのファイルはあるが `feature_order` キーが未定義または不正である。前者は分割結果の記録から、後者は既存ファイルへの `feature_order` キーの追記から始める。

新しい作業を始めず、intent と feature-partitioning を実施し、承認された分割結果（機能ごとの依存の主張と理由、順序の導出を含む）を `.reviewcompass/feature-dependency.yaml` の `feature_order` キーに記録する。記録後に `next` を再実行する。feature 立ち上げの手順は `docs/operations/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。

なお、`feature_order` と `depends_on` の整合違反（依存される機能が先に並んでいない、循環依存がある）は本 kind ではなく `unknown`／DEVIATION（fail-closed）になる。理由に従って `feature-dependency.yaml` を修正する。

### `completed`

全 workflow_state が完了している。通常の次タスクはない。

利用者指示により maintenance、reopen、または新規 workflow を開始できる。maintenance を始める場合は `maintenance_in_progress` の事前調査と開始条件を確認する。

### `unknown`

状態判定できない。推測で進めず、`reasons` と `current_state` を利用者へ報告する。

## 3. 共通禁止事項

- `next` を実行せずに次作業を提案しない。
- `resume_in_progress`、`reopen_in_progress`、`post_write_verification`、`post_write_policy_violation`、`post_write_human_decision_required` を通常ワークフローより後回しにしない。
- `lightweight_self_check` を通常ワークフローより後回しにしない。
- `reopen_classification_required` を「再確認で足りる」と独断して下流成果物を更新しない。
- `next_action` と異なる side track に入る場合、または `next` 判定自体を修復する場合は、maintenance in-progress を作らずに編集を始めない。
- 事前調査を省略して maintenance を始めない。影響範囲・依存関係・ブロッカーの確認が済んでいない状態で in-progress YAML を作成しない。
- spec.json の workflow_state 変更、commit、push は不可逆操作として扱い、対応する precheck サブコマンドを実行する。
- 検証者は `target_files` 全体を見る。ファイルごとの分業を独立多重チェックとして扱わない。
- 本質的指摘を独断で逐語的指摘に落とさない。迷う場合は利用者へ上げる。


## docs/operations/DEPLOYMENT.md

# DEPLOYMENT：クリーン配布方針

最終更新：2026-06-10（初期デプロイを自己テスト用の全機能検証セットとして定義）

本文書は ReviewCompass を外部アプリへ配置する前に、開発リポジトリ内の成果物をどのように整理し、配布対象をどう扱うかを定める運用方針である。現時点では、配布対象を開発リポジトリから削って作るのではなく、配布対象を明示して切り出す方式を採用する。

## 1. 基本方針

ReviewCompass の開発リポジトリには、実行に必要なファイル、仕様正本、研究証跡、レビュー記録、実験結果、作業メモが混在している。この状態のまま外部アプリへ配置すると、不要な履歴や開発専用ファイルが対象アプリへ混入する。

そのため、デプロイ前整理の目的は、開発リポジトリを即座に削減することではなく、次の 2 つを分けることである。

- **開発リポジトリ**：研究証跡、レビュー履歴、実験結果、作業メモを保持する。
- **配布物**：外部アプリで ReviewCompass を実行するために必要な最小ファイルだけを含む。

## 2. 初期デプロイ配布物 v0 の定義

初期デプロイ配布物 v0 は、第3者配布用の最小セットではなく、利用者本人がテスターとして実アプリに適用し、ReviewCompass の全機能を確認するための検証用セットとする。開発リポジトリ内にあるファイルを暗黙に含めず、配布 manifest で明示した allowlist のみを配布対象にする。

初期デプロイ配布物 v0 に含めるものは次の通り。

### 2.1 プロジェクト定義

| 配布パス | 理由 |
| --- | --- |
| `pyproject.toml` | Python 依存関係と最小プロジェクト情報を示すため。 |

### 2.2 runtime コア

| 配布パス | 理由 |
| --- | --- |
| `runtime/config/config.yaml.template` | 対象アプリ側 `.reviewcompass/config.yaml` の雛形。 |
| `runtime/config/terminology.yaml.template` | 対象アプリ側の用語設定雛形。 |
| `runtime/config/reviewcompass.yaml` | ReviewCompass 本体側の既定設定。 |
| `runtime/foundation/layer1_framework.yaml` | ReviewCompass 共通の評価軸定義。 |
| `runtime/foundation/metadata_contract.yaml` | 実行記録の共通メタデータ契約。 |
| `runtime/prompts/primary_detection/primary_reviewer.prompt.md` | 主役レビューの既定プロンプト。 |
| `runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md` | 敵対役レビューの既定プロンプト。 |
| `runtime/prompts/judgment/judgment_reviewer.prompt.md` | 判定役レビューの既定プロンプト。 |
| `runtime/runtime_core/**/*.py` | review-run の実行、記録、検証、プロンプト解決に使う本体コード。 |
| `runtime/runtime_core/**/*.yaml` | runtime_core が参照する語彙、配置、スキーマ定義。 |
| `runtime/schemas/*.schema.json` | runtime の出力・観測記録の JSON Schema。 |
| `runtime/validators/contracts/*.schema.json` | validator 結果などの検証契約。 |

### 2.3 review-run API 実行部

| 配布パス | 理由 |
| --- | --- |
| `tools/api_providers/__init__.py` | Python package として読み込むため。 |
| `tools/api_providers/config_loader.py` | API 設定の読み込みに必要。 |
| `tools/api_providers/providers.py` | 各 provider 呼び出しに必要。 |
| `tools/api_providers/response_formatter.py` | レビュー応答の整形に必要。 |
| `tools/api_providers/review_triage.py` | review-run の所見整理に必要。 |
| `tools/api_providers/prepare_post_write_review.py` | post-write API review 前に review-target を生成するため。 |
| `tools/api_providers/run_review.py` | review-run の CLI 入口。 |
| `tools/api_providers/run_role.py` | 役単位の CLI 入口。 |
| `tools/api_providers/prompt_templates/*.md` | provider 別の API 呼び出しプロンプト。 |
| `config/api-settings.yaml` | 利用者本人の初期デプロイ検証で、既存の API / CLI 経路設定をそのまま確認するため。 |

`config/api-settings.yaml` は初期デプロイ検証では含める。ただし、同ファイルには API key、token、password などの秘密値を置かず、秘密値は実行環境の環境変数など配布物外で扱う。第3者配布では、経緯コメントや検証用 variant を除いた API 設定テンプレートを別途作成し、そのテンプレートへ差し替える。

### 2.4 conformance-evaluation

| 配布パス | 理由 |
| --- | --- |
| `tools/conformance-evaluation-check.py` | conformance-evaluation の CLI 入口。 |
| `tools/conformance-evaluation-cross-feature.py` | 機能横断 conformance-evaluation の CLI 入口。 |
| `tools/conformance_evaluation/*.py` | conformance-evaluation の本体コード。 |
| `tools/conformance_evaluation/schemas/*.schema.json` | evaluation record と intent diff の検証に必要。 |
| `schemas/review-criteria/conformance_evaluation.yaml` | conformance-evaluation の評価基準。 |

### 2.5 workflow-management

| 配布パス | 理由 |
| --- | --- |
| `tools/check-workflow-action.py` | workflow state と不可逆操作前検査の CLI 入口。 |
| `tools/document_link_lint.py` | 正本文書・規律文書の参照検査に必要。 |
| `tools/deployment_independence_lint.py` | 配置非依存性の検査に必要。 |
| `tools/guarded-git-commit.py` | commit 操作を workflow-management の検査に通すため。 |
| `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` | 判定点ごとの必読プロンプト対応を機械判定するため。 |
| `docs/operations/WORKFLOW_NAVIGATION.md` | workflow navigation の正本手順。 |
| `docs/operations/WORKFLOW_PRECHECK.md` | 事前検査の運用手順。 |
| `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` | 事前検査の詳細仕様。 |
| `docs/operations/REOPEN_PROCEDURE.md` | reopen 手続きの正本手順。 |
| `docs/operations/SESSION_WORKFLOW_GUIDE.md` | 作業完了時レポート契約と review-run 処理手順。 |
| `docs/disciplines/discipline_*.md` | workflow-management が判定時に読む規律文書。 |
| `.reviewcompass/specs/workflow-management/post-write-verification-spec.yaml` | 書き込み後検証の動作仕様。 |
| `.reviewcompass/specs/workflow-management/yaml-audit-spec.yaml` | YAML 監査の動作仕様。 |

`tools/check-workflow-action.py` には ReviewCompass 開発リポジトリ自身の feature order や carry-forward register 依存が残っている。そのため初期デプロイでは、汎用配布物としてではなく、利用者本人による実アプリ検証で依存箇所を発見する対象として含める。

### 2.6 self-improvement

| 配布パス | 理由 |
| --- | --- |
| `tools/self-improvement-check.py` | self-improvement の機械検査 CLI 入口。 |
| `tools/self_improvement/*.py` | 改善提案、carry-forward、承認済み更新の検査に必要。 |
| `tools/self_improvement/schemas/*.schema.json` | self-improvement 記録の検証に必要。 |
| `learning/workflow/schemas/*.schema.json` | self-improvement が読む workflow 改善用の正本 schema。 |
| `learning/workflow/proposals/README.md` | 改善提案の配置先を初期デプロイで確認するため。 |
| `learning/workflow/approved-updates/README.md` | 承認済み改善の配置先を初期デプロイで確認するため。 |
| `learning/workflow/rejected-updates/README.md` | 却下済み改善の配置先を初期デプロイで確認するため。 |
| `learning/workflow/rollback/README.md` | ロールバック記録の配置先を初期デプロイで確認するため。 |
| `learning/workflow/metrics/README.md` | 効果測定記録の配置先を初期デプロイで確認するため。 |
| `learning/workflow/carry-forward-register/README.md` | 持ち越し台帳の配置先を初期デプロイで確認するため。 |
| `learning/workflow/carry-forward-register/reviewcompass-import.yaml` | 現行の持ち越し台帳処理を検証するため。 |

### 2.7 analysis / evaluation

| 配布パス | 理由 |
| --- | --- |
| `analysis/` | ReviewCompass の分析機能を実アプリ上で確認するため。 |
| `evaluation/` | ReviewCompass の評価機能を実アプリ上で確認するため。 |

### 2.8 対象アプリ側生成テンプレート

| 配布パス | 理由 |
| --- | --- |
| `templates/specs/spec.json.template` | 対象アプリ側 `.reviewcompass/specs/<feature>/spec.json` の雛形。 |
| `templates/specs/feature-dependency.yaml.template` | 対象アプリ側 `.reviewcompass/feature-dependency.yaml`（feature 一覧・開発順・依存）の雛形。 |
| `templates/review/manual_dogfooding_review_template.md` | 初期デプロイで手動 review-run を記録するため。 |
| `templates/todo/TODO_NEXT_SESSION.template.md` | 初期デプロイ中のセッション引き継ぎを確認するため。 |
| `templates/entry/AGENT_ENTRY.template.md` | 対象アプリ側 `.reviewcompass/AGENT_ENTRY.md`（複数 LLM 共通のセッション入口規律）の雛形。 |
| `templates/hooks/pre-bash-precheck.sh.template` | 対象アプリ側 commit／push 事前検査 hook の雛形（初期設定時に絶対パスへ置換）。 |
| `templates/hooks/claude-settings.json.template` | 対象アプリ側 `.claude/settings.json` への hook 登録の雛形。 |
| `templates/hooks/codex-hooks.json.template` | 対象アプリ側 `.codex/hooks.json` の雛形。 |

## 3. 初期デプロイ配布物 v0 に含めないもの

次のファイル群は、初期デプロイ配布物 v0 に含めない。

- `AGENTS.md`
- `.codex/`
- `.claude/`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`・`WORKFLOW_NAVIGATION_FOR_CODEX.md`（開発リポジトリ専用の手引き。対象アプリ側の入口は `templates/entry/` から実体化する AGENT_ENTRY が担うため、意図的に配布しない）
- `.reviewcompass/post-write-verification/`
- `.reviewcompass/effective-prompts/`
- `.reviewcompass/approvals/`
- `.reviewcompass/specs/*/reviews/`
- `.reviewcompass/specs/*/conformance/`
- `.reviewcompass/specs/_cross_feature/`
- `docs/notes/`
- `docs/archive/`
- `docs/plan/`
- `docs/sessions/`
- `docs/reviews/`
- `docs/experiments/`
- `docs/logs/`
- `docs/discipline-compliance-reports/`
- `tools/experiments/`
- `tools/**/tests/`
- `tests/`
- `learning/workflow/carry-forward-register/sources/`
- `learning/workflow/deployment-readiness/`
- `learning/workflow/replication-pilots/`
- `logs/`
- `SES26/`

`.reviewcompass/specs/` は、初期デプロイ配布物には workflow-management の動作仕様 YAML だけを含める。ReviewCompass 自身の要件、設計、タスク、レビュー記録、conformance 証跡は、対象アプリ側へ持ち込まない。

`learning/workflow/` は、初期デプロイ配布物には self-improvement の実行に必要な配置先 README、schema、現行 carry-forward register だけを含める。deployment-readiness、replication-pilots、carry-forward register の source 文書は開発証跡として除外する。

これらは不要物として直ちに削除するのではなく、研究証跡または開発履歴として開発リポジトリに保持する。削除、別リポジトリ分離、アーカイブ移動は、配布 manifest と配布物生成が安定した後に判断する。

## 4. 第3者配布で再検討するもの

初期デプロイ配布物 v0 は利用者本人の検証用であり、第3者配布用の最終形ではない。第3者配布時には、次の配布単位を再検討する。

| 配布単位 | 候補 | 条件 |
| --- | --- | --- |
| workflow-management 汎用実行部 | `check-workflow-action.py` 相当、`WORKFLOW_DISCIPLINE_MAP.yaml` 相当、規律文書 | 初期デプロイで発見した ReviewCompass 開発リポジトリ固有依存を外す。 |
| LLM 別 adapter 一式 | 入口正本テンプレート（`templates/entry/`）、hook テンプレート（`templates/hooks/`）、操縦 LLM 別の API 既定 variant（`config/api-settings.yaml` の `*_codex_operator` 系等） | 初期デプロイ版は Claude Code と Codex CLI に対応済み（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`）。第3者配布では、操縦 LLM の追加（例：Gemini 操縦時の variant）、LLM 別注意のファイル分離、開発リポジトリ用手引き（`WORKFLOW_NAVIGATION_FOR_CLAUDE.md`／`FOR_CODEX.md`）の扱いを再検討する。 |
| 開発者向け検査 | `tools/document_link_lint.py`、`tools/deployment_independence_lint.py` | 配布物生成側の CI または開発者向け pack として追加する。 |
| 第3者配布用 API 設定テンプレート | `config/api-settings.yaml` から経緯コメントや検証用 variant を除いたテンプレート | 初期デプロイ検証では現行 `config/api-settings.yaml` を使い、第3者配布時に差し替える。 |
| 第3者向け最小コア | runtime、review-run、conformance-evaluation の最小セット | 全機能検証後、不要機能を除いて再定義する。 |

## 5. 配布物生成

外部アプリ pilot や本格デプロイでは、開発リポジトリをそのまま使わない。manifest で許可されたファイルだけを、一時的な配布ディレクトリにコピーして使う。

想定する流れは次の通り。

1. `deploy-manifest.yaml` を読む。
2. `tools/build-deploy-package.py --clean --verify` で、許可されたファイルだけを `build/deploy/ReviewCompass/` などへコピーする。
3. `--verify` で、allowlist 外ファイル、exclude 対象ファイル、欠落ファイルがないことを機械検査する。
4. `--smoke-external-app-root <外部アプリroot>` で、配布物だけを使って外部アプリ root の `.reviewcompass/specs/<feature>/reviews/` へ review-run 成果物を書けることを確認する。
5. 実アプリ pilot は、この生成済み配布物を使って実施する。

配布物生成時に、開発リポジトリ側の workflow state や仕様状態を変更してはならない。

## 6. 外部アプリ側の扱い

外部アプリの git リポジトリには、アプリ側状態だけを置く。

外部アプリ側に生成または更新される候補は次の通り。

- `<対象アプリ>/.reviewcompass/config.yaml`
- `<対象アプリ>/.reviewcompass/AGENT_ENTRY.md`（複数 LLM 共通の入口規律。テンプレートから実体化）
- `<対象アプリ>/.reviewcompass/feature-dependency.yaml`（feature 一覧・開発順・依存）
- `<対象アプリ>/.reviewcompass/specs/<feature>/requirements.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/design.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/tasks.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/spec.json`
- `<対象アプリ>/.reviewcompass/specs/<feature>/reviews/`
- `<対象アプリ>/CLAUDE.md`・`AGENTS.md`（入口への参照 1 行の追記）
- `<対象アプリ>/.claude/settings.json`・`.claude/hooks/`（commit／push 事前検査 hook）
- `<対象アプリ>/.codex/hooks.json`・`.codex/hooks/`（同上）

これらは対象アプリの仕様、状態、レビュー記録であり、対象アプリ側 git リポジトリの変更として扱う。ReviewCompass 側の開発証跡、実験ログ、過去 review-run 記録は対象アプリ側へ持ち込まない。

## 7. 第3者への配布

第3者へ ReviewCompass を配布するときは、対象アプリごとに GitHub 上で ReviewCompass リポジトリを fork させる方式を標準にしない。標準は、ReviewCompass 開発リポジトリから生成したクリーン配布物を渡す方式とする。

配布形式は、初期段階では zip / tarball / GitHub Release asset のいずれかを想定する。将来、運用が安定した段階で PyPI package や専用 installer に移行してよい。

第3者側の導入手順は次の形を基本とする。

1. ReviewCompass の配布物を取得する。
2. 配布物を展開する、または package として install する。
3. 対象アプリの git リポジトリで ReviewCompass を実行する。
4. 対象アプリ側に `.reviewcompass/config.yaml` と `.reviewcompass/specs/` を生成または更新する。
5. 対象アプリ側の判断で `.reviewcompass/` 配下の変更を commit / push する。

ReviewCompass 本体を改変したい場合は、第3者の対象アプリ repo 内で個別 fork を増やすのではなく、ReviewCompass 開発リポジトリに対する issue / pull request / patch 提案として扱う。

## 8. 2 つの git リポジトリの責務

デプロイ時は、ReviewCompass 側リポジトリと対象アプリ側リポジトリを分けて扱う。

| リポジトリ | 主な責務 | 変更されるもの |
| --- | --- | --- |
| ReviewCompass 側 | ツール本体、既定設定、スキーマ、テンプレート、プロンプト、配布物生成 | 配布 manifest、ツール実装、正本資産 |
| 対象アプリ側 | アプリ固有の仕様、状態、レビュー記録、上書き設定 | `.reviewcompass/config.yaml`、`.reviewcompass/specs/` |

対象アプリで ReviewCompass を実行しても、ReviewCompass 側リポジトリの workflow state を暗黙に変更しない。対象アプリ側に生成された `.reviewcompass/` 配下の変更を commit / push するかは、対象アプリ側の運用判断として扱う。

## 9. 機械チェック

配布物には、次の機械チェックを設ける。

- allowlist 外のファイルが配布物に含まれていないこと。
- `docs/notes/`、`tools/experiments/`、`.reviewcompass/post-write-verification/` などの非配布対象が混入していないこと。
- 絶対パス、固定ユーザパス、開発リポジトリ固有パスが配布対象に混入していないこと。
- 配布物だけで最小 smoke test が通ること。
- 外部アプリ root の `.reviewcompass/specs/` を読み書きできること。

`tools/deployment_independence_lint.py` は、絶対パスや配置非依存性の検査に使う。`tools/build-deploy-package.py --verify` は、配布 manifest と組み合わせて、配布物そのものの混入検査を行う。

## 10. 当面の次作業

1. 実アプリ pilot で使う外部アプリ root を決める。
2. `config/api-settings.yaml` に秘密値が含まれていないことを確認する。
3. `tools/build-deploy-package.py --clean --verify --smoke-external-app-root <外部アプリroot>` を実アプリ用の一時 root で実行する。
4. 実アプリ pilot では、開発リポジトリではなく生成済み配布物を使う。
5. pilot で見つかった ReviewCompass 開発リポジトリ固有依存を、第3者配布前の修正候補として記録する。

この順序により、開発リポジトリの研究証跡を失わずに、外部アプリへ渡す ReviewCompass を小さく、説明可能で、検査可能な状態にする。


## deploy-manifest.yaml

name: reviewcompass-initial-self-test
version: 1
distribution_type: initial_self_test
description: >
  Initial deployment package for the ReviewCompass owner to test all features
  against a real external application. This is not the third-party minimal
  distribution.
source_policy:
  mode: allowlist
  root: repository
output:
  default_directory: build/deploy/ReviewCompass
include:
  - path: pyproject.toml
    reason: Python dependency and project metadata.

  - path: config/api-settings.yaml
    reason: Existing API / CLI route configuration for owner-operated initial tests.

  - path: runtime/config/README.md
    reason: Runtime configuration directory explanation.
  - path: runtime/config/config.yaml.template
    reason: Target app .reviewcompass/config.yaml template.
  - path: runtime/config/terminology.yaml.template
    reason: Target app terminology configuration template.
  - path: runtime/config/reviewcompass.yaml
    reason: ReviewCompass default runtime configuration.
  - path: runtime/foundation/README.md
    reason: Foundation runtime assets explanation.
  - path: runtime/foundation/layer1_framework.yaml
    reason: Common review stage and role framework.
  - path: runtime/foundation/metadata_contract.yaml
    reason: Shared execution metadata contract.
  - path: runtime/prompts/README.md
    reason: Prompt asset layout explanation.
  - path: runtime/prompts/primary_detection/primary_reviewer.prompt.md
    reason: Default primary reviewer prompt.
  - path: runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md
    reason: Default adversarial reviewer prompt.
  - path: runtime/prompts/judgment/judgment_reviewer.prompt.md
    reason: Default judgment reviewer prompt.
  - path: runtime/runtime_core/**/*.py
    reason: Runtime execution, evidence writing, validation, and prompt resolution code.
  - path: runtime/runtime_core/**/*.yaml
    reason: Runtime vocabularies, layout, projection, and schema assets.
  - path: runtime/runtime_core/run_layout/README.md
    reason: Runtime run layout explanation.
  - path: runtime/schemas/README.md
    reason: Runtime schema directory explanation.
  - path: runtime/schemas/*.schema.json
    reason: Runtime output and evidence JSON schemas.
  - path: runtime/validators/contracts/README.md
    reason: Validator contract directory explanation.
  - path: runtime/validators/contracts/*.schema.json
    reason: Validator result and invalidation marker contracts.

  - path: tools/README.md
    reason: Tool namespace and CLI naming explanation.
  - path: tools/api_providers/__init__.py
    reason: API provider package marker.
  - path: tools/api_providers/config_loader.py
    reason: API provider configuration loading.
  - path: tools/api_providers/providers.py
    reason: Provider invocation implementation.
  - path: tools/api_providers/response_formatter.py
    reason: Review response formatting.
  - path: tools/api_providers/review_triage.py
    reason: Review-run finding triage.
  - path: tools/api_providers/prepare_post_write_review.py
    reason: Post-write review-target preparation before API review.
  - path: tools/api_providers/run_review.py
    reason: Review-run CLI entry point.
  - path: tools/api_providers/run_role.py
    reason: Role-level review CLI entry point.
  - path: tools/api_providers/prompt_templates/*.md
    reason: Provider-specific API prompt templates.
  - path: tools/session-record-backfill.py
    reason: Session record single-capture CLI used by deployed Codex session capture hook.
  - path: tools/session-record-extractor.py
    reason: Session record extraction CLI used by session backfill.
  - path: tools/session_record_extractor/*.py
    reason: Session record extraction library used by session backfill.

  - path: tools/foundation_validators/*.py
    reason: Foundation validation helpers for all-feature self-test.
  - path: tools/conformance-evaluation-check.py
    reason: Conformance-evaluation CLI entry point.
  - path: tools/conformance-evaluation-cross-feature.py
    reason: Cross-feature conformance-evaluation CLI entry point.
  - path: tools/conformance_evaluation/*.py
    reason: Conformance-evaluation implementation package.
  - path: tools/conformance_evaluation/schemas/*.schema.json
    reason: Conformance-evaluation record and intent diff schemas.
  - path: schemas/review-criteria/conformance_evaluation.yaml
    reason: Conformance-evaluation review criteria.

  - path: tools/check-workflow-action.py
    reason: Workflow state and irreversible-action guard CLI.
  - path: tools/check_workflow_action/**
    reason: Runtime placement constants, read resolvers, and freeze checker imported by the guard CLI.
  - path: tools/document_link_lint.py
    reason: Document link and prompt-source reference lint.
  - path: tools/deployment_independence_lint.py
    reason: Deployment independence lint.
  - path: tools/guarded-git-commit.py
    reason: Commit wrapper that enforces workflow-management checks.
  - path: docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
    reason: Machine-readable decision-point to prompt-source map.
  - path: docs/operations/WORKFLOW_NAVIGATION.md
    reason: Workflow navigation contract.
  - path: docs/operations/WORKFLOW_PRECHECK.md
    reason: Precheck operational contract.
  - path: docs/operations/WORKFLOW_PRECHECK_DETAILS.md
    reason: Detailed precheck specification.
  - path: docs/operations/REOPEN_PROCEDURE.md
    reason: Reopen procedure.
  - path: docs/operations/SESSION_WORKFLOW_GUIDE.md
    reason: Session completion and review-run handling guide.
  - path: docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md
    reason: Initial owner-operated deployment guide.
  - path: docs/operations/INITIAL_SETUP_LLM_GUIDE.md
    reason: LLM-facing initial setup guide.
  - path: docs/disciplines/discipline_*.md
    reason: Workflow-management discipline prompts.
  - path: .reviewcompass/specs/workflow-management/post-write-verification-spec.yaml
    reason: Post-write verification behavior contract.
  - path: .reviewcompass/specs/workflow-management/yaml-audit-spec.yaml
    reason: YAML audit behavior contract.

  - path: tools/self-improvement-check.py
    reason: Self-improvement machine verification CLI.
  - path: tools/self_improvement/*.py
    reason: Self-improvement implementation package.
  - path: tools/self_improvement/schemas/*.schema.json
    reason: Self-improvement intermediate schemas.
  - path: learning/workflow/schemas/*.schema.json
    reason: Canonical workflow learning schemas.
  - path: learning/workflow/proposals/README.md
    reason: Proposal output location explanation.
  - path: learning/workflow/approved-updates/README.md
    reason: Approved update location explanation.
  - path: learning/workflow/rejected-updates/README.md
    reason: Rejected update location explanation.
  - path: learning/workflow/rollback/README.md
    reason: Rollback record location explanation.
  - path: learning/workflow/metrics/README.md
    reason: Metrics record location explanation.
  - path: learning/workflow/carry-forward-register/README.md
    reason: Carry-forward register location explanation.
  - path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
    reason: Current carry-forward register used by workflow checks.

  - path: analysis/**
    reason: Analysis feature package for full initial self-test.
  - path: evaluation/**
    reason: Evaluation feature package for full initial self-test.

  - path: templates/specs/spec.json.template
    reason: Target app spec.json template.
  - path: templates/specs/feature-dependency.yaml.template
    reason: Target app feature order and dependency definition template.
  - path: templates/review/manual_dogfooding_review_template.md
    reason: Manual review-run record template for initial tests.
  - path: templates/todo/TODO_NEXT_SESSION.template.md
    reason: Session handoff template for initial tests.
  - path: templates/entry/AGENT_ENTRY.template.md
    reason: Target app multi-LLM agent entry discipline template.
  - path: templates/hooks/pre-bash-precheck.sh.template
    reason: Target app commit/push precheck hook template (placeholder substitution at setup).
  - path: templates/hooks/session-record-capture-current-on-todo.sh.template
    reason: Target app Codex previous-session capture hook template (placeholder substitution at setup).
  - path: templates/hooks/claude-settings.json.template
    reason: Claude Code hook registration template for target apps.
  - path: templates/hooks/codex-hooks.json.template
    reason: Codex CLI hook registration template for target apps.
exclude:
  - path: AGENTS.md
    reason: Local agent instructions, not a deployable runtime asset.
  - path: .codex/**
    reason: Local Codex configuration.
  - path: .claude/**
    reason: Local Claude configuration.
  - path: .reviewcompass/post-write-verification/**
    reason: Development post-write verification evidence.
  - path: .reviewcompass/effective-prompts/**
    reason: Generated effective prompts.
  - path: .reviewcompass/approvals/**
    reason: Local approval records.
  - path: .reviewcompass/specs/*/reviews/**
    reason: ReviewCompass development review evidence.
  - path: .reviewcompass/specs/*/conformance/**
    reason: ReviewCompass development conformance evidence.
  - path: .reviewcompass/evidence/**
    reason: ReviewCompass development evidence compartment (review runs, conformance records, estimation logs).
  - path: .reviewcompass/runtime/**
    reason: Runtime artifacts compartment (precheck log, effective prompts, commit approval record).
  - path: .reviewcompass/specs/_cross_feature/**
    reason: ReviewCompass internal cross-feature evidence.
  - path: docs/notes/**
    reason: Development notes and evidence.
  - path: docs/archive/**
    reason: Archived development material.
  - path: docs/plan/**
    reason: Historical planning material.
  - path: docs/sessions/**
    reason: Session records.
  - path: docs/reviews/**
    reason: Development review records.
  - path: docs/experiments/**
    reason: Experiment records.
  - path: docs/logs/**
    reason: Development logs.
  - path: docs/discipline-compliance-reports/**
    reason: Internal compliance evidence.
  - path: tools/experiments/**
    reason: Experiment tooling and outputs.
  - path: tools/**/tests/**
    reason: Tool test suites are not part of the deployed runtime.
  - path: tests/**
    reason: Repository test suites are not part of the deployed runtime.
  - path: learning/workflow/carry-forward-register/sources/**
    reason: Historical Markdown import sources.
  - path: learning/workflow/deployment-readiness/**
    reason: Development deployment-readiness evidence.
  - path: learning/workflow/replication-pilots/**
    reason: Replication pilot evidence.
  - path: logs/**
    reason: Local logs.
  - path: SES26/**
    reason: Local session material.
checks:
  - name: allowlist_only
    description: Generated package must contain only include entries after excludes.
  - name: no_development_evidence
    description: Generated package must not contain excluded evidence directories.
  - name: deployment_independence_lint
    description: Distributed Markdown / YAML / JSON assets must avoid local absolute paths.
  - name: smoke_test_external_app_root
    description: Package must run against an external application root and read/write target .reviewcompass state.


## stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml

process_id: maintenance
title: post-write review-target preflight
trigger: "post-write validation の API 検査で短い criteria ID だけが渡され、検査観点の明示証跡が薄かったため、API 検査前の review-target 生成を機械化する"
mainline_blocked_by: stages/in-progress/reopen-procedure-2026-06-19.yaml
completed_at: "2026-06-19"
classification: local_workflow_guard_improvement
reason: "post-write API review の入力生成と証跡保存を改善する局所変更。workflow phase/gate の意味や reopen 本線の成果物内容は変更しない"
allowed_scope:
  - "post-write API review 前の review-target 生成"
  - "criteria-file 経由の API review 実行"
  - "rendered prompt の review-run 証跡保存"
  - "配布 manifest と運用文書の追従"
allowed_files:
  - tools/api_providers/prepare_post_write_review.py
  - tools/api_providers/run_review.py
  - tools/api_providers/run_role.py
  - tools/api_providers/tests/test_prepare_post_write_review.py
  - tools/api_providers/tests/test_run_review.py
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/DEPLOYMENT.md
  - deploy-manifest.yaml
  - tests/operations/test_session_workflow_guide.py
  - tests/deployment/test_deploy_manifest.py
  - stages/in-progress/reopen-procedure-2026-06-19.yaml
  - stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml
completion_conditions:
  - "post-write API review 前に review-target.md / review-target.yaml を機械生成できる"
  - "run_review.py / run_role.py が --criteria-file を受け取り、criteria 出典 path / sha256 を rounds.yaml に記録する"
  - "API へ送る rendered prompt を review-run の prompts/ 配下に保存し、model_result に path / sha256 を記録する"
  - "機微情報らしい token を含む target は review-target 生成時点で fail-closed する"
completed_actions:
  - "tests: prepare_post_write_review の review-target 生成と secret-like target fail-closed を追加"
  - "tests: run_review が --criteria-file を使い rendered prompt を保存する期待を追加"
  - "implementation: prepare_post_write_review.py を追加"
  - "implementation: run_review.py / run_role.py に --criteria-file と criteria 出典記録を追加"
  - "implementation: review-run の prompts/ 配下に rendered prompt を保存"
  - "documentation: WORKFLOW_NAVIGATION の post_write_verification 標準手順を prepare → run_review --criteria-file に更新"
  - "deployment: deploy-manifest.yaml と DEPLOYMENT.md に新 CLI を追加"
verification:
  - command: ".venv/bin/python3 -m pytest tools/api_providers/tests/test_run_review.py::test_run_review_uses_criteria_file_and_records_prompt_artifact -q"
    result: "passed"
  - command: ".venv/bin/python3 -m pytest tools/api_providers/tests/test_prepare_post_write_review.py -q"
    result: "2 passed"
  - command: ".venv/bin/python3 -m pytest tools/api_providers/tests/test_run_review.py tools/api_providers/tests/test_run_role.py tools/api_providers/tests/test_prepare_post_write_review.py -q"
    result: "29 passed"
  - command: ".venv/bin/python3 -m pytest tests/operations/test_session_workflow_guide.py tests/deployment/test_deploy_manifest.py -q"
    result: "13 passed"
  - command: "PYTHONPYCACHEPREFIX=/private/tmp/reviewcompass-pycache .venv/bin/python3 -m py_compile tools/api_providers/run_review.py tools/api_providers/run_role.py tools/api_providers/prepare_post_write_review.py"
    result: "passed"
  - command: "git diff --check"
    result: "passed"
  - command: ".venv/bin/python3 tools/api_providers/prepare_post_write_review.py --target docs/operations/WORKFLOW_NAVIGATION.md --target docs/operations/DEPLOYMENT.md --target deploy-manifest.yaml --target stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml --review-run-dir .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite --criteria-id post_write_review_target_preflight_contract_clearance --change-summary \"post-write API review 前に review-target を機械生成し、run_review は criteria-file と rendered prompt 証跡を保存するようにした。標準手順と配布 manifest も追従した。\" --review-question \"post-write API review の標準手順が、短い criteria ID だけに依存せず、review-target 生成、criteria-file 利用、rendered prompt 保存、機微情報チェックを一貫して要求しているか。\""
    result: "passed"
  - command: ".venv/bin/python3 tools/api_providers/run_review.py --variant post_write_verification_google --target docs/operations/WORKFLOW_NAVIGATION.md --target docs/operations/DEPLOYMENT.md --target deploy-manifest.yaml --target stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml --phase post_write_verification --criteria-file .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite/review-target.md --review-run-dir .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite"
    result: "passed: no findings"
  - command: ".venv/bin/python3 tools/api_providers/review_triage.py list-pending --review-run-dir .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite"
    result: "no pending findings"
post_write_verification:
  manifest: .reviewcompass/post-write-verification/post-write-2026-06-19-268.yaml
  review_run: .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite
current_status: completed
return_to: "integrated-design reopen design drafting"

