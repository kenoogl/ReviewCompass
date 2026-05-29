---
date: 2026-05-29
session: 40
auditor: claude_code_main_session + 7 subagents (sonnet)
purpose: tasks フェーズ approval 前の 2 軸整合性チェック（縦軸＝intent→tasks、横軸＝機能間）
note: 本記録は §5.12 改訂時に「alignment 段の正本手順」を正本化する際の検証済み実例として参照する（事後正本化方針、2026-05-29 利用者決定）
---

## 0. 実施方法

- **縦軸**：機能ごとに検証役サブエージェント（Sonnet）を 1 体ずつ、計 7 体を並列起動。各々が requirements.md／design.md／tasks.md を全文通読し、(1) design→tasks 被覆漏れ (2) 浮いたタスク (3) requirements→design 被覆 (4) 確定値の不一致 (5) 未解決ブロッカー の 5 観点で「事実のみ」報告（修正案・重大度判断はさせない＝枠組み伝染バイアス回避）。
- **横軸**：メインセッション（Opus）が機能間契約（接合面・成果物配置・所有非重複・依存順）を確認。
- **統合**：縦横の所見を集約し、本物の断層だけを利用者に提示。

## 1. 縦軸監査の生件数（サブエージェント報告、未検証）

| 機能 | 1.被覆漏れ | 2.浮いたタスク | 3.req→design | 4.値不一致 | 5.ブロッカー | 計 |
|---|---|---|---|---|---|---|
| foundation | 2 | 0 | 2 | 1 | 0 | 5 |
| runtime | 5 | 0 | 0 | 2 | 3 | 10 |
| evaluation | 4 | 2 | 1 | 2 | 1 | 10 |
| analysis | 4 | 3 | 3 | 3 | 2 | 15 |
| workflow-management | 5 | 3 | 1 | 4 | 1 | 14 |
| self-improvement | 2 | 1 | 0 | 1 | 1 | 5 |
| conformance-evaluation | 3 | 0 | 1 | 3 | 1 | 8 |
| **計** | 25 | 9 | 8 | 16 | 9 | **67** |

※ これらはサブエージェントの生報告であり、メインセッションによる検証（真偽・重大度）は未実施。後述の triage で分類する。

## 2. 横断的なパターン（テーマ）

生 67 件を見ると、機能をまたいで同型の所見が繰り返し出ている：

- **T-1（複数機能）design §先送り論点が tasks の DVT に引き継がれていない**：runtime（5件）・evaluation（8項目）・workflow-management（§機能依存マップ §6 の変更検知）。design 段で「alignment gate で詰める」とした論点が tasks の遅延確認事項テーブル（DVT）に転記されておらず、実装着手前提が不明確になっている恐れ。
- **T-2（複数機能）要件追跡表が受入単位でなく要件単位で集約**：analysis・conformance-evaluation。design.md の追跡表が「Req N → §節」で集約され、受入基準（受入 1／2/3…）の個別行がない。tasks 側は受入単位で展開しているので、design↔tasks の追跡粒度が非対称。
- **T-3（複数機能）triad-review の F-xxx／A-xxx 対処で tasks に足した記述が design に逆反映されていない**：analysis（README 3件・配置分離・所有移管）・workflow-management（template_vars・差し戻し機構）・self-improvement（シンボリックリンク再作成）。tasks 段で正当に足した内容だが design に根拠節がない＝「浮いたタスク」に見える。
- **T-4（複数機能）確定値（スキーマ項目リスト・enum・件数）の design↔tasks 不一致**：evaluation の analysis_run_manifest.yaml（9項目の構成が design と tasks で 4 項目ずつ食い違う）、workflow-management の手戻り種別（design 定義から計算すると 15 種だが tasks は 14 種と記述）、runtime の V1（confidence_label の §判断7 引用が design に実体なし）。
- **T-5（複数機能）DVT は延期理由付きで実装ブロッカーではない**：各機能の大半の DVT は延期理由・解除トリガーが明記済みで、tasks 完了をブロックしない（運用ルール準拠）。

## 3. triage（メインセッションによる分類・暫定、要検証）

