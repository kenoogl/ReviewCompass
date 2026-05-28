---
type: tasks_triad_review
target: .reviewcompass/specs/self-improvement/tasks.md
target_commit: 9794942
target_content_hash: <未計測、セッション 39 起草分（T-001〜T-011）>
date: 2026-05-29
mode: subagent_mediated
session: session-39
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: 約 6
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 3
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 2
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 2, ERROR: 7, WARN: 6, INFO: 1 }
    count: 16
  adversarial:
    by_counter_status: { counter_evidence_raised: 4, no_counter_evidence_after_challenge: 12 }
    independent_findings: { ERROR: 3, WARN: 2, INFO: 1 }
    count: 22
  judgment:
    by_judgment: { must-fix: 5, should-fix: 8, leave-as-is: 8 }
    by_waterfall: { 機能内対処: 6, 遡及: 5, 波及: 0, 延期: 0 }
    論点群数: 15
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（foundation／runtime／evaluation／analysis／workflow-management tasks-triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で言及のみで本体未整備、foundation tasks-triad-review（セッション 30）の仮設定を継承
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）。本記録 §1.2 に主役の事実誤認（A-011 を未解決と誤認）の事後検証結果を明記
  - 3 役の生出力はサブエージェントログ（~/.claude/projects/-Users-Daily-Development-ReviewCompass/<session-id>/subagents/）から復元可能
---

# レビュー記録：self-improvement tasks triad-review

本記録は self-improvement 機能の tasks.md（11 タスク T-001〜T-011、コミット `9794942`）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は仮設定 7 観点（上流仕様の網羅／タスク粒度の妥当性／タスク依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。16 件の所見（CRITICAL 2／ERROR 7／WARN 6／INFO 1）を提示した。

### 1.1 主役所見一覧（16 件、F-001〜F-016）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 1：上流仕様の網羅 | CRITICAL | tasks.md T-010 責務欄、design §19.3 | T-010 が `roles/role_diff_report.json` を「A-011 対処済み」と記述するが design §19.3 は未解決と明示＝偽完了宣言 | fact |
| F-002 | 6：機能横断波及の早期検出 | CRITICAL | T-010 完了条件 2、DVT | A-011 未消化なのに対応する DVT 項目が未登録、T-010 完了条件 2 が機械検証不能のまま実装開始できてしまう | fact |
| F-003 | 4：完了条件の機械判定可能性 | ERROR | design §12.5 手順 3 行571、T-008 完了条件 5 | design §12.5 手順 3 の採用率計算式が `(approved+superseded)/(...)` で §12.1（分子 approved のみ）と矛盾、T-008 完了条件 5 が継承 | fact |
| F-004 | 1：上流仕様の網羅 | ERROR | requirements Req 4 受入 2、design §6.2、T-002 完了条件 2 | requirements は source 値域 3 値だが design §6.2 が observation_pattern 追加で 4 値、差分追跡 DVT がない | fact |
| F-005 | 7：成果物配置と命名の整合 | ERROR | design §11.1 配置ツリー、T-001 完了条件 1・3 | design §11.1 配置ツリーに learning/workflow/metrics/ がない、T-001 完了条件 1（metrics 含む 5 ディレクトリ）と 3（§11.1 と一致）が自己矛盾 | fact |
| F-006 | 7：成果物配置と命名の整合 | ERROR | tools/self_improvement/、tools/self-improvement-check.py | アンダースコアとハイフンで命名規則混在、Python import 問題 | fact |
| F-007 | 7：成果物配置と命名の整合 | ERROR | T-002/T-003 と T-004/T-007/T-008 のスキーマ配置 | スキーマ配置が tools/self_improvement/ と learning/workflow/ に分散、一貫ポリシー不明 | mixed |
| F-008 | 3：依存順の整合性 | ERROR | T-007 前提（T-001、T-006）、design §11.6 | T-007 前提に T-005 がない、§11.6 整合性検査で検証モデル使用の可能性 | mixed |
| F-009 | 3：依存順の整合性 | ERROR | T-010 前提（T-004、T-006） | T-010 前提が T-004/T-006 のみで T-002/T-003/T-008 が欠落、完了条件 3 は T-008 連動と明記 | fact |
| F-010 | 4：完了条件の機械判定可能性 | WARN | T-002 完了条件 5、T-010 完了条件 1 | T-002（運用文書明示＝人手）と T-010（grep 機械検証）が同種原則に異なる検証手段 | fact |
| F-011 | 4：完了条件の機械判定可能性 | WARN | T-001 成果物（tools/README.md 追記） | T-001 成果物に tools/README.md 追記があるが完了条件に検証がない | fact |
| F-012 | 5：テスト要件の妥当性 | WARN | T-004 テスト要件、design §8.8 | §8.8 は update に diff/対照表を要求するが T-004 テスト要件は 3 種別のみ（update/new_discipline 欠落） | fact |
| F-013 | 5：テスト要件の妥当性 | WARN | T-005 テスト要件・完了条件 2 | 90% ちょうどの昇格可否の機械判定基準が曖昧 | mixed |
| F-014 | 2：タスク粒度の妥当性 | WARN | T-004 完了条件、requirements Req 3 受入 2 | target_discipline_path が docs/disciplines/ プレフィックスである機械検証が T-004 完了条件にない | fact |
| F-015 | 6：機能横断波及の早期検出 | WARN | T-004/T-007/T-008 スキーマ配置 | スキーマ 3 つが learning/workflow/ 直下でデータ YAML と混在、workflow-management 接合で誤参照リスク | inference |
| F-016 | 1：上流仕様の網羅 | INFO | tasks.md 要件追跡表末尾 2 行 | 末尾 2 行（Boundary Context／権限分離）が requirements 正式番号体系に対応せず記法相違 | fact |

