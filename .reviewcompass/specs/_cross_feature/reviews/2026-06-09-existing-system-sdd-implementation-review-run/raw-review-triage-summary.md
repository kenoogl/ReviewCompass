# implementation triad-review 利用者提示要約

## 実行結果

- variant: `implementation_review_independent_3way`
- primary: `anthropic-api / claude-sonnet-4-6`
- adversarial: `openai-api / gpt-5.4`
- judgment: `gemini-api / gemini-3.1-pro-preview`
- parse status: 全 3 モデル parsed
- findings: 12 件
- severity: WARN 5 件、INFO 7 件
- CRITICAL / ERROR: 0 件

## 同根まとめ

### C1: workflow-management の「既存実装で受ける」証跡が薄い

該当:

- primary-001
- primary-002
- adversarial-001
- judgment-002

内容:

workflow-management について「新規コード不要」と判断しているが、Requirement 9 / XDI-WM-002 の各要素が既存コード・既存テストのどこで満たされているかの対応表が review-target 内では薄い、という指摘。

判断案:

- `should-fix`

理由:

コードの不備というより、実装レビューの証跡不足。`tools/check-workflow-action.py` の該当関数、`tests/tools/test_check_workflow_action.py` の coverage、`downstream_impact_decisions` 完了時検査を明示すれば解消できる。

### C2: PostHocIntentDiff の出力契約がもう少し明示できる

該当:

- primary-003
- adversarial-002
- judgment-001

内容:

`needs_human_decision` の意味、classification と downstream handoff の関係、schema による出力検査が review-target 上で十分に説明されていない。特に tasks phase 候補を dedicated classification にするか、既存の `downstream_impact_candidate` で tasks phase を表す設計を明示する必要がある。

判断案:

- `should-fix`

理由:

T-016 の契約境界に関わる。実装自体は最低フィールドと分類値域を持つが、下流 workflow-management がどう読むかの説明とテスト名の明示を補うと安全。

### C3: indirect feature 5 件の no-change 証跡が薄い

該当:

- primary-005
- adversarial-003
- judgment-003

内容:

foundation / runtime / evaluation / analysis / self-improvement について、implementation 変更なしの判断はあるが、各 feature を確認した証跡が review-target だけでは薄い、という指摘。

判断案:

- `should-fix`

理由:

全 7 feature 対象の review としては、間接 feature の no-change 理由を 1 つの表にまとめ、過去の requirements/design/tasks review-wave 証跡と implementation drafting 証跡を結び直すのがよい。

### C4: 新規 T-016 テストの内訳が分かりにくい

該当:

- primary-004

内容:

テスト総数は示されているが、どのテストが今回追加された T-016 用なのか分かりにくい、という指摘。

判断案:

- `leave-as-is` または C2 と合わせて `should-fix`

理由:

単独では情報提示レベル。ただし C2 の補足で T-016 テスト名を review-target / implementation-drafting に明示すれば同時に解消できる。

### C5: CE trial run と reopen state の接続が不明瞭

該当:

- primary-006

内容:

PostHocIntentDiff の試行記録は作られているが、それが `downstream_impact_decisions` に直接書き戻されるわけではない。そのため、reopen 完了条件との関係が review-target では分かりにくい、という指摘。

判断案:

- `should-fix`

理由:

T-016 は候補抽出、WM は reopen 記録という責務分担なので、直接書き戻さないこと自体は妥当。ただし「CE は候補を出すだけ」「WM が gate ごとに downstream_impact_decisions に判断を記録する」という境界を明記した方がよい。

## 推奨判断

CRITICAL / ERROR はないが、WARN が 5 件あり、同根は証跡不足と契約説明不足に集約される。

推奨は次の通り。

1. C1, C2, C3, C5 を `should-fix` として反映する
2. C4 は C2 の反映に含める
3. 実装コードの大きな作り直しではなく、実装ドラフティング証跡、review-target、必要なら小さな出力契約テストを補強する

## 利用者判断待ち

この要約をもとに、implementation triad-review の指摘を上記の判断案で反映してよいか承認が必要。

## 承認後の反映

利用者発言「承認」に基づき、12 件すべてを `should-fix` として triage 済みにした。

反映内容：

- C1: workflow-management の既存実装対応表を `.reviewcompass/specs/workflow-management/implementation-drafting.md` と review-target に追記した
- C2: PostHocIntentDiff の classification、`phase: tasks`、`needs_human_decision`、CE→WM handoff の意味を `.reviewcompass/specs/conformance-evaluation/implementation-drafting.md` と review-target に追記した
- C2: schema とコード定数の同期を検査する `test_t016_post_hoc_intent_diff_schema_tracks_classification_contract` を追加した
- C3: indirect feature 5 件の implementation no-change 判断表を cross-feature drafting と review-target に追記した
- C4: T-016 追加テストの内訳を implementation-drafting と review-target に明記した
- C5: CE は候補抽出に留まり、WM が `downstream_impact_decisions` に gate 判断を記録する責務分担を明記した
