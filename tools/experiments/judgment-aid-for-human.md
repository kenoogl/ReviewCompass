# 利用者本人判定支援資料：foundation／tasks の must-fix 9 件

最終更新：2026-05-27（セッション 31、本実験第 1 段階の人本人判定取得用）

本文書は、ReviewCompass の 7 モデル比較実験（実験ノート [`docs/experiments/n-model-comparison.md`](../../docs/experiments/n-model-comparison.md) §3 〜 §5）において、利用者本人が must-fix 9 件（topic-02 〜 topic-10）の判定を行うための統合説明資料である。

各論点について：(1) 元の問題、(2) 3 役レビューの判定、(3) 判定役の推奨（**人本人のみ閲覧可**）、(4) 候補案、(5) 6 経路（API 5 + CLI 1）の判定結果分布、をまとめている。

詳細は元レビュー記録 [`.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md`](../../.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md) を参照。

---

## topic-02（F-002）：T-003 の語彙数記述（5 種 → 6 種）

**元の問題**：tasks.md T-003 の責務欄に「4 種の状態語彙」、完了条件に「5 種の語彙」と書かれている。実際に列挙されている語彙は 6 種で、数値が矛盾している。

**主役（Sonnet 4.6）**：重大度 ERROR。「責務欄『4 種』と完了条件『5 種（実際は 6 語彙）』の数値不整合」。

**反論役（Opus 4.7）**：反証あり。「『4 種』は責務分離 4 種で正しい、『5 種』が誤記。実際の列挙は 6 種。ERROR ではなく WARN レベル」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「WARN 相当だが完了条件の機械判定可能性に直結するため must-fix に格上げ。『5 種』を『6 種』に訂正、または列挙語彙数の整理」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（「5 種」を「6 種」に訂正、列挙数と一致させる）

**候補案**：
- **案 1**：完了条件の「5 種の語彙」を「6 種の語彙」に訂正、列挙数と一致させる
- **案 2**：列挙を 5 語彙に絞る（confidence_label を別行として整理）

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 |
|---|---|---|---|
| Sonnet API | 採用：案 1 | 0.92 | 9／3 |
| Sonnet CLI | 採用：案 1 | 0.92 | 9／3 |
| GPT-5.5 | 採用：案 1 | 0.95 | 10／3 |
| GPT-5.4 | 採用：案 1 | 0.97 | 10／3 |
| Gemini-flash | 採用：案 1 | 1.0 | 10／2 |
| Gemini-pro | 採用：案 1 | 0.95 | 9／3 |

**観察**：全 6 経路が「採用：案 1」で完全一致。

---

## topic-03（F-003）：T-003 の必須項目数 22 → 20

**元の問題**：tasks.md T-003「必須項目 22 件」と書かれているが、design.md §3 のテーブルを数えると 20 項目。2 項目の差がある。

**主役（Sonnet 4.6）**：重大度 ERROR。「『必須項目 22 件』が design.md §3 のテーブル 20 項目と乖離（2 項目過多）」。

**反論役（Opus 4.7）**：同意（反証材料なし）。「design.md §3 テーブル 20 項目を機械的に確認」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「テスト要件『必須項目数テスト』が直接参照する数字のため修正必須」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（tasks.md を 20 項目に訂正、遡及不要）

**候補案**：
- **案 1**：tasks.md T-003 の「必須項目 22 件」を「必須項目 20 件」に訂正
- **案 2**：design.md を再確認し、もし 22 項目が正しいなら design.md 側を修正（遡及）

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 |
|---|---|---|---|
| Sonnet API | 採用：案 1 | 0.88 | 9／2 |
| Sonnet CLI | 採用：案 1 | 0.95 | 9／2 |
| GPT-5.5 | 採用：案 1 | 0.95 | 10／2 |
| GPT-5.4 | 採用：案 1 | 0.97 | 10／2 |
| Gemini-flash | 採用：案 1 | 0.95 | 10／2 |
| Gemini-pro | 採用：案 1 | 0.95 | 10／1 |

**観察**：全 6 経路が「採用：案 1」で完全一致。

---

## topic-04（F-004）：テスト戦略の語彙正本整合カバレッジ

**元の問題**：tasks.md T-009 のテスト戦略「語彙正本整合」項目に counter_status／validator_status／evidence_class／review_mode の **4 語彙のみ列挙**。設計の語彙正本は 7 語彙で、severity／final_label／confidence_label の 3 語彙が T-009 でカバーされない。