### 1.2 主役の注目発見と、メインセッションによる事後検証

主役は最も危険な所見として F-001／F-002（A-011 の「偽完了宣言」と DVT 未登録）、F-003（採用率計算式の矛盾）、F-005（metrics 配置の自己矛盾）を挙げた。

**メインセッション（起草者 Opus 4.7）による事後検証**（計画書 §5.23.12.7 準拠）：主役の F-001／F-002 は「design §19.3 で A-011 が未解決と明示されている」という事実主張に依拠しているが、これは **前提誤り**である。横断所見の正本 `.reviewcompass/pending-cross-feature-findings.md` 166 行で **A-011 は「✅ 対処済み（2026-05-26、セッション 28）」** と明記され、evaluation 設計に `roles/role_diff_report.json` が実際に新設済み。A-016 も同 247 行で対処済み。tasks.md（2026-05-29 起草）の「A-011／A-016 対処済み」は **最新の正本に従った正しい記述**である。陳腐化しているのは design.md §13.3（611 行）と §19.3（923 行）であって tasks ではない（敵対役 G-001 が正しく指摘）。よって主役の CRITICAL 認定 2 件は前提誤りで、判定役により leave-as-is とされた。

これは **起草者・主役バイアスの一例**：主役が design 本文（陳腐化済み）だけを根拠に最重大認定を下し、横断所見の正本を参照しなかった。敵対役が正本を参照して反証を成立させた。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への counter_status 付与（16 件）

counter_evidence_raised（反証あり）は 4 件（F-001／F-002／F-008／F-013）、残り 12 件は no_counter_evidence_after_challenge（同意）。

