# Main Preanalysis: workflow-management design reopen protocol review

作成日: 2026-07-01
対象 gate: `stages/design.yaml#triad-review`
現在状態: `next --json` は `triad_review_protocol.state=main_preanalysis_required`
位置づけ: 実 review-run 前の main preanalysis。これは reviewer への正解ではなく、source selection と判断項目の仮説である。

全 claim 共通の欠落扱い: named target section が存在しない、名称変更で対応箇所を特定できない、または必要な設計責務が別節にも見つからない場合は、vacuous pass とせず finding 候補として扱う。

## Review Requirement

今回の triad-review は、`workflow-management` の `design.md` を対象に、requirements Requirement 5 受入 7 で確定した reopen protocol mechanization 契約が、設計層へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを確認する。

最低限の問いは次である。

- `requirements.md` の edited phase / downstream impact / fail-closed / superseding reopen 契約が、`design.md` の reopen 機械強制モデルへ設計として落ちているか。
- `design.md` の審査対象は design 本文であり、tasks / implementation の correctness はこの gate の対象外である。
- behavior-path claim を含むため、文書だけでなく `next --json`、`reopen-finalize`、commit preflight、関連 runner / tests を source material 候補に含める。
- review-run、proxy_model、`spec.json` 更新、phase/gate 完了、commit、push はこの preanalysis の範囲外であり、ここでは実行しない。

## Materials Read

### Target

- `.reviewcompass/specs/workflow-management/design.md`
  - §reopen 機械強制モデル §5: 第3過程の pending / completed / required gates、`edited_phases` の full gate chain、`impacted_downstream_phases` の downstream impact decision、検出順。
  - §session 跨ぎ状態管理モデル §1: `drafting_completed_gates`、`active_reopen_scope`、`active_impact_review_scope`、`downstream_impact_decisions`。
  - §Req 12 設計モデル §11: reopen scope / impact review scope と next state uniqueness。
  - §Req 16 設計モデル §2: active reopen scope と impact review scope。
  - §review-run 後の proxy_model 判断代行モデル: proxy_model と human-only 操作の境界。
  - §Req 14 設計モデル §1〜3: approval gate record、human-only predicate、proxy apply の停止条件。

### Source Materials

- `.reviewcompass/specs/workflow-management/requirements.md`
  - Requirement 5 受入 7: `edited_phases`、`impacted_downstream_phases`、`downstream_impact_decisions`、edited phase の full gate、`next --json` / `reopen-finalize` / commit preflight fail-closed、superseding reopen record。
  - Requirement 12 受入 13〜14: `next --json` の reopen 出力契約、active gate / required action / reopen scope / impact review scope / pending gates / completed gates / state refs、一意 action selector、preflight が `next --json` を複製しない規則。
  - Requirement 14 受入 11: proxy_model は commit / push / `spec.json` 更新 / phase approval / reopen finalize / approval_required な不可逆操作の許可を代行しない。
  - Requirement 16 受入 11〜14: active reopen scope と impact review scope、consumer / derivative feature scope、proxy_model 適用境界、human-required predicate。
- `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`
  - 問題: requirements を実質修正した reopen が requirements triad-review / review-wave を再実行せず finalize され、下流 design/tasks/implementation 影響が通常の reopen 連鎖ではなく補足メタデータ扱いになった。
  - invariants: `edited_phases`、full review gates、`impacted_downstream_phases`、`downstream_impact_decisions`、`next --json` / `reopen-finalize` / commit preflight の fail-closed。criteria draft では、この plan は path-only 参照にせず、必要な excerpt を source material に埋め込む。
- `stages/in-progress/reopen-procedure-2026-07-01.yaml`
  - 現在の active state: `classification=R-0`、`edited_phases=[requirements]`、`impacted_downstream_phases=[design,tasks,implementation]`。
  - design drafting は完了し、次 gate は `stages/design.yaml#triad-review`。
  - `drafting_completed_gates` は `stages/requirements.yaml#drafting` と `stages/design.yaml#drafting`。
- `.reviewcompass/specs/workflow-management/spec.json`
  - requirements approval は完了済み。
  - design/tasks/implementation は drafting から approval まで false。
  - `recheck.upstream_change_pending=true`、`impacted_downstream_phases=[design,tasks,implementation]`。
- `.reviewcompass/guidance/REOPEN_PROCEDURE.md`
  - 正本本文を実質修正した phase は triad-review→review-wave→alignment→approval を再実施する。
  - 下流影響判定は requirements / design / tasks / implementation のいずれでも必須。
  - 修正不要でも gate、feature scope、判断、理由、証跡を `downstream_impact_decisions` に記録する。
- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`
  - design review は requirements.md から design.md への引き継ぎを確認する。
  - tasks.md / implementation は参照文脈になり得るが、correctness target ではない。
  - source materials は path-only 禁止で、目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分ける。
- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
  - main preanalysis、preanalysis sufficiency audit、criteria draft、prompt quality review、実 review-run の順序。
  - behavior-path claim では runner / guard / preflight / tests を source に含める。
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
  - prompt 作成前に main LLM が材料揃えを行い、claim ごとの target / source / out of scope、必要抜粋、未読、推測、機微情報リスクを分ける。
- `tools/check-workflow-action.py`
  - edited phase と downstream phase から必須 gate / downstream decision を算出する関数群。
  - `next --json`、`reopen-finalize`、commit preflight が不足検出面になる。
  - ただし、この code/test material は behavior-path の補助文脈であり、design.md が満たすべき規範は requirements.md / REOPEN_PROCEDURE.md / workflow guidance である。現在実装の correctness は design triad-review の審査対象ではない。
- `tests/tools/test_check_workflow_action.py`
  - behavior-path の補助文脈として存在を確認する。テスト本文・現在実装の correctness は design review の審査対象ではない。

## Claim Decomposition

### Claim 1: requirements-to-design vertical transfer

- Claim: `design.md` は Requirement 5 受入 7 の目的・責務境界・受入条件・禁止事項を、reopen 機械強制モデルに設計として引き継いでいるか。
- Target: `design.md` §reopen 機械強制モデル §5。
- Source: `requirements.md` Requirement 5 受入 7、plan invariants、REOPEN_PROCEDURE。
- Out of scope: tasks.md / implementation code の正しさ。
- Finding condition: requirements の義務が設計から欠落する、または設計が requirements より弱い。

### Claim 2: edited phase full gate chain

- Claim: `edited_phases` に含まれる phase は trigger_map の最小 gate ではなく full gate chain を必須にする、と design が定めているか。
- Target: `design.md` §reopen 機械強制モデル §5。
- Source: Requirement 5 受入 7、current reopen state、plan invariants RPMR-I1/I2。
- Out of scope: 現在の implementation が完全に full gate chain を検査しているかの判定。
- Finding condition: edited phase が alignment / approval だけで足りるように読める。

### Claim 3: downstream impact decision evidence

- Claim: `impacted_downstream_phases` について、変更不要時も `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を持つ decision record が必要だと design が定めているか。
- Target: `design.md` §reopen 機械強制モデル §5、§session 跨ぎ状態管理モデル §1、§Req 12 設計モデル §11、§Req 16 設計モデル §2。
- Source: Requirement 5 受入 7、Requirement 16 受入 11〜12、REOPEN_PROCEDURE。
- Out of scope: design/tasks/implementation の downstream 正本文そのものの十分性。
- Finding condition: no-impact / existing-sufficient の証跡義務が省略可能に読める、または feature scope が active reopen scope / impact review scope と矛盾する。

### Claim 4: fail-closed surface order

- Claim: 不足検出の通常経路は `next --json`、完了直前は `reopen-finalize`、最後の保険は commit preflight であり、commit preflight を初検出点にしない設計になっているか。
- Target: `design.md` §reopen 機械強制モデル §5、§Req 12 設計モデル §11。
- Source: Requirement 5 受入 7、REOPEN_PROCEDURE 第3〜4過程。
- Supporting context only: behavior-path source summary。code/test path は provenance hint であり、criteria に excerpt を埋め込まない限り、現在実装の挙動を規範 source として扱わない。
- Out of scope: 個々の関数のコードレビュー、現在実装が requirements を満たすかの correctness 判定。
- Finding condition: commit preflight だけでよいように読める、または `next --json` / `reopen-finalize` の検出責務が曖昧。

### Claim 5: superseding reopen policy

- Claim: push 済みの不完全 completed reopen は履歴改変ではなく superseding reopen record として扱い、同じ full gate chain を満たす設計になっているか。
- Target: `design.md` §reopen 機械強制モデル §5。
- Source: Requirement 5 受入 7、plan RPMR-Q3 as historical planning context superseded by Requirement 5 acceptance 7、current reopen trigger。
- Out of scope: 過去 completed reopen record の内容修正。
- Finding condition: 履歴改変を許す、superseding 理由が記録されない、または superseding reopen では full gate chain が不要に見える。

### Claim 6: review target boundary

- Claim: design triad-review の prompt は design.md を target とし、tasks / implementation correctness を out of scope にできるか。
- Target: `design.md` と review prompt requirement。
- Source: SESSION_WORKFLOW_GUIDE vertical intent transfer、requirements.md。
- Out of scope: tasks.md / implementation の正しさ。
- Finding condition: design review が tasks / implementation correctness まで同時に判定する形になり、対象が広がりすぎる。

### Claim 7: next --json reopen output and preflight boundary

