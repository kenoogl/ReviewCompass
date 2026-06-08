# 全 feature 仕様・実装乖離横断監査（代表例ベース）

作成日: 2026-06-08
版: draft-1
作成者: Codex
状態: 未承認の監査メモ
対象リポジトリ版: `c89beff5634a5f9e6ce9a8dcce734be3195dd67a`
対象版メモ: 本文書は未コミットの新規メモであり、監査入力は `c89beff Record conformance drift audit process` の直後、本文書の追加前のリポジトリ状態で固定する。
自己参照除外: 本文書は本監査の証拠入力ではない。commit と承認が完了するまで、conformance-evaluation tooling の authoritative evidence ingestion 対象から除外する。

## 0. 位置づけ

本メモは、`docs/notes/2026-06-08-conformance-drift-audit-process.md` で定義した read-only 監査を、全 feature に横展開した記録である。

初回の詳細監査は `workflow-management` を対象に実施済みであり、結果は `docs/notes/2026-06-08-workflow-management-conformance-drift-audit.md` に記録している。本メモでは、その結果を基準に、`foundation`、`runtime`、`evaluation`、`analysis`、`self-improvement`、`conformance-evaluation` へ同じ見方を広げ、同根の問題をまとめる。

この監査は `conformance-evaluation` 本格実装前の手作業テストケースである。仕様や実装を直接修正するものではなく、requirements / design / operations / tests / carry-forward のどこに戻すべきかを判断するための材料を整理する。

## 1. 監査方法

- 対象 feature は `foundation`、`runtime`、`evaluation`、`analysis`、`workflow-management`、`self-improvement`、`conformance-evaluation` の 7 件。
- 仕様側は各 feature の `requirements.md`、`design.md`、`tasks.md`、関連 operations 文書、実装レビュー記録を参照した。
- 実装側は `tools/`、`tests/`、review-run 成果物、post-write / review-wave の運用成果物を参照した。
- 判定は、実装由来の契約が現仕様のどこに対応しているかを read-only で確認し、本メモ内のローカル分類語彙として `spec-missing`、`code-missing`、`mismatch`、`implementation-detail`、`ownership-unclear` に分類する。この分類語彙の正本所有候補は `conformance-evaluation` の requirements / design であり、まだ採用済みの共有語彙ではない。
- 本メモでは候補を記録するだけで、仕様採用・実装修正・workflow state 更新は行わない。

本メモの代表 drift item は網羅リストではない。全 feature に横展開したときに同根性が見える代表例だけを抽出し、後続の機械化で必要な出力粒度を確認するための監査サンプルとして記録する。

本メモの traceability level は path-level である。line-level anchors、claim-level decomposition、confidence scoring は未実施であり、完全な conformance-evaluation fixture として使う場合は追加抽出が必要である。

`owner_candidate` の候補値は次の意味で使う。

- `requirements`: 利用者向け・feature 外部向けの要求として所有する候補。
- `design`: feature 内部構造や設計判断として所有する候補。
- `operations`: 運用手順・workflow discipline として所有する候補。
- `tool_contract`: CLI / helper / validator の入出力契約として所有する候補。
- `test_contract`: テストが最も具体的な契約を保持しており、上位仕様へ戻すか未判断の候補。
- `review_evidence`: review-run や triage 成果物が契約の所在や完了判定を示している候補。
- `carry_forward`: 未解決・後続判断項目として持ち越す候補。

### 1.1 参照証拠

