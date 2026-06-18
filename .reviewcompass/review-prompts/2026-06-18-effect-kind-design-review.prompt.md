# 設計深掘りレビュー：effect_kind の語彙設計

## レビューの目的

`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` の §3・§3.1 に、
`effect_kind` の分類をめぐる矛盾が2つ発見された。

本レビューは、その矛盾を解消するための設計判断を深掘りすることを目的とする。

---

## 背景：現在の矛盾

### 矛盾1（クラスタ A）：effect_kind の表記ゆれ

§3 の表では多くの操作（例：`apply_approved_reopen_plan`、`record_human_decision`、
`finalize_reopen` など）の `effect_kind` を `state_mutation`（状態変更）と記載している。

しかし §3.1 では、これらの操作を「`effect_kind: irreversible_action`（取り消し不能操作）に
該当し、承認ゲートが必要」として列挙している。

同一操作に対して2種類の `effect_kind` 名が使われており、どちらが正しいかが定まっていない。

### 矛盾2（クラスタ B）：record_human_decision の循環依存

§3.1 は `record_human_decision`（人間判断の記録コマンド）を `irreversible_action` と分類し、
承認ゲートが必要とした。

しかし §5.1 が定義する承認ゲートは
「`wait_for_human_decision` → 人間が判断 → `record_human_decision`」
という順序で終わる。

`record_human_decision` 自体に承認ゲートを課すと、
承認を記録するために承認が必要という循環依存になる。

---

## 検討対象の2案

### 案1：irreversible_action を独立した種別とする

`effect_kind` を `read / write / state_mutation / external_call / irreversible_action` の5種とし、
承認ゲートが必要な操作はすべて `irreversible_action` とする。

- ガードの判定：`effect_kind == "irreversible_action"` の1条件で完結する
- 循環依存の解消：`record_human_decision` を `state_mutation` に分類し直す
  （根拠：人間が判断を確定した瞬間は `wait_for_human_decision` であり、
   `record_human_decision` はその記録を機械的にファイルへ書き出すだけ）
- Phase 1 の語彙（5種）をそのまま使える

### 案2：state_mutation のサブセット＋approval_required フラグとする

`effect_kind` から `irreversible_action` を削除し、4種
（`read / write / state_mutation / external_call`）にする。
代わりに `approval_required: true / false` フラグを操作契約に追加する。

- ガードの判定：`effect_kind == "state_mutation" AND approval_required == true` の2条件
- 循環依存の解消：`record_human_decision` は `state_mutation + approval_required: false`
  （承認はすでに取得済みとして、記録行為には再度の承認を不要とする）
- Phase 1 の語彙変更が必要

---

## レビューで答えてほしい問い

次の問いに対して、設計の整合性・実装への影響・将来の拡張性の観点から独立して分析し、
判断と根拠を示すこと。

1. 案1 と 案2 のどちらが、後続の Phase 2〜5（registry・preflight・ガード実装）において
   より誤りを生みにくいか。根拠を示すこと。

2. `record_human_decision` を `state_mutation` と分類することは、
   「取り消し不能」という性質に照らして正当化できるか。
   この分類が将来の実装で問題を起こす可能性があるなら指摘すること。

3. 案1 と 案2 のどちらを採用しても解消されない問題、または両案に共通する潜在的な欠陥があれば指摘すること。

4. 最終的にどちらの案を推奨するか、1文で明確に述べること。

---

## 出力形式

YAML 形式で次の構造で出力すること。

```yaml
findings:
  - severity: ERROR / WARN / INFO
    question_id: "1" / "2" / "3" / "4"
    description: |
      （分析内容）
    rationale: |
      （根拠）
```

severity の基準：
- ERROR：設計に欠陥があり、このままでは実装で重大な問題が生じる
- WARN：設計の弱点であり、改善を強く推奨する
- INFO：参考情報または補足
