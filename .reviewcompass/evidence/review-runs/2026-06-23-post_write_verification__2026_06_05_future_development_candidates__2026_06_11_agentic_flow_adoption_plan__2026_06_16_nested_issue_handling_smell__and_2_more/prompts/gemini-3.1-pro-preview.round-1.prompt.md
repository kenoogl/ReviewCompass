prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: post_write_verification__2026_06_05_future_development_candidates__2026_06_11_agentic_flow_adoption_plan__2026_06_16_nested_issue_handling_smell__and_2_more
phase: post_write_verification
generated_at: 2026-06-23T01:18:32.722370+00:00

## Change Summary

post-write verification target files changed: docs/notes/2026-06-05-future-development-candidates.md, docs/notes/2026-06-11-agentic-flow-adoption-plan.md, docs/notes/2026-06-16-nested-issue-handling-smell.md, docs/notes/2026-06-16-operation-registry-preflight-design.md, docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md

## Review Question

Verify that the listed post-write target files are consistent with the source materials, keep target/source/out-of-scope separation clear, and do not weaken prompt-manifest preflight, finding policy, or post-write verification stop conditions.

## Target Files

- /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-05-future-development-candidates.md sha256=76ff6b6f9e2ac06cf54f0e89b4c9bb5db6a7576e559c165cb73628667e66ac89
- /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-11-agentic-flow-adoption-plan.md sha256=a9993076c9aba10060ce27f7d882066766b4f386e8809c135cbbf3b2ab219cdb
- /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-16-nested-issue-handling-smell.md sha256=d3a1460de7638d24cbdcc34981761f5f7e63d7f1f5a25fa77f4e9404be2c7ea5
- /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-16-operation-registry-preflight-design.md sha256=31600062b2b185d898df35a823f676f7a55f5dcd18d48240dd6e5d3a5830577b
- /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md sha256=03b5901cac6916ed3a0781dec316b18b9dd31a1f80fe1f1bf13816d1714ec761

## Source Materials

### /Users/Daily/Development/ReviewCompass/.reviewcompass/guidance/WORKFLOW_NAVIGATION.md

content_mode: full_text
content_sha256: 864340be0009cdee9f549516864a003527c608bba2492f2effe3045f731ff14f

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
content_sha256: 03a9b994c6b5fb4b99ebbbf169e48d76568c5b6190716bbe9e5e181844c9450d

```text
# API Review Prompt Quality

最終更新：2026-06-20

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

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む

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

### /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-05-future-development-candidates.md

content_mode: full_text
content_sha256: 76ff6b6f9e2ac06cf54f0e89b4c9bb5db6a7576e559c165cb73628667e66ac89

```text
# 今後開発検討すべき項目リスト

作成日：2026-06-05

この候補台帳の未実装候補は backlog plan へ移設済み。実装済み候補と移設済み候補の
詳細本文は、この旧台帳には残さない。

## 移設済み候補

- D-001 / D-002 / D-003:
  `.reviewcompass/backlog/plans/plan-2026-06-23-review-wave-recheck-pointer-hardening.yaml`
- D-007:
  `.reviewcompass/backlog/plans/plan-2026-06-23-autonomous-ledger-auditability.yaml`
- D-009:
  `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-convergence-policy.yaml`
- D-010:
  `.reviewcompass/backlog/plans/plan-2026-06-23-agent-adapter-revision.yaml`
- D-011:
  `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-assignment-tuning.yaml`
- D-012 / D-013 / D-014:
  `.reviewcompass/backlog/plans/plan-2026-06-23-triage-explanation-guard-quality.yaml`
- D-015 / D-016 / D-017:
  `.reviewcompass/backlog/plans/plan-2026-06-23-feature-quality-followups.yaml`
- D-018:
  `.reviewcompass/backlog/plans/plan-2026-06-23-false-positive-reversal-metrics.yaml`
- D-022 / D-024:
  `.reviewcompass/backlog/plans/plan-2026-06-23-reconstruction-cleanup-followups.yaml`

## 既存 backlog plan へ整理済みの候補

- D-006:
  `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-decision-mechanization.yaml`
- D-026:
  `.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml`

## 実装済みとして旧台帳から削除した候補

- D-004 normalized finding schema
- D-005 finding-to-fix traceability
- D-008 dogfooding event ledger
- D-019 time / cost / model assignment
- D-020 cross-repository replication
- D-021 deployable reconstruction readiness
- D-023 deployment independence lint
- D-025 TDD cycle evidence
- D-027 side track state model