| 主役 ID | counter_status | 要旨 |
|---|---|---|
| F-001 | counter_evidence_raised | A-011 は実際は対処済み（正本 166 行）。tasks の記述は正しく、偽完了でない。陳腐化は design 側（G-001）。CRITICAL 過大 |
| F-002 | counter_evidence_raised | F-001 と同根。A-011 対処済みのため「未消化なのに DVT 未登録」の前提が崩れる。CRITICAL 過大 |
| F-003 | no_counter_evidence_after_challenge | §12.1 と §12.5 手順 3 で分子が矛盾、所見妥当。ERROR 維持 |
| F-004 | no_counter_evidence_after_challenge | source 3 値→4 値の差分追跡 DVT がない、所見妥当。ただし severity は WARN 寄り（上位互換拡張への下流追従漏れ） |
| F-005 | no_counter_evidence_after_challenge | §11.1 ツリーに metrics/ がなく T-001 完了条件 1 と 3 が両立不能、所見妥当。ERROR 維持 |
| F-006 | no_counter_evidence_after_challenge | 命名混在は事実。ただし機能的に両立可（パッケージ＝アンダースコア／CLI スクリプト＝ハイフン）、WARN 相当に緩和余地 |
| F-007 | no_counter_evidence_after_challenge | スキーマ配置分散の一貫ポリシー記述がない、所見妥当 |
| F-008 | counter_evidence_raised | §11.6 整合性検査は front-matter 検査／`[[name]]` grep／archive README 確認の 3 点で T-005 検証モデルを呼ばない。T-005 を前提に加える根拠は薄い。ERROR 過大 |
| F-009 | no_counter_evidence_after_challenge | T-010 完了条件 3 が T-008 連動と明記なのに前提に T-008 欠落、所見妥当。ERROR 維持 |
| F-010 | no_counter_evidence_after_challenge | 主役の対比はやや不正確だが、同種原則への検証手段の割れは事実。WARN 維持 |
| F-011 | no_counter_evidence_after_challenge | tools/README.md 追記の完了条件検証なし、所見妥当。WARN 維持 |
| F-012 | no_counter_evidence_after_challenge | §8.8 全 5 種別のテスト網羅に対し T-004 は 3 種別のみ、所見妥当。WARN 維持 |
| F-013 | counter_evidence_raised | §9.3 と T-005 完了条件 2 が「90% 以上で昇格」と明記済み。90% は昇格可で一意、曖昧性なし。WARN 不要 |
| F-014 | no_counter_evidence_after_challenge | target_discipline_path プレフィックスの機械検証が T-004 完了条件にない、所見妥当。WARN 維持 |
| F-015 | no_counter_evidence_after_challenge | スキーマとデータの混在で誤参照懸念に合理性。WARN が妥当 |
| F-016 | no_counter_evidence_after_challenge | 末尾 2 行の記法相違は事実。INFO 妥当 |

### 2.2 敵対役の独立所見（6 件、G-001〜G-006）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| G-001 | 設計の内部整合 | ERROR | design §13.3 行611、§19.3 行923、tasks T-010 | design がA-011 対処後も未更新で陳腐化（「追加予定」「消化予定」「前提」）。tasks は正しく「対処済み」と書くため真逆。正すべきは design 本文 | cross_document_inconsistency |
| G-002 | 検証可能性 | ERROR | design §8.5 行302、T-004 完了条件 4 | proposal_id 採番「proposals/ の最大番号＋1」だが approved/rejected は git mv で別ディレクトリへ移動（§10.5）。proposals/ には pending しか残らず採番衝突。全 4 ディレクトリ走査すべき | logical_defect |
| G-003 | 設計と要件の対応 | ERROR | T-004 完了条件 5、T-005 完了条件 1、requirements Req 4 受入 5 | T-004（statistical_evidence 必須化）前提に T-005（生成）がない。status_change 必須化と生成責務の依存逆転。T-004 単独では埋められない | dependency_inversion |
| G-004 | 段階的導入の妥当性 | WARN | T-009 MV-3、design §17.1、§13.5 | MV-3（materialization_commit_hash 実在検査）の書き込み主体は workflow-management。第 1 期は常に null で vacuously pass。null 時の扱い未定義 | spec_gap |
| G-005 | 設計の内部整合 | WARN | T-001 成果物、§11.1 | findings/backtests/templates の README パスが個別列挙されず（.gitkeep のみ）、完了条件 2 と粒度不一致 | inconsistency |
| G-006 | 実装可能性 | INFO | T-009、F-006 補足 | F-006 命名混在は意図的に説明可能（パッケージ vs CLI スクリプト）。ERROR を WARN へ緩和余地 | severity_mitigation |

### 2.3 敵対役の総評

1. 主役の CRITICAL 2 件（F-001／F-002）は前提事実が誤り。真の問題は design 本文の陳腐化（G-001）。論点の主体を tasks から design へ移す必要がある。
2. proposal_id 採番ロジックの論理欠陥（G-002）。主役が誰も突いていない実装レベルの確定バグ。
3. statistical_evidence の供給と必須検証の依存逆転（G-003）＋ metrics ディレクトリ自己矛盾（F-005）。tasks 着手前に design §11.1／§8.5／§8.9 の修正が必要。

---

## 3. 判定役判定（judgment、Opus 4.7）

判定役は主役 16 件＋敵対役独立 6 件＝22 件を 15 論点群に集約し、最終判定を下した。

### 3.1 最終判定表

