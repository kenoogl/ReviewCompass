# Guidance Legacy Cleanup Repair Plan

作成日: 2026-06-22

## 目的

旧 `docs/operations` / `docs/disciplines` に残っていた guidance 正本の残骸整理後、`next --json` が `post_write_policy_violation` を返したため、現状態を通常の post-write 検証として扱わず、修復作業として扱う方針を記録する。

## 現状態

`next --json` の判定:

- verdict: `DEVIATION`
- next action: `post_write_policy_violation`
- 理由: post-write-verification pending 中に、現在の post-write target 以外の禁止ファイルが変更されている

この状態では、次を実行しない。

- API review-run
- post-write manifest 作成
- commit
- push

## なぜ旧 guidance 整理が必要だったか

`.reviewcompass/guidance` が現行正本である一方、旧 `docs/operations` / `docs/disciplines` に同役割のファイルが残っていた。

二重配置のままだと、作業者が旧ファイルを正本と誤認し、次の問題を起こしやすい。

- 正本と旧ファイルのどちらを読むべきか迷う
- 片方だけを修正して差分が再発する
- active reference の旧パス混入を検出しにくい
- effective prompt / deploy manifest / navigation の参照先が混線する

そのため、旧配置ファイルを残すよりも、正本を `.reviewcompass/guidance` に一本化する方が安全である。

## なぜ tool / test 変更が必要になったか

旧ファイルを削除すると、現役のコード・テスト・fixture が旧パスを正常例として扱っていた箇所が壊れる。

今回の `tools` / `tests` 変更は、機能追加ではなく、正本移設後の参照先を新配置へ合わせるための追従である。

主な追従:

- `tools/check-workflow-action.py` の fallback discipline map を `.reviewcompass/guidance` へ変更
- conformance ownership の source kind 判定で `.reviewcompass/guidance` を `operations` として扱う
- prompt / manifest / post-write flow のテスト入力を新正本パスへ変更
- deploy / relocation contract に沿うよう fixtures を更新

## 今回の変更範囲

削除:

- `docs/operations` 配下の移設済み guidance 正本 9 ファイル
- `docs/disciplines` 配下の移設済み discipline 正本 5 ファイル

更新:

- 入口・運用文書の旧パス参照
- active fixture / tests の旧パス参照
- guidance 正本を読むコードの fallback / 分類
- pending self-improvement proposal 内の移設済み discipline 参照

履歴メモ、過去 review-run、過去 stage 記録は原則として書き換えない。

## 検証済み内容

実行済み:

- `tests/workflow-management/test_guidance_file_relocation_contract.py`
- `tests/deployment/test_deploy_manifest.py`
- `tests/tools/test_commit_single_turn_policy_docs.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/conformance-evaluation/test_contract_ownership.py`
- `tests/tools/test_check_workflow_action.py`
- `tools/api_providers/tests/test_post_write_review_flow.py`

結果:

- `309 passed`
- `git diff --check` 問題なし
- 削除対象 14 ファイルが存在しないことを確認済み
- active surface の旧正本ファイル名参照は検出されない

## 修復方針

1. 現在の差分は、通常 post-write 検証中の追加作業ではなく、旧 guidance 二重管理を解消する修復作業として扱う。
2. `post_write_policy_violation` の間は API review-run、post-write manifest、commit、push に進まない。
3. 変更内容そのものは関連テストで妥当性を確認済みのため、安易に旧配置へ戻さない。
4. 通常 post-write に戻るには、現在の workflow policy 上で禁止扱いになっている差分をどう扱うかを利用者判断で確定する。
5. 判断後、必要なら dedicated repair / side-track 記録としてこのメモを根拠に残す。

## 戻る条件

次のいずれかを利用者判断で選ぶ。

- 案 A: 現差分を正式な修復作業として承認し、次の機械的処理へ進む
- 案 B: 禁止扱いの tool / test / discipline 変更を切り戻し、旧 guidance cleanup の範囲を縮小する
- 案 C: 旧 guidance cleanup 全体を一旦戻し、別作業単位として再実施する

推奨は案 A。理由は、旧 guidance の二重配置は実害のある混線原因であり、今回の追従変更は参照整合のために必要だったため。

## 利用者判断

2026-06-22、利用者は案 A を選択した。

決定内容:

- 現差分を、通常 post-write 検証中のついで変更ではなく、旧 guidance 二重管理を解消する正式な修復作業として扱う
- 旧 guidance cleanup 全体を戻さない
- tool / test / fixture の追従変更も、旧正本パス削除に必要な整合修正として扱う

確認済みの制約:

- `post_write_policy_violation` の間は commit / push / API review-run / post-write manifest 作成へ進まない
- 現行の `side-track-stack` は read-only の `current` のみで、A案承認を stack へ機械登録する操作はない
- operation registry には `repair_workflow_state` があるが、現行 CLI には `repair-workflow-state` サブコマンドが未実装であり、この判断を機械的に消費する経路は未整備である

従って、次の作業は「A案承認済みの修復作業を workflow にどう消費させるか」の判断である。

## 修復例外の扱い

2026-06-22、利用者は「今回だけ手動の修復例外として扱う」と判断した。

決定内容:

- 今回の旧 guidance cleanup 差分は、通常 post-write-verification pending 中の禁止変更ではなく、二重配置解消に必要な手動修復例外として扱う
- この判断は今回限りであり、今後の同種作業では `repair_workflow_state` の機械処理実装または専用 side-track / repair 記録の整備を優先する
- `next --json` の `post_write_policy_violation` は、現行実装上は残る可能性がある。これは今回の差分内容の不正ではなく、手動修復例外を機械的に消費する経路が未実装であることを示す

運用上の注意:

- commit / push へ進む場合は、このメモを根拠に、今回限りの手動修復例外として利用者が明示承認したことを commit rationale に含める
- この例外運用を常態化しない。次回以降は、`repair_workflow_state` 相当の機械処理を実装してから同種の例外消費を行う
