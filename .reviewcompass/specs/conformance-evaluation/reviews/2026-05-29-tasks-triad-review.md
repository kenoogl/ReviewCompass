---
type: tasks_triad_review
target: .reviewcompass/specs/conformance-evaluation/tasks.md
target_commit: 9be3501
target_content_hash: <未計測、セッション 39 起草分（T-001〜T-013）>
date: 2026-05-29
mode: subagent_mediated
session: session-39
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: 約 2.5
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: 約 2.5
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
    by_severity: { CRITICAL: 2, ERROR: 8, WARN: 7, INFO: 3 }
    count: 20
  adversarial:
    by_counter_status: { counter_evidence_raised: 7, no_counter_evidence_after_challenge: 13 }
    independent_findings: { ERROR: 2, WARN: 2, INFO: 1 }
    count: 25
  judgment:
    by_judgment: { must-fix: 2, should-fix: 9, leave-as-is: 5 }
    by_waterfall: { 機能内対処: 7, 遡及: 2, 波及: 0, 延期: 0 }
    論点群数: 16
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（他機能 tasks-triad-review と同配置）
  - tasks 観点 7 つは計画書 §5.9.2 で言及のみで本体未整備、foundation tasks-triad-review（セッション 30）の仮設定を継承
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの事実主張はメインセッションで事後検証（計画書 §5.23.12.7）。本記録 §1.2／§2.3 に主役の CRITICAL 2 件が格下げされた経緯と、敵対役 G-003（axis 値域矛盾）・確定事実（A-011/A-012 対処済み）の検証結果を明記
  - 3 役の生出力はサブエージェントログから復元可能
---

# レビュー記録：conformance-evaluation tasks triad-review

本記録は conformance-evaluation 機能の tasks.md（13 タスク T-001〜T-013、コミット `9be3501`）に対する 3 役レビューの結果である。3 役配置「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は仮設定 7 観点（上流仕様の網羅／タスク粒度／依存順の整合性／完了条件の機械判定可能性／テスト要件の妥当性／機能横断波及の早期検出／成果物配置と命名の整合）を網羅実施。20 件の所見（CRITICAL 2／ERROR 8／WARN 7／INFO 3）を提示した。

### 1.1 主役所見一覧（20 件、F-001〜F-020）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| F-001 | 3 | CRITICAL | T-008 前提タスク欄 | T-008（3 役レビュー機構）の前提が「T-001」のみで T-005（6 criteria）欠落。変更意図フロー図と不一致 | fact |
| F-002 | 3 | ERROR | T-009 前提タスク欄 | T-009（評価記録）前提が T-003/T-004 のみで T-006（推定）/T-007（比較）欠落。評価記録スキーマが推定・比較出力に依存 | fact |
| F-003 | 3 | ERROR | T-011 前提タスク欄 | T-011（接合面）前提に T-005/T-008 欠落 | fact |
| F-004 | 3 | WARN | T-012 前提タスク欄 | T-012（機械検査）前提に T-006/T-007 欠落（MV-5 が推定根拠形式に依存） | fact |
| F-005 | 1 | ERROR | 要件追跡表 Req8受入2 | Req8受入2 が T-011 のみ。分離の機械検証 T-012(MV-3)・運用文書化 T-001 が未追跡 | fact |
| F-006 | 1 | ERROR | 要件追跡表 Req1受入1 | Req1受入1 が「T-006＋全タスク（スコープ前提）」で曖昧、照合除外 T-005(§8.2) 未追跡 | fact |
| F-007 | 4 | CRITICAL | T-004 完了条件2／T-012 完了条件3 | MV-6（遮断必須）の完了条件が実質機械判定不能。プロンプトログの形式・場所・grep コマンドが未具体化 | mixed |
| F-008 | 4 | ERROR | T-004 テスト要件 | feature-partitioning が推定時に正しく渡される（遮断されない）ポジティブ確認テストが欠如 | fact |
| F-009 | 5 | ERROR | T-006 テスト要件 | intent 推察テスト（軽量 triad-review 適用）が欠如 | fact |
| F-010 | 5 | ERROR | T-003 テスト要件 | feature-partitioning 候補提示の出力形式テストが欠如 | fact |
| F-011 | 5 | WARN | T-007 テスト要件 | CF/JD 発番テストが衝突回避のみ、最初の採番・桁拡張境界未記載 | fact |
| F-012 | 5 | WARN | T-004 テスト要件 | オプション機能テストが CLI 引数 `--check-partitioning` を参照していない | fact |
| F-013 | 2 | WARN | T-002／T-008 責務欄 | T-002 責務に「6 criteria/3役への参照確立」がありモード切替の責務を超える | fact |
| F-014 | 2 | WARN | T-005 成果物・完了条件4 | conformance_evaluation.yaml が DVT-C001 で配置延期なのに完了条件4 に組み込み、完了判定が曖昧 | fact |
| F-015 | 6 | ERROR | tasks.md 持ち越し事項／design §20.1 | tasks（phase:tasks）が「triad-review で確認する」は時系列不整合。A-011/A-012 対処済みなら本文断言すべき | fact |
| F-016 | 6 | WARN | DVT-C002 | 「機能横断段（tasks review-wave）」の括弧書きが誤解を招く | fact |
| F-017 | 7 | ERROR | T-001 成果物／design §12.2・§18.2 | tools/conformance_evaluation/schemas/ が design に記載なし（設計側の明示欠如） | mixed |
| F-018 | 7 | WARN | T-001 成果物 | CONFORMANCE_EVALUATION.md 追記が既存/新規か曖昧 | fact |
| F-019 | 1 | INFO | 要件追跡表 Req3受入7 | 判定値保持が T-008 のみ、T-007(§10.4 judgment_id) 未追跡 | fact |
| F-020 | 1 | INFO | design §20.1／tasks.md 持ち越し事項 | design §20.1 が A-011/A-012「消化予定」、tasks「対処済み」で不一致（F-015 同根） | mixed |