| 論点ID群 | 判定 | 対処文書 | waterfall分類 | 判定理由（要約） |
|---|---|---|---|---|
| F-001 / F-002 / G-001 | F-001・F-002 は leave-as-is、**G-001 は must-fix** | design.md（§13.3 行611・§19.3 行923） | 遡及 | A-011/A-016 は対処済み（正本 166/247 行）。tasks の記述は正しく偽完了でない。陳腐化は design 本文（G-001）。tasks 完了基準が要求する design §20 整合検査が破綻するため design の遡及修正が必要 |
| F-003 | **must-fix** | design.md（§12.5 手順 3 行571） | 遡及 | §12.1・§8.6・T-008 完了条件 2 は分子 approved のみ。§12.5 手順 3 だけ分子 approved+superseded。矛盾式が手動集計運用に流入。design §12.5 を修正必須 |
| F-004 | should-fix | tasks.md（DVT 追記） | 機能内対処 | source 3 値→4 値の差分が DVT 未登録。下流が上流拡張に追従する正方向で内部整合は取れているため延期・追跡で足る |
| F-005 | **must-fix** | design.md（§11.1 配置ツリー 行453-472） | 遡及 | §11.1 ツリーに metrics/ がないが §12.3 等が使用。T-001 完了条件 1（metrics 必須）と 3（§11.1 と一致）が衝突し配置検査が必ず失敗。§11.1 に metrics/ 追記必要 |
| F-006 / G-006 | should-fix | tasks.md（命名規約明文化） | 機能内対処 | パッケージ＝アンダースコア／CLI スクリプト＝ハイフンとして両立可。ERROR は過大、文書化不足が実体 |
| F-007 / F-015 | should-fix | tasks.md（配置ポリシー明文化） | 機能内対処 | ツール内部スキーマ＝tools 配下／データ正本スキーマ＝learning 配下の分離方針を一文で確定すべき |
| F-008 | leave-as-is | — | — | 敵対役反証成立。§11.6 整合性検査は T-005 検証モデルを呼ばない。ERROR 過大 |
| F-009 | should-fix | tasks.md（T-010 前提タスク） | 機能内対処 | T-010 完了条件 3 が T-008 連動なのに前提に欠落。ただし T-010 は T-008 完了を厳密に待たず起草可能、依存順の明示漏れに留まる |
| F-010 | leave-as-is | — | — | T-002 と T-010 は検証対象が異なる（運用宣言 vs 語彙 grep）。同種原則への異手段でなく対象差 |
| F-011 | leave-as-is | — | — | tools/README.md は既存ファイルへの追記で本機能の正本成果物でない。完了条件外でも実害なし |
| F-012 | should-fix | tasks.md（T-004 テスト要件） | 機能内対処 | §8.8 全 5 種別のテスト網羅が望ましい。update/new_discipline のテスト追加。実装段で補える |
| F-013 | leave-as-is | — | — | 敵対役反証成立。§9.3・T-005 完了条件 2 とも「90% 以上で昇格」と明記、90% は昇格可で一意。曖昧性なし |
| F-014 | should-fix | tasks.md（T-004 完了条件） | 機能内対処 | target_discipline_path プレフィックスの機械検証を完了条件に一項目追加 |
| F-016 | leave-as-is | — | — | 末尾 2 行は横断的観点の追記で意図的。T-011 の双方向整合チェックが正式番号体系で検査するため実害なし |
| G-002 | **must-fix** | design.md（§8.5 行302）＋ tasks.md（T-004 完了条件 4） | 遡及 | proposals/ には pending しか残らず採番衝突（ID 重複）。「通番リセットなし」の設計意図とも矛盾。全 4 ディレクトリ走査が必要。ID 重複は履歴連結（T-007）を破壊するため致命的 |
| G-003 | **must-fix** | tasks.md（T-004／T-005 依存順）＋ design.md（責務記述） | 遡及 | T-004 が必須化する statistical_evidence の生成責務は T-005。依存順 T-004→T-005 では status_change 提案が T-004 段階で完成不能。生成責務の前後関係を整理 |
| G-004 | should-fix | tasks.md（T-009 MV-3）＋ design.md（§17.1） | 機能内対処 | MV-3 は第 1 期は常に null で vacuously pass。null 時の扱い（スキップか fail-closed か）を一文で確定 |
| G-005 | leave-as-is | — | — | 責務本文と完了条件 2・テスト要件でカバー済み。粒度不一致は表記レベルで実害なし |