**主役（Sonnet 4.6）**：重大度 WARN。「3 語彙が網羅されない」。

**反論役（Opus 4.7）**：同意。「語彙正本整合のカバレッジが 3 語彙で漏れる」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「語彙正本整合の網羅性に直結」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（T-009 で 7 語彙すべての整合確認、設計の意図に整合）

**候補案**：
- **案 1**：T-009 のテスト要件に severity／final_label／confidence_label の値テストを追加（T-009 で 7 語彙すべての整合確認、責務集中型）
- **案 2**：severity／final_label は T-004 の enum 値テストでカバー、confidence_label は T-003 でカバーする旨を T-009 に明記（責務分散型）

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 | 主な理由（要約） |
|---|---|---|---|---|
| Sonnet API | **採用：案 2** | 0.78 | 5／8 | 責務分散の方が tasks.md の構造に沿う |
| Sonnet CLI | 採用：案 1 | 0.78 | 8／5 | 設計の意図（束ねる）に整合 |
| GPT-5.5 | 採用：案 1 | 0.88 | 9／6 | 責務集中型が網羅性で優位 |
| GPT-5.4 | 採用：案 1 | 0.9 | 9／6 | 同上 |
| Gemini-flash | 採用：案 1 | 0.95 | 9／4 | 同上 |
| Gemini-pro | 採用：案 1 | 0.9 | 9／4 | 同上 |

**観察**：Sonnet API のみ案 2、他 5 経路は案 1。**Sonnet API と Sonnet CLI で経路差**（同一モデルだが異なる判断、観点 4）。

---

## topic-05（F-006）：T-004 完了条件の参照先

**元の問題**：tasks.md T-004 完了条件「severity／counter_status／final_label の enum 値が design.md §判断 7 と一致」と書かれている。実際は §判断 7 は所有関係宣言節で、enum 値の実体は §3（validator_status／evidence_class／review_mode）、§4 finding 節（severity／counter_status）、§4 necessity_judgment 節（final_label）に分散。参照先が不正確。

**主役（Sonnet 4.6）**：重大度 WARN。「参照先『§判断 7』は所有関係宣言節、実際の enum 値は §3 と §4 各節」。

**反論役（Opus 4.7）**：同意。「§判断 7 は所有関係宣言、enum 値は §3 と §4 が正本」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「参照先の不正確はテスト要件で参照する正本箇所のため修正必須」。

**判定役の推奨（人本人のみ閲覧可）**：**案 2**（両参照に明示、所有関係と enum 値の両方を確認）

**候補案**：
- **案 1**：参照先を「design.md §4 finding 節（severity／counter_status）と §4 necessity_judgment 節（final_label）」に訂正（enum 値だけを参照、簡潔）
- **案 2**：参照先を「design.md §判断 7（所有関係）＋ §4 finding 節（severity／counter_status）＋ §4 necessity_judgment 節（final_label、enum 値）」と両参照に明示

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 | 主な理由（要約） |
|---|---|---|---|---|
| Sonnet API | 採用：案 2 | 0.78 | 5／8 | 所有関係と enum 値の両方を参照、設計の意図を反映 |
| Sonnet CLI | 採用：案 2 | 0.78 | 6／8 | 同上 |
| GPT-5.5 | 採用：案 2 | 0.9 | 7／9 | 同上 |
| GPT-5.4 | 採用：案 1 | 0.9 | 9／6 | enum 値だけを参照、簡潔 |
| Gemini-flash | 採用：案 1 | 0.9 | 9／5 | 同上 |
| Gemini-pro | **別案を提示** | 0.95 | 7／5 | 別案：両方明示しつつ、構造を簡素化 |

**観察**：3 分岐。案 2 が 3、案 1 が 2、別案が 1。

---

## topic-06（F-009）：T-009 の累積件数記述

**元の問題**：tasks.md T-009 完了条件「累積テスト件数が 60 件＋ foundation テスト件数（見込み 40〜60 件、合計 100〜120 件想定）」。60 件の積算基点が tasks.md 単体では特定不能（cross-reference 不在）。

**主役（Sonnet 4.6）**：重大度 WARN。「累積テスト件数『60 件＋』の積算基点が未定義」。

**反論役（Opus 4.7）**：同意。「基点未定義で充足判断不可」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「累積件数の基点未定義は機械判定不能」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（累積件数の記述を削除、「すべて pass」を完了条件とする）

