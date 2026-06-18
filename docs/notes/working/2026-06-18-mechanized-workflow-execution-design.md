---
date: 2026-06-18
record_type: design-note
status: draft
topic: mechanized-workflow-execution
related:
  - docs/notes/2026-06-16-next-json-unique-state-redesign.md
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
---

# ワークフロー機械化最大化の設計メモ

## 1. 動機

### 1.0 ReviewCompass の価値と本設計の位置づけ

仕様駆動開発（要件・設計・実装を段階的に仕様化しながら進める開発手法）では、**裁定**（何が正しいか・何をすべきか・これで十分かの判断）が随所に発生する。この裁定は専門知識と認知負荷を要し、人によって結果がばらつく。

ReviewCompass の価値は**裁定の負荷を下げながら、裁定の品質と追跡性を上げる**ことである。

| 価値 | 手段 |
|---|---|
| 次に何をすべきかの裁定をなくす | `next --json` が唯一のアクションを返す |
| 成果物が正しいかの裁定を支援する | AI による複数モデルレビュー |
| 裁定を記録・再利用可能にする | 承認記録・判断記録の構造化保存 |

本設計はこの価値の**実現精度を上げる**ものである。現状は「裁定負荷を下げているように見えて、実は LLM という不透明な場所に移しているだけ」になっている部分がある。

- `next --json` が唯一のアクションを返さなければ、「次に何をすべきか」の裁定は消えていない
- 有効プロンプトが長く曖昧なままでは、LLM の解釈次第で動きが変わり、裁定の品質が安定しない
- LLM が暗黙に判断を変えると、裁定が行われたこと自体が記録されず、追跡性が失われる

機械化は自動化が目的ではなく、裁定の負荷を本当に下げるための手段である。

### 1.1 現状の構造

現在の処理連鎖は次のとおりである。

```
next --json を実行
  → next_action を返す（唯一性は現状未保証）
    → kind / required_action から DISCIPLINE_MAP で判定点（decision point）を解決
      → 判定点に対応する有効プロンプトを生成・ロード
        → LLM が読む
          → LLM が判断・実行
```

`next --json` が返すのは「アクション（next_action）」であり「判定点」ではない。判定点は DISCIPLINE_MAP 上の概念であり、返ってきたアクションの `kind` と `required_action` を照合して初めて決まる。

### 1.2 不安定要素

この連鎖には4つの構造的な不安定点がある。

1. **`next --json` の唯一性未保証**：現状の実装では、`commit_stop_point` と `pending_gate` が同一応答に混在するなど、返すアクションが唯一に定まらない場合がある（2026-06-16 設計メモが指摘する中核欠陥）。これは有効プロンプト以前の問題である。
2. **LLM のバイアス**：訓練の偏りにより、指示を正しく読んでいても従えない場合がある。
3. **手作業のタスク組み立て**：人が手順を組む場合、抜け・順序誤り・解釈ずれが入る。
4. **遵守の無保証**：有効プロンプトを読んだかどうか、読んだとおりに動いたかどうか、現状は誰も確認できない。

### 1.3 従来の対処の限界

「有効プロンプトを読ませる強制（読了証跡、ガード）」は不安定要素を軽減するが根本的には解消しない。LLM が有効プロンプトに従う、という前提自体が不安定要素であるためである。不安定要素1（唯一性未保証）はそもそも有効プロンプト到達前の問題であり、読了強制では対処できない。

---

## 2. 中核思想

**機械実行できるものを機械に移し、LLM の担当範囲を言語タスクだけに絞る。人間判断が必要な場面は、構造化されたチャンネルを通じて明示的に記録する。**

目指す処理連鎖：

```
next --json
  → 機械コマンドが実行できる部分を自動実行
    → 人間判断が必要な場合は明示的チャンネルで受け取り記録
    → LLM は言語タスクの入出力だけを担当
      → 機械が事後条件を検査
        → next --json を再実行
```

実際の開発は設計通りに進まない。アドホックな対応や手順の変更、優先順位の急な変化が起きる。この設計はそれを排除するのではなく、**人間判断の入り方を構造化**することで対応する。LLM が暗黙に手順を変えることと、人間が明示的に判断を記録することは根本的に異なる。

---

## 3. タスクの分類

判定点が定まった後の各タスクを次の2種類に分ける。

### 3.1 機械タスク（ツールが実行する）

言語理解を必要とせず、アルゴリズムで確定できる処理。

