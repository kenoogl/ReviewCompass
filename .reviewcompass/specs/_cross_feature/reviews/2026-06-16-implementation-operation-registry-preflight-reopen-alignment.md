---
date: 2026-06-16
gate: stages/implementation.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: operation-registry-preflight-unified-design
decision: existing_sufficient
---

# implementation alignment（整合確認）：operation registry / preflight

reopen R-0 の第3過程、workflow-management implementation フェーズの alignment。Requirement 12 r2、design、tasks、implementation triad-review 対処、implementation review-wave 判定との整合を確認する。

## Requirement 12 r2 との整合

| 要件観点 | implementation での扱い | 整合判定 |
| --- | --- | --- |
| operation registry | `stages/operation-registry.yaml` に初期 operation contract を置き、loader / schema validator を `tools/check_workflow_action/operation_registry.py` に追加した。 | 整合。 |
| read-only preflight | `operation-preflight` は registry、workflow state、parser 由来 option、path 文字列を読むだけで、review-run / manifest / approval / session record / commit / deploy output を作らない。 | 整合。 |
| response / verdict | `operation-preflight-v1`、`allowed_verdicts`、`exit_code_contract`、`state_refs`、`checks`、`planned_outputs`、`reasons` を返す。 | 整合。 |
| command validation | 手書き option 表を廃止し、対象 entrypoint の parser 生成 `--help` から option を抽出して registry の `canonical_invocation.options` と照合する。Phase 1 の parser adapter として扱い、第二正本化を避ける。 | 整合。 |
| family required checks | `family_required_checks` の各項目を `checks[]` に個別出力し、executor 未定義の check は `not_implemented` で DEVIATION とする。 | 整合。 |
| review artifact preflight | `review_run_create` / `triage_decide` の operation family で target / manifest / criteria / approval / artifact drift / staged-vs-unstaged の check を実行する。 | 整合。 |
| serial_only approval chain | commit approval chain operation を `serial_only` として登録し、nonce / digest / expiry / consume / invalidated / target 系 check executor を用意した。 | 整合。 |
| current-session formal record guard | session record capture operation を登録し、current / target session id と formal output 禁止の check executor を用意した。 | 整合。 |
| nested issue handling | nested issue operation を登録し、parent / discovered issue / relation / allowed files / return condition / nesting depth の check executor を用意した。 | 整合。 |
| deployment / export | deployment planned output は絶対パスと `..` traversal を DEVIATION にし、path を作成せず文字列・resolve 関係だけで境界を確認する。 | 整合。 |
| reopen scope / impact review scope | workflow state operation は `next --json` を読み、current mainline、required action、phase / stage、direct / indirect features、pending / completed / superseded gates、state files を `state_refs.next_action` に返す。 | 整合。 |
| LLM 非依存 | registry validator は `llm` / `provider` / `model` / `model_id` / `proxy_model_id` を再帰的に拒否し、テストで確認した。 | 整合。 |

## design との整合

- design の Phase 1 / Phase 2 分離に合わせ、今回は read-only preflight のみを実装した。
- design の operation contract schema にある `operation_id`、`kind`、`operation_family`、`canonical_invocation`、`workflow_binding`、`required_inputs`、`target_identity`、`planned_outputs`、`sequence_mode`、policy 群、`family_required_checks`、`vocabulary_refs` を実装 schema として検査する。
- design は command validation の正本を parser / parser adapter としている。実装は Phase 1 の adapter として、対象 CLI の parser が生成する `--help` から option を抽出する。これは registry 側の手書き option 表ではなく、実 parser 由来の read-only 観測値として扱う。将来、各 CLI が機械可読 parser export を持つ場合は、この adapter を置き換えられる。
- design の fail-closed 方針に合わせ、未登録 operation、schema 欠落、未知 kind / family / sequence mode、未知 check、parser option 不一致、path traversal を DEVIATION とする。

## tasks との整合

T-014 の成果物と完了条件に対して、実装は次を満たす。

- `stages/operation-registry.yaml` を追加済み。
- `tools/check_workflow_action/operation_registry.py` を追加済み。
- `tools/check_workflow_action/operation_preflight.py` を追加済み。
- `tools/check-workflow-action.py operation-preflight --operation-id <id> --json` を追加済み。
- registry schema、family checks、next state dimensions、review artifact check、deployment/export boundary、LLM 非依存、exit-code contract を `tests/tools/test_operation_registry_preflight.py` で確認済み。
- Phase 1 の read-only preflight に限定し、runner-enabled operation は実装していない。

## implementation triad-review 対処との整合

implementation triad-review の同根クラスタと対処は次である。

| cluster | final_label | 対処 |
| --- | --- | --- |
| C1: Known invocation が第二正本化 | must-fix | 手書き `KNOWN_INVOCATIONS` を廃止し、parser 生成 `--help` から option を抽出する adapter に変更。`--verify` 受理と `--file` 拒否のテストを追加。 |
| C2: family_required_checks が宣言だけ | must-fix | 各 declared check を `checks[]` に個別出力し、未実装 check は `not_implemented` で DEVIATION。 |
| C3: deployment/export path 境界が浅い | must-fix | 絶対パスと `..` traversal を拒否し、path を作成しないテストを追加。 |
| C4: exit-code / JSON contract | should-fix | response に `exit_code_contract` を追加し、CLI 側で未知 verdict を明示的に DEVIATION 化。 |
| C5: LLM/provider/model 独立性 | leave-as-is | 既存実装を維持。 |
| C6: 既存 CLI 回帰証跡 | leave-as-is | 既存回帰テスト通過を維持。 |

## review-wave 判定との整合

`2026-06-16-implementation-operation-registry-preflight-review-wave.md` は no_impact と判定し、他 6 機能への implementation 正本修正不要とした。

今回の implementation は workflow-management が所有する operation 操作前チェック入口であり、foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation の所有コードや実装タスクを変更しない。したがって review-wave 判定と整合する。

## 検証結果

実行済み検証：

- `python3 -m unittest tests.tools.test_operation_registry_preflight -v`：11 tests OK
- `python3 tools/check-workflow-action.py operation-preflight --operation-id workflow_next_preflight --json`：OK
- `python3 tools/check-workflow-action.py operation-preflight --operation-id review_run_create --json`：OK
- `python3 tools/api_providers/review_triage.py assert-apply-fixes-ready --review-run-dir ... --approval-record ...`：OK
- `python3 -m unittest tests.tools.test_review_wave_summary tests.tools.test_decision_source_lint -v`：14 tests OK
- `python3 -m unittest tests.tools.test_check_workflow_action -v`：189 tests OK
- `git diff --check`：OK

## 判定

- **decision：existing_sufficient**。
- implementation は Requirement 12 r2、design、tasks、triad-review 対処、review-wave 判定と整合する。
- 他 feature の implementation 正本を再オープンする必要はない。
- 次段は implementation approval であり、人間承認 gate とする。
