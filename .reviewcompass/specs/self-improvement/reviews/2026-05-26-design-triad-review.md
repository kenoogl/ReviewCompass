---
type: design_triad_review
target: .reviewcompass/specs/self-improvement/design.md
target_commit: dd8eba9
date: 2026-05-26
mode: subagent_mediated
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 449
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 220
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  prompt_artifact_path: メインセッション内の自己完結プロンプト（templates 未整備）
  duration_seconds: 130
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 12, INFO: 3 }
    count: 19
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 8, INFO: 2 }
    count: 13
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 7, WARN: 20, INFO: 5 }
    count: 32
    judgment_distribution: { must-fix: 13, should-fix: 17, leave-as-is: 2 }
    waterfall_class_distribution: { 機能内対処: 27, 波及: 2, 遡及: 1, 延期: 0, leave-as-is: 2 }
---

# レビュー記録：self-improvement 設計 triad-review

本記録は ReviewCompass の self-improvement 機能の設計文書（design.md、起草時 643 行→ must-fix 反映後 約 950 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。依存マップ順 6/7。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点（要件全件の網羅／アーキテクチャ整合性／データモデル・スキーマ詳細／API 接合面の具体化／アルゴリズム＋性能達成手段／失敗モード処理＋観測性／セキュリティ・プライバシーの具体化／依存選定／テスト戦略／移行戦略）を網羅実施。19 件の所見（ERROR 4／WARN 12／INFO 3）を提示。

主役所見の主要発見：

- F-003（ERROR）：consolidation の複数規律パス YAML フィールド欠如
- F-004（ERROR）：signal_extraction（新規実装）の設計詳細章なし
- F-015（ERROR）：「機械検査可能で担保」の具体検査方法未定義
- F-017（ERROR）：テスト戦略が設計文書全体に欠如
- F-001／F-002／F-005／F-006／F-007／F-008／F-010〜F-014／F-016／F-018／F-019（WARN）：各観点の精緻化対象
- F-009／F-013（INFO）：軽微な改善余地
- F-011（INFO）：grep 確認後に降格、敵対役 counter_evidence で事実誤認確定

主役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（19 件）

敵対役は主役 19 件のすべてに対し 3 値判定（counter_evidence_raised／no_counter_evidence_after_challenge／not_assessed）を付与：

- `counter_evidence_raised`：4 件（F-003／F-005／F-009／F-011）
- `no_counter_evidence_after_challenge`：15 件
- `not_assessed`：0 件

主役 19 件のうち 4 件に反証を提示：

- F-003：consolidation の複数規律対応は「複数提案の組み合わせ運用」で吸収可能と解釈（§7.3）
- F-005：章番号体系の不整合は severity を ERROR → WARN／INFO 減格余地
- F-009：conformance-evaluation の入力ファイル配置先は conformance-evaluation 側の責務
- F-011：`[[name]]` 形式は現用、事実誤認（grep で確認）

### 2.2 独立発見（13 件、A-001〜A-013）

敵対役は強制的差異化（forced-divergence、計画書 §5.15.5）の精神で独立発見 13 件（ERROR 3／WARN 8／INFO 2）を提示。主な独立発見：

- A-001（ERROR、**遡及**）：撤廃 README の配置先が requirements（`docs/archive/disciplines/`）と design（`docs/disciplines/archive/`）で不一致。実体は design 側が正しい
- A-002（ERROR）：proposal_id の発番ルール（採番権者・名前空間・通番リセット規則）未定義
- A-003（ERROR、**波及**）：self-improvement の status `approved` 遷移と workflow-management の手続き完了の時系列衝突
- A-004／A-005／A-006／A-007／A-008／A-009／A-010／A-012（WARN）：options-precheck-log との関係未整理／A-011 持ち越しとの依存／提案間依存フィールド欠落／superseded と reopen-procedure の衝突／計画書 §5.16.12 とのサイクル割当不整合／パイロット運用閾値の根拠不在／入力源 3 の機械可読化方針／空置きディレクトリ所有権者未定義
- A-011／A-013（INFO）：Ruby 拡張子と実装言語未確定／status_change の遵守率証拠と statistical_evidence の接続未定義

敵対役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（32 件）

判定役は主役 19 件＋敵対役独立発見 13 件＝計 32 件のすべてについて、judgment（must-fix／should-fix／leave-as-is）と waterfall_class（機能内対処／波及／遡及／延期／leave-as-is）を判定。

### 3.2 severity 再評定

敵対役の counter_evidence を受けた severity 再評定：

