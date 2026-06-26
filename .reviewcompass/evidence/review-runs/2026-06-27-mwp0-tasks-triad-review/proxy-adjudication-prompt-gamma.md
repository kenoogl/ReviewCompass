# proxy_model 判断依頼：クラスタ γ（受入11(6)⑥の責務重複）

## 依頼の位置付け

workflow-management 機能の tasks フェーズ triad-review（MWP-0 追記分）における must-fix クラスタの採否判断を依頼する。あなたの役割は「どの修正案を採用するか」を決定することである。実装は担当しない。

## 問題の説明

Requirement 2 受入11(6) は `required_action` 値ごとのフィールド制約（スキーマの if/then 表現）を定義している：

- ① `commit_stop_point` 時：`active_gate=null` 等
- ② `run_reopen_pending_gate` 時：`active_gate` 非 null 等
- ③ `run_reopen_drafting` 時：`active_gate` は `stages/<phase>.yaml#drafting` 形式
- ④ `repair_workflow_state` 時：`active_gate=null`、`repair_reasons` 非空
- ⑤ `wait_for_human_decision` 時：`blocked_by.type` で停止理由を区別
- ⑥ `run_maintenance` 時：`action_parameters` に6サブフィールド必須

現在の tasks.md では：
- **T-015 完了条件2**：「条件付き必須フィールドが `if/then` 構文で定義されていること：`repair_reasons`（`required_action = "repair_workflow_state"` のとき必須）・`action_parameters`（`required_action = "run_maintenance"` のとき必須）（手動確認）」と記載 → これは④と⑥を扱っている
- **T-020 先送り事項(a)**：「受入11(6)②〜⑥の `required_action` 値ごとのフィールド制約を `if/then` 構文で定義する」と記載 → ⑥が T-015 と重複している

⑥（run_maintenance 時の action_parameters）が T-015 と T-020 の両方に含まれており、どちらが実装責任を持つのかが不明確になっている。

## 元 review raw への参照

- claude-sonnet-4-6.round-1.txt（WARN）：「T-020 先送り事項(a)の対象範囲を②〜⑤に限定するか、①⑥は T-015 で対処済みとの注記が望ましい」と指摘
- gpt-5.5.round-1.txt（WARN）：「受入11(6) は machine-checkable な構造を要求しており、各 required_action 値の担当タスクを明示する必要がある。⑥が重複しており①の commit_stop_point についてもどのタスクが担当するか不明」と指摘
- gemini-3.1-pro-preview.round-1.txt（WARN）：「⑥（action_parameters等）は T-015 の対象と重複しており、実装・テスト責務が両方に定義されると重複や完了確認漏れが生じる」と指摘（3モデル共通）

## 候補案

**案 A（T-020 先送り事項(a)の範囲を②〜⑤に限定し、注記を追加）**

T-020 責務4(a) を次のように修正する：
> 受入11(6)**②〜⑤**の `required_action` 値ごとのフィールド制約を `next_action_response.schema.json` の `if/then` 構文で定義する（**①は T-015 完了条件2の `repair_reasons` で対処済み、⑥は T-015 完了条件2の `action_parameters` で対処済みのため除外**）

- 利点：重複が排除され、T-020 の担当範囲が明確になる。T-015 を読めば①⑥は対処済みとわかる。
- 弱点：T-020 のテスト要件にも「受入11(6)②〜⑥」と記載されているため、そちらも「②〜⑤」に修正が必要になる。

**案 B（T-015 に「①⑥のみを担当」と注記し、T-020 は②〜⑥のまま維持）**

T-015 完了条件2の if/then 記述に注記を加える：
> 条件付き必須フィールドが `if/then` 構文で定義されていること：`repair_reasons`（④相当）・`action_parameters`（⑥相当）（**①③⑤は受入11(6) 制約として別途検証が必要。②〜⑥の詳細機械検証は T-020 先送り事項(a) で対処**）

- 利点：T-020 の記述を変えなくて済む。
- 弱点：T-015 に T-020 への前方参照が生まれる。また T-020 の「②〜⑥」には引き続き⑥が含まれているため重複が解消されない。

**案 C（T-015 の if/then 記述を④⑥のみに明示し、T-020 で①②③④⑤⑥の全範囲を担当と整理）**

T-015 完了条件2を修正して「④`repair_reasons` と⑥`action_parameters` の if/then のみを手動確認」に限定し、T-020 では「①〜⑥すべてを機械検証可能な if/then で定義する（④⑥は T-015 で手動確認済みの範囲と重複するが、機械検証の追加なので問題なし）」と整理する。

- 利点：受入11(6)の完全カバーが T-020 に集約される。
- 弱点：T-015 の手動確認と T-020 の機械検証が重複し、どちらが正本か曖昧になる可能性がある。

## 私（メインセッション LLM）の推薦案

**案 A**を推薦する。T-020 の先送り事項(a)を②〜⑤に明示的に絞り込み、「①⑥は T-015 対処済み」と注記することで、責務の重複を最小の変更で解消できる。ただしテスト要件の「②〜⑥」も「②〜⑤」に合わせて修正が必要である点に注意する。

## あなたへの問い

この問題（受入11(6)⑥の T-015 と T-020 の責務重複）に対して、案 A・案 B・案 C のどれを採用すべきか、あるいはいずれも採用せず別の対処が必要か、判断してください。

回答は以下のフィールドを持つ YAML のみを返してください（マークダウンのコードブロック記法は使わず、YAML テキストだけを返してください）。`proxy_model_id` には、あなた自身のモデル ID を記入してください：

proxy_model_id: （例：gpt-5.5）
finding_id: gamma
adopted_option: （案A / 案B / 案C / 別案 のいずれか）
rationale: （判断理由、2〜4文）
rejected_options:
  - option: （棄却した案の名前）
    reason: （棄却理由）
final_label: must-fix
