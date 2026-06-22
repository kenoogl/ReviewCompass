---
date: 2026-06-22
record_type: working-note
status: active
topic: postwrite-prompt-mechanization-checklist
related:
  - docs/notes/working/2026-06-21-llm-boundary-and-postwrite-prompt-mechanization-plan.md
  - docs/notes/working/2026-06-21-postwrite-prompt-mechanization-side-track-retroactive-record.md
  - .reviewcompass/guidance/effective-prompts/next-action-post-write-policy-violation.prompt.md
  - tools/api_providers/prepare_post_write_review.py
  - tools/api_providers/post_write_review_flow.py
  - tools/check_workflow_action/prompt_audit.py
---

# Post-write Prompt 機械化 作業チェックリスト

## 1. 目的

このチェックリストは、post-write prompt 機械化を「信頼して使える状態」まで進めるための確認表である。

狭義の side-track は終了済みだが、post-write prompt 生成から API 実行可否判定までの全体は未完了である。そのため、次の作業では、残作業を小さい機械処理単位に分け、各単位で確認してから進める。

## 2. 完了済みとして扱うもの

- [x] `post_write_policy_violation` から API review-run を開始しない gate がある。
- [x] `post_write_policy_violation` 用 canonical effective prompt がある。
- [x] `post_write_verification` の review target に target 本文を含める補修がある。
- [x] `post_write_verification` の review target に source material 本文を含める補修がある。
- [x] prompt manifest に target/source の `content_mode` と `content_sha256` を残す処理がある。
- [x] `post_write_review_flow.py prepare` で `next_action.kind == post_write_verification` 以外を止める処理がある。

## 3. 未完了として扱うもの

### 3.1 Canonical Effective Prompt

- [ ] `post_write_verification` 用 canonical effective prompt を正本として固定する。
- [ ] `post_write_human_decision_required` 用 canonical effective prompt を正本として固定する。
- [ ] runtime 生成物と canonical 正本の関係を明確にする。
- [ ] stale canonical prompt を通常 action として返さない検査を用意する。

確認条件:

- `.reviewcompass/guidance/effective-prompts/` に正本が存在する。
- `next --json` または関連処理が、都度合成ではなく正本 prompt を参照する。
- 元文書変更時の freshness audit へ接続できる。

### 3.2 `post_write_policy_violation.inspect`

- [ ] dirty worktree の変更ファイルを機械分類する。
- [ ] guidance / tools / tests / docs notes / runtime artifacts を別 cluster に分ける。
- [ ] review-run / post-write manifest / commit を forbidden として出す。
- [ ] read-only operation としてファイルを書かないことをテストする。

確認条件:

- `post_write_policy_violation` 地点では、レビュー実行ではなく分類結果が出る。
- 次に許可される操作と禁止操作が機械出力に含まれる。

### 3.3 Source Bundle Builder

- [ ] target 本文を full text または non-summary excerpt として出す。
- [ ] source material 本文を full text または non-summary excerpt として出す。
- [ ] path / SHA だけの bundle を拒否する。
- [ ] target と source material の役割を区別する。
- [ ] SHA と本文の一致を検査する。

確認条件:

- main LLM の要約が target 本文の代替にならない。
- API reviewer が、path-only ではなく実本文を読める。

### 3.4 Prompt Builder

- [ ] source bundle から固定構造の prompt を生成する。
- [ ] prompt 必須セクションを固定する。
- [ ] `1 prompt 1 primary judgment` を守る。
- [ ] runner の output contract と prompt の出力要求を一致させる。
- [ ] variant は設定キーから解決し、手選択にしない。

必須セクション:

- Review Purpose
- User Review Requirements
- Target Materials
- Source Materials
- Review Criteria
- Non-goals / Out of Scope
- Main Preanalysis
- Required Checks
- Output Contract
- Sensitive Information Check

### 3.5 Prompt Audit

- [ ] target file body がない prompt を拒否する。
- [ ] source material body がない prompt を拒否する。
- [ ] path-only source で終わる prompt を拒否する。
- [ ] 要約禁止の場面で summary 表記がある prompt を拒否する。
- [ ] 複数の独立判断を押し込んだ prompt を拒否する。
- [ ] output contract と runner/schema の不一致を拒否する。
- [ ] runner / variant / role が用途と違う prompt を拒否する。
- [ ] prompt source refs と生成 manifest がない prompt を拒否する。
- [ ] sensitive information の疑いがある prompt を拒否する。

確認条件:

- prompt audit が `DEVIATION` の場合、API runner へ進まない。
- invalid prompt を保存する場合も、有効な review result として扱わない。

### 3.6 Runner Gate

- [ ] `next_action.kind == post_write_verification` であることを gate が確認する。
- [ ] prompt audit が `OK` の場合だけ API runner を許可する。
- [ ] prompt audit がない場合は API runner を止める。
- [ ] prompt audit が `DEVIATION` の場合は user approval だけで上書き実行しない。
- [ ] post-write verification 用 variant が post-write context から解決される。
- [ ] CLI default への暗黙 fallback を拒否する。
- [ ] invalid prompt 由来の response を valid review-run として登録しない。

確認条件:

- API provider 起動前に、prompt / manifest / audit / variant / output contract が揃う。
- prompt quality review、proxy decision、post-write verification の runner/schema を混同しない。

### 3.7 実運用ケース確認

- [ ] 実際の post-write 対象ファイルで source bundle、prompt、manifest、audit result が一貫する。
- [ ] generated prompt に target 本文、source material、out of scope、required checks、output contract が含まれる。
- [ ] path / SHA only prompt が拒否される。
- [ ] author summary target が拒否される。
- [ ] 複数判断詰め込み prompt が拒否される。
- [ ] `api_review_prompt_quality` の既定 variant が `claude-sonnet-4-6` / `gemini-3.1-pro-preview` へ解決される。
- [ ] post-write verification の API variant が CLI default へ暗黙 fallback しない。

確認条件:

- この段階まで通って初めて、post-write prompt 機械化を完了扱いにする。

## 4. 次に進める順序

1. このチェックリストを残タスクの確認表として承認する。
2. 3.1 の canonical effective prompt 固定化から始める。
3. TDD で red test を追加する。
4. red test の失敗を確認する。
5. テスト追加 commit を作る。
6. 実装で test pass へ進む。
7. 各小単位ごとに確認、commit、次項目へ進む。

## 5. 現在の判断

次に着手すべき最小単位は、`post_write_verification` 用 canonical effective prompt の固定化である。

理由:

- `post_write_policy_violation` 用 canonical prompt は既にある。
- `post_write_verification` は API prompt 生成へ進む入口なので、ここが runtime 生成や都度合成に寄ると、その後の source bundle / prompt builder / prompt audit が安定しない。
- まず読むべき prompt を固定しないと、後段の機械処理の入力地点が揺れる。

## 6. 進行ログ

### 2026-06-22: 3.1 red test

追加した確認:

- `tests/tools/test_check_workflow_action.py`
  - `NextNavigationTests.test_next_post_write_verification_returns_canonical_effective_prompt`

確認結果:

- 失敗を確認済み。
- 失敗理由は、`post_write_verification` の `effective_prompt_path` が、期待する `.reviewcompass/guidance/effective-prompts/next-action-post-write-verification.prompt.md` ではなく、`.reviewcompass/runtime/effective-prompts/next_action_kind-post_write_verification.prompt.md` になっていること。

次の作業:

- この red test をテスト追加 commit として固定する。
- その後、実装ではテストを変更せず、`post_write_verification` 用 canonical effective prompt 正本と discipline map の参照を追加して pass させる。
