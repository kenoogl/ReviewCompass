# 設計判断の評価：JSON Schema の $id 形式と相対 $ref の組み合わせ

phase: design
criteria: workflow_management_phase1_schema_definitions_cluster_a_id_ref_design
round_id: round-2

## 評価の背景

ReviewCompass というワークフロー管理ツールが、`next --json` コマンドの出力仕様を
JSON Schema Draft 2020-12 の形式で 2 ファイルに定義する。

### ファイル配置と役割

どのプロジェクトに配布されても、2 ファイルは常に同じディレクトリ `.reviewcompass/schema/` に並ぶ。

```
.reviewcompass/
  schema/
    required_action.schema.json      # "required_action" の19語彙を定義する語彙ファイル
    next_action_response.schema.json # コマンド応答の構造を定義するファイル（語彙ファイルを参照する）
```

`next_action_response.schema.json` は `required_action` フィールドの値を制限するために、
語彙ファイルを参照する必要がある。

### テスト環境

Python の `jsonschema` ライブラリ（Draft 2020-12 対応）でスキーマを検証する。
テストコードは `.reviewcompass/schema/` ディレクトリからファイルを読み込んで検証を行う。

---

## 確定している設計事項

以下は変更の対象ではなく、前提として固定されている。

- スキーマ形式：JSON Schema Draft 2020-12
- `$schema` キー：`"https://json-schema.org/draft/2020-12/schema"`
- 語彙ファイルの `type`：`"string"`、`enum`：19語彙の列挙
- 応答ファイルの `type`：`"object"`、必須フィールドの列挙

---

## 問題となっている設計箇所

当初の設計案では、2 ファイルの `$id`（スキーマの識別子）として URN 形式を使っていた。

```json
// required_action.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:required_action",
  "type": "string",
  "enum": ["repair_workflow_state", "run_post_write_verification", ...]
}
```

```json
// next_action_response.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:reviewcompass:schema:next_action_response",
  "type": "object",
  "properties": {
    "next_action": {
      "properties": {
        "required_action": {
          "$ref": "./required_action.schema.json"  ← 相対パス
        }
      }
    }
  }
}
```

**問題の核心：** JSON Schema では `$id` が参照解決の基底 URI（起点）となる。
URN（`urn:` で始まる識別子）には階層的なパス構造がないため、
`"./required_action.schema.json"` のような相対パスを解決しようとしても
行き先が RFC 3986 の規則上未定義になる。
バリデータによって動作が異なり、参照解決に失敗する可能性がある。

---

## 検討中の 2 案

### 案ア：`$id` を HTTP URL 形式に変更し、相対 `$ref` を維持する

```json
// required_action.schema.json
{
  "$id": "https://schema.reviewcompass.example/required_action.schema.json",
  ...
}

// next_action_response.schema.json
{
  "$id": "https://schema.reviewcompass.example/next_action_response.schema.json",
  "properties": {
    "next_action": {
      "properties": {
        "required_action": {
          "$ref": "./required_action.schema.json"  ← 相対パスのまま
        }
      }
    }
  }
}
```

`schema.reviewcompass.example` は実在しなくてよく、論理的な名前空間として機能する。
HTTP URL 形式の `$id` の場合、相対 `$ref` は `$id` を起点として解決されるため、
`./required_action.schema.json` は `https://schema.reviewcompass.example/required_action.schema.json`
に解決される。ただし、バリデータはその URL にアクセスするわけではなく、
あくまでスキーマを識別子として参照する（URI として解決するかはバリデータの実装に依存する）。

### 案イ：`$id` を省略し、ファイルパスで解決させる

```json
// required_action.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  // $id なし
  "type": "string",
  "enum": [...]
}

// next_action_response.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  // $id なし
  "type": "object",
  "properties": {
    "next_action": {
      "properties": {
        "required_action": {
          "$ref": "./required_action.schema.json"  ← 相対パス
        }
      }
    }
  }
}
```

`$id` がない場合、多くのバリデータはファイルの読み込みパスを基底 URI として使う。
Python の `jsonschema` ライブラリでは `RefResolver` にファイルパスを渡すことで
相対 `$ref` が解決される。ただし、スキーマに識別子がないため、
バリデータ内部でスキーマを指定するときはファイルパスを使う必要がある。

---

## 評価してほしいこと

上記 2 案について、以下の観点から技術的に分析してほしい。

1. JSON Schema Draft 2020-12 の仕様に基づいて、どちらの案が相対 `$ref` を正しく解決できるか
2. Python の `jsonschema` ライブラリで 2 ファイルを読み込んで相互参照を検証する場合、
   各案はどのような動作をするか
3. 2 つのスキーマファイルが常に同じディレクトリに配置される前提で、
   デプロイ先のプロジェクトが変わっても参照が壊れないようにするには、どちらが適切か
4. 上記 2 案以外に、この問題を解決するより良い方法があれば提案してほしい
5. 案ア・案イそれぞれの主要なリスクと制限を挙げてほしい

選択肢の枠を超えた分析を歓迎する。