### 3.2 by_judgment 集計

- **must-fix：5 件**（F-003 / F-005 / G-001 / G-002 / G-003）
- **should-fix：8 件**（F-004 / F-006＝G-006 / F-007＝F-015 / F-009 / F-012 / F-014 / G-004）
- **leave-as-is：8 件**（F-001 / F-002 / F-008 / F-010 / F-011 / F-013 / F-016 / G-005）

### 3.3 判定役の総括（実装段前に必ず対処すべき must-fix）

最優先（実装が確実に破綻する論理欠陥）：
1. **G-002（採番衝突）**：design §8.5 と T-004 完了条件 4 を「全 4 ディレクトリ走査の最大番号＋1」に修正。
2. **G-003（依存逆転）**：T-004 が必須化する statistical_evidence の生成責務（T-005）との前後関係を明示。

design 本文の整合修正（tasks は正しいが上流が矛盾）：
3. **F-005（metrics 配置）**：design §11.1 ツリーに learning/workflow/metrics/ を追記。
4. **F-003（採用率計算式）**：design §12.5 手順 3 の分子を approved のみに修正。
5. **G-001（design 陳腐化）**：design §13.3・§19.3 を A-011/A-016 対処済みに合わせて更新。

---

## 4. 統合節（メインセッションによる集約）

### 4.1 must-fix 5 件の対処方針案（利用者議論用、各案に後段影響）

本節は規律 [must-fix-discussion-obligation] に従い、各 must-fix に対処方針の選択肢と後段影響を整理する。**確定は利用者議論を経てから**であり、本節は議論の素材である。

#### must-fix-1：G-002 採番衝突

- **事実**：design §8.5 行302「採番手順：proposals/ 配下の最大番号＋1」。§10.5 行441-444 で approved→approved-updates/、rejected→rejected-updates/、superseded→approved-updates/ へ git mv。proposals/ には pending のみ残る。
- **案 1（推奨）**：採番の走査対象を全 4 ディレクトリ（proposals/approved-updates/rejected-updates/rollback/）に拡張。design §8.5 と tasks T-004 完了条件 4 の両方を修正。
  - 後段影響：T-004 実装で全ディレクトリ走査が必要、T-009 MV 検査の対象範囲も整合。履歴連結（T-007）の ID 一意性が保たれる。
- **案 2**：採番台帳ファイル（`learning/workflow/.id-counter`）を単一の真実源として導入し、ディレクトリ走査をやめる。
  - 後段影響：新規ファイルの追加と並行更新の競合管理が必要。第 1 期手動運用には過剰。
- 私の評価：案 1 が最小修正で設計意図（通番リセットなし）に忠実。案 2 は将来の自動化で再検討余地。

#### must-fix-2：G-003 依存逆転

- **事実**：§8 行357 status_change は statistical_evidence 必須。§9.2 行381 で T-005 が statistical_evidence を生成・記録。tasks 依存順は T-004→T-005。
- **論点の整理**：T-004 は提案モデル（スキーマ＋検証ロジック）を**作る**タスク、T-005 は検証手段を**作る**タスク。コードを組む順序としては T-004→T-005 で破綻しない（T-004 は「status_change 提案に statistical_evidence が無ければ DEVIATION」と検証するだけで、値の中身は生成しない）。一方、実行時に実際の status_change 提案を完成させるには T-005 の生成物が要る。
- **案 1**：依存順は現状維持（T-004→T-005）とし、tasks に「T-004 は statistical_evidence の存在検証のみ、生成は T-005 の責務」と責務境界を一文明記。design 側も §8.9／§9.2 の責務分担を明確化。
  - 後段影響：最小修正。実装は現行依存順で進む。
- **案 2**：T-004 の前提タスクに T-005 を追加（T-005→T-004 に逆転）。
  - 後段影響：データの流れ（§5.1：提案→検証）と逆行し、依存順の基本原則を崩す。提案モデルが検証モデルに依存する不自然な構造。
- 私の評価：案 1 が妥当。判定役は「依存逆転」と強く表現したが、ビルド順序とランタイムのデータ流れを分離すれば現行順序で問題ない。責務境界の明文化で解消する論点。**判定役が must-fix にやや過大評価した可能性があり、議論で確認したい**。

#### must-fix-3：F-005 metrics 配置欠落

