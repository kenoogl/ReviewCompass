---
type: design_triad_review
target: .reviewcompass/specs/conformance-evaluation/design.md
target_commit: dda65ec
date: 2026-05-26
mode: subagent_mediated
primary:
  provider: claude_code_subagent
  model_full_id: claude-sonnet-4-6
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 571
adversarial:
  provider: claude_code_subagent
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 225
judgment:
  provider: claude_code_subagent
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 191
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 9, INFO: 2 }
    count: 15
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 7, WARN: 5, INFO: 1 }
    count: 13
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 7, WARN: 16, INFO: 5 }
    count: 28
    judgment_distribution: { must-fix: 12, should-fix: 13, leave-as-is: 3 }
    waterfall_class_distribution: { 機能内対処: 19, 波及: 6, 遡及: 1, 延期: 0, leave-as-is: 3 }
---

# レビュー記録：conformance-evaluation 設計 triad-review

本記録は ReviewCompass の conformance-evaluation 機能の設計文書（design.md、起草時 930 行→ must-fix 反映後 約 1150 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。依存マップ順 7/7、全 7 機能の design 段 drafting＋triad-review 完了。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点を網羅実施。15 件の所見（ERROR 4／WARN 9／INFO 2）を提示。

主役所見の主要発見：

- F-004（ERROR）：YAML サンプルの axis 値が 2 軸 6 criteria 構造と不整合
- F-008（ERROR）：推定アルゴリズムで design→requirements 逆算の順序依存性が欠落
- F-012（ERROR）：phase_order に self-improvement 混入（判定役で leave-as-is に再評価、誤所見）
- F-014（ERROR）：CONFORMANCE_EVALUATION.md への言及が一切なし（判定役で leave-as-is、実存）
- F-001／F-002／F-003／F-005／F-006／F-007／F-009／F-010／F-015（WARN）：各観点の精緻化対象
- F-011／F-013（INFO）：軽微な改善余地

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（15 件）

- `counter_evidence_raised`：3 件（F-005／F-012／F-014）
- `no_counter_evidence_after_challenge`：11 件
- `not_assessed`：1 件（F-009）

主役 15 件のうち 3 件に反証を提示：

- F-005：評価記録の front-matter は §5.9.3 の所見メタデータ必須化と対象が異なる、severity 過大
- F-012：phase_order 誤記は事実訂正で済む、ERROR は過大
- F-014：`CONFORMANCE_EVALUATION.md` は実存、設計責務の射程外、ERROR は過大

### 2.2 独立発見（13 件、A-001〜A-013）

敵対役は強制的差異化（forced-divergence、計画書 §5.15.5）の精神で独立発見 13 件（ERROR 7／WARN 5／INFO 1）を提示。主な独立発見：

- A-001（ERROR、遡及）：12 criteria vs 6 criteria の語彙揺れ（requirements.md／CONFORMANCE_EVALUATION.md／計画書／pending-findings）
- A-002（ERROR）：finding_id ／ judgment_id の発番ルール未定義
- A-003（ERROR、波及）：信頼度ラベル 3 値が foundation に未登録、独自語彙導入
- A-004（ERROR）：§7.3 の遮断 3 手法提示が規律 options-presentation の事前検査宣言義務違反
- A-005（ERROR）：workflow-management スキーマ拡張の相互参照証跡なし
- A-006（ERROR）：「6 つのモデル」と宣言、構造的レベル非対称
- A-007（ERROR、波及）：foundation 受入番号の機械照合なし
- A-008／A-009／A-010／A-011／A-012（WARN）：analysis 接合面スキーマ未定義／API 障害対応の数値パラメータ／モード切替明示指定方法／target_commit と materialization_commit_hash の整合／検査スクリプト責務分担境界
- A-013（INFO）：完了基準が自己宣言のみで verifying_command 併記なし

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（28 件）

判定役は主役 15 件＋敵対役独立発見 13 件＝計 28 件のすべてについて、judgment と waterfall_class を判定。

### 3.2 severity 再評定