### 1.2 主役の注目発見と、メインセッションによる事後検証

主役は最も危険な所見として F-001（T-008 前提の T-005 欠落、CRITICAL）と F-007（MV-6 完了条件が機械判定不能、CRITICAL）を挙げた。

**メインセッション（起草者 Opus 4.7）による事後検証**（計画書 §5.23.12.7 準拠）：主役の CRITICAL 2 件はいずれも敵対役の反証により格下げされた（§2.3）。F-001 は T-008（3 役レビュー機構）が §11.3 で §5.9 規律のメタ流用を担うのみで axis/criterion_id を生成せず（それは T-006/T-007 の責務）、T-005 を直接必要としないため CRITICAL は過大。F-007 は design §7.3 に第 1 期の遮断手順 4 項目があり §18.1/§18.4 に運用が定義済みのため「実質機械判定不能」は言い過ぎ。真に実装段を止める致命性を持つのは、主役が見落とし敵対役が発見した **G-003（axis 値域矛盾）** と、self-improvement topic-103 と同型の **design §20.1 陳腐化（F-015 群）** であった。前回（self-improvement）と同じく、起草者・主役が見落とした構造的欠陥を敵対役が補正した。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への counter_status 付与（20 件）

counter_evidence_raised（反証あり＝severity 過大の指摘）は 7 件（F-001／F-003／F-005／F-007／F-009／F-013／F-017）、残り 13 件は no_counter_evidence_after_challenge（同意）。

