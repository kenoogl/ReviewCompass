# Main Preanalysis：workflow-management requirements reopen protocol review

作成日: 2026-07-01
対象 gate: `stages/requirements.yaml#triad-review`
現在状態: `next --json` は `triad_review_protocol.state=main_preanalysis_required`
位置づけ: 実 review-run 前の main preanalysis。これは reviewer への正解ではなく、source selection と判断項目の仮説である。

## Review Requirement

今回の triad-review は、`workflow-management` の `requirements.md` を対象に、reopen protocol mechanization review の要求が requirements に正しく落ちているかを確認する。

最低限の問いは次である。

- 上流判断材料、reopen 分類、利用者判断、計画メモの目的・責務境界・受入条件・禁止事項が、`requirements.md` へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
- `requirements.md` の審査対象は requirements 本文であり、design / tasks / implementation の correctness はこの gate の対象外である。
- `next --json`、`reopen-finalize`、commit preflight などの behavior-path claim を含むため、文書だけでなく runner / guard / tests も source material 候補に含める。
- review-run、proxy_model、`spec.json` 更新、phase/gate 完了、commit、push はこの preanalysis の範囲外であり、ここでは実行しない。

## Materials Read

### Target

- `.reviewcompass/specs/workflow-management/requirements.md`
  - Requirement 5 受入 7: `edited_phases`、`impacted_downstream_phases`、`downstream_impact_decisions`、edited phase の full gate、fail-closed、superseding reopen record。
  - Requirement 16 受入 11〜14: active reopen scope と `spec.json.reopened` の区別、他 feature consumer / derivative 影響、proxy_model 適用可否、human-required predicate。
  - Requirement 3 受入 5: proxy_model は重要件判断だけを代行し、commit / push / `spec.json` 更新 / phase 移行を代行しない。
  - Requirement 2 受入 9/13 と Requirement 9 受入 3/5 は関連する target 内文脈だが、実 review-run では `requirements.md` 全体が target として渡される。source material としては扱わない。

### Source Materials

- `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`
  - 問題: requirements を実質修正した reopen が requirements triad-review / review-wave を再実行せず finalize され、下流 design/tasks/implementation 影響が通常の reopen 連鎖ではなく補足メタデータ扱いになった。
  - invariants: `edited_phases`、full review gates、`impacted_downstream_phases`、`downstream_impact_decisions`、`next --json` / `reopen-finalize` / commit preflight の fail-closed。
- `stages/in-progress/reopen-procedure-2026-07-01.yaml`
  - 現在の active state: `classification=R-0`、`edited_phases=[requirements]`、`impacted_downstream_phases=[design,tasks,implementation]`、pending gates は requirements/design/tasks/implementation の triad-review→review-wave→alignment→approval。
  - `drafting_completed_gates` は `stages/requirements.yaml#drafting`。
- `.reviewcompass/specs/workflow-management/spec.json`
  - requirements は `drafting=true`、`triad-review/review-wave/alignment/approval=false`。
  - design/tasks/implementation は drafting から approval まで false。
  - `recheck.upstream_change_pending=true`、`impacted_downstream_phases=[design,tasks,implementation]`。
- `.reviewcompass/guidance/REOPEN_PROCEDURE.md`
  - 正本本文を実質修正した phase は triad-review→review-wave→alignment→approval を再実施する。
  - 下流影響判定は intent に限らず feature-partitioning / requirements / design / tasks / implementation のいずれでも必須。
  - 修正不要でも gate、feature scope、判断、理由、証跡を `downstream_impact_decisions` に記録する。
- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`
  - requirements review は「上流判断材料 → requirements.md」を確認する。
  - design.md / tasks.md は参照資料であり、審査対象ではない。
  - source materials は path-only 禁止で、目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分ける。
- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2`
  - review-run 後、proxy_model 判断依頼、実装修正、`spec.json` 更新、フェーズ移行の前に利用者提示 gate で停止する。
  - proxy_model は重要件判断だけを扱い、不可逆操作を代行しない。
- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
  - main preanalysis、preanalysis sufficiency audit、criteria draft、prompt quality review、実 review-run の順序。
  - behavior-path claim では runner / guard / preflight / tests を source に含める。
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
  - prompt 作成前に main LLM が材料揃えを行い、claim ごとの target / source / out of scope、必要抜粋、未読、推測、機微情報リスクを分ける。
- `tools/check-workflow-action.py`
  - `_required_downstream_impact_phases_for_edited_phases` は edited phase から下流 phase を動的算出する。
  - `_gate_chain_for_edited_phases_and_downstream` は edited phase と full reopen downstream を full gate に展開する。
  - `_reopen_downstream_impact_action` は downstream decision 不足時に `record_reopen_downstream_impact_decision` を返す。
  - `_validate_reopen_finalize_downstream_impact_decisions` は impacted downstream phase に対応する decision 不足を拒否する。
- `tests/tools/test_check_workflow_action.py`
  - `test_reopen_start_initializes_edited_phase_downstream_scope`
  - `test_reopen_start_design_edit_uses_full_reopen_gates_without_impact_only_chain`
  - `test_reopen_start_false_scope_follows_dynamic_downstream_phase`
  - `test_reopen_finalize_rejects_impacted_downstream_phases_without_decisions`

## Claim Decomposition

### Claim 1: edited phase の full gate requirement

- Claim: `requirements.md` は、実質編集された phase が triad-review / review-wave / alignment / approval の全 gate を再実施する必要を十分に要求しているか。
- Target: Requirement 5 受入 7。
- Source: plan invariants RPMR-I1/I2、REOPEN_PROCEDURE 第3過程、current reopen state pending gates。
- Out of scope: 実装が完全に正しいかの判定。実装は source として参照するが、この review の合否対象は requirements 本文。
- Finding condition: edited phase が alignment/approval だけで足りる余地を残す、drafting 完了記録との接続が曖昧、または full gate の対象 phase が requirements に限定される。

### Claim 2: downstream impact decision requirement

- Claim: `requirements.md` は、上流 phase 編集後の下流 phase について、変更不要の場合も gate / feature scope / decision / rationale / evidence を持つ decision record を必須にしているか。
- Target: Requirement 5 受入 7、Requirement 16 受入 11/12。Requirement 9 受入 3/5 は同じ target document 内の関連文脈であり、source material ではない。
- Source: plan invariants RPMR-I3/I4、REOPEN_PROCEDURE 第3過程、current `spec.json.recheck`、current `stages/in-progress/reopen-procedure-2026-07-01.yaml`。
- Out of scope: design/tasks/implementation の本文が現時点で十分かどうか。
- Finding condition: downstream impact decision が finalize 直前の補足で足りるように読める、変更不要時の証跡義務が弱い、または impact review scope と active reopen scope が混同される。

### Claim 3: fail-closed surfaces

- Claim: `requirements.md` は不足検出地点を `next --json`、`reopen-finalize`、commit preflight に分散し、commit だけを初検出地点にしないことを要求しているか。
- Target: Requirement 5 受入 7。Requirement 2 受入 9/13 は同じ target document 内の関連文脈であり、source material ではない。
- Source: plan invariants RPMR-I5/I6/I7、runner functions、related tests。
- Out of scope: 各 runner の詳細実装の完全性。ただし behavior-path claim の source selection として runner/test は必要。
- Finding condition: `next --json` または `reopen-finalize` の fail-closed が requirements から読めない、または commit preflight だけでよいように読める。

### Claim 4: superseding reopen record policy

- Claim: `requirements.md` は、既存 completed reopen に手続き不備がある場合、履歴改変ではなく superseding reopen record として扱う方針を要求しているか。
- Target: Requirement 5 受入 7。
- Source: plan question RPMR-Q3、current reopen trigger、REOPEN_PROCEDURE の履歴保持方針。
- Out of scope: 過去 completed reopen の修正実施。
- Finding condition: push 済み completed record の扱いが未定義、履歴改変を許すように読める、または supersede 理由の記録義務がない。

