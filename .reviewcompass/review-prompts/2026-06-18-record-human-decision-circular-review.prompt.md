# 設計深掘りレビュー：record_human_decision の循環依存

## 問題の所在

`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §3.1 は、
`record_human_decision`（人間判断の記録コマンド）を
「`effect_kind: irreversible_action`（取り消し不能操作）に該当し、
実行前に承認ゲートを通す必要がある」として列挙している。

一方 §5.1 は、承認ゲートを次の順序と定義している。

```
wait_for_human_decision（人間判断を待つ）
  → 人間が判断を下す
    → record_human_decision（判断を記録する）
      → 対象の不可逆操作を実行
```

この2つを組み合わせると次の矛盾が生じる。

- `record_human_decision` を実行するには承認ゲートを通す必要がある
- 承認ゲートは `record_human_decision` の完了で終わる
- よって `record_human_decision` を実行するには `record_human_decision` の完了が先に必要

これは論理的なデッドロック（どちらも先に始められない行き詰まり）であり、
実装フローが成立しない。

---

## 解消候補として挙がっている方向性

**方向性 X：`record_human_decision` を `state_mutation`（状態変更）に再分類する**

根拠：人間が判断を確定した瞬間は `wait_for_human_decision` の段階である。
`record_human_decision` はその結果をファイルに書き出す機械的な後処理に過ぎず、
新たな判断を伴わないため取り消し不能とは言えない。

問題：ファイルに書き出すという行為は取り消せるのか？
削除すれば「なかったこと」にできるが、それは審査記録の改ざんに相当する可能性がある。

**方向性 Y：承認ゲートの定義を変え、`record_human_decision` を gate の外に出す**

例えば承認ゲートを次のように再定義する。

```
wait_for_human_decision（人間判断を待つ・ここで人間が判断する）
  ← ここまでが承認ゲート ←
    → record_human_decision（判断を記録する。ゲートの外の機械処理）
      → 対象の不可逆操作を実行
```

この場合、`record_human_decision` は「ゲート通過後の機械処理」となり、
`effect_kind: write`（書き込み）または `state_mutation` で十分になる。

問題：承認ゲートが「判断を得るところまで」と「記録するところまで」のどちらで終わるかが、
audit trail（操作記録・証跡）の観点から重要になる。

**方向性 Z：`record_human_decision` 自体を廃止し、`wait_for_human_decision` に統合する**

人間が判断を下した時点で即座に記録まで行う設計にする。
`record_human_decision` という独立した `required_action` を持たない。

問題：人間の判断入力と記録コマンドを1つにすると、
「判断はしたが記録前にセッションが切れた」場合のリカバリ手順が複雑になる。

---

## レビューで答えてほしい問い

次の問いに対して独立して分析し、判断と根拠を示すこと。

1. 方向性 X・Y・Z のどれが最も設計として整合的か。
   Phase 0（next --json の選択層実装）と Phase 5（ガード強制）の実装を念頭に置いて答えること。

2. `record_human_decision` を `state_mutation` と分類した場合（方向性 X）、
   audit trail（操作証跡の完全性）に問題は生じるか。
   具体的な失敗シナリオがあれば示すこと。

3. 承認ゲートの「終わり」をどこに置くべきか。
   「人間が判断した瞬間」か「その判断がシステムに記録された瞬間」か、
   設計上どちらが正しいか。

4. 3つの方向性以外に有望な解消策はあるか。

5. 最終的にどの方向性を推奨するか、1文で明確に述べること。

---

## 出力形式

YAML 形式で次の構造で出力すること。

```yaml
findings:
  - severity: ERROR / WARN / INFO
    question_id: "1" / "2" / "3" / "4" / "5"
    description: |
      （分析内容）
    rationale: |
      （根拠）
```