| 主役 ID | counter_status | 要旨 |
|---|---|---|
| F-001 | counter_evidence_raised | T-008 は §11.3 のメタ流用が主体、axis/criterion_id は T-006/T-007 が生成。T-005 を直接必要としない。CRITICAL→WARN 相当 |
| F-002 | no_counter_evidence_after_challenge | 評価記録は推定・比較出力に内容依存、前提明示が弱い。ただし推移依存で破綻せず WARN 寄り |
| F-003 | counter_evidence_raised | T-011 前提の T-006 が既に T-005 を前提に持つため推移的に充足。T-008 は接合面に直接寄与せず。ERROR→INFO/WARN |
| F-004 | no_counter_evidence_after_challenge | MV-5 は推定根拠形式に依存、T-012 前提に T-006 欠落は事実。MV-5 は警告続行可粒度のため WARN 妥当 |
| F-005 | counter_evidence_raised | Req8受入2 は責務の所在宣言で MV-3 検証対象は Req8受入4（T-001+T-009 で追跡済み）。ERROR 過大 |
| F-006 | no_counter_evidence_after_challenge | Req1受入1 の「全タスク（スコープ前提）」は曖昧、照合除外 T-005 未追跡は妥当。ERROR→WARN 相当 |
| F-007 | counter_evidence_raised | design §7.3 に手順 4 項目＋§18.1/§18.4 に運用定義あり。「機械判定不能」は言い過ぎ。CRITICAL→ERROR/should-fix |
| F-008 | no_counter_evidence_after_challenge | feature-partitioning 尊重のポジティブ確認テスト明示が弱い、所見妥当。WARN 寄り |
| F-009 | counter_evidence_raised | T-006「階層別扱いテスト」が intent 参考扱いを包含しうる。ERROR→INFO/WARN |
| F-010 | no_counter_evidence_after_challenge | candidates.md 出力形式テストの欠落は妥当 |
| F-011 | no_counter_evidence_after_challenge | 最初の採番・桁拡張境界テスト未記載は妥当。WARN |
| F-012 | no_counter_evidence_after_challenge | `--check-partitioning` 未参照は事実。WARN |
| F-013 | counter_evidence_raised | モード入口が共有構造参照を持つのは自然。WARN→INFO |
| F-014 | no_counter_evidence_after_challenge | DVT-C001 延期中の yaml を完了条件4 が要求する矛盾、所見妥当。WARN |
| F-015 | no_counter_evidence_after_challenge | A-011/A-012 対処済み（pending 166/190 行）、design §20.1 陳腐化。tasks の時系列宣言は不整合、本文断言すべき。ERROR 妥当（重要） |
| F-016 | no_counter_evidence_after_challenge | 「機能横断段（tasks review-wave）」括弧書きは消化段の誤解を招く。WARN |
| F-017 | counter_evidence_raised | schemas/ は §9.4/§8.5/T-009 から導出可能。ERROR→INFO/WARN |
| F-018 | no_counter_evidence_after_challenge | CONFORMANCE_EVALUATION.md は A-001 で既存と判明、追記/新規が曖昧。WARN |
| F-019 | no_counter_evidence_after_challenge | judgment_id 発番は T-007 だが受入7 の趣旨は T-008 で満たす。INFO |
| F-020 | no_counter_evidence_after_challenge | F-015 同根。design §20.1 と tasks/pending の不一致。INFO |

### 2.2 敵対役の独立所見（5 件、G-001〜G-005）

| ID | 観点 | severity | target_location | description（要約） | evidence_type |
|---|---|---|---|---|---|
| G-001 | 依存順記述の食い違い | ERROR | tasks.md 変更意図 §依存順（行325） | 変更意図の依存順記述の矢印（T-002/T-008 を T-006 と同列に置く）とタスク前提欄（T-002/T-008 は T-001 直後）が構造的に食い違う | fact |
| G-002 | MV-7 の追跡漏れ | WARN | T-012 前提／MV-7 | MV-7（foundation 受入番号照合）の検査対象を生む T-006/T-008/T-004 と T-012 の依存欠落 | inference |
| G-003 | axis 値域矛盾 | WARN | T-005／§10.5／§14.5 | T-005（axis 2 値 fail-closed）と §10.5・§14.5（axis 3 値、intent 含む）が衝突。3 値目 intent をどのタスク責務とするか未確定 | fact |
| G-004 | 安全性語彙と実体の時期ギャップ | INFO | MV-6／DVT-C004 | MV-6「遮断必須」の技術実体（DVT-C004）がフェーズ 4 第 2 サイクル延期、第 1 期は手動のみ | fact |
| G-005 | 双方向依存（循環） | WARN | T-002↔T-003/T-004 | T-002 が振り分け先（T-003/T-004）存在を完了条件に、T-003/T-004 が T-002 を前提に。循環の解き方未明示 | fact |

### 2.3 敵対役の総評

1. design §20.1 の陳腐化と tasks の時系列宣言（F-015/F-020、確度高）：A-011/A-012 は対処済みだが design §20.1 が「消化予定」のまま。self-improvement 同型。
2. **axis の値域矛盾（2 値 vs 3 値、G-003、確度中〜高）**：主役 20 件が見落とした構造的欠陥。T-005（2 値 fail-closed）と §10.5/§14.5（3 値 incl intent）の衝突。
3. MV-6「遮断必須」の名目と実体の時期ギャップ（F-007 緩和版＋G-004、確度中）：主役の CRITICAL は過大、実体は ERROR/should-fix。

