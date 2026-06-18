# 設計判断 ラウンド2：Registry 登録を前提とした3案の比較評価

phase: design
criteria: workflow_management_phase1_schema_definitions_cluster_a_id_ref_design
round_id: round-2

## ラウンド1 の確定事項

前ラウンドの3者評価で次が確定した。

1. **Python `jsonschema` ライブラリで2ファイルを相互参照させるには、`referencing.Registry`（スキーマ登録表）に両ファイルを明示的に登録する実装が必須である。** 案ア・イ・ウのどれを選んでも、この実装コストに差はない。
2. **`RefResolver`（旧 API）は `jsonschema` v4.18 以降で非推奨。** 新 API は `referencing.Registry` + `referencing.Resource`。

---

## ラウンド2 の評価対象

「Registry にどのキーで登録するか」という具体的な実装比較を評価してほしい。
以下に3案の登録コードの骨格を示す。

### 案ア：`$id` を HTTP URL 形式にする

スキーマファイルの中身：
```json
// required_action.schema.json
{ "$id": "https://schema.reviewcompass.example/required_action.schema.json", ... }

// next_action_response.schema.json
{ "$id": "https://schema.reviewcompass.example/next_action_response.schema.json",
  "$ref": "./required_action.schema.json" を内部で使用 }
```

テスト・検証コードの骨格：
```python
from referencing import Registry, Resource

vocab   = json.load(open(".reviewcompass/schema/required_action.schema.json"))
response = json.load(open(".reviewcompass/schema/next_action_response.schema.json"))

registry = Registry().with_resources([
    ("https://schema.reviewcompass.example/required_action.schema.json",
     Resource.from_contents(vocab)),
    ("https://schema.reviewcompass.example/next_action_response.schema.json",
     Resource.from_contents(response)),
])
```

登録キーはスキーマの `$id` と一致するため、`$ref: "./required_action.schema.json"` は
`https://schema.reviewcompass.example/required_action.schema.json` に解決され、
登録済みリソースが見つかる。

---

### 案イ：`$id` を省略する

スキーマファイルの中身：
```json
// required_action.schema.json
{ /* $id なし */ ... }

// next_action_response.schema.json
{ /* $id なし */
  "$ref": "./required_action.schema.json" を内部で使用 }
```

テスト・検証コードの骨格：
```python
from pathlib import Path
from referencing import Registry, Resource

schema_dir = Path(".reviewcompass/schema").resolve()  # 絶対パスに変換

vocab   = json.load(open(schema_dir / "required_action.schema.json"))
response = json.load(open(schema_dir / "next_action_response.schema.json"))

# file:// URI は実行環境の絶対パスを含む
vocab_uri    = (schema_dir / "required_action.schema.json").as_uri()
response_uri = (schema_dir / "next_action_response.schema.json").as_uri()

registry = Registry().with_resources([
    (vocab_uri,    Resource.from_contents(vocab)),
    (response_uri, Resource.from_contents(response)),
])
```

`$id` がないため、基底 URI は登録キー（`file://` URI）になる。
`$ref: "./required_action.schema.json"` は `file:///.../required_action.schema.json` に解決され、
登録済みリソースが見つかる。
ただし登録キーに実行環境の絶対パスが含まれるため、別マシンに配布しても同じ登録コードは使えない。

---

### 案ウ：`$id` を URN のまま維持し、`$ref` も URN に変える

スキーマファイルの中身：
```json
// required_action.schema.json
{ "$id": "urn:reviewcompass:schema:required_action", ... }

// next_action_response.schema.json
{ "$id": "urn:reviewcompass:schema:next_action_response",
  "$ref": "urn:reviewcompass:schema:required_action" を内部で使用 }
```

テスト・検証コードの骨格：
```python
from referencing import Registry, Resource

vocab   = json.load(open(".reviewcompass/schema/required_action.schema.json"))
response = json.load(open(".reviewcompass/schema/next_action_response.schema.json"))

registry = Registry().with_resources([
    ("urn:reviewcompass:schema:required_action",    Resource.from_contents(vocab)),
    ("urn:reviewcompass:schema:next_action_response", Resource.from_contents(response)),
])
```

ファイルパスや URL と無関係に、URN という固定の識別子だけで登録・参照できる。
登録キーはどの環境でも同じ文字列であるため、テストコードを変更せず配布できる。

---

## 評価してほしいこと

上記3案のテスト・検証コード骨格を前提に、以下を技術的に分析してほしい。

1. **JSON Schema Draft 2020-12 の仕様準拠性：** 案ア・イ・ウそれぞれで、`$ref` の解決が仕様上どのように定義されているか。仕様上の保証がある案とそうでない案はどれか。

2. **デプロイ先が変わったときの壊れにくさ：** スキーマを別のプロジェクトに配布したとき、登録コードを書き換えずに済む案はどれか。

3. **`referencing.Registry` の動作との整合性：** Python の `referencing` ライブラリで実際に上記コードが正しく動作するか。バリデータが `$ref` を正常に解決できるか。

4. **意図しない落とし穴：** 各案を採用した場合に、テストが通るのに実際には想定と異なる動作をするリスクがあるか。

5. **推奨案とその理由：** 3案のうちどれが最も適切か。または上記3案以外に良い方法があれば提案してほしい。

選択肢の枠を超えた分析を歓迎する。
