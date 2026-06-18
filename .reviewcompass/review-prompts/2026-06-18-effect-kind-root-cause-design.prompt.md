# 設計深掘りレビュー：effect_kind の設計原則と根本解決

## これまでの議論の経緯

ReviewCompass の統合設計メモ（`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`）を
3モデルでレビューした結果、次の問題が浮かび上がった。

- §3 の対応表と §3.1 のリストで、同じ操作の `effect_kind` 分類が食い違っている
- `run_reopen_pending_gate` の approval ゲートで「承認要求を設定する操作」が `irreversible_action` に分類されており、「承認ゲートを守る操作」と「承認ゲートを設定する操作」が混同されている

これらは個別の修正で解決できるが、その前に設計の根本に問題があるかどうかを確認したい。

## 現在の設計

`effect_kind` は機械化設計メモ（`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`）
で「副作用の種別」と定義されており、次の5値を取る。

```
read / write / state_mutation / external_call / irreversible_action
```

同メモには以下の記述がある。

> `effect_kind: irreversible_action`（取り消し不能操作）を持つ操作（commit、push、spec.json の workflow_state 更新など）は、
> 承認ゲートを通過してからでないと実行できない。

また Phase 5 の計画として以下が書かれている。

> `effect_kind: irreversible_action` に承認ゲートを強制する

つまり現在の設計では `effect_kind` が次の2つの役割を同時に担っている。

- 役割1：「操作が何をするか」を表す分類（副作用の種別）
- 役割2：「承認ゲートが必要かどうか」の判定基準

## 注目すべき点

`effect_kind` の5値を観察すると、次のことに気づく。

`read / write / state_mutation / external_call` の4値は「操作が何をするか」を表す言葉である。
それに対して `irreversible_action` は「操作の結果が取り消せないこと」を表す言葉であり、
「何をするか」ではなく「どのような性質を持つか」を表している。

これらは性質が異なる概念である。

さらに実際の操作を見ると：

- `run_post_write_verification`（外部レビューAPIの呼び出し）は `external_call` であるが、承認ゲートは不要
- `apply_approved_reopen_plan`（spec.json の workflow_state を書き換える）は現在 `state_mutation` であるが、承認ゲートが必要とされている
- `reopen-set-blocker`（承認要求の構造化・`run_reopen_pending_gate` の approval ゲートで実行される操作）は承認ゲートを「設定する」操作であり、承認ゲートが「守る」不可逆操作ではない

また、承認ゲートを構成する操作（`wait_for_human_decision`・`record_human_decision`）は
承認ゲートの「対象」ではなく、承認ゲートの「部品」であることを §3.1 は明示している。
これは正しい区別である。

## レビューで答えてほしい問い

1. `effect_kind` が「副作用の種別」と「承認ゲートの要否の判定基準」の2役を担うことは、
   設計の原則として成立しうるか。
   成立しない場合、どのような問題が実装段階で顕在化するか。

2. `irreversible_action` という値は、残り4値（`read / write / state_mutation / external_call`）と
   同じ軸に置いてよい概念か。
   これらが同じ列挙型として並ぶことで生じる設計上の問題を示すこと。

3. 「承認ゲートを設定する操作」（例：`reopen-set-blocker` の実行）と
   「承認ゲートが守る不可逆操作」（例：`commit_stop_point` の実行）は、
   operation contract（操作契約）においてどのように区別されるべきか。

4. Phase 5 で「`effect_kind: irreversible_action` に承認ゲートを機械的に強制する」という計画がある。
   承認ゲートの要否の判定基準を `effect_kind` 以外の軸で持たせる場合、
   この計画はどのように書き直されるべきか。

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    question_id: "1" / "2" / "3" / "4"
    description: |
      （分析内容）
    rationale: |
      （根拠）
```
