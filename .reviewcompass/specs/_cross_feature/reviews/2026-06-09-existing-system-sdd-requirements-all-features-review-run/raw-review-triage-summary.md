# Raw Review Triage Summary: existing-system SDD requirements, all features

対象: `requirements.triad-review`

review-run: `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-all-features-review-run`

## Role Assignments

| role | provider | model | parse |
| --- | --- | --- | --- |
| primary | anthropic-api | claude-sonnet-4-6 | parsed |
| adversarial | openai-api | gpt-5.4 | parsed |
| judgment | gemini-api | gemini-3.1-pro-preview | parsed |

全 7 feature を対象にした review-run。先行の 2 feature 限定 review-run は不足として扱い、本 review-run が requirements triad-review の正規候補である。

## Same-Root Clusters

### Cluster A: conformance-evaluation Requirement 10 の tasks 取り扱いが既存スコープと衝突する

提案ラベル: must-fix

関係所見:

- `claude-sonnet-4-6` ERROR: CE Requirement 10 AC2 が `tasks または実装上の作業契約候補` を抽出対象に含めるが、既存 CE scope は tasks を対象外としている。
- `gpt-5.4` ERROR: task-level artifacts の抽出は、requirements/design 候補抽出を超え、下流計画責務と重なる。
- `gemini-3.1-pro-preview` ERROR: tasks を CE に扱わせるなら feature-partitioning の再オープンが必要。そうでなければ Requirement 10 を requirements/design 中心へ戻すべき。

平易な説明:

今回の追加要件は「コードから仕様差分を拾う」ために、tasks や実装上の作業契約まで CE が扱うように読める。一方、既存の CE は requirements/design を中心に扱い、tasks は対象外としてきた。ここを曖昧にしたまま設計へ進むと、CE がどこまで責任を持つかがぶれる。

推奨対応:

- CE Requirement 10 では、tasks.md 本体の推定・再作成はしない、と明記する。
- CE が扱うのは、コード由来の「下流影響候補」「実装変更候補」「作業契約候補の証拠」であり、正式な tasks 更新は WM の reopen 手続きで行う、と分離する。
- もし CE に tasks 推定そのものを持たせるなら、feature-partitioning を再オープンして責務境界を再判定する。

### Cluster B: CE の分類・出力・証跡構造がまだ設計可能な粒度まで定まっていない

提案ラベル: should-fix

関係所見:

- `claude-sonnet-4-6` ERROR: 分類 5 種と出力構造の境界条件、必須フィールド、schema 参照が不足。
- `gpt-5.4` WARN: 分類が排他的か、feature 単位か phase 単位か、WM がどう消費するか不明。
- `gemini-3.1-pro-preview` WARN: foundation の構造化証拠語彙との対応が不足。

平易な説明:

候補をどう分類し、どんな形で出すかがまだゆるい。設計段で詳細化してもよいが、requirements 段でも「最低限どの情報を持つか」は決めた方がよい。

推奨対応:

- 各候補に `feature`, `phase`, `classification`, `code_refs`, `existing_spec_refs`, `reasoning_summary`, `needs_human_decision` を持たせる方針を requirements に追記する。
- 詳細 schema は design 段で確定する、と書く。
- foundation の証拠・メタデータ契約を参照し、再定義しないことを明記する。

### Cluster C: workflow-management Requirement 9 の停止点と handoff が曖昧

提案ラベル: should-fix

関係所見:

- `claude-sonnet-4-6` ERROR: conflict stop condition の gate artifact、approver、override 条件が未定義。
- `gpt-5.4` WARN: 衝突候補が出た場合、どの review/gate が必須か、全衝突候補が進行を止めるかが不明。
- `gemini-3.1-pro-preview` WARN: `side track` / `maintenance 進行中ファイル` / stop condition が foundation schema に接続されていない。
- `claude-sonnet-4-6` WARN: CE output を WM が受け取る interface contract が未定義。

平易な説明:

衝突候補が出たときに、どの状態ファイルに何を書いて、誰が承認すれば再開できるかがまだ曖昧。ここが曖昧だと、また LLM 判断で進めてしまう危険がある。

推奨対応:

- 衝突候補が出た場合は、reopen record の `current_blocker` に human approval 待ちを設定する、または該当 phase の approval gate で止める、といった機械状態を明記する。
- `downstream_impact_decisions` に、判定対象 gate、feature_scope、decision、rationale、evidence、decision_actor を残すことを明記する。
- CE から WM への handoff artifact 名を仮でも決める。

### Cluster D: indirect features は requirements 本文変更なしでよい可能性が高いが、確認記録は必要

提案ラベル: should-fix

関係所見:

- `claude-sonnet-4-6` WARN: foundation/runtime/evaluation/analysis は indirect_check_only の確認記録が不足。
- `gpt-5.4` INFO: direct/indirect split は plausibly justified。indirect features の requirements 本文変更は現時点で必須ではない。
- `gemini-3.1-pro-preview` INFO: foundation/runtime/evaluation/analysis/self-improvement の indirect_check_only 判断は妥当。

平易な説明:

他 5 feature は、今回の主責務を持つわけではないので requirements 本文を直さなくてもよさそう。ただし「見たうえで既存で足りる」と記録しないと、確認したことにならない。

推奨対応:

- review-wave または alignment で、各 indirect feature について `existing_sufficient` / `no_impact` の判定、理由、証跡を `downstream_impact_decisions` に記録する。
- requirements triad-review の段階では、本文変更なしの暫定判断として扱う。

### Cluster E: reopen gate sequence は適切

提案ラベル: leave-as-is

関係所見:

- `gpt-5.4` INFO: material requirements changes なので requirements triad-review → review-wave → alignment → approval は適切。
- `claude-sonnet-4-6` INFO: trace entries は requirements 段として適切。

平易な説明:

今回 requirements 本文を実質修正したので、triad-review からやり直す判断は正しい。全 feature 対象に直したことも妥当。

## Proposed Triage

| cluster | proposal | reason |
| --- | --- | --- |
| A | must-fix | CE の責務境界が矛盾したままだと requirements triad-review を完了できない |
| B | should-fix | 設計・テストの安定性に必要 |
| C | should-fix | workflow 停止点の曖昧さは再逸脱につながる |
| D | should-fix | 本文変更は不要でも確認記録が必要 |
| E | leave-as-is | gate sequence と全 feature scope は適切 |

## Stop Point

この summary は利用者提示ゲート用の草案である。proxy_model 判断、requirements 本文修正、spec.json 更新、phase 移行には進まない。
