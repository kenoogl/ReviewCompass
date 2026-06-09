# implementation triad-review r2 利用者提示要約

## 実行結果

- variant: `implementation_review_independent_3way`
- primary: `anthropic-api / claude-sonnet-4-6`
- adversarial: `openai-api / gpt-5.4`
- judgment: `gemini-api / gemini-3.1-pro-preview`
- parse status: 全 3 モデル parsed
- findings: 8 件
- severity: WARN 3 件、INFO 5 件
- CRITICAL / ERROR: 0 件
- Gemini: no findings

## 前回からの変化

前回の同根指摘はかなり薄まった。特に、WM 対応表、T-016 出力契約、間接 feature no-change 表は評価対象に入った。

残った指摘は、主に「さらに証跡を細かく出せる」という内容で、コードの大きな欠陥ではない。

## 同根まとめ

### R2-C1: schema とコード定数の一致を review-target 内にも明示してほしい

該当:

- primary-001

内容:

テストでは schema と `ALLOWED_CLASSIFICATIONS` の一致を検査しているが、review-target 本文に実際の enum 一覧と一致確認結果が直接書かれていない、という指摘。

判断案:

- `leave-as-is`

理由:

これは review-target の読みやすさの要求であり、機械検査としては `test_t016_post_hoc_intent_diff_schema_tracks_classification_contract` で確認済み。追加修正してもよいが、必須ではない。

### R2-C2: workflow-management の既存実装がいつから存在したかの provenance が薄い

該当:

- primary-002
- adversarial-002

内容:

WM の該当関数が「今回の reopen より前からあった」ことを、commit や変更履歴として示してほしい、という指摘。

判断案:

- `leave-as-is`

理由:

今回の implementation review の主目的は、現在のコードが要件を満たしているかの確認である。既存実装の成立時点まで追うなら git 履歴監査になるが、今回の gate 完了条件ではない。

### R2-C3: `needs_human_decision=false` でも CE が reopen YAML へ書き戻さないことをもっと直接テストしてほしい

該当:

- primary-003

内容:

既存テストは tasks.md 非破壊を確認しているが、reopen YAML へ書き戻さないことまで明示したテスト名ではない、という指摘。

判断案:

- `should-fix`

理由:

小さなテスト追加で契約を機械的に固定できる。CE は候補抽出、WM は reopen state 更新、という責務分担をより強くできる。

### R2-C4: analysis の将来取り込みが忘れられないか

該当:

- primary-004

内容:

「T-016 output is not yet a reportable analysis intake artifact」という表現が、将来の分析取込候補を示しているなら追跡が必要ではないか、という指摘。

判断案:

- `leave-as-is`

理由:

今回の reopen chain では analysis への実装影響なしと判断済み。将来 T-016 出力を analysis 成果物にする intent / requirement が出た時点で reopen するのが筋で、今ここで analysis task を増やすと範囲外になる。

### R2-C5: reopen YAML の実際の該当フィールド抜粋が review-target にない

該当:

- primary-005

内容:

`drafting_completed_gates` や `downstream_impact_decisions` の実際の YAML 内容を抜粋してほしい、という指摘。

判断案:

- `leave-as-is`

理由:

review-target は該当ファイルを evidence として列挙しており、機械判定も `next --json` で確認している。抜粋追加は読みやすさの補足であり、必須ではない。

### R2-C6: cross-feature implementation drafting の結論を review-target にもう少し要約してほしい

該当:

- primary-006

内容:

cross-feature implementation drafting の結論そのものを review-target に短く書くとよい、という指摘。

判断案:

- `leave-as-is`

理由:

review-target には direct / indirect scope、実装変更、no-change 表をすでに含めている。追加してもよいが、必須ではない。

### R2-C7: named regression test を Tests Run に直接出してほしい

該当:

- adversarial-001

内容:

`test_next_reopen_requires_drafting_before_triad_review` は証跡表にあるが、Tests Run ではモジュール全体実行として書かれている。特定テストを実行したことも直接書くとよい、という指摘。

判断案:

- `should-fix`

理由:

小さなテスト実行と記録だけで解消できる。WM 側の中核証跡なので明示する価値がある。

## 推奨判断

推奨は次の通り。

1. R2-C3 と R2-C7 を `should-fix` として反映する
2. R2-C1, R2-C2, R2-C4, R2-C5, R2-C6 は `leave-as-is`
3. 反映後、追加テストを実行し、implementation triad-review を完了扱いに進める

## 利用者判断待ち

この r2 の判断案を承認するか確認が必要。

## 承認後の反映

利用者発言「承認」に基づき、R2-C3 と R2-C7 を `should-fix`、R2-C1 / R2-C2 / R2-C4 / R2-C5 / R2-C6 を `leave-as-is` として triage 済みにした。

反映内容：

- R2-C3: `test_t016_post_hoc_intent_diff_outputs_candidates_and_record` に reopen YAML 非破壊確認を追加した
- R2-C7: `test_next_reopen_requires_drafting_before_triad_review` を単独実行し、workflow-management implementation drafting と review-target に記録した

検証：

- `.venv/bin/python3 -m pytest tests/conformance-evaluation/test_conformance_evaluation.py -q`：pass
- `.venv/bin/python3 -m unittest tests.tools.test_check_workflow_action.NextNavigationTests.test_next_reopen_requires_drafting_before_triad_review -v`：pass
