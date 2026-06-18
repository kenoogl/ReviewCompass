# 設計深掘りレビュー：effect_kind と承認ゲート要否の設計

## 背景と現状

ReviewCompass の設計では、各操作（required_action）に `effect_kind` という属性を付与する。
`effect_kind` は機械化設計メモ §3.1 で「副作用の種別」と定義されており、次の5つの値を取る。

```
read / write / state_mutation / external_call / irreversible_action
```

同メモには「`effect_kind: irreversible_action` を持つ操作は承認ゲートを通過しなければならない」とも書かれている。
つまり `effect_kind` は「副作用の種別を表す属性」であると同時に「承認ゲートの要否を決める判定基準」として使われている。

## 問題の状況

現在の設計には次の食い違いがある。

§3 の対応表では次の操作を `effect_kind: state_mutation`（状態変更）に分類している。

- `repair_workflow_state`（状態修復コマンドの実行）
- `apply_approved_reopen_plan`（spec.json の workflow_state を書き換える）
- `run_reopen_start`（reopen plan の生成と in-progress YAML 作成）
- `advance_reopen_after_commit_stop_point`（commit stop point の消費）
- `advance_reopen_after_approval_stop_point`（step advance）
- `finalize_reopen`（completed YAML への移動）

一方 §3.1 では、これら6つを「承認ゲートが必要な操作」として列挙している。

承認ゲートの要否の判定基準が `effect_kind: irreversible_action` であるとすれば、
上記6つは `state_mutation` に分類されているため、承認ゲートをスキップする実装になる。

また Phase 5 の計画として「`effect_kind: irreversible_action` に承認ゲートを機械的に強制する」とある。
分類が `state_mutation` のまま変わらなければ、Phase 5 でも承認ゲートが掛からない。

## 検討の参考材料

**`state_mutation` と `irreversible_action` の実質的な違いについて**

`commit_stop_point`（git commit）は `irreversible_action` に分類されている。
`apply_approved_reopen_plan`（spec.json の workflow_state 更新）は `state_mutation` に分類されている。

どちらも「元に戻すには意図的な操作が必要」という意味では同程度に不可逆である。
しかし git commit は「外部リポジトリへの公開」という側面を持つのに対し、
spec.json の更新はローカルファイルの変更である点が異なる。

この違いが `effect_kind` の分類に影響すべきかどうかは設計の意図による。

**`effect_kind` が1つの属性で2役を担うことの意味**

「副作用の種別（何をするか）」と「承認ゲートの要否（どのくらい危険か）」は、
原理的には別の問いである。

- `external_call`（外部 API 呼び出し）は承認ゲートが不要な場合もある（例：レビュー実行）
- `state_mutation`（状態変更）でも承認ゲートが必要な場合がある（上記6つの操作）
- `write`（ファイル書き込み）は通常承認ゲートが不要

現在の設計で `irreversible_action` だけが「承認ゲート必要」の唯一の判定値になっているが、
実際には `state_mutation` でも承認ゲートが必要な操作が存在することが今回判明した。

## レビューで答えてほしい問い

1. 「副作用の種別」と「承認ゲートの要否」を1つの属性（`effect_kind`）で表現することは
   設計として成立するか。それとも本質的に別の軸として分離すべきか。
   どちらが正しいかを根拠とともに示すこと。

2. 上記6つの操作（`apply_approved_reopen_plan` 等）が `state_mutation` とされていることと、
   承認ゲートが必要であることは、矛盾なく両立できるか。
   両立できるなら、その設計を具体的に説明すること。

3. Phase 5 で「`effect_kind: irreversible_action` に承認ゲートを機械的に強制する」という計画は、
   今回の問題を踏まえて妥当か。
   この計画を維持する場合と変更する場合の影響を示すこと。

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    question_id: "1" / "2" / "3"
    description: |
      （分析内容）
    rationale: |
      （根拠）
```
