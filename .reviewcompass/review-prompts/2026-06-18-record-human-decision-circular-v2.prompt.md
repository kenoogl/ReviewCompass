# 設計深掘りレビュー：record_human_decision の循環依存（第2回）

## 設計の前提

ReviewCompass は、ワークフローの各操作を `effect_kind`（副作用の種別）で分類し、
取り消し不能な操作には実行前に「承認ゲート」を通すことを必須としている。

`effect_kind` の語彙：
- `read`：読み取りのみ
- `write`：ファイルへの書き込み（取り消し可能）
- `state_mutation`：システム状態の変更（取り消し可能）
- `external_call`：外部 API の呼び出し
- `irreversible_action`：取り消し不能な操作。実行前に承認ゲートを必ず通す。

承認ゲート（§5.1 の定義）：

```
1. wait_for_human_decision：LLM が判断材料を提示し、人間が判断を下す
2. record_human_decision：人間の判断内容を構造化ファイルに書き出す
3. 対象の不可逆操作を実行する
```

## 問題の状況

`required_action`（次に実行すべき操作の識別子）の一つに `record_human_decision` がある。

設計メモ §3.1 は `record_human_decision` を `irreversible_action` と分類し、
「実行前に承認ゲートを通す必要がある」としている。

一方、§5.1 の承認ゲート定義では、`record_human_decision` はゲートのステップ 2 に位置する。

この2つを組み合わせると：

- `record_human_decision` を実行するには承認ゲートのステップ 1・2 を先に踏む必要がある
- ステップ 2 は `record_human_decision` そのもの
- よって `record_human_decision` を実行するには `record_human_decision` の完了が先に必要

## レビューで答えてほしい問い

1. `record_human_decision` はなぜ `irreversible_action` に分類されたと考えられるか。
   その分類の背景にある意図を分析すること。

2. `record_human_decision` という操作の性質を分析すること。
   - この操作は本当に取り消し不能か。取り消せるとすれば何をすれば取り消せるか。
   - 取り消した場合に何が失われるか。
   - 承認ゲートのステップ 2 としての役割と、独立した `required_action` としての役割は
     同じものか、別物か。

3. この循環依存はどこに根本原因があるか。
   `record_human_decision` の分類の問題か、承認ゲートの定義の問題か、
   それとも別の何かか。

4. 循環を解消するために設計のどこを変えるべきか、独自に提案すること。
   提案は具体的に、かつ他の操作や承認ゲート全体との整合を保つこと。

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