---

## 3. 判定役判定（judgment、Opus 4.7）

判定役は主役 20 件＋敵対役独立 5 件＝25 件を 16 論点群に集約し、最終判定を下した。

### 3.1 by_judgment 集計

- **must-fix：2 論点**（G-003 axis 値域矛盾 ／ F-015・F-020・G-001陳腐化部分＝A-011/A-012 陳腐化）
- **should-fix：9 論点**（F-001 ／ F-002・F-004・G-002 ／ F-006 ／ F-007 ／ F-008・F-010 ／ F-011・F-012・F-014・F-016・F-018 ／ F-017 ／ G-005）
- **leave-as-is：5〜6 論点**（F-003 ／ F-005 ／ F-009 ／ F-013 ／ F-019 ／ G-004）

主役の CRITICAL 2 件（F-001／F-007）はいずれも維持せず格下げ（F-001→should-fix 相当、F-007→should-fix）。真に実装段を止める must-fix は G-003 と F-015 群の 2 件のみ。

### 3.2 判定役の総括（実装段前に必ず対処すべき must-fix）

いずれも **design.md の遡及修正**を要する。

1. **G-003（axis 値域矛盾）— 最優先**：design 内部で axis が 2 値（§8.1/§9.4/§10.4/§20.3）と 3 値（§10.5 の `axis: intent`／§14.5 の必須フィールド）に分裂。tasks T-005 完了条件1「axis 2 値 fail-closed」が §10.5/§14.5 と衝突し、そのまま実装すると intent 差異記録を弾く。design 段で「2 値＋intent 別フィールド」か「3 値拡張」かを確定し、§10.5・§14.5・§8.1・§9.4・§10.4・§20.3 を一貫させ T-005 完了条件に伝播。利用者と議論のうえ確定すべき論点。
2. **F-015/F-020/G-001陳腐化（A-011/A-012 陳腐化）**：A-011/A-012 は対処済み（pending 166/190 行）だが design §20.1 が「消化予定」と陳腐化。design §20.1 を「対処済み」に修正し、tasks.md「持ち越し事項」の「triad-review で確認する」を本レビュー完了を踏まえた確定記述に改める。

補足（must-fix でないが実装前に整えると混乱を防げる should-fix）：G-005（T-002↔T-003/T-004 の循環の解き方未明示、完了条件の表現を「ディスパッチ機構の確立」に整える）、F-014（DVT-C001 延期中 yaml を T-005 完了条件4 が要求する文言矛盾）。

---

## 4. 統合節（メインセッションによる集約）

### 4.1 must-fix 2 件の対処方針案（利用者議論用、各案に後段影響）

本節は規律 [must-fix-discussion-obligation] に従い、各 must-fix に対処方針の選択肢と後段影響を整理する。**確定は利用者議論を経てから**。

#### must-fix-1：G-003 axis 値域矛盾

- **事実**：照合対象の axis は 2 値（requirements/design、§8.1）。だが intent 差異記録（§10.5）は `axis: intent` を「独立軸として例外的に追加」、analysis 出力必須フィールド（§14.5）は「3 値（requirements/design/intent）」。起草完了基準 §20.3 は「2 値」と書く。tasks T-005 完了条件1 は「axis 2 値、未知 axis は fail-closed」で、axis=intent を弾く。
- **案 1**：**axis は照合対象の 2 値（requirements/design）に固定し、intent は別フィールド扱い**にする。intent 差異記録は `axis` を使わず `reference_axis: intent` 等の別フィールドに分離。§10.5・§14.5 を「intent は axis でなく参考情報専用フィールド」に修正、§14.5 の必須フィールドから intent を外し参考フィールドに。T-005 の 2 値 fail-closed は維持。
  - 後段影響：照合の中心構造（2 軸 6 criteria）が単純なまま保たれ、intent の参考情報性（must-fix 対象外）がフィールド構造でも明確化。design §10.5/§14.5 の修正が必要。