| 種別 | 参照 |
| --- | --- |
| 初回監査 | `docs/notes/2026-06-08-workflow-management-conformance-drift-audit.md` |
| review-wave 記録 | `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-review-wave.md` |
| review-wave 改善メモ | `docs/notes/2026-06-04-implementation-review-wave-improvements.md` |
| foundation tests | `tests/foundation/test_t001_layout.py` から `tests/foundation/test_t010_completion.py` |
| runtime tests | `tests/runtime/test_t001_layout.py` から `tests/runtime/test_t011_traceability.py` |
| evaluation tests | `tests/evaluation/test_t001_layout.py` から `tests/evaluation/test_t011_integration_pipeline.py`、`tests/evaluation/test_downstream_interface.py` |
| analysis tests | `tests/analysis/test_analysis_t001_layout.py` から `tests/analysis/test_analysis_t011_traceability.py` |
| workflow-management tests | `tests/tools/test_check_workflow_action.py`、`tests/tools/test_guarded_git_commit.py`、`tests/tools/test_workflow_management_implementation_drafting.py`、`tests/tools/test_workflow_management_implementation_triad_prep.py` |
| self-improvement implementation | `tools/self_improvement/`、`tools/self_improvement/schemas/` |
| conformance-evaluation operations | `docs/operations/CONFORMANCE_EVALUATION.md` |
| conformance-evaluation implementation | `tools/conformance_evaluation/check_mode.py`、`tools/conformance_evaluation/generation_mode.py`、`tools/conformance_evaluation/comparison_model.py`、`tools/conformance_evaluation/evaluation_record.py` |
| conformance-evaluation tests | `tests/conformance-evaluation/test_conformance_evaluation.py` |
| implementation review evidence | `.reviewcompass/specs/foundation/reviews/2026-06-01-implementation-triad-review.md`、`.reviewcompass/specs/runtime/reviews/2026-06-02-implementation-triad-review.md`、`.reviewcompass/specs/evaluation/reviews/2026-06-03-implementation-triad-review.md`、`.reviewcompass/specs/analysis/reviews/2026-06-03-implementation-review-run/`、`.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/`、`.reviewcompass/specs/self-improvement/reviews/2026-06-04-self-improvement-implementation-review-run/`、`.reviewcompass/specs/conformance-evaluation/reviews/2026-06-04-conformance-evaluation-implementation-review-run/` |

## 2. feature 別サマリ

| Feature | 観測結果 | 主な差分候補 |
| --- | --- | --- |
| foundation | shared vocabularies、schema encoding、metadata、completion report、strategy coverage はテストで強く契約化されている。概ね仕様と整合しているが、completion / encoding の細かな fail-closed 条件はテストが最も具体的である。 | `implementation-detail` / `ownership-unclear`: completion report の双方向整合、schema encoding edge case、strategy coverage count を foundation 仕様本文に戻すか、validator 契約に閉じるか。 |
| runtime | session controller、axis selector、step executor、validation bridge、evidence writer、bundle exporter が詳細な manifest / state transition / immutability / provenance 契約を持つ。 | `spec-missing` / `ownership-unclear`: manifest field count、state transition table、raw immutable / derived separation、failure observation、bundle checksum / provenance の正本位置。 |
| evaluation | bundle intake、admission、classifier、readiness、metrics、reporting、diff report、staleness propagation がテストで精密化されている。review-wave では feature-local evidence pointer の問題も出た。 | `ownership-unclear`: API review-run bundle の置き場所、admission / readiness の語彙、staleness の downstream 伝播、dogfooding metrics の仕様所有者。 |
| analysis | evaluation / conformance intake、claim map、evidence register、caveat register、figures、convergence、destinations、staleness が横断入力に依存する。 | `spec-missing` / `mismatch`: analysis が runtime raw evidence を読まない非干渉契約、invalid / analysis_blocked の exclusion 扱い、空 caveat register、destination manifest の責務境界。 |
| workflow-management | 詳細は `docs/notes/2026-06-08-workflow-management-conformance-drift-audit.md` に記録済み。`next`、post-write verification、commit approval、audit-commit、autonomous plan / ledger が仕様本文より濃く実装契約化されている。 | `spec-missing`: post-write manifest coverage、review_run traceability、commit approval target hash、guarded commit side effect、audit-commit、autonomous ledger。 |
| self-improvement | input model、signal extraction、proposal、verification、approval、rollback、effect measurement、machine verification、carry-forward register が多段の fail-closed 契約を持つ。 | `spec-missing` / `ownership-unclear`: rejection / declined adoption の語彙、proposal id の桁境界、superseded reopen fields、direct discipline write の fail-closed、carry-forward general fields の local reference 禁止。 |
| conformance-evaluation | requirements / design は豊富だが、現実装は generation / check mode の first-pass pipeline と比較モデル中心。手作業監査で欲しい出力は、現ツールの自動出力より広い。 | `ownership-unclear`: 6 criteria 全面比較、feature 横断 drift clustering、証拠 refs 付き設計スケッチ、contract ownership map、反映候補の分類出力が、既存仕様の必須実装契約か、次段の carry-forward か未判断。 |

### 2.1 代表 drift item と所有候補