- **事実**：design §11.1 ツリー行453-472 に metrics/ がない。§12.3 行555・§12.4・§17.3 が learning/workflow/metrics/ を使用。T-001 完了条件 1（5 ディレクトリに metrics 含む）と完了条件 3（§11.1 と一致）が衝突。
- **案 1（推奨）**：design §11.1 ツリーに `metrics/` を追記（§12.3 の使用と整合）。
  - 後段影響：T-001 完了条件の衝突解消。最小修正で章間整合が回復。
- 私の評価：単純な記載漏れの遡及修正。異論の余地が小さい。

#### must-fix-4：F-003 採用率計算式の矛盾

- **事実**：§12.1 行540 と §8.6 行324 は採用率＝approved／(approved+rejected+superseded)（分子 approved）。§12.5 手順 3 行571 だけ `(approved+superseded)/(...)`（分子に superseded を含む）。
- **論点**：superseded（後続提案で上書きされた過去の承認）を「採用」に数えるか。§8.6 の定義意図（superseded は無効化された過去の承認）からは分子に含めない（§12.1 が正）のが自然。
- **案 1（推奨）**：§12.5 手順 3 の分子を approved のみに修正し、§12.1 に統一。
  - 後段影響：T-008 完了条件 5（§12.5 の 4 ステップ再現）が正しい式を継承。
- **案 2**：逆に §12.1 を §12.5 に合わせ分子を approved+superseded にする。
  - 後段影響：superseded を採用に数える意味づけが必要。F-013 対処（pending 除外）の議論時の設計意図と整合しない。dominated。
- 私の評価：案 1。§12.1 が複数箇所で一貫しており、§12.5 のみの孤立した誤記と判断。

#### must-fix-5：G-001 design 本文の陳腐化

- **事実**：design §13.3 行611「A-011 対処で evaluation 設計に追加予定」「design.alignment は A-011 消化に依存」、§19.3 行923「A-011（既存、design レビュー波段で消化予定）」「A-011 消化が design.alignment の前提」。正本では A-011/A-016 ともセッション 28 で対処済み。
- **案 1（推奨）**：design §13.3・§19.3 を「A-011 対処済み（セッション 28、evaluation に role_diff_report.json 新設済み）」に更新。§19.3 の「design.alignment の前提」記述も「対処済みのため前提充足」へ。
  - 後段影響：tasks の「対処済み」記述と design 本文が整合。design.alignment 段（将来）での前提充足確認がスムーズ。
- 私の評価：遡及修正だが正本に合わせるだけで異論の余地が小さい。なお design は design.approval まで完了済みのため、この修正は**確定済み design への遡及修正**であり、再オープン手続き（軽量、§5.23.13）の要否を利用者と確認する必要がある。

### 4.2 利用者議論履歴

#### 4.2.1 7 モデル比較実験の概要（セッション 39、2026-05-29）

12 論点群を topic-99〜110 に展開し、7 モデル（Opus 4.7 起草者／Sonnet 4.6 CLI／Sonnet 4.6 API／GPT-5.5／GPT-5.4／Gemini-3.5-flash／Gemini-3.1-pro）で評価。プロンプトは推奨案を含めない方針（起草者バイアス防止）。集計スクリプト `_aggregate_self_improvement_eval_temp.py`。

結果：**完全一致 4 件（topic-99／100／105／110、いずれも案 1）、割れ 8 件**。

| topic | 所見 | 種別 | 分布 | 備考 |
|---|---|---|---|---|
| 99 | G-002 | must | 全 7 案 1 | 完全一致 |
| 100 | G-003 | must | 全 7 案 1 | 完全一致。起草者の「must-fix 過大評価の疑い」に対し全モデルが案 1（軽い責務境界明記）を選択、案 2（依存逆転）は誰も採らず |
| 101 | F-005 | must | 案 1×5／別案×2 | 別案＝案 1＋再オープン手続き＋全体点検（実質案 1） |
| 102 | F-003 | must | 案 1×6／別案×1 | **枠組み伝染バイアス検出**（§4.2.3） |
| 103 | G-001 | must | 案 1×4／深掘×1／質問×1／別案×1 | 非決定・別案いずれも案 1＋再オープン手続き＋全体点検（実質案 1） |
| 104 | F-004 | should | 案 1×6／案 2×1 | 案 2＝要件を 4 値に更新（遡及） |
| 105 | F-006 | should | 全 7 案 1 | 完全一致 |
| 106 | F-007 | should | 案 1×4／案 2×1／別案×2 | 別案＝schemas/ 専用サブ階層（案 1 の精緻化） |
| 107 | F-009 | should | 案 1×2／別案×5 | **起草者バイアス検出**（§4.2.2） |
| 108 | F-012 | should | 案 1×6／別案×1 | 別案＝案 1＋new_discipline テストの検証可能形定義 |
| 109 | F-014 | should | 案 1×3／案 2×2／別案×2 | 別案＝案 1 と案 2 の統合（目的と手段） |
| 110 | G-004 | should | 全 7 案 1 | 完全一致 |