### A. 実装をブロックし得る／要対処（高）
- evaluation T-4：analysis_run_manifest.yaml の必須項目が design（行517-527）と tasks T-006（行105）で 4 項目ずつ食い違う。スキーマ実装の正本が二重で矛盾。**要検証・要確定**
- workflow-management T-4：手戻り種別の総数が design/requirements 定義では 15 種、tasks は「14 種」。trigger_map の網羅性に関わる。**要検証**
- workflow-management 5：DVT-W003 の解除に必要な `stages/discipline-update.yaml` が T-003 責務には「新設」とあるが成果物リストから欠落。**要検証**

### B. 記述の不整合（中、this-session 由来含む）
- conformance-evaluation T-4：**DVT-C002 が tasks 行344 で「解除済」だが行358 の機能横断段持ち越し事項では「機能横断段で消化」のまま**。今セッションの DVT-C002 解除（私の編集）で行358 の更新漏れ＝**this-session 由来の実在不整合**。
- runtime V1：tasks が「foundation 所有は §判断7 の全7件」と書くが、runtime/design.md §判断7 はパターン定義除外の節で語彙件数・confidence_label を含まない（引用先が design 内に実体なし）。

### C. ドキュメント粒度・低優先（記録のみで可の候補）
- T-2（要件追跡表の集約粒度）：内容は被覆、行粒度の非対称のみ。低。
- T-3（F-xxx 対処の design 逆反映漏れ）：tasks の追加は正当、design 逆反映は整形課題。低〜中。
- foundation の被覆漏れ2件・req→design 2件：入れ子 required の完了条件・節名表記（§配置）等、軽微。
- 各機能の DVT（延期理由付き）：ブロッカーでない。

### D. 横断テーマ T-1（design 先送り論点の DVT 未転記）
- 中〜高の可能性。design 段で先送りした論点が tasks に転記されず、実装が未確定前提で始まる恐れ。機能ごとに「先送り論点が本当に未解決のまま実装着手を許すか」を確認すべき。**要検証**

## 4. 横軸監査（メインセッション実施）

- **所有正本の非重複**：✓ 重複なし。foundation=語彙正本／runtime=phase_profile・treatment・step_outcome／evaluation=admission 3値・陳腐化伝播選択ロジック／analysis=maturity_label・limitation_type・fragment_type・regeneration_status／workflow-management=completion_predicate・verdict・手戻り種別記号・依存種別／self-improvement=提案 YAML スキーマ(§8.4)／conformance-evaluation=6 criteria・target_commit。
- **依存順（phase_order）**：✓ 整合。feature-dependency.yaml は workflow-management 単独所有、conformance-evaluation のみ連想配列構造（DVT-C002 で検証済み）。
- **主要接合面**：✓ A-019（self-improvement↔workflow-management）・DVT-C002（conformance↔workflow-management）検証済み。
- **残る doc gap（低）**：workflow-management 接合面が evaluation／analysis の要件追跡表に行として現れない（内容は接合面記述にあり、追跡表の粒度の問題）。

横軸に契約矛盾なし。

## 5. 検証済みの本物の断層（A・B 群、実ファイルで確認）

**B 群：今セッション（A-018 対処・alignment 補修）由来の不整合**
1. **conformance-evaluation/tasks.md**：DVT-C002 を行344 で「解除済」にしたが、行358（機能横断段への持ち越し事項）が「DVT-C002 も機能横断段で消化する」のまま。私の更新漏れ。→ 行358 修正
2. **runtime/tasks.md 行27・206**：私が補修で「foundation 所有は §判断7 の全7件」と書いたが、runtime/design.md の §判断7 は「パターン定義依存の除外」で語彙件数を含まない（7語彙の §判断7 は foundation/design.md 側）。引用先が曖昧・誤り。→ 「foundation/design.md §判断7」と明示するか §判断7 参照を外す