**候補案**：
- **案 1**：累積件数の記述を削除し、「すべてのテストが pytest で pass」のみ完了条件とする
- **案 2**：積算基点を明示（「サイクル 4 完了時点で累積 60 件、foundation 完成時に 100〜120 件想定」）

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 | 主な理由（要約） |
|---|---|---|---|---|
| Sonnet API | **別案を提示** | 0.78 | 5／6 | DoD は pass のみ、件数は別管理 |
| Sonnet CLI | 採用：案 1 | 0.85 | 9／3 | 機械判定可能、cross-reference 不要 |
| GPT-5.5 | 採用：案 1 | 0.86 | 9／6 | 同上 |
| GPT-5.4 | 採用：案 1 | 0.87 | 9／5 | 同上 |
| Gemini-flash | **別案を提示**（2tn） | 0.9 | 5／8 | DoD は pass のみ、参考情報として件数残置（案 1+案 2 折衷） |
| Gemini-pro | 別案を提示 | 0.9 | 6／4 | カバレッジ目標として別途定義 |

**観察**：3 分岐。案 1 が 3、別案が 3。**Sonnet API と Sonnet CLI で経路差**（同一モデルだが異なる判断、観点 4）。

---

## topic-07（F-010）：T-008 の「書き込み権限なし」表記

**元の問題**：tasks.md T-008「`tools/foundation_validators/check_encoding_convention.py`（Python スクリプト、書き込み権限なし）」と書かれているが、「書き込み権限なし」が属性指定として意味不明（ファイル権限か副作用なしか）。

**主役（Sonnet 4.6）**：重大度 WARN。「『書き込み権限なし』が意味不明」。

**反論役（Opus 4.7）**：同意。「『書き込み権限なし』は属性指定として意味不明」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「『書き込み権限なし』は誤記または不要記述、削除必須」。

**判定役の推奨（人本人のみ閲覧可）**：**案 2**（読み取り専用検証器、ファイル書き込みの副作用なし と明示）

**候補案**：
- **案 1**：「（書き込み権限なし）」を削除
- **案 2**：「（読み取り専用検証器、ファイル書き込みの副作用なし）」と明示

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 |
|---|---|---|---|
| Sonnet API | 採用：案 2 | 0.82 | 5／8 |
| Sonnet CLI | 採用：案 2 | 0.88 | 5／8 |
| GPT-5.5 | 採用：案 2 | 0.88 | 6／9 |
| GPT-5.4 | 採用：案 2 | 0.89 | 6／9 |
| Gemini-flash | 採用：案 2 | 0.95 | 6／9 |
| Gemini-pro | 採用：案 2 | 0.95 | 4／9 |

**観察**：全 6 経路が「採用：案 2」で完全一致。

---

## topic-08（A-001）：T-003 に run_status／human_signoff_status の値テスト追加

**元の問題**：tasks.md T-003 の語彙正本値テストでは validator_status／evidence_class／review_mode／confidence_label の 4 語彙のみ。run_status（4 値）と human_signoff_status（4 値）の値テストが欠落。両者とも foundation の責務（design.md §3 で正本として宣言）。

**反論役（Opus 4.7）独立発見**：重大度 ERROR。「run_status と human_signoff_status の値テストが欠落」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「run_status／human_signoff_status の値テスト欠落は語彙正本整合の網羅性に直結」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（T-003 のテスト要件に追加、合計 6 語彙の値テスト）

**候補案**：
- **案 1**：T-003 のテスト要件に run_status と human_signoff_status の値テストを追加（合計 6 語彙の値テスト）
- **案 2**：現状維持（責務分離 4 種は記述のみで、値テストは 4 語彙のみ）

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 |
|---|---|---|---|
| Sonnet API | 採用：案 1 | 0.92 | 9／2 |
| Sonnet CLI | 採用：案 1 | 0.87 | 9／3 |
| GPT-5.5 | 採用：案 1 | 0.95 | 9／2 |
| GPT-5.4 | 採用：案 1 | 0.95 | 9／2 |
| Gemini-flash | 採用：案 1 | 1.0 | 10／3 |
| Gemini-pro | 採用：案 1 | 0.95 | 10／2 |

**観察**：全 6 経路が「採用：案 1」で完全一致。

---

## topic-09（A-002）：要件追跡表と T-001 本文の双方向整合

**元の問題**：要件追跡表「Requirement 5：パターン定義依存の除外 | T-001（配置規約に含めない方針の明示）」と書かれている。一方 T-001 本文の対応要件欄は「Requirement 7（リポジトリ内資産の規則）」のみ。Req 5 の追跡が双方向で整合しない。