### Claim 5: proxy_model / human-only boundary

- Claim: `requirements.md` は、proxy_model が重要件判断だけを扱い、commit / push / `spec.json` 更新 / phase 移行を代行しない境界を維持しているか。
- Target: Requirement 3 受入 5、Requirement 16 受入 13/14。
- Source: SESSION_WORKFLOW_GUIDE 3.3-a-2、API_REVIEW_PROMPT_QUALITY、今回実装された protocol runner の blocked operations。
- Out of scope: 実際の proxy_model decision の生成、採否判断、実装修正。
- Finding condition: proxy_model decision が gate 完了、spec 更新、phase 移行、commit/push の承認として読める余地を残す。

### Claim 6: review scope boundary

- Claim: requirements triad-review の prompt は requirements.md を target とし、design/tasks/implementation correctness を out of scope にできるか。
- Target: SESSION_WORKFLOW_GUIDE vertical intent transfer と Requirement 5/16 の requirements 文。
- Source: current next required inputs、plan、REOPEN_PROCEDURE。
- Out of scope: downstream document correctness。ただし downstream が影響対象であることと、後続 gate が必要であることは scope 内。
- Finding condition: requirements review が downstream correctness まで同時に判定する形になり、対象が広がりすぎる。

## Proposed Prompt Split

現時点では、実 review-run は 1 prompt で足りる可能性が高い。ただし required checks は上記 6 claim に分ける。理由は、判断対象が同一 target (`requirements.md`) であり、source materials も同一の reopen protocol / current state / guidance / runner-test excerpts に集約できるため。

prompt quality review で「behavior-path claim と requirements 文書品質 claim を分けるべき」と判断された場合は、次の 2 prompt に分割する。

1. Requirements vertical transfer: plan / user decisions / reopen procedure から Requirement 5/16 への写像。
2. Behavior-path contract sufficiency: `next --json`、`reopen-finalize`、commit preflight、proxy boundary の fail-closed surfaces が requirements として十分に表現されているか。

## Model-Readable Source Material Needed For Criteria

criteria draft には path だけでなく、少なくとも次の structured excerpts を含める。

- plan summary: 旧 reopen の問題点、RPMR-I1〜I7、RPMR-Q3、mechanization gaps RPMR-G1〜G4。
- current reopen state summary: classification、edited phase、pending gates、drafting completed gate、downstream phases。
- current workflow state summary: requirements false gates、downstream false gates、recheck。
- target excerpt: Requirement 5 受入 7、Requirement 16 受入 11〜14、Requirement 3 受入 5。
- guidance summary: REOPEN_PROCEDURE 第3過程、SESSION_WORKFLOW_GUIDE vertical review、API_REVIEW_PROMPT_QUALITY behavior-path rule。
- behavior-path source summary: runner functions and tests listed above, without asking reviewer to judge implementation correctness.

## Sensitive Information / Minimization

- API keys、tokens、password、nonce は見つけていない。
- 個人情報は source material に含めない。
- review-run criteria には会話ログ全文を入れない。利用者判断は plan / reopen state / guidance の構造化要約に絞る。
- raw review artifacts from old review-runs are not needed for this preanalysis unless prompt quality audit later requires comparison with stale prior runs.

## Unread / Open / Assumptions

- 未読: 古い completed reopen record 本文。今回の review requirement は superseding policy の要件化であり、過去記録の再審査は target ではないため、criteria draft では必要になった場合だけ source に追加する。
- 未読: 全 design/tasks/implementation 本文。requirements review では downstream correctness は out of scope のため、現時点では必要最小限の関連節だけで足りる。
- open: prompt を 1 本にするか、behavior-path claim を分割するかは preanalysis sufficiency audit と prompt quality review で確認する。
- assumption: review-run の variant / role assignment はまだ未確定。criteria draft 以降で確定するまで実 review-run は開始しない。

## Next Step

次は preanalysis sufficiency audit。main preanalysis を正解として扱わず、source materials から材料選定・判断項目・source selection が足りているかを監査する。