- F-005：WARN 維持（敵対役の WARN 妥当範囲を採用）
- F-009：INFO 維持（敵対役の counter_evidence を採用、leave-as-is）
- F-011：WARN → INFO 降格（敵対役の事実誤認指摘を採用、leave-as-is）
- F-003：ERROR 維持（counter_evidence は救済策の提示で問題自体は残存）

### 3.3 judgment の分布

| judgment | 件数 | 内訳 |
|---|---|---|
| **must-fix** | **13 件** | F-001、F-002、F-003、F-004、F-006、F-008、F-015、F-017、A-001、A-002、A-003、A-007、A-009 |
| **should-fix** | **17 件** | F-005、F-007、F-010、F-012、F-013、F-014、F-016、F-018、F-019、A-004、A-005、A-006、A-008、A-010、A-011、A-012、A-013 |
| **leave-as-is** | **2 件** | F-009、F-011 |
| **合計** | **32 件** | |

### 3.4 waterfall_class の分布

| waterfall_class | 件数 | 内訳 |
|---|---|---|
| **機能内対処** | **27 件** | F-001、F-002、F-003、F-004、F-005、F-006、F-007、F-010、F-012、F-013、F-014、F-015、F-016、F-017、F-018、F-019、A-002、A-004、A-005、A-006、A-007、A-008、A-009、A-010、A-011、A-012、A-013 |
| **波及** | **2 件** | F-008（→ workflow-management 機能設計）、A-003（→ workflow-management 機能設計） |
| **遡及** | **1 件** | A-001（→ requirements.md、軽量 reopen 手続き） |
| **延期** | **0 件** | — |
| **leave-as-is** | **2 件** | F-009、F-011 |
| **合計** | **32 件** | |

### 3.5 severity 別の最終件数（再評定後）

- CRITICAL：0 件
- ERROR：7 件（F-003、F-004、F-015、F-017、A-001、A-002、A-003）
- WARN：20 件
- INFO：5 件（F-009、F-011、F-013、A-011、A-013）

---

## 4. 統合（integration）

### 4.1 must-fix 13 件の対処方針と利用者承認の出典

運営ガイド §3.3 (a-1) 規律（must-fix 議論義務）に従い、must-fix 13 件を 8 グループに分けて 1 件ずつ深掘り議論。各グループで「経緯」「複数候補案」「各案の利点と弱点」「後段で発生し得る問題の深掘り」「推奨案と根拠」を平易な日本語で提示し、利用者明示承認を得てから反映。

| グループ | 所見 | 対処方針 | 利用者承認発言 |
|---|---|---|---|
| G1-1 | F-004 | signal_extraction 専用章を §7（旧 §7 提案モデルは §8 に繰り上げ）として新設 | 「候補 1」 |
| G1-2 | F-015 | 機械検査の具体手段を §17 として新設 | 「候補 1」 |
| G1-3 | F-017 | テスト戦略を §18（Open Issues 直前）として新設 | 「候補 1」 |
| G2 | F-003／F-006 | YAML スキーマに `source_discipline_paths` 配列を追加（consolidation 専用フィールド） | 「候補 1」 |
| G3 | A-001（遡及） | requirements.md 行 125 を実体配置・design.md と整合する `docs/disciplines/archive/<日付>-<id>/README.md` に修正、軽量 reopen 手続き | 「候補 1」 |
| G4 | A-002 | proposal_id：採番権者は self-improvement、接頭辞分離（`WP-NNN` ／ `RB-NNN`）、通番リセットなし、3 桁から 4 桁拡張 | 「候補 1」 |
| G5 | A-003／F-008（波及） | 本機能 design.md §13.5 に時系列契約・完了通知形式を詳細記述、4 状態維持、pending-cross-feature-findings.md に A-012 として追記 | 「候補 1」 |
| G6 | A-007 | superseded 遷移時に reopen-procedure 5 ステップを §8.7／§10.5／Decision 6 に明示 | 「候補 1」 |
| G7 | A-009 | パイロット運用閾値を 90% に確定、本セッション 27 利用者明示承認の出典を §9.3／Decision 10 に併記 | 「候補 1、90%」 |
| G8 | F-001／F-002 | §14 要件追跡表を受入基準単位に詳細化（旧 §13 は §14 に繰り上げ） | 「候補 1」 |

### 4.2 反映箇所一覧（design.md、機能内対処 13 件＋遡及 1 件＋波及 2 件）

design.md（643 行 → 約 950 行、+307 行、章番号体系を 17 章 → 20 章に拡張）：