- Claim: `design.md` は Requirement 12 受入 13〜14 の `next --json` reopen 出力契約を設計として引き継いでいるか。具体的には required action、active gate、phase/stage、reopen scope、impact review scope、direct/indirect features、flag policy、pending/completed gates、state refs を LLM の文脈解釈ではなく機械可読 state から一意に出し、operation preflight はそれを複製せず参照する、という境界である。
- Target: `design.md` §Req 12 設計モデル §11、§軽量版検査スクリプトモデル §4〜5、§session 跨ぎ状態管理モデル §1。
- Source: Requirement 12 受入 13〜14、Requirement 5 受入 7、Requirement 16 受入 11〜12。
- Out of scope: `next --json` 実装コードの correctness 判定。
- Finding condition: output field list が欠落する、scope / gate / state refs の一意性が曖昧、reopen scope / impact review scope が欠落・矛盾・stale な場合に `OK` ではなく `WARN` または `DEVIATION` で停止する条件が欠落する、または preflight が `next --json` を複製・再選択できるように読める。

### Claim 8: proxy_model and human-only authorization boundary

- Claim: `design.md` は proxy_model を review-run 後の重要件判断・triage 補助に限定し、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize、approval_required な不可逆操作の実行許可を human-only として扱う境界を設計しているか。加えて、human-only decision 境界、未解決 approval gate、`approval_required: true` operation、未解決 review-wave impact evidence が proxy applicability より優先され、triage leave-as-is や proxy approved が human-required 証跡を打ち消さない優先順位を設計しているか。
- Target: `design.md` §review-run 後の proxy_model 判断代行モデル、§Req 14 設計モデル §1〜3。該当箇所が存在しない場合は、欠落を finding 候補として扱う。
- Source: Requirement 14 受入 11、Requirement 16 受入 13〜14、SESSION_WORKFLOW_GUIDE §3.3(a-2)。
- Out of scope: proxy_model 実装コードの correctness、個別 finding の採否。
- Finding condition: proxy_model が human-only operation を許可できるように読める、human-required predicate の優先順位や競合解決が欠落する、または human-only override / approval gate record / operation contract との関係が設計から欠落する。

## Proposed Prompt Split

実 review-run は 1 prompt とする案が妥当である。理由は、全 claim の target が `design.md` であり、問いは requirements / guidance から design への transfer に統一されるためである。ただし、この判断は preanalysis sufficiency audit の確認を経て criteria draft に反映する。

ただし criteria draft では、Claim 4 の behavior-path source を「実装 correctness の審査材料」ではなく「requirements が求める検出面を設計が明示しているかを確認する補助文脈」と明記する。tool / test の現在挙動を規範として扱ってはならない。この境界を criteria に明記できない場合だけ、behavior-path design sufficiency を別 prompt に分割する。

## Model-Readable Source Material Needed For Criteria

criteria draft には path だけでなく、少なくとも次の structured excerpts を含める。

- target excerpt: `design.md` §reopen 機械強制モデル §5、§session 跨ぎ状態管理モデル §1 の関連行、§Req 12 設計モデル §11、§Req 16 設計モデル §2、§review-run 後の proxy_model 判断代行モデル、§Req 14 設計モデル §1〜3。
- requirements excerpt: Requirement 5 受入 7、Requirement 12 受入 13〜14、Requirement 14 受入 11、Requirement 16 受入 11〜14。
- plan excerpt: 旧 reopen の問題点、RPMR-I1〜I7、RPMR-Q3。path-only にせず、criteria 用 source material へ必要本文を埋め込む。
- current reopen state summary: classification、edited phase、completed requirements gates、design drafting completed gate、pending design/tasks/implementation gates。
- guidance excerpt: REOPEN_PROCEDURE 第3〜4過程、SESSION_WORKFLOW_GUIDE vertical review、SESSION_WORKFLOW_GUIDE §3.3(a-2)、API_REVIEW_PROMPT_QUALITY behavior-path rule。
- behavior-path source summary: runner functions and tests listed above, explicitly without asking reviewer to judge implementation correctness. code/test excerpt を criteria に埋め込まない場合、reviewer はこれらの path を参照必須にしてはならず、finding は requirements / guidance に基づく設計上の不足だけに限定する。

## Sensitive Information / Minimization

- API keys、tokens、password、nonce は見つけていない。
- 個人情報は source material に含めない。
- review-run criteria には会話ログ全文を入れない。利用者判断は plan / reopen state / guidance の構造化要約に絞る。
- raw review artifacts from old review-runs are not needed for this preanalysis unless prompt quality audit later requires comparison with stale prior runs.

## Unread / Open / Assumptions

- 未読: 古い completed reopen record 本文。今回の design review requirement は superseding policy の設計化であり、過去記録の再審査は target ではないため、criteria draft では必要になった場合だけ source に追加する。
- 未読: implementation の詳細コード全体。behavior-path source summary に必要な関数・テスト名は把握したが、design review ではコード correctness は out of scope。
- resolved: 実 review-run は 1 prompt とする。ただし behavior-path claim は補助文脈に限定し、実装 correctness を審査対象にしないことを criteria に明記する。
- assumption: review-run の variant / role assignment はまだ未確定。criteria draft 以降で確定するまで実 review-run は開始しない。

## Next Step

次は preanalysis sufficiency audit。main preanalysis を正解として扱わず、source materials から材料選定・判断項目・source selection が足りているかを監査する。
