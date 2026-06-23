---
date: 2026-06-18
record_type: design-note
status: draft
topic: integrated-design-selection-and-execution-layers
related:
  - docs/notes/2026-06-16-next-json-unique-state-redesign.md
  - docs/notes/2026-06-18-mechanized-workflow-execution-design.md
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
---

# 統合設計メモ：選択層と実行層の接続

## 1. このメモの目的と入力資料の位置づけ

本メモは、2つの設計メモを入力資料として、それらの接続点を整理したものである。

| 入力資料 | 役割 | 通称 |
|---|---|---|
| `2026-06-16-next-json-unique-state-redesign.md` | **選択層の設計**：`next --json` が返す唯一アクションの定義、19段階優先順位、`required_action` 語彙、reopen plan compiler | D-003 |
| `2026-06-18-mechanized-workflow-execution-design.md` | **実行層の設計**：選択されたアクションを実行する仕組み（operation contract・タスク分類・有効プロンプト構造化・Phase 1-6） | 機械化設計 |

本メモはこの2本を入力として参照し、接続点を整理する。

---

## 2. 全体構造：選択層と実行層の境界

### 2.1 処理連鎖（end-to-end）

```
next --json
  → required_action（唯一）を返す      ← 選択層（D-003）が保証
    → operation contract を参照          ← 実行層（機械化設計）が規定
      → preconditions を機械確認
        → 言語タスク（LLM が担当）または機械タスク（ツールが自動実行）
          → postconditions を機械確認
            → next --json を再実行
```

### 2.2 境界の定義

**選択層（D-003）** は次を保証する。

- `next --json` が返す `required_action` は常に1つだけである
- `phase` / `stage` / `active_gate` は active workflow unit がある時だけ非 null になる
- 不整合状態では通常アクションを返さず `repair_workflow_state` を返す

**実行層（機械化設計）** は次を規定する。

- 各 `required_action` に対応する operation contract（前提条件・副作用種別・事後条件）
- タスク分類：言語タスク（LLM）/ 機械タスク（ツール）/ 人間判断（明示的チャンネル）
- 有効プロンプトの構造（言語タスクの仕様書として再定義）

選択層が「何をすべきか」を唯一に決め、実行層が「どうやって実行するか」を規定する。この分離により、`next --json` の出力さえ正しければ、実行層は独立して強化できる。

---

## 3. `required_action` 語彙と operation contract の対応

D-003 §4.2 で定義された19種の `required_action` それぞれについて、
機械化設計 §3.1 の `effect_kind` および実行構造を対応付ける。

| required_action | effect_kind | 実行主体 | approval_required |
|---|---|---|---|
| `repair_workflow_state` | `state_mutation` | 構造化コマンド | はい |
| `run_post_write_verification` | `external_call` | ツール（run_review.py） | いいえ |
| `wait_for_human_decision` | `read` | LLM（提示） | いいえ |
| `record_human_decision` | `state_mutation` | 構造化コマンド | いいえ（承認ゲートの部品） |
| `run_maintenance` | `write` / `state_mutation`（§7 item 6） | LLM + ツール | 操作による（§7 item 6） |
| `draft_reopen_plan_candidates` | `write` | LLM（言語タスク） | いいえ |
| `apply_approved_reopen_plan` | `state_mutation` | 構造化コマンド（spec rollback） | はい |
| `advance_reopen_after_approval_stop_point` | `state_mutation` | 構造化コマンド | はい |
| `repair_canonical_documents` | `write` | LLM（言語タスク） | いいえ |
| `commit_stop_point` | `state_mutation` | guarded commit | はい |
| `advance_reopen_after_commit_stop_point` | `state_mutation` | 構造化コマンド | はい |
| `run_reopen_drafting` | `write` | LLM（言語タスク） | いいえ |
| `run_reopen_pending_gate` | `external_call` / `write` / `state_mutation`（§3.2 参照・§7 item 6） | ツールまたは LLM（gate 種別による） | いいえ（§3.2 参照） |
| `finalize_reopen` | `state_mutation` | 構造化コマンド（reopen-finalize） | はい |
| `collect_required_decisions` | `write` | LLM（言語タスク） | いいえ |
| `draft_reopen_classification` | `write` | LLM（言語タスク） | いいえ |
| `run_reopen_start` | `state_mutation` | 構造化コマンド（reopen-start） | はい |
| `run_workflow_stage` | ステージ種別による（§7 item 6） | LLM または ツール | ステージ種別による（§7 item 6） |
| `completed` | `read` | LLM（候補提示） | いいえ |

### 3.1 `approval_required: true` の操作（承認ゲートが必要な操作）

D-003 §3（原則）と機械化設計 §3.1 の承認ゲート定義を統合する。

