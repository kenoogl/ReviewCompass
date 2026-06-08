# REOPEN_PROCEDURE：再オープン手続きの運用手順

最終更新：2026-05-28（セッション 37 新設、暫定版）

## 0. 位置づけ

本文書は ReviewCompass の再オープン手続き（やり直し）を実行可能な手順にした運用文書である。正本は計画書 `docs/plan/reconstruction-plan-2026-05-21.md` の §5.6（手戻り種別・trigger_map・4 過程構成）と §5.24（spec.json の recheck／reopened 運用）。本文書はそれらを実行時の手順として参照可能にする（運営ガイド §1 と同じ位置づけ。計画書の改定なしに本文書を更新できる）。

**暫定版**：本手順は ReviewCompass 自身の自己適用検証（dogfooding）の中で運用し、必要が生じれば見直す。素材 `docs/coordination/workflow-repair-procedure.md`（先行プロジェクト）の 10 ステップを、現在の 5 段ワークフロー（drafting → triad-review → review-wave → alignment → approval）に再構成したもの。素材は旧ワークフロー（手戻り種別 A/B/C/D、各フェーズに単一の alignment gate）前提だったため、現行構造に合わせて作り直した。

## 1. いつ使うか

下流の段（triad-review／review-wave／alignment／approval）で、上流フェーズ（過去フェーズ）の修正が必要な「遡及（そきゅう）所見」を発見したとき。同じフェーズの他機能への影響（波及）は機能横断段（review-wave）で扱い、本手続きの対象外。所見の波及種別の判断は運営ガイド `SESSION_WORKFLOW_GUIDE.md` §3 を参照。

## 2. 4 過程の実行手順

計画書 §5.6.1 の 4 過程構成を実行手順にしたもの。各過程は「停止せず連続実行できる作業の単位」で、人の承認点で締める。

### 第1過程：判定とフラグ差し戻し（actor=llm、自律で連続実行）

1. 遡及所見を発見し、下流の作業を停止する
2. 手戻り種別を判定する（N／R／D／A／I × 深さ、計画書 §5.6）
3. 上流変更を既存 feature の責務境界へ写像し、feature impact を判定する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で行う
   - 既存 feature に受け皿がある場合：該当 feature ごとに `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only` のいずれかを判定する
   - 既存 feature に受け皿がない場合：`new_feature_required` として新 feature 候補を作る
   - 判定が重要、曖昧、広範囲の場合は 3 役レビューに送る
4. trigger_map で再実施対象の段を決定する（依存順＝`feature-dependency.yaml#phase_order`）
5. 種別判定と feature impact 判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に記録する（雛形：`templates/review/reopen_classification_template.md`）
6. 進行中状態ファイル `stages/in-progress/reopen-procedure-<日付>.yaml` を発行する
7. spec.json のフラグを差し戻す（計画書 §5.24.8.1）：
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
   - alignment（整合チェック）を実施し、波及（同フェーズの他機能への影響）の有無を確認
   - 上流変更に対する下流影響判定を `downstream_impact_decisions` に記録する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で必須とする
   - 「既存で受けられる」「修正不要」と判断する場合も、判定対象 gate、feature 範囲、判断、理由、証跡を記録する。修正不要は reopen を省略する理由ではなく、reopen 後の影響判定結果としてのみ扱う
   - 波及あり → triad-review に戻して対処（機能内対処または機能横断段へ）
   - 波及なし → approval へ
   - approval は人の承認（actor=human または proxy_model）

→ **停止点：各フェーズの approval（人の承認）。全フェーズ完了後にコミット**

### 第4過程：完了（連続実行）

10. 整合性の最終確認（上流の変更が下流に正しく伝わったか）
11. recheck をクリアする（`upstream_change_pending=false`、`impacted_downstream_phases=[]`）。`reopened.<上流>` は `true` のまま残す（履歴）。進行中状態ファイルを `stages/completed/` へ移動する

→ **停止点：コミット**

第4過程の完了 commit では、`stages/completed/reopen-procedure-*.yaml` に `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` と、`pending_gates` の各 gate を覆う `downstream_impact_decisions` が必要である。`feature_impact_decisions` は、既存 feature ごとに `feature`、`decision`、`rationale`、`evidence` を持つ。`decision` は `reopen_existing_feature`、`no_reopen_existing_feature`、`indirect_check_only`、`new_feature_required` のいずれかとする。`new_feature_decision.decision` は `no_new_feature` または `new_feature_required` とする。`downstream_impact_decisions` の各判定は最低限、`gate`、`feature_scope`、`decision`、`rationale`、`evidence` を持つ。`decision` は `affected_update_required`、`existing_sufficient`、`no_impact`、`approved`、`proxy_approved` のいずれかとする。`impacted_downstream_phases` に列挙した各フェーズには、対応する `downstream_impact_decisions[].gate` を少なくとも 1 件記録する。

## 3. 手戻り種別と trigger_map

計画書 §5.6 を参照。種別記号 N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ（どこまで上流に戻るか）。trigger_map（全 15 種、計画書 §5.6）が種別から再実施対象段を返す。再実施対象は各フェーズの alignment と approval（drafting／triad-review／review-wave は原則そのまま）。

## 4. 状態遷移の早見表（現在版、暫定）

| 発見した問題 | 修正フェーズ | 主なアクション |
|---|---|---|
| 要件の問題 | requirements | requirements を修正 → 下流（design／tasks／implementation）を reopen 対象に → 依存順に連鎖再実施 |
| 設計の問題 | design | design を修正 → 下流（tasks／implementation）を reopen 対象に → 連鎖再実施 |
| タスクの問題 | tasks | tasks を修正 → 下流（implementation）を reopen 対象に → 連鎖再実施 |
| 意図の問題 | intent | intent を修正 → 全機能の下流（requirements 以降）を reopen 対象に → 連鎖再実施 |

本表は素材 `workflow-repair-procedure.md` §3 状態遷移表を現在の 5 段ワークフローに簡略化したもの。詳細な遷移（implementation close 判定など）は今後の運用で必要に応じて拡充する。

## 5. spec.json の更新

計画書 §5.24.8.1 を参照。`reopened` は 6 フェーズ（intent／feature-partitioning／requirements／design／tasks／implementation）を対象とする。intent と feature-partitioning は機能横断段のため、これらの `reopened` は全機能で同じ値になる。

## 6. 記録の確実性について

本手続きの各ステップを LLM が忘れず実行する保証はない（ワークフロー記録全般が持つ脆さ）。これは最小単純優先（計画書 §5.24.2）と多層防御（§5.8）で対処する方針であり、本手続きでは特に、第1過程の承認・各コミット・各 approval を停止点として人の確認を挟むことで、記録漏れを検出可能にする。

## 7. 関連参照

- 計画書 §5.6（手戻り種別・trigger_map・4 過程構成 §5.6.1）
- 計画書 §5.24.8.1（再オープン時の recheck／reopened 更新手順）
- 運営ガイド `SESSION_WORKFLOW_GUIDE.md` §3（所見の波及種別と処理段）
- workflow-management 設計 `.reviewcompass/specs/workflow-management/design.md` §reopen 機械強制モデル
- 素材（旧、参考）：`docs/coordination/workflow-repair-procedure.md`（先行プロジェクトの 10 ステップ原文、本リポジトリには未配置）