| 例 | 実行主体 |
|---|---|
| ファイルの存在確認・ハッシュ照合 | ツール |
| spec.json フラグの更新 | 構造化コマンド |
| staged 差分の digest 計算 | ツール |
| 前提条件・事後条件の検査 | guard |
| レビュー実行の起動・結果収集 | ツール |
| commit・push の実行 | guarded コマンド |
| 次の `next --json` の実行 | 自動 |

機械タスクは **operation contract（操作契約）** として形式化する。各操作が以下の属性を持つことで、機械が事前検査と実行強制を担える。

| 属性 | 役割 |
|---|---|
| `canonical_commands` | LLM が記憶でコマンドを推測せず、registry（操作台帳）から正式コマンドを得る |
| `effect_kind` | 副作用の種別。`read / write / state_mutation / external_call` の4値 |
| `approval_required` | 実行前に人間の承認が必要か。`true / false` |
| `sequence` | `serial_only`（直列専用）か `single_step` か。並列実行の機械的禁止に使う |
| `pending_conflicts` | 他の保留中操作との混線条件。worktree 混線（同一作業ツリーへの別変更混入）を事前に検出する |
| `preconditions` | 操作開始前に満たすべき機械確認条件 |
| `postconditions` | 操作完了後に機械が確認する条件 |

`approval_required: true` を持つ操作は、承認ゲート（`approval_gate`）を通過してからでないと実行できない。該当する操作は `commit_stop_point`・`apply_approved_reopen_plan`・`run_reopen_start`・`advance_reopen_after_commit_stop_point`・`advance_reopen_after_approval_stop_point`・`finalize_reopen`・`repair_workflow_state` であり、統合設計メモ §3.1 を正本とする。`approval_required` は副作用の種別（`effect_kind`）とは独立した属性であり、`state_mutation` であっても `approval_required: false` になる操作がある（例：`record_human_decision` は承認ゲートの部品であり、自身は承認不要）。

### 3.2 言語タスク（LLM が担当する）

言語理解・生成・判断が不可欠な処理。

| 例 | 入出力の形式 |
|---|---|
| 要件・設計の起草 | 入力：既存文書。出力：更新文書 |
| 所見のトリアージ判断 | 入力：構造化所見。出力：ラベル＋理由 |
| 審査・分類の候補生成 | 入力：状態情報。出力：構造化候補リスト |
| 曖昧な判断の提示 | 入力：状態。出力：選択肢＋推奨 |

言語タスクも、入力と出力の形式を明示し、LLM の解釈余地を最小化する。

### 3.3 人間判断タスク（明示的チャンネルを通じて記録する）

実際の開発では、機械も LLM も進めない判断が必要になる場面がある。この設計はそれを「例外」として扱うのではなく、明示的なチャンネルとして組み込む。

**重要な区別：**

| 種類 | 何が起きるか | 結果 |
|---|---|---|
| **LLM の暗黙の逸脱** | LLM が文脈を読んで手順を飛ばす・変える | 変更が記録されず、機械は新しい状態を知らない。後から追跡不能 |
| **人間の明示的な判断** | 人間が構造化コマンドを通じて決定を下す | 判断がシステム状態に記録され、機械は新しい正しい状態から再開できる |

**明示的チャンネルの一覧：**

| action | 用途 |
|---|---|
| `wait_for_human_decision` | 機械が進めない判断点で、判断材料を提示して人間に委ねる |
| `record_human_decision` | 人間の判断をシステム状態に記録し、機械が新しい状態から再開できるようにする |
| side track push | 予期しない作業が発生したとき、スタックに積んで逸脱を明示的に記録する |
| `collect_required_decisions` | あらかじめ予測できなかった判断が必要になったとき、機械が立ち止まり問いを構造化して提示する |
| `repair_workflow_state` | 状態が予測外の形に壊れたとき、修復の必要性を明示して人間判断を求める |

これらを通じた人間判断は柔軟性を保ちながら、すべての決定を追跡可能にする。

**側道のネストとコミット混線：**

側道が別の側道を開くと、作業が縦方向に深くネストする。このとき、staged エリア（コミット待ちの変更置き場）に複数の作業レベルの変更が混在する「コミット混線」が発生する。

