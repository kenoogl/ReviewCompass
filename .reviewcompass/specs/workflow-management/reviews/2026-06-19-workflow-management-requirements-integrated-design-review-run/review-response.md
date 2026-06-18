# Requirements Triad Review 反映記録

作成日: 2026-06-19

## 対象

この記録は、proxy_model triage decision で採用した所見を `.reviewcompass/specs/workflow-management/requirements.md` へどのように反映したかを示す。

対象 review run:

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/`

判断元:

- `proxy-decision-summary.md`
- `proxy-approval.yaml`
- `triage.yaml`

## 反映した所見

### C1: 19 `required_action` と複合 operation の要件粒度

最終ラベル: `must-fix`

反映内容:

- Requirement 13 に、19語彙の operation contract 対応表が最低限 `required_action`、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、実行主体、分岐条件の有無、参照する preconditions / postconditions を持つことを追加した。
- 複合操作または条件分岐を持つ操作は、未確定 placeholder や代表値だけで表さず、分岐条件と最大副作用を requirements レベルで明示することを追加した。

### C2: side-track stack と commit mixing 防止の不変条件

最終ラベル: `must-fix`

反映内容:

- Requirement 14 に、`staged_file_set` と `staged_file_digest` を side-track push 時点、pop 直前、commit / push 直前に採取・照合できることを追加した。
- `allowed_files` 外の staged 変更、予期しない digest 変化、親子 frame 間で明示許可されていない staged file set の重なり、pop 時の digest / set 不一致を、Phase 3 では WARN 以上、Phase 5 では `DEVIATION` または `repair_workflow_state` として扱うことを追加した。
- git index が本線復帰条件を満たさない場合、または side track 内の commit / push 後の index 変化を説明する記録がない場合、通常作業へ戻してはならないことを追加した。

### C3: 承認ゲートと `record_human_decision`

最終ラベル: `should-fix`

反映内容:

- Requirement 13 に、`record_human_decision` は判断記録を書き込む場合でも `approval_required: false` であり、完了だけでは対象 operation の承認充足にならないことを追加した。
- Requirement 14 に、承認、拒否、保留、修正要求の各判断が、対象 operation ID、対象 `required_action`、対象 artifact または staged file set digest、判断者、判断時刻、出典を持つことを追加した。
- 承認以外の判断が記録されている場合、不可逆操作を許可してはならないことを追加した。

### C4: structured effective prompt の第1層機械検査

最終ラベル: `should-fix`

反映内容:

- Requirement 15 に、`language_task.output_format` と `postconditions` の対応検査を追加した。
- `preconditions_checked` は機械確認済み条件だけを参照することを追加した。
- `on_completion` が operation contract の postconditions または次 action と矛盾しないことを検査対象に追加した。

### C5: cross-feature impact と review-wave への持ち上げ

最終ラベル: `should-fix`

反映内容:

- Requirement 16 に、workflow-management の reopen scope と consumer / derivative としての impact review scope を review-wave で区別することを追加した。
- foundation、runtime、evaluation、analysis、self-improvement、conformance-evaluation などへの正本変更要否と consumer 契約影響を確認することを追加した。

### C6: D-003 / Phase 0 の canonical anchor

最終ラベル: `should-fix`

反映内容:

- Requirement 16 で、現在の D-003 stable anchor を `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` として維持した。
- 正本昇格または移動が起きた場合は、新しい stable canonical anchor を requirements または design で明示する必要があることを維持・明確化した。

### C7: `spec.json.reopened` と現在 R-0 scope の意味づけ

最終ラベル: `should-fix`

反映内容:

- Requirement 16 に、`spec.json.reopened` は履歴フラグとして保持され得るため、現在の active reopen scope と同一視しないことを追加した。
- 現在の scope、impact review scope、direct / indirect feature、flag policy を in-progress reopen record、classification record、`spec.json.recheck`、後続の review-wave / alignment 証跡で区別して記録することを追加した。

## 反映しなかった所見

C8 と C9 は `leave-as-is` と判断済みである。

これらのクラスタだけを理由にした requirements 変更は行っていない。

## 残作業

- 更新した requirements と関連記録に対して post-write verification を実施する。
- 未解決の本質的指摘がなければ、requirements triad-review gate の完了を記録する。
