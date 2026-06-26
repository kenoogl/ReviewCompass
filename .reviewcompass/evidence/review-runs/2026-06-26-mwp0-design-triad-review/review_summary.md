# Design Triad-Review 結果サマリ：MWP-0 kind 再設計

日時：2026-06-26
フェーズ：design / triad-review
機能：workflow-management
審査対象：`.reviewcompass/specs/workflow-management/design.md`（§5.2・§5.3・§5.4 の MWP-0 追記）
バリアント：design_review_3way_opus_primary
役・モデル：主役 claude-opus-4-8（Anthropic）/ 敵対役 gpt-5.5（OpenAI）/ 判定役 gemini-3.1-pro-preview（Gemini）

## 総合評価：所見対処済み・修正完了

| 役 | 所見数 |
|----|--------|
| 主役（Anthropic claude-opus-4-8） | 5 |
| 敵対役（OpenAI gpt-5.5） | 11 |
| 判定役（Gemini gemini-3.1-pro-preview） | 7 |

## 修正した所見

### CRITICAL-1：型定義表の「14値」が旧値のまま残存（全員一致）
- **内容**：§5.2 フィールド型定義表の `kind` 行に「14値インライン定義」という旧記述が残っていた
- **修正**：「7値インライン定義、§5.2 値域表参照・MWP-0 反映」に変更

### ERROR-2：`in_progress` の `stage: commit_stop_point` が受入 11(6) と矛盾（敵対役・判定役）
- **内容**：§5.3 で `commit_stop_point` を `stage: "commit_stop_point"` として統合すると記述したが、受入 11(6) は `required_action = "commit_stop_point"` 時に `stage=null` と定めており矛盾
- **修正**：§5.3 `in_progress` 節に「commit_stop_point 時は stage=null（受入 11(6) 参照）」の旨を明記。`stage` フィールドの説明も修正

### ERROR-3：`action_parameters` 廃止と受入 11 必須の配置レベルの違いが未記述（全員一致）
- **内容**：§5.3 `blocking_in_progress` 節の廃止フィールドに `action_parameters` を列挙したが、受入 11(2) が `next_action.action_parameters`（`run_maintenance` 時必須）と同名のため矛盾に見えた
- **修正**：廃止対象が「`blocking_in_progress` 詳細フィールドとしての `action_parameters`」であり `next_action.action_parameters`（`run_maintenance` 用）は別物で廃止しないことを注記

### ERROR-4：§Req 12 §11 に廃止予定フィールドが廃止注記なく残存（全員一致）
- **内容**：operation preflight の `state_refs.next_action` 一覧に `direct_features` / `indirect_features` / `next_drafting_gate` が廃止注記なく残存
- **修正**：各行に「2026-06-26 MWP-0 廃止予定」コメントを追記

### ERROR-5：`feature` 廃止と受入 11 必須の関係が未記述（敵対役）
- **内容**：§5.3 `reopen_in_progress` 節で `feature` を廃止と記述したが、受入 11 は `feature` を `next_action` の必須フィールドとして定義しており矛盾に見えた
- **修正**：廃止対象が「旧 reopen 独自の意味での `feature`」であり、`next_action` の必須フィールドとしての `feature` は別物で存続することを注記

### WARN-6：`resuming` 吸収時の null 許容が表に未記載（敵対役・判定役）
- **内容**：`blocking_phase: in_progress` への `resuming` 吸収時に `unit_id`/`parent_unit_id` が null になることが§5.3 表から読み取れなかった
- **修正**：廃止フィールドの説明に「`resuming` 統合時は `unit_id`/`parent_unit_id` が null を許容する」旨を追記

## 対処しない所見（スコープ外・設計フェーズ未解決）

### 受入 11(6) の required_action 制約が §5.2 スキーマ設計に未反映（敵対役・判定役）
MWP-0 以前からある既存の問題。受入 11(6) の各制約（`commit_stop_point` 時の null 制約等）を JSON Schema の `if/then` で表現する作業は、tasks・implementation フェーズで扱う。

### `commit-preflight` がサブコマンド構成表に未登録（主役・敵対役・判定役）
`commit-preflight` の完全な仕様定義（応答スキーマ・exit code・構成表への追記）は MWP-0 の tasks フェーズで対応する。§5.4 は今回の設計スコープ（kind の移動先の定義）として記録する。

### `reopen_classification_required` 旧値が変更意図節に残存（敵対役のみ）
変更意図節の歴史的記述。旧挙動の説明であり実装対象外だが、誤解を招く場合に備えて tasks フェーズで注記追加を検討する。

### `reason` フィールドと最上位 `reasons` 配列の関係（敵対役のみ）
`reason`（`next_action` 内の単一文字列）は design で追加するフィールドであり受入 11 の `reasons`（最上位配列）と別物。tasks フェーズで明確化する。
