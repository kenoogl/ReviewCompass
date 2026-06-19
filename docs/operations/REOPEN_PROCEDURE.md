# REOPEN_PROCEDURE：再オープン手続きの運用手順

最終更新：2026-06-10（現行の運用手順として更新）

## 0. 位置づけ

本文書は ReviewCompass の再オープン手続き（やり直し）を実行可能な手順にした運用文書である。運用時は本文書を手順の入口とし、形式的な契約は [workflow-management design](../../.reviewcompass/specs/workflow-management/design.md)、[workflow-management tasks](../../.reviewcompass/specs/workflow-management/tasks.md)、および [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md) の reopen 関連記述と整合させる。

本手順は、現在の 5 段ワークフロー（drafting → triad-review → review-wave → alignment → approval）を前提とする。

## 1. いつ使うか

下流の段（triad-review／review-wave／alignment／approval）で、上流フェーズ（過去フェーズ）の修正が必要な「遡及（そきゅう）所見」を発見したとき。同じフェーズの他機能への影響（波及）は機能横断段（review-wave）で扱い、本手続きの対象外。所見の波及種別の判断は [SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md) を参照する。

## 2. 4 過程の実行手順

再オープン手続きは 4 過程で扱う。各過程は「停止せず連続実行できる作業の単位」で、人の承認点または commit 停止点で締める。

### 第1過程：判定とフラグ差し戻し（actor=llm、自律で連続実行）

1. 遡及所見を発見し、下流の作業を停止する
2. 手戻り種別を判定する（N／R／D／A／I × 深さ）
3. 上流変更を既存 feature の責務境界へ写像し、feature impact を判定する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で行う
   - 既存 feature に受け皿がある場合：該当 feature ごとに `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only` のいずれかを判定する
   - 既存 feature に受け皿がない場合：`new_feature_required` として新 feature 候補を作る
   - 判定の主軸は、文書内の挿入箇所ではなく、実装上の所有責務である。変更が実装責務または契約正本を変え得る feature は direct impact として扱い、出力を読むだけ、派生物を作るだけ、手続きを確認するだけの feature は indirect check として扱う
   - 各 feature impact 判定には `impact_basis` を記録する。値は `implementation_ownership`、`contract_ownership`、`consumer_or_derivative_only`、`no_implementation_impact`、`new_feature_boundary` のいずれかとする
   - 判定が重要、曖昧、広範囲の場合は 3 役レビューに送る
4. trigger_map で再実施対象の段を決定する（依存順＝`feature-dependency.yaml#feature_order`。旧称 phase_order）
5. 種別判定と feature impact 判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に記録する。形式は既存の `docs/reviews/reopen-classification-*.md` の記録例に合わせる
6. 進行中状態ファイル `stages/in-progress/reopen-procedure-<日付>.yaml` を発行する
7. spec.json のフラグを差し戻す：
   - 上流：`reopened.<上流>=true`、上流の修正対象段（alignment／approval）を `false` に
   - 下流：`recheck.upstream_change_pending=true`、`impacted_downstream_phases` に下流確認対象を列挙する。下流段を `false` に戻すか、完了扱いのまま影響なし／間接確認のみとするかは feature impact 判定と下流影響判定で決める
   - 上流段を `false` に戻しても、同フェーズ後段または下流フェーズ段を機械的にすべて `false` にする必要はない。ただし完了 commit までに、残した段を含む feature impact 判定と下流影響判定を手続き記録へ明示する
   - 複数段を実際に差し戻す場合は、下流側から上流側へ `false` にすると作業状態を読みやすい。影響なしと判定した段は `true` のまま残してよい
   - `recheck.upstream_change_pending=true` または空でない `impacted_downstream_phases` を含む `spec.json` 変更は、対応する `stages/in-progress/reopen-procedure-*.yaml` と同じ停止点 commit に含める

→ **停止点：フラグ差し戻しの内容（手戻り種別・再実施範囲・差し戻し）を人が承認する**（この時点ではコミットしない）

### 第2過程：正本修正（actor=human または llm）

8. 上流フェーズの正本（仕様文書の該当箇所）を修正する

→ **停止点：コミット**（第1過程のフラグ差し戻しと本過程の正本修正をまとめて 1 コミット）

### 第3過程：連鎖再実施（依存順、各 approval で停止）

9. 依存順に上流 → 下流の各フェーズで：
   - `pending_gates` は review 系 gate（triad-review／review-wave／alignment／approval）の処理順を表す。phase の正本本文を更新する必要があり、先頭 gate が triad-review の場合、triad-review の前に drafting を実施する。drafting 完了後は `drafting_completed_gates` に `stages/<phase>.yaml#drafting` を記録し、その後に triad-review へ進む
   - 正本本文（`.reviewcompass/specs/<feature>/<phase>.md`）を実質修正した phase は、triad-review → review-wave → alignment → approval の順に再実施する。これは requirements／design／tasks／implementation のいずれでも同じ
   - 正本本文を修正していない phase は、trigger_map の pending gate に従って alignment（整合チェック）から再確認してよい
   - 上流変更に対する下流影響判定を `downstream_impact_decisions` に記録する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で必須とする
   - 「既存で受けられる」「修正不要」と判断する場合も、判定対象 gate、feature 範囲、判断、理由、証跡を記録する。修正不要は reopen を省略する理由ではなく、reopen 後の影響判定結果としてのみ扱う
   - 波及あり → triad-review に戻して対処（機能内対処または機能横断段へ）
   - 波及なし → approval へ
   - approval は人の承認（actor=human または proxy_model）

