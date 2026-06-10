---
type: requirements_triad_review  # 計画書 §5.9.3 の type 値（種別に応じて変更：requirements_triad_review／design_triad_review／tasks_triad_review／implementation_conformance_review）
target: <抽出先パス>              # 例：.reviewcompass/specs/foundation/requirements.md
target_commit: <commit_hash>     # 抽出先ファイルが含まれるコミットの sha
target_content_hash: <sha256>    # 抽出先ファイル内容の sha256
date: <YYYY-MM-DD>
mode: manual_dogfooding          # 手動 dogfooding を明示（runtime_mediated との直交軸、§5.23.5）
session: <セッション番号>          # 例：session-19
primary:
  provider: human_manual         # 手動模倣
  model: <レビュー者名>            # 例：keno（人間レビュー者の名前）
  attempts: 1
  duration_minutes: <分>
  prompt_artifact_path: runtime/prompts/primary_detection/primary_reviewer.prompt.md
  prompt_artifact_hash: <sha256>  # プロンプト本体のハッシュ。雛形が未整備の場合は <未整備> と記入
adversarial:
  provider: human_manual
  model: <レビュー者名>            # 主役と異なる人間が望ましい、同じ場合は manual_dogfooding_caveats に明示
  duration_minutes: <分>
  prompt_artifact_path: runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md
  prompt_artifact_hash: <sha256>
judgment:
  provider: human_manual
  model: <レビュー者名>
  duration_minutes: <分>
  prompt_artifact_path: runtime/prompts/judgment/judgment_reviewer.prompt.md
  prompt_artifact_hash: <sha256>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 0, INFO: 0 }
    count: 0
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 0, INFO: 0 }
    count: 0
  judgment:
    by_severity: { CRITICAL: 0, ERROR: 0, WARN: 0, INFO: 0 }
    count: 0
    judgment_distribution: { must-fix: 0, should-fix: 0, leave-as-is: 0 }
manual_dogfooding_caveats:        # 手動模倣の限界を明示（§5.23.4）
  - <例：主役と敵対役が同じレビュー者で独立性が損なわれる可能性>
  - <例：モデル多様化規律は適用不可>
  - <例：ファイル遮断規律は適用不可>
---

# レビュー記録：<対象機能> <種別>

## 1. 主役レビュー（primary）

### 観点 1（Criterion 1）：<観点名>

#### 所見

- **finding_id**：F-001
- **severity**：<CRITICAL／ERROR／WARN／INFO>
- **target_location**：<ファイル名 §節番号／行番号／AC 番号>
- **description**：<30 文字以上、対象の何が問題かを具体的に>
- **rationale**：<100 文字以上、なぜ問題なのかの根拠>
- **evidence_type**：<fact／inference／mixed>
- **verifying_commands**：（fact または mixed の場合、最低 1 つ）
  - `<例：grep -n 'P1' foundation/requirements.md>`

#### 所見

（複数の所見がある場合は同じ構造で繰り返す）

### 観点 2（Criterion 2）：<観点名>

（同様）

### 該当なし観点の明示

- 観点 N：該当なし（理由：<簡潔に>）

---

## 2. 敵対役レビュー（adversarial）

### 主役所見への反論

- **対象 finding_id**：F-001
- **counter_status**：<counter_evidence_raised／no_counter_evidence_after_challenge／not_assessed>
- **counter_rationale**：<反証または同意の根拠>

### 独立発見（主役が指摘しなかった所見）

- **finding_id**：A-001
- **severity**：<CRITICAL／ERROR／WARN／INFO>
- **target_location**：<同上>
- **description**：<同上>
- **rationale**：<同上>
- **evidence_type**：<同上>
- **verifying_commands**：（同上）

---

## 3. 判定役レビュー（judgment）

### 各所見への判定

- **finding_id**：F-001
- **judgment**：<must-fix／should-fix／leave-as-is>
- **rationale**：<50 文字以上、採否の根拠>

---

## 4. 統合（integration）

### 採用所見一覧

| finding_id | severity | judgment | target_location | 概要 |
|---|---|---|---|---|
| F-001 | ERROR | must-fix | foundation/requirements.md §3.1 | 用語「P1」の重複定義 |

### 抽出元との対応

- 抽出元 finding（あれば）：<元仕様で対応する論点があれば、その章節を記す>
- 新規発見（抽出による）：<抽出作業中に新たに発見した論点>

### 残課題

- <次回セッションで扱う論点があれば箇条書きで>

---

**雛形の使い方**：

1. 本ファイルをコピーして `.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md` として保存
2. front-matter の `<placeholder>` を実値で埋める
3. レビューを 3 役順に実施し、所見を本文に記入
4. 統合後、`docs/extraction-mapping.md` の該当機能行の「実施履歴」欄に実施日と本ファイルへの相対リンクを追記
5. レビュー記録は雛形であり、手動 dogfooding の限界（§5.23.4）は `manual_dogfooding_caveats` に必ず明記する