- **案 2**：**axis を 3 値（requirements/design/intent）に拡張**し、intent は「参考情報専用の軸（must-fix 対象外）」と位置づける。T-005 完了条件を「axis 3 値、ただし intent は参考情報専用」に修正、§8.1/§9.4/§10.4/§20.3 を 3 値に統一。
  - 後段影響：axis が 3 値になり「2 軸 6 criteria」という設計の看板（Decision 4）と表現が衝突。6 criteria は requirements/design の 2 軸のままなので、axis 値域（3 値）と criteria 軸（2 軸）が別概念になり、かえって混乱を招く恐れ。
- 私の評価：**案 1 が優れる**。Decision 4「2 軸 6 criteria」の設計思想を保ち、intent の参考情報性を構造で表現できる。案 2 は axis という語に「照合軸」と「記録上の軸」の二義を持たせ混乱を招く。ただし設計の意図確定は利用者判断。

#### must-fix-2：F-015/F-020/G-001陳腐化（A-011/A-012 陳腐化）

- **事実**：A-011/A-012 は対処済み（正本 pending 166/190 行、セッション28）。design §20.1 行1005-1006 が「design レビュー波段で消化予定」と陳腐化。tasks.md「持ち越し事項」は「対処済み」と正しく書くが「triad-review で確認する」と未完了形が残る。
- **案 1（推奨）**：design §20.1 の A-011/A-012 記述を「✅ 対処済み（セッション28、出典 pending 166/190 行）」に更新。tasks.md「持ち越し事項」の「triad-review で確認する」を「本 triad-review で確認済み、A-011/A-012 は対処済み」と確定記述に改める。§14.3/§14.5 等で A-011 を参照している箇所も対処済み前提に整える。
  - 後段影響：状態の真実源（pending）と design が整合し、後続の機能横断段で「未消化」誤認による二重処理を防ぐ。self-improvement topic-103 と同じ対処。
- 私の評価：self-improvement と完全に同型。案 1 で異論の余地が小さい。なお design は approval 完了済みのため、A-2 再オープン手続き（軽量、§5.23.13）の要否を利用者と確認する必要がある（self-improvement と同じ）。

#### should-fix の主な対処方針（議論短縮用、まとめて確認可）

- 依存順の明示漏れ（F-002/F-004/G-002）：推移依存で実害なし。前提タスク欄に「緩い依存（完了検証前提）」として明記すれば追跡精度が上がる（self-improvement topic-107 の hard/soft 区別を流用可）
- G-005（T-002↔T-003/T-004 循環）：T-002 完了条件を「振り分け先パイプラインへのディスパッチ機構の確立（実体完成でなくインタフェース確立）」に整える
- F-014：T-005 完了条件4 を「conformance_evaluation.yaml はフェーズ 2 配置後に 6 criteria 網羅を整合確認（DVT-C001）」に整え、延期と完了条件の矛盾感を消す
- F-006/F-019：要件追跡表に T-005（§8.2 照合除外）／T-007（judgment_id）を追記
- F-008/F-010/F-011/F-012：テスト要件の補強（feature-partitioning ポジティブ確認／候補提示形式／発番境界／--check-partitioning）
- F-007/F-017/F-016/F-018：MV-6 プロンプトログ形式の明記方針／schemas/ の design 追記／DVT-C002 括弧書き／CONFORMANCE_EVALUATION.md 既存明記

### 4.2 利用者議論履歴

7 モデル比較実験（topic-111〜120、10 件 × 7 モデル）を実施。**完全一致 6 件、割れ 4 件（すべて 6 対 1）**。前回 self-improvement で確立した枠組み伝染バイアスの再発防止ガイドライン（深掘り欄に結論を書かない／両面の事実併記／前提を疑う別案を歓迎）を適用。**今回は起草者バイアスが出ず、起草者（Opus）の判定が全 10 件で多数派と一致**。利用者議論（2026-05-29 セッション 39）で 10 件すべてを確定、人本人判定を `tools/experiments/results/topic-NN-human.yaml`（111〜120）に保存。