#### 4.2.2 topic-107（F-009）— 起草者バイアスの検出と補正

起草者（Opus、メインセッション）は案 1（T-010 の前提に T-008 を追加）を選んだが、**5 モデルが独立に同じ別案に収束**：前提を「硬い依存（着手前提）」と「緩い依存（完了検証前提）」に区別し、T-008 だけでなく**起草者が見落とした T-002 も緩い依存として追加**する。案 1（過剰直列化）と案 2（不整合の隠蔽）の両方の弱点を回避。利用者は起草者案 1 を撤回し**別案を採用**（人評価 `topic-107-human.yaml`、2026-05-29「はい」）。

#### 4.2.3 topic-102（F-003）— 枠組み伝染バイアスの検出と補正

採用率の計算式。6 モデル（起草者含む）が案 1（§12.5 を分子 approved のみに統一）を選んだが、これは**起草者がプロンプト深掘り欄に「§12.5 だけが孤立した誤記」「§12.1 が設計意図に合う」と自説の結論を書き込んだため、6 モデルが案 1 に誘導された**結果である。Gemini-3.5-flash だけが枠組みを破り「分子 approved のみ・分母に superseded を含めると、改善（上書き）のたびに却下なしで採用率が下がる不条理（悪いインセンティブ）」を提起。利用者は「他はどうなのか」と問い返したうえで少数派を採用し、**案 2（superseded を分子・分母の両方に含める：採用率＝(approved＋superseded)÷(approved＋rejected＋superseded)）に確定**（人評価 `topic-102-human.yaml`、2026-05-29）。superseded は却下されたのではなく一度は採用されたものであり、self-improvement の目的（規律の継続的改善）を罰する指標は目的と矛盾する、という判断。**多数決なら不条理な式が通っていた**。

#### 4.2.4 方法論上の発見：枠組み伝染バイアスと再発防止ガイドライン

topic-102 と topic-107 の対比（同一実験内の自然対照）から、**起草者が問題文に書いた枠組み・結論がレビューするモデル群に伝染する**現象を実証的に検出した。結論を押し付けた topic（102）は 6 モデルが同調し、押し付けなかった topic（107）は 5 モデルが自由に発想してより良い別案を出した。検出機構は 4 種（深掘り欄への自説結論注入／評価語／事実の片面提示／二択アンカリング）。

利用者指示（2026-05-29「重要な議論なので、記録に残し、今後のプロンプト作成時のガイドラインにすること」）により、実験ノート `docs/experiments/n-model-comparison.md` §3.4.2 に「セッション 39 の追加教訓：枠組み伝染バイアス」として再発防止ガイドライン（深掘り欄は事実としての後段影響だけ／両面に切れる事実の併記／前提を疑う別案の明示的歓迎／起草後の自己検査 7〜9 項目）を追記した。

#### 4.2.5 全 12 topic の利用者確定結果

利用者議論（2026-05-29 セッション 39）で 12 件すべてを確定。人本人判定を `tools/experiments/results/topic-NN-human.yaml` に保存（12 件）。

