# proxy_model 判断依頼：クラスタ β（完了条件4の根拠参照誤り）

## 依頼の位置付け

workflow-management 機能の tasks フェーズ triad-review（MWP-0 追記分）における must-fix クラスタの採否判断を依頼する。あなたの役割は「どの修正案を採用するか」を決定することである。実装は担当しない。

## 問題の説明

T-020 の完了条件4に次の記述がある：

> WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述を更新する（**design §5.4 反映**）。

しかし design §5.4 は `commit-preflight` サブコマンドの kind 設計（3値の値域定義）を扱っており、WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止については何も書いていない。

正しい根拠は reopen 分類文書（`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）の「手引き改修：WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述改修が必要」節にある。

「design §5.4 反映」という参照は誤りであり、誰かが後から追うと誤った設計節を正本として混同する可能性がある。

## 元 review raw への参照

- claude-sonnet-4-6.round-1.txt（WARN）：「完了条件4に reopen 分類文書の参照がなく、design §5.4 だけでは根拠として不十分」と指摘
- gpt-5.5.round-1.txt（WARN）：「design §5.4 は commit-preflight の kind 設計であり、WORKFLOW_NAVIGATION.md 更新を直接指示していない。根拠は reopen 分類文書にある」と指摘
- gemini-3.1-pro-preview.round-1.txt（ERROR）：「対象の design §5.4 には該当の記述が存在しない。タスク定義内で誤った設計箇所を根拠として参照しており、トレーサビリティが損なわれている」と指摘（3モデル共通・gemini は ERROR）

## 候補案

**案 A（根拠参照を正しい文書に差し替える）**

完了条件4を次のように修正する：
> WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述を更新する（根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md` §手引き改修）。

- 利点：誤った参照が除去され、正しい根拠文書に辿れるようになる。最小限の変更で問題を解消できる。
- 弱点：なし（修正内容は自明）

**案 B（両方の根拠を列挙する）**

> WORKFLOW_NAVIGATION.md の `next_drafting_gate` 廃止に伴う記述を更新する（根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md` §手引き改修。関連：design §5.4 commit-preflight 設計）。

- 利点：分類文書と design の両方から辿れる。
- 弱点：design §5.4 は直接の根拠ではないため「関連」として残すのが正確だが、将来的に混同を招く可能性がある。

## 私（メインセッション LLM）の推薦案

**案 A**を推薦する。誤った参照を取り除き正しい文書に差し替えるだけであり、変更量も最小である。design §5.4 は直接の根拠でないため、案 B のように残す必要はない。

## あなたへの問い

この問題（完了条件4の根拠参照誤り）に対して、案 A・案 B のどれを採用すべきか、あるいはいずれも採用せず別の対処が必要か、判断してください。

回答は以下のフィールドを持つ YAML のみを返してください（マークダウンのコードブロック記法は使わず、YAML テキストだけを返してください）。`proxy_model_id` には、あなた自身のモデル ID を記入してください：

proxy_model_id: （例：gpt-5.5）
finding_id: beta
adopted_option: （案A / 案B / 別案 のいずれか）
rationale: （判断理由、2〜4文）
rejected_options:
  - option: （棄却した案の名前）
    reason: （棄却理由）
final_label: must-fix
