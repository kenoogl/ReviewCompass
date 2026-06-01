---
date: 2026-06-02
classifier: claude_code_main_session
classification: 波及（同フェーズ横方向）：foundation requirements の review_mode 語彙拡張に伴う analysis／evaluation への波及。両機能の requirements／design／tasks を参照方式へ修正
trigger_source: foundation の review_mode 正本に api_mediated を追加（2026-06-01 セッション 46、reopen-classification-2026-06-01-foundation-review-mode.md）の第3過程 alignment で発見した、analysis／evaluation の下流波及
feature: [analysis, evaluation]
findings: [review-mode-propagation-analysis-evaluation]
---

## 分類根拠

本再オープンは、foundation の review_mode 語彙正本に `api_mediated` を追加した変更（**foundation への追加日は 2026-06-01 セッション 46**、R 起点再オープン）の **第3過程（連鎖再実施）の alignment** を foundation で実施中に発見した、analysis／evaluation への機能横断の波及を処理する（**本波及対処は 2026-06-02**、front-matter の date を参照）。

**セッション 46 の「波及なし」判断の訂正**：先行記録 [reopen-classification-2026-06-01-foundation-review-mode.md](reopen-classification-2026-06-01-foundation-review-mode.md) の「適用範囲の注記」（行 68-70）は「下流機能はレビューモード語彙を参照するのみで再定義していないため、機能横断の波及（他機能の正本修正）は発生しない」と判断していた。しかし第3過程 alignment の深掘りで、analysis／evaluation の requirements／design／tasks に「3 値」「3 経路」という **固定の数値・列挙が参照ではなく書き写されている** ことが判明した。これは A-018（[reopen-classification-2026-05-29-foundation-a018.md](reopen-classification-2026-05-29-foundation-a018.md)）で問題になった「固定値の散在」と同型である。よってセッション 46 の「波及なし」判断を「波及あり」に訂正する。

利用者明示承認の出典（2026-06-02）：

- 波及対処の実施＝「案ア」（今すぐ analysis・evaluation を修正）
- 修正方式＝「やり方 2」（固定値を書き換えるのでなく、参照方式に変えて将来の波及を断つ。A-018 教訓と一貫）
- 集団規則（種類 B）の方針＝「推奨案」（runtime_mediated を標準、それ以外のレビューモードはすべて別集団とする原則ベースの記述）

## 問題の事実

foundation の review_mode 正本は 4 値（`manual_dogfooding`／`runtime_mediated`／`subagent_mediated`／`api_mediated`）に拡張済み。しかし analysis／evaluation の仕様文書には旧 3 値前提の固定記述が残る。該当箇所は 2 種類に分かれる。

- **種類 A（全レビューモードを指すだけ）**：「3 経路の差分を保持」「review_mode 3 値正本を参照」等。数値・固定列挙を消し、「foundation の review_mode 正本が定める全レビューモード」「値は foundation 正本を参照」という参照方式へ書き換える。
- **種類 B（レビューモードごとの扱いを規定する仕分けルール）**：evaluation の比較母集団規則。「runtime_mediated を標準集団、手動とサブエージェントは別集団」という具体名列挙を、「runtime_mediated を標準集団、それ以外のレビューモード（手動・サブエージェント・独立 API 経由等）はそれぞれ別集団」という原則ベースへ書き換える。これにより `api_mediated` は自動的に「別集団」に入り、将来のモード追加でも再修正不要となる。

`api_mediated` の位置づけ：独立 API 経由の triad-review（仕様レビュー段）は、実行時経由（`runtime_mediated`）とは性質が異なる開発・検証用レビューであり、手動・サブエージェントと同じ「標準母集団から外す別集団」に属する（利用者承認「推奨案」2026-06-02）。

## 連鎖再実施対象（REOPEN_PROCEDURE §4、計画書 §5.6）

両機能とも requirements が起点の波及が design／tasks に及ぶ。再実施対象は各フェーズの **alignment と approval のみ**。drafting／triad-review／review-wave は据え置く（正本は手で修正し、整合確認＝alignment と承認＝approval のみを再実施する）：

- analysis：requirements（alignment／approval）／design（alignment／approval）／tasks（alignment／approval）
- evaluation：requirements（alignment／approval）／design（alignment／approval）／tasks（alignment／approval）

implementation は両機能とも全段 false（未着手）のため対象外。

## spec.json フラグ差し戻し（第1過程ステップ 6、承認済み・2026-06-02）

**analysis/spec.json**：