- **新規 §7**：signal_extraction モデル（F-004）
- **§8.4**：YAML スキーマに `source_discipline_paths` 配列、`depends_on`、`superseded_by`／`superseded_at`／`reopen_reason`、`materialized_at`／`materialization_commit_hash` を追加（F-003／F-006／A-002／A-007／A-003／F-008）
- **§8.5**：proposal_id 発番ルール（A-002）
- **§8.7**：superseded 遷移の reopen-procedure 5 ステップ（A-007）
- **§9.3**：パイロット運用閾値 90%、出典併記（A-009）
- **§10.5**：4 状態遷移管理に reopen-procedure 5 ステップを明示（A-007）
- **§13.5**：workflow-management との時系列契約・完了通知形式・ロールバック責務を詳細記述（A-003／F-008）
- **§14**：要件追跡表を受入基準単位に詳細化、全 32 受入基準を §章節と対応（F-001／F-002）
- **新規 §17**：機械検査の具体手段（4 検査ポイント MV-1〜MV-4、F-015）
- **新規 §18**：テスト戦略（5 モデル＋ 7 指標のテスト対象とテストレベル、F-017）
- **§19**：Open Issues に A-001（遡及）／A-003／F-008（波及）／A-011（依存）を明示
- **§20**：起草完了基準を 20 章対応に更新、must-fix 13 件の対処をすべてチェック

requirements.md（A-001 遡及）：

- 行 125 を `docs/archive/disciplines/<日付>/README.md` → `docs/disciplines/archive/<日付>-<id>/README.md` に修正、軽量 reopen 手続きの注記を追記

pending-cross-feature-findings.md（A-003／F-008 波及登録）：

- A-012 として追記（self-improvement と workflow-management の時系列契約・完了通知形式、design レビュー波段で消化予定）

### 4.3 should-fix 17 件と leave-as-is 2 件の処理状況

- **should-fix 17 件**：本セッション 27 では原則として反映せず、design.alignment 段以降の改善余地として記録。一部は must-fix 対処に伴って自然に解消（F-005／F-018 は章番号変更で部分対処、F-013 は §8.6 で採用率分母の意図明記、A-011 は §15 Decision 7 で実装言語の将来決定を明記、A-012 は §11.1 で空置きディレクトリ所有権の注記、A-013 は §8.8 で status_change の遵守率証拠を statistical_evidence と接続）
- **leave-as-is 2 件**：F-009（conformance-evaluation 側の責務）／F-011（`[[name]]` 形式は現用、事実誤認）

### 4.4 波及所見の処理

- **A-003／F-008**：本機能 design.md §13.5 で時系列契約・完了通知形式を「提案」として詳細記述。workflow-management 側の合意は design レビュー波段で取る。`pending-cross-feature-findings.md` に A-012 として追記済み

### 4.5 関連参照

- 設計文書：[.reviewcompass/specs/self-improvement/design.md](../design.md)
- 要件文書：[.reviewcompass/specs/self-improvement/requirements.md](../requirements.md)
- 計画書 §5.16：[docs/plan/reconstruction-plan-2026-05-21.md](../../../../docs/plan/reconstruction-plan-2026-05-21.md) 行 1957〜2135
- 持ち越し所見：[.reviewcompass/pending-cross-feature-findings.md](../../../pending-cross-feature-findings.md)
- 規律：[docs/disciplines/](../../../../docs/disciplines/)

### 4.6 利用者議論で判明した重要事項（後段への引き継ぎ）

- **章番号変更（リナンバリング）が alignment レビューの対象になる**（利用者指摘 2026-05-26 セッション 27）：本機能 design.md で 17 章 → 20 章への章番号変更を実施。利用者明示承認「案 A」（章番号変更採用、「他機能でも同様の問題が生じていたはずなので後ほど対処」）。design.alignment 段でリナンバリング前後の対応表と他機能の章構造との整合確認が必要、本セッション 27 では本機能のみ対処済み、他機能（foundation／runtime／evaluation／analysis／workflow-management）は別途追跡が必要
- **規律 [options-presentation] の事前検査宣言義務を本 triad-review で実用**（本セッション 27 新設）：複数案提示の場面（G1-1／G1-2／G1-3／G2／G3／G4／G5／G6／G7／G8 の各議論）で (a)(b)(c)(d) を明示宣言、dominated 案を除外して合理案のみを提示する規律を本セッション内で運用、効果測定ログ `docs/discipline-compliance-reports/options-precheck-log.md` への記録は次セッション以降
