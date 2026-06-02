---
date: 2026-06-02
classifier: claude_code_main_session
classification: 遡及（上流フェーズ・縦方向）。種別 A（tasks）。runtime implementation 段の T-011 起草中に、tasks.md の要件追跡表（要件→タスク）と各タスク本文の対応要件欄（タスク→要件）が作業単位で食い違っていることを発見。文書整合のみの修正で、要件の中身・実装は変更しない
trigger_source: runtime implementation T-011（テスト戦略整備）の「要件追跡表の双方向整合を機械検証」着手時。foundation T-010 同型の集合ベース検査では Requirement 10 のみ検出されるが、作業単位で突き合わせると 6 要件で食い違いが残存していることを発見。利用者は厳密整合（案 ア）を選択
feature: [runtime]
findings: [traceability-table-body-mismatch]
---

## 分類根拠

runtime の implementation 段（drafting 中、T-011 テスト戦略整備）で、tasks.md の要件追跡表と各タスク本文の対応要件欄の双方向整合を機械検証しようとした際、両者が作業単位で食い違っていることを発見した。これは下流段（implementation）で上流段（tasks）の文書修正を要する遡及所見であり、種別 A（tasks）。runtime 単機能で他機能への波及はない。

要件の中身・実装コードは変更しない。修正は tasks.md の対応注記の整合化（文書整合）のみ。

## 問題の事実（機械抽出）

**要件追跡表（要件→タスク、tasks.md 行 179〜188）**と**各タスク本文の対応要件欄（タスク→要件）**を突き合わせた結果：

- 集合ベース検査（foundation T-010 同型、要件番号の有無）：Requirement 10 のみ「表にあって本文にない」
- 作業単位検査（表の各マス ⇔ 各タスク本文）：6 要件で食い違い

| 要件 | 本文は担うが表に無い | 表は担うとするが本文に無い |
|---|---|---|
| 要件1 | T-001, T-011 | T-009 |
| 要件2 | — | T-004 |
| 要件4 | T-001 | — |
| 要件5 | T-002 | — |
| 要件6 | T-007, T-008 | — |
| 要件10 | — | T-004, T-011 |

（要件 3・7・8・9 は一致）

## 採用する整合規約（利用者明示承認「ア」2026-06-02）

要件追跡表を各タスク本文の対応要件の正確な逆対応にする（両者を完全な裏返しにし、作業単位の双方向整合を構造的に保証する）。慣例：テスト作業 T-011 は特定の検証役を持つ要件（要件1・要件10）のみに載せる。配置・境界を担う作業（T-001／T-009）は受入基準を実体として担うなら載せる。

## 正本修正の対象（第2過程、9 件）

**要件追跡表に作業を追加（5 件）**：

- 要件1 行：+T-001（受入6 実行配置・命名・書き込み順序の所有）、+T-011（受入1〜6 網羅検証）
- 要件4 行：+T-001（受入1 スキーマ準拠の実行レベル証拠出力の配置）
- 要件5 行：+T-002（受入1 決定単位提示の起点）
- 要件6 行：+T-007（受入9 署名＝順序の起点）、+T-008（受入3 無効化が生証拠を改変しない）

**タスク本文の対応要件に要件を追加（4 件）**：

- T-009：+要件1（受入5 実行終了境界の露出）
- T-004：+要件2（受入3〜5 treatment 別の段実行・省略）
- T-004：+要件10（受入2 固定パターン非依存の動的判定）
- T-011：+要件10（参照規約なしの機械検証）

修正後、表と本文は完全な逆対応となり、集合ベース・作業単位の双方向検査をともに通る。

## 連鎖再実施対象（REOPEN_PROCEDURE §4、計画書 §5.6）

- runtime：起点 tasks。tasks の alignment（整合確認）／approval（再承認）を再実施（drafting／triad-review／review-wave は据え置き、正本を手修正のうえ整合確認・承認のみ再実施）

implementation は drafting 中で alignment／approval 未了（全 false）のため、追加の差し戻しは不要。修正後の tasks を通常フローで取り込む。

## spec.json フラグ差し戻し（第1過程ステップ 6、承認済み「はい」2026-06-02）

**runtime/spec.json**：

- `reopened.tasks`：true 維持（セッション47 で既に true、履歴フラグ §5.24.8.1）
- `workflow_state.tasks.alignment`：true → **false**
- `workflow_state.tasks.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["implementation"]**

## 補助層 D（書き込み後の独立検証）の扱い

本記録（docs/reviews/reopen-classification-*.md）は規律 post-write-verification の対象。小規模（既存同型記録の構造踏襲）扱いとし、独立系統 1 体での検証対象とする。仕様文書（.reviewcompass/specs/）と tasks.md 本体の修正はワークフロー段（tasks alignment／approval）で検証されるため補助層 D 対象外。