| topic | 所見 | 確定 | 分布 |
|---|---|---|---|
| 111 | G-003 axis 矛盾 | 案 1（axis 2 値固定・intent 別フィールド） | 全 7 案 1 |
| 112 | F-015 design 陳腐化 | 案 1（§20.1 更新＋全体点検） | 全 7 案 1 |
| 113 | F-001 T-008 前提 | **別案**（案 2＋変更意図フロー図修正） | 案 2×6／別案×1 |
| 114 | F-002 依存順 | 案 1（緩い依存を明記） | 案 1×6／別案×1 |
| 115 | F-006 追跡表 | 案 1（T-005／T-007 追記） | 全 7 案 1 |
| 116 | F-007 MV-6 ログ | **別案**（最小仕様＋DVT 連動） | 案 1×6／別案×1 |
| 117 | F-008 テスト | 案 1（肯定確認・候補提示） | 全 7 案 1 |
| 118 | F-011 群 細部 | 案 1（5 件まとめ整備） | 全 7 案 1 |
| 119 | F-017 schemas/ | 案 1（設計に 1 行追記） | 全 7 案 1 |
| 120 | G-005 循環 | 案 1（完了条件言い換え） | 案 1×6／別案×1 |

利用者が別案を採用した 2 件：topic-113（Gemini-3.1-pro の「案 2＋フロー図修正」、文書間整合まで担保）／topic-116（Sonnet API の「段階的具体化＝最小仕様を今＋詳細は DVT 連動」、最重要検査の安全性と未確定性の両立。起草者も当初案 1 から見直して同意）。

### 4.3 反映箇所

確定 10 件を上流順（design → tasks）に反映。承認済み design は A-1 再オープン手続き（`docs/reviews/reopen-classification-2026-05-29-conformance.md`、進行中状態 `stages/in-progress/reopen-procedure-2026-05-29-conformance.yaml`）で修正。要件（requirements）の修正はなし。

**design.md**
- §10.5：intent 差異記録の axis を `reference_axis: intent` 別フィールドに分離（topic-111）
- §14.5：analysis 出力の必須フィールド axis を 2 値に、`reference_axis` を任意フィールドに（topic-111）
- §20.1（1005-1006 行）：A-011／A-012 を「対処済み」に更新（topic-112）
- §14.3（721 行）：role_diff_report.json の「追加予定」を「対処済み」に更新（topic-112）
- §18.2：tools/conformance_evaluation/schemas/ の配置を 1 行追記（topic-119）

**tasks.md**
- T-002 完了条件 3：ディスパッチ機構の確立に言い換え、循環解消（topic-120）
- T-005 完了条件 1：axis 2 値固定・intent 別フィールド分離を明記（topic-111）／完了条件 4：フェーズ 2 配置後の整合確認に整える（topic-118 F-014）
- T-008 責務：責務境界（axis/criterion_id は T-006/T-007、T-008 は T-005 不要）を明記（topic-113）
- T-009／T-012 前提：硬い依存／緩い依存を区別し T-006／T-007 を緩い依存に明記（topic-114）
- T-012 責務：MV-6 第 1 期最小仕様（ログ必須フィールド・命名規則・grep 雛形）を記述＋DVT-C004 連動（topic-116）
- T-003／T-004 テスト要件：候補提示形式・feature-partitioning 肯定確認・--check-partitioning を追加（topic-117・topic-118）
- T-007 テスト要件：発番境界（最初の採番・桁拡張）を追加（topic-118 F-011）
- 要件追跡表：Req1受入1 に T-005、Req3受入6/7 に T-007 を追記（topic-115）
- 変更意図の依存順フロー図：T-001 から T-005／T-002／T-008 が並列分岐するよう整合修正（topic-113）
- DVT-C002：括弧書き「機能横断段（tasks review-wave）」を明確化（topic-118 F-016）
- T-001：CONFORMANCE_EVALUATION.md を既存ファイルへの追記と明記（topic-118 F-018）

**全体点検（topic-112 条件）**：design を点検し、§20.1／§14.3／§14.5 以外に同種の陳腐化記述・axis 3 値残存がないことを確認（信頼度ラベル・correspondence_type の 3 値は別概念）。

### 4.4 機能横断段への持ち越し

- A-017／A-018／A-019（既登録の未消化所見）：本機能の tasks 段では機能内対処せず、機能横断段（tasks review-wave）で一括消化。
- DVT-C002（workflow-management のスキーマ拡張＝連想配列構造の許容との整合）：機能横断段で workflow-management 側と突き合わせ。
- 本 triad-review で確認した design §20.1 の A-011/A-012 陳腐化（must-fix-2）は機能内の遡及修正で対処（持ち越しでない）。
- 7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施（2 回方式、計画書 §5.5 ／ §5.9.6）。