**A 群：既存の design↔tasks 不整合（今セッション以前から存在）**
3. **evaluation**：`analysis_run_manifest.yaml` の必須項目が design（行517-527：analysis_logic_version／input_run_set／generated_at／metric_set_version／phase_metric_profile_version／comparison_contract_version／protocol/runtime/prompt_set_version_coverage）と tasks T-006（行105：左記のうち generated_at・metric_set_version・phase_metric_profile_version・comparison_contract_version を欠き、代わりに analysis_run_id・analysis_started_at・analysis_completed_at・output_artifact_ids を持つ）で 4 項目ずつ食い違う。さらに tasks 行105 は「design 行517-527 で必須宣言、9項目：[tasks の異なるリスト]」と design を誤引用。→ どちらを正本にするか確定が必要（design 側に identity 項目を足すなら design 再オープン）
4. **workflow-management**：手戻り種別の総数が design/requirements の深さ値域（N:1＋R:2＋D:3＋A:4＋I:5）から 15 種だが、tasks は「14 種」と 4 箇所（行94・97・162・167）で記述。→ 14→15 へ訂正、または 1 種除外の根拠明示
5. **workflow-management**：T-003 成果物リスト（行82-90）に `stages/discipline-update.yaml` が無いが、T-010 行206 は「T-003 が discipline-update.yaml の枠を新設」と参照。DVT-W003 は段集合本体を後続に延期。枠の新設責務の所在が矛盾。→ T-003 成果物に枠を追加するか、T-010 の参照表現を修正

**T-1（横断テーマ）：design 先送り論点が tasks DVT に未転記**（runtime 5項目・evaluation 8項目・workflow-management）。design 段は承認済みのため「承認時に open のまま受容」か「解決済みで節が陳腐化」かの判別が要る。実装着手前提に関わる項目（例：evaluation の処理方式メトリクスの JSON Schema 詳細）は要確認。→ 機能ごとに判断

**C 群（低・記録のみ可）**：T-2（要件追跡表の集約粒度）／T-3（triad-review の F-xxx 対処の design 逆反映漏れ）／foundation の軽微な節名表記・入れ子 required の完了条件等。実装を妨げない整形課題。

## 6. 対処方針（利用者確定済み、2026-05-29 セッション40）

- **B群1（conformance DVT-C002 行358 等）**：✅ 修正済み（消化済みに更新）
- **B群2（runtime §判断7 引用）**：✅ 修正済み（foundation/design.md §判断7 と明示）
- **#3（evaluation manifest 項目食い違い）**：**案2＝evaluation design を再オープン**し analysis_run_manifest.yaml を「版管理4＋実行識別4＋共通5＝13項目」に統一、tasks T-006 も揃える（実行識別は Req 5 受入 2、版管理は Req 5 受入 5）
- **#4（手戻り種別 14 対 15）**：tasks の「14種」→「15種」訂正（workflow-management/tasks.md 4箇所、tasks のみ）。正本は 15 種（design 行451 の14他種別＋例示D-1、design 行435「完全二次元表記」）
- **#5（discipline-update.yaml 枠の所在）**：案(b)＝T-010 行206 の文言修正（discipline-update.yaml は DVT-W003 で後続確定、T-003 が枠を新設するのではない）。design 9ファイル体制は維持、tasks のみ
- **T-1（design 先送り論点の DVT 未転記）**：案(B)＝runtime（5項目）・evaluation（8項目）の design 先送り論点を各 tasks の DVT に転記（延期理由付き、workflow-management の DVT-W001〜W007 と同じ扱い）。design 再オープンせず
- **C群**：記録のみ、実装フェーズで随時整形

## 7. 手続き上の教訓（§5.12／workflow-management 正本化時に反映）

- **alignment 段は「design 先送り論点の解決状況」を確認すべき**：runtime・evaluation は design に「design alignment 段で詰める」と書いた先送り論点を、詰めた記録なしに design 承認まで通過させていた（T-1）。現在の alignment 段（自動整合判定）はこの確認を含んでいない。workflow-management の cross-spec-alignment.yaml 段集合の正本化時、alignment 段の完了述語に「上流フェーズの先送り論点が解決済みか、DVT として延期理由付きで転記済みか」を含めるべき。
- **2軸チェック（縦軸＝intent→tasks、横軸＝機能間）を alignment 段の正本手順に組み込む**：本監査の方法（§0）を alignment 段の標準手順の検証済み実例とする。