今後の作業候補、残作業、完了条件は `.reviewcompass/backlog/index.yaml` と各 backlog plan
を正として確認する。
```

### /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-11-agentic-flow-adoption-plan.md

content_mode: full_text
content_sha256: a9993076c9aba10060ce27f7d882066766b4f386e8809c135cbbf3b2ab219cdb

```text
# Agentic Flow 論文から ReviewCompass へ取り込む実装計画

作成日：2026-06-11

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。
```

### /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-16-nested-issue-handling-smell.md

content_mode: full_text
content_sha256: d3a1460de7638d24cbdcc34981761f5f7e63d7f1f5a25fa77f4e9404be2c7ea5

```text
# nested issue handling smell

日付：2026-06-16

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。
```

### /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-16-operation-registry-preflight-design.md

content_mode: full_text
content_sha256: 31600062b2b185d898df35a823f676f7a55f5dcd18d48240dd6e5d3a5830577b

```text
# operation registry / preflight 設計メモ

日付：2026-06-16

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。
```

### /Users/Daily/Development/ReviewCompass/docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md

content_mode: full_text
content_sha256: 03b5901cac6916ed3a0781dec316b18b9dd31a1f80fe1f1bf13816d1714ec761

```text
# maintenance workflow 遵守の修正候補メモ

作成日: 2026-06-17

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。
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
docs/notes/2026-06-05-future-development-candidates.md
docs/notes/2026-06-11-agentic-flow-adoption-plan.md
docs/notes/2026-06-16-nested-issue-handling-smell.md
docs/notes/2026-06-16-operation-registry-preflight-design.md
docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md

# Target document
## docs/notes/2026-06-05-future-development-candidates.md

# 今後開発検討すべき項目リスト

作成日：2026-06-05

この候補台帳の未実装候補は backlog plan へ移設済み。実装済み候補と移設済み候補の
詳細本文は、この旧台帳には残さない。

## 移設済み候補

- D-001 / D-002 / D-003:
  `.reviewcompass/backlog/plans/plan-2026-06-23-review-wave-recheck-pointer-hardening.yaml`
- D-007:
  `.reviewcompass/backlog/plans/plan-2026-06-23-autonomous-ledger-auditability.yaml`
- D-009:
  `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-convergence-policy.yaml`
- D-010:
  `.reviewcompass/backlog/plans/plan-2026-06-23-agent-adapter-revision.yaml`
- D-011:
  `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-assignment-tuning.yaml`
- D-012 / D-013 / D-014:
  `.reviewcompass/backlog/plans/plan-2026-06-23-triage-explanation-guard-quality.yaml`
- D-015 / D-016 / D-017:
  `.reviewcompass/backlog/plans/plan-2026-06-23-feature-quality-followups.yaml`
- D-018:
  `.reviewcompass/backlog/plans/plan-2026-06-23-false-positive-reversal-metrics.yaml`
- D-022 / D-024:
  `.reviewcompass/backlog/plans/plan-2026-06-23-reconstruction-cleanup-followups.yaml`

## 既存 backlog plan へ整理済みの候補

- D-006:
  `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-decision-mechanization.yaml`
- D-026:
  `.reviewcompass/backlog/plans/plan-2026-06-23-workflow-navigator-webui.yaml`

## 実装済みとして旧台帳から削除した候補

- D-004 normalized finding schema
- D-005 finding-to-fix traceability
- D-008 dogfooding event ledger
- D-019 time / cost / model assignment
- D-020 cross-repository replication
- D-021 deployable reconstruction readiness
- D-023 deployment independence lint
- D-025 TDD cycle evidence
- D-027 side track state model

今後の作業候補、残作業、完了条件は `.reviewcompass/backlog/index.yaml` と各 backlog plan
を正として確認する。


## docs/notes/2026-06-11-agentic-flow-adoption-plan.md

# Agentic Flow 論文から ReviewCompass へ取り込む実装計画

作成日：2026-06-11

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-action-execution-spec.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。

## docs/notes/2026-06-16-nested-issue-handling-smell.md

# nested issue handling smell

日付：2026-06-16

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-nested-issue-stack.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。


## docs/notes/2026-06-16-operation-registry-preflight-design.md

# operation registry / preflight 設計メモ

日付：2026-06-16

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-operation-registry-preflight.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。


## docs/notes/2026-06-17-maintenance-workflow-compliance-improvement-candidates.md

# maintenance workflow 遵守の修正候補メモ

作成日: 2026-06-17

このメモの実作業候補は backlog plan へ移設済み。

移設先：

- `.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml`

この旧メモには、移設済みの計画本文を残さない。今後の作業候補、残作業、完了条件は
backlog plan 側を正として確認する。
