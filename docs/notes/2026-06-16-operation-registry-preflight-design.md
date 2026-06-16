# operation registry / preflight 設計メモ

日付：2026-06-16

## 目的

`docs/notes/2026-06-16-workflow-recovery-smell-inventory.md` で整理した手戻りは、
個別には review-run、post-write、commit approval、reopen、session-record の問題に
見える。しかし根は共通している。

- 操作開始前に、前提状態を機械的に確認しきれていない
- 操作が作る成果物と既存成果物の衝突を、作成前に判定できていない
- 順序依存のある操作を、実行側が並列化できてしまう
- 正本コマンドや引数を、記憶や前例から推測してしまう
- 後段 guard で回復しているが、作成前・実行前には止められていない

根本対応は、個別 helper を増やすことではなく、各操作を **operation contract** として
登録し、実行前に同じ形式で preflight できる層を作ることである。

このメモ作成中にも同じ型の小さな手戻りが発生した。post-write triage の確認で
`tools/review_triage.py` を正規 entrypoint と推測して実行したが、実在パスは
`tools/api_providers/review_triage.py` だった。これは大きな事故ではないが、
「正本コマンドを確認せず、記憶・推測で実行してから探し直す」型であり、
operation registry / command registry が防ぐべき対象例である。

## 既に部分的にある対応

新規に全部を作る必要はない。現時点でも、次の部品は既に存在する。

### 1. workflow precheck の入口

