prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
triad_review

# Criteria
# Post-write Review Target

criteria_id: proxy-decision-record-naming-consistency
phase: post_write_verification
generated_at: 2026-06-24T02:55:14.507453+00:00

## Change Summary

proxy_model 判断レコードの命名・属性・意味づけが、実装コード（proxy-approval.yaml / approved_by / 承認扱い）、設計書（proxy-decision-bundle / decided_by / 承認ではないと明記）、タスク・テスト・規律（approval-proxy / 承認扱い）の間で3つ巴に食い違っている。テスト test_session_record_contract.py が design.md に approval-proxy を期待する assert がこの不整合の一症状として顕在化した。

## Review Question

proxy_model 判断レコードの正本となる命名・属性キー・意味づけ（承認か判断か）は何か。実装を正本にするか設計書の新整理に合わせるか、どの成果物が stale でどう整合させるべきか。選択肢を1つ選ぶ形に限定せず、安全観点（人間承認との混同防止）を含め開いて分析してほしい。

## Target Files

- .reviewcompass/evidence/review-runs/2026-06-24-proxy-decision-record-naming-consistency/proxy-record-consistency-brief.md sha256=9134300d32d70332b22ae0c57f2c04ecf893ea196963f8bfc048fcc1f3d2869f

## Source Materials

- none

## Target File Contents

### .reviewcompass/evidence/review-runs/2026-06-24-proxy-decision-record-naming-consistency/proxy-record-consistency-brief.md

content_mode: full_text
content_sha256: 9134300d32d70332b22ae0c57f2c04ecf893ea196963f8bfc048fcc1f3d2869f