この表の owner はすべて候補であり、採用済み所有者ではない。`Primary owner candidate` は現時点で最も近い所有先の仮説、`Secondary owner candidate` は代替候補である。

| ID | Feature | Classification (provisional) | Primary owner candidate (provisional) | Secondary owner candidate (provisional) | Contract refs | Code / test / evidence side |
| --- | --- | --- | --- | --- | --- | --- |
| XDI-FOUND-001 | foundation | `ownership-unclear` | `tool_contract` | `test_contract` | `.reviewcompass/specs/foundation/requirements.md`、`.reviewcompass/specs/foundation/design.md` | `tools/foundation_validators/check_completion.py`、`tools/foundation_validators/check_encoding_convention.py`、`tests/foundation/test_t008_encoding.py`、`tests/foundation/test_t010_completion.py` |
| XDI-RUNTIME-001 | runtime | `spec-missing` | `design` | `tool_contract` | `.reviewcompass/specs/runtime/requirements.md`、`.reviewcompass/specs/runtime/design.md` | `tests/runtime/test_t002_session_controller.py`、`tests/runtime/test_t008_evidence_writer.py`、`tests/runtime/test_t009_validation_bridge.py`、`tests/runtime/test_t010_bundle_exporter.py` |
| XDI-EVAL-001 | evaluation | `ownership-unclear` | `operations` | `review_evidence` | `.reviewcompass/specs/evaluation/requirements.md`、`.reviewcompass/specs/evaluation/design.md` | `.reviewcompass/specs/evaluation/reviews/2026-06-03-implementation-triad-review.md`、`docs/notes/review-runs/evaluation-implementation-triad-2026-06-03-r1/`、`tests/evaluation/test_t002_intake.py`、`tests/evaluation/test_t010_staleness.py` |
| XDI-ANALYSIS-001 | analysis | `spec-missing` | `design` | `operations` | `.reviewcompass/specs/analysis/requirements.md`、`.reviewcompass/specs/analysis/design.md` | `tests/analysis/test_analysis_t002_intake.py`、`tests/analysis/test_analysis_t005_caveat_register.py`、`tests/analysis/test_analysis_t008_conformance_intake.py`、`tests/analysis/test_analysis_t009_destinations.py` |
| XDI-WM-001 | workflow-management | `spec-missing` | `operations` | `tool_contract` | `.reviewcompass/specs/workflow-management/requirements.md`、`.reviewcompass/specs/workflow-management/design.md`、`docs/operations/WORKFLOW_NAVIGATION.md`、`docs/disciplines/discipline_post_write_verification.md` | `tools/check-workflow-action.py`、`tools/guarded-git-commit.py`、`tests/tools/test_check_workflow_action.py`、`tests/tools/test_guarded_git_commit.py` |
| XDI-SI-001 | self-improvement | `spec-missing` | `requirements` | `test_contract` | `.reviewcompass/specs/self-improvement/requirements.md`、`.reviewcompass/specs/self-improvement/design.md` | `tools/self_improvement/approval_model.py`、`tools/self_improvement/proposal_model.py`、`tools/self_improvement/carry_forward_register.py`、`tools/self_improvement/machine_verification.py` |
| XDI-CE-001 | conformance-evaluation | `ownership-unclear` | `carry_forward` | `requirements` | `.reviewcompass/specs/conformance-evaluation/requirements.md`、`.reviewcompass/specs/conformance-evaluation/design.md`、`docs/operations/CONFORMANCE_EVALUATION.md` | `tools/conformance_evaluation/check_mode.py`、`tools/conformance_evaluation/generation_mode.py`、`tests/conformance-evaluation/test_conformance_evaluation.py` |

### 2.2 drift item とクラスタ対応

| Drift item | Related clusters |
| --- | --- |
| XDI-FOUND-001 | XDRIFT-001、XDRIFT-002、XDRIFT-006 |
| XDI-RUNTIME-001 | XDRIFT-001、XDRIFT-003、XDRIFT-005、XDRIFT-006 |
| XDI-EVAL-001 | XDRIFT-002、XDRIFT-003、XDRIFT-006 |
| XDI-ANALYSIS-001 | XDRIFT-003、XDRIFT-005、XDRIFT-006 |
| XDI-WM-001 | XDRIFT-001、XDRIFT-002、XDRIFT-003、XDRIFT-004、XDRIFT-005、XDRIFT-006 |
| XDI-SI-001 | XDRIFT-001、XDRIFT-002、XDRIFT-004、XDRIFT-005 |
| XDI-CE-001 | XDRIFT-001、XDRIFT-003、XDRIFT-004、XDRIFT-007 |

