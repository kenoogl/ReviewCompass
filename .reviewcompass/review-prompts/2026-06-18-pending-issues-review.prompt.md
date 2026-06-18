# 設計文書レビュー：approval_required 分離後の未解決4問題

## 背景

前のレビューで `approval_required`（実行前に人間の承認が必要かを示す属性）を
`effect_kind`（副作用の種別）から独立した属性として分離する修正を実施した。
その修正に対する検証レビューで、さらに4つの問題が指摘された。

---

## 問題1：§3 の表における `run_reopen_pending_gate` の `approval_required` の記述

統合設計メモ §3 の対応表（全 required_action の一覧）では
`run_reopen_pending_gate` の `approval_required` が「gate 種別による（§3.2 参照）」と
書かれている。

しかし参照先の §3.2 の表（gate 種別ごとの詳細）を見ると、
定義されている全 gate 種別（`triad-review`, `alignment`, `approval`, `drafting`）において
`approval_required` は一律「いいえ」となっている。

§3.2 の設計根拠：「承認要求の設定自体は可逆。承認が必要なのはその後の対象操作。」
（承認ゲートを「設定する」操作に承認は不要。承認が必要なのは設定後に待つ操作である。）

§3 の「gate 種別による」という記述と §3.2 の「一律いいえ」の間に矛盾がある。

---

## 問題2：§3.2 と §7 における `alignment` gate の `effect_kind` の矛盾

§3.2 の表では `alignment` gate の `effect_kind` を `write` と確定値で記載している。

一方、§7（未確定事項）の1番では：
「`alignment` の effect_kind が未確定。選択肢：`write`（合意記録の作成）/
`state_mutation`（alignment flag の更新）」と未決のまま記録されている。

同一文書内で確定値（§3.2）と未確定（§7）が並存している。

`alignment` gate の実体は「LLM による承認材料の提示と合意確認」という言語作業であり、
その結果として何を書くか（ファイルか状態フラグか）が設計上まだ決まっていない。

---

## 問題3：Phase 2 の `operation-list --json` の設計漏れ

機械化設計メモ §3.1 の operation contract 属性表には `approval_required` が追加されている。

しかし Phase 2 の実装仕様では：
「各操作の `canonical_commands / effect_kind / sequence / pending_conflicts` を返す」
となっており、`approval_required` が含まれていない。

Phase 5 では `approval_required: true` の操作に承認ゲートを機械的に強制する計画だが、
Phase 2 の registry が `approval_required` を返さなければ、
後続 Phase の preflight 検査やガードが `approval_required` の値を取得できない。

---

## 問題4：承認証跡（承認記録）と対象操作の紐付けが未定義

設計では `record_human_decision`（判断を記録する操作）→ `next --json` 再実行 →
`approval_required: true` の対象操作を実行、という流れを想定している。

しかし「この承認記録が、今実行しようとしている特定の操作を承認したものである」
という事実を機械的に確かめる仕組みが文書に書かれていない。

承認記録が持つべき情報（対象 required_action、コマンド内容、
ワークフロー状態のダイジェスト、有効期限、使用済みフラグ等）が未定義のため、
Phase 5 のガードが「何らかの承認記録が存在する」しか確認できない状況になっている。

---

## 確認してほしいこと

- 問題1〜4について、それぞれ設計として問題があるかどうかを分析すること。
- 問題2の `alignment` の `effect_kind` については、
  `alignment` gate が実際に何をする操作かという観点から、
  どのように分類されるべきかを独立して考察すること。
  選択肢の枠を超えて考えてよい。
- 問題3は単純な書き漏れと判断してよいか、それとも設計上の理由で
  除外された可能性があるかを検討すること。
- 問題4の深刻さを評価し、今すぐ定義が必要か、実装フェーズで解決できるかを判断すること。
- 問題間に見落とされている依存関係や相互影響があれば指摘すること。

---

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    target_location: 対象箇所
    description: |
      （指摘内容）
    rationale: |
      （根拠）
```

問題が見つからない場合は `findings: []` と返すこと。