- F-005：WARN 維持
- F-009：WARN 維持（not_assessed → should-fix、機能内対処）
- F-011：INFO 維持（敵対役の事実誤認なし）
- F-012：ERROR → INFO 降格（判定役で誤所見と判定、leave-as-is）
- F-014：ERROR → INFO 降格（敵対役 counter_evidence 採用、leave-as-is）

### 3.3 judgment の分布

| judgment | 件数 | 内訳 |
|---|---|---|
| **must-fix** | **12 件** | F-003、F-004、F-006、F-008、F-015、A-001、A-002、A-003、A-004、A-007、A-008、A-011 |
| **should-fix** | **13 件** | F-001、F-002、F-005、F-007、F-009、F-010、F-011、A-005、A-006、A-009、A-010、A-012、A-013 |
| **leave-as-is** | **3 件** | F-012、F-013、F-014 |
| **合計** | **28 件** | |

### 3.4 waterfall_class の分布

| waterfall_class | 件数 | 内訳 |
|---|---|---|
| **機能内対処** | **19 件** | F-001、F-002、F-003、F-004、F-005、F-007、F-008、F-009、F-010、F-011、F-015、A-002、A-004、A-006、A-009、A-010、A-012、A-013 |
| **波及** | **6 件** | F-006（→ evaluation）、A-003（→ foundation）、A-005（→ workflow-management）、A-007（→ foundation）、A-008（→ analysis）、A-011（→ self-improvement） |
| **遡及** | **1 件** | A-001（→ requirements.md／CONFORMANCE_EVALUATION.md／計画書、軽量 reopen） |
| **延期** | **0 件** | — |
| **leave-as-is** | **3 件** | F-012、F-013、F-014 |
| **合計** | **28 件** | |

### 3.5 severity 別の最終件数（再評定後）

- CRITICAL：0 件
- ERROR：7 件（F-004、F-008、A-001、A-002、A-003、A-004、A-007）
- WARN：16 件
- INFO：5 件（F-011、F-012、F-013、F-014、A-013）

---

## 4. 統合（integration）

### 4.1 must-fix 12 件の対処方針と利用者承認の出典

運営ガイド §3.3 (a-1) 規律（must-fix 議論義務）に従い、must-fix 12 件を 10 グループに分けて 1 件ずつ深掘り議論。各グループで「経緯」「複数候補案」「各案の利点と弱点」「後段で発生し得る問題の深掘り」「推奨案と根拠」を平易な日本語で提示し、利用者明示承認を得てから反映。

| グループ | 所見 | 対処方針 | 利用者承認発言 |
|---|---|---|---|
| G1 | F-004 | YAML サンプルを §8.1 の正本（2 軸 6 criteria 構造）に揃える | 「候補 1」 |
| G2 | F-008 | §9.2 推定アルゴリズムを「design 先行→ requirements 逆算」の順序に書き換え | 「候補 1」 |
| G3 | A-002 | finding_id ／ judgment_id 発番ルール：CF-NNN ／ JD-NNN、self-improvement Decision 9 と同型 | 「候補 1」 |
| G4 | A-003（波及） | 信頼度ラベルを foundation 語彙体系に追加要請、本機能 §9.5 ／ §13.1 修正、波及登録 A-013 | 「候補 1」 |
| G5 | A-001（遡及） | 現役記述（requirements.md／CONFORMANCE_EVALUATION.md／計画書）の「12 criteria」→「6 criteria」、軽量 reopen | 「候補 1」 |
| G6 | F-015 | 計画書側を本機能 design.md の階層型命名（`conformance check` ／ `conformance generate`）に書き換え、軽量 reopen | 「候補 2」 |
| G7 | F-003 | 参照側を章タイトル参照に書き換え（番号なし 5 章を維持） | 「候補 2」 |
| G8 | A-004 | 規律 options-presentation 本体を改訂、対象範囲を「利用者に判断を仰ぐ複数案提示の応答」に限定 | 「候補 3」 |
| G9 | A-007 | 機械検査 MV-7（foundation 受入番号照合）を追加 | 「候補 1」 |
| G10 | F-006 ／ A-008 ／ A-011（波及 3 件） | 本機能 design.md §14 ／ §12.3 に詳細記述、`pending-cross-feature-findings.md` に波及登録 A-014 ／ A-015 ／ A-016 | 「候補 1」 |