## 3. 同根クラスタ

### XDRIFT-001: 実装テストが hidden spec になっている

多くの feature で、requirements / design よりも tests が最も具体的な契約を持っている。

代表例:

- `workflow-management`: post-write coverage matrix、review_run traceability、audit-commit、commit approval hash。
- `runtime`: manifest field count、state transition、validation bridge、bundle checksum。
- `evaluation`: admission / readiness / classifier / staleness の precise vocabulary。
- `self-improvement`: proposal id boundary、declined adoption phrase、superseded reopen fields。
- `conformance-evaluation`: CF-999 / CF-1000 boundary、MV6 prompt isolation、mode switch。

反映候補:

- tests を単なる検証ではなく「実装由来契約の証拠」として扱う。
- conformance-evaluation の出力候補として `source_kind: test | implementation | operation_doc | review_run` を記録する。
- stable external contract は requirements / design に戻し、内部境界値や helper 挙動は implementation-detail として残す。

### XDRIFT-002: 契約の正本所有者が曖昧になっている

同じ契約が requirements、design、operations、tests、review-run、workflow state に分散している。

代表例:

- review-wave で出た feature-local evidence pointer。
- evaluation review-run が `docs/notes/review-runs/` にあり、feature namespace には pointer が必要だった。
- workflow-management の post-write verification は operations / discipline / checker / tests にまたがる。
- analysis の intake destination は evaluation / conformance との境界契約でもある。
- self-improvement の carry-forward register は analysis / workflow-management と接続する。

反映候補:

- drift item ごとに `contract_owner` を付ける。
- 候補値は `requirements`、`design`、`operations`、`tool_contract`、`test_contract`、`review_evidence`、`carry_forward` とする。
- 所有者が決められない項目は `ownership-unclear` として一括判断する。

本メモでの初期適用は 2.1 の `Owner candidate` に記録した。これは未承認の候補であり、採用判断ではない。本メモでは `contract_owner` と書く場合も、採用済み所有者ではなく `owner_candidate` を意味する。

### XDRIFT-003: 証拠 traceability の形が feature ごとに違う

review-run、bundle、manifest、evidence register、carry-forward register は、どれも証拠追跡のための構造だが、feature ごとに形式が異なる。

代表例:

- workflow-management: raw / rounds / triage / summary / target-manifest / target-source-manifest。
- runtime: review_case、validation refs、bundle provenance。
- evaluation: bundle intake、admission record、metrics reports、diff reports。
- analysis: claim map、evidence register、caveat register、destination manifest。
- self-improvement: input provenance、proposal / verification / approval / rollback linkage。
- conformance-evaluation: evaluation record、related artifacts、materialization commit independence。

反映候補:

- conformance-evaluation の本格実装では、feature ごとの差分を直接比較する前に、共通の evidence ref model に正規化する余地がある。
- 少なくとも `path`、`lines`、`source_kind`、`contract_claim`、`confidence`、`owner_candidate` を出力する。

これは候補 schema であり、本メモの本文に完全適用したものではない。部分対応として、2.1 の `Contract refs` と `Code / test / evidence side` は `path` / `source_kind` の候補を表し、`Owner candidate` は `owner_candidate` の候補を表す。`lines`、`contract_claim`、`confidence` は本メモでは未付与である。

### XDRIFT-004: 人間判断と authorization が複数 feature に分散している

承認、却下、保留、proxy decision、commit approval、human review required が各 feature で別々に表現されている。

代表例:

- workflow-management: commit approval、proxy decision、post-write human decision required、autonomous execution approval。
- runtime: human signoff 4 values、absent vs deferral。
- self-improvement: explicit approval / rejection、declined adoption phrase、unverifiable user audit。
- conformance-evaluation: generated docs の `human_review_required: true`、triad review policy。
- evaluation: readiness / fatal / blocked / exploratory classification。

反映候補:

- human decision vocabulary の所有候補を foundation / workflow-management / feature-local extension として比較する。
- feature 固有の判断は拡張語彙として定義し、共通語彙との対応表を作る。

