# Raw Review Triage Summary: existing-system SDD requirements

対象: `requirements.triad-review`

review-run: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-review-run`

## Role Assignments

| role | provider | model | parse |
| --- | --- | --- | --- |
| primary | anthropic-api | claude-sonnet-4-6 | parse_failed |
| adversarial | openai-api | gpt-5.4 | parsed |
| judgment | gemini-api | gemini-3.1-pro-preview | parsed |

`primary` は parser 失敗だが、raw response は保存済みで、人間可読な所見を含む。

## Same-Root Clusters

### Cluster A: conformance-evaluation Requirement 10 の tasks 取り扱いが既存スコープと衝突する

提案ラベル: must-fix

関係所見:

- `gpt-5.4` ERROR: CE Requirement 10 AC-2 が `tasks` と `実装上の作業契約候補` を抽出対象に含めるが、既存 CE scope との整合が未説明。
- `gemini-3.1-pro-preview` ERROR: CE 既存スコープは requirements/design 中心で tasks は対象外なのに、CE Requirement 10 が tasks を明示している。
- `claude-sonnet-4-6` raw WARN: 同じく tasks を scope extension として明示する必要を指摘。

平易な説明:

今回の追加要件では、コードから requirements/design だけでなく tasks や実装上の作業契約も拾う、と書いている。一方、既存の conformance-evaluation は tasks を対象外としてきた。ここを説明せずに進むと、後続の design/tasks で「CE がどこまで担当するのか」がぶれる。

推奨対応:

- Requirement 10 で、tasks は既存の tasks.md 本文を直接推定・再作成する対象ではなく、実装上の作業契約候補や下流影響候補として抽出する、という位置づけを明記する。
- 既存スコープを本格拡張するなら、その旨を Requirement 1/2/3 側にも反映する。

### Cluster B: CE の分類と出力形式がまだ設計・テスト可能な粒度まで定まっていない

提案ラベル: should-fix

関係所見:

- `gpt-5.4` WARN: AC-3 の分類 5 種と AC-6 の出力 4 種の関係が未定義。
- `gpt-5.4` WARN: LLM 推定理由の証跡要件が弱い。
- `claude-sonnet-4-6` raw WARN: artifact structure と handoff contract が未定義。

平易な説明:

候補に付けるラベルと、最終的に出す成果物の形がまだ少しふわっとしている。後続でテストを書くには、候補ごとに何を必ず持つのかをもう少し決めた方がよい。

推奨対応:

- 候補ごとに `classification`、`evidence`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` を持つ、など最低限の構造を requirements で軽く示す。
- 詳細 schema は design 段で確定すると明記する。

### Cluster C: workflow-management Requirement 9 の停止点が曖昧

提案ラベル: should-fix

関係所見:

- `gpt-5.4` WARN: conflict candidate 発見時の「人間承認または所定レビュー」がどの gate か不明。
- `gemini-3.1-pro-preview` WARN: state machine 上の表現が不明。
- `claude-sonnet-4-6` raw WARN: `existing_sufficient` 判定の権限と証跡条件が弱い。

平易な説明:

衝突候補を見つけたときに、どこで止まり、誰が何を承認すれば次へ進めるのかが曖昧。ここが曖昧だと、また LLM 判断で進めてしまう穴になる。

推奨対応:

- 衝突候補が出た場合は、該当 phase の approval または reopen record の `current_blocker` に human approval を設定して停止する、といった機械状態を requirements に含める。
- `existing_sufficient` でも、対象 gate、理由、証跡、判定者を `downstream_impact_decisions` に残すことを明記する。

### Cluster D: reopen pending gates は適切

提案ラベル: leave-as-is

関係所見:

- `gpt-5.4` INFO: material requirements change なので requirements triad-review → review-wave → alignment → approval は適切。
- `claude-sonnet-4-6` raw INFO: gate sequence は現手続きと整合。

平易な説明:

今回、requirements 本文を実質的に修正したので、alignment へ飛ばず triad-review からやり直す判断は正しい。

## Prompt Issue

`gpt-5.4` は review-target 自体の出力指示に小さな矛盾があると指摘した。`verifying_commands` を要求している一方で、「at least」の列挙が一部の欄だけに見えたためである。実際の target 末尾は `at least` として `verifying_commands` も含めており、レビュー結果そのものの blocker ではない。

提案ラベル: leave-as-is

## Proposed Triage

| cluster | proposal | reason |
| --- | --- | --- |
| A | must-fix | CE の責務境界が矛盾したままだと design/tasks へ進めない |
| B | should-fix | 後続の設計・テスト安定性に影響する |
| C | should-fix | workflow の停止点が曖昧だと同じ逸脱が再発する |
| D | leave-as-is | gate sequence は適切 |
| Prompt Issue | leave-as-is | review-target の表現問題であり requirements 本体の blocker ではない |

## Stop Point

この summary は利用者提示ゲート用の草案である。proxy_model 判断、requirements 本文修正、spec.json 更新、phase 移行には進まない。