### 4.2 反映箇所一覧

design.md（930 → 約 1150 行、+220 行、20 章維持）：

- §5.3／アーキテクチャ §3：CLI 命名を計画書改訂方針と整合（G6）
- §6.2／§7.1／§9.2／§9.3：design 先行→ requirements 逆算の順序を明示（G2、Decision 10）
- §7.3：自律ファイル探索の禁止条項を追記（F-010 部分対処）
- §8.1：axis（requirements ／ design の 2 値）と criterion_id（criterion-1〜6）を明示（G1）
- §8.5：YAML スキーマ例に axis ／ criterion_short_name を追加
- §9.4：YAML サンプルを 2 軸 6 criteria 構造に整合（G1）
- §9.5：信頼度ラベルを foundation 追加要請として書き換え（G4、Decision 11）
- §10.4：食い違い記録の axis ／ criterion_id ／ correspondence_type の 3 値（section_existence／claim_correspondence／code_reference_alignment）に統一（G1）
- §10.5：intent 差異記録の修正（G1）
- §10.7：finding_id ／ judgment_id 発番ルール新設（G3、Decision 9）
- §11.2：軽量／本格使い分けに design 推定の直接性を反映（G2）
- §12.3：front-matter に model_full_id ／ prompt_artifact_hash を追加、target_commit ／ materialization_commit_hash の整合ルール明示（F-005 部分対処、G10、A-011 対処）
- §13.4：workflow-management のスキーマ拡張との相互参照証跡明示
- §13.5：phase_order に self-improvement を含む 7 機能体制（workflow-management/design.md と整合、F-012 leave-as-is）
- §14.1：foundation 接合面に信頼度ラベル追加要請、機械検査 MV-7 明示（G4、G9）
- §14.3：evaluation 接合面に突き合わせ詳細追記（G10）
- §14.5：analysis 接合面に機械可読出力スキーマ詳細追記（G10）
- §14.6：self-improvement 接合面に commit hash 整合ルール明示（G10）
- §15：要件追跡表を章タイトル参照に書き換え、Req 8 を受入単位で展開（G7、F-001 対処）
- §16 Decision 9〜12：finding_id 発番（G3）／推定順序（G2）／信頼度 foundation 追加（G4）／規律対象範囲（G8）の 4 件を追加
- §18 機械検査：MV-7（foundation 受入番号照合）を追加、§18.3 fail-closed の粒度を MV ID 別に区別（G9、F-009 部分対処）
- §20.1：A-001／F-006／A-008／A-011／A-003 の遡及／波及登録を明示

requirements.md（A-001 遡及）：

- 行 33 ／ 34 の「12 criteria」→「6 criteria」（軽量 reopen）

CONFORMANCE_EVALUATION.md（A-001 遡及）：

- 行 33 の Requirement 4 説明：「12 criteria／4 上流フェーズ × 3 criteria」→「6 criteria／2 上流フェーズ × 3 criteria（intent は参考情報、feature-partitioning と tasks は対象外）」
- §4 節タイトルと本文：12 criteria → 6 criteria、4 軸列挙（intent／requirements／design／tasks）→ 2 軸列挙（requirements／design）に書き換え、除外階層を明示
- 他箇所の「12 criteria」→「6 criteria」を全件置換

計画書（A-001 遡及／F-015 遡及）：

- 行 141：「12 criteria 雛形（intent 3・requirements 3・design 3・tasks 3）」→「6 criteria 雛形（requirements 3・design 3、2026-05-24 セッション 23 改訂で 2 軸 6 criteria に絞り込み、intent は参考情報、feature-partitioning と tasks は対象外）」（軽量 reopen）
- 他箇所の「12 criteria」→「6 criteria」を全件置換
- 行 1010／1163：CLI 命名「reviewcompass generate-spec ／ reviewcompass conformance-check」→「reviewcompass conformance generate ／ reviewcompass conformance check（2026-05-26 セッション 27 改訂）」（軽量 reopen）

規律本体 discipline_options_presentation.md（G8、軽量手続き）：

- 「対象範囲」節を新設、対象を「利用者に判断を仰ぐ複数案提示の応答」に限定、設計文書内の比較記述は対象外と明示

