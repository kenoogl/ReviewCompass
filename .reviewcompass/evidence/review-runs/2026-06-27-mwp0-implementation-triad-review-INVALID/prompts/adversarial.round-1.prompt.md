# MWP-0 実装レビュー（敵対役）

## あなたの役割

あなたは **敵対役レビュアー（adversarial reviewer）** です。あなたの仕事は「問題を見つけること」ではなく、「問題だと言われていることが本当に問題なのかを批判的に検証すること」です。実装が正しい場合は正しいと言い、過剰な修正要求が不要であれば不要と言ってください。

---

## 背景（主役と同じ）

ReviewCompass の `next --json` コマンドが返す `kind` 値を 14 種類から 7 種類に整理した（MWP-0）。コミット前確認の3値（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）を `commit-preflight` サブコマンドへ移動した。

**要件（受入 12）：**
> `next --json` の `kind` は 7 種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。

---

## 審査対象の claim

以下の4つの claim は「実装に問題がある可能性がある」として提示されたものです。各 claim について、**本当に問題か**を批判的に評価してください。

### claim-A：commit-preflight スキーマと実装の整合性

`_commit_preflight_next_action()` は post-write 検証待ちのとき `kind: "verification_pending"` を返す。しかし `commit_preflight_response.schema.json` の `kind` enum は3値のみ（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）であり `"verification_pending"` を含まない。

**確認してほしいこと：**
- この「スキーマ違反」は実際にランタイムで問題になるか（スキーマ検証が実施されているか）
- `commit-preflight` が `verification_pending` を返すことは、ユーザーに「commit 不可」を伝えるために合理的な動作ではないか
- `commit_preflight_response.schema.json` の役割は何か（スキーマが実際に検証に使われていなければ、不一致は実害なし）
- この不整合が must-fix である根拠はあるか、または should-fix 以下で十分か

### claim-B：blocking_phase サブフィールドの値の不一致

設計書 §5.3 は `blocking_phase` を `required` / `in_progress` / `return_pending` の3値と定義しているが、実装は旧値（`blocking_unit_required` / `blocking_unit_in_progress` / `parent_resume_pending` / `maintenance_in_progress` / `resume_in_progress`）を使っている。

**確認してほしいこと：**
- `blocking_phase` の値は実際に機械処理されているか（WORKFLOW_NAVIGATION.md や別のコードが解釈しているか）、それとも人間が読むためのラベルに過ぎないか
- 旧値は情報量の面で新値より豊富（`in_progress` では `maintenance_in_progress` と `blocking_unit_in_progress` が区別できない）。旧値を維持することに合理性はないか
- テストが `blocking_phase` 値を検証していないのは、この値が外部インターフェイスでないため意図的と言えるか
- この不一致は本当に「設計書に従うべき」か、それとも「設計書の記述が不完全だった（旧値をそのまま使うことを想定していなかった）」という解釈も成立するか

### claim-C：verification_type の `pending` vs `post_write_verification`

設計書 §5.3 の表は `verification_type: "pending"` と書いているが、実装・WORKFLOW_DISCIPLINE_MAP.yaml・テストはすべて `"post_write_verification"` を使っている。

**確認してほしいこと：**
- 実装・カタログ・テストが一貫して `"post_write_verification"` を使っているなら、設計書の表の `"pending"` は「誤記」または「意図の先走り」であり、設計書を更新するだけで済む（実装変更不要）ではないか
- WORKFLOW_DISCIPLINE_MAP.yaml の `by_verification_type` ルックアップは `"post_write_verification"` キーで動作しており、`"pending"` に変更すると動かなくなる。つまり実装の整合性はすでに取れており、設計書の記述が実態と合っていないだけではないか
- `lightweight_self_check` は設計書に記載がないが、実装とカタログに存在する。これは「設計書の漏れ」として設計書を更新すれば済む軽微な問題ではないか
- この claim は実質「設計書の更新が必要」という指摘に過ぎず、実装の修正は不要だという主張は成立するか

### claim-D：if/then 制約の不完全実装

① の省略（`blocked_by.type = "commit_stop_point"` をスキーマに含めていない）
②③ の省略（`phase`/`stage` と `active_gate` の一致チェックがスキーマにない）

**確認してほしいこと：**
- ②③ の `phase`/`stage` と `active_gate` の一致は JSON Schema では表現できない（`$data` pointer は非標準拡張）。省略は技術的に不可避であり、leave-as-is が正しいのではないか
- ① の `blocked_by.type = "commit_stop_point"` について：実装内で `blocked_by.type` が `"workflow_phase_end"` と `"commit_stop_point"` の2種類が使われているなら、スキーマに一方を固定する制約は書けない。この省略も技術的制約による合理的な判断ではないか
- そもそも `commit_stop_point` の時に `blocked_by.type` が何であるべきかは実装で決まることであり、スキーマがその実装詳細を強制することは適切か

---

## 期待する回答形式

各 claim について：
- **評価**：「問題として成立する」「問題として成立しない」「部分的に成立する」のいずれか
- **根拠**：判断の根拠（なぜ問題ありまたは問題なしと判断するか）
- **推奨アクション**：must-fix / should-fix / leave-as-is / 設計書更新のみ
- **反論がある場合の提案**：問題なしと判断した場合に、主張の誤りを修正するための説明

最後に全体評価として以下を記載してください：
- 実装として許容できる範囲に収まっているか（overall: OK / CONCERNS）
- 最も重大な問題があるとすればどれか（なければ「なし」）