`approval_required: true` となる操作は、実行前に必ず承認ゲートを通す。
`approval_required` は `effect_kind`（副作用の種別）とは独立した属性であり、
`state_mutation` であっても承認ゲートが必要な操作がある。
該当する `required_action` は次のとおり。

- `commit_stop_point`（guarded commit）
- `apply_approved_reopen_plan`（spec.json workflow_state の rollback）
- `run_reopen_start`（reopen plan の生成と in-progress YAML 作成）
- `advance_reopen_after_commit_stop_point`（commit stop point の消費）
- `advance_reopen_after_approval_stop_point`（step advance）
- `finalize_reopen`（completed YAML への移動）
- `repair_workflow_state`（状態修復コマンドの実行）

`record_human_decision` は「判断を記録する操作」（`effect_kind: state_mutation`、`approval_required: false`）であり、
承認ゲートの対象操作ではなく、承認ゲートを構成する部品である。
承認ゲートを通す対象はあくまで上記リストの操作であり、
`record_human_decision` 自体を承認ゲートに通す必要はない。

`run_maintenance` は操作内容によって変わる。maintenance YAML の `approval_required` が `true` のものは承認ゲートを通す。

### 3.2 `run_reopen_pending_gate` の gate 種別による分岐

`run_reopen_pending_gate` は `active_gate` の種別に応じて実行層が変わる。

| active_gate の種別 | 実行主体 | effect_kind | approval_required |
|---|---|---|---|
| `triad-review` / `review-wave` | ツール（run_review.py） | `external_call` | いいえ |
| `alignment` | LLM（言語タスク：承認材料の提示と合意確認） | `write` | いいえ |
| `approval` | 承認ゲート経由（構造化コマンド） | `state_mutation` | いいえ（承認要求の設定自体は可逆。承認が必要なのはその後の対象操作） |
| `drafting`（run_reopen_drafting として分離） | LLM（言語タスク） | `write` | いいえ |

`approval` gate は D-003 §8.4 S-032 に従い、承認要求の構造化（`reopen-set-blocker`）が実行内容であり、直接 completed にしない。

---

## 4. 19段階優先順位と Phase 0-6 の関係

### 4.1 Phase 0 は D-003 の実装

機械化設計 §7 は「本メモの設計を実装してから D-003 と照合する」と述べていた。
ただし、**選択層が壊れたままでは実行層の機械化が無意味になる**。

D-003 §6 の19段階優先順位を「**Phase 0**」と位置づけ、機械化設計の Phase 1 より先に着手する。
Phase 0 と Phase 1 はほぼ同時並行で進めることができるが、
Phase 1 の語彙（`effect_kind`・`phase_boundary` 等）は Phase 0 の実装でも参照するため、
**Phase 1 のスキーマ定義が Phase 0 の実装の前提**になる。

```
Phase 1（スキーマ定義）→ Phase 0（選択層実装）→ Phase 2〜6（実行層強化）
```

### 4.2 各 Phase の目的と D-003 との関係

| Phase | 目的 | D-003 との関係 |
|---|---|---|
| Phase 0 | 19段階優先順位・`required_action` 唯一化・invariant 検査・reopen plan compiler の実装 | D-003 全体が Phase 0 の仕様 |
| Phase 1 | `effect_kind` / `phase_boundary` 語彙・operation contract スキーマ・スナップショットスキーマ定義 | D-003 §8.0 の軸定義（feature / phase / stage）とスキーマを整合させる |
| Phase 2 | 読み取り専用 registry（`operation-list --json`） | D-003 の `command registry / operation schema`（§8 情報源一覧）の実装 |
| Phase 3 | preflight 警告（ブロックなし） | D-003 §5.3 の invariant 関数を preflight に組み込む |
| Phase 4 | 有効プロンプトの構造化（言語タスクの仕様書化） | D-003 §4.1 の JSON 契約フィールドと有効プロンプトの `language_task` 構造を対応させる |
| Phase 5 | 機械的ブロック（ガード追加） | D-003 §7 の commit gate invariant 検査を強制に昇格 |
| Phase 6 | LLM 裁判官（意味的監査） | D-003 §8 のシナリオを監査テストケースとして使う |

### 4.3 Phase 0 の完了条件

D-003 §7.1 に記載の6つの失敗テストが全てパスし、
D-003 §9 に記載の「現在の D-003 reopen に必要な workflow state repair」が
機械的に検出できること。

---

## 5. 統一定義

### 5.1 承認ゲート（approval gate）

**選択層からの視点（D-003）：** `required_action` として `wait_for_human_decision` / `record_human_decision` のペアで表現される。

**実行層からの視点（機械化設計）：** `approval_required: true` を持つ操作の前に必須の、明示的チャンネルによる人間判断記録。

