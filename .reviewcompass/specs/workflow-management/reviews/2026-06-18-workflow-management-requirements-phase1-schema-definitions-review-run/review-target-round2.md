# 深掘りレビュー（ラウンド2）：クラスタ A・D の集中審査

round_id: round-2
phase: requirements
gate: stages/requirements.yaml#triad-review
criteria: workflow_management_phase1_schema_definitions_requirements_reopen_triad_review

## 審査の位置付け

ラウンド1の3者レビュー（claude-sonnet-4-6・gpt-5.5・gemini-3.1-pro-preview）の結果、
2つのクラスタについて複数モデルが指摘したため、以下の集中審査を実施する。

- **クラスタ A**：`run_maintenance` 時の `action_parameters` フィールドの「必須性」と「追加フィールド許可」が要件レベルで曖昧
- **クラスタ D**：後方互換フィールド `pending_gates`・`next_pending_gate` の整合条件が未定義

ラウンド1の所見は以下に示す。各クラスタについて設計上の論点を深く分析してほしい。

---

## ラウンド1 所見（参考）

### クラスタ A に関わる所見

**claude-sonnet-4-6（WARN）：**
> AC11(6) の「maintenance_action 等6フィールドを含める」という記述は、要件として不完全。
> 要件レベルで6フィールド全名称を列挙するか、あるいは「スキーマファイルで完全定義する
>（要件はフィールド数と必須性のみ規定）」と明示的に委譲する記述に改めるべき。

**gpt-5.5（ERROR）：**
> `run_maintenance` 時に必須となる `action_parameters` の6フィールドが具体名・型・必須性
> として列挙されていない。requirements 段階で D-003 §4.2 の該当6フィールドを明示するか、
> 厳密な参照先を指定する必要がある。

### クラスタ D に関わる所見

**claude-sonnet-4-6（WARN）：**
> `pending_gates`・`next_pending_gate` をオプションフィールドとして残すと明記されているが、
> 新規実装のコンシューマがこれらのフィールドを無視すべきか読み取ってもよいか、あるいは
> 将来削除される予定があるかが要件に記載されていない。

**gpt-5.5（WARN）：**
> オプションであることは明示されているが、存在する場合に `pending_gates` が `future_gates`
> と一致すべきか、`next_pending_gate` が `active_gate` と一致すべきかが不明である。
> これによりスキーマ上は矛盾した JSON を許容し、既存コードとの互換性確認が曖昧になる。

---

## 審査対象となる要件本文（受入11の関連箇所）

以下は `.reviewcompass/specs/workflow-management/requirements.md` Requirement 2 受入11 の
該当部分を正確に引用したものである。

### 受入11（2）: next_action 必須フィールドと条件付きフィールド

```text
（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、
値域は design で確定）・`required_action`（受入10のスキーマを参照）・`active_gate`
（文字列または null）・`feature`（文字列または null）・`phase`（文字列または null）・
`stage`（文字列または null）・`required_feature_scope`（配列）・`blocked_by`
（オブジェクトまたは null）・`future_gates`（配列）・`state_refs`（オブジェクト）の
10フィールドとする。これに加え、`repair_reasons`（配列）は `repair_workflow_state` 時に
必須となる条件付きフィールド（非空配列・最低1要素）とし、`action_parameters`（オブジェクト）
は `run_maintenance` 等の補助情報が必要な action 種別で必須となる条件付きフィールドとして
定義する。
```

### 受入11（5）: 後方互換フィールド

```text
（5）後方互換のため `pending_gates`・`next_pending_gate` はオプションフィールドとして
定義し、このスキーマの正本フィールドは `future_gates`・`active_gate` とする。
```

### 受入11（6）: required_action 値ごとのフィールド制約

```text
（6）`required_action` の値ごとにフィールドの値制約（相互排他）がある。以下は D-003 §4.2
で確定している制約であり、スキーマはこれらを機械的に検証できる構造で表現する（スキーマ上の
表現方法は design で確定）。① `commit_stop_point` の時：`active_gate=null`・`phase=null`・
`stage=null`・`blocked_by.type="commit_stop_point"`。② `run_reopen_pending_gate` の時：
`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`。
③ `run_reopen_drafting` の時：`active_gate` は `stages/<phase>.yaml#drafting` 形式・
`phase`/`stage` はその drafting 単位と一致。④ `repair_workflow_state` の時：
`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` に修復理由を含める。
⑤ `wait_for_human_decision` の時：`blocked_by.type` で停止理由を区別。⑥ `run_maintenance`
の時：`action_parameters` に `maintenance_action`・`allowed_scope`・`allowed_files`・
`completion_conditions`・`active_stack_frame_id`・`parent_frame_id` を含める。
上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action`
種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）。
```

---

## 審査の論点

### 論点 A：action_parameters の6フィールドの必須性

現在の受入11(6) は `run_maintenance` 時に `action_parameters` に6フィールドを「含める」
（contain）と記述している。

以下の問いに対して、設計上の論点を分析してほしい。

**問い A-1**：要件フェーズでは「6フィールドを含める（含めなければならない）」という記述で
十分か。それとも「6フィールドは全て必須（required）であり、追加フィールドは許可するか
禁止するか」まで要件として確定すべきか。どちらの判断が設計上の手戻りリスクを最も小さくするか。

**問い A-2**：「含める」という記述を「6フィールド全て必須とし、追加フィールドは design で
確定する」と読むことができるか。それとも「最低限この6フィールドが存在すればよい（追加は
自由）」と読むべきか。

**問い A-3**：テスト駆動開発（TDD）の観点で、失敗テスト（`tests/tools/test_phase1_schema_definitions.py`
に17テストが存在）を書いた開発者が「含める」という記述から一意に実装できるか。

### 論点 D：pending_gates の整合条件

現在の受入11(5) は後方互換フィールドを「オプションフィールドとして定義」とだけ記述している。

**問い D-1**：スキーマとしてオプションフィールドを定義する場合、「存在した場合は正本フィールドと
一致しなければならない」という整合条件を要件に含めるべきか。それとも整合条件はスキーマの
外にある実装やランタイムが保証すればよい責任境界か。

**問い D-2**：`pending_gates` が `future_gates` と一致しない場合、スキーマはこれを不正な
JSON として弾くべきか（schema validation エラー）、それとも semantics の問題として
スキーマ外で扱うべきか。どちらが `next --json` の利用者（人間・LLM・ツール）にとって
より分かりやすい契約か。

**問い D-3**：受入11(5) に整合条件の記述がなくても、設計フェーズで十分に解決できるか。
それとも要件として確定しないと下流フェーズで解釈が分かれるリスクがあるか。

---

## 期待する出力

各論点（A-1、A-2、A-3、D-1、D-2、D-3）について分析し、**要件として現状維持でよいか、
修正すべきか**について根拠とともに結論を示してほしい。

結論を特定の方向に誘導する意図はない。設計の観点から最も合理的な判断を独立して下してほしい。

severity は次のように使う：
- `ERROR`：このまま design フェーズへ進むと重大な解釈差が生じるブロッカー
- `WARN`：修正が望ましいが、design フェーズで解決可能
- `INFO`：情報的な観察、修正不要