- `tools/check-workflow-action.py`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`

既に `spec-set`、`commit`、`push`、`audit-commit`、`next`、`reopen-start`、
`reopen-advance-gate`、`autonomous-plan`、`commit-approval`、`decision-source-lint`
などのサブコマンドを持つ。

この層は、operation registry の実装先として自然である。

### 2. `next --json` と effective prompt

`check-workflow-action.py next --json` は、現在の workflow 状態から次に許される作業を
返す。`post_write_verification`、`post_write_policy_violation`、
`post_write_human_decision_required`、`reopen_in_progress`、`maintenance_in_progress`
など、作業順序の優先順位も既に機械判定している。

また、判定点ごとに effective prompt を生成し、必要な規律だけを束ねる仕組みもある。
これは「操作前に読むべき規律を operation ごとに確定する」基盤として使える。

### 3. commit 前 preflight

`check-workflow-action.py commit` は、既に多くの横断検査を集約している。

- staged ファイル分類
- commit approval の検査
- LLM 実行代行承認の検査
- post-write-verification 完了確認
- reopen 手続き記録の整合確認
- 進行中セッション記録の混入防止
- deployment independence lint
- document link lint
- decision-source-lint

これは「不可逆操作の operation contract」としてかなり進んでいる。

### 4. commit approval nonce / delegation

`check-workflow-action.py commit-approval` と
`tools/check_workflow_action/commit_approval.py` には、次が既にある。

- `prepare`
- `record`
- `delegate-execution`
- `invalidate`
- staged exact index への nonce / target digest 束縛
- secret redaction と residual secret 検出
- LLM/provider/model 非依存の record
- 実行代行承認の別ファイル保存
- `delegate-execution` 保存前の再検証
- atomic write helper

このため、commit 実行代行承認そのものはかなり整っている。残る根本課題は、
`prepare -> record -> delegate-execution -> guarded commit` を operation として
直列実行させる wrapper / runner が無いことである。

### 5. `stage` サブコマンド

`check-workflow-action.py stage` は、進行中セッション記録を検出し、それだけを
staging 対象から除外する。

これは「作業者が手で除外する」のではなく、「対象を機械処理で分ける」既存例である。
operation preflight では、この発想を staged / unstaged / pending 手続きの分離にも
広げる。

### 6. post-write-verification 判定

post-write まわりには次の既存部品がある。

- `is_post_write_verification_target`
- `list_post_write_verification_targets`
- `is_forbidden_post_write_pending_change`
- `evaluate_post_write_manifest_state`
- `validate_post_write_completion_for_targets`
- `review_run_traceability_satisfied`
- `tools/make-post-write-manifest.py`
- `tools/api_providers/review_triage.py write-manifest`

既に manifest の target hash、coverage、review-run traceability、未解決本質指摘は
検査できる。残る穴は、review-run / bundle / approval record を作る前の preflight である。

### 7. reopen の機械更新と完了検査

reopen には次がある。

- `reopen-start`
- `reopen-advance-gate`
- `validate_reopen_completion_impact_decisions`
- `pending_gates` / `completed_gates` / `required_gates` の検査
- `downstream_impact_decisions` の対応検査

特に、`completed_gates` と `downstream_impact_decisions` の対応漏れは、既に commit 前検査で
部分的に検出される。残る穴は、reopen 完了操作そのものを operation として扱い、
完了前に lint / repair candidates を出す導線である。

### 8. autonomous-plan 系

`autonomous-plan`、`autonomous-plan-template`、`autonomous-plan-record-integration` は、
作業境界、allowed paths、承認、停止条件、統合ゲートを構造化して検査する。

これは operation contract の先行例である。ただし対象は autonomous parallel に限られ、
通常の review-run、triage、post-write、reopen、commit にはまだ一般化されていない。

### 9. session-record の current guard

`tools/session-record-promote-draft.py` は `--current-session-id` を要求し、current session と
同じ session id の正式昇格を拒否する。

また commit guard は、staged の session record について元ログ hash の変化を見て、
進行中セッション記録のコミットを拒否する。

残る穴は、formal 2 層記録を書ける入口全体で current-session guard を共通化することである。

### 10. deployment / export 系の一部 preflight

`tools/build-deploy-package.py --clean` は危険な出力先を拒否する既存防止がある。
ただし deployment smoke の外部 app root 書き込みや runtime bundle export の
出力先衝突は、operation contract としてはまだ整理途上である。

## まだ足りないもの

既存部品は多いが、次が欠けている。

1. **operation registry**
   - どの操作が存在するか
   - 正規コマンドは何か
   - 必須引数は何か
   - 何を作るか
   - どの操作が直列専用か
   - どの pending 状態と衝突するか

2. **作成前 preflight**
   - review-run dir が空か
   - review target が phase に必要な一次情報を含むか
   - approval record に finding id / final label があるか
   - bundle が空でないか
   - staged / unstaged のどちらを見るべきか
   - 操作に使う entrypoint が実在し、正規パスと一致しているか

3. **runner / wrapper**
   - commit approval chain のような順序依存操作を一括で直列実行する
   - 各段階の成果物存在、digest、stale 状態を確認する
   - 並列実行対象から明示的に外す

4. **既存成果物衝突 policy**
   - 上書き禁止
   - 明示フラグがある場合だけ再実行
   - 一時ファイル生成後に検証して rename
   - 失敗時に既存正本を壊さない

5. **workflow 混線 preflight**
   - post-write pending 中に対象外差分が混ざっていないか
   - review-run / reopen / commit approval 中に別作業差分を始めていないか
   - 混線時に、pending 完了、別 worktree、保留メモ化、side-track 承認を提示する

## 提案する設計

### operation contract

各 operation を次の構造で表す。
この例では contract 側の `checks[]` と response 側の `checks[]` を同じ名前で扱っているが、
層は別である。contract 側は `implementation_status` で「実装として検査可能か」を表し、
response 側は `status` で「今回の preflight 実行結果」を表す。

```yaml
operation_id: commit_approval_chain
kind: irreversible
canonical_commands:
  - name: prepare
    command:
      - .venv/bin/python3
      - tools/check-workflow-action.py
      - commit-approval
      - prepare
      - --json
    resolution: resolved
  - name: record
    command:
      - .venv/bin/python3
      - tools/check-workflow-action.py
      - commit-approval
      - record
      - --nonce
      - "<nonce>"
      - --source-text-stdin
      - --json
    resolution: template
    placeholders:
      - nonce
  - name: delegate-execution
    command:
      - .venv/bin/python3
      - tools/check-workflow-action.py
      - commit-approval
      - delegate-execution
      - --nonce
      - "<nonce>"
      - --source-text-stdin
      - --json
    resolution: template
    placeholders:
      - nonce
  - name: guarded-commit
    command:
      - .venv/bin/python3
      - tools/guarded-git-commit.py
      - -m
      - "<message>"
      - --rationale
      - "<rationale>"
    resolution: template
    placeholders:
      - message
      - rationale
preconditions:
  - git_repo
  - staged_exact_index_present
  - post_write_completed
inputs:
  - name: user_instruction
    source: stdin
    redaction: required
input_schema:
  required:
    - user_instruction
  optional: []
identity:
  primary_key:
    - operation_id
    - target_digest
  target_selectors:
    staged_files: from_git_index
outputs:
  - .reviewcompass/runtime/approvals/commit-approval-challenge.json
  - .reviewcompass/runtime/approvals/commit-approval.json
  - .reviewcompass/runtime/approvals/commit-execution-delegation.json
worktree_policy:
  dirty_scope: staged_only
  mixed_staged_unstaged: reject
pending_conflicts:
  - next_action_kind: post_write_verification
    scope: any
  - next_action_kind: reopen_in_progress
    scope: unrelated
  - next_action_kind: maintenance_in_progress
    scope: unrelated
command_validation:
  command_must_exist: true
  subcommands_must_exist: true
  options_must_exist: true
  positional_arguments_must_match_parser: true
sequence:
  mode: serial_only
  steps:
    - prepare
    - record
    - delegate-execution
    - guarded-commit
artifact_policy:
  overwrite: deny_without_invalidate
  atomic_write: required
failure_policy:
  partial_outputs: invalidate_or_report