pending-cross-feature-findings.md（A-013 ／ A-014 ／ A-015 ／ A-016 波及登録）：

- A-013：信頼度ラベル 3 値を foundation 語彙体系に追加要請（design レビュー波段で foundation 改訂と合わせて消化）
- A-014：evaluation との接合面の突き合わせ詳細（design レビュー波段で evaluation 設計改訂と合わせて消化）
- A-015：analysis との接合面の機械可読出力スキーマ（design レビュー波段で analysis 設計改訂と合わせて消化）
- A-016：target_commit と self-improvement の materialization_commit_hash の整合ルール（design レビュー波段で self-improvement 設計と合わせて消化）

### 4.3 should-fix 13 件と leave-as-is 3 件の処理状況

- **should-fix 13 件**：本セッション 27 では原則として反映せず、design.alignment 段以降の改善余地として記録。一部は must-fix 対処に伴って自然に解消（F-001 は §15 Req 8 受入単位展開で部分対処、F-005 は §12.3 で model_full_id 追加で部分対処、F-009 は §18.3 で粒度区別で部分対処、F-010 は §7.3 で自律ファイル探索禁止追記で部分対処、A-013 は §20.3 の完了基準確認で手動検証）
- **leave-as-is 3 件**：F-012（誤所見、self-improvement を含む phase_order が workflow-management/design.md と整合）／F-013（性能テストはフェーズ 4 第 2 サイクル詳細化）／F-014（CONFORMANCE_EVALUATION.md 実存、参照は任意）

### 4.4 波及所見の処理

- **F-006 ／ A-008 ／ A-011（G10、波及 3 件）**：本機能 design.md §14 ／ §12.3 で詳細記述（本機能側合意点）、`pending-cross-feature-findings.md` に A-014 ／ A-015 ／ A-016 として追記
- **A-003（G4、波及）**：本機能 §9.5 ／ §13.1 で foundation 追加要請として記述、`pending-cross-feature-findings.md` に A-013 として追記
- **A-007（G9、波及）**：機械検査 MV-7 として本機能内で対処（foundation 受入番号照合）、波及登録は不要（foundation 改訂時に MV-7 が機械的に追従）

### 4.5 関連参照

- 設計文書：[../design.md](../design.md)
- 要件文書：[../requirements.md](../requirements.md)
- 計画書 §5.10：[../../../../docs/plan/reconstruction-plan-2026-05-21.md](../../../../docs/plan/reconstruction-plan-2026-05-21.md) 行 1053〜1237
- 持ち越し所見：[../../../pending-cross-feature-findings.md](../../../pending-cross-feature-findings.md)
- 規律：[../../../../docs/disciplines/discipline_options_presentation.md](../../../../docs/disciplines/discipline_options_presentation.md)

### 4.6 利用者議論で判明した重要事項（後段への引き継ぎ）

- **規律 [options-presentation] の対象範囲明確化（Decision 12、軽量手続き）**：本セッション 27 で新設した規律が、その規律自身が運用される最初の本格場面（本機能 design.md §7.3 の遮断 3 手法）で違反指摘を受けた。利用者明示承認「候補 3」により規律の対象範囲を「利用者に判断を仰ぐ複数案提示の応答」に限定する小改訂を実施。設計文書内の比較記述は対象外と明確化
- **章番号体系の整合確認（design.alignment 段で消化予定）**：本機能 design.md は self-improvement 設計と同じく 20 章構成（番号なし 5 章＋番号付き §6〜§20 の 15 章）を採用。他機能（foundation／runtime／evaluation／analysis／workflow-management）の design.md でも同様の章番号体系の不整合が存在する可能性、design.alignment 段で全機能横断の章構造整合確認が必要（利用者明示承認「他機能でも生じていたはずなので後ほど対処」2026-05-26 セッション 27）
- **全 7 機能の design.drafting＋triad-review 完了**：依存マップ順 7/7 完了、本機能が最終機能。次は design レビュー波段（review-wave）で機能横断波及所見 A-011／A-012／A-013／A-014／A-015／A-016 の集約消化、その後 design.alignment（LLM 自動判定）→ design.approval（利用者明示承認）の順