| topic | 所見 | 確定 | 主な反映先 |
|---|---|---|---|
| 99 | G-002 採番衝突 | 案 1（全 4 ディレクトリ走査） | design §8.5 ＋ tasks T-004 |
| 100 | G-003 依存逆転 | 案 1（責務境界明記、実装順維持） | design §8.9 ＋ tasks T-004／T-005 |
| 101 | F-005 metrics 配置 | 案 1（§11.1 に追記）＋再オープン＋全体点検 | design §11.1 |
| 102 | F-003 採用率 | **案 2**（superseded を分子分母両方に） | design §8.6・§12.1・§12.5 ＋ tasks T-008 |
| 103 | G-001 陳腐化 | 案 1（§13.3・§19.3 更新）＋再オープン＋全体点検 | design §13.3・§19.3 |
| 104 | F-004 source 差分 | **案 2**（要件を 4 値に更新） | requirements Req 4 受入 2 |
| 105 | F-006 命名 | 案 1（命名規約明記） | tasks T-001 |
| 106 | F-007 スキーマ配置 | 案 1＋schemas/ 専用サブフォルダ | design §11.1 ＋ tasks T-001／T-004 |
| 107 | F-009 前提 | **別案**（hard/soft 区別＋T-002 追加） | tasks T-010 |
| 108 | F-012 テスト | 案 1＋new_discipline は検証可能形を先に定義 | tasks T-004 |
| 109 | F-014 path 検証 | **別案**（案 1 と案 2 を統合） | design §8.4 ＋ tasks T-004 |
| 110 | G-004 MV-3 | 案 1（空値スキップ） | design §17.1 ＋ tasks T-009 |

起草者・多数決と利用者判断が分かれた 3 件：topic-107（起草者バイアス、§4.2.2）／topic-102（枠組み伝染バイアス、§4.2.3）／topic-104（少数派採用、6 モデル案 1 に対し利用者は案 2）。

### 4.3 反映箇所

確定 12 件を上流順（要件 → 設計 → tasks）に反映。承認済みの requirements／design は A-2 再オープン手続き（`docs/reviews/reopen-classification-2026-05-29.md`、進行中状態 `stages/in-progress/reopen-procedure-2026-05-29.yaml`）で修正。

**requirements.md**
- Req 4 受入 2：source 値域を 3 値 → 4 値（`observation_pattern` 追加、topic-104）

**design.md**
- §8.4：target_discipline_path に pattern 制約注記（topic-109）
- §8.5：採番手順を全 4 ディレクトリ走査に（topic-99）
- §8.9：status_change の statistical_evidence 責務境界（生成は §9.2／T-005）を明記（topic-100）
- §8.6・§12.1・§12.5：採用率を (approved＋superseded)／(approved＋rejected＋superseded) に統一（topic-102、案 2）
- §11.1：配置図に metrics/ と schemas/ を追記、スキーマ配置方針（正本性で分離＋schemas/ サブフォルダ）を記述（topic-101・topic-106）
- §13.3（619 行）・§19.3（931 行）：A-011／A-016 を「対処済み」に更新（topic-103、全体点検で他に陳腐化なしを確認）
- §17.1：MV-3 に「materialization_commit_hash が空なら正常スキップ」を明記（topic-110）

**tasks.md**
- T-001：schemas/ サブフォルダの配置・命名規約（topic-105・topic-106）、完了条件・テスト要件更新
- T-004：採番全 4 ディレクトリ（topic-99）、責務境界（topic-100）、スキーマパス schemas/（topic-106）、全 5 種別テスト（topic-108）、target_discipline_path pattern 完了条件・テスト（topic-109）
- T-005：statistical_evidence 生成責務の明記（topic-100）
- T-008：採用率式を案 2 に（topic-102）
- T-009：MV-3 空値スキップ（topic-110）
- T-010：前提タスクを硬い依存／緩い依存に区別＋T-002 追加（topic-107）、schemas/ による誤参照排除注記（topic-106）
- 全スキーマパスを `schemas/` サブフォルダに統一（topic-106 整合）

**全体点検（topic-101／103 条件）**：requirements・design を点検し、§11.1・§13.3・§19.3 以外に同種の配置漏れ・陳腐化記述がないことを確認（design §19.3 は「未消化なし」に更新済み）。

### 4.3 反映箇所

（確定した対処を tasks.md／design.md のどこに反映したかをここに記録する。）

*（未記入：利用者議論で確定後に追記）*

### 4.4 機能横断段への持ち越し

- A-019（workflow-management T-010 の approved_update スキーマと self-improvement §8.4 正本の不一致）：本機能の tasks 段では機能内対処せず、DVT-S001 で追跡。機能横断段（tasks review-wave）で workflow-management 側を §8.4 に整合させる方向で消化。
- 本 triad-review で新たな機能横断波及所見は検出されなかった（must-fix 5 件はすべて self-improvement 内の tasks.md／design.md で完結する遡及・機能内対処）。