state_refs:
  next_action_kinds:
    - completed
    - post_write_verification
    - reopen_in_progress
    - maintenance_in_progress
  workflow_phase: not_applicable
  workflow_gate: not_applicable
  canonical_predicates:
    - validate_commit_approval
    - validate_commit_execution_delegation
    - validate_post_write_completion_for_targets
checks:
  - id: staged_exact_index_present
    implementation_status: checked
    verdict_on_fail: DEVIATION
  - id: mixed_staged_unstaged
    implementation_status: checked
    verdict_on_fail: DEVIATION
  - id: unrelated_pending_workflow
    implementation_status: not_checked
    verdict_on_unknown: WARN
```

最初から YAML 正本にする必要はない。初期実装では Python の registry 定義でよい。
重要なのは、各操作の前提、入力、出力、順序、衝突条件を一つの形式で扱うことである。
`kind` の初期許容値は `irreversible`、`review_artifact`、`workflow_state`、
`evidence_capture` に固定する。未知の `kind` は Phase 1 では registry 定義エラーとして
`DEVIATION` 扱いにする。拡張する場合は SDD 側で値を追加してから registry へ反映する。
特に、`worktree_policy`、`pending_conflicts`、`command_validation` は必須の考え方とする。
これを持たないと、post-write pending 中の別作業混在、staged / unstaged の取り違え、
存在しない option の推測実行を operation ごとの個別実装で再発させる。
また、`input_schema` と `identity` も必須である。`post_write_review` なら target files と
review-run dir、`triage_decide` なら review-run dir / finding id / final label、
`session_record_promote` なら session id / current session id のように、operation ごとの
対象識別子を機械可読に定義する。これが無いと read-only preflight が操作対象を特定できず、
結局 operation ごとの ad hoc 分岐へ戻る。
`state_refs` は、既存 workflow の正本名を参照するために持たせる。operation contract が
独自に phase 名、gate 名、pending 名を発明すると、`next` や commit guard と別の語彙が
増えてしまう。Phase 1 では、既存関数名、next action kind、reopen gate 名、workflow phase 名を
参照するだけでよい。新しい状態語彙を operation registry 側で勝手に作らない。
該当する workflow phase / gate が無い operation は、`null` ではなく `not_applicable` と書く。
`null` だと未確認なのか非該当なのかが区別できないためである。
`state_refs.next_action_kinds` は「許可状態の列挙」ではなく、この operation が参照する
既存 `next_action.kind` 語彙の一覧である。`completed` は `next --json` が既存 workflow guard 上の
停止理由なしを示す action kind として扱う。`post_write_verification`、
`reopen_in_progress`、`maintenance_in_progress` は衝突候補の action kind として参照し、
独自の `*_pending` などの別名は作らない。
この配列には、完了状態を表す語と衝突候補を表す語が同居し得る。意味の違いは
`pending_conflicts[]` や `checks[]` 側で表現し、`state_refs` 自体は「参照語彙の索引」に留める。
`checks` は preflight が実際に確認した項目を列挙する。未実装の検査は空欄や `{}` ではなく、
`not_checked` と `verdict_on_unknown` を明示する。
ここで使う `verdict_on_fail` / `verdict_on_unknown` は preflight の返す `verdict` であり、
review finding の重大度（CRITICAL / ERROR / WARN / INFO）ではない。
contract 側で使える verdict 値は `OK` / `WARN` / `DEVIATION` に固定する。
contract 側の `checks[].implementation_status` は registry 実装側の状態で、許容値は
`checked` / `not_checked` / `not_applicable` とする。response 側の `checks[].status` は実行結果で、
許容値は `pass` / `fail` / `not_checked` とする。

### 新サブコマンド案

```bash
tools/check-workflow-action.py operation-list --json
tools/check-workflow-action.py operation-preflight <operation-id> --json [--input <yaml>]
tools/check-workflow-action.py operation-plan <operation-id> --json [--input <yaml>]
```

初期段階では read-only に限定する。つまり、既存 CLI を実行せず、次だけを返す。

- 実行可否
- 足りない入力
- 衝突している pending / dirty / staged
- 作成予定成果物
- 正規コマンド
- 直列専用かどうか
- 次に人が行うべきこと

runner は後段でよい。

read-only preflight の共通レスポンスは、operation によらず少なくとも次を返す。

```json
{
  "schema_version": "operation-preflight-v1",
  "operation_id": "triage_decide",
  "verdict": "OK",
  "allowed_verdicts": ["OK", "WARN", "DEVIATION"],
  "sequence_mode": "single_step",
  "allowed_sequence_modes": ["single_step", "serial_only"],
  "state_refs": {
    "next_action_kinds": [
      "completed",
      "post_write_verification",
      "reopen_in_progress",
      "maintenance_in_progress"
    ],
    "workflow_phase": "not_applicable",
    "workflow_gate": "not_applicable",
    "canonical_predicates": []
  },
  "required_inputs": ["review_run_dir", "finding_id", "final_label"],
  "missing_inputs": [],
  "template_available": false,
  "target_identity": {
    "review_run_dir": ".reviewcompass/evidence/review-runs/<run-id>",
    "finding_id": "<finding-id>",
    "final_label": "must_fix"
  },
  "worktree_state": {
    "source": "actual_worktree",
    "overridable_by_input": false,
    "observed": {}
  },
  "pending_conflicts": [
    {
      "id": "post_write_verification",
      "status": "absent",
      "blocking": true,
      "evidence": []
    },
    {
      "id": "reopen_in_progress",
      "status": "absent",
      "blocking": true,
      "evidence": []
    },
    {
      "id": "maintenance_in_progress",
      "status": "absent",
      "blocking": true,
      "evidence": []
    }
  ],
  "checks": [
    {
      "id": "approval_record_contains_finding_and_label",
      "status": "pass",
      "verdict_on_fail": "DEVIATION"
    }
  ],
  "planned_outputs": [],
  "canonical_commands": [],
  "next_step": "string"
}
```

各 operation 固有の詳細は `target_identity`、`worktree_state`、`planned_outputs` に入れ、
トップレベルの形は揃える。これを TDD の最初の期待 JSON として固定する。

共通レスポンス object の初期 schema は次の表にまとめる。これは JSON schema 正本ではなく、
SDD 昇格時に fixture または schema へ落とすための設計メモである。
この節に出る field 名、許容値、required 条件、verdict 導出規則は、後続 SDD で検討する
候補であり、このメモ単体では最終 API 契約として扱わない。実装へ入る時点で、
テスト fixture、JSON schema、既存 parser adapter との対応を改めて固定する。

| field | type | required | notes |
|---|---|---|---|
| schema_version | string | yes | 初期値は `operation-preflight-v1` |
| operation_id | string | yes | registry 上の operation id |
| verdict | string | yes | `OK` / `WARN` / `DEVIATION` |
| allowed_verdicts | string[] | yes | 許容 verdict の列挙 |
| sequence_mode | string | yes | `single_step` / `serial_only` |
| allowed_sequence_modes | string[] | yes | 許容 sequence mode の列挙 |
| state_refs | object | yes | 参照する既存 workflow 語彙。許可状態の列挙ではない |
| required_inputs | string[] | yes | operation が要求する明示入力名 |
| missing_inputs | string[] | yes | 未充足の明示入力名 |
| template_available | boolean | yes | 不足入力に template 候補を出せるか |
| target_identity | object | yes | operation 固有の対象識別子 |
| worktree_state | object | yes | git / workflow など実状態の観測結果 |
| pending_conflicts | object[] | yes | 衝突候補ごとの観測結果 |
| checks | object[] | yes | preflight が実行または未実装表示した検査 |
| planned_outputs | string[] | yes | 生成予定成果物。read-only phase では作らない |
| canonical_commands | object[] | yes | 正規コマンド。確認専用 operation では空配列可 |
| next_step | string | yes | 人間向けの次アクション |

`checks[]` の初期 sub-field は次を想定する。これも schema 正本ではなく、SDD 昇格時の
fixture 候補である。

| field | response required | notes |
|---|---:|---|
| id | yes | check id |
| status | yes | response 側は `pass` / `fail` / `not_checked` |
| verdict_on_fail | conditional | `status: fail` になり得る check で必須 |
| verdict_on_unknown | conditional | `status: not_checked` になり得る check で必須 |
| covers_pending_conflicts | no | 複数 pending conflict を集約する check の対応 id 配列 |
| evidence | no | 実状態から得た根拠 |

共通レスポンスのトップレベル項目はすべて必須とする。`schema_version`、`operation_id`、
`verdict`、`sequence_mode`、`next_step` は文字列、`allowed_verdicts`、
`allowed_sequence_modes`、`required_inputs`、`missing_inputs`、`planned_outputs`、
`canonical_commands` は配列、`template_available` は boolean、
`state_refs`、`target_identity`、`worktree_state` は object、`pending_conflicts` と
`checks` は object 配列である。値の詳細制約は SDD 昇格時に JSON schema または同等の
テスト fixture として固定する。
`pending_conflicts[].status` の初期許容値は `absent` / `present` / `not_checked` とする。
`present` かつ `blocking: true` は `DEVIATION`、`not_checked` かつ `blocking: true` は
Phase 1 では `WARN`、runner-enabled operation では `DEVIATION` へ昇格する。
`--input <yaml>` は、明示入力をまとめて渡すための補助であり、実 worktree 状態や git index を
上書きするものではない。preflight は、CLI / input YAML 由来の申告値と、git index・既存 YAML・
既存成果物などの実状態を分けて返す。安全系の状態判定は実状態を正とし、申告値だけで
`OK` にしてはいけない。
同じ明示入力が CLI 引数と input YAML の両方にあり、値が一致しない場合は `DEVIATION` とする。
値が一致する場合は重複していてもよい。CLI が無く input YAML だけに値がある場合は、
その値を明示入力として扱う。ただし実状態由来の値は input YAML で上書きできない。
表の「明示入力」は、CLI または input YAML で与えられなければ `missing_inputs` に入る。
ただし operation が template 生成候補を持つ入力は、`missing_inputs` と同時に
`template_available: true` を返せる。表の「状態入力」は実状態から読むため、
ユーザが直接埋める missing input にはしない。

`verdict` の意味は次で固定する。

- `OK`：既知の必須入力、既知の状態検査、既知の衝突検査がすべて通っており、次操作へ進める
- `WARN`：契約フィールドはあるが、一部の非遮断検査が未実装または注意情報として残る。
  read-only caller は注意として表示する。runner-enabled operation では、明示的な許可方針が
  無い限り停止する
- `DEVIATION`：必須入力欠落、既知の衝突、存在しない command / option、上書き禁止違反など、
  操作を開始してはいけない状態

Phase 1 では contract field の存在を必須にする。検査ロジックが未実装の field は
`not_checked` として出してよいが、その場合は `OK` ではなく `WARN` に倒す。
安全に関係する既知衝突を検査できないまま `OK` にしてはいけない。
全体 `verdict` は、`missing_inputs`、`pending_conflicts`、`checks` の最も重い判定から導出する。
`checks` に `status: not_checked` かつ `verdict_on_unknown: WARN` が一つでもあれば、
他がすべて通っていても全体 `verdict` は `WARN` になる。
`checks[].verdict_on_fail` は `status: fail` になり得る check で必須、
`checks[].verdict_on_unknown` は `status: not_checked` になり得る check で必須とする。
`pending_conflicts[]` は衝突候補ごとの観測結果であり、`checks[]` はその観測や入力検査から
導かれる検査単位である。複数の pending conflict を 1 つの check に集約してよいが、
集約する場合は `checks[].covers_pending_conflicts` で対象 id を列挙する。
また、例示 JSON が `absent` だけで `OK` になる場合でも、TDD fixture では
`not_checked` conflict が `WARN` へ倒れる例を別に用意する。
ただし Phase 1 の `WARN` は「既存 workflow をただちに止める実行ゲート」ではなく、
read-only advisory とする。operation runner に組み込む段階では、runner-enabled operation の
安全系 `not_checked` は `DEVIATION` にするか、その operation を runner-enabled にしない。
つまり、Phase 1 は設計と観測のための警告、Phase 2 以降は実行前停止に使う。

`operation-plan` は `operation-preflight` の結果を元に、人が次に実行するコマンド列と
必要入力を表示する read-only 表示である。Phase 1 では成果物を書かず、`verdict` の範囲も
`operation-preflight` と同じにする。Phase 2 の runner 実装に入るまでは、
`operation-plan` は実行・template 生成・ファイル作成をしない。
`canonical_commands` は preflight / plan の両方で同じトップレベル必須フィールドとする。
ただし、実行コマンドを持たない確認専用 operation では空配列を許す。実行可能な
operation では command registry が解決できる command object を返す。

### command registry との関係

`reopen-status` や `next --file` のような誤認を防ぐには、operation registry とは別に
command registry が必要である。
今回の `tools/review_triage.py` と `tools/api_providers/review_triage.py` の取り違えも
同じ分類である。存在しない補助コマンド名だけでなく、実在しない script path の推測実行も
preflight の対象にする。

ただし、初期実装では command registry を独立 runner にしない。責務境界は次とする。

- operation registry：作業単位の前提、入力、出力、順序、成果物衝突、pending 衝突を扱う
- command registry：実在するサブコマンド、option を機械可読に返す
- operation preflight：必要に応じて command registry を参照し、存在しないコマンドや
  option を実行前に拒否する

つまり、command registry は operation preflight の補助情報であり、Phase 1 では
独立した `command-preflight` 実行導線を必須にしない。後で必要になった場合だけ、
独立サブコマンドへ切り出す。
canonical command の正本は operation contract 側に置く。command registry は
「その command / option が実 parser に存在するか」を検証する参照情報であり、
正規手順そのものを二重管理しない。

将来、command registry を独立導線に切り出すなら、次のような表示系サブコマンドが考えられる。
ただし Phase 1 の必須実装ではない。

```bash
tools/check-workflow-action.py command-list --json
tools/check-workflow-action.py command-preflight next --candidate-option file --json
```

初期実装では、`operation-preflight` が内部で `--help` 相当または parser 情報を参照し、
存在しないサブコマンドや option を拒否できれば足りる。
正本は help 文字列ではなく、`argparse` parser を作るコード側に置く。実装時は parser 構築を
関数化し、`parser._actions` / subparser choices から command / option の存在を機械判定する。
help 出力は人間向け表示であり、機械判定の正本にしない。
この command registry が検査するのは、argparse が宣言している範囲に限定する。
具体的には、サブコマンド存在、option 名、required option、choices、mutually exclusive group、
位置引数の個数・名前づけなどである。target file の中身、approval record の意味的妥当性、run dir の衝突、
staged / unstaged の選択などは dynamic / semantic constraint なので、operation contract の
`checks` 側で扱う。
parser が実行時に動的生成される subcommand や、plugin 的に後から注入される option は
Phase 1 の command registry の対象外とする。対象外の command を使う operation は、
registry に登録する前に静的に検査可能な entrypoint を用意する。
`tools/guarded-git-commit.py` のように `check-workflow-action.py` 以外の entrypoint を
canonical command に含める場合は、その entrypoint 用の parser adapter を用意する。
adapter が無い間は command validation の該当 check を `not_checked` とし、全体 verdict は
少なくとも `WARN` にする。

Phase 1 の command validation は、次のように切り分ける。

- parser adapter があり、実 parser から存在しない command / option / required input 欠落を
  確認できた場合は `DEVIATION`
- parser adapter があり、command / option / required input が確認できた場合は `OK`
- parser adapter が無く、静的確認できない entrypoint は `not_checked` とし、全体 verdict は
  少なくとも `WARN`
- runner-enabled operation では、上記の `not_checked` を残したまま実行へ進めない

つまり Phase 1 が read-only advisory であることと、parser で確認できる明白な誤コマンドを
`DEVIATION` として返すことは両立する。`WARN` は「確認不能」、`DEVIATION` は「確認済みの不成立」
として使い分ける。

## operation の初期対象

最初から全対応しない。既存部品が多く、効果が高い順に扱う。

### Phase 1: read-only registry

| operation | kind | source smell |
|---|---|---|
| `commit_approval_chain` | `irreversible` | 主要 3 件 #3、B-11 |
| `post_write_review` | `review_artifact` | B-9、B-12、B-14 |
| `review_run_create` | `review_artifact` | B-1、B-8 |
| `triage_decide` | `review_artifact` | B-2 |
| `reopen_finalize` | `workflow_state` | B-10 |
| `session_record_promote` | `evidence_capture` | B-6 |
| `document_type_preflight` | `review_artifact` | B-12 |
| `review_criteria_preflight` | `review_artifact` | B-13 |
| `post_write_manifest_coverage_preflight` | `review_artifact` | B-14 |

この段階では、実行せず preflight だけを返す。
`deployment_smoke` と `bundle_export` は Phase 1 の初期登録対象には含めない。
ただし同じ contract で扱える将来候補として、後続の比較表には残す。

Phase 1 の各 operation は、少なくとも次の入力粒度を持つ。

| operation | 明示入力 | 状態入力 | target identity |
|---|---|---|---|
| commit_approval_chain | user instruction（stdin/no-store） | staged index | target digest、staged file set digest |
| post_write_review | target files、review-run dir、criteria、variant | dirty / staged state | target file sha256、review-run id |
| review_run_create | target、phase、criteria、review-run dir、variant | existing run dir | target manifest、run id |
| triage_decide | review-run dir、finding id、final label、approval record path（任意。無ければ template 候補） | triage.yaml、model-result-summary.yaml | review-run dir、finding id、final label |
| reopen_finalize | in-progress reopen file | spec.json、completed/in-progress files | process id、pending/completed/required gates |
| session_record_promote | session id、current session id、source | draft path、formal output path | session id、current session id、draft path、formal output path |
| document_type_preflight | target files | file type、front matter、document location | target file sha256、document type |
| review_criteria_preflight | target files、document type、criteria id | effective prompt、criteria template | criteria digest、target file sha256 |
| post_write_manifest_coverage_preflight | review-run dir、manifest path | target-manifest、bundle manifest、current post-write targets | review-run target set、manifest target set |

この表は Phase 1 の registry 最小充足条件である。`worktree_policy` と
`pending_conflicts` も全 operation に持たせるが、Phase 4 までは共通混線防止を
完全実装しない。Phase 1 では「未実装なら `not_checked` と出す」ことを許し、
契約フィールド自体は先に固定する。
ここでいう「明示入力」は CLI 引数や stdin で与える値、「状態入力」は git index や
既存 YAML のように preflight が読み取る値である。`triage_decide` の approval record は
実行には必要だが、Phase 1 の read-only preflight では無ければ `missing_inputs` と
`template_available: true` を返す。template 生成は Phase 2 の wrapper 側責務である。

### Phase 2: wrapper 化

- `commit_approval_chain`
  - 直列専用
  - `prepare -> record -> delegate-execution -> guarded commit`
  - 各段階で digest / stale / existence を確認

- `triage_decide`
  - approval record の finding id / final label 事前検査
  - 不足時は approval template を生成、または明確な停止メッセージ

- `post_write_review`
  - target files と review-run dir の整合確認
  - bundle 空検出
  - manifest の coverage が review-run の実 target set または bundle manifest を超えないことを確認

`review_run_create` と `post_write_review` の責務は分ける。`review_run_create` は
review-run directory、target、phase、criteria、variant、target manifest の作成前条件を扱う。
`post_write_review` はそれを利用する上位 operation であり、post-write 対象ファイル、
review-run、triage、write-manifest、traceability のまとまりを扱う。run dir の予約や上書き拒否は
`review_run_create`、post-write manifest との対応と unresolved finding の扱いは
`post_write_review` の責務である。

### Phase 3: artifact policy 共通化

- atomic write helper を review-run / triage / proxy approval / bundle export に横展開する
- 既存ファイル上書きは既定拒否
- 明示フラグ付き再実行だけ許す

### Phase 4: worktree 混線防止

- pending 手続きと dirty / staged 差分を照合する
- post-write pending 中の対象外変更を開始前に止める
- side-track へ進む場合は maintenance in-progress を要求する

## operation 別の既存部品と不足

| operation | 導入段階 | 既存部品 | 不足 |
|---|---|---|---|
| commit_approval_chain | Phase 1 / 2 | `prepare` / `record` / `delegate-execution` / guarded commit / digest 検査 | 直列 wrapper、並列実行防止、chain 全体の状態表示 |
| post_write_review | Phase 1 / 2 | `next` の pending 判定、manifest 判定、traceability 判定、`tools/make-post-write-manifest.py` | post-write target と review-run の対応検査、diff bundle helper、manifest / triage traceability の開始前表示 |
| review_run_create | Phase 1 / 2 | `tools/api_providers/run_review.py` / `tools/api_providers/run_role.py` / target-manifest | 既存 run dir 上書き防止、run id 衝突検査、phase 別 target 一次情報検査 |
| triage_decide | Phase 1 / 2 | `tools/api_providers/review_triage.py decide` / `write-manifest` / approval record 検査 | approval template、finding id / final label preflight、正規 entrypoint path 検査、atomic decision write |
| reopen_finalize | Phase 1 | `reopen-start` / `reopen-advance-gate` / completion impact validation | finalize operation、gate 正規化 lint、修復候補表示 |
| session_record_promote | Phase 1 | `tools/session-record-promote-draft.py` の current-session-id 拒否、commit guard | backfill 側との current guard 共通化、formal 出力入口の棚卸し |
| document_type_preflight | Phase 1 | front matter、配置、post-write 対象判定 | 文書タイプと review 期待値の機械判定、仕様候補化の警告 |
| review_criteria_preflight | Phase 1 | effective prompt、criteria id | 文書タイプ別 scope / out-of-scope / finding policy の生成・検査 |
| post_write_manifest_coverage_preflight | Phase 1 / 2 | target-manifest、manifest、`review_run_traceability_satisfied` | review-run 実 target set と manifest target_files の一致、multi-target bundle manifest |
| deployment_smoke | 将来候補 | `tools/build-deploy-package.py --clean` | 外部 app root 書き込み対象の事前一覧と衝突拒否 |
| bundle_export | 将来候補 | provenance 欠落拒否 | 出力先存在 preflight、再輸出 policy |

成果物の単位は SDD 昇格時に object 化する。Phase 1 のメモでは path 配列で示すが、
実装時は `file` / `directory` / `group` を区別し、review-run directory のような複数ファイル成果物は
group として扱う。group の一部だけが存在する半壊状態は衝突として検出し、atomic write は
単一ファイル単位と operation group 単位を分けて定義する。

## 実装時の注意

- `next --json` を置き換えない。operation preflight は `next` の後段で使う。
- commit guard を弱めない。operation runner は作成前防止であり、guard は最後の保険として残す。
- semantic judgment は自動化しない。機械化するのは構造、存在、順序、対象一致、衝突、hash まで。
- 既存サブコマンドを消さない。まず registry から既存サブコマンドを参照する。
- 初期実装は read-only preflight に限定し、runner は高リスク operation から追加する。
- TDD では、operation contract の JSON 出力を先に固定する。

## 最初の実装候補

最初の実装は `operation-preflight commit_approval_chain` がよい。

理由：

- 不可逆操作に近く、効果が大きい
- 既存部品がほぼそろっている
- 直列専用という operation registry の価値が分かりやすい
- 今回実際に `record` と `delegate-execution` の並列実行ミスが起きた
- 成功条件と失敗条件をテストしやすい

期待する最小出力：

```json
{
  "schema_version": "operation-preflight-v1",
  "operation_id": "commit_approval_chain",
  "verdict": "WARN",
  "allowed_verdicts": ["OK", "WARN", "DEVIATION"],
  "sequence_mode": "serial_only",
  "allowed_sequence_modes": ["single_step", "serial_only"],
  "state_refs": {
    "next_action_kinds": [
      "completed",
      "post_write_verification",
      "reopen_in_progress",
      "maintenance_in_progress"
    ],
    "workflow_phase": "not_applicable",
    "workflow_gate": "not_applicable",
    "canonical_predicates": [
      "validate_commit_approval",
      "validate_commit_execution_delegation",
      "validate_post_write_completion_for_targets"
    ]
  },
  "required_inputs": ["user_instruction"],
  "missing_inputs": [],
  "template_available": false,
  "target_identity": {
    "target_digest": "commit-approval-v1:<digest>",
    "staged_file_set_digest": "commit-approval-v1:<digest>"
  },
  "worktree_state": {
    "source": "actual_worktree",
    "overridable_by_input": false,
    "observed": {
      "staged_files": "present",
      "mixed_staged_unstaged": "absent"
    }
  },
  "pending_conflicts": [
    {
      "id": "post_write_verification",
      "status": "not_checked",
      "blocking": true,
      "evidence": []
    },
    {
      "id": "reopen_in_progress",
      "status": "not_checked",
      "blocking": true,
      "evidence": []
    },
    {
      "id": "maintenance_in_progress",
      "status": "not_checked",
      "blocking": true,
      "evidence": []
    }
  ],
  "checks": [
    {
      "id": "staged_exact_index_present",
      "status": "pass",
      "verdict_on_fail": "DEVIATION"
    },
    {
      "id": "mixed_staged_unstaged",
      "status": "pass",
      "verdict_on_fail": "DEVIATION"
    },
    {
      "id": "unrelated_pending_workflow",
      "status": "not_checked",
      "covers_pending_conflicts": [
        "post_write_verification",
        "reopen_in_progress",
        "maintenance_in_progress"
      ],
      "verdict_on_unknown": "WARN"
    },
    {
      "id": "guarded_git_commit_parser_adapter",
      "status": "not_checked",
      "verdict_on_unknown": "WARN"
    }
  ],
  "planned_outputs": [
    ".reviewcompass/runtime/approvals/commit-approval-challenge.json",
    ".reviewcompass/runtime/approvals/commit-approval.json",
    ".reviewcompass/runtime/approvals/commit-execution-delegation.json"
  ],
  "canonical_commands": [
    {
      "name": "prepare",
      "resolution": "resolved",
      "placeholders": [],
      "command": [".venv/bin/python3", "tools/check-workflow-action.py", "commit-approval", "prepare", "--json"]
    },
    {
      "name": "record",
      "resolution": "template",
      "placeholders": ["nonce"],
      "command": [".venv/bin/python3", "tools/check-workflow-action.py", "commit-approval", "record", "--nonce", "<nonce>", "--source-text-stdin", "--json"]
    },
    {
      "name": "delegate-execution",
      "resolution": "template",
      "placeholders": ["nonce"],
      "command": [".venv/bin/python3", "tools/check-workflow-action.py", "commit-approval", "delegate-execution", "--nonce", "<nonce>", "--source-text-stdin", "--json"]
    },
    {
      "name": "guarded-commit",
      "resolution": "template",
      "placeholders": ["message", "rationale"],
      "command": [".venv/bin/python3", "tools/guarded-git-commit.py", "-m", "<message>", "--rationale", "<rationale>"]
    }
  ],
  "next_step": "run_prepare"
}
```

## このメモの位置づけ

このメモは設計入口であり、仕様正本ではない。実装へ入る場合は、workflow-management の
SDD 手順に乗せる。既存 workflow precheck の適用範囲を広げるため、
`docs/operations/WORKFLOW_PRECHECK.md` と `.reviewcompass/specs/workflow-management/`
のどちらへ反映するかを最初に判断する。

反映先の判断基準は次とする。

- 要件・受入基準・状態遷移・fail-closed 条件は `.reviewcompass/specs/workflow-management/`
  に載せる
- 運用時に人や LLM が呼ぶコマンド、利用順序、出力の読み方は `docs/operations/` に載せる
- 実装詳細や registry の内部表現は `tools/check_workflow_action/` とテストで固定する
- どちらにも関係する場合は、SDD 側を正本、operations 側を運用導線として同期させる

本メモ内の JSON 形状、verdict 計算規則、許容値、fail-closed 条件は、実装に入る時点で
SDD 側へ昇格する。調査結果や既存部品の棚卸しは、このメモに残すだけでよい。

なお、本メモの「既に部分的にある対応」は、2026-06-16 に以下を読んで拾った。

- `tools/check-workflow-action.py --help`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/commit_approval.py`
- `tools/session-record-promote-draft.py`
- `tools/make-post-write-manifest.py`
- `config/api-settings.yaml`
