prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: maintenance_commit_clearance_unification_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T00:58:55.951033+00:00

## Change Summary

maintenance 完了 commit の判定を commit-preflight と commit 本体で共通化し、本線 reopen in-progress YAML の同伴 stage を不要にした。

## Review Question

maintenance 完了 commit の標準手順と完了記録が、本線 reopen state を人工的に変更せず、mainline_blocked_by による coverage で commit を許可する contract と矛盾していないか。

## Target Files

- docs/operations/WORKFLOW_NAVIGATION.md sha256=840dfe2e7f30ff3d18492d6713ee969d9e75341ad7aad086d479266813e76a85
- docs/operations/WORKFLOW_PRECHECK_DETAILS.md sha256=d5279e60525ecc9f7d5ed03d6bd62df17892ff4812b0be85d27b3f9ae207c9f4
- stages/completed/maintenance-2026-06-19-maintenance-commit-clearance-unification.yaml sha256=9e88f4070814f4ae0cf956f2d590cb23b691adbdfe4412d445f7e96fbc71cfc1

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
docs/operations/WORKFLOW_PRECHECK_DETAILS.md
stages/completed/maintenance-2026-06-19-maintenance-commit-clearance-unification.yaml

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


## docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# WORKFLOW_PRECHECK 詳細仕様

本文書は `tools/check-workflow-action.py` と `tools/guarded-git-commit.py` の詳細仕様を定める。運用時に読む短い契約は [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md) を正とし、本書は実装・保守・テストで必要な詳細を補う。

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

`tools/guarded-git-commit.py` は `commit --execution-actor llm` を先に実行し、exit 2 なら commit しない。exit 1 は既定では停止し、人の判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、期限付き承認レコードは消費済みにする。

通常 workflow の `intent.approval` / `feature-partitioning.approval` 完了後の停止点は、`next --json` が `kind: commit_stop_point` として検出する。これらは `stages/in-progress/` を使わない通常 commit であるため、commit guard 側では特別な in-progress 例外を要求せず、通常どおり承認レコード、staged 範囲、post-write-verification、文書 lint を検査する。

nonce challenge を使う commit 手順は、次の順序で逐次実行する。

1. `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行し、`OK` を確認する。
2. `git add ...` で対象を stage する。
3. `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を単独で実行する。
4. 返された `nonce` を使い、`.venv/bin/python3 tools/guarded-git-commit.py ... --approval-nonce <nonce> --approval-source-text-line-stdin` を stdin 入力可能な実行形で起動する。
5. guarded commit が承認入力待ちになってから、承認 1 行（例：`コミット\n`）を渡す。

`commit-approval prepare` と `commit --json` precheck を並列化しない。`prepare` 後の challenge は staged exact index と承認状態に束縛されるため、guarded commit 以外の承認系コマンドを挟まない。`--approval-source-text-line-stdin` を指定して空 stdin で実行すると challenge が invalidated になり得るため、非対話・空入力の実行形では使わない。

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


## stages/completed/maintenance-2026-06-19-maintenance-commit-clearance-unification.yaml

process_id: maintenance
title: maintenance commit clearance unification
trigger: "commit-preflight は maintenance 完了 commit を許可したが、guarded commit 本体が本線 in-progress YAML の同伴 stage を要求し、承認 digest 作り直しが発生した"
mainline_blocked_by: stages/in-progress/reopen-procedure-2026-06-19.yaml
completed_at: "2026-06-19"
classification: local_workflow_guard_improvement
reason: "commit-preflight と commit 本体の maintenance 完了判定を共通化し、本線 state を人工的に変更しない commit 経路へ戻す局所修正"
allowed_scope:
  - "maintenance 完了 commit の clearance 判定共通化"
  - "maintenance 完了 commit で本線 in-progress YAML の同伴 stage を不要にする"
  - "commit-preflight / commit の回帰テスト"
  - "運用文書の staging contract 更新"
allowed_files:
  - tools/check-workflow-action.py
  - tests/tools/test_check_workflow_action.py
  - docs/operations/WORKFLOW_PRECHECK_DETAILS.md
  - docs/operations/WORKFLOW_NAVIGATION.md
  - .reviewcompass/evidence/review-runs/2026-06-19-maintenance-commit-clearance-unification-postwrite/
  - .reviewcompass/post-write-verification/post-write-2026-06-19-269.yaml
  - stages/completed/maintenance-2026-06-19-maintenance-commit-clearance-unification.yaml
completion_conditions:
  - "commit 本体が maintenance 完了 YAML だけの staged set を許可する"
  - "commit-preflight が同じ maintenance 完了条件で stage / approval 作成を許可する"
  - "判定 helper が stage 前 / stage 後で同じ coverage 条件を使う"
completed_actions:
  - "tests: maintenance 完了 commit が本線 reopen state を同伴 stage しなくても通る期待へ更新"
  - "tests: commit-preflight が本線 reopen state を変えない maintenance 完了 commit 候補を許可する期待を追加"
  - "implementation: _completed_maintenance_files_cover_in_progress を追加し、stage 前 / stage 後の判定を共通化"
  - "implementation: is_completed_maintenance_commit_allowed から本線 in-progress staged 必須条件を削除"
  - "documentation: WORKFLOW_PRECHECK_DETAILS / WORKFLOW_NAVIGATION に本線 in-progress を同伴 stage しない contract を追記"
verification:
  - command: ".venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_allows_completed_maintenance_without_staging_mainline_reopen_state -v"
    result: "passed"
  - command: ".venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests.test_commit_preflight_allows_completed_maintenance_without_reopen_state_change -v"
    result: "passed"
  - command: ".venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.CommitExitCodeTests -v"
    result: "75 tests passed"
  - command: ".venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests -v"
    result: "45 tests passed"
  - command: "PYTHONPYCACHEPREFIX=/private/tmp/reviewcompass-pycache .venv/bin/python3 -m py_compile tools/check-workflow-action.py"
    result: "passed"
  - command: "git diff --check"
    result: "passed"
  - command: ".venv/bin/python3 tools/api_providers/run_review.py --variant post_write_verification_google --target docs/operations/WORKFLOW_NAVIGATION.md --target docs/operations/WORKFLOW_PRECHECK_DETAILS.md --target stages/completed/maintenance-2026-06-19-maintenance-commit-clearance-unification.yaml --phase post_write_verification --criteria-file .reviewcompass/evidence/review-runs/2026-06-19-maintenance-commit-clearance-unification-postwrite/review-target.md --review-run-dir .reviewcompass/evidence/review-runs/2026-06-19-maintenance-commit-clearance-unification-postwrite"
    result: "passed: no findings"
post_write_verification:
  manifest: .reviewcompass/post-write-verification/post-write-2026-06-19-269.yaml
  review_run: .reviewcompass/evidence/review-runs/2026-06-19-maintenance-commit-clearance-unification-postwrite
current_status: completed
return_to: "integrated-design reopen design drafting"

