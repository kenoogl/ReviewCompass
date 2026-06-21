---
date: 2026-06-21
record_type: working-memo
status: completed
completed_at: 2026-06-22 00:11:25 +0900
completion_commit: 4a7d30c9
topic: postwrite-prompt-mechanization-side-track-retroactive-record
related:
  - docs/notes/working/2026-06-21-llm-boundary-and-postwrite-prompt-mechanization-plan.md
  - docs/notes/working/2026-06-21-guidance-file-move-redo-plan.md
  - docs/notes/working/2026-06-20-api-review-prompt-audit-discussion-record.md
  - docs/notes/working/2026-06-20-api-review-prompt-quality-side-track.md
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
  - .reviewcompass/guidance/discipline_post_write_verification.md
---

# Post-write Prompt 機械化 Side-track 事後認定記録

## 1. 位置付け

このメモは、guidance relocation の本線作業中に発生した補修作業を、事後的に side track として認定する記録である。

本来は side track 開始時点で記録すべきだったが、今回は API review prompt の品質欠陥と post-write 後続手順の未機械化を調査・補修してから、利用者確認により side track として扱うことを明示した。

したがって、この記録は「最初から正規 side track として開始した」という主張ではない。正確には、**事後認定 side track** である。

## 2. 本線

本線作業:

- guidance / operations / discipline 系ファイルを `.reviewcompass/guidance/` へ移す配置整理
- deploy manifest、hooks、templates、tests の参照更新
- post-write verification を通して guidance relocation 作業を安全に完了させること

本線の到達点:

- guidance relocation の初期移動と参照更新は進行中
- post-write verification に進もうとした段階で、API review prompt の品質欠陥が判明した

## 3. 分岐理由

分岐理由は次の通り。

1. `post_write_policy_violation` の地点から、API review-run へ進むべきでない状態で進みかけた。
2. `prepare_post_write_review.py` が、review target の本文ではなく path / SHA だけを prompt に含める構造だった。
3. API 送信前に prompt manifest audit / prompt quality gate が機械的に接続されていなかった。
4. その場で prompt を組み立てる余地が残っており、LLM の振れを生む状態だった。
5. invalid な review-run 結果を post-write verification 証跡として扱う危険があった。

これらは guidance relocation 自体の問題ではなく、post-write review prompt 機械化の欠陥である。そのため本線から切り分け、補修用 side track として扱う。

## 4. 既に実施したこと

この side track として、すでに次を実施した。

- LLM 処理を残す場所 / 残さない場所の境界を整理した。
- `docs/notes/working/2026-06-21-llm-boundary-and-postwrite-prompt-mechanization-plan.md` を作成した。
- Phase 0 の red test を追加した。
- red test 追加 commit を作成した。
  - commit: `248a100fd26847af1124b3f24adabc5ade888aae`
  - subject: `Add post-write prompt mechanization red tests`
- Phase 0 実装として、次の修正を未コミットで実施した。
  - `prepare_post_write_review.py` が target 本文を `## Target File Contents` に展開する。
  - metadata に `content_mode: full_text` / `content_sha256` を残す。
  - `run_review.py` が `post_write_verification` 実行前に prompt manifest を監査する。
  - `decision_point.kind != post_write_verification` の場合、API provider を起動せず停止する。
  - prompt manifest audit が `DEVIATION` の場合、API provider を起動せず停止する。

## 5. 検証済み事項

Phase 0 実装後、次を確認済み。

- `tools/api_providers/tests/test_prepare_post_write_review.py tools/api_providers/tests/test_run_review.py`: `18 passed`
- `tools/api_providers/tests`: `178 passed`
- `tests/workflow-management/test_prompt_audit.py tests/tools/test_effective_prompt_contract.py`: `13 passed`
- `tests/deployment/test_deploy_manifest.py tests/deployment/test_deploy_package_external_app_smoke.py`: `7 passed`

## 6. 終了記録

この side track は、2026-06-22 00:11:25 +0900 の commit
`4a7d30c9 Add canonical post-write policy prompt` で実質終了した。

終了時点で満たした条件:

- Phase 0 実装差分がコミット済みである。
- `post_write_policy_violation` から API review-run を開始しないことが機械的に固定されている。
- `post_write_policy_violation` 用 canonical effective prompt が固定されている。
- path / SHA だけの post-write prompt ではなく、対象本文を含む review target を生成することがテストで固定されている。
- canonical prompt 追加に対する post-write verification が実行され、manifest が保存されている。

未完了として残す事項:

- post-write prompt generation / audit のさらなる機械検査強化は、別の workflow operation 機械化改善として扱う。

## 7. 復帰先

この side track 完了後、guidance relocation の本線へ戻った。

戻った地点:

- guidance relocation の参照更新済み差分を、正しい post-write verification flow で検査する地点

本線復帰後に実施した作業:

- `3bff3841 Point guidance references to deployed location`
- `9d9f9f1d Update deployed guidance consumers`
- `main` を `origin/main` へ push 済み

## 8. 運用上の課題

今回の side track は開始時点で記録されず、利用者確認後に事後認定した。

これは次の運用課題を示している。

- 本線から補修作業へ切り替わる時点で、side track 認定を先に行うべきだった。
- side track 終了時には、終了宣言と終了記録を明示するべきだった。
- 今回は `4a7d30c9` で実質終了していたが、終了宣言が遅れたため、後から終了点を確認する必要が生じた。
- `side-track-stack` は read-only の `current` CLI しかなく、push / pop を正規 CLI として実行できない。
- side track 開始操作が機械化されていないため、LLM が working note で代替する余地が残っている。
- 今後は side track push / pop の正規 CLI 化、または `next --json` から side track 開始候補を返す導線が必要である。

この課題は、今回の post-write prompt 機械化 side track の直接対象ではないが、後続の workflow operation 機械化改善で扱うべきである。

## 9. 停止点

このメモは side track の事後認定および終了記録であり、それ自体は commit、API review-run、post-write manifest 作成、guidance relocation 本線復帰を許可しない。

現在は side track 外であり、通常の `next --json` 判定に従う。