### XDRIFT-005: 非干渉・出力先境界の guard が横断的に増えている

アドホック機能追加により、出力先や読み取り境界を守る guard が増えた。これは品質上は良いが、仕様のどこに置くかが不明瞭になりやすい。

代表例:

- runtime: raw evidence immutable、derived separation。
- evaluation: bundle physical placement preserving run structure。
- analysis: runtime raw evidence を直接読まない、evaluation / conformance outputs を書かない。
- workflow-management: post-write pending 中の禁止混在。
- self-improvement: workflow-management route を通さない discipline direct write を fail-closed。
- conformance-evaluation: generation と check の mode separation、MV6 prompt isolation。

観測:

- feature 境界ルールは cross-feature contract として扱う余地がある。
- 現在の分類語彙では、境界違反と所有境界不明を `mismatch` または `ownership-unclear` のどちらに寄せるかが未分化である。
- この未分化自体は XDI-META-001 として 4 節に持ち越す。
- 影響を受ける可能性がある代表 item は XDI-ANALYSIS-001、XDI-WM-001、XDI-SI-001 である。

### XDRIFT-006: staleness / invalidation / recheck の lifecycle が分散している

review-wave で foundation recheck clearing が問題になったのと同様、staleness や invalidation の lifecycle は複数 feature にまたがる。

代表例:

- foundation: validator / invalidation marker schema。
- runtime: validation bridge、failure marker、revalidation refs。
- evaluation: staleness propagation、downstream artifacts。
- analysis: staleness register、dependency update。
- workflow-management: recheck clearing evidence、next action priority。

反映候補:

- `stale`、`invalid`、`analysis_blocked`、`recheck_pending`、`cleared` の共通 lifecycle を定義する。
- recheck clearing には証拠種別と人間承認の要否を明示する。

### XDRIFT-007: conformance-evaluation 自身の実装が、今回の手作業監査にまだ追いついていない

`tools/conformance_evaluation/check_mode.py` は two-stage isolation と evaluation record 出力を持つが、現状は criterion-1 の placeholder comparison に近い。`generation_mode.py` は human-reviewable な推定文書を生成するが、今回の監査で必要だった横断クラスタ化、所有者推定、証拠 refs の構造化までは出力しない。

これは欠点というより、本格実装の次のテストケースである。

観測:

- 現ツールは、手作業監査で必要になった横断クラスタ化、所有者推定、証拠 refs の構造化をまだ直接出力しない。
- 2.1 と 2.2 は、将来の自動化で必要になる可能性がある出力粒度を観測として示している。

## 4. 未採用の判断候補

本節は作業指示ではなく、後続で人間判断が必要な候補を記録する。

| ID | Judgment candidate | Owner candidate | Depends on |
| --- | --- | --- | --- |
| XDI-META-001 | 境界違反と所有境界不明を既存分類語彙のまま扱うか、別語彙として定義するか。 | `carry_forward` / `requirements` | none |
| XDI-META-002 | `contract ownership map` を別 artifact として作るか。 | `carry_forward` / `design` | XDI-META-001 |
| XDI-META-003 | conformance-evaluation の本格実装テストに、`workflow-management` 単体監査と本メモを fixture として使うか。 | `carry_forward` / `test_contract` | XDI-META-001、XDI-META-002、本文書の commit / approval 完了 |
| XDI-META-004 | hidden spec 化しているテスト契約を feature ごとに仕分けるか。 | `carry_forward` / `test_contract` | XDI-META-002 |
| XDI-META-005 | stable external contract だけを requirements / design に戻すか。 | `carry_forward` / `requirements` | XDI-META-002、XDI-META-004 |
| XDI-META-006 | implementation-detail と判定したものを tool contract / test contract として記録するか。 | `carry_forward` / `tool_contract` | XDI-META-002、XDI-META-004 |

## 5. 後続 fixture 候補

本節も作業指示ではなく、今回の手作業監査を将来の自動化テストへ転用する場合の候補を記録する。

- 入力候補: `workflow-management` 単体監査メモ。
- 入力候補: 本メモの 2.1 代表 drift item 表。
- 入力候補: 本メモの XDRIFT-001 から XDRIFT-007。
- 出力候補 field: `feature`、`contract_id`、`claim`、`source_refs`、`source_kind`、`classification`、`owner_candidate`、`related_cluster`、`confidence`。