→ **停止点：各フェーズの approval（人の承認）。全フェーズ完了後にコミット**

### 第4過程：完了（連続実行）

10. 整合性の最終確認（上流の変更が下流に正しく伝わったか）
11. `reopen-finalize` で recheck をクリアする（`upstream_change_pending=false`、`impacted_downstream_phases=[]`）、第4過程完了履歴を追加する、進行中状態ファイルを `stages/completed/` へ移動する、の 3 点を一括で行う。`reopened.<上流>` は `true` のまま残す（履歴）。

→ **停止点：コミット**

第4過程の完了 commit では、`stages/completed/reopen-procedure-*.yaml` に `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` と、`pending_gates` の各 gate を覆う `downstream_impact_decisions` が必要である。`feature_impact_decisions` は、既存 feature ごとに `feature`、`decision`、`impact_basis`、`rationale`、`evidence` を持つ。`decision` は `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only`、`new_feature_required` のいずれかとする。`impact_basis` は `implementation_ownership`、`contract_ownership`、`consumer_or_derivative_only`、`no_implementation_impact`、`new_feature_boundary` のいずれかとする。`new_feature_decision.decision` は `no_new_feature` または `new_feature_required` とする。`downstream_impact_decisions` の各判定は最低限、`gate`、`feature_scope`、`decision`、`rationale`、`evidence` を持つ。`decision` は `affected_update_required`、`existing_sufficient`、`no_impact`、`approved`、`proxy_approved` のいずれかとする。`impacted_downstream_phases` に列挙した各フェーズには、対応する `downstream_impact_decisions[].gate` を少なくとも 1 件記録する。完了 commit に正本本文の変更が含まれる phase は、`pending_gates` に triad-review／review-wave／alignment／approval をすべて含め、drafting を実施した phase は `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` を含める。

## 3. 手戻り種別と trigger_map

種別記号は N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ（どこまで上流に戻るか）で表す。trigger_map（全 15 種）は種別から再実施対象段を返す。trigger_map の alignment／approval-only は、該当 phase の正本本文を修正しない再確認に限る。正本本文を修正した phase は、その phase の triad-review／review-wave／alignment／approval を再実施対象に加える。

## 4. 状態遷移の早見表

| 発見した問題 | 修正フェーズ | 主なアクション |
|---|---|---|
| 要件の問題 | requirements | requirements を修正 → 下流（design／tasks／implementation）を reopen 対象に → 依存順に連鎖再実施 |
| 設計の問題 | design | design を修正 → 下流（tasks／implementation）を reopen 対象に → 連鎖再実施 |
| タスクの問題 | tasks | tasks を修正 → 下流（implementation）を reopen 対象に → 連鎖再実施 |
| 意図の問題 | intent | intent を修正 → 全機能の下流（requirements 以降）を reopen 対象に → 連鎖再実施 |

本表は代表例である。実際の再実施対象は、手戻り種別、trigger_map、正本本文を修正した phase、feature impact 判定、下流影響判定を合わせて決める。

## 5. spec.json の更新

`reopened` は 6 フェーズ（intent／feature-partitioning／requirements／design／tasks／implementation）を対象とする。intent と feature-partitioning は機能横断段のため、これらの `reopened` は全機能で同じ値になる。commit 時には [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md#commit) の reopen 検査により、recheck 印付き spec.json と reopen 手続き記録の対応、完了時の feature impact 判定、下流影響判定、影響フェーズ網羅が確認される。

## 6. 記録の確実性について

本手続きの各ステップを LLM が忘れず実行する保証はない（ワークフロー記録全般が持つ脆さ）。本手続きでは、第1過程の承認、各 commit、各 approval を停止点として人の確認を挟む。また、`tools/check-workflow-action.py` の `reopen-start`、`spec-set`、`commit`、`next` の各判定で、記録漏れや手順逸脱を検出可能にする。

## 7. 関連参照

- [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md)（reopen-start と commit 前検査の運用契約）
- [WORKFLOW_PRECHECK_DETAILS.md](WORKFLOW_PRECHECK_DETAILS.md)（reopen 関連の commit 検査詳細）
- [WORKFLOW_NAVIGATION.md](WORKFLOW_NAVIGATION.md)（`reopen_in_progress`、`reopen_classification_required`、`stage` の読み方）
- [SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md)（所見提示、判断停止、作業完了時報告の運用）
- [workflow-management design](../../.reviewcompass/specs/workflow-management/design.md)（reopen 機械強制モデル、後追い intent の下流再展開モデル）
- [workflow-management tasks](../../.reviewcompass/specs/workflow-management/tasks.md)（T-007、T-008、XDI-WM-002）
- `tools/check-workflow-action.py`（`reopen-start`、`spec-set`、`commit`、`next` の実装）
