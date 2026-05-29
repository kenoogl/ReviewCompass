---
date: 2026-05-29
classifier: claude_code_main_session
classification: A-1
trigger_source: foundation tasks/review-wave（機能横断段）で確定した上流（design）への遡及所見 A-018
feature: foundation
findings: [A-018(topic-121)]
---

## 分類根拠

本再オープンは foundation の tasks 段 review-wave（機能横断段）＋7 モデル比較実験で確定した遡及所見 A-018 を処理する。発見フェーズは tasks（起点記号 A）。戻る先は design（foundation/design.md 内部の語彙正本件数の自己矛盾）。よって種別は **A-1**（tasks で発見、design まで戻る、深さ 1）。

利用者は対処方針として「別案」を選択（2026-05-29 セッション 40）。別案の適用範囲は (ア)＝核心 1〜3 ＋補足 4 のすべて。再オープン手続きは軽量でなく正規手続き（REOPEN_PROCEDURE.md）を取ることを利用者が明示指定。

## 問題の事実（A-018）

foundation/design.md 内で「所有する語彙正本の件数」が 3 か所で食い違っている：

- §判断 7（行 594-602）：**7 件**列挙（counter_status／validator_status／evidence_class／review_mode／severity／final_label／confidence_label）＝最新で正しい
- 行 644（テスト戦略・語彙正本整合）：**4 件のみ**列挙（severity／final_label／confidence_label が欠落）＝検査対象の漏れ
- 行 736（変更意図）：「語彙正本数を 4 から 6 に拡張」＝confidence_label 追加が未反映

下流の analysis（7 件参照）／evaluation（6 件参照）は各機能の正しい参照範囲であり矛盾ではない（confidence_label は推定タスク用で、推定タスクを扱う analysis は参照し、扱わない evaluation は参照しない）。

## design まで戻る所見（深さ 1：A-1）

- **A-018（topic-121、語彙正本件数の自己矛盾）**：foundation/design.md の §判断 7・行 644・行 736 の件数記述を整合させ、所有数（全件）と各機能参照数（部分集合）の二層構造を明文化する

## trigger_map A-1 による連鎖再実施対象（計画書 §5.6）

- stages/design.yaml#alignment
- stages/design.yaml#approval
- stages/tasks.yaml#alignment
- stages/tasks.yaml#approval

drafting／triad-review／review-wave は再実施対象外（正本修正は手で行い、整合確認と承認のみ再実施）。foundation の tasks は現在 review-wave 進行中（alignment／approval はまだ false）のため、design 再承認後に通常フローで段通過する。implementation は未着手（全 false）。

## spec.json フラグ差し戻し（第1過程ステップ6、承認後に実行）

foundation/spec.json：
- `reopened.design`：false → **true**
- `workflow_state.design.alignment`：true → **false**
- `workflow_state.design.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["tasks"]**

## 正本修正の対象（第2過程で実施）

**foundation/design.md（核心、必須）**：
1. 行 644（実施済み）：語彙を 7 件再列挙するのではなく「§判断 7 が列挙する語彙正本のすべてが、それぞれの正本位置（実行メタデータ用は metadata_contract.yaml、finding／necessity_judgment 用は対応スキーマ、推定タスク用 confidence_label は §3.5）に正しく列挙されている」とし、§判断 7 を参照する方式に変更。あわせて二層構造の一文を追記。【厳密チェックでの是正】当初案の「4 語彙→7 語彙に再列挙」は、confidence_label が metadata_contract.yaml にも対応スキーマにも無い（§3.5 で「実行メタデータとは別に」所有）ため「metadata_contract.yaml に列挙」と書くと偽の主張になる。よって再列挙をやめ §判断 7 参照＋正本位置の明示に是正
2. 行 736（**要確認・後述**）：書き換えではなく追記方式。行 736（4→6、セッション 25 の正確な履歴）は残し、抜けているセッション 28（confidence_label 追加、6→7、A-013）の変更意図記録を追記する。「4→7 に書き換え」は履歴改ざんになるため不可
3. 行 602（§判断 7 末尾、実施済み）：二層構造を追記。固定件数（analysis 7／evaluation 6）は埋め込まず「推定タスクを扱う機能は confidence_label を含め、扱わない機能は含めない」と仕組みで説明（A-018 が問題視する固定値散在を再生産しないため）

**evaluation（補足、item 4）— 配置先：案あ（tasks.md）を利用者が選択（実施済み）**：
4. evaluation/tasks.md 行 219 に「confidence_label は推定タスク用であり evaluation は推定タスクを扱わないため参照範囲外。よって上記 6 件のみを参照する」と明記。evaluation の再オープンは不要（tasks 段は review-wave 進行中の通常変更で吸収）。当初案の「foundation §判断 7 は全 7 件」という固定値併記は是正で削除（固定値散在の回避）

## 全体点検（実施済み）

foundation/design.md 全体を grep で点検。語彙正本件数の固定値の食い違いは §判断 7・行 644・行 736 以外には無し。行 659・行 715 の完成判定基準は既に「§判断 7 に列挙された語彙正本のすべて」と参照方式で書かれており修正不要。行 30「6 つの隣接機能」・行 378/734「severity 4 値」は語彙正本件数ではない（無関係）。
