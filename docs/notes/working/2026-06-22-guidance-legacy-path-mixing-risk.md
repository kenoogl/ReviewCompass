# Guidance Legacy Path Mixing Risk

作成日: 2026-06-22

## 背景

post-write prompt 機械化作業中に、`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` と `docs/operations/WORKFLOW_NAVIGATION.md` の両方を更新しかけた。

利用者確認により、現在の実行時・配布時に読むべき正本は `.reviewcompass/guidance/` 側であり、旧 `docs/operations/` / `docs/disciplines/` 側を同時更新対象として扱うことは誤りだと確認した。

## 確認した問題

- `.reviewcompass/guidance` と旧 `docs/operations` / `docs/disciplines` に同名 guidance / discipline ファイルが重複して残っている。
- 旧パス参照が `AGENTS.md`、`TODO_NEXT_SESSION.md`、`docs/operations/DEPLOYMENT.md`、`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`、一部テスト、テンプレートに残っている。
- `tests/workflow-management/test_guidance_file_relocation_contract.py` はこの問題を検出する意図のテストだが、現状で失敗する。
- その結果、作業者が旧ファイルを正本または同期対象と誤認し、今回のように不要な正本文書変更を混ぜる危険がある。

## リスク

- API review 用 prompt や effective prompt の参照元を誤る。
- post-write verification 対象と tool/test 変更が混在し、`post_write_policy_violation` を誘発する。
- 配布 manifest と実際の参照先がずれ、外部適用時に古い規律を読む。
- 文書更新・実装更新・検証更新が同一コミットに混線し、後から原因追跡しにくくなる。

## 後続作業候補

現作業を完了・コミットした後、別作業として次を判断する。

1. 旧 `docs/operations` / `docs/disciplines` guidance 残骸を削除するか。
2. 旧パス参照を `.reviewcompass/guidance` へ統一するか。
3. テスト fixture の旧パス利用を、歴史的 fixture と現行契約 fixture に分離するか。
4. `test_guidance_file_relocation_contract.py` を通すことを完了条件にするか。
5. 今後、guidance 変更時に旧パスが存在すれば fail-closed する機械ガードを追加するか。

## 現時点の扱い

この問題は重要だが、今すぐ整理すると現行の post-write prompt 機械化実装コミットと混線する。そのため、本メモに記録し、現作業の終了後に別作業として判断する。