**反論役（Opus 4.7）独立発見**：重大度 WARN。「要件追跡表と本文の双方向不整合」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「要件追跡表と本文の双方向不整合は機械検査で必ず引っかかる」。

**判定役の推奨（人本人のみ閲覧可）**：**案 1**（T-001 本文に Requirement 5 を追加、双方向整合）

**候補案**：
- **案 1**：T-001 本文の対応要件欄に「Requirement 5（パターン定義依存の除外）」を追加
- **案 2**：要件追跡表から Requirement 5 行を削除し、Requirement 5 は T-001 ではなく別の処置とする

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 |
|---|---|---|---|
| Sonnet API | 採用：案 1 | 0.87 | 8／3 |
| Sonnet CLI | 採用：案 1 | 0.85 | （score 未記入） |
| GPT-5.5 | 採用：案 1 | 0.88 | 9／4 |
| GPT-5.4 | 採用：案 1 | 0.88 | 9／4 |
| Gemini-flash | **深掘り要求**（2tn） | 0.9 | 4／5 | T-001 の本旨が不明、Req 5 が能動／消極か確定不能 |
| Gemini-pro | 採用：案 1 | 0.95 | 10／3 |

**観察**：5 経路が案 1、Gemini-flash のみ深掘り要求（マルチターン後）。

---

## topic-10（A-005）：T-010 完了条件のレポート構造

**元の問題**：tasks.md T-010 完了条件「レポート出力（標準出力に整形済み YAML）が design.md §完成判定基準と一致」。design.md §完成判定基準は 6 項目の自然言語宣言、YAML レポートの構造（必須キー、値域）が未定義。

**反論役（Opus 4.7）独立発見**：重大度 WARN。「T-010 完了条件のレポート（YAML）構造が未定義」。

**判定役（Opus 4.7）**：must-fix／機能内対処。「レポート形状の最低限の明示が必須」。

**判定役の推奨（人本人のみ閲覧可）**：**案 2**（6 判定項目すべてが pass を完了条件とし、出力形式は実装段で確定）

**候補案**：
- **案 1**：T-010 の完了条件に YAML レポートの最低限の構造（例：`checks: { all_pass: true, items: [{ name, status, details }] }`）を明示
- **案 2**：完了条件を「6 判定項目すべてが pass」と表現し、出力形式は実装段で確定する旨を明示

**6 経路の判定**：

| 判定者 | decision | confidence | 案 1／案 2 | 主な理由（要約） |
|---|---|---|---|---|
| Sonnet API | 別案を提示 | 0.78 | 6／4 | YAML を上流（design.md）でスキーマ定義（遡及） |
| Sonnet CLI | 採用：案 2 | 0.82 | 4／8 | 出力形式は実装段で確定 |
| GPT-5.5 | 別案を提示 | 0.86 | 7／5 | 機能内対処では不十分、design.md でスキーマ定義 |
| GPT-5.4 | 別案を提示 | 0.89 | 6／5 | 同上 |
| Gemini-flash | 採用：案 1 | 0.9 | 9／4 | tasks.md でスキーマ明示、機械判定可能 |
| Gemini-pro | **別案を提示**（2tn） | 0.95 | 6／3 | 波及種別を「機能内対処」→「遡及」に変更、design.md でスキーマ定義 |

**観察**：別案が 4、案 2 が 1、案 1 が 1。**多数が「機能内対処では不十分、上流の design.md に遡及すべき」と提案**。

---

## 利用者本人の判定欄

判定を入れたい論点について、以下の形式で記入してください。

```
### topic-NN

- decision：採用：案 1 / 採用：案 2 / 別案を提示 / 深掘り要求
- rationale：判断の理由
- confidence：0.0〜1.0
- case_scores：案 1=?, 案 2=?
- comment：（任意）
```

### 9 件まとめての判定（同意なら「同意」、異なるなら個別記載）

（記入欄）

---

## 関連参照

- 元レビュー記録：[`.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md`](../../.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md)
- 対象 tasks.md：[`.reviewcompass/specs/foundation/tasks.md`](../../.reviewcompass/specs/foundation/tasks.md)
- 対象 design.md：[`.reviewcompass/specs/foundation/design.md`](../../.reviewcompass/specs/foundation/design.md)
- 実験ノート：[`docs/experiments/n-model-comparison.md`](../../docs/experiments/n-model-comparison.md)
- 各経路の生 YAML：`tools/experiments/results/topic-NN-*.yaml`
