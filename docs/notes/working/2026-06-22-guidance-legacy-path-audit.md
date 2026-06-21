# Guidance Legacy Path Audit

作成日: 2026-06-22

## 目的

旧 `docs/operations` / `docs/disciplines` 配置と、現行 `.reviewcompass/guidance` 配置が混在している問題について、削除や参照更新へ進む前に監査した結果を記録する。

本メモは監査記録であり、配置変更や参照更新は行わない。

## 結論

`.reviewcompass/guidance` を現行正本とする契約は、配布 manifest、実行コード、現行テストの多くでは成立している。一方で、旧配置ファイル本体と旧パス参照が多数残っており、作業者が旧ファイルを正本または同期対象と誤認する危険が高い。

旧配置整理は、単純削除ではなく、次の順序で行うべきである。

1. `.reviewcompass/guidance` を正本として採用することを再確認する。
2. 旧配置との差分がパス置換だけかを確認する。
3. 現行手順面の旧パス参照を `.reviewcompass/guidance` へ更新する。
4. 履歴メモや review-run 証跡の旧パスは、履歴として残すものと現在手順へ影響するものを分ける。
5. 旧 guidance / discipline ファイルを削除し、`tests/workflow-management/test_guidance_file_relocation_contract.py` を通す。

## 重複ファイル監査

### `docs/operations` と `.reviewcompass/guidance`

内容一致:

- `WORKFLOW_PRECHECK_DETAILS.md`
- `REOPEN_PROCEDURE.md`
- `COMMIT_OPERATION_CARD.md`
- `INITIAL_SETUP_LLM_GUIDE.md`

内容不一致:

- `WORKFLOW_DISCIPLINE_MAP.yaml`
- `WORKFLOW_NAVIGATION.md`
- `WORKFLOW_PRECHECK.md`
- `SESSION_WORKFLOW_GUIDE.md`
- `API_REVIEW_PROMPT_QUALITY.md`

不一致の性質:

- 確認した差分は、主に旧 `docs/operations` / `docs/disciplines` パスと新 `.reviewcompass/guidance` パスの違いである。
- `WORKFLOW_DISCIPLINE_MAP.yaml` は大量の参照パス差分を含む。現行実行コードは `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` を読むため、旧 map は削除候補である。
- `SESSION_WORKFLOW_GUIDE.md` には相対リンク差分もある。削除前に、`.reviewcompass/guidance` 側のリンクが実際に解決できるかを別途確認する必要がある。

### `docs/disciplines` と `.reviewcompass/guidance`

内容一致:

- `discipline_approval_operation.md`
- `discipline_llm_as_judge_prompting.md`
- `discipline_post_write_verification.md`
- `discipline_workflow_state_truth_source.md`

内容不一致:

- `discipline_yaml_audit.md`

不一致の性質:

- `discipline_yaml_audit.md` の差分は、再オープン手続き参照先が旧 `docs/operations/REOPEN_PROCEDURE.md` か新 `.reviewcompass/guidance/REOPEN_PROCEDURE.md` かの違いである。

## 現行面の旧パス参照

旧 guidance パスを現在手順として読ませる危険がある代表例:

- `AGENTS.md`
- `TODO_NEXT_SESSION.md`
- `docs/operations/DEPLOYMENT.md`
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- `docs/disciplines/discipline_must_fix_discussion_obligation.md`
- `docs/disciplines/discipline_workflow_precheck_invocation.md`
- `docs/disciplines/discipline_yaml_audit.md`
- `templates/todo/TODO_NEXT_SESSION.template.md`
- 一部の `tests/*`

特に `AGENTS.md` と `TODO_NEXT_SESSION.md` は作業開始時に直接読まれるため、旧パス参照の優先度が高い。

## `docs/notes` 側の扱い

`docs/notes` には旧パス参照が多数ある。ただし一括置換すべきではない。

履歴として残すべき可能性が高いもの:

- `docs/notes/review-runs/**`
- `docs/notes/post-write-verification-review/**`
- `docs/notes/archive/**`
- 過去日付の作業記録で、当時の配置を説明しているもの

現在手順や後続作業の判断時に再確認すべきもの:

- `docs/notes/working/2026-06-21-guidance-file-move-active-reference-inventory.md`
- `docs/notes/working/2026-06-21-guidance-file-move-redo-plan.md`
- `docs/notes/working/2026-06-21-effective-prompt-freshness-audit-plan.md`
- `docs/notes/working/2026-06-21-workflow-operation-mechanization-improvement-plan.md`
- `docs/notes/working/2026-06-22-guidance-legacy-path-mixing-risk.md`

これらは、旧配置問題を判断する材料として読むべきである。作業中メモ自体を安易に書き換えるのではなく、記載内容が現在手順として使われていないかを確認する。履歴証跡や raw review-run 内の旧パスは、証跡改変になるため原則として触らない。

## テスト結果

`tests/workflow-management/test_guidance_file_relocation_contract.py` は現状で失敗する。

結果:

- `15 failed, 2 passed`

失敗理由:

- 旧 `docs/operations` / `docs/disciplines` 配置に guidance / discipline ファイル本体が残っている。
- active surface に旧パス参照が残っている。

このテストは、旧配置整理作業の完了条件として有効である。

## 後続作業案

旧 guidance 整理は、post-write prompt 機械化や通常実装と混ぜず、独立作業として行う。

推奨順序:

1. 旧配置整理専用の作業単位を作る。
2. `AGENTS.md`、`TODO_NEXT_SESSION.md`、`docs/operations/DEPLOYMENT.md`、テンプレート、active docs の旧パスを更新する。
3. tests / fixtures の旧パス利用を、現行契約テストと歴史的 fixture に分類する。
4. 内容一致または新パス差分のみと確認した旧 guidance / discipline ファイルを削除する。
5. `test_guidance_file_relocation_contract.py` と deploy 関連テストを通す。
6. その後に `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` へ `post_write_review_flow.py` の標準手順を反映する。

## 現時点の停止判断

本監査では削除・参照更新へ進まない。現作業は監査結果の保存までとし、次に旧配置整理を実施するかを利用者判断に戻す。