**統一定義：** 取り消し不能な操作を実行する前に、人間の判断を構造化コマンドで記録し、
その記録内容に応じて選択層（`next --json`）が次の操作を決めるチャンネル。

```
wait_for_human_decision
  → (人間が判断を下す)
    → record_human_decision（判断内容を記録するだけ）
      → next --json を再実行
          ↓ 承認     → 対象の不可逆操作を実行
          ↓ 拒否     → 対象操作の中止。次の required_action は各 operation contract で定義
          ↓ 保留     → 再び wait_for_human_decision へ
          ↓ 修正要求 → 再起草へ戻す（draft 系の required_action）
```

- `wait_for_human_decision` と `record_human_decision` は必ずペアで完結する。
- `record_human_decision` は「判断を記録する操作」であり、対象操作の実行を直接引き起こさない。
- 記録された判断の内容（承認 / 拒否 / 保留 / 修正要求）を読んで次の `required_action` を決めるのは、
  選択層（`next --json`）の責務である。
- 拒否時・保留時に `next --json` が何を返すかは各 `required_action` の operation contract で定義する。
- 「記録が完了した」ことと「承認された」ことは別の事実である。記録の完了は対象操作の許可を意味しない。
- `approval gate` という語は「このペアの構造と、その後の選択層による分岐を含む全体」を指す。

reopen の `approval` gate（`run_reopen_pending_gate` の一種）は、
この承認ゲートを `reopen-set-blocker` → `wait_for_human_decision` → `record_human_decision` の順で踏む。
拒否された場合の動作（reopen の中止・再起草・blocker 維持）は reopen の operation contract で定義する。

### 5.2 側道とスタック（side track stack）

**選択層からの視点（D-003 §8.6）：** side track frame をスタックとして管理し、`next --json` は常にスタック top の frame だけを返す。`required_action=run_maintenance` として表現される。

**実行層からの視点（機械化設計 §3.3）：** `side-track-push/pop` で側道を開閉する。push 時に staged 差分 digest とファイルセットを記録し、コミット混線を検査する。

**統一定義：** 側道はスタックとして管理され、以下の属性を持つ。

```yaml
# スタックフレームの最低限の属性（D-003 §8.6 + 機械化設計 §3.3 の統合）
frame_id: string
kind: maintenance | side_track
parent_frame_id: string | null
pushed_by: string
allowed_scope: list
allowed_files: list
completion_conditions: list
return_to: string
title: string                    # Navigator WebUI 向けの人間可読ラベル
spawned_from:
  outer_node: string             # 派生元の大工程
  inner_node: string             # 派生元の細かい作業
  trigger: string                # きっかけとなった操作
staged_file_digest: string       # コミット混線検査用
staged_file_set: list            # コミット混線検査用
```

`return_to` は機械参照であり、LLM が復帰先を解釈・選択しない。
`side-track-pop` は top frame だけを閉じ、`next --json` が直下の frame を自動的に再開する。

`max_depth`（既定 2）を超えた側道開始は Phase 3 で警告、Phase 5 でブロックする。

### 5.3 状態スナップショット（workflow state snapshot）

**選択層からの視点（D-003）：** `next --json` の `current_state` と `state_refs` として部分的に表れる。`next --json` 自体はスナップショットを出力しない。

**実行層からの視点（機械化設計 §8）：** Navigator WebUI が読む機械可読ファイル。Phase 1 でスキーマを定義し、Phase 2 で出力を開始する。

**統一定義：** `.reviewcompass/runtime/workflow-state-snapshot.yaml` に出力される現在状態ファイル。`next --json` の実行後に自動更新される。

```yaml
# スナップショットの必須項目（D-003 current_state + 機械化設計 §8 を統合）
schema_version: "1"
generated_by: "next --json"
generated_at: string

current_work:
  required_action: string
  title: string                  # 人間可読ラベル
  outer_node: string             # 大工程名（feature / reopen / maintenance）
  inner_node: string             # 細かい作業名（phase / stage / gate）
  active_gate: string | null

active_side_tracks:
  - title: string
    spawned_from:
      outer_node: string
      inner_node: string
      trigger: string
    return_to:
      outer_node: string
      inner_node: string
    staged_file_digest: string

git_tree_summary:
  status: clean | dirty
  dirty_files: list

post_write_manifest_summary:
  status: none | pending | complete

workflow_state_summary:
  completed_features: list
  in_progress_feature: string | null
  in_progress_phase: string | null
```

スナップショットは `next --json` の副産物であり、`next --json` 自体の出力を変えない。
スナップショットが古い（`next --json` を実行せずに手動更新した）場合は信頼しない。

---

## 6. D-003 の未決事項と機械化設計の関係

