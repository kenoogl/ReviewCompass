# 機能横断 design.review-wave 記録

日時：2026-06-26
フェーズ：design
段：review-wave
対象機能：workflow-management（唯一の未完了機能）
持ち越し所見：0件
上流成果物の新旧確認：未実施所見なし

## 審査プロンプト

以下が外部 API（3モデル）へ送信するプロンプト本文である。

---

### 背景と目的

このレビューは ReviewCompass プロジェクトの `workflow-management` 機能における design フェーズの `review-wave`（全機能横断のまとめレビュー）である。

今回の変更（MWP-0）は `next --json` コマンドの応答フィールド `kind` の値域を旧14値から7値へ整理し、コミット操作前確認用の3値を `commit-preflight` サブコマンドへ移動したことである。この変更に対応して `design.md` の §5.2・§5.3・§5.4 が追記・修正された。

`triad-review`（3役レビュー）は完了しており、所見6件の対処が済んでいる。今回の `review-wave` では、対処後の設計が上流の要件の意図・責務境界・受入条件・禁止事項を欠落・弱体化・逸脱・未根拠追加なく引き継いでいるかを独立した視点で確認する。

---

### 上流要件（requirements.md 抜粋）

**Requirement 2 受入 11（`next_action_response.schema.json` の定義）の要点**

- 最上位の必須フィールド：`verdict`・`exit_code`・`next_action`・`reasons`・`current_state` の5つ
- `verdict` は最上位にのみ置き `next_action` 内には含めない
- `next_action` の最低限の必須フィールド（10個）：`kind`・`required_action`・`active_gate`・`feature`・`phase`・`stage`・`required_feature_scope`・`blocked_by`・`future_gates`・`state_refs`
- `action_parameters` は `run_maintenance` のみを対象とする条件付き必須フィールド（6サブフィールド必須）
- `feature` の取り得る値：単一機能名・`"all_features"`・null の3種のみ
- 進行中の作業単位がない場合、`feature`・`phase`・`stage`・`active_gate` はすべて null
- `required_action` の値ごとのフィールド制約（受入 11(6)）：
  - ① `commit_stop_point` 時：`active_gate=null`・`phase=null`・`stage=null`・`blocked_by.type="commit_stop_point"`
  - ② `run_reopen_pending_gate` 時：`active_gate` 非 null・`phase`/`stage` は `active_gate` と一致・`blocked_by=null`
  - ③ `run_reopen_drafting` 時：`active_gate` は `stages/<phase>.yaml#drafting` 形式
  - ④ `repair_workflow_state` 時：`active_gate=null`・`phase=null`・`stage=null`・`repair_reasons` 非空
  - ⑤ `wait_for_human_decision` 時：`blocked_by.type` で停止理由を区別
  - ⑥ `run_maintenance` 時：`action_parameters` に6サブフィールドを含める

**Requirement 2 受入 12（`kind` 値域の限定）**