| 問題 | 影響 |
|---|---|
| 側道 A の変更と側道 B の変更が同じ staged エリアに混在する | どの変更がどの作業レベルに属するか追跡不能になる |
| 混線したままコミットする | 作業単位の粒度が崩れ、後から revert できなくなる |
| 深さ無制限に側道が開く | 復帰条件が管理できなくなる |

機械的対策：

- 側道 push 時点で次をスタックに記録する
  - **作業タイトル**（人間が読めるラベル。Navigator で「今何の作業をしているか」として表示される）
  - **派生元**（どの外側工程・内側工程から、何をきっかけに側道に入ったか）
  - **復帰先**（側道を抜けた後に戻る作業位置）
  - その時点の staged 差分 digest とファイルセット（コミット混線の検査に使う）
- コミット直前に `operation-preflight commit --json` が「staged ファイルが現作業レベルのファイルセットに収まっているか」を検査する
- 超過分（別レベルの変更が混入）を検出した場合はコミットを中断して報告する
- `max_depth`（最大ネスト深さ。デフォルト 2）を超えた側道開始を機械が警告し、`repair_workflow_state` で人間判断を求める

---

## 4. 有効プロンプトの再定義

### 4.1 従来の役割と限界

現在の有効プロンプトは「参照文書を1本に束ねた説明書」である。LLM に何をすべきかを伝えるが、何を機械が実行するかは記述されていない。

### 4.2 新しい役割

有効プロンプトは「言語タスクの仕様書」になる。機械タスクはツールが自動実行するため、有効プロンプトには記述しない。

### 4.3 新しい構造

```yaml
decision_point: next_action_kind:completed

# 機械タスク（ツールが事前に自動実行済み）
preconditions_checked:
  - 全 workflow_state が完了していること
  - 進行中ファイルが存在しないこと
  - post-write pending がないこと

# LLM への言語タスク指示
language_task:
  document_kind: none  # 生成文書なし（提示のみ）
  input:
    - next_action（next --json の返値）
    - 利用者の直近の指示
  output_format:
    - 次作業候補のリスト（構造化）
    - 利用者への提示文
  constraints:
    - 利用者の指示がない場合は候補提示のみ
    - spec.json の変更は行わない
    - side track 開始前に3行の宣言を行う

# 事後条件（ツールが実行後に検査）
postconditions:
  - 出力が output_format に従っていること

# 必須の終了操作（ツールが自動実行）
on_completion:
  - next --json を再実行する
```

---

## 5. 有効プロンプト監査ツール

有効プロンプトが新しい構造に従っているかを監査するツールを設ける。

### 5.1 第1層：機械検査（自動実行）

| 検査項目 | 検査方法 |
|---|---|
| 参照先ファイルの実在 | パスの存在確認 |
| アンカーが実在する節を指しているか | `<a id="...">` タグの照合 |
| 全判定点で有効プロンプトが生成できるか | 全エントリを一括生成 |
| 必須構造節が揃っているか | `preconditions_checked`・`language_task`・`postconditions`・`on_completion` の存在確認 |
| 有効プロンプトの長さが上下限内か | 文字数確認（空・全文丸ごとを検出） |
| DISCIPLINE_MAP 未登録の action kind がないか | コードが返せる kind と MAP の照合 |
| review 対象の manifest（対象一覧）が実際の review-run ターゲットと一致するか | manifest のファイルセットと review-run の実行ターゲットを照合 |
| staged ファイルが現作業レベルのファイルセットに収まっているか（コミット混線検査） | 側道スタックに記録したファイルセットとの差分確認 |

### 5.2 第2層：意味的妥当性（LLM 裁判官）

第1層を通過した判定点について、LLM 裁判官が次を確認する。

```
判定点: <id>
有効プロンプト本文: <内容>
WORKFLOW_NAVIGATION.md の該当節: <内容>

問い：
1. 前提条件は、この判定点で機械的に確認できる条件をすべて網羅しているか？
2. 言語タスクの入出力形式は明確か？LLM の解釈余地が残っていないか？
3. 事後条件は、言語タスクの出力が正しいかを確認できるか？
4. 不足している機械タスクはあるか？
```

出力形式（構造化）：

```json
{
  "decision_point": "completed",
  "verdict": "gap_found",
  "gaps": [
    {
      "section": "language_task.constraints",
      "description": "side track 宣言ルール（WORKFLOW_NAVIGATION_FOR_CLAUDE.md §2 規則6）が未含有",
      "severity": "must_fix"
    }
  ],
  "unnecessary": [],
  "confidence": "high"
}
```