D-003 §9 は「現在の D-003 reopen は workflow state repair が必要」と述べている。
この状態修復は次の順序で行う。

1. **Phase 0 の invariant 検査を実装する**（D-003 §7.2 ステップ2の `validate_reopen_state_for_next()`）
2. 実装後に `next --json` を実行し、`verdict=DEVIATION`・`required_action=repair_workflow_state` が返ることを確認する
3. `reopen-recompile`（D-003 §7.2 ステップ9）を実装し、reopen plan の派生値を再導出する
4. `reopen-recompile` を実行して in-progress YAML の `pending_gates` と `commit_stop_point` の整合を機械的に修復する

機械化設計 §7 は「D-003 の再開は本メモの実装完了後に判断する」と述べていたが、
Phase 0 の実装は機械化設計 Phase 1〜2 と並行して進めることができる（スキーマ定義が先）。

---

## 7. 未確定事項（継続検討）

次の事項は両メモで未確定または判断保留になっており、実装時に決める。

1. **`run_reopen_pending_gate` の gate 種別ごとの effect_kind と approval_required の定義（§3.2 の詳細補足）**
   - `drafting` は `write`（承認不要）、`triad-review` は `external_call`（承認不要）、
     `review-wave` は `external_call`（承認不要）として概ね決まる。
   - `alignment` は `write`（承認不要）に確定。LLM が整合確認レポートをファイルに書き出す操作であり、
     ワークフロー状態フラグの更新は後続の操作（`commit_stop_point` 等）が担う。§3.2 と一致。
   - `approval` gate は §3.2 を参照（承認要求の設定自体は `state_mutation`・承認不要）
   - `run_workflow_stage` のステージ種別（異なる operation）との混同注意：`run_workflow_stage` の effect_kind は §7 item 6 を参照

2. **Phase 0 と Phase 1 の並行作業の分割**（方針確定）
   - Phase 0 の TDD（テスト先行開発）を始める前に必要な最小 Phase 1 作業は次の2点のみ。
     1. `required_action` の19語彙を `.reviewcompass/schema/` 配下にスキーマファイルとして正式定義する
     2. `next --json` の応答スキーマ（`kind`・`feature`・`required_action` 等のフィールドと型）を同配下に定義する
   - D-003 の設計書（`docs/notes/2026-06-16-next-json-unique-state-redesign.md`）には語彙がすでに列挙されており、スキーマファイル化が残作業。
   - `effect_kind`・`phase_boundary`・operation contract スキーマ・スナップショットスキーマは Phase 0 と並行で定義してよい（Phase 0 の選択ロジックはこれらを参照しない）。

3. **スナップショット出力の実装方針**
   - 設計方針は §5.3 で確定：`next --json` の副産物として実行後に自動出力する。専用サブコマンドは設けない。
   - 未確定なのは実装詳細（`check-workflow-action.py` のどのコードパスで書き出すか）。Phase 2 の `operation-list --json` 実装と合わせて確定する。

4. **D-003 §8 の72シナリオを Phase 6 の監査テストとして使う方法**
   - シナリオを構造化テストフィクスチャとして保存するか、
     テストコード内に直接記述するかは Phase 6 着手時に決める。

5. **承認記録と対象操作の紐付け方法**
   - `record_human_decision` が記録する判断と、承認対象となった `required_action` をどう結びつけるか（セッション識別子・タイムスタンプ・操作 ID 等）。
   - `wait_for_human_decision` で設定した承認要求と、`record_human_decision` の記録を同一の承認フローとして追跡できるデータ構造が必要。
   - Phase 0 の invariant 検査実装または Phase 5 の承認ゲート強制実装時に具体化する。

6. **`effect_kind` が操作内容によって変わる操作のスキーマ上の扱い**
   - `run_maintenance`・`run_reopen_pending_gate`・`run_workflow_stage` は、実行される内部操作・ゲート種別によって `effect_kind` が変わる。
   - 機械化設計 §3.1 は `effect_kind` を単一 enum で定義しているが、これらの「複合操作」が単一値制約に適合するかは未確定。
   - 選択肢：① 最大副作用の `effect_kind` を代表値として採用し注記で補足する　② `effect_kind` を list 型に拡張してスキーマを修正する　③ 複合操作を内部ステップに分解して各ステップを単一 enum にする。
   - Phase 1 のスキーマ定義時に確定する。

---

## 8. この統合設計メモの扱い

本メモは入力資料（D-003・機械化設計）の接続点を整理した**作業中メモ**である。
正本への昇格は行わない。

実装が進み、Phase 0 の requirements/design が更新される段階で、
本メモの内容を適宜 `.reviewcompass/specs/workflow-management/` へ織り込む。
その時点で本メモの status を `superseded` に更新する。