`commit_candidate`・`commit_mixing_risk`・`commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。

これらは「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であるため。

`next --json` の `kind` は作業の現在地を示す7種類に限定する：
`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`

---

### 審査対象（design.md §5.2〜§5.4 の本文）

**§5.2 `kind` フィールドの値域**

`kind` は `next_action_response.schema.json` 内にインライン `enum` として定義する（`kind` は `next_action_response` 内でのみ参照されるため別ファイル化しない）。

2026-06-26 MWP-0 反映：旧14値を7値へ整理した。旧値との対応は `docs/notes/2026-06-26-next-json-kind-redesign.md` の新旧対照表を正本とする。

| 優先順位 | 値 | 意味 |
|---:|---|---|
| 1 | `reopen_in_progress` | 再開手続き中（サブステップは詳細フィールドで返す） |
| 2 | `blocking_in_progress` | 本線とは別の作業中（maintenance / side track / resume を統合） |
| 3 | `verification_pending` | 書き込み後の検証（post-write verification）待ち |
| 4 | `in_progress` | 通常の作業中（stage / cross_feature_stage / upstream_recheck / commit_stop_point を統合） |
| 5 | `feature_definition_required` | プロジェクト立ち上げ時の初期設定未完了（特殊ケース・verdict: OK） |
| 6 | `completed` | 全作業完了 |
| 7 | `unknown` | 想定外のエラー状態（ファイル破損・整合違反など・verdict: DEVIATION） |

値の追加・変更はこの表と `next_action_response.schema.json` の `enum` 修正で完結する。

**§5.3 `kind` 詳細フィールド設計（MWP-0 反映）**

全 kind 共通フィールド：`kind`（現在地のカテゴリ7値）・`required_action`（次にすべき操作）・`reason`（状態の説明）

`in_progress` の追加フィールド：旧 stage / cross_feature_stage / upstream_recheck / commit_stop_point の4種類を統合する。ただし commit_stop_point を統合する場合、受入 11(6) の制約に従い `stage` の値は null になる（`stage: "commit_stop_point"` という文字列値は取らない）。

| フィールド | 説明 |
|-----------|------|
| `feature` | 対象機能名（cross_feature_stage 相当は `"all_features"` 固定、commit_stop_point 時は null） |
| `phase` | 現在のフェーズ（commit_stop_point 時は null） |
| `stage` | 現在のステージ（commit_stop_point 時は null・受入 11(6) 参照） |
| `upstream_phase` | 上流フェーズ名（upstream_recheck 相当の場合のみ） |

`blocking_in_progress` の追加フィールド：`blocking_phase` サブフィールドで段階を区別（`required` / `in_progress` / `return_pending` の3値）

廃止フィールドと理由：`resuming`（`blocking_phase: in_progress` に統合・この時 `unit_id`/`parent_unit_id` は null を許容）/ `completion_conditions`（`return_conditions` に統一）/ `action_parameters`（他フィールドの重複コピー）/ その他。

注：廃止する `action_parameters` は `blocking_in_progress` 詳細フィールドとしての `action_parameters` であり、`next_action` 直下の条件付き必須フィールド（`required_action = "run_maintenance"` のとき必須・受入 11(2)）とは配置レベルが異なる別物である。後者は廃止しない。

`verification_pending` の追加フィールド：`verification_type` サブフィールドで種類を区別（`pending` / `policy_violation` / `human_decision_required` の3値）

`reopen_in_progress` の廃止フィールド：`next_drafting_gate`（`active_gate` で代替）/ 旧 reopen 独自の意味での `feature`（`required_feature_scope` で代替。`next_action` の必須フィールドとしての `feature` は別物であり存続する）/ `direct_features` / `indirect_features` / `feature_impact_scope_basis`

**§5.4 `commit-preflight` サブコマンドの kind 設計（MWP-0 反映）**

2026-06-26 MWP-0 の受入 12 により、次の3種類の判定を `next --json` の `kind` から除外し `commit-preflight` サブコマンドの出力にのみ含める。

| `kind` | 意味 |
|--------|------|
| `commit_candidate` | コミット可能状態 |
| `commit_mixing_risk` | 異なる作業単位が混在したコミット |
| `commit_unit_stale` | コミット単位の情報が古い |

これら3値は「コミット操作の前確認」であり「作業の現在地」ではない。`commit-preflight` は既存のコミット手前の必須確認手順（手順：commit-preflight → git add → guarded commit）として確立されており、これらを `commit-preflight` に集約することで `next --json` の `kind` 値域を「作業の現在地カテゴリ」に限定できる。

`commit-preflight` サブコマンドが返す `kind` の値域はこの3値とし、`next --json` は `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` を返さない。

---

### `triad-review` で修正済みの所見（参考）

1. §5.2 フィールド型定義表の `kind` 行に「14値」という旧記述が残存 → 「7値インライン定義」に修正済み
2. `commit_stop_point` 時に `stage: "commit_stop_point"`（文字列値）としていたが受入 11(6)① と矛盾 → `stage=null` に修正済み
3. `blocking_in_progress` 廃止フィールドの `action_parameters` が受入 11(2) の必須フィールドと混同されていた → 配置レベルが別物である旨の注記を追記済み
4. operation preflight の参照一覧に廃止予定フィールドが廃止注記なく残存 → 廃止予定コメントを追記済み
5. `reopen_in_progress` の `feature` 廃止が `next_action` の必須フィールドとしての `feature` と混同されていた → 別物である旨の注記を追記済み
6. `resuming` 統合時に `unit_id`/`parent_unit_id` が null を許容することが表から読み取れなかった → 注記を追記済み

---

### レビューの問い

上記の要件（Req 2 受入 11・受入 12）と、設計（§5.2・§5.3・§5.4）を独立して比較し、以下を分析してください。

**主問：** 上流要件の目的・責務境界・受入条件・禁止事項が、`triad-review` 対処後の §5.2〜§5.4 に欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。

具体的に確認してほしい観点（ただし、これ以外の問題を発見した場合も報告してください）：

1. §5.2 の7値リストが受入 12 の7値リスト（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）と完全に一致しているか
2. §5.4 の commit-preflight への3値移動が、受入 12 の「コミット操作の前確認は next --json の kind から除外する」意図を正確に実現しているか
3. §5.3 の `in_progress` における `commit_stop_point` 時の `stage=null` 設計が、受入 11(6)① の制約と整合しているか（`docs/notes` の `stage: commit_stop_point` 記述との関係を含む）
4. §5.3 の `action_parameters` 廃止注記が、受入 11(2)（`run_maintenance` 時の `action_parameters` 条件付き必須）を弱体化していないか

所見は重大度（must-fix / should-fix / consider）と対象節（§5.2 / §5.3 / §5.4）を明示してください。

---

## レビュー結果

実施日：2026-06-27
review-run ディレクトリ：`.reviewcompass/evidence/review-runs/2026-06-26-mwp0-design-review-wave/`

| モデル | 役割 | 所見数 | 最高重大度 |
|---|---|---|---|
| claude-opus-4-8 | 主役 | 2 | WARN |
| gpt-5.5 | 敵対役 | 4 | ERROR |
| gemini-3.1-pro-preview | 判定役 | 2 | ERROR |

### 所見の対処

| クラスタ | 内容 | 対処 |
|---|---|---|
| A（3モデル共通）| 受入 11(6) 全制約がスキーマ設計に未反映 | 先送り済み事項と同根。tasks フェーズで対応 |
| B（WARN）| `reason` vs `reasons` の関係が不明確 | 先送り済み事項と同根。tasks フェーズで対応 |
| C（ERROR・新規）| 「enum 修正で完結する」が受入 12 値域限定を弱める | §5.2 末尾に「値種の増減は受入 12 改訂が必要」を追記 |
| D（WARN・新規）| `completion_conditions` 廃止と action_parameters の混同 | §5.3 廃止フィールドに「`action_parameters.completion_conditions` は別物・存続」を注記 |
| E（WARN・新規）| docs/notes 正本スコープが限定されていない | §5.2 の正本参照に「新旧対照の正本範囲は kind 値域のみ」を追記 |
| F（INFO・新規）| 「廃止」vs「廃止予定」の表現差 | consider 相当。tasks フェーズで統一 |

### 判定

- 新規所見3件（C・D・E）を design.md §5.2〜§5.3 に修正適用済み
- 先送り事項（A・B・F）は tasks フェーズへ引き継ぎ
- 上流要件（Req 2 受入 11・受入 12）の意図・責務境界・受入条件・禁止事項は対処後の設計に引き継がれている
- **design.review-wave：通過**