---

## 6. 判定点ごとの機械化率の目標

| 判定点 | 現状の機械化率 | 目標 |
|---|---|---|
| `completed` | 低（提示内容は LLM 任せ） | 候補リストの構造化、side track 宣言の強制 |
| `post_write_verification` | 中（レビュー起動はツール） | 対象ファイル・ダイジェスト・バリアント選択を自動決定 |
| `maintenance_in_progress` | 中（YAML 読み取りはツール） | completion_conditions の機械確認 |
| `reopen_in_progress` | 低（gate 選択は LLM 依存） | active_gate を機械が一意に決定（2026-06-16 設計メモ §6） |
| `stage`（通常ワークフロー） | 中（stage 選択はツール） | 入力文書のロード、出力先・形式の自動決定 |

---

## 7. D-003 との関係

2026-06-16 設計メモ（D-003 reopen 設計）は `next --json` の唯一セレクタ契約を定義した。本メモはその延長として、**セレクタが返した判定点以降の処理**を機械化する設計を補う。

**実装の順序方針（統合設計メモ §4.1 を正本とする）：**

統合設計メモ §4.1 で方針が確定した。D-003 を「Phase 0」として位置づけ、本メモの Phase 1 スキーマ定義の直後に着手する。

```
Phase 1（スキーマ定義）→ Phase 0（D-003 選択層実装）→ Phase 2〜6（実行層強化）
```

Phase 0 の完了条件は統合設計メモ §4.3 を参照。旧来の「本メモの実装完了後に D-003 と照合する」という方針は統合設計メモ §4.1 によって更新された。

---

## 8. 未確定事項（次の検討で決める）

1. 有効プロンプトの新フォーマットのスキーマ定義ファイルは `.reviewcompass/schema/effective-prompt-format.yaml` に置く（方針決定済み）。`WORKFLOW_DISCIPLINE_MAP.yaml` 本体は現在 `docs/operations/` にあるが、配置移動は Phase 2 完了後に独立した保守作業として行う（後述）。
2. 機械タスクの自動実行をどのコマンドが担うか（`next --json` の呼び出し側か、新規サブコマンドか）
3. LLM 裁判官（§5.2）の実行基盤（既存の `run_review.py` を使うか、新規スクリプトか）
4. 言語タスクの入出力形式の具体的なスキーマ定義
5. 状態スナップショット（Navigator WebUI が読む機械可読な現在状態ファイル）の形式。Phase 1 でスキーマを定義し、Phase 2 で出力を開始する。最低限必要な項目は次のとおり（Navigator WebUI 計画書 §2・§5 を参照）。

```yaml
current_work:
  title: "（人間が読めるラベル）"
  outer_node: "（外側の大工程名）"
  inner_node: "（内側の細かい作業ステップ名）"

active_side_tracks:           # 入れ子になった側道をスタック順に並べる（最初が最上位）
  - title: "（この側道の作業タイトル）"
    spawned_from:
      outer_node: "（派生元の外側工程）"
      inner_node: "（派生元の内側工程）"
      trigger: "（きっかけとなった操作）"
    return_to:
      outer_node: "（復帰先の外側工程）"
      inner_node: "（復帰先の内側工程）"
    staged_file_digest: "（コミット混線検査用）"

git_tree_summary:
  status: "clean / dirty"
  dirty_files: []

post_write_manifest_summary:
  status: "none / pending / complete"
```

出力先：`.reviewcompass/runtime/workflow-state-snapshot.yaml`

---

## 9. この設計が変えないこと

- `next --json` の出力形式（既存の `kind`・`required_action`・`effective_prompt_path` の構造）
- WORKFLOW_NAVIGATION.md の判定点の定義
- 既存の guard（guarded-git-commit 等）の動作

本設計は既存の机械的正確性の基盤の上に、機械化層を追加する。既存契約は変えない。

また、次のことも変えない。

- **意味的な正しさの判断（semantic judgment）を自動化しない**。LLM 裁判官（§5.2）は監査の補助であり、最終判断は人間が担う。
- **`next --json` を「次に何をするか」の唯一の起点**とする役割は変えない。operation contract はその選択結果を実行しやすくする補助機構であり、`next --json` を置き換えない。
- **既存のガード（guarded-git-commit 等）の動作**は変えない。新しい検査はガードの前段に追加する。

---

## 10. 段階的開発ステップ