```text
# 検討資料：proxy_model 判断レコードの命名・意味づけ不整合

## 背景

ReviewCompass では、外部 API レビューで出た所見の採否を、人間ではなく別の AI モデル
（proxy_model と呼ぶ）に委ねる運用がある。その判断結果を束ねるレコードの「ファイル名」
「属性キー」「意味づけ（承認か否か）」が、実装コード・設計書・タスク仕様・運用規律・
テストの間で食い違っている。本資料はその不整合を逐語抜粋で提示する。

各抜粋は出典（ファイル:行）を明記する。判断に必要な範囲に絞っており、機密情報は含まない。

## 不整合の要約

| 観点 | (A) 実装コード | (B) 設計書 design.md | (C) タスク/テスト/規律 |
|---|---|---|---|
| 束ねファイル名 | `proxy-approval.yaml` | `proxy-decision-bundle-<日付>.yaml` | `approval-proxy-<日付>.yaml` |
| 属性キー | `approved_by: proxy_model` | `decided_by: proxy_model` | `approved_by`（承認扱い） |
| 意味づけ | 承認レコード | **承認レコードではない**（明記） | 「実装着手を許可する proxy approval record」 |
| 実体 | 実際に書かれ検査されている | 文書のみ・未実装 | 旧称が残存 |

3 つの異なるファイル名と 2 つの異なる属性キー、そして「承認か否か」という意味づけの差が併存している。

## 逐語抜粋

### (A) 実装コード — 実際に生成・検査されている形

`tools/make-proxy-approval.py:2,15`
```
"""proxy_model 裁定レコード（proxy-approval.yaml・decisions/*.yaml）を、正本が受け入れる …
  - proxy-approval.yaml（approved_action/approved_by/review_run_id/各 presented フラグ/ …
```

`tools/make-proxy-approval.py:142,161`
```
"approved_by": "proxy_model",
```

`tools/api_providers/review_triage.py:256-257`
```
if decision.get("approved_by") != "proxy_model":
  errors.append(f"{finding_id}: decision approved_by must be proxy_model")
```

→ 実装は束ねファイルを `proxy-approval.yaml`、属性を `approved_by: proxy_model` として
生成・検査する。「approval（承認）」の枠組み。

### (B) 設計書 design.md — 文書上の新しい整理（未実装）

`.reviewcompass/specs/workflow-management/design.md:249,252`
```
  proxy-decision-bundle-<日付>.yaml
…
`proxy-decisions/<finding-id>.decision.yaml` は最低限、`finding_id`、`decided_by: proxy_model`、
… を持つ。`proxy-decision-bundle-<日付>.yaml` は対象 review-run、対象 finding、参照した
decision、summary/triage 提示済みフラグを束ねる。proxy decision bundle は承認 record ではなく、
human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize を
許可しない。
```

→ 設計書は束ねファイルを `proxy-decision-bundle-<日付>.yaml`、属性を `decided_by: proxy_model`
とし、「これは承認レコードではない」と明記する。「decision（判断）」の枠組み。ただし、この
ファイル名・属性をコードはどこにも実装していない。

### (C) タスク仕様 / テスト / 運用規律 — 旧称が残存

`.reviewcompass/specs/workflow-management/tasks.md:128`
```
7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、
`proxy-decisions/<finding-id>.decision.yaml`、… を検査し、欠落または triage との不一致が
あれば DEVIATION にする。…
```

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md:206,235`
```
4. メインセッション LLM は proxy_model の raw response を保存し、
`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
…
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record
```

`tests/tools/test_session_record_contract.py:90-93`（design.md に対する assert）
```
assert "proxy decision" in design
assert "approval-proxy-<日付>.yaml" in design
assert "candidate_options" in design
assert "source_raw_paths" in design
```

→ タスク・規律・テストは束ねファイルを `approval-proxy-<日付>.yaml` と呼び、「実装着手を
許可する proxy approval record（承認レコード）」として扱う。テストは design.md に
`approval-proxy-<日付>.yaml` が含まれることを期待するが、design.md は (B) の新称に
変わっているため、この assert は現状一致しない。

## 補足（経緯の推測・未確証）

- 歴史的 review-run 成果物では、最古（2026-06-04）が `approval-proxy-2026-06-04.yaml`、
  以降の多くが `proxy-approval.yaml`。つまり実装側の束ね名は
  `approval-proxy-<日付>.yaml` → `proxy-approval.yaml` と変遷した形跡がある。
- design.md の `proxy-decision-bundle` 表記と「承認ではない」という整理は、安全上の意図
  （proxy の判断を人間承認と混同させない）を持つように読めるが、コード・タスク・規律へは
  反映されていない。
- 上記「経緯」は推測であり、確証は git 履歴の追加確認が必要。

## 判断してほしいこと（開いた問い）

次を独立に分析してほしい。**特定の選択肢（A/B/C）から1つ選ぶ形に限定しない。** 枠を超えた
整理（第4の命名、属性とファイル名を分けて考える、現状維持が妥当、など）も歓迎する。

1. proxy_model の判断レコードは「承認（approval / approved_by）」と「承認ではない判断
   （decision / decided_by）」のどちらの意味づけが妥当か。両者の利点・リスク（特に人間承認との
   混同防止という安全観点）を含めて評価してほしい。
2. その意味づけを前提にしたとき、束ねファイル名・属性キーの正本はどうあるべきか。
3. コード・design・tasks・規律・テストのうち、どれが正本で、どれを stale として直すべきか。
   実装（コードが現に生成・検査している形）を正本にするか、設計書の新しい整理に実装を
   合わせるか、という方向性も論じてほしい。
4. 見落としや、上の要約・抜粋に含まれない確認すべき材料があれば指摘してほしい。

## 範囲

- 範囲内：proxy_model 判断レコードの命名・属性・意味づけの正本化と、各成果物の整合方針。
- 範囲外：proxy_model 運用そのものの是非、外部 API レビュー全体の設計、無関係なリファクタ。
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/evidence/review-runs/2026-06-24-proxy-decision-record-naming-consistency/proxy-record-consistency-brief.md

# Target document
# 検討資料：proxy_model 判断レコードの命名・意味づけ不整合

## 背景

ReviewCompass では、外部 API レビューで出た所見の採否を、人間ではなく別の AI モデル
（proxy_model と呼ぶ）に委ねる運用がある。その判断結果を束ねるレコードの「ファイル名」
「属性キー」「意味づけ（承認か否か）」が、実装コード・設計書・タスク仕様・運用規律・
テストの間で食い違っている。本資料はその不整合を逐語抜粋で提示する。

各抜粋は出典（ファイル:行）を明記する。判断に必要な範囲に絞っており、機密情報は含まない。

## 不整合の要約

| 観点 | (A) 実装コード | (B) 設計書 design.md | (C) タスク/テスト/規律 |
|---|---|---|---|
| 束ねファイル名 | `proxy-approval.yaml` | `proxy-decision-bundle-<日付>.yaml` | `approval-proxy-<日付>.yaml` |
| 属性キー | `approved_by: proxy_model` | `decided_by: proxy_model` | `approved_by`（承認扱い） |
| 意味づけ | 承認レコード | **承認レコードではない**（明記） | 「実装着手を許可する proxy approval record」 |
| 実体 | 実際に書かれ検査されている | 文書のみ・未実装 | 旧称が残存 |

3 つの異なるファイル名と 2 つの異なる属性キー、そして「承認か否か」という意味づけの差が併存している。

## 逐語抜粋

### (A) 実装コード — 実際に生成・検査されている形

`tools/make-proxy-approval.py:2,15`
```
"""proxy_model 裁定レコード（proxy-approval.yaml・decisions/*.yaml）を、正本が受け入れる …
  - proxy-approval.yaml（approved_action/approved_by/review_run_id/各 presented フラグ/ …
```

`tools/make-proxy-approval.py:142,161`
```
"approved_by": "proxy_model",
```

`tools/api_providers/review_triage.py:256-257`
```
if decision.get("approved_by") != "proxy_model":
  errors.append(f"{finding_id}: decision approved_by must be proxy_model")
```

→ 実装は束ねファイルを `proxy-approval.yaml`、属性を `approved_by: proxy_model` として
生成・検査する。「approval（承認）」の枠組み。

### (B) 設計書 design.md — 文書上の新しい整理（未実装）

`.reviewcompass/specs/workflow-management/design.md:249,252`
```
  proxy-decision-bundle-<日付>.yaml
…
`proxy-decisions/<finding-id>.decision.yaml` は最低限、`finding_id`、`decided_by: proxy_model`、
… を持つ。`proxy-decision-bundle-<日付>.yaml` は対象 review-run、対象 finding、参照した
decision、summary/triage 提示済みフラグを束ねる。proxy decision bundle は承認 record ではなく、
human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize を
許可しない。
```

→ 設計書は束ねファイルを `proxy-decision-bundle-<日付>.yaml`、属性を `decided_by: proxy_model`
とし、「これは承認レコードではない」と明記する。「decision（判断）」の枠組み。ただし、この
ファイル名・属性をコードはどこにも実装していない。

### (C) タスク仕様 / テスト / 運用規律 — 旧称が残存

`.reviewcompass/specs/workflow-management/tasks.md:128`
```
7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、
`proxy-decisions/<finding-id>.decision.yaml`、… を検査し、欠落または triage との不一致が
あれば DEVIATION にする。…
```

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md:206,235`
```
4. メインセッション LLM は proxy_model の raw response を保存し、
`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
…
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record
```

`tests/tools/test_session_record_contract.py:90-93`（design.md に対する assert）
```
assert "proxy decision" in design
assert "approval-proxy-<日付>.yaml" in design
assert "candidate_options" in design
assert "source_raw_paths" in design
```

→ タスク・規律・テストは束ねファイルを `approval-proxy-<日付>.yaml` と呼び、「実装着手を
許可する proxy approval record（承認レコード）」として扱う。テストは design.md に
`approval-proxy-<日付>.yaml` が含まれることを期待するが、design.md は (B) の新称に
変わっているため、この assert は現状一致しない。

## 補足（経緯の推測・未確証）

- 歴史的 review-run 成果物では、最古（2026-06-04）が `approval-proxy-2026-06-04.yaml`、
  以降の多くが `proxy-approval.yaml`。つまり実装側の束ね名は
  `approval-proxy-<日付>.yaml` → `proxy-approval.yaml` と変遷した形跡がある。
- design.md の `proxy-decision-bundle` 表記と「承認ではない」という整理は、安全上の意図
  （proxy の判断を人間承認と混同させない）を持つように読めるが、コード・タスク・規律へは
  反映されていない。
- 上記「経緯」は推測であり、確証は git 履歴の追加確認が必要。

## 判断してほしいこと（開いた問い）

次を独立に分析してほしい。**特定の選択肢（A/B/C）から1つ選ぶ形に限定しない。** 枠を超えた
整理（第4の命名、属性とファイル名を分けて考える、現状維持が妥当、など）も歓迎する。

1. proxy_model の判断レコードは「承認（approval / approved_by）」と「承認ではない判断
   （decision / decided_by）」のどちらの意味づけが妥当か。両者の利点・リスク（特に人間承認との
   混同防止という安全観点）を含めて評価してほしい。
2. その意味づけを前提にしたとき、束ねファイル名・属性キーの正本はどうあるべきか。
3. コード・design・tasks・規律・テストのうち、どれが正本で、どれを stale として直すべきか。
   実装（コードが現に生成・検査している形）を正本にするか、設計書の新しい整理に実装を
   合わせるか、という方向性も論じてほしい。
4. 見落としや、上の要約・抜粋に含まれない確認すべき材料があれば指摘してほしい。

## 範囲

- 範囲内：proxy_model 判断レコードの命名・属性・意味づけの正本化と、各成果物の整合方針。
- 範囲外：proxy_model 運用そのものの是非、外部 API レビュー全体の設計、無関係なリファクタ。