- `reopened.requirements`：false → **true**
- `reopened.design`：false → **true**
- `reopened.tasks`：false → **true**
- `workflow_state.requirements.alignment`：true → **false**
- `workflow_state.requirements.approval`：true → **false**
- `workflow_state.design.alignment`：true → **false**
- `workflow_state.design.approval`：true → **false**
- `workflow_state.tasks.alignment`：true → **false**
- `workflow_state.tasks.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["requirements","design","tasks"]**

**evaluation/spec.json**（`reopened.design` は A-018 で既に true、維持）：

- `reopened.requirements`：false → **true**
- `reopened.tasks`：false → **true**
- `workflow_state.requirements.alignment`：true → **false**
- `workflow_state.requirements.approval`：true → **false**
- `workflow_state.design.alignment`：true → **false**
- `workflow_state.design.approval`：true → **false**
- `workflow_state.tasks.alignment`：true → **false**
- `workflow_state.tasks.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["requirements","design","tasks"]**

## 正本修正の対象（第2過程で実施）

「3 方式比較データ」（primary／adversarial／judgment の 3 方式、§5.9.6）と「3 役」（主役・敵対役・判定役）はレビューモードと無関係のため修正対象外。

### analysis（種類 A）

- requirements.md 105（Req 6 受入 1）：レビューモード語彙正本の参照記述を参照方式へ
- requirements.md 119（Req 7 受入 3）：「3 経路（…）の所見出力の差分」→ 全レビューモード別の差分
- requirements.md 132（Req 8 受入 1）：「3 経路比較データ」→ レビューモード別比較データ
- design.md 112：コメント「3 経路の所見差分」→ レビューモード別の所見差分
- design.md 133：コメント「3 経路比較データ」→ レビューモード別比較データ
- design.md 179（出力先表）：「3 経路比較データ」のみ（「3 方式比較データ」は不変）
- design.md 213：「mode_diff_report.json（3 経路差分）」→ レビューモード別差分
- design.md 271：「review_mode：…（3 値、再定義しない）」→ 値は foundation 正本を参照
- design.md 418／420／425（§可視化モデル §2）：節見出し・本文・review_mode 値を参照方式へ
- design.md 489：「mode_comparison_report.json：3 経路比較データ」→ レビューモード別比較データ
- design.md 699（判断 7）／722（要件追跡表）／789（完成判定）：「3 経路」→ レビューモード別
- design.md 780（先送り論点）：「3 経路の恒久運用」→ 各レビューモードの恒久運用
- tasks.md 87（T-002）／136（T-007）：「foundation 3 値正本」→ foundation 正本

### evaluation（種類 A）

- requirements.md 139（Req 9 目的）：「3 経路の証拠が…混ざらない」→ 各レビューモードの証拠が…
- requirements.md 143（受入 1）：レビューモード語彙正本の参照記述を参照方式へ
- requirements.md 149（受入 7）：「3 経路（…）別の所見差分」→ レビューモード別の所見差分
- design.md 146：「modes/：3 経路（…）別の所見差分」→ レビューモード別の所見差分
- design.md 270（直交軸）：「review_mode（…、foundation 3 値正本）」→ 参照方式
- design.md 458／463（レビューモード差分報告）：「3 経路別」「review_mode 3 値」→ 参照方式
- design.md 700（要件追跡表）：「3 経路集団規則」→ レビューモード母集団規則
- tasks.md 149／150（T-009）：「3 経路別差分」「foundation review_mode 正本 3 値」→ 参照方式

### evaluation（種類 B：仕分けルールを原則ベースへ）

- requirements.md 144（受入 2）：「標準の runtime_mediated 比較セットから、手動レビュー証拠とサブエージェント経由証拠を除外」→「runtime_mediated 以外のレビューモード（手動・サブエージェント・独立 API 経由等）を除外」
- requirements.md 147（受入 5）：「手動 dogfooding／サブエージェント経由／実行時経由の引き継ぎ境界」→「各レビューモードの引き継ぎ境界」
- requirements.md 148（受入 6）：「手動 dogfooding 証拠は別集団、サブエージェント経由証拠は第三集団」→「runtime_mediated を標準集団、それ以外のレビューモードはそれぞれ別集団」
- design.md 416-426（§4 レビューモード母集団規則）：runtime_mediated＝標準、それ以外はすべて別集団、の原則ベースへ書き換え

### 経緯記述（履歴改ざん禁止、追記方式）

- analysis requirements.md 147（Change Intent）／design.md 801（Change Intent）の「3 値体制（2 値→3 値の拡張経緯）」：当時の事実として保持し、末尾に「その後 2026-06-02 に api_mediated を追加し 4 値（foundation 正本を参照）」を追記する。

## 補助層 D（書き込み後の独立検証）の扱い

本記録ファイルは `docs/reviews/` 配下の `reopen-classification-*.md` であり、規律 [discipline_post_write_verification.md](../disciplines/discipline_post_write_verification.md) の対象。コミット前に独立系統（OpenAI／Google）で検証する。仕様文書（`.reviewcompass/specs/` 配下）はワークフロー段で検証されるため補助層 D の対象外。