一度に全機能を実装すると既存の動作を壊すリスクが高く、手戻りも大きくなる。次の6段階で進める。各 Phase の終了時に `next --json` が `completed` を返す状態に戻してからコミットする。Phase をまたいだ途中状態はコミットしない。

### Phase 1：語彙・スキーマ定義（実行挙動を変えない）

目的：後の実装の土台になる語彙とスキーマ（型定義）を確定する。この段階でコードを動かす変更は一切しない。

- `effect_kind` の語彙を確定する（`read / write / state_mutation / external_call` の4値。`irreversible_action` は廃止）
- `approval_required` を operation contract の独立した属性として定義する（`true / false`）
- `phase_boundary` の語彙を確定する（`scratch / evidence / canonical_update / approval_gate`）
- operation contract の YAML スキーマを定義する
- コミット混線の検査ルール（ファイルセット記録方式）を文書化する
- **新規スキーマファイルは最初から `.reviewcompass/schema/` に置く**（既存ファイルの移動は Phase 2 完了後に別タスクで行うため、ここでは新規ファイルのみ）
- **状態スナップショットのスキーマを定義する**（§8 項目5 の形式。Navigator WebUI 計画書 §2・§5 と整合させる）

完了条件：スキーマファイルが `.reviewcompass/schema/` に存在し、テストでスキーマ自体の整合性を確認できること。状態スナップショットのスキーマが Navigator WebUI 計画書の必須項目を網羅していること。

### Phase 2：読み取り専用 registry（既存の動作を変えない）

目的：各操作の contract 情報を返す読み取り専用 API を作る。

- `check-workflow-action.py operation-list --json` を実装する
- 各操作の `canonical_commands / effect_kind / approval_required / sequence / pending_conflicts` を返す
- `next --json` をはじめ既存コマンドの動作は変えない

完了条件：全操作が registry に登録されており、テストで内容がスキーマに適合することを確認できること。

**Phase 2 完了後に独立した保守タスクを実施する：**

> `docs/operations/` にある実行時参照ファイル（`WORKFLOW_DISCIPLINE_MAP.yaml` 等）を `.reviewcompass/` 配下へ移動する。`check-workflow-action.py` のパス参照、テストのパス参照を更新し、`next --json` が移動前と同じ結果を返すことを確認してコミットする。機能実装とファイル移動を同一コミットに混在させない。

### Phase 3：事前検査（警告のみ、ブロックしない）

目的：問題を検出して報告するが、実行を止めない。既存フローへの影響を最小化する。

- `operation-preflight <id> --json` を実装する
- `pending_conflicts` の検出（警告のみ）
- 側道スタックの depth 計算（`max_depth` 超過の警告のみ）
- コミット混線の検出（staged ファイルのセット差分、警告のみ）
- 有効プロンプトの第1層機械検査（§5.1）をこの preflight に組み込む

完了条件：各警告が正しい条件で発火し、誤検知がないことをテストで確認できること。

### Phase 4：有効プロンプトの構造化

目的：有効プロンプトを「言語タスクの仕様書」に作り替える。

- DISCIPLINE_MAP を新構造（`preconditions_checked / language_task / postconditions / on_completion`）に更新する
- `document_kind` を各判定点に明示する
- 既存の `next --json` の `effective_prompt_path` との互換を保ちながら新構造を追加する

完了条件：全判定点で新構造の有効プロンプトが生成でき、テストで構造の完全性を確認できること。

### Phase 5：機械的強制（ガード追加）

目的：警告だけだったものを機械的にブロックする。実行への影響が最も大きい段階。

- `sequence: serial_only` の実行ガードを追加する
- コミット混線を検出したらコミットをブロックする
- `max_depth` 超過の側道開始をブロックし `repair_workflow_state` を要求する
- `approval_required: true` の操作に承認ゲートを強制する

完了条件：ブロック条件が正しく機能し、かつ正常パスがブロックされないことをテストで確認できること。

### Phase 6：LLM 裁判官（任意・後回し可）

目的：§5.2 の意味的監査を実装する。Phase 5 まで完了してから着手する。

- 構造化した有効プロンプトと WORKFLOW_NAVIGATION.md の該当節を入力に、LLM が gap を返す
- `run_review.py` の流用か新規スクリプトかは実装時に決定する
- 出力は構造化 JSON（§5.2 参照）

完了条件：構造化出力が schema に適合し、既知の gap を正しく検出できることをテストで確認できること。
